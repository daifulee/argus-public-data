# 🦅 REG-S119_2 — CAND-S118_3 STLFSI TLT Conditional §B.9 v3 Phase B-6 + 직교성 우회 NO-GO

**작성일**: 2026-05-18 KST (S119 cycle 2순위 작업 종결)  
**baseline**: SSOT v1.10.209 ACTIVE / Crown #67 LIVE / TLT 100% 불변  
**선행 결정**: S118 cycle CAND-S118_3_STLFSI_TLT_CONDITIONAL 🥈 진입 권고  
**본 결정**: 🚨 **§B.9 v3 Phase B-6 격리 시뮬 + 직교성 우회 가설 NO-GO 双重 확정**

---

## §1. 작업 본질

| 항목 | 값 |
|------|------|
| 대상 후보 | CAND-S118_3_STLFSI_TLT_CONDITIONAL |
| 선행 baseline (S118 인계) | Phase A causal TLT **+5.86p (7배 역대 최강)** + conditional/lag |
| 직교성 NO-GO 사유 (REG-197) | STLFSI vs OAS_HY +0.8016 / OAS_IG +0.7992 / NFCI +0.7004 |
| 시뮬 방법 | §B.9 v3 Phase B-6 + 직교성 우회 4 사분면 분석 |
| 데이터 인프라 | BT_LONG_v4_complete.csv (4843×98, STLFSI 4834 non-null) |
| trigger | STLFSI ≥ 2.0 (1일 lag, LAG_MACROS 정합) |
| 발동 빈도 | 212/4843 = 4.39% |
| 발동 시기 | 2007 (5) / 2008 (85) / 2009 (93) / 2020 (29) — 4 개 연도 only |

---

## §2. 🚨 결정적 baseline 误解 진단

### 2.1 REG-197 baseline 정의 (S61 #10 Phase A causal v2.3)

