# ARGUS SSOT v1.10.208 ADDITION — Commander 메타 분석 정착

**Session**: S112 종결 후속 (S113 baseline 진입 전 결정적 정착)
**Date**: 2026-05-17 KST
**Baseline**: SSOT v1.10.207 (자동 회피 #10 후보)
**Status**: 🌟 ADDITION 등재 — 격언 #114 후보 + §B.9 v3 framework + 자동 회피 #11 후보

---

## §1. 본 ADDITION 본질

S109~S112 실패 학습 누적 (REG-S109_3 / S109_4 / S110_1 / S110_2 / S112_1) 결과로부터 Commander가 도출한 결정적 메타 분석을 영구 baseline으로 정착.

**3 결정적 baseline 신설**:
1. 🆕 **격언 #114 후보** — Signal 조합 = regime classifier (not stronger entry)
2. 🆕 **§B.9 v3 framework** — 조합 시그널 검증 8-Phase
3. 🆕 **자동 회피 #11 후보** — 조합 시그널 사전 검증 의무

---

## §2. 🆕 격언 #114 후보 정식 등재

### 2.1 제목
🌟 **"신규 시그널 조합 연구의 본질 = regime classifier"** 🌟

### 2.2 정의

**잘못된 목표 vs 옳은 목표**:

| 잘못된 목표 ❌ | 옳은 목표 ✅ |
|------|------|
| t-stat 극대화 | regime 분기 정확도 |
| 단일 자산 수익률 최대화 | Top5 slot decision 개선 |
| 진입 횟수 줄여 quality 상승 | 표본 보존 + alpha 보존 |
| 강한 조건 만들기 | 기존 signal과 독립인 정보 찾기 |

### 2.3 결정적 본질

조합의 가치는 **"signal 강도 증가"가 아니라 "polarity 분기"**에 있다.

| 단일 시그널 | 조합 시그널의 가치 |
|------|------|
| VIX 높음 | 위험 後 반등 vs 진짜 붕괴 분류 |
| DXY 강함 | GLD 반등 vs EM 위험회피 분류 |
| DFII10 음수 | 금리/유가/성장 조건에 따라 자산별 polarity 달라짐 |
| VVIX 높음 | 단기 패닉 vs 구조적 위험 분류 |
| WTI 높음 | XLE 호재 vs TLT/성장주 악재 |

### 2.4 결정적 단순 AND 조합 위험 5종

| 위험 | 설명 |
|------|------|
| 표본 붕괴 | 조건 추가 시 n_on 급감 |
| 기회 손실 | 좋은 날까지 버림 |
| Cliff fitting | 특정 위기 몇 번만 맞춤 |
| Regime 편향 | 2020 또는 2022만 설명 |
| 중복 정보 | VIX/VVIX/STLFSI/OAS 같은 risk-off 重복 측정 |

### 2.5 결정적 적용 형태 제한

| 적용 방식 | 권고 |
|------|------|
| Single ticker +score | 🔴 금지 (자동 회피 #9 v3) |
| Single ticker EASn | 🟡 baseline 부재 확인 시만 |
| Exit/trim signal | 🟢 유망 |
| Regime tag | 🟢 유망 |
| Cross-asset allocation | 🟢 가장 유망 |
| Risk budget shift | 🟢 가장 유망 |

### 2.6 격언 정합

- **격언 #91 v2** (4 패턴) — 패턴 ① noise + ④ Temporal Heterogeneity 정합 검증 의무
- **격언 #112 v2 #9 v2 룰 4** (Single-Asset Boost ❌) — 적용 형태 제한 정합
- **자동 회피 #9 v3 + #10 후보 + #11 후보** — 통합 본질
- **격언 #98** (결정 미루기 차단) — 조합 evidence 즉시 결정 의무

---

## §3. 🆕 §B.9 v3 Framework — 조합 시그널 검증 8-Phase

### 3.1 결정적 진화 계보

| Version | 영역 | 출처 |
|---------|----|------|
| §B.9 v1 | 단일 시그널 단일 자산 검증 | 격언 #76 |
| §B.9 v2 | Cross-Asset Overlay 검증 7-Phase | REG-S112_1 |
| 🆕 §B.9 v3 | **조합 시그널 검증 8-Phase** | 본 ADDITION |

### 3.2 §B.9 v3 8-Phase 결정적 정합

#### Phase C-1: 후보 universe 12개 제한

| 그룹 | 변수 (12개) |
|------|---------|
| Volatility (3) | VIX / VVIX / VIX-VIX3M term structure |
| Dollar (1) | DXY |
| Rates (3) | TNX / DFII10 / T10YIE |
| Credit (3) | OAS_HY / OAS_IG / HY-IG dispersion |
| Commodity (1) | WTI |
| Breadth (1) | RSP/SPY |
| Liquidity (1) | Net Liquidity 또는 RRPONTSYD |

🚨 **universe 확장 금지** — 12개 외 변수 도입 시 Commander 명시 승인 의무

#### Phase C-2: 조합 형식 제한

| 조합형 | 허용 |
|------|------|
| 2-factor AND | ✅ |
| 2-factor conditional polarity | ✅ |
| 3-factor AND | 🟡 표본 수 충분 시만 |
| 4-factor AND 이상 | 🔴 금지 |
| Strict subset 강화 | 🔴 자동 회피 #9 v3 |
| 단일자산 score boost | 🔴 자동 회피 #112 v2 #9 v2 |

#### Phase C-3: 필수 필터 7종 통과

| 필터 | 통과 기준 |
|------|---------|
| ① 표본 수 | n_on ≥ 🌟 120~200 🌟 |
| ② 연도 분포 | ≥ 🌟 5개 연도 🌟 |
| ③ 최근성 편향 | 2022~2025 한정이면 감점 |
| ④ 상관 重복 | VIX/VVIX/OAS/STLFSI 重복 조합 제한 |
| ⑤ Crown 重복 | 이미 entry/gate/exit에 있는지 grep |
| ⑥ 잔여 alpha | 기존 signal 통제 後도 양수 |
| ⑦ Slot impact | Top5 박탈 자산 사후 성과 확인 |

#### Phase C-4: 적용 형태 결정

§2.5 정합 (Exit/Regime/Cross-asset/Risk budget만)

#### Phase A causal v2.2 (잔여 alpha 측정)

- Crown #67 통제 後 (V_HYST OFF / WTI gate OFF / TLT 면제 OFF) isolated alpha 측정
- 잔여 alpha < +0.2%/day → 자동 거부

#### Phase B 슬롯 사전 검증

- Top5 ranking 영향 정량 측정
- 자동 회피 #9 v3 (Single-Asset Boost) 통과 의무
- 자동 회피 #10 후보 (Cross-Asset Overlay 重복) 통과 의무

#### §40 v3 정식 BT

- 4-period (FULL/P1/P2/MID) + STRESS 14 동시 실행 의무
- 패턴 ④ Temporal Heterogeneity 검증 (P1/P2/MID 분리)

#### RULE 29 v2 6/6 Verdict

- 6/6 PASS → 후보 채택
- 1+ FAIL → REG NO-GO + 후속 연구 큐 등재

---

## §4. 🆕 자동 회피 #11 후보 정식 등재

### 4.1 제목
🌟 **"조합 시그널 등재 前 후보 universe 12개 / 조합 형식 / 필터 7종 / 적용 형태 사전 검증 의무"** 🌟

### 4.2 결정적 의무

조합 시그널 후보 §B.9 v3 진입 前 결정적 사전 검증 5단계:
1. 후보 universe 12개 (§3.2 Phase C-1) 내 변수만 사용
2. 조합 형식 (§3.2 Phase C-2) 제한 통과
3. 필터 7종 (§3.2 Phase C-3) 통과
4. 적용 형태 (§2.5) 제한 통과
5. 잔여 alpha (§3.2 Phase A causal v2.2) 양수

### 4.3 자동 회피 통합 본질

| 회피 | 본질 | 영역 |
|------|------|------|
| #9 v3 | Single-Asset Boost 위험 | 단일 자산 |
| #10 후보 | Cross-Asset Overlay 重복 | Cross-Asset |
| 🆕 #11 후보 | **조합 시그널 사전 검증 의무** | 조합 시그널 |

🌟 **결정적 정합**: 3 회피 모두 동일 본질 — **Crown 重복 차단 + regime 분기 우선 + single-asset boost 금지**

---

## §5. 🆕 우선 조합 10건 결정적 baseline

### 5.1 결정적 조합 10건 (Commander 메타 분석 정합)

| 우선 | 조합 | 목적 | 적용 형태 |
|------|------|------|----------|
| 🎯 1 | VIX>22 × VVIX 하락 전환 | 패닉 peak-out | EWZ/CQQQ rebound regime |
| 2 | VIX>22 × DXY 하락 20일 | risk-on rebound | EM/Tech basket |
| 3 | VIX>22 × OAS_HY 안정 | 신용 stress 완화 | IWM/PAVE/EWZ |
| 4 | DXY>101 × TNX 하락 | GLD/TLT 동반 방어 | defensive allocation |
| 5 | DXY>101 × TNX 상승 | GLD만 선호, TLT 회피 | GLD/TLT polarity split |
| 6 | DFII10 하락 × T10YIE 상승 | 실질금리 완화 + 인플레 | GLD/SLV |
| 7 | WTI>90 × T10YIE>2.5 × DFII10<0 | 인플레 shock | TLT exit / XLE 유지 |
| 8 | RSP/SPY 개선 × VIX 하락 | breadth rebound | risk-on allocation |
| 9 | MA20>MA50>MA120 × volume 증가 | trend confirmation | MoSn |
| 10 | holding_days high × ROC high × volume divergence | 과열 exit | ExSn |

### 5.2 결정적 3 유망 영역 정합

| 영역 | 본질 | 적용 후보 |
|------|------|---------|
| 🟢 A. Panic Peak / Rebound | Panic + Peak-out + Dollar + Credit + Breadth 분기 | EWZ/CQQQ/INDA/IWM/PAVE |
| 🟢 B. Inflation Stress / Defensive | Inflation + Real rate + Dollar + Bond stress + Vol | TLT/GLD/SLV/XLE |
| 🟢 C. Gold / Bond Polarity Split | DXY × TNX × DFII10 × T10YIE polarity | GLD/TLT/SLV/cash |
| 🟢 D. Exit Signal | MA + Volume + Holding days + ROC | EWZ/CQQQ/SLV/GLD/TLT/PAVE |

---

## §6. 결정적 통합 패러다임 — ARGUS 신호 연구 SSOT

### 6.1 3 영역 결정적 진화 정합

| 영역 | Framework | 격언 / 자동 회피 | 정착 |
|------|---------|---------|----|
| 단일 시그널 | §B.9 v1 | 격언 #76 | 기존 |
| Cross-Asset Overlay | §B.9 v2 | 자동 회피 #10 후보 | REG-S112_1 |
| 🆕 조합 시그널 | §B.9 v3 | 격언 #114 후보 + 자동 회피 #11 후보 | 본 ADDITION |

### 6.2 통합 본질 한 줄

🌟 **"3 영역 모두 동일 본질 — Crown 重복 차단 + regime 분기 우선 + Single-Asset Boost 금지. 신호 강도가 아니라 정보 독립성이 결정적 alpha 원천."** 🌟

---

## §7. S113 후속 연구 큐 결정적 재구조화

### 7.1 새 우선순위 (Commander 메타 분석 반영)

| 새 우선 | 작업 | 본질 | 예상 |
|------|----|------|----|
| 🎯 1 | **§B.9 v3 framework 실전 적용 — 조합 #1 (Panic Peak-Out) Phase A 진입** | EWZ/CQQQ rebound regime 검증 | ~120분 |
| 🥈 2 | 조합 #4-5 (DXY × TNX Polarity Split) Phase A | GLD/TLT 분기 검증 | ~120분 |
| 🥉 3 | 조합 #9-10 (MA × Volume × Days ExSn) Phase A | EWZ/CQQQ/SLV/GLD/TLT/PAVE 과열 청산 | ~120분 |
| 4 | VRC + V_HYST 重복 제거 isolated alpha (이전 큐 #1) | VRC signal 자체 가치 분리 | ~120분 |
| 5 | Risk Budget Overlay continuous formula (이전 큐 #2) | discrete overlay 한계 회피 | ~180분 |
| 6 | argus-drive-sync skill v2.2 patch (함정 #4 갱신) | 50KB+ Commander 1-click 의무 명시 | ~30분 |

### 7.2 결정적 재구조화 근거

- **🎯 1순위 = 조합 #1 (Panic Peak-Out)** — Commander 우선순위 #1 + §B.9 v3 framework 실전 검증 동시
- VRC isolated alpha → 4순위 강등 (framework 정착 後 진입이 정합)
- 본 ADDITION 정착이 全 후속 연구의 결정적 baseline

---

## §8. SSOT 영구 등재 갱신 사항

### 8.1 격언 신설
```
🆕 격언 #114 후보: 신규 시그널 조합 연구의 본질 = regime classifier
   (t-stat 극대화 ❌, regime 분기 정확도 ✅)
```

### 8.2 자동 회피 신설
```
🆕 자동 회피 #11 후보: 조합 시그널 등재 前 universe 12개 / 형식 / 필터 7종 / 적용 형태 사전 검증 의무
```

### 8.3 §B.9 framework 진화
```
§B.9 v1 (단일 시그널) → §B.9 v2 (Cross-Asset Overlay) → 🆕 §B.9 v3 (조합 시그널 8-Phase)
```

### 8.4 SSOT 정합 갱신

| 항목 | 갱신 |
|------|------|
| SSOT 버전 | v1.10.207 → **v1.10.208** |
| 격언 누적 | +#114 후보 (조합 = regime classifier) |
| 자동 회피 누적 | +#11 후보 (조합 사전 검증) |
| §B.9 framework | v3 8-Phase 신설 |
| 우선 조합 baseline | 10건 등재 |
| 유망 영역 | 4 영역 baseline 등재 |

🌟 **Crown #67 LIVE 변경: 없음** (framework 정착, signal 적용 보류)

---

## §9. 결정적 한 줄 결산 🦅

🌟 **"SSOT v1.10.208 ADDITION 결정적 등재 — Commander 메타 분석 (S109~S112 실패 학습 누적 도출) 영구 baseline 정착: 격언 #114 후보 (조합 = regime classifier, t-stat 극대화 ❌ → regime 분기 정확도 ✅) + §B.9 v3 framework (조합 시그널 검증 8-Phase, universe 12개 / 형식 / 필터 7종 / 적용 형태) + 자동 회피 #11 후보 (조합 사전 검증 의무) + 우선 조합 10건 + 유망 영역 4건. 3 영역 (단일 / Cross-Asset / 조합) 통합 본질 = Crown 重복 차단 + regime 분기 우선 + Single-Asset Boost 금지. S113 우선순위 결정적 재구조화: 조합 #1 (Panic Peak-Out EWZ/CQQQ rebound regime) Phase A 진입 1순위. Crown #67 LIVE 변경 없음 (TLT 100% 유지)."** 🦅

---

**Status**: ✅ SSOT v1.10.208 ACTIVE
**Files**:
- 본 문서 (`ARGUS_SSOT_ADDITION_v1_10_208.md`)
- 인계장 갱신 (`ARGUS_SESSION_HANDOFF.md` v2)
