#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGUS 비자본 선행·레짐 신호 일일 누적 페처 (S230 신설)
===================================================================
목적: §40v3 자본 NO-GO이나 '선행지표로 의미 있는' Regime Tag 신호(ARGUS SIGNAL
      SSOT v1.0)를 매 영업일 1행 누적 저장 -> argus-public-data/argus_regime_signals.csv.
      자본 배분 금지 (전 항목 자본 무효) — 레짐 모니터링·audit 트리거·브리핑 컨텍스트 용도.

소스 (중복 FRED 호출 없음 — 기존 일일 산출물 재사용):
  - fred_broad.csv  : DEXKOUS·WALCL·M2REAL·JTSJOL·RRSFS·PERMIT·IPG3344S
  - argus_data.csv  : WTI·MOVE

수록 신호 (Regime Tag SSOT v1.0):
  SIG-A1 USD_KRW(DEXKOUS)        -> SMH/SLV 레짐  (z>0.5 = KRW_WEAK)
  SIG-A2 US유동성(WALCL/M2REAL/JTSJOL/RRSFS) -> CQQQ 역풍 (composite z<-0.5 = LIQ_CONTRACTION)
  SIG-A3 주택(PERMIT yoy)         -> PAVE 사이클 (yoy 하위30% = HOUSING_BUST)
  SIG-B1 반도체생산(IPG3344S yoy) -> SMH 사이클  (yoy 하위30% = SEMI_TROUGH)
  SIG-B2 WTI∩MOVE                -> EWZ 회복환경 (WTI<70 ∩ MOVE 60d 하락 = EWZ_RECOVERY)
  (TIER C IRON_ORE/COT = alt-data 확장 슬롯 — 별도 소싱 시 확장)

특성: 멱등 upsert(같은 Date 교체) · 컬럼 합집합 · raw 값 + 파생(z/yoy/pct) + 상태 플래그 동시 저장
      -> 후속 분석에서 임계·정의 변경에도 재현 가능. 자본 게이트(§40v3) 불변.

