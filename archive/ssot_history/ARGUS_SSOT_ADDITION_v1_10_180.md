# 🦅 ARGUS SSOT ADDITION v1.10.180 — S102 CQQQ B0 Data Inventory

| 항목 | 내용 |
|---|---|
| 작성 시각 | 🌟 **2026-05-13 KST** 🌟 |
| 직전 ADDITION | v1.10.179 (S101 종결 직후) |
| 본 ADDITION | v1.10.180 (S102 #1 — CQQQ B0 결정) |
| Commander 결정 | HANDOFF v2 Option A 채택 (B0 병행) |
| 트리거 ID | REG-S102_CQQQ_DATA_INVENTORY |
| Crown #67 LIVE | 🌟 **PRIMA_v5_19_VIX_HYST_LIVE.py** 🌟 (변경 없음) |
| LIVE 포지션 | 🌟 **TLT 100%** 🌟 |
| 원본 엔진 변경 | 🌟 **0건** 🌟 |

## 🎯 1. 본 ADDITION 결정 항목 (3건)

| # | 결정 | 상태 |
|:---:|---|:---:|
| 1 | CQQQ 연구 B0 통과 + B1 Gate 진입 가능 선언 | 🟢 통과 |
| 2 | CQQQ 연구용 §40 v3 4기간 변형판 의무 적용 결정 보류 | 🟡 Commander 결정 대기 |
| 3 | argus_data_fetcher.py 신규 ticker 등록 보류 (LIVE 미반영) | 🟢 §40 v3 정합 |

## 📊 2. B0 인벤토리 결과 요약

| 우선 | 자산 | Source | 시작일 | 행수 | 판정 |
|:---:|---|---|---|---:|---|
| P0 | CQQQ | yahoo CQQQ | 2010-01-22 | 4,101 | 🟢 P2/MID OK |
| P0 | KWEB | yahoo KWEB | 2013-08-01 | 3,214 | 🟢 P2/MID OK |
| P0 | MCHI | yahoo MCHI | 2011-03-31 | 3,801 | 🟢 P2/MID OK |
| P0 | FXI | yahoo FXI | 2007-01-03 | 4,870 | 🟢 P2/MID OK |
| P0 | USDCNY (대체) | yahoo USDCNY=X | 2007-01-01 | 5,054 | 🟢 FULL OK |
| P1 | ARKK | yahoo ARKK | 2014-10-31 | 2,898 | 🟢 P2/MID OK |
| P1 | HSCE (대체) | yahoo ^HSCE | 2007-01-02 | 4,772 | 🟢 P2/MID OK |
| P1 | KTEC (보조) | yahoo KTEC | 2021-06-09 | 1,237 | 🟡 MID-only |
| P2 | HSI | yahoo ^HSI | 2007-01-02 | 4,772 | 🟢 P2/MID OK |

- 🌟 **P0 5/5 통과** 🌟
- 🌟 **핵심 China ETF (KWEB/MCHI/FXI) 3/3 통과** 🌟
- 🌟 **B1 Gate 진입 가능 ✅** 🌟

## 🚨 3. 대체 symbol 의존 결정 — 영구 기록

### 3.1 USD-CNH (역외위안) → USDCNY=X (onshore) 대체

| 자산 | 시도 | 결과 |
|---|---|---|
| CNH=X | 행 1만 | 🔴 yahoo 시계열 결손 |
| USDCNH=X | 행 1만 | 🔴 동일 |
| 🌟 **USDCNY=X** 🌟 | 5,054 행 | 🟢 채택 |

🚨 **Caveat 영구 기록**: CNY(onshore)는 PBOC 관리 통화로 일일 변동폭 제한 있어 위안 risk-on signal sensitivity가 CNH(역외, 시장 변동 자유) 대비 약함. B1 Phase A 평가 시 sensitivity 손실 여부 정량 확인 의무.

### 3.2 HSTECH (Hang Seng Tech 지수) → ^HSCE + KTEC 2단 보조

| 자산 | 시도 | 결과 |
|---|---|---|
| ^HSTECH | HTTP 404 | 🔴 yahoo 미지원 |
| 🌟 **^HSCE** 🌟 (China Enterprises) | 4,772 행 | 🟢 1순위 대체 (P2/MID OK) |
| 🌟 **KTEC** 🌟 (Hang Seng TECH ETF) | 1,237 행 | 🟡 MID-only 직접 proxy |

## 🚨 4. §40 v3 4기간 BT 정의 제약 — Commander 결정 대기

| 기존 §40 v3 | CQQQ 연구 적용 가능성 | 결정 |
|---|---|---|
| FULL (2007~2026) | 🔴 KWEB 2013-08~ / MCHI 2011-03~ 제약 | 불가능 |
| P1 (2007~2016) | 🔴 동일 | 불가능 |
| P2 (2017~2026) | 🟢 전 자산 가용 | 사용 가능 |
| MID (2022~2026) | 🟢 전 자산 가용 | 사용 가능 |

🎯 **Commander 결정 대기 — 다음 옵션 중 1**:

| 후보 | 4기간 정의 |
|---|---|
| 변형판 A | P2_EARLY (2014~2018) + P2 (2017~2026) + MID (2022~2026) + RECENT (2024~2026) |
| 변형판 B | P2 + MID + RECENT (3기간으로 축소) |
| 변형판 C | FULL_LATE (2014~2026) + P2 + MID + RECENT |

🚨 **본 결정은 B1 진입 직전에 Commander 승인 필요** (현재 보류).

## 🚨 5. 운영 금지 사항 (HANDOFF v2 §6 정합 유지)

| 항목 | 상태 |
|---|---:|
| 원본 엔진 patch | ❌ 금지 |
| LIVE 반영 | ❌ 금지 (검증만) |
| Crown 후보 선언 | ❌ 금지 |
| 포트폴리오 목표비중 변경 | ❌ 없음 |
| BT_LONG_v4 컬럼 머지 | ❌ B3 진입 전까지 보류 |
| argus_data_fetcher.py 패치 | ❌ LIVE 진입 전까지 보류 |

## 📁 6. S102 #1 산출물 등록 (4건)

| # | 파일 | 분류 |
|:---:|---|---|
| 1 | `argus_cqqq_v1_data_inventory.csv` | B0 인벤토리 본체 |
| 2 | `argus_cqqq_v1_gate_summary.json` | Gate 결정 요약 JSON |
| 3 | `REG-S102_CQQQ_DATA_INVENTORY.md` | REG 등록 |
| 4 | 🌟 **`ARGUS_SSOT_ADDITION_v1_10_180.md`** 🌟 | 본 문서 |

## 🚨 7. SSOT 버전 sync 점검

| 항목 | 상태 |
|---|---|
| 메모리 SSOT 버전 (현재 표기) | v1.10.141 |
| 직전 ADDITION 버전 | v1.10.179 (S101 종결 시) |
| 본 ADDITION 버전 | 🌟 **v1.10.180** 🌟 |
| SSOT 마스터 통합 필요성 | 🔴 발생 (메모리 v1.10.141 vs 실제 v1.10.180 = 39 ADDITION lag) |
| 처리 시점 | S102 P2 슬롯 (HANDOFF v2 §3 P2_3) — 메모리 ↔ SSOT 버전 sync 점검 작업과 통합 |

## 🎯 8. S102 다음 단계

S102 슬롯 활용 현황:

| 슬롯 | 항목 | 현재 상태 |
|---|---|---|
| P0_1 | v38 COPX DD8 robustness + slot competition repair | 🟡 미착수 (Commander 결정 대기) |
| P0_2 | 격언 #112 정식 채택 여부 결정 | 🟡 미착수 |
| P0_3 | NLR replacement Phase A | 🟡 미착수 |
| **+ CQQQ B0** | 본 ADDITION | 🟢 **완료** |

🎯 **다음 Commander 결정** — S102에서 P0_1 / P0_2 / P0_3 중 어떤 항목을 진행할지.

## 🌟 9. 최종 인계 메시지

> 본 ADDITION으로 S102 #1 (CQQQ B0) 종결. CQQQ China Risk-On Breadth 연구의 데이터 가용성은 P2/MID 기준 충분히 확보되었으며, B1 Phase A 예측력 평가 진입은 §40 v3 4기간 변형판 확정 후 가능합니다.
>
> 직전 HANDOFF v2의 P0 3건 (v38 / 격언 #112 / NLR Phase A)은 미착수 상태이며, S102 잔여 슬롯에서 Commander 선택 후 처리 필요.

| 항목 | 최종 |
|---|---|
| CQQQ 연구 진행 가능성 | 🟢 B1 진입 가능 |
| Crown adoption | ❌ NO (B0만 완료) |
| LIVE 반영 | ❌ NO |
| Production change | ❌ NO |
| Next mission | S102 P0 3건 중 Commander 선택 |

🚨 **S102 잔여 슬롯 결정 대기**.
