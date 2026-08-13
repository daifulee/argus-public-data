# =====================================================================
# ARGUS — 광범위 FRED 거시지표 추출 v2 (Colab + GHA 겸용)
# 목적: 선행신호 탐색용 broad 거시지표 자료 축적 → argus_fred_broad.csv 산출
#
# 🦅 v2 (2026-08-13, S288 DIR-S288_DATA_SUPPLY_SSOT 근본 대책):
#   [추가 1] THREEFYTP10 — ACM 10년 기간프리미엄 (NY Fed, FRED 경유) → 신규 카테고리 "기간프리미엄"
#   [추가 2] EBP — Gilchrist–Zakrajšek 초과채권프리미엄 (연준 노트 CSV, 비FRED) + GZ 스프레드
#   [추가 3] 실행환경 겸용 — FRED_API_KEY 를 환경변수에서 우선 회수 (GHA secrets),
#            키 부재 시 keyless fredgraph.csv 폴백 → Colab 수동 실행도 기존과 동일하게 동작
#   [불변]   기존 130종 시리즈 목록·일간 그리드·ffill·메타 산출 로직 100% 보존
#
# 사용법 (Colab): 기존과 동일 — 키 입력 후 실행 → CSV 다운로드 → 레포 업로드
# 사용법 (GHA)  : deploy_fred_broad.yml 이 주 1회 + 수동 실행 → 자동 커밋
# 주석: 한국어. 저빈도(월간 등)는 ffill, frequency 메타 동시 산출(발표시차 보정용)
# =====================================================================

# --- 0) 라이브러리 ---
import io
import os
import subprocess
import sys
import time

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "fredapi", "pandas", "requests"], check=False)
import numpy as np
import pandas as pd
import requests

# --- 1) FRED API KEY — 환경변수 우선 (GHA secrets), 없으면 아래 상수 (Colab 수동) ---
FRED_API_KEY = os.environ.get("FRED_API_KEY", "PASTE_YOUR_FRED_API_KEY_HERE")
_UA = {"User-Agent": "ARGUS-fetcher/2.0 (+https://github.com/daifulee/argus-public-data)"}

_fred = None
if FRED_API_KEY and "PASTE" not in FRED_API_KEY:
    try:
        from fredapi import Fred
        _fred = Fred(api_key=FRED_API_KEY)
        print("FRED 접근: API 키 모드")
    except Exception as _e:
        print(f"fredapi 초기화 실패({type(_e).__name__}) → keyless 폴백")
if _fred is None:
    print("FRED 접근: keyless fredgraph.csv 모드")


def fred_series(sid: str, start: str) -> pd.Series:
    """FRED 시리즈 회수 — API 키 모드 우선, keyless fredgraph.csv 폴백."""
    if _fred is not None:
        s = _fred.get_series(sid, observation_start=start)
        return s[~s.index.duplicated(keep="last")].sort_index()
    r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={start}",
                     headers=_UA, timeout=90)
    r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text))
    d.columns = ["Date", "v"]
    d["Date"] = pd.to_datetime(d["Date"])
    d["v"] = pd.to_numeric(d["v"], errors="coerce")
    s = d.dropna().set_index("Date")["v"]
    return s[~s.index.duplicated(keep="last")].sort_index()


# --- 2) 추출 대상 시리즈 (카테고리별 broad 셋 — v1 130종 100% 보존 + 기간프리미엄 신설) ---
#   ARGUS 유니버스(반도체/원전/구리/금은/EM/기술/방산/유틸/금융/에너지) driver 망라
SERIES = {
 "금리_명목":   ["DGS1MO","DGS3MO","DGS6MO","DGS1","DGS2","DGS3","DGS5","DGS7","DGS10","DGS20","DGS30"],
 "금리_실질":   ["DFII5","DFII7","DFII10","DFII20","DFII30"],
 "정책금리":    ["FEDFUNDS","DFF","DFEDTARU","DFEDTARL"],
 "수익률커브":  ["T10Y2Y","T10Y3M","T5YFF"],
 "기간프리미엄":["THREEFYTP10"],   # 🆕 v2 — ACM 10년 기간프리미엄 (Fisher·성장/긴축발 분해와 직교축)
 "기대인플레":  ["T5YIE","T7YIE","T10YIE","T5YIFR","T20YIEM"],
 "물가":        ["CPIAUCSL","CPILFESL","PCEPI","PCEPILFE","PPIACO","PPIFIS"],
 "신용스프레드":["BAMLH0A0HYM2","BAMLC0A0CM","BAMLC0A4CBBB","BAMLH0A3HYC","BAMLEMCBPIOAS","BAMLC0A1CAAA"],
 "통화유동성":  ["M1SL","M2SL","M2REAL","WALCL","WRESBAL","RRPONTSYD","WTREGEN","BOGMBASE","TOTRESNS"],
 "금융여건":    ["NFCI","ANFCI","STLFSI4","NFCICREDIT","NFCILEVERAGE","NFCIRISK"],
 "환율":        ["DTWEXBGS","DTWEXAFEGS","DEXUSEU","DEXJPUS","DEXKOUS","DEXCHUS","DEXUSUK",
                 "DEXCAUS","DEXMXUS","DEXBZUS","DEXINUS","DEXTAUS","DEXSDUS","DEXSIUS"],
 "활동생산":    ["INDPRO","IPMAN","IPG3344S","TCU","MCUMFN"],
 "주문투자":    ["NEWORDER","DGORDER","AMTMNO","ACOGNO","BUSINV","ISRATIO"],
 "소비소매":    ["RSAFS","RRSFS","PCE","DSPIC96"],
 "노동":        ["ICSA","CCSA","PAYEMS","UNRATE","SAHMCURRENT","SAHMREALTIME","JTSJOL","AWHMAN"],
 "심리선행":    ["UMCSENT","USSLIND","USALOLITONOSTSAM"],
 "주택":        ["HOUST","PERMIT","MORTGAGE30US","CSUSHPINSA","MSACSR"],
 "변동성":      ["VIXCLS","OVXCLS","VXNCLS","GVZCLS"],
 "원자재":      ["DCOILWTICO","DCOILBRENTEU","GOLDAMGBD228NLBM","PCOPPUSDM","DHHNGSP",
                 "PALUMUSDM","PNICKUSDM"],
}

