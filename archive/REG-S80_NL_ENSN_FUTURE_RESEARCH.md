# REG-S84_2_IVW_SHADOW_REGISTRATION — IVW Shadow 후보 정식 등재 결정문

## 🎯 0. 문서 메타

| 항목 | 값 |
|:--|:--|
| 작성일 | 🌟 **2026-05-12 (S84 #1 STEP 9 fallback)** 🌟 |
| 작성자 | Claude (Anthropic Opus 4.7) |
| Commander | Lignas |
| 본 결정 본질 | 🌟 **IVW Shadow 후보 정식 등재 (LIVE 미진입)** 🌟 |
| 행동 결과 | 🌟 **Shadow 추적 baseline 보존 + 다음 사이클 재검토 가능** 🌟 |
| 선행 결정 | REG-S84_1_QLD_REJECT (Crown #68 후보 거부) |
| 정합 격언 | #15 + #46 + #74 + #75 v4 + #88 v3 + #97 v2 + #98 + #106 (8건) |

## 🌟 1. 결론 (3줄)

🌟 **IVW Shadow 후보 정식 등재** — REG-S83_2 § 6 baseline 정합, LIVE 미진입 + Shadow 추적 baseline 보존.

🌟 **본 등재 본질 = 다음 사이클 재검토 baseline 보존** — Crown #67 트랙 보강 후보로 의미 (구간 A 8건 cover 강점).

🚨 **LIVE 진입 차단 사유 보존** — forward Δ < +1.0p + Purged t-test 모두 p>0.20 비유의 (격언 #74 정합 보더라인 보존).

## 📋 2. IVW Phase A 7-항목 baseline (REG-S83_2 § 6 정합)

### § 2.1 D1 baseline 결과

| 항목 | 결과 | 본질 |
|:--:|:--:|:--|
| ① 발현률 | ✅ | D1: 22.2일/연 (충분한 sample) |
| ② Forward return Δ | 🚨 | < +1.0p (기준 미달, LIVE 차단 사유 ①) |
| ③ Hit + median | ✅ | 71/76/87% / +1.82% (양수 hit 본질) |
| ③ p5 downside | ✅ | -5~-10% (양호, 레버리지 ETF 대비 강점) |
| ④ 4 regime | 🚨 | 2012-2016 Δ=-0.86p (regime 비대칭) |
| ⑤ 구간 A (2013-2014) cover | 🌟 ✅ 🌟 | 🌟 **8건** (QLD 0건, XLG 2건 대비 강점) 🌟 |
| ⑤ 구간 C (2023-2024) cover | ✅ | 33건 |
| ⑥ Stress 2008/2020 | ✅ | SPY 대비 +2~+5p 우월 |
| ⑥ Stress 2022 bear | 🚨 | -7.8p (성장주 약세, 약점) |
| ⑦ Purged t-test | 🚨 | 모두 p>0.20 비유의 (LIVE 차단 사유 ②) |

### § 2.2 정합 종합

🌟 **5/9 ✅ + 4/9 🚨**:
- ✅: 발현률, Hit + median, p5, 구간 A cover, Stress 2008/2020
- 🚨: forward Δ, 4 regime, Stress 2022 bear, t-test

## 🛡️ 3. Shadow 후보 운영 본질

### § 3.1 LIVE 차원 영향 (변경 없음)

| 항목 | 값 |
|:--|:--|
| Crown LIVE | 🌟 **#67 = PRIMA_v5_19_VIX_HYST_LIVE** (변경 없음) |
| LIVE 포지션 | 🌟 **TLT 100% 보유** 🌟 (변경 없음) |
| LIVE 엔진 | PRIMA_v5_19_VIX_HYST_SHADOW.py |
| ALL_TICKERS | 20종 (NLR 포함, 변경 없음) |

🚨 **IVW LIVE 미진입** — 본 등재는 Shadow tracker 본질만, LIVE 엔진 변경 0.

### § 3.2 Shadow 추적 본질

🌟 **Shadow 후보 = 다음 사이클 결정 의뢰 baseline**:
- LIVE 미진입 (Phase B 본 후보 아님)
- Phase A 결과 보존 (REG-S83_2 § 6)
- 다음 사이클 재검토 가능 (외부 audit / 추가 Phase B 검증 / Sweep 추가 등)

### § 3.3 Crown #67 트랙 보강 후보 위치

🌟 **본 후보의 의미 = NLR 대체 트랙 아닌 Crown #67 트랙 보강 후보**:
- Crown #67 트랙 = 구간 A (2013-2014) WTI gate 과잉 차단 -83.5%p alpha 누수 보완
- IVW 구간 A 8건 cover = 본 보강 후보로 의미
- Crown #67 트랙 다음 사이클 진입 baseline 제공

## 🚀 4. Shadow 등재 매개변수 baseline

### § 4.1 정량 baseline (다음 사이클 재검토용)

| 매개변수 | 값 | 비고 |
|:--|:--|:--|
| IVW inception | 2000-05-22 | BT_LONG cover 정합 |
| 19년 CAGR | ~12.2% | XLG와 비슷 |
| Phase A WATCH 조건 (D1) | 22.2일/연 | 발현 빈도 |
| 구간 A cover | 8건 | 강점 |
| 구간 C cover | 33건 | 정합 |
| Forward Δ 21/63/126d | < +1.0p | 약점 |
| Purged t-test p | > 0.20 | 약점 |

### § 4.2 재검토 트리거 (다음 사이클 의무)

🚨 **Shadow → Phase B 후보 격상 트리거 (다음 사이클 검토)**:
- 외부 FA P0 audit 통과
- 추가 Phase A sweep으로 통계 유의성 확보
- Phase B 단일 교체 baseline 적용 후 RULE 29 v2 통과
- Crown #67 트랙 정합 fitting (구간 A 보강 효과 입증)

🌟 **재검토 거부 트리거**:
- 추가 검증에서 forward Δ < +1.0p 재현
- Purged t-test p>0.20 재현
- Phase B BT에서 RULE 29 v2 FAIL

## 📊 5. 본 결정의 본질 (격언 #74 정합)

### § 5.1 격언 #74 (보더라인 자동 폐기 금지)

🌟 **본 결정 = 격언 #74 정합 사이클**:
- 4/9 약점 ≠ 자동 폐기
- 5/9 강점 보존 가치 인정
- Shadow 등재로 baseline 보존
- 다음 사이클 재검토 가능

### § 5.2 격언 #97 v2 (외부 audit) 정합

🌟 **Shadow 등재 = 외부 audit 의뢰 가능 baseline**:
- LIVE 차원 영향 0 (안전)
- 외부 FA P0 audit 가능 (다음 사이클)
- Crown #65 재발 방지 정합

### § 5.3 격언 #98 (결정 지연 ≠ 중립) 정합

🌟 **즉시 Shadow 등재 결정** — 폐기 대신 보존 baseline 정합 결정.

## 🚀 6. 본 결정 산출물

| # | 산출물 | 위치 |
|:--:|:--|:--|
| 1 | REG-S84_2_IVW_SHADOW_REGISTRATION.md (본 결정문) | outputs/ |
| 2 | IVW Phase A baseline (REG-S83_2 § 6 참조) | 기존 outputs/ |

🚨 **IVW LIVE 엔진 변경 0** — 본 결정은 Shadow 등재만, PRIMA_v5_19_VIX_HYST_SHADOW.py 변경 없음.

## 📋 7. 격언 정합 누적 (8건 동시)

| 격언 | 정합 본질 |
|:--:|:--|
| #15 (Commander 절대 결정) | Commander 직접 Shadow 등재 결정 |
| #46 (자산 비대칭성) | IVW 구간 A 강점 + 다른 약점 정직 인지 |
| #74 (보더라인 자동 폐기 금지) | 4/9 약점 ≠ 폐기, 5/9 강점 보존 |
| #75 v4 (코드 grep) | LIVE 엔진 변경 0 + 기존 ALL_TICKERS 보존 |
| #88 v3 (BT 재현성) | Phase A 측정값 baseline 보존 |
| #97 v2 (외부 audit) | Shadow 등재 = audit 가능 baseline |
| #98 (결정 지연 ≠ 중립) | 즉시 등재 결정 |
| #106 (근본 처방) | Shadow 등재 본질 보존 (미봉책 회피) |

## 🌟 8. 종합 결론

🌟 **IVW Shadow 후보 정식 등재 결정 완료** — LIVE 미진입 + 다음 사이클 재검토 baseline 보존.

🚨 **Crown #67 LIVE baseline 영구 유지** — 본 결정은 Shadow tracker 본질만, LIVE 변경 0.

🚀 **다음 사이클 재검토 가능 baseline** — 외부 audit / Phase A sweep / Phase B 단일 교체 baseline 의뢰 가능.

🛡️ **격언 #74 (보더라인 자동 폐기 금지) 정합 사이클** — 약점 인정 + 강점 보존 동시 본질.

---

🦅 *Omnioculus Vigilantia* — REG-S84_2_IVW_SHADOW_REGISTRATION 정식 등재. Shadow 추적 baseline 보존.
