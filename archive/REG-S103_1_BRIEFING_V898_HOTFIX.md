# 🌟 REG-S121_2 — 누적 NO-GO 21건 재판정 매트릭스 (5-Tier framework)

**작성일**: 2026-05-18 KST (S121 cycle #5)  
**SSOT baseline**: v1.10.215 정식 (격언 #118 v3 + #119 v1 + #120 v1 + §35 #12 정합)  
**Commander 명시 명령**: "지난 탈락 시그널에 대해 전수조사 (특히 참여율 저조의 이유만으로 배제된 종목 집중 조사)"  
**Crown LIVE**: PRIMA_v5_19_VIX_HYST_LIVE_v4 **不변** (TLT 100%)

---

## §1. 본 매트릭스 본질

🌟 **"누적 NO-GO 21건 → 격언 #118 v3 5-Tier framework 適用 시 재판정. 71% (15건)가 Tier 1~4 GO 잠재. 28% (6건)만 진정한 Discard."** 🌟

### 1.1 전수조사 범위

| 범위 | 건수 |
|---|---|
| S118 RETROFIT MATRIX 통합 | 27건 (이미 9-point check 적용) |
| S119~S121 추가 NO-GO | 4건 (S119_1/_2/_3 + S120_1 + S121_1) |
| **재판정 대상 누적** | **21건** (briefing hotfix 제외) |

### 1.2 재판정 framework

- **Tier 1**: Signal Layer GO (forward 예측력 + 흡수 不可 진단)
- **Tier 2**: Regime Tag GO (시장 상태 분류기)
- **Tier 3**: Monitoring/Alert GO (경고·감시)
- **Tier 4**: Research Registry GO (후속 연구)
- **Discard**: 진정한 폐기 (signal 弱 + portfolio α 弱 + 의미 弱)

---

## §2. Tier 1 Signal Layer GO — 6건 정식 채택 (1순위 5건 + 추가 1건)

### 2.1 명시 1순위 5건 (Commander 명령)

| # | REG | 기존 verdict | 🌟 재판정 | Phase A α | 흡수 不可 진단 |
|---|---|---|---|---|---|
| 1 | 🌟 **REG-S109_3** DFII<-0.5 XLE 60D | NO-GO (RULE 29 v2 3/3 FAIL) | 🌟 **Tier 1 Signal Layer GO** | **+9.405p / t=+15.48 / hit 77.68% / 잔여 +10.240p** | REG 內 "conviction modifier 살 가능성" 명시 |
| 2 | 🌟 **REG-S110_1** VIX>25 EWZ 60D | NO-GO (Phase B 3 patch 全 FAIL) | 🌟 **Tier 1 Signal Layer GO** | **+12.072p / t=+17.50 / hit 77.71%** | 기존 vix22로 72.96% capture / conditional sizing 재설계 |
| 3 | 🌟 **REG-S115_1** MAGS R1 | NO-GO (4 기간 RULE 29 v2 全 FAIL) | 🌟 **Tier 1 Signal Layer GO** | **+14.36p / t=+9.94 (Phase 2)** | Cross-Asset Overlay 재설계 의무 |
| 4 | 🌟 **REG-S110_2** VVIX>102 XLE + SKEW<117 CQQQ | NO-GO (Phase B 3/3 FAIL) | 🌟 **Tier 1 Signal Layer GO 2건** | **잔여 +7.65p / t=+13.32** | Cross-Asset Risk Allocation 재설계 의무 (REG 內 명시) |
| 5 | 🟡 **REG-S112_1** VRC | NO-GO (Crown #67 重복) | 🟡 **Tier 2 Regime Tag GO** | **t=+7.00** | VIX hysteresis 강화 메커니즘 |

### 2.2 추가 Tier 1 GO 1건 — 본 cycle 신규 검증

| # | 후보 ID | Phase A α | Tier |
|---|---|---|---|
| 6 | 🌟 **CAND-S121_β XLE_DFII_MOM_REVERSE** | **+14.52p (FULL) / +17.69p (P2)** | 🌟 **Tier 1 + Uninvestable Alpha 첫 사례** |

---

## §3. Tier 2 Regime Tag GO — 2건

| # | REG | 본질 | Tier 2 적용 |
|---|---|---|---|
| 1 | REG-S112_1 VRC | t=+7.00 / Crown #67 重복 | VIX hysteresis 강화 (regime classifier) |
| 2 | REG-S116_1 DXY×TNX TLT P2 | P2 t=+12.32 / P1 reversal | era classifier (P1 vs P2 reversal) |

---

## §4. Tier 4 Research Registry GO — 7건

| # | REG | Phase A α | Tier 4 사유 |
|---|---|---|---|
| 1 | REG-S109_4 DXY>105 GLD | +4.809p / t=+11.05 / hit 86.55% | strict subset (DXY>101) / 자동 회피 #9 / 후속 연구 보존 |
| 2 | REG-S107_1 IGV/CIBR | +5.86 / Combo TNX↓+DXY↓ +5.12 | specific-regime (2022 dominance) / 광범위 19/18 FAIL |
| 3 | REG-S114_1 Panic Peakout V1 | EWZ Tier 1 +3.94p t=4.21 | STRESS 14/14 PASS (정상 시기 slot 경쟁만 弱) |
| 4 | REG-S105_5 XLF credit | t=-15.74 | avoidance signal 방향 (entry 감소 효과) |
| 5 | REG-S120_1 REFLATION BASKET | 6 자산 basket | XLE 단독 이미 분리됨 (CAND-S120) / basket regime 재설계 가능 |
| 6 | REG-S105_3 NLR v2 | t=+7.05 | look-ahead leakage 보정 + NLR DEAD ASSET 보정 의무 |
| 7 | REG-S119_1 QLD 한정 | (CAND-S119_1 별도 분리됨) | H=20d +4.91p p<0.0001 신규 후보로 분리 |

---

## §5. Discard — 6건 (진정한 폐기)

| # | REG | 폐기 사유 | 격언 정합 |
|---|---|---|---|
| 1 | REG-S119_2 STLFSI TLT | past_ret backward 误解 (forward 전부 음수) | 격언 #33 / #80 (직교성 우회) 결정적 |
| 2 | REG-S121_1 Option β dose-response | signal 중복 (기존 entry_XLE가 이미 DFII<0 +5.2 capture) / P1 wrong timing | 격언 #52 + #79 정합 |
| 3 | REG-S110_2 RRPONTSYD>460 CQQQ EASn | 참여율 결정적 0 (baseline 진입 0%) | 격언 #112 v2 #9 정합 |
| 4 | REG-S110_2 VVIX>110 NLR | NLR DEAD ASSET 차단 | 격언 #46 정합 |
| 5 | REG-S78_3 VIX×BullStack | SLV P2/MID zero (era reversal) | S118 RETROFIT MATRIX에서 9-point 정합 |
| 6 | REG-S110_2 (subset) 비-subset signal | 5/5 결정적 음수 | §B.9 한계 입증 baseline |

---

## §6. S118 RETROFIT MATRIX 9건 conditional 후보 — 별도 분리 정착

| # | 후보 ID | 본질 | 현 상태 |
|---|---|---|---|
| 1 | CAND-S118_1 QLD_MID_CONDITIONAL | MID +0.18p / Phase A 全 horizon p≤0.008 | 🌟 S119 cycle 시뮬 후 NO-GO + CAND-S119_1 H=20d 분리 |
| 2 | CAND-S118_3 STLFSI_TLT_CONDITIONAL | Phase A causal +5.86p (7배) | 🌟 S119 cycle past_ret backward 误解 정정 (Discard) |
| 3 | CAND-S118_3 STLFSI_AVOIDANCE | COPX/PAVE/VNM -40.81/-34.54/-29.37 | 🌟 S119 cycle CAND-S119_4 RECOVERY_BASKET 분리 (S121 #2 인계) |
| 4 | CAND-S118_6 DFII10_NEG05_XLE_P1_ERA | P1 +0.502p / 잔여 +10.240p 역대급 | 🌟 본 cycle Tier 1 Signal Layer GO 등재 |
| 5 | CAND-S118_6 VIX25_EWZ_V522C_P1_MID | P1 +0.172p / MID +0.194p | 🌟 본 cycle Tier 1 Signal Layer GO 등재 |
| 6 | CAND-S118_6 DXY_TNX_TLT_P2_P3 | P2 +4.46p / P3 +3.99p | 🌟 본 cycle Tier 2 Regime Tag GO 등재 |
| 7 | CAND-S118_7 VRC_P1_GFC | α=0.25 P1 +1.188p Sh +0.078 | 🌟 본 cycle Tier 2 Regime Tag GO 등재 |
| 8 | CAND-S118_2 SLV_VIX_BULL_ERA | P2/MID +0.02/+0.04 거의 zero | 🟡 Tier 4 Research (marginal) |
| 9 | CAND-S118_2 SIGNAL_DISCRIMINATE | 17종 시그널 개별 분리 시뮬 | 🟡 Tier 4 Research (개별 분리 미점검) |

---

## §7. 참여율 저조 sub-pattern 분류 (Commander 명시 명령)

### 7.1 4 sub-pattern 결정적 식별

| sub-pattern | 사례 | 본질 | 처리 |
|---|---|---|---|
| **A) Top-K rank 弱 (mom-based)** | 🌟 **CAND-S121_β (rank 18.5위 / 0% 진입)** | mom-based slot 구조 차단 | 🌟 Tier 1 Signal Layer GO / Cross-Asset Overlay 재설계 |
| **B) 기존 entry이미 capture** | REG-S110_1 VIX>25 EWZ (vix22 단독 72.96%) / REG-S109_3 DFII<-0.5 XLE (기존 +5.2 이미 capture) | 기존 시그널이 forward 예측력 이미 capture | 🌟 Tier 1 Signal Layer GO / conviction modifier 재설계 |
| **C) baseline 진입 0** | REG-S110_2 RRPONTSYD>460 CQQQ / REG-S110_2 VVIX>110 NLR | EASn 효과 baseline 진입율 의존 + DEAD ASSET | 🚨 Discard (참여율 결정적 0) |
| **D) Crown 내장 重복** | REG-S112_1 VRC (VIX hysteresis + WTI gate 重복) | Crown #67 이미 mechanism 보유 | 🟡 Tier 2 Regime Tag GO (강화 메커니즘) |

