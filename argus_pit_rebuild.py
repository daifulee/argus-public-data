#!/usr/bin/env python3
# =====================================================================
# ARGUS — BT 파일 FRED 계열 발표일(Point-in-Time) 정렬 재구성기
# VERSION : v1.1.1-PITREBUILD
# DATE    : 2026-11-10 (S291 후속, 과최적화 감사 2단계)
# CHANGE  : v1.1.1 — 진단 지표 결함 처방(run 42782642010 실측). '개정 관측 비율'을 관측별 행 수로
#           세어, 판본 창이 여러 개인 계열(DFII10·T10YIE 계열·RRPONTSYD)은 같은 관측이 창마다
#           다시 회수되며 0.74~0.78 로 부풀었다. → 관측별 '서로 다른 값' 개수 > 1 로 센다.
#           재구성 값·calendar 산출에는 영향 없음(바이트 동일 확인).
#           v1.1.0 — GHA 첫 실행(run 42780636492) 실측 결함 3건 처방
#             ① 일간 계열 5종 HTTPError: ALFRED 는 요청 1회당 판본일 2,000개 상한이 있고
#                클라이언트 쪽 쪽나누기가 없다. → fred/series/vintagedates 로 판본일 목록을 먼저
#                받고, 판본 1,900개 단위 실시간 창(window)으로 나눠 회수한다. 창 끝은 다음 창
#                시작 전날로 잡아 틈을 없애고, 마지막 창은 9999-12-31 까지 연다
#             ② USD_CNY 미래 관측 1,809건(불변식이 차단): realtime_start=1776-07-04 요청 시
#                판본 추적 이전 구간 행이 1776 시작으로 돌아와 모든 관측이 처음부터 '게시됨'
#                으로 보였다(추정 — 판본일 목록 회수 후 재확인). → 판본 창을 첫 판본일부터
#                요청하고, 판본 시작일 < 관측일인 행은 버리고 건수를 기록한다
#             ③ NFCI·SAHM·OAS 등 커버 부족 강등: 판본 추적이 BT 시작(2007) 이후에 시작하는
#                계열이 있다. → 계열별 혼합(hybrid): 결정일 기준일이 첫 판본일 이전이면
#                calendar, 이후면 ALFRED. 분할 경계는 매니페스트에 기록
#             + HTTP 오류 시 FRED error_message 를 로그에 남긴다(키는 가림)
#             + 불변식 위반이어도 매니페스트·관측일 로그를 남겨 아티팩트로 진단 가능하게 한다
#             + Timestamp.day_of_week → day_of_week (pandas 4 경고)
#           calendar 산출은 v1.0.x 와 바이트 단위 동일해야 한다.
#           v1.0.1 — alfred 실측 게시 지연·개정 비율 매니페스트 기록
#           v1.0.0 — 신설. LIVE 계약(fred_prior_date_v1)과 BT 의 시점 규약 불일치 처방
# ---------------------------------------------------------------------
# 두 가지 방식
#   alfred   : FRED_API_KEY 로 ALFRED 판본을 받아 LIVE 계약과 같은 규칙으로 결정일별 값을
#              고른다. 판본 추적 이전 결정일은 calendar 로 잇는다(혼합). (GHA·Colab 용)
#   calendar : 키 없이 BT 의 현재 판본 값을 발표 일정 규칙으로 '늦게' 배치한다.
#              시점 미래정보만 제거하고 개정 미래정보는 남는다. 규칙은 추정이며
#              매니페스트에 그 사실을 적는다.
# 공통
#   - 결정일 d 의 판본 기준일 = d - 1일 (LIVE 계약과 동일)
#   - 관측 경과 상한 = 계약의 MAX_OBSERVATION_AGE_DAYS (초과 시 NaN, 계약과 동일)
#   - 장기 동결 구간 탐지(--nan-frozen 시 NaN 처리, 기본은 표기만)
#   - 구성요소가 바뀌면 Net_Liquidity 재계산
#   - 출력 3종: 재구성 CSV / <출력>.pit_obs.csv(결정일별 사용 관측일) /
#               <출력>.manifest.json(방식·규칙·통계·해시)
# 사용 예
#   python argus_pit_rebuild.py --input BT_LONG_v6_FEAT_RF.csv \
#       --output BT_LONG_v6_FEAT_RF_PIT.csv --mode calendar
#   FRED_API_KEY=... python argus_pit_rebuild.py --input ... --output ... --mode alfred
#   python argus_pit_rebuild.py --selftest
# =====================================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

