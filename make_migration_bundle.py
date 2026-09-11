# -*- coding: utf-8 -*-
"""
ARGUS Migration Dependency Bundle 생성기 v2.0  —  PHASE A (PREPARE)
─────────────────────────────────────────────────────────────────────
이 스크립트는 마이그레이션 4단계 중 **네트워크가 허용되는 유일한 단계**다.

    PHASE A  PREPARE   [network allowed]   ← 이 파일
    PHASE B  BASELINE REPLAY [network OFF] ┐
    PHASE C  MIGRATE         [network OFF] ┤ argus_data_fetcher (CALENDAR_MIGRATION_MODE=1)
    PHASE D  VERIFY                        ┘

왜 이렇게 하는가
    목표는 `Crown Δ = calendar migration effect` 를 성립시키는 것이다.
    그러려면 before 와 after 가 **오직 캘린더만** 달라야 한다.
    결측 세션 복구는 그 자체가 Yahoo historical retrieval 이므로, 마이그레이션 중에 하면
    '무네트워크' 가 성립하지 않는다. 그래서 여기서 미리 얼려 둔다.

동결 대상 (전량 필수 — 부분 번들 금지)
    ① 결측 정규장 세션 × MARKET_IMMUTABLE 전 열   → missing_market.csv
    ② MU · HYG · LQD 가격 (SMH_TRIFLAG 의존)       → smh_prices.csv
    ③ wsts_yoy.json                                → wsts_yoy.json  (루트 fallback 금지)
    ④ manifest.json — 위 3종 sha256 + 원본 CSV sha256

사용
    python make_migration_bundle.py
    python make_migration_bundle.py --years 7 --fetcher argus_data_fetcher.py

SSOT
    세션 캘린더 · MARKET_IMMUTABLE 목록 · exact-date 회수는 **fetcher 모듈에서 직접 import** 한다.
    여기에 사본을 만들지 않는다 — 사본을 만드는 순간 둘이 갈라진다.
"""
import argparse, hashlib, importlib.util, json, os, sys
from datetime import datetime, timezone

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLE_DIR = os.path.join(SCRIPT_DIR, "migration_inputs")
SMH_SYMBOLS = ["MU", "HYG", "LQD"]


