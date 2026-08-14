#!/usr/bin/env python3
# =====================================================================
# ARGUS — 광범위 FRED 거시지표 수집 (GitHub Actions 프로덕션)
# 출처: argus_fred_broad_extract_colab.py (S225 검증, 셀 일치율 99.91%) 이식
# 변경점(콜랩 대비):
#   1) FRED_API_KEY = os.environ (GHA Secret) — 하드코딩 제거
#   2) in-script pip 제거 — 의존성은 워크플로(fred_broad.yml)가 설치
#   3) 10% 초과실패 시 중단(abort) — 산출/커밋 차단(API 장애 보호)
#   4) 일시 네트워크 오류 재시도(전송 실패 → 거짓 abort 방지)
# 🦅 v3.3 (2026-08-14, S288): GPR URL 공식 경로 우선 해석. 제작자 페이지는 날짜 포함 파일명만
#      링크하며, 쓰던 날짜 없는 URL 은 비공식이라 예고 없이 사라질 수 있다. 일간 데이터는 매주
#      월요일 갱신이므로 최근 월요일부터 6주 역순으로 (xls, dta) 를 훑고, 전부 실패해야 비공식
#      URL 을 마지막으로 시도한다. 성공 경로를 매 실행 로그에 명시.
# 🦅 v3.2 (2026-08-14, S288): GPR 포맷 2경로 — xls(xlrd) 실패 시 dta(pandas 내장)로 폴백.
#      xlrd 를 requirements 에 넣으면 ①로, 넣지 않아도 ②로 동작한다. 경로를 로그에 명시.
# 🦅 v3.1 (2026-08-14, S288): GPR 수집 실패 원인 표면화 — 실행 로그가 'ImportError' 만 찍어
#      원인을 알 수 없었다. engine='xlrd' 명시 + 의존성 부재 시 처방 문구 + 예외 메시지 전문 출력.
#      전제: requirements.txt 에 xlrd>=2.0.1 추가 필요(.xls 구형 BIFF 는 xlrd 전용).
# 🦅 v3 (2026-08-13, S288 CAND-EWZ_GPR_SIZING):
#   7) GPRD 계열 추가 — Caldara-Iacoviello 지정학 리스크 지수 (일간 1985+, 비FRED xls).
#      EBP 선례 준용: urllib 회수 · 실패해도 FRED 산출 계속 · abort 계산 제외.
#   8) 🚨 GPR_HIGH 를 **여기서** 산출한다 (소비층 재계산 금지).
#      이유: GPR_HIGH = MA30 > 확장 q90(min 500)인데, argus_data.csv 는 414행뿐이라
#      fetcher 에서 계산하면 min_periods 미달로 영구 침묵한다. 또 fetcher 는 영업일
#      그리드라 rolling(30)이 30영업일(≈42달력일)이 되어 연구 정의와 어긋난다.
#      원본 달력 그리드 + 40년 이력이 있는 이 지점이 유일하게 옳은 계산 위치다.
# 🦅 v2 (2026-08-13, S288 DIR-S288_DATA_SUPPLY_SSOT):
#   5) THREEFYTP10 추가 — ACM 10년 기간프리미엄 (신규 카테고리 "기간프리미엄")
#   6) EBP·GZ_SPREAD 추가 — Gilchrist–Zakrajšek (연준 노트 CSV, 비FRED).
#      표준 라이브러리(urllib)만 사용 → 의존성·워크플로 무변경.
#      실패해도 FRED 산출은 계속(부분 실패 허용·침묵 금지) · abort 계산에서 제외.
# 산출: argus_fred_broad.csv (FRED 110지표 + EBP 계열) + argus_fred_meta.csv
# 주석: 한국어. 저빈도(월간 등)는 영업일 그리드 ffill.
# =====================================================================
import io
import os
import sys
import time
import urllib.request

import numpy as np
import pandas as pd
from fredapi import Fred

