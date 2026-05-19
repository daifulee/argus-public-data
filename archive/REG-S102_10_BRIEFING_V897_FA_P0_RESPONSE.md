# 📋 REG-S105_5 — P3-4 XLF Credit Decomposition Phase B 자동 거부

| 항목 | 값 |
|:--|:--|
| 등재일 | 2026-05-16 KST |
| Session | S105 #1 (P3-4 자율 진행) |
| 영역 | XLF Credit Decomposition Signal Stack |
| 결정자 | Commander Lignas (Phase B OOS 정합 자동 거부) |
| 격언 정합 | #20 / #73 (본격 입증) / #80 / #98 / #112 v2 (정식 채택 사례 #5) |
| 선행 학습 | REG-S105_3 (NLR) + REG-S105_4 (VNM) — 동일 patterns 정합 |

---

## § 0. 결론 우선

🚨 **P3-4 XLF Credit Decomposition Signal Stack 자동 거부** — Phase B 5 variant 모두 폐기.

🌟 **OAS_HY_60d_chg t=-15.74** = ARGUS 역대 최강 통계 신호 → 그러나 LIVE alpha 부재.

🌟 **격언 #112 v2 정식 채택 사례 #5 확정** (5 사례 누적).

🟢 **Crown #67 LIVE 무변** — entry_XLF OAS_HY>7.0 Hard Gate 정당성 재입증.

---

## § 1. Phase A 결과 (12 강 후보)

### 1.1 Credit Decomposition 6건 (External, look-ahead 부재)

| 순위 | Signal | Δ | t | 분류 |
|:-:|:--|:-:|:-:|:-:|
| 🥇 | OAS_HY_60d_chg>+15% | **-6.99p** | **-15.74** | EASn |
| 🥈 | OAS_HY_60d_chg<-15% | +4.66p | +9.77 | EnSn |
| 🥉 | HY-IG spread_60d<-15% | +4.27p | +9.60 | EnSn |
| 4 | HYG_LQD_RS>+2% | +2.31p | +6.00 | EnSn |
| 5 | HYG_LQD_RS<-2% | -2.66p | -5.98 | EASn |
| 6 | HY-IG spread>3.0 | +1.06p | +3.03 | EnSn |

### 1.2 Self-ref 5건 (look-ahead 위험)

| Signal | Δ | t | 분류 |
|:--|:-:|:-:|:-:|
| XLF_DEV120>+15 | +6.35p | +8.03 | EnSn |
| XLF_BearStack | -2.86p | -6.55 | EASn |
| XLF_m1>+10% | +5.24p | +6.41 | EnSn |
| XLF_BullStack | +1.70p | +4.89 | EnSn |
| XLF_DEV120<-10 | -2.03p | -3.38 | EASn |

⚠️ **P3-2 학습 의무**: Self-ref Phase B 진입 부재.

### 1.3 상대 강도 1건

| Signal | Δ | t |
|:--|:-:|:-:|
| XLF_rel_SPY_m3>+5p | +3.15p | +6.06 |

---

## § 2. Phase B 본격 결과 (5 External Variant)

### 2.1 Variant 영역

| Variant | 영역 | IN ΔC | OOS ΔC | OOS ΔM | 판정 |
|:-:|:--|:-:|:-:|:-:|:--|
| V1 | OAS_HY_60d_chg>+15% Hard EASn | -0.43p | 0.00 | 0.00 | 🔴 폐기 |
| V2 | OAS_HY_60d_chg<-15% EnSn 가산 | +0.06p | 0.00 | 0.00 | 🔴 폐기 |
| V3 | HYG_LQD_RS<-2% Hard EASn | **-5.03p** | **-3.07p** | **-1.35p** | 🔴 폐기 (큰 손실) |
| V4 | OAS_HY_60d_chg 양방향 | -0.36p | 0.00 | 0.00 | 🔴 폐기 |
| V5 | Full (HY_chg + HYG_LQD_RS) | **-5.05p** | **-3.07p** | -1.35p | 🔴 폐기 (가장 큰 손실) |

### 2.2 본격 본질 발견 3건

#### 2.2.1 V3/V5 OOS -3.07p — slot stealing 본격 입증

| 영역 | 본격 본질 |
|:--|:--|
| HYG_LQD_RS<-2% Hard EASn | XLF 진입 자체 차단 (Credit 위기 환경) |
| 결과 | 진입 차단 시기 = 실제 XLF 상승 시기 (false positive) |
| OOS -3.07p | 다른 자산 slot 박탈 + XLF 미진입 = 큰 손실 |
| 격언 #73 정합 | Hard Gate 추가 = slot stealing 음수 |

#### 2.2.2 V1/V2/V4 진입 부재 + in-sample micro 손실

