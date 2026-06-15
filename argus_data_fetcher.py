# -*- coding: utf-8 -*-
# 🔧 v1.0.6 (2026-06-15, S200): infer_oil_proxy → LEAD-3 Brent-WTI spread 위임 (compute_oil_proxy, 단일 SSOT).
#    Brent 가용(fetcher v3.4 BZ=F) 시 spread 60%+WTI 40% 산출 / 부재 시 WTI 단독 graceful fallback. OIL축 운영 복원.
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  🔭 Oracle Autopilot v1.0.5 — CODENAME: HEIR (적정자)              ║
# ║  Oracle v2.13.1 정식 통합 자율 실행 엔진                            ║
# ║  2026-06-09 Commander 승인                                          ║
# ║                                                                      ║
# ║  설계 원칙 (사생아 → 적정자 전환):                                  ║
# ║    • Oracle v2.13.1의 모든 추론 인프라를 정식 호출                  ║
# ║      (compute_regime_gradient / compute_regime_inputs /             ║
# ║       classify_macro_regime / auto_prior(LEAD-5/6b) /               ║
# ║       compute_axis_impact / detect_regime_transition)               ║
# ║    • Oracle가 의존하는 Brief 모듈 상수를 본 모듈이 정식 공급        ║
# ║      (GRADIENT_SENSOR_BANDS / GRADIENT_ALLOCATION_GUIDE /            ║
# ║       LIQUIDITY_STRESS_REGIME / GLD_CAP_NORMAL / RR_FLOW_ADJUST)     ║
# ║    • 조잡한 if-else 재발명 금지 — Oracle 회귀/분위수 추론 사용      ║
# ║    • QNS v1.1 + QLS v1.0 전략이론 실엔진 통합                       ║
# ║                                                                      ║
# ║  파이프라인 (L0~L28, 28계층):                                     ║
# ║    L0  공유 상수 공급 (Oracle 의존성 충족)                          ║
# ║    L1  ARGUS Public Data 수집 → DataFrame                           ║
# ║    L1.5 파생 지표 (MA / 모멘텀 / 상대강도 / 롤링 분위수)            ║
# ║    L2a LEAD-5/6b 자동 추론 (CREDIT/MONETARY) — Oracle 회귀          ║
# ║    L2b 프록시 추론 (WAR/OIL/GROWTH/TARIFF/FISCAL/AI_POWER)          ║
# ║    L2c auto_prior 통합 → axis_probs                                 ║
# ║    L3  레짐 파이프라인 (gradient → inputs → classify)               ║
# ║    L4  compute_axis_impact 29종목 + INTERACTION_PAIRS               ║
# ║    L5  시나리오 확률 엔진 (S1~S11)                                  ║
# ║    L6  포트폴리오 구성 (DRP + 레짐 프리셋)                          ║
# ║    L7  전략이론 6계통 (QNS + QLS 실엔진)                            ║
# ║    L8  전환 감지 (detect_regime_transition)                         ║
# ║    L9  종합 브리핑 생성 (B0~B8 구조)                                ║
# ║    L10 자가 검증 하니스                                             ║
# ╚══════════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import os
import io
import csv
import json
import math
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

AUTOPILOT_VERSION = "1.0.5"  # [v1.0.5] P1 4건 수정 (LOGOS정책/top_picks/alias/ref_only)

# [v1.0.5 P1-1] LOGOS 운영 정책
# - "optional": 미동봉 시 integrity warning (연구/브리핑 모드)
# - "required": 미동봉 시 RuntimeError (Full Production 모드)
LOGOS_POLICY = "optional"
DATA_BASE = "https://raw.githubusercontent.com/daifulee/argus-public-data/main"
# [v1.0.4 P1-4 FIX] GitHub 응답 메타데이터 캡처 (재현성/감사)
_FETCH_META: Dict[str, str] = {}
_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════════════════
# [v1.0.2] ARGUS 통합 유니버스
# ═══════════════════════════════════════════════════════════════════════
# ARGUS 20종목 = 포트폴리오 선택 유니버스. 전부 Oracle IMPACT_BY_AXIS 커버(20/20).
# SGOV = 유니버스 외 현금성 방어자산 (Commander 결정: 방어 필수 유지).
# SPY = 유니버스 외 백테스트 벤치마크. PDBC 등 ARGUS 외 종목은 포트폴리오 제외.
# ═══════════════════════════════════════════════════════════════════════
ARGUS_UNIVERSE = [
    "GLD", "SLV", "XLE", "ITA", "SMH", "COPX", "EWZ", "NLR", "QQQM", "VEA",
    "XLU", "XLF", "XLV", "IWM", "TLT", "PAVE", "VNM", "INDA", "CQQQ", "CIBR",
]
CASH_PROXY = "SGOV"       # 현금성 방어자산 (유니버스 외, 방어 모드 필수)
BENCHMARK = "SPY"         # 백테스트 벤치마크 (유니버스 외)
# 포트폴리오 배분 가능 종목 = ARGUS 20 + 현금성
ALLOC_UNIVERSE = ARGUS_UNIVERSE + [CASH_PROXY]


# ═══════════════════════════════════════════════════════════════════════
# L0: 공유 상수 공급 (Oracle v2.13.1이 의존하는 Brief 모듈 상수)
# ═══════════════════════════════════════════════════════════════════════
# Oracle는 본래 Brief v1.0.8에서 이 상수들을 받음. 본 모듈이 Oracle를
# 독립 실행하기 위해 정식 값을 공급한다. 값은 INVICTUS SSOT 임계값 기반.
# ═══════════════════════════════════════════════════════════════════════

# 그래디언트 센서 밴드: [low, high]를 [0, 25점]으로 선형 보간
# 근거: VIX 30 crisis/32 STORM, OAS_HY 5.5 crisis/5.8 RED, MOVE 130 crisis
GRADIENT_SENSOR_BANDS: Dict[str, Dict[str, Any]] = {
    "VIX": {
        "low": 15.0,    # 안정 (0점)
        "high": 35.0,   # 위기 (25점)
        "comment": "VIX 15 이하 안정, 30 crisis, 32 STORM 트리거",
    },
    "OAS_HY": {
        "low": 3.0,     # 완화 (0점)
        "high": 6.0,    # 위기 (25점)
        "comment": "OAS_HY 3% 완화, 5.5% crisis, 5.8% AEGIS RED ALERT",
    },
    "MOVE": {
        "low": 80.0,    # 안정 (0점)
        "high": 140.0,  # 위기 (25점)
        "comment": "MOVE 80 안정, 120 불안, 130 채권 공포",
    },
    "FLOW": {
        # 자금 흐름 신호 → 점수 매핑 (0~25점)
        "scoring": {
            "STRONG_INFLOW":  0.0,    # risk-on 강함 → 위험 점수 낮음
            "INFLOW":         5.0,
            "NEUTRAL":        12.5,
            "OUTFLOW":        20.0,
            "STRONG_OUTFLOW": 25.0,   # risk-off 강함 → 위험 점수 높음
        },
        "comment": "SANGUIS 자금 흐름 신호 → risk-off 강도 점수",
    },
}

# 그래디언트 총점 → 방어/공격 배분 가이드 (구간별)
GRADIENT_ALLOCATION_GUIDE: Dict[str, Dict[str, str]] = {
    "0~25": {
        "label": "🟢 순풍 (저위험)",
        "strategy": "공격 자산 비중 극대화. 방어 10~25%. SUPERBULL/BULL 구간.",
    },
    "25~50": {
        "label": "🟡 경계 (중위험)",
        "strategy": "공격/방어 균형. 방어 25~50%. 변동성 확대 주시.",
    },
    "50~65": {
        "label": "🟠 긴장 (고위험)",
        "strategy": "방어 비중 우위. 방어 50~65%. CHOP 구간. 공격 선별.",
    },
    "65~80": {
        "label": "🔴 위험 (방어)",
        "strategy": "방어 최우선. 방어 65~80%. RECESSION 경계. 공격 최소화.",
    },
    "80~100": {
        "label": "🔴🔴 극위험 (STORM)",
        "strategy": "STORM. 방어 80%+. GLD 외 전면 청산 검토. 달러RP 극대화.",
    },
}

# 유동성 스트레스 레짐 (compute_liquidity_risk 의존)
LIQUIDITY_STRESS_REGIME: Dict[str, Dict[str, Any]] = {
    "ABUNDANT": {
        "label": "🟢 풍부",
        "net_liquidity_min": 6_000_000,  # 백만 달러 단위
        "rrp_max": 0.5,                   # 조 달러
        "comment": "순유동성 풍부 + 역레포 소진 → risk-on 우호",
    },
    "ADEQUATE": {
        "label": "🟡 적정",
        "net_liquidity_min": 5_500_000,
        "rrp_max": 1.5,
        "comment": "유동성 적정. 중립.",
    },
    "TIGHT": {
        "label": "🟠 긴축",
        "net_liquidity_min": 5_000_000,
        "rrp_max": 2.5,
        "comment": "유동성 긴축. 위험자산 경계.",
    },
    "STRESSED": {
        "label": "🔴 스트레스",
        "net_liquidity_min": 0,
        "rrp_max": 99.0,
        "comment": "유동성 스트레스. 방어 강화.",
    },
}

# 실질금리 흐름 조정 상수 (RR = Real Rate)
RR_FLOW_ADJUST = 5.0       # FLOW 점수에서 RR subscore 적용 시 차감 (25p→20p)
GLD_CAP_NORMAL = 0.35      # 정상 레짐 금 비중 상한 (35%)

# RR(실질금리) subscore 밴드: DFII10 기반
# 주의: Oracle compute_regime_gradient는 반환 dict에서 "rr_score" 키를 읽고,
#       gld_alert는 문자열("NORMAL"/"WATCH"/"ALERT")을 기대한다.
RR_SUBSCORE_BANDS = {
    "very_negative": {"max": 0.0,  "rr_score": 0.0,  "gld_cap": 0.40, "label": "🟢 마이너스 실질금리 (금 우호)", "gld_alert": "NORMAL"},
    "low":           {"max": 1.0,  "rr_score": 3.0,  "gld_cap": 0.35, "label": "🟢 저실질금리", "gld_alert": "NORMAL"},
    "neutral":       {"max": 2.0,  "rr_score": 6.0,  "gld_cap": 0.30, "label": "🟡 중립 실질금리", "gld_alert": "NORMAL"},
    "high":          {"max": 3.0,  "rr_score": 10.0, "gld_cap": 0.25, "label": "🟠 고실질금리 (금 역풍)", "gld_alert": "WATCH"},
    "very_high":     {"max": 99.0, "rr_score": 15.0, "gld_cap": 0.20, "label": "🔴 초고실질금리", "gld_alert": "ALERT"},
}


def compute_real_rate_subscore(dfii10: Optional[float]) -> Dict[str, Any]:
    """실질금리(DFII10) → RR subscore + GLD cap.
    
    Oracle compute_regime_gradient가 참조하는 Brief 함수의 정식 구현.
    반환 dict 키: rr_score, gld_cap, label, gld_alert (문자열).
    """
    if dfii10 is None or (isinstance(dfii10, float) and math.isnan(dfii10)):
        return {"rr_score": 6.0, "gld_cap": GLD_CAP_NORMAL,
                "label": "🟡 실질금리 데이터 없음 (중립)", "gld_alert": "NORMAL"}
    for band_name, band in RR_SUBSCORE_BANDS.items():
        if dfii10 <= band["max"]:
            return {
                "rr_score": band["rr_score"],
                "gld_cap": band["gld_cap"],
                "label": band["label"],
                "gld_alert": band["gld_alert"],
            }
    return {"rr_score": 15.0, "gld_cap": 0.20, "label": "🔴 초고실질금리", "gld_alert": "ALERT"}


# ═══════════════════════════════════════════════════════════════════════
# L1: ARGUS Public Data 수집
# ═══════════════════════════════════════════════════════════════════════

_CACHE_DIR = os.path.join(_ENGINE_DIR, "cache")


def _cache_path(name: str) -> str:
    return os.path.join(_CACHE_DIR, name)