# --- 0) 설정 상수 ---
START = "2006-01-01"          # ARGUS BT 시작(2007) 대비 여유 1년
SLEEP = 0.12                  # FRED rate-limit 여유 (검증값)
RETRY = 3                     # 비-단종 시리즈 전송 오류 재시도 횟수
ABORT_FRAC = 0.10             # 예상가능 시리즈의 10% 초과 실패 시 중단
OUT_BROAD = "argus_fred_broad.csv"
OUT_META = "argus_fred_meta.csv"
EBP_URL = "https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv"
# 🆕 v3: GPR daily (Caldara-Iacoviello 2022 AER) — 1985+ 일간 무료 공개
GPR_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"
# 🆕 v3.2: 무의존성 대체 경로 — pandas.read_stata 는 내장이라 xlrd 설치가 불필요하다
GPR_DTA_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.dta"
GPR_BASE = "https://www.matteoiacoviello.com/gpr_files/"
GPR_LOOKBACK_WEEKS = 6   # 일간 GPR 은 매주 월요일 갱신 — 6주 역순 탐색 후 비공식 URL 폴백
GPR_MA = 30        # 이동평균 창 (달력일 — 원본 그리드 기준)
GPR_Q = 0.90       # 고조 판정 분위
GPR_MINP = 500     # 확장 분위 최소 표본

# --- 1) 추출 대상 시리즈 (검증된 111종 + v2 기간프리미엄 1종, 카테고리별) ---
#   ARGUS 유니버스(반도체/원전/구리/금은/EM/기술/방산/유틸/금융/에너지) driver 망라
SERIES = {
    "금리_명목":   ["DGS1MO", "DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30"],
    "금리_실질":   ["DFII5", "DFII7", "DFII10", "DFII20", "DFII30"],
    "정책금리":    ["FEDFUNDS", "DFF", "DFEDTARU", "DFEDTARL"],
    "수익률커브":  ["T10Y2Y", "T10Y3M", "T5YFF"],
    "기간프리미엄": ["THREEFYTP10"],   # 🆕 v2 — ACM 10년 기간프리미엄 (NY Fed, FRED 경유)
    "기대인플레":  ["T5YIE", "T7YIE", "T10YIE", "T5YIFR", "T20YIEM"],
    "물가":        ["CPIAUCSL", "CPILFESL", "PCEPI", "PCEPILFE", "PPIACO", "PPIFIS"],
    "신용스프레드": ["BAMLH0A0HYM2", "BAMLC0A0CM", "BAMLC0A4CBBB", "BAMLH0A3HYC", "BAMLEMCBPIOAS", "BAMLC0A1CAAA"],
    "통화유동성":  ["M1SL", "M2SL", "M2REAL", "WALCL", "WRESBAL", "RRPONTSYD", "WTREGEN", "BOGMBASE", "TOTRESNS"],
    "금융여건":    ["NFCI", "ANFCI", "STLFSI4", "NFCICREDIT", "NFCILEVERAGE", "NFCIRISK"],
    "환율":        ["DTWEXBGS", "DTWEXAFEGS", "DEXUSEU", "DEXJPUS", "DEXKOUS", "DEXCHUS", "DEXUSUK",
                    "DEXCAUS", "DEXMXUS", "DEXBZUS", "DEXINUS", "DEXTAUS", "DEXSDUS", "DEXSIUS"],
    "활동생산":    ["INDPRO", "IPMAN", "IPG3344S", "TCU", "MCUMFN"],
    "주문투자":    ["NEWORDER", "DGORDER", "AMTMNO", "ACOGNO", "BUSINV", "ISRATIO"],
    "소비소매":    ["RSAFS", "RRSFS", "PCE", "DSPIC96"],
    "노동":        ["ICSA", "CCSA", "PAYEMS", "UNRATE", "SAHMCURRENT", "SAHMREALTIME", "JTSJOL", "AWHMAN"],
    "심리선행":    ["UMCSENT", "USSLIND", "USALOLITONOSTSAM"],
    "주택":        ["HOUST", "PERMIT", "MORTGAGE30US", "CSUSHPINSA", "MSACSR"],
    "변동성":      ["VIXCLS", "OVXCLS", "VXNCLS", "GVZCLS"],
    "원자재":      ["DCOILWTICO", "DCOILBRENTEU", "GOLDAMGBD228NLBM", "PCOPPUSDM", "DHHNGSP",
                    "PALUMUSDM", "PNICKUSDM"],
}

