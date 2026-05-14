# 🦅 ARGUS SSOT ADDITION v1.10.185 — S103 #3 v38 candidate engine NO-GO

| 항목 | 내용 |
|---|---|
| 작성 시각 | 🌟 **2026-05-14 KST** 🌟 |
| 직전 ADDITION | v1.10.184 (S103 #2 보강) |
| 본 ADDITION | v1.10.185 (S103 #3 — v38 candidate engine 설계 + BT) |
| Commander 결정 | 🎯 P0_B v38 candidate engine 진입 (5축 baseline) |
| Crown #67 LIVE | 🌟 **PRIMA_v5_19_VIX_HYST_LIVE_v4.py** 🌟 (변경 없음) |
| LIVE 포지션 | 🌟 **TLT 100%** 🌟 |
| 원본 엔진 변경 | 🌟 **0건** 🌟 |
| LIVE 반영 | 🌟 **0건** 🌟 |
| 산출 candidate | v38, v38_v2, v38_v3 (3개 시도, 모두 NO-GO) |
| 최종 판정 | 🔴 **v38_v3 NO-GO (STRESS 14 breach 1건)** |

## 🎯 1. 본 ADDITION 결정 항목 (5건)

| # | 결정 | 상태 |
|:---:|---|:---:|
| 1 | v38 candidate engine 5축 설계 통합 시도 | 🟢 완료 |
| 2 | v38 v1 (combined band) — DEV120 분포 부정합 dead code | 🔴 dead |
| 3 | v38_v2 (DEV120 band [25,35] + DD20 band [-12,-8]) — comb>0.5 0건 | 🔴 dead |
| 4 | v38_v3 (DEV120≥30 AND DD20≤-8 점 임계값) — 4기간 통과 + STRESS 1 breach | 🔴 NO-GO |
| 5 | v37 NO-GO 사유 4건 vs v38_v3 비교 정량 입증 | 🟢 완료 |

## 📊 2. v38 3 시도 비교

### 2.1 v38 v1 (combined band soft trigger DEV200=50 / DD20=-8)
- DEV120 분포 (max 52.5)에 50 임계값 적용 → comb>0.5 = 0건 (dead code)
- 본질적 오류: m dict의 컬럼명 COPX_DEV120 (실제 120일 windowing) 에 DEV200 임계값 적용

### 2.2 v38_v2 (band [25,35] × band [-12,-8] DEV120 분포 정합)
- 양 변수 곱 logic = 동시 강함 요구 → 0/4014 발동 (dead code)
- 결정적 발견: COPX 광산주 특성상 DEV120 high + DD20 low time-shifted, 동시 발생 희소

### 2.3 v38_v3 (점 임계값 DEV120≥30 AND DD20≤-8)
- v37 정합 점 임계값 + AND-logic
- 발동 7건 (2021 2 + 2026 5)
- 4기간 BT: ✅ CAGR/Sharpe/MDD(4기간) ALL PASS
- STRESS 14: 🔴 CRASH10D_REBOUND20D MDD -1.67p breach + ΔCAGR -3.65p

## 🚨 3. v38_v3 vs v37 NO-GO 사유 정량 비교

| 사유 | v37 | v38_v3 | 정합 |
|---|---|---|:---:|
| ① 격언 #91 ② Cliff | (47.5,-7) -1.556p / (45,-7) -5.963p | P2 +0.383p (cliff 해소) | ✅ 해소 |
| ② 격언 #52 Slot Cascade | CRASH10D -0.79p / equity -0.46% | CRASH10D -3.65p / MDD -1.67p | 🔴 악화 |
| ③ 격언 #88 ExSn Asymmetry | cooldown override 부재 | cooldown 자체 미구현 | ⚪ 무관 |
| ④ n=4 Small Sample | P2 4 HALF | trigger 7건 (n=7) | 🟡 동일 |

🚨 **결정적 결론**: v38_v3 는 v37의 **격언 #91 ② cliff은 해소** 했으나, **격언 #52 slot cascade는 악화**. 본질적으로 v37 4사유 중 ②번이 v38 5축 설계로 해소 불가능 한계 노출.

## 🚨 4. 격언 누적 강화

### 4.1 격언 #52 Slot Cascade — 결정적 의무 입증 강화

> v38_v3 4기간 BT 정상 통과 (avg ΔCAGR +0.137p / Sharpe +0.009) 에도 STRESS CRASH10D 단일 시나리오에서 -3.65p / MDD -1.67p breach → **§40 v3 4기간 BT + STRESS 14 동시 검증 의무 결정적**.

### 4.2 격언 #91 ② cliff 해소 정량 입증

> v37 (47.5, -7) cliff -1.556p / (45, -7) -5.963p → v38_v3 점 임계값 변경 (DEV200>50 → DEV120≥30) 으로 P2 +0.383p 양수 알파 = cliff 메커니즘 해소 입증.

### 4.3 격언 #80 양방향 결정자 — 추가 정합

> v38_v3 4기간 BT 강력 PASS → STRESS 14 단일 breach. Phase A 직교 알파 → BT alpha 패턴과 정합. **§40 v3 통합 (4기간 + STRESS 14) 만이 진정한 채택 자격**.

### 4.4 격언 #112 후보 — Cooldown-as-Cliff-Driver

> v38_v3 는 cooldown 메커니즘 미구현 → cliff 해소 + 양수 알파 입증 → cooldown 자체가 cliff driver였음 입증 일부 정합.
> v38_v3는 cooldown 없이도 STRESS breach 발생 → cooldown만이 유일한 cliff driver는 아님.
> → 격언 #112 **부분 정합**, 추가 검증 필요.

## 🚨 5. 운영 금지 사항 100% 보존

| 항목 | 상태 |
|---|:---:|
| 원본 엔진 patch | ❌ 0건 |
| Crown #67 LIVE 변경 | ❌ 없음 |
| LIVE 반영 | ❌ 없음 |
| Crown 후보 선언 | ❌ 없음 (v38_v3 NO-GO) |
| 포트폴리오 변경 | ❌ 없음 |
| BT_LONG_v4 컬럼 머지 | ❌ 보류 |

## 📁 6. 본 ADDITION 산출물 (8건)

| # | 파일 |
|:---:|---|
| 1 | `PRIMA_v5_21_v38_CANDIDATE.py` (v1 dead code) |
| 2 | `PRIMA_v5_21_v38v2_CANDIDATE.py` (v2 dead code) |
| 3 | `PRIMA_v5_21_v38v3_CANDIDATE.py` (v3 NO-GO) |
| 4 | `v38v3_4period_BT.json` (4기간 BT 결과) |
| 5 | `v38v3_stress_14.json` (STRESS 14 결과) |
| 6 | `v38v3_final_summary.json` (종합) |
| 7 | `REG-S103_3_V38_NOGO.md` (REG 등록) |
| 8 | 🌟 **본 ADDITION** 🌟 `ARGUS_SSOT_ADDITION_v1_10_185.md` |

## 🎯 7. S103 #4 다음 단계 권고

| 우선 | 항목 | 권고 |
|:---:|---|---|
| 🚨 P0_A | 격언 #112 정식 채택 결정 | 🎯 부분 정합 인지 후 정식 채택 결정 (~30m) |
| 🟡 P1 | v38_v4 설계 — cooldown 추가 + slot cascade 해소 | (S104+) |
| 🟡 P1 | BT_LONG_v5 데이터 브리지 (China direct breadth) | (S104+) |
| 🟢 P2 | S103 종결 + S104 HANDOFF | (선택 가능) |

## 🌟 8. 최종 인계 메시지

> S103 #3 = v38 candidate engine 3 시도 결과:
> - v38 v1, v2 dead code (DEV120 분포 부정합)
> - v38_v3 점 임계값 정합 + 4기간 통과 + STRESS 1 breach = NO-GO
> - **격언 #91 ② cliff 해소 + 격언 #52 slot cascade 미해소** 양면 결과
> - 격언 #112 부분 정합 입증 + Crown #67 LIVE 변경 0 / 포트폴리오 0 / 원본 patch 0
>
> v38_v3 가 4기간 BT 정상 통과로 1차 후보 자격 확보했으나 STRESS 14 breach 1건으로 NO-GO. 격언 #80 + §40 v3 통합 검증 의무 결정적 강화.

| 항목 | 최종 |
|---|---|
| Production adoption | ❌ NO |
| Crown promotion | ❌ NO |
| LIVE 반영 | ❌ NO |
| Research continuation | ✅ YES (v38_v4 cooldown 통합 / 격언 #112 정식 채택 결정 / BT_LONG_v5) |
| Next mission | S103 #4 → P0_A 격언 #112 정식 채택 또는 S103 종결 |

🚨 **S103 #4 진입 시 본 ADDITION + SSOT v1.10.184 + HANDOFF v3 정합 진행**.
