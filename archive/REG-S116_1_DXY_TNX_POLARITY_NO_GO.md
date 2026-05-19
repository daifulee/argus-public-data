# 🚨 REG-S109_3 — DFII10<-0.5 XLE 60D v5_21 NO-GO

**등재일**: 2026-05-17 (S109)
**Commander**: Lignas
**결정**: 🔴 **Crown #68 후보 NO-GO** (v5_21 patch 단독)
**격언 정합**: 🌟 **#52 결정적 입증** 🌟 + #25 + #76 + #87 + #97 v2 + #112 v2 #8 v2

---

## 🎯 §1. 결론 한 줄

🌟 **"DFII10<-0.5 XLE 60D는 좋은 signal이지만 나쁜 patch였다.**
**v5_21 단독 Crown #68 후보는 NO-GO, signal 자체는 후속 연구 큐 (XLE conviction modifier)로 보존."** 🌟

---

## 📊 §2. Phase A 결정적 검증 (signal quality)

### 2.1 단독 시그널 강도 (격언 #25 + #76 + #87 정합)

| 지표 | 실측 | 평가 |
|------|------|------|
| n_on | 654 | 인계장 baseline 완전 일치 ✅ |
| spread | 🌟 **+9.405%p** 🌟 | 3축 polarity inversion 최상위급 |
| hit rate | 🌟 **77.68%** 🌟 | 결정적 신뢰 |
| t-stat | 🌟 **+15.482** 🌟 | p = 1.7e-47 (결정적 유의) |
| 격언 #87 | 🌟 **5/5 years PASS** 🌟 | 인계장 4/4 baseline 더 강함 |
| 격언 #76 plateau | 🌟 **-0.5는 plateau 중심** 🌟 (DFII10 ∈ [-0.6, -0.3]) |
| 격언 #25 잔여 효과 | 🌟 **+10.240%p** 🌟 (dfii0 통제 후 분리, t=+9.963) |
| 격언 #112 v2 #8 v2 polarity | XLE EnSn 강 3순위 (spread 1위) |

### 2.2 자산별 polarity 결정적 정형화 (격언 #112 v2 #8 v2)

| Rank | Ticker | t-stat | polarity |
|------|--------|--------|----------|
| 🥇 1 | PDBC | +17.804 | 🟢 EnSn 강 |
| 🥈 2 | XLF | +16.386 | 🟢 EnSn 강 |
| 🥉 3 | 🌟 **XLE** 🌟 | +15.482 | 🟢 EnSn 강 (spread 1위) |
| 21 | GLD | -16.632 | 🔴 EASn 강 |
| 22 | TLT | -18.621 | 🔴 EASn 강 |

🚨 **인계장 §2.2 정정 발견**: "DFII10<-0.5 → 금/장기채 EnSn" 표기는 실측 정반대 (TLT/GLD EASn 강) — 별도 정정 의무

---

## 🚨 §3. Phase B portfolio BT 결과 (Crown #68 후보 NO-GO)

### 3.1 4기간 BT 매트릭스 (RULE 29 v2 평가 baseline)

| Period | baseline CAGR | v5_21 CAGR | 🚨 Δ CAGR | 🚨 Δ Sharpe | 🚨 Δ MDD |
|--------|------------|-----------|-----------|-----------|---------|
| FULL | +34.365% | +34.001% | -0.364%p | -0.015 | 🔴 -4.067%p |
| P1 | +29.275% | +29.777% | +0.502%p | +0.023 | 🔴 -4.067%p |
| P2 | +39.352% | +37.986% | 🔴 -1.366%p | -0.058 | -0.215%p |
| MID | +46.450% | +44.918% | 🔴 -1.532%p | -0.039 | 0.000%p |
| **avg** | — | — | 🚨 **-0.690%p** | 🚨 **-0.0226** | 🚨 **-2.088%p** |
| **min** | — | — | 🚨 **-1.532%p** | 🚨 **-0.0584** | 🚨 **-4.067%p** |

### 3.2 RULE 29 v2 평가 결과 — 3/3 ALL FAIL