def sha256_of(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_fetcher(path):
    spec = importlib.util.spec_from_file_location("argus_fetcher_for_bundle", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description="ARGUS Migration Dependency Bundle 생성 (PHASE A)")
    ap.add_argument("--years", type=float, default=5.0, help="MU/HYG/LQD 이력 연수 (기본 5)")
    ap.add_argument("--fetcher", default="argus_data_fetcher.py", help="fetcher 파일명")
    args = ap.parse_args()

    fetcher_path = os.path.join(SCRIPT_DIR, args.fetcher)
    if not os.path.exists(fetcher_path):
        print(f"🔴 fetcher 없음: {fetcher_path}")
        return 1
    try:
        import yfinance as yf  # noqa: F401
    except ImportError:
        print("🔴 yfinance 미설치 — 번들 생성 불가")
        return 1

    print(f"📦 PHASE A — PREPARE  (fetcher={args.fetcher})")
    F = load_fetcher(fetcher_path)

    src_csv = F.OUTPUT_PATH
    if not os.path.exists(src_csv):
        print(f"🔴 원본 CSV 없음: {src_csv}")
        return 1
    src_sha = sha256_of(src_csv)
    print(f"  원본 CSV sha256 {src_sha[:16]}…")

    df = pd.read_csv(src_csv, index_col=0, parse_dates=True)
    df.index.name = "Date"

    # ── ① 결측 정규장 세션 탐지 (fetcher 의 캘린더 SSOT 사용) ──
    snap = F._calendar_integrity_snapshot(df, "bundle_prepare")
    if not str(snap.get("calendar_source") or "").startswith("exchange_calendars:"):
        print(f"🔴 캘린더 소스가 1순위가 아니다 ({snap.get('calendar_source')}) — 번들 생성 중단")
        print("   처방: requirements 에 exchange-calendars 를 고정 버전으로 설치 후 재실행")
        return 1
    missing = list(snap.get("missing_dates") or [])
    ghost = list(snap.get("ghost_dates") or [])
    print(f"  캘린더 감사: 유령 {len(ghost)}건 · 결측 {len(missing)}건 "
          f"({snap.get('calendar_source')})")

    os.makedirs(BUNDLE_DIR, exist_ok=True)
    files = {}

    # ── ② 결측 세션 × MARKET_IMMUTABLE 동결 ──
    mkt = F._market_repair_map()
    cols = [c for c in mkt if c in df.columns]
    mm_path = os.path.join(BUNDLE_DIR, "missing_market.csv")
    if missing:
        print(f"  📥 결측 세션 {len(missing)}일 × MARKET_IMMUTABLE {len(cols)}열 회수")
        rows, incomplete = {}, {}
        for ds in missing:
            d = pd.Timestamp(ds).date()
            vals, miss = {}, []
            for col in cols:
                v = F.yf_value_on_exact_date(mkt[col], d)
                if v is None:
                    miss.append(col)
                else:
                    vals[col] = v
            rows[pd.Timestamp(d)] = vals
            if miss:
                incomplete[str(d)] = miss
            print(f"     {d}  {len(vals)}/{len(cols)}열")
        if incomplete:
            print("🔴 결측 세션 동결 불완전 — 번들 생성 중단 (부분 번들 금지)")
            for k, v in incomplete.items():
                print(f"     {k}: 누락 {v[:12]}")
            print("   MARKET_IMMUTABLE 은 전일값 대체를 허용하지 않으므로 "
                  "이 상태로는 마이그레이션이 fail-closed 된다.")
            return 1
        mm = pd.DataFrame.from_dict(rows, orient="index")[cols].sort_index()
        mm.index.name = "Date"
        mm.to_csv(mm_path)
        files["missing_market.csv"] = sha256_of(mm_path)
        print(f"  💾 {mm_path}  {len(mm)}행 × {len(mm.columns)}열")
    else:
        if os.path.exists(mm_path):
            os.remove(mm_path)
        print("  ⏭️ 결측 세션 없음 — missing_market.csv 생략")

    # ── ③ MU/HYG/LQD 동결 ──
    start = (pd.Timestamp.now() - pd.Timedelta(days=int(365.25 * args.years))).strftime("%Y-%m-%d")
    print(f"  📥 MU · HYG · LQD 가격 회수 ({start} ~)")
    import yfinance as yf
    raw = yf.download(SMH_SYMBOLS, start=start, progress=False, auto_adjust=True)
    if raw is None or len(raw) == 0:
        print("🔴 가격 회수 실패 — 번들 생성 중단 (fail-closed)")
        return 1
    close = raw["Close"] if hasattr(raw.columns, "levels") else raw
    absent = [s for s in SMH_SYMBOLS if s not in close.columns]
    if absent:
        print(f"🔴 심볼 누락 {absent} — 번들 생성 중단 (부분 번들 금지)")
        return 1
    close = close[SMH_SYMBOLS].copy()
    close.index = pd.to_datetime(close.index)
    if close.index.tz is not None:
        close.index = close.index.tz_localize(None)
    close.index = close.index.normalize()
    close.index.name = "Date"
    close = close.dropna(how="all").sort_index()
    # 🔧 v2.1 [P1-14] 컬럼 존재만으로는 부족하다. 유효 관측량을 fetcher 의 상수로 검사한다.
    #   MU 만 1000행이고 LQD 가 전부 NaN 이어도 '완전한 번들' 로 통과하면
    #   SMH_TRIFLAG 가 조용히 거의 전부 0 이 된다.
    min_rows = getattr(F, "SMH_BUNDLE_MIN_ROWS", 400)
    for s in SMH_SYMBOLS:
        n = int(pd.to_numeric(close[s], errors="coerce").notna().sum())
        if n < min_rows:
            print(f"🔴 {s} 유효 {n}행 < 최소 {min_rows}행 — 번들 생성 중단")
            print("   126일 momentum + 189일 rolling warm-up 을 채우지 못한다. --years 를 늘릴 것.")
            return 1
        print(f"     {s} 유효 {n}행 ✅")
    if close.index.has_duplicates or not close.index.is_monotonic_increasing:
        print("🔴 가격 인덱스 중복 또는 비단조 — 번들 생성 중단")
        return 1
    px_path = os.path.join(BUNDLE_DIR, "smh_prices.csv")
    close.to_csv(px_path)
    files["smh_prices.csv"] = sha256_of(px_path)
    print(f"  💾 {px_path}  {len(close)}행 "
          f"({close.index[0].date()} ~ {close.index[-1].date()})")

    # ── ④ WSTS 동결 (필수) ──
    src_wsts = os.path.join(SCRIPT_DIR, "wsts_yoy.json")
    if not os.path.exists(src_wsts):
        print("🔴 wsts_yoy.json 없음 — 번들 생성 중단 (fail-closed)")
        print("   v3.9.12 는 레포 루트 fallback 을 금지한다. 번들 생성과 마이그레이션 사이에")
        print("   upstream 이 wsts 를 바꾸면 Crown Δ 에 dependency change 가 섞이기 때문이다.")
        return 1
    dst_wsts = os.path.join(BUNDLE_DIR, "wsts_yoy.json")
    with open(src_wsts, "rb") as a, open(dst_wsts, "wb") as b:
        b.write(a.read())
    try:
        ws = F.parse_wsts_yoy_json(dst_wsts)
    except Exception as e:
        print(f"🔴 wsts_yoy.json 파싱 실패 ({type(e).__name__}: {e}) — 번들 생성 중단")
        return 1
    if ws is None or len(ws) == 0:
        print("🔴 wsts_yoy.json 시리즈 0건 — 번들 생성 중단")
        return 1
    files["wsts_yoy.json"] = sha256_of(dst_wsts)
    print(f"  💾 {dst_wsts}  PIT 시리즈 {len(ws)}건 "
          f"({ws.index[0].date()} ~ {ws.index[-1].date()})")

    # ── ⑤ manifest ──
    manifest = {
        "bundle_version": "2.0",
        "phase": "A_PREPARE",
        "purpose": "calendar migration 의 before/after 를 동일 입력으로 계산하기 위한 동결본",
        "source_csv": os.path.basename(src_csv),
        "source_csv_sha256": src_sha,
        "source_csv_rows": int(len(df)),
        "calendar_source": snap.get("calendar_source"),
        "ghost_dates": ghost,
        "missing_dates": missing,
        "smh_symbols": SMH_SYMBOLS,
        "smh_observed_through": str(close.index[-1].date()),
        "wsts_entries": int(len(ws)),
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_sha256": files,
        "note": "fetcher 는 이 해시를 현재 파일과 대조한다. 불일치 시 fail-closed. "
                "원본 CSV 해시도 대조하므로 CSV 가 바뀌면 번들을 다시 만들어야 한다.",
    }
    mf_path = os.path.join(BUNDLE_DIR, "manifest.json")
    with open(mf_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"  💾 {mf_path}")

    print("\n✅ PHASE A 완료 — 동결 파일")
    for k, v in files.items():
        print(f"   {k:22s} sha256 {v[:16]}…")
    print(f"   원본 CSV               sha256 {src_sha[:16]}…")
    print("\n다음 단계")
    print("   CALENDAR_MIGRATION_MODE=1 python argus_data_fetcher.py")
    print("   → 로그에서 external_network_calls = 0 확인 (가드 범위: 트랜잭션 전체)")
    print("   → Crown 대조: BEFORE = migration_baseline_frozen.csv / AFTER = argus_data.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