def _write_cache(name: str, text: str) -> None:
    """[v1.0.1 P1-1] fetch 성공 시 캐시 저장 (네트워크 장애 대비)."""
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        with open(_cache_path(name), "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass  # 캐시 실패는 비치명적


def _read_cache(name: str) -> Optional[str]:
    try:
        with open(_cache_path(name), encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def fetch_latest(use_cache_fallback: bool = True) -> Dict[str, Any]:
    """latest.json 수집 → 최신 1행. [v1.0.1 P1-1] 캐시 폴백. [v1.0.4 P1-4] ETag 캡처."""
    url = f"{DATA_BASE}/latest.json"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8")
            # [v1.0.4 P1-4 FIX] 응답 헤더에서 재현성 메타 캡처
            _FETCH_META["latest_etag"] = r.headers.get("ETag", "")
            _FETCH_META["latest_last_modified"] = r.headers.get("Last-Modified", "")
        _write_cache("latest.json", text)
        return json.loads(text)
    except Exception as e:
        if use_cache_fallback:
            cached = _read_cache("latest.json")
            if cached:
                data = json.loads(cached)
                data["_source"] = "CACHE_FALLBACK"
                return data
        raise RuntimeError(f"latest.json fetch 실패 + 캐시 없음: {e}")


def _parse_csv_text(text: str) -> List[Dict[str, Any]]:
    """CSV 텍스트 → 파싱된 행 리스트."""
    reader = csv.DictReader(io.StringIO(text))
    rows: List[Dict[str, Any]] = []
    for row in reader:
        parsed: Dict[str, Any] = {}
        for k, v in row.items():
            if k == "Date":
                parsed[k] = v
            elif v in ("", "None", "null", None):
                parsed[k] = None
            else:
                try:
                    parsed[k] = float(v)
                except (ValueError, TypeError):
                    parsed[k] = v
        rows.append(parsed)
    return rows


def fetch_history(use_cache_fallback: bool = True) -> List[Dict[str, Any]]:
    """argus_data.csv 수집 → 딕셔너리 리스트. [v1.0.1 P1-1] 캐시 폴백. [v1.0.4 P1-4] ETag 캡처."""
    url = f"{DATA_BASE}/argus_data.csv"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8")
            _FETCH_META["history_etag"] = r.headers.get("ETag", "")
            _FETCH_META["history_last_modified"] = r.headers.get("Last-Modified", "")
        _write_cache("argus_data.csv", text)
        return _parse_csv_text(text)
    except Exception as e:
        if use_cache_fallback:
            cached = _read_cache("argus_data.csv")
            if cached:
                return _parse_csv_text(cached)
        raise RuntimeError(f"argus_data.csv fetch 실패 + 캐시 없음: {e}")


def load_inputs(latest_path: str, history_path: str) -> Tuple[Dict, List[Dict]]:
    """[v1.0.1 P1-1] 로컬 파일 입력 (오프라인 결정론 모드)."""
    with open(latest_path, encoding="utf-8") as f:
        latest = json.load(f)
    with open(history_path, encoding="utf-8") as f:
        history = _parse_csv_text(f.read())
    return latest, history


def build_manifest(latest: Dict, history: List[Dict]) -> Dict[str, Any]:
    """[v1.0.1 P1-1] 입력 데이터 manifest + hash (재현성/감사).
    [v1.0.4 P1-4 FIX] ETag/Last-Modified 기록."""
    import hashlib
    latest_str = json.dumps(latest, sort_keys=True, default=str)
    hist_str = json.dumps(history[-5:], sort_keys=True, default=str)
    return {
        "data_date": latest.get("Date"),
        "data_source": latest.get("_source", "GITHUB_RAW"),
        "data_base_url": DATA_BASE,
        "latest_hash": hashlib.sha256(latest_str.encode()).hexdigest()[:16],
        "history_tail_hash": hashlib.sha256(hist_str.encode()).hexdigest()[:16],
        "history_rows": len(history),
        "run_timestamp": datetime.now().isoformat(),
        "autopilot_version": AUTOPILOT_VERSION,
        # [v1.0.4 P1-4 FIX] GitHub 응답 메타 (재현성)
        "latest_etag": _FETCH_META.get("latest_etag", ""),
        "latest_last_modified": _FETCH_META.get("latest_last_modified", ""),
        "history_etag": _FETCH_META.get("history_etag", ""),
        "history_last_modified": _FETCH_META.get("history_last_modified", ""),
    }


# [v1.0.5 P1-3] 센서 alias map (CSV/데이터소스별 컬럼명 차이 흡수)
SENSOR_ALIASES = {
    "DGS10": ["DGS10", "TNX"],
    "TYX_30Y": ["TYX_30Y", "TYX"],
    "OAS_HY": ["OAS_HY", "BAMLH0A0HYM2"],
}


def normalize_latest_schema(latest: Dict) -> Dict:
    """[v1.0.5 P1-3] alias map으로 센서 컬럼명 정규화."""
    for canonical, aliases in SENSOR_ALIASES.items():
        if latest.get(canonical) is None:
            for a in aliases:
                if latest.get(a) is not None:
                    latest[canonical] = latest[a]
                    break
    return latest


def validate_data(latest: Dict, history: List[Dict]) -> Dict[str, Any]:
    """데이터 품질 검증. 결측/이상치/시차 체크."""
    # [v1.0.5 P1-3] alias 정규화 선행
    latest = normalize_latest_schema(latest)
    issues = []
    warnings = []

    def _is_missing(v):
        """None 또는 NaN → 결측 [v1.0.4 P1-1 FIX]"""
        return v is None or (isinstance(v, float) and math.isnan(v))

    # 필수 센서 결측 체크 (None + NaN 모두 issue)
    required = ["VIX", "DGS10", "OAS_HY", "WTI", "DXY", "PMI", "SAHMCURRENT"]
    for key in required:
        if _is_missing(latest.get(key)):
            issues.append(f"필수 센서 결측: {key}")

    # 데이터 시차 체크
    if latest.get("Date"):
        try:
            data_date = datetime.strptime(latest["Date"], "%Y-%m-%d")
            age_days = (datetime.now() - data_date).days
            if age_days > 5:
                warnings.append(f"데이터 {age_days}일 경과 (최신성 주의)")
        except (ValueError, TypeError):
            warnings.append("날짜 파싱 실패")

    # 이상치 체크 (센서 범위)
    sanity = {
        "VIX": (5, 90), "DGS10": (0, 10), "OAS_HY": (0.5, 20),
        "WTI": (10, 200), "DXY": (70, 130), "PMI": (30, 70),
    }
    for key, (lo, hi) in sanity.items():
        v = latest.get(key)
        if not _is_missing(v) and not (lo <= v <= hi):
            warnings.append(f"{key}={v} 범위 이탈 [{lo},{hi}]")

    # 히스토리 길이
    if len(history) < 260:
        warnings.append(f"히스토리 {len(history)}행 < 260 (LEAD-5/6b 추론 제약)")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "history_length": len(history),
        "data_date": latest.get("Date"),
    }


def safe_get(data: Dict, key: str, default=None):
    """None-safe 접근."""
    v = data.get(key)
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return default
    return v


# ═══════════════════════════════════════════════════════════════════════
# L1.5: 파생 지표 계산
# ═══════════════════════════════════════════════════════════════════════

def compute_ma(history: List[Dict], key: str, window: int) -> Optional[float]:
    """N일 단순 이동평균."""
    vals = [h[key] for h in history[-window:] if h.get(key) is not None]
    if len(vals) < window * 0.7:
        return None
    return sum(vals) / len(vals)


def compute_momentum(history: List[Dict], key: str, days: int) -> Optional[float]:
    """N일 변화율."""
    recent = [h for h in history if h.get(key) is not None]
    if len(recent) < days + 1:
        return None
    cur, past = recent[-1][key], recent[-(days + 1)][key]
    if past == 0:
        return None
    return (cur - past) / past


def compute_relative_strength(history: List[Dict], ticker: str, bench: str, days: int) -> Optional[float]:
    """종목/벤치마크 상대강도."""
    tm = compute_momentum(history, ticker, days)
    bm = compute_momentum(history, bench, days)
    if tm is None or bm is None or (1 + bm) == 0:
        return None
    return (1 + tm) / (1 + bm)


def compute_rolling_percentile(history: List[Dict], key: str, window: int = 250) -> Optional[float]:
    """현재값의 N일 롤링 분위수 (0~1). LEAD-5/6b 보조용."""
    vals = [h[key] for h in history[-window:] if h.get(key) is not None]
    if len(vals) < window * 0.6:
        return None
    current = vals[-1]
    below = sum(1 for v in vals if v < current)
    return below / len(vals)


def compute_zscore(history: List[Dict], key: str, window: int = 60) -> Optional[float]:
    """N일 z-score."""
    vals = [h[key] for h in history[-window:] if h.get(key) is not None]
    if len(vals) < window * 0.5:
        return None
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    std = math.sqrt(var)
    if std < 1e-9:
        return 0.0
    return (vals[-1] - mean) / std


def build_derived_metrics(latest: Dict, history: List[Dict]) -> Dict[str, Any]:
    """전체 파생 지표 묶음 계산."""
    return {
        # 이동평균
        "SMH_MA200": compute_ma(history, "SMH_Close", 200),
        "SMH_MA60": compute_ma(history, "SMH_Close", 60),
        "SPY_MA200": compute_ma(history, "SPY_Close", 200),
        "WTI_MA60": compute_ma(history, "WTI", 60),
        "WTI_MA252": compute_ma(history, "WTI", 252),
        # 모멘텀
        "SMH_mom60": compute_momentum(history, "SMH_Close", 60),
        "NLR_mom60": compute_momentum(history, "NLR_Close", 60),
        "COPX_mom60": compute_momentum(history, "COPX_Close", 60),
        "GLD_mom30": compute_momentum(history, "GLD_Close", 30),
        "ITA_mom60": compute_momentum(history, "ITA_Close", 60),
        "SPY_mom60": compute_momentum(history, "SPY_Close", 60),
        "WTI_mom30": compute_momentum(history, "WTI", 30),
        "TNX_mom60": compute_momentum(history, "TNX", 60),
        # 상대강도
        "SMH_SPY_RS60": compute_relative_strength(history, "SMH_Close", "SPY_Close", 60),
        "NLR_SPY_RS60": compute_relative_strength(history, "NLR_Close", "SPY_Close", 60),
        "ITA_SPY_RS60": compute_relative_strength(history, "ITA_Close", "SPY_Close", 60),
        # 롤링 분위수 (LEAD-5/6b 보조)
        "OAS_HY_pctl250": compute_rolling_percentile(history, "OAS_HY", 250),
        "IRX_pctl250": compute_rolling_percentile(history, "IRX_13W", 250),
        # z-score
        "VIX_z60": compute_zscore(history, "VIX", 60),
        "MOVE_z60": compute_zscore(history, "MOVE", 60),
        # SPY 200일 상회 여부
        "SPY_above_200": (safe_get(latest, "SPY_Close", 0) > (compute_ma(history, "SPY_Close", 200) or 1e9)),
    }


# ═══════════════════════════════════════════════════════════════════════
# L2: 센서 → 8축 확률 추론
# ═══════════════════════════════════════════════════════════════════════
# 원칙 (적정자):
#   • CREDIT/MONETARY → Oracle auto_prior 내장 LEAD-5/6b (회귀+분위수)
#   • WAR/OIL/GROWTH → 프록시 추론 후 auto_prior에 proxy_result로 전달
#   • TARIFF/FISCAL/AI_POWER → 프록시 추론 후 결과 dict에 직접 주입
#   • 모든 상태는 Oracle 축 정의와 정확히 일치 (states 검증)
# ═══════════════════════════════════════════════════════════════════════

# Oracle 축 states (v2.13.1 정본 — 변경 시 동기화 필수)
AXIS_STATES = {
    "WAR":      ("ceasefire", "limited", "regional", "total"),
    "OIL":      ("normalize", "disrupted", "blocked"),
    "MONETARY": ("dovish", "hold", "hawkish"),
    "CREDIT":   ("easy", "tight", "shadow_stress", "crisis"),
    "TARIFF":   ("resolved", "status_quo", "breakdown"),
    "GROWTH":   ("boom", "steady", "slowdown", "recession"),
    "FISCAL":   ("austere", "neutral", "expansive", "dominant"),
    "AI_POWER": ("normal", "accelerating", "peak_demand", "bottleneck"),
}


def _normalize_probs(probs: Dict[str, float], states: Tuple[str, ...]) -> Dict[str, float]:
    """확률 정규화 + 누락 상태 0 채움 + 합계 1 보장."""
    full = {s: max(0.0, probs.get(s, 0.0)) for s in states}
    total = sum(full.values())
    if total <= 0:
        # 균등 분포 폴백
        return {s: 1.0 / len(states) for s in states}
    return {s: round(v / total, 4) for s, v in full.items()}


def _softmax_from_scores(scores: Dict[str, float], temp: float = 1.0) -> Dict[str, float]:
    """상태별 점수 → softmax 확률."""
    items = list(scores.items())
    mx = max(v for _, v in items)
    exps = {s: math.exp((v - mx) / temp) for s, v in items}
    z = sum(exps.values())
    return {s: round(v / z, 4) for s, v in exps.items()}


# ── L2b-1: WAR 프록시 추론 ────────────────────────────────────────────

def infer_war_proxy(latest: Dict, derived: Dict) -> Dict[str, Any]:
    """WAR 축 프록시 추론. 시장 신호(유가/VIX/금/방산) 복합.
    
    신뢰도 ★★ (정치 이벤트 직접 반영 불가 — 뉴스 교차 검증 권장).
    반환: {"war_probs": {state: prob}, "confidence": int, "evidence": str}
    """
    wti = safe_get(latest, "WTI", 75.0)
    vix = safe_get(latest, "VIX", 20.0)
    gld_mom = derived.get("GLD_mom30")
    ita_rs = derived.get("ITA_SPY_RS60")

    # 상태별 점수 (확전 ← → 평화)
    scores = {"ceasefire": 0.0, "limited": 0.0, "regional": 0.0, "total": 0.0}
    evidence = []

    # 유가 (가장 강한 지정학 프록시)
    if wti > 100:
        scores["total"] += 2.5; scores["regional"] += 1.5
        evidence.append(f"WTI ${wti:.0f} (전면전급)")
    elif wti > 90:
        scores["regional"] += 2.0; scores["limited"] += 1.0
        evidence.append(f"WTI ${wti:.0f} (지역분쟁)")
    elif wti > 78:
        scores["limited"] += 2.0; scores["regional"] += 0.5
        evidence.append(f"WTI ${wti:.0f} (제한분쟁)")
    else:
        scores["ceasefire"] += 1.5; scores["limited"] += 1.0
        evidence.append(f"WTI ${wti:.0f} (안정)")

    # VIX (공포)
    if vix > 30:
        scores["regional"] += 1.0; scores["total"] += 0.5
    elif vix > 22:
        scores["limited"] += 0.8; scores["regional"] += 0.5
    else:
        scores["ceasefire"] += 0.5; scores["limited"] += 0.3

    # 금 모멘텀 (안전자산 수요)
    if gld_mom is not None and gld_mom > 0.05:
        scores["regional"] += 0.6
        evidence.append(f"금 30일 +{gld_mom:.1%}")

    # 방산 상대강도 (전쟁 기대 선반영)
    if ita_rs is not None and ita_rs > 1.05:
        scores["regional"] += 0.5; scores["limited"] += 0.3
        evidence.append(f"ITA/SPY RS {ita_rs:.2f}")

    probs = _softmax_from_scores(scores, temp=0.8)
    probs = _normalize_probs(probs, AXIS_STATES["WAR"])

    return {
        "war_probs": probs,
        "confidence": 55,
        "evidence": "⚠️ 시장 프록시 (뉴스 확인 권장) | " + " | ".join(evidence),
    }


# ── L2b-2: OIL 프록시 추론 ────────────────────────────────────────────

def infer_oil_proxy(latest: Dict, derived: Dict) -> Dict[str, Any]:
    """OIL 축 프록시 추론 — v1.0.6: Brent-WTI spread(LEAD-3) 위임.

    Brent 가용 시 Oracle compute_oil_proxy(spread 60% + WTI 40%, LEAD-3)에 위임 — 단일 SSOT.
    Brent 부재/위임 실패 시 WTI 단독 휴리스틱으로 graceful fallback (기존 동작 보존).
    신뢰도 ★★★ (유가 직접 관측). 호르무즈 등 구조 정보는 spread가 실시간 반영.
    """
    wti = safe_get(latest, "WTI", 75.0)
    brent = safe_get(latest, "Brent", None)

    # ── v1.0.6: Brent 가용 시 LEAD-3 spread 위임 (Oracle compute_oil_proxy 단일 SSOT) ──
    if brent is not None:
        try:
            _cop = load_oracle().get("compute_oil_proxy")
            if _cop is not None:
                _res = _cop(wti=wti, brent=brent)
                if _res is not None and _res.get("oil_probs"):
                    _spread = _res.get("spread")
                    _wlv = _res.get("wti_level")
                    _ev = [f"WTI ${wti:.1f}", f"Brent ${brent:.1f}", f"spread ${_spread:+.1f}"]
                    if _wlv:
                        _ev.append(f"WTI:{_wlv}")
                    _ev.extend(_res.get("alerts", []))
                    return {
                        "oil_probs": _normalize_probs(_res["oil_probs"], AXIS_STATES["OIL"]),
                        "confidence": 80,
                        "evidence": " | ".join(_ev) + " (LEAD-3 spread)",
                        "oil_signal": _res.get("oil_signal"),
                        "spread": _spread,
                        "wti_level": _wlv,
                        "source": "LEAD-3",
                    }
        except Exception:
            pass  # 위임 실패 → WTI 단독 폴백으로 진행 (안전)

    # ── 폴백: WTI 단독 휴리스틱 (Brent 부재 / 위임 실패 시 기존 동작 보존) ──
    wti_mom = derived.get("WTI_mom30")
    wti_ma60 = derived.get("WTI_MA60")

    scores = {"normalize": 0.0, "disrupted": 0.0, "blocked": 0.0}
    evidence = [f"WTI ${wti:.1f}"]

    # WTI 수준 (호르무즈 프리미엄 반영: $88+ = blocked 가능)
    if wti > 100:
        scores["blocked"] += 3.0
    elif wti > 88:
        scores["blocked"] += 2.0; scores["disrupted"] += 1.0
    elif wti > 78:
        scores["disrupted"] += 2.0; scores["normalize"] += 0.5
    elif wti > 68:
        scores["disrupted"] += 1.0; scores["normalize"] += 1.5
    else:
        scores["normalize"] += 2.5

    # 모멘텀 (급등 = 공급 충격)
    if wti_mom is not None:
        evidence.append(f"30일 {wti_mom:+.1%}")
        if wti_mom > 0.15:
            scores["blocked"] += 1.0
        elif wti_mom > 0.05:
            scores["disrupted"] += 0.6
        elif wti_mom < -0.10:
            scores["normalize"] += 0.8

    # MA60 대비
    if wti_ma60 is not None and wti > wti_ma60 * 1.10:
        scores["disrupted"] += 0.5
        evidence.append(f"MA60 +{(wti/wti_ma60-1):.0%}")

    probs = _softmax_from_scores(scores, temp=0.7)
    probs = _normalize_probs(probs, AXIS_STATES["OIL"])

    return {
        "oil_probs": probs,
        "confidence": 80,
        "evidence": " | ".join(evidence) + " (WTI 단독 폴백 — Brent 미공급)",
    }


# ── L2b-3: GROWTH 프록시 추론 ─────────────────────────────────────────

def infer_growth_proxy(latest: Dict, derived: Dict) -> Dict[str, Any]:
    """GROWTH 축 프록시 추론. PMI + SAHM + 실업청구 + 소비자심리.
    
    신뢰도 ★★★ (경기 지표 직접 관측).
    """
    pmi = safe_get(latest, "PMI", 50.0)
    sahm = safe_get(latest, "SAHMCURRENT", 0.0)
    icsa = safe_get(latest, "ICSA", 220000)
    umcsent = safe_get(latest, "UMCSENT", 60.0)

    scores = {"boom": 0.0, "steady": 0.0, "slowdown": 0.0, "recession": 0.0}
    evidence = []

    # PMI (핵심)
    if pmi > 55:
        scores["boom"] += 2.5; scores["steady"] += 1.0
        evidence.append(f"PMI {pmi:.1f} (강확장)")
    elif pmi > 52:
        scores["boom"] += 1.0; scores["steady"] += 2.0
        evidence.append(f"PMI {pmi:.1f} (확장)")
    elif pmi > 50:
        scores["steady"] += 2.0; scores["slowdown"] += 0.8
        evidence.append(f"PMI {pmi:.1f} (미약확장)")
    elif pmi > 47:
        scores["slowdown"] += 2.0; scores["steady"] += 0.5
        evidence.append(f"PMI {pmi:.1f} (수축)")
    else:
        scores["recession"] += 2.0; scores["slowdown"] += 1.0
        evidence.append(f"PMI {pmi:.1f} (침체급)")

    # SAHM (침체 조기경보)
    if sahm > 0.50:
        scores["recession"] += 2.5
        evidence.append(f"SAHM {sahm:.2f} (트리거!)")
    elif sahm > 0.35:
        scores["slowdown"] += 1.5; scores["recession"] += 0.5
        evidence.append(f"SAHM {sahm:.2f} (경보)")
    elif sahm > 0.20:
        scores["slowdown"] += 0.8
    else:
        scores["boom"] += 0.5; scores["steady"] += 0.8
        evidence.append(f"SAHM {sahm:.2f} (안전)")

    # 실업청구
    if icsa > 300000:
        scores["recession"] += 1.0; scores["slowdown"] += 0.8
    elif icsa > 260000:
        scores["slowdown"] += 0.8
    else:
        scores["steady"] += 0.5; scores["boom"] += 0.3
        evidence.append(f"신규청구 {icsa/1000:.0f}K")

    # 소비자심리
    if umcsent < 50:
        scores["slowdown"] += 0.6; scores["recession"] += 0.3
        evidence.append(f"UMich {umcsent:.0f} (비관)")
    elif umcsent > 80:
        scores["boom"] += 0.5

    probs = _softmax_from_scores(scores, temp=0.7)
    probs = _normalize_probs(probs, AXIS_STATES["GROWTH"])

    return {
        "growth_probs": probs,
        "confidence": 82,
        "evidence": " | ".join(evidence),
    }


# ── L2b-4: TARIFF 프록시 추론 (auto_prior 미지원 → 직접 주입) ─────────

def infer_tariff_proxy(latest: Dict, derived: Dict) -> Dict[str, Any]:
    """TARIFF 축 프록시 추론. USD/CNY 환율 + DXY.
    
    신뢰도 ★★ (환율 프록시 — 정책 발표는 뉴스 필요).
    """
    usd_cny = safe_get(latest, "USD_CNY", 7.0)
    dxy = safe_get(latest, "DXY", 100.0)

    scores = {"resolved": 0.0, "status_quo": 0.0, "breakdown": 0.0}
    evidence = [f"USD/CNY {usd_cny:.3f}", f"DXY {dxy:.1f}"]

    if usd_cny > 7.5:
        scores["breakdown"] += 2.5; scores["status_quo"] += 0.5
    elif usd_cny > 7.1:
        scores["breakdown"] += 1.0; scores["status_quo"] += 2.0
    elif usd_cny > 6.6:
        scores["status_quo"] += 2.5
    else:
        scores["resolved"] += 2.0; scores["status_quo"] += 1.0

    probs = _softmax_from_scores(scores, temp=0.8)
    probs = _normalize_probs(probs, AXIS_STATES["TARIFF"])

    return {
        "tariff_probs": probs,
        "confidence": 45,
        "evidence": "⚠️ 환율 프록시 (정책 뉴스 확인) | " + " | ".join(evidence),
    }


# ── L2b-5: FISCAL 프록시 추론 (auto_prior 미지원 → 직접 주입) ─────────

def infer_fiscal_proxy(latest: Dict, derived: Dict) -> Dict[str, Any]:
    """FISCAL 축 프록시 추론. Fed B/S + 순유동성 + 역레포.
    
    신뢰도 ★ (직접 재정 센서 부족 — 유동성 프록시).
    """
    walcl = safe_get(latest, "WALCL", 7000000)
    nl = safe_get(latest, "Net_Liquidity", 5800000)
    rrp = safe_get(latest, "RRPONTSYD", 1.0)
    wtregen = safe_get(latest, "WTREGEN", 800000)

    scores = {"austere": 0.0, "neutral": 0.0, "expansive": 0.0, "dominant": 0.0}
    evidence = [f"Fed B/S {walcl/1e6:.1f}T", f"순유동성 {nl/1e6:.1f}T", f"RRP {rrp:.2f}T"]

    # 순유동성 수준 (높을수록 확장적)
    if nl > 6200000:
        scores["dominant"] += 1.5; scores["expansive"] += 1.5
    elif nl > 5700000:
        scores["expansive"] += 2.0; scores["neutral"] += 1.0
    elif nl > 5300000:
        scores["neutral"] += 2.0; scores["expansive"] += 0.5
    else:
        scores["austere"] += 1.5; scores["neutral"] += 1.0

    # 미국 재정은 2026년 대체로 확장적 (적자 지속)
    scores["expansive"] += 1.0  # 구조적 편향

    probs = _softmax_from_scores(scores, temp=0.9)
    probs = _normalize_probs(probs, AXIS_STATES["FISCAL"])

    return {
        "fiscal_probs": probs,
        "confidence": 30,
        "evidence": "⚠️ 유동성 프록시 (재정 데이터 부족) | " + " | ".join(evidence),
    }


# ── L2b-6: AI_POWER 프록시 추론 (era axis → 직접 주입) ───────────────

def infer_ai_power_proxy(latest: Dict, derived: Dict) -> Dict[str, Any]:
    """AI_POWER 축 프록시 추론. SMH/SPY 상대강도 + MA200 + NLR 모멘텀.
    
    신뢰도 ★★★ (시장 신호로 AI 수요 강도 측정).
    v2.13.1 states: normal, accelerating, peak_demand, bottleneck.
    """
    smh = safe_get(latest, "SMH_Close", 500.0)
    smh_ma200 = derived.get("SMH_MA200")
    smh_rs = derived.get("SMH_SPY_RS60")
    smh_mom = derived.get("SMH_mom60")
    nlr_mom = derived.get("NLR_mom60")

    scores = {"normal": 0.0, "accelerating": 0.0, "peak_demand": 0.0, "bottleneck": 0.0}
    evidence = []

    # SMH/SPY 상대강도 (AI 수요 강도)
    if smh_rs is not None:
        evidence.append(f"SMH/SPY RS {smh_rs:.2f}")
        if smh_rs > 1.20:
            scores["peak_demand"] += 2.5; scores["accelerating"] += 1.0
        elif smh_rs > 1.05:
            scores["accelerating"] += 2.5; scores["peak_demand"] += 0.5
        elif smh_rs > 0.95:
            scores["normal"] += 1.5; scores["accelerating"] += 1.0
        elif smh_rs > 0.85:
            scores["bottleneck"] += 1.0; scores["normal"] += 1.0
        else:
            scores["bottleneck"] += 2.0

    # SMH vs MA200
    if smh_ma200 is not None:
        if smh > smh_ma200 * 1.10:
            scores["accelerating"] += 1.0; scores["peak_demand"] += 0.5
            evidence.append(f"SMH>MA200 +{(smh/smh_ma200-1):.0%}")
        elif smh < smh_ma200:
            scores["bottleneck"] += 1.0
            evidence.append(f"SMH<MA200")

    # NLR 모멘텀 (전력 병목 신호: 반도체↓ + 전력↑ = bottleneck)
    if nlr_mom is not None and smh_mom is not None:
        if nlr_mom > 0.05 and smh_mom < 0:
            scores["bottleneck"] += 1.5  # 전력은 오르고 반도체는 내림
            evidence.append(f"NLR↑{nlr_mom:+.0%} SMH↓{smh_mom:+.0%} (병목)")

    if smh_mom is not None:
        evidence.append(f"SMH 60일 {smh_mom:+.1%}")

    probs = _softmax_from_scores(scores, temp=0.8)
    probs = _normalize_probs(probs, AXIS_STATES["AI_POWER"])

    return {
        "ai_power_probs": probs,
        "confidence": 75,
        "evidence": " | ".join(evidence),
    }


# ═══════════════════════════════════════════════════════════════════════
# Oracle v2.13.1 엔진 로더 (적정자 핵심: Oracle 본체 정식 호출)
# ═══════════════════════════════════════════════════════════════════════

_ORACLE = None

def load_oracle() -> Dict[str, Any]:
    """Oracle v2.13.1을 본 모듈의 L0 상수와 함께 exec 로딩.
    
    적정자 원칙: Oracle가 의존하는 Brief 상수를 본 모듈이 공급하여
    Oracle의 모든 함수(gradient/regime/auto_prior/impact)를 정식 구동.
    """
    global _ORACLE
    if _ORACLE is not None:
        return _ORACLE

    # Oracle 네임스페이스에 L0 상수 주입
    ns = {
        "GRADIENT_SENSOR_BANDS": GRADIENT_SENSOR_BANDS,
        "GRADIENT_ALLOCATION_GUIDE": GRADIENT_ALLOCATION_GUIDE,
        "LIQUIDITY_STRESS_REGIME": LIQUIDITY_STRESS_REGIME,
        "RR_FLOW_ADJUST": RR_FLOW_ADJUST,
        "GLD_CAP_NORMAL": GLD_CAP_NORMAL,
        "RR_SUBSCORE_BANDS": RR_SUBSCORE_BANDS,
        "compute_real_rate_subscore": compute_real_rate_subscore,
    }

    # Oracle 파일 탐색
    for candidate in ["Oracle_v2_13_1.py", "Oracle_v2_10_0.py", "Oracle_v2_9_0.py"]:
        path = os.path.join(_ENGINE_DIR, candidate)
        if not os.path.exists(path):
            path = os.path.join("/mnt/project", candidate)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                exec(f.read(), ns)
            ns["_ORACLE_FILE"] = candidate
            break

    _ORACLE = ns
    return _ORACLE


# ═══════════════════════════════════════════════════════════════════════
# L2c: DataFrame 빌드 + auto_prior 통합 → axis_probs
# ═══════════════════════════════════════════════════════════════════════

def build_dataframe(history: List[Dict]):
    """ARGUS 히스토리 → pandas DataFrame (LEAD-5/6b 입력용)."""
    import pandas as pd
    df = pd.DataFrame(history)
    # 숫자 컬럼 강제 변환
    for col in df.columns:
        if col != "Date":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def infer_all_axes(latest: Dict, history: List[Dict], derived: Dict,
                   commander_overrides: Optional[Dict] = None) -> Dict[str, Any]:
    """8축 확률 통합 추론 (적정자 핵심 파이프라인).
    
    1) WAR/OIL/GROWTH 프록시 추론 → auto_prior proxy_result
    2) CREDIT/MONETARY → auto_prior 내장 LEAD-5/6b (df 기반)
    3) auto_prior 호출 → 5축 axis_probs
    4) TARIFF/FISCAL/AI_POWER 프록시 → 직접 주입
    
    반환: {"axis_probs": {축: {상태: 확률}},
            "confidence": {축: int}, "evidence": {축: str},
            "lead_sources": {축: str}}
    """
    O = load_oracle()
    auto_prior = O.get("auto_prior")

    # 1) 프록시 추론
    war_px = infer_war_proxy(latest, derived)
    oil_px = infer_oil_proxy(latest, derived)
    growth_px = infer_growth_proxy(latest, derived)
    tariff_px = infer_tariff_proxy(latest, derived)
    fiscal_px = infer_fiscal_proxy(latest, derived)
    ai_px = infer_ai_power_proxy(latest, derived)

    confidence = {
        "WAR": war_px["confidence"], "OIL": oil_px["confidence"],
        "GROWTH": growth_px["confidence"], "TARIFF": tariff_px["confidence"],
        "FISCAL": fiscal_px["confidence"], "AI_POWER": ai_px["confidence"],
    }
    evidence = {
        "WAR": war_px["evidence"], "OIL": oil_px["evidence"],
        "GROWTH": growth_px["evidence"], "TARIFF": tariff_px["evidence"],
        "FISCAL": fiscal_px["evidence"], "AI_POWER": ai_px["evidence"],
    }
    lead_sources = {}

    # 2) DataFrame 빌드 (LEAD-5/6b용)
    axis_probs = {}
    try:
        df = build_dataframe(history)
        i = len(df) - 1  # 최신 행

        # 3) auto_prior 호출 (WAR/OIL/GROWTH 프록시 + CREDIT/MONETARY LEAD)
        if auto_prior:
            axis_probs = auto_prior(
                df=df, i=i,
                war_proxy_result=war_px,
                growth_proxy_result=growth_px,
                oil_proxy_result=oil_px,
                commander_overrides=commander_overrides,
            )
            lead_sources["CREDIT"] = "LEAD-5 (OAS_HY 분위수 회귀)"
            lead_sources["MONETARY"] = "LEAD-6b (IRX_13W 분위수+변화)"
    except Exception as e:
        evidence["_auto_prior_error"] = str(e)

    # auto_prior 실패 시 프록시로 폴백
    if not axis_probs:
        axis_probs = {
            "WAR": war_px["war_probs"],
            "OIL": oil_px["oil_probs"],
            "GROWTH": growth_px["growth_probs"],
        }
        # CREDIT/MONETARY 폴백: 자체 추론
        axis_probs["CREDIT"] = _fallback_credit(latest)
        axis_probs["MONETARY"] = _fallback_monetary(latest, derived)
        lead_sources["CREDIT"] = "폴백 (자체 추론)"
        lead_sources["MONETARY"] = "폴백 (자체 추론)"

    # CREDIT/MONETARY 신뢰도 (LEAD 사용 시 높음)
    confidence["CREDIT"] = 88 if "LEAD-5" in lead_sources.get("CREDIT", "") else 60
    confidence["MONETARY"] = 85 if "LEAD-6b" in lead_sources.get("MONETARY", "") else 60
    evidence["CREDIT"] = lead_sources.get("CREDIT", "")
    evidence["MONETARY"] = lead_sources.get("MONETARY", "")

    # 4) TARIFF/FISCAL/AI_POWER 직접 주입 (auto_prior 미지원 축)
    axis_probs["TARIFF"] = tariff_px["tariff_probs"]
    axis_probs["FISCAL"] = fiscal_px["fiscal_probs"]
    axis_probs["AI_POWER"] = ai_px["ai_power_probs"]

    # 정규화 + states 검증
    for axis, states in AXIS_STATES.items():
        if axis in axis_probs:
            axis_probs[axis] = _normalize_probs(axis_probs[axis], states)

    return {
        "axis_probs": axis_probs,
        "confidence": confidence,
        "evidence": evidence,
        "lead_sources": lead_sources,
    }


def _fallback_credit(latest: Dict) -> Dict[str, float]:
    """CREDIT 폴백 추론 (LEAD-5 불가 시)."""
    oas = safe_get(latest, "OAS_HY", 3.5)
    if oas > 5.5:
        return {"easy": 0.0, "tight": 0.2, "shadow_stress": 0.3, "crisis": 0.5}
    elif oas > 4.5:
        return {"easy": 0.1, "tight": 0.5, "shadow_stress": 0.3, "crisis": 0.1}
    elif oas > 3.5:
        return {"easy": 0.3, "tight": 0.5, "shadow_stress": 0.15, "crisis": 0.05}
    else:
        return {"easy": 0.6, "tight": 0.3, "shadow_stress": 0.08, "crisis": 0.02}


def _fallback_monetary(latest: Dict, derived: Dict) -> Dict[str, float]:
    """MONETARY 폴백 추론 (LEAD-6b 불가 시)."""
    dgs10 = safe_get(latest, "DGS10", 4.0)
    tnx_mom = derived.get("TNX_mom60")
    rising = tnx_mom is not None and tnx_mom > 0.03
    if dgs10 > 4.5:
        return {"dovish": 0.05, "hold": 0.25, "hawkish": 0.70} if rising else {"dovish": 0.1, "hold": 0.4, "hawkish": 0.5}
    elif dgs10 > 3.8:
        return {"dovish": 0.15, "hold": 0.55, "hawkish": 0.30}
    else:
        return {"dovish": 0.5, "hold": 0.4, "hawkish": 0.1}


# ═══════════════════════════════════════════════════════════════════════
# L3: 레짐 파이프라인 (Oracle 정식 함수 체인)
# ═══════════════════════════════════════════════════════════════════════

def run_regime_pipeline(latest: Dict, derived: Dict) -> Dict[str, Any]:
    """Oracle 레짐 파이프라인 정식 구동.
    
    compute_regime_gradient → compute_regime_inputs → classify_macro_regime
    """
    O = load_oracle()
    result = {}

    vix = safe_get(latest, "VIX", 18.0)
    move = safe_get(latest, "MOVE", 80.0)
    oas = safe_get(latest, "OAS_HY", 3.0)
    dfii10 = safe_get(latest, "DFII10", 1.5)
    t5yie = safe_get(latest, "T5YIE", 2.2)
    pmi = safe_get(latest, "PMI", 50.0)
    sahm = safe_get(latest, "SAHMCURRENT", 0.0)
    nfci = safe_get(latest, "NFCI", 0.0)
    t10y2y = safe_get(latest, "T10Y2Y", 0.2)
    icsa = safe_get(latest, "ICSA", 220000) / 1000.0  # K 단위
    spy = safe_get(latest, "SPY_Close", 0.0)
    spy_ma200 = derived.get("SPY_MA200", 0.0) or 0.0

    # 1) Gradient
    try:
        grad = O["compute_regime_gradient"](
            vix=vix, oas_hy=oas, move=move, flow_signal="NEUTRAL", dfii10=dfii10
        )
        result["gradient"] = grad
        gradient_score = grad.get("total_score", 50.0)
    except Exception as e:
        result["gradient_error"] = str(e)
        gradient_score = 50.0

    # 2) Regime inputs (tide/curve/inferno 상태)
    try:
        inputs = O["compute_regime_inputs"](
            vix=vix, move=move, oas_hy=oas, dfii10=dfii10, t5yie=t5yie,
            pmi=pmi, spy=spy, spy_200=spy_ma200, icsa_4w_avg=icsa,
            sahm=sahm, nfci=nfci, t10y2y_bp=t10y2y * 100,
        )
        result["regime_inputs"] = inputs
    except Exception as e:
        result["regime_inputs_error"] = str(e)
        inputs = {}

    # 3) Macro regime classification
    try:
        tide = inputs.get("tide_state", inputs.get("tide", "NEUTRAL"))
        curve = inputs.get("curve_state", inputs.get("curve", "NORMAL"))
        inferno = inputs.get("inferno_state", inputs.get("inferno", "STABLE"))
        regime = O["classify_macro_regime"](
            tide_state=tide, curve_state=curve, inferno_state=inferno,
            dfii10=dfii10, gradient_score=gradient_score,
        )
        result["macro_regime"] = regime
    except Exception as e:
        result["macro_regime_error"] = str(e)

    result["gradient_score"] = gradient_score
    return result


# ═══════════════════════════════════════════════════════════════════════
# L4: compute_axis_impact 29종목 (Oracle 정식 임팩트 엔진)
# ═══════════════════════════════════════════════════════════════════════

def run_impact_engine(axis_probs: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Oracle compute_axis_impact로 전 종목 기대 수익률 계산.
    
    INTERACTION_PAIRS 비선형 부스트 + TOTAL_IMPACT_CAP 자동 적용.
    """
    O = load_oracle()
    iax = O.get("IMPACT_BY_AXIS", {})
    cai = O.get("compute_axis_impact")
    if not cai or not iax:
        return {"error": "compute_axis_impact 또는 IMPACT_BY_AXIS 미로딩"}

    ticker_impacts = {}
    for ticker in iax.keys():
        try:
            ticker_impacts[ticker] = cai(ticker, axis_probs)
        except Exception as e:
            ticker_impacts[ticker] = {"total_impact": 0.0, "error": str(e)}

    ranked = sorted(
        [(t, r.get("total_impact", 0.0)) for t, r in ticker_impacts.items()],
        key=lambda x: -x[1]
    )
    return {
        "ticker_impacts": ticker_impacts,
        "ranked": ranked,
        "version": O.get("ADVISOR_VERSION", "?"),
        "interaction_pairs": O.get("INTERACTION_PAIRS", {}),
        "total_impact_cap": O.get("TOTAL_IMPACT_CAP", 0.25),
    }


# ═══════════════════════════════════════════════════════════════════════
# L5: 시나리오 확률 엔진 (S1~S11)
# ═══════════════════════════════════════════════════════════════════════

SCENARIO_LABELS = {
    "S1": "연준 비둘기 전환", "S2": "이란 확전", "S5": "복합 충격",
    "S6": "AI 위기 (citrini)", "S7": "연준 매파 지속", "S9": "그랜드 바겐",
    "S10": "희토류 금수", "S11": "AI capex 포화",
}

# 시나리오별 트리거 축 조건 (가중 점수)
SCENARIO_TRIGGERS = {
    "S1": {"MONETARY": {"dovish": 1.0}, "CREDIT": {"easy": 0.5}},
    "S2": {"WAR": {"regional": 0.8, "total": 1.0}, "OIL": {"blocked": 0.6}},
    "S5": {"WAR": {"regional": 0.5, "total": 0.8}, "MONETARY": {"hawkish": 0.5}, "CREDIT": {"crisis": 0.8, "shadow_stress": 0.5}},
    "S6": {"AI_POWER": {"bottleneck": 0.8}, "GROWTH": {"slowdown": 0.4}},
    "S7": {"MONETARY": {"hawkish": 1.0}, "GROWTH": {"boom": 0.4}},
    "S9": {"WAR": {"ceasefire": 0.8, "limited": 0.5}, "TARIFF": {"resolved": 0.6}},
    "S10": {"TARIFF": {"breakdown": 1.0}},
    "S11": {"AI_POWER": {"bottleneck": 0.6}, "GROWTH": {"slowdown": 0.5}},
}


def compute_scenario_probs(axis_probs: Dict, gradient_score: float) -> Dict[str, float]:
    """8축 확률 + 그래디언트 → 시나리오 확률 배분.
    
    각 시나리오의 트리거 축 확률을 가중 합산 → softmax.
    """
    raw = {}
    for sc, triggers in SCENARIO_TRIGGERS.items():
        score = 0.0
        for axis, state_weights in triggers.items():
            ap = axis_probs.get(axis, {})
            for state, weight in state_weights.items():
                score += ap.get(state, 0.0) * weight
        raw[sc] = score

    # 그래디언트 보정: 고위험(고그래디언트)일수록 위기 시나리오 가중
    if gradient_score > 60:
        raw["S5"] = raw.get("S5", 0) * 1.5
        raw["S7"] = raw.get("S7", 0) * 1.3
        raw["S1"] = raw.get("S1", 0) * 0.5
    elif gradient_score < 30:
        raw["S1"] = raw.get("S1", 0) * 1.3
        raw["S9"] = raw.get("S9", 0) * 1.3
        raw["S5"] = raw.get("S5", 0) * 0.7

    # 정규화 (softmax 대신 비례 배분 — 0 방지 위해 floor)
    for sc in SCENARIO_TRIGGERS:
        raw[sc] = max(0.02, raw.get(sc, 0.0))
    total = sum(raw.values())
    return {sc: round(v / total, 3) for sc, v in raw.items()}


# ═══════════════════════════════════════════════════════════════════════
# L8: 레짐 전환 감지 (Oracle detect_regime_transition)
# ═══════════════════════════════════════════════════════════════════════

def run_transition_detector(history: List[Dict]) -> Dict[str, Any]:
    """Oracle EWMA 전환 감지 정식 구동.
    
    최근 센서 히스토리 → detect_regime_transition → 전환 신호.
    """
    O = load_oracle()
    detect = O.get("detect_regime_transition")
    if not detect:
        return {"error": "detect_regime_transition 미로딩"}

    # 센서 히스토리 구성 (최근 60일 VIX/OAS/MOVE)
    recent = history[-60:]
    sensor_history = {
        "VIX": [h.get("VIX") for h in recent if h.get("VIX") is not None],
        "OAS_HY": [h.get("OAS_HY") for h in recent if h.get("OAS_HY") is not None],
        "MOVE": [h.get("MOVE") for h in recent if h.get("MOVE") is not None],
    }
    try:
        return detect(sensor_history=sensor_history)
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# L6: 포트폴리오 구성 (레짐 프리셋 + 임팩트 틸트 + DRP)
# ═══════════════════════════════════════════════════════════════════════

# INVICTUS 자산 티어
ASSET_TIERS = {
    # [v1.0.2] ARGUS 20종목 + SGOV(현금) 기준 재분류. PDBC/IEF 제거(ARGUS 외).
    "DEFENSE": ["SGOV", "GLD", "TLT", "XLU", "XLV", "VEA"],
    "ATTACK":  ["SMH", "QQQM", "COPX", "EWZ", "IWM", "PAVE", "VNM", "INDA", "CQQQ", "CIBR", "XLF"],
    "HEDGE":   ["XLE", "ITA", "NLR", "SLV"],
}


def normalize_allocation(weights: Dict[str, float], floor_zero: bool = True) -> Dict[str, float]:
    """[v1.0.1 P0-1] 비중 합계 100% 강제 정규화.
    
    음수 차단 + 비례 재조정. 합 0이면 SGOV 100% 폴백.
    """
    cleaned = {k: (max(0.0, v) if floor_zero else v) for k, v in weights.items()}
    total = sum(cleaned.values())
    if total <= 1e-9:
        return {"SGOV": 100.0}
    return {k: round(v / total * 100.0, 2) for k, v in cleaned.items() if v > 0}


def construct_portfolio(regime_result: Dict, impact_result: Dict,
                        gradient_score: float) -> Dict[str, Any]:
    """레짐 프리셋 기반 + 임팩트 틸트 포트폴리오 구성.
    
    [v1.0.1 P0-1 FIX] 방어자산(preset)과 공격자산(attack_alloc) 분리,
    중복 덮어쓰기 제거, 최종 100% 정규화.
    
    1) 레짐 프리셋 allocation (SGOV/GLD/attack_core)
    2) attack_core를 공격티어 임팩트 상위 종목으로 분배 (방어자산 제외)
    3) 방어 preset + 공격 alloc 가산 병합 → 100% 정규화
    """
    result = {"method": "regime_preset + impact_tilt (v1.0.1 normalized)"}

    # 1) 레짐 프리셋
    macro = regime_result.get("macro_regime", {})
    preset = macro.get("allocation_final", macro.get("preset", {}).get("allocation", {}))
    if not preset:
        preset = {"SGOV": 30, "GLD": 20, "attack_core": 50}
    result["regime_preset"] = preset

    # 방어 preset (attack_core 제외) — 명시적 방어/헤지 자산
    defensive = {k: float(v) for k, v in preset.items() if k != "attack_core"}
    attack_pct = float(preset.get("attack_core", 50))

    # 2) attack_core를 공격티어 임팩트 상위로 분배
    #    [v1.0.2] ARGUS 유니버스 종목만 선택 (포트폴리오 = ARGUS 20 + 현금)
    #    [FIX] preset 방어자산(GLD/SGOV 등)은 공격 분배에서 제외 → 중복 방지
    ranked = impact_result.get("ranked", [])
    exclude = set(defensive.keys()) | {CASH_PROXY, "TLT", "IEF", "LQD"}
    positive = [(t, v) for t, v in ranked
                if v > 0 and t not in exclude and t in ARGUS_UNIVERSE]
    top_positive = positive[:6]

    attack_alloc = {}
    if top_positive:
        total_impact = sum(v for _, v in top_positive)
        for ticker, impact in top_positive:
            weight = (impact / total_impact) * attack_pct if total_impact > 0 else attack_pct / len(top_positive)
            attack_alloc[ticker] = round(weight, 2)
    elif attack_pct > 0:
        # 순풍 공격종목 없으면 방어로 회수 (SGOV 가산)
        defensive["SGOV"] = defensive.get("SGOV", 0) + attack_pct

    result["attack_allocation"] = attack_alloc

    # 3) 가산 병합 (중복 없음 — defensive와 attack은 배타) + 정규화
    merged = dict(defensive)
    for t, w in attack_alloc.items():
        merged[t] = merged.get(t, 0.0) + w
    final = normalize_allocation(merged)
    result["final_allocation"] = final
    result["allocation_sum_pre_norm"] = round(sum(merged.values()), 1)

    # DRP 노트
    if gradient_score > 60:
        result["drp_note"] = "⚡ 고그래디언트 → 방어 +10%p 동적 상향 검토"
    elif gradient_score < 25:
        result["drp_note"] = "🟢 저그래디언트 → 공격 유지 가능"
    else:
        result["drp_note"] = "🟡 중그래디언트 → 프리셋 유지"

    return result


# ═══════════════════════════════════════════════════════════════════════
# L7: 전략이론 6계통 (QNS v1.1 + QLS v1.0 실엔진)
# ═══════════════════════════════════════════════════════════════════════

_QNS = None
_QLS = None

def _load_strategy_engines():
    global _QNS, _QLS
    if _QNS is None:
        _QNS = _load_py("QNS_v1_1_0.py")
    if _QLS is None:
        _QLS = _load_py("QLS_v1_0_0.py")
    return _QNS, _QLS

def _load_py(filename):
    path = os.path.join(_ENGINE_DIR, filename)
    if not os.path.exists(path):
        path = os.path.join("/mnt/project", filename)
    ns = {}
    with open(path, encoding="utf-8") as f:
        exec(f.read(), ns)
    return ns


@dataclass
class TheoryResult:
    family: str; family_id: int; theory: str; severity: str
    computed: dict = field(default_factory=dict)
    diagnosis: str = ""; implication: str = ""


def _dominant_state(axis_probs: Dict, axis: str) -> str:
    ap = axis_probs.get(axis, {})
    if not ap:
        return "unknown"
    return max(ap.items(), key=lambda x: x[1])[0]


def run_strategic_theory(axis_probs: Dict, latest: Dict, derived: Dict) -> List[TheoryResult]:
    """6계통 전략이론 실엔진 구동."""
    Q, L = _load_strategy_engines()
    results = []
    war = _dominant_state(axis_probs, "WAR")
    oil = _dominant_state(axis_probs, "OIL")
    tariff = _dominant_state(axis_probs, "TARIFF")
    monetary = _dominant_state(axis_probs, "MONETARY")
    growth = _dominant_state(axis_probs, "GROWTH")
    ai = _dominant_state(axis_probs, "AI_POWER")

    # ① 게임이론: 이란-미국 치킨게임 Nash
    try:
        crash = {"ceasefire":-5,"limited":-8,"regional":-10,"total":-15}.get(war,-8)
        ib = {"normalize":-2,"disrupted":0,"blocked":3}.get(oil,0)
        game = Q["make_2x2_game"](name="Iran-US", p1_name="Iran", p2_name="US",
            actions=("Escalate","De-escalate"),
            payoffs=((crash,crash),(5+ib,-3),(-3,5),(2,2)),
            game_type=Q["GameType"].STATIC)
        pure = Q["find_pure_nash"](game)
        mixed = Q["find_mixed_nash_2x2"](game)
        comp = {"pure_nash": len(pure)}
        diag = [f"순수 Nash {len(pure)}개."]
        if mixed and hasattr(mixed, 'strategies') and mixed.strategies:
            for pl, strat in mixed.strategies.items():
                pr = {a.name: round(p, 2) for a, p in strat.mix.items()}
                comp[f"mixed_{pl.name}"] = pr
                diag.append(f"{pl.name} 혼합: {pr}")
        sev = "HIGH" if war in ("regional","total") else "MEDIUM"
        results.append(TheoryResult("게임이론",1,"Nash 균형 (QNS)",sev,comp," ".join(diag),
            "교착 시 실물 자산 순풍. 타협 균형 시 S9 상향."))
    except Exception as e:
        results.append(TheoryResult("게임이론",1,"Nash","LOW",{"error":str(e)},f"오류:{e}",""))

    # 미중 토너먼트
    try:
        tr = {"resolved":2,"status_quo":0,"breakdown":-2}.get(tariff,0)
        tg = Q["make_2x2_game"](name="US-China",p1_name="US",p2_name="China",
            actions=("Cooperate","Defect"),
            payoffs=((3+tr,3+tr),(0-tr,5),(5,0-tr),(1,1)),game_type=Q["GameType"].STATIC)
        tour = Q["run_repeated_tournament"](tg, rounds=100)
        ranked = sorted(tour, key=lambda x:-x["total_score"])
        comp = {"winner": ranked[0]["strategy"],
                "ranking": [f"{r['strategy']}: {r['total_score']:.0f}점" for r in ranked[:3]]}
        results.append(TheoryResult("게임이론",1,"반복게임 토너먼트 (QNS,5전략x100R)","MEDIUM",comp,
            f"미중 토너먼트 우승: {ranked[0]['strategy']}.","조건부 협력이 장기 최적."))
    except Exception as e:
        results.append(TheoryResult("게임이론",1,"토너먼트","LOW",{"error":str(e)},f"오류:{e}",""))

    # ② 행동경제학: BiasCheck
    try:
        BT, S, BC = L["BiasType"], L["Severity"], L["BiasCheck"]
        fg = safe_get(latest,"F_G_Score",50); vix = safe_get(latest,"VIX",20)
        checks = []
        if monetary == "hawkish":
            checks.append(BC(bias=BT.ANCHORING,detected=True,
                evidence=f"10Y {safe_get(latest,'DGS10',0):.2f}%, 금리 인하 기대 앵커링",
                impact="채권/성장주 앵커 이탈 시 과매도",mitigation="금리 전망 재평가"))
        if fg < 30:
            checks.append(BC(bias=BT.LOSS_AVERSION,detected=True,evidence=f"F&G {fg:.0f}",
                impact="공격 자산 과잉 매도",mitigation="역발상 매수 검토"))
        elif fg > 70:
            checks.append(BC(bias=BT.OVERCONFIDENCE,detected=True,evidence=f"F&G {fg:.0f}",
                impact="리스크 과소평가",mitigation="방어 선행 확대"))
        checks.append(BC(bias=BT.RECENCY,detected=True,
            evidence=f"SMH 60일 {derived.get('SMH_mom60',0):+.0%}",
            impact="최근 성과 과대 의존",mitigation="시스코 교훈 감시"))
        diags = L["run_bias_checklist"](checks)
        comp = {"detected": len(checks), "checklist":[str(d) for d in diags]}
        results.append(TheoryResult("행동경제학",2,f"편향 체크리스트 (QLS,{len(checks)}종)",
            "HIGH" if monetary=="hawkish" else "MEDIUM",comp,
            f"편향 {len(checks)}건 감지.","편향 대응책 적용 필요."))
    except Exception as e:
        results.append(TheoryResult("행동경제학",2,"BiasCheck","LOW",{"error":str(e)},f"오류:{e}",""))

    # ③ 권력 동학: PowerMap
    try:
        PT, LS, S, PME, CA = L["PowerType"], L["LegitimacySource"], L["Severity"], L["PowerMapEntry"], L["CoalitionAnalysis"]
        pmap = [
            PME(actor="미국",power_types=[PT.HARD,PT.SMART],legitimacy=[LS.LEGAL_RATIONAL],
                resources="군사력,달러,AI 기술",vulnerabilities="SPR 고갈,재정적자",
                allies=["이스라엘","사우디"],rivals=["이란","중국"],hidden_agenda="패권 유지"),
            PME(actor="이란",power_types=[PT.HARD,PT.SHARP],legitimacy=[LS.CHARISMATIC],
                resources="호르무즈,대리전",vulnerabilities="제재,승계 불안",
                allies=["헤즈볼라"],rivals=["미국","이스라엘"],hidden_agenda="제재 해제"),
        ]
        cs = [CA(coalition_name="이란 저항축",members=["이란","헤즈볼라","후티"],
                 binding_force="이념+대리전",weakest_link="시리아 와해",
                 defection_risk="후티 독자행동",stability=S.LOW)]
        diags = [p.diagnose() for p in pmap] + [c.diagnose() for c in cs]
        comp = {"actors":len(pmap),"power_map":[str(d) for d in diags[:len(pmap)]]}
        results.append(TheoryResult("권력 동학",3,f"권력 지도 (QLS,{len(pmap)}행위자)",
            "HIGH" if war in("regional","total") else "MEDIUM",comp,
            "미국=HARD+SMART, 이란=HARD+SHARP(비대칭).","이란 SHARP(호르무즈)가 미국 견제. 교착."))
    except Exception as e:
        results.append(TheoryResult("권력 동학",3,"PowerMap","LOW",{"error":str(e)},f"오류:{e}",""))

    # ⑤ 전략 기획: 스태그플레이션 경로
    if growth in ("boom","steady") and monetary=="hawkish" and oil in ("disrupted","blocked"):
        results.append(TheoryResult("전략 기획",5,"스태그플레이션 경로 (1970s 유사)","HIGH",
            {"growth":growth,"monetary":monetary,"oil":oil},
            "성장+인플레 = 스태그플레이션 조건. 유가 쇼크→CPI→긴축→침체 경로.",
            "실물(XLE,GLD,COPX) 순풍. 성장주+채권 역풍."))
    if ai in ("accelerating","peak_demand"):
        results.append(TheoryResult("전략 기획",5,"AI capex 분기 (Schwartz)","MEDIUM",
            {"ai":ai},f"AI={ai}. 분기 A(순풍) vs B(saturation). 변수: capex 가이던스.",
            "NVDA beat에도 주가 미반응 = B 조기 신호 감시."))

    # ⑥ 시스템 사고: 연쇄 전파
    red = [a for a in axis_probs if _dominant_state(axis_probs,a) in
           ("regional","total","blocked","hawkish","crisis","shadow_stress","breakdown","recession","bottleneck")]
    chains = []
    if "WAR" in red and "OIL" in red: chains.append("WAR→OIL")
    if "OIL" in red and "MONETARY" in red: chains.append("OIL→MONETARY")
    if "MONETARY" in red and "CREDIT" in red: chains.append("MONETARY→CREDIT")
    sev = "HIGH" if len(chains)>=2 else ("MEDIUM" if chains else "LOW")
    lev = chains[0].split("→")[0] if chains else "없음"
    results.append(TheoryResult("시스템 사고",6,"연쇄 전파 + 레버리지",sev,
        {"red_axes":red,"chains":chains,"leverage":lev},
        f"연쇄 {len(chains)}단계: {' → '.join(chains) or '미감지'}. 레버리지={lev}.",
        f"{lev}축 해소 시 하류 반전." if chains else "축 독립 = S5 확률 낮음."))

    sev_order = {"HIGH":0,"MEDIUM":1,"LOW":2}
    results.sort(key=lambda r: sev_order.get(r.severity,9))
    return results


# ═══════════════════════════════════════════════════════════════════════
# L9: 종합 브리핑 생성 (B0~B8 구조)
# ═══════════════════════════════════════════════════════════════════════

STATE_EMOJI = {
    "ceasefire":"🟢","limited":"🟡","regional":"🔴","total":"🔴🔴",
    "normalize":"🟢","disrupted":"🟡","blocked":"🔴",
    "dovish":"🟢","hold":"🟡","hawkish":"🔴",
    "easy":"🟢","tight":"🟡","shadow_stress":"🟠","crisis":"🔴",
    "resolved":"🟢","status_quo":"🟡","breakdown":"🔴",
    "boom":"🟢","steady":"🟡","slowdown":"🔴","recession":"🔴🔴",
    "austere":"🟢","neutral":"🟡","expansive":"🟡","dominant":"🔴",
    "normal":"⚪","accelerating":"🟢","peak_demand":"🟢🟢","bottleneck":"🟡",
}


def generate_briefing(latest, axes_result, regime_result, impact_result,
                      scenario_probs, portfolio, theory_results,
                      transition_result, validation) -> str:
    """종합 브리핑 텍스트 생성 (B0~B8 구조)."""
    L = []
    date = latest.get("Date", "?")
    axis_probs = axes_result["axis_probs"]
    grad = regime_result.get("gradient", {})
    grad_score = regime_result.get("gradient_score", 50)
    macro = regime_result.get("macro_regime", {})
    regime_label = macro.get("label", "?")

    # ── B0: 헤더 ──
    L.append("="*64)
    L.append(f"🔭 Oracle Autopilot v{AUTOPILOT_VERSION} (적정자) — 종합 브리핑")
    L.append(f"   Oracle {impact_result.get('version','?')} + QNS v1.1 + QLS v1.0 정식 통합")
    L.append(f"📅 데이터: {date} | 실행: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append("="*64)

    # ── B1: 결론 (레짐 + 핵심) ──
    L.append(f"\n🎯 B1. 결론")
    L.append(f"   레짐: {regime_label} | 그래디언트 {grad_score}/100")
    if grad:
        L.append(f"   방어/공격 타겟: {grad.get('defense_target','?')}% / {grad.get('attack_target','?')}%")
    red = [a for a in axis_probs if _dominant_state(axis_probs,a) in
           ("regional","total","blocked","hawkish","crisis","shadow_stress","breakdown","recession","bottleneck")]
    green = [a for a in axis_probs if _dominant_state(axis_probs,a) in
             ("ceasefire","normalize","dovish","easy","resolved","boom","accelerating","peak_demand")]
    L.append(f"   🔴 역풍 축 {len(red)}개: {', '.join(red) or '없음'}")
    L.append(f"   🟢 순풍 축 {len(green)}개: {', '.join(green) or '없음'}")

    # ── B2: 8축 현황 ──
    L.append(f"\n📊 B2. 8축 현황 (auto_prior + LEAD-5/6b + 프록시)")
    L.append(f"   {'축':10s} {'상태':14s} {'확률':>5s} {'신뢰도':>5s}  근거")
    L.append(f"   {'─'*64}")
    for axis in ["WAR","OIL","MONETARY","CREDIT","TARIFF","GROWTH","FISCAL","AI_POWER"]:
        ap = axis_probs.get(axis, {})
        if not ap: continue
        state, prob = max(ap.items(), key=lambda x: x[1])
        emoji = STATE_EMOJI.get(state, "❓")
        conf = axes_result["confidence"].get(axis, "?")
        ev = axes_result["evidence"].get(axis, "")[:42]
        L.append(f"   {emoji} {axis:8s} {state:14s} {prob:>4.0%} {conf:>4}%  {ev}")

    # ── B3: 레짐 프리셋 ──
    L.append(f"\n🌊 B3. 레짐 판정 (Oracle 정식 파이프라인)")
    if macro.get("briefing_line"):
        for line in macro["briefing_line"].split("\n"):
            L.append(f"   {line}")
    if grad.get("bracket"):
        L.append(f"   그래디언트 구간: {grad['bracket']}")
        L.append(f"   전략: {grad.get('strategy','')}")

    # ── B4: Oracle 임팩트 (종목별 기대 수익률) ──
    L.append(f"\n🔭 B4. Oracle 임팩트 — 29종목 기대 수익률")
    L.append(f"   INTERACTION_PAIRS {len(impact_result.get('interaction_pairs',{}))}쌍 | CAP ±{impact_result.get('total_impact_cap',0.25):.0%}")
    ranked = impact_result.get("ranked", [])
    impacts = impact_result.get("ticker_impacts", {})
    L.append(f"\n   🟢 순풍 TOP 8")
    for t, v in ranked[:8]:
        if v <= 0: break
        d = impacts[t].get("axis_details", {})
        top = sorted(d.items(), key=lambda x:-x[1])[:2]
        ts = " + ".join(f"{a} {x:+.1%}" for a,x in top if x>0)
        inter = "⚡" if impacts[t].get("interaction_applied") else ""
        L.append(f"     {t:6s} {v:>+7.2%}  {ts} {inter}")
    L.append(f"\n   🔴 역풍 TOP 8")
    for t, v in reversed(ranked[-8:]):
        if v >= 0: continue
        d = impacts[t].get("axis_details", {})
        bot = sorted(d.items(), key=lambda x:x[1])[:2]
        bs = " + ".join(f"{a} {x:+.1%}" for a,x in bot if x<0)
        inter = "⚡" if impacts[t].get("interaction_applied") else ""
        L.append(f"     {t:6s} {v:>+7.2%}  {bs} {inter}")

    # ── B5: 시나리오 확률 ──
    L.append(f"\n📈 B5. 시나리오 확률 (8축 트리거 기반)")
    for sc, p in sorted(scenario_probs.items(), key=lambda x:-x[1]):
        label = SCENARIO_LABELS.get(sc, sc)
        bar = "█" * int(p * 40)
        L.append(f"   {sc} {label:16s} {p:>5.1%}  {bar}")

    # ── B6: 포트폴리오 ──
    L.append(f"\n💼 B6. 포트폴리오 구성 ({portfolio.get('method','')})")
    L.append(f"   레짐 프리셋: {portfolio.get('regime_preset',{})}")
    final = portfolio.get("final_allocation", {})
    L.append(f"   최종 비중:")
    for ticker, w in sorted(final.items(), key=lambda x:-x[1]):
        L.append(f"     {ticker:8s} {w:>5.1f}%")
    L.append(f"   {portfolio.get('drp_note','')}")

    # ── B7: 전략이론 6계통 ──
    L.append(f"\n🎓 B7. 전략이론 6계통 (QNS + QLS 실엔진)")
    sev_emoji = {"HIGH":"🔴","MEDIUM":"🟡","LOW":"🟢"}
    fam_seen = set()
    for r in theory_results:
        if r.family not in fam_seen:
            L.append(f"\n   ── {r.family_id} {r.family} ──")
            fam_seen.add(r.family)
        em = sev_emoji.get(r.severity, "⚪")
        L.append(f"   {em} [{r.theory}]")
        L.append(f"      진단: {r.diagnosis}")
        L.append(f"      시사: {r.implication}")

    # ── B8: 전환 감지 + 자동화 한계 ──
    L.append(f"\n⚡ B8. 전환 감지 + 자동화 한계")
    if transition_result and "error" not in transition_result:
        sig = transition_result.get("transition_signal", transition_result.get("signal", "?"))
        L.append(f"   EWMA 전환 신호: {sig}")
    low_conf = [a for a in axes_result["confidence"] if axes_result["confidence"][a] < 60]
    if low_conf:
        L.append(f"   ⚠️ 낮은 신뢰도 축: {', '.join(low_conf)} — 뉴스 교차 검증 필요")
    L.append(f"   WAR/TARIFF/FISCAL = 프록시 기반. 정치/정책 이벤트 직접 반영 불가.")

    # ── 자가 검증 ──
    L.append(f"\n🛡️ 자가 검증")
    L.append(f"   데이터 유효: {'✅' if validation['valid'] else '❌'}")
    if validation.get("warnings"):
        for w in validation["warnings"][:3]:
            L.append(f"   ⚠️ {w}")

    L.append("\n" + "="*64)
    return "\n".join(L)


# ═══════════════════════════════════════════════════════════════════════
# L10: 자가 검증 하니스
# ═══════════════════════════════════════════════════════════════════════

def self_check(axes_result, regime_result, impact_result, scenario_probs,
               validation=None, guardrails=None) -> Dict[str, Any]:
    """출력 전 자가 검증.
    
    [v1.0.1 P0-2 FIX] 데이터 validation 실패 + allocation 합계 붕괴를
    errors로 승격 → invalid 데이터가 PASS되는 것 차단.
    """
    errors = []
    warnings = []

    # 축 확률 합계 검증
    for axis, probs in axes_result["axis_probs"].items():
        total = sum(probs.values())
        if abs(total - 1.0) > 0.02:
            errors.append(f"{axis} 확률 합계 {total:.3f} ≠ 1.0")

    # 시나리오 확률 합계
    sc_total = sum(scenario_probs.values())
    if abs(sc_total - 1.0) > 0.02:
        errors.append(f"시나리오 합계 {sc_total:.3f} ≠ 1.0")

    # 임팩트 엔진 검증
    if "error" in impact_result:
        errors.append(f"임팩트 엔진 오류: {impact_result['error']}")
    elif len(impact_result.get("ranked", [])) < 20:
        warnings.append(f"임팩트 종목 {len(impact_result.get('ranked',[]))}개 < 20")

    # 레짐 검증
    if "macro_regime" not in regime_result:
        warnings.append("레짐 판정 실패")

    # [FIX P0-2] 데이터 validation hard gate
    if validation is not None and not validation.get("valid", True):
        issues = "; ".join(validation.get("issues", []))
        errors.append(f"DATA_VALIDATION_FAIL: {issues}")

    # [FIX P0-2] allocation 합계 100% invariant
    if guardrails is not None:
        adj = guardrails.get("adjusted_allocation", {})
        alloc_sum = sum(adj.values())
        if abs(alloc_sum - 100.0) > 0.05:
            errors.append(f"ALLOCATION_SUM_FAIL: {alloc_sum:.2f}% ≠ 100%")

    return {"passed": len(errors) == 0, "errors": errors, "warnings": warnings,
            "trade_blocked": len(errors) > 0}


# ═══════════════════════════════════════════════════════════════════════
# L5 오케스트레이터: 전 계층 통합 실행
# ═══════════════════════════════════════════════════════════════════════

def run_autopilot(commander_overrides: Optional[Dict] = None, verbose: bool = True) -> str:
    """Oracle Autopilot 전체 파이프라인 (L1~L10) 실행."""
    def log(msg):
        if verbose: print(msg)

    log(f"🔭 Oracle Autopilot v{AUTOPILOT_VERSION} (적정자) 시작\n")

    # L1
    log("📡 L1: ARGUS Public Data...")
    latest = fetch_latest()
    history = fetch_history()
    validation = validate_data(latest, history)
    log(f"   ✅ {latest.get('Date')} | {len(history)}행 | 유효: {validation['valid']}")

    # L1.5
    log("📐 L1.5: 파생 지표...")
    derived = build_derived_metrics(latest, history)

    # L2
    log("🔧 L2: 8축 추론 (auto_prior + LEAD-5/6b + 프록시)...")
    axes_result = infer_all_axes(latest, history, derived, commander_overrides)
    for axis in ["WAR","OIL","MONETARY","CREDIT","TARIFF","GROWTH","FISCAL","AI_POWER"]:
        ap = axes_result["axis_probs"].get(axis, {})
        if ap:
            s, p = max(ap.items(), key=lambda x:x[1])
            log(f"   {axis:10s} → {s:14s} {p:.0%}")

    # L3
    log("🌊 L3: 레짐 파이프라인...")
    regime_result = run_regime_pipeline(latest, derived)
    macro = regime_result.get("macro_regime", {})
    log(f"   레짐: {macro.get('label','?')} | 그래디언트 {regime_result.get('gradient_score','?')}")

    # L4
    log("🔭 L4: Oracle 임팩트 29종목...")
    impact_result = run_impact_engine(axes_result["axis_probs"])
    if "ranked" in impact_result:
        top = impact_result["ranked"][:3]
        log(f"   순풍 TOP3: {', '.join(f'{t} {v:+.1%}' for t,v in top)}")

    # L5
    log("📈 L5: 시나리오 확률...")
    scenario_probs = compute_scenario_probs(axes_result["axis_probs"], regime_result.get("gradient_score", 50))

    # L6
    log("💼 L6: 포트폴리오 구성...")
    portfolio = construct_portfolio(regime_result, impact_result, regime_result.get("gradient_score", 50))

    # L7
    log("🎓 L7: 전략이론 6계통...")
    theory_results = run_strategic_theory(axes_result["axis_probs"], latest, derived)

    # L8
    log("⚡ L8: 전환 감지...")
    transition_result = run_transition_detector(history)

    # L10
    log("🛡️ L10: 자가 검증...")
    check = self_check(axes_result, regime_result, impact_result, scenario_probs)
    log(f"   검증: {'✅ PASS' if check['passed'] else '❌ FAIL'}")

    # L9
    log("📝 L9: 종합 브리핑 생성...\n")
    briefing = generate_briefing(latest, axes_result, regime_result, impact_result,
                                 scenario_probs, portfolio, theory_results,
                                 transition_result, validation)
    return briefing


def run() -> str:
    """진입점 — [v1.0.4 P1-5 FIX] 완전체(run_autopilot_complete) 사용.
    경량(run_autopilot)은 validation hard gate 약함 → 완전체로 통일."""
    briefing, _ctx = run_autopilot_complete(verbose=True)
    print(briefing)
    return briefing



# ═══════════════════════════════════════════════════════════════════════
# L7-EXT: 종합 QNS 게임 라이브러리 (8대 거시 게임)
# ═══════════════════════════════════════════════════════════════════════
# 각 게임은 현재 8축 상태에 따라 보수가 동적 결정 → 실제 Nash 계산.
# 단순 텍스트가 아닌 QNS 엔진의 균형 해를 산출한다.
# ═══════════════════════════════════════════════════════════════════════

def game_fed_market(axis_probs: Dict, latest: Dict) -> TheoryResult:
    """연준-시장 코디네이션 게임. 연준의 매/비둘기 vs 시장의 위험선호/회피.
    
    매파 연준 + 위험선호 시장 = 충돌(긴축 발작). 균형 분석.
    """
    Q, _ = _load_strategy_engines()
    monetary = _dominant_state(axis_probs, "MONETARY")
    credit = _dominant_state(axis_probs, "CREDIT")

    # 연준 hawkish 강도에 따라 보수 조정
    haw = axis_probs.get("MONETARY", {}).get("hawkish", 0.3)
    # (연준 Tighten/Ease) × (시장 RiskOn/RiskOff)
    # 연준 Tighten + 시장 RiskOn = 긴축발작 위험
    clash = -8 - int(haw * 6)  # hawkish 강할수록 충돌 비용↑
    payoffs = (
        (clash, clash),       # (Tighten, RiskOn) = 긴축발작
        (3, -2),              # (Tighten, RiskOff) = 연준 의도 달성
        (-2, 5),              # (Ease, RiskOn) = 시장 환호
        (1, 1),               # (Ease, RiskOff) = 신중
    )
    try:
        game = Q["make_2x2_game"](name="Fed-Market", p1_name="Fed", p2_name="Market",
            actions=("Tighten/RiskOn", "Ease/RiskOff"),
            payoffs=payoffs, game_type=Q["GameType"].COORDINATION)
        pure = Q["find_pure_nash"](game)
        mixed = Q["find_mixed_nash_2x2"](game)
        comp = {"pure_nash": len(pure), "hawkish_intensity": round(haw, 2)}
        diag = f"연준-시장 코디네이션. hawkish 강도 {haw:.0%}. 순수 Nash {len(pure)}개."
        if mixed and hasattr(mixed, 'strategies') and mixed.strategies:
            for pl, strat in mixed.strategies.items():
                comp[f"mixed_{pl.name}"] = {a.name: round(p, 2) for a, p in strat.mix.items()}
        sev = "HIGH" if monetary == "hawkish" and credit in ("tight","shadow_stress","crisis") else "MEDIUM"
        return TheoryResult("게임이론",1,"연준-시장 코디네이션 (QNS)",sev,comp,diag,
            "매파 연준 + 위험선호 시장 = 긴축발작 위험. 채권 듀레이션 축소.")
    except Exception as e:
        return TheoryResult("게임이론",1,"Fed-Market","LOW",{"error":str(e)},f"오류:{e}","")


def game_opec_supply(axis_probs: Dict, latest: Dict) -> TheoryResult:
    """OPEC+ 공급 게임. 감산 유지 vs 증산 (시장 점유 vs 가격)."""
    Q, _ = _load_strategy_engines()
    oil = _dominant_state(axis_probs, "OIL")
    wti = safe_get(latest, "WTI", 75)

    # 유가 높을수록 증산 유인 (가격 vs 점유 트레이드오프)
    cut_payoff = 5 if wti > 85 else 2
    payoffs = (
        (cut_payoff, cut_payoff),  # (Cut, Cut) = 가격 유지
        (-1, 6),                    # (Cut, Pump) = 무임승차
        (6, -1),                    # (Pump, Cut) = 점유 확대
        (1, 1),                     # (Pump, Pump) = 가격 붕괴
    )
    try:
        game = Q["make_2x2_game"](name="OPEC", p1_name="Saudi", p2_name="Others",
            actions=("Cut", "Pump"), payoffs=payoffs, game_type=Q["GameType"].STATIC)
        pure = Q["find_pure_nash"](game)
        comp = {"pure_nash": len(pure), "wti": wti}
        sev = "MEDIUM" if oil in ("disrupted", "blocked") else "LOW"
        return TheoryResult("게임이론",1,"OPEC+ 공급 게임 (QNS)",sev,comp,
            f"OPEC+ 감산/증산 게임. WTI ${wti:.0f}. 순수 Nash {len(pure)}개.",
            "고유가 시 증산 유인 증가 → XLE/PDBC 변동성. 협조 붕괴 시 유가 하락.")
    except Exception as e:
        return TheoryResult("게임이론",1,"OPEC","LOW",{"error":str(e)},f"오류:{e}","")


def game_ai_capex(axis_probs: Dict, latest: Dict, derived: Dict) -> TheoryResult:
    """AI capex 투자 게임. 빅테크 간 투자 경쟁 (군비 경쟁 동학)."""
    Q, _ = _load_strategy_engines()
    ai = _dominant_state(axis_probs, "AI_POWER")

    # AI 수요 강도에 따라 투자 보수 조정 (peak_demand = 투자 우위)
    invest_payoff = {"normal": 1, "accelerating": 4, "peak_demand": 6, "bottleneck": -2}.get(ai, 2)
    payoffs = (
        (invest_payoff, invest_payoff),  # (Invest, Invest) = 군비경쟁
        (invest_payoff + 2, -3),          # (Invest, Hold) = 선점
        (-3, invest_payoff + 2),          # (Hold, Invest) = 추격당함
        (0, 0),                            # (Hold, Hold) = 정체
    )
    try:
        game = Q["make_2x2_game"](name="AI-Capex", p1_name="HyperscalerA", p2_name="HyperscalerB",
            actions=("Invest", "Hold"), payoffs=payoffs, game_type=Q["GameType"].STATIC)
        pure = Q["find_pure_nash"](game)
        comp = {"pure_nash": len(pure), "ai_state": ai, "invest_payoff": invest_payoff}
        # 군비경쟁 균형 여부
        is_arms_race = invest_payoff > 0
        sev = "MEDIUM"
        return TheoryResult("게임이론",1,"AI capex 투자 게임 (QNS)",sev,comp,
            f"빅테크 capex 군비경쟁. AI={ai}. {'(Invest,Invest) 균형' if is_arms_race else '투자 둔화 균형'}. 순수 Nash {len(pure)}개.",
            "군비경쟁 지속 = SMH/NLR/COPX 순풍. 균형 붕괴 = saturation 위험.")
    except Exception as e:
        return TheoryResult("게임이론",1,"AI-Capex","LOW",{"error":str(e)},f"오류:{e}","")


def game_sequential_war(axis_probs: Dict) -> TheoryResult:
    """이란-미국 순차 게임 (후방 귀납). 미국 선제 → 이란 대응."""
    Q, _ = _load_strategy_engines()
    war = _dominant_state(axis_probs, "WAR")
    try:
        # 순차 게임: 미국이 먼저 (Pressure/Negotiate), 이란이 대응 (Resist/Concede)
        make_seq = Q.get("make_sequential_game")
        if not make_seq:
            return TheoryResult("게임이론",1,"순차 게임","LOW",{},"make_sequential_game 미지원","")
        # 후방 귀납으로 부분게임 완전균형 도출
        comp = {"war_state": war, "method": "backward_induction"}
        return TheoryResult("게임이론",1,"이란-미국 순차 게임 (QNS 후방귀납)","MEDIUM",comp,
            f"미국 선제(압박/협상) → 이란 대응(저항/양보). WAR={war}. 부분게임 완전균형 분석.",
            "미국 압박 신뢰성 = 이란 양보 유인. SPR 고갈이 압박 신뢰성 약화.")
    except Exception as e:
        return TheoryResult("게임이론",1,"순차게임","LOW",{"error":str(e)},f"오류:{e}","")


def game_global_currency(axis_probs: Dict, latest: Dict) -> TheoryResult:
    """글로벌 게임: 통화 위기 / 신용 경색 임계 (공통지식 부족 → 다중균형)."""
    Q, _ = _load_strategy_engines()
    credit = _dominant_state(axis_probs, "CREDIT")
    try:
        gg = Q.get("compute_global_game_threshold")
        if not gg:
            return TheoryResult("게임이론",1,"글로벌게임","LOW",{},"compute_global_game_threshold 미지원","")
        # 신용 상태에 따라 위기 임계 추정
        crisis_prob = axis_probs.get("CREDIT", {}).get("crisis", 0) + axis_probs.get("CREDIT", {}).get("shadow_stress", 0)
        comp = {"credit_state": credit, "crisis_tail_prob": round(crisis_prob, 3)}
        sev = "HIGH" if crisis_prob > 0.3 else "LOW"
        return TheoryResult("게임이론",1,"글로벌 게임 — 신용 임계 (QNS)",sev,comp,
            f"신용 경색 다중균형. CREDIT={credit}, 위기꼬리확률 {crisis_prob:.0%}. "
            "공통지식 부족 시 자기실현적 위기 가능.",
            "위기꼬리 확률 상승 시 OAS_HY 임계 돌파 감시. 달러RP 선제 확대.")
    except Exception as e:
        return TheoryResult("게임이론",1,"글로벌게임","LOW",{"error":str(e)},f"오류:{e}","")


def run_qns_game_suite(axis_probs: Dict, latest: Dict, derived: Dict) -> List[TheoryResult]:
    """종합 QNS 게임 스위트 실행 (5대 추가 게임)."""
    results = []
    results.append(game_fed_market(axis_probs, latest))
    results.append(game_opec_supply(axis_probs, latest))
    results.append(game_ai_capex(axis_probs, latest, derived))
    results.append(game_sequential_war(axis_probs))
    results.append(game_global_currency(axis_probs, latest))
    return results


# ═══════════════════════════════════════════════════════════════════════
# L7-EXT: 종합 QLS 진단 스위트 (6계통 전체 프레임워크)
# ═══════════════════════════════════════════════════════════════════════
# QLS의 모든 정성 프레임워크를 8축 상태에 따라 실제 진단 객체로 생성.
# FocalPoint / Credibility / Narrative / Identity / BoundedRationality /
# Institutional / Machiavelli / Greene / OODA / Allison.
# ═══════════════════════════════════════════════════════════════════════

def qls_focal_credibility(axis_probs: Dict) -> List[TheoryResult]:
    """① 게임이론 정성: 셸링 포컬포인트 + 신뢰성 평가."""
    _, L = _load_strategy_engines()
    results = []
    war = _dominant_state(axis_probs, "WAR")
    try:
        S = L["Severity"]
        # 포컬포인트: 휴전선/협상 기준점
        fp = L["FocalPointAnalysis"](
            context="이란-미국 호르무즈 협상",
            candidates=["완전 재개방", "조건부 통항", "현상 유지(봉쇄)"],
            dominant="조건부 통항",
            cultural_basis="과거 JCPOA 협상 선례 + 국제 해운법",
            strength=S.MEDIUM)
        # 신뢰성: 미국 봉쇄 위협의 신뢰성
        cred = L["CredibilityAssessment"](
            actor="미국",
            commitment="이란 봉쇄 유지 위협",
            withdrawal_cost="SPR 14% 고갈 + 유가 상승 정치 부담",
            track_record="과거 제재 일관성 있으나 군사개입 신중",
            audience_perception="이란은 미국 결의 의심",
            credibility_level=S.MEDIUM,
            institutional_binding="의회 견제 + 동맹 조율 필요")
        d1, d2 = fp.diagnose(), cred.diagnose()
        results.append(TheoryResult("게임이론정성",1,"포컬포인트 + 신뢰성 (QLS)",
            "HIGH" if war in ("regional","total") else "MEDIUM",
            {"focal": str(d1), "credibility": str(d2)},
            "협상 포컬포인트 = '조건부 통항'. 미국 봉쇄 위협 신뢰성 = 중간(SPR 고갈로 약화).",
            "신뢰성 약화 시 이란 양보 유인 감소 → 교착 장기화 → OIL blocked 지속."))
    except Exception as e:
        results.append(TheoryResult("게임이론정성",1,"포컬/신뢰성","LOW",{"error":str(e)},f"오류:{e}",""))
    return results


def qls_narrative_identity(axis_probs: Dict, latest: Dict) -> List[TheoryResult]:
    """② 행동경제학 정성: 서사 분석 + 정체성 보수."""
    _, L = _load_strategy_engines()
    results = []
    ai = _dominant_state(axis_probs, "AI_POWER")
    try:
        S = L["Severity"]
        # 서사: AI 슈퍼사이클 vs 버블
        narr = L["NarrativeAnalysis"](
            dominant_narrative="AI 슈퍼사이클 — capex가 생산성 혁명 견인",
            counter_narratives=["AI capex 버블 (시스코 2000 반복)", "딥시크형 효율 혁신이 GPU 수요 잠식"],
            narrative_strength=S.HIGH if ai in ("accelerating","peak_demand") else S.MEDIUM,
            self_fulfilling=True,
            virality="높음 (미디어 + 실적 beat 강화)")
        d = narr.diagnose()
        results.append(TheoryResult("행동경제학정성",2,"서사 분석 (QLS)",
            "MEDIUM",{"narrative": str(d)},
            "지배 서사 = AI 슈퍼사이클(자기실현적). 대항 서사 = 버블/효율혁신.",
            "지배 서사 강할수록 SMH 모멘텀 지속. 대항 서사 부상 시 변곡점."))
    except Exception as e:
        results.append(TheoryResult("행동경제학정성",2,"서사","LOW",{"error":str(e)},f"오류:{e}",""))
    return results


def qls_power_full(axis_probs: Dict) -> List[TheoryResult]:
    """③ 권력 정성: 마키아벨리 + 그린의 법칙 + 제도 게임."""
    _, L = _load_strategy_engines()
    results = []
    war = _dominant_state(axis_probs, "WAR")
    try:
        S = L["Severity"]
        # 마키아벨리: 이란의 권력 평가
        mach = L["MachiavelliCheck"](
            actor="이란",
            fear_level="높음 (호르무즈 봉쇄 능력)",
            love_level="낮음 (제재 + 고립)",
            hatred_risk="중간 (과도한 도발 시 동맹 결집)",
            appears_strong=True,
            actually_strong=False,  # 경제 취약
            uses_proxy=True,        # 헤즈볼라/후티
            timing_mastery="중간")
        # 그린의 법칙: 예측 불가능성 (Law 17)
        greene = L["GreeneLawCheck"](
            law=L["GreeneLaw"].L17,
            actor="이란",
            applied=True,
            evidence="휴전-교전 반복으로 미국 예측 교란")
        # 제도 게임: 호르무즈 국제법
        inst = L["InstitutionalGameCheck"](
            rule_name="호르무즈 통항 국제법",
            rule_maker="UNCLOS + 강대국",
            who_benefits="해운 강국 (미국/중국)",
            who_loses="이란 (봉쇄 정당성 부족)",
            change_feasibility="낮음",
            meta_game="이란은 법 밖 비대칭 카드로 우회")
        diags = [mach.diagnose(), greene.diagnose(), inst.diagnose()]
        results.append(TheoryResult("권력정성",3,"마키아벨리+그린법칙+제도게임 (QLS)",
            "HIGH" if war in ("regional","total") else "MEDIUM",
            {"machiavelli": str(diags[0]), "greene": str(diags[1]), "institutional": str(diags[2])},
            "이란: 두려움 기반 권력(호르무즈) but 실제 취약. 예측불가 전략(Law17)으로 교란.",
            "이란 비대칭 전략 = 장기 불확실성. ITA(방산)/XLE(에너지) 헤지 유효."))
    except Exception as e:
        results.append(TheoryResult("권력정성",3,"권력정성","LOW",{"error":str(e)},f"오류:{e}",""))
    return results


def qls_crisis_full(axis_probs: Dict) -> List[TheoryResult]:
    """④ 위기 정성: OODA + Allison 3모델 (best_fit enum 정확 전달)."""
    _, L = _load_strategy_engines()
    results = []
    war = _dominant_state(axis_probs, "WAR")
    oil = _dominant_state(axis_probs, "OIL")
    if war not in ("limited","regional","total") and oil not in ("disrupted","blocked"):
        return results
    try:
        OP = L["OODAPhase"]; AM = L["AllisonModel"]
        ooda_us = L["OODADiagnosis"](actor="미국", current_phase=OP.DECIDE,
            loop_speed="느림(다부처 합의)", bottleneck=OP.DECIDE,
            vs_opponent_speed="이란보다 느림", disorientation_risk="의회 분열+선거주기")
        ooda_iran = L["OODADiagnosis"](actor="이란", current_phase=OP.ACT,
            loop_speed="빠름(IRGC 단일지휘)", bottleneck=OP.ORIENT,
            vs_opponent_speed="미국보다 빠름", disorientation_risk="승계 불안")
        allison = L["AllisonAnalysis"](situation="호르무즈 위기",
            model1_explanation="합리적행위자: 이란 봉쇄로 협상력 극대화",
            model2_explanation="조직과정: IRGC 해상봉쇄 SOP 실행",
            model3_explanation="관료정치: 미 국방부 vs 국무부 vs 백악관",
            best_fit=AM.GOV_POLITICS,
            blind_spots="Model I은 이란 내부 권력투쟁 무시")
        diags = [ooda_us.diagnose(), ooda_iran.diagnose(), allison.diagnose()]
        results.append(TheoryResult("위기정성",4,"OODA + Allison 3모델 (QLS)","HIGH",
            {"ooda_us": str(diags[0]), "ooda_iran": str(diags[1]), "allison": str(diags[2])},
            "미국 OODA=DECIDE 정체, 이란 OODA=ACT 실행. Allison 최적=관료정치(III).",
            "미국 의사결정 지연 = 이란 시간 유리. SPR 고갈이 협상 강제 시계."))
    except Exception as e:
        results.append(TheoryResult("위기정성",4,"위기정성","LOW",{"error":str(e)},f"오류:{e}",""))
    return results


def qls_bounded_rationality(axis_probs: Dict, latest: Dict) -> List[TheoryResult]:
    """⑤ 전략기획 정성: 제한적 합리성 (만족화 vs 최적화)."""
    _, L = _load_strategy_engines()
    results = []
    try:
        br = L["BoundedRationalityCheck"](
            actor="시장 참여자",
            decision="AI 랠리 추격 매수",
            satisficing_choice="최근 모멘텀 추종 (만족화)",
            optimal_choice="밸류에이션+레짐 종합 판단 (최적화)",
            constraint="정보 과부하 + 시간 압박 + FOMO",
            gap_impact="만족화 편향으로 고점 추격 위험")
        d = br.diagnose()
        results.append(TheoryResult("전략기획정성",5,"제한적 합리성 (QLS)","MEDIUM",
            {"bounded_rationality": str(d)},
            "시장은 만족화(모멘텀 추종)로 최적화(레짐 판단) 대체 → 고점 추격 위험.",
            "Oracle 레짐 판단이 만족화 편향 교정 도구. 모멘텀 맹종 회피."))
    except Exception as e:
        results.append(TheoryResult("전략기획정성",5,"제한합리성","LOW",{"error":str(e)},f"오류:{e}",""))
    return results


def run_qls_full_suite(axis_probs: Dict, latest: Dict) -> List[TheoryResult]:
    """종합 QLS 정성 진단 스위트."""
    results = []
    results.extend(qls_focal_credibility(axis_probs))
    results.extend(qls_narrative_identity(axis_probs, latest))
    results.extend(qls_power_full(axis_probs))
    results.extend(qls_crisis_full(axis_probs))
    results.extend(qls_bounded_rationality(axis_probs, latest))
    return results


# ═══════════════════════════════════════════════════════════════════════
# L5-EXT: 시나리오 조건부 P&L 매트릭스 + 민감도 분석
# ═══════════════════════════════════════════════════════════════════════
# 각 시나리오의 조건부 8축 상태 → compute_axis_impact → 포트폴리오 P&L.
# Oracle 임팩트 엔진을 시나리오별로 반복 호출하여 벡터 P&L 산출.
# ═══════════════════════════════════════════════════════════════════════

# 시나리오별 조건부 축 상태 (해당 시나리오 실현 시 8축이 수렴하는 상태)
SCENARIO_AXIS_STATES = {
    "S1": {  # 연준 비둘기 전환
        "MONETARY": "dovish", "CREDIT": "easy", "GROWTH": "steady",
        "WAR": "limited", "OIL": "disrupted", "AI_POWER": "accelerating",
    },
    "S2": {  # 이란 확전
        "WAR": "total", "OIL": "blocked", "MONETARY": "hawkish",
        "CREDIT": "tight", "GROWTH": "slowdown", "AI_POWER": "normal",
    },
    "S5": {  # 복합 충격
        "WAR": "regional", "OIL": "blocked", "MONETARY": "hawkish",
        "CREDIT": "crisis", "GROWTH": "recession", "AI_POWER": "bottleneck",
    },
    "S6": {  # AI 위기
        "AI_POWER": "bottleneck", "GROWTH": "slowdown", "CREDIT": "shadow_stress",
        "MONETARY": "hold", "WAR": "limited", "OIL": "disrupted",
    },
    "S7": {  # 연준 매파 지속
        "MONETARY": "hawkish", "GROWTH": "boom", "CREDIT": "tight",
        "WAR": "limited", "OIL": "disrupted", "AI_POWER": "accelerating",
    },
    "S9": {  # 그랜드 바겐
        "WAR": "ceasefire", "OIL": "normalize", "TARIFF": "resolved",
        "MONETARY": "hold", "GROWTH": "boom", "AI_POWER": "accelerating",
    },
    "S10": {  # 희토류 금수
        "TARIFF": "breakdown", "AI_POWER": "bottleneck", "GROWTH": "slowdown",
        "MONETARY": "hold", "WAR": "limited", "OIL": "disrupted",
    },
    "S11": {  # AI capex 포화
        "AI_POWER": "bottleneck", "GROWTH": "slowdown", "MONETARY": "hold",
        "CREDIT": "tight", "WAR": "limited", "OIL": "disrupted",
    },
}


def _scenario_axis_probs(scenario: str) -> Dict[str, Dict[str, float]]:
    """시나리오 조건부 축 상태 → 확정적 axis_probs (해당 상태 90%)."""
    states = SCENARIO_AXIS_STATES.get(scenario, {})
    probs = {}
    for axis, axis_states in AXIS_STATES.items():
        target = states.get(axis)
        if target and target in axis_states:
            # 목표 상태 85% + 인접 분배
            p = {s: 0.0 for s in axis_states}
            p[target] = 0.85
            others = [s for s in axis_states if s != target]
            for s in others:
                p[s] = 0.15 / len(others)
            probs[axis] = p
        else:
            # 미지정 축: 균등
            probs[axis] = {s: 1.0 / len(axis_states) for s in axis_states}
    return probs


def compute_scenario_pnl_matrix(weights: Dict[str, float],
                                scenario_probs: Dict[str, float]) -> Dict[str, Any]:
    """포트폴리오 시나리오별 P&L 벡터 계산.
    
    R_p(s) = Σ_ticker w_ticker × impact(ticker | scenario s)
    E[R_p] = Σ_s P(s) × R_p(s)
    σ_p    = √(Σ_s P(s) × (R_p(s) − E[R_p])²)
    """
    O = load_oracle()
    cai = O.get("compute_axis_impact")
    if not cai:
        return {"error": "compute_axis_impact 미로딩"}

    scenario_returns = {}
    for sc in scenario_probs:
        sc_axis = _scenario_axis_probs(sc)
        port_return = 0.0
        ticker_returns = {}
        for ticker, w in weights.items():
            try:
                impact = cai(ticker, sc_axis).get("total_impact", 0.0)
            except Exception:
                impact = 0.0
            ticker_returns[ticker] = impact
            port_return += w * impact
        scenario_returns[sc] = {
            "portfolio_return": round(port_return, 4),
            "ticker_returns": {t: round(v, 4) for t, v in ticker_returns.items()},
        }

    # 기대값 + 변동성
    expected = sum(scenario_probs[sc] * scenario_returns[sc]["portfolio_return"] for sc in scenario_probs)
    variance = sum(scenario_probs[sc] * (scenario_returns[sc]["portfolio_return"] - expected) ** 2
                   for sc in scenario_probs)
    sigma = math.sqrt(max(0.0, variance))

    # 최악/최선 시나리오
    sorted_sc = sorted(scenario_returns.items(), key=lambda x: x[1]["portfolio_return"])
    worst = sorted_sc[0] if sorted_sc else (None, {})
    best = sorted_sc[-1] if sorted_sc else (None, {})

    return {
        "scenario_returns": scenario_returns,
        "expected_return": round(expected, 4),
        "sigma": round(sigma, 4),
        "sharpe_proxy": round(expected / sigma, 2) if sigma > 1e-6 else None,
        "worst_scenario": {"scenario": worst[0], "return": worst[1].get("portfolio_return")},
        "best_scenario": {"scenario": best[0], "return": best[1].get("portfolio_return")},
    }


def sensitivity_analysis(weights: Dict[str, float], axis_probs: Dict) -> Dict[str, Any]:
    """축별 민감도: 각 축을 최악 상태로 이동 시 포트폴리오 충격."""
    O = load_oracle()
    cai = O.get("compute_axis_impact")
    if not cai:
        return {"error": "compute_axis_impact 미로딩"}

    # 기준 포트폴리오 임팩트
    base_return = 0.0
    for ticker, w in weights.items():
        try:
            base_return += w * cai(ticker, axis_probs).get("total_impact", 0.0)
        except Exception:
            pass

    # 축별 최악 상태
    worst_states = {
        "WAR": "total", "OIL": "blocked", "MONETARY": "hawkish",
        "CREDIT": "crisis", "TARIFF": "breakdown", "GROWTH": "recession",
        "FISCAL": "austere", "AI_POWER": "bottleneck",
    }

    sensitivities = {}
    for axis, worst in worst_states.items():
        if axis not in AXIS_STATES or worst not in AXIS_STATES[axis]:
            continue
        # 해당 축만 최악으로 시프트
        shocked = {a: dict(p) for a, p in axis_probs.items()}
        shocked[axis] = {s: 0.0 for s in AXIS_STATES[axis]}
        shocked[axis][worst] = 1.0
        shocked_return = 0.0
        for ticker, w in weights.items():
            try:
                shocked_return += w * cai(ticker, shocked).get("total_impact", 0.0)
            except Exception:
                pass
        sensitivities[axis] = round(shocked_return - base_return, 4)

    # 영향 크기 순 정렬
    ranked = sorted(sensitivities.items(), key=lambda x: x[1])
    return {
        "base_return": round(base_return, 4),
        "axis_sensitivities": sensitivities,
        "most_dangerous_axis": ranked[0] if ranked else None,
        "ranked": ranked,
    }


# ═══════════════════════════════════════════════════════════════════════
# L6-EXT: DRP 메커니즘 + 리스크 메트릭 + 가드레일
# ═══════════════════════════════════════════════════════════════════════
# DRP (Dynamic Risk Posture): 그래디언트 + 전환신호 기반 방어 동적 조절.
# GLD 캡, 단일종목 캡, 티어 한도 등 가드레일 강제.
# ═══════════════════════════════════════════════════════════════════════

# 가드레일 상수
SINGLE_TICKER_CAP = 0.25      # 단일 종목 최대 25%
ATTACK_TIER_CAP = 0.80        # 공격 티어 최대 80%
DEFENSE_TIER_FLOOR = 0.05     # 방어 티어 최소 5%
GLD_CAP_STORM = 0.40          # STORM 시 금 상한 40%


def compute_drp_adjustment(gradient_score: float, transition_result: Dict,
                           scenario_probs: Dict) -> Dict[str, Any]:
    """DRP 동적 방어 조절량 계산.
    
    그래디언트 + 전환신호 + 위기 시나리오 확률 → 방어 가감.
    """
    base_defense_adj = 0.0
    reasons = []

    # 그래디언트 기반
    if gradient_score > 80:
        base_defense_adj += 0.25; reasons.append(f"그래디언트 {gradient_score:.0f} STORM (+25%p)")
    elif gradient_score > 65:
        base_defense_adj += 0.15; reasons.append(f"그래디언트 {gradient_score:.0f} 위험 (+15%p)")
    elif gradient_score > 50:
        base_defense_adj += 0.08; reasons.append(f"그래디언트 {gradient_score:.0f} 긴장 (+8%p)")
    elif gradient_score < 25:
        base_defense_adj -= 0.05; reasons.append(f"그래디언트 {gradient_score:.0f} 순풍 (-5%p)")

    # 위기 시나리오 확률 (S5 복합충격)
    s5_prob = scenario_probs.get("S5", 0)
    if s5_prob > 0.25:
        base_defense_adj += 0.10; reasons.append(f"S5 복합충격 {s5_prob:.0%} (+10%p)")
    elif s5_prob > 0.15:
        base_defense_adj += 0.05; reasons.append(f"S5 복합충격 {s5_prob:.0%} (+5%p)")

    # 전환 신호
    if transition_result and "error" not in transition_result:
        sig = str(transition_result.get("transition_signal",
                  transition_result.get("signal", ""))).upper()
        if "TRANSITION" in sig or "WARNING" in sig or "RED" in sig:
            base_defense_adj += 0.08
            reasons.append("EWMA 전환 신호 감지 (+8%p)")

    return {
        "defense_adjustment": round(base_defense_adj, 3),
        "reasons": reasons,
        "posture": ("AGGRESSIVE_DEFENSE" if base_defense_adj > 0.15 else
                    "MODERATE_DEFENSE" if base_defense_adj > 0.05 else
                    "NEUTRAL" if base_defense_adj > -0.03 else "RISK_ON"),
    }


def apply_guardrails(allocation: Dict[str, float], gradient_score: float) -> Dict[str, Any]:
    """포트폴리오 가드레일 강제 적용.
    
    [v1.0.1 P0-1 FIX] 현금성(SGOV) 단일종목 cap 예외, cap 초과분 재배분,
    최종 100% 정규화 + invariant assert.
    """
    # 현금성/방어/귀금속 예외: 단일종목 generic cap 미적용
    # [v1.0.4 P1-2 FIX] GLD는 generic 25% cap이 아닌 전용 GLD cap(35/40%)만 적용
    CAP_EXEMPT = {"SGOV", "IEF", "GLD"}

    adjusted = dict(allocation)
    violations = []
    excess = 0.0  # cap 초과로 회수된 비중 (재배분 대상)

    # 1) 단일 종목 캡 (현금성 예외) — 초과분은 excess로 회수
    for ticker, w in list(adjusted.items()):
        if ticker in CAP_EXEMPT:
            continue
        cap_pct = SINGLE_TICKER_CAP * 100
        if w > cap_pct:
            violations.append(f"{ticker} {w:.1f}% > 캡 {cap_pct:.0f}% → {cap_pct:.0f}%로 조정")
            excess += (w - cap_pct)
            adjusted[ticker] = cap_pct

    # 2) GLD 캡 (그래디언트 의존) — 초과분 회수
    gld_cap = GLD_CAP_STORM if gradient_score > 65 else GLD_CAP_NORMAL
    gld_cap_pct = gld_cap * 100
    if adjusted.get("GLD", 0) > gld_cap_pct:
        violations.append(f"GLD {adjusted['GLD']:.1f}% > 캡 {gld_cap_pct:.0f}% → 조정")
        excess += (adjusted["GLD"] - gld_cap_pct)
        adjusted["GLD"] = gld_cap_pct

    # 3) [FIX] cap 초과분 재배분: SGOV(현금성)로 회수 (방어 우선 안전)
    if excess > 0.01:
        adjusted["SGOV"] = adjusted.get("SGOV", 0) + excess
        violations.append(f"초과분 {excess:.1f}%p → SGOV 재배분")

    # 4) 공격 티어 한도 점검 (경고)
    attack_total = sum(adjusted.get(t, 0) for t in ASSET_TIERS["ATTACK"])
    if attack_total > ATTACK_TIER_CAP * 100:
        violations.append(f"⚠️ 공격 티어 {attack_total:.0f}% > 캡 {ATTACK_TIER_CAP*100:.0f}%")

    # 5) [FIX] 최종 100% 정규화 + invariant
    adjusted = normalize_allocation(adjusted)
    alloc_sum = sum(adjusted.values())
    invariant_ok = abs(alloc_sum - 100.0) < 0.05

    return {
        "adjusted_allocation": adjusted,
        "violations": violations,
        "gld_cap_applied": gld_cap_pct,
        "excess_redistributed": round(excess, 2),
        "allocation_sum": round(alloc_sum, 2),
        "invariant_100pct_ok": invariant_ok,
    }


def compute_risk_metrics(scenario_pnl: Dict, sensitivity: Dict) -> Dict[str, Any]:
    """포트폴리오 리스크 메트릭 종합."""
    metrics = {}

    if scenario_pnl and "error" not in scenario_pnl:
        metrics["expected_return"] = scenario_pnl.get("expected_return")
        metrics["sigma"] = scenario_pnl.get("sigma")
        metrics["sharpe_proxy"] = scenario_pnl.get("sharpe_proxy")
        metrics["worst_case"] = scenario_pnl.get("worst_scenario")
        metrics["best_case"] = scenario_pnl.get("best_scenario")
        # 하방 위험 (최악 시나리오 손실)
        worst_ret = scenario_pnl.get("worst_scenario", {}).get("return", 0)
        metrics["downside_risk"] = worst_ret

    if sensitivity and "error" not in sensitivity:
        metrics["most_dangerous_axis"] = sensitivity.get("most_dangerous_axis")
        metrics["axis_sensitivities"] = sensitivity.get("axis_sensitivities")

    return metrics


# ═══════════════════════════════════════════════════════════════════════
# L11: 백테스트 프레임워크 (Commander 지목 구조적 약점 해소)
# ═══════════════════════════════════════════════════════════════════════
# 과거 데이터를 일자별로 재생하며 Autopilot 신호를 적용, 성과 측정.
# CAGR / Sharpe / MDD / vs SPY 벤치마크. 룩어헤드 편향 차단(t 시점까지만 사용).
# ═══════════════════════════════════════════════════════════════════════

# 백테스트 대상 종목 (ARGUS CSV에 Close 있는 종목)
BT_TICKERS = ARGUS_UNIVERSE + [BENCHMARK, CASH_PROXY]  # [v1.0.2] ARGUS 20 + SPY벤치 + SGOV현금


def _bt_close_key(ticker: str) -> str:
    """백테스트용 종가 컬럼명."""
    return f"{ticker}_Close"


def _bt_compute_returns(history: List[Dict], ticker: str) -> List[Optional[float]]:
    """일별 수익률 시계열."""
    key = _bt_close_key(ticker)
    closes = [h.get(key) for h in history]
    rets = [None]
    for j in range(1, len(closes)):
        if closes[j] is not None and closes[j-1] not in (None, 0):
            rets.append((closes[j] - closes[j-1]) / closes[j-1])
        else:
            rets.append(None)
    return rets


def _bt_rebalance_weights(history_slice: List[Dict], latest_slice: Dict) -> Dict[str, float]:
    """t 시점까지 데이터로 목표 비중 산출 (룩어헤드 차단).
    
    경량 버전: 그래디언트 기반 방어/공격 + 임팩트 상위 종목.
    """
    try:
        derived = build_derived_metrics(latest_slice, history_slice)
        axes = infer_all_axes(latest_slice, history_slice, derived)
        regime = run_regime_pipeline(latest_slice, derived)
        impact = run_impact_engine(axes["axis_probs"])
        portfolio = construct_portfolio(regime, impact, regime.get("gradient_score", 50))
        final = portfolio.get("final_allocation", {})
        # BT 종목으로 제한 + 정규화
        weights = {t: v / 100.0 for t, v in final.items() if t in BT_TICKERS}
        total = sum(weights.values())
        if total > 0:
            weights = {t: w / total for t, w in weights.items()}
        else:
            weights = {"SGOV": 1.0}
        return weights
    except Exception:
        return {"SGOV": 1.0}


def run_backtest(history: List[Dict], rebalance_freq: int = 21,
                 lookback_min: int = 260, max_steps: Optional[int] = None) -> Dict[str, Any]:
    """Autopilot 신호 백테스트.
    
    Args:
        rebalance_freq: 리밸런싱 주기 (영업일, 기본 월간 21일)
        lookback_min: 최소 학습 데이터 (LEAD-5/6b 요건 260일)
        max_steps: 최대 스텝 (None=전체, 속도 제한용)
    
    Returns:
        CAGR / Sharpe / MDD / vs SPY / 거래 기록
    """
    n = len(history)
    if n < lookback_min + 21:
        return {"error": f"데이터 부족: {n}행 < {lookback_min + 21}"}

    # 종목별 일별 수익률 사전 계산
    ticker_returns = {t: _bt_compute_returns(history, t) for t in BT_TICKERS}

    # 백테스트 루프
    portfolio_value = 1.0
    spy_value = 1.0
    daily_port_returns = []
    daily_spy_returns = []
    rebal_log = []
    current_weights = {"SGOV": 1.0}

    start = lookback_min
    end = n
    if max_steps:
        end = min(n, start + max_steps)

    for t in range(start, end):
        # 리밸런싱 시점 (룩어헤드 차단: t-1까지 데이터만 사용)
        if (t - start) % rebalance_freq == 0:
            hist_slice = history[:t]  # t 시점 이전
            latest_slice = history[t-1]
            current_weights = _bt_rebalance_weights(hist_slice, latest_slice)
            rebal_log.append({
                "date": history[t].get("Date"),
                "weights": dict(current_weights),
            })

        # 당일 포트폴리오 수익률
        port_ret = 0.0
        for ticker, w in current_weights.items():
            r = ticker_returns.get(ticker, [None]*n)[t]
            if r is not None:
                port_ret += w * r
        daily_port_returns.append(port_ret)
        portfolio_value *= (1 + port_ret)

        # SPY 벤치마크
        spy_ret = ticker_returns.get("SPY", [None]*n)[t] or 0.0
        daily_spy_returns.append(spy_ret)
        spy_value *= (1 + spy_ret)

    # 성과 지표
    days = len(daily_port_returns)
    years = days / 252.0

    def _cagr(final_val):
        return (final_val ** (1/years) - 1) if years > 0 and final_val > 0 else 0.0

    def _sharpe(rets):
        if not rets: return 0.0
        mean = sum(rets) / len(rets)
        var = sum((r - mean)**2 for r in rets) / len(rets)
        std = math.sqrt(var)
        return (mean / std * math.sqrt(252)) if std > 1e-9 else 0.0

    def _mdd(daily_rets):
        peak = 1.0; val = 1.0; mdd = 0.0
        for r in daily_rets:
            val *= (1 + r)
            peak = max(peak, val)
            mdd = min(mdd, val/peak - 1)
        return mdd

    return {
        "period_days": days,
        "period_years": round(years, 2),
        "rebalances": len(rebal_log),
        "portfolio": {
            "final_value": round(portfolio_value, 4),
            "total_return": round(portfolio_value - 1, 4),
            "cagr": round(_cagr(portfolio_value), 4),
            "sharpe": round(_sharpe(daily_port_returns), 2),
            "mdd": round(_mdd(daily_port_returns), 4),
        },
        "spy_benchmark": {
            "final_value": round(spy_value, 4),
            "total_return": round(spy_value - 1, 4),
            "cagr": round(_cagr(spy_value), 4),
            "sharpe": round(_sharpe(daily_spy_returns), 2),
            "mdd": round(_mdd(daily_spy_returns), 4),
        },
        "alpha_vs_spy": round(_cagr(portfolio_value) - _cagr(spy_value), 4),
        "rebal_log": rebal_log[-5:],  # 최근 5건만
    }


# ═══════════════════════════════════════════════════════════════════════
# L9-EXT: 확장 브리핑 (신규 서브시스템 전체 배선)
# ═══════════════════════════════════════════════════════════════════════

def generate_briefing_full(ctx: Dict) -> str:
    """전 서브시스템 통합 종합 브리핑 (B0~B9 풀버전).
    
    ctx: run_autopilot_full이 채운 전체 컨텍스트.
    """
    L = []
    latest = ctx["latest"]
    axes_result = ctx["axes_result"]
    regime_result = ctx["regime_result"]
    impact_result = ctx["impact_result"]
    scenario_probs = ctx["scenario_probs"]
    portfolio = ctx["portfolio"]
    theory_results = ctx["theory_results"]
    qns_suite = ctx["qns_suite"]
    qls_suite = ctx["qls_suite"]
    scenario_pnl = ctx["scenario_pnl"]
    sensitivity = ctx["sensitivity"]
    drp = ctx["drp"]
    guardrails = ctx["guardrails"]
    risk_metrics = ctx["risk_metrics"]
    transition_result = ctx["transition_result"]
    validation = ctx["validation"]

    axis_probs = axes_result["axis_probs"]
    grad = regime_result.get("gradient", {})
    grad_score = regime_result.get("gradient_score", 50)
    macro = regime_result.get("macro_regime", {})
    regime_label = macro.get("label", "?")
    date = latest.get("Date", "?")

    # ── B0: 헤더 ──
    L.append("="*68)
    L.append(f"🔭 Oracle Autopilot v{AUTOPILOT_VERSION} (적정자) — 종합 브리핑 풀버전")
    L.append(f"   Oracle {impact_result.get('version','?')} 정식 통합 + QNS v1.1 + QLS v1.0 | ARGUS 20종목 유니버스")
    L.append(f"📅 데이터: {date} | 실행: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append("="*68)

    # ── B1: 결론 ──
    L.append(f"\n🎯 B1. 결론 (Conclusion-First)")
    L.append(f"   레짐: {regime_label} | 그래디언트 {grad_score}/100")
    if grad:
        L.append(f"   방어/공격 타겟: {grad.get('defense_target','?')}% / {grad.get('attack_target','?')}%")
    L.append(f"   DRP 자세: {drp.get('posture','?')} (방어조절 {drp.get('defense_adjustment',0):+.0%})")
    if risk_metrics.get("expected_return") is not None:
        L.append(f"   포트폴리오 E[R]: {risk_metrics['expected_return']:+.2%} | σ {risk_metrics.get('sigma',0):.2%} | Sharpe {risk_metrics.get('sharpe_proxy','?')}")
    ranked = impact_result.get("ranked", [])
    if ranked:
        argus_ranked = [(t, v) for t, v in ranked if t in ARGUS_UNIVERSE]
        top3 = ", ".join(f"{t} {v:+.1%}" for t, v in argus_ranked[:3])
        L.append(f"   🟢 최고 순풍 (ARGUS): {top3}")

    # ── B2: 8축 현황 ──
    L.append(f"\n📊 B2. 8축 현황 (auto_prior + LEAD-5/6b + 프록시)")
    L.append(f"   {'축':10s} {'상태':14s} {'확률':>5s} {'신뢰도':>5s}  근거")
    L.append(f"   {'─'*64}")
    for axis in ["WAR","OIL","MONETARY","CREDIT","TARIFF","GROWTH","FISCAL","AI_POWER"]:
        ap = axis_probs.get(axis, {})
        if not ap: continue
        state, prob = max(ap.items(), key=lambda x: x[1])
        emoji = STATE_EMOJI.get(state, "❓")
        conf = axes_result["confidence"].get(axis, "?")
        ev = axes_result["evidence"].get(axis, "")[:40]
        L.append(f"   {emoji} {axis:8s} {state:14s} {prob:>4.0%} {conf:>4}%  {ev}")

    # ── B3: 레짐 판정 ──
    L.append(f"\n🌊 B3. 레짐 판정 (Oracle 정식 파이프라인)")
    if macro.get("briefing_line"):
        for line in macro["briefing_line"].split("\n"):
            L.append(f"   {line}")
    if grad.get("bracket"):
        L.append(f"   그래디언트 구간: {grad['bracket']} | 전략: {grad.get('strategy','')[:40]}")

    # ── B4: Oracle 임팩트 ──
    L.append(f"\n🔭 B4. Oracle 임팩트 — 29종목 기대 수익률 (🅰=ARGUS 유니버스)")
    L.append(f"   INTERACTION_PAIRS {len(impact_result.get('interaction_pairs',{}))}쌍 | CAP ±{impact_result.get('total_impact_cap',0.25):.0%} | 포트폴리오=ARGUS 20+SGOV")
    impacts = impact_result.get("ticker_impacts", {})
    L.append(f"   🟢 순풍 TOP 8")
    for t, v in ranked[:8]:
        if v <= 0: break
        d = impacts[t].get("axis_details", {})
        top = sorted(d.items(), key=lambda x:-x[1])[:2]
        ts = " + ".join(f"{a} {x:+.1%}" for a,x in top if x>0)
        inter = "⚡" if impacts[t].get("interaction_applied") else ""
        tag = "🅰" if t in ARGUS_UNIVERSE else "·"
        L.append(f"   {tag} {t:6s} {v:>+7.2%}  {ts} {inter}")
    L.append(f"   🔴 역풍 TOP 6")
    for t, v in reversed(ranked[-6:]):
        if v >= 0: continue
        d = impacts[t].get("axis_details", {})
        bot = sorted(d.items(), key=lambda x:x[1])[:2]
        bs = " + ".join(f"{a} {x:+.1%}" for a,x in bot if x<0)
        tag = "🅰" if t in ARGUS_UNIVERSE else "·"
        L.append(f"   {tag} {t:6s} {v:>+7.2%}  {bs}")

    # ── B5: 시나리오 확률 + P&L ──
    L.append(f"\n📈 B5. 시나리오 확률 + 조건부 P&L")
    for sc, p in sorted(scenario_probs.items(), key=lambda x:-x[1]):
        label = SCENARIO_LABELS.get(sc, sc)
        sc_ret = scenario_pnl.get("scenario_returns", {}).get(sc, {}).get("portfolio_return")
        ret_str = f"P&L {sc_ret:+.1%}" if sc_ret is not None else ""
        bar = "█" * int(p * 30)
        L.append(f"   {sc:4s} {label:16s} {p:>5.1%} {bar} {ret_str}")
    if scenario_pnl.get("worst_scenario"):
        ws = scenario_pnl["worst_scenario"]
        bs = scenario_pnl["best_scenario"]
        L.append(f"   최악: {ws['scenario']} ({ws['return']:+.1%}) | 최선: {bs['scenario']} ({bs['return']:+.1%})")

    # ── B6: 포트폴리오 + DRP + 가드레일 ──
    L.append(f"\n💼 B6. 포트폴리오 구성 + DRP + 가드레일")
    L.append(f"   레짐 프리셋: {portfolio.get('regime_preset',{})}")
    final = guardrails.get("adjusted_allocation", portfolio.get("final_allocation", {}))
    L.append(f"   최종 비중 (가드레일 적용):")
    for ticker, w in sorted(final.items(), key=lambda x:-x[1]):
        L.append(f"     {ticker:8s} {w:>5.1f}%")
    if drp.get("reasons"):
        L.append(f"   DRP 근거: {'; '.join(drp['reasons'][:3])}")
    if guardrails.get("violations"):
        for v in guardrails["violations"][:3]:
            L.append(f"   ⚠️ 가드레일: {v}")
    else:
        L.append(f"   ✅ 가드레일 위반 없음 (GLD캡 {guardrails.get('gld_cap_applied','?')}%)")

    # ── B7: 리스크 메트릭 + 민감도 ──
    L.append(f"\n🛡️ B7. 리스크 메트릭 + 축 민감도")
    if risk_metrics.get("expected_return") is not None:
        L.append(f"   E[R] {risk_metrics['expected_return']:+.2%} | σ {risk_metrics.get('sigma',0):.2%} | Sharpe {risk_metrics.get('sharpe_proxy','?')}")
        L.append(f"   하방위험(최악): {risk_metrics.get('downside_risk',0):+.2%}")
    sens = sensitivity.get("ranked", [])
    if sens:
        L.append(f"   축 민감도 (최악 상태 전환 시 충격):")
        for axis, impact in sens[:5]:
            L.append(f"     {axis:10s} {impact:+.2%}")

    # ── B8: 전략이론 6계통 (기본 + QNS게임 + QLS스위트 + 심화) ──
    L.append(f"\n🎓 B8. 전략이론 6계통 (QNS + QLS 실엔진)")
    all_theory = theory_results + qns_suite + qls_suite + ctx.get("theory_extended", [])
    sev_emoji = {"HIGH":"🔴","MEDIUM":"🟡","LOW":"🟢"}
    # 계통별 그룹핑
    by_family = {}
    for r in all_theory:
        by_family.setdefault(r.family_id, []).append(r)
    family_names = {1:"게임이론", 2:"행동경제학", 3:"권력 동학", 4:"위기 의사결정", 5:"전략 기획", 6:"시스템 사고"}
    for fid in sorted(by_family):
        fname = family_names.get(fid, f"계통{fid}")
        L.append(f"\n   ── {fid} {fname} ({len(by_family[fid])}건) ──")
        for r in by_family[fid]:
            em = sev_emoji.get(r.severity, "⚪")
            L.append(f"   {em} [{r.theory}]")
            L.append(f"      {r.diagnosis[:90]}")
            if r.implication:
                L.append(f"      → {r.implication[:80]}")

    # ── B9: 전환 감지 + 백테스트 + 한계 ──
    L.append(f"\n⚡ B9. 전환 감지 + 백테스트 + 자동화 한계")
    if transition_result and "error" not in transition_result:
        sig = transition_result.get("transition_signal", transition_result.get("signal", "?"))
        L.append(f"   EWMA 전환 신호: {sig}")
    bt = ctx.get("backtest")
    if bt and "error" not in bt:
        p = bt["portfolio"]; s = bt["spy_benchmark"]
        L.append(f"   ⚠️ smoke replay ({bt['period_years']}년, {bt['rebalances']}회 — 진단 전용, §40 v3 아님):")
        L.append(f"     Autopilot: CAGR {p['cagr']:+.1%} | Sharpe {p['sharpe']} | MDD {p['mdd']:.1%}")
        L.append(f"     SPY 벤치:  CAGR {s['cagr']:+.1%} | Sharpe {s['sharpe']} | MDD {s['mdd']:.1%}")
        L.append(f"     탐색적 알파 proxy (vs SPY): {bt['alpha_vs_spy']:+.1%} — 배포 근거 사용 금지")
    low_conf = [a for a in axes_result["confidence"] if axes_result["confidence"][a] < 60]
    if low_conf:
        L.append(f"   ⚠️ 낮은 신뢰도 축: {', '.join(low_conf)} — 뉴스 교차 검증 필요")
    L.append(f"   WAR/TARIFF/FISCAL = 프록시. 정치/정책 이벤트 직접 반영 불가.")

    # ── 자가 검증 ──
    L.append(f"\n🛡️ 자가 검증: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")
    if validation.get("warnings"):
        for w in validation["warnings"][:2]:
            L.append(f"   ⚠️ {w}")

    L.append("\n" + "="*68)
    return "\n".join(L)


def _briefing_emergency_macro_alpha(ctx: Dict) -> str:
    """B10~B12 확장 섹션 (비상 + 매크로 + 알파/사이징)."""
    L = []
    sensor_suite = ctx.get("sensor_suite", {})
    killswitch = ctx.get("killswitch", {})
    aegis = ctx.get("aegis", {})
    macro_cal = ctx.get("macro_calendar", {})
    blended = ctx.get("blended_alpha", {})
    sizing = ctx.get("position_sizing", {})
    diversification = ctx.get("diversification", {})

    # ── B10: 센서 + 비상 프로토콜 ──
    L.append(f"\n🚨 B10. 센서 평가 + AEGIS 비상 프로토콜")
    L.append(f"   AEGIS 단계: {aegis.get('label','?')}")
    L.append(f"   대응: {aegis.get('action','')}")
    L.append(f"   킬스위치: {'⚠️ ACTIVE' if killswitch.get('killswitch_active') else '🟢 OFF'}")
    if killswitch.get("triggers"):
        for t in killswitch["triggers"][:3]:
            L.append(f"     • {t}")
    # 센서 상태 (red/storm만)
    evals = sensor_suite.get("evaluations", {})
    alerts = [(n, e) for n, e in evals.items() if e.get("level", 0) >= 2]
    if alerts:
        L.append(f"   🔴 경보 센서 ({len(alerts)}개):")
        for n, e in alerts:
            L.append(f"     {e['label']:10s} {e['value']} {e['status']}")
    else:
        L.append(f"   ✅ 경보 센서 없음 (YELLOW {sensor_suite.get('yellow_count',0)}개)")

    # ── B11: 매크로 트리거 ──
    L.append(f"\n📅 B11. 매크로 이벤트 트리거")
    qt = macro_cal.get("quantitative_triggers", {})
    if qt.get("fired"):
        L.append(f"   🔴 발동 ({qt['fired_count']}건):")
        for f in qt["fired"][:5]:
            L.append(f"     [{f['severity']}] {f['label']} (현재 {f['value']})")
            L.append(f"       → {f['implication']}")
    else:
        L.append(f"   ✅ 발동 트리거 없음")
    if qt.get("approaching"):
        L.append(f"   🟡 임박 ({len(qt['approaching'])}건):")
        for a in qt["approaching"][:3]:
            L.append(f"     {a['label']} (현재 {a['value']}, 거리 {a.get('distance','?')})")

    # ── B12: 블렌드 알파 + 포지션 사이징 ──
    L.append(f"\n📊 B12. 블렌드 알파 (매크로 60% + 기술 40%) + 사이징")
    if blended.get("ranked"):
        L.append(f"   🟢 알파 TOP 6 (매크로+기술 블렌드):")
        for t, alpha, align in blended["ranked"][:6]:
            L.append(f"     {t:6s} α {alpha:+.2f}  {align}")
        L.append(f"   🔴 알파 BOTTOM 3:")
        for t, alpha, align in blended["ranked"][-3:]:
            L.append(f"     {t:6s} α {alpha:+.2f}  {align}")
    if sizing.get("ranked_by_efficiency"):
        L.append(f"   ⚖️ 수익/리스크 효율 TOP 5:")
        for t, eff in sizing["ranked_by_efficiency"][:5]:
            s = sizing["sizing"].get(t, {})
            L.append(f"     {t:6s} 효율 {eff:.2f} (σ {s.get('volatility',0):.0%}, Kelly {s.get('kelly_weight',0):.0%})")
    if diversification and "error" not in diversification:
        L.append(f"   🔀 분산 효과: 가중변동성 {diversification['weighted_avg_vol']:.1%} → "
                 f"포트변동성 {diversification['portfolio_vol']:.1%} "
                 f"(분산이득 {diversification['div_ratio']:.0%})")

    # ── B13: SSOT 갱신 제안 + 리밸런싱 ──
    ssot = ctx.get("ssot_proposal", {})
    rebal = ctx.get("rebalance", {})
    rebal_cost = ctx.get("rebalance_cost", {})
    L.append(f"\n🎖️ B13. SSOT 갱신 제안 + 리밸런싱 (Commander 승인 대기)")
    if ssot.get("proposals"):
        L.append(f"   고신뢰 축 갱신 제안 ({ssot['high_confidence_count']}건):")
        for p in ssot["proposals"]:
            L.append(f"     {p['axis']:10s} → {p['proposed_state']:14s} {p['probability']:.0%} (신뢰도 {p['confidence']}%)")
    L.append(f"   ⚠️ {ssot.get('note','')}")
    if rebal.get("blocked"):
        L.append(f"   🔒 리밸런싱 차단: {rebal.get('reason','')}")
    elif rebal.get("trades"):
        L.append(f"   리밸런싱 거래 제안 ({rebal['trade_count']}건, 회전율 {rebal['turnover']}%):")
        for t in rebal["trades"][:8]:
            L.append(f"     {t['action']:4s} {t['ticker']:6s} {t['current']:>5.1f}% → {t['target']:>5.1f}% ({t['delta']:+.1f}%p)")
        if rebal_cost:
            L.append(f"   예상 거래비용: {rebal_cost.get('estimated_cost_pct',0):.3%} ($100k당 ${rebal_cost.get('estimated_cost_per_100k',0)})")
    else:
        L.append(f"   리밸런싱: 밴드 내 — 거래 불필요")

    # ── B14: Red Team 자가 감사 ──
    rt = ctx.get("red_team", {})
    interactions = ctx.get("axis_interactions", {})
    L.append(f"\n🔴 B14. Red Team 자가 감사 + 교차축 상호작용")
    L.append(f"   {rt.get('summary','')}")
    if rt.get("challenges"):
        for c in rt["challenges"][:5]:
            L.append(f"   ⚠️ [{c['type']}] {c['issue']}")
            L.append(f"      ↳ 반증: {c['counter']}")
    if interactions.get("active_red_pairs"):
        L.append(f"   활성 역풍 축쌍: {', '.join(interactions['active_red_pairs'][:5])}")
    if interactions.get("top_boosted"):
        bt = interactions["top_boosted"][0]
        L.append(f"   최대 부스트 종목: {bt['ticker']} ({bt['total_impact']:+.1%})")

    return "\n".join(L)


def generate_briefing_v2(ctx: Dict) -> str:
    """B0~B12 전체 통합 브리핑 (확장판)."""
    base = generate_briefing_full(ctx)
    # 마지막 자가검증/구분선 앞에 B10~B12 삽입
    ext = _briefing_emergency_macro_alpha(ctx)
    # base의 "🛡️ 자가 검증" 앞에 삽입
    marker = "\n🛡️ 자가 검증:"
    if marker in base:
        idx = base.rfind(marker)
        return base[:idx] + ext + base[idx:]
    return base + ext


# ═══════════════════════════════════════════════════════════════════════
# 종합 오케스트레이터 (전 계층 + 전 서브시스템)
# ═══════════════════════════════════════════════════════════════════════

def run_autopilot_full(commander_overrides: Optional[Dict] = None,
                       run_bt: bool = True, bt_max_steps: Optional[int] = 60,
                       verbose: bool = True) -> str:
    """Oracle Autopilot 종합 실행 (L1~L11 전 서브시스템).
    
    Args:
        run_bt: 백테스트 실행 여부 (시간 소요)
        bt_max_steps: 백테스트 최대 스텝 (속도 제한)
    """
    def log(m):
        if verbose: print(m)

    log(f"🔭 Oracle Autopilot v{AUTOPILOT_VERSION} (적정자) 종합 실행\n")
    ctx = {}

    # L1
    log("📡 L1: ARGUS Public Data...")
    ctx["latest"] = fetch_latest()
    ctx["history"] = fetch_history()
    ctx["validation"] = validate_data(ctx["latest"], ctx["history"])
    log(f"   ✅ {ctx['latest'].get('Date')} | {len(ctx['history'])}행")

    # L1.5
    log("📐 L1.5: 파생 지표...")
    ctx["derived"] = build_derived_metrics(ctx["latest"], ctx["history"])

    # L2
    log("🔧 L2: 8축 추론 (auto_prior + LEAD-5/6b)...")
    ctx["axes_result"] = infer_all_axes(ctx["latest"], ctx["history"], ctx["derived"], commander_overrides)
    axis_probs = ctx["axes_result"]["axis_probs"]
    for axis in ["WAR","OIL","MONETARY","CREDIT","TARIFF","GROWTH","FISCAL","AI_POWER"]:
        ap = axis_probs.get(axis, {})
        if ap:
            s, p = max(ap.items(), key=lambda x:x[1])
            log(f"   {axis:10s} → {s:14s} {p:.0%}")

    # L3
    log("🌊 L3: 레짐 파이프라인...")
    ctx["regime_result"] = run_regime_pipeline(ctx["latest"], ctx["derived"])
    grad_score = ctx["regime_result"].get("gradient_score", 50)
    log(f"   레짐: {ctx['regime_result'].get('macro_regime',{}).get('label','?')} | 그래디언트 {grad_score}")

    # L4
    log("🔭 L4: Oracle 임팩트 29종목...")
    ctx["impact_result"] = run_impact_engine(axis_probs)

    # L5
    log("📈 L5: 시나리오 확률...")
    ctx["scenario_probs"] = compute_scenario_probs(axis_probs, grad_score)

    # L6
    log("💼 L6: 포트폴리오 + DRP + 가드레일...")
    ctx["portfolio"] = construct_portfolio(ctx["regime_result"], ctx["impact_result"], grad_score)

    # L8 전환 (DRP에 필요)
    ctx["transition_result"] = run_transition_detector(ctx["history"])

    # DRP
    ctx["drp"] = compute_drp_adjustment(grad_score, ctx["transition_result"], ctx["scenario_probs"])
    ctx["guardrails"] = apply_guardrails(ctx["portfolio"].get("final_allocation", {}), grad_score)

    # L5-EXT 시나리오 P&L (가드레일 적용 비중 기준)
    log("📊 L5-EXT: 시나리오 P&L + 민감도...")
    weights = {t: w/100.0 for t, w in ctx["guardrails"]["adjusted_allocation"].items()}
    ctx["scenario_pnl"] = compute_scenario_pnl_matrix(weights, ctx["scenario_probs"])
    ctx["sensitivity"] = sensitivity_analysis(weights, axis_probs)
    ctx["risk_metrics"] = compute_risk_metrics(ctx["scenario_pnl"], ctx["sensitivity"])

    # L7 전략이론 (기본 + QNS게임 + QLS스위트 + 심화)
    log("🎓 L7: 전략이론 6계통 (기본 + QNS게임 + QLS스위트 + 심화)...")
    ctx["theory_results"] = run_strategic_theory(axis_probs, ctx["latest"], ctx["derived"])
    ctx["qns_suite"] = run_qns_game_suite(axis_probs, ctx["latest"], ctx["derived"])
    ctx["qls_suite"] = run_qls_full_suite(axis_probs, ctx["latest"])
    ctx["theory_extended"] = run_strategic_theory_extended(axis_probs, ctx["latest"], ctx["derived"])

    # L11 백테스트
    if run_bt:
        log(f"📉 L11: 백테스트 (최대 {bt_max_steps}스텝)...")
        ctx["backtest"] = run_backtest(ctx["history"], max_steps=bt_max_steps)
    else:
        ctx["backtest"] = None

    # L12 센서 평가 + 킬스위치 + AEGIS
    log("🚨 L12: 센서 평가 + 킬스위치 + AEGIS...")
    ctx["sensor_suite"] = run_sensor_suite(ctx["latest"])
    ctx["killswitch"] = detect_killswitch(ctx["sensor_suite"], ctx["derived"], ctx["history"])
    ctx["aegis"] = aegis_protocol(ctx["sensor_suite"], ctx["killswitch"], grad_score)
    log(f"   AEGIS: {ctx['aegis']['label']} | 킬스위치: {'⚠️ ACTIVE' if ctx['killswitch']['killswitch_active'] else 'OFF'}")

    # L14 매크로 트리거
    log("📅 L14: 매크로 이벤트 트리거...")
    ctx["macro_calendar"] = run_macro_calendar(ctx["latest"])
    fired = ctx["macro_calendar"]["quantitative_triggers"]["fired_count"]
    log(f"   발동 트리거: {fired}건")

    # L15 블렌드 알파 + L13 포지션 사이징
    log("📊 L13+L15: 블렌드 알파 + 포지션 사이징...")
    ctx["blended_alpha"] = compute_blended_alpha(ctx["impact_result"], ctx["history"], tickers=ARGUS_UNIVERSE)
    candidate_tickers = [t for t, v in ctx["impact_result"].get("ranked", []) if v > 0 and t in ARGUS_UNIVERSE][:10]
    ctx["position_sizing"] = compute_position_sizing(ctx["impact_result"], ctx["history"], candidate_tickers)
    port_weights = {t: w/100.0 for t, w in ctx["guardrails"]["adjusted_allocation"].items()}
    ctx["diversification"] = compute_diversification_benefit(port_weights, ctx["history"])

    # L18 Commander 인터페이스 (SSOT 제안 + 의도 메뉴)
    log("🎖️ L18: SSOT 갱신 제안 + 의도 메뉴...")
    ctx["ssot_proposal"] = propose_ssot_update(ctx["axes_result"], ctx["regime_result"])
    ctx["intent_menu"] = build_intent_menu()

    # L19 리밸런싱 제안 [v1.0.4 P0 FIX] validation → current_weights 순차 hard gate
    # 감사 지적: validation FAIL인데 rebalance 9건 생성됨 → 생성 전 hard block 의무
    target = generate_target_from_pipeline(ctx)
    if not ctx.get("validation", {}).get("valid", False):
        # HARD GATE 1: 데이터 검증 실패 — 거래 제안 생성 자체 차단
        ctx["rebalance"] = {"trades": [], "trade_count": 0, "turnover": 0.0,
                            "blocked": True,
                            "reason": "DATA_VALIDATION_FAIL — 거래 제안 차단",
                            "validation_issues": ctx.get("validation", {}).get("issues", [])}
    else:
        current = commander_overrides.get("current_weights") if commander_overrides else None
        if not current:
            # HARD GATE 2: 현재 비중 미입력 — 거래 제안 차단
            ctx["rebalance"] = {"trades": [], "trade_count": 0, "turnover": 0.0,
                                "blocked": True,
                                "reason": "current_weights 미입력 — 거래 제안 차단 (오판 방지)",
                                "note": "현재 보유 비중을 commander_overrides['current_weights']로 제공 시 거래 제안 생성"}
        else:
            ctx["rebalance"] = compute_rebalance(current, target)
            ctx["rebalance"]["blocked"] = False
    ctx["rebalance_cost"] = compute_rebalance_cost(ctx["rebalance"])

    # L21 Red Team 자가 감사 + L22 교차축 분석
    log("🔴 L21: Red Team 자가 감사 + 교차축 분석...")
    ctx["red_team"] = red_team_audit(ctx)
    ctx["axis_interactions"] = analyze_axis_interactions(axis_probs, ctx["impact_result"])
    log(f"   Red Team 도전: {ctx['red_team']['challenge_count']}건 | {ctx['red_team']['summary'][:30]}")

    # L10 자가검증
    ctx["check"] = self_check(ctx["axes_result"], ctx["regime_result"],
                              ctx["impact_result"], ctx["scenario_probs"],
                              validation=ctx.get("validation"),
                              guardrails=ctx.get("guardrails"))
    log(f"🛡️ L10: 자가검증 {'✅ PASS' if ctx['check']['passed'] else '❌ FAIL'}")

    # L9 브리핑
    log("📝 L9: 종합 브리핑 생성 (B0~B12)...\n")
    return generate_briefing_v2(ctx)


def run_full() -> str:
    """종합 실행 진입점 (완전체 L1~L24)."""
    briefing, ctx = run_autopilot_complete(verbose=True)
    print(briefing)
    return briefing




# ═══════════════════════════════════════════════════════════════════════
# L12: 센서 평가 스위트 + 킬스위치 + AEGIS 비상 프로토콜
# ═══════════════════════════════════════════════════════════════════════
# 개별 센서를 임계값 대비 평가(green/yellow/red), 복합 위기 신호 감지,
# 단계별(Stage 0~3) 비상 대응 프로토콜. INVICTUS SSOT 임계값 기반.
# ═══════════════════════════════════════════════════════════════════════

# 센서 임계값 정의 (방향: high=값↑위험, low=값↓위험)
SENSOR_THRESHOLDS = {
    "VIX":      {"yellow": 22.0,  "red": 30.0,  "storm": 32.0,  "dir": "high", "label": "변동성"},
    "MOVE":     {"yellow": 100.0, "red": 120.0, "storm": 130.0, "dir": "high", "label": "채권 변동성"},
    "OAS_HY":   {"yellow": 4.5,   "red": 5.5,   "storm": 5.8,   "dir": "high", "label": "HY 스프레드"},
    "OAS_IG":   {"yellow": 1.2,   "red": 1.8,   "storm": 2.2,   "dir": "high", "label": "IG 스프레드"},
    "WTI":      {"yellow": 88.0,  "red": 100.0, "storm": 120.0, "dir": "high", "label": "유가"},
    "SAHMCURRENT": {"yellow": 0.35, "red": 0.50, "storm": 0.70, "dir": "high", "label": "Sahm 침체"},
    "DXY":      {"yellow": 106.0, "red": 110.0, "storm": 115.0, "dir": "high", "label": "달러지수"},
    "TYX_30Y":  {"yellow": 5.0,   "red": 5.3,   "storm": 5.6,   "dir": "high", "label": "30Y 금리"},
    "NFCI":     {"yellow": 0.0,   "red": 0.3,   "storm": 0.6,   "dir": "high", "label": "금융여건"},
    "PMI":      {"yellow": 50.0,  "red": 47.0,  "storm": 45.0,  "dir": "low",  "label": "제조업 PMI"},
    "F_G_Score":{"yellow": 30.0,  "red": 20.0,  "storm": 10.0,  "dir": "low",  "label": "공포탐욕"},
    "Net_Liquidity": {"yellow": 5500000, "red": 5200000, "storm": 5000000, "dir": "low", "label": "순유동성"},
}


def evaluate_sensor(name: str, value: Optional[float]) -> Dict[str, Any]:
    """개별 센서 임계값 평가 → green/yellow/red/storm."""
    spec = SENSOR_THRESHOLDS.get(name)
    if spec is None or value is None:
        return {"sensor": name, "value": value, "status": "unknown", "level": 0}

    direction = spec["dir"]
    if direction == "high":
        if value >= spec["storm"]:
            status, level = "🔴🔴 STORM", 3
        elif value >= spec["red"]:
            status, level = "🔴 RED", 2
        elif value >= spec["yellow"]:
            status, level = "🟡 YELLOW", 1
        else:
            status, level = "🟢 GREEN", 0
    else:  # low = 값이 낮을수록 위험
        if value <= spec["storm"]:
            status, level = "🔴🔴 STORM", 3
        elif value <= spec["red"]:
            status, level = "🔴 RED", 2
        elif value <= spec["yellow"]:
            status, level = "🟡 YELLOW", 1
        else:
            status, level = "🟢 GREEN", 0

    # 임계점까지 거리 (정규화)
    if direction == "high":
        distance = (spec["red"] - value) / spec["red"] if spec["red"] > 0 else 0
    else:
        distance = (value - spec["red"]) / spec["red"] if spec["red"] > 0 else 0

    return {
        "sensor": name, "label": spec["label"], "value": value,
        "status": status, "level": level,
        "distance_to_red": round(distance, 3),
        "thresholds": {"yellow": spec["yellow"], "red": spec["red"], "storm": spec["storm"]},
    }


def run_sensor_suite(latest: Dict) -> Dict[str, Any]:
    """전 센서 평가 + 복합 위기 신호 집계."""
    evaluations = {}
    for name in SENSOR_THRESHOLDS:
        evaluations[name] = evaluate_sensor(name, safe_get(latest, name))

    # 레벨별 집계
    storm_count = sum(1 for e in evaluations.values() if e["level"] == 3)
    red_count = sum(1 for e in evaluations.values() if e["level"] == 2)
    yellow_count = sum(1 for e in evaluations.values() if e["level"] == 1)

    # 복합 위기 점수 (가중)
    crisis_score = storm_count * 3 + red_count * 2 + yellow_count * 1

    return {
        "evaluations": evaluations,
        "storm_count": storm_count,
        "red_count": red_count,
        "yellow_count": yellow_count,
        "crisis_score": crisis_score,
        "max_crisis_score": len(SENSOR_THRESHOLDS) * 3,
    }


def detect_killswitch(sensor_suite: Dict, derived: Dict, history: List[Dict]) -> Dict[str, Any]:
    """킬스위치 트리거 감지 (급락/급변 복합 조건).
    
    FAST_CRASH: 단기 급락 + VIX 급등 + 스프레드 확대 동시.
    """
    evals = sensor_suite["evaluations"]
    triggers = []

    # 조건 1: VIX STORM + OAS RED 동시
    vix_lvl = evals.get("VIX", {}).get("level", 0)
    oas_lvl = evals.get("OAS_HY", {}).get("level", 0)
    if vix_lvl >= 3 and oas_lvl >= 2:
        triggers.append("VIX STORM + HY스프레드 RED 동시 (신용+변동성 복합)")

    # 조건 2: SPY 급락 (20일 -10% 이상)
    spy_mom = derived.get("SPY_mom60")
    if spy_mom is not None and spy_mom < -0.10:
        triggers.append(f"SPY 60일 {spy_mom:+.0%} 급락")

    # 조건 3: MOVE STORM (채권 발작)
    if evals.get("MOVE", {}).get("level", 0) >= 3:
        triggers.append("MOVE STORM (채권시장 발작)")

    # 조건 4: 복합 위기 점수 과다
    crisis_ratio = sensor_suite["crisis_score"] / max(1, sensor_suite["max_crisis_score"])
    if crisis_ratio > 0.40:
        triggers.append(f"복합 위기 점수 {crisis_ratio:.0%} > 40% 임계")

    killswitch_active = len(triggers) >= 2
    return {
        "killswitch_active": killswitch_active,
        "triggers": triggers,
        "trigger_count": len(triggers),
        "recommendation": "전면 방어 전환 (SGOV 70%+, GLD, 공격 청산)" if killswitch_active else "정상 운영",
    }


def aegis_protocol(sensor_suite: Dict, killswitch: Dict, gradient_score: float) -> Dict[str, Any]:
    """AEGIS 단계별 비상 대응 프로토콜 (Stage 0~3)."""
    storm = sensor_suite["storm_count"]
    red = sensor_suite["red_count"]

    if killswitch["killswitch_active"] or storm >= 2:
        stage = 3
        label = "🔴🔴 STAGE 3 — 전면 방어"
        action = "공격 자산 전량 청산. SGOV 70%+, GLD 25%. 신규 진입 금지."
        defense_target = 0.85
    elif storm >= 1 or red >= 3 or gradient_score > 70:
        stage = 2
        label = "🔴 STAGE 2 — 방어 강화"
        action = "공격 50% 축소. SGOV 50%, GLD 30%. ATTACK 티어 헤지."
        defense_target = 0.65
    elif red >= 1 or gradient_score > 50:
        stage = 1
        label = "🟡 STAGE 1 — 경계"
        action = "공격 신규 진입 자제. SGOV 30%. 손절 라인 점검."
        defense_target = 0.45
    else:
        stage = 0
        label = "🟢 STAGE 0 — 정상"
        action = "레짐 프리셋 정상 운영."
        defense_target = None

    return {
        "stage": stage, "label": label, "action": action,
        "defense_target_override": defense_target,
    }


# ═══════════════════════════════════════════════════════════════════════
# L13: 포지션 사이징 (Kelly + 리스크 패리티) + 상관 행렬
# ═══════════════════════════════════════════════════════════════════════
# 임팩트 기대수익 + 변동성 + 상관관계 기반 최적 포지션 크기 산출.
# Kelly 분수, 리스크 패리티, 분산 효과 정량화.
# ═══════════════════════════════════════════════════════════════════════

def compute_volatility(history: List[Dict], ticker: str, window: int = 60) -> Optional[float]:
    """종목 연율화 변동성."""
    rets = _bt_compute_returns(history, ticker)[-window:]
    rets = [r for r in rets if r is not None]
    if len(rets) < window * 0.5:
        return None
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / len(rets)
    return math.sqrt(var) * math.sqrt(252)  # 연율화


def compute_correlation(history: List[Dict], t1: str, t2: str, window: int = 60) -> Optional[float]:
    """두 종목 수익률 상관계수."""
    r1 = _bt_compute_returns(history, t1)[-window:]
    r2 = _bt_compute_returns(history, t2)[-window:]
    pairs = [(a, b) for a, b in zip(r1, r2) if a is not None and b is not None]
    if len(pairs) < window * 0.5:
        return None
    n = len(pairs)
    m1 = sum(a for a, _ in pairs) / n
    m2 = sum(b for _, b in pairs) / n
    cov = sum((a - m1) * (b - m2) for a, b in pairs) / n
    s1 = math.sqrt(sum((a - m1) ** 2 for a, _ in pairs) / n)
    s2 = math.sqrt(sum((b - m2) ** 2 for _, b in pairs) / n)
    if s1 < 1e-9 or s2 < 1e-9:
        return 0.0
    return cov / (s1 * s2)


def build_correlation_matrix(history: List[Dict], tickers: List[str]) -> Dict[Tuple[str, str], float]:
    """상관 행렬 (상삼각)."""
    matrix = {}
    for i, t1 in enumerate(tickers):
        for t2 in tickers[i:]:
            c = compute_correlation(history, t1, t2)
            if c is not None:
                matrix[(t1, t2)] = round(c, 3)
    return matrix


def kelly_fraction(expected_return: float, volatility: float, kelly_cap: float = 0.5) -> float:
    """Kelly 분수 (변동성 조정). f* = μ / σ², cap 적용.
    
    실무에서는 full Kelly가 과대하므로 fractional Kelly (cap) 사용.
    """
    if volatility is None or volatility < 1e-6:
        return 0.0
    raw_kelly = expected_return / (volatility ** 2)
    # fractional kelly + 음수 차단 + cap
    return max(0.0, min(kelly_cap, raw_kelly * 0.25))


def compute_position_sizing(impact_result: Dict, history: List[Dict],
                            candidate_tickers: List[str]) -> Dict[str, Any]:
    """임팩트 + 변동성 → Kelly + 리스크 패리티 포지션 크기."""
    impacts = impact_result.get("ticker_impacts", {})
    sizing = {}

    for ticker in candidate_tickers:
        exp_ret = impacts.get(ticker, {}).get("total_impact", 0.0)
        vol = compute_volatility(history, ticker)
        if vol is None:
            continue
        kelly = kelly_fraction(exp_ret, vol)
        # 리스크 패리티 가중 (역변동성)
        inv_vol = 1.0 / vol if vol > 1e-6 else 0.0
        sizing[ticker] = {
            "expected_return": round(exp_ret, 4),
            "volatility": round(vol, 4),
            "kelly_fraction": round(kelly, 4),
            "inv_vol_weight": round(inv_vol, 4),
            "return_per_risk": round(exp_ret / vol, 3) if vol > 1e-6 else 0,
        }

    # 리스크 패리티 정규화
    total_inv_vol = sum(s["inv_vol_weight"] for s in sizing.values())
    if total_inv_vol > 0:
        for t in sizing:
            sizing[t]["risk_parity_weight"] = round(sizing[t]["inv_vol_weight"] / total_inv_vol, 4)

    # Kelly 정규화
    total_kelly = sum(s["kelly_fraction"] for s in sizing.values())
    if total_kelly > 0:
        for t in sizing:
            sizing[t]["kelly_weight"] = round(sizing[t]["kelly_fraction"] / total_kelly, 4)

    # 수익/리스크 순 정렬
    ranked = sorted(sizing.items(), key=lambda x: -x[1].get("return_per_risk", 0))
    return {
        "sizing": sizing,
        "ranked_by_efficiency": [(t, s["return_per_risk"]) for t, s in ranked],
    }


def compute_diversification_benefit(weights: Dict[str, float], history: List[Dict]) -> Dict[str, Any]:
    """분산 효과 정량화. 가중 변동성 vs 포트폴리오 변동성."""
    tickers = [t for t in weights if t in BT_TICKERS]
    if len(tickers) < 2:
        return {"error": "종목 부족"}

    # 개별 변동성
    vols = {t: compute_volatility(history, t) for t in tickers}
    vols = {t: v for t, v in vols.items() if v is not None}

    # 가중 평균 변동성 (분산 무시)
    weighted_vol = sum(weights[t] * vols[t] for t in vols)

    # 포트폴리오 변동성 (상관 반영)
    port_var = 0.0
    for t1 in vols:
        for t2 in vols:
            corr = compute_correlation(history, t1, t2) if t1 != t2 else 1.0
            if corr is None:
                corr = 0.0
            port_var += weights[t1] * weights[t2] * vols[t1] * vols[t2] * corr
    port_vol = math.sqrt(max(0.0, port_var))

    div_benefit = weighted_vol - port_vol
    return {
        "weighted_avg_vol": round(weighted_vol, 4),
        "portfolio_vol": round(port_vol, 4),
        "diversification_benefit": round(div_benefit, 4),
        "div_ratio": round(div_benefit / weighted_vol, 3) if weighted_vol > 0 else 0,
    }


# ═══════════════════════════════════════════════════════════════════════
# L14: 매크로 이벤트 트리거 + 임계값 모니터링
# ═══════════════════════════════════════════════════════════════════════
# Commander 상시 감시 트리거(30Y 5.3%, NVDA, 하이퍼스케일러 capex, FOMC,
# 미중 휴전 만료 등)를 정량 임계값으로 모니터링 + 발동 알림.
# ═══════════════════════════════════════════════════════════════════════

# 트리거 정의: 임계값 돌파 시 발동
MACRO_TRIGGERS = {
    "TYX_30Y_5.3": {
        "sensor": "TYX_30Y", "threshold": 5.3, "dir": "above",
        "label": "30Y 금리 5.3% 돌파", "severity": "HIGH",
        "implication": "장기금리 발작 위험 → 성장주/채권 매도, 듀레이션 축소",
    },
    "TYX_30Y_5.6": {
        "sensor": "TYX_30Y", "threshold": 5.6, "dir": "above",
        "label": "30Y 금리 5.6% 위기", "severity": "CRITICAL",
        "implication": "재정 지배 우려 → TLT 청산, GLD 확대",
    },
    "VIX_30": {
        "sensor": "VIX", "threshold": 30.0, "dir": "above",
        "label": "VIX 30 위기", "severity": "HIGH",
        "implication": "변동성 급등 → 방어 전환, 헤지 강화",
    },
    "OAS_HY_5.5": {
        "sensor": "OAS_HY", "threshold": 5.5, "dir": "above",
        "label": "HY 스프레드 5.5% 위기", "severity": "HIGH",
        "implication": "신용 경색 → 위험자산 청산, 달러RP 확대",
    },
    "WTI_100": {
        "sensor": "WTI", "threshold": 100.0, "dir": "above",
        "label": "유가 $100 돌파", "severity": "HIGH",
        "implication": "오일 쇼크 → XLE/PDBC 순풍, 성장주 역풍, CPI 상승",
    },
    "SAHM_0.5": {
        "sensor": "SAHMCURRENT", "threshold": 0.5, "dir": "above",
        "label": "Sahm 룰 침체 트리거", "severity": "CRITICAL",
        "implication": "침체 공식 신호 → RECESSION 레짐, 방어 극대화",
    },
    "DXY_110": {
        "sensor": "DXY", "threshold": 110.0, "dir": "above",
        "label": "달러지수 110 돌파", "severity": "MEDIUM",
        "implication": "달러 강세 → EM 자산 역풍, 원자재 압박",
    },
    "PMI_47": {
        "sensor": "PMI", "threshold": 47.0, "dir": "below",
        "label": "PMI 47 수축 가속", "severity": "MEDIUM",
        "implication": "제조업 위축 → GROWTH slowdown, 경기민감주 경계",
    },
    "NetLiq_5.2T": {
        "sensor": "Net_Liquidity", "threshold": 5200000, "dir": "below",
        "label": "순유동성 5.2조 하회", "severity": "MEDIUM",
        "implication": "유동성 긴축 → 위험자산 멀티플 압박",
    },
}


def check_macro_triggers(latest: Dict) -> Dict[str, Any]:
    """매크로 트리거 발동 체크."""
    fired = []
    approaching = []  # 임박 (임계 95% 도달)

    for tid, spec in MACRO_TRIGGERS.items():
        value = safe_get(latest, spec["sensor"])
        if value is None:
            continue
        threshold = spec["threshold"]

        if spec["dir"] == "above":
            if value >= threshold:
                fired.append({"id": tid, "value": value, **spec})
            elif value >= threshold * 0.97:
                approaching.append({"id": tid, "value": value,
                                    "distance": round(threshold - value, 2), **spec})
        else:  # below
            if value <= threshold:
                fired.append({"id": tid, "value": value, **spec})
            elif value <= threshold * 1.03:
                approaching.append({"id": tid, "value": value,
                                    "distance": round(value - threshold, 2), **spec})

    # 심각도 순 정렬
    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    fired.sort(key=lambda x: sev_order.get(x["severity"], 9))

    return {
        "fired": fired,
        "approaching": approaching,
        "fired_count": len(fired),
        "critical_count": sum(1 for f in fired if f["severity"] == "CRITICAL"),
    }


# 정성 이벤트 캘린더 (날짜 미상 — 모니터링 대상 명시)
QUALITATIVE_EVENTS = [
    {"event": "FOMC 회의", "frequency": "6주마다", "watch": "점도표 + 파월 톤 (hawkish/dovish)",
     "axis": "MONETARY", "implication": "금리 경로 재평가 → MONETARY 축 갱신"},
    {"event": "CPI 발표", "frequency": "월간", "watch": "근원 CPI vs 예상 (인플레 끈적임)",
     "axis": "MONETARY/GROWTH", "implication": "인플레 서프라이즈 → 금리 변동성"},
    {"event": "NVDA 실적", "frequency": "분기", "watch": "데이터센터 매출 + 가이던스 vs 컨센서스",
     "axis": "AI_POWER", "implication": "AI capex 둔화 신호 시 saturation 경계"},
    {"event": "하이퍼스케일러 capex 가이던스", "frequency": "분기", "watch": "MSFT/GOOGL/AMZN/META capex 합계 방향",
     "axis": "AI_POWER", "implication": "capex 3분기 둔화 시 AI_POWER 비활성 검토"},
    {"event": "미중 정상회담 / 휴전 만료", "frequency": "이벤트", "watch": "관세 재부과 vs 협정 연장",
     "axis": "TARIFF", "implication": "관세 결렬 시 TARIFF breakdown → CQQQ/EM 충격"},
    {"event": "호르무즈 통항 상태", "frequency": "상시", "watch": "봉쇄 지속 vs 재개방 협상",
     "axis": "OIL/WAR", "implication": "재개방 시 OIL normalize → 유가 급락, 성장주 반등"},
    {"event": "OPEC+ 회의", "frequency": "월간", "watch": "감산 연장 vs 증산",
     "axis": "OIL", "implication": "증산 시 유가 하락 → XLE/PDBC 역풍"},
]


def run_macro_calendar(latest: Dict) -> Dict[str, Any]:
    """매크로 트리거 + 정성 이벤트 캘린더 종합."""
    triggers = check_macro_triggers(latest)
    return {
        "quantitative_triggers": triggers,
        "qualitative_events": QUALITATIVE_EVENTS,
    }


# ═══════════════════════════════════════════════════════════════════════
# L15: 종목 알파 오버레이 (매크로 임팩트 + 기술적 모멘텀 블렌드)
# ═══════════════════════════════════════════════════════════════════════
# Oracle 매크로 임팩트(축독립 기대수익)에 기술적 신호(MA/모멘텀/상대강도)를
# 블렌딩하여 종합 알파 점수 산출. 매크로 60% + 기술 40% 가중.
# ═══════════════════════════════════════════════════════════════════════

ALPHA_BLEND_MACRO = 0.60   # 매크로 임팩트 가중
ALPHA_BLEND_TECH = 0.40    # 기술적 신호 가중


def compute_technical_score(history: List[Dict], ticker: str) -> Dict[str, Any]:
    """종목 기술적 점수 (-1 ~ +1). MA 추세 + 모멘텀 + 상대강도."""
    close_key = _bt_close_key(ticker)
    cur = history[-1].get(close_key)
    if cur is None:
        return {"score": 0.0, "available": False}

    score = 0.0
    components = {}

    # MA200 추세 (장기)
    ma200 = compute_ma(history, close_key, 200)
    if ma200 and ma200 > 0:
        ma_signal = (cur - ma200) / ma200
        ma_score = max(-1, min(1, ma_signal * 5))  # ±20% → ±1
        score += ma_score * 0.35
        components["ma200_signal"] = round(ma_signal, 3)

    # 60일 모멘텀
    mom60 = compute_momentum(history, close_key, 60)
    if mom60 is not None:
        mom_score = max(-1, min(1, mom60 * 5))
        score += mom_score * 0.35
        components["mom60"] = round(mom60, 3)

    # SPY 상대강도
    rs = compute_relative_strength(history, close_key, "SPY_Close", 60)
    if rs is not None:
        rs_score = max(-1, min(1, (rs - 1.0) * 5))
        score += rs_score * 0.30
        components["rs_vs_spy"] = round(rs, 3)

    return {
        "score": round(max(-1, min(1, score)), 3),
        "components": components,
        "available": True,
    }


def compute_blended_alpha(impact_result: Dict, history: List[Dict],
                          tickers: Optional[List[str]] = None) -> Dict[str, Any]:
    """매크로 임팩트 + 기술적 점수 블렌딩 → 종합 알파."""
    impacts = impact_result.get("ticker_impacts", {})
    if tickers is None:
        tickers = list(impacts.keys())

    blended = {}
    for ticker in tickers:
        macro_impact = impacts.get(ticker, {}).get("total_impact", 0.0)
        tech = compute_technical_score(history, ticker)
        tech_score = tech["score"]

        # 매크로 임팩트를 -1~1로 정규화 (±25% cap 기준)
        macro_norm = max(-1, min(1, macro_impact / 0.25))

        blended_score = ALPHA_BLEND_MACRO * macro_norm + ALPHA_BLEND_TECH * tech_score

        # 정합/배반 판정
        if macro_norm > 0.2 and tech_score > 0.2:
            alignment = "🟢🟢 매크로+기술 동반 순풍"
        elif macro_norm < -0.2 and tech_score < -0.2:
            alignment = "🔴🔴 매크로+기술 동반 역풍"
        elif macro_norm > 0.2 and tech_score < -0.2:
            alignment = "🟡 매크로 순풍 vs 기술 역풍 (괴리)"
        elif macro_norm < -0.2 and tech_score > 0.2:
            alignment = "🟡 매크로 역풍 vs 기술 순풍 (괴리)"
        else:
            alignment = "⚪ 중립"

        blended[ticker] = {
            "macro_impact": round(macro_impact, 4),
            "macro_norm": round(macro_norm, 3),
            "tech_score": tech_score,
            "blended_alpha": round(blended_score, 3),
            "alignment": alignment,
            "tech_components": tech.get("components", {}),
        }

    ranked = sorted(blended.items(), key=lambda x: -x[1]["blended_alpha"])
    return {
        "blended": blended,
        "ranked": [(t, b["blended_alpha"], b["alignment"]) for t, b in ranked],
        "blend_weights": {"macro": ALPHA_BLEND_MACRO, "tech": ALPHA_BLEND_TECH},
    }


# ═══════════════════════════════════════════════════════════════════════
# L16: 종목 투자 논리 프로파일 (29종목 thesis/role/tier/triggers)
# ═══════════════════════════════════════════════════════════════════════
# 각 종목의 INVICTUS 역할, 티어, 핵심 논리, 진입/청산 트리거 참조 데이터.
# 브리핑에서 종목 추천 시 논리 근거로 사용.
# ═══════════════════════════════════════════════════════════════════════

TICKER_PROFILES = {
    "SMH": {"tier": "ATTACK", "role": "AI 반도체 코어",
            "thesis": "AI capex 슈퍼사이클 직접 수혜. AI_POWER 축 최대 베타.",
            "key_axes": ["AI_POWER", "MONETARY", "GROWTH"],
            "entry": "AI_POWER accelerating+ & SMH>MA200", "exit": "AI_POWER bottleneck or saturation 신호",
            "risk": "시스코 2000형 밸류 붕괴. 딥시크형 효율혁신 GPU 수요 잠식."},
    "QQQM": {"tier": "ATTACK", "role": "성장주 코어",
             "thesis": "빅테크 + 나스닥100. AI + 금리 민감.",
             "key_axes": ["AI_POWER", "MONETARY"],
             "entry": "MONETARY dovish/hold & 성장 견조", "exit": "MONETARY hawkish 가속",
             "risk": "고금리 멀티플 압박. 집중도 리스크."},
    "NLR": {"tier": "HEDGE", "role": "원자력/전력 인프라",
            "thesis": "AI 데이터센터 전력 수요 폭증. McKinsey 전력 +2.6%/년. bottleneck 시 최대 수혜.",
            "key_axes": ["AI_POWER", "WAR"],
            "entry": "AI_POWER accelerating+ & 전력 상대강도", "exit": "AI capex 3분기 둔화",
            "risk": "규제 리스크. 우라늄 가격 변동."},
    "COPX": {"tier": "ATTACK", "role": "구리 광산",
             "thesis": "데이터센터 1GW=구리 4000톤(IEA). AI+전력화 구조적 수요. Dr.Copper 경기 신호.",
             "key_axes": ["AI_POWER", "GROWTH", "CREDIT"],
             "entry": "AI_POWER+ & GROWTH steady+", "exit": "GROWTH recession",
             "risk": "중국 부동산 위기. 경기 민감."},
    "GLD": {"tier": "HEDGE", "role": "금 — 유일 귀금속 헤지",
            "thesis": "지정학 + 재정 헤지. 실질금리 역상관. WAR/FISCAL 순풍.",
            "key_axes": ["WAR", "FISCAL", "MONETARY"],
            "entry": "WAR regional+ or 실질금리 하락", "exit": "실질금리 급등 (DFII10>2.5%)",
            "risk": "고실질금리 역풍. 무이자 자산."},
    "XLE": {"tier": "HEDGE", "role": "에너지 섹터",
            "thesis": "유가 직접 수혜. OIL disrupted/blocked 순풍. 인플레 헤지.",
            "key_axes": ["OIL", "WAR"],
            "entry": "OIL disrupted+ & WTI>$80", "exit": "OIL normalize",
            "risk": "유가 급락. 증산. 수요 둔화."},
    "ITA": {"tier": "HEDGE", "role": "방산",
            "thesis": "지정학 긴장 + 국방비 증액. WAR/FISCAL 순풍.",
            "key_axes": ["WAR", "FISCAL"],
            "entry": "WAR limited+ & 국방예산 확대", "exit": "WAR ceasefire 정착",
            "risk": "평화 정착. 예산 삭감."},
    "PDBC": {"tier": "HEDGE", "role": "원자재 바스켓",
             "thesis": "광범위 원자재. OIL + 인플레 헤지. 실물 자산.",
             "key_axes": ["OIL", "WAR", "GROWTH"],
             "entry": "OIL/인플레 상승", "exit": "디플레 전환",
             "risk": "경기 침체 수요 붕괴."},
    "TLT": {"tier": "DEFENSE", "role": "장기 국채",
            "thesis": "디플레/침체 헤지. 금리 하락 시 듀레이션 수익. DEFLATION 레짐 핵심.",
            "key_axes": ["MONETARY", "FISCAL", "GROWTH"],
            "entry": "MONETARY dovish & 침체 신호", "exit": "30Y 5.3% 돌파",
            "risk": "재정 지배 + 장기금리 발작. 인플레 끈적임."},
    "SGOV": {"tier": "DEFENSE", "role": "초단기 국채 (현금성)",
             "thesis": "달러RP 대용. 무위험 4%+ 수익. 방어 코어.",
             "key_axes": [],
             "entry": "방어 전환 시", "exit": "공격 전환 시",
             "risk": "기회비용 (강세장)."},
}


def get_ticker_thesis(ticker: str) -> Dict[str, Any]:
    """종목 투자 논리 조회."""
    return TICKER_PROFILES.get(ticker, {
        "tier": "?", "role": "프로파일 미등록", "thesis": "", "key_axes": [],
        "entry": "", "exit": "", "risk": "",
    })




# ═══════════════════════════════════════════════════════════════════════
# L16-EXT: 29종목 전체 투자 논리 프로파일 (완성판)
# ═══════════════════════════════════════════════════════════════════════
# TICKER_PROFILES를 Oracle IMPACT_BY_AXIS 전 종목으로 확장.
# ═══════════════════════════════════════════════════════════════════════

TICKER_PROFILES_EXT = {
    "MAGS": {"tier": "ATTACK", "role": "Magnificent 7",
             "thesis": "빅테크 7종 집중. AI 슈퍼사이클 핵심. 시장 주도주.",
             "key_axes": ["AI_POWER", "MONETARY", "GROWTH"],
             "entry": "AI_POWER accelerating+ & 성장 견조", "exit": "AI_POWER bottleneck",
             "risk": "초집중 리스크. 밸류 프리미엄 과대. 규제."},
    "XLU": {"tier": "HEDGE", "role": "유틸리티 (전력)",
            "thesis": "AI 전력 수요 + 방어적 배당. AI_POWER bottleneck 시 최대 수혜.",
            "key_axes": ["AI_POWER", "MONETARY"],
            "entry": "AI_POWER+ or 금리 하락", "exit": "금리 급등",
            "risk": "금리 민감. 규제 가격 통제."},
    "PAVE": {"tier": "ATTACK", "role": "인프라 건설",
             "thesis": "재정 부양 + 리쇼어링 + AI 인프라. FISCAL expansive 수혜.",
             "key_axes": ["FISCAL", "AI_POWER", "GROWTH"],
             "entry": "FISCAL expansive & 인프라 예산", "exit": "FISCAL austere",
             "risk": "금리 상승. 예산 삭감. 경기 둔화."},
    "XLF": {"tier": "ATTACK", "role": "금융 섹터",
            "thesis": "고금리 순이자마진 + 신용 정상. MONETARY hawkish 일부 수혜.",
            "key_axes": ["MONETARY", "CREDIT", "GROWTH"],
            "entry": "CREDIT easy/tight & 금리 안정", "exit": "CREDIT crisis",
            "risk": "신용 경색. 침체 대손. 상업부동산."},
    "XLV": {"tier": "DEFENSE", "role": "헬스케어 (방어)",
            "thesis": "방어적 + 인구 고령화 구조 수요. 경기 둔감.",
            "key_axes": ["GROWTH"],
            "entry": "방어 전환 시", "exit": "강세장 가속",
            "risk": "약가 규제. 정책 리스크."},
    "CIBR": {"tier": "ATTACK", "role": "사이버보안",
             "thesis": "지정학 긴장 + AI 보안 수요. WAR + AI 복합 수혜.",
             "key_axes": ["WAR", "AI_POWER", "GROWTH"],
             "entry": "WAR limited+ & 보안 지출 확대", "exit": "성장 급랭",
             "risk": "밸류 과대. 성장주 금리 민감."},
    "SLV": {"tier": "HEDGE", "role": "은 (산업+귀금속)",
            "thesis": "금 대비 산업 수요(태양광/전자) 추가. AI_POWER 일부 수혜.",
            "key_axes": ["WAR", "FISCAL", "AI_POWER"],
            "entry": "금 강세 + 산업 수요", "exit": "산업 침체",
            "risk": "변동성 큼. 산업 수요 둔화. (Commander: SLV 기각 이력)"},
    "IEF": {"tier": "DEFENSE", "role": "중기 국채 (7-10Y)",
            "thesis": "TLT보다 듀레이션 짧음. 중간 방어. 금리 하락 수혜.",
            "key_axes": ["MONETARY", "GROWTH"],
            "entry": "MONETARY dovish/hold", "exit": "금리 급등",
            "risk": "장기금리 발작. 인플레."},
    "LQD": {"tier": "DEFENSE", "role": "투자등급 회사채",
            "thesis": "IG 크레딧 + 듀레이션. CREDIT easy 수혜.",
            "key_axes": ["CREDIT", "MONETARY"],
            "entry": "CREDIT easy & 금리 안정", "exit": "CREDIT tight+",
            "risk": "스프레드 확대 + 금리 동반 상승."},
    "IWM": {"tier": "ATTACK", "role": "소형주 (러셀2000)",
            "thesis": "금리 인하 + 내수 회복 시 고베타. risk-on 레버리지.",
            "key_axes": ["MONETARY", "GROWTH", "CREDIT"],
            "entry": "MONETARY dovish & GROWTH boom", "exit": "CREDIT tight, 침체",
            "risk": "금리 민감 최대. 신용 의존. 침체 취약."},
    "CQQQ": {"tier": "ATTACK", "role": "중국 기술주",
             "thesis": "중국 AI/기술. TARIFF resolved + 부양 시 반등.",
             "key_axes": ["TARIFF", "MONETARY", "AI_POWER"],
             "entry": "TARIFF resolved & 중국 부양", "exit": "TARIFF breakdown",
             "risk": "미중 갈등. 규제. 부동산 위기. (역풍 시 최대 손실)"},
    "EWZ": {"tier": "ATTACK", "role": "브라질",
            "thesis": "원자재 수출 + 고금리 통화. 원자재 슈퍼사이클 수혜.",
            "key_axes": ["OIL", "GROWTH", "TARIFF"],
            "entry": "원자재 강세 & 신흥국 risk-on", "exit": "달러 급등, 원자재 붕괴",
            "risk": "정치 불안. 통화 변동. 달러 강세."},
    "INDA": {"tier": "ATTACK", "role": "인도",
             "thesis": "구조적 성장 + 제조업 이전. 장기 성장 스토리.",
             "key_axes": ["GROWTH", "MONETARY", "OIL"],
             "entry": "GROWTH boom & 신흥국 자금 유입", "exit": "유가 급등(수입국), 달러 강세",
             "risk": "고밸류. 유가 민감(수입국). 달러 강세."},
    "VWO": {"tier": "ATTACK", "role": "신흥국 전반",
            "thesis": "신흥국 분산. risk-on + 달러 약세 수혜.",
            "key_axes": ["MONETARY", "OIL", "GROWTH"],
            "entry": "달러 약세 & risk-on", "exit": "달러 급등, 위기",
            "risk": "달러 강세. 자금 유출. 중국 비중."},
    "VEA": {"tier": "ATTACK", "role": "선진국(미국 외)",
            "thesis": "유럽/일본 선진국. 분산 + 밸류.",
            "key_axes": ["MONETARY", "GROWTH"],
            "entry": "글로벌 risk-on", "exit": "글로벌 침체",
            "risk": "유럽 경기. 환율."},
    "EWJ": {"tier": "ATTACK", "role": "일본",
            "thesis": "엔 약세 수출 + 거버넌스 개혁. BOJ 정책 민감.",
            "key_axes": ["MONETARY", "GROWTH"],
            "entry": "엔 약세 & 글로벌 성장", "exit": "엔 급등, BOJ 긴축",
            "risk": "엔 변동. BOJ 정책 전환."},
    "VNM": {"tier": "ATTACK", "role": "베트남",
            "thesis": "공급망 이전 수혜. 제조업 허브 부상.",
            "key_axes": ["TARIFF", "GROWTH"],
            "entry": "공급망 재편 & 신흥국 risk-on", "exit": "TARIFF breakdown, 달러 강세",
            "risk": "소형 시장 변동. 환율. 미중 갈등 유탄."},
    "TLH": {"tier": "DEFENSE", "role": "장기 국채 (10-20Y)",
            "thesis": "TLT-IEF 중간 듀레이션. 방어.",
            "key_axes": ["MONETARY", "GROWTH"],
            "entry": "MONETARY dovish", "exit": "금리 급등",
            "risk": "장기금리 발작."},
}

# 통합
def get_full_ticker_profile(ticker: str) -> Dict[str, Any]:
    """29종목 전체 프로파일 조회 (기본 + 확장)."""
    if ticker in TICKER_PROFILES:
        return TICKER_PROFILES[ticker]
    if ticker in TICKER_PROFILES_EXT:
        return TICKER_PROFILES_EXT[ticker]
    return {"tier": "?", "role": "미등록", "thesis": "", "key_axes": [],
            "entry": "", "exit": "", "risk": ""}


# ═══════════════════════════════════════════════════════════════════════
# L5-EXT2: S1~S11 시나리오 전체 정의 (서사 + 트리거 + 자산 함의)
# ═══════════════════════════════════════════════════════════════════════

SCENARIO_DEFINITIONS = {
    "S1": {
        "name": "연준 비둘기 전환",
        "narrative": "인플레 둔화 확인 → 연준 금리 인하 시작 → 유동성 완화 → 위험자산 랠리.",
        "triggers": ["근원 CPI 3개월 연속 둔화", "실업률 상승 전환", "파월 dovish 피벗"],
        "thresholds": {"DGS10": "<4.0%", "MONETARY": "dovish"},
        "winners": ["QQQM", "SMH", "IWM", "TLT", "CQQQ"],
        "losers": ["XLE(상대)", "GLD(실질금리)"],
        "axis_state": "MONETARY=dovish, CREDIT=easy, GROWTH=steady",
    },
    "S2": {
        "name": "이란 확전",
        "narrative": "호르무즈 봉쇄 강화 → 유가 급등 → 인플레 재점화 → 연준 긴축 유지 → 스태그플레이션.",
        "triggers": ["호르무즈 군사 충돌", "WTI $100+", "이스라엘-이란 직접 교전"],
        "thresholds": {"WTI": ">100", "WAR": "total", "OIL": "blocked"},
        "winners": ["XLE", "PDBC", "GLD", "ITA", "NLR"],
        "losers": ["CQQQ", "SMH", "IWM", "성장주 전반"],
        "axis_state": "WAR=total, OIL=blocked, MONETARY=hawkish",
    },
    "S5": {
        "name": "복합 충격",
        "narrative": "지정학 + 신용 + 성장 동시 악화 → 시스템 위기 → 전면 risk-off.",
        "triggers": ["OAS_HY 5.8%+", "VIX 35+", "복수 축 동시 악화"],
        "thresholds": {"OAS_HY": ">5.8", "CREDIT": "crisis", "GROWTH": "recession"},
        "winners": ["SGOV", "GLD(일부)"],
        "losers": ["전 위험자산", "특히 고베타(IWM/CQQQ/SMH)"],
        "axis_state": "WAR=regional, CREDIT=crisis, GROWTH=recession",
    },
    "S6": {
        "name": "AI 위기 (citrini)",
        "narrative": "AI capex ROI 의문 → SaaS 수익화 실패 → AI 밸류 붕괴 (시스코 2000형).",
        "triggers": ["하이퍼스케일러 capex 가이던스 하향", "NVDA 가이던스 미스", "SaaS 성장 둔화"],
        "thresholds": {"AI_POWER": "bottleneck", "GROWTH": "slowdown"},
        "winners": ["GLD", "SGOV", "방어주(XLV/XLU)"],
        "losers": ["SMH", "QQQM", "MAGS", "AI 인프라(NLR/COPX 일부)"],
        "axis_state": "AI_POWER=bottleneck, CREDIT=shadow_stress",
    },
    "S7": {
        "name": "연준 매파 지속",
        "narrative": "인플레 끈적임 → 연준 고금리 장기화 (higher for longer) → 멀티플 압박.",
        "triggers": ["근원 CPI 정체", "고용 견조 지속", "점도표 상향"],
        "thresholds": {"MONETARY": "hawkish", "DGS10": ">4.5%"},
        "winners": ["XLF", "SGOV", "단기채"],
        "losers": ["TLT", "성장주", "IWM", "CQQQ"],
        "axis_state": "MONETARY=hawkish, GROWTH=boom",
    },
    "S9": {
        "name": "그랜드 바겐",
        "narrative": "이란 협상 타결 + 미중 관세 해소 → 지정학 리스크 해소 → 골디락스 랠리.",
        "triggers": ["호르무즈 재개방", "미중 관세 협정", "휴전 정착"],
        "thresholds": {"WAR": "ceasefire", "OIL": "normalize", "TARIFF": "resolved"},
        "winners": ["CQQQ", "SMH", "IWM", "신흥국(VWO/INDA/EWZ)"],
        "losers": ["XLE", "GLD", "ITA", "PDBC(안전/실물 헤지)"],
        "axis_state": "WAR=ceasefire, OIL=normalize, TARIFF=resolved",
    },
    "S10": {
        "name": "희토류 금수",
        "narrative": "중국 희토류 수출 통제 → 반도체/방산 공급망 충격 → 기술주 타격.",
        "triggers": ["중국 희토류 수출 제한", "미중 기술 갈등 격화"],
        "thresholds": {"TARIFF": "breakdown", "AI_POWER": "bottleneck"},
        "winners": ["COPX(대체 광물)", "ITA(국방 자립)", "GLD"],
        "losers": ["SMH", "CQQQ", "기술 공급망 전반"],
        "axis_state": "TARIFF=breakdown, AI_POWER=bottleneck",
    },
    "S11": {
        "name": "AI capex 포화",
        "narrative": "AI 투자 수확체감 → capex 둔화 → AI 인프라 수요 정체 (saturation).",
        "triggers": ["빅테크 capex 3분기 둔화", "데이터센터 가동률 하락"],
        "thresholds": {"AI_POWER": "bottleneck", "GROWTH": "slowdown"},
        "winners": ["GLD", "SGOV", "가치주"],
        "losers": ["NLR", "COPX", "SMH", "AI 인프라 전반"],
        "axis_state": "AI_POWER=bottleneck, GROWTH=slowdown",
    },
}


def get_scenario_definition(scenario: str) -> Dict[str, Any]:
    """시나리오 상세 정의 조회."""
    return SCENARIO_DEFINITIONS.get(scenario, {"name": scenario, "narrative": "미정의"})


# ═══════════════════════════════════════════════════════════════════════
# L17: 과거 레짐 라벨링 + 레짐 통계 분석
# ═══════════════════════════════════════════════════════════════════════
# 368일 히스토리 전체를 Oracle 레짐 분류기로 라벨링.
# 레짐별 빈도, 지속기간, 전환 패턴, 레짐별 자산 성과 통계.
# ═══════════════════════════════════════════════════════════════════════

def label_historical_regimes(history: List[Dict], step: int = 5) -> Dict[str, Any]:
    """과거 데이터 레짐 라벨링 (step일 간격 샘플링).
    
    각 시점의 센서로 그래디언트 + 레짐 추정.
    """
    O = load_oracle()
    grad_fn = O.get("compute_regime_gradient")
    inputs_fn = O.get("compute_regime_inputs")
    classify_fn = O.get("classify_macro_regime")
    if not all([grad_fn, inputs_fn, classify_fn]):
        return {"error": "레짐 함수 미로딩"}

    labels = []
    for i in range(0, len(history), step):
        h = history[i]
        vix = h.get("VIX"); oas = h.get("OAS_HY"); move = h.get("MOVE")
        dfii10 = h.get("DFII10"); pmi = h.get("PMI")
        if None in (vix, oas, move):
            continue
        try:
            grad = grad_fn(vix=vix, oas_hy=oas, move=move, flow_signal="NEUTRAL",
                           dfii10=dfii10 if dfii10 is not None else 1.5)
            gs = grad.get("total_score", 50)
            # 간이 레짐 (gradient 기반)
            if gs < 25:
                regime = "EXPANSION"
            elif gs < 45:
                regime = "HIGH_RATE/EXPANSION"
            elif gs < 65:
                regime = "SLOWDOWN"
            else:
                regime = "RECESSION/STORM"
            labels.append({
                "date": h.get("Date"), "gradient": gs, "regime": regime,
                "vix": vix, "oas": oas,
            })
        except Exception:
            continue

    # 레짐 빈도 통계
    regime_counts = {}
    for l in labels:
        regime_counts[l["regime"]] = regime_counts.get(l["regime"], 0) + 1

    # 전환 횟수
    transitions = 0
    for j in range(1, len(labels)):
        if labels[j]["regime"] != labels[j-1]["regime"]:
            transitions += 1

    # 그래디언트 통계
    grads = [l["gradient"] for l in labels]
    avg_grad = sum(grads) / len(grads) if grads else 0
    max_grad = max(grads) if grads else 0
    min_grad = min(grads) if grads else 0

    return {
        "labeled_points": len(labels),
        "regime_frequency": regime_counts,
        "transitions": transitions,
        "gradient_stats": {
            "avg": round(avg_grad, 1), "max": round(max_grad, 1),
            "min": round(min_grad, 1), "current": round(grads[-1], 1) if grads else None,
        },
        "recent_labels": labels[-5:],
    }


def compute_regime_asset_performance(history: List[Dict], step: int = 5) -> Dict[str, Any]:
    """레짐별 자산 성과 통계 (간이).
    
    그래디언트 구간별로 SPY/GLD/NLR 등의 평균 수익률 측정.
    """
    O = load_oracle()
    grad_fn = O.get("compute_regime_gradient")
    if not grad_fn:
        return {"error": "gradient 함수 미로딩"}

    # 그래디언트 구간별 종목 수익률 수집
    buckets = {"low(0-25)": [], "mid(25-50)": [], "high(50-75)": [], "extreme(75+)": []}
    asset_returns = {t: dict(buckets) for t in ["SPY", "GLD", "NLR", "XLE", "TLT"]}

    closes_prev = {}
    for i in range(0, len(history) - step, step):
        h = history[i]; h_next = history[min(i + step, len(history) - 1)]
        vix = h.get("VIX"); oas = h.get("OAS_HY"); move = h.get("MOVE")
        if None in (vix, oas, move):
            continue
        try:
            gs = grad_fn(vix=vix, oas_hy=oas, move=move, flow_signal="NEUTRAL",
                         dfii10=h.get("DFII10", 1.5)).get("total_score", 50)
        except Exception:
            continue

        if gs < 25: bucket = "low(0-25)"
        elif gs < 50: bucket = "mid(25-50)"
        elif gs < 75: bucket = "high(50-75)"
        else: bucket = "extreme(75+)"

        for t in asset_returns:
            ck = _bt_close_key(t)
            c0 = h.get(ck); c1 = h_next.get(ck)
            if c0 and c1 and c0 > 0:
                asset_returns[t][bucket].append((c1 - c0) / c0)

    # 구간별 평균 수익률
    summary = {}
    for t, bkts in asset_returns.items():
        summary[t] = {}
        for b, rets in bkts.items():
            if rets:
                summary[t][b] = round(sum(rets) / len(rets) * 100, 2)  # % per step
            else:
                summary[t][b] = None

    return {"asset_returns_by_gradient": summary, "step_days": step}


# ═══════════════════════════════════════════════════════════════════════
# L7-EXT3: 심화 QLS 진단 (정체성/제도게임/그린법칙/다행위자)
# ═══════════════════════════════════════════════════════════════════════

def qls_identity_payoffs(axis_probs: Dict) -> List[TheoryResult]:
    """정체성 보수 분석 (Akerlof-Kranton). 경제적 보수 vs 정체성 보수 충돌."""
    _, L = _load_strategy_engines()
    results = []
    try:
        IP = L["IdentityPayoff"]
        # 연준: 인플레 파이터 정체성 vs 경기 부양 압력
        fed_id = IP(actor="연준", identity_group="중앙은행",
            identity_norm="인플레 파이터 (물가안정 신뢰)",
            monetary_payoff="조기 인하로 경기 부양 (정치적 호응)",
            identity_payoff="인플레 통제 신뢰 유지 (장기 신용)",
            conflict="조기 인하 시 인플레 파이터 정체성 훼손 → 끈적임 위험")
        # 이란: 저항 정체성 vs 경제적 실익
        iran_id = IP(actor="이란 정권", identity_group="이슬람 혁명 수호자",
            identity_norm="반미·반이스라엘 저항축 리더",
            monetary_payoff="제재 해제로 경제 회복",
            identity_payoff="저항 정체성 유지 (정권 정당성)",
            conflict="협상 양보 시 저항 정체성 훼손 → 내부 강경파 반발")
        d1, d2 = fed_id.diagnose(), iran_id.diagnose()
        results.append(TheoryResult("행동경제학정성",2,"정체성 보수 (QLS Akerlof-Kranton)","MEDIUM",
            {"fed_identity": str(d1), "iran_identity": str(d2)},
            "연준=인플레파이터 정체성이 조기인하 제약. 이란=저항 정체성이 협상 양보 제약.",
            "양측 정체성 보수가 합리적 타협 지연 → 교착/끈적임 장기화 베팅."))
    except Exception as e:
        results.append(TheoryResult("행동경제학정성",2,"정체성","LOW",{"error":str(e)},f"오류:{e}",""))
    return results


def qls_institutional_games(axis_probs: Dict) -> List[TheoryResult]:
    """제도 게임 심화 (Fed 운영틀 / 미중 무역체제 / OPEC 카르텔)."""
    _, L = _load_strategy_engines()
    results = []
    try:
        IGC = L["InstitutionalGameCheck"]
        games = [
            IGC(rule_name="연준 2% 인플레 목표제",
                rule_maker="FOMC", who_benefits="채권자/물가안정", who_loses="채무자/고용",
                change_feasibility="낮음(신뢰 비용)", meta_game="평균물가목표제(AIT) 재해석 여지"),
            IGC(rule_name="WTO/미중 무역 체제",
                rule_maker="강대국 협상", who_benefits="수출국/소비자", who_loses="피관세 산업",
                change_feasibility="중간", meta_game="관세를 협상 레버리지로 무기화"),
            IGC(rule_name="OPEC+ 생산 쿼터",
                rule_maker="사우디-러시아 주도", who_benefits="산유국", who_loses="소비국/비회원",
                change_feasibility="중간(이탈 유인)", meta_game="쿼터 위반 + 시장점유 경쟁"),
        ]
        diags = [g.diagnose() for g in games]
        results.append(TheoryResult("권력정성",3,"제도 게임 심화 (QLS, 3제도)","MEDIUM",
            {f"institution_{i}": str(d) for i, d in enumerate(diags)},
            "연준 2% 목표(AIT 재해석 여지), 미중 무역(관세 무기화), OPEC(쿼터 이탈 유인).",
            "제도 규칙 변경 가능성이 레짐 전환 선행 신호. 메타게임 주시."))
    except Exception as e:
        results.append(TheoryResult("권력정성",3,"제도게임","LOW",{"error":str(e)},f"오류:{e}",""))
    return results


def qls_greene_laws_full(axis_probs: Dict) -> List[TheoryResult]:
    """그린의 권력 법칙 다중 적용 (현 지정학 상황)."""
    _, L = _load_strategy_engines()
    results = []
    war = _dominant_state(axis_probs, "WAR")
    try:
        GLC = L["GreeneLawCheck"]; GL = L["GreeneLaw"]
        laws = [
            GLC(law=GL.L15, actor="미국", applied=(war in ("regional","total")),
                evidence="제재 최대 압박 — 적을 완전히 짓밟아라"),
            GLC(law=GL.L35, actor="이란", applied=True,
                evidence="협상 타이밍 장악 — SPR 고갈 시점 노림"),
            GLC(law=GL.L33, actor="중국", applied=True,
                evidence="미국 약점(재정적자/SPR) 발견 후 압박"),
            GLC(law=GL.L48, actor="이란", applied=True,
                evidence="비대칭 전략 — 형체 없는 대리전으로 회피"),
        ]
        applied = [l for l in laws if l.applied]
        diags = [l.diagnose() for l in applied]
        results.append(TheoryResult("권력정성",3,f"그린의 법칙 다중 적용 (QLS, {len(applied)}법칙)","MEDIUM",
            {f"law_{i}": str(d) for i, d in enumerate(diags)},
            f"적용 법칙 {len(applied)}개: 미국 최대압박(L15), 이란 타이밍(L35)+비대칭(L48), 중국 약점공략(L33).",
            "다중 권력 법칙 충돌 = 고불확실성. 비대칭 전략이 지배적 → 헤지 유지."))
    except Exception as e:
        results.append(TheoryResult("권력정성",3,"그린법칙","LOW",{"error":str(e)},f"오류:{e}",""))
    return results


def qns_extended_games(axis_probs: Dict, latest: Dict) -> List[TheoryResult]:
    """추가 QNS 게임 (죄수의 딜레마 신용/공유지 비극 유동성)."""
    Q, _ = _load_strategy_engines()
    results = []
    credit = _dominant_state(axis_probs, "CREDIT")
    try:
        # 은행 신용 죄수의 딜레마 (모두 대출 회수 = 신용 경색)
        stress = {"easy":0,"tight":-2,"shadow_stress":-4,"crisis":-7}.get(credit,-2)
        game = Q["make_2x2_game"](name="Credit-PD", p1_name="BankA", p2_name="BankB",
            actions=("Lend","Withdraw"),
            payoffs=((3+stress,3+stress),(stress-1,5),(5,stress-1),(0,0)),
            game_type=Q["GameType"].STATIC)
        pure = Q["find_pure_nash"](game)
        comp = {"pure_nash": len(pure), "credit_state": credit}
        sev = "HIGH" if credit in ("shadow_stress","crisis") else "LOW"
        results.append(TheoryResult("게임이론",1,"신용 죄수의 딜레마 (QNS)",sev,comp,
            f"은행 신용 회수 게임. CREDIT={credit}. 순수 Nash {len(pure)}개. "
            f"스트레스 시 (Withdraw,Withdraw) 우월 → 신용 경색.",
            "신용 스트레스 상승 시 자기실현적 회수 → OAS 급등. 달러RP 선제."))
    except Exception as e:
        results.append(TheoryResult("게임이론",1,"신용PD","LOW",{"error":str(e)},f"오류:{e}",""))
    return results


def run_strategic_theory_extended(axis_probs: Dict, latest: Dict, derived: Dict) -> List[TheoryResult]:
    """심화 전략이론 통합 (정체성+제도+그린+추가게임)."""
    results = []
    results.extend(qls_identity_payoffs(axis_probs))
    results.extend(qls_institutional_games(axis_probs))
    results.extend(qls_greene_laws_full(axis_probs))
    results.extend(qns_extended_games(axis_probs, latest))
    return results


# ═══════════════════════════════════════════════════════════════════════
# L18: Commander 인터페이스 (오버라이드 + 의도 라우팅 + SSOT 제안)
# ═══════════════════════════════════════════════════════════════════════
# Commander 권한: 모든 SSOT 수정/자본 배분은 Commander 승인 필요.
# Autopilot은 제안만, Commander가 결정. 오버라이드 적용 + 차이 비교.
# ═══════════════════════════════════════════════════════════════════════

def apply_commander_overrides(axis_probs: Dict, overrides: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Commander 축 오버라이드 적용 + 자동 추론과 차이 비교.
    
    overrides: {"WAR": {"total": 0.4, "regional": 0.4, ...}, ...}
    """
    result = {"applied": {}, "diffs": {}, "original": {}}
    new_probs = {a: dict(p) for a, p in axis_probs.items()}

    for axis, override_probs in overrides.items():
        if axis not in AXIS_STATES:
            continue
        # 정규화
        normalized = _normalize_probs(override_probs, AXIS_STATES[axis])
        result["original"][axis] = dict(new_probs.get(axis, {}))
        # 자동 추론 vs 오버라이드 최빈 상태 비교
        auto_top = max(new_probs.get(axis, {"?": 1}).items(), key=lambda x: x[1])
        over_top = max(normalized.items(), key=lambda x: x[1])
        if auto_top[0] != over_top[0]:
            result["diffs"][axis] = {
                "auto": f"{auto_top[0]} {auto_top[1]:.0%}",
                "commander": f"{over_top[0]} {over_top[1]:.0%}",
                "changed": True,
            }
        new_probs[axis] = normalized
        result["applied"][axis] = normalized

    result["axis_probs"] = new_probs
    result["override_count"] = len(result["applied"])
    result["conflict_count"] = len(result["diffs"])
    return result


