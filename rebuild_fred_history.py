"""지정 구간을 당시 가용 판본으로 다시 만드는 별도 복구 도구. 원본은 덮어쓰지 않는다."""
from pathlib import Path
import argparse,json,os
import pandas as pd
from argus_observation_contract import SERIES,fetch_record,inspect_record,columns_for

def rebuild(frame,start,end,api_key,cache_dir,max_sessions=10,request_get=None):
    out=frame.copy()
    if not isinstance(out.index,pd.DatetimeIndex) or not out.index.is_unique or not out.index.is_monotonic_increasing:
        raise ValueError('날짜 순서·중복을 먼저 확인해야 합니다')
    dates=out.loc[start:end].index
    if not len(dates):raise ValueError('선택 구간에 자료가 없습니다')
    if len(dates)>max_sessions:raise ValueError('지정한 세션 수 상한 초과; 구간을 나누어 실행해야 합니다')
    added={k:pd.Series(index=out.index,dtype='float64' if k==c or k.endswith('_vintage_value') else 'object')
           for c in SERIES for k in columns_for(c) if k not in out}
    out=pd.concat([out,pd.DataFrame(added,index=out.index)],axis=1)
    for c in SERIES:
        for k in columns_for(c):
            if k!=c and not k.endswith('_vintage_value'):out[k]=out[k].astype(object)
    out=out.copy()
    errors=[];verified=0
    for t in dates:
        for c in SERIES:
            record=fetch_record(c,t,api_key,request_get=request_get,cache_dir=cache_dir)
            issues=inspect_record(record,c,t)
            for k,v in record.items():
                out.at[t,k]=v
            if issues:errors.append({'date':str(t.date()),'indicator':c,'issues':issues})
            else:verified+=1
    if all(c in out for c in ('WALCL','WTREGEN','RRPONTSYD')):
        out.loc[dates,'Net_Liquidity']=out.loc[dates,'WALCL']-out.loc[dates,'WTREGEN']-1000*out.loc[dates,'RRPONTSYD']
    return out,{'sessions':len(dates),'verified_records':verified,'required_records':len(dates)*len(SERIES),'errors':errors,'complete':not errors,'scope':'selected_dates_only','publication_time':'not_inferred'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    p.add_argument('--start',required=True);p.add_argument('--end',required=True);p.add_argument('--max-sessions',type=int,default=10)
    p.add_argument('--cache',default='fred_vintage_cache');a=p.parse_args()
    src=Path(a.input);dst=Path(a.output)
    if src.resolve()==dst.resolve():raise ValueError('출력은 원본과 다른 경로여야 합니다')
    if dst.exists() or dst.with_suffix('.audit.json').exists():raise ValueError('기존 결과를 덮어쓰지 않습니다')
    df=pd.read_csv(src,parse_dates=['Date'],index_col='Date',low_memory=False)
    out,report=rebuild(df,a.start,a.end,os.getenv('FRED_API_KEY',''),a.cache,a.max_sessions)
    dst.parent.mkdir(parents=True,exist_ok=True);out.to_csv(dst,index_label='Date')
    dst.with_suffix('.audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='errors'},ensure_ascii=False))
    if not report['complete']:raise SystemExit(2)
if __name__=='__main__':main()
