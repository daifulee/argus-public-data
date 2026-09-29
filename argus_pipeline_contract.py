"""거래일별 데이터와 게시 증거 계약. 네트워크 읽기와 상태 저장은 명시적으로 호출한다."""
from __future__ import annotations
import argparse
import base64
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request
import zipfile

DATA_RECEIPT = 'argus_data_publication.json'
BRIEF_RECEIPT = 'argus_brief_publication.json'
STATE_PATH = 'data/argus_pipeline_recovery_state.json'
HOLD_PATH = 'argus_pipeline_hold.json'
FILES = ('argus_data.csv', 'argus_data_daily.csv', 'argus_data_weekly.csv',
         'argus_data_monthly.csv', 'latest.json')
ACTIVE = {'queued', 'in_progress', 'waiting', 'pending', 'requested'}
PUBLIC = 'daifulee/argus-public-data'
# 제공된 수집기 v3.9.22의 ETF_TICKERS와 동일. 종목 추가 시 계약도 함께 갱신한다.
CLOSE_TICKERS = ('GLD SLV COPX NLR QQQM VNM IWM PAVE SMH EWZ XLE INDA ITA TLT VEA '
                 'XLF XLV XLU CQQQ CIBR SGOV SPY IEF HYG TIP LQD PDBC').split()


class IntegrityError(ValueError):
    pass


class DataNotReady(ValueError):
    pass


def utc(value):
    stamp = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if stamp.tzinfo is None:
        raise IntegrityError('시간대 없는 시각')
    return stamp.astimezone(dt.timezone.utc)


def expected_session(now=None):
    import pandas as pd
    import exchange_calendars as xcals
    stamp = pd.Timestamp(now or dt.datetime.now(dt.timezone.utc))
    if stamp.tzinfo is None:
        raise IntegrityError('현재 시각의 시간대 필요')
    stamp = stamp.tz_convert('UTC')
    cal = xcals.get_calendar('XNYS')
    sessions = cal.sessions_in_range((stamp - pd.Timedelta(days=30)).date(), stamp.date())
    finished = [(s, cal.session_close(s)) for s in sessions if cal.session_close(s) <= stamp]
    if not finished:
        raise IntegrityError('완결 거래일 없음')
    session, close = finished[-1]
    return str(session.date()), close.to_pydatetime()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def csv_last(blob):
    rows = list(csv.DictReader(io.StringIO(blob.decode('utf-8-sig'))))
    if not rows or 'Date' not in rows[0]:
        raise IntegrityError('Date 열 또는 데이터 행 없음')
    dates = [dt.date.fromisoformat(row['Date']) for row in rows]
    if dates != sorted(set(dates)):
        raise IntegrityError('날짜 중복 또는 역순')
    return str(dates[-1]), rows[-1]


def verify_data(receipt, blobs, expected):
    if not isinstance(receipt, dict) or receipt.get('schema') != 'argus_data_publication/1.0':
        raise IntegrityError('데이터 게시 증거 스키마 오류')
    hashes = receipt.get('files_sha256', {})
    for name in FILES:
        if name not in blobs or hashes.get(name) != digest(blobs[name]):
            raise IntegrityError('데이터 해시 불일치: ' + name)
    day, row = csv_last(blobs['argus_data.csv'])
    daily_day, _ = csv_last(blobs['argus_data_daily.csv'])
    latest = json.loads(blobs['latest.json'])
    if not (day == daily_day == latest.get('Date') == receipt.get('session')):
        raise IntegrityError('통합·일일·latest·게시 증거 날짜 불일치')
    if day > expected:
        raise IntegrityError('미래 또는 미완결 입력')
    if day < expected:
        raise DataNotReady(f'데이터 미도착: {day} != {expected}')
    # 최신 날짜 라벨만 붙은 이월 종가를 배포 완료로 승격하지 않는다.
    if row.get('CLOSE_FRESHNESS') != 'fresh':
        raise DataNotReady('정확 거래일 종가가 모두 준비되지 않음')
    source_columns = {t + '_Close_source' for t in CLOSE_TICKERS}
    source_columns.update(k for k in row if k.endswith('_Close_source'))
    for column in sorted(source_columns):
        if column not in row:
            raise IntegrityError('종가 출처 열 누락: ' + column)
        if row[column] != 'market_batch_live':
            raise DataNotReady('당일 실측 종가 미확보: ' + column)
        try:
            price = float(row[column.removesuffix('_source')])
        except (KeyError, ValueError, TypeError) as exc:
            raise IntegrityError('종가 값 형식 오류: ' + column) from exc
        if not math.isfinite(price) or price <= 0:
            raise IntegrityError('종가 값 범위 오류: ' + column)
    return receipt