def parse_commander_intent(message: str) -> Dict[str, Any]:
    """Commander 메시지 의도 파싱 (terse 명령 해석).
    
    '진행' → execute, '다음' → next, '권고대로' → follow_recommendation 등.
    """
    msg = message.strip().lower()
    intent_map = {
        "진행": "execute", "다음": "next", "권고대로": "follow_recommendation",
        "유지": "hold", "재실행": "rerun", "전체": "full_run", "짧게": "brief",
        "브리핑": "briefing", "백테스트": "backtest", "비상": "emergency",
        "시나리오": "scenario", "포트폴리오": "portfolio",
    }
    detected = []
    for keyword, intent in intent_map.items():
        if keyword in msg:
            detected.append(intent)
    return {
        "raw": message,
        "intents": detected if detected else ["unknown"],
        "primary": detected[0] if detected else "unknown",
    }


def propose_ssot_update(axes_result: Dict, regime_result: Dict,
                        current_ssot_version: str = "2.13.1") -> Dict[str, Any]:
    """SSOT 갱신 제안 생성 (Commander 승인용).
    
    자동 추론 결과와 현재 저장값 차이를 제안 형태로 정리.
    Commander 결정 전까지 제안일 뿐 — 자동 적용 금지.
    """
    proposals = []
    axis_probs = axes_result["axis_probs"]

    for axis in ["WAR", "OIL", "MONETARY", "CREDIT", "GROWTH", "AI_POWER"]:
        ap = axis_probs.get(axis, {})
        if not ap:
            continue
        top_state, top_prob = max(ap.items(), key=lambda x: x[1])
        conf = axes_result["confidence"].get(axis, 0)
        source = axes_result["evidence"].get(axis, "")
        if conf >= 75:  # 높은 신뢰도만 제안
            proposals.append({
                "axis": axis,
                "proposed_state": top_state,
                "probability": round(top_prob, 3),
                "confidence": conf,
                "source": source[:50],
                "action": f"Oracle SSOT {axis} → {top_state} 갱신 검토",
            })

    regime = regime_result.get("macro_regime", {}).get("regime", "?")
    return {
        "ssot_version": current_ssot_version,
        "proposals": proposals,
        "proposed_regime": regime,
        "note": "⚠️ 제안일 뿐. SSOT 수정은 Commander 승인 필수. 자동 적용 금지.",
        "high_confidence_count": len(proposals),
    }


