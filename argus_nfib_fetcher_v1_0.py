# VERSION: argus_nfib_fetcher_v1_0
# DATE: 2026-07-02 KST (S247)
# CHANGE: 신설 — NFIB SBET API(문서 §2.9 검증 소스)에서 낙관지수 월값 수집 → nfib_opt.json 조건부 갱신
# 규약: monthyear(데이터월 1일) → asof=데이터월 말일 저장. 소비 모듈 PIT_LAG 14일 → 익월 공표일 정합 (look-ahead 원천 차단)
# 가드: 값범위 75~115 / 월 단조 / 중복 금지 / 원자적 쓰기 / 실패·무변경 시 파일 불변 exit 0 (fail-safe)
import json, os, sys, tempfile
import pandas as pd

URL='https://api.nfib-sbet.org/rest/sbetdb/_proc/getIndicators2'
HDR={'X-DreamFactory-Application-Name':'sbet','User-Agent':'Mozilla/5.0'}
JSON_PATH=os.environ.get('NFIB_JSON_PATH','nfib_opt.json')
VMIN,VMAX=75.0,115.0

def fetch_api():
    """문서 §2.9 그대로: form-encoded POST → [{'monthyear':'2026/5/1','OPT_INDEX':94.44},...]"""
    import requests
    data={'app_name':'sbet',
     'params[0][name]':'minYear','params[0][param_type]':'IN','params[0][value]':'2006',
     'params[1][name]':'minMonth','params[1][param_type]':'IN','params[1][value]':'1',
     'params[2][name]':'maxYear','params[2][param_type]':'IN','params[2][value]':str(pd.Timestamp.now().year),
     'params[3][name]':'maxMonth','params[3][param_type]':'IN','params[3][value]':'12',
     'params[4][name]':'indicator','params[4][param_type]':'IN','params[4][value]':'OPT_INDEX'}
    r=requests.post(URL,timeout=30,headers=HDR,data=data); r.raise_for_status()
    return r.json()

def to_records(raw):
    out=[]
    for it in raw:
        d=pd.to_datetime(it['monthyear']); v=float(it['OPT_INDEX'])
        if not (VMIN<=v<=VMAX): raise ValueError(f'범위가드: {d.date()} {v}')
        out.append({'asof':(d+pd.offsets.MonthEnd(0)).strftime('%Y-%m-%d'),'opt':round(v,2)})
    out.sort(key=lambda x:x['asof'])
    if len({r['asof'] for r in out})!=len(out): raise ValueError('중복 월 가드')
    return out

def merge_write(new):
    cur=json.load(open(JSON_PATH,encoding='utf-8')) if os.path.exists(JSON_PATH) else {'meta':{},'series':[]}
    old=cur.get('series',[]); last=max((r['asof'] for r in old),default='1900-01-01')
    add=[r for r in new if r['asof']>last]
    if not add:
        print(f'변경 없음 (최신 asof {last})'); return False
    if old and add[0]['asof']<=last: raise ValueError('단조 가드')
    cur['series']=old+add
    cur.setdefault('meta',{}).update({'convention':'asof=데이터월 말일; 유효일=asof+14d','last_update':pd.Timestamp.now().strftime('%Y-%m-%d')})
    fd,tmp=tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(JSON_PATH)) or '.')
    with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(cur,f,ensure_ascii=False,indent=1)
    os.replace(tmp,JSON_PATH)
    print(f'추가 {len(add)}개월: {", ".join(r["asof"]+"="+str(r["opt"]) for r in add)}'); return True

def selftest():
    sample=[{'monthyear':'2026/5/1','OPT_INDEX':94.44},{'monthyear':'2026/4/1','OPT_INDEX':95.4}]
    rec=to_records(sample)
    assert rec[0]=={'asof':'2026-04-30','opt':95.4} and rec[1]=={'asof':'2026-05-31','opt':94.44}, rec
    print('SELFTEST PASS: 문서 스키마 → 말일 규약 변환 정합'); return 0

if __name__=='__main__':
    if '--selftest' in sys.argv: sys.exit(selftest())
    try:
        merge_write(to_records(fetch_api()))
    except Exception as e:
        print(f'fail-safe 무변경 종료: {e}'); sys.exit(0)