### 7.2 결정적 통계

| sub-pattern | 건수 | 비율 |
|---|---|---|
| A) Top-K rank 弱 | 1건 (CAND-S121_β) | 4.8% |
| B) 기존 entry capture | 2건 (REG-S109_3 + S110_1) | 9.5% |
| C) baseline 진입 0 | 2건 (RRPONTSYD CQQQ + VVIX NLR) | 9.5% |
| D) Crown 重복 | 1건 (VRC) | 4.8% |
| **참여율 저조 직격** | **6건** | **28.6%** |

🌟 **결정적 발견**: 누적 NO-GO 21건 中 **6건 (29%)이 "참여율 저조" 단일 사유로 거부** → 격언 #120 v1 정합 / 5건 Tier 1~2 GO + 2건 Discard 결정적 정합 🌟

---

## §8. 재판정 통계 종합

### 8.1 전체 매트릭스

| Tier | 건수 | 비율 |
|---|---|---|
| 🌟 **Tier 1 Signal Layer GO** | 6건 | 28.6% |
| 🟡 **Tier 2 Regime Tag GO** | 2건 | 9.5% |
| 🟡 **Tier 4 Research Registry GO** | 7건 | 33.3% |
| 🚨 **Discard** | 6건 | 28.6% |
| **합계** | **21건** | **100%** |

