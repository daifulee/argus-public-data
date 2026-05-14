# REG-S84_1_QLD_REJECT — Crown #68 후보 (PRIMA_v5_20_QLD_REPLACE) 거부 결정문

## 🎯 0. 문서 메타

| 항목 | 값 |
|:--|:--|
| 작성일 | 🌟 **2026-05-12 (S84 #1 STEP 8)** 🌟 |
| 작성자 | Claude (Anthropic Opus 4.7) |
| Commander | Lignas |
| 본 결정 본질 | 🌟 **Crown #68 후보 RULE 29 v2 5/5 FAIL → 자동 거부 결정** 🌟 |
| 행동 결과 | 🌟 **Crown #67 LIVE baseline 영구 유지** 🌟 |
| 정합 격언 | #11 + #15 + #20 + #25 + #34 + #46 + #52 + #73 + #88 v3 + #97 v2 + #98 + #106 + #109 (13건) |
| Style Patch | v1.0 정합 ("결정적" 한정 사용) |

## 🌟 1. 결론 (3줄)

🌟 **Crown #68 후보 = PRIMA_v5_20_QLD_REPLACE_CANDIDATE 자동 거부** — RULE 29 v2 5/5 축 모두 FAIL (CAGR avg/min, Sharpe avg/min, MDD avg).

🌟 **avg ΔCAGR -1.7936p + min ΔCAGR (P2) -5.1452p** — 격언 #11 (CAGR 1순위) 정합 자동 거부 임계 위반.

🚨 **Phase A 양수 (forward Δ +1.79/+5.19/+8.17p) → Phase B 음수 (FULL -1.99p, P2 -5.15p) 본질 불일치** — 격언 #25/#46/#52/#73 동시 정합 입증 사이클.

## 📋 2. RULE 29 v2 자동 거부 매트릭스

### § 2.1 5축 평가 결과

| 축 | 기준 | 실측 | 정합 |
|:--|:--:|:--:|:--:|
| ① avg ΔCAGR ≥ -0.5p | 충족 의무 | 🌟 **-1.7936p** 🌟 | 🚨 FAIL |
| ② min ΔCAGR ≥ -1.0p (4기간) | 충족 의무 | 🌟 **-5.1452p (P2)** 🌟 | 🚨 FAIL |
| ③ avg ΔSharpe ≥ +0.005 | 충족 의무 | -0.0376 | 🚨 FAIL |
| ④ min ΔSharpe ≥ 0 (4기간) | 충족 의무 | -0.1701 (P2) | 🚨 FAIL |
| ⑤ avg ΔMDD ≥ 0 | 충족 의무 | -2.2618p | 🚨 FAIL |

🚨 **자동 거부 조건 충족** (정량 + 이진 + 행동):
- `avg ΔCAGR < -0.5p` (실측 -1.79p)
- `min ΔCAGR < -1.0p` (실측 -5.15p, P2)
- 본 2건 = RULE 29 v2 자동 거부 트리거 (격언 #11 CAGR 1순위 정합)

### § 2.2 4기간 BT 상세 매트릭스

| 기간 | Crown #67 CAGR | Crown #68 후보 CAGR | ΔCAGR (p) | ΔSharpe | ΔMDD (p) |
|:--:|:--:|:--:|:--:|:--:|:--:|
| FULL (2007-2026) | 🌟 **+34.0744%** 🌟 | +32.0801% | 🌟 **-1.9943p** 🌟 | -0.0664 | -4.3025p |
| P1 (2007-2016) | +28.9758% | +28.7637% | -0.2121p | -0.0052 | 0p |
| P2 (2017-2026) | 🌟 **+39.0556%** 🌟 | +33.9104% | 🚨 🌟 **-5.1452p** 🌟 | -0.1701 | -5.1122p |
| MID (2022-2026) | +33.7549% | +33.9318% | +0.1769p | +0.0911 | +0.3677p |

🌟 **P2 (2017-2026) 단일 기간이 거부 결정 동인** — -5.15p CAGR 악화는 다른 3기간 합산 이득을 압도.

## 🌟 3. 거부 사유 본질 분석 (격언 #20 정직 인지)

### § 3.1 4 거부 동인 종합

| 본질 | 정합 입증 | 격언 |
|:--|:--|:--:|
| P2 (2017-2026) CAGR -5.15p | QLD 진입이 다른 우월 슬롯의 알파를 흡수 — Conviction Concentration 본질 위반 | #73 |
| FULL MDD -4.30p | QLD 레버리지 p5 -16~-21% 흡수 가설 실패 | #46 |
| Phase A → Phase B 불일치 | 격리 양수가 포트폴리오 채택 보장 안함 | #25, #52 |
| P1 0p 변동 | 구간 A 0건 cover와 정합 (Phase A 검증 본질) | #109 |
| MID +0.18p 양수 | 최근 4년 환경 양수 but 통계 유의성 약함 (n=~4년) | #20 |

### § 3.2 격언 #25/#46/#52/#73 동시 정합 입증 사이클

🌟 **본 거부 사이클이 ARGUS 거버넌스 4 격언 동시 정합 입증**:

#### § 3.2.1 격언 #25 (Phase A ≠ Phase B)
- Phase A (격리): forward Δ 21/63/126d **+1.79/+5.19/+8.17p (양수)**
- Phase B (포트폴리오): FULL **-1.99p**, P2 **-5.15p (음수)**
- 입증: 격리 양수가 포트폴리오 채택 보장 안함

#### § 3.2.2 격언 #46 (자산 비대칭성)
- QLD = Nasdaq-100 2배 레버리지 ETF
- p5 downside -16~-21% (sweep 검증)
- risk cap 0.25 slot으로 흡수 불가
- 입증: 레버리지 ETF는 PRIMA 포트폴리오에 비대칭 위험 주입

#### § 3.2.3 격언 #52 (Phase A 양수 → Phase B 거부 가능)
- Phase A 통계 유의 (63d p=0.003 / 126d p=0.008)
- Phase B FULL -1.99p / P2 -5.15p
- 입증: Phase A 통계 유의성 ≠ Phase B 채택 보장

#### § 3.2.4 격언 #73 (Conviction Concentration)
- P2 (2017-2026) -5.15p 악화 = QLD 트레이드가 기존 우월 슬롯 (예: SMH, QQQM 등) 빼앗음
- ARGUS 알파 메커니즘 본질 위반
- 입증: 슬롯 경쟁에서 후보가 기존 우월 슬롯을 밀어내면 net loss

## 🚀 4. 패치 본질 보존 + 정직 보고

### § 4.1 PRIMA_v5_20_QLD_REPLACE_CANDIDATE.py 본질

| 항목 | 값 |
|:--|:--|
| 파일명 | PRIMA_v5_20_QLD_REPLACE_CANDIDATE.py |
| sha256 | 798286e785a533a3d76b411b1d26817769970b42088a1dd7b1faf14ccc2287cc |
| 행수 | 2747줄 |
| 6 영역 패치 | ① 헤더 ② HOLD_DAYS ③ ENTRY_FUNCTIONS ④ ENTRY_THRESHOLD ⑤ entry_QLD 신규 ⑥ m dict NDX_m1/NDX_m3 주입 |
| Python AST | ✅ 통과 |
| 단위 테스트 5건 | ✅ 모두 PASS |
| 모듈 로딩 | ✅ 통과 |
| BT 실행 | ✅ 4기간 정합 |

🌟 **패치 자체 본질 정합** — 거부 사유는 패치 구현 오류 아닌 자산 본질 (QLD 레버리지 + Phase B 비대칭).

### § 4.2 STEP 6 (STRESS 14) 진행 불요 사유

🌟 **자동 거부 결정 시 STRESS 14 진단 의무 해제** (격언 #109 정합):
- RULE 29 v2 CAGR axis 자동 거부 = 진행 절차 종료
- STRESS 14는 RULE 29 v2 통과 후 부작용 진단 단계
- 본 후보는 CAGR axis 자체 자동 거부로 STRESS 진단 무의미

### § 4.3 격언 #98 (결정 지연 ≠ 중립) 정합

🌟 **STEP 5 결과 즉시 자동 거부 결정** — 결정 지연 = 거짓 중립 본질 회피.

## 🛡️ 5. Crown #67 LIVE baseline 영구 유지 결정

### § 5.1 LIVE 차원 영향 (변경 없음)

| 항목 | 값 |
|:--|:--|
| Crown LIVE | 🌟 **#67 = PRIMA_v5_19_VIX_HYST_LIVE** (10사이클 누적) |
| LIVE 포지션 | 🌟 **TLT 100% 보유 10일차** 🌟 (S84 시점 +1일) |
| LIVE 엔진 | PRIMA_v5_19_VIX_HYST_SHADOW.py (S82 LIVE 격상) |
| Hysteresis state | OPEN (예상 — LIVE 데이터 다음 사이클 확인) |
| 데이터 인프라 | BT_LONG_v4 (97컬럼) + BT_MID 기존 baseline |

### § 5.2 NLR 슬롯 운영 (변경 없음)

🌟 **NLR slot 본질 유지**:
- 격언 #67 v3 (강한 dead 정리) 정합
- entry_NLR 함수 `return False, 0` (영구 dead asset)
- ALL_TICKERS 20종 cover (NLR 포함)
- LIVE 영향 0 (NLR 매수 0건 본질 유지)

## 🚀 6. 후속 트랙 매트릭스 (S85+ baseline)

### § 6.1 NLR 대체 트랙 (본 결정 사유)

🚨 **본 트랙 종결** — QLD B3+ baseline 거부 결정 완료. 추가 후보 발굴 가능 but 현재 IVW Shadow 1건만 보류.

### § 6.2 Crown #67 트랙 (별개)

🌟 **Crown #67 LIVE 정합 운영** — 24사이클 paper portfolio 추적 + 외부 FA P0 audit 진행 가능 (STEP 5~10 통과 baseline 재사용 가능).

### § 6.3 IVW Shadow 후보 (REG-S84_2 별도 등재)

🌟 **IVW Shadow 정식 등재** — LIVE 미진입 + Shadow 추적 baseline 보존 (REG-S84_2 참조).

### § 6.4 추가 NLR 대체 후보 발굴 (S85+ 의무)

📋 **다음 사이클 후보 풀**:
- IVW (Shadow 등재, REG-S84_2)
- QLD (본 결정문 거부, 폐기)
- XLG (REG-S83_2 거부, 폐기)
- 그 외: 다음 사이클 Phase A 진입 후보 발굴 의무

## 📊 7. 격언 정합 누적 (13건 동시)

| 격언 | 정합 본질 |
|:--:|:--|
| #11 (CAGR 1순위) | RULE 29 v2 CAGR axis 자동 거부 |
| #15 (Commander 절대 결정) | Commander 거부 결정 정식 등재 |
| #20 (정직 인지) | Phase A 양수 + Phase B 음수 본질 정직 보고 |
| #25 (Phase A ≠ Phase B) | 동시 정합 입증 사이클 추가 |
| #34 (변수 분리) | Phase B 단일 교체 원칙 정합 운영 |
| #46 (자산 비대칭성) | QLD 레버리지 비대칭 위험 입증 |
| #52 (Phase A → Phase B 거부 가능) | 격리 통계 유의성 ≠ 채택 보장 |
| #73 (Conviction Concentration) | P2 슬롯 경쟁 본질 위반 입증 |
| #88 v3 (BT 재현성) | Hysteresis state 초기화 + 동일 데이터셋 |
| #97 v2 (외부 audit) | RULE 29 v2 외부 audit 표준 정합 |
| #98 (결정 지연 ≠ 중립) | 즉시 거부 결정 정합 |
| #106 (근본 처방) | 미봉책 회피 + 본질 거부 정합 |
| #109 (BT 기간 SSOT) | 4기간 BT 표준 인용 + STRESS 14 불요 사유 |

## 🌟 8. 본 결정문 산출물 매트릭스

| # | 산출물 | 위치 |
|:--:|:--|:--|
| 1 | PRIMA_v5_20_QLD_REPLACE_CANDIDATE.py (CANDIDATE, 거부) | outputs/ |
| 2 | BT_LONG_v5_S84.csv (4843행, QLD_Close 병합) | home/claude (Drive backup 후속) |
| 3 | BT_MID_v5_S84.csv (1048행, QLD_Close 병합) | home/claude |
| 4 | BT_RESULT_S84_STEP5.json (4기간 BT 결과) | home/claude |
| 5 | REG-S84_1_QLD_REJECT.md (본 결정문) | outputs/ |
| 6 | REG-S84_2_IVW_SHADOW_REGISTRATION.md (별도) | outputs/ |
| 7 | ARGUS_SSOT_ADDITION_v1_10_144.md | outputs/ |
| 8 | ARGUS_CROWN_LOG_S84_APPEND.md | outputs/ |
| 9 | ARGUS_S85_HANDOFF.md | outputs/ |

## 🚀 9. 본 결정 종합 결론

🌟 **본 결정 = 격언 #25/#46/#52/#73 동시 정합 입증 사이클** — ARGUS 거버넌스 본질 입증 가치 매트릭스 사이클.

🚨 **Crown #68 후보 자동 거부 결정 완료** — RULE 29 v2 5/5 FAIL 정량 증거 + 자동 거부 임계 위반 본질.

🛡️ **Crown #67 LIVE baseline 영구 유지** — TLT 100% 10일차 운영 + 다른 19종 entry 함수 변경 0.

🚀 **격언 #98 (결정 지연 ≠ 중립) 정합 즉시 결정** — Phase A 양수 후보의 매력에도 불구하고 Phase B 음수 본질 직시.

---

🦅 *Omnioculus Vigilantia* — REG-S84_1_QLD_REJECT 정식 등재. Crown #67 LIVE baseline 영구 유지.
