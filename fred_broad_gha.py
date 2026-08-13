#!/usr/bin/env python3
# =====================================================================
# ARGUS — 광범위 FRED 거시지표 수집 (GitHub Actions 프로덕션)
# 출처: argus_fred_broad_extract_colab.py (S225 검증, 셀 일치율 99.91%) 이식
# 변경점(콜랩 대비):
#   1) FRED_API_KEY = os.environ (GHA Secret) — 하드코딩 제거
#   2) in-script pip 제거 — 의존성은 워크플로(fred_broad.yml)가 설치
#   3) 10% 초과실패 시 중단(abort) — 산출/커밋 차단(API 장애 보호)
#   4) 일시 네트워크 오류 재시도(전송 실패 → 거짓 abort 방지)
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