# --- 2) 단종 시리즈(상시 실패) — 10% abort 계산에서 제외 ---
#   S225 실측: 아래 2종은 FRED API 미존재(단종) → 항상 실패.
#   기대 성공 = 총 시리즈 - 2 (v2: 112 - 2 = 110).
KNOWN_DEAD = {"GOLDAMGBD228NLBM", "T7YIE"}


def fetch_series(fred, sid):
    """시리즈 1종 추출. 비-단종은 전송 오류 시 재시도, 단종은 1회만 시도."""
    tries = 1 if sid in KNOWN_DEAD else RETRY
    last_exc = None
    for t in range(tries):
        try:
            s = fred.get_series(sid, observation_start=START)
            s = s[~s.index.duplicated(keep="last")].sort_index()
            return s
        except Exception as e:  # noqa: BLE001 — 전송/존재 오류 모두 포착
            last_exc = e
            if t < tries - 1:
                time.sleep(1.5 * (t + 1))  # 점증 backoff
    raise last_exc


def fetch_ebp():
    """🆕 v2: EBP·GZ 스프레드 (연준 노트 월간 CSV, 비FRED).

    표준 라이브러리만 사용 — 의존성·워크플로 무변경.
    반환: {이름: Series}. 실패 시 빈 dict (FRED 산출은 계속 · abort 미포함).
    """
    out = {}
    try:
        req = urllib.request.Request(
            EBP_URL, headers={"User-Agent": "ARGUS-fetcher/2.0 (+github.com/daifulee/argus-public-data)"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        d = pd.read_csv(io.StringIO(raw))
        dc = next(c for c in d.columns if "date" in c.lower())
        d[dc] = pd.to_datetime(d[dc])
        d = d.set_index(dc).sort_index()
        for col, name in [("ebp", "EBP"), ("gz_spread", "GZ_SPREAD")]:
            hit = [c for c in d.columns if c.lower() == col]
            if hit:
                s = pd.to_numeric(d[hit[0]], errors="coerce").dropna()
                s = s[s.index >= START]
                s = s[~s.index.duplicated(keep="last")].sort_index()
                if len(s):
                    out[name] = s
    except Exception as e:  # noqa: BLE001
        print(f"  [EBP] ❌ 연준 노트 CSV 실패: {type(e).__name__} — FRED 산출 계속", file=sys.stderr)
    return out


def _gpr_candidates(today=None):
    """🆕 v3.3: GPR 다운로드 후보 URL 목록 — 공식(날짜 포함) 우선 · 비공식(날짜 없음) 최후.

    제작자 페이지는 `data_gpr_daily_recent_YYYYMMDD.(xls|dta)` 만 링크한다.
    현재 쓰던 날짜 없는 URL 은 서버에 실재하나 **페이지에 없는 비공식 경로**라
    예고 없이 사라질 수 있다 → 공식 경로를 먼저 시도한다.

    일간 데이터는 **매주 월요일** 갱신되므로 최근 월요일부터 역순으로 훑는다.
    6주까지 거슬러도 없으면 원천이 멈춘 것이므로 비공식 URL 로 마지막 시도.
    """
    from datetime import date, timedelta
    d0 = today or date.today()
    mon = d0 - timedelta(days=d0.weekday())      # 이번 주 월요일
    out = []
    for k in range(GPR_LOOKBACK_WEEKS):
        tag = (mon - timedelta(weeks=k)).strftime("%Y%m%d")
        out.append((f"{GPR_BASE}data_gpr_daily_recent_{tag}.xls", "xls", f"공식 {tag}"))
        out.append((f"{GPR_BASE}data_gpr_daily_recent_{tag}.dta", "dta", f"공식 {tag}"))
    out.append((GPR_URL, "xls", "비공식(날짜없음)"))
    out.append((GPR_DTA_URL, "dta", "비공식(날짜없음)"))
    return out


def _gpr_load():
    """후보 URL 을 순서대로 시도해 (DataFrame, 경로설명) 반환. 전부 실패 시 예외.

    포맷 2종: .xls 는 xlrd 필요 · .dta 는 pandas 내장(무의존성).
    xlrd 미설치 환경에서도 .dta 로 살아남는다. 어느 경로로 성공했는지 반드시 로그에 남긴다.
    """
    _hdr = {"User-Agent": "ARGUS-fetcher/3.3 (+github.com/daifulee/argus-public-data)"}
    errs = []
    for url, kind, label in _gpr_candidates():
        try:
            req = urllib.request.Request(url, headers=_hdr)
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            df = (pd.read_excel(io.BytesIO(raw), engine="xlrd") if kind == "xls"
                  else pd.read_stata(io.BytesIO(raw)))
            print(f"  [GPR] 회수 경로 = {label} / {kind} ({len(raw):,}B, {len(df)}행)")
            if errs:
                print(f"  [GPR] ↳ 앞선 시도 {len(errs)}건 실패 (첫 사유 {errs[0]})")
            return df, f"{label}/{kind}"
        except Exception as e:  # noqa: BLE001
            errs.append(f"{label}/{kind}: {type(e).__name__}")
    raise RuntimeError(
        "GPR 전 경로 실패 — 시도 " + str(len(errs)) + "건. 사유 예: "
        + " · ".join(errs[:4])
        + " | .xls 계열이 ImportError 면 requirements.txt 에 xlrd>=2.0.1 을 추가하십시오."
    )



def fetch_gpr():
    """🆕 v3: GPRD 지정학 리스크 지수 + GPR_HIGH 플래그 (일간 · 비FRED xls).

    🚨 GPR_HIGH 를 이 함수에서 산출하는 이유 — 소비층(fetcher)에서 계산하면 두 가지가 깨진다.
       ① argus_data.csv 는 수백 행뿐이라 확장 분위(min 500) 가 영구 미성립 → 신호 침묵.
       ② fetcher 는 영업일 그리드라 rolling(30) 이 30영업일(≈42달력일)로 정의가 바뀐다.
       원본 달력 그리드 + 1985년부터의 전체 이력이 있는 여기가 유일하게 옳은 계산 위치다.

    GPR_HIGH = GPRD_MA30 > 확장 q90(min 500) — 확장 분위라 look-ahead 없음(PIT 안전).
    반환: {이름: Series} · 실패 시 빈 dict (FRED 산출 계속 · abort 계산 제외).
    """
    out = {}
    try:
        # 🔴 v3.2: 포맷 2경로. 원천은 하나(Caldara-Iacoviello)이고 배포 포맷만 둘이다.
        #   ① .xls  — xlrd 필요. GHA 에 없으면 ImportError (실사고 2026-08-14).
        #   ② .dta  — pandas 내장 read_stata. 추가 의존성 없음.
        #   ①이 의존성 문제로 실패하면 ②로 넘어간다. 어느 경로로 성공했는지 로그에 남긴다.
        #   다운로드 자체는 이미 성공이 증명됐다(실패 지점이 파싱 단계였다).
        d, _via = _gpr_load()
        dc = next(c for c in d.columns if str(c).lower() == "date")
        d[dc] = pd.to_datetime(d[dc], errors="coerce")
        d = d.dropna(subset=[dc])
        d = d[~d[dc].duplicated(keep="last")].set_index(dc).sort_index()

        gcol = next((c for c in d.columns if str(c).upper() == "GPRD"), None)
        if gcol is None:
            raise KeyError("GPRD 컬럼 부재")
        gprd = pd.to_numeric(d[gcol], errors="coerce").ffill()

        # MA30 — 파일이 제공하면 그대로(연구 정의와 동일), 없으면 원본 그리드에서 산출
        mcol = next((c for c in d.columns if str(c).upper() == "GPRD_MA30"), None)
        ma30 = pd.to_numeric(d[mcol], errors="coerce") if mcol else \
            gprd.rolling(GPR_MA, min_periods=10).mean()

        q = ma30.expanding(min_periods=GPR_MINP).quantile(GPR_Q)
        high = (ma30 > q).astype(float)

        for name, s in [("GPRD", gprd), ("GPRD_MA30", ma30), ("GPR_HIGH", high)]:
            s = s.dropna()
            s = s[s.index >= START]
            if len(s):
                out[name] = s
        for extra in ["GPRD_ACT", "GPRD_THREAT"]:
            hit = next((c for c in d.columns if str(c).upper() == extra), None)
            if hit:
                s = pd.to_numeric(d[hit], errors="coerce").dropna()
                s = s[s.index >= START]
                if len(s):
                    out[extra] = s
    except Exception as e:  # noqa: BLE001
        # 🔴 v3.1: 예외 종류만 찍으면 원인을 알 수 없다(실사고: ImportError 만 보고 원인 불명).
        #   메시지 전문을 남긴다 — fail-safe 는 원인을 감추지 않는다(원칙 I).
        print(f"  [GPR] ❌ GPR 수집 실패: {type(e).__name__}: {e} — FRED 산출 계속", file=sys.stderr)
    return out


def main():
    # --- FRED 키 확인 (없으면 즉시 실패 — 빈 산출/커밋 방지) ---
    api_key = os.environ.get("FRED_API_KEY", "").strip()
    if not api_key:
        print("❌ FRED_API_KEY 환경변수 부재 — GHA Secret 등록 필요. 중단.", file=sys.stderr)
        sys.exit(1)

    fred = Fred(api_key=api_key)

    flat = [(cat, sid) for cat, ids in SERIES.items() for sid in ids]
    attempted = len(flat)
    expected_ok = attempted - len(KNOWN_DEAD)
    print(f"총 {attempted}개 시리즈 추출 시작 (기대 성공 {expected_ok}, 단종 {len(KNOWN_DEAD)})...\n")

    all_series = {}
    meta_rows = []
    failed = []

    for k, (cat, sid) in enumerate(flat, 1):
        try:
            s = fetch_series(fred, sid)
            if s is None or len(s) == 0:
                raise ValueError("빈 시리즈")
            all_series[sid] = s
            # 발표 빈도 추정 (관측 간격 중앙값)
            if len(s) > 5:
                gap = int(np.median(np.diff(s.index.values).astype("timedelta64[D]").astype(int)))
            else:
                gap = np.nan
            freq = "일간" if (not np.isnan(gap) and gap <= 4) else \
                   ("주간" if (not np.isnan(gap) and gap <= 10) else
                    ("월간" if (not np.isnan(gap) and gap <= 40) else "분기+"))
            meta_rows.append({"series": sid, "category": cat, "n_obs": len(s),
                              "start": str(s.index.min().date()) if len(s) else "",
                              "end": str(s.index.max().date()) if len(s) else "",
                              "freq": freq, "gap_days": gap})
            print(f"  [{k:3d}/{attempted}] ✅ {sid:18s} {cat:10s} n={len(s):5d} {freq}")
        except Exception as e:  # noqa: BLE001
            failed.append(sid)
            meta_rows.append({"series": sid, "category": cat, "n_obs": 0,
                              "start": "", "end": "", "freq": "FAIL", "gap_days": np.nan})
            tag = "단종(예상)" if sid in KNOWN_DEAD else "실패(비예상)"
            print(f"  [{k:3d}/{attempted}] ❌ {sid:18s} {cat:10s} {tag}: {type(e).__name__}")
        time.sleep(SLEEP)

    # --- 2b) 🆕 v2: EBP 계열 수집 (비FRED · abort 미포함 · 실패 허용) ---
    # 🆕 v3: GPR 병합 (EBP 와 동일 규약 — abort 계산 제외)
    gpr_series = fetch_gpr()
    for name, s in gpr_series.items():
        all_series[name] = s
        meta_rows.append({"series": name, "category": "지정학", "n_obs": len(s),
                          "start": str(s.index.min().date()), "end": str(s.index.max().date()),
                          "freq": "일간", "gap_days": 1})
    if gpr_series:
        _hi = gpr_series.get("GPR_HIGH")
        print(f"  [GPR] ✅ {len(gpr_series)}계열 수집 · GPR_HIGH 발화 "
              f"{int(_hi.sum()) if _hi is not None else 0}/{len(_hi) if _hi is not None else 0}일")
    else:
        meta_rows.append({"series": "GPRD", "category": "지정학", "n_obs": 0, "freq": "FAIL"})

    ebp_series = fetch_ebp()
    for name, s in ebp_series.items():
        all_series[name] = s
        meta_rows.append({"series": name, "category": "신용_EBP", "n_obs": len(s),
                          "start": str(s.index.min().date()), "end": str(s.index.max().date()),
                          "freq": "월간", "gap_days": 30})
        print(f"  [EBP] ✅ {name:18s} 신용_EBP  n={len(s):5d} 월간 (연준 노트)")
    if not ebp_series:
        meta_rows.append({"series": "EBP", "category": "신용_EBP", "n_obs": 0,
                          "start": "", "end": "", "freq": "FAIL", "gap_days": np.nan})

    # --- 3) 10% 초과실패 abort 판정 (단종·EBP 제외) ---
    unexpected = [s for s in failed if s not in KNOWN_DEAD]
    ok_count = len(all_series)
    print("\n----- 수집 요약 -----")
    print(f"성공 {ok_count}/{attempted}+EBP{len(ebp_series)} (기대 {expected_ok}) / 비예상 실패 {len(unexpected)}")
    if unexpected:
        print(f"비예상 실패 목록: {unexpected}")
    missing_dead = [s for s in KNOWN_DEAD if s in all_series]
    if missing_dead:
        print(f"ℹ️ 단종 표기 시리즈가 복구됨(검토 필요): {missing_dead}")

    if len(unexpected) > expected_ok * ABORT_FRAC:
        print(f"\n🛑 ABORT: 비예상 실패 {len(unexpected)} > 임계 {expected_ok * ABORT_FRAC:.1f} "
              f"({ABORT_FRAC:.0%} of {expected_ok}). 산출/커밋 차단.", file=sys.stderr)
        sys.exit(2)

    # --- 4) 영업일 그리드 정렬 + ffill (저빈도 발표 보정) ---
    #   조립은 pd.concat(axis=1) 일괄 — 컬럼 루프 삽입(DataFrame 단편화) 회피.
    #   각 시리즈를 동일 idx로 reindex·ffill 후 concat → 컬럼 순서·값 루프본과 동일.
    idx = pd.bdate_range(START, pd.Timestamp.today().normalize())
    cols = {}
    for sid, s in all_series.items():  # dict 순서 = SERIES 정의 순서 보존 (EBP 계열은 말미)
        cols[sid] = s.reindex(idx.union(s.index)).sort_index().ffill().reindex(idx)
    df = pd.concat(cols, axis=1) if cols else pd.DataFrame(index=idx)
    df.index = idx
    df.index.name = "Date"

    # --- 5) 저장 ---
    df.to_csv(OUT_BROAD)
    pd.DataFrame(meta_rows).to_csv(OUT_META, index=False)

    print(f"\n===== 완료 =====")
    print(f"산출 {OUT_BROAD}: {df.shape[0]}행 × {df.shape[1]}열")
    print(f"기간 {df.index.min().date()} ~ {df.index.max().date()}")
    print(f"메타 {OUT_META}: {len(meta_rows)}행")
    sys.exit(0)


if __name__ == "__main__":
    main()
