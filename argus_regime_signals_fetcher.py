#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGUS 비자본 선행·레짐 신호 일일 누적 페처 v2 (S230, FRED API 직접)
===================================================================
목적: §40v3 자본 NO-GO이나 '선행지표로 의미 있는' Regime Tag 신호(ARGUS SIGNAL
      SSOT v1.0)를 매 영업일 1행 누적 저장 -> argus-public-data/argus_regime_signals.csv.
      자본 배분 금지 — 레짐 모니터링·audit·브리핑 컨텍스트 용도.

[v2 근본 수정] fred_broad.csv 위치 의존 제거 (v1은 404 — public 레포에 부재).
   필요한 7개 FRED 시리즈를 FRED API에서 직접 페치 (자체완결). FRED_API_KEY 시크릿 사용.
   로컬 fred_broad.csv가 있으면(LOCAL_FRED_CSV) 그것 우선 — API 호출 회피.

소스:
  - FRED API     : DEXKOUS·WALCL·M2REAL·JTSJOL·RRSFS·PERMIT·IPG3344S (또는 LOCAL_FRED_CSV)
  - argus_data.csv : WTI·MOVE (argus-public-data 루트, LOCAL_DATA_CSV 우선)

수록 신호 (Regime Tag SSOT v1.0):
  SIG-A1 USD_KRW(DEXKOUS)        -> SMH/SLV  (z>0.5 = KRW_WEAK)
  SIG-A2 US유동성(WALCL/M2REAL/JTSJOL/RRSFS) -> CQQQ 역풍 (composite z<-0.5 or chg60<0 = LIQ_CONTRACTION)
  SIG-A3 주택(PERMIT yoy)         -> PAVE     (yoy 하위30% = HOUSING_BUST)
  SIG-B1 반도체생산(IPG3344S yoy) -> SMH      (yoy 하위30% = SEMI_TROUGH)
  SIG-B2 WTI∩MOVE                -> EWZ 회복환경 (WTI<70 ∩ MOVE 60d 하락 = EWZ_RECOVERY)
  (TIER C IRON_ORE/COT = alt-data 확장 슬롯)

특성: 멱등 upsert · 컬럼 합집합 · raw+파생(z/yoy/pct)+상태 플래그 동시 저장 · 신선도 가드(exit 3).

env: FRED_API_KEY(필수, 단 LOCAL_FRED_CSV 제공 시 불요) / REGIME_CSV / LOCAL_FRED_CSV /
     LOCAL_DATA_CSV / FRESHNESS_DAYS / FRED_START
"""
import os
import io
import sys
import json
import urllib.request
import urllib.parse
import numpy as np
import pandas as pd

PUBLIC_BASE = "https://raw.githubusercontent.com/daifulee/argus-public-data/main"
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
UA = {"User-Agent": "ARGUS-RegimeSignals/2.0 (+https://github.com/daifulee/argus-public-data)"}
OUT_CSV = os.environ.get("REGIME_CSV", "argus_regime_signals.csv")
FRESHNESS_DAYS = int(os.environ.get("FRESHNESS_DAYS", "7"))
FRED_START = os.environ.get("FRED_START", "2005-01-01")
FRED_SERIES = ["DEXKOUS", "WALCL", "M2REAL", "JTSJOL", "RRSFS", "PERMIT", "IPG3344S"]


def fetch_fred(series_ids, api_key, start=FRED_START):
    """FRED API에서 시리즈들을 페치 -> 영업일 인덱스 ffill DataFrame (컬럼=series_id)."""
    frames = {}
    for sid in series_ids:
        q = urllib.parse.urlencode({
            "series_id": sid, "api_key": api_key,
            "file_type": "json", "observation_start": start,
        })
        req = urllib.request.Request(f"{FRED_BASE}?{q}", headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r:
            obs = json.loads(r.read().decode()).get("observations", [])
        data = {}
        for o in obs:
            v = o.get("value", ".")
            try:
                data[pd.Timestamp(o["date"])] = float(v) if v not in (".", "") else np.nan
            except (ValueError, KeyError):
                continue
        frames[sid] = pd.Series(data)
    df = pd.DataFrame(frames).sort_index()
    if df.empty:
        raise RuntimeError("FRED 페치 결과 공백 — API 키/시리즈 확인")
    bidx = pd.bdate_range(df.index.min(), df.index.max())
    return df.reindex(bidx).ffill()


def read_fred():
    """LOCAL_FRED_CSV 있으면 우선, 없으면 FRED API 직접 페치."""
    local = os.environ.get("LOCAL_FRED_CSV", "")
    if local and os.path.exists(local):
        df = pd.read_csv(local)
        dc = "Date" if "Date" in df.columns else df.columns[0]
        df[dc] = pd.to_datetime(df[dc])
        return df.set_index(dc).sort_index()
    key = os.environ.get("FRED_API_KEY", "")
    if not key:
        raise RuntimeError(
            "FRED_API_KEY 미설정 + LOCAL_FRED_CSV 부재. "
            "워크플로 env 에 FRED_API_KEY 시크릿을 전달하거나 LOCAL_FRED_CSV 경로 지정."
        )
    return fetch_fred(FRED_SERIES, key)


def read_data():
    """argus_data.csv — LOCAL_DATA_CSV 우선, 없으면 PUBLIC fetch."""
    local = os.environ.get("LOCAL_DATA_CSV", "")
    if local and os.path.exists(local):
        df = pd.read_csv(local)
    else:
        req = urllib.request.Request(f"{PUBLIC_BASE}/argus_data.csv", headers=UA)
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
    """fred + argus_data -> Regime 신호 시계열(일별)."""
    out = pd.DataFrame(index=fred.index)

    if "DEXKOUS" in fred.columns:
        krw = fred["DEXKOUS"].ffill()
        out["USD_KRW"] = krw
        out["USD_KRW_z"] = _z(krw)
        out["KRW_WEAK"] = (out["USD_KRW_z"] > 0.5).astype("Int64")

    liq_cols = [c for c in ["WALCL", "M2REAL", "JTSJOL", "RRSFS"] if c in fred.columns]
    if liq_cols:
        zmat = pd.concat([_z(fred[c].ffill()) for c in liq_cols], axis=1)
        comp = zmat.mean(axis=1)
        out["US_LIQ_z"] = comp
        out["US_LIQ_chg60"] = comp.diff(60)
        out["LIQ_CONTRACTION"] = ((comp < -0.5) | (out["US_LIQ_chg60"] < 0)).astype("Int64")

    if "PERMIT" in fred.columns:
        permit = fred["PERMIT"].ffill()
        out["PERMIT"] = permit
        out["PERMIT_yoy"] = permit.pct_change(252)
        out["PERMIT_yoy_pct"] = _pct_rank(out["PERMIT_yoy"])
        out["HOUSING_BUST"] = (out["PERMIT_yoy_pct"] < 0.30).astype("Int64")

    if "IPG3344S" in fred.columns:
        ipg = fred["IPG3344S"].ffill()
        out["IPG3344S"] = ipg
        out["IPG3344S_yoy"] = ipg.pct_change(252)
        out["IPG3344S_yoy_pct"] = _pct_rank(out["IPG3344S_yoy"])
        out["SEMI_TROUGH"] = (out["IPG3344S_yoy_pct"] < 0.30).astype("Int64")

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
    fred = read_fred()
    data = read_data()
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
