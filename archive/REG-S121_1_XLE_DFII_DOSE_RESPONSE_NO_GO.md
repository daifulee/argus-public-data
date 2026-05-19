# REG-S112_1 — Volatility Regime Classifier (VRC) v0.1 결정적 NO-GO

**Session**: S112 #1  
**Date**: 2026-05-17 KST  
**Type**: 신규 메커니즘 후보 NO-GO (Cross-Asset Risk Allocation 첫 시도)  
**Verdict**: 🚨🚨 **NO-GO** — RULE 29 v2 룰 ①②④ FAIL + 격언 #91 v2 패턴 ④ 결정적 입증

---

## §1. 본질 요약

S110#2에서 신설된 **격언 #112 v2 #9 v2 룰 7** (Cross-Asset Risk Allocation 신규 패러다임 정착 의무)에 따른 첫 메커니즘 후보 (Volatility Regime Classifier, VRC)의 결정적 평가 cycle.

🎯 **결정적 결론**: VRC v0.1 NO-GO — Crown #67 baseline이 이미 VVIX 시그널 효과를 cross-asset 형식으로 capture하고 있어 신규 overlay의 effective alpha = 0 (또는 음수).

---

## §2. Phase 0 결정적 평가 — 4 후보 비교

| Rank | Candidate | Composite Score | 결정 |
|------|-----------|----------------|------|
| 🥇 1 | **Volatility Regime Classifier (VVIX)** | 8.85 | **Phase 1 진입** |
| 🥈 2 | Risk Budget Overlay | 7.80 | Phase 1 後속 |
| ❌ 3 | Conditional Rebalance (RRPONTSYD) | 3.65 | Reality check FAIL (t=-0.18) |
| ❌ 4 | Regime-Tag Rotation (T10Y3M/STLFSI) | 3.55 | Reality check FAIL (t<+0.67) |

✅ VRC가 정량적 결정적 우위 (t=+7.00, p<0.0001) — Phase 1 진입 결정.

---

## §3. Phase 1 결정적 설계 (VRC v0.1)

### 3.1 State Machine (Hysteresis)
```
NORMAL + VVIX > 110 → DEFENSIVE
DEFENSIVE + VVIX < 105 → NORMAL (margin 5)
```

### 3.2 Overlay 메커니즘
```
NORMAL: portfolio = Crown #67 Top5 (변경 없음)
DEFENSIVE: portfolio = (1-α) × Crown #67 Top5 + α × defensive_sleeve (equal weight)
```

### 3.3 Defensive Sleeve (PRIMA universe 정합)
TLT / GLD / XLU / XLV (4 active tickers)

### 3.4 Phase A Reality Check (BT_LONG 4843일)
- def-agg spread: +0.32%/day (전체), +0.13%/day (4-ticker active)
- t-stat: +7.00 (전체), +4.06 (4-ticker active)
- 패턴 ③ Robust Plateau (thr 98~130 모든 구간)
- SPY baseline 대비 Sharpe +0.597 → +0.854 (α=0.5)

---

## §4. Phase 3 결정적 BT 결과 (α Sweep)

### 4.1 v5.20A baseline (VRC OFF)

| Period | CAGR | Sharpe | MDD |
|--------|------|--------|-----|
| FULL | +34.07% | +1.633 | -21.73% |
| P1 | +28.98% | +1.418 | -21.73% |
| P2 | +33.85% | +1.630 | -19.09% |
| MID | +45.96% | +2.217 | -13.96% |

### 4.2 α Sweep BT (Δ vs baseline)

| α | avg ΔCAGR | min ΔCAGR | avg ΔSharpe | min ΔSharpe | avg ΔMDD |
|---|----------|----------|-------------|-------------|----------|
| 0.25 | **-0.789p** ❌ | **-2.339p** ❌ | +0.0781 ✅ | +0.0066 ✅ | +1.644p ✅ |
| 0.50 | **-1.647p** ❌ | **-4.701p** ❌ | +0.1383 ✅ | -0.0157 ❌ | +2.810p ✅ |
| 0.75 | **-2.573p** ❌ | **-7.083p** ❌ | +0.1638 ✅ | -0.0729 ❌ | +3.373p ✅ |
| 1.00 | **-3.565p** ❌ | **-9.483p** ❌ | +0.1361 ✅ | -0.1673 ❌ | +3.216p ✅ |

### 4.3 결정적 Period Decomposition (격언 #91 v2 패턴 ④ Temporal Heterogeneity)

| α | P1 ΔCAGR | P2 ΔCAGR | MID ΔCAGR |
|---|----------|----------|-----------|
| 0.25 | +1.188p ✅ | -1.732p ❌ | -2.339p ❌ |
| 0.50 | +2.331p ✅ | -3.592p ❌ | -4.701p ❌ |
| 0.75 | +3.428p ✅ | -5.576p ❌ | -7.083p ❌ |
| 1.00 | +4.479p ✅ | -7.676p ❌ | -9.483p ❌ |

🚨 **결정적 입증**: P1 alpha ✅, P2/MID alpha 결정적 손실 → 격언 #91 v2 패턴 ④ 결정적 사례.