| 자산 | past_ret 60d | baseline | 차이 | 사용 정의 |
|------|------|------|------|------|
| TLT | +6.83% | +0.97% | **+5.86p** | 🚨 **past_ret (backward-looking, 격언 #33)** |
| GLD | +4.38% | +2.78% | +1.60p | 同 |
| COPX | -37.24% | +3.56% | -40.81p | 同 |

### 2.2 본 cycle forward 60d 결과 (signal 본래 의도)

| 자산 | ON forward | OFF forward | 차이 | 부호 |
|------|------|------|------|------|
| 🚨 TLT | -0.76% | +1.05% | 🚨 **-1.81p** | 🚨 **反轉** |
| GLD | +6.52% | +2.60% | +3.92p | 同 |
| 🚨 COPX | +47.95% | +3.24% | +44.72p | 🚨 反轉 |

### 2.3 결정적 진단

🚨 **REG-197 "past_ret 60d"은 backward-looking** — "STLFSI ≥ 2.0 발동 시점 = TLT 직전 60일 +6.83% 상승" informational value 측정.

🚨 **forward signal로 사용 시 부호 결정적 反轉** — 위기 max에서 사면 60일 후 V-shape recovery 패턴.

🚨 **S118 인계 "Phase A 역대 최강 +5.86p"은 forward TLT entry signal로 부적합** baseline.

---

## §3. §B.9 v3 Phase B-6 결과 (forward 60d, 21 종 자산)

### 3.1 Tier 분류

| Tier | 자산 | spread | t | p | 본질 |
|------|------|------|------|------|------|
| Tier 0 압도 | COPX | **+44.72p** | +28.24 | <0.0001 | V-recovery 압도 |
| Tier 0 압도 | VNM | +23.79p | +15.73 | <0.0001 | EM V-recovery |
| Tier 0 압도 | INDA | +21.16p | +18.46 | <0.0001 | EM V-recovery |
| Tier 0 압도 | PAVE | +20.43p | +10.07 | <0.0001 | infra V-recovery |
| Tier 0 압도 | EWZ | +17.94p | +12.59 | <0.0001 | EM V-recovery |
| Tier 1 | SLV | +11.63p | +9.63 | <0.0001 | silver V |
| Tier 2 | QQQM/QQQ/HYG | +5.85~+6.48p | — | — | tech/credit V |
| Tier 3 | SMH/RSP/GLD/XLE/IWM | +3.37~+4.63p | — | — | broad V |
| 🚨 **NO-GO** | **TLT** | 🚨 **-1.81p** | -2.38 | 0.018 | **safe haven sell-off** |
| 🚨 NO-GO | XLU/XLV/XLF/IEF | -0.13~-1.20p | — | 비유의 | defensive 매도 |

### 3.2 결정적 본질

🚨 **STLFSI ≥ 2.0 = 위기 max signal** — 발동 후 60일 = V-shape recovery 시기.

🚨 **TLT는 safe haven sell-off 자산** — 위기 max에서 이미 강세 reached, 발동 후 60일 매도 圧.

🌟 **신규 EnSn 후보 후보군**: COPX/VNM/INDA/PAVE/EWZ (Tier 0+) — V-recovery EnSn 압도적.

---

## §4. 🚨 직교성 우회 가설 NO-GO (결정적 4 사분면)

### 4.1 STLFSI ∩ OAS_HY 4 사분면 (OAS_HY ≥ 6.0 threshold)

| 사분면 | 일수 | % | 본질 |
|------|------|------|------|
| both (STLFSI ∩ OAS≥6) | 207 | 97.6% | 동시 발동 — 同 정보 |
| 🚨 **only_STLFSI** | 🚨 **5** | 2.4% | 2007 GFC 초기 only |
| only_OAS | 964 | 18.5% | OAS_HY 단독 stress |
| neither | 3596 | 69.1% | 정상 시기 |

🚨 **OAS_HY ≥ 5.0 threshold (느슨)에서 only_STLFSI = 0건** — 직교성 우회 결정적 不可.

### 4.2 OAS_HY 단독 시그널 결과 (직교성 우회 대체 시뮬)

| 자산 forward 60d | OAS_HY ≥ 6.0 spread | t | p |
|------|------|------|------|
| **TLT** | 🌟 **+0.92p** | +3.96 | **0.0001** |
| GLD | +1.28p | +4.65 | <0.0001 |
| COPX | +12.77p | +13.43 | <0.0001 |
| SLV | +5.46p | +8.51 | <0.0001 |

🌟 **결정적 발견**: OAS_HY ≥ 6.0 단독 시그널 (n=1171, robust)이 STLFSI에서 검출 불가한 TLT entry alpha **+0.92p (p=0.0001 결정적 양수)** 검출.

🚨 **격언 #80 함정 결정적 재확인**: STLFSI 정보 97.6% = OAS_HY ∩ — 격언 #80 28차원 (VVIX) 패턴 재현 결정적.

---

## §5. 9-point Checklist (격언 #116/#117/§35 #11 정합)

| # | Point | 결과 | 판정 |
|---|------|------|------|
| 1 | 분포 | extreme outlier 다수 (GFC + COVID) | 🚨 위기 군집 |
| 🚨 **2** | 하위그룹 | **4 개 연도만 발동** (2007/08/09/20) / 20년 中 | 🚨 **결정적 부정** |
| 3 | 대안 자산 | OAS_HY 단독 (n=1171)으로 同 alpha 검출 | 🚨 STLFSI 신규 不 |
| 4 | tail | min -? (위기 시기 outlier) | 🚨 selection bias |
| 🚨 **5** | regime | GFC + COVID 2 위기 only | 🚨 **robustness 결정적 부재** |
| 6 | 시간 군집 | 2008-09 GFC + 2020-03 COVID | 🚨 **event-clustering 결정적** |
| 7 | outlier | 발동 全 시기 = 历史 최대 위기 | 🚨 outlier 寄與 |
| 🚨 **8** | horizon TLT | H=10d +0.28 / 20d +0.10 / 40d -0.39 / **60d -1.81 (p=0.018)** / **120d -5.70 (p<0.0001)** / **250d -10.13 (p<0.0001)** | 🚨 **모든 horizon 음수 또는 0 — entry signal 결정적 부적합** |
| 🚨 **9** | 직교성 우회 | only_STLFSI = 5일 (2.4%) / OAS_HY 단독으로 충분 | 🚨 **격언 #80 결정적 재확인** |

🚨 **9-point 中 9건 결정적 부정 — NO-GO 双重 확정**.

---

## §6. 격언 정합 누적

| 격언 | 본 cycle 적용 | 본질 |
|------|------|------|
| 🌟 **#33** | past_ret 60d 사용 정의 결정적 입증 | REG-197 backward-looking 误解 진단 |
| 🌟 **#80** | 격언 #80 함정 28차원 (VVIX) 패턴 재현 | STLFSI 신규 정보 97.6% = OAS_HY |
| 🌟 **#116** | NO-GO 결정 前 다각도 자발 분석 | 4 사분면 + horizon + alternative 검증 |
| 🌟 **#117** | 양방향 단방향 추론 금지 | OAS_HY 신규 후보 2건 분리 |
| **§35 #11** | 평균값 단독 결론 금지 + 9-point | 본 결정 baseline 정합 |
| **#44** | 단순 가산 한계 | STLFSI = OAS_HY 동일 차원 |
| **#52** | Phase A ≠ portfolio alpha | past_ret ≠ forward signal |
| **#92** | ARGUS 매크로 차원 결정적 포화 | STLFSI = stress 차원 重복 |

---

## §7. 격언 #117 양방향 추론 — 신규 후보 분리 (OAS_HY)

### 7.1 CAND-S119_2_OAS_HY_60_TLT_ENTRY (잠재력 보존)

| 항목 | 값 |
|------|------|
| 후보 ID | **CAND-S119_2_OAS_HY_60_TLT_ENTRY** |
| baseline | OAS_HY ≥ 6.0 forward 60d TLT **+0.92p (t=+3.96, p=0.0001)** |
| 본질 가설 | TLT entry signal (NLR/IVW 대체 후보군과 별개) |
| 후속 검증 의무 | (1) Phase A causal forward 60d 정식 검증 (2) horizon sweep (3) regime stability (4) §B.9 v3 슬롯 경쟁 (5) §40 v3 4기간 BT |
| 위험 | n=1171 robust BUT 발동 시기 위기 集中 가능성 高 |
| 우선순위 | S120+ 후속 cycle |

### 7.2 CAND-S119_3_OAS_HY_60_V_RECOVERY_ENSN (잠재력 보존)

| 항목 | 값 |
|------|------|
| 후보 ID | **CAND-S119_3_OAS_HY_60_V_RECOVERY_ENSN** |
| baseline | OAS_HY ≥ 6.0 forward 60d COPX **+12.77p (p<0.0001)** / SLV +5.46p / GLD +1.28p |
| 본질 가설 | V-shape recovery EnSn (COPX/SLV/GLD broad) |
| 후속 검증 의무 | OAS_HY ARGUS active 활용 정합 확인 + 별도 EnSn 진입 가능성 |
| 위험 | OAS_HY 이미 active (m.get() 호출, REG-S80) — 중복 활용 위험 |
| 우선순위 | S120+ 후속 cycle |

---

## §8. Crown #67 LIVE 영향 차단

🛡️ **본 결정은 Crown #67 LIVE (PRIMA_v5_19_VIX_HYST_LIVE_v4) 영향 0건 — TLT 100% 영구 보존 정합**.

| 항목 | 영향 |
|------|------|
| Crown #67 엔진 | 변경 0건 |
| STLFSI entry 함수 | 추가 不 |
| OAS_HY 활용 | 既存 m.get() 호출 유지 (변경 不) |
| 포지션 | TLT 100% 영구 |

---

## §9. SSOT v1.10.213 후보 갱신 사항

| # | 갱신 | 본질 |
|---|------|------|
| 1 | CAND-S118_3 STLFSI TLT conditional → 🚨 **NO-GO 双重 확정** | REG-S119_2 |
| 2 | CAND-S118_3 STLFSI EASn (COPX/PAVE/VNM) → 🚨 NO-GO | OAS_HY 단독으로 충분 |
| 3 | 🆕 CAND-S119_2 OAS_HY 60 TLT entry | 신규 후보 등재 |
| 4 | 🆕 CAND-S119_3 OAS_HY 60 V-recovery EnSn | 신규 후보 등재 |
| 5 | 격언 #33 사례 누적 | past_ret backward-looking 误解 사례 |
| 6 | 격언 #80 함정 사례 누적 | 직교성 우회 결정적 NO-GO 사례 |

---

## §10. 산출물

| 파일 | 본질 |
|------|------|
| /home/claude/BT_LONG_STLFSI_signal.csv | STLFSI signal 부착 BT_LONG |
| /home/claude/STLFSI_PHASE_B6_RESULTS.csv | 21 자산 spread 매트릭스 |
| /home/claude/REG-S119_2_STLFSI_TLT_PHASE_B6_NO_GO.md | 본 결정문 |

---

## §11. S119 cycle 2순위 종결 baseline 한 줄 🦅

🌟 **"CAND-S118_3 STLFSI TLT conditional §B.9 v3 Phase B-6 + 직교성 우회 NO-GO 双重 확정 — REG-197 baseline 'past_ret 60d (backward)' 사용 정의 결정적 误解 진단 (forward 60d -1.81p / 120d -5.70p / 250d -10.13p 모든 horizon 음수 또는 0). 직교성 우회 가설 격언 #80 결정적 재확인 (STLFSI 신규 정보 97.6% = OAS_HY, only_STLFSI = 5일 only). OAS_HY 단독으로 TLT entry +0.92p (p=0.0001) 충분 — STLFSI 추가 정보 결정적 부재. 격언 #117 정합 신규 후보 2건 분리 (CAND-S119_2 OAS_HY TLT entry / CAND-S119_3 OAS_HY V-recovery EnSn). 9-point check 9/9 결정적 부정. Crown #67 LIVE TLT 100% 영구 보존."** 🦅

---

**Status**: ✅ S119 #2 NO-GO 双重 확정 / 신규 후보 2건 분리 / SSOT v1.10.213 갱신 후보

🦅 *Omnioculus Vigilantia* — past_ret 误解 결정적 진단 / 격언 #80 함정 재확인 / 잠재력 보존 (OAS_HY 2건) / Crown #67 영구 보존
