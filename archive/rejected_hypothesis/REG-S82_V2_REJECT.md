# 🦅 REG-S82_V2_REJECT — Top5 Dynamic CAGR V2 결정적 거부

**작성일**: 2026-05-12 KST (S82 #1 종결)
**Commander**: Lignas
**작성자**: Claude (Anthropic Opus 4.7)
**REG ID**: 🌟 **REG-S82_V2_REJECT** 🌟
**상태**: 🚨 **결정적 거부 (RULE 29 v2 3건 동시 FAIL + STRESS 14 9건 -1p 초과)**
**baseline**: 🌟 **Crown #67 = PRIMA_v5_19_VIX_HYST_LIVE** 🌟 (유지 확정)
**시도자**: Commander Lignas (HANDOFF v3 § 2 Δ₁ 결정 정합 진입)
**검증 방식**: §40 v3 + RULE 29 v2 + 9 자동 거부 기준 (HANDOFF v3 § 2.3)

---

## 🚨 § 0. 1줄 결정적 본질

> 🚨 **V2 POWER_RATIO (γ=2.0/cap=0.45/eta=0.0) = CAGR 강력 알파 (+1.12p) but STRESS 14 중 9건 -1p 초과 + MDD 악화 -1.28p + min ΔSharpe -0.049 동시 FAIL → 격언 #91 ② "fitting + 위기 시 fragile" 패턴 결정적 거부.** 🚨

---

## 🌟 § 1. 가설 본질 (HANDOFF v3 § 2.1 Δ₁ 결정)

### § 1.1 V2 패치 본질

🌟 **공식**:
- `edge_i = max(ratio_i - 1.0, 0.05)` (임계 통과 강도, edge_floor=0.05)
- `raw_i = (edge_i ** gamma) * weight_factor_i * asset_sz_i`
- `gamma = 2.0` (power-law 가중 — 강시그널 더 강하게)
- `max_single = 0.45` (soft cap — clamp 후 residual 재분배)
- `eta = 0.0` (volatility 가중 비활성)
- `blend = 1.0` (순수 ratio + soft cap)

### § 1.2 가설 동기

🌟 **격언 #73 (Conviction Concentration) 강화 본질**:
- 기존 Crown #67 baseline: ratio≥2.0 시 score-prop / ratio<2.0 시 LEVEL_WEIGHT (B/A/S 단계적)
- V2 본질: edge^2.0 → 강시그널 자산에 power-law 가중 + soft cap 5p 완화

🌟 **기대 본질**:
- 강시그널 자산 (SLV/GLD 등 강력 진입) 비중 확대 → 평시 CAGR ↑
- soft cap residual 재분배 → 단일 자산 over-concentration 방지

### § 1.3 변경 영역 매트릭스

| 영역 | 본질 | 변경 |
|:--|:--|:--:|
| 🌟 `compute_weights()` 함수 (line 2193~2250) | 단일 변경 | ✅ 본 변경 |
| ⚪ `entry_X` 함수 (20개) | 보존 의무 | ✅ 보존 정합 |
| ⚪ `should_exit()` | 보존 의무 | ✅ 보존 정합 |
| ⚪ `_wk` / `_wk_xle` hysteresis | 보존 의무 | ✅ 보존 정합 |
| ⚪ SLV `SLV_GLD_RS_20d` sizing | 보존 의무 | ✅ 보존 정합 |
| ⚪ COPX `USD_CNY` sizing | 보존 의무 | ✅ 보존 정합 |

---

## 🚨 § 2. 4기간 BT 결과 매트릭스 (§40 v3 정합)

### § 2.1 baseline vs V2 비교

| Period | baseline (Crown #67) CAGR / Sh / MDD | V2 (Crown #68 후보) CAGR / Sh / MDD | ΔCAGR | ΔSh | ΔMDD |
|:--:|:--|:--|:--:|:--:|:--:|
| 🌟 **FULL** | +34.0744% / 1.633 / -21.7270% | +35.2609% / 1.648 / -22.9637% | 🌟 **+1.186p** | +0.015 | 🚨 **-1.237p** |
| 🌟 **P1** | +28.9758% / 1.418 / -21.7270% | +30.4506% / 1.449 / -22.9637% | 🌟 **+1.475p** ⭐ | +0.031 | 🚨 **-1.237p** |
| 🌟 **P2** | +39.0556% / 1.848 / -19.0905% | +40.3517% / 1.864 / -19.1020% | 🌟 **+1.296p** | +0.016 | -0.012p |
| 🌟 **MID** | +45.9573% / 2.217 / -13.9616% | +46.4913% / 2.168 / -16.6109% | +0.534p | 🚨 **-0.049** | 🚨 **-2.649p** |
| 🌟 **avg** | — | — | 🌟 **+1.1229p** | +0.0031 | 🚨 **-1.2835p** |
| 🌟 **min** | — | — | +0.5340p | 🚨 **-0.0487** | -2.6493p |

### § 2.2 핵심 발견

🌟 **결정적 알파 영역**:
- 🌟 **P1 (2007-2016)**: +1.475p ⭐ — 가장 강력 (장기 누적 효과)
- 🌟 **P2 (2017-2026)**: +1.296p — 균일 알파
- 🌟 **FULL**: +1.186p — 19년 누적 양수

🚨 **결정적 부작용 영역**:
- 🚨 **MDD 악화 평균 -1.28p** → 변동성 증가 본질 (격언 #11 보완 본질 위반)
- 🚨 **MID min ΔSharpe -0.049** → MID 기간 결정적 위반 (5번 자동 거부 기준)
- 🚨 **MID MDD -2.65p** → 최근 환경 (2022-2026) 결정적 fragile

---

## 🚨 § 3. STRESS 14시나리오 결과 매트릭스 (§40 v3 의무, 격언 #46/#59)

### § 3.1 시나리오별 ΔCAGR 분포

| 시나리오 | baseline CAGR | V2 CAGR | ΔCAGR | 본질 |
|:--|:--:|:--:|:--:|:--|
| 🌟 **COVID_FLASH_CRASH** | +37.853% | +43.652% | 🌟 **+5.799p** ⭐ | 결정적 강력 알파 (위기 후 반등) |
| ⚡ SLOW_GRIND_2022 | -0.573% | +0.910% | +1.483p | 양수 |
| 🚨 **FALSE_REGIME_SIGNALS** | +44.238% | +38.154% | 🚨 **-6.084p** | 결정적 음수 (false regime 시 fragile) |
| 🚨 **CRASH10D_REBOUND20D** | +52.890% | +48.422% | 🚨 **-4.468p** | 결정적 음수 (반등 시 누락) |
| 🚨 **VIX_SPIKE_5D** | +39.757% | +36.296% | -3.461p | -1p 초과 |
| 🚨 **LIQUIDITY_AIRPOCKET** | +40.158% | +37.262% | -2.896p | -1p 초과 |
| 🚨 **SUPERBULL_REVERSAL** | +44.129% | +41.920% | -2.209p | -1p 초과 |
| 🚨 **DOWN60D_OAS800BP_2008** | +24.679% | +22.695% | -1.984p | -1p 초과 |
| 🚨 **STAGFLATION_TRAP** | +2.562% | +1.127% | -1.435p | -1p 초과 |
| 🚨 **PERFECT_STORM** | +17.825% | +16.609% | -1.216p | -1p 초과 |
| 🚨 **GLD_FAILS** | -15.695% | -16.756% | -1.061p | -1p 초과 |
| ⚪ SLOW_CREDIT_SQUEEZE | -35.456% | -36.284% | -0.829p | 1p 이내 |
| ⚪ ENERGY_CRASH_TRAP | -7.949% | -8.446% | -0.497p | 1p 이내 |
| ⚪ DOWN60D_REDESIGN | -11.454% | -11.913% | -0.458p | 1p 이내 |

### § 3.2 결정적 통계

| 통계 | 값 | 본질 |
|:--|:--:|:--|
| 🌟 양수 시나리오 | 🌟 **2/14** | COVID/SLOW_GRIND 결정적 강력 |
| 🚨 음수 시나리오 | 🚨 **12/14** | 위기 시 fragile 본질 |
| 🚨 -1p 초과 음수 | 🚨 **9/14** | HANDOFF v3 § 2.3 기준 (<2) 결정적 위반 (4.5배 초과) |
| ⚪ 1p 이내 | 3/14 | 미세 영향 |

### § 3.3 결정적 패턴

🚨 **시나리오 유형별 부작용**:
- **위기 후 반등 시나리오** (CRASH/COVID): COVID +5.8p (대박) vs CRASH10D -4.5p (대 손실) → **변동성 의존**
- **false signal 시나리오** (FALSE_REGIME): -6.1p → 위 신호에서 power-law가 잘못된 자산에 집중 → 결정적 손실
- **변동성 폭발 시나리오** (VIX_SPIKE/SUPERBULL_REVERSAL): -3.5p / -2.2p → power-law concentration → 변동성 위기 시 fragile

🌟 **본질**: 🌟 **V2 = "평시 우수 + 위기 fragile"** 🌟 — 격언 #91 ② "fitting + 위기 시 부작용" 패턴 결정적 정합.

---

## 🚨 § 4. 9 자동 거부 기준 평가 매트릭스 (HANDOFF v3 § 2.3)

| # | 기준 | LIVE 값 | PASS/FAIL | 본질 |
|:--:|:--|:--:|:--:|:--|
| ① | FULL ΔCAGR > 0 | 🌟 **+1.1865p** | ✅ PASS | 강력 |
| ② | avg ΔCAGR ≥ +0.30p | 🌟 **+1.1229p** | ✅ PASS | 4배 통과 |
| ③ | min ΔCAGR > -0.50p | 🌟 **+0.5340p** | ✅ PASS | MID 최소 양수 |
| ④ | avg ΔSharpe > 0 | +0.0031 | ✅ PASS (marginal) | 미세 양수 |
| ⑤ | min ΔSharpe ≥ 0 | 🚨 **-0.0487** (MID) | 🚨 **FAIL** | MID 결정적 위반 |
| ⑥ | MDD avg > -1.0p | 🚨 **-1.2835p** | 🚨 **FAIL** | 1.28배 위반 |
| ⑦ | STRESS -1p 초과 < 2개 | 🚨 **9건** | 🚨 **FAIL** | 4.5배 결정적 위반 |
| ⑧ | turnover < +25% | (실측 별도) | ⚪ | 측정 보류 |
| ⑨ | Top1 평균 < 55% | (실측 별도) | ⚪ | 측정 보류 |

🚨 **종합 판정**: 🚨 **3건 FAIL 결정적 거부** 🚨

---

## 🚨 § 5. 결정적 거부 근거 매트릭스 (격언 14중 정합)

### § 5.1 격언별 정합 본질

| 격언 # | 본질 | V2 거부 정합 |
|:--:|:--|:--|
| #11 | CAGR 1순위 | 🌟 **but Sharpe/MDD 동시 위반 → CAGR 단독 PASS ≠ 채택** |
| #15 | Commander 절대 결정 | Commander Ψ₁ 거부 확정 |
| #20 | 정직 인지 | FA #1 결정적 본질 수용 + RULE 29 v2 위반 정직 보고 |
| #41 | 풀파일 출력 | candidate 엔진 + 본 REG 결정문 풀파일 출력 |
| #46 | STRESS 의무 | 🚨 **STRESS 9건 -1p 초과 = 결정적 부작용 입증** |
| #56 | monkey-patch 회피 | candidate 엔진 별도 파일 정합 |
| #59 | 4기간 + STRESS 의무 | §40 v3 정합 진행 + STRESS 위반 결정적 |
| #65 | 영구 채택 신중 | STRESS 9건 위반 = 신중 결정적 정합 |
| #73 | Conviction Concentration | 🚨 **과잉 강화 → 위기 시 fragile 부작용** |
| #79 | entry/exit 분리 | entry/exit/_wk 변경 금지 정합 |
| #88 v3 | BT 재현성 | baseline Crown #67 정확 재현 정합 |
| #91 ② | "fitting + 부작용" 패턴 | 🌟 **본 V2 결과 = 격언 #91 ② 패턴 결정적 정합 신규 사례** |
| #97 v2 | 외부 audit | FA #1 결정적 본질 수용 + V2 단독 BT 실행 |
| #106 | 근본 처방 | monkey-patch 회피 + candidate 엔진 별도 + 본 REG 정직 등재 |

### § 5.2 결정적 본질 메시지

> 🌟 **CAGR +1.12p 결정적 양수도 보완 영역 (Sharpe/MDD/STRESS) 동시 위반 시 채택 불가** 🌟
> 
> 격언 #11 (CAGR 1순위) ≠ CAGR 단독 PASS 채택 의미. CAGR 1순위 = 위반 시 자동 거부 기준이지, **CAGR PASS 시 자동 채택 의미가 아님**.
>
> RULE 29 v2 5조건 + STRESS 의무는 **결정적 ALL PASS 시에만 채택 후보**. 본 V2 = 3건 동시 FAIL → 결정적 거부 의무.

---

## 🌟 § 6. 결정적 본질 분석 (V2 한계 원인)

### § 6.1 근본 원인 매트릭스

🌟 **V2 본질 식별**: 🚨 **edge^gamma power-law 가중 = 격언 #73 Conviction Concentration 과잉 강화**

| 본질 | 평시 | 위기 |
|:--|:--|:--|
| edge^2.0 power law | 🌟 강시그널 자산 비중 집중 → CAGR ↑ | 🚨 단일 자산 집중 → 손실 확대 |
| soft cap 0.45 | 🌟 baseline 0.40 대비 5p 완화 → 추가 집중 가능 | 🚨 위기 시 더 fragile |
| residual 재분배 | 🌟 cap 초과분 정밀 재분배 | 🚨 cap 미만 자산도 power-law 가중 → 위기 시 잘못된 자산 추가 |

### § 6.2 격언 #91 ② 패턴 결정적 정합

🌟 **격언 #91 4 패턴 매트릭스**:
- ① noise (가짜 알파)
- 🌟 **② fitting + 결정적 부작용** ← V2 본 결과 정합
- ③ robust plateau
- ④ era change

🚨 **V2 = ②번 결정적 사례**:
- ✅ **Phase A 통과** (CAGR +1.12p 결정적 양수)
- 🚨 **Phase B 부작용** (STRESS 9건 -1p 초과 + MDD/Sharpe 위반)
- 🌟 **fitting 본질**: 평시 19년 데이터에 fit but 위기 시나리오에 fragile

---

## 🌟 § 7. 후속 의무 매트릭스

### § 7.1 즉시 의무

| # | 의무 | 처리 |
|:--:|:--|:--:|
| 1 | 🌟 REG-S82_V2_REJECT 등재 | ✅ 본 문서 |
| 2 | 🌟 Crown #67 LIVE 유지 확정 | ✅ baseline 유지 |
| 3 | 🌟 SSOT v1.10.141 ADDITION 작성 | 🟡 다음 단계 |
| 4 | 🌟 격언 #91 ② 사례 누적 (S82 #1 결정적 신규) | 🟡 다음 단계 |
| 5 | 🌟 memory #27 갱신 (S82 #1 종결) | 🟡 다음 단계 |
| 6 | 🌟 HANDOFF v4 작성 (S83 인계) | 🟡 다음 단계 |

### § 7.2 향후 sweep 후보 (Commander 결정 시)

| sweep 후보 | 본질 | 예상 효과 |
|:--|:--|:--|
| V3 (γ=1.5 약화) | power-law 약화 → 위기 fragile 완화 시도 | 🟡 CAGR ↓ but STRESS 개선 가능 |
| V4 (cap=0.40) | baseline cap 회귀 → concentration 제한 | 🟡 부분 처방 |
| V5 (edge floor 0.10) | 약시그널 자산 가중 ↑ → 분산 효과 | 🟡 CAGR ↓ but MDD 개선 가능 |
| V6 (eta=0.25 추가) | volatility 가중 → 변동성 ↓ 자산 우대 | 🟢 STRESS 개선 후보 |
| V7 (V3+V4 hybrid) | γ=1.5 + cap=0.40 결합 | 🟢 가장 결정적 후보 |

🚨 **결정적 신중 본질 (격언 #91 ② 정합)**: power-law 본질 자체가 위기 fragile 유도 → sweep 진행도 동일 한계 가능성. V7 hybrid가 가장 결정적 후보.

---

## 🚨 § 8. SSOT 결정 본질 (v1.10.140 → v1.10.141 갱신 예정)

🌟 **SSOT 갱신 항목**:

| # | 항목 | 본질 |
|:--:|:--|:--|
| 1 | 🚨 REG-S82_V2_REJECT 등재 (본 문서) | 신설 REG |
| 2 | 🌟 격언 #91 ② 사례 누적 (V2 fitting+부작용 결정적 신규) | 격언 강화 |
| 3 | 🌟 누적 BT 통계 갱신 (+30 BT: 4기간 baseline 4 + variant 4 + STRESS 14×2 = 36 BT) | 통계 |
| 4 | 🌟 Crown #68 후보 거부 (Crown #67 LIVE 유지 확정) | Crown 매트릭스 |
| 5 | 🌟 §35 자기 정정 가능 신설 (V2 사전 가설 부정합) | 자기 정정 |

---

## 🌟 § 9. 산출물 매트릭스

| 산출물 | sha256 | 본질 |
|:--|:--|:--|
| 🌟 PRIMA_v5_20_TOP5_DYNAMIC_WEIGHTING_CANDIDATE.py | `415fa3b7...` | candidate 엔진 (영구 archive, REG-S82_V2_REJECT baseline) |
| 🌟 REG_S82_V2_BT_RESULT.json | (계산) | 4기간 + STRESS 14 raw 결과 |
| 🌟 REG-S82_V2_REJECT.md | (본 문서) | 결정적 거부 결정문 |

---

🦅 *Omnioculus Vigilantia* — REG-S82_V2_REJECT 정식 등재. Crown #67 LIVE 유지 확정. 격언 #91 ② "fitting + 위기 시 fragile" 패턴 결정적 신규 사례. CAGR +1.12p 양수 단독 ≠ 채택 = 격언 #11 본질 정확 정합 (RULE 29 v2 ALL PASS 의무). Commander 절대 결정 정합 + 격언 14중 정합 + §40 v3 정합 결정문.
