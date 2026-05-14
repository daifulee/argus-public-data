# 🦅 REG-S101_2 — (47.5, -7) Cliff Root Cause 정밀 분석

| 항목 | 내용 |
|---|---|
| REG ID | REG-S101_2 |
| 등록 시각 | 🌟 **2026-05-13 KST** 🌟 |
| 분류 | Cliff Mechanism Forensic (격언 #91 ② 정밀 분리) |
| 대상 | v37 candidate P2 (47.5, -7) cell ΔCAGR **-1.556%p** 의 root cause |
| 발견 | idx 267 (2021-01-25) **단 하루의 micro-edge** = 5년치 cliff 결정 |
| 신규 격언 후보 | **#112 Cooldown-as-Cliff-Driver** |

## 🎯 1. 등록 동인

S101 #1 외부 FA cold audit에서 (47.5, -7) cell의 P2 ΔCAGR cliff을 발견. 이는 단순 임계값 sensitivity인가, 아니면 더 깊은 cascade인가? — 이를 trade-by-trade 정밀 분석으로 분리.

## 🚨 2. 핵심 발견 — Single Micro-Edge

### idx 267 (2021-01-25) 시그널 정확값

| 변수 | 값 | (50, -8) | (47.5, -7) |
|---|---:|:---:|:---:|
| COPX 가격 | 🌟 **$28.275** 🌟 | — | — |
| DEV200 | 🌟 **+49.662** 🌟 | ❌ (50 미달 0.34%p) | ✅ (47.5 초과 2.16%p) |
| DD20 | 🌟 **-7.558** 🌟 | ❌ (-8 미달 0.44%p) | ✅ (-7 미달 0.56%p) |
| 트리거 | — | ❌ | ✅ |

→ **두 임계값 모두 1단위 미만 차이로 cell이 갈림** = 격언 #91 ② **가장 깨끗한 직접 증거**

## 🔴 3. 6-Step Cascade Mechanism

| step | idx | event | 격언 |
|:---:|:---:|---|:---:|
| 1 | **267** (2021-01-25) | DEV200=+49.66 / DD20=-7.56 → (47.5,-7) HALF 트리거, (50,-8) 면제 | #91 ② |
| 2 | 268~272 | cooldown 5d window 활성화 (idx 273까지 차단) | #56 |
| 3 | **269** (2021-01-27) | STORM 청산 + SC21.1\|S BUY 신호 — 🔒 cooldown 차단 | #52 |
| 4 | 269~285 (16d) | COPX 🌟 **$26.46 → $34.98 = +32.2%** 🌟 rally missed | 핵심 손해 |
| 5 | **309** (2021-03-25) | 24거래일 지연 후 BUY $29.99 | 시간 손실 |
| 6 | 누적 | P2 ΔCAGR cell jump **-1.907%p** | cliff 완성 |

## 📊 4. 시그널 timeseries (idx 263~290)

| idx | date | COPX | DEV200 | DD20 | (50,-8) | (47.5,-7) |
|---:|---|---:|---:|---:|:---:|:---:|
| 263 | 2021-01-19 | $28.835 | +55.628 | -5.727 | ❌ DD>-8 | ❌ DD>-7 |
| 266 | 2021-01-22 | $28.809 | +53.172 | -5.814 | ❌ DD>-8 | ❌ DD>-7 |
| **267** | **2021-01-25** | **$28.275** | **+49.662** | **-7.558** | ❌ both | ✅ |
| 268 | 2021-01-26 | $27.822 | +46.637 | -9.041 | ❌ DEV< | ❌ DEV< |
| 269 | 2021-01-27 | $26.461 | +38.929 | -13.488 | ❌ DEV< | ❌ DEV< |
| 285 | 2021-02-19 | $34.979 | +70.919 | 0.000 | ❌ DD=0 | ❌ DD=0 |
| 290 | 2021-02-26 | $32.881 | +56.383 | -8.669 | ✅ | ✅ |

🎯 **idx 267 미만 micro-edge**: DEV200 +49.66 (50 미만 0.34%p) + DD20 -7.56 (-8 미만 0.44%p) — **두 axis 모두 1단위 미만 차이로 5년치 cumulative ΔCAGR 결정**

## 🔒 5. Cooldown Window Block 검증

(47.5, -7) cell: idx 267 HALF → cooldown until idx 272 (5거래일)

| idx | date | COPX | (47.5,-7) | (50,-8) |
|---:|---|---:|:---:|---|
| 267 | 2021-01-25 | $28.275 | HALF | — |
| 268 | 2021-01-26 | $27.822 | 🔒 BLOCKED | — |
| **269** | **2021-01-27** | **$26.461** | 🔒 BLOCKED | **BUY SC21.1\|S** |
| 270 | 2021-01-28 | $27.350 | 🔒 BLOCKED | — |
| 271 | 2021-01-29 | $26.408 | 🔒 BLOCKED | — |
| 272 | 2021-02-01 | $28.017 | 🔒 BLOCKED | — |
| 273 | 2021-02-02 | $27.697 | OK (post-cool) | — |

→ idx 269 SC21.1|S BUY 신호는 (47.5, -7)에서 **명시적으로 cooldown 차단**됨

## 📊 6. 손해 분해 (P2 ΔCAGR -1.907%p)

| 구성 요소 | 비중 |
|---|:---:|
| idx 267 너무 일찍 HALF ($28.275 → 즉시 $26.46) | 단기 변동 (작음) |
| **idx 269 SC21.1\|S BUY missed** ($26.46 → $32.88 = +24.3%) | 🚨 **주요** |
| idx 290 추가 HALF 미발동 (이미 50% 보유) | 부차적 |
| idx 309 24거래일 지연 재진입 | 시간 누적 |

## 🚨 7. 숨겨진 candidate 설계 결함

| 결함 | 영향 |
|---|---|
| Cooldown override 메커니즘 부재 | SC ≥ 20 / STORM_BUY 같은 high-conviction 신호 차단 |
| v36 설계 문서에 영역 누락 | 설계 단계에서 catch 못함 |
| 격언 #88 (ExSn Asymmetry) 위반 | exit invariant ≠ entry invariant 분리 안 됨 |

## 🚀 8. 격언 #112 후보 (MANIFESTO 별도 등록)

🌟 **"Cooldown-as-Cliff-Driver"** — 임계값 sweep 시 cooldown window 위치 이동이 직후의 high-conviction 진입 신호를 차단해 격언 #52 slot cascade 트리거. 임계값 sweep 시 cooldown window 내 entry signal density 동반 검사 의무.

(격언 #91 ② + #56 + #52 + #88 의 결합 사례)

## 🎯 9. v38 후속 P0 권고

| 우선순위 | 항목 |
|:---:|---|
| 🚨 P0 | Cooldown override (SC ≥ 20 / STORM_BUY 직후 무시) |
| 🚨 P0 | 3-axis sweep (DEV200 × DD20 × cooldown_days) |
| 🔴 P1 | DEV200 hard cliff → soft trigger (50~60 linear weight) 검토 |
| 🟡 P2 | DD20 lookback period sweep (20d → 15/25/30d) |

## 📁 10. 산출물

| 파일 | 내용 |
|---|---|
| ARGUS_V37_CLIFF_ROOT_CAUSE_S101_2.md | cliff 정밀 분석 종합 보고서 |
| /tmp/cliff_origin_audit.py | trade-by-trade diff 코드 |
| /tmp/cliff_root_audit.py | micro-edge + cooldown block 검증 코드 |