| 영역 | 본질 |
|:--|:--|
| OOS 0 | XLF LIVE 진입 자체 부재 영역 (Crown #67 LIVE 영역 baseline) |
| IN_SAMPLE -0.43/-0.36 | 2008 GFC 영역 baseline 영역 baseline 약간 영향 (slot 영역 baseline 박탈) |
| 본질 | Credit signal 추가 = XLF 영역 baseline 진입 빈도 추가 차단 |

#### 2.2.3 ARGUS 역대 최강 t-stat 영역 baseline LIVE alpha 부재

| 영역 | 값 |
|:--|:--|
| Phase A OAS_HY_60d_chg t | **-15.74** (ARGUS 역대 최강) |
| Phase B Variant V1 OOS | **0.00** (LIVE alpha 부재) |
| 본격 본질 | t-stat 강함 ≠ LIVE alpha (격언 #80 본격 입증) |

---

## § 3. 격언 #112 v2 정식 채택 사례 #5 확정

### 3.1 사례 누적 (5건)

| 사례 | 세션 | 영역 | OOS 결과 | 판정 |
|:-:|:-:|:--|:--|:--|
| #1 | S105 #1 | S105-QA Phase 0 score multiplier | OOS -0.32pp 음수 | 폐기 ✅ |
| #2 | S105 #1 | P2-1 TLT 임계 1.5→1.0 | avg -0.007pp micro | reject ✅ |
| #3 | S105 #1 | P3-2 NLR_v2 self-ref | 5/5 폐기 (변환률 0%) | 자동 거부 ✅ |
| #4 | S105 #1 | P3-3 VNM External EM | 5/5 폐기 (변환률 0%) | 자동 거부 ✅ |
| **#5** | **S105 #1** | **P3-4 XLF Credit Decomp** | **5/5 폐기 (V3/V5 OOS -3.07p)** | **자동 거부 ✅** |

### 3.2 정식 채택 의무 baseline 강화

5 사례 누적 = **격언 #112 v2 정식 채택 의무 무조건 baseline**.

본격 본질:
> **"Phase A 강함 (t-stat 매우 큼) ≠ Phase B alpha (LIVE 채택)"**
> 
> 5 사례 영역 baseline OAS_HY_60d_chg t=-15.74 (역대 최강) 영역 baseline 영역 baseline LIVE alpha 부재.
> Walk-Forward OOS BT 영역 baseline 영역 baseline 절대 의무.

---

## § 4. Crown #67 LIVE 무변 + entry_XLF 정당성 재입증

### 4.1 LIVE 차원 영향 (변경 없음)

| 항목 | 값 |
|:--|:--|
| Crown LIVE | 🌟 #67 = PRIMA_v5_19_VIX_HYST_LIVE_v4 (무변) |
| LIVE 포지션 | 🌟 TLT 100% (무변) |
| entry_XLF() | OAS_HY>7.0 Hard Gate + DFII10/WTI/TNX/FVX_5Y/MOVE (무변) |
| ENTRY_THRESHOLD['XLF'] | 무변 |

### 4.2 entry_XLF OAS_HY>7.0 Hard Gate 본격 정당성

기존 entry_XLF logic = **OAS_HY>7.0 (90 percentile)** Hard Gate baseline.

**본 P3-4 결과 baseline 영역 baseline 검증**:
- OAS_HY_60d_chg>+15% (V1) → OAS_HY>7.0 영역 baseline 포함 (대부분 중복)
- HYG_LQD_RS<-2% (V3) → IG 우월 시점 = 신용 위기 (OAS_HY>7.0 정합)
- 따라서 OAS_HY>7.0 Hard Gate 영역 baseline = **이미 본격 Credit risk 영역 baseline 차단** baseline.

→ Credit Decomposition 추가 의미 부재 + slot stealing 영역 baseline 손실.

---

## § 5. 본 cycle 본격 patterns (3 사례 연속)

| 영역 | P3-2 NLR | P3-3 VNM | P3-4 XLF |
|:--|:--|:--|:--|
| 1Y alpha (vs SPY) | +52.70p | +14.79p | **-15.81p** |
| Phase A 강 후보 | 6건 | 10건 | 12건 |
| Phase B 채택 | 0건 | 0건 | 0건 |
| 변환률 | 0% | 0% | 0% |
| OOS 손실 | 0 | 0 | **-3.07p (V3/V5)** |
| 본격 본질 | 격언 #80 입증 | 격언 #73 + #80 | 격언 #73 + #80 + 본격 손실 사례 |

→ **3 사례 연속 본격 입증** baseline. ARGUS LIVE 엔진 매우 robust + 외부 signal 추가 의미 부재 baseline.

---

## § 6. 격언 정합 audit

| 격언 | 정합 |
|:--|:--|
| #20 (정직 인지) | ✅ "역대 최강 t=-15.74 ≠ LIVE alpha" 본격 명시 |
| #73 (slot stealing) | 🌟 **본격 입증** — V3/V5 OOS -3.07p (Hard Gate 추가 영역 baseline 큰 손실) |
| #80 (도구 ≠ alpha) | 🌟 본격 강화 사례 (t=-15.74 영역 baseline LIVE alpha 부재) |
| #98 (Commander 절대 권한) | ✅ Commander 채택 기준 정합 자동 거부 |
| **#112 v2** | 🌟 **정식 채택 사례 #5 확정** (5 사례 누적 = 무조건 정식 채택 baseline) |

---

## 🦅 본 REG 결론

P3-4 XLF Credit Decomposition Signal Stack = **자동 거부 정식 등재** baseline.

본격 본질:
1. 🚨 ARGUS 역대 최강 t-stat (OAS_HY_60d_chg=-15.74) 영역 LIVE alpha 부재
2. 🚨 V3/V5 OOS -3.07p = slot stealing 본격 손실 사례
3. 🌟 격언 #73 본격 입증 (Hard Gate 추가 = slot 박탈)
4. 🌟 격언 #112 v2 정식 채택 사례 #5 확정 (5 사례 누적)
5. 🟢 entry_XLF OAS_HY>7.0 Hard Gate 본격 정당성 재입증

🎯 **본격 결정적 본질**: ARGUS LIVE 엔진 매우 robust. 외부 신호 추가 = slot stealing 손실 baseline 의무.

*Omnioculus Vigilantia* — P3-4 XLF Credit Decomposition 자동 거부 정식 등재.