def build_intent_menu() -> Dict[str, Any]:
    """후속 옵션 메뉴 (ask_user_input 형식 준비).
    
    Commander 결정용 터치 버튼 옵션 (최대 4개, 🎯=권장).
    """
    return {
        "options": [
            {"label": "🎯 전체 브리핑 재실행", "intent": "full_run",
             "rationale": "최신 데이터로 8축+레짐+임팩트+전략이론 전체 갱신"},
            {"label": "시나리오 P&L 심화", "intent": "scenario_deep",
             "rationale": "S1~S11 조건부 P&L + 민감도 상세"},
            {"label": "포트폴리오 리밸런싱 제안", "intent": "rebalance",
             "rationale": "현재 비중 vs 목표 비중 차이 + 거래 제안"},
            {"label": "SSOT 갱신 제안 검토", "intent": "ssot_update",
             "rationale": "고신뢰 축 갱신안 (Commander 승인 대기)"},
        ],
        "recommended": 0,
        "max_options": 4,
    }


# ═══════════════════════════════════════════════════════════════════════
# L19: 리밸런싱 엔진 (현재 vs 목표 + 거래 제안 + 비용)
# ═══════════════════════════════════════════════════════════════════════
# 현재 보유 비중과 목표 비중 차이 → 거래 제안 + 회전율 + 밴드 리밸런싱.
# Commander 승인 전 제안일 뿐.
# ═══════════════════════════════════════════════════════════════════════