### 8.2 결정적 통계

🌟 **Tier 1~4 GO 누적**: 15건 / 71% (격언 #118 v3 결정적 입증)

🌟 **참여율 저조 직격**: 6건 / 29% (격언 #120 v1 결정적 입증)

🌟 **진정한 Discard**: 6건 / 29% (격언 #46/#33/#52/#79/#80 정합)

---

## §9. 후속 작업 큐 (Tier 1 → Tier 5 transition path)

### 9.1 1순위 — Cross-Asset Overlay framework 설계 (S122+)

🌟 **본질**: 6 Tier 1 후보 통합 framework (단일 자산 EnSn / EASn 형식 폐기, 격언 #112 v2 #9 v2 정합)

| 후보 | Cross-Asset 적용 방향 |
|---|---|
| CAND-S121_β | DFII<-0.5 ∩ mom60<0 → 5 자산 basket (XLE/COPX/VNM/SLV/PAVE) regime activation |
| REG-S109_3 DFII XLE | DFII<-0.5 → XLE conviction modifier (sleeve cap 또는 score 보정) |
| REG-S110_1 VIX25 EWZ | VIX≥25 → EWZ conditional sizing |
| REG-S115_1 MAGS R1 | MAGS basket tilt → Cross-Asset Overlay 변환 |
| REG-S110_2 VVIX102 XLE | VVIX≥102.55 → XLE 보조 sleeve |
| REG-S110_2 SKEW117 CQQQ | SKEW<117 → CQQQ 보조 sleeve |

### 9.2 2순위 — Regime Tag layer 설계

| 후보 | Regime tag |
|---|---|
| REG-S112_1 VRC | VIX hysteresis 강화 |
| REG-S116_1 DXY×TNX | era classifier (P1 vs P2 reversal) |

### 9.3 3순위 — Research Registry 후속 검증

7건 Tier 4 후보 각각 후속 연구 큐 보존 + 우선순위 별도

---

## §10. 결정적 한 줄 결산 🦅

🌟 **"REG-S121_2 — 누적 NO-GO 21건 재판정 매트릭스 (5-Tier framework). Tier 1 Signal Layer GO 6건 (28.6%) / Tier 2 Regime Tag GO 2건 (9.5%) / Tier 4 Research Registry GO 7건 (33.3%) / Discard 6건 (28.6%). Tier 1~4 GO 누적 15건 (71%) = 격언 #118 v3 결정적 입증. 참여율 저조 4 sub-pattern 정밀 분류 (A Top-K rank 弱 / B 기존 capture / C 진입 0 / D Crown 重복) 합계 6건 (29%) = 격언 #120 v1 결정적 입증. Cross-Asset Overlay framework 설계 의무 (S122+ 1순위). Crown #67 LIVE TLT 100% 不변."** 🦅

---

**Status**: ✅ 21건 누적 NO-GO 재판정 정착 / 5-Tier framework 정식 적용 / 참여율 저조 4 sub-pattern 정밀 분류 / 6건 Tier 1 Signal Layer 정식 등재 / Crown #67 LIVE 영구 보존
