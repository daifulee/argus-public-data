"""argus_fred_semi_live.py — FRED 반도체 수요 선행신호 라이브 모듈 (S214)

목적: Oracle AI_POWER LEAD-7 활성을 위한 라이브 피드.
  SEMI_REACCEL = (A34SNO_roc3m>0) & (U34SIS_roc3m<0)          # 주문↑ ∩ 재고↓
  CONSUMER_ELEC = (RSEAS_roc3m>0) & (R42343M163SCEN_roc3m<0)  # 소매↑ ∩ 채널재고↓

발표일(pub_lag) PIT: 각 월간 시리즈는 기준월 말일 + pub_lag일에 발행.
  신호 month M = 구성 시리즈 중 max(pub_lag) 경과 후 사용 가능 (look-ahead 차단).
  일간 date D = 발행일 ≤ D 인 최신 month의 신호값 (forward-fill).

자본 중립: LEAD-7은 Oracle 보고 전용, PRIMA 미반영 (frontier 닫힘 7c8ca3d57611).
통합: argus_data_fetcher.py의 fetch_today_row(today_row) + build_seed(이력)에서 호출.
"""
import io
import time
import datetime as _dt
import urllib.request
import pandas as pd
import numpy as np

# LEAD-7 v0.1 최소 시리즈 (검증 신호 SEMI_REACCEL/CONSUMER_ELEC 전용)
SEMI_SERIES = {
    "A34SNO":         35,   # 전자제품 신규주문 (SEMI_REACCEL 주문)
    "U34SIS":         35,   # 전자제품 재고/출하비율 (SEMI_REACCEL 재고)
    "RSEAS":          16,   # 전자·가전 소매 advance (CONSUMER_ELEC 소매)
    "R42343M163SCEN": 45,   # 컴퓨터 도매 재고/판매 (CONSUMER_ELEC 채널재고)
}
# 신호별 구성 시리즈 + 발행 가능 시점 = max(구성 pub_lag)
SIGNAL_DEF = {
    "SEMI_REACCEL":  (("A34SNO", "U34SIS"),         35),
    "CONSUMER_ELEC": (("RSEAS", "R42343M163SCEN"),  45),
}


def _fetch_fred_raw(sid: str, start: str, api_key: str = "") -> pd.Series:
    """월간 FRED 시리즈 fetch (API key 우선 + graph CSV anonymous fallback).
    반환: Series(index=월초 Timestamp, value=float). 실패 시 빈 Series.
    """
    # ① FRED API (key 의무)
    if api_key:
        try:
            url = (f"https://api.stlouisfed.org/fred/series/observations"
                   f"?series_id={sid}&observation_start={start}"
                   f"&api_key={api_key}&file_type=json&sort_order=asc")
            with urllib.request.urlopen(url, timeout=30) as r:
                import json
                obs = json.loads(r.read().decode())["observations"]
            idx, val = [], []
            for o in obs:
                if o["value"] in (".", ""):
                    continue
                idx.append(pd.Timestamp(o["date"])); val.append(float(o["value"]))
            if val:
                return pd.Series(val, index=idx, name=sid)
        except Exception:
            pass
    # ② graph CSV anonymous fallback
    try:
        url_csv = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        with urllib.request.urlopen(url_csv, timeout=30) as r:
            df = pd.read_csv(io.BytesIO(r.read()))
        df.columns = ["date", "value"]
        df = df[df["value"] != "."]
        df["date"] = pd.to_datetime(df["date"]); df["value"] = df["value"].astype(float)
        return pd.Series(df["value"].values, index=df["date"].values, name=sid)
    except Exception:
        return pd.Series(dtype=float, name=sid)


def _avail_date(obs_month: pd.Timestamp, pub_lag: int) -> pd.Timestamp:
    """기준월 obs(월초) → 발행 가능일 = 월말 + pub_lag일."""
    month_end = (obs_month + pd.offsets.MonthEnd(0))
    return month_end + pd.Timedelta(days=pub_lag)