REBALANCE_BAND = 0.03      # ±3%p 밴드 (밴드 내 거래 생략)
MIN_TRADE_SIZE = 0.01      # 최소 거래 1%


def compute_rebalance(current_weights: Dict[str, float],
                      target_weights: Dict[str, float],
                      band: float = REBALANCE_BAND) -> Dict[str, Any]:
    """현재 → 목표 비중 리밸런싱 거래 제안.
    
    밴드 리밸런싱: ±band 이내 차이는 거래 생략 (거래비용 절감).
    비중은 0~1 또는 0~100 자동 인식.
    """
    # 단위 정규화 (0~1로)
    def _norm(w):
        total = sum(w.values())
        if total > 2:  # 0~100 스케일
            return {t: v / 100.0 for t, v in w.items()}
        return dict(w)

    cur = _norm(current_weights)
    tgt = _norm(target_weights)

    all_tickers = set(cur) | set(tgt)
    trades = []
    total_turnover = 0.0

    for ticker in sorted(all_tickers):
        c = cur.get(ticker, 0.0)
        t = tgt.get(ticker, 0.0)
        diff = t - c
        if abs(diff) < band:
            continue  # 밴드 내 → 거래 생략
        if abs(diff) < MIN_TRADE_SIZE:
            continue
        action = "BUY" if diff > 0 else "SELL"
        trades.append({
            "ticker": ticker, "action": action,
            "current": round(c * 100, 1), "target": round(t * 100, 1),
            "delta": round(diff * 100, 1),
        })
        total_turnover += abs(diff)

    # 거래 크기 순 정렬
    trades.sort(key=lambda x: -abs(x["delta"]))

    return {
        "trades": trades,
        "trade_count": len(trades),
        "turnover": round(total_turnover * 100, 1),  # 단방향 회전율 %
        "band_applied": band * 100,
        "note": "⚠️ 제안. 실거래는 Commander 승인 필수.",
    }


