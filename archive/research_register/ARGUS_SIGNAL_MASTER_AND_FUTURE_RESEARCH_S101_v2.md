# 🦅 ARGUS 시그널 총정리 + 향후 연구과제 마스터 문서 v2

| 항목 | 값 |
|:--|:--|
| 버전 | 🌟 **v2 (외부 audit 2건 통합 보강)** 🌟 |
| 작성일 | 🌟 **2026-05-13 KST** 🌟 |
| Commander | Lignas |
| 작성자 | Claude (Anthropic Opus 4.7) |
| LIVE baseline | 🌟 **Crown #67 = PRIMA_v5_19_VIX_HYST_LIVE_v4** 🌟 |
| Briefing baseline | 🌟 **prima_briefing_v8_9_3** 🌟 |
| 우주 | 20종 ETF (NLR 포함, DEAD 처리 상태) |
| SSOT 기준 | v1.10.178 |
| 격언 정합 | #11/#15/#20/#25/#46/#48/#56/#73/#80/#87/#88 v3/#91/#94/#96 v2/#97 v2/#98/#106/#107/#109/#110/#111/**#112 후보** |
| 외부 audit | Audit 1 (Relative breadth, S101#1) + Audit 2 (Crown System Final Review, S101#2) |

---

## 🎯 § 0. 결론 3줄

🌟 **현행 시그널 자산**: 4 분류 (EnSn / EASn / MoSn / ExSn) × 20 종목 × 매크로 지표 28종 = 진입 가산 점수 **141건** + 진입 회피 페널티 **18건** + 청산 트리거 **8건** + 모멘텀 게이트 **3건** + 인터랙션/특수 **9건**.

🌟 **외부 audit 통합 발견**: ① Audit 1 → Relative breadth batch 6 후보 신규 + Lane 문제 (entry/sizing/MoSn/shadow) ② Audit 2 → 10대 메타 발견 (특히 "추가"보다 "제거" 강력, Slot allocator 본질) + Tier S 5종 + 3 구조적 위험 인지.

🚨 **운영 원칙 (격언 #25 + #112 후보)**: ARGUS = stock picker 아닌 slot allocator. Phase A 강함 ≠ BT alpha. 모든 후보 §40 v3 + RULE 29 v2 + 외부 FA P0 audit 필수. **threshold sweep 과최적화 + interaction explosion 위험 인지 의무**.

---

## 📊 § 1. 시그널 4 분류 체계 (격언 #91 정식)

### § 1.1 페이즈 × 극성 매트릭스

| 페이즈 | 양의 시그널 (alpha 흡수) | 음의 시그널 (alpha 회피) |
|:--:|:--|:--|
| **진입 전 (Pre-entry)** | 📥 **EnSn** (Entry Signal) | ⚡ **EASn** (Entry Avoidance Signal) |
| **보유 중 (During-holding)** | 📊 **MoSn** (Momentum Signal) | 📤 **ExSn** (Exit Signal) |

🌟 **본질**: 본 4 분류는 격언 #91 4 패턴 정합 입증 결과 도출 (S62 #40 정식 입증):
- ① noise (제거 대상)
- ② fitting + 핵심알파 (DXY>105 보존 / DXY>100 STRESS 7/14 거부)
- ③ robust plateau (격언 #76 정합 sweep 통과)
- ④ 시대적 변화 (격언 #19 정합)

### § 1.2 4 분류별 운영 본질

| 분류 | 본질 | 운영 위치 | 격언 |
|:--:|:--|:--|:--:|
| 📥 EnSn | 진입 시 양의 점수 가산 | `entry_*()` 함수 `s+=` | #11/#25/#48 |
| ⚡ EASn | 진입 시 음의 점수 (회피) | `entry_*()` 함수 `s-=` | #44/#52 |
| 📊 MoSn | 환경 강도 조절 (RgSn 포함) | `m['*_BullStack']` dict | #34/#43/#46 |
| 📤 ExSn | 청산 트리거 (FULL/HALF) | `should_exit()` 함수 | #87/#94 |

### § 1.3 🆕 **Lane 분류 매트릭스 (Audit 1 통합)**

🌟 **Audit 1 결정적 통찰**: "좋은 시그널을 잘못된 lane에 넣으면 망가진다"

| Lane | 본질 | 현 활용 | 미발굴 영역 |
|:--:|:--|:--|:--|
| Entry boost | s+= 가산 (현행 141건) | 20종 EnSn | — |
| Sizing modifier | 비중 조절 (×1.0/×0.5) | SLV RS / COPX USD_CNY | 18종 미발굴 |
| MoSn (RgSn) | 환경 강도 조절 | XLE/VNM BullStack 2종 | 18종 미발굴 |
| Shadow only | LIVE 미진입 (모니터링) | NLR 대체 IVW | 결정적 미발달 |

🚨 **결정적 입증**: HYG/LQD entry boost = IWM/SMH/VEA/XLE/INDA 5종 BT FAIL → 시그널 부재 아닌 **lane 오선택**.

---

## 📊 § 2. 매크로 지표별 시그널 임계값 마스터 매트릭스

🌟 **본 매트릭스 출처**: `PRIMA_v5_19_VIX_HYST_LIVE_v4.py` line 3000 `SIGNAL_RULES` dict + `TICKER_SPEC` dict + `entry_*()` 함수 grep (격언 #75 v4 정합).

### § 2.1 매크로 지표 28종 분포

| 카테고리 | 지표 | 임계값 셋 | 핵심 종목 |
|:--|:--|:--|:--|
| **금리** | TNX (10년물) | 4.1 / 4.0 / 3.5 / 2.5 / 4.8 | GLD/SLV/TLT/ITA/XLV/XLF |
| | TYX_30Y | 4.71 | GLD/SLV/XLE/ITA/XLU/EWZ/VEA |
| | FVX_5Y | 0.77 | XLF/IWM/VEA |
| | DFII10 (실질) | 0 / 0.5 / 1 / 2 (hard) | SLV/XLE/XLF/XLV/VNM/TLT |
| **변동성** | VIX | 22 / 18 / 16 / 35 / 16~22 | 8 종목 |
| | MOVE | 52.38 | XLF/IWM/VEA/VNM |
| | VVIX | 120 (조합 후보) | 미사용 |
| | SKEW | 140 (조합 후보) | 미사용 |
| **통화/원자재** | DXY | 110 / 105 / 101 / 100 / 95 / 93 | GLD/SLV/SMH/INDA/CIBR/TLT |
| | WTI (일반 게이트) | 90 (`_wk`) | 18 종목 |
| | WTI (XLE 게이트) | 95 / 110 (인플레) | XLE |
| | WTI (점수) | 60 / 70 / 85 (음수) | 14 종목 |
| | USD_CNY | 7.0 / 6.5 | COPX (sizing) |
| | USD_KRW | 1400 (조합 후보) | 미사용 |
| **신용 스프레드** | OAS_HY | 7.0 (hard gate) | XLU/XLF |
| | OAS_IG | 0.89 | GLD/SLV |
| **인플레 기대** | T10YIE | 2.0 / 2.3 / 2.5 / 2.6 | SLV/PAVE/ITA/TLT/XLE |
| | T5YIE | 2.5 (조합 후보) | 미사용 |
| **거시 지표** | PMI | 48 / 50 | EWZ/XLV |
| | NFCI | 0 / -0.5 | XLV |
| | SAHMCURRENT | 0.3 (조합) / 2.4 | COPX/VNM/INDA/CQQQ |
| | UMCSENT | 60 (조합 후보) | 미사용 |
| | ICSA | 400K (조합 후보) | 미사용 |
| | STLFSI | 1.0 (조합 후보) | 미사용 |
| | T10Y3M | <0 (조합 후보) | 미사용 |
| **종목 모멘텀** | ticker_m1 | -3 / 0 / -5 / +3 | ITA/CIBR/XLU/IWM |
| | ticker_m3 | -5 / 0 | INDA/XLV/PAVE/IWM/CQQQ |
| | COPX_DEV120 | -30 / -25 / +35 | COPX (modifier) |
| **유동성 (미사용)** | Net_Liquidity | 1.5/2.0/2.5 (P0 후보) | 향후 TLT |
| | WALCL | (미사용) | 향후 |
| | WTREGEN | (미사용) | 향후 |
| | RRPONTSYD | (미사용) | 향후 |
| **🆕 Relative breadth (Audit 1 신규)** | RSP/SPY ratio roc60 | <q20 | GLD MoSn/Sizing 후보 |
| | COPX/GLD ratio | >q80 | CQQQ EnSn 후보 |
| | QQQ/SPY ratio | >q90 | COPX EnSn 후보 (narrow) |
| | DXY chg60 | <q10 | IWM EnSn 후보 |
| | VVIX (분위수) | >q90 | XLE EnSn 후보 (crisis) |

🚨 **결정적 본질**: 현행 LIVE 28 매크로 지표 중 **4 유동성 지표 (Net_Liquidity / WALCL / WTREGEN / RRPONTSYD) = 완전 부재** + 🆕 **5 Relative breadth 지표 (Audit 1 신규) = 완전 부재** → 본 9 영역이 향후 연구 P0~P1 최강 후보.

---

## 📊 § 3. 티커별 EnSn 매트릭스 (20 종목 전수)

*(S101 v1 § 3 내용 보존 — 변경 없음. 가독성 위해 본 v2에서는 압축 표기.)*

| 분류 | 종목 | EnSn 건수 | ENTRY_THRESHOLD |
|:--:|:--:|:--:|:--:|
| 🟢 풍부 | SLV | 8 (+1.5/+7.5/+5/+2/+2/+1.5/+1.5/-3.5/-9) | s>3.0 |
| 🟢 풍부 | VNM | 9 (Hard gate DFII10<1 + 8 EnSn) | s>3.0 |
| 🟢 풍부 | COPX | 10 (+12.7/+5/+6.4/+2/+2/+4/+1.5/-7.7/-5.8/-3) | s>5.0 |
| 🟡 중간 | GLD | 7 | s>1.5 |
| 🟡 중간 | EWZ | 7 | s>5.0 |
| 🟡 중간 | XLE | 6 (+ Bull/BearStack RgSn) | s>2.0 |
| 🟡 중간 | SMH | 5 | s>3.0 |
| 🟡 중간 | XLF | 7 (+ OAS_HY hard gate) | s>2.5 |
| 🟡 중간 | IWM | 7 | s>2.5 |
| 🟡 중간 | VEA | 7 | s>2.5 |
| 🟡 중간 | XLV | 6 | s>1.5 |
| 🟡 중간 | TLT | 5 (+ WTI>90 조건부 gate) | s>1.5 |
| 🟡 중간 | ITA | 5 | s>2.0 |
| 🟡 중간 | PAVE | 5 | s>4.5 |
| 🟡 중간 | INDA | 5 | s>3.0 |
| 🟡 중간 | CQQQ | 5 | s>4.5 |
| 🟠 단순 | XLU | 4 (+ OAS_HY hard gate) | s>1.0 |
| 🟠 단순 | CIBR | 4 | s>3.5 |
| 🔴 DEAD | NLR | 0 (영구 DEAD, Crown #59) | 4.5 |
| 🔴 부재 | QQQM | 0 (bull_only gate 자동 진입) | 2.0 |

🌟 **상세 매트릭스는 S101 v1 § 3.1~§ 3.4 참조** (820 라인 원본 보존).

---

## 📊 § 4. ExSn (청산 트리거) 매트릭스 — `should_exit()`

🌟 **출처**: `PRIMA_v5_19_VIX_HYST_LIVE_v4.py` line 2263.

### § 4.1 S급 (FULL — 즉시 전량 청산)

| # | 트리거 | 임계 | 대상 | 격언 |
|:--:|:--|:--:|:--|:--:|
| 1 | WTI>90 | WTI>90 (TLT/XLE 제외) | 일반 18종 | #48 |
| 2 | XLE_W95 | WTI>95 (평소) | XLE | #28/#29 |
| 3 | XLE_W110 | WTI>110 (인플레: T10YIE>2.3 ∩ DFII10<0) | XLE | #28/#29 |
| 4 | TLT_WTI90_T10YIE26 | WTI>90 ∩ T10YIE>2.6 (Crown #52) | TLT | #65 |
| 5 | STORM | VIX>35 | GLD/TLT 제외 18종 | — |
| 6 | STOPLOSS | drawdown<-15% | 전 종목 | — |
| 7 | TARGET_Xd | held_days≥target_days | 종목별 (21~126d) | — |

### § 4.2 B급 (HALF — 50% 부분청산)

| # | 트리거 | 임계 | 대상 | 격언 |
|:--:|:--|:--:|:--|:--:|
| 1 | SLV_TNX | TNX>4.8 | SLV (36회 발동, S41 #1) | #18 |
| 2 | TLT_DXY | DXY>100 | TLT (26회 발동, S37 #3, Crown #37) | #28 |
| 3 | EWZ_DXY | DXY>105 | EWZ (n=290, Crown #61, S62 #18) | #87/#94 |

🌟 **EWZ_DXY** (Audit 2 §9): ExSn 발굴 6번째 시도에서 첫 채택 (GLD/TLT 5/5 거부 후). **격언 #94 (ExSn 우선순위 의무) + #87 (ExSn 사전 평가 적용) 정합 운영 첫 양수 결과**.

### § 4.3 보유 기간 (target_days) 매트릭스

| hold | 종목 |
|:--:|:--|
| 21d | XLU |
| 42d | ITA / COPX / VEA / IWM / PAVE / CQQQ |
| 63d | SLV / XLE / SMH / NLR / QQQM / XLF / XLV / VNM / INDA / CIBR |
| 126d | GLD / EWZ / TLT / VNM |

### § 4.4 ExSn 청산 비대칭성 (격언 #88)

🚨 **20 종목 중 종목별 individual ExSn = 단 3종 (SLV/TLT/EWZ)** — 17종 결정적 미발달 (Audit 2 §9 ExSn 연구 가능성 영역).

---

## 📊 § 5. MoSn (Momentum Signal) — BullStack/BearStack

### § 5.1 정의

| MoSn | 정의 |
|:--|:--|
| BullStack | MA20 > MA50 > MA120 (지속 강세 추세) |
| BearStack | MA20 < MA50 < MA120 (지속 약세 추세) |
| Neutral | 기타 (점수 변경 없음) |

### § 5.2 종목별 MoSn 운영 매트릭스

| 종목 | MoSn 적용 | 운영 본질 |
|:--:|:--|:--|
| XLE | XLE_BullStack / BearStack | WTI>85 환경 트리거 강도 조절 (RgSn) |
| VNM | VNM_BullStack | DFII10>2 환경 강도 조절 |
| 나머지 18종 | 미적용 | 결정적 미발굴 영역 (Tier S Audit 2) |

🚨 **MoSn 영역 결정적 미발달**: Audit 2 §1~§4 본질 정합 — "추가"보다 "제거", Asset asymmetry 강함, Macro 직관 ≠ 알파.

---

## 📊 § 6. 인터랙션 시그널 (RgSn — 환경 인터랙션)

### § 6.1 채택 인터랙션 (9건)

| # | 종목 | 인터랙션 | 점수 | Crown |
|:--:|:--|:--|:--:|:--:|
| 1 | SLV | DXY<95 ∩ T10YIE>2.0 | +1.5 | **#60 (Audit 2 S급)** |
| 2 | ITA | DXY<95 ∩ T10YIE<2.0 | +1.5 | 후보 |
| 3 | PAVE | DXY<95 ∩ T10YIE<2.0 | +3.0 | 후보 (시너지 +11.118p) |
| 4 | CQQQ | DXY>95 ∩ SAHM>0.3 | +4.0 | #56 (S51) |
| 5 | EWZ | OAS_HY - OAS_IG ≥5.5 | +1.5 | v5.11 ReSn 후보 |
| 6 | XLE | BullStack ∩ WTI>85 | +2.4 | RgSn |
| 7 | XLE | BearStack ∩ WTI>85 | −2.4 | RgSn |
| 8 | VNM | BullStack ∩ DFII10>2 | +4.0 | RgSn |
| 9 | TLT | WTI>90 ∩ 디스인플레 | +2.0 | #36 (S35) |

### § 6.2 거부된 인터랙션 (반례 사례)

| # | 종목 | 인터랙션 | 거부 사유 | 격언 |
|:--:|:--|:--|:--|:--:|
| 1 | GLD | DXY<95 ∩ T10YIE>2.0 | -0.197p (SLV +0.306p 대비) | #48 |
| 2 | GLD | EWZ_DXY 동일 가설 | -3.145p | #48 |
| 3 | 다수 | DXY>100 STRESS 7/14 | fitting + fragile | #91 |
| 4 | TLT | NLR (Top5 dynamic CAGR V2) | RULE 29 v2 3건 FAIL + STRESS 14 9건 -1p 초과 | #73 |

---

## 📊 § 7. Gate (게이트) 시스템

### § 7.1 WTI 게이트 (`_wk` + `_wk_xle`) — Crown #67 V_18.5_HYST_1.0

🌟 **`_wk(m)` 일반 게이트 (Crown #67, S79 #1)** — **Audit 2 §6 Hysteresis state engine S급 입증**:
- WTI ≤ 89: unconditional OPEN
- WTI > 89: VIX hysteresis
  - OPEN → BLOCKED: WTI>90 ∩ VIX≥18.5
  - BLOCKED → OPEN: VIX<17.5 (마진 1.0)

🌟 **`_wk_xle(m)` XLE 게이트** (Hysteresis H1 마진 $1):
- 인플레 (T10YIE>2.3 ∩ DFII10<0): block $110 / release $109
- 평소: block $95 / release $94

### § 7.2~§ 7.4 기타 Gate

*(S101 v1 §7 내용 보존)*

---

## 📊 § 8. Score Modifier / Sizing (compute_weights)

*(S101 v1 §8 내용 보존)* — **Audit 2 Tier S "Adaptive sizing" 신규 연구 영역 식별**.

| 종목 | 조건 | sizing |
|:--:|:--|:--:|
| SLV | RS_20d > 0 | ×1.0 |
| SLV | RS_20d ≤ 0 | ×0.5 |
| COPX | USD_CNY>7.0 | ×1.2 |
| COPX | USD_CNY<6.5 | ×0.8 |
| COPX | USDCNY_chg20<-1.0 | ×1.1 |
| COPX | COPX_DEV120<-30 | s+=4.0 |

🚨 **결정적 미발달**: 20종 중 sizing modifier 적용 = SLV/COPX 2종만. 18종 미발굴 (Audit 2 Tier S).

---

## 📊 § 9. 향후 연구과제 종합 (v2 보강)

### § 9.1 🥇 P0: Net Liquidity (NL) EnSn 발굴 (REG-S80_NL_ENSN)

🌟 **결정적 본질**: ARGUS LIVE 20개 종목 entry signal 중 **Net Liquidity (NL) 직접 사용 = 0건**.

#### Phase A Top 5 후보

| 순위 | 종목 | Δ uplift | t-stat | 본질 |
|:--:|:--:|:--:|:--:|:--|
| 🥇 1 | TLT | 🌟 **+2.75p** 🌟 | 🔴 **+13.51** | ARGUS 역사상 최강 t-stat |
| 🥈 2 | PAVE | +1.73p | +3.55 | 인프라 (정부 지출 직접) |
| 🥉 3 | INDA | +1.63p | +5.16 | 신흥국 |
| 4 | CIBR | +1.51p | +3.65 | 사이버 보안 |
| 5 | QQQM | +0.87p | +2.37 | 대형 기술주 (약함) |

🌟 **총 예상**: ~95분 + 외부 FA audit.

### § 9.2 🥈 P1: 조합 인터랙션 시그널 6건 (REG-S80_COMBO)

| # | 조합 시그널 | 동시 발현 | 적용 후보 |
|:--:|:--|:--:|:--|
| 🥇 1 | T10Y3M<0 ∩ SAHM>0.3 | 200일 (4.1%) | XLF/IWM ExSn |
| 🥈 2 | SKEW>140 ∩ VIX>20 | 169일 (3.5%) | 위험자산 일괄 ExSn |
| 🥉 3 | UMCSENT<60 ∩ T5YIE>2.5 | 133일 (2.7%) | GLD/SLV EnSn 강화 |
| 4 | USD_KRW>1400 ∩ DXY>105 | 100일 (2.1%) | EWZ/VNM/INDA ExSn |
| 5 | STLFSI>1.0 ∩ VVIX>120 | 51일 (1.1%) | 전 자산 STORM 후보 |
| 6 | ICSA>400K ∩ VIX>20 | 854일 (17.6%) | 🚨 임계 강화 필요 |

🌟 **예상 시간**: ~285분 (4.75시간).

### § 9.3~§ 9.9

*(S101 v1 § 9.3~§ 9.9 내용 보존: DEAD EnSn 보강 / 임계값 최적화 / MoSn / ExSn / NLR 대체 / Crown #67 LIVE / V2 거부 / EASn 영역)*

### § 9.10 🆕 **P0+ 신규: Relative Breadth Batch (Audit 1 통합)**

🌟 **결정적 출처**: 외부 audit (S101#1, 2026-05-13 KST). 본 SSOT v1.10.178 등재 부재 → **신규 P0+ 후보 정식 등재**.

🚨 **격언 #20 정직 인지**: Audit 1 인용 수치 ("Raw Phase A 8,332개 / Phase B 큐 160개 / Shortlist 30개") = 본 SSOT/REG 출처 부재 → 외부 audit 권고 단계, Phase A 정량 수치 (t-stat, p-val) 미제시.

#### Relative Breadth 후보 6건 (Audit 1)

| 우선 | 종목 | 후보 시그널 | Lane | Audit 1 권고 본질 |
|:--:|:--|:--|:--:|:--|
| 🥇 1 | GLD | RSP/SPY ratio roc60 < q20 | MoSn / Sizing | robust plateau + momentum 독립성 양호 |
| 🥈 2 | CQQQ | COPX/GLD ratio > q80 | EnSn / EASn | robust plateau + 독립성 (lane 확인 필요) |
| 🥉 3 | COPX | QQQ/SPY ratio > q90 | EnSn (narrow) | 강하지만 narrow / momentum overlap |
| 4 | IWM | DXY chg60 < q10 | EnSn (FX) | HYG/LQD와 다른 계열이라 살아 있음 |
| 5 | XLE | VVIX > q90 | EnSn (crisis) | volatility crisis only 가능성 |
| 6 | PAVE | SAHMCURRENT > q80 | EnSn (lag 강제) | Phase A robust + lag/momentum 검증 필요 |

#### 추가 신규 영역 (Audit 1 §4)

| 종목 | 후보 | 영역 |
|:--|:--|:--|
| SMH | DXY chg60 < q10 + volatility 후보 | FX/volatility 미발굴 |
| VEA | DXY chg60 < q10 (FX/EASn) | FX/EASn 재검토 |
| VNM | DXY chg60 + T10Y3M 극단 | FX/rates 후보 |
| CIBR | VIX/VVIX 변화율 | volatility crisis |
| XLF | DXY chg60 + QQQ/SPY (음의 후보) | overlap/momentum 위험 |
| XLU | Net Liquidity 계열 (방어주) | NL P0와 통합 가능 |

#### 진입 절차 (격언 #25 + Audit 1 §4 Lane 분류)

| 단계 | 본질 | 시간 |
|:--:|:--|:--:|
| 1 | Phase A 정량 재검증 (t-stat 산출 + plateau sweep) | 60분 |
| 2 | Lane 결정 (entry/sizing/MoSn/shadow 4 옵션) | 30분 |
| 3 | §B.9 slot 사전 검증 | 20분 |
| 4 | §40 v3 BT 4기간 + STRESS 14 | 35분 |
| 5 | RULE 29 v2 6/6 평가 | 10분 |

🌟 **총 예상**: ~155분 + 외부 FA audit.

### § 9.11 🆕 **P0++ 신규: Lane 분류 audit 체계 정식 등재 (Audit 1 § 4)**

🌟 **결정적 본질**: HYG/LQD entry boost = IWM/SMH/VEA/XLE/INDA 5종 BT FAIL → 시그널 부재 아닌 **lane 오선택** (Audit 1 §3).

#### Lane 의무 검증 체크리스트

| # | 항목 | 본질 |
|:--:|:--|:--|
| 1 | 후보 시그널의 정확한 Lane 결정 (4 옵션) | entry boost / sizing / MoSn / shadow |
| 2 | Lane 별 BT 분리 (entry 실패 시 sizing/MoSn 재시도) | 격언 #56 + #91 ② 정합 |
| 3 | Slot competition pre-check (격언 #52 + #73) | §B.9 의무 |
| 4 | Asset asymmetry 명시 (격언 #46 + #48) | 동일 시그널 자산별 차이 |
| 5 | Sweep + plateau 확인 (격언 #76) | 단일 임계 fitting 회피 |

### § 9.12 🥈 P5+ 격상: MoSn 영역 결정적 미발달 (Audit 2 Tier S)

🚨 **현황**: 20 종목 중 MoSn 적용 = 단 2종 (XLE/VNM).

🌟 **Audit 2 §1 본질**: "강한 알파는 추가가 아니라 제거" → MoSn 영역 = **제거 알파의 잠재 영역** (현행 Macro 직관 단순 가산 vs 환경별 강도 조절).

🌟 **연구 방향**:
- 종목별 BullStack/BearStack RgSn 인터랙션 탐색 (18종)
- MA200/MA250 추가 (장기 추세 확인)
- Stack ratio (m20/m50/m120) 점수화

### § 9.13 🥈 P5+ 격상: ExSn 영역 결정적 미발달 (Audit 2 §9)

🚨 **현황**: 20 종목 중 종목별 individual ExSn = 단 3종 (SLV/TLT/EWZ).

🌟 **Audit 2 §9 본질**: "Exit optimization / partial liquidation / dynamic reduction 향후 큰 연구 가치" → Crown #61 (EWZ DXY ExSn) 첫 성공이 **다음 17종 ExSn 발굴 동력**.

🌟 **연구 방향**:
- GLD: TNX>5 (강금리) 청산
- XLE: T10YIE<1.5 (디스인플레) 청산
- SMH: WTI>100 ∩ VIX<14 (과열) 청산
- IWM: SAHMCURRENT>0.5 (침체 가속) 청산

### § 9.14 🆕 **P1+ 신규: Adaptive Sizing 영역 (Audit 2 Tier S)**

🌟 **Audit 2 Tier S §3**: "Adaptive sizing — 아직 미개척".

🚨 **현황**: 20종 중 sizing modifier 적용 = SLV/COPX 2종만.

🌟 **연구 방향**:
- 종목별 RS 시그널 sizing (SLV RS_20d 모델 18종 확장)
- 매크로 조건부 sizing (DXY/VIX/PMI 환경별)
- Conviction-based scaling (signal_level S/A/B/C → sizing 차등)

### § 9.15 🆕 **P0+ 신규: Slot Suppression 연구 (Audit 2 Tier S §1)**

🌟 **Audit 2 §2 본질**: "ARGUS = stock picker 아닌 slot allocator" → **slot suppression이 strongest alpha source**.

🌟 **연구 방향**:
- Slot competition 정량 분석 (각 자산이 다른 자산의 알파를 얼마나 훼손하는지)
- Suppression matrix (20×20 자산 간 slot poisoning 정량화)
- Conditional suppression rules (특정 매크로 환경에서만 슬롯 차단)

### § 9.16 🆕 **P1+ 신규: Interaction Graph 확장 (Audit 2 Tier S §4)**

🌟 **Audit 2 §5 본질**: Crown #60 (DXY<95 ∩ T10YIE>2) 성공이 **pairwise interaction / conditional regime graph / macro topology** 가능성 입증.

🌟 **연구 방향**:
- 매크로 28종 × 28종 pairwise interaction matrix (756 조합)
- Conditional regime graph (어떤 매크로 환경에서 어떤 매크로가 가산되는지)
- Macro topology (매크로 간 종속성 / 인과 그래프)

### § 9.17 🆕 **P2+ 신규: Dynamic Universe Pruning (Audit 2 Tier A §1)**

🌟 **Audit 2 §8 본질**: Crown #59 (NLR dead asset) 의미 → **universe pruning이 실제 alpha**.

🌟 **연구 방향**:
- Asset death detection 자동화 (현행 manual)
- Replacement candidate auto-discovery (NLR → IVW shadow 등)
- Periodic universe review cadence (annual 또는 quarterly)

### § 9.18 🆕 **P2+ 신규: State Machine 확장 (Audit 2 Tier A §2)**

🌟 **Audit 2 §6 본질**: Crown #67 (WTI/VIX hysteresis) 성공이 **state-machine 방향 입증**.

🌟 **연구 방향**:
- 다른 매크로에 hysteresis 적용 (DXY/T10YIE/PMI hysteresis)
- Multi-state regime machine (Risk-on / Risk-off / Transition / Crisis)
- State transition probability modeling

---

## 📊 § 10. 운영 격언 정합 매트릭스 (총 22건, #112 후보 신설)

| 격언 | 본질 | 본 문서 적용 |
|:--:|:--|:--|
| #11 | CAGR 1순위 | RULE 29 v2 의무 |
| #15 | Commander 절대 결정 | 모든 채택/거부 |
| #20 | 정직 인지 | Audit 1 출처 부재 수치 명시 |
| #25 | Phase A ≠ Phase B | §B.9 + §40 v3 의무 |
| #46 | 자산 비대칭성 | 동일 시그널 자산별 차이 |
| #48 | 종목별 검증 | 일괄 적용 금지 |
| #56 | monkey-patch 회피 | hysteresis 함수 자체 |
| #73 | Conviction Concentration | cap removal -3.5p |
| #80 | Phase A ≠ BT 채택 | 신규 시그널 vs 조건부 분리 |
| #87 | ExSn 사전 평가 의무 | n분포/Phase A/cover |
| #88 v3 | BT 재현성 + 4기간 + STRESS 14 | §40 v3 정합 |
| #91 | 4 패턴 (noise/fitting/plateau/era) | 시그널 분류 정식 |
| #94 | ExSn 우선순위 의무 | ExSn 결정적 미발달 |
| #96 v2 | Data fetch 6단계 의무 | DBnomics 종결 |
| #97 v2 | 외부 audit 의무 | Audit 1 + Audit 2 정합 |
| #98 | 결정 지연 ≠ 중립 | 본 시점 보류 정당화 |
| #106 | 근본 처방 | hysteresis = 근본 |
| #107 | GHA User-Agent 의무 | Discord webhook |
| #109 | BT 기간 SSOT | FULL/P1/P2/MID |
| #110 | 세션 본질 최대화 | 본 문서 본질 ≥85% |
| #111 | SSOT 단일 source | Canonical JSON |
| 🆕 **#112 후보** | **🌟 Slot Allocator 본질 🌟** | **ARGUS = stock picker 아닌 slot allocator. 모든 시그널 평가는 신호 정확도가 아닌 포트폴리오 수익률 기여도로 판정.** |

### § 10.1 🆕 격언 #112 후보 정식 본문 (Audit 2 §2 + §10)

> **🌟 격언 #112: Slot Allocator 본질 (2026-05-13 신설 후보) 🌟**
>
> ARGUS 엔진의 본질은 **stock picker가 아닌 slot allocator**다. 시그널 품질의 진정한 기준은 "예측 정확도"가 아니라 **"최종 포트폴리오 CAGR/Sharpe 기여도"**다.
>
> **운영 원칙**:
> 1. 모든 후보 평가는 §40 v3 BT 4기간 + STRESS 14 결과로 판정
> 2. Phase A 강함 ≠ Phase B alpha (격언 #25 정합)
> 3. 가장 강한 알파 source = "추가"가 아닌 **"잘못된 슬롯 점유 제거"** (Audit 2 §1)
> 4. Asset asymmetry 의무 검증 (격언 #46 정합)
> 5. Slot competition pre-check (§B.9 의무, 격언 #52 + #73 정합)
>
> **결정적 입증 사례 (Audit 2 §1)**:
> - Crown #44 (COPX NL 제거) = S급
> - Crown #45 (COPX TNX 제거) = S+급
> - Crown #47 (SMH MOVE 제거) = S급
> - Crown #53 (SLV DXY>101 EASn) = S급
>
> 모두 "좋은 신호 추가"가 아닌 "잘못된 진입 제거"가 알파 source.

---

## 📊 § 11. 시그널 발굴 사이클 로드맵 (다음 12 사이클, v2 재정렬)

| Cycle | 우선 | 작업 | 예상 시간 |
|:--:|:--:|:--|:--:|
| S102 | P0 | Crown #67 dual-run Step 2 외부 FA | 외부 |
| S103 | 🆕 P0+ | **Relative breadth GLD RSP/SPY Phase A 정량 재검증** | 90분 |
| S104 | 🆕 P0++ | **Lane 분류 audit 체계 SSOT 정식 등재** | 60분 |
| S105 | P0 | NL EnSn TLT 단일 §40 v3 BT (격언 #88) | 95분 |
| S106 | P0 | NL EnSn plateau sweep 5종 (PAVE/INDA/CIBR/QQQM/COPX) | 180분 |
| S107 | 🆕 P0+ | **Relative breadth CQQQ COPX/GLD + COPX QQQ/SPY BT** | 240분 |
| S108 | P1 | 조합 P0 T10Y3M<0 ∩ SAHM>0.3 BT | 120분 |
| S109 | 🆕 P0+ | **Slot Suppression Matrix 정량 분석 (20×20)** | 300분 |
| S110 | P3 | DEAD EnSn 보강 (NLR 대체 신규 발굴) | 240분 |
| S111 | P4 | 임계값 차원 C/D sweep 1차 (5종 핵심) | 300분 |
| S112 | 🆕 P5+ | **MoSn 영역 발굴 (18종 BullStack/BearStack Phase A)** | 360분 |
| S113 | 🆕 P5+ | **ExSn 영역 발굴 (17종 individual ExSn Phase A)** | 360분 |
| S114 | 🆕 P1+ | **Adaptive Sizing 18종 + Interaction Graph 확장 (756 pairs)** | 600분 |

🌟 **총 예상**: ~50시간 (외부 FA 제외, 12+ 사이클 합산, v1 30시간 → v2 50시간 확장).

---

## 📊 § 12. 본 문서 본질 정리 (v2)

🌟 **현 ARGUS LIVE 시그널 자산**:
- 📥 **EnSn**: 141건 (20 종목 × 평균 7건)
- ⚡ **EASn**: 18건 (대부분 WTI>85 단순)
- 📊 **MoSn**: 3건 (XLE/VNM, 결정적 미발달)
- 📤 **ExSn**: 8건 (7 일반 + 3 individual, 결정적 미발달)
- 🌟 **인터랙션 RgSn**: 9건 (격언 #44 역방향)
- 🚨 **DEAD/부재**: 4종 (NLR/QQQM/XLU/CIBR)

🌟 **v2 신규 등록 향후 연구 영역 (12건)**:
1. 🥇 **NL EnSn TLT 가산** (Phase A t=+13.51) — 기존
2. 🥈 **조합 인터랙션 6종** — 기존
3. 🥉 **DEAD EnSn 4종 보강** — 기존
4. **임계값 최적화 5 차원** — 기존
5. **MoSn 영역 (18종)** — 기존, 격상
6. **ExSn 영역 (17종)** — 기존, 격상
7. 🆕 **Relative Breadth Batch 6 후보** — Audit 1 신규
8. 🆕 **Lane 분류 audit 체계** — Audit 1 신규
9. 🆕 **Slot Suppression Matrix (20×20)** — Audit 2 Tier S §1 신규
10. 🆕 **Adaptive Sizing (18종 확장)** — Audit 2 Tier S §3 신규
11. 🆕 **Interaction Graph (756 pairs)** — Audit 2 Tier S §4 신규
12. 🆕 **State Machine 확장 (DXY/T10YIE/PMI hysteresis)** — Audit 2 Tier A §2 신규

🚨 **결정적 운영 원칙 (v2 강화)**:
- 모든 후보는 §40 v3 (4기간 BT + STRESS 14) + RULE 29 v2 (5축) 의무
- Phase A 강함 ≠ Phase B alpha (격언 #25 결정적)
- 외부 FA P0 audit 필수 (격언 #97 v2)
- 🆕 **Lane 분류 의무** (entry/sizing/MoSn/shadow) — Audit 1 §4
- 🆕 **Slot allocator 본질 인지** — 격언 #112 후보 (Audit 2 §2)
- Commander 절대 결정권 (격언 #15)

---

## 📊 § 13. 🆕 Audit 2 — Crown System Final Review 10대 메타 발견 통합

🌟 **출처**: 외부 audit S101#2 (2026-05-13 KST), Crown #41~#67 실 BT 재검증 기반.

### § 13.1 Crown 전체 재평가 (Audit 2 §2)

| Crown | 핵심 | 최종평가 | 유형 |
|:--:|:--|:--:|:--|
| #41 | GLD dead cleanup | ⚪ hygiene | dead cleanup |
| #42 | MA cleanup | ⚪ hygiene | cleanup |
| #43 | SLV PMI 제거 | 🟡 약함 | recession legacy |
| **#44** | **COPX NL 제거** | 🌟 **S급** | **slot alpha** |
| **#45** | **COPX TNX 제거** | 🌟 **S+급** | **structural alpha** |
| #46 | EWZ WTI 제거 | 🟢 A급 | asset asymmetry |
| **#47** | **SMH MOVE 제거** | 🌟 **S급** | **regime cleanup** |
| #48 | QQQM dead cleanup | ⚪ hygiene | dead cleanup |
| #49 | VEA PMI 제거 | 🟡 약함 | P1 only |
| #50 | audit partial | ⚪ 거의 dead | infra/safety |
| #52 | TLT conditional | 🟡 방어형 | defensive |
| **#53** | **SLV DXY>101** | 🌟 **S급** | **macro asymmetry** |
| #58 | NLR TNX dead | ⚪ dead transition | dead asset precursor |
| #59 | NLR dead asset | ⚪ exact dead | universe pruning |
| #60 | SLV interaction | 🟢 A급 | interaction alpha |
| #61 | EWZ DXY ExSn | 🟢 A급 | ExSn success |
| **#67** | **WTI/VIX hysteresis** | 🌟 **S급** | **state engine** |

🌟 **S급/S+급 5건**: #44, #45, #47, #53, #67 → 본질 = **"잘못된 진입/가산 제거" (4건) + "state engine" (1건)**.

### § 13.2 10대 메타 발견 (Audit 2 §3~§12)

| # | 발견 | 본질 | 격언 정합 |
|:--:|:--|:--|:--:|
| 🌟 1 | **"추가"보다 "제거"가 강력** | S급 5건 중 4건 = 잘못된 진입 제거 | #112 후보 |
| 🌟 2 | **Slot competition = 진짜 본질** | ARGUS = stock picker 아닌 slot allocator | #112 후보 |
| 🌟 3 | **Macro 직관 자주 틀림** | TNX↑→COPX 약화 직관 → 실제 제거가 강함 | #25 |
| 🌟 4 | **Asset asymmetry 강함** | GLD/SLV/COPX/EWZ 동일 시그널 ≠ 동일 결과 | #46/#48 |
| 🌟 5 | **Interaction alpha 진짜 존재** | Crown #60 DXY<95 ∩ T10YIE>2 성공 | #91 |
| 🌟 6 | **Hysteresis > threshold** | Crown #67 state engine 결정적 | #106 |
| 🌟 7 | **Stress robustness 중요** | CAGR 양수 + STRESS 탈락 후보 다수 | #88 v3 |
| 🌟 8 | **Dead code 검출 체계 유효** | Crown #41/#48/#59 exact zero 재현 | #56 |
| 🌟 9 | **ExSn 연구 가능성 입증** | Crown #61 EWZ DXY 첫 성공 | #87/#94 |
| 🌟 10 | **Signal quality = 포트폴리오 기여도** | 예측력 아닌 CAGR/Sharpe 기여도 | #11/#15/#112 |

---

## 📊 § 14. 🆕 Audit 2 — Tier S/A/B 우선순위 통합 매트릭스

🌟 **출처**: Audit 2 §13~§15.

### § 14.1 Tier S — 최우선

| 연구 | 이유 | S101 v2 등재 |
|:--:|:--|:--:|
| Slot suppression | strongest alpha source | § 9.15 신규 |
| Hysteresis state | Crown #67 성공 | § 7.1 / § 9.18 |
| Adaptive sizing | 아직 미개척 | § 9.14 신규 |
| Interaction graph | Crown #60 성공 | § 9.16 신규 |
| ExSn optimization | Crown #61 성공 | § 9.13 격상 |

### § 14.2 Tier A

| 연구 | 이유 | S101 v2 등재 |
|:--:|:--|:--:|
| Dynamic universe pruning | Crown #59 의미 | § 9.17 신규 |
| State machine | regime 안정성 | § 9.18 신규 |
| Partial exits | stress 최적화 | § 9.13 통합 |

### § 14.3 Tier B (위험 인지)

| 연구 | 위험 | S101 v2 대응 |
|:--:|:--|:--|
| 단순 additive macro | 이미 포화 경향 | Audit 2 §3 정합 — 추가보다 제거 강조 |
| threshold sweep | 과최적화 위험 | § 9.4 P3 임계값 최적화 — **신중 검토 필요** |

🚨 **결정적 본질**: Audit 2 Tier B "threshold sweep 과최적화 위험" = 본 S101 v1 P3 임계값 최적화 5 차원과 정합 충돌 → **격언 #25 + #91 (fitting + fragile) 정합 의무**. Commander 결정 필요.

---

## 📊 § 15. 🆕 Audit 2 — 3 구조적 위험 인지 (Live Forward 검증 의무)

🌟 **출처**: Audit 2 §16~§18.

### § 15.1 🚨 Overfitting 가능성

| 영역 | 위험 본질 | 대응 |
|:--|:--|:--|
| threshold sweep | 과최적화 | live forward + walk-forward + unseen regime 의무 |
| interaction explosion | 756 pairs 조합 폭발 | Sweep + plateau 의무 (격언 #76) |
| asset-specific tuning | 종목별 미세 조정 fitting | Asset asymmetry 명시 (격언 #46/#48) |

### § 15.2 🚨 Crown Inflation

🌟 **본질**: 현 Crown 번호 = alpha + cleanup + infra + shadow 혼합 → **번호 자체는 품질 척도가 아님**.

🌟 **연구 방향**:
- Crown 품질 정량 기준 신설 (S/S+/A/B/C 5단계 통일)
- Hygiene Crown vs Alpha Crown 명시 분리
- Crown ID 재정렬 검토 (역사적 SSOT 보존 + tag 추가)

### § 15.3 🚨 Live Forward Validation 부족

🚨 **결정적 weakness**:

| 영역 | 미검증 본질 |
|:--|:--|
| slippage | LIVE 거래 시 실제 체결 차이 |
| revision | 매크로 지표 revision (PMI/ICSA) |
| latency | data fetch latency |
| regime drift | 신규 매크로 환경 (2026년+) |

🌟 **대응**: Crown #67 dual-run (S102 외부 FA) → 최소 3영업일 + 격언 #112 후보 정합 운영.

---

## 📊 § 16. 본 v2 통합 본질 정리

🌟 **v1 → v2 변경 본질**:

| 영역 | v1 | v2 |
|:--:|:--:|:--:|
| 향후 연구 영역 | 9건 | 🌟 **17건 (12 신규)** 🌟 |
| 격언 | 21건 | 🌟 **22건 (#112 후보 신설)** 🌟 |
| 사이클 로드맵 | 12 사이클 30시간 | 🌟 **12+ 사이클 50시간** 🌟 |
| 외부 audit 통합 | 0건 | 🌟 **2건 (Audit 1 + Audit 2)** 🌟 |
| Lane 분류 | 부재 | 🌟 **4 Lane (entry/sizing/MoSn/shadow)** 🌟 |
| 메타 통찰 | 부분 | 🌟 **10대 메타 발견 정식 등재** 🌟 |
| 위험 인지 | 부분 | 🌟 **3 구조적 위험 정식 등재** 🌟 |

🌟 **결정적 본질 (v2)**:
- ARGUS = stock picker 아닌 slot allocator (격언 #112 후보)
- 가장 강한 알파 source = "추가"가 아닌 **"잘못된 슬롯 점유 제거"**
- Phase A 강함 ≠ BT alpha (격언 #25)
- Lane 분류 의무 (entry/sizing/MoSn/shadow)
- threshold sweep + interaction explosion 위험 인지
- Live forward validation 의무

🌟 **현 시점 LIVE 상태**: Crown #67 = PRIMA_v5_19_VIX_HYST_LIVE + briefing v8.9.3. dual-run candidate Step 1 push 대기.

---

🦅 *Omnioculus Vigilantia* — ARGUS 시그널 마스터 v2 + 향후 연구과제 SSOT 정식 등재 + 외부 audit 2건 통합 + 격언 #112 후보 신설. 본 문서 = S101 #2 종결 시점 ARGUS 시그널 전수 + 12+ 사이클 로드맵 + 격언 #110 (본질 최대화) + 격언 #97 v2 (외부 audit 의무) 정합 단일 reference.
