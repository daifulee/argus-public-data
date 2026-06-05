#!/usr/bin/env python3
"""
🦅 ARGUS latest.json 생성기 v1.0 (argus-public-data self-update 정합)
argus_data.csv 마지막 행 → 단일 객체 latest.json (기존 형식 보존, 격언 #105)

기존 latest.json 형식 (실측 검증 완료 — 불일치 0건, 키 104/104 일치):
  - 단일 dict (list 아님)
  - Date        : "YYYY-MM-DD" 문자열 (시간 제거)
  - 수치 컬럼    : float (반올림 없음, 원본 정밀도 보존)
  - 문자열 컬럼  : str  (예: VIX_source='yahoo_live', F_G_Rating='greed')
  - bool 컬럼    : bool
  - 결측(NaN)    : null (예: XLE_BullStack)

사용:
  python make_latest_json.py        # ./argus_data.csv → ./latest.json
"""
import json
import os

import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "argus_data.csv")
JSON_PATH = os.path.join(SCRIPT_DIR, "latest.json")


def to_jsonable(v):
    """스칼라 값을 JSON 직렬화 형식으로 변환 (기존 형식 보존).

    우선순위: 결측 → null / bool → bool / 숫자 → float / 그 외 → str
    bool 을 숫자보다 먼저 검사한다 (float(True)=1.0 오변환 방지).
    """
    # 결측 (np.nan / None) → null
    if pd.isna(v):
        return None
    # bool (파이썬 bool + numpy bool) → bool
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    # 숫자 → float (반올림 없음). 실패 시 문자열로 처리
    try:
        return float(v)
    except (ValueError, TypeError):
        return str(v)


def build_latest(csv_path: str) -> dict:
    """argus_data.csv 마지막 행을 단일 객체(dict)로 변환."""
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True).sort_index()
    if len(df) == 0:
        raise SystemExit("🚨 argus_data.csv 행 없음 — latest.json 생성 중단")

    last = df.iloc[-1]
    # Date: 인덱스 마지막 → 날짜만 (시간 제거)
    rec = {"Date": df.index[-1].strftime("%Y-%m-%d")}
    for col in df.columns:
        rec[col] = to_jsonable(last[col])
    return rec


def main():
    rec = build_latest(CSV_PATH)
    # indent=2: argus_ecy_fetcher_v2 주입 포맷과 일관 (기존 형식 보존)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    n_null = sum(1 for v in rec.values() if v is None)
    print(f"✅ latest.json 생성 완료: Date={rec['Date']}, "
          f"키 {len(rec)}개 (null {n_null}개) → {JSON_PATH}")


if __name__ == "__main__":
    main()