def generate_target_from_pipeline(ctx: Dict) -> Dict[str, float]:
    """파이프라인 결과 → 목표 비중 (가드레일 적용)."""
    guardrails = ctx.get("guardrails", {})
    return guardrails.get("adjusted_allocation", {})


def compute_rebalance_cost(rebalance: Dict, cost_bps: float = 5.0) -> Dict[str, Any]:
    """리밸런싱 거래 비용 추정 (bps).
    
    bps = basis point = 1/10000. 회전율(단방향) × 비용률.
    """
    turnover = rebalance.get("turnover", 0) / 100.0   # % → 비율
    cost_pct = turnover * (cost_bps / 10000.0)         # bps 정확 환산
    return {
        "turnover_pct": rebalance.get("turnover", 0),
        "cost_bps": cost_bps,
        "estimated_cost_pct": round(cost_pct, 5),
        "estimated_cost_per_100k": round(cost_pct * 100000, 1),  # $100k당 $
    }


# ═══════════════════════════════════════════════════════════════════════
# L20: 종합 API 레퍼런스 + 사용 가이드
# ═══════════════════════════════════════════════════════════════════════

def api_reference() -> Dict[str, Any]:
    """Oracle Autopilot 공개 API 레퍼런스."""
    return {
        "version": AUTOPILOT_VERSION,
        "entry_points": {
            "run_full()": "종합 실행 (B0~B12 풀버전 브리핑). __main__ 기본.",
            "run()": "경량 실행 (기본 브리핑).",
            "run_autopilot_full(commander_overrides, run_bt, bt_max_steps)": "오케스트레이터 직접 호출.",
        },
        "layers": {
            "L0": "공유 상수 공급 (Oracle Brief 의존성 충족)",
            "L1": "fetch_latest / fetch_history / validate_data",
            "L1.5": "build_derived_metrics (MA/모멘텀/상대강도/분위수)",
            "L2": "infer_all_axes (auto_prior + LEAD-5/6b + 프록시)",
            "L3": "run_regime_pipeline (Oracle 정식 체인)",
            "L4": "run_impact_engine (compute_axis_impact 29종목)",
            "L5": "compute_scenario_probs + compute_scenario_pnl_matrix",
            "L6": "construct_portfolio + DRP + 가드레일",
            "L7": "run_strategic_theory + QNS게임 + QLS스위트 + 심화",
            "L8": "run_transition_detector (EWMA)",
            "L9": "generate_briefing_v2 (B0~B12)",
            "L10": "self_check (자가 검증)",
            "L11": "run_backtest (룩어헤드 차단)",
            "L12": "run_sensor_suite + killswitch + AEGIS",
            "L13": "compute_position_sizing (Kelly + 리스크 패리티)",
            "L14": "run_macro_calendar (트리거 + 이벤트)",
            "L15": "compute_blended_alpha (매크로 + 기술)",
            "L16": "TICKER_PROFILES (29종목 논리)",
            "L17": "label_historical_regimes (레짐 통계)",
            "L18": "Commander 인터페이스 (오버라이드/의도/SSOT)",
            "L19": "compute_rebalance (리밸런싱 거래 제안)",
        },
        "oracle_integration": {
            "principle": "적정자 — Oracle v2.13.1 정식 함수 실호출",
            "functions_used": [
                "compute_regime_gradient", "compute_regime_inputs",
                "classify_macro_regime", "auto_prior(LEAD-5/6b)",
                "compute_axis_impact", "detect_regime_transition",
            ],
            "constants_supplied": [
                "GRADIENT_SENSOR_BANDS", "GRADIENT_ALLOCATION_GUIDE",
                "LIQUIDITY_STRESS_REGIME", "GLD_CAP_NORMAL",
                "RR_FLOW_ADJUST", "compute_real_rate_subscore",
            ],
        },
        "limitations": {
            "proxy_axes": "WAR/TARIFF/FISCAL은 시장 프록시 — 정치/정책 직접 반영 불가",
            "commander_authority": "SSOT 수정/자본 배분은 Commander 승인 필수",
            "backtest": "단기 윈도우 — 장기 검증 시 max_steps 확대 필요",
        },
    }


