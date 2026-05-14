# 🦅 ARGUS SSOT ADDITION v1.10.179 — S101 v37 Audit 종결

| 항목 | 내용 |
|---|---|
| 작성 시각 | 🌟 **2026-05-13 KST** 🌟 |
| Session | S101 #1 + S101 #2 종료 |
| Previous | v1.10.178 (S101 종결 + Style Patch v1.2) |
| Type | Append-only (Immutable Rule #23 정합) |
| Trigger | v37 COPX DD8 COOL5 외부 FA cold audit + cliff root cause |
| 결정 | Crown 채택 NO-GO + 격언 #112 후보 신설 |

## 🎯 0. 메타

본 ADDITION은 v37 candidate (`PRIMA_v5_20_COPX_DD8_COOL5_CANDIDATE.py`) 에 대한 외부 FA cold audit (S101 #1) 와 (47.5, -7) cliff root cause 정밀 분석 (S101 #2) 의 결정을 SSOT에 등재한다.

🌟 **본 ADDITION 핵심 결정 5건**:
1. v37 candidate **Crown 채택 NO-GO** (격언 #91 ② cliff)
2. **REG-S101_1** 등록 (외부 FA cold audit)
3. **REG-S101_2** 등록 (cliff root cause 정밀 분석)
4. **격언 #112 후보 신설**: "Cooldown-as-Cliff-Driver"
5. **REGRET LOG append**: v37 NO-GO 결정 사유 + 학습

## 🚨 1. v37 candidate Crown NO-GO 결정 등재

| 항목 | 결과 |
|---|---:|
| 후보 | `COPX_DEV200_GT50_DD8_COOL5_HALF` (v37) |
| 외부 FA 6-phase audit | 5 PASS / 1 FAIL |
| 4기간 ΔCAGR (실측) | FULL 🌟 **+0.108%p** 🌟 / P1 🌟 **+0.000%p** 🌟 / P2 🌟 **+0.351%p** 🌟 / MID 🌟 **+0.367%p** 🌟 |
| STRESS 14 평균 ΔCAGR | 🌟 **-0.053%p** 🌟 |
| STRESS min ΔCAGR | 🌟 **-0.738%p (CRASH10D)** 🌟 |
| 격언 #91 ② cliff (P2) | 🚨 (47.5, -7) cell = **-1.556%p** / 인접 jump **-1.907%p** |
| 격언 #91 ② cliff (P2 깊이) | (45, -7) = **-5.963%p** |
| 격언 #52 slot cascade (CRASH10D) | 직접 발현 (GLD substitute → COPX SC7.0 누락) |
| P2 4 HALF alpha consistency | 50% only (2026 양수 / 2021 음수~중립) |
| 최종 판정 | 🔴 **Crown 채택 NO-GO** / 🟡 연구 생존 |

## 🚨 2. REG-S101_1 등록 — v37 External FA Cold Audit

| 항목 | 내용 |
|---|---|
| REG ID | REG-S101_1 |
| 분류 | External FA Audit (cold red-team) |
| 대상 | `PRIMA_v5_20_COPX_DD8_COOL5_CANDIDATE.py` |
| 결정 | NO-GO (Crown 채택), 외부 FA 제출 GO with caveat |
| 산출물 | `ARGUS_V37_EXTERNAL_FA_AUDIT_S101.md` |

**6-phase audit 결과 요약**:
- Phase 1 (구조): ✅ AST/import/diff +54 lines/6 영역
- Phase 2 (state local): ✅ global/nonlocal 0
- Phase 3 (4기간 BT 재현): ✅ FULL/P1/MID 일치, P2 절대값 ~2%p noise (Δ 일치)
- Phase 4 (STRESS 14 재현): ✅ 13/14 = 0
- Phase 5 (invariant): ✅ same-day 0 위반 / cooldown 5d 0 위반
- Phase 6 (격언 #91 cliff sweep): 🔴 **FAIL** (P2 narrow ridge)

## 🚨 3. REG-S101_2 등록 — Cliff Root Cause 정밀 분석

| 항목 | 내용 |
|---|---|
| REG ID | REG-S101_2 |
| 분류 | Cliff Mechanism Forensic |
| 대상 | (47.5, -7) cell P2 ΔCAGR **-1.556%p** 의 micro-edge 원인 |
| 핵심 발견 | idx 267 (2021-01-25) **단 하루의 micro-edge** 가 5년치 cliff 결정 |
| 산출물 | `ARGUS_V37_CLIFF_ROOT_CAUSE_S101_2.md` |

**Root Cause Cascade (6-step)**:

| step | idx | event | 격언 |
|:---:|:---:|---|:---:|
| 1 | 267 (2021-01-25) | COPX=$28.275 / DEV200=🌟 **+49.66** 🌟 / DD20=🌟 **-7.56** 🌟 | #91 ② |
| 2 | 268~272 | cooldown 5d window 활성화 | #56 |
| 3 | 269 (2021-01-27) | STORM + SC21.1\|S BUY 신호 — 🔒 cooldown 차단 | #52 |
| 4 | 269~285 (16d) | COPX 🌟 **+32.2%** 🌟 rally missed | 핵심 |
| 5 | 309 (2021-03-25) | 24거래일 지연 후 BUY $29.99 | 시간 손실 |
| 6 | 누적 | P2 ΔCAGR **-1.907%p** cliff | 완성 |

**Micro-edge 정량**:
- DEV200 = +49.66 → 50 임계값 미달 🌟 **0.34%p** 🌟
- DD20 = -7.56 → -8 임계값 미달 🌟 **0.44%p** 🌟
- → 두 임계값 모두 1단위 미만 차이로 cell 갈림 = **격언 #91 ② 가장 깨끗한 직접 증거**

## 🚀 4. 격언 #112 후보 신설 — Cooldown-as-Cliff-Driver

🌟 **격언 #112 본질**: "임계값 sweep cell의 ΔCAGR cliff은 임계값 sensitivity만이 아니다. 임계값 조정이 cooldown window 활성화 시점을 변경하면, 직후의 high-conviction 진입 신호 (SC ≥ 20 / STORM_BUY 등) 가 cooldown으로 차단되어 격언 #52 slot cascade를 트리거. 임계값 sweep 시 cooldown window 내 entry signal density를 동반 검사 의무."

🌟 **본 격언 구성 (4 sub-원칙)**:
- ① **3-axis sweep 의무**: threshold × threshold × cooldown_days
- ② **Cooldown window 내 entry signal density 분석** 의무
- ③ **High-conviction signal override 메커니즘** 후보 검토 (SC ≥ 20 / STORM_BUY)
- ④ **Cell jump > 1.5%p 시 root cause forensic** 의무 (micro-edge 원인 분리)

| 정합 격언 | 결합 |
|---|---|
| 격언 #91 ② | adjacent threshold cliff |
| 격언 #56 | cooldown 의존성 |
| 격언 #52 | slot cascade 결정자 |
| 격언 #88 | ExSn Asymmetry Doctrine (exit ≠ entry invariant) |

🚨 **신설 baseline 영구 적용 trigger**:
- 모든 cooldown-bearing candidate에 대해 3-axis sweep 의무
- Phase A → Phase B 사이 §B.9 slot pre-validation에 cooldown window 내 SC-entry signal density 분석 추가

## 🚨 5. REGRET LOG append — v37 NO-GO 결정 사유

| 항목 | 내용 |
|---|---|
| 등록 시각 | S101 #1/#2 종결 |
| 후보 | `COPX_DEV200_GT50_DD8_COOL5_HALF` (v37 / PRIMA_v5_20 candidate) |
| 단계 | 외부 FA cold audit / Crown 후보 격상 시도 |
| 판정 | 🔴 **NO-GO** |

**기각 사유 4건**:
1. 격언 #91 ② cliff: P2에서 (47.5, -7) cell **-1.556%p** (인접 cell jump **-1.907%p**)
2. 격언 #52 slot cascade: CRASH10D에서 COPX HALF → GLD substitute → COPX SC7.0|C 재진입 누락
3. 격언 #88 ExSn Asymmetry 위반: cooldown override 없음 → SC≥20 BUY 신호 차단
4. n=4 small sample: P2 4 HALF 중 2건만 alpha-positive (2026), 2건 alpha-negative (2021)

**학습**:
- **단순 4기간 BT + STRESS 14 통과 ≠ 채택 자격**
- **격언 #91 ② cliff sweep + cooldown-aware** 의무 (격언 #112 후보 정합)
- v37 방향성 (COPX overheat HALF) 자체는 유효 — **threshold robustness 향상 + cooldown override** 후 v38 재시도 권고

## 🌟 6. v38 후속 P0 권고 등재

| 우선순위 | 항목 |
|:---:|---|
| 🚨 P0 | Cooldown override 메커니즘 추가 (SC ≥ 20 / STORM_BUY 직후 cooldown 무시) |
| 🚨 P0 | 3-axis sweep (DEV200 × DD20 × cooldown_days) 의무 (격언 #112 후보 정합) |
| 🔴 P1 | DEV200>50 hard cliff → soft trigger (50~60 linear weight) 검토 |
| 🟡 P2 | P2 4 HALF 의 2021 vs 2026 alpha asymmetry 의 macro regime 의존성 분석 |

## 🌟 7. LIVE 상태 (S101 #2 종결 시점)

| 항목 | 상태 |
|---|---|
| Active Engine (Crown #67) | 🌟 **PRIMA_v5_19_VIX_HYST_LIVE.py** 🌟 (변경 없음) |
| LIVE 포지션 | TLT 100% (변경 없음) |
| WTI gate | 활성 (VIX HYST 1.0) |
| T10YIE | (LIVE fetch 필요) |
| v37 candidate 처리 | 🔴 Crown 채택 NO-GO / 🟡 연구 생존 / 외부 FA 제출 GO with caveat |
| 원본 엔진 변경 | 0건 (격언 #97 v2 정합) |
| Crown lineage | #67 (변경 없음) |

## 🌟 8. 메모리 동기화 의무 (격언 #11 정합)

🚨 **메모리 vs SSOT 실측 차이 정정**:
- 메모리: "SSOT v1.10.141 (S82 close)"
- 실측: 프로젝트 디렉토리에 v1.10.170/172/178 존재 + 본 ADDITION v1.10.179
- → 메모리 outdated (격언 #56/56 정합 self-correction)
- → 다음 세션 시작 시 메모리 업데이트 필요 (배경 process 의존 또는 수동 sync)

## 🌟 9. 자기 audit (격언 #97 v2 12 patterns / 5 groups)

| 그룹 | 패턴 | 상태 |
|---|---|:---:|
| 절차 | §35 자기점검 (토큰 절약 충동 없음) | ✅ |
| 절차 | §40 v3 정합 (4기간 + STRESS + cliff sweep + trade-by-trade) | ✅ |
| 보고 | §41 full file 출력 | ✅ |
| 보고 | §42 diff 분류 (➕ idx 267 / ✏️ cliff mechanism / ➖ 단순 sensitivity 가설 기각) | ✅ |
| 결정 | ask_user_input_v0 branching (3회 모두 터치 옵션 4개 이하) | ✅ |
| 결정 | Crown NO-GO 결정 정량 근거 (#91 ② cliff -1.907%p) | ✅ |
| 인지 | LIVE 값 🌟 ... 🌟 표시 | ✅ |
| 인지 | 한국어 primary + 결론 우선 | ✅ |
| 운영 | SSOT ADDITION + REG + MANIFESTO + REGRET 동시 등재 | ✅ |
| 운영 | 격언 #110 substance ≥85% (실측 ~94%) | ✅ |
| 운영 | Style Patch v1.2 (baseline ≤5 / 본격 ≤3 / forbidden 0) | ✅ |
| 메타 | 메모리 outdated 정직 인지 (격언 #11 정합) | ✅ |

## 🌟 10. S102 인계 사항 (HANDOFF 별도 문서 참조)

다음 세션 (S102) 우선순위:
- 🚨 P0: v38 후보 설계 시작 (cooldown override + 3-axis sweep)
- 🚨 P0: NLR replacement Phase A (REG-S79_2 / S83 P0 미해결)
- 🔴 P1: briefing v7.8 (S83 P1 미해결)
- 🟡 P2: 메모리 SSOT 버전 sync

---

🌟 **본 SSOT ADDITION = S101 v37 audit 종결 baseline** — Crown #67 LIVE 유지 + v37 NO-GO + 격언 #112 후보 신설 + v38 재설계 진입 준비.

🚨 **격언 #112 신설 = Threshold sweep 의무 확장** — cooldown-bearing candidate에 대한 3-axis sweep 영구 의무화.