def compute_semi_signals(start_iso: str, today, api_key: str = "") -> pd.DataFrame:
    """4개 시리즈 fetch → roc3m → SEMI_REACCEL/CONSUMER_ELEC → pub_lag PIT → 일간 ffill.

    Args:
        start_iso: 이력 시작 (예: "2006-01-01")
        today:     기준일 (str 또는 date/Timestamp) — 이 날짜까지의 일간 신호 반환
        api_key:   FRED_API_KEY (GHA secret). 부재 시 graph CSV fallback.
    Returns:
        DataFrame(index=일간 Date, columns=[SEMI_REACCEL, CONSUMER_ELEC]).
        데이터 부족 시 해당 컬럼 NaN (Oracle LEAD-7가 DEFAULT 폴백).
    """
    today = pd.Timestamp(today)
    # ① 시리즈 fetch (월간)
    raw = {}
    for sid in SEMI_SERIES:
        s = _fetch_fred_raw(sid, start_iso, api_key)
        if len(s):
            raw[sid] = s.sort_index()
    if not raw:
        # 전체 실패 → 빈 신호 (LEAD-7 DEFAULT 폴백)
        didx = pd.date_range(start_iso, today, freq="D")
        return pd.DataFrame({"SEMI_REACCEL": np.nan, "CONSUMER_ELEC": np.nan}, index=didx)

    # ② 월간 그리드 정렬 + roc3m
    monthly = pd.DataFrame(raw)
    monthly = monthly.resample("MS").last()  # 월초 정렬
    roc = {}
    for sid in monthly.columns:
        roc[f"{sid}_roc3m"] = monthly[sid] / monthly[sid].shift(3) - 1.0

    # ③ 신호 계산 (월간)
    g = lambda k: roc.get(k, pd.Series(np.nan, index=monthly.index))
    sig_m = pd.DataFrame(index=monthly.index)
    sig_m["SEMI_REACCEL"]  = ((g("A34SNO_roc3m") > 0) & (g("U34SIS_roc3m") < 0)).astype(float)
    sig_m["CONSUMER_ELEC"] = ((g("RSEAS_roc3m") > 0) & (g("R42343M163SCEN_roc3m") < 0)).astype(float)
    # roc 미산출(시리즈 부족) month는 NaN 처리
    for col, (comps, _) in SIGNAL_DEF.items():
        miss = pd.Series(False, index=monthly.index)
        for c in comps:
            if f"{c}_roc3m" not in roc:
                miss |= True
            else:
                miss |= roc[f"{c}_roc3m"].isna()
        sig_m.loc[miss, col] = np.nan

    # ④ pub_lag PIT: 각 신호 month M의 발행일 = max(구성 pub_lag)
    avail = {}
    for col, (comps, lag) in SIGNAL_DEF.items():
        avail[col] = pd.Series(
            [_avail_date(m, lag) for m in sig_m.index], index=sig_m.index
        )

    # ⑤ 일간 ffill (date D = 발행일 ≤ D 인 최신 month 신호)
    didx = pd.date_range(start_iso, today, freq="D")
    out = pd.DataFrame(index=didx)
    for col in ["SEMI_REACCEL", "CONSUMER_ELEC"]:
        avail_dates = avail[col].values
        vals = sig_m[col].values
        daily = pd.Series(np.nan, index=didx)
        # 발행일 기준 step 함수 (D 이전 발행된 최신 month 값)
        order = np.argsort(avail_dates)
        ad_sorted = pd.to_datetime(avail_dates[order])
        v_sorted = vals[order]
        pos = np.searchsorted(ad_sorted.values, didx.values, side="right") - 1
        mask = pos >= 0
        daily.iloc[mask] = v_sorted[pos[mask]]
        out[col] = daily.ffill()
    return out


def latest_semi_signals(today, api_key: str = "", start_iso: str = "2006-01-01") -> dict:
    """today_row용: 기준일의 최신 신호값 dict 반환 (PIT). 데이터 부재 시 NaN."""
    df = compute_semi_signals(start_iso, today, api_key)
    if len(df) == 0:
        return {"SEMI_REACCEL": np.nan, "CONSUMER_ELEC": np.nan}
    last = df.iloc[-1]
    return {"SEMI_REACCEL": float(last["SEMI_REACCEL"]) if pd.notna(last["SEMI_REACCEL"]) else np.nan,
            "CONSUMER_ELEC": float(last["CONSUMER_ELEC"]) if pd.notna(last["CONSUMER_ELEC"]) else np.nan}


if __name__ == "__main__":
    import os
    key = os.environ.get("FRED_API_KEY", "")
    sigs = latest_semi_signals(_dt.date.today(), key)
    print("최신 반도체 선행신호:", sigs)