---

## §5. 결정적 RULE 29 v2 6/6 평가

| α | 룰 ① | 룰 ② | 룰 ③ | 룰 ④ | 룰 ⑤ | Verdict |
|---|------|------|------|------|------|---------|
| 0.25 | ❌ | ❌ | ✅ | ✅ | ✅ | 3/5 → **NO-GO** |
| 0.50 | ❌ | ❌ | ✅ | ❌ | ✅ | 2/5 → **NO-GO** |
| 0.75 | ❌ | ❌ | ✅ | ❌ | ✅ | 2/5 → **NO-GO** |
| 1.00 | ❌ | ❌ | ✅ | ❌ | ✅ | 2/5 → **NO-GO** |

🚨🚨 **모든 α 값 NO-GO** — RULE 29 v2 룰 ① ② FAIL 결정적

---

## §6. 결정적 메타 학습 (3건 신설)

### 메타 1: Crown 내장 mechanism 重복 차단 결정적 의무
- Crown #67은 이미 VIX hysteresis + WTI gate + entry_TLT 면제 등 **cross-asset risk allocation 내장**
- VRC overlay = 重복 defensive injection → optimal portfolio 훼손
- 결정적 본질: **Phase A alpha (BT_LONG 평균) ≠ Phase B alpha (슬롯 경쟁)**
- 격언 #52 baseline 6번째 사례 (Phase A vs Phase B 정합)

### 메타 2: Temporal Heterogeneity 결정적 입증
- P1 (GFC era): VRC 결정적 ✅ (+1.19~+4.48p)
- P2/MID (2017~): VRC 결정적 ❌ (-1.73~-9.48p)
- 결정적 본질: 구조 변화 — Crown #67이 점진적 발전하며 이미 VVIX 시그널 효과 capture
- 격언 #91 v2 패턴 ④ baseline 사례

### 메타 3: Cross-Asset Overlay도 Crown 重복 mechanism 차단 의무
- Single-Asset Boost ❌ 패러다임은 옳음 (격언 #112 v2 #9 v2)
- 그러나 Cross-Asset Overlay도 Crown 重복 mechanism 차단 결정적 의무
- 신규 패러다임 등재 의무: **Crown 內 미存 mechanism만 채택**

---

## §7. 후속 연구 큐 (격언 #112 v2 #9 v2 룰 8 정합)

1. **VRC + Crown #67 V_HYST 중복 제거 후 isolated alpha 측정** cycle
2. 후보 #2 (Risk Budget Overlay continuous formula) 결정적 재검토
3. **Phase A causal v2.1 + Crown 內 mechanism 완전 cross-check protocol** 신설 (메타 1 결정적 baseline)

---

## §8. SSOT 영구화 결정적 권고

### 8.1 자동 회피 #10 신설 후보
**"Cross-Asset Overlay 등재 前 Crown 內 mechanism 완전 cross-check 의무"**

검증 절차:
1. VVIX/VIX/RRP 등 시그널이 이미 Crown 內 활용되는지 grep
2. 활용 시 → isolated alpha 측정 (Crown mechanism 제외 후 측정)
3. Cross-check 通過한 候보만 §B.9 v2 진입 허용

### 8.2 격언 #91 v2 패턴 ④ baseline 사례 추가
- REG-S112_1 = 패턴 ④ Temporal Heterogeneity 결정적 입증 첫 사례
- P1 alpha + P2/MID negative → 격언 #91 v2 4 패턴 中 ④번째 baseline 확립

---

## §9. 한 줄 결산 🦅

🌟 **"REG-S112_1 결정적 NO-GO: VRC v0.1 (VVIX hysteresis + Portfolio Target Overlay) — Phase A 결정적 alpha (t=+7.00) but Phase B 슬롯 경쟁에서 Crown #67 내장 mechanism (VIX hysteresis + WTI gate + entry_TLT 면제)과 결정적 重복 → 모든 α 값 RULE 29 v2 룰 ①② FAIL + 격언 #91 v2 패턴 ④ Temporal Heterogeneity 결정적 첫 입증 사례 (P1 alpha ✅ vs P2/MID negative ❌). 메타 학습 3건 신설 (Crown 重복 차단 / Temporal Heterogeneity / Cross-Asset Overlay protocol). 자동 회피 #10 후보 신설 (Cross-Asset Overlay 等재 前 Crown 內 mechanism cross-check 의무). 신규 패러다임 첫 cycle = NO-GO but framework + 메타 학습 결정적 baseline 정착."** 🦅

---

**Status**: ✅ REG 등재 완결  
**Crown #67 LIVE 변경**: 없음 (NO-GO)  
**Files**:
- `/home/claude/PRIMA_VRC_OVERLAY_v0_1.py` (prelim 코드)
- `/home/claude/PRIMA_v5_25_VRC.py` (통합 엔진, BT 결과 NO-GO)
- `/home/claude/phase3_alpha_sweep_results.json` (실측 BT 결과)
- `/home/claude/REG-S112_1_VRC_NO_GO.md` (본 등재)
