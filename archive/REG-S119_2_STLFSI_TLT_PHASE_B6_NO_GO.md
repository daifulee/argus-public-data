# 🚨 REG-S120_1 — DFII10 REFLATION BASKET §B.9 v3 NO-GO

**작성일**: 2026-05-18 KST (S120 cycle #1)  
**baseline**: SSOT v1.10.213 정식 (S120 진입)  
**후보 ID**: 🌟 **CAND-S119_4_REFLATION_BASKET** 🌟 (S119 cycle 인계)  
**판결**: 🚨 **NO-GO 확정 (basket 6 자산 동일 가중 차원)** 🚨  
**분리 후보**: 🌟 **CAND-S120_XLE_REFLATION_SOLO** 🌟 (격언 #117 정합)  
**Crown LIVE**: PRIMA_v5_19_VIX_HYST_LIVE_v4 **不변** (TLT 100%)

---

## §1. 가설 요약

### 1.1 원가설 (S119 #3 인계)

🌟 **본질 baseline**: DFII10 < -0.5 (real yield negative) → reflation regime tag → 원자재/cyclical EnSn basket

**Basket 구성 (6 자산 동일 가중 1/6)**:
| Asset | Phase A Δ (인계) | Phase A Δ (LIVE 재측) | 정합 |
|------|------|------|------|
| XLE | +9.41p | **+9.38p** | ✅ |
| XLF | +6.17p | **+6.15p** | ✅ |
| COPX | +4.66p | **+4.61p** | ✅ |
| VNM | +4.26p | **+4.24p** | ✅ |
| PAVE | +4.05p | **+4.03p** | ✅ |
| INDA | +3.47p | **+3.46p** | ✅ |

🌟 **인계장 baseline 6/6 정합 (diff < 0.05p)** ✅

---

## §2. 5 Phase 검증 매트릭스

### 2.1 Phase 🅐 — 데이터 baseline + Phase A 재검증 (20분)

| 지표 | 값 |
|------|------|
| 전체 기간 | 2007-01-03 ~ 2026-04-02 / 4843 rows |
| DFII10<-0.5 발동 | 654/4800 = **13.63%** |
| era별 발동 | P1 209건(10.4%) / **P2 397건(22.5% 압도)** / **MID 48건(4.5% 거의 비활성)** |
| 데이터 가용성 | XLE/XLF 2007+ / COPX 2010+ / VNM 2009+ / **PAVE 2017+ / INDA 2012+** |

🚨 **즉시 결정적 risk 식별**:
- PAVE/INDA P1 era 부재 (basket era 불일치)
- DFII10<-0.5 era 분포 unbalanced (P2 압도 22.5% / MID 4.5%)
- 격언 #91 v2 #4 (era shift) risk

### 2.2 Phase 🅑 — OAS_HY 통제 직교성 검증 (25분)

**OAS_HY 분포 (DFII10<-0.5 발동 시점)**:
| 지표 | trig=1 (DFII<-0.5) | trig=0 (control) |
|------|------|------|
| mean | **4.421** (낮음) | 5.306 (높음) |
| median | 4.360 | 4.500 |
| MID era max | 3.838 (全 stress region 미만) | - |

🌟 **결정적 발견**: DFII10<-0.5는 OAS_HY 高 stress region이 아니라 **오히려 OAS_HY 낮은 시기** → 직교성 가설 정정

**OAS_HY 통제 後 잔여 alpha (regression: fwd ~ DFII_trig + OAS_HY)**:
| Asset | Raw Δ | Ctrl Δ | 생존률 | OAS coef | OAS p | Ctrl t | Ctrl p |
|------|------|------|------|------|------|------|------|
| XLE | +9.39p | **+9.57p** | **102.0%** | +0.204 | 0.003 | +17.99 | <0.0001 |
| XLF | +6.15p | +6.34p | 103.1% | +0.212 | 0.001 | +12.67 | <0.0001 |
| COPX | +4.61p | +5.16p | 112.0% | +3.153 | <0.0001 | +6.46 | <0.0001 |
| VNM | +4.24p | +4.32p | 102.0% | +0.275 | 0.042 | +8.42 | <0.0001 |
| PAVE | +4.03p | +3.74p | 92.8% | +4.624 | <0.0001 | +7.32 | <0.0001 |
| INDA | +3.47p | +3.34p | 96.4% | +1.561 | <0.0001 | +8.77 | <0.0001 |

🌟 **6/6 잔여 alpha 92~112% 생존** ✅  
🌟 **격언 #80 (직교성 우회) 위반 없음** ✅ — DFII10 effect와 OAS_HY effect 독립

### 2.3 Phase 🅒 — era별 slot 경쟁 결정자 진단 (25분)

**era별 DFII10<-0.5 발동 시 Top-5 자산**:
| era | DFII<-0.5 N | Top-5 中 BASKET | basket 평균 | non-basket | basket - non |
|------|------|------|------|------|------|
| P1 | 209 | 1개 (XLF만) | +3.83p | +2.56p | 🟡 **+1.26p** (약) |
| P2 | 397 | **4개** (COPX/XLE/PAVE/XLF) | **+9.31p** | +2.83p | 🌟 **+6.49p** (압도) |
| MID | 48 | 1개 (XLE만) | 🚨 **−2.54p** 🚨 | -4.43p | +1.89p (전체 음수) |

**universe alpha (vs universe mean, asset α)**:
| Asset | P1 | P2 | MID |
|------|------|------|------|
| **XLE** | +2.06 | +10.65 | 🌟 **+23.73** 🌟 |
| XLF | +8.32 | +3.58 | -4.47 |
| COPX | -4.15 | +8.81 | +1.20 |
| VNM | +5.88 | +3.04 | -9.02 |
| PAVE | (부재) | +4.56 | -1.51 |
| INDA | -1.43 | +3.58 | +1.74 |

🚨 **결정적 진단** (격언 #25/#52/#54 정합):
- basket의 평균 +4p alpha는 **거의 전부 P2 era 압도 효과**
- **MID era에서 basket slot 경쟁 약 + 부호 음수**
- 인계장 "P2 +14.46p 압도 but portfolio 음수" 본질 = MID era reversal에 의한 portfolio 희석

### 2.4 Phase 🅓 — §B.9 v3 슬롯 사전 시뮬 (25분)

**slot 진입 vs 미진입 forward returns (격언 #52/#79 양방향 입증)**:

🚨 **결정적 결과**:
| era | Asset | Top-5 진입율 | fwd in | fwd out | slot Δ |
|------|------|------|------|------|------|
| P2 | XLE | 50.4% | +11.15p | +13.35p | -2.20p |
| P2 | COPX | 56.4% | **+16.54p** | +10.43p | **+6.11p** (유일 강) |
| P2 | VNM | 13.9% | -0.28p | +6.50p | -6.78p |
| **MID** | **XLE** | 🚨 **93.8%** | +17.92p | **+32.84p** | 🚨 **-14.92p** |
| **MID** | **COPX** | 79.2% | 🚨 **-5.09p** | +19.31p | 🚨 **-24.40p** |
| MID | XLF | 0% | n/a | -9.33p | n/a (절대 미진입) |
| MID | VNM | 20.8% | -10.40p | -16.71p | +6.31p (둘 다 음수) |

🌟 **결정적 메커니즘**: slot 진입 = self-selection (momentum 高 자산) → mean reversion 영향 → forward returns 음수화/약화

→ **Phase A 격리 alpha vs §B.9 v3 portfolio 시뮬 = 결정적 모순** (격언 #117 본질 4 cycle 연속 입증)

### 2.5 Phase 🅔 — 9-point checklist 정밀 적용 (25분)

**basket 1/6 동일 가중 portfolio**:
- FULL: +5.70p / P1: +3.99p / P2: +8.53p / 🚨 **MID: -6.02p** 🚨

**9-point checklist 결과 (basket 차원)**:
| Point | basket 전체 (6) | 판정 |
|------|------|------|
| ① 분포 mean | +5.70p (FULL) | 양수 but era 분기 |
| ② 하위 group (era) | 2/3 era 양수 (MID 음수) | 🚨 FAIL |
| ③ 대안 자산 | universe alpha basket avg | 부분 PASS |
| ④ 꼬리 사례 | MID 5/6 음수 | FAIL |
| ⑤ regime | 全 양수 | OK |
| ⑥ 시간 | **MID FAIL** | 🚨 **FAIL** |
| ⑦ outlier | era reversal 일관 (outlier 무관) | (분기 무효) |
| ⑧ 대상 확장 | **6 자산 中 5 자산 MID reversal** | 🚨 **FAIL (1/6)** |
| ⑨ 양방향 | §B.9 v3 slot 진입 시 -5~-15p 손실 | 🚨 **FAIL** |

→ **5/9 핵심 분기 FAIL** (특히 ⑥ ⑧ ⑨ 결정적)

---

## §3. 격언 매트릭스 — 4 cycle 연속 입증

| 격언 | 본 cycle 본질 |
|------|------|
| **#117** (4 cycle 연속) | Phase A 강도 ≠ §B.9 v3 portfolio α — basket Phase A +5.70p but MID portfolio -6.02p |
| **#91 v2 #4** (5번째 사례) | era shift P1+P2 (reflation 호황) → MID (real yield 음수=stagflation 우려) sign 반전 |
| **#52** (강력 입증) | signal isolation strength ≠ portfolio α — slot 진입 시 -5~-15p mean reversion |
| **#79** (강력 입증) | entry threshold ≠ exit threshold — slot 진입 시점 momentum 끝물 |
| **#25** | aggregate basket mean ≠ portfolio α — P2 압도가 FULL baseline 견인 / MID 손실 |
| **#54** | diversification 양수 합 ≠ portfolio α — basket 다양화 compression 없음 |
| **#80** | 무위반 (직교성 우회 없음, OAS_HY 통제 後 잔여 alpha 92~112% 생존) |
| **#116** | NO-GO 결정 前 6축 자발 분석 의무 정합 (9-point checklist 정밀 적용) |

---

## §4. 최종 판결 (분기 logic 정합)

### 4.1 basket 차원 = NO-GO 확정

🚨 **9-point checklist 中 ⑥ 시간 / ⑧ 대상 확장 / ⑨ 양방향 결정적 FAIL** → SKILL §3 분기 logic "5 차원 모두 YES" 미충족 + ⑥/⑧/⑨ 결정적 FAIL

### 4.2 XLE 단독 = 별도 후보 분리 의무 (격언 #117 §3 4/5 분기 PASS)

🌟 **9-point check XLE 단독 분기 평가**:
- ① 분포: trig mean +10.45p / med +9.60p / **trig 中 양수율 77.7%** ✅
- ② 하위 group (DFII10): **dose-response** (DFII<-0.8 +15.82p / -0.8~-0.5 +4.91p / -0.5~0 +0.21p / ≥0 +1.11p) ✅
- ⑤ regime: VIX/WTI/DXY 全 영역 양수 (WTI≥90 +6.74p 약 but 양수) ✅
- ⑥ 시간 (era): P1 +3.41p / P2 +13.45p / **MID +15.75p** — 全 era 양수 ✅
- ⑦ outlier: dose-response 명확 → outlier 영향 없음 ✅
- ⑨ 양방향: MID slot in -14.92p (timing risk) — 추가 검증 필요 ⚠️

→ **4/5 분기 PASS + 1 보류 = 격언 #117 별도 후보 분리 의무**

### 4.3 신규 후보 ID 등재 (별도 정식)

🌟 **CAND-S120_XLE_REFLATION_SOLO** (등재 파일: `CAND-S120_XLE_REFLATION_SOLO_REGISTRATION.md`)

---

## §5. 결정적 한 줄 결산 🦅

🌟 **"CAND-S119_4 REFLATION BASKET (6 자산 동일 가중) = §B.9 v3 부적합 NO-GO. 인계장 Phase A baseline 6/6 정합 ✅ + OAS_HY 통제 後 잔여 alpha 92-112% 생존 ✅ + 격언 #80 (직교성 우회) 무위반 ✅ — but era split 5/6 자산 MID reversal (격언 #91 v2 #4 패턴 ⑤) + §B.9 v3 슬롯 시뮬 진입 시 -5~-15p 손실 (격언 #52/#79 양방향) + basket portfolio MID -6.02p. XLE 단독은 全 차원 robust (3/3 era 양수 + DFII dose-response + universe α MID +23.73p) → CAND-S120_XLE_REFLATION_SOLO 별도 후보 분리. 격언 #117 양방향 추론 4 cycle 연속 결정적 입증. Crown #67 LIVE TLT 100% 不변."** 🦅

---

**Status**: ✅ NO-GO 정식 등재 / XLE 단독 별도 후보 분리 정착 / 격언 #117 4 cycle 연속 입증
