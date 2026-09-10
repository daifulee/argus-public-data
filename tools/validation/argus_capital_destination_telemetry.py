#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARGUS Capital Destination Telemetry v0.1
========================================

목적
----
PRIMA2 자본 엔진을 수정하지 않고 run_prima4()의 실제 weight 경로를 관측하여
다음 검증 산출물을 생성한다.

1) compute_weights() 호출 전수 기록
2) 거래일별 EOD 확정 비중
3) 실제 다음 거래일 수익에 적용된 비중(applied weight)
4) Position.entry_score 기반 allocation cohort
5) initial allocated weight / exposure days / weight-days / gross P&L
6) 일별 turnover 재구성
7) 두 variant 간 capital destination / weight path / turnover / gross P&L 차분

중요한 정의
-----------
- BUY 로그의 pct=100은 실제 비중이 아니다.
- run_prima4()는 진입 후 compute_weights()를 다시 호출하므로,
  해당 거래일의 마지막 compute_weights() snapshot을 EOD 확정 비중으로 본다.
- EOD(t) 비중은 엔진 실행 순서상 다음 거래일 t+1의 자산수익 계산에 적용된다.
  따라서 applied_weight(t) = EOD_weight(previous trading day)로 재구성한다.
- cohort_id는 ticker + Position.entry_date를 기본 식별자로 사용한다.
- 같은 날짜 다종목 진입은 date_cohort_id로 별도 그룹화해
  "6개 진입일 × 4종목 = 24개 독립 P&L cohort" 같은 오인을 방지한다.

엔진 불변성
-----------
- 엔진 파일을 수정하지 않는다.
- engine.compute_weights를 실행 중에만 observer wrapper로 교체하고 finally에서 복원한다.
- wrapper는 original compute_weights의 반환값을 그대로 반환한다.

사용 예
-------
단일 런:
    python argus_capital_destination_telemetry.py run \
      --engine PRIMA2.py --data BT_LONG.csv --out telemetry_on

variant 설정 모듈 사용:
    python argus_capital_destination_telemetry.py run \
      --engine PRIMA2.py --data BT_LONG.csv \
      --configure c106_off_config.py --out telemetry_off

configure 파일은 아래 인터페이스만 가지면 된다.
    def configure(engine):
        # validation-only monkey patch
        ...

두 런 비교(두 번째 - 첫 번째):
    python argus_capital_destination_telemetry.py compare \
      --first telemetry_on --second telemetry_off --out compare_off_minus_on

Python 3.10+ / pandas / numpy 필요.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import linecache
import math
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

import numpy as np
import pandas as pd


TOOL_VERSION = "0.1.0"
DEFAULT_EPS = 1e-12


# -----------------------------------------------------------------------------
# 기본 유틸리티
# -----------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_default(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return None if math.isnan(v) else v
    if isinstance(obj, (pd.Timestamp, np.datetime64)):
        return str(pd.Timestamp(obj))
    if isinstance(obj, Path):
        return str(obj)
    return str(obj)


def dump_json(path: Path, obj: Any) -> None:
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, default=json_default),
        encoding="utf-8",
    )


def load_py_module(path: Path, prefix: str) -> Any:
    name = f"{prefix}_{hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:12]}"
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"모듈 로드 실패: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # 일반 ARGUS CSV: Date 열
    date_col = None
    for c in ("Date", "date", "DATE"):
        if c in df.columns:
            date_col = c
            break

    if date_col is not None:
        idx = pd.to_datetime(df[date_col], errors="coerce")
        if idx.notna().sum() == 0:
            raise ValueError(f"날짜 열 파싱 실패: {date_col}")
        df = df.drop(columns=[date_col])
        df.index = idx
    elif not isinstance(df.index, pd.DatetimeIndex):
        # 첫 열이 unnamed index/date인 경우 보수적 탐지
        first = df.columns[0]
        parsed = pd.to_datetime(df[first], errors="coerce")
        if parsed.notna().mean() > 0.95:
            df = df.drop(columns=[first])
            df.index = parsed
        else:
            raise ValueError("Date/date 열을 찾지 못했습니다.")

    df = df[~df.index.isna()].copy()
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def price_column_map(engine: Any, df: pd.DataFrame) -> Dict[str, str]:
    out: Dict[str, str] = {}
    tickers = list(getattr(engine, "ALL_TICKERS", []))
    for t in tickers:
        for c in (t, f"{t}_Close"):
            if c in df.columns:
                out[t] = c
                break
    if "QQQM" not in out:
        for c in ("QQQ", "QQQ_Close"):
            if c in df.columns:
                out["QQQM"] = c
                break
    return out


