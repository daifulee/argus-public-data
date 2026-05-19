# 🌟 REG-S113_1 — 조합 #1 (Panic Peak-Out) Phase A~B Verdict 🦅

**REG ID**: REG-S113_1
**작성일**: 2026-05-17 KST
**조합명**: Panic Peak-Out
**Factor**: VIX>22 ∩ VVIX peak -5% (D4 정의)
**§B.9 v3 framework 단계**: Phase A~B 완결 / Phase C (§40 v3 BT) 대기
**잠정 Verdict**: 🟢 **조건부 GO 후보** (Tier 1 EWZ Gate B only, §40 v3 BT 결과로 최종 결정)
**SSOT**: v1.10.209 ACTIVE
**Crown 영향**: 변경 없음 (Crown #67 = PRIMA_v5_19_VIX_HYST_LIVE_v4 LIVE 유지)

---

## §0. REG 한 줄 결산

🌟 **"조합 #1 (VIX>22 × VVIX peak -5%) — Phase A causal v2.2 + Phase B 슬롯 사전 검증 完了. D4 정의 + Gate B 분리 + EWZ Tier 1 verdict 정착. 잔여 α (V_HYST 重복 차단 + Gate B 분리 後) FULL +3.94p, t=4.21 / 全 시기 패턴 ③ 完全 PASS. §40 v3 BT 진입 가능 (S114 1순위)."** 🦅

---

## §1. Factor 정의

### 1.1 Factor A (Trigger)

| 항목 | 정의 |
|------|----|
| 변수 | VIX |
| 조건 | VIX > 22 |
| 본질 | Panic regime 진입 임계 |
| 표본 (BT_LONG) | 1,349일 (4,827일 中 27.95%) |
| 연도 분포 | 18년 (2007~2026) |

### 1.2 Factor B (Confirmation)

| 항목 | 정의 |
|------|----|
| 변수 | VVIX |
| 조건 | VVIX_t / VVIX_max5(shift 1) < 0.95 |
| 본질 | Panic 피크에서 -5% 이상 압축 (peak-out 강도 측면) |
| D3 비교 | D3 (peak-out, D1∩momentum) 패턴 ④ Temporal Hetero 발견 → 채택 不可 |
| **D4 선택 근거** | 패턴 ③ Robust Plateau (全 시기 PASS) |

### 1.3 조합 ON 정의

```
combo_ON = (VIX > 22) ∩ ((VVIX_t / max(VVIX_(t-5):VVIX_(t-1))) < 0.95)
```

| 항목 | 값 |
|------|----|
| 표본 | **618일** (4,827일 中 12.80%) |
| 연도 분포 | 18년 |
| 2020+ | 257일 |

---

## §2. Phase A causal v2.2 결과

### 2.1 Forward return 측정 (signal t → entry t+1 → return t+1+H)

| 자산 | H=5 | H=20 | H=60 (raw α) |
|------|----|----|----|
| EWZ | +0.64p, t=2.28 🟡 | +2.15p, t=4.18 ✅ | 🌟 **+7.99p, t=9.92** 🌟 ✅ |
| XLE | +0.69p, t=2.83 🟡 | +1.44p, t=3.24 ✅ | +4.39p, t=7.03 ✅ |
| IWM | +0.38p, t=1.93 ❌ | +1.62p, t=4.62 ✅ | +4.31p, t=7.81 ✅ |
| SMH | +0.22p, t=1.03 ❌ | +1.39p, t=3.51 ✅ | +3.18p, t=4.93 ✅ |
| SPY | +0.21p, t=1.35 ❌ | +1.07p, t=3.98 ✅ | +2.30p, t=5.41 ✅ |
| GLD | -0.02p, t=-0.18 ❌ | +0.12p, t=0.47 ❌ | +1.24p, t=3.30 ✅ |

### 2.2 잔여 α 측정 (V_HYST 重복 차단 後)

V_HYST 블록 (VIX≥18.5) 內 조합 ON vs OFF — Crown #67 重복 100%이므로 잔여 α 측정 의무.

| 자산 | H=60 잔여 α | t-stat | Raw 대비 감소율 | Verdict |
|------|----|----|----|----|
| **EWZ** | 🌟 **+5.26p** 🌟 | 🌟 **5.77** 🌟 | 34% ↓ | ✅ **최강** |
| SMH | +2.58p | 3.54 | 19% ↓ | ✅ |
| IWM | +2.53p | 4.11 | 41% ↓ | ✅ |
| SPY | +1.76p | 3.70 | 23% ↓ | ✅ |
| XLE | +1.48p | 2.10 | 66% ↓ | ✅ (단, WTI 게이트로 제한) |
| GLD | +0.66p | 1.61 | 47% ↓ | 🟡 marginal |

### 2.3 시기별 분기 (격언 #91 v2 패턴 ④ 차단)

H=60 잔여 α (V_HYST 블록 內):

| 자산 | P1 (07-15) | P2 (16-26) | MID (18-24) | FULL | 분류 |
|------|----|----|----|----|----|
| **EWZ** | ✅ +7.35p (t=5.54) | ✅ +2.91p (t=2.37) | ✅ +3.62p (t=2.98) | ✅ +5.26p (t=5.77) | 🟢 **패턴 ③ Robust Plateau** |
| IWM | ✅ +1.35p (t=1.55) | ✅ +4.06p (t=4.89) | ✅ +4.06p (t=4.39) | ✅ +2.53p (t=4.11) | 🟢 패턴 ③ Robust Plateau |
| SMH | ✅ +2.26p (t=2.58) | ✅ +3.28p (t=2.93) | ✅ +2.43p (t=2.12) | ✅ +2.58p (t=3.54) | 🟢 패턴 ③ Robust Plateau |
| SPY | ✅ +1.41p (t=2.00) | ✅ +2.31p (t=3.91) | ✅ +1.96p (t=3.06) | ✅ +1.76p (t=3.70) | 🟢 패턴 ③ Robust Plateau |
| XLE | ✅ +1.66p (t=1.91) | 🟡 +1.50p (t=1.37) | 🟡 +1.10p (t=0.89) | ✅ +1.48p (t=2.10) | ⚠️ 패턴 ④ Temporal Hetero |
| GLD | ✅ +1.08p (t=1.80) | ❌ +0.12p (t=0.22) | 🟡 +0.86p (t=1.51) | 🟡 +0.66p (t=1.61) | ❌ 미정/약함 |

---

## §3. Phase B 슬롯 사전 검증 결과

### 3.1 Crown #67 baseline gate 분류

| Gate | 정의 | 표본 | 비중 | Crown #67 baseline |
|------|----|----|----|----|
| Gate A | V_HYST 블록 ∩ WTI>90 | 151일 | 24.4% | TLT 100% (T10YIE<2.5 면제) |
| Gate B | V_HYST 블록 ∩ WTI≤90 | 467일 | 75.6% | 모멘텀 자산 진입 |
| Gate C | V_HYST 해제 | 0일 | 0.0% | (조합 ON은 V_HYST 블록의 부분집합이므로 不可) |

### 3.2 Phase B-2 박탈자 분석

#### Gate A — TLT 박탈 정당화 ❌

| 자산 | 평균 60일 ret | 중앙값 | 표본 |
|------|----|----|----|
| **TLT (baseline)** | -1.37% | -1.43% | 145 |
| EWZ | -0.59% | +4.29% | 145 |
| SMH | -4.14% | -2.26% | 145 |
| IWM | -1.53% | -0.54% | 145 |
| SPY | -2.48% | -1.29% | 145 |
| **4 자산 평균** | -2.19% | -0.07% | — |

**박탈 가치**: -0.82p / paired t = -0.49 / p = 0.6282 / 박탈 정당화율 66.2%

🚨 **Gate A에서 TLT 박탈 정당화 不可** — paired t-test 유의성 없음.

#### Gate B — 4 자산 boost 정당화 🌟

| 자산 | 평균 60일 ret | 양수율 | 표본 |
|------|----|----|----|
| **EWZ** | 🌟 **+12.27%** 🌟 | 76.8% | 465 |
| **SMH** | 🌟 **+11.54%** 🌟 | 81.1% | 465 |
| IWM | +8.54% | 77.8% | 465 |
| SPY | +7.01% | 82.6% | 465 |
| GLD | +5.84% | 70.8% | 465 |
| XLE | +7.53% | 71.4% | 465 |
| **TLT (baseline)** | +0.51% | 53.8% | 465 |
| **4 자산 평균** | 🌟 **+9.84%** 🌟 | — | — |

**박탈 가치 vs TLT**: 🌟 **+9.33p** 🌟

✅ **Gate B에서 4 자산 boost 압도적 정당화**.

### 3.3 Gate B 분리 後 시기별 분기 재검증 (결정적 새 발견)

Gate B 분리 後 (V_HYST ∩ WTI≤90 ∩ 조합 OFF baseline):

| 자산 | P1 | P2 | MID | FULL | 분류 |
|------|----|----|----|----|----|
| **EWZ** | ✅ +3.43p (t=2.74) | ✅ +3.90p (t=2.77) | ✅ +4.54p (t=3.19) | ✅ +3.94p (t=4.21) | 🟢 **패턴 ③ 完全 PASS** |
| SMH | ❌ -1.08p (t=-1.28) | ✅ +6.59p (t=6.45) | ✅ +5.71p (t=5.53) | ✅ +2.04p (t=2.81) | 🟡 패턴 ③ 약함 (P1 反転) |
| IWM | ❌ -1.69p (t=-1.88) | ✅ +6.03p (t=7.13) | ✅ +6.20p (t=6.36) | ✅ +1.97p (t=3.08) | 🟡 패턴 ③ 약함 (P1 反転) |
| SPY | ❌ -0.92p (t=-1.34) | ✅ +3.88p (t=7.38) | ✅ +3.55p (t=6.08) | ✅ +1.30p (t=2.90) | 🟡 패턴 ③ 약함 (P1 反転) |

⚠️ **결정적 발견**: Gate B 분리 後 SMH/IWM/SPY는 P1 (2008 금융위기 영역) 잔여 α 음수. 단순 4 자산 균등 boost는 P1 시기 손실 가능. EWZ만 全 시기 패턴 ③ 완전 PASS.

### 3.4 Cross-Asset Overlay 重복 (자동 회피 #10 후보)

VRC overlay 대리 metric: VVIX/VIX^0.5 ratio가 20일 평균보다 -10% 이상 압축.

| 항목 | 표본 |
|------|----|
| 조합 #1 ON | 618일 |
| VRC ON (대리) | 166일 |
| 重복 (兩 ON) | 82일 (조합의 **13.3%**) |
| 조합 only | 536일 (86.7%) |
| VRC only | 84일 |

✅ **重복율 13.3% (낮음)** → 본 조합과 VRC는 분리된 시그널. **자동 회피 #10 후보 PASS**.

---

## §4. Tier 분류 (자동 회피 #11 v2 단계 5)

### 4.1 Tier 결정적

| Tier | 자산 | 적용 조건 | 본질 |
|------|------|------|------|
| 🟢 **Tier 1** | **EWZ** | Gate B 만 (V_HYST ∩ WTI≤90) | 패턴 ③ 完全 PASS / 잔여 α (Gate B 분리) +3.94p / regime tag 최적 |
| 🟡 Tier 2 | SMH/IWM/SPY | Gate B + **2016+ 시기 only** | 패턴 ③ 약함 (P1 反転) / P2/MID 강함 |
| ❌ Tier 3 | XLE | — | 패턴 ④ Temporal Hetero (P2/MID 약화) |
| ❌ Tier 4 | GLD | — | 미정/약함 (방어성 자산은 panic peak-out regime tag 부적합) |
| ❌ Tier 5 | Gate A 시점 | — | TLT 박탈 정당화 不可 (paired t=-0.49) |

### 4.2 Tier 1 EWZ 단독 진입 시뮬레이션 baseline (S114 §40 v3 BT 사전 ref)

| 항목 | 값 |
|------|----|
| 조합 ON ∩ Gate B | 467일 (75.6% of 조합 ON) |
| EWZ 평균 60일 ret (Gate B 內 조합 ON) | +12.27% |
| EWZ Gate B 內 baseline (조합 OFF) | +8.33% |
| **잔여 α (Gate B 분리)** | 🌟 **+3.94p (t=4.21)** 🌟 |
| 시기 robustness | P1 ✅ / P2 ✅ / MID ✅ / FULL ✅ |

---

## §5. §B.9 v3 framework Phase B 정합

본 cycle은 §B.9 v3 framework Phase B 5단계 완전 진행 (SSOT v1.10.209 §3에 본질 명시).

| Phase | 상태 |
|------|----|
| B-1 Crown gate 분류 | ✅ 完了 |
| B-2 박탈자 분석 | ✅ 完了 |
| B-3 Cross-Asset Overlay 重복 | ✅ 完了 |
| B-4 Gate 분기 verdict | ✅ 完了 |
| B-5 자산 Tier 분류 | ✅ 完了 |

---

## §6. §40 v3 BT 대기 사항

### 6.1 S114 진입 BT 설계 권고

| 항목 | 권고 |
|------|----|
| 엔진 baseline | Crown #67 (PRIMA_v5_19_VIX_HYST_LIVE_v4) |
| 신호 통합 | EWZ Tier 1 boost (Gate B 만 활성) |
| 기간 | 4-period (FULL/P1/P2/MID) |
| STRESS | 14 시나리오 (의무) |
| RULE 29 v2 | 6/6 통과 의무 (CAGR avg ≥ -0.5p / 4BT ≥ -1p) |
| 부가 BT | Tier 2 (SMH+IWM+SPY) 추가 vs EWZ 단독 비교 (P1 손실 검증) |

### 6.2 사전 예측 (정성)

| 시나리오 | 예측 |
|------|----|
| EWZ Tier 1 단독 boost (Gate B only) | 🟢 RULE 29 v2 통과 가능 (P1~MID 全 시기 잔여 α 양수) |
| Tier 1+2 균등 boost | 🟡 P1 시기 SMH/IWM/SPY 음수 손실 위험 |
| Tier 1+2+3 균등 boost | ❌ XLE 패턴 ④ + GLD 무관성으로 손실 확대 위험 |
| Gate 분기 미적용 (Gate A 동시 활성) | ❌ Gate A -0.82p × 24.4% = -0.20p 손실 |

---

## §7. 결정적 한 줄 결산 🦅

🌟 **"REG-S113_1 — 조합 #1 (Panic Peak-Out) Phase A~B 完了. D4 정의 (VVIX peak -5%) + Gate B 분리 + EWZ Tier 1 verdict 정착. 잔여 α (Gate B 분리 後) FULL +3.94p, t=4.21 / 全 시기 패턴 ③ 完全 PASS. Tier 1 EWZ만 Gate B 활성 적용 권고. SMH/IWM/SPY (Tier 2) P1 反転 위험 / XLE 패턴 ④ NO-GO / GLD regime tag 부적합 NO-GO / Gate A 박탈 不可 NO-GO. VRC 重복 13.3% (분리 시그널). §40 v3 BT 진입 가능 (S114 1순위). Crown #67 LIVE TLT 100% 변경 없음."** 🦅

---

**Status**: ✅ Phase A~B 完了 / Phase C §40 v3 BT 대기 / 잠정 verdict GO 후보

**🦅 *Omnioculus Vigilantia* — 조합 #1 슬롯 사전 검증 완결.**