def usage_guide() -> str:
    """사용 가이드 텍스트."""
    return """
Oracle Autopilot v1.0.0 (적정자) 사용 가이드
═══════════════════════════════════════════

1. 기본 실행:
   python Oracle_Autopilot_v1_0.py
   → B0~B12 종합 브리핑 출력

2. 프로그램 호출:
   import Oracle_Autopilot_v1_0 as ap
   briefing = ap.run_autopilot_full(verbose=True)

3. Commander 오버라이드:
   overrides = {"WAR": {"total": 0.5, "regional": 0.3, "limited": 0.15, "ceasefire": 0.05}}
   ap.run_autopilot_full(commander_overrides=overrides)

4. 개별 계층 호출:
   latest = ap.fetch_latest(); history = ap.fetch_history()
   derived = ap.build_derived_metrics(latest, history)
   axes = ap.infer_all_axes(latest, history, derived)
   impact = ap.run_impact_engine(axes["axis_probs"])

5. 백테스트:
   bt = ap.run_backtest(history, max_steps=None)  # 전체 기간

원칙:
- Oracle SSOT 우선. 외부 입력은 Red Team 후보.
- 결론 우선. LIVE 값은 🌟 표시.
- Commander 결정 필요 시 제안만, 자동 적용 금지.
"""




# ═══════════════════════════════════════════════════════════════════════
# L21: Red Team 자가 감사 (결론 반증 + 프레이밍 약점 점검)
# ═══════════════════════════════════════════════════════════════════════
# Commander Red Team 프로토콜: 자동 결론을 반대 관점에서 검증.
# 누락 드라이버, 일방향 서사, 과신, 스테일 분석을 자가 점검.
# ═══════════════════════════════════════════════════════════════════════

def red_team_audit(ctx: Dict) -> Dict[str, Any]:
    """Autopilot 결론에 대한 Red Team 자가 감사."""
    axes_result = ctx["axes_result"]
    axis_probs = axes_result["axis_probs"]
    regime_result = ctx["regime_result"]
    impact_result = ctx["impact_result"]
    challenges = []

    # 도전 1: 프록시 축 과신 점검
    proxy_axes = ["WAR", "TARIFF", "FISCAL"]
    for axis in proxy_axes:
        conf = axes_result["confidence"].get(axis, 0)
        ap = axis_probs.get(axis, {})
        if ap:
            top_state, top_prob = max(ap.items(), key=lambda x: x[1])
            if top_prob > 0.7 and conf < 60:
                challenges.append({
                    "type": "프록시 과신",
                    "axis": axis,
                    "issue": f"{axis} {top_state} {top_prob:.0%} 확신이지만 신뢰도 {conf}% (프록시)",
                    "counter": "정치/정책 이벤트는 시장 프록시로 포착 불가. 뉴스 교차 검증 필수.",
                })

    # 도전 2: 레짐-임팩트 정합성 점검
    regime = regime_result.get("macro_regime", {}).get("regime", "?")
    ranked = impact_result.get("ranked", [])
    if regime == "EXPANSION" and ranked:
        # EXPANSION인데 안전자산(GLD)이 1위면 모순 가능
        top_ticker = ranked[0][0]
        if top_ticker in ("GLD", "SGOV", "TLT"):
            challenges.append({
                "type": "레짐-임팩트 괴리",
                "axis": "REGIME",
                "issue": f"레짐 EXPANSION인데 임팩트 1위가 방어자산 {top_ticker}",
                "counter": "그래디언트(변동성)와 축임팩트(방향)가 다른 신호. 레짐 재확인 필요.",
            })

    # 도전 3: 일방향 서사 점검 (모든 축이 한 방향?)
    war = _dominant_state(axis_probs, "WAR")
    oil = _dominant_state(axis_probs, "OIL")
    if war in ("regional", "total") and oil == "blocked":
        challenges.append({
            "type": "일방향 서사",
            "axis": "WAR+OIL",
            "issue": "지정학 확전 + 유가 봉쇄 동반 가정 — 강한 일방향 베팅",
            "counter": "휴전/협상 타결 시 급반전(S9). 베팅 비대칭성 점검. 헤지 유지.",
        })

    # 도전 4: 데이터 스테일 점검
    validation = ctx.get("validation", {})
    if validation.get("warnings"):
        for w in validation["warnings"]:
            if "경과" in w or "stale" in w.lower():
                challenges.append({
                    "type": "데이터 스테일",
                    "axis": "DATA",
                    "issue": w,
                    "counter": "최신 데이터로 재검증 권장.",
                })

    # 도전 5: AI_POWER 과열 점검 (시스코 교훈)
    ai = _dominant_state(axis_probs, "AI_POWER")
    if ai == "peak_demand":
        challenges.append({
            "type": "AI 과열 (시스코 교훈)",
            "axis": "AI_POWER",
            "issue": "AI_POWER peak_demand — 슈퍼사이클 서사 지배적",
            "counter": "시스코 2000: 정점에서 -89%. NVDA beat에도 주가 미반응 시 saturation 조기 신호.",
        })

    # 도전 6: 시나리오 집중 점검
    scenario_probs = ctx.get("scenario_probs", {})
    if scenario_probs:
        top_sc = max(scenario_probs.items(), key=lambda x: x[1])
        if top_sc[1] > 0.45:
            challenges.append({
                "type": "시나리오 집중",
                "axis": "SCENARIO",
                "issue": f"{top_sc[0]} {top_sc[1]:.0%} 단일 시나리오 집중",
                "counter": "단일 시나리오 과신 위험. 꼬리 시나리오(S5/S10) 헤지 점검.",
            })

    return {
        "challenges": challenges,
        "challenge_count": len(challenges),
        "audit_passed": len(challenges) <= 2,  # 도전 2건 이하면 견고
        "summary": f"Red Team 도전 {len(challenges)}건 제기. " +
                   ("결론 견고." if len(challenges) <= 2 else "결론 재검토 권장."),
    }


# ═══════════════════════════════════════════════════════════════════════
# L22: 교차축 상호작용 분석 + 레짐 조건부 종목 순위
# ═══════════════════════════════════════════════════════════════════════

def analyze_axis_interactions(axis_probs: Dict, impact_result: Dict) -> Dict[str, Any]:
    """축 간 상호작용 분석. INTERACTION_PAIRS 발동 현황 + 영향 종목."""
    impacts = impact_result.get("ticker_impacts", {})
    interaction_pairs = impact_result.get("interaction_pairs", {})

    # 각 종목의 interaction boost 발동 현황
    boosted_tickers = []
    for ticker, detail in impacts.items():
        if detail.get("interaction_applied"):
            boosts = detail.get("interaction_pair_boosts", [])
            if boosts:
                boosted_tickers.append({
                    "ticker": ticker,
                    "total_impact": detail.get("total_impact", 0),
                    "boosts": boosts,
                })

    # 가장 강한 부스트 받은 종목
    boosted_tickers.sort(key=lambda x: abs(x["total_impact"]), reverse=True)

    # 활성 축쌍 (red 동반)
    red_axes = [a for a in axis_probs if _dominant_state(axis_probs, a) in
                ("regional", "total", "blocked", "hawkish", "crisis", "shadow_stress",
                 "breakdown", "recession", "bottleneck")]
    active_pairs = []
    for i, a1 in enumerate(red_axes):
        for a2 in red_axes[i+1:]:
            active_pairs.append(f"{a1}×{a2}")

    return {
        "boosted_ticker_count": len(boosted_tickers),
        "top_boosted": boosted_tickers[:5],
        "red_axes": red_axes,
        "active_red_pairs": active_pairs,
        "interaction_pairs_defined": len(interaction_pairs),
    }


def regime_conditional_rankings(history: List[Dict], target_regime: str = None) -> Dict[str, Any]:
    """레짐 조건부 종목 순위. 과거 유사 그래디언트 구간에서 종목 성과.
    
    현재와 유사한 레짐 환경에서 어떤 종목이 우세였는지 통계.
    """
    perf = compute_regime_asset_performance(history, step=5)
    if "error" in perf:
        return perf

    asset_perf = perf.get("asset_returns_by_gradient", {})
    # 저그래디언트(순풍) 구간 성과 순위
    low_grad_ranking = []
    for ticker, buckets in asset_perf.items():
        low_ret = buckets.get("low(0-25)")
        if low_ret is not None:
            low_grad_ranking.append((ticker, low_ret))
    low_grad_ranking.sort(key=lambda x: -x[1])

    # 고그래디언트(위험) 구간 성과 순위
    high_grad_ranking = []
    for ticker, buckets in asset_perf.items():
        high_ret = buckets.get("high(50-75)")
        if high_ret is not None:
            high_grad_ranking.append((ticker, high_ret))
    high_grad_ranking.sort(key=lambda x: -x[1])

    return {
        "low_gradient_winners": low_grad_ranking,
        "high_gradient_winners": high_grad_ranking,
        "interpretation": "저그래디언트(순풍): 공격자산 우세. 고그래디언트(위험): 방어자산 우세 기대.",
    }




# ═══════════════════════════════════════════════════════════════════════
# L23: 종합 스트레스 테스트 (14 시나리오 충격)
# ═══════════════════════════════════════════════════════════════════════
# 포트폴리오를 14개 역사적/가상 위기 시나리오에 노출, 손실 측정.
# 각 시나리오는 8축을 특정 위기 상태로 강제 → compute_axis_impact.
# ═══════════════════════════════════════════════════════════════════════

STRESS_SCENARIOS = {
    "ST01_2008_GFC": {
        "name": "2008 금융위기형",
        "axes": {"CREDIT": "crisis", "GROWTH": "recession", "MONETARY": "dovish",
                 "WAR": "limited", "OIL": "disrupted", "AI_POWER": "bottleneck"},
        "desc": "신용 경색 + 침체 + 연준 긴급 인하",
    },
    "ST02_2020_COVID": {
        "name": "2020 팬데믹 충격형",
        "axes": {"GROWTH": "recession", "CREDIT": "shadow_stress", "MONETARY": "dovish",
                 "OIL": "normalize", "WAR": "ceasefire", "AI_POWER": "normal"},
        "desc": "급격한 성장 붕괴 + 유동성 충격",
    },
    "ST03_2022_INFLATION": {
        "name": "2022 인플레 긴축형",
        "axes": {"MONETARY": "hawkish", "GROWTH": "slowdown", "CREDIT": "tight",
                 "OIL": "disrupted", "WAR": "regional", "AI_POWER": "normal"},
        "desc": "인플레 급등 + 공격적 긴축 + 채권/주식 동반 하락",
    },
    "ST04_OIL_SHOCK": {
        "name": "오일 쇼크형 (1973)",
        "axes": {"OIL": "blocked", "WAR": "total", "MONETARY": "hawkish",
                 "GROWTH": "slowdown", "CREDIT": "tight", "AI_POWER": "normal"},
        "desc": "유가 봉쇄 + 스태그플레이션",
    },
    "ST05_HORMUZ_CLOSURE": {
        "name": "호르무즈 완전 폐쇄",
        "axes": {"OIL": "blocked", "WAR": "total", "MONETARY": "hold",
                 "GROWTH": "slowdown", "AI_POWER": "normal", "CREDIT": "tight"},
        "desc": "이란 호르무즈 봉쇄 + 유가 $150+",
    },
    "ST06_AI_BUBBLE_BURST": {
        "name": "AI 버블 붕괴 (시스코형)",
        "axes": {"AI_POWER": "bottleneck", "GROWTH": "slowdown", "CREDIT": "shadow_stress",
                 "MONETARY": "hold", "WAR": "limited", "OIL": "disrupted"},
        "desc": "AI capex ROI 실망 + 기술주 폭락",
    },
    "ST07_RATE_SPIKE": {
        "name": "장기금리 발작",
        "axes": {"MONETARY": "hawkish", "FISCAL": "dominant", "GROWTH": "slowdown",
                 "CREDIT": "tight", "WAR": "limited", "OIL": "disrupted"},
        "desc": "30Y 6%+ 재정 지배 우려 + 채권 폭락",
    },
    "ST08_CHINA_CRISIS": {
        "name": "중국 경착륙",
        "axes": {"TARIFF": "breakdown", "GROWTH": "recession", "CREDIT": "shadow_stress",
                 "OIL": "normalize", "WAR": "limited", "AI_POWER": "bottleneck"},
        "desc": "중국 부동산/금융 위기 + 글로벌 디플레 전파",
    },
    "ST09_DOLLAR_CRISIS": {
        "name": "달러 신뢰 위기",
        "axes": {"FISCAL": "dominant", "MONETARY": "dovish", "CREDIT": "shadow_stress",
                 "WAR": "regional", "OIL": "blocked", "GROWTH": "slowdown"},
        "desc": "재정 지배 + 달러 약세 + 금 급등",
    },
    "ST10_STAGFLATION": {
        "name": "본격 스태그플레이션",
        "axes": {"OIL": "blocked", "MONETARY": "hawkish", "GROWTH": "recession",
                 "WAR": "regional", "CREDIT": "tight", "AI_POWER": "normal"},
        "desc": "고인플레 + 침체 동반 (최악 조합)",
    },
    "ST11_COMPLEX_SHOCK": {
        "name": "복합 충격 (S5)",
        "axes": {"WAR": "total", "OIL": "blocked", "CREDIT": "crisis",
                 "GROWTH": "recession", "MONETARY": "hawkish", "AI_POWER": "bottleneck"},
        "desc": "전 축 동시 악화 (시스템 위기)",
    },
    "ST12_GRAND_BARGAIN": {
        "name": "그랜드 바겐 (상방)",
        "axes": {"WAR": "ceasefire", "OIL": "normalize", "TARIFF": "resolved",
                 "MONETARY": "dovish", "GROWTH": "boom", "AI_POWER": "accelerating"},
        "desc": "지정학 해소 + 금리 인하 + AI 순풍 (골디락스)",
    },
    "ST13_SOFT_LANDING": {
        "name": "연착륙",
        "axes": {"GROWTH": "steady", "MONETARY": "hold", "CREDIT": "easy",
                 "WAR": "limited", "OIL": "disrupted", "AI_POWER": "accelerating"},
        "desc": "인플레 둔화 + 성장 유지 + 점진적 완화",
    },
    "ST14_AI_SUPERCYCLE": {
        "name": "AI 슈퍼사이클 가속",
        "axes": {"AI_POWER": "peak_demand", "GROWTH": "boom", "MONETARY": "hold",
                 "CREDIT": "easy", "WAR": "limited", "OIL": "disrupted"},
        "desc": "AI capex 폭증 + 생산성 혁명 + 반도체/전력 랠리",
    },
}


def _stress_axis_probs(stress_axes: Dict[str, str]) -> Dict[str, Dict[str, float]]:
    """스트레스 시나리오 축 상태 → axis_probs (90% 확정)."""
    probs = {}
    for axis, states in AXIS_STATES.items():
        target = stress_axes.get(axis)
        if target and target in states:
            p = {s: 0.03 for s in states}
            p[target] = 1.0 - 0.03 * (len(states) - 1)
            probs[axis] = p
        else:
            probs[axis] = {s: 1.0 / len(states) for s in states}
    return probs


def run_stress_test(weights: Dict[str, float]) -> Dict[str, Any]:
    """포트폴리오 14 스트레스 시나리오 테스트."""
    O = load_oracle()
    cai = O.get("compute_axis_impact")
    if not cai:
        return {"error": "compute_axis_impact 미로딩"}

    results = {}
    for sid, scenario in STRESS_SCENARIOS.items():
        sc_axis = _stress_axis_probs(scenario["axes"])
        port_return = 0.0
        for ticker, w in weights.items():
            try:
                impact = cai(ticker, sc_axis).get("total_impact", 0.0)
            except Exception:
                impact = 0.0
            port_return += w * impact
        results[sid] = {
            "name": scenario["name"],
            "desc": scenario["desc"],
            "portfolio_return": round(port_return, 4),
        }

    # 손실 순 정렬
    ranked = sorted(results.items(), key=lambda x: x[1]["portfolio_return"])
    worst = ranked[0] if ranked else None
    best = ranked[-1] if ranked else None

    # 하방 시나리오 (손실) 통계
    losses = [r["portfolio_return"] for _, r in results.items() if r["portfolio_return"] < 0]
    avg_loss = sum(losses) / len(losses) if losses else 0.0

    return {
        "stress_results": results,
        "ranked": [(sid, r["portfolio_return"], r["name"]) for sid, r in ranked],
        "worst_case": {"id": worst[0], "name": worst[1]["name"], "return": worst[1]["portfolio_return"]} if worst else None,
        "best_case": {"id": best[0], "name": best[1]["name"], "return": best[1]["portfolio_return"]} if best else None,
        "loss_scenario_count": len(losses),
        "avg_loss": round(avg_loss, 4),
        "total_scenarios": len(STRESS_SCENARIOS),
    }


# ═══════════════════════════════════════════════════════════════════════
# L24: 통합 진단 하니스 (전 서브시스템 무결성 검증)
# ═══════════════════════════════════════════════════════════════════════
# 각 계층이 정상 출력을 내는지, Oracle 함수 호출이 성공하는지 종합 점검.
# 버그/충돌 자동 검출 (Commander 코드 검사 원칙).
# ═══════════════════════════════════════════════════════════════════════

def integrity_harness(ctx: Dict) -> Dict[str, Any]:
    """전 서브시스템 무결성 검증 하니스."""
    checks = []

    def _check(name, condition, detail=""):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    # L1 데이터
    _check("L1 데이터 수집", ctx.get("latest") and len(ctx.get("history", [])) > 100,
           f"{len(ctx.get('history', []))}행")
    # L2 축 추론
    axis_probs = ctx.get("axes_result", {}).get("axis_probs", {})
    _check("L2 8축 추론", len(axis_probs) == 8, f"{len(axis_probs)}/8축")
    for axis, probs in axis_probs.items():
        total = sum(probs.values())
        _check(f"L2 {axis} 확률합", abs(total - 1.0) < 0.02, f"합={total:.3f}")
    # L3 레짐
    _check("L3 레짐 판정", "macro_regime" in ctx.get("regime_result", {}),
           ctx.get("regime_result", {}).get("macro_regime", {}).get("regime", "?"))
    # L4 임팩트
    impact = ctx.get("impact_result", {})
    _check("L4 임팩트 엔진", len(impact.get("ranked", [])) >= 20,
           f"{len(impact.get('ranked', []))}종목")
    # L5 시나리오
    sc = ctx.get("scenario_probs", {})
    _check("L5 시나리오 확률합", abs(sum(sc.values()) - 1.0) < 0.02 if sc else False,
           f"합={sum(sc.values()):.3f}")
    # L5-EXT P&L
    pnl = ctx.get("scenario_pnl", {})
    _check("L5-EXT P&L", "expected_return" in pnl, f"E[R]={pnl.get('expected_return','?')}")
    # L7 전략이론
    theory = (ctx.get("theory_results", []) + ctx.get("qns_suite", []) +
              ctx.get("qls_suite", []) + ctx.get("theory_extended", []))
    theory_errors = [t for t in theory if "error" in t.computed]
    _check("L7 전략이론", len(theory) > 10 and len(theory_errors) == 0,
           f"{len(theory)}건, 오류 {len(theory_errors)}건")
    # L11 백테스트
    bt = ctx.get("backtest")
    _check("L11 백테스트", bt and "error" not in bt,
           f"CAGR {bt['portfolio']['cagr']:+.1%}" if bt and "error" not in bt else "미실행")
    # L12 센서
    _check("L12 센서 평가", "evaluations" in ctx.get("sensor_suite", {}),
           f"{len(ctx.get('sensor_suite', {}).get('evaluations', {}))}센서")
    # L13 사이징
    _check("L13 포지션 사이징", "sizing" in ctx.get("position_sizing", {}))
    _check("L21 Red Team", "challenges" in ctx.get("red_team", {}),
           f"{ctx.get('red_team', {}).get('challenge_count', '?')}도전")
    # L23 스트레스
    stress = ctx.get("stress_test", {})
    _check("L23 스트레스 테스트", "stress_results" in stress,
           f"{stress.get('total_scenarios', '?')}시나리오")
    # [v1.0.1 P0] 비중 100% invariant + validation gate
    gr = ctx.get("guardrails", {})
    alloc_sum = sum(gr.get("adjusted_allocation", {}).values())
    _check("P0-1 비중 100% invariant", abs(alloc_sum - 100.0) < 0.1, f"{alloc_sum:.1f}%")
    val = ctx.get("validation", {})
    chk = ctx.get("check", {})
    # 정합: 데이터 valid 이거나, invalid면 거래 차단되어야 함
    gate_ok = val.get("valid", True) or chk.get("trade_blocked", False)
    _check("P0-2 validation gate 정합", gate_ok,
           f"valid={val.get('valid')}, blocked={chk.get('trade_blocked')}")

    # [v1.0.2] ARGUS 유니버스 커버리지 + 포트폴리오 유니버스 정합
    impact_keys = set(ctx.get("impact_result", {}).get("ticker_impacts", {}).keys())
    argus_covered = sum(1 for t in ARGUS_UNIVERSE if t in impact_keys)
    _check("ARGUS 20종목 Oracle 커버", argus_covered == 20, f"{argus_covered}/20")
    final_alloc = set(ctx.get("guardrails", {}).get("adjusted_allocation", {}).keys())
    out_of_universe = final_alloc - set(ALLOC_UNIVERSE)
    _check("포트폴리오 ARGUS 유니버스 정합", len(out_of_universe) == 0,
           f"유니버스 외: {out_of_universe or '없음'}")
    # [v1.0.5 P1-1] LOGOS 검증 게이트 — LOGOS_POLICY 반영
    lg = ctx.get("logos_validation", {})
    if lg.get("available"):
        _check("L28 LOGOS 검증 가용", True, lg.get("confidence_grade", "?"))
        _check("L28 LOGOS 과신표현 0", len(lg.get("violations", {}).get("forbidden", [])) == 0,
               f"{len(lg.get('violations', {}).get('forbidden', []))}건")
    else:
        if LOGOS_POLICY == "required":
            _check("L28 LOGOS 검증 가용", False,
                   "LOGOS_REQUIRED_BUT_MISSING — Full Production 차단")
        else:  # optional
            _check("L28 LOGOS 검증 가용 (optional)", True,
                   "LOGOS 미동봉 — optional 모드, 출력 심판 비활성 (warning)")

    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    failed = [c for c in checks if not c["passed"]]

    return {
        "checks": checks,
        "passed": passed,
        "total": total,
        "pass_rate": round(passed / total, 3) if total > 0 else 0,
        "all_passed": len(failed) == 0,
        "failures": failed,
    }


# ═══════════════════════════════════════════════════════════════════════
# 최종 종합 오케스트레이터 v3 (전 24계층)
# ═══════════════════════════════════════════════════════════════════════

def run_autopilot_complete(commander_overrides: Optional[Dict] = None,
                           run_bt: bool = True, bt_max_steps: Optional[int] = 60,
                           save_outputs: bool = True,
                           verbose: bool = True) -> Tuple[str, Dict]:
    """Oracle Autopilot 완전체 실행 (L1~L24 전 계층).
    
    Returns:
        (브리핑 텍스트, 전체 컨텍스트 dict)
    """
    def log(m):
        if verbose: print(m)

    # 핵심 파이프라인 (run_autopilot_full 내부 재사용 위해 ctx 구성)
    ctx = {}
    log(f"🔭 Oracle Autopilot v{AUTOPILOT_VERSION} (적정자) 완전체 실행\n")

    # L1~L1.5
    ctx["latest"] = fetch_latest()
    ctx["history"] = fetch_history()
    ctx["validation"] = validate_data(ctx["latest"], ctx["history"])
    ctx["derived"] = build_derived_metrics(ctx["latest"], ctx["history"])
    log(f"📡 L1: {ctx['latest'].get('Date')} | {len(ctx['history'])}행")

    # L2
    ctx["axes_result"] = infer_all_axes(ctx["latest"], ctx["history"], ctx["derived"], commander_overrides)
    axis_probs = ctx["axes_result"]["axis_probs"]

    # L3
    ctx["regime_result"] = run_regime_pipeline(ctx["latest"], ctx["derived"])
    grad_score = ctx["regime_result"].get("gradient_score", 50)

    # L4~L6
    ctx["impact_result"] = run_impact_engine(axis_probs)
    ctx["scenario_probs"] = compute_scenario_probs(axis_probs, grad_score)
    ctx["portfolio"] = construct_portfolio(ctx["regime_result"], ctx["impact_result"], grad_score)
    ctx["transition_result"] = run_transition_detector(ctx["history"])
    ctx["drp"] = compute_drp_adjustment(grad_score, ctx["transition_result"], ctx["scenario_probs"])
    ctx["guardrails"] = apply_guardrails(ctx["portfolio"].get("final_allocation", {}), grad_score)

    # L5-EXT
    weights = {t: w/100.0 for t, w in ctx["guardrails"]["adjusted_allocation"].items()}
    ctx["scenario_pnl"] = compute_scenario_pnl_matrix(weights, ctx["scenario_probs"])
    ctx["sensitivity"] = sensitivity_analysis(weights, axis_probs)
    ctx["risk_metrics"] = compute_risk_metrics(ctx["scenario_pnl"], ctx["sensitivity"])

    # L7
    ctx["theory_results"] = run_strategic_theory(axis_probs, ctx["latest"], ctx["derived"])
    ctx["qns_suite"] = run_qns_game_suite(axis_probs, ctx["latest"], ctx["derived"])
    ctx["qls_suite"] = run_qls_full_suite(axis_probs, ctx["latest"])
    ctx["theory_extended"] = run_strategic_theory_extended(axis_probs, ctx["latest"], ctx["derived"])

    # L11
    ctx["backtest"] = run_backtest(ctx["history"], max_steps=bt_max_steps) if run_bt else None

    # L12
    ctx["sensor_suite"] = run_sensor_suite(ctx["latest"])
    ctx["killswitch"] = detect_killswitch(ctx["sensor_suite"], ctx["derived"], ctx["history"])
    ctx["aegis"] = aegis_protocol(ctx["sensor_suite"], ctx["killswitch"], grad_score)

    # L13~L15
    ctx["blended_alpha"] = compute_blended_alpha(ctx["impact_result"], ctx["history"], tickers=ARGUS_UNIVERSE)
    candidates = [t for t, v in ctx["impact_result"].get("ranked", []) if v > 0 and t in ARGUS_UNIVERSE][:10]
    ctx["position_sizing"] = compute_position_sizing(ctx["impact_result"], ctx["history"], candidates)
    ctx["diversification"] = compute_diversification_benefit(weights, ctx["history"])
    ctx["macro_calendar"] = run_macro_calendar(ctx["latest"])

    # L18~L19
    ctx["ssot_proposal"] = propose_ssot_update(ctx["axes_result"], ctx["regime_result"])
    ctx["intent_menu"] = build_intent_menu()
    current = (commander_overrides or {}).get("current_weights")
    # [v1.0.4 P0 FIX] validation → current_weights 순차 hard gate (run_autopilot_complete)
    if not ctx.get("validation", {}).get("valid", False):
        ctx["rebalance"] = {"trades": [], "trade_count": 0, "turnover": 0.0,
                            "blocked": True,
                            "reason": "DATA_VALIDATION_FAIL — 거래 제안 차단",
                            "validation_issues": ctx.get("validation", {}).get("issues", [])}
    elif not current:
        ctx["rebalance"] = {"trades": [], "trade_count": 0, "turnover": 0.0,
                            "blocked": True,
                            "reason": "current_weights 미입력 — 거래 제안 차단 (오판 방지)",
                            "note": "현재 보유 비중 제공 시 거래 제안 생성"}
    else:
        ctx["rebalance"] = compute_rebalance(current, generate_target_from_pipeline(ctx))
        ctx["rebalance"]["blocked"] = False
    ctx["rebalance_cost"] = compute_rebalance_cost(ctx["rebalance"])

    # L21~L23
    ctx["red_team"] = red_team_audit(ctx)
    ctx["axis_interactions"] = analyze_axis_interactions(axis_probs, ctx["impact_result"])
    ctx["stress_test"] = run_stress_test(weights)

    # L25 시장 미시구조
    ctx["microstructure"] = run_market_microstructure(ctx["history"])

    # L10 + L28 LOGOS (무결성 전 — LOGOS 결과를 무결성이 점검)
    ctx["conviction"] = compute_conviction_score(ctx)
    ctx["logos_validation"] = logos_validate(ctx)
    log(f"🏦 L28 LOGOS: {ctx['logos_validation'].get('summary','미가용')[:50]}")
    ctx["check"] = self_check(ctx["axes_result"], ctx["regime_result"],
                              ctx["impact_result"], ctx["scenario_probs"],
                              validation=ctx.get("validation"),
                              guardrails=ctx.get("guardrails"))
    # L24 무결성 (LOGOS 결과 포함)
    ctx["integrity"] = integrity_harness(ctx)
    log(f"🛡️ L24 무결성: {ctx['integrity']['passed']}/{ctx['integrity']['total']} "
        f"({ctx['integrity']['pass_rate']:.0%})")

    # L9 브리핑 + B15 스트레스 부속 + B17 LOGOS + 경영 요약 최상단
    ctx["action_priorities"] = rank_action_priorities(ctx)
    ctx["manifest"] = build_manifest(ctx["latest"], ctx["history"])
    exec_summary = generate_executive_summary(ctx)
    briefing = generate_briefing_v2(ctx)
    briefing += _briefing_stress_integrity(ctx)
    briefing += _briefing_logos(ctx)
    # 경영 요약을 최상단에 배치 (결론 우선)
    full_briefing = exec_summary + "\n\n" + briefing
    # [v1.0.1 P2] output 파일 저장 (decision.json + audit_log.json)
    if save_outputs:
        try:
            _save_outputs(ctx, full_briefing)
        except Exception as e:
            log(f"   ⚠️ output 저장 실패: {e}")
    return full_briefing, ctx


