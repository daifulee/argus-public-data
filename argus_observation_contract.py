"""관측일과 당시 가용 판본을 구분하는 일별 자료 계약.

FRED의 일별 판본은 정확한 장중 발표 시각을 제공하지 않는다.
따라서 종가 의사결정일보다 앞선 날짜의 판본만 채택한다.
publication_at은 추정해서 채우지 않는다. 판본 경계는 발표 시각이 아니다.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
from numbers import Real
from pathlib import Path
import hashlib
import json
import math
import uuid

VERSION = 'fred_prior_date_v1'
SERIES = {
    'DFII10':'DFII10', 'T10YIE':'T10YIE', 'T5YIE':'T5YIE',
    'OAS_HY':'BAMLH0A0HYM2', 'OAS_IG':'BAMLC0A0CM',
    'SAHMCURRENT':'SAHMCURRENT', 'T10Y3M':'T10Y3M', 'T10Y2Y':'T10Y2Y',
    'WALCL':'WALCL', 'WTREGEN':'WTREGEN', 'RRPONTSYD':'RRPONTSYD',
    'ICSA':'ICSA', 'CCSA':'CCSA', 'UMCSENT':'UMCSENT', 'NFCI':'NFCI',
    'USD_CNY':'DEXCHUS', 'DGS10':'DGS10', 'STLFSI':'STLFSI4',
}
# 운영 신선도 상한이다. 발표 날짜를 추정하거나 매매 임계값을 바꾸는 수치가 아니다.
MAX_OBSERVATION_AGE_DAYS = {**dict.fromkeys(SERIES, 14),
    **dict.fromkeys(('NFCI','STLFSI','ICSA','CCSA','WALCL','WTREGEN'), 35),
    **dict.fromkeys(('SAHMCURRENT','UMCSENT'), 75)}
REQUIRED = ('DFII10','T10YIE','OAS_HY','OAS_IG','NFCI','SAHMCURRENT','STLFSI')
FIELDS = ('source','status','asof_date','vintage_date','observation_date',
          'realtime_start','realtime_end','retrieved_at','series_id',
          'error_code','publication_at','time_precision','contract_version',
          'vintage_value','response_sha256')


def finite(value):
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(float(value))


def day(value):
    """날짜 표기의 앞 열 자리만 사용하며, 유효한 ISO 날짜만 허용한다."""
    return date.fromisoformat(str(value)[:10])


def empty_record(column, target, code='UNVERIFIED'):
    d=day(target)
    r={column:float('nan')}
    r.update({column+'_'+k:None for k in FIELDS})
    r.update({column+'_source':'fred_vintage_missing',column+'_status':'unverified',
              column+'_asof_date':d.isoformat(),column+'_vintage_date':(d-timedelta(days=1)).isoformat(),
              column+'_series_id':SERIES[column],column+'_error_code':code,
              column+'_time_precision':'daily_prior_date_not_intraday',
              column+'_contract_version':VERSION})
    return r


def _parse_payload(payload, column, target, retrieved_at):
    """요청 날짜가 실제 응답 판본 범위에 포함되는지 검사한다."""
    r=empty_record(column,target,'NO_VALID_PRIOR_DATE_OBSERVATION')
    cutoff=day(r[column+'_vintage_date']);best=None
    try:
        if not day(payload['realtime_start']) <= cutoff <= day(payload['realtime_end']):
            return empty_record(column,target,'RESPONSE_VINTAGE_MISMATCH')
        observations=payload['observations']
        if not isinstance(observations,list):raise ValueError()
        for o in observations:
            try:
                if isinstance(o.get('value'),bool):continue
                v=float(o['value']);observed=day(o['date'])
                start=day(o['realtime_start']);end=day(o['realtime_end'])
                if not math.isfinite(v) or observed>cutoff or not start<=cutoff<=end:continue
                if best is None or observed>best[0]:best=(observed,v,start,end)
            except (KeyError,ValueError,TypeError,OverflowError):continue
    except (KeyError,ValueError,TypeError):
        return empty_record(column,target,'INVALID_RESPONSE_SCHEMA')
    if best is not None:
        observed,v,start,end=best
        if (day(target)-observed).days > MAX_OBSERVATION_AGE_DAYS[column]:
            return empty_record(column,target,'OBSERVATION_AGE_EXCEEDED')
        digest=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
        r.update({column:v,column+'_source':'fred_prior_date_vintage',column+'_status':'verified_prior_date',
                  column+'_observation_date':str(observed),column+'_realtime_start':str(start),
                  column+'_realtime_end':str(end),column+'_vintage_value':v,
                  column+'_retrieved_at':retrieved_at,column+'_error_code':'',column+'_response_sha256':digest})
    return r


def fetch_record(column,target,api_key,request_get=None,cache_dir=None,now=None):
    """최신값·익명 그래프 자료로 우회하지 않는다. 요청 실패는 인증된 값으로 표시하지 않는다."""
    d=day(target);cutoff=d-timedelta(days=1)
    stamp=datetime.now(timezone.utc) if now is None else now
    if stamp.tzinfo is None:raise ValueError('수집 시각에 시간대 필요')
    if cutoff>=stamp.astimezone(timezone.utc).date():return empty_record(column,d,'FUTURE_VINTAGE_REQUEST')
    cached=Path(cache_dir)/(SERIES[column]+'_'+str(cutoff)+'.json') if cache_dir else None
    if cached and cached.is_file():
        try:
            item=json.loads(cached.read_text(encoding='utf-8'))
            if item['series_id']!=SERIES[column] or item['vintage_date']!=str(cutoff):raise ValueError()
            retrieved=datetime.fromisoformat(item['retrieved_at'])
            if retrieved.tzinfo is None or retrieved>stamp:raise ValueError()
            r=_parse_payload(item['payload'],column,d,item['retrieved_at'])
            if r[column+'_status']=='verified_prior_date':return r
        except (OSError,ValueError,KeyError,TypeError):pass
    if not api_key:return empty_record(column,d,'FRED_API_KEY_MISSING')
    if request_get is None:
        import requests
        request_get=requests.get
    params={'series_id':SERIES[column],'api_key':api_key,'file_type':'json',
            'realtime_start':str(cutoff),'realtime_end':str(cutoff),
            'observation_end':str(cutoff),'sort_order':'desc','limit':100}
    try:
        response=request_get('https://api.stlouisfed.org/fred/series/observations',params=params,timeout=20)
        response.raise_for_status();payload=response.json()
        r=_parse_payload(payload,column,d,stamp.isoformat())
    except Exception:
        # 인증정보가 포함될 수 있는 예외 문자열은 출력하지 않는다.
        return empty_record(column,d,'FRED_REQUEST_OR_PARSE_ERROR')
    if cached and r[column+'_status']=='verified_prior_date':
        cached.parent.mkdir(parents=True,exist_ok=True)
        item={'series_id':SERIES[column],'vintage_date':str(cutoff),'retrieved_at':stamp.isoformat(),'payload':payload}
        tmp=cached.with_name(cached.name+'.'+uuid.uuid4().hex+'.tmp')
        try:
            tmp.write_text(json.dumps(item,ensure_ascii=False,allow_nan=False),encoding='utf-8');tmp.replace(cached)
        finally:
            tmp.unlink(missing_ok=True)
    return r


def inspect_record(row,column,target):
    """값과 판본 메타데이터의 분리·과거 라벨 복사를 검출한다."""
    issues=[];p=column+'_';d=day(target)
    if not finite(row.get(column)):issues.append('NONFINITE')
    if row.get(p+'contract_version')!=VERSION:issues.append('CONTRACT_VERSION')
    if row.get(p+'series_id')!=SERIES[column]:issues.append('SERIES_ID')
    if row.get(p+'status')!='verified_prior_date' or row.get(p+'source')!='fred_prior_date_vintage':issues.append('UNVERIFIED')
    try:
        a=day(row[p+'asof_date']);v=day(row[p+'vintage_date']);o=day(row[p+'observation_date'])
        lo=day(row[p+'realtime_start']);hi=day(row[p+'realtime_end'])
        if a!=d or v!=d-timedelta(days=1) or o>v or not lo<=v<=hi:issues.append('DATE_OR_VINTAGE_MISMATCH')
        if (d-o).days>MAX_OBSERVATION_AGE_DAYS[column]:issues.append('OBSERVATION_AGE_EXCEEDED')
        receipt=datetime.fromisoformat(str(row[p+'retrieved_at']))
        if receipt.tzinfo is None:issues.append('RECEIPT_TIMEZONE')
    except (KeyError,ValueError,TypeError):issues.append('METADATA_MISSING')
    vv=row.get(p+'vintage_value')
    if not finite(vv) or (finite(row.get(column)) and not math.isclose(float(vv),float(row[column]),rel_tol=1e-12,abs_tol=1e-12)):issues.append('VALUE_METADATA_MISMATCH')
    digest=row.get(p+'response_sha256')
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):issues.append('RESPONSE_EVIDENCE_MISSING')
    return issues


def columns_for(column):
    return [column]+[column+'_'+k for k in FIELDS]


def protected_column(column):
    return any(column==c or column.startswith(c+'_') for c in SERIES)


def mask_invalid_records(df):
    """기존 자료를 바꾸지 않고 새 계약 수집행의 무효값 재보완을 막는다."""
    out=df.copy()
    for c in SERIES:
        marker=c+'_contract_version'
        if c not in out or marker not in out:continue
        active=out[marker].notna()
        for t in out.index[active]:
            if inspect_record(out.loc[t],c,t):out.at[t,c]=float('nan')
    return out
