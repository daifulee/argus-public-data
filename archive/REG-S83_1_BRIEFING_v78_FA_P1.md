# 🦅 REG-S119_1 — CAND-S118_1 QLD MID Conditional §B.9 v3 Phase B-6 NO-GO

**작성일**: 2026-05-18 KST (S119 cycle 1순위 작업 종결)  
**baseline**: SSOT v1.10.209 ACTIVE / Crown #67 LIVE / TLT 100% 불변  
**선행 결정**: S118 cycle CAND-S118_1_QLD_MID_CONDITIONAL 🥇 진입 권고  
**본 결정**: 🚨 **§B.9 v3 Phase B-6 격리 시뮬 NO-GO** (격언 #116/#117/§35 #11 9-point check 정합)

---

## §1. 작업 본질

| 항목 | 값 |
|------|------|
| 대상 후보 | CAND-S118_1_QLD_MID_CONDITIONAL |
| 선행 baseline | post-COVID regime MID +0.18p / Sharpe +0.0911 / MDD +0.37p / Phase A 全 horizon p≤0.008 |
| 시뮬 방법 | §B.9 v3 Phase B-6 (S114 #1 신설, MAGS R1 첫 적용 정합) |
| 데이터 인프라 | Yahoo QLD fetch + BT_MID_2022_2026 병합 → BT_MID_v5_S119.csv (1048×82) |
| entry_QLD 함수 | S80 HANDOFF spec 정합 재현 (WTI≤90 + VIX<16 + QQQM_m3>5 + RS/VIX/TNX score≥3.5) |
| 발동 빈도 | 23/1048 = **2.19%** (very sparse) |
| 발동 시기 | 2023 (16건) / 2024 (5건) / 2025 (2건) — 2022·2026 0건 |

---

## §2. §B.9 v3 Phase B-6 spread 결과 (forward 60-day return)

### 2.1 18종 자산 spread 매트릭스

| Tier | 자산 | spread | t-stat | p-value | 본질 |
|------|------|------|------|------|------|
| Tier 2 | XLE | **+6.82p** | +4.18 | 0.0003 | energy/value rotation 동행 |
| Tier 3 | PAVE | +4.50p | +3.26 | 0.0033 | infrastructure 동행 |
| Tier 3 | XLF | +4.13p | +4.77 | 0.0001 | financials 동행 |
| Tier 3 | XLV | +4.11p | +3.66 | 0.0013 | healthcare 동행 |
| Tier 3 | IWM | +3.21p | +3.00 | 0.0060 | small-cap 동행 |
| Tier 3 | RSP | +3.02p | +3.98 | 0.0005 | equal-weight 동행 |
| Tier 4 | SMH | +2.09p | +0.95 | 0.35 | semi (비유의) |
| 🚨 **Tier 4** | 🚨 **QLD** | 🚨 **+0.91p** | +0.42 | 0.68 | **자기 자신 비유의** |
| Tier 4 | QQQM | +0.53p | +0.51 | 0.61 | leverage 본체 비유의 |
| NO-GO | MAGS | -0.83p | -0.71 | 0.49 | Mag 7 부진 |
| 🚨 NO-GO | CQQQ | **-7.33p** | -2.77 | 0.011 | 중국 tech 결정적 부진 |

### 2.2 결정적 발견 (격언 #52 정합)

🚨 **본질**: entry_QLD ON 시기 = broad value/cyclical rotation 시기. QLD 자체가 leverage NDX 우월 자산이 아닌, broad market alpha 동행 효과. 

| 본질 | baseline |
|------|------|
| Phase A "MID +0.18p" 본질 | 1:1 NLR 대체 BT (slot 경쟁 不在) baseline |
| 본 격리 시뮬 본질 | portfolio addition으로 entry_QLD 추가 alpha |
| 결정적 차이 | 1:1 대체 ≠ portfolio addition (격언 #52) |
| 본 결과 | QLD self alpha 거의 zero — broad rotation 동행 |

---

## §3. 9-point Checklist (격언 #116/#117/§35 #11 의무)

### 3.1 결과 종합

| # | Point | 본 cycle 결과 | 판정 |
|---|------|------|------|
| 1 | 분포 검증 | ON skew +0.359, >0 일수 78.3% | 🟢 양수 편향 OK |
| 🚨 **2** | 하위그룹 | **全 연도 ON < OFF** (2023: 13.4 vs 19.0 / 2024: 0.8 vs 7.0 / 2025: -1.6 vs 9.6) | 🚨 **결정적 부정** |
| 🚨 **3** | 대안 자산 | SMH ON +11.23% > QLD ON +9.33% | 🚨 **자산 대체 우월** |
| 4 | 꼬리 (tail) | ON min -5.14% vs OFF min -44.61% | 🟡 bull regime selection bias |
| 🚨 **5** | regime | ON VIX [10.83, 13.99] 매우 좁음 | 🚨 **robustness 약** |
| 🚨 **6** | 시간 군집 | 2023-06 (7건) + 2023-11 (7건) 군집 | 🚨 **event-clustering** |
| 🚨 **7** | outlier | 최고 3건 모두 2023-11 군집 | 🚨 **군집 outlier 寄與** |
| 🌟 **8** | 대상 확장 | **H=20d spread +4.91p (p<0.0001)** / H=60d/120d 비유의 | 🌟 **신규 후보 발견** |
| 🚨 **9** | 양방향 추론 (slot 경쟁) | QLD self baseline +8.42% strong + signal alpha 약 + SMH 우월 | 🚨 **격언 #52 회피 FAIL** |

### 3.2 종합 판정 (격언 #116/#117 정합)

🚨 **9-point 中 7건 결정적 부정 + 2건 신규 후보 가능성**

| 차원 | 부정/긍정 | 본질 |
|------|------|------|
| 정량 alpha | 🚨 부정 | QLD spread +0.91p (p=0.68) 비유의 |
| 하위그룹 | 🚨 부정 | 全 연도 ON < OFF |
| robustness | 🚨 부정 | VIX regime 좁음 + 시간 군집 + outlier 寄與 |
| 대안 비교 | 🚨 부정 | SMH 우월 / broad rotation 동행 |
| slot 경쟁 | 🚨 부정 | 격언 #52 회피 FAIL |
| 단기 horizon | 🌟 긍정 | H=20d 결정적 alpha (신규 후보) |

🚨 **NO-GO 확정 baseline 정합** — 5 차원 全 부정 + 1 차원 (단기) 별도 후보 분리.

---

## §4. 격언 정합 누적 (본 cycle 입증)

| 격언 | 본 cycle 적용 | 본질 |
|------|------|------|
| 🌟 **#52** | Phase A ≠ portfolio alpha 결정적 입증 | 1:1 대체 +0.18p ≠ 격리 시뮬 +0.91p (p=0.68) |
| 🌟 **#80 v2** | 양방향 slot 경쟁 결정적 입증 | broad rotation 동행 ≠ QLD 자체 alpha |
| 🌟 **#116** | NO-GO 결정 前 다각도 자발 분석 정합 | 9-point check 정밀 적용 |
| 🌟 **#117** | 양방향 단방향 추론 금지 정합 | H=20d 신규 후보 별도 분리 의무 |
| **§35 #11** | 평균값 단독 결론 금지 + 9-point checklist 적용 | 본 결정 baseline 정합 |
| **#46** | 자산 비대칭 (QLD 레버리지) | bull regime only 발동 — selection bias |
| **#56** | monkey-patch ≠ 결정 | 격리 시뮬은 결정 권한 (§B.9 v3 정합) |

---

## §5. 신규 conditional 후보 분리 (격언 #117 의무)

### 5.1 CAND-S119_1_QLD_SHORT_HORIZON_CONDITIONAL

| 항목 | 값 |
|------|------|
| 후보 ID | **CAND-S119_1_QLD_SHORT_HORIZON_CONDITIONAL** |
| baseline | H=20d spread **+4.91p** (t=+5.30, p<0.0001) 결정적 |
| 본질 가설 | short-term momentum overlay (HOLD_DAYS 20) |
| 후속 검증 의무 | (1) SMH H=20d 비교 (2) 다른 단기 signal과 직교성 (3) Phase A causal 재진행 |
| 위험 | regime 좁음 (VIX low only) + 발동 sparse (2.19%) + bull market selection bias |
| 우선순위 | S120+ 후속 cycle (CAND-S118_3 STLFSI TLT 와 함께 분리 평가) |

🌟 **결정적 본질**: H=20d alpha는 SMH도 동일 horizon에서 더 강할 가능성 高 (ON ret +11.23% > QLD +9.33%) — 후속 검증 必須.

---

## §6. Crown #67 LIVE 영향 차단 (Commander 5대 원칙 #5)

🛡️ **본 결정은 Crown #67 LIVE (PRIMA_v5_19_VIX_HYST_LIVE_v4) 영향 0건 — TLT 100% 영구 보존 정합**.

| 항목 | 영향 |
|------|------|
| Crown #67 엔진 | 변경 0건 |
| ENTRY_FUNCTIONS dict | entry_QLD 추가 不 |
| ENTRY_THRESHOLD dict | 변경 0건 |
| 포지션 | TLT 100% 영구 |

---

## §7. SSOT 통합 사항 (v1.10.213 후보 갱신)

### 7.1 SSOT 추가 항목

| # | 항목 | 본질 |
|---|------|------|
| 1 | CAND-S118_1_QLD_MID_CONDITIONAL | 🚨 **NO-GO 확정** (REG-S119_1) |
| 2 | CAND-S119_1_QLD_SHORT_HORIZON_CONDITIONAL | 🆕 신규 후보 등재 (H=20d +4.91p) |
| 3 | 격언 #52 사례 누적 | broad rotation 동행 ≠ self alpha |
| 4 | §B.9 v3 Phase B-6 누적 사례 | MAGS R1 PASS / QLD entry FAIL 대비 |

### 7.2 데이터 산출물

| 파일 | 본질 |
|------|------|
| /home/claude/BT_MID_v5_S119.csv | QLD_Close 병합 1048×82 |
| /home/claude/BT_MID_v5_S119_with_signal.csv | entry_QLD trigger + features 합성 |
| /home/claude/PHASE_B6_RESULTS.csv | 18 자산 spread 매트릭스 |
| /home/claude/REG-S119_1_QLD_MID_CONDITIONAL_PHASE_B6_NO_GO.md | 본 결정문 |

---

## §8. S119 cycle 종결 baseline 한 줄 🦅

🌟 **"CAND-S118_1 QLD MID conditional §B.9 v3 Phase B-6 격리 시뮬 NO-GO 확정 — QLD self spread +0.91p (p=0.68 비유의), 全 연도 ON < OFF, SMH 우월, broad value/cyclical rotation 동행 효과 결정적 입증 (격언 #52). 9-point check 7/9 결정적 부정. 단, H=20d spread +4.91p (p<0.0001) 신규 후보 CAND-S119_1_QLD_SHORT_HORIZON_CONDITIONAL 별도 분리 (격언 #117). Crown #67 LIVE TLT 100% 영구 보존."** 🦅

---

**Status**: ✅ S119 #1 NO-GO 확정 / 신규 후보 1건 분리 / SSOT v1.10.213 갱신 후보

🦅 *Omnioculus Vigilantia* — NO-GO 9-point check 정밀 정합 / 잠재력 보존 (신규 후보 분리) / Crown #67 영구 보존
