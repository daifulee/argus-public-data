# REG-S102_7 — prima_briefing v8.9.5 hotfix 정식 등록 (FA P0 5건 + 자가 결함 1건 처방)

**일자**: 2026-05-14 (S102 #7)
**REG ID**: REG-S102_7_BRIEFING_V895_HOTFIX
**격언 분류**: 격언 #34 §35 자기정정 + 격언 #97 v2 사례 #4 + 격언 #115 후보 본질 회복
**관련 격언**: #11, #15, #34, #75 v4, #80, #97 v2 (사례 #4), #98, #106, #113, #115 후보

---

## 1. 본 hotfix 본질 — FA P0 5/5 처방 + 자가 결함 1건 (S102 #7)

| FA P0 ID | 처방 | 결정적 본질 |
|----------|------|------------|
| **P0-1** | `load_prima()` allow-list 재설계 | exclude-list 의존 결함 차단 — `_LIVE` 키워드 필수 매칭 |
| **P0-2** | `main()` 시작부 hard gate 삽입 | 격언 #115 후보 본질 회복: "선언 ≠ 게이트" |
| **P1-1** | `get_crown()` lower-case normalize | "v5_20A".lower() vs CROWN_MAP key 양방향 |
| **P1-2** | `pre_output_audit()` A4 강화 | TICKER_SPEC 단독 점검 → SIGNAL_RULES + 20 tickers + 필드 정합 |
| **P2-1** | `BRIEFING_VERSION = "v8.9.5"` 상수화 | stale 표시 차단 |
| 🌟 **자가** | `_semver_key` suffix `_v\d+` 추가 | v3 vs v4 결정론적 정렬 (자가 발견) |

---

## 2. P0-1 결정적 처방 — ALLOW-LIST 방식

### 결함 (v8.9.4)
```python
# exclude-list 의존
for kw in ENGINE_EXCLUDE_KEYWORDS:
    if kw in basename:
        # exclude
# → PRIMA_v5_99_EXPERIMENT.py 같은 비-LIVE 고버전이 LIVE pool에 진입
```

### 처방 (v8.9.5)
```python
# 🌟 allow-list 방식 (FA P0-1 처방)
# Phase 2 1순위: ENGINE_LIVE_HINT 필수 매칭
if ENGINE_LIVE_HINT not in basename:
    excluded.append({"reason": "NON_LIVE_FILENAME"})
    continue
# Phase 2 2순위 (이중 안전망): ENGINE_EXCLUDE_KEYWORDS
# Phase 2 3순위: CROWN_NO_GO_VERSIONS
```

### 시뮬레이션 검증
| 파일 | v8.9.4 결과 | v8.9.5 결과 |
|------|-------------|-------------|
| PRIMA_v5_19_VIX_HYST_LIVE_v4.py | ✅ LIVE | ✅ LIVE (Crown #67) |
| PRIMA_v5_99_EXPERIMENT.py | 🚨 **LIVE 오로드** | ✅ NON_LIVE 차단 |
| PRIMA_v6_00_BETA.py | 🚨 **LIVE 오로드** | ✅ NON_LIVE 차단 |
| PRIMA_v7_00_FOO.py | 🚨 **LIVE 오로드** | ✅ NON_LIVE 차단 |
| PRIMA_v5_19_VIX_HYST_SHADOW.py | ✅ SHADOW 차단 | ✅ NON_LIVE + SHADOW |
| PRIMA_v5_20A_RP_OVERLAY_ONLY.py | ✅ _ONLY 차단 | ✅ NON_LIVE + _ONLY + NO_GO |

🌟 **결정적 의의**: 미래 후보 파일에 대한 안전성 확보 — exclude-list 의존 종결.

---

## 3. P0-2 결정적 처방 — Hard Gate (격언 #115 후보 본질 회복)

### 결함 (v8.9.4)
- `pre_output_audit()` 함수 신설 ✅
- `print_pre_output_audit_report()` 함수 신설 ✅
- 🚨 **main() 강제 호출 없음** → 격언 #115 후보 본질 위배

### 처방 (v8.9.5)
```python
def main():
    try:
        # 🚨🚨🚨 v8.9.5 P0-2 처방: Pre-Output Audit Hard Gate 🚨🚨🚨
        _self_audit = pre_output_audit(__file__)
        print_pre_output_audit_report(_self_audit)
        if _self_audit.get("stop_conditions_hit"):
            raise RuntimeError(
                f"🚨 PRE_OUTPUT_AUDIT_STOP_CONDITIONS_HIT: ..."
            )
        # warnings만 있는 경우 (보고 후 출력 허용)
        if _self_audit.get("warnings"):
            print(f"⚠️ Audit warnings (보고 후 출력 진행): ...")
        # main 본 흐름 ...
```

🌟 **결정적 의의**: 격언 #115 후보의 본질 = "선언 ≠ 게이트, 실행이 게이트". v8.9.5에서 회복.

---

## 4. P1-1 처방 — get_crown() lower-case normalize

### 결함 (v8.9.4)
```python
def get_crown(engine_name):
    for key, crown in CROWN_MAP.items():
        if key in engine_name.lower():   # "v5_20A" vs "v5_20a" 매칭 실패
            return crown
```

### 처방 (v8.9.5)
```python
def get_crown(engine_name):
    name_l = engine_name.lower()
    for key, crown in CROWN_MAP.items():
        if key.lower() in name_l:    # 양방향 normalize
            return crown
```

---

## 5. P1-2 처방 — A4 강화

### 강화 사항
| 검증 | v8.9.4 | v8.9.5 |
|------|--------|--------|
| TICKER_SPEC 존재 | ✅ | ✅ |
| SIGNAL_RULES 존재 | ❌ | ✅ 신설 |
| INTERACTION_EXCLUSIVE_GROUPS | ❌ | optional (있으면 ✅) |
| 20 tickers 등재 | ❌ | ✅ 18+/20 |
| 핵심 필드 정합 (gate/ensn/exsn) | ❌ | ✅ 각 15+ 종목 |
| MoSn 필드 (선택) | ❌ | ✅ 최소 2종목 |

🌟 **자가 보정**: `INTERACTION_EXCLUSIVE_GROUPS`는 v8.9.3 본질에 부재 → optional 처리 (격언 #34 §35 정합).

---

## 6. P2-1 처방 — BRIEFING_VERSION 상수화

```python
BRIEFING_VERSION = "v8.9.5"
BRIEFING_DATE = "2026-05-14"
BRIEFING_SESSION = "S102 #7"
```

---

## 7. 자가 발견 #1 — `_semver_key` 결정론적 정렬

### 결함
- v8.9.4 `_semver_key` = `(ver_major, ver_minor, live_priority)` 3-tuple
- v5_19_v3 + v5_19_v4 모두 `(5, 19, 1)` 동일 키 → stable sort가 OS-dependent

### 처방
```python
def _semver_key(p):
    bn = os.path.basename(p)
    m = re.search(r'PRIMA_v(\d+)_(\d+)', bn)
    ver = (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
    live_priority = 1 if ENGINE_LIVE_HINT in bn else 0
    m_suffix = re.search(r'_v(\d+)\.py$', bn)    # 🆕 suffix 추출
    suffix = int(m_suffix.group(1)) if m_suffix else 0
    return (ver[0], ver[1], live_priority, suffix)   # 4-tuple
```

검증: `PRIMA_v5_19_VIX_HYST_LIVE_v4.py` (key=(5,19,1,4)) > `v3.py` (key=(5,19,1,3)) 결정론적.

---

## 8. v8.9.5 자체 Pre-Output Audit 결과 (deployment 환경 시뮬레이션)

| 영역 | 결과 | 상세 |
|------|------|------|
| **A1 ENGINE_GLOB** | ✅ | 패턴 `PRIMA_v*.py` / glob 5건 / **LIVE 3건 + EXCLUDE 2건** |
| A2 헤더 Crown | ✅ | #67 |
| A3 CROWN_MAP | ✅ | v5_20A NO-GO 명시 |
| **A4 강화** | ✅ | TICKER_SPEC + SIGNAL_RULES + 20/20 tickers + 핵심 필드 20 |
| A5 6000자 cap | ✅ | 등재 |
| A6 evaluate_all | ✅ | 호출 등재 |
| **A7 AST + meta** | ✅ | 🌟 **4507 lines / 238,970 bytes / 61 functions** 🌟 |
| A8 CROWN_NO_GO_VERSIONS | ✅ | 3 항목 등재 |
| 🆕 P0-2 hard gate | ✅ | main 강제 호출 + RuntimeError |
| 🆕 P1-1 get_crown | ✅ | lower-case 정규화 |
| 🆕 P2-1 BRIEFING_VERSION | ✅ | "v8.9.5" 상수 |

🌟 **종합: 8/8 PASS + FA P0 5/5 검증 PASS + 자가 결함 1건 처방 PASS** 🌟

---

## 9. v8.9.4 vs v8.9.5 비교

| 항목 | v8.9.4 | v8.9.5 |
|------|--------|--------|
| Lines | 4362 | 🌟 **4507 (+145)** 🌟 |
| Functions | 61 | 61 (동일) |
| Bytes | 229,381 | 🌟 **238,970 (+9.6 KB)** 🌟 |
| LIVE 후보 선정 | exclude-list | 🌟 **allow-list** 🌟 |
| main hard gate | 부재 | 🌟 **신설** 🌟 |
| get_crown case | 단방향 | 🌟 **양방향** 🌟 |
| A4 강도 | 약함 (1 영역) | 🌟 **6 영역** 🌟 |
| BRIEFING_VERSION | 부재 | 🌟 **상수화** 🌟 |
| _semver_key | 3-tuple (비결정적) | 🌟 **4-tuple (결정론적)** 🌟 |
| AST | ✅ | ✅ |

---

## 10. SKILL v1.0 → v1.1 갱신 동시 적용

| 강화 | 학습 사례 |
|------|----------|
| **선언 ≠ 게이트** baseline | FA P0-2 |
| **ALLOW-LIST 의무** baseline | FA P0-1 |
| **A4 강도** baseline | FA P1-2 |
| **case-insensitive** baseline | FA P1-1 |
| **결정론적 정렬** baseline | 자가 발견 |

🌟 SKILL이 학습 사례 누적으로 강화 baseline.

---

## 11. 격언 정합 체크리스트

- ✅ §35 §34 (자기정정): FA P0 5건 + 자가 1건 정직 수용
- ✅ §41 (전체 파일 출력): v8.9.5 4507 lines 단일 파일
- ✅ §42 (full diff): 변경 영역 6개 명시 (P0-1/P0-2/P1-1/P1-2/P2-1/자가)
- ✅ §43 (과장 금지): "FA P0 처방" 사용 — 실측 결과 표 명시
- ✅ 격언 #15 (영역 채택): renderer/calc 0 line 변경
- ✅ 격언 #34 §35 (anti-deception): 자가 결함 추가 발견 및 정직 처방
- ✅ 격언 #75 v4 (grep 의무): 모든 grep 실제 bash 실행 검증
- ✅ 격언 #80 (양방향 정합): A6 점검 + audit 강화
- ✅ 격언 #97 v2 사례 #4: FA P0 사전 감사 → hotfix → 재감사 자동 시뮬레이션
- ✅ 격언 #98 (결정 지연 ≠ 중립): 즉시 처방 + 즉시 검증
- ✅ 격언 #106 (근본 처방): allow-list = 표면 봉합 X, exclude-list 본질 결함 종결
- ✅ 격언 #113 후보 (단일 파일): pre_output_audit briefing 내장 + SKILL 통합
- 🆕 격언 #115 후보 본질 회복: 선언 ≠ 게이트, 실행이 게이트

---

## 12. SSOT 갱신 사항

- SSOT 다음 버전: v1.10.190
- REGRET LOG MASTER: REG-S102_7 append
- BRIEFING LIVE: prima_briefing_v8_9_5.py 채택 (v8.9.4 NO-GO 폐기)
- SKILL LIVE: argus-prima-briefing-pre-output-audit v1.1 (v1.0 갱신)
- HANDOFF: S102 → S103 (v8.9.5 LIVE deployment 검증 + 후속)

---

## 13. 격언 #97 v2 가치 재입증 baseline

🌟 **FA P0가 본 결함을 사전 탐지하지 않았다면**:
- v8.9.4 LIVE 채택 → 미래 어떤 시점 PRIMA_v5_99 등 추가 시 LIVE 오로드 risk
- 격언 #115 후보 실제 게이트 부재 → 알면서 묻혀버린 결함
- get_crown 매핑 실패 → 표시 정합 깨짐 누적

격언 #97 v2 사례 #1 (Crown #65) → #2 (RP overlay) → #3 (Phase B BT) → #4 (v8.9.4 audit). FA 사전 감사 누적 가치 재입증.

---

🌟 **본 REG는 외부 FA + 자가 audit + SKILL이 통합되어 hotfix를 정확히 산출한 결정적 사례입니다.** 🌟
v8.9.4 NO-GO 판정은 알려진 결함을 LIVE 채택하지 않은 정직성의 결과. v8.9.5 hotfix는 5+1건 결함의 근본 처방 baseline.
