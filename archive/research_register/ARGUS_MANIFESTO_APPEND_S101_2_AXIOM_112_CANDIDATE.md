# 🦅 ARGUS MANIFESTO LOG APPEND S101 #2 — 격언 #112 후보 신설

| 항목 | 내용 |
|---|---|
| 등록 시각 | 🌟 **2026-05-13 KST** 🌟 |
| Session | S101 #2 종결 |
| 신설 격언 번호 | **#112** |
| 격언 이름 | **Cooldown-as-Cliff-Driver** (쿨다운 cliff 동인) |
| 발견 trigger | v37 candidate (47.5, -7) cell ΔCAGR -1.907%p cliff 정밀 분석 |
| 정합 격언 | #91 ② + #56 + #52 + #88 의 결합 사례 |
| 상태 | 🟡 **후보 등재** (Commander 정식 채택 결정 대기) |

## 🌟 격언 #112 본질

> **"임계값 sweep cell의 ΔCAGR cliff은 임계값 sensitivity만이 아니다. 임계값 조정이 cooldown window 활성화 시점을 변경하면, 직후의 high-conviction 진입 신호 (SC ≥ 20 / STORM_BUY 등) 가 cooldown으로 차단되어 격언 #52 slot cascade를 트리거. 임계값 sweep 시 cooldown window 내 entry signal density를 동반 검사 의무."**

## 🚀 본 격언 구성 — 4 sub-원칙

### ① 3-axis sweep 의무
- 모든 cooldown-bearing candidate에 대해 threshold₁ × threshold₂ × cooldown_days 의 3-axis sweep 의무
- 2-axis (threshold만) sweep 은 cliff 원인 분리에 불충분 (S101 #1 실증)

### ② Cooldown window 내 entry signal density 분석 의무
- HALF/SELL 트리거 직후 cooldown 기간 (예: 5d) 내 모든 SC급 / STORM_BUY 진입 신호 빈도 측정
- Phase A → Phase B 사이 §B.9 slot pre-validation 에 본 분석 추가

### ③ High-conviction signal override 메커니즘 후보 검토
- SC ≥ 20 또는 STORM_BUY 같은 high-conviction 진입 신호는 cooldown 무시 옵션 검토
- 격언 #88 ExSn Asymmetry 정합 — exit invariant ≠ entry invariant 분리

### ④ Cell jump > 1.5%p 시 root cause forensic 의무
- 임계값 sweep cell jump 가 1.5%p 초과 시 micro-edge 원인 분리 (trade-by-trade 분석) 의무
- 단일 day micro-edge 가 cumulative 손해를 결정하는 케이스 catch

## 🔴 발견 케이스 — S101 #2

| 발견 차원 | 정량 |
|---|---:|
| Cell jump | (50,-8) +0.351%p → (47.5,-7) **-1.556%p** = 🌟 **-1.907%p** 🌟 |
| Single day trigger | idx 267 (2021-01-25) 단 하루 |
| Micro-edge | DEV200 50 미달 0.34%p + DD20 -8 미달 0.44%p |
| Missed upside | idx 269~285 COPX 🌟 **+32.2%** 🌟 rally |
| Cumulative impact | P2 5년 ΔCAGR 결정 |

## 🚨 결합 격언 참조

| 격언 | 역할 |
|:---:|---|
| **#91 ②** | adjacent threshold cliff (직접 trigger 원인) |
| **#56** | cooldown 의존성 (window 활성화) |
| **#52** | slot competition cascade (효과 증폭) |
| **#88** | ExSn Asymmetry Doctrine (exit ≠ entry invariant) |

## 🎯 영구 적용 조건 (Commander 정식 채택 시)

| 조건 | 강제 시점 |
|---|---|
| 모든 cooldown-bearing candidate 3-axis sweep | Phase A 진입 직후 |
| Cooldown window 내 SC-entry signal density 분석 | §B.9 slot pre-validation 단계 |
| Cell jump > 1.5%p forensic | sweep 결과 검토 시 |
| High-conviction signal override 설계 검토 | candidate 설계 단계 |

## 📋 Commander 결정 대기 사항

🎯 **격언 #112 정식 채택 여부**:
- 옵션 A: 즉시 채택 — 영구 baseline 등재
- 옵션 B: v38 candidate 첫 적용 후 채택 확정
- 옵션 C: 추가 케이스 누적 후 결정

## 🌟 본 후보 baseline 정합 자기 검증

| 영역 | 점검 |
|---|:---:|
| 정량 근거 | ✅ S101 #2 실측 정량 (cell jump -1.907%p, micro-edge 0.34/0.44%p) |
| 격언 신설 trigger | ✅ S101 #1 cold audit + S101 #2 forensic |
| 4 sub-원칙 명료성 | ✅ 각각 강제 시점/방법 명시 |
| 기존 격언 정합 | ✅ #91/#56/#52/#88 결합 사례로 명시 |
| 영구 적용 trigger | ✅ Commander 결정 대기 baseline |