VERSION = "v1.1.1-PITREBUILD"
CONTRACT = "fred_prior_date_v1"          # LIVE 계약과 같은 규칙임을 표기
UA = {"User-Agent": "Mozilla/5.0 argus-pit-rebuild"}   # 격언 #107: 명시 UA

# ---------------------------------------------------------------------
# 계열 명세
#   fred    : FRED 시리즈 ID
#   kind    : daily / weekly / monthly
#   obs_dow : 주간 계열의 관측 기준 요일(월=0). 변경일을 이 요일로 되돌려 관측일로 본다
#   rule    : calendar 방식에서 '관측일 → 최초 판본 게시일' 추정 규칙
#   max_age : 계약의 관측 경과 상한(일)
#   ※ rule 은 공표 일정에서 끌어낸 추정이다. alfred 방식이 정본이다.
# ---------------------------------------------------------------------
SPEC = {
    "DFII10":      dict(fred="DFII10",       kind="daily",   rule="next_bday",       max_age=14),
    "T10YIE":      dict(fred="T10YIE",       kind="daily",   rule="next_bday",       max_age=14),
    "T5YIE":       dict(fred="T5YIE",        kind="daily",   rule="next_bday",       max_age=14),
    "T10Y3M":      dict(fred="T10Y3M",       kind="daily",   rule="next_bday",       max_age=14),
    "OAS_HY":      dict(fred="BAMLH0A0HYM2", kind="daily",   rule="next_bday",       max_age=14),
    "OAS_IG":      dict(fred="BAMLC0A0CM",   kind="daily",   rule="next_bday",       max_age=14),
    # RRPONTSYD 는 2013 이전 역레포 운영이 드물어 장기 상수가 실측값이다 → 동결 탐지 제외
    "RRPONTSYD":   dict(fred="RRPONTSYD",    kind="daily",   rule="next_bday",       max_age=14, sparse=True),
    "USD_CNY":     dict(fred="DEXCHUS",      kind="daily",   rule="h10_next_monday", max_age=14),
    "NFCI":        dict(fred="NFCI",         kind="weekly",  obs_dow=4, rule="plus5",  max_age=35),
    "STLFSI":      dict(fred="STLFSI4",      kind="weekly",  obs_dow=4, rule="plus6",  max_age=35),
    "ICSA":        dict(fred="ICSA",         kind="weekly",  obs_dow=5, rule="plus5",  max_age=35),
    "WALCL":       dict(fred="WALCL",        kind="weekly",  obs_dow=2, rule="plus1",  max_age=35),
    "WTREGEN":     dict(fred="WTREGEN",      kind="weekly",  obs_dow=2, rule="plus1",  max_age=35),
    "SAHMCURRENT": dict(fred="SAHMCURRENT",  kind="monthly", rule="bls_empsit",        max_age=75),
    "UMCSENT":     dict(fred="UMCSENT",      kind="monthly", rule="last_friday_same",  max_age=75),
}
# 동결 탐지 임계(같은 값이 연속되는 달력일 수) — 이를 넘으면 실측이 아니라 ffill 로 본다
FROZEN_DAYS = {"daily": 21, "weekly": 63, "monthly": 150}
# FRED 가 아닌 월간 열도 동결 탐지 대상에 넣는다 (PMI 동결 실측 2014-09~2021-12)
EXTRA_FROZEN = {"PMI": "monthly"}


# ---------------------------------------------------------------------
# 게시일 추정 규칙 (calendar 방식 전용)
# ---------------------------------------------------------------------
def _next_bday(d: pd.Timestamp) -> pd.Timestamp:
    return (d + pd.offsets.BDay(1)).normalize()