| 평가 | 기준 | 실측 | 판정 |
|------|------|------|------|
| 1st CAGR | avg ≥-0.5p, all ≥-1p | avg -0.690%p / min -1.532%p | 🚨 **FAIL** |
| 2nd Sharpe | avg ≥+0.005, all ≥0 | avg -0.0226 / min -0.0584 | 🚨 **FAIL** |
| 3rd MDD | avg ≥0 | avg -2.088%p (FULL/P1 -4.07%p) | 🚨 **FAIL** |

🚨 **최종 판정**: Crown #68 후보 NO-GO

### 3.3 STRESS 14 비결정 (정합)

- 🟡 全 14 시나리오 Δ CAGR/Sharpe/MDD = 0
- 사건 부재 (DFII10<-0.5 미발화) 또는 _wk_xle/gate 우선 차단
- → 결정적 의사결정에 영향 없음 (PASS도 FAIL도 아님)

---

## 🌟 §4. 격언 #52 결정적 입증 — Phase A strength ≠ BT alpha

본 BT 결과는 격언 #52 결정적 입증의 단일 세션 표본:

| 단계 | 결과 |
|------|------|
| Phase A 단독 시그널 | spread +9.405%p, t=+15.482, 5/5 years (3축 全 최강) |
| Phase B portfolio BT | CAGR -0.69%p, Sharpe -0.023, MDD -2.09%p (RULE 29 v2 3/3 FAIL) |

**근본 원인 진단** (3 가설 정량 분석):

| # | 가설 | 정량 증거 |
|---|------|---------|
| 1 | 🌟 **표본 손실 vs alpha trade-off** | dfii0(952) → dfii_neg05(654), **31.3% 표본 손실** → XLE entry 횟수 감소 |
| 2 | portfolio 다양화 손실 | XLE 진입 부재 시 TLT/GLD 등 과집중 → MDD 악화 -4.07%p (FULL/P1) |
| 3 | _wk_xle 게이트 우선 작동 | WTI>95 환경에서 dfii_neg05 시그널 무관 → STRESS 14 비결정 정합 |

---

## 🎯 §5. Signal vs Patch 분리 — Commander 결정적 통찰

🌟 **본 후보의 결정적 분리**:

| 분리 | 처분 | 격언 정합 |
|------|------|---------|
| 🟢 **DFII10<-0.5 signal 자체** | ✅ 보존 (후속 연구 큐) | 격언 #25/#76/#87/#112 v2 #8 v2 |
| 🔴 **v5_21 patch 형식 (단순 EnSn 가중치 +9.0 단독)** | ❌ NO-GO 폐기 | 격언 #52 + 자동 회피 #9 |

**Commander 핵심 통찰**:
> "이 후보는 'Entry gate 강화'가 아니라 'XLE conviction modifier'였어야 할 가능성이 큼."

즉, **signal의 활용 방식 재설계 필요** — entry signal이 아니라:
- conviction modifier (S 등급 → SS 등급 boost)
- regime confidence amplifier
- portfolio sizing 보조 변수
- multi-asset overlay 신호

---

## 🚨 §6. 자동 회피 영역 #9 신설 권고

🌟 **신설 영역 #9**:

> 🚨 **"단순 임계값 강화 전략 (Entry gate strength tweak without portfolio interaction analysis) —**
> **격언 #52 + 격언 #25 + 격언 #76 정합 위반 위험 자동 차단"**

### 6.1 자동 회피 발동 조건

| # | 조건 | 위반 격언 |
|---|------|---------|
| a | 기존 EnSn 시그널의 더 strict 임계값으로 단순 교체 | #25 |
| b | 표본 손실 ≥ 25% + 잔여 alpha < 표본 손실 효과 | #52 |
| c | portfolio 다양화 손실 검증 없는 단독 patch | #52 |
| d | conviction modifier vs entry gate 분리 검토 부재 | 본 #9 |

### 6.2 발동 시 의무 처방