def make_data_receipt(root, expected, run_id='', source_revision=''):
    root = Path(root)
    blobs = {name: (root / name).read_bytes() for name in FILES}
    receipt = {'schema': 'argus_data_publication/1.0', 'session': expected,
               'files_sha256': {k: digest(v) for k, v in blobs.items()},
               'run_id': str(run_id), 'source_revision': source_revision,
               'verified_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
    verify_data(receipt, blobs, expected)
    (root / DATA_RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    return receipt


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme != 'https':
            raise IntegrityError('비암호화 리다이렉트 거부')
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if urllib.parse.urlsplit(newurl).hostname != 'api.github.com':
            redirected.remove_header('Authorization')
        return redirected


class GitHub:
    def __init__(self, repo, token):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
            raise ValueError('저장소 이름 오류')
        if not token:
            raise ValueError('GitHub 토큰 필요: ' + repo)
        self.repo, self.token = repo, token
        self.opener = urllib.request.build_opener(SafeRedirect())

    def request(self, method, suffix, body=None, binary=False):
        req = urllib.request.Request('https://api.github.com/repos/' + self.repo + suffix,
            data=None if body is None else json.dumps(body).encode(), method=method,
            headers={'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
                     'Content-Type': 'application/json', 'X-GitHub-Api-Version': '2022-11-28',
                     'User-Agent': 'ARGUS-Pipeline/2.0'})
        with self.opener.open(req, timeout=30) as response:
            raw = response.read()
        return raw if binary else (json.loads(raw) if raw else None)

    def head(self):
        return self.request('GET', '/git/ref/heads/main')['object']['sha']

    def blob(self, path, ref='main', optional=False):
        if path.startswith('/') or '..' in path.split('/'):
            raise IntegrityError('파일 경로 오류')
        suffix = '/contents/' + urllib.parse.quote(path, safe='/') + '?ref=' + urllib.parse.quote(ref, safe='')
        try:
            obj = self.request('GET', suffix)
        except urllib.error.HTTPError as exc:
            if optional and exc.code == 404:
                return None, None
            raise
        if obj.get('encoding') == 'base64':
            return base64.b64decode(obj['content']), obj['sha']
        # Contents API가 큰 파일 내용을 생략하면 같은 Git blob을 직접 읽는다.
        content = self.request('GET', '/git/blobs/' + obj['sha'])
        if content.get('encoding') != 'base64':
            raise IntegrityError('지원하지 않는 파일 인코딩')
        return base64.b64decode(content['content']), obj['sha']

    def put(self, path, value, old_sha=None):
        raw = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False, indent=2).encode()
        body = {'message': 'ARGUS pipeline evidence [skip ci]', 'branch': 'main',
                'content': base64.b64encode(raw).decode()}
        if old_sha:
            body['sha'] = old_sha
        return self.request('PUT', '/contents/' + urllib.parse.quote(path, safe='/'), body)['content']['sha']

    def runs(self, workflow, since):
        result = []
        for page in range(1, 11):
            query = urllib.parse.urlencode({'branch': 'main', 'per_page': 100, 'page': page,
                                           'created': '>=' + since.isoformat()})
            rows = self.request('GET', '/actions/workflows/' + urllib.parse.quote(workflow, safe='') + '/runs?' + query)['workflow_runs']
            result.extend(rows)
            if len(rows) < 100:
                return result
        raise IntegrityError('실행 목록 페이지 한도 초과 — 자동 실행 금지')

    def dispatch(self, workflow, inputs):
        return self.request('POST', '/actions/workflows/' + urllib.parse.quote(workflow, safe='') + '/dispatches',
                            {'ref': 'main', 'inputs': inputs})

    def diagnostic(self, run):
        rows = self.request('GET', f"/actions/runs/{run['id']}/artifacts?per_page=100")['artifacts']
        name = f"argus-pipeline-result-{run['id']}-{run.get('run_attempt', 1)}"
        matches = [a for a in rows if a['name'] == name and not a.get('expired')]
        if len(matches) != 1:
            return {'retryable': False, 'reason': '이번 실행의 구조화된 오류 증거 없음'}
        raw = self.request('GET', f"/actions/artifacts/{matches[0]['id']}/zip", binary=True)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            info = archive.getinfo('argus_pipeline_result.json')
            if info.file_size > 65536:
                raise IntegrityError('오류 증거 크기 초과')
            result = json.loads(archive.read(info))
        if str(result.get('run_id')) != str(run['id']) or int(result.get('run_attempt', 0)) != run.get('run_attempt', 1):
            raise IntegrityError('오류 증거 실행 식별 불일치')
        return result


def read_data(client, expected, commit=None):
    commit = commit or client.head()
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise IntegrityError('고정 커밋 형식 오류')
    hold, _ = client.blob(HOLD_PATH, commit, optional=True)
    if hold is not None and json.loads(hold).get('active') is not False:
        raise IntegrityError('마이그레이션 검증 대기 — 운영자 NORMAL 수동 실행 필요')
    raw, _ = client.blob(DATA_RECEIPT, commit, optional=True)
    if raw is None:
        raise DataNotReady('검증된 데이터 게시 증거 없음')
    receipt = json.loads(raw)
    blobs = {name: client.blob(name, commit)[0] for name in FILES}
    verify_data(receipt, blobs, expected)
    return commit, receipt, blobs


def brief_is_current(receipt, data, html):
    if not isinstance(receipt, dict) or receipt.get('schema') != 'argus_brief_publication/1.0':
        return False
    return (receipt.get('session') == data['session']
            and receipt.get('data_hashes') == data['files_sha256']
            and receipt.get('html_sha256') == digest(html)
            and receipt.get('maq_outcome') == 'success')


def save_failure(exc, path='argus_pipeline_result.json'):
    # 확인된 일시적 데이터 미도착만 자동 재시도한다. 기타 오류를 추측으로 분류하지 않는다.
    import subprocess
    retryable = isinstance(exc, DataNotReady) or (isinstance(exc, subprocess.CalledProcessError) and exc.returncode == 75)
    result = {'run_id': os.getenv('GITHUB_RUN_ID', ''), 'run_attempt': int(os.getenv('GITHUB_RUN_ATTEMPT', '1')),
              'retryable': retryable, 'reason': type(exc).__name__ + ': ' + str(exc),
              'status': 'DATA_NOT_READY' if retryable else 'BLOCKED'}
    Path(path).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['fetch', 'publish-brief'])
    args = parser.parse_args()
    client = GitHub(PUBLIC, os.environ['PUBLIC_REPO_PAT'])
    expected, _ = expected_session()
    try:
        if args.mode == 'fetch':
            desired = os.getenv('PIPELINE_SESSION', '')
            if desired and desired != expected:
                raise IntegrityError('요청 세션이 현재 완결 세션과 다름')
            commit, receipt, blobs = read_data(client, expected, os.getenv('PIPELINE_DATA_COMMIT') or None)
            for name, blob in blobs.items():
                Path(name).write_bytes(blob)
            Path('argus_pipeline_input.json').write_text(json.dumps({'commit': commit, 'receipt': receipt}), encoding='utf-8')
            print('PINNED DATA VERIFY PASS:', expected, commit)
        else:
            pinned = json.loads(Path('argus_pipeline_input.json').read_text(encoding='utf-8'))
            if pinned['receipt']['session'] != expected:
                raise IntegrityError('빌드 중 거래일 변경 — 완료 증거 게시 금지')
            html = Path('briefing.html').read_bytes()
            # 변경 가능한 main을 한 번 고정한 뒤 서빙 HTML을 검증한다.
            remote_commit = client.head()
            remote_html, _ = client.blob('briefing.html', remote_commit)
            if digest(remote_html) != digest(html):
                raise IntegrityError('원격 HTML과 빌드본 불일치')
            if os.getenv('MAQ_CAUSAL_OUTCOME') != 'success':
                raise IntegrityError('MAQ 실패 — 완료 증거 게시 금지')
            receipt = {'schema': 'argus_brief_publication/1.0', 'session': expected,
                       'data_commit': pinned['commit'], 'data_hashes': pinned['receipt']['files_sha256'],
                       'html_sha256': digest(html), 'html_commit': remote_commit, 'maq_outcome': 'success',
                       'auxiliary': {key: os.getenv(key) for key in ['ORACLE_SHADOW_OUTCOME', 'DIVERGENCE_CAUSAL_OUTCOME', 'SCOREBOARD_CAUSAL_OUTCOME']},
                       'run_id': os.getenv('GITHUB_RUN_ID'), 'verified_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
            _, old_sha = client.blob(BRIEF_RECEIPT, optional=True)
            client.put(BRIEF_RECEIPT, receipt, old_sha)
            verified_commit = client.head()
            check, _ = client.blob(BRIEF_RECEIPT, verified_commit)
            if json.loads(check) != receipt:
                raise IntegrityError('완료 증거 원격 대조 실패')
            verified_html, _ = client.blob('briefing.html', verified_commit)
            if not brief_is_current(receipt, pinned['receipt'], verified_html):
                raise IntegrityError('완료 증거 저장 중 원격 HTML 변경')
            print('BRIEF DELIVERY RECEIPT PASS:', expected)
    except Exception as exc:
        save_failure(exc)
        raise


if __name__ == '__main__':
    main()