def _rule(name: str, obs: pd.Timestamp) -> pd.Timestamp:
    """관측일 → 최초 게시일(추정). 휴일 이동은 반영하지 않는다(보수 방향 오차는 1일 이내)."""
    if name == "next_bday":            # 일간 FRED: 다음 영업일 게시
        return _next_bday(obs)
    if name == "h10_next_monday":      # H.10 주간 공표: 관측 주의 다음 월요일
        return (obs + pd.Timedelta(days=7 - obs.day_of_week)).normalize()
    if name == "plus1":                # H.4.1: 수요일 관측 → 목요일 공표
        return obs + pd.Timedelta(days=1)
    if name == "plus5":                # NFCI 금→수 / ICSA 토→목
        return obs + pd.Timedelta(days=5)
    if name == "plus6":                # STLFSI 금→목
        return obs + pd.Timedelta(days=6)
    if name == "bls_empsit":           # 고용보고서: 12일이 든 주(일~토)가 끝난 뒤 세 번째 금요일
        #  BLS 공표 규칙. 셧다운·공휴일 이동(예: 2026-07-02 목) 은 반영하지 않는다
        d12 = obs.to_period("M").to_timestamp() + pd.Timedelta(days=11)
        sat = d12 + pd.Timedelta(days=(5 - d12.day_of_week) % 7)
        return sat + pd.Timedelta(days=20)
    if name == "first_friday_next":    # (v1.0.0 초안 규칙 — 4~7일 낙관 오차 실측으로 미사용)
        m = (obs + pd.offsets.MonthBegin(1)).normalize()
        return m + pd.Timedelta(days=(4 - m.day_of_week) % 7)
    if name == "last_friday_same":     # 미시간 확정치: 관측 달 마지막 금요일(근사)
        e = (obs + pd.offsets.MonthEnd(0)).normalize()
        return e - pd.Timedelta(days=(e.day_of_week - 4) % 7)
    raise ValueError(f"알 수 없는 규칙: {name}")


def _norm_obs(col: str, d: pd.Timestamp) -> pd.Timestamp:
    """BT 변경일을 관측일로 정규화한다. 주간은 기준 요일로, 월간은 월초로 되돌린다."""
    sp = SPEC[col]
    if sp["kind"] == "weekly":
        return (d - pd.Timedelta(days=(d.day_of_week - sp["obs_dow"]) % 7)).normalize()
    if sp["kind"] == "monthly":
        return d.to_period("M").to_timestamp()
    return d.normalize()


# ---------------------------------------------------------------------
# 판본 행(rows) 구성 — 공통 형식: obs, rs, re, value
#   rs = 판본 시작일(최초 게시), re = 판본 종료일(NaT = 현재까지 유효)
# ---------------------------------------------------------------------
def rows_from_calendar(col: str, s: pd.Series) -> pd.DataFrame:
    """BT 현재 판본 값 + 게시 규칙. 개정 이력은 없으므로 관측당 1행."""
    x = s.dropna()
    if x.empty:
        return pd.DataFrame(columns=["obs", "rs", "re", "value"])
    if SPEC[col]["kind"] == "daily":
        obs = x.index.normalize()
        val = x.values
    else:
        # 주간·월간: BT 는 관측일 표기이므로 각 날짜를 관측 기준일로 되돌려 묶고
        # 묶음의 마지막 값을 그 관측의 값으로 본다. 값이 안 바뀐 기간도 관측으로 남긴다
        # (변경점만 쓰면 무변동 기간이 사라져 경과 상한에 걸려 NaN 이 된다 — v1.0.0 시험 중 실측)
        key = pd.DatetimeIndex([_norm_obs(col, d) for d in x.index])
        g = x.groupby(key).last()
        obs = g.index
        val = g.values
    r = pd.DataFrame({"obs": obs, "value": val}).drop_duplicates("obs", keep="last")
    r["rs"] = [_rule(SPEC[col]["rule"], o) for o in r["obs"]]
    r["re"] = pd.NaT
    return r[["obs", "rs", "re", "value"]].reset_index(drop=True)


VINTAGE_WINDOW = 1900      # ALFRED 요청 1회당 판본일 상한 2,000 (JSON) 아래로 여유를 둔다


