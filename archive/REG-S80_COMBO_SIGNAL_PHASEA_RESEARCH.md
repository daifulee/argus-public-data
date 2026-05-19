# REG-S107_1 — IGV AI Software Monetization Research 자동 거부

**작성**: S107 종결 (2026-05-17 KST)
**Commander**: Lignas
**REG 분류**: P0 (Phase A 자동 폐기, 격언 #19 정합)
**격언 #112 v2 사례**: **#7 신규 등재** (Specific-Regime Asset 카테고리)
**선례**: REG-S106_1 (Universe Pruning 사례 #6)

---

## 🎯 §1. 한 줄 결론

🌟 **"IGV는 specific-regime asset이며 generalizable robust alpha source가 아니다. NLR replacement 후보 자격 부재."** 🌟

→ **Phase A 단계 자동 폐기**. Phase B (OOS/Walk-Forward) 진입 차단.

---

## 📊 §2. 검증 절차 (Phase A 0순위 + A.1 + A.2 + 0.5 + A.3)

| Phase | 작업 | 결과 |
|-------|------|------|
| 0순위 | QQQM/SMH/CIBR/SPY correlation 사전 진단 | 🟡 YELLOW (Pearson 0.29 / Spearman 0.85 / CIBR 0.91) |
| A.1 | RS Signal Discovery (4 pair × 3 window = 12) | 8건 PARTIAL (t-stat 강, mono 0/8) |
| A.2 | CIBR 차별화 검증 | 🚨 절대 우위 부재 + 선별 marginal (40D t=+2.27) |
| 0.5 | 격언 #87 Yearly stability (RS 상위 4건) | 🔴 **4/4 FAIL** |
| A.3 | Macro Signal (TNX/DFII10/DXY/MOVE/Combo) 15건 | 🔴 14 FAIL + 🟡 1 BORDER |
| **합계** | **19건 검증** | 🟢 **0** / 🟡 **1** / 🔴 **18** (95% FAIL) |

---

## 🚨 §3. 결정적 부정 신호 5건

### 3.1 데이터 contamination 2건 확정

| Anomaly | 본질 | 영향 |
|---------|------|------|
| QQQM 합성 데이터 | 2007~2020-10-12 백필 추정 (실제 출시 2020-10-13) | 5.5년 클린 기간만 사용 가능 |
| 2026-03-25 spike | QQQM 240→588 (+144.5%), PDBC 사례 정합 | 1일 제외 + BT_LONG_v5 신뢰성 의문 |

### 3.2 RS Signal Yearly Stability 4/4 FAIL

| RS Pair × Window | 전체 t-stat | 음수 연도 | sig_neg | 결정적 약점 |
|------------------|------------|---------|---------|------------|
| IGV/SMH RS 40D | +8.02 (최강) | 1/6 (2020) | 1건 | mono 실패 + 2020 t=-6.13 |
| IGV/CIBR RS 60D | +5.86 (hit 69.4%) | 2/6 | 0 | 2021/2024 spread 음수 |
| IGV/SMH RS 60D | +5.72 | 2/6 | **2건** | 시기별 방향 반대 (2020 -15%, 2025 +19%) |
| IGV/QQQM RS 40D | +5.70 | 3/6 | **2건** | 6년 중 3년 음수 (가장 불안정) |

→ 🌟 **2021 강세장 효과 의존 가짜 alpha** 🌟

### 3.3 Macro Signal Yearly Stability 14/15 FAIL

| Macro Signal × Window | 전체 t-stat | 평가 | 결정적 약점 |
|----------------------|------------|------|-----------|
| TNX↓ 60D | +6.45 | 🔴 FAIL | +yr 3/6, sig_neg 1 |
| DFII10↓ all | -0.11 ~ +1.78 | 🔴 FAIL | spread 약함 |
| **DXY↓ 40D** | **+7.86** | 🔴 FAIL | +yr 5/6 매력적, sig_neg 1 |
| DXY↓ 60D | +9.79 | 🔴 FAIL | +yr 4/6, sig_neg 1 |
| MOVE↑ all | -3.61 ~ +0.39 | 🔴 FAIL | sig_neg 다수 |
| 🆕 **Combo TNX↓+DXY↓ 40D** | **+5.12** | 🟡 **유일 BORDER** | 2022 dominance (+8.78% t=+4.53) |

### 3.4 2022 Dominance — Combo BORDER 후보 결정적 약점

Combo TNX↓+DXY↓ 40D 연도별 spread:

| 연도 | spread | t-stat | 비중 |
|------|--------|--------|------|
| 2020 | -1.21% | -0.64 | 약 음수 |
| 2021 | +0.99% | +0.68 | 약 양수 |
| **2022** | 🌟 **+8.78%** 🌟 | **+4.53** | 🚨 **80% 견인** |
| 2023 | -0.57% | -0.66 | 약 음수 |
| 2024 | +1.57% | +1.13 | borderline |
| 2025 | +3.31% | +1.87 | 양수 |

→ 🌟 **2022 dovish pivot 단일 regime 의존** 🌟

### 3.5 CIBR 절대 우위 부재

| Window | IGV - CIBR forward return | t-stat | win-rate |
|--------|--------------------------|--------|----------|
| 20D | -0.459% | -4.46 | 44.5% |
| 40D | -0.933% | -6.60 | 45.7% |
| 60D | -1.086% | -6.35 | 45.5% |

→ 🌟 **CIBR이 평균적으로 IGV를 능가** 🌟. IGV는 NLR replacement 후보 자격 부재.

---

## 🎯 §4. 자동 거부 결정 (5중 부정 신호 정합)

| # | 부정 신호 | 위반 격언 |
|---|---------|---------|
| 1 | 데이터 contamination 2건 | 격언 #75 (검증 의무) |
| 2 | 19/19 alpha 부재 (RS 4 + Macro 14 + 1 BORDER) | 격언 #87 (n-distribution stability) |
| 3 | 2022 dominance (단일 regime 의존) | 격언 #112 v2 사례 #1~6 누적 |
| 4 | CIBR 절대 우위 부재 | NLR replacement 자격 미충족 |
| 5 | mono 0/8 + 시기별 방향 반대 | trend-following alpha 부재 |

🌟 **결정**: Phase A 단계에서 자동 폐기. Phase B/C/D/E 진입 차단. 🌟

---

## 📊 §5. 격언 #112 v2 사례 #7 신규 카테고리

**카테고리 명**: 🆕 **Specific-Regime Asset 자동 거부**

**정의**: 자산이 특정 regime (특정 연도/macro condition)에 강한 alpha를 보이지만, regime 외 일관성 부족으로 generalizable robust alpha 부재 시 자동 폐기.

**판별 기준**:
1. Phase A.1 단일 측정 t-stat 강 (≥ +2.0)
2. 격언 #87 yearly stability 5/6 이상 양수 + sig_neg 0건 미충족
3. 단일 연도 spread가 전체 spread의 50% 초과 견인

**자동 회피 영역** (S107 신설):
- Specific-regime asset (예: 2021 강세장 의존 / 2022 dovish pivot 의존)

---

## 🌟 §6. ARGUS Alpha 본질 정밀 정의 (S107 학습)

🌟 **ARGUS alpha = breadth × signal-driven × regime-robust** 🌟

| 성분 | S105/S106 정량 | S107 신규 |
|------|----------------|-----------|
| breadth | +11.32p (S106) | — |
| signal-driven | +9.72p (S106) | — |
| **regime-robust** | 암묵적 | 🆕 **명시 정의** (격언 #112 v2 사례 #7) |

→ 본 정의로 Crown #67의 alpha 본질이 정밀하게 분해됨.

---

## 📋 §7. S107 누적 자동 회피 영역

| 사례 | 영역 | 손실 |
|------|------|------|
| #1 | score multiplier | OOS -0.32p |
| #2 | threshold tweak | micro -0.007p |
| #3 | self-ref signal | 5/5 폐기 |
| #4 | external EM signal | 5/5 폐기 |
| #5 | XLF Credit Decomposition | 5/5 폐기 |
| #6 | Universe Pruning (N<15) | 6/6 폐기 |
| 🆕 **#7** | **Specific-Regime Asset (IGV)** | **19건 중 95% FAIL** |

---

## 📋 §8. 검증 산출물

| 파일 | Phase |
|------|-------|
| `S107_PhaseA0_IGV_QQQM_PreDiagnosis.json` | 0순위 raw |
| `S107_PhaseA0_IGV_QQQM_PreDiagnosis_v2_clean.json` | 0순위 클린 |
| `S107_PhaseA1_A2_results.json` | A.1 + A.2 |
| `S107_PhaseA_Aphorism87_YearlyStability.json` | 0.5 yearly |
| `S107_PhaseA3_MacroSignal.json` | A.3 macro |

---

## 🦅 §9. 결정 권고

🌟 **본 REG는 S107 종결 시점 정식 등재된다.** 🌟

→ SSOT v1.10.X+1 update 시 격언 #112 v2 사례 #7 통합
→ S108 진입 시 자동 회피 영역에 "Specific-Regime Asset" 추가
→ IGV는 ARGUS universe 등재 영구 차단 (REG-S107_1 정합)

**다음 우선순위 (S108)**:
1. Combo Signal Phase A (REG-S80 6 combinations)
2. Net Liquidity EnSn (TLT+NL, REG-S80)
3. Memory snapshot S68 overdue 해소

---

**작성**: S107 종결 (2026-05-17 KST)
**REG**: 정식 등재
**선례**: REG-S106_1 (사례 #6) + REG-S105_3 (NLR DEAD) + REG-S105_5 (XLF Credit) + REG-S80 (Dead EnSn audit)

✅ **기만 차단 5조 통과**
