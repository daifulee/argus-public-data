# 📋 ARGUS SSOT ADDITION v1.10.202 — P3-2 NLR Uranium Signal Stack Phase A

| 항목 | 값 |
|:--|:--|
| 등재일 | 2026-05-16 KST |
| Session | S105 #1 (P3-2 자율 진행) |
| 영역 | NLR Self-Referential Signal Stack |
| 결정자 | Commander Lignas (격언 #98) |
| 격언 정합 | #11 / #20 / #80 (입증) / #87 / #97 v2 / #98 / #109 |

---

## § 0. 결론 우선

🌟 **6건 강 후보 발견** (|t|>3.0, p<0.05). 그 중 **NLR_m1<-10% (t=+7.05)** = ARGUS 역사상 가장 강한 self-referential signal 중 하나.

🚨 그러나 entry_NLR() = return False, 0 (영구 DEAD) → **LIVE 미보유 alpha 영역**. 격언 #80 본격 입증 사례.

→ Commander 결정 의무: NLR 영구 DEAD 부활 또는 본 알파 영구 포기.

---

## § 1. 본격 NLR 영역 status

| 항목 | 값 |
|:--|:--|
| BT data | NLR_Close / NLR_Volume (4,688 days, 2007-08-15 ~ 2026-04-02) |
| 외부 uranium 매크로 | **부재** (URA / URNM / CCJ / U3O8 / U.UN 모두 외부 fetch 의무) |
| 1Y 성과 | NLR +67.78% vs SPY +15.08% → alpha +52.70p |
| 현재 LIVE | entry_NLR() = return False, 0 (영구 DEAD, S55 #2 결정) |

---

## § 2. Phase A 통계 결과 (12 signal 검증)

### 2.1 강 후보 6건 (|t|>3.0, p<0.05)

| 순위 | Signal | n | strong_ret | baseline_ret | Δ | t-stat | p-val | 본질 |
|:-:|:--|:-:|:-:|:-:|:-:|:-:|:-:|:--|
| 🥇 | NLR_m1<-10% | 283 | +6.46% | +1.42% | **+5.04p** | **+7.05** | 0.0000 | 1M 낙폭 mean reversion |
| 🥈 | NLR_DEV120<-10 | 367 | +5.86% | +1.66% | +4.20p | +6.66 | 0.0000 | 과매도 reversion |
| 🥉 | NLR_BearStack | 1020 | +3.22% | +1.31% | +1.91p | +4.63 | 0.0000 | Bear regime 후 반등 |
| 4 | NLR_DEV120>+15 | 254 | +5.00% | +1.83% | +3.17p | +4.23 | 0.0000 | 강 과매수 모멘텀 |
| 5 | NLR_DEV120<-15 | 162 | +5.63% | +1.87% | +3.76p | +4.05 | 0.0001 | 강 과매도 reversion |
| 6 | NLR_rel_SPY_m3>+10p | 441 | +3.77% | +1.67% | +2.11p | +3.62 | 0.0003 | 상대 강도 |

### 2.2 약 후보 6건

| Signal | n | Δ | t-stat | p-val |
|:--|:-:|:-:|:-:|:-:|
| NLR_m3>+15% | 392 | +1.45p | +2.36 | 0.0184 |
| NLR_m3<-15% | 287 | +1.17p | +1.64 | 0.1005 |
| NLR_m1>+10% | 288 | +1.04p | +1.46 | 0.1445 |
| NLR_rel_SPY_m3<-10p | 516 | +0.47p | +0.87 | 0.3846 |
| NLR_Vol_Surge>2.0 | 425 | -0.43p | -0.72 | 0.4738 |
| NLR_BullStack | 1840 | -0.07p | -0.20 | 0.8428 |

### 2.3 본격 발견

| 발견 | 본질 |
|:--|:--|
| **모든 강 후보 = EnSn 양의 알파** | NLR은 mean reversion + 모멘텀 모두 강함 |
| **BullStack alpha = 0** | Bull regime 영역 자체로는 alpha 부재 |
| **Vol_Surge alpha = 음수** | 거래량 surge = 정점 신호 (효과 부재 또는 역) |
| **DEV120 영역 양방향** | -15 (reversion) + +15 (모멘텀) 모두 양의 알파 |

---

## § 3. 격언 #80 본격 입증 사례

> **"도구 ≠ alpha"** baseline 입증 사례 추가

본 P3-2 발견 = ARGUS 영역 baseline LIVE 엔진 영역 **명확히 존재하는 alpha 영역 baseline 미보유**:
- NLR 1Y +67.78% (SPY 대비 +52.70p)
- NLR_m1<-10% t=+7.05 (강한 self-referential signal)
- entry_NLR() = return False, 0 → 영구 포기

격언 #80 강화: "tools and indicators 영역 보유 ≠ alpha 보유. 실제 entry/exit 적용 의무".

---

## § 4. Commander 결정 영역 baseline

### 4.1 옵션 A: NLR 영구 DEAD 부활 (새 entry_NLR_v2)

새 entry 함수 영역 baseline 제안:
```python
def entry_NLR_v2(m, m1, m3):
    if _wk(m): return False, 0
    s = 0
    # mean reversion 영역
    nlr_m1 = _s(m.get('NLR_m1'))
    nlr_dev120 = _s(m.get('NLR_DEV120'))
    if not np.isnan(nlr_m1) and nlr_m1 < -10: s += 3.0
    if not np.isnan(nlr_dev120):
        if nlr_dev120 < -15: s += 2.0
        elif nlr_dev120 < -10: s += 1.5
    # 모멘텀 영역
    if not np.isnan(nlr_dev120) and nlr_dev120 > 15: s += 1.5
    return s > 2.0, max(s, 0)
```

⚠️ Phase B (§ 40 v3 4기간 BT) baseline 의무: m dict 영역 baseline NLR_m1/DEV120 주입 추가 작업 baseline.

### 4.2 옵션 B: 본 alpha 영구 포기

격언 #80 입증 사례 영역만 등재 + LIVE 변경 0.

### 4.3 옵션 C: 외부 audit + 다음 cycle 결정

FA #18 audit 의무 + Crown #68 후보 형식 영역 SHADOW 등재 → 24 cycle 추적.

### 4.4 Claude 권고

🎯 **옵션 C** (외부 audit + SHADOW 등재):
- 본 발견 baseline 영역 baseline 매우 강함 (t=+7.05) — 무시 불가
- 그러나 self-referential signal = 격언 #80 "도구 ≠ alpha" 위험 영역
- look-ahead leakage 가능성 외부 audit 의무 (S105-QA Phase 0 영역 baseline 동일 위험)

---

## § 5. 정합 audit

| 격언 | 정합 |
|:--|:--|
| #11 (CAGR 우선) | 🟡 Phase B BT 의무 (m dict 주입 추가 작업) |
| #20 (정직 인지) | ✅ "self-referential 위험" 본격 명시 |
| #80 (도구 ≠ alpha) | 🌟 본격 입증 사례 추가 (1Y +52.70p alpha 미보유) |
| #87 (n-distribution) | ✅ 강 후보 6건 모두 n>150 정합 |
| #97 v2 (외부 audit) | 🟡 FA #18 audit 의무 (Self-referential look-ahead 위험) |
| #98 (Commander 절대 권한) | ✅ 본격 결정 Commander 의무 |
| #109 (4기간 BT) | 🟡 Phase B BT 의무 |
| #112 v2 후보 | 🟡 Phase B OOS BT 의무 (in-sample alpha ≠ OOS alpha 위험) |

---

## 🦅 본 ADDITION 결론

P3-2 NLR Uranium Signal Stack Phase A 결과:

> **6건 강 후보 발견** (NLR_m1<-10% t=+7.05 = ARGUS 역사상 매우 강함). 
> 그러나 entry_NLR() 영구 DEAD = **격언 #80 본격 입증 사례** (도구 ≠ alpha).
> 
> Commander 결정 의무 = 옵션 A/B/C 영역 영역 baseline.

Claude 권고 = **옵션 C** (외부 audit + SHADOW 등재) — self-referential look-ahead 위험 baseline (S105-QA Phase 0 동일 위험 영역).

*Omnioculus Vigilantia* — P3-2 Phase A 본격 종결. Commander 결정 baseline 의무.