def safe_float(v: Any) -> Optional[float]:
    try:
        x = float(v)
        if math.isfinite(x):
            return x
    except Exception:
        pass
    return None


def normalize_date(v: Any) -> Optional[str]:
    if v is None:
        return None
    try:
        return str(pd.Timestamp(v).date())
    except Exception:
        return str(v)


def position_snapshot(positions: Mapping[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for ticker, p in positions.items():
        entry_date = normalize_date(getattr(p, "entry_date", None))
        row = {
            "ticker": str(ticker),
            "entry_date": entry_date,
            "cohort_id": f"{ticker}|{entry_date}",
            "date_cohort_id": entry_date,
            "entry_price": safe_float(getattr(p, "entry_price", None)),
            "entry_score": safe_float(getattr(p, "entry_score", None)),
            "entry_threshold": safe_float(getattr(p, "entry_threshold", None)),
            "weight_factor": safe_float(getattr(p, "weight_factor", None)),
            "held_days": int(getattr(p, "held_days", 0)),
            "target_days": int(getattr(p, "target_days", 0)),
            "level": str(getattr(p, "level", "N/A")),
        }
        rows.append(row)
    return rows


def classify_compute_phase(engine_path: Path, lineno: int) -> str:
    """소스 줄 주변 문맥으로 compute_weights 호출 위치를 표시용 분류한다.

    결과 계산에는 phase가 사용되지 않는다. EOD는 같은 날짜의 마지막 snapshot을
    사용하므로 line-number 분류 실패가 자본 결과를 바꾸지 않는다.
    """
    lo = max(1, lineno - 4)
    hi = lineno + 2
    ctx = "\n".join(linecache.getline(str(engine_path), i) for i in range(lo, hi + 1))
    if "if new_tickers" in ctx or "new_tickers:" in ctx:
        return "POST_ENTRY"
    if "RESCUE" in ctx or "_rtk" in ctx:
        return "POST_RESCUE"
    if "wts_changed" in ctx:
        return "POST_EXIT"
    if "elif pos" in ctx or "매일 동적 비중" in ctx:
        return "DAILY_REWEIGHT"
    if "final_weights" in ctx:
        return "FINAL_SNAPSHOT"
    return "OTHER"


# -----------------------------------------------------------------------------
# compute_weights observer
# -----------------------------------------------------------------------------

@dataclass
class WeightCall:
    seq: int
    date: Optional[str]
    i: Optional[int]
    caller_lineno: int
    phase: str
    weight_sum: float
    n_positions: int
    weights_json: str
    positions_json: str


class WeightObserver:
    def __init__(self, engine: Any, engine_path: Path):
        self.engine = engine
        self.engine_path = engine_path
        self.original = engine.compute_weights
        self.calls: List[WeightCall] = []
        self.seq = 0

    def wrapper(self, positions: Mapping[str, Any], m: Any = None) -> Dict[str, float]:
        # 원본을 먼저 호출한다. 관측기가 반환값을 바꾸지 않는 것이 핵심 불변식이다.
        weights = self.original(positions, m)

        caller = inspect.currentframe().f_back  # type: ignore[union-attr]
        try:
            caller_name = caller.f_code.co_name if caller is not None else ""
            if caller_name != "run_prima4":
                return weights

            loc = caller.f_locals
            date = normalize_date(loc.get("date"))
            i_raw = loc.get("i")
            i_val = int(i_raw) if isinstance(i_raw, (int, np.integer)) else None
            lineno = int(caller.f_lineno)
            phase = classify_compute_phase(self.engine_path, lineno)

            pos_rows = position_snapshot(positions)
            weights_clean = {str(k): float(v) for k, v in weights.items()}
            self.seq += 1
            self.calls.append(
                WeightCall(
                    seq=self.seq,
                    date=date,
                    i=i_val,
                    caller_lineno=lineno,
                    phase=phase,
                    weight_sum=float(sum(weights_clean.values())),
                    n_positions=len(pos_rows),
                    weights_json=json.dumps(weights_clean, ensure_ascii=False, sort_keys=True),
                    positions_json=json.dumps(pos_rows, ensure_ascii=False, sort_keys=True),
                )
            )
            return weights
        finally:
            # frame reference cycle 방지
            del caller

    def __enter__(self) -> "WeightObserver":
        self.engine.compute_weights = self.wrapper
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.engine.compute_weights = self.original


# -----------------------------------------------------------------------------
# snapshot → EOD / Applied / Cohort 변환
# -----------------------------------------------------------------------------

def calls_dataframe(calls: Iterable[WeightCall]) -> pd.DataFrame:
    return pd.DataFrame([asdict(c) for c in calls])


def expand_weight_json(df_calls: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
    rows = []
    for r in df_calls.itertuples(index=False):
        w = json.loads(r.weights_json)
        row = {"date": r.date, "seq": r.seq, "phase": r.phase, "caller_lineno": r.caller_lineno}
        for t in tickers:
            row[t] = float(w.get(t, 0.0))
        rows.append(row)
    return pd.DataFrame(rows)


def expand_position_json(df_calls: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for r in df_calls.itertuples(index=False):
        for p in json.loads(r.positions_json):
            p = dict(p)
            p.update({"date": r.date, "seq": r.seq, "phase": r.phase, "caller_lineno": r.caller_lineno})
            rows.append(p)
    return pd.DataFrame(rows)


def build_eod_snapshots(
    calls: pd.DataFrame,
    equity_dates: pd.DatetimeIndex,
    tickers: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """거래일별 마지막 compute_weights 호출을 EOD 확정 상태로 채택."""
    if calls.empty:
        eod_w = pd.DataFrame(0.0, index=equity_dates, columns=tickers)
        eod_pos = pd.DataFrame(columns=["date", "ticker", "cohort_id"])
        return eod_w, eod_pos

    c = calls.dropna(subset=["date"]).copy()
    c["date_ts"] = pd.to_datetime(c["date"])
    last_idx = c.groupby("date_ts", sort=True)["seq"].idxmax()
    last = c.loc[last_idx].sort_values("date_ts")

    # weight wide
    w_rows = []
    pos_rows = []
    for r in last.itertuples(index=False):
        w = json.loads(r.weights_json)
        wr = {"date": r.date_ts}
        for t in tickers:
            wr[t] = float(w.get(t, 0.0))
        w_rows.append(wr)

        for p in json.loads(r.positions_json):
            pr = dict(p)
            pr["date"] = r.date_ts
            pos_rows.append(pr)

    eod_w = pd.DataFrame(w_rows).set_index("date") if w_rows else pd.DataFrame(columns=tickers)
    eod_w = eod_w.reindex(equity_dates)

    # compute_weights 호출이 없는 날은 직전 EOD 상태를 유지한다.
    # 초기 구간은 현금 100%이므로 0으로 채운다.
    eod_w = eod_w.ffill().fillna(0.0)
    for t in tickers:
        if t not in eod_w.columns:
            eod_w[t] = 0.0
    eod_w = eod_w[tickers]

    eod_pos = pd.DataFrame(pos_rows)
    if not eod_pos.empty:
        eod_pos["date"] = pd.to_datetime(eod_pos["date"])
    return eod_w, eod_pos


def build_applied_weights(eod_w: pd.DataFrame) -> pd.DataFrame:
    """엔진 일간수익 계산에 실제 적용되는 비중 = 전 거래일 EOD 비중."""
    return eod_w.shift(1).fillna(0.0)


def build_applied_position_map(
    eod_pos: pd.DataFrame,
    dates: pd.DatetimeIndex,
    tickers: List[str],
) -> pd.DataFrame:
    """전일 EOD Position identity를 오늘 수익 적용 cohort identity로 이동."""
    base = pd.DataFrame(index=dates, columns=tickers, dtype=object)
    if eod_pos.empty:
        return base

    for r in eod_pos.itertuples(index=False):
        d = pd.Timestamp(r.date)
        if d in base.index and r.ticker in base.columns:
            base.at[d, r.ticker] = r.cohort_id

    # 포지션이 없는 날짜를 ffill하면 안 된다. EOD position table 자체가 sparse이므로
    # weight>0인 곳에서만 cohort를 사용하게 하고, identity 이동만 shift한다.
    return base.shift(1)


def build_daily_turnover(applied_w: pd.DataFrame) -> pd.DataFrame:
    prev = applied_w.shift(1).fillna(0.0)
    abs_delta = (applied_w - prev).abs()
    out = pd.DataFrame(index=applied_w.index)
    out["turnover"] = abs_delta.sum(axis=1)
    out["changed_ticker_n"] = (abs_delta > DEFAULT_EPS).sum(axis=1)
    out["max_abs_weight_change"] = abs_delta.max(axis=1)
    return out


def build_asset_returns(df: pd.DataFrame, pmap: Dict[str, str], tickers: List[str]) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for t in tickers:
        c = pmap.get(t)
        if c is None:
            out[t] = np.nan
        else:
            s = pd.to_numeric(df[c], errors="coerce")
            out[t] = s.pct_change()
    return out


def build_cohort_summary(
    eod_pos: pd.DataFrame,
    eod_w: pd.DataFrame,
    applied_w: pd.DataFrame,
    applied_cohort: pd.DataFrame,
    asset_rets: pd.DataFrame,
    eps: float,
) -> pd.DataFrame:
    if eod_pos.empty:
        return pd.DataFrame()

    # cohort metadata는 최초 관측값을 사용
    meta_cols = [
        "cohort_id", "date_cohort_id", "ticker", "entry_date", "entry_price",
        "entry_score", "entry_threshold", "target_days", "level"
    ]
    meta = eod_pos.sort_values("date").drop_duplicates("cohort_id", keep="first")
    meta = meta[[c for c in meta_cols if c in meta.columns]].set_index("cohort_id")

    rows: List[Dict[str, Any]] = []
    for cid, m in meta.iterrows():
        t = str(m["ticker"])
        entry_date = pd.Timestamp(m["entry_date"])

        initial_w = float(eod_w.at[entry_date, t]) if entry_date in eod_w.index and t in eod_w.columns else 0.0

        if t in applied_cohort.columns:
            mask_cid = applied_cohort[t].astype(object).eq(cid)
        else:
            mask_cid = pd.Series(False, index=applied_w.index)
        w = applied_w[t].where(mask_cid, 0.0) if t in applied_w.columns else pd.Series(0.0, index=applied_w.index)
        active = w.abs() > eps

        r = asset_rets[t] if t in asset_rets.columns else pd.Series(np.nan, index=applied_w.index)
        gross_series = (w * r.fillna(0.0)).where(active, 0.0)

        active_dates = list(w.index[active])
        first_exp = active_dates[0] if active_dates else None
        last_exp = active_dates[-1] if active_dates else None

        # cohort 내부 weight-path variation. 포트폴리오 전체 turnover와 별개 진단치.
        # entry/exit 경계 포함을 위해 양끝에 0을 붙인다.
        vals = w.loc[mask_cid].to_numpy(dtype=float) if mask_cid.any() else np.array([], dtype=float)
        if len(vals):
            extended = np.r_[0.0, vals, 0.0]
            path_variation = float(np.abs(np.diff(extended)).sum())
        else:
            path_variation = 0.0

        rows.append({
            "cohort_id": cid,
            "date_cohort_id": m.get("date_cohort_id"),
            "ticker": t,
            "entry_date": normalize_date(entry_date),
            "entry_price": m.get("entry_price"),
            "entry_score": m.get("entry_score"),
            "entry_threshold": m.get("entry_threshold"),
            "target_days": m.get("target_days"),
            "level": m.get("level"),
            "initial_allocated_weight": initial_w,
            "allocated_at_entry": bool(abs(initial_w) > eps),
            "exposure_days": int(active.sum()),
            "exposure_weight_days": float(w.sum()),
            "max_weight": float(w.max()) if len(w) else 0.0,
            "mean_weight_when_exposed": float(w[active].mean()) if active.any() else 0.0,
            "first_exposure_date": normalize_date(first_exp),
            "last_exposure_date": normalize_date(last_exp),
            "gross_pnl_nav": float(gross_series.sum()),
            "gross_pnl_pct": float(gross_series.sum() * 100.0),
            "nonzero_gross_pnl": bool(abs(float(gross_series.sum())) > eps),
            "cohort_weight_path_variation": path_variation,
        })

    return pd.DataFrame(rows).sort_values(["entry_date", "ticker"]).reset_index(drop=True)


def build_date_cohort_summary(cohort: pd.DataFrame, eps: float) -> pd.DataFrame:
    if cohort.empty:
        return pd.DataFrame()
    g = cohort.groupby("date_cohort_id", dropna=False)
    rows = []
    for dcid, x in g:
        pnl = float(x["gross_pnl_nav"].sum())
        rows.append({
            "date_cohort_id": dcid,
            "ticker_n": int(x["ticker"].nunique()),
            "tickers": "|".join(sorted(x["ticker"].astype(str).unique())),
            "allocated_ticker_n": int(x["allocated_at_entry"].sum()),
            "total_initial_allocated_weight": float(x["initial_allocated_weight"].sum()),
            "total_exposure_weight_days": float(x["exposure_weight_days"].sum()),
            "gross_pnl_nav": pnl,
            "gross_pnl_pct": pnl * 100.0,
            "nonzero_gross_pnl": bool(abs(pnl) > eps),
        })
    return pd.DataFrame(rows).sort_values("date_cohort_id").reset_index(drop=True)


# -----------------------------------------------------------------------------
# 단일 run
# -----------------------------------------------------------------------------

def run_telemetry(args: argparse.Namespace) -> int:
    engine_path = Path(args.engine).resolve()
    data_path = Path(args.data).resolve()
    outdir = Path(args.out).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    engine = load_py_module(engine_path, "argus_engine")

    configure_sha = None
    if args.configure:
        cfg_path = Path(args.configure).resolve()
        cfg = load_py_module(cfg_path, "argus_configure")
        if not hasattr(cfg, "configure"):
            raise AttributeError("configure 모듈에 configure(engine) 함수가 없습니다.")
        cfg.configure(engine)
        configure_sha = sha256_file(cfg_path)

    df = load_data(data_path)
    pmap = price_column_map(engine, df)
    tickers = sorted(set(getattr(engine, "ALL_TICKERS", [])))

    run_kwargs: Dict[str, Any] = {
        "max_positions": int(args.max_positions),
        "rebal_freq": int(args.rebal_freq),
    }
    if args.start_date:
        run_kwargs["start_date"] = args.start_date
    if args.end_date:
        run_kwargs["end_date"] = args.end_date

    with WeightObserver(engine, engine_path) as obs:
        result = engine.run_prima4(df, **run_kwargs)

    calls = calls_dataframe(obs.calls)
    equity = result.get("equity", pd.Series(dtype=float))
    if not isinstance(equity, pd.Series):
        equity = pd.Series(equity)
    equity.index = pd.to_datetime(equity.index)
    equity_dates = pd.DatetimeIndex(equity.index)

    eod_w, eod_pos = build_eod_snapshots(calls, equity_dates, tickers)
    applied_w = build_applied_weights(eod_w)
    applied_cohort = build_applied_position_map(eod_pos, equity_dates, tickers)
    daily_turn = build_daily_turnover(applied_w)

    # 엔진 input_integrity_gate / 기간 slice 후 실제 사용 날짜와 정렬하기 위해
    # 원본 df를 equity 날짜로 재색인한다.
    df_run = df.reindex(equity_dates)
    asset_rets = build_asset_returns(df_run, pmap, tickers)
    cohort = build_cohort_summary(eod_pos, eod_w, applied_w, applied_cohort, asset_rets, args.eps)
    date_cohort = build_date_cohort_summary(cohort, args.eps)

    # 현금 weight도 저장
    eod_out = eod_w.copy()
    eod_out.insert(0, "CASH", (1.0 - eod_w.sum(axis=1)).clip(lower=0.0))
    applied_out = applied_w.copy()
    applied_out.insert(0, "CASH", (1.0 - applied_w.sum(axis=1)).clip(lower=0.0))

    # 실제 적용비중 기준 gross P&L per ticker
    gross_by_ticker = (applied_w * asset_rets.fillna(0.0)).sum(axis=0)

    calls.to_csv(outdir / "weight_calls.csv", index=False)
    eod_pos.to_csv(outdir / "eod_positions_long.csv", index=False)
    eod_out.to_csv(outdir / "eod_weights.csv", index_label="Date")
    applied_out.to_csv(outdir / "applied_weights.csv", index_label="Date")
    applied_cohort.to_csv(outdir / "applied_cohort_ids.csv", index_label="Date")
    daily_turn.to_csv(outdir / "daily_turnover.csv", index_label="Date")
    cohort.to_csv(outdir / "cohort_summary.csv", index=False)
    date_cohort.to_csv(outdir / "date_cohort_summary.csv", index=False)

    tlog = result.get("trade_log")
    if isinstance(tlog, pd.DataFrame):
        tlog_df = tlog.copy()
    elif isinstance(tlog, list):
        tlog_df = pd.DataFrame(tlog)
    else:
        tlog_df = pd.DataFrame()
    if not tlog_df.empty:
        tlog_df.to_csv(outdir / "engine_trade_log.csv", index=False)

    # 실제 수익 적용 단위 long table — cohort 귀속과 zero 원인 추적의 기본 원장
    alloc_rows = []
    for d in applied_w.index:
        for t in tickers:
            wv = float(applied_w.at[d, t])
            cid = applied_cohort.at[d, t] if t in applied_cohort.columns else None
            rv = asset_rets.at[d, t] if t in asset_rets.columns else np.nan
            if abs(wv) <= args.eps and (cid is None or (isinstance(cid, float) and np.isnan(cid))):
                continue
            alloc_rows.append({
                "Date": d,
                "ticker": t,
                "cohort_id": cid,
                "applied_weight": wv,
                "asset_return": float(rv) if pd.notna(rv) else np.nan,
                "gross_pnl_nav": float(wv * rv) if pd.notna(rv) else np.nan,
                "gross_pnl_pct": float(wv * rv * 100.0) if pd.notna(rv) else np.nan,
            })
    pd.DataFrame(alloc_rows).to_csv(outdir / "applied_allocations_long.csv", index=False)

    summary = {
        "tool_version": TOOL_VERSION,
        "engine_path": str(engine_path),
        "engine_sha256": sha256_file(engine_path),
        "data_path": str(data_path),
        "data_sha256": sha256_file(data_path),
        "configure_path": str(Path(args.configure).resolve()) if args.configure else None,
        "configure_sha256": configure_sha,
        "run_kwargs": run_kwargs,
        "date_start": normalize_date(equity_dates.min()) if len(equity_dates) else None,
        "date_end": normalize_date(equity_dates.max()) if len(equity_dates) else None,
        "equity_rows": int(len(equity)),
        "compute_weight_calls": int(len(calls)),
        "cagr": safe_float(result.get("cagr")),
        "sharpe": safe_float(result.get("sharpe")),
        "mdd": safe_float(result.get("mdd")),
        "trade_log_event_n": int(len(tlog_df)),
        "engine_n_trades": int(result.get("n_trades", 0)) if result.get("n_trades") is not None else None,
        "reconstructed_turnover_sum": float(daily_turn["turnover"].sum()),
        "days_with_turnover": int((daily_turn["turnover"] > args.eps).sum()),
        "capital_cohort_n": int(len(cohort)),
        "date_cohort_n": int(cohort["date_cohort_id"].nunique()) if not cohort.empty else 0,
        "allocated_cohort_n": int(cohort["allocated_at_entry"].sum()) if not cohort.empty else 0,
        "exposed_cohort_n": int((cohort["exposure_days"] > 0).sum()) if not cohort.empty else 0,
        "nonzero_pnl_cohort_n": int(cohort["nonzero_gross_pnl"].sum()) if not cohort.empty else 0,
        "gross_pnl_by_ticker_nav": {k: float(v) for k, v in gross_by_ticker.items()},
        "notes": [
            "EOD weight = 각 거래일의 마지막 compute_weights snapshot",
            "Applied weight = 전 거래일 EOD weight",
            "BUY pct는 실제 allocation weight로 사용하지 않음",
            "cohort P&L은 gross asset-return attribution이며 portfolio interaction/cost residual은 별도 비교 필요",
        ],
    }
    dump_json(outdir / "run_summary.json", summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2, default=json_default))
    return 0


# -----------------------------------------------------------------------------
# 두 run 비교
# -----------------------------------------------------------------------------

def read_weight_file(directory: Path, name: str) -> pd.DataFrame:
    p = directory / name
    if not p.exists():
        raise FileNotFoundError(p)
    df = pd.read_csv(p, parse_dates=["Date"]).set_index("Date")
    return df


def compare_runs(args: argparse.Namespace) -> int:
    first = Path(args.first).resolve()
    second = Path(args.second).resolve()
    outdir = Path(args.out).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    a = read_weight_file(first, "applied_weights.csv")
    b = read_weight_file(second, "applied_weights.csv")
    idx = a.index.union(b.index).sort_values()
    cols = sorted(set(a.columns) | set(b.columns))
    a = a.reindex(idx, columns=cols).fillna(0.0)
    b = b.reindex(idx, columns=cols).fillna(0.0)

    delta = b - a  # second - first
    delta.to_csv(outdir / "applied_weight_delta_second_minus_first.csv", index_label="Date")

    # 일별/종목별 자본 이동 long table
    dl = (delta.reset_index()
          .melt(id_vars=["Date"], var_name="ticker", value_name="delta_weight"))
    dl = dl[dl["delta_weight"].abs() > args.eps].copy()
    dl["direction"] = np.where(dl["delta_weight"] > 0, "ABSORB", "RELEASE")
    dl.to_csv(outdir / "daily_capital_destination_long.csv", index=False)

    rows = []
    for t in cols:
        s = delta[t]
        rows.append({
            "ticker": t,
            "weight_days_delta": float(s.sum()),
            "positive_weight_days": float(s.clip(lower=0).sum()),
            "negative_weight_days": float((-s.clip(upper=0)).sum()),
            "days_changed": int((s.abs() > args.eps).sum()),
            "max_abs_delta_weight": float(s.abs().max()),
            "max_positive_delta_weight": float(s.max()),
            "max_negative_delta_weight": float(s.min()),
        })
    destination = pd.DataFrame(rows)
    destination = destination[(destination["weight_days_delta"].abs() > args.eps) |
                              (destination["days_changed"] > 0)].copy()
    destination = destination.sort_values("weight_days_delta", ascending=False)
    destination.to_csv(outdir / "capital_destination.csv", index=False)

    # turnover: 각 run의 실제 재구성값을 읽고 second-first 비교
    ta = pd.read_csv(first / "daily_turnover.csv", parse_dates=["Date"]).set_index("Date")
    tb = pd.read_csv(second / "daily_turnover.csv", parse_dates=["Date"]).set_index("Date")
    tdf = pd.DataFrame(index=idx)
    tdf["first_turnover"] = ta["turnover"].reindex(idx).fillna(0.0)
    tdf["second_turnover"] = tb["turnover"].reindex(idx).fillna(0.0)
    tdf["delta_turnover"] = tdf["second_turnover"] - tdf["first_turnover"]
    tdf.to_csv(outdir / "turnover_delta.csv", index_label="Date")

    # cohort topology 비교
    ca = pd.read_csv(first / "cohort_summary.csv") if (first / "cohort_summary.csv").exists() else pd.DataFrame()
    cb = pd.read_csv(second / "cohort_summary.csv") if (second / "cohort_summary.csv").exists() else pd.DataFrame()
    a_ids = set(ca.get("cohort_id", pd.Series(dtype=str)).astype(str))
    b_ids = set(cb.get("cohort_id", pd.Series(dtype=str)).astype(str))
    cohort_cmp = pd.DataFrame({
        "cohort_id": sorted(a_ids | b_ids),
    })
    if not cohort_cmp.empty:
        cohort_cmp["in_first"] = cohort_cmp["cohort_id"].isin(a_ids)
        cohort_cmp["in_second"] = cohort_cmp["cohort_id"].isin(b_ids)
        cohort_cmp["topology_status"] = np.select(
            [cohort_cmp["in_first"] & ~cohort_cmp["in_second"],
             ~cohort_cmp["in_first"] & cohort_cmp["in_second"]],
            ["FIRST_ONLY", "SECOND_ONLY"],
            default="BOTH",
        )
    cohort_cmp.to_csv(outdir / "cohort_topology_compare.csv", index=False)

    summary_a = json.loads((first / "run_summary.json").read_text(encoding="utf-8"))
    summary_b = json.loads((second / "run_summary.json").read_text(encoding="utf-8"))

    neg_total = float((-destination["weight_days_delta"].clip(upper=0)).sum())
    pos_total = float(destination["weight_days_delta"].clip(lower=0).sum())

    summary = {
        "tool_version": TOOL_VERSION,
        "delta_definition": "SECOND_MINUS_FIRST",
        "first": str(first),
        "second": str(second),
        "cagr_delta": (summary_b.get("cagr") or 0.0) - (summary_a.get("cagr") or 0.0),
        "sharpe_delta": (summary_b.get("sharpe") or 0.0) - (summary_a.get("sharpe") or 0.0),
        "mdd_delta": (summary_b.get("mdd") or 0.0) - (summary_a.get("mdd") or 0.0),
        "turnover_delta_sum": float(tdf["delta_turnover"].sum()),
        "turnover_first_sum": float(tdf["first_turnover"].sum()),
        "turnover_second_sum": float(tdf["second_turnover"].sum()),
        "weight_days_released": neg_total,
        "weight_days_absorbed": pos_total,
        "cohort_first_only_n": int((cohort_cmp.get("topology_status") == "FIRST_ONLY").sum()) if not cohort_cmp.empty else 0,
        "cohort_second_only_n": int((cohort_cmp.get("topology_status") == "SECOND_ONLY").sum()) if not cohort_cmp.empty else 0,
        "max_abs_weight_delta": float(delta.abs().to_numpy().max()) if delta.size else 0.0,
        "days_any_weight_changed": int((delta.abs().max(axis=1) > args.eps).sum()),
        "notes": [
            "capital destination은 applied weight 기준 SECOND-FIRST 누적 weight-days",
            "CASH 포함: 투자비중 감소가 현금으로 간 경우도 명시적으로 보존",
            "BUY/SELL topology 동일 여부와 weight-path 동일 여부를 분리",
        ],
    }
    dump_json(outdir / "compare_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=json_default))
    return 0


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ARGUS Capital Destination Telemetry")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run", help="단일 엔진 variant telemetry 실행")
    r.add_argument("--engine", required=True, help="PRIMA2 engine .py")
    r.add_argument("--data", required=True, help="입력 CSV")
    r.add_argument("--out", required=True, help="산출 디렉터리")
    r.add_argument("--configure", help="configure(engine) 함수를 가진 validation-only .py")
    r.add_argument("--start-date")
    r.add_argument("--end-date")
    r.add_argument("--max-positions", type=int, default=5)
    r.add_argument("--rebal-freq", type=int, default=5)
    r.add_argument("--eps", type=float, default=DEFAULT_EPS)
    r.set_defaults(func=run_telemetry)

    c = sub.add_parser("compare", help="두 telemetry run 비교 (SECOND-FIRST)")
    c.add_argument("--first", required=True, help="첫 번째 telemetry 디렉터리")
    c.add_argument("--second", required=True, help="두 번째 telemetry 디렉터리")
    c.add_argument("--out", required=True, help="비교 산출 디렉터리")
    c.add_argument("--eps", type=float, default=DEFAULT_EPS)
    c.set_defaults(func=compare_runs)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