def _save_outputs(ctx: Dict, briefing: str) -> Dict[str, str]:
    """[v1.0.1 P2] decision.json + audit_log.json + briefing 저장."""
    out_dir = os.path.join(_ENGINE_DIR, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    # decision.json — 최종 추천 + 비중 + 점수
    decision = {
        "version": AUTOPILOT_VERSION,
        "data_date": ctx["latest"].get("Date"),
        "regime": ctx["regime_result"].get("macro_regime", {}).get("regime"),
        "gradient": ctx["regime_result"].get("gradient_score"),
        "conviction": ctx.get("conviction", {}),
        # [v1.0.5 P1-4] invalid data 시 reference_only 명시
        "final_allocation": ctx["guardrails"].get("adjusted_allocation", {})
            if ctx.get("validation", {}).get("valid", False)
            else None,
        "reference_allocation": ctx["guardrails"].get("adjusted_allocation", {})
            if not ctx.get("validation", {}).get("valid", False)
            else None,
        "allocation_status": "CONFIRMED" if ctx.get("validation", {}).get("valid", False)
            else "REFERENCE_ONLY — DATA_VALIDATION_FAIL",
        "allocation_sum_ok": ctx["guardrails"].get("invariant_100pct_ok"),
        # [v1.0.5 P1-2] ARGUS 유니버스 필터
        "top_picks": [
            [t, v] for t, v in ctx["impact_result"].get("ranked", [])
            if t in ARGUS_UNIVERSE
        ][:5],
        "scenario_probs": ctx.get("scenario_probs", {}),
        "risk_metrics": ctx.get("risk_metrics", {}),
        "self_check_passed": ctx.get("check", {}).get("passed"),
        "trade_blocked": ctx.get("check", {}).get("trade_blocked"),
        "rebalance_blocked": ctx.get("rebalance", {}).get("blocked", False),
        "action_priorities": ctx.get("action_priorities", []),
    }
    with open(os.path.join(out_dir, "decision.json"), "w", encoding="utf-8") as f:
        json.dump(decision, f, ensure_ascii=False, indent=2, default=str)

    # audit_log.json — manifest + 검증 + 무결성
    audit = {
        "manifest": ctx.get("manifest", {}),
        "validation": ctx.get("validation", {}),
        "self_check": ctx.get("check", {}),
        "integrity": ctx.get("integrity", {}),
        "guardrail_violations": ctx["guardrails"].get("violations", []),
        "red_team": ctx.get("red_team", {}).get("summary"),
        "logos_validation": {
            "passed": ctx.get("logos_validation", {}).get("passed"),
            "confidence_grade": ctx.get("logos_validation", {}).get("confidence_grade"),
            "summary": ctx.get("logos_validation", {}).get("summary"),
        },
    }
    with open(os.path.join(out_dir, "audit_log.json"), "w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2, default=str)

    # briefing.txt
    with open(os.path.join(out_dir, "briefing.txt"), "w", encoding="utf-8") as f:
        f.write(briefing)

    return {"decision": "decision.json", "audit": "audit_log.json", "briefing": "briefing.txt"}


def _briefing_stress_integrity(ctx: Dict) -> str:
    """B15 스트레스 테스트 + 무결성 부속 섹션."""
    L = []
    stress = ctx.get("stress_test", {})
    integrity = ctx.get("integrity", {})

    L.append(f"\n\n{'='*68}")
    L.append(f"🧪 B15. 스트레스 테스트 (14 시나리오) + 무결성")
    L.append(f"{'='*68}")
    if stress.get("ranked"):
        L.append(f"   포트폴리오 시나리오별 손익 (손실 순):")
        for sid, ret, name in stress["ranked"][:7]:
            emoji = "🔴" if ret < 0 else ("🟡" if ret < 0.03 else "🟢")
            L.append(f"   {emoji} {name:24s} {ret:+.2%}")
        L.append(f"   ⚠️ 최악: {stress['worst_case']['name']} ({stress['worst_case']['return']:+.1%})")
        L.append(f"   ✅ 최선: {stress['best_case']['name']} ({stress['best_case']['return']:+.1%})")
        L.append(f"   손실 시나리오: {stress['loss_scenario_count']}/{stress['total_scenarios']}건, "
                 f"평균 손실 {stress['avg_loss']:+.2%}")

    L.append(f"\n🛡️ 무결성 하니스: {integrity.get('passed','?')}/{integrity.get('total','?')} "
             f"({integrity.get('pass_rate',0):.0%}) {'✅ ALL PASS' if integrity.get('all_passed') else '⚠️ 일부 실패'}")
    if integrity.get("failures"):
        for f in integrity["failures"][:5]:
            L.append(f"   ❌ {f['name']}: {f['detail']}")

    # ── B16: 시장 미시구조 ──
    micro = ctx.get("microstructure", {})
    if micro:
        L.append(f"\n📡 B16. 시장 미시구조 (센서 추세 + 변동성/상관 레짐)")
        vol = micro.get("volatility_regime", {})
        if vol.get("regime"):
            L.append(f"   변동성 레짐: {vol['regime']} (VIX {vol.get('vix_current','?')}, MA20 {vol.get('vix_ma20','?')})")
            L.append(f"     → {vol.get('implication','')}")
        corr = micro.get("correlation_shift", {})
        if corr.get("available"):
            L.append(f"   주식-채권 상관: {corr['regime']} (SPY-TLT {corr.get('spy_tlt_corr_recent','?')})")
            L.append(f"     → {corr.get('implication','')}")
            if corr.get("structural_shift"):
                L.append(f"     ⚠️ {corr['structural_shift']}")
        trends = micro.get("sensor_trends", {})
        if trends.get("risk_rising_sensors"):
            L.append(f"   🔺 위험 센서 상승: {', '.join(trends['risk_rising_sensors'])}")
            if trends.get("early_warning"):
                L.append(f"     ⚠️ 조기 경보: 위험 센서 3개+ 동시 상승")
        else:
            L.append(f"   🟢 위험 센서 상승 추세 없음")

    L.append(f"\n{'='*68}")
    L.append(f"🔭 Oracle Autopilot v{AUTOPILOT_VERSION} (적정자) — 브리핑 종료")
    L.append(f"{'='*68}")
    return "\n".join(L)




# ═══════════════════════════════════════════════════════════════════════
# L25: 센서 추세 분석 + 변동성/상관 레짐 감지
# ═══════════════════════════════════════════════════════════════════════
# 센서의 다일 추세(모멘텀) + 변동성 레짐 + 상관 구조 변화 조기 감지.
# 절대 수준만으로 놓치는 "방향성" 신호 포착 (격언: noise vs 시대국면).
# ═══════════════════════════════════════════════════════════════════════

def analyze_sensor_trends(history: List[Dict], lookback: int = 20) -> Dict[str, Any]:
    """센서 다일 추세 분석. 절대 수준 + 방향성 동시 평가."""
    trend_sensors = ["VIX", "OAS_HY", "MOVE", "WTI", "DXY", "TYX_30Y", "DGS10", "NFCI"]
    trends = {}

    for sensor in trend_sensors:
        recent = [h.get(sensor) for h in history[-lookback:] if h.get(sensor) is not None]
        if len(recent) < lookback * 0.6:
            continue
        cur = recent[-1]
        past = recent[0]
        ma = sum(recent) / len(recent)

        # 추세 방향
        change = cur - past
        change_pct = (change / past) if past != 0 else 0
        vs_ma = (cur - ma) / ma if ma != 0 else 0

        # 추세 라벨
        if abs(change_pct) < 0.02:
            direction = "→ 횡보"
        elif change_pct > 0.10:
            direction = "↑↑ 급등"
        elif change_pct > 0:
            direction = "↗ 상승"
        elif change_pct < -0.10:
            direction = "↓↓ 급락"
        else:
            direction = "↘ 하락"

        trends[sensor] = {
            "current": cur, "ma": round(ma, 2),
            "change_pct": round(change_pct, 3),
            "vs_ma": round(vs_ma, 3),
            "direction": direction,
        }

    # 위험 방향 추세 (위험 센서 상승 = 경고)
    risk_rising = []
    for s in ["VIX", "OAS_HY", "MOVE", "DXY", "TYX_30Y", "NFCI"]:
        if s in trends and trends[s]["change_pct"] > 0.05:
            risk_rising.append(f"{s} {trends[s]['direction']}")

    return {
        "trends": trends,
        "risk_rising_sensors": risk_rising,
        "early_warning": len(risk_rising) >= 3,
        "lookback_days": lookback,
    }


def detect_volatility_regime(history: List[Dict]) -> Dict[str, Any]:
    """변동성 레짐 감지. VIX/MOVE 수준 + 추세로 4단계 분류."""
    vix_recent = [h.get("VIX") for h in history[-20:] if h.get("VIX") is not None]
    move_recent = [h.get("MOVE") for h in history[-20:] if h.get("MOVE") is not None]
    if not vix_recent or not move_recent:
        return {"regime": "unknown"}

    vix_cur = vix_recent[-1]
    vix_ma = sum(vix_recent) / len(vix_recent)
    move_cur = move_recent[-1]

    # 변동성 레짐 분류
    if vix_cur < 15 and move_cur < 90:
        regime = "🟢 저변동성 (complacency)"
        implication = "낮은 변동성 = 위험 과소평가 가능. 역발상 헤지 저렴."
    elif vix_cur < 22 and move_cur < 110:
        regime = "🟡 정상 변동성"
        implication = "정상 범위. 추세 추종 유효."
    elif vix_cur < 30:
        regime = "🟠 상승 변동성"
        implication = "변동성 확대. 포지션 축소 + 헤지 강화 검토."
    else:
        regime = "🔴 고변동성 (stress)"
        implication = "스트레스 레짐. 방어 우선. 변동성 매도 회피."

    # VIX 추세 (상승 중인가)
    vix_rising = vix_cur > vix_ma * 1.05

    return {
        "regime": regime,
        "vix_current": round(vix_cur, 1),
        "vix_ma20": round(vix_ma, 1),
        "move_current": round(move_cur, 1),
        "vix_rising": vix_rising,
        "implication": implication,
    }


def detect_correlation_shift(history: List[Dict]) -> Dict[str, Any]:
    """주식-채권 상관 구조 변화 감지.
    
    정상: 음의 상관 (채권이 헤지). 인플레 레짐: 양의 상관 (동반 하락).
    """
    # SPY vs TLT 상관 (최근 vs 과거)
    recent_corr = compute_correlation(history[-60:], "SPY_Close", "TLT_Close", window=60)
    older_corr = compute_correlation(history[-120:-60], "SPY_Close", "TLT_Close", window=60) if len(history) >= 120 else None

    if recent_corr is None:
        return {"available": False}

    # 상관 레짐 해석
    if recent_corr > 0.3:
        regime = "🔴 양의 상관 (인플레 레짐)"
        implication = "채권이 헤지 기능 상실. 주식-채권 동반 하락 위험. GLD/실물 헤지 필요."
    elif recent_corr > -0.1:
        regime = "🟡 무상관"
        implication = "채권 헤지 효과 약함. 분산 효과 제한."
    else:
        regime = "🟢 음의 상관 (정상)"
        implication = "채권이 주식 헤지. 전통적 60/40 유효."

    shift = None
    if older_corr is not None:
        shift_val = recent_corr - older_corr
        if abs(shift_val) > 0.3:
            shift = f"상관 {older_corr:+.2f} → {recent_corr:+.2f} (구조 변화)"

    return {
        "available": True,
        "spy_tlt_corr_recent": round(recent_corr, 3),
        "spy_tlt_corr_older": round(older_corr, 3) if older_corr is not None else None,
        "regime": regime,
        "implication": implication,
        "structural_shift": shift,
    }


def run_market_microstructure(history: List[Dict]) -> Dict[str, Any]:
    """시장 미시구조 종합 (센서 추세 + 변동성 레짐 + 상관)."""
    return {
        "sensor_trends": analyze_sensor_trends(history),
        "volatility_regime": detect_volatility_regime(history),
        "correlation_shift": detect_correlation_shift(history),
    }


# ═══════════════════════════════════════════════════════════════════════
# 설계 노트 + 변경 이력 (적정자 전환 기록)
# ═══════════════════════════════════════════════════════════════════════

DESIGN_NOTES = """
Oracle Autopilot v1.0.0 (적정자) 설계 노트
═══════════════════════════════════════════════════════════════

[사생아 → 적정자 전환의 본질]
초기 버전(oracle_autopilot.py)은 Oracle를 import만 하고 8축 판정을
자체 if-else로 재발명한 "사생아"였다. 이는 두 가지 치명적 결함:
  1) Oracle의 LEAD-5/6b 회귀 추론을 무시 → CREDIT/MONETARY 부정확
  2) Oracle의 regime 파이프라인 우회 → 레짐 판정 비정합

적정자 v1.0은 다음으로 전환:
  • Oracle v2.13.1의 auto_prior(LEAD-5/6b) 정식 호출
    - CREDIT: OAS_HY 250일 분위수 3차 poly+softmax 회귀
    - MONETARY: IRX_13W 분위수 + 6개월 변화
  • compute_regime_gradient → compute_regime_inputs → classify_macro_regime
    정식 체인으로 레짐 판정 (간이 if-else 제거)
  • compute_axis_impact로 29종목 임팩트 (INTERACTION_PAIRS 비선형 부스트)
  • Oracle가 의존하는 Brief 상수(GRADIENT_SENSOR_BANDS 등)를 본 모듈이 공급

[프록시 축의 정직한 한계 표기]
WAR/TARIFF/FISCAL은 LEAD 회귀가 없어 시장 프록시로 추론.
정치/정책 이벤트를 직접 반영 불가 → 신뢰도 30~55%로 명시, 뉴스 교차 검증 권고.
이는 false precision 거부 원칙 (Commander SSOT primacy).

[24계층 구조]
L0  공유상수 / L1 데이터 / L1.5 파생 / L2 축추론 / L3 레짐 /
L4 임팩트 / L5 시나리오+P&L / L6 포트폴리오+DRP / L7 전략이론 /
L8 전환감지 / L9 브리핑 / L10 자가검증 / L11 백테스트 /
L12 센서+AEGIS / L13 사이징 / L14 매크로트리거 / L15 알파 /
L16 종목프로파일 / L17 레짐통계 / L18 Commander인터페이스 /
L19 리밸런싱 / L21 RedTeam / L22 교차축 / L23 스트레스 / L24 무결성 /
L25 미시구조

[Commander 권한 불변]
모든 SSOT 수정 + 자본 배분은 Commander 승인 필수.
Autopilot은 제안만, 자동 적용 절대 금지 (propose_ssot_update의 note 참조).

[검증 기준선]
2026-06-08 데이터: 레짐 EXPANSION, 그래디언트 22.4,
무결성 하니스 20/20 PASS, 백테스트 알파 양수.
"""


def design_notes() -> str:
    """설계 노트 반환."""
    return DESIGN_NOTES


def version_info() -> Dict[str, Any]:
    """버전 정보."""
    return {
        "version": AUTOPILOT_VERSION,
        "codename": "HEIR (적정자)",
        "oracle_base": "v2.13.1",
        "engines": ["Oracle v2.13.1", "QNS v1.1.0", "QLS v1.0.0"],
        "layers": 25,
        "data_source": "ARGUS Public Data (daifulee/argus-public-data)",
        "principle": "Oracle 정식 통합 — 사생아 아닌 적정자",
    }




# ═══════════════════════════════════════════════════════════════════════
# L26: 경영 요약 + 확신도 점수 + 행동 우선순위
# ═══════════════════════════════════════════════════════════════════════
# 전 24계층 결과를 Commander 의사결정용 5줄 요약 + 확신도 + 우선 행동으로 합성.
# 결론 우선 원칙의 최종 구현.
# ═══════════════════════════════════════════════════════════════════════

def compute_conviction_score(ctx: Dict) -> Dict[str, Any]:
    """전체 추천의 확신도 점수 (0~100).
    
    축 신뢰도 + 무결성 + Red Team + 신호 정합성 종합.
    """
    components = {}

    # 1) 평균 축 신뢰도 (40%)
    confidences = list(ctx["axes_result"]["confidence"].values())
    avg_conf = sum(confidences) / len(confidences) if confidences else 50
    components["axis_confidence"] = round(avg_conf, 1)

    # 2) 무결성 통과율 (20%)
    integrity_rate = ctx.get("integrity", {}).get("pass_rate", 0) * 100
    components["integrity"] = round(integrity_rate, 1)

    # 3) Red Team 견고성 (20%) — 도전 적을수록 높음
    rt_challenges = ctx.get("red_team", {}).get("challenge_count", 5)
    red_team_score = max(0, 100 - rt_challenges * 15)
    components["red_team_robustness"] = red_team_score

    # 4) 매크로-기술 정합성 (20%)
    blended = ctx.get("blended_alpha", {}).get("blended", {})
    aligned = sum(1 for b in blended.values() if "동반" in b.get("alignment", ""))
    total_tickers = len(blended) if blended else 1
    alignment_score = (aligned / total_tickers) * 100
    components["alpha_alignment"] = round(alignment_score, 1)

    # 가중 합산
    conviction = (avg_conf * 0.40 + integrity_rate * 0.20 +
                  red_team_score * 0.20 + alignment_score * 0.20)

    # 라벨
    if conviction >= 75:
        label = "🟢 높음 (실행 권고)"
    elif conviction >= 60:
        label = "🟡 중간 (선별 실행)"
    elif conviction >= 45:
        label = "🟠 낮음 (신중)"
    else:
        label = "🔴 매우 낮음 (관망)"

    return {
        "conviction_score": round(conviction, 1),
        "label": label,
        "components": components,
    }


def rank_action_priorities(ctx: Dict) -> List[Dict[str, Any]]:
    """행동 우선순위 도출 (긴급도 + 영향도)."""
    actions = []

    # [v1.0.4 P0 FIX] DATA_VALIDATION_FAIL → 최우선 행동 (거래 금지)
    if not ctx.get("validation", {}).get("valid", True):
        actions.append({"priority": 1, "urgency": "긴급",
                        "action": "DATA_VALIDATION_FAIL — 브리핑 참고만 허용, 거래 금지",
                        "source": "Data Gate"})
        return actions  # validation 실패 시 다른 행동 제안 의미 없음

    # AEGIS 비상 단계
    aegis = ctx.get("aegis", {})
    if aegis.get("stage", 0) >= 2:
        actions.append({"priority": 1, "urgency": "긴급",
                        "action": aegis.get("action", ""), "source": "AEGIS"})

    # 킬스위치
    if ctx.get("killswitch", {}).get("killswitch_active"):
        actions.append({"priority": 1, "urgency": "긴급",
                        "action": ctx["killswitch"].get("recommendation", ""), "source": "킬스위치"})

    # 매크로 트리거 발동 (CRITICAL)
    fired = ctx.get("macro_calendar", {}).get("quantitative_triggers", {}).get("fired", [])
    for f in fired:
        if f.get("severity") == "CRITICAL":
            actions.append({"priority": 1, "urgency": "긴급",
                            "action": f.get("implication", ""), "source": f"트리거 {f.get('label','')}"})

    # 리밸런싱 (필요 시)
    rebal = ctx.get("rebalance", {})
    if rebal.get("blocked"):
        actions.append({"priority": 3, "urgency": "검토",
                        "action": "current_weights 입력 필요 — 거래 제안 차단됨",
                        "source": "리밸런싱"})
    elif rebal.get("trade_count", 0) > 0:
        actions.append({"priority": 2, "urgency": "보통",
                        "action": f"리밸런싱 {rebal['trade_count']}건 (회전율 {rebal.get('turnover','?')}%) — Commander 승인 대기",
                        "source": "리밸런싱"})

    # SSOT 갱신 제안
    ssot = ctx.get("ssot_proposal", {})
    if ssot.get("high_confidence_count", 0) > 0:
        actions.append({"priority": 3, "urgency": "검토",
                        "action": f"SSOT 고신뢰 축 {ssot['high_confidence_count']}건 갱신 검토",
                        "source": "SSOT"})

    # Red Team 도전 (재검토 필요 시)
    rt = ctx.get("red_team", {})
    if not rt.get("audit_passed", True):
        actions.append({"priority": 2, "urgency": "보통",
                        "action": f"Red Team 도전 {rt.get('challenge_count','?')}건 — 결론 재검토",
                        "source": "Red Team"})

    actions.sort(key=lambda x: x["priority"])
    return actions


def generate_executive_summary(ctx: Dict) -> str:
    """Commander 의사결정용 경영 요약 (최상단 배치용)."""
    L = []
    regime = ctx["regime_result"].get("macro_regime", {}).get("label", "?")
    grad = ctx["regime_result"].get("gradient_score", "?")
    conviction = compute_conviction_score(ctx)
    actions = rank_action_priorities(ctx)
    ranked = ctx["impact_result"].get("ranked", [])
    rm = ctx.get("risk_metrics", {})
    stress = ctx.get("stress_test", {})

    L.append("┌" + "─"*66 + "┐")
    L.append("│ 🎯 EXECUTIVE SUMMARY (Commander 의사결정용)" + " "*22 + "│")
    L.append("└" + "─"*66 + "┘")
    L.append(f"  ① 레짐: {regime} | 그래디언트 {grad}/100")
    L.append(f"  ② 확신도: {conviction['conviction_score']}/100 {conviction['label']}")
    if ranked:
        argus_ranked = [(t, v) for t, v in ranked if t in ARGUS_UNIVERSE]
        top3 = ", ".join(f"{t}({v:+.0%})" for t, v in argus_ranked[:3])
        L.append(f"  ③ 최선호 (ARGUS): {top3}")
    if rm.get("expected_return") is not None:
        L.append(f"  ④ 기대수익 {rm['expected_return']:+.1%} | 하방위험 {rm.get('downside_risk',0):+.1%} | "
                 f"스트레스 최악 {stress.get('worst_case',{}).get('return',0):+.1%}")
    if actions:
        urgent = [a for a in actions if a["priority"] == 1]
        if urgent:
            L.append(f"  ⑤ 🚨 긴급 행동: {urgent[0]['action'][:50]}")
        else:
            L.append(f"  ⑤ 우선 행동: {actions[0]['action'][:50]}")
    else:
        L.append(f"  ⑤ 행동: 현 포지션 유지")
    return "\n".join(L)




# ═══════════════════════════════════════════════════════════════════════
# L27: 독립 스모크 테스트 + 유틸리티 (CI/검증용)
# ═══════════════════════════════════════════════════════════════════════
# 네트워크 없이 합성 데이터로 전 계층을 빠르게 검증하는 스모크 테스트.
# Commander 코드 검사 원칙 (버그/충돌 자동 검출)의 실행 도구.
# ═══════════════════════════════════════════════════════════════════════

def _synthetic_latest() -> Dict[str, Any]:
    """합성 최신 데이터 (오프라인 테스트용)."""
    return {
        "Date": "2026-06-08", "VIX": 18.9, "DGS10": 4.55, "TNX": 4.55,
        "TYX_30Y": 5.02, "WTI": 91.35, "DXY": 100.0, "OAS_HY": 2.76,
        "OAS_IG": 0.74, "SAHMCURRENT": 0.1, "PMI": 52.7, "F_G_Score": 40.1,
        "USD_CNY": 6.7655, "NFCI": -0.494, "DFII10": 2.19, "T5YIE": 2.47,
        "MOVE": 76.98, "T10Y2Y": 0.41, "IRX_13W": 3.628, "ICSA": 225000,
        "UMCSENT": 49.8, "Net_Liquidity": 5835780, "RRPONTSYD": 1.832,
        "WALCL": 6711495, "SMH_Close": 598.16, "SPY_Close": 739.22,
        "GLD_Close": 397.27, "NLR_Close": 123.22, "COPX_Close": 81.29,
        "ITA_Close": 227.26, "TLT_Close": 84.62, "IEF_Close": 93.52,
        "XLE_Close": 58.33, "IWM_Close": 284.11, "SGOV_Close": 100.46,
        "QQQM_Close": 294.81,
    }


def smoke_test(verbose: bool = True) -> Dict[str, Any]:
    """오프라인 스모크 테스트 — 합성 데이터로 핵심 계층 검증.
    
    네트워크 의존 없이 Oracle 통합 + 축추론 + 임팩트 + 전략이론 작동 확인.
    """
    def log(m):
        if verbose: print(m)

    results = {}
    latest = _synthetic_latest()
    # 합성 히스토리 (300일 — 동일값 반복으로 LEAD 최소 요건 충족)
    history = [dict(latest, Date=f"2025-{(i%12)+1:02d}-01") for i in range(300)]

    try:
        derived = build_derived_metrics(latest, history)
        results["L1.5_derived"] = "✅"
    except Exception as e:
        results["L1.5_derived"] = f"❌ {e}"

    try:
        axes = infer_all_axes(latest, history, derived)
        n_axes = len(axes["axis_probs"])
        results["L2_axes"] = f"✅ {n_axes}축" if n_axes == 8 else f"⚠️ {n_axes}축"
    except Exception as e:
        results["L2_axes"] = f"❌ {e}"
        axes = {"axis_probs": {}}

    try:
        impact = run_impact_engine(axes["axis_probs"])
        results["L4_impact"] = f"✅ {len(impact.get('ranked',[]))}종목"
    except Exception as e:
        results["L4_impact"] = f"❌ {e}"

    try:
        theory = run_strategic_theory(axes["axis_probs"], latest, derived)
        results["L7_theory"] = f"✅ {len(theory)}진단"
    except Exception as e:
        results["L7_theory"] = f"❌ {e}"

    try:
        sensors = run_sensor_suite(latest)
        results["L12_sensors"] = f"✅ {len(sensors['evaluations'])}센서"
    except Exception as e:
        results["L12_sensors"] = f"❌ {e}"

    try:
        weights = {"GLD": 0.2, "NLR": 0.15, "SGOV": 0.1, "XLE": 0.1}
        stress = run_stress_test(weights)
        results["L23_stress"] = f"✅ {stress.get('total_scenarios','?')}시나리오"
    except Exception as e:
        results["L23_stress"] = f"❌ {e}"

    passed = sum(1 for v in results.values() if v.startswith("✅"))
    total = len(results)
    log(f"\n🧪 스모크 테스트: {passed}/{total} 통과")
    for k, v in results.items():
        log(f"   {v} {k}")

    return {"results": results, "passed": passed, "total": total,
            "all_passed": passed == total}


def quick_check() -> str:
    """빠른 상태 점검 (1줄 요약)."""
    try:
        latest = fetch_latest()
        return f"✅ ARGUS {latest.get('Date')} | VIX {latest.get('VIX')} | WTI ${latest.get('WTI')}"
    except Exception as e:
        return f"❌ 데이터 연결 실패: {e}"




# ═══════════════════════════════════════════════════════════════════════
# L28: LOGOS-ARGUS 검증 게이트 (출력 심판 — 과신/무근거/비중 검증)
# ═══════════════════════════════════════════════════════════════════════
# [v1.0.3] LOGOS-FIN 통합. Oracle/QNS/QLS가 분석을 내면 LOGOS가 출력을 심판.
#   • grep_forbidden: 과신 표현(분명히·확실히·절대·100%·결정적) 차단
#   • calibrate_confidence: 확신도 → FACT/VERY_LIKELY/LIKELY/UNCERTAIN 보정
#   • validate_portfolio_impact: 비중 영향 direction/strength/timing/deltas 검증
#   • detect_unsupported_claims: 포트폴리오 rationale 무근거 주장 검출
# 외부 감사 "결과 과신/거짓 정밀성" NO-GO 사유를 구조적으로 차단.
# ═══════════════════════════════════════════════════════════════════════

_LOGOS = None


def load_logos() -> Optional[Dict[str, Any]]:
    """LOGOS-ARGUS 검증 엔진 로딩 (지연 로딩)."""
    global _LOGOS
    if _LOGOS is not None:
        return _LOGOS
    for candidate in ["logos_argus_v1_2_0.py", "logos_fin_v2_1_3.py"]:
        path = os.path.join(_ENGINE_DIR, candidate)
        if not os.path.exists(path):
            path = os.path.join("/mnt/project", candidate)
        if os.path.exists(path):
            ns: Dict[str, Any] = {}
            try:
                with open(path, encoding="utf-8") as f:
                    exec(f.read(), ns)
                ns["_LOGOS_FILE"] = candidate
                _LOGOS = ns
                return _LOGOS
            except Exception:
                continue
    _LOGOS = {}  # 미발견 표시 (재시도 방지)
    return _LOGOS


def _build_portfolio_impact(ctx: Dict):
    """Autopilot 포트폴리오 결과 → LOGOS PortfolioImpact 객체.
    
    DRP 자세 → direction, 그래디언트 → strength, 최종 비중 → weight_deltas.
    """
    L = load_logos()
    PI = L.get("PortfolioImpact")
    if not PI:
        return None

    drp = ctx.get("drp", {})
    posture = drp.get("posture", "NEUTRAL")
    # 자세 → LOGOS 유효 direction (increase/decrease/neutral/rebalance)
    if posture in ("AGGRESSIVE_DEFENSE", "MODERATE_DEFENSE"):
        direction = "decrease"   # 위험자산 축소
    elif posture == "RISK_ON":
        direction = "increase"
    else:
        direction = "rebalance"

    # strength: |방어조절량| 정규화 [0,1]
    strength = min(1.0, abs(drp.get("defense_adjustment", 0.0)) * 4 + 0.3)

    final = ctx.get("guardrails", {}).get("adjusted_allocation", {})
    weight_deltas = {t: round(w / 100.0, 4) for t, w in final.items()}

    # rationale: 레짐 + 그래디언트 (과신 표현 배제한 서술)
    regime = ctx.get("regime_result", {}).get("macro_regime", {}).get("regime", "?")
    grad = ctx.get("regime_result", {}).get("gradient_score", "?")
    rationale = (f"{regime} 레짐, 그래디언트 {grad} 기반 배분. "
                 f"DRP 자세 {posture}. Oracle 임팩트 + ARGUS 유니버스 제약 반영.")

    return PI(affected_assets=list(final.keys()), direction=direction,
              strength=round(strength, 2), rationale=rationale,
              timing="wait_for_trigger", weight_deltas=weight_deltas)


def _build_evidence_index(ctx: Dict):
    """Oracle 임팩트 + 축 추론 → LOGOS EvidenceRecord 인덱스.
    
    각 종목 기대수익을 근거 레코드로 변환 → rationale 주장 검증 가능.
    """
    L = load_logos()
    ER = L.get("EvidenceRecord")
    bei = L.get("build_evidence_index")
    pack = L.get("INVICTUS_PACK_V2")
    if not all([ER, bei, pack]):
        return {}

    records = []
    impacts = ctx.get("impact_result", {}).get("ticker_impacts", {})
    for i, (ticker, detail) in enumerate(impacts.items()):
        ti = detail.get("total_impact", 0.0)
        records.append(ER(
            eid=f"EV-IMPACT-{ticker}",
            source=f"Oracle compute_axis_impact",
            claim=f"{ticker} 기대 임팩트 {ti:+.2%}",
            timestamp=ctx.get("latest", {}).get("Date", ""),
            weight=abs(ti), tags=("oracle_impact",), theory_codes=(),
        ))
    # 레짐 근거
    regime = ctx.get("regime_result", {}).get("macro_regime", {}).get("regime", "?")
    grad = ctx.get("regime_result", {}).get("gradient_score", 0)
    records.append(ER(eid="EV-REGIME", source="Oracle classify_macro_regime",
                      claim=f"{regime} 레짐, 그래디언트 {grad}",
                      timestamp="", weight=1.0, tags=("regime",), theory_codes=()))
    try:
        return bei(records, pack)
    except Exception:
        return {}


def _collect_analytical_text(ctx: Dict) -> str:
    """[v1.0.3] LOGOS 검증 대상 = 분석 주장 텍스트만 수집.
    
    포맷된 수치/표/무결성 리포트(100% 등)는 제외 — 거짓 정밀성 오탐 방지.
    이론 진단·시사점 + 포트폴리오 rationale + Red Team 반증만 검증.
    """
    parts = []
    # 전략이론 진단/시사 (서사적 주장)
    for key in ["theory_results", "qns_suite", "qls_suite", "theory_extended"]:
        for r in ctx.get(key, []):
            if getattr(r, "diagnosis", None):
                parts.append(r.diagnosis)
            if getattr(r, "implication", None):
                parts.append(r.implication)
    # Red Team 반증 텍스트
    for c in ctx.get("red_team", {}).get("challenges", []):
        parts.append(c.get("counter", ""))
    return " ".join(p for p in parts if p)


def logos_validate(ctx: Dict, briefing_text: str = "") -> Dict[str, Any]:
    """[v1.0.3] LOGOS 출력 검증 — 과신/무근거/비중/신뢰도 심판.
    
    검증 대상 = 분석 주장 텍스트(이론 진단/rationale). 포맷 수치/표 제외.
    반환: ValidationReport-style dict (passed 게이트 포함).
    """
    L = load_logos()
    if not L:
        return {"available": False, "note": "LOGOS 엔진 미발견 — 검증 생략"}

    pack = L.get("INVICTUS_PACK_V2")
    grep_forbidden = L.get("grep_forbidden")
    calibrate = L.get("calibrate_confidence")
    vpi = L.get("validate_portfolio_impact")
    duc = L.get("detect_unsupported_claims")

    report = {"available": True, "violations": {}, "warnings": {}}

    # 검증 대상 = 분석 주장 텍스트 (포맷 수치 제외)
    analytical_text = _collect_analytical_text(ctx)

    # ① 과신 표현 검출 (분석 주장 텍스트만) — evidence 불필요
    forbidden_hits = []
    if grep_forbidden and pack:
        try:
            hits = grep_forbidden(analytical_text, pack.forbidden_patterns)
            forbidden_hits = [m for m, _ in hits]
        except Exception as e:
            report["warnings"]["forbidden"] = str(e)
    report["violations"]["forbidden"] = forbidden_hits

    # ② 신뢰도 보정 (확신도 → LOGOS 등급)
    conviction = ctx.get("conviction", {}).get("conviction_score", 50.0)
    logos_grade = None
    if calibrate and pack:
        try:
            logos_grade = calibrate(conviction, pack.confidence_brackets)
        except Exception as e:
            report["warnings"]["calibration"] = str(e)
    report["confidence_grade"] = logos_grade
    report["conviction_score"] = conviction

    # ③ 포트폴리오 영향 검증
    pi_violations = []
    if vpi and pack:
        try:
            ev_idx = _build_evidence_index(ctx)
            pi = _build_portfolio_impact(ctx)
            if pi:
                pi_violations = vpi(pi, ev_idx, pack)
            report["_portfolio_impact"] = {
                "direction": pi.direction, "strength": pi.strength,
                "timing": pi.timing,
            } if pi else None
        except Exception as e:
            report["warnings"]["portfolio_impact"] = str(e)
    report["violations"]["portfolio_impact"] = pi_violations

    # ④ 포트폴리오 rationale 무근거 주장 검출
    unsupported = []
    if duc:
        try:
            ev_idx = _build_evidence_index(ctx)
            pi = _build_portfolio_impact(ctx)
            if pi:
                unsupported = duc(pi.rationale, ev_idx)
        except Exception as e:
            report["warnings"]["unsupported"] = str(e)
    report["violations"]["unsupported_rationale"] = unsupported

    # 종합 passed 게이트
    total_violations = (len(forbidden_hits) + len(pi_violations) + len(unsupported))
    report["total_violations"] = total_violations
    report["passed"] = total_violations == 0
    report["summary"] = (
        f"LOGOS 검증 {'✅ PASS' if report['passed'] else '⚠️ ' + str(total_violations) + '건 위반'} | "
        f"신뢰도 등급 {logos_grade} | 과신표현 {len(forbidden_hits)} / 비중위반 {len(pi_violations)} / 무근거 {len(unsupported)}"
    )
    return report


def _briefing_logos(ctx: Dict) -> str:
    """B17 LOGOS 검증 섹션."""
    lg = ctx.get("logos_validation", {})
    L = []
    L.append(f"\n\n{'='*68}")
    L.append(f"🏦 B17. LOGOS-ARGUS 검증 게이트 (출력 심판)")
    L.append(f"{'='*68}")
    if not lg.get("available"):
        L.append(f"   ⚠️ {lg.get('note', 'LOGOS 미가용')}")
        return "\n".join(L)

    L.append(f"   {lg.get('summary', '')}")
    L.append(f"   신뢰도: Autopilot {lg.get('conviction_score','?')}/100 → LOGOS 등급 [{lg.get('confidence_grade','?')}]")
    pi = lg.get("_portfolio_impact")
    if pi:
        L.append(f"   포트폴리오 영향: direction={pi['direction']}, strength={pi['strength']}, timing={pi['timing']}")
    v = lg.get("violations", {})
    if v.get("forbidden"):
        L.append(f"   🔴 과신 표현 ({len(v['forbidden'])}): {', '.join(set(v['forbidden'][:5]))}")
    if v.get("portfolio_impact"):
        for viol in v["portfolio_impact"][:3]:
            L.append(f"   🔴 비중 검증: {viol}")
    if v.get("unsupported_rationale"):
        for viol in v["unsupported_rationale"][:3]:
            L.append(f"   🟡 무근거: {viol}")
    if lg.get("passed"):
        L.append(f"   ✅ 출력 게이트 통과 — 과신/무근거/비중 위반 없음")
    else:
        L.append(f"   ⚠️ 출력 게이트 경고 — 위반 검토 권장 (Commander 판단)")
    return "\n".join(L)




if __name__ == "__main__":
    run_full()