| 단계 | 작업 |
|------|------|
| 1 | Phase A signal 보존 (후속 연구 큐) |
| 2 | Phase B portfolio BT 의무 (격언 #56) |
| 3 | conviction modifier 형태 재설계 검토 |
| 4 | RULE 29 v2 3/3 PASS 시에만 Crown 후보 진입 |

---

## 🔁 §7. 전환 트리거 5건 (Commander 명시)

| # | 상황 | 다음 행동 |
|---|------|---------|
| 1 | Conservative incremental이 4기간 평균 ΔCAGR ≥ +0.20%p, ΔMDD ≥ 0 | 후보 재상승 가능 |
| 2 | Stepwise가 P2/MID 손실을 모두 제거 | 연구 재개 가능 |
| 3 | XLE 진입 횟수 감소가 10% 미만인데도 alpha 훼손 | signal polarity/slot interaction 재진단 |
| 4 | XLE 진입 횟수 감소가 25% 이상 | 단순 임계값 강화 금지 REG 확정 |
| 5 | DXY>101 GLD 또는 VIX>25 EWZ가 §B.9 통과 | S109 주력 후보 전환 |

---

## 📋 §8. 후속 연구 큐

| # | 연구 후보 | 우선순위 | 격언 정합 |
|---|---------|---------|---------|
| 1 | DFII10<-0.5 XLE conviction modifier (entry gate ≠ modifier) | 🟡 중간 | #9 신설 정합 |
| 2 | Stepwise 재조정 (dfii<-0.5:+9.0 / dfii<0:+5.2 / dfii<1:+2.0) | 🟢 낮음 (overfit 위험) | #25 우려 |
| 3 | Conservative incremental (dfii<-0.5:+6.7 / dfii<0:+5.2) | 🟢 낮음 | #25 안전 |
| 4 | DFII10<-0.5 + vix22 시너지 조합 (Phase A.3.2 orthogonal +2.76%p 추가) | 🟡 중간 | 직교성 검증 |
| 5 | DFII10<-0.5 portfolio sizing modifier (multi-asset overlay) | 🟢 낮음 | 신규 설계 |
| 6 | 인계장 §2.2 정정 — TLT/GLD는 EASn 강 (정반대) | 🚨 결정적 | 정정 의무 |

---

## 📜 §9. 메타 학습 (S109 단일 세션 결정적 입증)

| # | 메타 학습 | 결정적 가치 |
|---|---------|----------|
| 1 | 🌟 격언 #52 결정적 입증 | Phase A spread +9.405%p → Portfolio CAGR -0.69%p |
| 2 | 표본 손실 (31.3%) vs alpha trade-off 정량화 | 잔여 +10.24%p alpha 보다 표본 효과 우위 |
| 3 | 단순 임계값 강화 strategy의 portfolio 한계 | 자동 회피 영역 #9 신설 baseline |
| 4 | Phase A → Phase B 단계 의무성 재입증 | §40 v3 (격언 #56) 정합 |
| 5 | RULE 29 v2 CAGR-first 평가의 결정적 가치 | 단일 axis 폐기 안전망 |
| 6 | 🌟 **signal vs patch 분리 통찰** | Commander 결정적 메타 통찰 (entry gate ≠ conviction modifier) |
| 7 | 인계장 §2.2 정정 발견 (TLT/GLD EASn) | polarity 사후 검증 의무 baseline |

---

## 🌟 §10. 본 REG 등재 최종 한 줄

🌟 **"DFII10<-0.5 XLE 60D v5_21 단독 patch는 Phase A spread +9.405%p, t=+15.482로 3축 Polarity Inversion 후보 中 최상위급 예측력을 보였으나, Phase B portfolio §40 v3 Back Test에서 RULE 29 v2 3/3 FAIL (avg ΔCAGR -0.690%p / ΔSharpe -0.0226 / ΔMDD -2.088%p)로 Crown #68 후보 NO-GO 판정. Signal 자체는 후속 연구 큐 (XLE conviction modifier 형태 재설계)로 보존, patch 형식만 폐기. 자동 회피 영역 #9 신설: 단순 임계값 강화 전략 portfolio 사전 검증 의무. 격언 #52 'Phase A strength ≠ Portfolio BT alpha' 결정적 입증."** 🌟

---

**작성**: S109 (2026-05-17 KST)
**버전**: v1 final
**다음 S109 작업**: S109 주력 후보 전환 (DXY>101/105 GLD 60D 또는 VIX>25 EWZ 60D)

✅ **기만 차단 5조 통과**
