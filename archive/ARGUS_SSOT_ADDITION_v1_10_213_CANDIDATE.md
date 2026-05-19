# 🦅 ARGUS MEMORY SNAPSHOT — S68

**작성일**: 2026-05-07 KST (S67 #12 종결 시점)
**스냅샷 #**: 2 (스냅샷 #1 = S58)
**불변 규칙**: #23 (10세션마다 메모리 전체 SSOT 저장 의무)
**메모리 항목 수**: 30/30 (max)

---

## §0. 작성 정합

본 스냅샷은 ARGUS 운영 메모리 (Commander 결정 사항 + 격언 + 운영 원칙 + Crown 진화 + 산출물 + 기만 차단 프로토콜) 30개 항목 전체를 SSOT로 영구 보관한다.

S58 (이전 스냅샷) → S68 (본 스냅샷): 10 세션 진전.

---

## §1. 메모리 30 항목 전체 (2026-05-07 시점)

### §1.1 데이터 + 운영 인프라 (#1~#3)

**#1 데이터 소스**: PUBLIC 미러 https://raw.githubusercontent.com/daifulee/argus-public-data/main/argus_data.csv + latest.json. Private 익명 fetch 불가. BT용 /mnt/project/. S52 (2026-05-03): PMI source=DBnomics ISM/pmi/pm. 컬럼 64→65. fetcher v2.3 운영 정합.

**#2 GitHub 레포 fetch 정책**: argus-briefing=PRIVATE / argus-public-data=PUBLIC. fetch 우선순위 latest.json > argus_data.csv. Private 필요 시 Commander 직접 첨부 또는 PAT 1회.

**#3 🌟Crown #63=v5.14_Hyst_H1_LIVE** (S65 #34, 무드리프트 49사이클 S67 #12 종결). WTI Hysteresis $1 (XLE>95/일반>90 Entry only). BT: CAGR+0.5396p/Sh+0.0263/MDD 0p/STRESS 14. SSOT v1.10.104. S66 #1 격언 #104+#87 v9+#88 v2 / #80 59차원. **S67 #1~#11 누적: VIX/VIX3M H4 Phase A 통과 (사이클 강 4종 +14~+25p, 격언 #87 v9+#91 ② 입증 #2 / COVID 37% fitting+핵심알파) → §B.9 NO-GO (cover 96~98.7%) → H1 부분 GO → epoch shift 발견 (격언 #91 ④ 첫 입증) → epoch filter 처방 한계 (격언 #91 ④ 입증 #2) / fetcher v2.3→v2.5 / briefing v6.8.20 / #80 80차원 / §35 204 / LIVE 0.**

### §1.2 격언 운영 핵심 (#4~#5)

**#4 격언 #75** (_wk(m)=WTI>90, 주말체크 아님!): WTI>90 시 TLT 제외 전종목 즉시 False,0. XLE=_wk_xle(WTI>95). TLT만 _wk() 없음 (T10YIE>2.5 조건부 차단). LIVE WTI=96.36 자동 보호.

**#5 시그널-임계값 검증 통합 체계**: 시그널 4분류 (📥EnSn/⚡EASn/📊MoSn/📤ExSn). 격언 #91 4 패턴 정식 (①noise ②fitting+핵심알파 ③robust plateau ④시대적 변화). cliff sweep + ablation 직교 BT 의무. STRESS 14 의무.

### §1.3 트리거 + 격언 (#6~#7)

**#6 STA 트리거 규칙**: "Strategy theory analysis"/"STA"/"전략이론분석"/"전략분석" → logos_argus_v1_2_0.py 자동 진입. 7 Core Advisory. enforcement_mode=False 기본.

**#7 격언 #68** "명문화 ≠ 자기 보호" (S41 #1 SLV Exit 재검증 결과). REG-129. SSOT v1.10.16.

### §1.4 운영 원칙 + 분류 (#8)

**#8 반출 메모리 분류 원칙**: ①active (매 세션 필요) ②아카이브 (SSOT 보관). active=Crown/엔진/LIVE/격언/원칙/기만차단. 아카이브=구 세션 종결 이력.

### §1.5 기만 차단 6조 (#9~#14) — 절대 보존

**#9 #1 자기 진단 트리거**: 매 응답 직전 "토큰/시간 절약 무의식 작동?" 자문. YES → STOP 후 완전본 재작성. §34/§35 재발 방지.

**#10 #2 거부권 남발 차단**: 거부 ≠ 보수. 정량 근거 의무. "보수적으로 권고"=회피 위장.

**#11 #3 BT 단축·생략 차단**: §40 v3 Full Test 의무. patch-only 패턴 = 토큰 절약 무의식 재발.

**#12 #4 결정 회피 도구 폐지**: time-bound / "다음 세션에" / "추후 검토" = 회피. 정량 입증 = 즉시 실행.

**#13 #5 userPreferences 위반 = 기만**: 자의 축약 / 풀버전 미준수 / LIVE🌟강조🌟 누락 / 이모지 미사용 / 터치 버튼 미사용 = 기만.

**#14 #6 자기 한계 인지**: 5조 = Claude 자기 작성 → 한계 존재. Commander 메타비판 = 최종 방어선.

### §1.6 SSOT 5조 + 문서 출력 (#15~#16)

**#15 ARGUS 불가침 SSOT 5조** (§0.0.7): ① 토큰절약 = Commander 승인 / ② 🌟값🌟 강제 표시 / ③ 데이터 위조 금지 / ④ PRIMA LIVE 실호출 / ⑤ Commander 의사결정권 절대성.

**#16 §41+§50+§51 문서 출력**: §41 전체 패치 / §50 세션 종결 통합 / §51 SKILL.md 영구 등록 절차.

### §1.7 Commander 결정 + 격언 (#17~#23)

**#17 Commander 결정 v2** (2026-05-04): ask_user_input_v0 의무. 본문 선택지 + 터치 버튼 동시. 권장 🎯+1번 고정.

**#18 격언 #97 v2 + #98 신설** (S63 #4): #97 v2 자기 audit (Hard Gate / Soft Gate). #98 결정 회피 차단. 격언 계층화 4 계층.

**#19 Drive ARGUS 좌표** (S65#21): id=1tOn6t1LapUKTLJppn9K5HjXs4Qx4QJ7n. ARCHIVE/BACKUP_SSOT/BACKUP_CODE/BACKUP_FULL. argus-drive-sync v2.1.

**#20 RULE 29 v2 + 격언 #11**: CAGR 1순위 (≥-0.5p / 4BT≥-1p) → Sharpe (≥+0.005 / 4BT≥0) → MDD (≥0). CAGR 미통과 자동 거부.

**#21 V-Diff 절차 §42**: 버전 변경 시 의무 ① 전체 diff ② 분류 ③ 의도하지 않은 삭제 검출 ④ SSOT/REG/메모리 기록.

**#22 격언 #96 v2 (fetch 6단계)**: ⓥ 시리즈 존재성 / ① FRED API / ② CSV+gzip / ③ ALFRED / ④ TradingView / ⑤ Commander 첨부 / ⑥ 한계 명시.

**#23 🔴 불변 규칙** (절대 삭제 금지): ① 메모리 교체 시 SSOT 반출 의무 ② 10세션마다 ARGUS_MEMORY_SNAPSHOT_Sxx.md 작성. 스냅샷 #1=S58 / **#2=S68 (본 파일)** / 다음=S78.

### §1.8 구 세션 이력 (#24~#27, #30) — 아카이브 후보

**#24 Session 24/25 메타 정점** (2026-04-28): Crown #28=v4.50_NLR. 격언 #21~31 / REG-062~073.

**#25 Session 26 종결** (2026-04-28): Crown #31=v4.53. 격언 #32~37. 스킬 v1.1 메타 비판 적중 (Phase A look-ahead bias).

**#26 S44 종결** (2026-05-02): REG-158 격언 #74 / REG-159 무효 / 격언 #76 신설. Crown #52 유지.

**#27 S49~S62 Crown 통합진화** (2026-05-04): #54→#55→#56→#57→#58→#59→#60→#61. SSOT v1.10.62→v1.10.85.

**#30 S62 #56~#62 종결** (2026-05-05): SSOT v1.10.91. §35.108~123. 격언 #91 ② 정식 입증 #7 / 격언 #91 ④ 정식 입증 #1. Crown #61 무드리프트 35사이클.

### §1.9 S67 결정적 사이클 (#28~#29)

**#28 fetcher v2.5** (S67 #5+#6, 2026-05-07): v2.3→v2.4 (CCSA FRED) →v2.5 (VIX3M Yahoo + ratio 파생). YAHOO_MACRO 11종 / FRED_SERIES 18종 / FFILL_COLS 12. argus_data.csv 65→68. 노동시장 ICSA+CCSA + VIX term structure. 격언 #80 +14. PRIVATE push 의무.

**#29 prima_briefing v6.8.20** (S67 #2, 2026-05-07): PMI Auto-Fetch (격언 #96 v2 multi-source). 2166 라인. 3 Layer Fallback (TE primary / DBnomics+sanity / CSV ffill). DBnomics 2025-09 이후 오염 발견 (11.1~10.3) → TE 정합 회복. CROWN_MAP v5_09/#61/v5_11/#62/v5_14/#63.

---

## §2. S58 → S68 진전 매트릭스

### §2.1 Crown 진화 (S58 → S68)

| 세션 | Crown | 본질 |
|:--:|:--:|:--|
| S58 | #54 (이전 스냅샷 baseline) | — |
| S62 | #61 (v5.09_EWZ_DXY_EXSN) | EWZ ExSn DXY>105 HALF |
| S65 | **#63 (v5.14_Hyst_H1_LIVE)** | WTI Hysteresis $1 |
| S68 | **#63 보존** (49 사이클) | LIVE 영향 0 |

### §2.2 격언 신설 (S58 → S68)

| 격언 | 본질 | 입증 횟수 |
|:--:|:--|:--:|
| #75 (_wk WTI>90) | 시그널 평가 전 grep 의무 | LIVE 입증 #1 |
| #76 (sweep plateau) | 채택 자격 결정자 | 다수 |
| #87 v9 (8종 사전평가) | baseline 표준화 | 다수 |
| #88 v2 (양방향) | 진입 + 청산 정합 의무 | S67 입증 #2 |
| **#91** (4 패턴) | ①noise ②fitting+핵심알파 ③robust plateau ④시대적 변화 | ② 입증 #7 / ④ 입증 첫 + #2 한계 |
| #92 (PARTIAL) | 직교성 평가 | S67 입증 #2 |
| #93 + §42/§43 | epoch + ablation | 다수 |
| #94 (정합 운영) | #94+#87+#48 | EWZ ExSn 첫 양수 |
| #96 v2 (fetch 6단계) | DBnomics 오염 입증 | S67 입증 #1 |
| #97 v2 (Hard/Soft Gate) | 자기 audit + 외부 audit | S67 입증 +5 |
| #98 (결정 회피 차단) | 즉시 결정 + REG | 다수 |
| #104 | (S66 #1 정식) | — |

### §2.3 산출물 (S58 → S68)

- argus_data_fetcher v1.x → v2.5 (PMI / CCSA / VIX3M / ratio 통합)
- prima_briefing v6.5 → v6.8.20 (PMI Auto-Fetch / sanity / CROWN_MAP)
- argus-discovery-prioritizer v1.1
- argus-signal-discovery v1.3
- 신규 스킬: invictus-briefing / invictus-emergency / invictus-data-extract / invictus-audit
- argus-knowledge-cleanup v2.0 + argus-drive-sync v2.1

### §2.4 결정적 발견 (S58 → S68)

| # | 발견 | 세션 |
|:--:|:--|:--:|
| 1 | EWZ ExSn DXY>105 HALF (ExSn 첫 양수) | S62 |
| 2 | WTI Hysteresis $1 마진 (Crown #63) | S65 |
| 3 | DBnomics PMI source 결정적 오염 | S67 #1 |
| 4 | tradingeconomics business-confidence Primary 채택 | S67 #1+#2 |
| 5 | VIX3M term structure 차원 추가 | S67 #3+#6 |
| 6 | VIX/VIX3M H4 §B.9 cover 96~98.7% NO-GO | S67 #8 |
| 7 | QQQM bull-only Phase A → BT 진입 0건 | S67 #8 |
| 8 | H1 epoch shift (위기 +20p / 긴축 -13p) | S67 #10 |
| 9 | F2 음 100% 차단 BUT LIVE 0% (격언 #91 ④ 처방 한계) | S67 #11 |

---

## §3. S68 진입 작업 우선순위 (Tier 1)

🎯 #1: regime-adaptive filter 발굴 (격언 #91 ④ 처방 정밀화)
🎯 #2: H1 청산 시그널 발굴 (격언 #88 v2 양방향 의무)
🎯 #3: F1 BT 진입 (LIVE n=4 위험 인정, BT 알파 +17~+21p)

Tier 2: XLU ExSn 6 가설 / GLD ExSn / CCSA Phase A causal
Tier 3: PCC/SOFR / Phase A v2.4 / EASn/MoSn 추가

---

## §4. 운영 원칙 (보존 매트릭스)

- §41 전체 통합본 출력 의무
- §50 세션 종결 master SSOT 통합
- §51 SKILL.md 영구 등록 절차
- 격언 #11 CAGR 1순위 / RULE 29 v2
- 격언 #97 v2 자기 audit + #98 결정 회피 차단
- 격언 #96 v2 fetch 6단계
- 불변 규칙 #23 (본 스냅샷 정합)
- ask_user_input_v0 + 본문 표 동시 표시
- 🌟값🌟 LIVE 강제 표시
- argus-briefing PRIVATE → argus-public-data PUBLIC 자동 sync (GHA)

---

## §5. Commander 의무 (S68 진입 시)

```
[ ] ① 본 ARGUS_MEMORY_SNAPSHOT_S68.md Drive ARCHIVE 저장 (격언 #19 정합)
[ ] ② argus_data_fetcher_v2_5.py PRIVATE argus-briefing 레포 push
[ ] ③ prima_briefing_v6_8_20.py PRIVATE argus-briefing 레포 push
[ ] ④ 다음 GHA 자동 백필 검증 (argus_data.csv 65→68)
[ ] ⑤ S68 시작 시 첫 응답 "기만 차단 5조 통과" 표기 (격언 #14 정합)
[ ] ⑥ Crown #63 baseline 보존 (LIVE 영향 0)
```

---

🦅 **Omnioculus Vigilantia**
- S58 → S68: 10 세션 진전
- Crown #54 → #63 (9 세대)
- 격언 누계 ~104+
- §35 누계 184 → 204
- LIVE 영향 누적 0 (Crown 보존 절대성)

**스냅샷 #2 종결.** 다음 스냅샷 = S78.