START = "2006-01-01"   # ARGUS BT 시작(2007) 대비 여유 1년

# --- 3) 추출 루프 (실패 skip + frequency 기록) ---
all_series = {}
meta_rows = []
flat = [(cat, sid) for cat, ids in SERIES.items() for sid in ids]
print(f"총 {len(flat)}개 시리즈 추출 시작...\n")
for k, (cat, sid) in enumerate(flat, 1):
    try:
        s = fred_series(sid, START)
        all_series[sid] = s
        # 발표 빈도 추정 (관측 간격 중앙값)
        if len(s) > 5:
            gap = np.median(np.diff(s.index.values).astype("timedelta64[D]").astype(int))
        else:
            gap = np.nan
        freq = "일간" if gap<=4 else ("주간" if gap<=10 else ("월간" if gap<=40 else "분기+"))
        meta_rows.append({"series": sid, "category": cat, "n_obs": len(s),
                          "start": str(s.index.min().date()) if len(s) else "",
                          "end": str(s.index.max().date()) if len(s) else "",
                          "freq": freq, "gap_days": gap})
        print(f"  [{k:3d}/{len(flat)}] ✅ {sid:18s} {cat:10s} n={len(s):5d} {freq}")
    except Exception as e:
        meta_rows.append({"series": sid, "category": cat, "n_obs": 0, "freq": "FAIL"})
        print(f"  [{k:3d}/{len(flat)}] ❌ {sid:18s} {cat:10s} 실패: {type(e).__name__}")
    time.sleep(0.12)   # rate limit 여유

# --- 3b) 🆕 v2: EBP (Gilchrist–Zakrajšek) — 비FRED 소스 (연준 노트 월간 CSV) ---
#     실패해도 전체 산출은 계속한다 (부분 실패 허용 · 침묵 금지)
try:
    _r = requests.get("https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv",
                      headers=_UA, timeout=90)
    _r.raise_for_status()
    _d = pd.read_csv(io.StringIO(_r.text))
    _dc = next(c for c in _d.columns if "date" in c.lower())
    _d[_dc] = pd.to_datetime(_d[_dc])
    _d = _d.set_index(_dc).sort_index()
    for _col, _name in [("ebp", "EBP"), ("gz_spread", "GZ_SPREAD")]:
        _hit = [c for c in _d.columns if c.lower() == _col]
        if _hit:
            s = pd.to_numeric(_d[_hit[0]], errors="coerce").dropna()
            s = s[s.index >= START]
            all_series[_name] = s
            meta_rows.append({"series": _name, "category": "신용_EBP", "n_obs": len(s),
                              "start": str(s.index.min().date()), "end": str(s.index.max().date()),
                              "freq": "월간", "gap_days": 30})
            print(f"  [EBP] ✅ {_name:18s} 신용_EBP  n={len(s):5d} 월간 (연준 노트)")
except Exception as e:
    meta_rows.append({"series": "EBP", "category": "신용_EBP", "n_obs": 0, "freq": "FAIL"})
    print(f"  [EBP] ❌ 연준 노트 CSV 실패: {type(e).__name__} — 나머지 산출 계속")

# --- 4) 일간 그리드 정렬 (영업일) + ffill (저빈도 발표 보정) ---
idx = pd.bdate_range(START, pd.Timestamp.today().normalize())
df = pd.DataFrame(index=idx)
for sid, s in all_series.items():
    df[sid] = s.reindex(df.index.union(s.index)).sort_index().ffill().reindex(df.index)

# --- 5) 저장 ---
df.index.name = "Date"
df.to_csv("argus_fred_broad.csv")
meta = pd.DataFrame(meta_rows)
meta.to_csv("argus_fred_meta.csv", index=False)

ok = (meta["n_obs"]>0).sum()
print(f"\n===== 완료 =====")
print(f"성공 {ok}/{len(meta)} 시리즈 / 일간 그리드 {df.shape[0]}행 × {df.shape[1]}열")
print(f"기간 {df.index.min().date()} ~ {df.index.max().date()}")
print(f"산출: argus_fred_broad.csv ({df.shape[1]}지표) + argus_fred_meta.csv (frequency 메타)")

# --- 6) 🆕 v2: 무결성 게이트 — 핵심 시리즈 결손 시 비정상 종료 (GHA 커밋 차단용) ---
_CRITICAL = ["DGS10", "DTWEXBGS", "WALCL", "VIXCLS", "DCOILWTICO"]
_missing = [c for c in _CRITICAL if c not in df.columns or df[c].notna().mean() < 0.9]
if _missing:
    print(f"🔴 무결성 게이트 FAIL — 핵심 시리즈 결손: {_missing} (커밋 금지)")
    sys.exit(1)
print("✅ 무결성 게이트 PASS — 커밋 가능")