env: REGIME_CSV / LOCAL_FRED_CSV / LOCAL_DATA_CSV / FRESHNESS_DAYS
"""
import os
import io
import sys
import urllib.request
import numpy as np
import pandas as pd

PUBLIC_BASE = "https://raw.githubusercontent.com/daifulee/argus-public-data/main"
UA = {"User-Agent": "ARGUS-RegimeSignals/1.0 (+https://github.com/daifulee/argus-public-data)"}
OUT_CSV = os.environ.get("REGIME_CSV", "argus_regime_signals.csv")
FRESHNESS_DAYS = int(os.environ.get("FRESHNESS_DAYS", "7"))


def _read(name_or_url, local_env):
    """로컬(env 지정) 우선 -> PUBLIC fetch. Date 인덱스 일별 정렬 반환."""
    local = os.environ.get(local_env, "")
    if local and os.path.exists(local):
        df = pd.read_csv(local)
    else:
        url = f"{PUBLIC_BASE}/{name_or_url}"
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r:
            df = pd.read_csv(io.StringIO(r.read().decode()))
    dc = "Date" if "Date" in df.columns else df.columns[0]
    df[dc] = pd.to_datetime(df[dc])
    return df.set_index(dc).sort_index()


def _z(s, win=252, mp=120):
    return (s - s.rolling(win, min_periods=mp).mean()) / s.rolling(win, min_periods=mp).std()


def _pct_rank(s, win=1260, mp=252):
    """rolling 백분위(0~1) — 최근값이 과거 win일 중 몇 퍼센타일인지."""
    return s.rolling(win, min_periods=mp).apply(lambda x: (x.iloc[-1] >= x).mean(), raw=False)


def compute_signals(fred, data):
    """fred_broad + argus_data -> Regime 신호 시계열(일별)."""
    out = pd.DataFrame(index=fred.index)

    # SIG-A1 USD_KRW (DEXKOUS)
    krw = fred["DEXKOUS"].ffill()
    out["USD_KRW"] = krw
    out["USD_KRW_z"] = _z(krw)
    out["KRW_WEAK"] = (out["USD_KRW_z"] > 0.5).astype("Int64")

    # SIG-A2 US유동성 클러스터 (WALCL/M2REAL/JTSJOL/RRSFS)
    liq_cols = ["WALCL", "M2REAL", "JTSJOL", "RRSFS"]
    have = [c for c in liq_cols if c in fred.columns]
    if have:
        zmat = pd.concat([_z(fred[c].ffill()) for c in have], axis=1)
        comp = zmat.mean(axis=1)
        out["US_LIQ_z"] = comp
        out["US_LIQ_chg60"] = comp.diff(60)
        out["LIQ_CONTRACTION"] = ((comp < -0.5) | (out["US_LIQ_chg60"] < 0)).astype("Int64")

    # SIG-A3 주택 (PERMIT yoy)
    if "PERMIT" in fred.columns:
        permit = fred["PERMIT"].ffill()
        out["PERMIT"] = permit
        out["PERMIT_yoy"] = permit.pct_change(252)
        out["PERMIT_yoy_pct"] = _pct_rank(out["PERMIT_yoy"])
        out["HOUSING_BUST"] = (out["PERMIT_yoy_pct"] < 0.30).astype("Int64")

    # SIG-B1 반도체생산 (IPG3344S yoy)
    if "IPG3344S" in fred.columns:
        ipg = fred["IPG3344S"].ffill()
        out["IPG3344S"] = ipg
        out["IPG3344S_yoy"] = ipg.pct_change(252)
        out["IPG3344S_yoy_pct"] = _pct_rank(out["IPG3344S_yoy"])
        out["SEMI_TROUGH"] = (out["IPG3344S_yoy_pct"] < 0.30).astype("Int64")

    # SIG-B2 WTI∩MOVE -> EWZ 회복환경
    if "WTI" in data.columns and "MOVE" in data.columns:
        wti = data["WTI"].reindex(out.index).ffill()
        move = data["MOVE"].reindex(out.index).ffill()
        out["WTI"] = wti
        out["MOVE"] = move
        out["MOVE_chg60"] = move.diff(60)
        out["EWZ_RECOVERY"] = ((wti < 70) & (out["MOVE_chg60"] < 0)).astype("Int64")

    return out


def latest_row(sig):
    """최신 거래일 1행 dict (Date + 신호 값/상태). NaN 제외."""
    last = sig.dropna(how="all").index[-1]
    r = {"Date": last.strftime("%Y-%m-%d")}
    for c in sig.columns:
        v = sig.loc[last, c]
        if pd.isna(v):
            continue
        r[c] = int(v) if str(sig[c].dtype) == "Int64" else round(float(v), 6)
    return r, last


def upsert(path, row):
    """멱등 upsert + 컬럼 합집합."""
    if os.path.exists(path):
        led = pd.read_csv(path)
    else:
        led = pd.DataFrame(columns=["Date"])
    for k in row:
        if k not in led.columns:
            led[k] = np.nan
    led = led[led["Date"] != row["Date"]]
    new = pd.DataFrame([row])
    for c in led.columns:
        if c not in new.columns:
            new[c] = np.nan if c != "Date" else row["Date"]
    led = pd.concat([led, new[led.columns]], ignore_index=True).sort_values("Date").reset_index(drop=True)
    led.to_csv(path, index=False)
    return len(led)


def main():
    fred = _read("fred_broad.csv", "LOCAL_FRED_CSV")
    data = _read("argus_data.csv", "LOCAL_DATA_CSV")
    sig = compute_signals(fred, data)
    row, last = latest_row(sig)

    age = (pd.Timestamp.utcnow().tz_localize(None) - last).days
    if age > FRESHNESS_DAYS:
        print(f"[WARN] 데이터 stale ({age}일 > {FRESHNESS_DAYS}일) — 누적 생략", file=sys.stderr)
        return 3

    n = upsert(OUT_CSV, row)
    flags = {k: v for k, v in row.items() if k in
             ("KRW_WEAK", "LIQ_CONTRACTION", "HOUSING_BUST", "SEMI_TROUGH", "EWZ_RECOVERY")}
    print(f"[OK] regime upsert: {row['Date']} | 활성레짐 {[k for k,v in flags.items() if v==1]} | 총 {n}행 -> {OUT_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
