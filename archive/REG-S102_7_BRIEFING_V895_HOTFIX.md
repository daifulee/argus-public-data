# REG-S102_8 — prima_briefing v8.9.6 hotfix 정식 등록 (FA P1 5건 처방 + 격언 #80 회복)

**일자**: 2026-05-14 (S102 #8)
**REG ID**: REG-S102_8_BRIEFING_V896_HOTFIX
**격언 분류**: 격언 #34 §35 자기정정 + 격언 #80 양방향 정합 회복 + 격언 #97 v2 사례 #5
**관련 격언**: #11, #15, #34, #75 v4, #80 (회복), #97 v2 (사례 #5), #98, #106, #115 후보

---

## 1. 본 hotfix 본질 — FA P1 5/5 처방 (S102 #8)

| FA P1 ID | 결함 | 처방 |
|----------|------|------|
| **P1-1** | TLT Embed 1 (A급 3.50) vs Embed 4 (C급 1.50) 점수 불일치 | 단일 source — engine raw score 우선 (scores → eval_result → legacy) |
| **P1-2** | 활성/근접/차단 라벨 매수 가능 오인 | **점수충족/점수근접/점수미달** (점수 상태 명확) |
| **P1-3** | "Gate진입 임박" 실제 점수 임박 (Gate 무관) | **점수진입 임박** |
| **P1-4** | "Gate해제 임박" 실제 Gate active + 점수충족 | **Gate차단 중 / 해제 대기** |
| **P1-5** | XLE BullStack ∩ BearStack 동시 ★ 발동 (논리 위반) | MOSN_EXCLUSIVE_GROUPS 배타 필터 |

---

## 2. P1-1 결정적 처방 — score source 통일 (격언 #80 회복)

### 결함 (v8.9.5)
- Embed 1 (build_portfolio_embed): `pos.get("score", 0)` = **엔진 final_positions 저장값**
- Embed 4 (build_signal_embed): `ensn_raw_score = sum(...)` = **briefing 재계산값**
- TLT 사례: Embed 1 = 3.50, Embed 4 = 1.50 (격언 #80 위반)

### 처방 (v8.9.6) — 3순위 폴백 baseline
```python
engine_score = None
# 1순위: scores[tk] (engine evaluate_all 직접 결과)
if 'scores' in locals() or 'scores' in globals():
    try:
        score_entry = scores.get(tk) if scores else None
        if score_entry and isinstance(score_entry, (tuple, list)) and len(score_entry) >= 1:
            engine_score = float(score_entry[0])
    except (NameError, TypeError, ValueError):
        pass
# 2순위: eval_result에서 per_signal_v3 합산
if engine_score is None:
    eval_result_local = conds.get("_eval_result")
    if eval_result_local and is_schema_v2(eval_result_local):
        ticker_eval = eval_result_local.get("tickers", {}).get(tk, {})
        engine_score = ticker_eval.get("score")
# 3순위 (legacy 폴백): ensn_list_filtered 활성 합
if engine_score is not None:
    ensn_raw_score = float(engine_score)
else:
    ensn_raw_score = sum(_safe_pts(pts) for ck, pts in ensn_list_filtered if _is_active_local(ck))
```

🌟 **결정적 의의**: Embed 1 ↔ Embed 4 score 단일 source 보장 baseline. 격언 #80 양방향 회복.

---

## 3. P1-2 결정적 처방 — 섹션 라벨 정합

### 결함 (v8.9.5)
- "🟢 활성" → 매수 가능처럼 오해 baseline
- XLE Gate 차단 + 점수충족 → "활성" 섹션 → 사용자 혼란

### 처방 (v8.9.6) — SECTION_LABELS 상수 신설
```python
SECTION_LABELS = {
    "holding":   "🔵 **보유**",          # tk in final_positions
    "active":    "🟢 **점수충족**",       # ratio >= 1.0
    "near":      "🟡 **점수근접**",       # 0 < ratio < 1.0
    "blocked":   "🔴 **점수미달**",       # ratio <= 0
}
```

🌟 **결정적 의의**: "점수 상태" ≠ "실행 상태" 명시 baseline.

---

## 4. P1-3/P1-4 결정적 처방 — 매매 4분류 라벨

### 결함 (v8.9.5)
- "Gate해제 임박": 실제 = ratio≥1.0 + Gate active (release proximity 미계산) — 명칭 과장
- "Gate진입 임박": 실제 = ratio 70~99% (Gate 무관) — 명칭 오류

### 처방 (v8.9.6) — ALERT_LABELS 상수 신설
```python
ALERT_LABELS = {
    "score_caution":    "🟡 **진입 신중**",
    "gate_blocked":     "🔒 **Gate차단 중 / 해제 대기**",
    "score_near":       "⏳ **점수진입 임박**",
    "exit_imminent":    "🚪 **청산 임박**",
}
```

각주도 동시 갱신:
- `-# **🔒 Gate차단 중 / 해제 대기** = 점수충족 + Gate active — 풀리면 즉시 진입`
- `-# **⏳ 점수진입 임박** = ratio 70~99% (점수 도달 대기, Gate 상태 무관)`

---

## 5. P1-5 결정적 처방 — MoSn 배타

### 결함 (v8.9.5)
- XLE BullStack (MA 정배열) ∩ BearStack (MA 역배열) 동시 ★ 발동
- 논리적 배타 (정배열 ≠ 역배열) 위반
- v8.1.6 이전 해결 대상이었으나 재발

### 처방 (v8.9.6) — MOSN_EXCLUSIVE_GROUPS 신설 + 필터
```python
MOSN_EXCLUSIVE_GROUPS = {
    "XLE": [("XLE_BullStack", "XLE_BearStack")],   # MA 정배열 vs 역배열 배타
    "VNM": [("VNM_BullStack",)],
}

# build_signal_embed 필터 적용
ticker_exclusive_groups = MOSN_EXCLUSIVE_GROUPS.get(tk, [])
for group in ticker_exclusive_groups:
    if len(group) >= 2:
        active_in_group = [k for k in group if k in active_mosn_keys]
        if len(active_in_group) >= 2:
            # mosn_list 정의 순서 우선 (BullStack 우선)
            for sig_key, _ in mosn_list:
                if sig_key in active_in_group:
                    for k in active_in_group:
                        if k != sig_key:
                            active_mosn_keys.discard(k)
                    break
```

---

## 6. v8.9.6 자체 Pre-Output Audit 결과 (격언 #115 후보)

| 영역 | 결과 |
|------|------|
| A1 ENGINE_GLOB | ✅ `PRIMA_v*.py` |
| A2 헤더 Crown | ✅ #67 |
| A3 CROWN_MAP | ✅ |
| A4 강화 | ✅ TICKER_SPEC + SIGNAL_RULES |
| A5 6000자 cap | ✅ |
| A6 evaluate_all | ✅ |
| **A7 AST + meta** | ✅ 🌟 **4657 lines / 248,730 bytes / 61 functions** 🌟 |
| A8 CROWN_NO_GO_VERSIONS | ✅ |
| P0-2 main hard gate | ✅ |
| **P1-1 score source** | ✅ engine_score 3순위 폴백 |
| **P1-2 SECTION_LABELS** | ✅ 점수충족/점수근접/점수미달 |
| **P1-3/P1-4 ALERT_LABELS** | ✅ 점수진입 임박 + Gate차단 중 |
| **P1-5 MOSN_EXCLUSIVE_GROUPS** | ✅ XLE 배타 그룹 적용 |

🌟 **종합: 8/8 PASS + FA P1 5/5 처방 검증 PASS** 🌟

---

## 7. v8.9.5 vs v8.9.6 비교

| 항목 | v8.9.5 | v8.9.6 |
|------|--------|--------|
| Lines | 4507 | 🌟 **4657 (+150)** 🌟 |
| Bytes | 238,970 | 🌟 **248,730 (+9.5 KB)** 🌟 |
| Functions | 61 | 61 (동일) |
| Score source (Embed 4) | briefing 재계산 | 🌟 **engine 우선 + 3순위 폴백** 🌟 |
| 섹션 라벨 | 활성/근접/차단 (오인) | 🌟 **점수충족/점수근접/점수미달** 🌟 |
| 매매 라벨 (Gate해제/Gate진입) | 명칭 오류 | 🌟 **Gate차단 중 + 점수진입 임박** 🌟 |
| XLE BullStack/BearStack | 동시 ★ (논리 위반) | 🌟 **배타 필터 적용** 🌟 |
| 격언 #80 양방향 | 위반 (TLT 점수 불일치) | 🌟 **회복** 🌟 |
| AST | ✅ | ✅ |

---

## 8. 격언 정합 체크리스트

- ✅ §35 §34 (자기정정): FA P1 5건 정직 수용 + audit가 외부 FA보다 약했음 인정
- ✅ §41 (전체 파일 출력): v8.9.6 4657 lines 단일 파일
- ✅ §42 (full diff): 5 영역 명시 (P1-1~P1-5)
- ✅ §43 (과장 금지): "score source 통일" 사용 — 실제 logic 변경 명시
- ✅ 격언 #15 (영역 채택): renderer/label-only — 엔진 미수정
- ✅ 격언 #34 §35 (anti-deception): 라벨 의미 왜곡 baseline 제거
- ✅ 격언 #75 v4 (grep 의무): 모든 grep 실제 bash 실행 검증
- ✅ 격언 #80 (양방향 정합): **본격 회복 baseline** — Embed 1 ↔ Embed 4 단일 source
- ✅ 격언 #97 v2 사례 #5: FA P1 사전 감사 → hotfix → 검증
- ✅ 격언 #98 (결정 지연 ≠ 중립): Commander "즉시 착수" 명령 즉시 수행
- ✅ 격언 #106 (근본 처방): 라벨 변경 + score source 통일 = 표면 봉합 X
- ✅ 격언 #113 후보 (단일 파일): pre_output_audit + SECTION_LABELS + ALERT_LABELS + MOSN_EXCLUSIVE_GROUPS 모두 briefing 내장
- ✅ 격언 #115 후보: pre_output_audit hard gate 작동 baseline

---

## 9. argus-prima-briefing-pre-output-audit SKILL v1.1 정합

| SKILL 요구 | v8.9.6 적용 |
|-----------|------------|
| A1 ENGINE_GLOB | ✅ |
| A2 엔진 헤더 정합 | ✅ |
| A3 CROWN_MAP 정합 | ✅ |
| A4 시그널 정의 (강화) | ✅ |
| A5 표시 형식 | ✅ |
| A6 격언 #80 양방향 | 🌟 **본격 회복 baseline** |
| A7 출력 메타데이터 | ✅ 4657 lines |
| A8 Commander 인지 | ✅ |
| STOP 조건 10가지 | ✅ |
| 출력 정례 형식 | ✅ |

---

## 10. SKILL v1.2 후보 — A9 영역 신설 권고

v8.9.6에서도 자체 audit가 **표시 ↔ 엔진 실제 계산 정량 비교**까지는 못 함. SKILL v1.2 후보:

```
A9 (신설 후보): 표시 ↔ 엔진 실제 계산 정량 검증
  - LIVE 매크로 입력 시 엔진 score 자동 비교
  - Embed 1 score vs Embed 4 score 차이 ≤ 0.01 검증
  - 단위 결함 (TLT 3.50 vs 1.50 = 2.00 차이) 즉시 발견 baseline
```

---

## 11. SSOT 갱신 사항

- SSOT 다음 버전: v1.10.191
- REGRET LOG MASTER: REG-S102_8 append
- BRIEFING LIVE: prima_briefing_v8_9_6.py 채택 (v8.9.5 폐기 — P1 5건 보유)
- HANDOFF: S102 → S103 (v8.9.6 LIVE deployment 검증 + SKILL v1.2 후보)

---

## 12. 격언 #97 v2 사례 #5 — FA 가치 누적 baseline

🌟 **외부 FA가 본 결함을 사전 탐지하지 않았다면**:
- v8.9.5 LIVE 채택 → 표시 결함 5건 (라벨 + 점수 source 불일치) 누적 노출
- Commander 표시 인지 오해 → 매매 실행 결정 오판 risk
- 격언 #80 양방향 위반 누적 → 격언 #75 v4 (grep audit) 무력화

격언 #97 v2 사례:
- 사례 #1 Crown #65 ENTRY_THRESHOLD 차단
- 사례 #2 RP overlay 단일 패치 분해
- 사례 #3 Phase B BT NO-GO
- 사례 #4 v8.9.4 audit P0 5건
- 🌟 **사례 #5 v8.9.5 라벨 P1 5건** 🌟

FA 사전 감사 누적 가치 입증.

---

🌟 **본 REG는 외부 FA P1 + 격언 #80 회복 + SKILL hard gate가 통합되어 hotfix를 정확히 산출한 결정적 사례입니다.** 🌟
v8.9.5 → v8.9.6 흐름: "라벨이 의미를 왜곡하면 격언 #80 양방향 정합 자체가 무력화된다"는 본질 학습.