def _fred_get(path: str, params: dict, api_key: str, tries: int = 4) -> dict:
    """FRED API GET. 실패 시 FRED error_message 를 남기되 키는 가린다."""
    q = urllib.parse.urlencode(dict(params, api_key=api_key, file_type="json"))
    url = f"https://api.stlouisfed.org/fred/{path}?{q}"
    last_msg = ""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as f:
                return json.loads(f.read())
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode("utf-8", "replace"))
                last_msg = str(body.get("error_message", ""))[:200]
            except Exception:
                last_msg = ""
            if api_key:
                last_msg = last_msg.replace(api_key, "***")
            print(f"    ⚠️ FRED {path} {params.get('series_id')} 재시도 {attempt + 1}: HTTP {e.code} {last_msg}")
            if e.code in (400, 404):            # 요청 자체 오류는 재시도해도 같다
                break
        except Exception as e:                     # 키가 담긴 URL 은 출력하지 않는다
            last_msg = type(e).__name__
            print(f"    ⚠️ FRED {path} {params.get('series_id')} 재시도 {attempt + 1}: {last_msg}")
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"FRED {path} 실패: {last_msg}")


def vintage_windows(vdates: list) -> list:
    """판본일 목록을 상한 이하 창으로 나눈다. 창 끝 = 다음 창 시작 전날, 마지막 창 끝 = 9999-12-31."""
    v = sorted(pd.to_datetime(vdates))
    out = []
    for i in range(0, len(v), VINTAGE_WINDOW):
        s = v[i]
        j = i + VINTAGE_WINDOW
        e = (v[j] - pd.Timedelta(days=1)) if j < len(v) else None
        out.append((s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d") if e is not None else "9999-12-31"))
    return out


def fetch_alfred(series_id: str, api_key: str, start: str, cache_dir: Path,
                 sleep: float = 0.15):
    """ALFRED 판본 회수 → (rows, meta). 캐시는 같은 실행 안에서만 쓴다."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cf = cache_dir / f"{series_id}_vintages_{start}.json"
    if cf.is_file():
        blob = json.loads(cf.read_text(encoding="utf-8"))
    else:
        # ① 판본일 목록
        vd, off = [], 0
        while True:
            j = _fred_get("series/vintagedates", dict(series_id=series_id, limit=10000, offset=off), api_key)
            batch = j.get("vintage_dates", [])
            vd.extend(batch)
            if len(batch) < 10000:
                break
            off += 10000
            time.sleep(sleep)
        if not vd:
            raise RuntimeError("판본일 0건")
        # ② 창별 관측 회수
        obsl = []
        wins = vintage_windows(vd)
        for (ws, we) in wins:
            off = 0
            while True:
                j = _fred_get("series/observations", dict(
                    series_id=series_id, realtime_start=ws, realtime_end=we,
                    observation_start=start, limit=100000, offset=off), api_key)
                batch = j.get("observations", [])
                obsl.extend(batch)
                if len(batch) < 100000:
                    break
                off += 100000
                time.sleep(sleep)
            time.sleep(sleep)
        blob = dict(vintage_dates=vd, windows=wins, observations=obsl)
        cf.write_text(json.dumps(blob), encoding="utf-8")
    r = pd.DataFrame(blob["observations"])
    meta = dict(vintage_count=len(blob["vintage_dates"]), windows=len(blob["windows"]),
                first_vintage=min(blob["vintage_dates"]), last_vintage=max(blob["vintage_dates"]))
    if r.empty:
        return pd.DataFrame(columns=["obs", "rs", "re", "value"]), meta
    r = r[r["value"] != "."].copy()
    r["value"] = r["value"].astype(float)
    r["obs"] = pd.to_datetime(r["date"])
    r["rs"] = pd.to_datetime(r["realtime_start"])
    r["re"] = pd.to_datetime(r["realtime_end"].replace("9999-12-31", None))
    r = r[["obs", "rs", "re", "value"]]
    # 판본 시작일이 관측일보다 이르면 게시 증거가 될 수 없다 → 버리고 건수 기록
    bad = r["rs"] < r["obs"]
    meta["dropped_rs_before_obs"] = int(bad.sum())
    r = r[~bad].drop_duplicates().reset_index(drop=True)
    return r, meta


# ---------------------------------------------------------------------
# 결정일별 시점 값 산출 — LIVE 계약과 같은 규칙
#   판본 기준일 c = d - 1일. c 시점 판본에 존재(rs ≤ c ≤ re)하는 관측 중
#   관측일이 가장 늦은 것을 고른다. 경과 상한 초과면 NaN.
# ---------------------------------------------------------------------
def build_pit(rows: pd.DataFrame, decisions: pd.DatetimeIndex, max_age: int):
    vals = np.full(len(decisions), np.nan)
    used = np.full(len(decisions), np.datetime64("NaT", "ns"), dtype="datetime64[ns]")
    if rows.empty:
        return vals, used
    rows = rows.sort_values(["obs", "rs"]).reset_index(drop=True)
    first = rows.groupby("obs")["rs"].min().sort_values()
    f_rs = first.values.astype("datetime64[ns]")
    f_obs_cummax = pd.Series(first.index.values).cummax().values.astype("datetime64[ns]")
    by_obs = {o: g for o, g in rows.groupby("obs")}
    obs_sorted = np.array(sorted(by_obs.keys()), dtype="datetime64[ns]")
    for i, d in enumerate(decisions):
        c = np.datetime64((d - pd.Timedelta(days=1)).normalize(), "ns")
        k = np.searchsorted(f_rs, c, side="right") - 1
        if k < 0:
            continue
        o = f_obs_cummax[k]                                   # c 까지 게시된 가장 늦은 관측
        j = np.searchsorted(obs_sorted, o, side="right") - 1
        for _ in range(8):                                    # 삭제된 관측이면 앞 관측으로 후퇴
            if j < 0:
                break
            g = by_obs[pd.Timestamp(obs_sorted[j])]
            ok = (g["rs"].values <= c) & (g["re"].isna().values | (g["re"].values >= c))
            if ok.any():
                if (c - obs_sorted[j]) / np.timedelta64(1, "D") <= max_age:
                    vals[i] = g["value"].values[ok][-1]
                    used[i] = obs_sorted[j]
                break
            j -= 1
    return vals, used


# ---------------------------------------------------------------------
# 동결 탐지
# ---------------------------------------------------------------------
def frozen_runs(s: pd.Series, limit_days: int):
    x = s.dropna()
    if x.empty:
        return []
    grp = x.ne(x.shift()).cumsum()
    out = []
    for _, g in x.groupby(grp):
        span = (g.index[-1] - g.index[0]).days
        if span > limit_days:
            out.append(dict(start=str(g.index[0].date()), end=str(g.index[-1].date()),
                            days=int(span), rows=int(len(g)), value=float(g.iloc[0])))
    return out


def sha12(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:12]


# ---------------------------------------------------------------------
# 본 처리
# ---------------------------------------------------------------------
def rebuild(df: pd.DataFrame, mode: str, api_key: str, cache_dir: Path,
            nan_frozen: bool, alfred_start: str = "2006-01-01", min_cover: float = 0.95):
    if not isinstance(df.index, pd.DatetimeIndex) or not df.index.is_monotonic_increasing \
            or not df.index.is_unique:
        raise ValueError("Date 인덱스가 정렬·유일해야 한다")
    out = df.copy()
    dec = df.index
    obs_log = pd.DataFrame(index=dec)
    man = dict(version=VERSION, contract=CONTRACT, mode_requested=mode, columns={})
    for col, sp in SPEC.items():
        if col not in df.columns:
            continue
        info = dict(fred=sp["fred"], kind=sp["kind"])
        method = None
        cal_rows = rows_from_calendar(col, df[col])
        vals_c, used_c = build_pit(cal_rows, dec, sp["max_age"])
        vals, used = vals_c, used_c
        if mode == "alfred":
            try:
                al_rows, meta = fetch_alfred(sp["fred"], api_key, alfred_start, cache_dir)
                info.update(alfred_vintages=meta["vintage_count"], alfred_windows=meta["windows"],
                            alfred_first_vintage=meta["first_vintage"],
                            alfred_dropped_rs_before_obs=meta.get("dropped_rs_before_obs", 0))
                if not al_rows.empty:
                    # 관측일 → 최초 판본 지연 실측 (판본 추적 이후 관측만 — 이전 관측은 첫 판본일로 잘린다)
                    fv = pd.Timestamp(meta["first_vintage"])
                    fr = al_rows.groupby("obs")["rs"].min()
                    fr = fr[fr.index >= fv]
                    if len(fr):
                        lag = (fr - fr.index).dt.days
                        info["alfred_first_release_lag_days"] = dict(
                            median=float(lag.median()), p90=float(lag.quantile(0.9)), n_obs=int(len(lag)))
                    # 창 경계 중복 회수와 개정을 구분: 같은 관측의 '서로 다른 값' 수로 센다
                    info["alfred_revised_obs_share"] = round(float((al_rows.groupby("obs")["value"].nunique() > 1).mean()), 4)
                vals_a, used_a = build_pit(al_rows, dec, sp["max_age"])
                cut = dec - pd.Timedelta(days=1)
                seg = np.asarray(cut >= pd.Timestamp(meta["first_vintage"]))   # 판본 추적 구간
                bt_ok = df[col].notna().values
                cover_a = float(np.isfinite(vals_a[seg & bt_ok]).mean()) if (seg & bt_ok).any() else 0.0
                info["alfred_cover_in_segment"] = round(cover_a, 4)
                info["alfred_segment_share"] = round(float(seg.mean()), 4)
                if seg.any() and cover_a + 1e-9 >= min_cover:
                    vals = np.where(seg, vals_a, vals_c)
                    used = np.where(seg, used_a, used_c)
                    method = "alfred_prior_date" if seg.all() else "hybrid_calendar_then_alfred"
                    if not seg.all():
                        info["hybrid_split_decision"] = str(dec[seg.argmax()].date())
                else:
                    info["downgrade_reason"] = (f"ALFRED 구간 커버 {cover_a:.3f} < {min_cover}"
                                                if seg.any() else "판본 추적이 BT 구간 밖")
            except Exception as e:
                info["downgrade_reason"] = f"ALFRED 실패: {str(e)[:160]}"
        if method is None:
            method = "calendar_rule_current_vintage"
        if method != "alfred_prior_date":
            info["rule"] = sp["rule"]
            info["note"] = ("calendar 구간은 시점 미래정보만 제거. 개정 미래정보 잔존. "
                            "게시 규칙은 공표 일정 기반 추정")
        old = df[col]
        new = pd.Series(vals, index=dec)
        lag_new = (dec - pd.DatetimeIndex(used)).days
        info.update(method=method,
                    changed_cells=int(((old - new).abs() > 1e-12).sum() + (old.notna() ^ new.notna()).sum()),
                    nan_before=int(old.isna().sum()), nan_after=int(new.isna().sum()),
                    median_obs_age_days=float(np.nanmedian(lag_new)) if np.isfinite(lag_new).any() else None)
        out[col] = new
        obs_log[col + "_obs"] = pd.DatetimeIndex(used)
        man["columns"][col] = info
        print(f"  {col:12s} {method:30s} 변경 {info['changed_cells']:5d} · NaN {info['nan_before']}→{info['nan_after']}"
              f" · 관측 경과 중앙값 {info['median_obs_age_days']}일")
    # 구성요소가 바뀌었으면 Net_Liquidity 재계산 (fetcher 정의와 동일)
    if all(c in out for c in ("WALCL", "WTREGEN", "RRPONTSYD")) and "Net_Liquidity" in out:
        out["Net_Liquidity"] = out["WALCL"] - out["WTREGEN"] - 1000 * out["RRPONTSYD"]
        man["Net_Liquidity"] = "재계산: WALCL - WTREGEN - 1000*RRPONTSYD"
    # 동결 탐지
    froz = {}
    targets = {c: SPEC[c]["kind"] for c in SPEC if c in out and not SPEC[c].get("sparse")}
    targets.update({c: k for c, k in EXTRA_FROZEN.items() if c in out})
    for c, k in targets.items():
        runs = frozen_runs(df[c], FROZEN_DAYS[k])
        if runs:
            froz[c] = runs
            if nan_frozen:
                for r in runs:
                    # 첫 관측 이후 갱신 주기 1회분은 정상 유지 구간으로 남기고 그 뒤만 NaN
                    keep = pd.Timestamp(r["start"]) + pd.Timedelta(days={"daily": 3, "weekly": 10, "monthly": 40}[k])
                    out.loc[keep:pd.Timestamp(r["end"]), c] = np.nan
    man["frozen_runs"] = froz
    man["frozen_action"] = "NaN 처리" if nan_frozen else "표기만 (값 유지)"
    return out, obs_log, man


# ---------------------------------------------------------------------
# 자체 시험 — 합성 판본으로 계약 규칙을 검증한다
# ---------------------------------------------------------------------
def selftest() -> int:
    fails = 0

    def chk(name, cond):
        nonlocal fails
        print(("  ✅ " if cond else "  ❌ ") + name)
        fails += 0 if cond else 1

    T = pd.Timestamp
    # 관측 1/1 은 1/2 게시, 1/5 에 개정. 관측 1/2 는 1/3 게시.
    rows = pd.DataFrame(dict(
        obs=[T("2024-01-01"), T("2024-01-01"), T("2024-01-02")],
        rs=[T("2024-01-02"), T("2024-01-05"), T("2024-01-03")],
        re=[T("2024-01-04"), pd.NaT, pd.NaT],
        value=[1.0, 1.5, 2.0]))
    dec = pd.DatetimeIndex([T("2024-01-02"), T("2024-01-03"), T("2024-01-04"), T("2024-01-06")])
    v, u = build_pit(rows, dec, 14)
    chk("결정일 1/2: 판본 1/1 에 게시분 없음 → NaN", np.isnan(v[0]))
    chk("결정일 1/3: 판본 1/2 → 관측 1/1 초판 1.0", v[1] == 1.0)
    chk("결정일 1/4: 판본 1/3 → 관측 1/2 = 2.0", v[2] == 2.0)
    chk("결정일 1/6: 판본 1/5 → 최신 관측 1/2 유지(개정은 1/1 관측)", v[3] == 2.0)
    v2, _ = build_pit(rows, pd.DatetimeIndex([T("2024-03-01")]), 14)
    chk("경과 상한 초과 → NaN", np.isnan(v2[0]))
    # 게시 규칙
    chk("NFCI 금 1/5 → 수 1/10", _rule("plus5", T("2024-01-05")) == T("2024-01-10"))
    chk("고용보고서 2020-04 → 2020-05-08 (BLS 실제)", _rule("bls_empsit", T("2020-04-01")) == T("2020-05-08"))
    chk("고용보고서 2020-03 → 2020-04-03 (BLS 실제)", _rule("bls_empsit", T("2020-03-01")) == T("2020-04-03"))
    chk("고용보고서 2026-02 → 2026-03-06 (BLS 일정표)", _rule("bls_empsit", T("2026-02-01")) == T("2026-03-06"))
    chk("H.10 화 1/2 → 월 1/8", _rule("h10_next_monday", T("2024-01-02")) == T("2024-01-08"))
    chk("일간 금 1/5 → 월 1/8", _rule("next_bday", T("2024-01-05")) == T("2024-01-08"))
    # calendar 경로: 금요일 관측 일간값은 월요일 결정에 쓰이지 않는다 (판본 기준 일요일)
    s = pd.Series([1.0, 2.0], index=pd.DatetimeIndex([T("2024-01-04"), T("2024-01-05")]))
    r = rows_from_calendar("OAS_HY", s)
    v3, u3 = build_pit(r, pd.DatetimeIndex([T("2024-01-08"), T("2024-01-09")]), 14)
    chk("월 1/8 결정 → 목 1/4 관측 사용", v3[0] == 1.0)
    chk("화 1/9 결정 → 금 1/5 관측 사용", v3[1] == 2.0)
    # 미래 관측 차단 불변식
    chk("사용 관측일 < 결정일 (전 항목)", all(pd.isna(x) or x < d for x, d in zip(pd.DatetimeIndex(u3), [T("2024-01-08"), T("2024-01-09")])))
    # 판본 창: 상한 이하 · 틈 없음 · 마지막 창 개방
    vd = [str((T("2010-01-01") + pd.Timedelta(days=i)).date()) for i in range(4000)]
    w = vintage_windows(vd)
    chk("판본 4,000개 → 창 3개", len(w) == 3)
    chk("창 경계 틈 없음 (끝+1일 = 다음 시작)", all(pd.Timestamp(w[k][1]) + pd.Timedelta(days=1) == pd.Timestamp(w[k + 1][0]) for k in range(len(w) - 1)))
    chk("마지막 창 9999-12-31 개방", w[-1][1] == "9999-12-31")
    # 판본 시작일 < 관측일 행은 미래 관측을 만든다 → build_pit 이전에 제거돼야 함을 확인
    leak = pd.DataFrame(dict(obs=[T("2024-06-01")], rs=[T("1776-07-04")], re=[pd.NaT], value=[9.0]))
    vl, ul = build_pit(leak, pd.DatetimeIndex([T("2024-01-10")]), 10 ** 6)
    chk("(가드 없을 때) 1776 시작 행은 미래 관측을 만든다 — 가드 필요성 확인", ul[0] == np.datetime64(T("2024-06-01")))
    print(f"  자체 시험 실패 {fails}건")
    return fails


def main():
    ap = argparse.ArgumentParser(description="ARGUS BT FRED 열 발표일 정렬 재구성")
    ap.add_argument("--input")
    ap.add_argument("--output")
    ap.add_argument("--mode", choices=["alfred", "calendar"], default="calendar")
    ap.add_argument("--cache", default="fred_alfred_cache")
    ap.add_argument("--nan-frozen", action="store_true", help="장기 동결 구간을 NaN 처리")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(1 if selftest() else 0)
    if not a.input or not a.output:
        ap.error("--input 과 --output 이 필요하다")
    src, dst = Path(a.input), Path(a.output)
    if src.resolve() == dst.resolve():
        raise ValueError("출력은 원본과 다른 경로여야 한다")
    for p in (dst, dst.with_suffix(".pit_obs.csv"), dst.with_suffix(".manifest.json")):
        if p.exists():
            raise ValueError(f"기존 결과를 덮어쓰지 않는다: {p}")
    key = os.getenv("FRED_API_KEY", "")
    if a.mode == "alfred" and not key:
        raise SystemExit("alfred 방식에는 FRED_API_KEY 가 필요하다")
    if selftest():
        raise SystemExit("자체 시험 실패 — 재구성 중단")
    print(f"🦅 {VERSION} · 방식 {a.mode} · 입력 {src.name}")
    df = pd.read_csv(src, parse_dates=["Date"], index_col="Date", low_memory=False)
    out, obs_log, man = rebuild(df, a.mode, key, Path(a.cache), a.nan_frozen)
    # 불변식: 어떤 결정일도 결정일 이후 관측을 쓰지 않는다
    viol = {c: int((obs_log[c] >= obs_log.index).sum()) for c in obs_log.columns}
    viol = {c: n for c, n in viol.items() if n}
    if viol:
        # 진단용: 본 CSV 는 쓰지 않고 매니페스트·관측일 로그만 남긴다 (아티팩트로 회수)
        dst.parent.mkdir(parents=True, exist_ok=True)
        obs_log.to_csv(dst.with_suffix(".pit_obs.csv"), index_label="Date")
        man.update(input=src.name, status="FAILED_INVARIANT", invariant_violations=viol)
        dst.with_suffix(".manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
        raise SystemExit(f"불변식 위반 (미래 관측): {viol}")
    # 가격·기타 열은 손대지 않았음을 확인
    untouched = [c for c in df.columns if c not in SPEC and c != "Net_Liquidity"
                 and not (a.nan_frozen and c in man["frozen_runs"])]
    diff = [c for c in untouched if not df[c].equals(out[c])]
    if diff:
        raise SystemExit(f"대상 외 열 변경 감지: {diff[:5]}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(dst, index_label="Date")
    obs_log.to_csv(dst.with_suffix(".pit_obs.csv"), index_label="Date")
    man.update(status="OK", input=src.name, input_sha12=sha12(src), output=dst.name, output_sha12=sha12(dst),
               rows=int(len(out)), cols=int(out.shape[1]), untouched_cols_verified=len(untouched),
               generated_utc=pd.Timestamp.now("UTC").isoformat())
    dst.with_suffix(".manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 출력 {dst.name} · {len(out)}행 × {out.shape[1]}열 · sha {man['output_sha12']}")
    for c, runs in man["frozen_runs"].items():
        for r in runs:
            print(f"  🧊 동결 {c}: {r['start']}~{r['end']} ({r['days']}일, 값 {r['value']}) → {man['frozen_action']}")


if __name__ == "__main__":
    main()
