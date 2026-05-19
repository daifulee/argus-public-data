# REG-S102_10 — v8.9.7 FA P0 응답 수신 + v8.9.8 hotfix 계획 (S102 #11)

**일자**: 2026-05-14 (S102 #11)
**REG ID**: REG-S102_10_BRIEFING_V897_FA_P0_RESPONSE
**격언 분류**: 격언 #97 v2 사례 #6 본격 확정 + 격언 #34 §35 자체 audit 한계 입증
**관련 격언**: #34, #75 v4, #80, #97 v2 (사례 #6), #98, #110, #115 후보

---

## 1. 본 REG 본질 — FA P0 NO-GO 응답 수신

### 1.1 흐름
1. S102 #10: 자체 audit 결함 8건 발견 + FA P0 의뢰서 작성
2. Commander → 외부 FA 의뢰서 전달
3. 🌟 **외부 FA P0 응답 수신**: NO-GO 확정 + v8.9.8 hotfix mandatory baseline
4. 본 REG: FA 응답 + v8.9.8 hotfix 계획 정식 등재

### 1.2 FA 응답 핵심 결과
| 영역 | 결과 |
|------|------|
| target | prima_briefing_v8_9_7.py |
| decision | 🔴 **NO-GO** |
| effective_status | v8.9.8 hotfix mandatory |
| FA ID | external-fa-p0-gpt-5-5-thinking |
| 응답일 | 2026-05-14 |

### 1.3 결함 누적 (자체 audit 8건 + FA 추가 3건 = 총 11건)
| 우선 | 자체 audit | FA 추가 | 총 |
|------|----------|--------|-----|
| 🔴 P0 | 2건 | **+1건 (BANNED_PHRASES)** | **3건** |
| 🟠 P1 | 4건 | **+2건 (build_one_glance + send_queue)** | **6건** |
| 🟡 P2 | 2건 | 0건 | 2건 |
| **총** | **8건** | **+3건** | 🚨 **11건** |

---

## 2. FA 추가 발견 결함 3건 (내 자체 audit 한계 baseline)

### 2.1 P0-3 추가: BANNED_PHRASES semantic stale 미검출

**FA 본질**:
- 현재 BANNED_PHRASES: `"WTI>90 즉차단"`, `"WTI>$90 즉차단"`, `"WTI>90즉청산"` 등 baseline
- 실제 stale 문구 (Embed 3): `"WTI > $95 — 전종목 즉시 청산"`, `"WTI > $90 — 일반 종목 즉시 청산"` baseline
- **금칙어가 현재 stale 문구를 못 잡음** baseline

**처방**:
```python
BANNED_PHRASES_SEMANTIC = [
    "전종목 즉시 청산",
    "일반 종목 즉시 청산",
    "모든 종목 신규 진입 차단",
    "일반 18종목 게이트 활성",
    "WTI > $95",
    "WTI > $90",
]
```

🚨 **본질**: AT-7 (stale version)는 버전 문자열만 검출 baseline → AT-7 확장 의무.

---

### 2.2 P1-7 추가: build_one_glance_embed() 미사용 stale 함수

**FA 본질**:
- 현재 main에서 호출 안 됨 baseline
- 그러나 함수 본문에 stale WTI 단독 logic 잔존:
```python
if not np.isnan(wti_v) and wti_v > 90:
    new_buy_line = "**신규매수**: 금지 (전종목 Gate 차단 레짐)"
```
- 후속 버전에서 다시 호출 시 같은 문제 재발 risk baseline

**처방**: 함수 archive 또는 deprecated 표시 또는 Crown #67 state-aware 갱신.

---

### 2.3 P1-8 추가: send_queue 라벨 stale

**FA 본질**:
- v8.9.7 매매 5분류 baseline
- 그러나 `send_queue` 라벨은 `("매매 4분류", [e_alert])` baseline
- Discord 출력 제목 직접 영향은 작지만 로그 stale baseline

**처방**: `("매매 5분류", [e_alert])` 갱신.

---

## 3. v8.9.8 hotfix 처방 계획 (FA 권고 정합)

### 3.1 P0 처방 3건 (필수)
| # | 처방 | 영역 |
|---|------|------|
| P0-1 | contribution_state 도입 (`CONTRIBUTED / SUPPRESSED_BY_ELIF / PROX_ONLY / DISPLAY_ONLY`) | 전 embed |
| P0-2 | build_macro_embed() WTI 문구 Crown #67 state-aware 갱신 | Embed 3 |
| P0-3 | BANNED_PHRASES_SEMANTIC 확장 + AT-7 강화 | banned phrase |

### 3.2 P1 처방 6건
| # | 처방 |
|---|------|
| P1-3 | VNM contribution map (P0-1 동일) |
| P1-4 | Portfolio/Signal 공통 signal builder (TLT tnx35 elif 정합) |
| P1-5 | format_proximity_pct() 중앙화 |
| P1-6 | VIX threshold-edge raw 표시 (`VIX 18.0 (raw 17.96, VIX>18=false)`) |
| P1-7 | build_one_glance_embed() archive/제거 |
| P1-8 | send_queue 라벨 "매매 4분류" → "매매 5분류" |

### 3.3 P2 처방 2건
| # | 처방 |
|---|------|
| P2-7 | EPS-safe ratio 분류 (`if ratio + 1e-9 >= 1.0`) |
| P2-8 | DecisionViewModel priority 의미 명확화 (또는 정렬용 미사용 명시) |

### 3.4 v8.9.8 변경 영역 (FA 정합)
```
contribution_state map 도입 → Embed 1, 2, 4 공통 적용
build_macro_embed() WTI 문구 교체 → Crown #67 hysteresis
BANNED_PHRASES_SEMANTIC 확장
format_proximity_pct() 중앙화
build_one_glance_embed() archive
send_queue 라벨 갱신
EPS-safe ratio 분류
priority 의미 명확화
```

---

## 4. v8.9.8 Acceptance Test 확장 (AT-11 ~ AT-20, 10개 신설 baseline)

| AT | 테스트 | 통과 조건 |
|----|--------|-----------|
| AT-11 | stale WTI macro phrase | "전종목 즉시 청산" / "일반 종목 즉시 청산" 0건 |
| AT-12 | contribution map 존재 | 모든 표시 signal에 contribution_state 보유 |
| AT-13 | TLT tnx4/tnx35 elif | TNX>4이면 tnx35 active 표시 금지 |
| AT-14 | SLV score CONTRIBUTED 합계 일치 | score = sum(CONTRIBUTED.points) |
| AT-15 | VIX threshold edge | raw 17.96이면 VIX>18=false 표시 |
| AT-16 | proximity single source | 동일 signal prox가 embed 간 동일 |
| AT-17 | Portfolio/Signal display parity | 동일 ticker active signal set 정합 |
| AT-18 | send_queue 라벨 | "매매 4분류" 문자열 0건 |
| AT-19 | build_one_glance stale WTI | 미사용 stale 함수 문구 0건 |
| AT-20 | ratio EPS | 0.999999999도 100% 경계 안정 처리 |

🌟 **총 AT 20개 baseline** (기존 10 + 신설 10) — S103에서 자동화 의무.

---

## 5. v8.9.8 작업 범위 (FA 권고 정합)

| 항목 | 처리 |
|------|------|
| PRIMA 엔진 | 🚨 **변경 금지** baseline |
| Crown #67 | 🟢 유지 |
| Back Test 영향 | 🌟 **0** 🌟 |
| RP overlay | 🟡 별도 lane 유지 |
| 변경 본질 | **renderer display semantics only** baseline |
| 목표 | v8.9.8 CLEAN GO baseline |

---

## 6. 격언 정합 체크리스트

- ✅ §35 §34 (자기정정): FA가 자체 audit 한계 보완 baseline 정직 인정
- ✅ §41 (전체 파일 출력): 본 REG + HANDOFF v3 출력
- ✅ §42 (full diff): FA 응답 + 처방 11건 명시
- ✅ §43 (과장 금지): "본질" 사용 — 실측 결과 표 명시
- ✅ 격언 #34 §35: Claude 자체 audit 한계 명시 + FA 보완 정합
- ✅ 격언 #75 v4: 본 결함 본질은 grep 의무 위반 (Embed 1 ↔ Embed 4 정합 audit 부재)
- ✅ 격언 #80 (양방향 정합): 본 결함의 본질
- ✅ 격언 #97 v2 사례 #6 **본격 확정** baseline: 외부 FA 가치 누적 강화 baseline
- ✅ 격언 #98 (결정 지연 ≠ 중립): FA 응답 즉시 처방 계획 baseline
- ✅ 격언 #110 (세션 substance): S102 마감 직전 FA 처리 baseline
- ✅ 격언 #115 후보 LIVE: SKILL v1.1 한계 baseline 입증 → v1.2 후보 (A9 영역 신설) 권고

---

## 7. SSOT 갱신 사항

- SSOT 다음 버전: **v1.10.194**
- REGRET LOG MASTER: REG-S102_10 append
- HANDOFF 갱신: v3 (S103 작업 범위 v8.9.8 hotfix + AT 20개)
- 격언 #97 v2 사례 #6 본격 확정 baseline
- SKILL v1.2 후보: A9 영역 신설 + contribution_state 검증 통합

---

## 8. 격언 #97 v2 사례 누적 결정적 확정 (6건)

| 사례 | hotfix | 차단된 결함 | FA 가치 |
|------|--------|-----------|--------|
| #1 Crown #65 | ENTRY_THRESHOLD 분리 | dict ↔ entry 불일치 | 사전 차단 |
| #2 RP overlay 단일 패치 | v5.20A 분해 | 격언 #48 폐기 risk | 사전 차단 |
| #3 Phase B BT | v5.20A REJECT | RULE 29 v2 CAGR-first | 사전 차단 |
| #4 v8.9.4 P0 5건 | v8.9.5 hotfix | allow-list + hard gate | 사전 차단 |
| #5 v8.9.5 P1 5건 | v8.9.6 hotfix | 격언 #80 회복 | 사전 차단 |
| 🌟 **#6 v8.9.7 결함 11건** 🌟 | 🌟 **v8.9.8 hotfix** 🌟 | **표시 정합 + semantic stale + 미사용 함수** | **자체 audit 한계 보완** |

🌟 **FA 사전 감사 누적 가치 baseline 결정적 입증** baseline.

---

## 9. 후속 작업 (S103 Phase A)

| 작업 | 우선 |
|------|-----|
| v8.9.8 hotfix 작업 (11건 처방) | 🔴 P0 |
| AT 20개 자동화 (AT-11 ~ AT-20 신설) | 🔴 P0 |
| v8.9.8 자체 pre_output_audit 8/8 PASS 검증 | 🟠 P1 |
| FA P0 재의뢰 baseline (v8.9.8 검증) | 🟠 P1 |
| SKILL v1.2 baseline (A9 영역 신설 검토) | 🟢 추후 |

---

🌟 **본 REG는 격언 #97 v2 사례 #6 본격 확정 baseline** baseline. 🌟
자체 audit 8건 → FA가 3건 추가 발견 → 총 11건 baseline 처방 baseline. SKILL v1.1의 한계 baseline 입증 + 외부 FA 사전 감사 가치 baseline 결정적 입증 baseline.
