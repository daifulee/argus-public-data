#!/usr/bin/env python3
# ======================================================================
# argus_brief_html_v2.py - ARGUS Brief HTML 생성기
# VERSION : v9.2.72-DISPLAY_CONSISTENCY
# CHANGE  : 명시 신규 엔진, 날짜축 정규화, 최신 판단 목표와 모의보유 분리.
#           필수 입력·엔진 날짜·계좌 근거로 행동 허용을 판정하고 원장은 전일 비교만 담당.
#           입력 열 합집합, 같은 날 위험 재진입 차단, 연속 보유와 전략 만기 시계 분리.
# CHANGE  : v9.2.70 [LEDGERCOVER] 🔴 결함 S291-12 — 원장 배지가 머리 행 하나만 보고 누적 결손을 못 봤다. 실측(2026-09-21): as_of 2026-09-18 · 기준일 2026-09-18 → ledger_missing_bdays 가 gap 0 → missing 0 을 내고 배지는 🟢 '일일 기록' 이었으나, 원장 개시 2026-08-13~09-18 26세션 중 기록은 17세션(65.4%) 이고 gap_note 는 6건 누적이었다. 결손 9세션(08-14·08-17·08-18·08-19·08-28·09-08·09-11·09-15·09-17) 이 한 번도 화면에 나온 적이 없다. 소급 기록은 DIR-S289_2 P6 로 금지되므로 복구 경로가 없고, 따라서 '보이게 하는 것'이 유일한 방어다. 처방: load_position_ledger_meta 가 history 의 as_of 집합과 gap_note 를 함께 싣고, ledger_coverage() 가 XNYS 세션 달력으로 구간 충족률을 잰다. 배지는 머리 지연과 누적 결손을 둘 다 판정에 넣어 '머리 행 최신이나 누적 결손 N세션' 상태를 구분해 적는다. 달력 조회 실패 시 판정하지 않고 사유를 남긴다(위조 금지). 자본·신호 무접촉 · 표시 전용.
# CHANGE  : v9.2.65 [FEATBASE] 🔴 S291 결함 S291-6 처방 — LIVE 가 Crown #106·#108 을 죽인 채 돌고 있었다.
#   실측(2026-09-21, 엔진 v0.5.44 evaluate_all, 결합 최종 2026-09-18):
#     현행 LIVE(v6_PDBCTRUNC 결합 56열) KIL_SUP=None · GPR_HIGH=None · sizing_mult('EWZ')=1.000
#     v6_FEAT 결합(58열)               KIL_SUP=1.0  · GPR_HIGH=1.0  · sizing_mult('EWZ')=0.300
#   기전 2겹: ① BT_LONG_NAME 이 FEAT 미포함 판본을 가리킨다 ② `common = set(bt) & set(ad_new)` 교집합이
#     argus_data 전용 열을 통째로 버린다 — BT 구간에 없으면 **최근 구간의 값까지 사라진다**.
#     GPR_HIGH 가 1 인 국면인데 EWZ 사이징 배수가 1.0 으로 나가고 있었다.
#   선행 기록: REG-S290_12 §2 · REG-S290_13 §4·§9 · REG-S290_15 §4·§5 가 BT·STRESS 쪽 결손을
#     이미 규명했다. 다만 §9 미결 #7 의 전환 대상 목록이 xlu_dsk_bt_harness·argus-backtest 스킬만
#     적었고 **본 브리핑이 빠져 있었다.** 그 누락의 정정이다.
#   처방 2건:
#     ① BT_LONG_NAME → BT_LONG_v6_PDBCTRUNC_FEAT.csv (입력 판본 교체, 1행)
#     ② 결합 직후 KIL_SUP·GPR_HIGH 도달 여부를 검사해 미도달이면 ::error:: 로 승격.
#        v9.2.54 가 '무성 강등 차단' 을 행수에만 걸었던 것을 **열 수준으로 확장**한다.
#        조용히 규칙이 죽는 경로를 구조적으로 막는다 — 저장·빌드는 막지 않는다.
#   🔴 자본 영향: EWZ 배수 1.0 → 0.3 은 **표시가 아니라 자본**이다. 오늘은 EWZ 미보유·점수 미달로
#      실효 0 이나, EWZ 진입 시점부터 비중이 3.33배 달라진다. §40v3 재검정 대상 여부는 Commander 판단.
#   ⚠️ 미조사: REG-S288_31(S288) 은 당시 LIVE 결합에서 sizing_mult('EWZ')=0.3 발동을 확인했다.
#      그때 교집합을 어떻게 통과했는지는 **조사하지 않았다**. v9.2.54 이전 판본이 있어야 확인된다.
# CHANGE  : 상세 설명 확장·21종 수치 조건 및 해석 한계 보완.
# CHANGE  : 21종 진입 설명 재검토; 현재 자격은 entry_ok 사용; 통계·인과 단정 제거.
# DATE    : 2026-09-17
# CHANGE  : 원장 결손 시 최신 입력의 엔진 재실행 목표를 보존. 전일 비교·주문과 목표 표시를 분리.
#           정본 일치는 최신성 보증과 구분. 원장 결손은 거래소 달력으로 검사하며 근사 폴백 금지.
# CHANGE  : v9.2.57 [UNIFIED] 🔴 S290 ACTIONGATE + BROKERALIGN 단일화.
#           폐기된 ACTIONGATE/BROKERALIGN 포크의 기능을 하나로 병합한다.
#           (1) PREFLIGHT 자산 점검 + 동일 버전 접미사 분기 네임스페이스 가드,
#           (2) ACTION_READY = DATA_FRESH ∧ HOLDINGS_GROUNDED ∧ ENGINE_VALID 하드 게이트,
#           (3) Engine State와 Broker Alignment 분리 유지,
#           (4) ACTION_READY=False이면 Broker Alignment의 SELL/BUY 방향 전체 비노출,
#           (5) Phantom Portfolio 검출은 게이트가 닫힌 상태의 종목집합 불일치에만 경고,
#           (6) brokerage의 '정확 주문 산출 가능' 의미는 orders_computable로 분리.
#           DATA_FRESH는 exchange_calendars:XNYS의 실제 완료 세션을 사용하며 근사 폴백 금지.
#           HOLDINGS_GROUNDED는 real_holdings/1.x의 실제 shares·statement가 검증된 상태를 뜻하며
#           cash.amount/entry_date는 별도 미확정값으로 취급한다. 실제 금액은 Commander 관리.
#           엔진·시그널·threshold·자본 로직 무접촉.
# CHANGE  : RETIRED [BROKERALIGN] 🔴 S290_14 표시 SSOT 분리. S290_10 REALHOLDINGS_SPLIT 이후 Discord는
#           argus_real_holdings.json(브로커 실제 주수) → 엔진 목표를 표시하지만 HTML Action Board는 여전히
#           엔진 원장 전일→당일 변화만 '결론/의무매도'로 표시해, 실보유 SLV·ITA 청산 + XLE·TLT 신규매수가
#           필요한 날에도 '유지 / 0건'으로 보이는 의미 충돌이 발생했다. 처방: (1) Action Board를 Engine State로
#           명시 분리, 엔진 상태/엔진 청산/엔진 현금으로 라벨 교정. (2) Broker Alignment 독립 카드 신설 —
#           transition 모듈의 brokerage_transition/1.1만 소비해 실보유 주수→엔진 목표 정렬 방향을 표시.
#           (3) main에서 argus_real_holdings.json을 transition 모듈의 load_real_holdings()로 검증 로드하고
#           compute_transition(..., real_holdings=...)에 전달. (4) cash.amount=null은 오류가 아니라 Commander
#           금액관리 정책으로 처리해 매수 금액·주수 계산만 잠금. (5) '실계좌 변경 없음' 오표현 제거 —
#           전일 대비 카드는 엔진 동결 원장→당일 목표 변화로 한정. legacy real_account.json 드리프트는
#           brokerage SSOT가 연결되면 억제. 엔진·시그널·threshold·자본 로직 무접촉.
# CHANGE  : v9.2.54 [BTV6] 🔴 BT 판본 v5 → v6 전면 교체 (Commander 지시 S289). 결함: LIVE 경로가 BT_LONG_v5_complete.csv(말미 2026-04-02)를 쓰는데 §40v3 백테스트는 BT_LONG_v6_PDBCTRUNC.csv(말미 2026-06-15)를 써 왔다 — 같은 엔진이 LIVE 와 BT 에서 서로 다른 입력을 보는 구조. fetch_live_data 의 결합 규칙(ad_new = ad[Date > bt_last])상 v5 를 쓰면 2026-04-03~06-15 구간을 argus_data 가 채우고, v6 를 쓰면 BT_LONG 이 채운다. 실측(Crown #110 동일 엔진·동일 날짜 2026-08-20): v5 결합 4,942행 → GLD 70.0/ITA 27.5/SMH 1.6/NLR 0.9 vs v6 결합 4,940행 → XLU 70.0/GLD 23.95/ITA 6.04. 재현값 최대 괴리 70%p 의 실제 원인이며, 행수 차이(420 대 4,942)가 아니다 — 420행 단독과 v5 결합은 완전히 같은 답을 낸다. 부수 근거: 가격 무결성 가드가 v5 말미 QQQM 2026-03-25~04-02 7행 ×2.432 부풀림(조정 기준 불일치)을 이미 기록하고 있다 — 교체는 그 오염 구간의 회피이기도 하다. 처방: BT_LONG 상수·회수 대상을 BT_LONG_v6_PDBCTRUNC.csv 로 교체. 엔진 규칙 무변경이므로 §40v3 재검정 대상이 아니다 — 오히려 LIVE 를 이미 v6 기준인 BT 와 정합시키는 교정이다. 무성 강등 차단: 결합 실패 시 argus_data 단독 폴백은 유지하되 ::error:: 로 승격(워크플로 4,000행 하한 검증이 배포를 차단한다). 표시·자본 로직 무접촉 — 입력 원천만 교체.
# CHANGE  : v9.2.53 [LEDGERDAILY] 🔴 원장 배지가 스키마 v2.0 을 판정하지 못하던 결함 2건 처방. (1) 임계 오정합 — 배지는 v9.2.35 시절 '정기 대사 장부' 전제로 5영업일 초과에만 경고했다. 스키마 v2.0 의 원장은 R1(각 행은 그날 산출)·R3(전이 지시 = 직전 영업일 행 → 당일 산출)에 따라 매 영업일 기록되어야 하므로 1영업일만 건너뛰어도 이미 결손이다. 실측(2026-08-19 기준): as_of 08-13 → 격차 4영업일인데 5 이하라 ✅ 초록 표시 — 6영업일 누적 차이가 전이 지시로 매일 재방출되는 동안 배지는 정상을 알렸다. 처방: 판정 축을 '지연'에서 '기록 결손 영업일수'로 교체 (missing = gap-1 · 0 정상 / 1~2 주의 / 3+ 경고). (2) 필드 오참조 — 배지가 v1.0 의 last_reconciled 를 읽는데 v2.0 에는 그 키가 없어 빈 문자열이 조용히 출력됐다('reconcile  ✅'). 처방: schema_version·recorded_at·crown 을 v2.0 1순위로 읽고 last_reconciled 는 구 스키마 폴백으로만 유지, 부재 시 '?' 명시(위조 금지 원칙 유지). 표시 전용 · 엔진·시그널·threshold·자본 무접촉 · 원장 파일 무수정.
# CHANGE  : v9.2.52 [ENGREC] 🔴 원장 재정의 반영 (Commander 지시 S288). 원장은 브로커리지 실보유 장부가 아니라 당일 엔진 산출을 동결한 기록이며, 목적은 백필 차단이다. v9.2.49~51 은 이를 '실보유'로 라벨링해 오독을 유발했다. 처방: '보유(원장)' → '전일 산출(원장)' · 전이 지시 부제 '원장 실보유 → 목표' → '전일 산출 → 당일 산출' · 재량 이탈 표기 제거(원장 대상 아님) · 격상일 규칙 변경분 표기 신설.
# CHANGE  : v9.2.51 [DEVFLAG] 전이 지시에 미해소 재량 이탈 표기 추가. Discord v1.2 에는 실리는데 HTML 에는 없어, Commander 가 의도적으로 초과 보유한 종목의 되돌림 지시가 매일 무조건적 지시로 읽혔다. 실측: SLV 20%(엔진 목표 7.4% 대비 2.7배, DEV-S288-1 OPEN)에 대해 -13.2%p 부분매도가 전이 지시 최대 항목. 지시 자체는 정확하나 그 종목이 Commander 결정에 종속됨을 함께 보여야 한다.
# CHANGE  : v9.2.50 [HOLDLABEL] 🔴 v9.2.49 자기 결함 교정. LEDGERSRC 가 portfolio 를 원장 기준 '목표'로 교체했는데, Action Board 의 '보유' 줄이 그 portfolio 를 그대로 읽어 아직 사지 않은 종목을 보유로 표기했다. 실측(2026-08-14): SLV 보유일 0d · 진입 1건 · 원장 체결 0건인데 '보유 SLV 6.8%' 로 출력 — Commander 가 이미 보유한 것으로 오인. 목표와 보유는 다른 것이며 한 변수를 두 라벨로 쓰면 안 된다. 처방: 보유 줄은 transition['current'](원장 실보유)를 읽고, 목표는 '목표'로 명시 분리. 미보유 신규 진입분은 보유 줄에서 제외하고 별도 진입 예정 표기.
# CHANGE  : v9.2.55 [N1+GATEBLOCK] 🔴 S290 DIR-S290_2 §3: ⑴ 목표비중 표에 당일 진입판정(entry_ok) 미달 표시 —
#           신규 편입은 🔴(신규매수 근거 없음) / 보유 지속은 🟡(최소보유 정상, 추가매수만 무근거)로 분리.
#           REG-S290_4 실측: 엔진이 entry_ok=False·ratio 0.24x 로 판정한 XLE 가 목표 25.4% 매수 지시로 노출됐다.
#           ⑵ transition v2.4.0 gate_blocked 소비 — 당일 청산분 재진입이 차단된 사실을 표시한다.
#           v2.3.0 이 이미 막고 있었으나 로그에만 남아 화면은 진입·청산 동시 표기만 보였다(휩쏘 피로의 표시층 원인).
#           비중·임계·시그널 무접촉. 판정은 엔진 evaluate_all 인용 (원칙 D·격언 #111).
# CHANGE  : v9.2.49 [LEDGERSRC] 🔴 Commander 지시: 전 카드의 데이터 원천을 포지션 원장으로 통일. 결함: 목표비중·Action Board·전일대비변경이 run_prima4 재현값을 읽었다. 재현값은 '처음부터 이 규칙으로 굴렸다면 지금 이랬을' 종착점이라 Crown 격상마다 과거 경로째 다시 그려진다(#103→#104 실측: 격상일 2026-08-11 인데 체결 경로는 2026-03-05 부터 갈림). 그 결과 실보유 XLU 69.9/GLD 22.2/ITA 7.4/TLT 0.5 인 계좌에 GLD 70/ITA 21.6/SLV 5.3/SMH 1.8/NLR 1.3 을 표시하고, 보유 7일(목표 21일)인 XLU 전량 매도를 지시했다 — 근거 없는 조기이탈(격언 #131). 처방: argus_position_transition.compute_transition() 을 호출해 원장 출발 목표·포지션·현금·전이 지시를 얻고, portfolio/fpos/cash_pct 단일 주입점에서 교체한다 → 하위 전 카드가 자동으로 원장 기준이 된다(카드별 개별 수정 0). 재현값은 목표비중 각주 대조표로 강등. 전일대비변경은 원장 fills 기준 실제 체결로 전환(재현 diff 폐기). 원장·전이 모듈 부재 시 종전 동작 폴백. 판정은 전량 엔진 함수 위임 — 규칙 사본 없음. 자본 로직 무접촉.
# CHANGE  : v9.2.48 [CARDORDER] Commander 지시(표시 전용): 카드 배열 재정의 + 매수 논리 2분할. (1) 순서 = 헤더·Action Board·전일대비변경·목표비중·Candidate Watch·Risk Board·매크로 스냅샷·트레일링·6M Holdings·1개월 수익률순위·포착률·STORM v2+Shadow Slot·Driver Cluster·보유 종목 상세·매수 후보 상세·상태 라벨·Gate 해제 후보·AAQG 각주·Appendix. 결정→감시→위험→맥락→상세 순으로, 매매 판단에 쓰는 카드를 상단에 모은다. (2) 구현은 블록 이동이 아니라 sentinel 재배열 — 산출 시점에 <!--§SECT:key§--> 를 심고 말미에 SECTION_ORDER 대로 재조립한다. 계산 순서(변수 의존)는 그대로 두고 출력 순서만 바꾸므로 대규모 코드 이동에 따르는 누락·역참조 사고가 원천 차단되고, SECTION_ORDER 미등재 섹션도 원 순서대로 보존된다(내용 소실 0). (3) v9.2.46 이 목표비중 각주 하나에 합쳐 두었던 매수 논리를 분리 — 보유 5종은 목표비중 각주, 후보 감시는 Candidate Watch 각주. 카드와 그 설명이 붙어 있어야 읽힌다.
# CHANGE  : v9.2.47 [CROWNXCHK] 🔴 Crown 배지 stale 원천 차단. 실사고: Crown #103 배포판이 `_CROWN_NUM="#101"` 을 갱신하지 않은 채 나갔고 #104 가 이를 상속 — 렌더러 1순위(ENGINE_METADATA.crown_number)가 낡은 값을 그대로 표시해 #104 산출물이 '#101' 배지로 발행됐다. 엔진 자가검사 CU5 는 ENGINE_METADATA == _CROWN_NUM 일치만 보므로 두 값이 함께 낡으면 통과한다(일관성 검사의 맹점). 처방: 파일명 CROWN(\d+) 이라는 독립 축을 신설해 엔진 자기신고와 교차 대조 — 불일치 시 hard fail(exit 1). 파일명에 CROWN 토큰이 없으면 SKIP(오탐 방지). 표시 전용 · 자본 로직 무접촉.
# CHANGE  : v9.2.46 [S288 CHARACTER] Commander 지시(표시 전용) 2건: (1) 21종 성격 한 줄 정의를 매수 논리에 반영 — TICKER_CHARACTER 사전 신설(축 / 한 줄 정의 / 근거 수치), 출처는 claude_ARGUS_21TICKER_CHARACTER_S288.md (엔진 채점식 + 19년 에피소드 838건 + SPY 상관 + era 분리 금리민감도 + VIX 국면 선행수익). (2) 매수 논리를 Top5 보유 종목 한정에서 **후보 감시 종목까지 확장** — _watch_candidates() 신설, render_slot_proximity 와 동일한 ratio·컷오프 정의를 공유해 두 카드의 서열 불일치를 원천 차단, 미보유 중 컷오프 0.80배 이상 최대 5종. 후보 블록에는 진입 자격/근접 라벨과 ratio·컷오프·Gate 차단 여부를 병기. 블록 생성은 _rationale_block() 으로 단일화(보유·후보 렌더 경로 이원화 방지). 진입 지시 아님(격언 #15) — 엔진·시그널·threshold·자본 무접촉.
# ---------
# VERSION : v9.2.45-OPPCOST
# DATE    : 2026-08-10
# CHANGE  : v9.2.45 [S288 OPPCOST] Commander 지시(표시 전용): 포착률 계기판에 "불참 이득" 열 신설 — 미보유 구간의 (포트폴리오 수익 − 그 종목 수익). 근거: 포착률은 분모가 단순 보유라 기회비용을 담지 못해 5슬롯 21종 구조에서 단독 오독을 유발한다. 실측(1Y) — 포착률 기준 실패로 보이던 XLE(-5%)·QQQM(-15%)·PAVE(3%)·XLF(0%) 는 불참 이득이 각각 +60.0/+67.8/+68.5/+73.1%p 로 불참이 옳았고, 진짜 놓친 종목은 SMH(-44.5%p)·COPX(-31.6%p) 2종뿐이었다. 포착률 순위와 발굴 우선순위가 다른 종목을 지목함을 계기판이 직접 보여주도록 배선. equity 길이 불일치 시 열 전체 — 처리(날조 0). 관측 전용 — 엔진·시그널·자본 무접촉.
# ---------
# VERSION : v9.2.44-CAPLEGEND
# DATE    : 2026-08-10
# CHANGE  : v9.2.44 [S288 CAPLEGEND] Commander 지시(표시 전용): 포착률 계기판 각주에 열 정의 4항 (자산 1Y / 엔진 포착 / 포착률 / 보유일) + 읽는 법 3항 추가. 종전 각주는 포착률 산식과 "낮음이 곧 실패가 아님" 만 한 줄로 담아, 나머지 3개 열이 무엇을 재는지 문서 밖 지식에 의존했다. 특히 100% 초과의 의미(로테이션 알파)가 어디에도 없어 계기판의 핵심 판독이 누락된 상태였다. 카드 자체로 판독이 닫히도록 보강. 관측 전용 — 엔진·시그널·자본 무접촉.
# ---------
# VERSION : v9.2.43-CAPFIX
# DATE    : 2026-08-10
# CHANGE  : v9.2.43 [S288 CAPFIX] 🔴 포착률 계기판 전면 오표시 교정. 결함: main 이 run_prima4 를 정수 인덱스 df 로 호출해 trade_log["date"] 가 위치 인덱스(int)로 반환되는데, _compute_capture_1y 가 이를 pd.to_datetime 으로 변환(→ 전량 1970-01-01) → 첫 날에 전 이벤트 소진 → 보유 재구성이 "최종 보유 5종이 1년 내내 100% 보유" 로 고정. 실측 오표시: SMH +99.2%/COPX +98.0% 를 포착 0% 로, 보유 5종을 포착 100% 로 보고(실제로는 2025-10~2026-01 SMH·COPX 보유 구간 존재). 처방 2층: (1) 날짜축을 df 에서 취하고 trade_log 가 위치 인덱스면 그 축으로 역매핑, (2) 축퇴 가드 — 보유일이 전 종목 0%/100% 로만 나오면 카드 자체를 억제하고 경고(틀린 숫자 서빙 금지, fail-loud). 관측 전용 — 엔진·시그널·자본 무접촉.
# ---------
# VERSION : v9.2.42-GATELINE
# DATE    : 2026-08-10
# CHANGE  : v9.2.42 [S288 GATELINE] Commander 적발(표시 전용): Crown 102 로 TLT 진입 게이트(DXY>100)가 신설되었는데 손으로 쓴 ENTRY_RATIONALE 본문은 그대로여서 하드 게이트 1건이 누락된 채 서빙될 뻔했다. 동일 유형 잠복 1건 동시 적발 — XLU 는 OAS_HY>7 하드 게이트가 본문에 부재. 처방 2층: (1) TLT 본문에 DXY>100 진입차단 + Crown 102 대칭 교정 해설 반영, (2) 근본 — 게이트만은 산문에서 분리해 엔진 TICKER_SPEC['gate'] 단일 원천에서 기계 산출(_gate_line + _GATE_LABEL 신설, main 에서 _ENGINE_TICKER_SPEC 주입). 엔진 게이트가 바뀌면 문구가 자동 추종하므로 손 문구 stale 이 구조적으로 불가능해진다. 미등재 토큰은 원문 노출(날조 0). 엔진·시그널·threshold·자본 무접촉.
# ---------
# VERSION : v9.2.41-TLTGATE
# DATE    : 2026-08-10
# CHANGE  : v9.2.41 [S288 TLTGATE] Crown 102(TLT 진입·청산 대칭차단) 표시 정합. 결함: 목표비중표 Gate 열이 TLT 를 무조건 '🔓 면제'로 하드코딩 — Crown 102 로 DXY>100 진입차단이 신설되면서 실제 차단 국면에 '면제'로 오표시될 구조. 처방 2건: (1) TLT Gate 열을 DXY 실측 분기로 전환('🔒 DXY>100' / '🔓 면제'), (2) Next Trigger 문구를 'DXY>100 TLT 50%청산 + 진입차단(Crown 102)'로 정정. 표시 전용 — 엔진·시그널·threshold·자본 무접촉.
# ---------
# VERSION : v9.2.39-SLOTVIS
# DATE    : 2026-08-06
# CHANGE  : v9.2.39 [S286 SLOTVIS] Commander 지시(표시 전용): 슬롯 경쟁 표시의 **범위 밖 침묵** 해소 + 다음 진입 스캔 잔여 표시. 결함(2026-08-06 실측): render_slot_proximity 가 진입 근접(0.80~1.0배)·탈락 근접(1.0~1.25배) **경계 구간만** 표시하고, 그보다 확실한 상태 — 미보유인데 컷오프 초과(SLV 3.67x = 컷오프 1.75x 의 2.10배) / 보유인데 컷오프 미만(TLT 1.04x = 0.59배, 이미 Top5 밖) — 를 전부 무표시했다. 전날 TLT 는 1.00배로 경계라 카드가 떴다가, 0.59배로 **악화되자 카드가 사라지는** 역전 현상 발생. 처방 2건: (1) 🟢 진입 자격 충족(미보유 ∩ ratio/컷오프 ≥ 1.0) + 🔴 이탈권(보유 ∩ < 1.0) 2종 신설, 우선순위 정렬(이탈권 > 진입자격 > 탈락근접 > 진입근접 > 빈슬롯) + 표시 상한 3→5. (2) Action Board 에 다음 진입 스캔 잔여 거래일 표시 — 엔진 rebal_freq(주간 5거래일) 단일 원천 소비, 보유 최소 held_days 기준 **하한 추정**임을 문구로 명시(엔진 내부 ls 미노출). 슬롯 만석 시 '스캔 미가동' 별도 표기. 표시 전용 — 엔진·시그널·threshold·자본 무접촉.
# ---------
# VERSION : v9.2.38-CROWNANCHOR
# DATE    : 2026-08-05
# CHANGE  : v9.2.38 [S286 CROWNANCHOR] 🔴 Crown 토큰 네임스페이스 충돌 근본 제거. 실사고(G2 Crown Stale Gate 재발): 외부 감시가 서빙 HTML 에서 `Crown #NN` 을 수집해 서빙 버전을 판정하는데, 문서에는 버전 표기(헤더·푸터 #101) 외에 **설계 계보 인용**(집중도 카드·D-2 부록·매수 논리 각주)이 같은 토큰 형태로 섞여 있었다. 실측 8개소 중 #101 은 2회뿐이고 #98 이 3회로 최빈 → 어떤 수집 규칙(최빈/최초/불일치검출)을 쓰든 오판. ⚠️ v9.2.36 매수 논리 각주가 계보 인용 2건(#93·#100)을 추가해 충돌을 5→8개소로 **악화**시킨 책임이 본 렌더러에 있다. 처방 3층: (1) `<meta name="crown">` 신설 — data-date meta 선례를 따른 기계 판독 단일 앵커. (2) 계보 인용의 토큰 형태를 `Crown #NN` → `Crown NN` 으로 분리 — 사람이 읽는 의미는 불변, 기계 수집 패턴과는 비충돌. (3) 🛡️ CROWNGUARD 신설 — 빌드 타임에 산출 HTML 의 `Crown #\d+` 토큰이 서빙 Crown 단일값인지 검사, 위반 시 exit(1). 향후 누구든 계보 인용을 `#` 형태로 되돌리면 GHA 가 빨간불로 차단한다(희망이 아니라 강제). 표시·검증 레인 전용 — 엔진·시그널·threshold·자본 무접촉.
# ---------
# VERSION : v9.2.37-FRESHGUARD2
# DATE    : 2026-08-05
# CHANGE  : v9.2.37 [S286 FRESHGUARD2] 🔴 층② 자기참조 결함 근본 처방. 실사고(2026-08-05 08:05 KST 빌드): 브리핑이 08-03 데이터로 생성됐는데 빌드 로그는 "🟢 최신(생성시)"를 출력했고, 열람 시점 층①(JS)만이 "🔴 STALE · 정본 08-04"를 잡아냈다. 원인: _read_canonical_date()가 **로컬 파일만** 읽는데 GHA 워크플로는 argus_data.csv 한 개만 로컬에 두므로, 빌드가 쓴 입력과 대조 대상이 동일 파일이 되어 항상 일치 → 검출력 0(동어반복). v9.2.32 주석이 밝힌 설계 의도("로컬 vs 원격 경쟁상태 검출")와 구현이 불일치했다. 처방: (1) _fetch_canonical_remote() 신설 — 원격 latest.json 을 **커밋 무관 캐시버스터**로 회수(중간 캐시 화석 차단, REG-S286 정합). (2) _read_canonical_date() 를 로컬 우선이 아니라 **원격 정본 우선 → 로컬 폴백**으로 전환하고, 로컬·원격을 모두 확보한 경우 둘을 비교해 불일치를 별도 경고. (3) 빌드 시점 정본이 산출 기준일보다 앞서면 기존 🔴 STALE 경로가 정상 발동(GHA 로그 가시화). 표시·검증 레인 전용 — 엔진·시그널·threshold·자본 무접촉. VGUARD 무영향.
# ---------
# VERSION : v9.2.36-RATIONALE
# DATE    : 2026-08-04
# CHANGE  : v9.2.36 [S286 RATIONALE] Commander 지시(표시 전용): 목표비중 카드 각주에 **보유(슬롯 선정) 종목 한정** 매수 논리 해설 추가. 엔진 코드에서 추출한 점수식 사실과 그 "왜"에 대한 해석을 문장 내 구분 표기(통념 → ARGUS 채점 → 해석). ENTRY_RATIONALE 21종 사전 신설(보유 종목만 렌더 — 미보유는 출력 0) + render_entry_rationale() 신설 + 목표비중 '비중 산정 안내' 블록 말미 배선. 텍스트는 html.escape 로 이스케이프(부등호 포함 조건식이 태그로 오인되는 사고 차단). VGUARD 무영향(v9 토큰 불변 — 해설 본문에 버전 문자열 미포함). 자본·시그널·threshold·엔진 무접촉.
# ---------
# VERSION : v9.2.35-RISKVIS
# DATE    : 2026-08-02
# CHANGE  : v9.2.35 [S285 RISKVIS] Commander 승인 3건(표시 전용): ② ExSn 임박도 % 소수1자리(99.8%가 100%로 반올림돼 "이미 발동" 오독 유발하던 결함) ③ Risk Board 집중도 카드 신설 — 단일종목 소프트캡(0.70, Crown #98 water-filling) 발동 상태 가시화(발동=설계 산출·캡 스윕 5점 중 0.7만 RULE29+STRESS 14/14 통과 근거 명시 / 미발동=여유 표시) ④ 헤더 원장 reconcile 배지 — argus_position_ledger.json(로컬 전용, AAQG_LOCAL 예외 패턴) as_of·last_reconciled 표시 + 기준일 대비 5영업일 초과 시 🔴 STALE(155.7%p 괴리 6영업일 방치 사건 재발 가시화). 자본·시그널·threshold 무변경.
# ---------
# VERSION : v9.2.34-AAQG_LOCAL
# DATE    : 2026-07-31
# CHANGE  : v9.2.34 [AAQG LOCAL 확정] Commander 재지시 "local로 유지" — v9.2.33의 AAQG_GRADES.csv 원격 게시 전환 방향을 철회. load_aaqg()를 로컬 전용(원격 시도 없음)으로 환원. aaqg_quarterly_update.py의 직전분기 비교 조회도 동일 사유로 로컬 전용 환원(v3.3). aaqg_quarterly_publish.yml은 저장소 미반영 권고. "모든 CSV 하드코딩"(v9.2.32) 원칙의 유일한 예외로 AAQG만 확정 존치.
# VERSION : v9.2.33-AAQG_REMOTE
# DATE    : 2026-07-31
# CHANGE  : v9.2.33 [AAQG 예외 해소] Commander "a" 선택(게시 워크플로 신설) 이행 — aaqg_quarterly_publish.yml 신설로 AAQG_GRADES.csv를 argus-public-data에 분기 게시하도록 완결. load_aaqg() 순서를 원격 우선→로컬 폴백→내장 fallback으로 전환. 워크플로 최초 실행(PUBLIC_DATA_PAT 시크릿 등록 필요) 전까지는 로컬/fallback 경로가 실질 작동 — 격리 재현 2개 시나리오(로컬 有/無) 모두 설계대로 검증.
# VERSION : v9.2.32-PUBLICDATA_HARDCODE
# DATE    : 2026-07-31
# CHANGE  : v9.2.32 [ALL-CSV HARDCODE] Commander 지시 — "모든 CSV는 argus-public-data 레포 자료를 사용하도록 하드코딩". 로컬 경로 후보 나열 방식이 저장소마다 무엇이 있고 없는지 추측하게 만들어 argus_daily_holdings.csv 미존재로 트레일링 성과가 반복 실패한 근본 원인 → argus_data.csv/BT_LONG_v5_complete.csv/holdings ledger 전량을 PUBLIC_BASE 하드코딩 원격 회수로 전환(_fetch_public_csv 신설). 예외 2건: (1) AAQG_GRADES.csv — 원격 미게시 확인(404 실측) → 로컬 유지 + Commander 결정 대기 명시. (2) _read_canonical_date() — 로컬 vs 원격 경쟁상태 검출이 목적 자체라 원격 전용화 시 비교 불능(FRESHGUARD 층2 무력화) → 예외 유지. 완전 격리(로컬 CSV 0개) 환경 실빌드로 검증(포트폴리오 산출·VGUARD 정상).
# VERSION : v9.2.31-VGUARD_USCORE
# DATE    : 2026-07-31
# CHANGE  : v9.2.40 [CAPTURE] (S286, Commander 지시 「포착률 상시 계기화」) 21종 1Y 포착률 계기판 신설 — trade_log 일별 보유 재구성으로 자산수익 vs 엔진 실현(보유 구간 곱연결) vs 포착률·보유일비중 산출(main→_CAPTURE_ROWS 전역 주입, _ENGINE_CONST 관례), generate_html 말미 카드 렌더. 근거 REG-S286_6·10(COPX 4.8% 최악 실측·21종 유휴 분해). 관측 전용 — 매매 지시 아님(격언 #15) · 자본·엔진 무접촉 · Crown/버전 토큰 신설 0 (VGUARD·CROWNGUARD 비충돌).
# CHANGE  : v9.2.31 [VGUARD REGEX FIX] v9.2.30 빌드가 GHA exit 1 로 실패한 실사고 근본 교정 — 렌더러·HTML 산출물은 모두 정상이었고, VGUARD 토큰 정규식의 문자 클래스 [A-Za-z0-9\-] 에 언더스코어가 빠져 RENDERER_VER="v9.2.30-TRAILLOCK_SAFE" 가 "v9.2.30-TRAILLOCK" 으로 절단 추출되어 자기 자신과 불일치 판정된 오탐이었다. 접미사에서 _ 를 빼는 우회 대신 스캐너의 토큰 정의를 RENDERER_VER 이 취할 수 있는 문자 집합과 일치시킨다([A-Za-z0-9_\-]). 본 버전 자체(_USCORE)가 언더스코어 포함 회귀 검증 케이스 역할을 겸한다.
# VERSION : v9.2.30-TRAILLOCK_SAFE
# DATE    : 2026-07-31
# CHANGE  : v9.2.30 [DEPLOY-ORDER SAFE] v9.2.29 하드 import 가 의존모듈 미반영 시 브리핑 전체를 중단시킨 실사고(GHA exit 1) 교정. try/except 방어 전환 — 구버전(v1) 모듈 잔존 시 브리핑은 정상 렌더하되 트레일링 섹션만 차단 카드로 대체. v1 함수를 호출하지 않으므로 "조용한 소급 BT 회귀"는 여전히 구조적으로 불가능(회귀 시뮬 검증: BT 수치 노출 False).
# VERSION : v9.2.29-TRAILLOCK
# DATE    : 2026-07-31
# CHANGE  : v9.2.29 [TRAILING HARDLOCK] Commander 지시 — "트레일링 성과는 실제 보유 장부 실현 수익률로 하드코딩". Crown 격상 반복 중 본 요구가 되풀이 유실된 이력 차단. L2 방어 적용: import 시 assert_realized_policy() 호출(정책 훼손 시 즉시 예외) + format_trailing_html() 호출에서 run_prima4 equity 전달 제거(BT equity 유입 경로 물리 차단). 표시 전용.
# VERSION : v9.2.28-CAP70DOC
# DATE    : 2026-07-31
# CHANGE  : v9.2.28 [CAP70 DOC SYNC] Crown #98 배포 후 실배포 페이지 점검에서 적발 — D-2 부록이 "단일자산 soft cap 40%" + "40% soft clamp 후 재정규화" + 폐기된 LEVEL_WEIGHT 하이브리드 설명을 그대로 유지하여, 본문 안내(70% 상한·ratio^DS_K)와 정면 모순. 표시 전용 교정: D-2를 Crown #98 water-filling 실로직으로 갱신(raw=(ratio×sizing)^DS_K → 정규화 → 70% 반복 water-filling, 보유 1종만 100%). 엔진·자본 무접촉.
# VERSION : v9.2.26-SLOTPROX
# CHANGE  : v9.2.26 [SLOT-PROXIMITY] 근접 정의 교정(Commander) — 신호 문턱 근접 → Top5 진입/탈락 근접. 컷오프=5위 ratio 기준, 진입 0.8~1.0배 / 탈락 1.0~1.25배. 빈 슬롯 시 경쟁부재 표시.
# CHANGE  : v9.2.25 [ENTRY-PROXIMITY] 진입 트리거 근접 카드 신설 — 청산 근접 카드와 대칭. 엔진 per_signal.prox 집계, 미보유 종목 최근접 미충족 EnSn 1건씩 노출(근접>=0.70, 최대 4건). 표시 전용.
# CHANGE  : v9.2.24 [FALLBACK-FIRST] _macro_fallback 우선 복원 — v9.2.23 live_value 우선이 인터랙션·모멘텀 신호 가독성 저하(구성 매크로값·단위 소실). fallback 미등록 신호만 live_value 보완.
# CHANGE  : v9.2.23 [LIVE-VALUE TUPLE] live_value tuple 허용 — 엔진 반환형(tuple) 미인식으로 전 종목이 _macro_fallback 의존하던 잠복 결함 해소. PDBC ensn 값 표시 정상화.
# VERSION : v9.2.22-PDBC21SYNC
# CHANGE  : v9.2.22 [PDBC 21종 동기] 1개월 수익률순위 UNIV를 엔진 ENTRY_FUNCTIONS 키에서 자가치유 도출(하드코딩 20종→동적) · footer "전체 N종목" 동적 · EXSN fallback PDBC(WTI 100/VIX None) · AAQG 라벨 "N종 채점"+PDBC 미채점 명시. S280 Crown #96 정합.
# VERSION : v9.2.27-FRESHGUARD
# DATE    : 2026-07-22
# CHANGE  : v9.2.21 [EMPTY-PORT-DISAMBIG] 빈 포트 의미 분리 — engine_ok 플래그 신설로 "run_prima4 실패"와 "엔진 정상+보유 0종(전량 현금)"을 구분. 구 로직은 두 상태 모두 portfolio=={}로 뭉개 WTI>90 전 종목 청산 시 정당한 현금 100%를 '데이터 없음'으로 오표시하고 현금을 0.0%로 고착시켰다(S280 실사건 2026-07-23). (1) main: engine_ok 신설 + `if eff:` 제거(성공 시 빈 dict도 정상 반영) + cash_pct=max(storm현금, 100-보유합) (2) generate_html: engine_ok 파라미터(기본 True=하위호환) (3) Action Board·목표비중 표시 3분화(실패 loud / 전량현금 정상 / 정상 포트) (4) v9.2.20 충전 블록 조건을 portfolio→engine_ok로 확장(보유 라인만 portfolio 유지) — 0종에서도 배지·변경상세 표시. 자본·엔진 무영향.
# CHANGE  : v9.2.27 [FRESHGUARD · REG-S284] 신선도 배지를 '열람 시점 재계산'으로 전환 — 정적 산출물의 시간 붕괴(decay) 제거. 결함: 배지는 생성 순간에 계산되어 HTML에 구워진다. 07-27 23:27 생성 시점엔 미국장 진행 중이라 07-24가 최신 완결 세션이었고 '최신' 표기가 참이었으나, 07-28 열람 시점엔 07-27 정산 데이터가 존재하여 같은 배지가 거짓이 된다. 정적 페이지는 스스로 갱신할 수 없다. → 빌드 타임 대조만으로는 해결 불가(그 결과도 함께 구워짐). 처방 2층: (1) 열람 시점 재계산 — 배지에 id/data-src 부여 + latest.json fetch 후 브라우저가 배지를 재작성(FRESHGUARD_JS). 언제 열어도 그 순간의 진실 표시. (2) 빌드 타임 보조 대조 — _read_canonical_date()로 생성 시점 정본과 대조, 워크플로 경쟁 상태(fetcher 커밋 전 curl) 검출. JS 미동작 시 '(생성시)' 접미로 시점 명시. VGUARD 무영향(v9토큰 불변).
# CHANGE  : v9.2.20 [ACTION-BOARD FILL] Action Board 여백 충전 — 변경 배지(진입/청산/리밸/슬롯) + 변경 상세 라인(진입·청산 티커+리밸 방향↓↑, 조정 사유 자명화) + 현재 보유 라인(종목별 비중). 모두 기존 _diff·portfolio 재사용, portfolio 부재 시 graceful 생략(fail-loud 배너가 대체). VGUARD 무영향.
# CHANGE  : v9.2.19 [ACTION-BOARD + FAIL-LOUD] (1) Action Board 결론·의무매도 하드코딩('유지'/'0건') 제거 → load_daily_diff() exited 건수=의무매도, changed·exited 유무로 결론 동적 산출(유지/청산/조정) + 변경 섹션과 diff 단일 소스(이중 로드 제거). (2) stale fallback fail-loud 전환: PORTFOLIO_FALLBACK 폐지→run_prima4 실패 시 빈 포트+'데이터 없음' 배너, AAQG asof/nxt fallback→'데이터 없음' 마커. VGUARD 무영향.
# CHANGE  : v9.2.18 [RISK-BOARD] 보유 ExSn 임박 카드(엔진 EXSN 주입) + 실계좌 드리프트(real_account.json) + 트리거 라벨 정밀화(WTI/VIX=전량청산 매도 / TNX>4.8·DXY>105·DXY>100=50% 부분청산 매도 / 매수 트리거 아님). 기존 TLT/Gate 카드 보존. VGUARD 무영향.
# CHANGE  : v9.2.15 [SRCDATE-FIX] 헤더 데이터 기준일을 df 마지막 행 실제 날짜(data_date)로 배선 — v9.2.14가 result['evaluated_at_date'](시퀀스 번호 393)를 표시해 "데이터 기준일 393 · 기준일 불명" 결함 → 실제 날짜+신선도 배지 정상화. generate_html(data_date=) 파라미터 신설, 호출부 df['Date'].iloc[-1] 전달. VGUARD 무영향(v9토큰 불변).
# CHANGE  : v9.2.14 [HEADER SRCDATE] 헤더에 데이터 기준일(source date) 라벨 + 신선도 배지(경과 영업일 색상) + <head> data-date meta 신설 — 데이터 정체 즉시 가시화(Commander 지시). VGUARD 무영향(렌더 v9토큰 불변).
# CHANGE  : v9.1.9 6M차트 재구성 / v9.2.0 매크로 신호등 3색 / v9.2.1 등급 체계 통합 / v9.2.3 AAQG v4.1 라벨·블렌드 70/30·R축 기여도 정합 / v9.2.4 D-2 등급순 정렬: AAQG 각주 단일화(결정 우선순위+ratio fallback+선정기준 일원화, 카드 D-2 흡수·번호 D-3~5→D-2~4)+AAQG Q공식 v4.0(60/20/20) 정정 / v9.2.5 1개월 누적 수익률순위(전체종목중) 섹션 신설 / v9.2.6 수익률순위 컴팩트화 / v9.2.7 이모지-티커 nowrap / v9.2.10 stale 해소 3종: 헤더 ENGINE 표기 #80→#89 정정 + Crown fallback 하드코딩('#78') 제거→파일명 CROWN\d+ 파싱(격상 영구 무관) + FOOTER 버전 문자열 RENDERER_VER 상수 단일화(이중 표기 제거) / v9.2.11 헤더 배지 RENDERER_VER 상수 배선 — v9.2.10이 푸터만 배선하고 배지(L807) 하드코딩 v9.2.9 잔존 → 단일 원천 완결(재발 구조 차단) / v9.2.12 VGUARD 빌드 타임 버전 무결성 게이트 — 산출 HTML의 v9.x 패턴 ≠ RENDERER_VER 단일값 또는 출현<2회 시 exit(1) → GHA FAIL = 결함 배포 물리적 차단 / v9.2.13 [T3-SIZEMULT S277] 목표비중 ratio 열에 자산 사이징 배수 마커(SLV ×½↓·COPX ×1.2↑) 표시 — 엔진 final_positions.size_mult 단일 원천 소비, "SLV 3.67x인데 비중 절반" 격차 해소(격언 #80) + 마커 존재 시 카드 하단 사유 설명줄 자동 부착(Commander 지시)
# ENGINE  : Crown #89 PRIMA2_v0_5_15_CROWN89_GSR_LIVE.py (run_prima4) ※ 표기 참고용 — 런타임은 ENGINE_GLOB 자동탐색(_LIVE)
# ======================================================================

"""
🦅 ARGUS Brief HTML v2 렌더러
엔진 evaluate_all 결과 → v2 다크 테마 인터랙티브 HTML

사용: python argus_brief_html_v2.py [--output index.html]
필요: BT_LONG_v4_complete.csv + argus_data.csv + PRIMA 엔진 (같은 디렉토리)
"""
import sys, os, glob, importlib.util, json, urllib.request
import pandas as pd, numpy as np
import warnings, argparse
from datetime import datetime

warnings.filterwarnings('ignore')
#!/usr/bin/env python3
"""
🦅 ARGUS Brief HTML v2 렌더러
엔진 evaluate_all 결과 → v2 다크 테마 인터랙티브 HTML

사용: python argus_brief_html_v2.py [--output index.html]
필요: BT_LONG_v4_complete.csv + argus_data.csv + PRIMA 엔진 (같은 디렉토리)
"""
import sys, os, re, glob, importlib.util, json, urllib.request
import html as _html
from argus_engine_contract import (load_engine as _contract_load_engine, normalize_data,
                                   engine_view, assess_readiness, evaluate_engine)
import pandas as pd, numpy as np
import warnings, argparse
from datetime import datetime, timezone, timedelta
KST = timezone(timedelta(hours=9))

# 버전 단일 진리원 (헤더 주석과 동기 의무) — FOOTER 등 표시부는 본 상수만 참조
RENDERER_VER = "v9.2.72-DISPLAY_CONSISTENCY"

# ══════════════════════════════════════════════════════════════
# 🛡️ v9.2.27 FRESHGUARD — 신선도 주장의 2층 처방
# ══════════════════════════════════════════════════════════════
#  원칙: 정적 산출물에 시간 상대적 주장을 굽지 않는다.
#        '최신'은 생성 시점의 사실일 뿐 열람 시점의 사실이 아니다.
#  층 1 (핵심) = FRESHGUARD_JS — 브라우저가 열람 시점에 latest.json을
#                가져와 배지를 재작성. decay 원천 제거.
#  층 2 (보조) = _read_canonical_date() — 빌드 시점 정본 대조.
#                워크플로 경쟁(fetcher 커밋 전 curl) 검출용.
FRESHGUARD_PATHS_JSON = ("latest.json", "./latest.json", "../latest.json",
                         "data/latest.json")
FRESHGUARD_PATHS_CSV = ("argus_data.csv", "./argus_data.csv", "../argus_data.csv",
                        "data/argus_data.csv")


def _fetch_canonical_remote(timeout=20):
    """🆕 v9.2.37: 원격 정본(latest.json) 최종행 날짜. 실패 시 None.

    🚨 캐시버스터 필수 — 중간 캐시가 구판을 200 OK 로 돌려주는 사고(REG-S286 실측:
       평문 회수 시 26일 화석 반환)를 차단한다. 커밋 sha 를 알 수 없는 시점이므로
       산출 기준일 후보 대신 프로세스 고유값(pid+시각 아님 — 재현성 위해 파일명 고정)을
       쓰지 않고, GitHub raw 가 무시하지 않는 임의 쿼리 파라미터를 부여한다.
    """
    import urllib.request as _ur
    import json as _json
    for _q in ("fg2", "fg2r"):
        try:
            _req = _ur.Request(f"{PUBLIC_BASE}/latest.json?cb={_q}",
                               headers={"User-Agent": "argus-brief-html/9.2.37"})
            with _ur.urlopen(_req, timeout=timeout) as _r:
                _d = _json.loads(_r.read().decode("utf-8", "replace")).get("Date")
            if _d:
                return str(_d)[:10]
        except Exception:
            continue
    return None


def _read_local_date():
    """빌드가 실제로 사용한 로컬 입력의 최종행 날짜. 없으면 None."""
    import os as _os
    import json as _json
    for _p in FRESHGUARD_PATHS_JSON:
        try:
            if _os.path.exists(_p):
                with open(_p, encoding="utf-8") as _f:
                    _d = _json.load(_f).get("Date")
                if _d:
                    return str(_d)[:10]
        except Exception:
            pass
    for _p in FRESHGUARD_PATHS_CSV:
        try:
            if _os.path.exists(_p):
                _last = ""
                with open(_p, encoding="utf-8") as _f:
                    for _line in _f:
                        if _line.strip():
                            _last = _line
                _c = _last.split(",")[0].strip()[:10]
                if len(_c) == 10 and _c[4] == "-":
                    return _c
        except Exception:
            pass
    return None


def _read_canonical_date():
    """빌드 시점 정본 최종행 날짜(YYYY-MM-DD). 회수 실패 시 None.

    🔴 v9.2.37 근본 처방 — 자기참조 제거.
      구 구현은 **로컬 파일만** 읽었다. GHA 워크플로는 argus_data.csv 하나만 로컬에
      두므로 "빌드가 쓴 입력"과 "정본 대조 대상"이 같은 파일이 되어 항상 일치했고,
      층② 검출력은 구조적으로 0 이었다(동어반복). 2026-08-05 08:05 KST 빌드가
      08-03 데이터로 생성됐음에도 로그가 '🟢 최신'을 출력한 실사고의 원인이다.
      → 정본은 **원격 latest.json**(캐시버스터 회수)을 1순위로 삼고, 로컬은 폴백으로만
        쓴다. 둘 다 확보되면 비교하여 워크플로 경쟁 상태를 별도 경고한다.
    """
    _remote = _fetch_canonical_remote()
    _local = _read_local_date()
    if _remote and _local and _remote != _local:
        print(f"⚠️ FRESHGUARD(층2): 로컬 입력 {_local} != 원격 정본 {_remote}"
              f" — fetcher 갱신 전 빌드(경쟁 상태) 의심")
    if _remote:
        return _remote
    if _local:
        print("⚠️ FRESHGUARD(층2): 원격 정본 회수 실패 — 로컬 입력으로 폴백(자기참조 주의)")
        return _local
    return None


# 열람 시점 재계산 스크립트. f-string 아님 — 중괄호 이스케이프 불필요.
# latest.json 은 briefing.html 과 같은 저장소 루트에 서빙되므로 상대경로 fetch 가능.
FRESHGUARD_JS = """<script>
(function(){
  var el = document.getElementById('fg-badge');
  if (!el || !window.fetch) return;
  var src = el.getAttribute('data-src');
  var gen = el.getAttribute('data-gen') || '';
  function paint(c, t, tip){ el.style.color = c; el.textContent = t; if (tip) el.title = tip; }
  fetch('latest.json', {cache: 'no-store'})
    .then(function(r){ if (!r.ok) throw 0; return r.json(); })
    .then(function(j){
      var canon = String(j.Date || '').slice(0, 10);
      if (!canon) throw 0;
      if (canon === src) {
        paint('#94a3b8', '정본 날짜 일치 · 최신성 별도 확인',
              '정본과 날짜만 같습니다. 거래 세션 신선도·원장 연속성·실행 가능 여부를 보증하지 않습니다: ' + canon);
      } else {
        paint('#f87171', '🔴 STALE · 정본 ' + canon,
              '이 페이지는 ' + src + ' 데이터로 ' + gen + ' 에 생성됨. 현재 정본은 ' + canon + '.');
      }
    })
    .catch(function(){
      paint('#94a3b8', '⚪ 미검증',
            '정본(latest.json) 회수 실패 — 열람 시점 신선도 확인 불가');
    });
})();
</script>"""


warnings.filterwarnings('ignore')

# ── 설정 ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_BASE = "https://raw.githubusercontent.com/daifulee/argus-public-data/main"
# ENGINE_GLOB: prima_briefing v9.0.2 규약 정합 — PRIMA*_v*.py (PRIMA+PRIMA2) + '_LIVE' allow-list
ENGINE_GLOB = os.path.join(SCRIPT_DIR, "PRIMA*_v*.py")
ENGINE_LIVE_HINT = "_LIVE"
ENGINE_EXCLUDE_KEYWORDS = ("SHADOW", "REJECTED", "DEPRECATED", "ARCHIVE", "CANDIDATE")

# 🔒 v9.2.32 (S284, Commander 지시): "모든 CSV는 argus-public-data 레포 자료를 사용하도록 하드코딩".
#   배경: argus_daily_holdings.csv 가 GHA 저장소(argus-briefing)에 없어 트레일링 성과가 두 차례
#   연속 실패(import 오류 → VGUARD 오탐 이후 세 번째 사고). 로컬 경로 후보 나열 방식은 저장소마다
#   무엇이 있고 없는지 추측하게 만들어 동일 계열 결함을 반복 유발한다. 단일 정본(공개 미러)만
#   신뢰하도록 원천 고정한다. 예외 1건: _read_canonical_date()(FRESHGUARD 층2)는 "로컬 vs 원격
#   경쟁상태 검출"이 목적 자체이므로 대상에서 제외(원격만 읽으면 비교 불능이 되어 목적 소멸).
PUBLIC_BASE = "https://raw.githubusercontent.com/daifulee/argus-public-data/main"


def _fetch_public_csv(name, timeout=25):
    """argus-public-data 레포에서 CSV 하드코딩 회수. 실패 시 예외 그대로 전파(호출부가 처리)."""
    import io as _io
    import urllib.request as _ur
    req = _ur.Request(f"{PUBLIC_BASE}/{name}", headers={"User-Agent": "argus-brief-html/9.2.32"})
    with _ur.urlopen(req, timeout=timeout) as r:
        txt = r.read().decode("utf-8", "replace")
    return _io.StringIO(txt)


BT_LONG_NAME = "BT_LONG_v6_PDBCTRUNC_FEAT.csv"   # 🔴 v9.2.65 (S291): FEAT 판본 — KIL_SUP·GPR_HIGH 보유. v9.2.54 가 v5→v6 로 바꾼 라인의 후속 정정
BT_LONG = os.path.join(SCRIPT_DIR, BT_LONG_NAME)
ARGUS_DATA = os.path.join(SCRIPT_DIR, "argus_data.csv")

EMOJIS = {
    "GLD":"🥇","SLV":"🥈","XLE":"⛽","ITA":"✈️","SMH":"🔬","COPX":"🟤",
    "NLR":"☢️","EWZ":"🇧🇷","QQQM":"💻","VEA":"🌍","VNM":"🇻🇳","IWM":"📊",
    "PAVE":"🏗️","CIBR":"🛡️","CQQQ":"🇨🇳","XLF":"🏦","XLV":"💊","XLU":"💡",
    "TLT":"📈","INDA":"🇮🇳","PDBC":"⚒️"
}

# ══════════════════════════════════════════════════════════════════════
# 🆕 v9.2.36 (S286, Commander 지시) — 종목별 매수·매도 논리 각주 (표시 전용)
# ══════════════════════════════════════════════════════════════════════
#  목적: 목표비중 각주에 **슬롯 선정(보유) 종목 한정**으로 "왜 이걸 샀는가"를 명시한다.
#  구조: (헤드라인, 통념, ARGUS 채점, 해석) 4단. 앞 3단은 엔진 코드에서 추출한 사실,
#        마지막 '해석'은 구조에서 도출한 추론이며 렌더에서 라벨로 구분 표기한다.
#  안전: 본문에 부등호(>, <)가 다수 포함되므로 렌더 시 html.escape 필수(태그 오인 차단).
#        버전 문자열(v9.x) 미포함 — VGUARD 토큰 스캔 무영향.
#  범위: 표시 전용. 엔진·시그널·threshold·자본 무접촉.
ENTRY_RATIONALE = {'XLE': ('고유가를 사되, 에너지 주가의 반응을 확인한다',
         '에너지 가격과 에너지 기업의 주가는 함께 움직이지 않을 수 있다.',
         '유가 >85에서도 자체 정배열이면 +2.4, 역배열이면 −2.4. 실질금리 <0의 기본 +5.2와 변동성지수 >22의 +4.3이 별도로 작용한다.',
         '유가 상승 자체보다 그 환경을 주가가 받아들이는지를 함께 읽는 설계다. 같은 고유가라도 주가가 약하면 점수를 깎는다. 낮은 실질금리는 투자 부담 완화라는 '
         '설명과 연결할 수 있지만, 그 경제적 원인이 이 가점의 성과를 만들었다고 확인된 것은 아니다.'),
 'TLT': ('유가 급등 속에서도 인플레이션 반응을 구분한다',
         '장기 국채의 방어 역할은 물가와 금리의 움직임에 따라 달라진다.',
         '유가 >90에서 기대인플레이션 >2.5이면 차단하고, ≤2.5로 확인되면 +2.0. 실질금리 <0은 −3.0으로 반대로 작용한다.',
         '유가가 뛰어도 기대물가가 따라오지 않는 상황을 별도로 평가하는 설계다. 물가 압력이 지속되는 충격과 경기 둔화 가능성을 구분하려는 해석은 가능하지만, 이 두 '
         '지표만으로 공급 충격과 수요 위축의 원인을 확정하지는 못한다.'),
 'GLD': ('같은 고금리에도 금의 매력을 다르게 평가한다',
         '명목금리가 높다는 사실만으로 금의 조건을 결정하지 않는다.',
         '10년 명목금리 >4.1의 +6.4는 실질금리 ≥2이면 +1.5로 줄어든다. 달러지수 >101의 +2.6도 >110에서는 사라진다.',
         '핵심은 명목금리 가점에 실질금리 제동을 함께 둔 점이다. 실질금리가 높은 고금리는 더 보수적으로 취급한다. 물가 기대가 섞인 고금리와의 구별로 읽을 수 '
         '있지만, 재정 불신이나 통화 불신을 직접 측정한 신호는 아니다.'),
 'SLV': ('금보다 강하게 반응하되, 강달러에 크게 제동을 건다',
         '귀금속이라는 공통점보다 금과 다른 조건의 조합이 중요하다.',
         '10년 금리 >4에 +7.5, 변동성지수 >22에 +5.0. 반면 달러지수 >101에는 −9.0으로 큰 감점이 붙는다.',
         '변동성이 커졌다는 이유만으로 은을 선호하지 않도록 달러 조건이 견제한다. 금에는 가점이 붙을 수 있는 달러 구간이 은에는 강한 역풍으로 취급된다. 산업 수요와 '
         '금융 여건의 차이라는 설명은 가능하지만, 달러 강세가 곧 수요 감소라는 뜻은 아니다.'),
 'COPX': ('구리의 낙관보다 크게 눌린 광산주를 찾는다',
          '평온한 상승 추종보다 불안과 가격 조정에 무게를 둔다.',
          '변동성지수 >22에 +12.7, <16에 −5.8. 120일 이격률 <−30%에 +4.0인 반면 >35%에는 −3.0이다.',
          '불안이 높고 주가가 깊게 내려온 상황을 기회 후보로 읽는 역발상 구조다. 구리 수요가 좋아졌다는 확인과는 다르므로 경기 악화가 이어지면 너무 일찍 들어갈 수 '
          '있다. 높은 가점의 의미는 강한 선호이지 높은 성공 확률이 아니다.'),
 'SMH': ('성장 이야기에 더해 조정 이후의 기회를 찾는다',
         '반도체의 장기 성장성과 엔진의 매수 시점은 별개다.',
         '유가 <60에 +5.0, >85에 −5.3. 변동성지수 >22에 +2.6이며 자체 역배열과 삼중 신호에도 각각 +2.0이다.',
         '주가가 이미 강한 때만 선택하는 모형이 아니다. 약한 가격 배열에도 가점을 주므로 산업 성장 추종 안에 조정 매수 성격이 섞여 있다. 매출·주문 회복을 직접 '
         '확인하는 식이 아니어서 가격 반등 신호와 실적 회복을 구분해야 한다.'),
 'ITA': ('방산 전망보다 가격 조정과 금융 환경을 채점한다',
         '항공·방산 투자지만 전쟁 뉴스가 직접 매수 버튼은 아니다.',
         '10년 금리 >4에 +2.6, 1개월 수익률 <−3%에 +2.3, 변동성지수 >22에 +1.9. 유가 >85에는 −2.4다.',
         '방산이라는 산업 특성 위에 금리와 조정 매수 조건을 얹은 설계다. 전쟁이나 국방 예산을 직접 입력받지 않으므로 지정학적 긴장이 커졌다는 이유만으로 점수가 '
         '좋아지지는 않는다. 업종 전망과 실제 채점 경로를 구분해서 읽는 것이 핵심이다.'),
 'NLR': ('원자력 기대를 여러 거시 조건으로 걸러낸다',
         '산업의 장기 기대보다 당장의 조건 조합을 본다.',
         '10년 금리 >4에 +2.6, 유가 <70과 달러지수 >101에 각각 +2.0. 유가 >85에는 −4.0이다.',
         '한 가지 원자력 뉴스보다 여러 환경이 함께 유리한지를 보는 설계로 읽힌다. 다만 특정 개수의 조건을 필수로 요구하지는 않는다. 금리와 저유가 가점만으로도 '
         '4.6점이므로 “세 조건이 맞아야 한다”는 설명은 실제 식과 다르다.'),
 'PAVE': ('인프라의 장기 수요보다 단기 공포와 조정을 포착한다',
          '장기 투자 주제를 가격 조정 구간에서 접근하는 성격이다.',
          '변동성지수 >22에 +6.9, 3개월 수익률 <−5%에 +6.7. 반대로 변동성지수 <16에는 −4.3이다.',
          '평온한 시장에서 계속 따라가기보다 불안이 커지거나 가격이 내려온 때에 관심을 높이는 구조다. 두 큰 가점은 반드시 동시에 필요하지 않다. 인프라 지출이나 '
          '수주 증가를 직접 확인한 매수로 해석하면 실제 신호보다 의미를 넓히게 된다.'),
 'QQQM': ('불안이 낮고 상승이 이어질 때 추세에 합류한다',
          '조정 매수형 종목들과 구별되는 상승 지속형이다.',
          '변동성지수 <16과 3개월 수익률 >5%를 함께 요구하며, 충족하면 고정 3.5점을 준다.',
          '불안이 잦아들고 상승이 이미 확인된 구간을 고른다. 바닥을 먼저 맞히기보다 추세가 이어지는 쪽을 택하는 셈이다. 급락 직후에는 가격이 싸더라도 조건이 맞지 '
          '않을 수 있고, 급반등 초반을 놓치는 대신 확인을 기다리는 성격이다.'),
 'PDBC': ('원자재라는 이름보다 실제 가격의 힘을 산다',
          '인플레이션 방어라는 명분보다 자체 상승 신호가 중심이다.',
          '40일 수익률 신호가 먼저 필요하다. 그 뒤 표준점수의 초과분에 비례해 점수를 늘리고 높은 상대변동성 신호에 +1.0을 더한다.',
          '상승이 강해질수록 선호도도 연속적으로 커지는 추세 설계다. “물가가 오르니 원자재를 산다”보다 실제 원자재 가격의 반응을 따른다. 다만 유가와 상대변동성 '
          '회피 조건도 쓰므로 거시 환경을 전혀 보지 않는 전략은 아니다.'),
 'XLU': ('방어주에서도 금리 부담과 가격 조정을 기회로 읽는다',
         '방어 업종이라는 이유만으로 상시 보유하는 방식은 아니다.',
         '10년 금리 >4에 +1.2, 30년 금리 >4.71에 +1.5, 1개월 수익률 <−3%에 +1.3을 준다.',
         '고금리와 가격 조정 구간을 후보로 보는 역발상 성격이 있다. 고금리가 유틸리티에 이롭다는 주장과는 다르다. 금리 가점만으로도 선택될 수 있어 단기 급락이 '
         '필수는 아니며, 금리 부담이 오래 지속될 때의 위험은 남는다.'),
 'XLF': ('금융주는 고금리보다 완화된 부담에 가점을 준다',
         '금리 상승이 금융주에 좋다는 단순 설명과 채점 방향이 다르다.',
         '실질금리 <0에 +3.6, 유가 <60에 +3.5, 10년 금리 <2.5에 +2.3. 유가 >85에는 −3.1이다.',
         '금리 수준 상승보다 실질금리와 에너지 부담이 낮은 조합을 선호한다. 자금 조달과 경기 부담 완화라는 해석은 가능하지만, 은행의 순이자마진이나 대손비용을 직접 '
         '측정하는 모형은 아니다. 저금리 가점을 이익 증가의 확인으로 읽지 않는다.'),
 'XLV': ('헬스케어의 방어성에 금융여건과 가격 조건을 더한다',
         '경기 불안만으로 매수하는 방어주 모형은 아니다.',
         '실질금리 <0에 +2.2, 금융여건지수 <−0.5에 +1.5, 3개월 수익률 <−5%에 +1.3을 준다.',
         '금융 부담이 낮은 환경과 가격 조정을 함께 평가한다. 불황 여부 하나로 종목을 고르기보다 업종 안으로 들어갈 조건을 찾는 구조다. 구매관리자지수 <48 항의 '
         '감점은 0이므로 이를 강한 경기침체 회피 신호로 설명하면 안 된다.'),
 'IWM': ('소형주의 회복을 기다리기보다 불안과 낙폭에 반응한다',
         '경기 민감 자산을 가격 조정 구간에서 평가한다.',
         '변동성지수 >22에 +3.8, 3개월 수익률 <−5%에 +3.1, 유가 <60에 +3.0. 유가 >85에는 −2.5다.',
         '시장이 편안할 때보다 불안과 낙폭이 커진 때에 가점이 모이는 조정 매수형이다. 낮은 유가는 추가 조건이지만 소형기업의 이익이나 차입 여건이 회복됐다는 확인은 '
         '아니다. 회복을 앞서 잡을 여지와 하락을 일찍 받을 위험이 함께 있다.'),
 'VEA': ('해외 선진국 주식의 조정을 유가와 금융 환경으로 평가한다',
         '지역 분산을 넘어 선택 시점에 거시 조건을 적용한다.',
         '변동성지수 >22에 +3.0, 유가 <60에 +2.8, >85에 −3.4. 낮은 5년 금리와 채권 변동성에도 가점이 있다.',
         '저유가와 시장 불안의 조합에서 선호도가 높아지는 구조다. 해외 선진국 전체의 실적 전망이 좋아졌음을 확인하는 방식은 아니다. 지역별 경기 차이보다 공통 금융 '
         '환경에 크게 반응하므로 분산 효과와 매수 타이밍의 근거를 구분해서 본다.'),
 'EWZ': ('브라질의 경기 기대에 불안과 신용 조건을 결합한다',
         '완만한 경기 위축 구간에 가점을 주지만 그 구간만 매수하지는 않는다.',
         '구매관리자지수 48 이상·50 미만에 +5.0, 변동성지수 >22에 +7.1. 고수익·투자등급 신용스프레드 차이 ≥5.5에도 +1.5다.',
         '경기가 약해지고 위험 회피가 커진 상황을 기회 후보로 보는 성격이다. 구매관리자지수가 48 아래로 내려가면 그 가점은 없어지지만 다른 조건으로 선택될 수 '
         '있다. 따라서 “둔화는 사고 침체는 피한다”는 단정은 정확하지 않다.'),
 'VNM': ('베트남에는 자체 추세와 실질금리 조건을 함께 요구한다',
         '다른 신흥국과 달리 실질금리에 별도 하한을 둔다.',
         '실질금리 ≥1이 필요하고, >2이면서 자체 정배열이면 해당 가점이 +2.0에서 +4.0으로 커진다.',
         '낮은 실질금리를 선호하는 다른 종목과 달리 일정 수준 이상의 실질금리에서 자체 추세를 확인하는 구조다. 이를 베트남 경제가 고금리 덕분에 좋아진다는 인과로 '
         '해석할 수는 없다. 국가별 예외 규칙인 만큼 여러 독립 구간에서의 재현성이 중요하다.'),
 'INDA': ('인도의 성장 이야기보다 조정 폭에 먼저 반응한다',
          '장기 성장 기대를 직접 입력하지 않는 조정 매수형이다.',
          '3개월 수익률 <−5%에 +4.3, 변동성지수 >22에 +3.9. 달러지수 >101과 샴 경기침체 지표 >2.4에도 가점이 있다.',
          '최근 가격이 약해지고 시장 불안이 커진 때에 선호도가 높아진다. 강달러나 미국 침체가 인도에 이롭다는 결론이 아니라, 그런 환경에서 나타난 매수 후보를 '
          '포착하는 조건이다. 장기 성장 전망과 단기 신호의 근거를 혼동하지 않는 것이 중요하다.'),
 'CQQQ': ('중국 기술주의 가격 기회에 금융여건 전환을 더한다',
          '저유가·불안 구간과 금융여건 변화가 함께 작용한다.',
          '유가 <60에 +5.9, 변동성지수 >22에 +5.0. 달러지수 >95와 샴 지표 >0.3의 결합에 +4.0, 활성화된 금융여건 고점 하락 신호에 '
          '+3.0이다.',
          '정책 기대만으로 중국 기술주를 사는 구조는 아니다. 기존 거시 가점 위에 금융여건이 정점에서 완화되는 신호를 더한다. 전환 포착이라는 해석은 가능하지만 중국 '
          '정책 자체를 측정하지 않으며, 달러 조건을 약달러 선호로 뒤집어 읽어서는 안 된다.'),
 'CIBR': ('보안 산업의 성장보다 조정과 약달러를 진입 기회로 본다',
          '장기 수요가 있는 산업도 매수 시점은 별도로 고른다.',
          '1개월 수익률 <−3%에 +3.9, 변동성지수 >22에 +3.5, 달러지수 <93에 +3.3. 유가 >85에는 −6.0이다.',
          '단기 조정과 약달러가 겹칠 때 기회가 커지는 설계다. 보안 사고나 기업의 보안 지출 증가를 직접 확인하는 식은 아니다. 성장 산업이라는 이유만으로 계속 '
          '따라가기보다 가격과 거시 환경을 기다리는 성격으로 읽는 편이 정확하다.')}


# 🆕 v9.2.42 (S288): 하드 게이트 줄 — 엔진 TICKER_SPEC['gate'] 단일 원천에서 기계 산출.
#   사고 배경: Crown 102 로 TLT 진입 게이트(DXY>100)가 신설되었으나 손으로 쓴 매수 논리
#   본문은 그대로여서 게이트 1건이 누락된 채 서빙될 뻔했다(Commander 적발). 산문은 사람이
#   쓰되 **게이트만은 코드에서 뽑는다** — 엔진이 바뀌면 문구가 자동으로 따라간다.
_GATE_LABEL = {
    "wti90":            "WTI>90 진입 차단",
    "wti100":           "WTI>100 진입 차단",
    "wti_xle110":       "WTI>110 진입 차단(XLE 전용 임계)",
    "wti90_t10yie25":   "WTI>90 ∩ T10YIE>2.5 진입 차단",
    "oashy7":           "OAS_HY>7% 진입 차단(신용위기)",
    "dxy100":           "DXY>100 진입 차단(Crown 102)",
    "dfii1_hard":       "DFII10<1 진입 차단",
    "bull_only":        "MA 정배열에서만 진입",
}

def _gate_line(tk):
    """TICKER_SPEC gate 문자열 → 사람이 읽는 하드 게이트 목록. 미등재 토큰은 원문 노출(날조 0)."""
    spec = _ENGINE_TICKER_SPEC.get(tk) or {}
    raw = str(spec.get("gate", "") or "")
    if not raw:
        return ""
    out = []
    for part in raw.replace("+", "|").split("|"):
        t = part.strip()
        if not t:
            continue
        note = ""
        if "(" in t:                      # 예: "wti100(셧다운 면제)"
            t, _, note = t.partition("(")
            note = " (" + note.rstrip(")") + ")"
        label = "변동성지수 16 미만과 3개월 수익률 5% 초과" if tk == "QQQM" and t.strip() == "bull_only" else _GATE_LABEL.get(t.strip(), t.strip())
        out.append(label + note)
    return " · ".join(out)


# 🆕 v9.2.46 (S288, Commander 지시) — 21종 성격 한 줄 정의 (표시 전용)
#  출처: claude_ARGUS_21TICKER_CHARACTER_S288.md — 엔진 채점식 직접 추출 +
#        19년 에피소드 838건 + SPY 상관 + era 분리 금리민감도 + VIX 국면 선행수익.
#  형식: (축, 한 줄 정의, 근거 수치). '해석'이며 엔진 의도 진술이 아니다.
TICKER_CHARACTER = {'GLD': {'role': '금 관련 자산 · 금리와 달러 조건의 결합',
         'threshold': 1.5,
         'rules': ['미국 10년 명목금리 >4.1: +6.4. 단, 10년 실질금리 ≥2이면 +1.5로 감등. 앞 조건 불충족 시 명목금리 >3.5: +3.0.',
                   '달러지수 >110: 달러 가점 0. 그 외 >101: +2.6. 유가 >85: −3.5.',
                   '투자등급 신용스프레드 <0.89: +2.0. 미국 30년 금리 >4.71: +1.5. 금은비 표준점수 >1: −3.0.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'SLV': {'role': '은 관련 자산 · 금과 다른 달러 민감 조건',
         'threshold': 3,
         'rules': ['미국 10년 금리 >4: +7.5, 그 외 >3.5: +4.0. 주식 변동성지수 >22: +5.0, 그 외 >18: +2.0.',
                   '10년 실질금리 <0: −3.5. 투자등급 신용스프레드 <0.89: +2.0. 30년 금리 >4.71: +1.5.',
                   '달러지수 >101: −9.0. 달러지수 <95 및 10년 기대인플레이션 >2: +1.5. 달러지수 ≥99 및 <101이며 10년 금리 >4: +1.5. 금은비 '
                   '표준점수 >1: +1.0.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'XLE': {'role': '에너지 주식 · 유가와 자체 추세를 함께 평가',
         'threshold': 2,
         'rules': ['10년 실질금리 <0: 기본 +5.2에 금융여건 상·하위 상태별 1.2배·0.8배 조정. 그 외 실질금리 <1: +2.0.',
                   '주식 변동성지수 >22: +4.3. 1개월 수익률 <−5%: +2.1. 30년 금리 >4.71: +1.5.',
                   '유가 >85일 때 자체 정배열 +2.4, 역배열 −2.4, 둘 다 아니면 0. 변동성지수 <16: 기본 −3.3에 달러 상·하위 상태별 1.5배·0.5배 '
                   '조정.'],
         'limits': '전용 이력 게이트: 열린 상태에서 유가 >110이면 차단, 차단 상태에서 ≤109이면 해제. 유가 결측 시 직전 게이트 상태를 유지한다.'},
 'TLT': {'role': '장기 국채 · 금리 조건과 인플레이션 제한',
         'threshold': 1.5,
         'rules': ['10년 금리 >4: +1.5, 그 외 >3.5: +0.8. 유가 >70 및 <90: +1.1. 달러지수 <95: +0.9.',
                   '10년 실질금리 <0: −3.0. 유가 >90이고 10년 기대인플레이션 ≤2.5로 확인되면 +2.0.',
                   '가감 후 점수 >1.5로 진입 자격을 먼저 판정한다. 자격 충족 및 유가 >90이면 반환 점수를 1.3배 한다. 이 배율이 진입 전 미달 점수를 구제하지 '
                   '않는다.'],
         'limits': '달러지수 >100이면 차단. 유가 >90 및 10년 기대인플레이션 >2.5이면 차단. 기대인플레이션 결측은 해당 유가 가점의 근거가 되지 않는다.'},
 'ITA': {'role': '항공·방산 주식 · 금리와 가격 조정 조건',
         'threshold': 1.5,
         'rules': ['10년 금리 >4: +2.6. 1개월 수익률 <−3%: +2.3. 주식 변동성지수 >22: +1.9.',
                   '유가 >85: −2.4. 30년 금리 >4.71: +1.5. 달러지수 <95 및 10년 기대인플레이션 <2: +1.5.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'SMH': {'role': '반도체 주식 · 거시 조건과 자체 가격 상태',
         'threshold': 3,
         'rules': ['유가 <60: +5.0, 그 외 <70: +2.0. 달러지수 >101: +3.3. 주식 변동성지수 >22: +2.6. 유가 >85: −5.3.',
                   '자체 역배열 신호: +2.0. 엔진의 삼중 신호가 1이면 +2.0. 단순한 상승 추세만을 요구하는 진입식이 아니다.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'COPX': {'role': '구리 광산 주식 · 변동성과 가격 이격 조건',
          'threshold': 5,
          'rules': ['주식 변동성지수 >22: +12.7, 그 외 >18: +5.0. 유가 <60: +6.4, 그 외 <70: +2.0.',
                    '유가 >85: −7.7. 주식 변동성지수 <16: −5.8. 샴 경기침체 지표 >2.4: +2.0. 10년 금리 <2: +2.0.',
                    '120일 가격 이격률 <−30%: +4.0, 그 외 <−25%: +1.5, 그 외 >35%: −3.0. 침체 가점과 깊은 하락 가점의 표본 집중을 별도 '
                    '검토해야 한다.'],
          'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'NLR': {'role': '원자력 관련 주식 · 여러 거시 가점의 합산',
         'threshold': 4.5,
         'rules': ['10년 금리 >4: +2.6. 주식 변동성지수 >22: +1.9. 유가 <70: +2.0. 달러지수 >101: +2.0. 유가 >85: −4.0.',
                   '10년 금리와 저유가 조건만으로도 4.6점이다. 세 조건 이상이 반드시 필요하지 않으며, 4.5점과 같으면 미충족이다.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'EWZ': {'role': '브라질 주식 · 경기 지표와 변동성 결합',
         'threshold': 5,
         'rules': ['구매관리자지수 <48: 해당 가점 0. ≥48 및 <50: +5.0. 주식 변동성지수 >22: +7.1.',
                   '유가 <60: +4.3, 그 외 <70: +1.5. 30년 금리 >4.71: +1.5. 고수익채권과 투자등급 신용스프레드 차이 ≥5.5: +1.5.',
                   '구매관리자지수가 48 미만이어도 다른 가점으로 진입할 수 있다. 이 한 항만으로 경기침체 진입 금지라고 해석하지 않는다.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'QQQM': {'role': '나스닥 100 주식 · 낮은 변동성과 상승 지속',
          'threshold': 1.5,
          'rules': ['주식 변동성지수 <16이고 3개월 수익률 >5%여야 한다. 둘 중 하나라도 미충족 또는 결측이면 진입 불가.',
                    '두 조건과 공통 제한을 통과하면 고정 3.5점이다. 다른 종목처럼 여러 가점을 계속 합산하는 구조가 아니다.'],
          'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'VEA': {'role': '미국 외 선진국 주식 · 유가·변동성·금리 조합',
         'threshold': 2,
         'rules': ['주식 변동성지수 >22: +3.0. 유가 <60: +2.8, 그 외 <70: +1.0. 유가 >85: −3.4.',
                   '미국 5년 금리 <0.77: +1.5. 채권 변동성지수 <52.38: +1.0. 미국 30년 금리 >4.71: +1.0.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'PDBC': {'role': '원자재 선물 관련 자산 · 자체 수익률 신호',
          'threshold': 2.5,
          'rules': ['유가가 결측이거나 >100이면 진입 차단. 20일 상대변동성 회피 신호가 켜져도 차단. 40일 수익률 진입 신호가 반드시 필요하다.',
                    '통과 후 점수 = 4.0 + 2.0 × max(40일 수익률 표준점수 −1.645, 0). 높은 상대변동성 신호가 켜지면 +1.0.',
                    '1.645는 연속 점수의 초과분 기준이며 40일 수익률 진입 신호 자체와 동일하지 않다. 상대변동성을 거래량으로 설명하지 않는다.'],
          'limits': '공통 게이트 대신 위 유가·상대변동성·40일 수익률 신호 제한을 사용한다.'},
 'XLU': {'role': '유틸리티 주식 · 금리와 단기 가격 조정',
         'threshold': 1,
         'rules': ['1개월 수익률 <−3%: +1.3, 그 외 <0%: +0.5. 10년 금리 >4: +1.2. 30년 금리 >4.71: +1.5.',
                   '1개월 수익률 >3% 항의 감점은 현재 0이다. 고금리와 단기 하락의 동시 충족을 필수로 요구하지 않는다.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다. 추가로 유가 >90 또는 '
                   '고수익채권 신용스프레드 >7이면 차단.'},
 'XLF': {'role': '금융 주식 · 낮은 실질금리와 저유가 조건',
         'threshold': 2,
         'rules': ['10년 실질금리 <0: +3.6, 그 외 <0.5: +1.5. 유가 <60: +3.5, 그 외 <70: +1.5.',
                   '10년 금리 <2.5: +2.3. 유가 >85: −3.1. 5년 금리 <0.77: +1.5. 채권 변동성지수 <52.38: +1.5.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다. 추가로 고수익채권 '
                   '신용스프레드 >7이면 차단.'},
 'XLV': {'role': '헬스케어 주식 · 금융여건과 가격 조정',
         'threshold': 1.5,
         'rules': ['10년 실질금리 <0: +2.2, 그 외 <0.5: +1.0. 금융여건지수 <−0.5: +1.5, 그 외 <0: +0.8.',
                   '3개월 수익률 <−5%: +1.3. 10년 금리 <2.5: +1.1. 구매관리자지수 <48 감점은 현재 0이다.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'IWM': {'role': '미국 소형주 · 변동성과 중기 하락 조건',
         'threshold': 2,
         'rules': ['주식 변동성지수 >22: +3.8, 그 외 >18: +1.5. 3개월 수익률 <−5%: +3.1.',
                   '유가 <60: +3.0, 그 외 <70: +1.0. 유가 >85: −2.5. 채권 변동성지수 <52.38: +1.5. 5년 금리 <0.77: +1.5.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'PAVE': {'role': '미국 인프라 관련 주식 · 변동성과 가격 조정',
          'threshold': 4.5,
          'rules': ['주식 변동성지수 >22: +6.9, 그 외 >18: +3.0. 3개월 수익률 <−5%: +6.7.',
                    '유가 ≥60 및 <70: +1.5. 주식 변동성지수 <16: −4.3. 달러지수 <95 및 10년 기대인플레이션 <2: +3.0.',
                    '큰 가점 하나로도 문턱을 넘을 수 있지만 감점과 공통 제한이 함께 적용된다. 단일 가점만 보고 최종 자격을 확정하지 않는다.'],
          'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'VNM': {'role': '베트남 주식 · 실질금리 수준과 자체 추세',
         'threshold': 3,
         'rules': ['10년 실질금리 결측 또는 <1이면 차단. 통과 후 기본 +2.0. 실질금리 >2이고 자체 정배열이면 이 항을 +4.0으로 대체.',
                   '10년 금리 >4: 해당 가점 0, 그 외 >3.5: +1.5. 유가 <60: +1.5, 그 외 <70: +0.8. 유가 >85: −2.0.',
                   '채권 변동성지수 <52.38: +1.0. 샴 경기침체 지표 >2.4: +1.5. 실질금리의 상승 속도가 아닌 수준 조건이다.'],
         'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다. 추가로 10년 실질금리 '
                   '결측 또는 <1이면 차단.'},
 'INDA': {'role': '인도 주식 · 중기 하락과 거시 가점',
          'threshold': 3,
          'rules': ['3개월 수익률 <−5%: +4.3, 그 외 <0%: +1.5. 주식 변동성지수 >22: +3.9.',
                    '달러지수 >101: +1.8. 샴 경기침체 지표 >2.4: +2.0. 주식 변동성지수 <16 감점은 현재 0이다.'],
          'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'CQQQ': {'role': '중국 기술주 · 저유가와 금융여건 전환',
          'threshold': 4.5,
          'rules': ['유가 <60: +5.9, 그 외 <70: +2.0. 주식 변동성지수 >22: +5.0. ≥16 및 ≤22: −2.3. 10년 금리 >4 가점은 현재 0이다.',
                    '달러지수 >95 및 샴 경기침체 지표 >0.3: +4.0. 달러지수 <95 조건으로 뒤집어 설명하지 않는다.',
                    '금융여건 고점 하락 기능이 활성화되어 있고 해당 신호 >0.5이면 +3.0. 이 신호의 사전 계산과 사용 설정이 필요하다.'],
          'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'},
 'CIBR': {'role': '사이버보안 주식 · 단기 조정과 약달러 조건',
          'threshold': 3.5,
          'rules': ['1개월 수익률 <−3%: +3.9, 그 외 <0%: +1.0. 주식 변동성지수 >22: +3.5.',
                    '달러지수 <93: +3.3. 유가 >85: −6.0. 산업 성장 전망을 직접 계량한 식이 아니라 이 조건들의 합산이다.'],
          'limits': '공통 유가·주식 변동성 제한과 그 이력 상태를 먼저 적용한다. 공급 구간 예외도 있어 당일 유가 하나만으로 통과를 추정하지 않는다.'}}


def _watch_candidates(scored, portfolio, max_slots=5, lo=0.80, cap=5):
    """🆕 v9.2.46: 후보 감시 종목 — 미보유 중 컷오프 대비 lo 배 이상(진입 자격 + 진입 근접).

    render_slot_proximity 와 **동일한 ratio·컷오프 정의**를 쓴다(두 카드의 서열 불일치 차단).
    빈 슬롯(컷오프 0)이면 ratio>0 미보유 전원이 후보다.
    """
    held = set(portfolio.keys()) if portfolio else set()
    cands = []
    for it in (scored or []):
        th = it.get('thresh') or 0
        if th <= 0:
            continue
        r = (it.get('eff_total') or 0) / th
        if r > 0:
            cands.append((it['tk'], r, it.get('blocked', False)))
    cands.sort(key=lambda x: -x[1])
    cutoff = cands[max_slots - 1][1] if len(cands) >= max_slots else 0.0
    out = []
    for tk, r, blk in cands:
        if tk in held:
            continue
        rc = (r / cutoff) if cutoff > 0 else None
        if rc is None or rc >= lo:
            out.append((tk, r, cutoff, rc, blk))
    return out[:cap]


EXIT_RATIONALE = {'XLE': '유가 >110 또는 변동성지수 >35에서는 전량 청산한다. 만기만 도달한 경우에는 자체 정배열이고 진입 가능한 다른 미보유 후보가 없으면 연장한다. 추세가 살아 있는 '
        '에너지를 만기만으로 버리지 않되 위험 청산은 우선한다.',
 'TLT': '유가 >90과 기대인플레이션 >2.6이 겹치면 전량 청산한다. 진입 제한 2.5와 청산 2.6 사이에는 여유 구간이 있다. 달러지수 >100은 먼저 절반 축소하며, 이미 '
        '반으로 줄인 뒤 다시 조건이 성립하면 잔여분을 청산한다.',
 'GLD': '유가 >90에서는 전량 청산하지만 주식 변동성 급등만으로는 청산하지 않는다. 주식시장 불안과 금의 보유 위험을 같은 신호로 취급하지 않는 구조다.',
 'SLV': '유가 청산 문턱은 기본 80이지만 달러지수 ≥99·<101에서는 95로 완화된다. 변동성지수 >40은 전량 청산, 10년 금리 >4.8은 먼저 절반 축소하고 반축소 '
        '상태에서 다시 성립하면 잔여분을 청산한다. 금리 상승 가점에도 과도한 금리에는 제동이 있다.',
 'COPX': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'SMH': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'ITA': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'NLR': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'PAVE': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'QQQM': '유가 >90 또는 변동성지수 >35에서는 전량 청산한다. 진입 때 요구한 변동성 <16을 벗어났다고 즉시 매도하는 것은 아니므로, 진입 확인과 보유 중 위험 한도가 '
         '다르다.',
 'PDBC': '유가 >100에서는 전량 청산하지만 주식 변동성지수만으로는 청산하지 않는다. 원자재의 자체 추세를 주식시장의 불안과 구분해 보유하는 구조다.',
 'XLU': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'XLF': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'XLV': '유가 >90 또는 변동성지수 >45에서는 전량 청산한다. 다수 주식 종목의 변동성 문턱 35보다 여유가 있어 시장 불안을 더 견디도록 설계되어 있다.',
 'IWM': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'VEA': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'EWZ': '유가 >90 또는 변동성지수 >35이면 전량 청산한다. 달러지수 >105에서는 먼저 절반 축소하고 반축소 상태에서 다시 성립하면 잔여분을 청산한다. 경기 불안에 진입 '
        '가점을 주더라도 강달러 위험은 별도로 줄인다.',
 'VNM': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'INDA': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'CQQQ': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.',
 'CIBR': '유가 >90 또는 주식 변동성지수 >35에서는 전량 청산한다. 조정 매수의 기회로 보는 불안에도 보유를 중단하는 상한을 둔다.'}

def _rationale_block(tk, extra=""):
    """종목 설명은 성격·논리·해석에 집중하고 표의 현재 판정을 반복하지 않는다."""
    r = ENTRY_RATIONALE.get(tk)
    if not r:
        return None
    E = _html.escape
    head, character, structure, interpretation = r
    detail = TICKER_CHARACTER.get(tk, {})
    icons = {"GLD":"🥇", "SLV":"🥈", "XLE":"🛢️", "TLT":"📈",
             "ITA":"✈️", "SMH":"💻", "COPX":"⛏️", "NLR":"⚛️",
             "EWZ":"🇧🇷", "QQQM":"🚀", "VEA":"🌍", "PDBC":"📦",
             "XLU":"💡", "XLF":"🏦", "XLV":"🩺", "IWM":"🏭",
             "PAVE":"🏗️", "VNM":"🇻🇳", "INDA":"🇮🇳", "CQQQ":"🐉", "CIBR":"🛡️"}
    parts = ['<div style="margin:9px 0;padding-left:9px;border-left:2px solid #475569;line-height:1.6">',
             '<div style="color:#bfdbfe;font-weight:700">'+icons.get(tk, '📌')+' '+E(tk)+' — '+E(head)+extra+'</div>',
             '<div><span style="color:#c4b5fd;font-weight:700">🔎 성격</span> '+E(character)+'</div>',
             '<div><span style="color:#67e8f9;font-weight:700">🟢 매수 관점</span> '+E(structure)+'</div>',
             '<div><span style="color:#fda4af;font-weight:700">🔴 매도 관점</span> '+E(EXIT_RATIONALE.get(tk, '청산 설명 미확인'))+'</div>',
             '<div><span style="color:#fcd34d;font-weight:700">💬 설계 해석</span> '+E(interpretation)+'</div>',
             '</div>']
    return ''.join(parts)


def render_entry_rationale(portfolio, watch=None):
    """🆕 v9.2.36: 매수 논리 각주. v9.2.46: 성격 한 줄 + **후보 감시 종목까지 확장**.

    보유(슬롯 선정) 종목 + 후보 감시(미보유, 컷오프 0.80배 이상) 종목을 각각 렌더한다.
    사전 미등재 종목은 조용히 생략하지 않고 명시 표기(날조 0 원칙).
    모든 텍스트는 html.escape 처리 — 본문 부등호가 태그로 오인되는 사고를 원천 차단.
    """
    if not portfolio and not watch:
        return ""
    E = _html.escape
    parts = []
    missing = []
    if portfolio:
        parts.append('<div style="color:#93c5fd;font-weight:700;margin:6px 0 3px">'
                     '🧭 종목별 매수·매도 논리 (모형 목표 %d종)</div>' % len(portfolio))
        for tk in portfolio:
            b = _rationale_block(tk)
            if b is None:
                missing.append(tk)
            else:
                parts.append(b)
    if watch:
        parts.append('<div style="color:#93c5fd;font-weight:700;margin:9px 0 3px">'
                     '🔭 후보 감시 매수·매도 논리 (미보유 %d종) '
                     '<span style="font-weight:400;color:#475569">— 슬롯 컷오프 0.80배 이상</span></div>'
                     % len(watch))
        for tk, r, cutoff, rc, blk in watch:
            if rc is None:
                lbl = '빈 슬롯 · ratio %.2fx' % r
            elif rc >= 1.0:
                lbl = '슬롯 상대비율 충족 · ratio %.2fx (컷오프 %.2fx)' % (r, cutoff)
            else:
                lbl = '진입 근접 · ratio %.2fx (컷오프 %.2fx · 부족 %.0f%%)' % (r, cutoff, (1.0 - rc) * 100)
            if blk:
                lbl += ' · 🔒 Gate 차단'
            b = _rationale_block(tk, extra=' <span style="color:#4ade80;font-size:11px">[%s]</span>' % E(lbl))
            if b is None:
                missing.append(tk)
            else:
                parts.append(b)
    if missing:
        parts.append('<div style="color:#fb923c">· 매수 논리 미등재: %s '
                     '(신규 편입 종목 — 해설 사전 갱신 필요)</div>'
                     % E(", ".join(missing)))
    parts.append('<div style="color:#94a3b8;margin-top:5px">📎 공통 매도: 진입가 대비 손실 15% 초과 또는 적용 보유기간 만기에는 전량 청산합니다(XLE 만기 연장 예외). 전량 청산 조건이 부분 축소보다 우선합니다. 방어 오버레이·배분 조정에 따른 비중 감소는 종목 청산과 별개입니다.</div>')
    return "".join(parts)


# 포트폴리오 (HANDOFF 기준 — 엔진 BT에서 자동 추출 불가 시 fallback)
# 🔴 v9.2.19 fail-loud: 포트폴리오 stale fallback 폐지.
#   구 PORTFOLIO_FALLBACK={"TLT":45.5,"XLE":54.5}는 run_prima4 실패 시 옛 포트를 실측처럼
#   노출 → 제거. 실패 시 빈 {} 시드 → generate_html이 '데이터 없음' loud 배너 출력.

# ── AAQG (ARGUS Asset Quality Grade) — 19년 BT 실적 종합 등급 ──
# 핵심 기준 = Q = 평균 예상 수익률(E) 60% + 표본 신뢰도(R) 20% + 안정성(S) 20% (v4.1 · 152라인 D-7 각주 정합)
# 분기마다 aaqg_quarterly_update.py 실행 → AAQG_GRADES.csv 갱신 (분기 시그널 리뷰 §8 연동)
# 표시 전용 — 엔진 자본 가중(LEVEL_WEIGHT)과 분리
# 🔒 v9.2.34 (S284, Commander 지시): "local로 유지" — v9.2.33 게시 워크플로 방향을 철회하고
#   로컬 전용으로 확정. "모든 CSV argus-public-data 하드코딩"(v9.2.32)의 유일한 예외로 남긴다.
#   aaqg_quarterly_publish.yml 은 저장소 미반영 권고.
AAQG_PATH = os.path.join(SCRIPT_DIR, "AAQG_GRADES.csv")
AAQG_VER = "v4.1"
AAQG_ASOF_FALLBACK = "⚠️ 데이터 없음"   # 🔴 v9.2.19 fail-loud: 구 "2026-06-27" stale 제거
AAQG_NEXT_FALLBACK = "⚠️ 데이터 없음"   # 🔴 v9.2.19 fail-loud: 구 "2026-06-30(Q2)" stale 제거
# (tk, 등급, Q, E63d%, E1회당%, Pace, 역할군표시, 에피소드, era활성, 승률%, payoff, 태그, 라벨, 전분기대비)
AAQG_FALLBACK_ROWS = [
    ('COPX', 'S', 83.0, 14.1, 5.7, 'SS', 'Burst 1/6', 62, 5, 63, 2.02, 'Cyclical·Infra', '', '유지'),
    ('GLD', 'S', 76.0, 9.1, 5.7, 'S', 'Core 1/4', 21, 3, 81, 4.55, 'Alpha·Hedge', '⚠️GC', '↑'),
    ('EWZ', 'A', 74.5, 12.0, 5.1, 'SS', 'External 1/3', 83, 5, 66, 1.69, 'Cyclical·EM', '⚠️GC', '유지'),
    ('CIBR', 'A', 68.6, 9.4, 5.8, 'S', 'Growth 1/4', 10, 3, 80, 1.82, 'Growth·Cyber', '', '유지'),
    ('CQQQ', 'A', 69.6, 10.2, 5.4, 'SS', 'Growth 2/4', 52, 5, 69, 1.02, 'Growth·China', '', '유지'),
    ('XLE', 'A', 68.3, 9.1, 4.6, 'A', 'Core 2/4', 64, 5, 72, 1.12, 'Cyclical·Inflation', '', '유지'),
    ('VNM', 'C', 63.2, 8.6, 5.9, 'B', 'Burst 2/6', 4, 2, 75, 2.97, 'EM·Frontier', '표본', '유지'),
    ('SLV', 'A', 60.8, 15.8, 4.0, 'SS', 'Burst 3/6', 89, 3, 69, 1.19, 'Alpha·Metal', '⚠️GC', '↑'),
    ('ITA', 'B', 60.8, 8.7, 4.3, 'B', 'Core 3/4', 25, 4, 72, 4.85, 'Defense', '', '↓'),
    ('NLR', 'B', 54.7, 8.8, 5.4, 'B', 'Burst 4/6', 11, 1, 64, 1.58, 'Infra·Nuclear', '표본', '유지'),
    ('SMH', 'B', 53.7, 8.2, 4.6, 'C', 'Growth 3/4', 51, 4, 67, 1.37, 'Growth·Semi', '', '유지'),
    ('PAVE', 'B', 54.9, 9.0, 4.3, 'A', 'Core 4/4', 26, 3, 62, 1.58, 'Infra', '', '유지'),
    ('IWM', 'B', 47.1, 8.2, 2.6, 'B', 'Burst 5/6', 74, 5, 64, 1.59, 'SmallCap·Beta', '⚠️GC', '↑'),
    ('TLT', 'C', 40.2, 6.0, 3.6, 'C', 'Hedge 1/3', 28, 4, 36, 5.14, 'Hedge', '⚠️↓', '유지'),
    ('XLF', 'C', 39.0, 5.6, 2.2, 'C', 'Burst 6/6', 70, 4, 64, 1.68, 'Cyclical·Fin', '⚠️GC', '유지'),
    ('XLV', 'C', 34.0, 5.4, 1.4, 'C', 'Hedge 2/3', 85, 4, 68, 1.5, 'Defensive·Health', '⚠️GC', '유지'),
    ('VEA', 'C', 32.2, 7.8, 2.4, 'C', 'External 2/3', 20, 1, 50, 1.54, 'DM·Beta', '⚠️GC 표본', '유지'),
    ('XLU', 'C', 30.6, 6.9, 2.4, 'C', 'Hedge 3/3', 21, 4, 43, 2.45, 'Defensive·Utility', '⚠️GC', '유지'),
    ('QQQM', 'C', 26.6, 4.3, 1.4, 'C', 'Growth 4/4', 78, 5, 62, 1.45, 'Growth·Beta', '⚠️GC', '유지'),
    ('INDA', 'C', 18.9, 3.5, 2.2, 'C', 'External 3/3', 37, 3, 46, 1.34, 'EM·India', '⚠️GC ⚠️↓', '유지'),
]

def load_aaqg():
    """AAQG v4.1 로드 — AAQG_GRADES.csv 로컬 전용, 부재 시 내장 fallback.
    🔒 v9.2.34 (S284, Commander 지시): 로컬 유지 확정 — 원격 시도 없음.
    반환: (grades, rows, asof, nxt, marks) — marks=⚠️ 라벨 보유 종목"""
    def _mk(rows):
        return {t[0]: '⚠️' for t in rows if '⚠️' in str(t[12])}

    def _cat(rows):
        # 역할군 단어만 (예: 'Core 1/4' → 'Core')
        return {t[0]: str(t[6]).split()[0] for t in rows if len(t) > 6 and str(t[6]) not in ('—', 'nan', '')}
    try:
        a = pd.read_csv(AAQG_PATH)
        rows = []
        for _, r in a.iterrows():
            lab = str(r['라벨']) if str(r['라벨']) != 'nan' else ''
            cat = f"{r['역할군']} {int(r['군내순위'])}/{int(r['군N'])}"
            rows.append((r['tk'], r['등급'], round(float(r['Q종합']), 1),
                         round(float(r['E63d%']), 1), round(float(r['E1회당%']), 1),
                         str(r['Pace']), cat, int(r['n_ep']), int(r['era_a']),
                         int(r['승률%']), round(float(r['payoff']), 2),
                         str(r['태그']), lab, str(r['전분기대비'])))
        grades = {t[0]: t[1] for t in rows}
        asof = str(a['갱신일'].iloc[0]) if '갱신일' in a.columns else AAQG_ASOF_FALLBACK
        nxt = str(a['차기갱신'].iloc[0]) if '차기갱신' in a.columns else AAQG_NEXT_FALLBACK
        print(f"  AAQG {AAQG_VER}: CSV {len(grades)}종목 (평가 {asof})")
        return grades, rows, asof, nxt, _mk(rows), _cat(rows)
    except Exception:
        grades = {t[0]: t[1] for t in AAQG_FALLBACK_ROWS}
        print(f"  AAQG {AAQG_VER}: 내장 fallback {len(grades)}종목 (평가 {AAQG_ASOF_FALLBACK})")
        return grades, AAQG_FALLBACK_ROWS, AAQG_ASOF_FALLBACK, AAQG_NEXT_FALLBACK, _mk(AAQG_FALLBACK_ROWS), _cat(AAQG_FALLBACK_ROWS)

# 신호별 한국어 조건 설명
SIGNAL_CONDS = {
    # 🆕 [S281] PDBC 자기참조 (Crown #96 편입 / #97 셧다운 진입)
    "pdbc_roc40_1367": "PDBC 40일 모멘텀 13.67% 이상 (BT19년 q95 절대문턱)",
    "pdbc_rvol_hi": "PDBC 20일 실현변동성 26% 이상 (고변동 동반 가산)",
    "pdbc_rvol_lo": "PDBC 20일 실현변동성 10.29% 이하 (저변동 회피·하드차단)",
    # 금리
    "tnx4": "미국채 10년물 금리 4.0% 이상",
    "tnx41": "미국채 10년물 금리 4.1% 이상",
    "tnx35": "미국채 10년물 금리 3.5% 이상",
    "tnx40": "미국채 10년물 금리 4.0% 이상",
    "tnx_low25": "미국채 10년물 금리 2.5% 미만",
    "tnx_lt2": "미국채 10년물 금리 2.0% 미만 (COPX 부스트)",
    "tyx471": "미국채 30년물 금리 4.71% 이상",
    "fvx077": "미국채 5년물 금리 0.77% 미만",
    # VIX
    "vix22": "변동성 지수(VIX) 22 이상",
    "vix18": "변동성 지수(VIX) 18 이상",
    "vix16": "변동성 지수(VIX) 16 미만 (감산)",
    "vix16_22": "변동성 지수(VIX) 16~22 구간 (감산)",
    "vix_low": "변동성 지수(VIX) 16 미만",
    # WTI
    "wti60": "국제유가(WTI) 60달러 미만",
    "wti70": "국제유가(WTI) 70달러 미만",
    "wti_70": "국제유가(WTI) 70달러 미만",
    "wti85": "국제유가(WTI) 85달러 초과 (감산)",
    "wti_70_90": "국제유가(WTI) 70~90달러 구간",
    "wti90_disinf": "유가 90+ 디스인플레(T10YIE≤2.5)",
    # 달러
    "dxy95": "달러인덱스(DXY) 95 미만",
    "dxy93": "달러인덱스(DXY) 93 미만",
    "dxy101": "달러인덱스(DXY) 101 초과 (감산)",
    "dxy95_t10yie20h": "달러 95 미만 ∩ 기대인플레 2.0% 이상",
    "dxy95_t10yie20": "달러 95 미만 ∩ 기대인플레 2.0% 이상",
    "dxy95_sahm03": "달러 95 미만 ∩ 실업악화(SAHM<0.3)",
    # 실질금리
    "dfii0": "실질금리(DFII10) 0% 미만",
    "dfii05": "실질금리(DFII10) 0.5% 미만",
    "dfii1": "실질금리(DFII10) 1.0% 이상",
    "dfii2": "실질금리(DFII10) 2.0% 이상",
    # 모멘텀
    "m1_crash5": "1개월 수익률 -5% 미만 (급락)",
    "m1_drop3": "1개월 수익률 -3% 미만 (하락)",
    "m1_neg": "1개월 수익률 0% 미만 (약세)",
    "m1_rise3": "1개월 수익률 +3% 초과 (감산)",
    "m3_crash5": "3개월 수익률 -5% 미만 (급락)",
    "m3_neg": "3개월 수익률 0% 미만 (약세)",
    # 신용/매크로
    "oasig089": "투자등급 신용스프레드(OAS_IG) 0.89 미만",
    "nfci_neg05": "금융여건지수(NFCI) -0.5 미만 (완화적)",
    "nfci0": "금융여건지수(NFCI) 0 미만",
    "pmi48": "제조업PMI 48 미만 (위축)",
    "pmi50": "제조업PMI 50 미만 (위축 근접)",
    "sahm24": "실업악화지표(SAHM) 2.4 이상 (침체)",
    "move5238": "채권변동성(MOVE) 52.38 이상",
    # 편향/복합
    "dev120_n30": "120일 이격도 -30% 미만 (폭락)",
    "dev120_n25": "120일 이격도 -25% 미만 (급락)",
    "dev120_p35": "120일 이격도 +35% 초과 (과열)",
    "bullstack_wti85": "유가 85+ ∩ 강세 스택(BullStack)",
    "bearstack_wti85": "유가 85+ ∩ 약세 스택 (elif)",
    "bull_only": "VIX 16 미만 ∩ 3개월 +5% 이상 (강세장 전용)",
    # VNM
    "vnm_bull_dfii2": "실질금리 2%+ ∩ VNM 강세스택",
    # COPX
    "tnx_lt2_boost": "미국채 10년물 2.0% 미만 (COPX +2.0)",
}

# ── CSS ──
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Noto Sans KR', sans-serif; background: #0f172a; color: #e2e8f0; font-size: 10px; line-height: 1.5; padding: 16px; max-width: 900px; margin: 0 auto; word-break: keep-all; }
.hdr { display:flex; align-items:center; justify-content:space-between; padding:10px 14px; background:linear-gradient(135deg,#1e293b,#0f172a); border-radius:10px; margin-bottom:12px; border-left:4px solid #3b82f6; flex-wrap:wrap; }
.hdr > div { min-width:0; max-width:100%; overflow-wrap:anywhere; }
.hdr .bv { white-space:normal; overflow-wrap:anywhere; max-width:100%; }
.hdr h1 { font-size:18px; font-weight:900; }
.badge { display:inline-block; padding:3px 10px; border-radius:5px; font-weight:700; font-size:10px; }
.bb { background:#3b82f6; color:#fff; } .bv { background:#1e293b; color:#64748b; }
.g2 { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.g3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; }
.card { background:#1e293b; border-radius:10px; padding:12px 16px; margin-bottom:10px; }
.ct { font-size:13px; font-weight:700; margin-bottom:8px; color:#e2e8f0; }
.al { border-left:4px solid #334155; padding-left:14px; }
.hbox { padding:8px 12px; border-radius:8px; border:1.5px solid; margin-bottom:6px; }
.stat { text-align:center; padding:8px; }
.stat-val { font-size:28px; font-weight:900; line-height:1.1; }
.stat-lbl { font-size:10px; color:#64748b; }
table { width:100%; border-collapse:collapse; font-size:10px; }
th { text-align:left; color:#64748b; font-weight:500; padding:5px 8px; border-bottom:1px solid #334155; font-size:9px; }
td { padding:5px 8px; border-bottom:1px solid rgba(30,41,59,0.5); }
.td { background:#0f172a; border-radius:8px; overflow:auto; -webkit-overflow-scrolling:touch; }
.gb { display:inline-block; padding:2px 8px; border-radius:4px; font-weight:700; font-size:10px; }
.gb-S { border:1.5px solid #facc15; color:#facc15; }
.gb-A { border:1.5px solid #22d3ee; color:#22d3ee; }
.gb-B { border:1.5px solid #4ade80; color:#4ade80; }
.gb-C { border:1.5px solid #94a3b8; color:#94a3b8; }
.sr { display:flex; align-items:center; gap:5px; padding:3px 8px; border-radius:4px; margin-bottom:1.5px; font-size:10px; }
.sh { font-size:8px; color:#475569; }
.si { width:16px; text-align:center; flex-shrink:0; }
.sn { min-width:120px; font-weight:600; }
.sc { flex:1; color:#64748b; font-size:9px; }
.sv { min-width:110px; text-align:right; color:#94a3b8; font-size:9px; }
.sp { min-width:38px; text-align:right; font-weight:700; }
.su { min-width:32px; text-align:right; color:#475569; font-size:9px; }
.sig-met { background:rgba(34,197,94,0.08); }
.sig-met-neg { background:rgba(248,113,113,0.08); }
.sig-open { background:rgba(59,130,246,0.06); }
.ah { display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1.5px solid #334155; margin-bottom:8px; flex-wrap:wrap; }
.am { display:flex; gap:14px; font-size:10px; color:#94a3b8; margin-bottom:8px; }
.warn { font-size:9px; color:#fbbf24; padding:4px 8px; background:rgba(251,191,36,0.06); border-radius:4px; margin-bottom:6px; }
.footer { text-align:right; font-size:8px; color:#334155; margin-top:8px; }
.kv { display:grid; grid-template-columns:auto 1fr; gap:3px 12px; font-size:11px; }
.kv .k { color:#64748b; } .kv .v { font-weight:600; }
details { margin-bottom: 6px; }
details summary { cursor: pointer; font-weight: 700; font-size: 12px; padding: 6px; color: #94a3b8; }
details summary:hover { color: #e2e8f0; }
details[open] summary { color: #e2e8f0; }
@media (max-width: 600px) {
    .g2, .g3 { grid-template-columns: 1fr; }
    .stat-val { font-size: 22px; }
    body { padding: 8px; font-size: 9px; }
    th, td { white-space: nowrap; }
    .sr { flex-wrap: wrap; row-gap: 2px; }
    .sn { min-width: 0; flex: 1 1 auto; }
    .sv { min-width: 0; white-space: nowrap; }
    .sc { flex: 1 1 100%; order: 9; padding-left: 21px; }
}
"""


def V(macro, key):
    """매크로 값 포맷"""
    v = macro.get(key)
    return f"{v:.2f}" if v is not None and not np.isnan(v) else "N/A"


# 매크로 신호등 임계 (🟢 안전 / 🟡 경계 / 🟠 위험) — v9.2.0
# mode: 'hi'=높을수록 위험, 'lo'=낮을수록 위험, 'mid'=적정대 이탈 시 위험
_MACRO_BANDS = {
    'VIX':     ('hi', 20, 30),
    'WTI':     ('hi', 80, 90),
    'TNX':     ('hi', 4.0, 4.7),
    'TYX_30Y': ('hi', 4.3, 5.0),
    'DXY':     ('hi', 103, 107),
    'NFCI':    ('hi', -0.3, 0.0),
    'DFII10':  ('hi', 1.8, 2.3),
    'MOVE':    ('hi', 100, 130),
    'OAS_IG':  ('hi', 0.9, 1.3),
    'OAS_HY':  ('hi', 3.5, 5.0),
    'PMI':     ('lo', 52, 48),
    'T10YIE':  ('mid', 2.0, 2.5, 1.7, 2.8),  # 안전[2.0,2.5] / 경계[1.7,2.0)∪(2.5,2.8] / 위험<1.7 or >2.8
}
_BAND_COLOR = {'safe': '#4ade80', 'warn': '#facc15', 'danger': '#fb923c'}  # 🟢🟡🟠


def macro_band_color(key, macro):
    """매크로 원시값 → 신호등 색 hex (해당 없음/결측 시 None)"""
    spec = _MACRO_BANDS.get(key)
    v = macro.get(key)
    if spec is None or v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    mode = spec[0]
    if mode == 'hi':            # 높을수록 위험
        _, warn, dang = spec
        band = 'safe' if v < warn else ('warn' if v < dang else 'danger')
    elif mode == 'lo':          # 낮을수록 위험
        _, warn, dang = spec
        band = 'safe' if v > warn else ('warn' if v > dang else 'danger')
    else:                       # 'mid' 적정대 이탈
        _, lo_s, hi_s, lo_d, hi_d = spec
        if lo_s <= v <= hi_s:
            band = 'safe'
        elif lo_d <= v <= hi_d:
            band = 'warn'
        else:
            band = 'danger'
    return _BAND_COLOR[band]


def sig_row(typ, name, cond, cur, res, pts, cum):
    """신호 행 HTML"""
    cls = {"met":"sig-met","open":"sig-open","fail":"","elif":""}.get(res,"")
    if res == "met" and pts is not None and pts < 0:
        cls = "sig-met-neg"
    icon = {"met":"✅","open":"🔓","fail":"✗","elif":"⊘"}.get(res,"·")
    ncol = {"gate":"#60a5fa","easn":"#fb923c","elif":"#78716c","sub":"#78716c"}.get(typ,"#e2e8f0")
    if pts is None:
        pts_h = '<span style="color:#475569">—</span>'
    elif pts > 0:
        pts_h = f'<span style="color:#4ade80">+{pts}</span>'
    elif pts < 0:
        pts_h = f'<span style="color:#ff8a8a">{pts}</span>'
    else:
        pts_h = '<span style="color:#475569">0</span>'
    cum_h = f"{cum:.1f}" if cum is not None else ""
    return (f'<div class="sr {cls}"><span class="si">{icon}</span>'
            f'<span class="sn" style="color:{ncol}">{name}</span>'
            f'<span class="sc">{cond}</span><span class="sv">{cur}</span>'
            f'<span class="sp">{pts_h}</span><span class="su">{cum_h}</span></div>\n')


# 신호 키 → 매크로 키 매핑 (현재값 자동 조회용)
_SIG_MACRO_MAP = {
    "tnx4":"TNX", "tnx41":"TNX", "tnx35":"TNX", "tnx40":"TNX", "tnx_low25":"TNX", "tnx_lt2":"TNX",
    "tyx471":"TYX_30Y", "fvx077":"FVX_5Y",
    "vix22":"VIX", "vix18":"VIX", "vix16":"VIX", "vix16_22":"VIX", "vix_low":"VIX",
    "wti60":"WTI", "wti70":"WTI", "wti_70":"WTI", "wti85":"WTI", "wti_70_90":"WTI",
    "dxy95":"DXY", "dxy93":"DXY", "dxy101":"DXY",
    "dfii0":"DFII10", "dfii05":"DFII10", "dfii1":"DFII10", "dfii2":"DFII10",
    "oasig089":"OAS_IG", "nfci_neg05":"NFCI", "nfci0":"NFCI",
    "pmi48":"PMI", "pmi50":"PMI", "sahm24":"SAHMCURRENT", "move5238":"MOVE",
}
# 복합 신호: 2개 이상 매크로
_SIG_MACRO_MULTI = {
    "wti90_disinf": ["WTI","T10YIE"],
    "dxy95_t10yie20h": ["DXY","T10YIE"], "dxy95_t10yie20": ["DXY","T10YIE"],
    "dxy95_sahm03": ["DXY","SAHMCURRENT"],
    "vnm_bull_dfii2": ["DFII10"],
    "bullstack_wti85": ["WTI"], "bearstack_wti85": ["WTI"],
    "bull_only": ["VIX"],
    "tnx_lt2_boost": ["TNX"],
}
# 종목 자체 지표
_SIG_TICKER_KEY = {
    "m1_crash5":"m1_return_pct", "m1_drop3":"m1_return_pct", "m1_neg":"m1_return_pct", "m1_rise3":"m1_return_pct",
    "m3_crash5":"m3_return_pct", "m3_neg":"m3_return_pct",
    "dev120_n30":"dev120_pct", "dev120_n25":"dev120_pct", "dev120_p35":"dev120_pct",
}

def _macro_fallback(sig_key, macro, tk_info):
    """신호 키에서 매크로/종목 현재값 자동 추출"""
    # 단일 매크로
    if sig_key in _SIG_MACRO_MAP:
        mk = _SIG_MACRO_MAP[sig_key]
        mv = macro.get(mk)
        if mv is not None and not (isinstance(mv, float) and np.isnan(mv)):
            return f"{mk}={mv:.2f}"
    # 복합 매크로
    if sig_key in _SIG_MACRO_MULTI:
        parts = []
        for mk in _SIG_MACRO_MULTI[sig_key]:
            mv = macro.get(mk)
            if mv is not None and not (isinstance(mv, float) and np.isnan(mv)):
                parts.append(f"{mk}={mv:.2f}")
        if parts:
            return " · ".join(parts)
    # 종목 자체 지표 (1M, 3M, DEV120)
    if sig_key in _SIG_TICKER_KEY:
        tk_key = _SIG_TICKER_KEY[sig_key]
        tv = tk_info.get(tk_key)
        if tv is not None:
            label = {"m1_return_pct":"1M","m3_return_pct":"3M","dev120_pct":"DEV120"}.get(tk_key, tk_key)
            return f"{label}={tv:+.1f}%"
    return "—"


# 🆕 v9.1.2 (S219 carry #A/#B): elif 배타 억제 — engine SIGNAL_RULES 기반
#   동일 (매크로/모멘텀, 방향) 그룹 내 최강 active 1개만 cum 가산, 나머지 ⊘(미반영)
#   엔진 entry_* 구간변환(Δ=0)과 표시 정합 — GLD 12.9→9.9 / SLV 15.0→11.0 중복계상 차단
_ENGINE_SIG_RULES = {}  # main()에서 eng.SIGNAL_RULES 주입 (zero-drift)
_ENGINE_CONST = {'DS_K': 4.0, 'SOFT_SINGLE_W': 0.4, 'REBAL_FREQ': 5, 'MAX_POS': 5}  # 🆕 [S277] main()에서 eng.DS_K/SOFT_SINGLE_W 주입 (비중 안내 단일 원천)
_ENGINE_EXSN = {}  # 🆕 [S277 RiskBoard] eng.EXSN_WTI/EXSN_VIX 주입
_ENGINE_TICKER_SPEC = {}  # 🆕 v9.2.42 (S288) main()에서 eng.TICKER_SPEC 주입 (하드 게이트 단일 원천)
_CAPTURE_ROWS = []  # 🆕 v9.2.40: 21종 1Y 포착률 (main에서 주입 · 표시 전용)


def _compute_capture_1y(eng, df, bt):
    """21종 최근 1Y 포착률 — trade_log 일별 보유 재구성 (관측 전용).

    반환: [(ticker, 자산1Y%, 엔진포착%, 포착률%(None=자산수익 미미), 보유일비중%, 불참이득%p(None=산출불가))]

    🆕 v9.2.45 불참 이득 = 미보유 구간의 (포트폴리오 수익 − 그 종목 수익).
       양수 = 안 산 것이 이득(슬롯을 더 나은 곳에 썼다) · 음수 = 놓친 알파.
       포착률은 분모가 단순 보유라 기회비용을 담지 못한다 — 5슬롯 21종 구조에서
       "낮은 포착률"의 옳고 그름은 그 시간에 포트가 무엇을 벌었는지로만 갈린다(격언 #129).
    """
    import numpy as _np
    dates = pd.to_datetime(df['Date']).reset_index(drop=True)
    account = bt.get('daily_account')
    if not isinstance(account, list) or not account:
        raise ValueError('체결 후 일별 모의보유 기록 없음')
    by_date = {str(row['date'])[:10]: frozenset(t for t,w in row['actual_weights'].items() if w > 0)
               for row in account}
    # 가격 수익은 전일 종가 체결 후 보유 종목으로 측정한다.
    held_by_day = [by_date.get(str(day.date()), frozenset()) for day in dates]
    n1y = min(252, len(dates) - 1)
    # 🆕 v9.2.45: 포트폴리오 일별 수익 (기회비용 대조군). 길이 불일치 시 불참 이득 생략.
    _eq = bt.get('equity')
    _pr = None
    if _eq is not None and len(_eq) == len(dates):
        _pr = pd.Series(_np.asarray(_eq, dtype=float)).pct_change()
    rows = []
    for tk in getattr(eng, 'ALL_TICKERS', []):
        col = f'{tk}_Close' if f'{tk}_Close' in df.columns else (tk if tk in df.columns else None)
        if col is None:
            continue
        px = pd.to_numeric(df[col], errors='coerce').reset_index(drop=True)
        i0 = len(px) - 1 - n1y
        if i0 < 0 or not _np.isfinite(px.iloc[i0]) or px.iloc[i0] <= 0:
            continue
        asset = (px.iloc[-1] / px.iloc[i0] - 1) * 100
        r = px.pct_change()
        cap_log = 0.0; hd = 0
        for i in range(i0 + 1, len(px)):
            if tk in held_by_day[i - 1] and _np.isfinite(r.iloc[i]):
                cap_log += _np.log1p(r.iloc[i]); hd += 1
        captured = (_np.expm1(cap_log)) * 100
        ratio = (captured / asset * 100) if abs(asset) >= 5.0 else None
        # 🆕 v9.2.45: 미보유 구간 기회비용 — 같은 날짜 집합에서 포트 수익 vs 종목 수익
        gap = None
        if _pr is not None:
            _a_log = 0.0; _p_log = 0.0; _n_out = 0
            for i in range(i0 + 1, len(px)):
                if tk in held_by_day[i - 1]:
                    continue
                _ri, _rp = r.iloc[i], _pr.iloc[i]
                if _np.isfinite(_ri) and _np.isfinite(_rp):
                    _a_log += _np.log1p(_ri); _p_log += _np.log1p(_rp); _n_out += 1
            if _n_out > 0:
                gap = (_np.expm1(_p_log) - _np.expm1(_a_log)) * 100
        rows.append((tk, round(asset, 2), round(captured, 2),
                     (round(ratio, 1) if ratio is not None else None),
                     round(hd / max(n1y, 1) * 100, 1),
                     (round(gap, 1) if gap is not None else None)))
    rows.sort(key=lambda x: -x[1])
    # 🛡️ v9.2.43 축퇴 가드 (fail-loud): 보유일 비중이 전 종목 0% 또는 100% 로만 나오면
    #   재구성이 무너진 것이다(날짜축 불일치 등). 틀린 숫자를 서빙하느니 카드를 접는다.
    _hd_set = {r[4] for r in rows}
    if rows and _hd_set.issubset({0.0, 100.0}):
        print("  ⚠️ 포착률 계기판 억제 — 보유일 재구성 축퇴(전 종목 0%/100%): trade_log 날짜축 불일치 의심")
        return []
    return rows


def render_capture_gauge():
    """🆕 v9.2.40: 21종 1Y 포착률 계기판 — 표시 전용 카드."""
    if not _CAPTURE_ROWS:
        return ""
    h = '<div class="card"><div class="card-header">📡 포착률 계기판 <span style="font-size:.75em;color:#64748b">최근 1년 · 자산 자체 수익 vs 엔진 실현(보유 구간 곱연결) · 표시 전용</span></div>'
    h += '<div class="card-body" style="font-size:.85em">'
    h += '<table style="width:100%;border-collapse:collapse"><tr style="color:#64748b;text-align:right">'
    h += ('<th style="text-align:left">종목</th><th>자산 1Y</th><th>엔진 포착</th>'
          '<th>포착률</th><th>보유일</th><th>불참 이득</th></tr>')
    for tk, asset, cap, ratio, hd, gap in _CAPTURE_ROWS:
        if ratio is None:
            rtxt, clr = '—', '#94a3b8'
        elif ratio < 20:
            rtxt, clr = f'{ratio:.0f}%', '#dc2626'
        elif ratio > 100:
            rtxt, clr = f'{ratio:.0f}%', '#16a34a'
        else:
            rtxt, clr = f'{ratio:.0f}%', '#334155'
        # 🆕 v9.2.45 불참 이득: 음수 = 놓친 알파(적색) · 양수 = 불참이 이득(녹색)
        if gap is None:
            gtxt, gclr = '—', '#94a3b8'
        elif gap < 0:
            gtxt, gclr = f'{gap:+.0f}%p', '#dc2626'
        else:
            gtxt, gclr = f'{gap:+.0f}%p', '#16a34a'
        h += (f'<tr style="text-align:right;border-top:1px solid #f1f5f9">'
              f'<td style="text-align:left;font-weight:700">{tk}</td>'
              f'<td>{asset:+.1f}%</td><td>{cap:+.1f}%</td>'
              f'<td style="color:{clr};font-weight:700">{rtxt}</td>'
              f'<td style="color:#64748b">{hd:.0f}%</td>'
              f'<td style="color:{gclr};font-weight:700">{gtxt}</td></tr>')
    h += '</table>'
    # 🆕 v9.2.44 (S288, Commander 지시): 열 정의 범례 — 각 열이 무엇을 재는지 각주에 명시.
    h += ('<div style="margin-top:6px;color:#64748b;line-height:1.5">'
          '<div style="font-weight:700;color:#94a3b8">▸ 열 정의</div>'
          '<div>· <b>자산 1Y</b> — 그 종목을 1년 내내 그냥 들고 있었을 때의 수익</div>'
          '<div>· <b>엔진 포착</b> — ARGUS 가 <b>실제 보유한 구간만</b> 곱연결한 수익</div>'
          '<div>· <b>포착률</b> — 엔진 포착 ÷ 자산 수익 (자산 |수익|&lt;5% 는 — 처리)</div>'
          '<div>· <b>보유일</b> — 1년 중 실제로 들고 있던 날의 비중</div>'
          '<div>· <b>불참 이득</b> — 미보유 구간의 (포트폴리오 수익 − 그 종목 수익). '
          '양수 = 안 산 것이 이득 · 음수 = 놓친 알파</div>'
          '</div>')
    h += ('<div style="margin-top:6px;color:#64748b;line-height:1.5">'
          '<div style="font-weight:700;color:#94a3b8">▸ 읽는 법</div>'
          '<div>· 포착률 <b>100% 초과</b> = 단순 보유보다 잘함 (오르는 구간만 골라 보유 = 로테이션 알파)</div>'
          '<div>· 포착률 <b>낮음이 곧 실패가 아님</b> — 신호 꺼진 구간·관문 봉쇄 구간 포함 '
          '(REG-S286_10: 21종 중 9종은 불참이 이익)</div>'
          '<div>· <b>포착률만으로 성패를 판정하지 말 것</b> — 5슬롯 21종 구조에서 낮은 포착률의 '
          '옳고 그름은 그 시간에 포트가 무엇을 벌었는지로 갈린다(격언 #129)</div>'
          '<div>· 발굴 우선순위 = 포착률이 낮고 <b>동시에 불참 이득이 음수</b>인 종목. '
          '포착률만 낮고 불참 이득이 양수면 불참이 옳았던 것이다</div>'
          '<div style="color:#475569;margin-top:3px">※ 관측 지표 — 매매 지시 아님(격언 #15).</div>'
          '</div>')
    h += '</div></div>\n'
    return h

def _compute_suppressed(sigs_data):
    """그룹 내 최강 active 외 약tier sig_key 집합 반환 (engine elif 정합)."""
    # 🔴 REG-S268_3c 처방 (S268): 전역 규칙이 비면 억제가 조용히 0건이 되어
    #   elif 배타 결함이 재발한다. 방어적으로 자가진단 로그를 남겨 무음 실패를 차단.
    if not _ENGINE_SIG_RULES:
        print("  ⚠️ [REG-S268_3] _ENGINE_SIG_RULES 미주입 — elif 억제 불가 (엔진 SIGNAL_RULES 확인 필요)")
    groups = {}
    for sk, sd in sigs_data.items():
        rule = _ENGINE_SIG_RULES.get(sk)
        if not rule:
            continue
        op, thr, macro_key = rule
        if not isinstance(thr, (int, float)):
            continue
        if isinstance(op, str) and op.startswith("ticker_"):
            op_dir = ">" if op.endswith("_p") else "<"
            field = op[len("ticker_"):-2] if op.endswith("_p") else op[len("ticker_"):]
            gkey = ("mom:" + field, op_dir)
        elif op in (">", ">=", "<", "<="):
            if macro_key is None:
                continue
            op_dir = ">" if op in (">", ">=") else "<"
            gkey = (macro_key, op_dir)
        else:
            continue  # interaction 등 그룹화 제외 (보존)
        groups.setdefault(gkey, []).append((sk, thr, op_dir))
    suppressed = set()
    for (_gk, op_dir), members in groups.items():
        members_sorted = sorted(members, key=(lambda x: -x[1]) if op_dir == ">" else (lambda x: x[1]))
        active = [m for m in members_sorted if sigs_data.get(m[0], {}).get('is_active')]
        if len(active) > 1:
            for sk, _t, _d in active[1:]:
                suppressed.add(sk)
    return suppressed


def build_signals_html(tk, per_signal, tickers_data, macro, gates):
    """종목별 전체 신호 HTML 생성"""
    wk_blocked = gates.get('general', {}).get('blocked', False)
    xle_blocked = gates.get('xle', {}).get('blocked', False)
    sigs_data = per_signal.get(tk, {})
    rows = ""

    # Eligibility comes from the actual entry function, not gate metadata or ratio.
    entry_ok = tickers_data.get(tk, {}).get('entry_ok')
    entry_state = '충족' if entry_ok is True else '미충족' if entry_ok is False else '미확인'
    rows += sig_row("gate", "엔진 진입 판정", _html.escape(_gate_line(tk) or "종목별 진입 함수"),
                    entry_state, "open" if entry_ok is True else "fail", None, None)

    cum = 0
    suppressed = _compute_suppressed(sigs_data)  # 🆕 v9.1.2: elif 배타 억제 키
    for sig_key, sd in sigs_data.items():
        active = sd.get('is_active', False)
        pts = sd.get('raw_pts', 0)
        lv = sd.get('live_value', [])

        # 현재값: 🆕 v9.2.24 (S281) — _macro_fallback 우선, 미해결 시에만 엔진 live_value 보완.
        #   v9.2.23이 live_value를 우선시켜 인터랙션·모멘텀 신호 가독성 저하
        #   (vnm_bull_dfii2=active / m1=10.22 등, 구성 매크로값·단위 소실). 우선순위 복원.
        #   fallback은 복합조건을 구성 매크로로 풀어 보여주므로 표시 품질이 우월.
        #   fallback 미등록 신호(PDBC 등)만 live_value로 보완 → 양쪽 모두 해결.
        cur_str = _macro_fallback(sig_key, macro, tickers_data.get(tk, {}))
        if not cur_str or str(cur_str).strip() in ('—', ''):
            if isinstance(lv, (list, tuple)) and len(lv) == 2 and isinstance(lv[1], (int, float)):
                cur_str = f"{lv[0]}={lv[1]:.2f}"
            elif isinstance(lv, (list, tuple)) and len(lv) >= 2 and str(lv[1]) not in ('inactive', '—', ''):
                cur_str = f"{lv[0]}={lv[1]}"

        prox = sd.get('prox', 0) or 0
        prox_str = f" ({prox*100:.0f}%)" if prox > 0.5 else ""
        cond_text = SIGNAL_CONDS.get(sig_key, "")

        if sig_key in suppressed and active:
            # 🆕 v9.1.2: elif 배타 — 조건 충족이나 그룹 내 최강에 의해 점수 미반영 (cum 가산 X)
            rows += sig_row("elif", f"EnSn · {sig_key}", cond_text, cur_str, "elif", pts, cum)
        elif active and pts > 0:
            cum += pts
            rows += sig_row("ensn", f"EnSn · {sig_key}", cond_text, cur_str, "met", pts, cum)
        elif active and pts < 0:
            cum += pts
            rows += sig_row("easn", f"EASn · {sig_key}", cond_text, cur_str, "met", pts, cum)
        elif active:
            rows += sig_row("ensn", f"EnSn · {sig_key}", cond_text, cur_str, "met", 0, cum)
        else:
            rows += sig_row("ensn", f"EnSn · {sig_key}", cond_text, f"{cur_str}{prox_str}", "fail", 0, cum)

    return rows, cum



# ══════════════════════════════════════════════════════════════════════
# 🚦 v9.2.57 [UNIFIED] PREFLIGHT · ACTION_READY · Phantom 검출
# ══════════════════════════════════════════════════════════════════════
_PREFLIGHT = []
_ACTION_READY = {}
_TARGET_STATUS = {}
_CONTRACT_READINESS = {}
_SIMULATED_STATE = {}
_BROKER_STATUS = {}
_ALIGNMENT = {}
_RATIONALE_CONTEXT = {}


def ledger_transition_status(ledger_as_of, data_date):
    """입력 날짜부터 기대 세션을 먼저 계산하여 원장 부재와 달력 오류를 구분한다."""
    expected = None
    try:
        import exchange_calendars as xcals
        cal = xcals.get_calendar("XNYS")
        day = pd.Timestamp(str(data_date)[:10])
        if pd.isna(day) or not cal.is_session(day):
            raise ValueError("data_date_not_session")
        expected = str(pd.Timestamp(cal.previous_session(day)).date())
        old = pd.Timestamp(str(ledger_as_of)[:10])
        if pd.isna(old) or not cal.is_session(old):
            raise ValueError("ledger_date_not_session")
        return {"valid": str(old.date()) == expected, "expected": expected,
                "as_of": str(old.date()), "error": None}
    except Exception as exc:
        return {"valid": False, "expected": expected, "as_of": str(ledger_as_of or "?"),
                "error": f"{type(exc).__name__}: {exc}"}


def select_previous_ledger(ledger, data_date):
    """화면과 전이 산출이 같은 직전 거래일 기록을 선택한다."""
    from argus_position_transition import select_previous_target
    return select_previous_target(ledger, data_date)


def read_broker_status(data_date, data=None):
    """공유 계좌 대사로 출처·평가 날짜·주수·현금·총액을 확인한다."""
    _BROKER_STATUS.clear()
    path = os.environ.get('ARGUS_REAL_HOLDINGS', os.path.join(SCRIPT_DIR, 'argus_real_holdings.json'))
    try:
        with open(path, encoding='utf-8') as f:
            book = json.load(f)
        if data is None:
            raise ValueError('계좌 평가 입력 없음')
        from argus_position_transition import ground_real_holdings
        status = ground_real_holdings(book, normalize_data(data))
        _BROKER_STATUS.update(grounded=bool(status.get('grounded')),
            issues=status.get('reasons', []), diagnostics=status,
            holdings=book if status.get('grounded') else None)
    except FileNotFoundError:
        _BROKER_STATUS.update(grounded=False, issues=['real_holdings_missing'])
    except Exception as exc:
        _BROKER_STATUS.update(grounded=False, issues=[f'{type(exc).__name__}: {exc}'])
    return _BROKER_STATUS.get('holdings')


def target_contract_valid(target, cash):
    """반올림 전 목표의 유한성·음수·총합을 검증한다. 빈 목표와 전량 현금은 허용한다."""
    try:
        if not isinstance(target, dict) or isinstance(cash, bool):
            return False
        vals = [float(v) for v in target.values()] + [float(cash)]
        return all(np.isfinite(v) and 0 <= v <= 1 for v in vals) and abs(sum(vals)-1) <= 1e-6
    except (TypeError, ValueError):
        return False


def render_target_source(data_date, engine_ok, transition):
    """목표는 계속 표시하되 실제 보유·전일 비교·주문으로 오인하지 않도록 출처를 명시한다."""
    if not engine_ok:
        text = "엔진 산출 실패 — 목표비중을 유효한 산출로 사용할 수 없습니다."
    elif transition is not None and (transition.get("comparison_status") or {}).get("valid"):
        text = "목표비중: 최신 엔진 판단 목표. 원장은 전일 비교에만 사용하며 실제 계좌 비중과 다릅니다."
    else:
        text = ("목표비중: 최신 확보 입력으로 엔진 전체를 재실행한 모형 목표입니다. "
                "원장 연속성 또는 전이 산출을 확인하지 못해 전일 대비 변경은 미확정입니다. "
                "과거 경로 재구성 목표이며 실제 보유와 다릅니다. 계좌 비교와 진입 가능 여부는 아래에서 별도로 판정합니다.")
    return ('<div class="hbox" style="display:block;color:#cbd5e1">'
            + _html.escape(text) + '<br><small>입력 기준일: '
            + _html.escape(str(data_date))
            + ' · 최신 완료 세션 충족 여부는 아래 데이터 검사에서 별도로 확인합니다.</small></div>')

REQUIRED_ASSETS = [
    ("엔진 산출 원장", "argus_position_ledger_causal.json", "ledger",
     "직전 목표의 관측 비교를 확인할 수 없다. 최신 엔진 목표 산출은 유지한다."),
    ("전이 레인", "argus_position_transition.py", "transition",
     "엔진 원장→목표와 브로커→목표 전이를 산출하지 못한다."),
    ("실보유 원장", "argus_real_holdings.json", "real_holdings",
     "실제 브로커 보유를 그라운딩할 수 없다."),
    ("트레일링 성과", "briefing_trailing_returns.py", "trailing",
     "실현 성과 섹션이 차단된다."),
]


def _renderer_namespace_guard():
    """동일 숫자 버전에 서로 다른 접미사가 공존하면 빌드를 차단한다."""
    here = os.path.basename(__file__)
    cur_num = RENDERER_VER.split("-", 1)[0]
    conflicts = []
    pat = re.compile(r'RENDERER_VER\s*=\s*["\']([^"\']+)["\']')
    for p in glob.glob(os.path.join(SCRIPT_DIR, "argus_brief_html_v2*.py")):
        if os.path.basename(p) == here:
            continue
        try:
            with open(p, encoding="utf-8") as f:
                txt = f.read(8192)
        except Exception:
            continue
        m = pat.search(txt)
        if not m:
            continue
        other = m.group(1)
        if other.split("-", 1)[0] == cur_num and other != RENDERER_VER:
            conflicts.append((os.path.basename(p), other))
    if conflicts:
        print("🔴 VERSION NAMESPACE FAIL — 동일 숫자 버전에 다른 접미사 공존")
        for fn, ver in conflicts:
            print(f"   {fn}: {ver}  ↔  {RENDERER_VER}")
        return False
    return True


def preflight_assets():
    """배포 자산을 시작 시점에 일괄 점검한다."""
    global _PREFLIGHT
    _PREFLIGHT = []
    print("🛫 PREFLIGHT: 배포 자산 점검")
    missing = 0
    for label, fname, key, impact in REQUIRED_ASSETS:
        p = os.path.join(SCRIPT_DIR, fname)
        if os.path.exists(p):
            _PREFLIGHT.append((label, fname, "OK", ""))
            print(f"   🟢 {label:<8s} {fname}")
            continue
        missing += 1
        alts = [os.path.basename(x) for x in glob.glob(os.path.join(SCRIPT_DIR, "*"))
                if key.split("_")[0] in os.path.basename(x).lower()
                and os.path.basename(x) != fname]
        note = ("유사 파일: " + ", ".join(alts[:4])) if alts else ""
        _PREFLIGHT.append((label, fname, "MISSING", note))
        print(f"   🔴 {label:<8s} {fname} — 부재")
        print(f"      영향: {impact}")
        if note:
            print(f"      🟡 {note}")
    if not _renderer_namespace_guard():
        raise RuntimeError("renderer version namespace conflict")
    print(f"   결손 {missing} / {len(REQUIRED_ASSETS)} · namespace OK")
    return missing


def _xnys_freshness(data_date_str):
    """마지막으로 완전히 끝난 XNYS 세션과 데이터 기준일을 비교한다.

    exchange_calendars를 사용할 수 없으면 근사값으로 정상 판정을 만들지 않고 fail-closed 한다.
    반환: (fresh, lag, expected_date, now_utc, error)
    """
    try:
        import exchange_calendars as _xcals
        now = pd.Timestamp.now(tz="UTC")
        cal = _xcals.get_calendar("XNYS")
        start = (now - pd.Timedelta(days=20)).date()
        end = (now + pd.Timedelta(days=1)).date()
        sessions = cal.sessions_in_range(start, end)
        completed = []
        for s in sessions:
            close = cal.session_close(s)
            if close <= now:
                completed.append((s, close))
        if not completed:
            return False, None, None, now.isoformat(), "completed_session_not_found"
        expected_s, _ = completed[-1]
        expected = pd.Timestamp(expected_s).date()
        data_date = pd.Timestamp(str(data_date_str)[:10]).date()
        chk = cal.sessions_in_range(data_date, data_date)
        if len(chk) != 1:
            return False, None, str(expected), now.isoformat(), "data_date_not_xnys_session"
        if data_date == expected:
            return True, 0, str(expected), now.isoformat(), None
        if data_date > expected:
            return False, -1, str(expected), now.isoformat(), "data_ahead_of_completed_session"
        rng = cal.sessions_in_range(data_date, expected)
        lag = max(0, len(rng) - 1)
        return False, int(lag), str(expected), now.isoformat(), None
    except Exception as e:
        now = pd.Timestamp.now(tz="UTC")
        return False, None, None, now.isoformat(), f"{type(e).__name__}: {e}"


def _broker_holdings_grounded(transition):
    """공유 계좌 대사를 통과한 결과만 행동 근거로 사용한다."""
    if _BROKER_STATUS:
        return bool(_BROKER_STATUS.get("grounded")), list(_BROKER_STATUS.get("issues") or [])
    return False, ['real_holdings_unverified']


def _broker_price_col(df, tk):
    for col in (f"{tk}_Close", tk):
        if col in df.columns:
            return col
    if tk == "QQQM":
        for col in ("QQQ_Close", "QQQ"):
            if col in df.columns:
                return col
    return None

def build_brokerage_transition(df, real_holdings, target, as_of_idx=None):
    """실제 브로커 주수 → 엔진 목표의 주문 출발점을 만든다.

    shares 만 정본으로 사용하고 현재 평가는 df 말미 종가로 다시 계산한다.
    cash.amount 가 있으면 정확 비중·달러 델타·진짜 편도 회전율을 계산한다.
    cash.amount 가 없으면 비중을 꾸며내지 않고, 확정 가능한 구조적 액션
    (보유→목표0 전량매도 / 미보유→목표>0 신규매수)만 반출한다.
    """
    if as_of_idx is None:
        as_of_idx = len(df) - 1
    row = df.iloc[as_of_idx]
    unresolved = []
    positions = {}
    pos_value = 0.0

    for raw_tk, p in (real_holdings.get("positions") or {}).items():
        tk = str(raw_tk).strip().upper()
        shares = float(p.get("shares") or 0.0)
        if shares <= 0:
            continue
        col = _broker_price_col(df, tk)
        px = None
        if col is not None:
            try:
                v = float(row[col])
                if np.isfinite(v) and v > 0:
                    px = v
            except Exception:
                px = None
        if px is None:
            unresolved.append(f"{tk}.current_price")
            value = None
        else:
            value = shares * px
            pos_value += value
        positions[tk] = {
            "shares": shares,
            "price": px,
            "value": value,
        }

    cash_raw = (real_holdings.get("cash") or {}).get("amount")
    cash_amount = None
    if cash_raw is not None:
        try:
            cash_amount = float(cash_raw)
            if not np.isfinite(cash_amount) or cash_amount < 0:
                raise ValueError
        except Exception:
            unresolved.append("cash.amount_invalid")
            cash_amount = None
    else:
        unresolved.append("cash.amount")

    exact = cash_amount is not None and not any(x.endswith("current_price") for x in unresolved)
    current_weights = {}
    cash_weight = None
    nav = None
    orders = []
    one_way = None
    target_cash = max(0.0, 1.0 - sum(float(v) for v in target.values()))

    if exact:
        nav = pos_value + cash_amount
        if nav <= 0:
            unresolved.append("portfolio_nav_nonpositive")
            exact = False
        else:
            current_weights = {tk: float(p["value"]) / nav for tk, p in positions.items()}
            cash_weight = cash_amount / nav
            l1 = abs(target_cash - cash_weight)
            for tk in sorted(set(current_weights) | set(target), key=lambda k: -target.get(k, 0.0)):
                a = current_weights.get(tk, 0.0)
                b = float(target.get(tk, 0.0))
                d = b - a
                l1 += abs(d)
                shares = positions.get(tk, {}).get("shares", 0.0)
                if abs(d) < 0.005:
                    act = "HOLD"
                elif b <= 1e-12 and shares > 0:
                    act = "SELL_ALL"
                elif a <= 1e-12 and b > 0:
                    act = "NEW_BUY"
                elif d > 0:
                    act = "ADD"
                else:
                    act = "REDUCE"
                orders.append({
                    "ticker": tk, "action": act,
                    "current_weight": a, "target_weight": b, "delta_weight": d,
                    "shares": shares,
                    "current_value": positions.get(tk, {}).get("value"),
                    "target_value": nav * b,
                    "delta_value": nav * d,
                })
            # 진짜 편도 회전율 = 현금 포함 L1 거리의 절반.
            one_way = 0.5 * l1
    if not exact:
        # cash 부재에서는 전체 포트 비중을 만들지 않는다. 구조적으로 확정 가능한 액션만 낸다.
        for tk in sorted(set(positions) | set(target), key=lambda k: -target.get(k, 0.0)):
            held = positions.get(tk, {}).get("shares", 0.0) > 0
            b = float(target.get(tk, 0.0))
            if held and b <= 1e-12:
                act = "SELL_ALL"
            elif (not held) and b > 1e-12:
                act = "NEW_BUY"
            elif held and b > 1e-12:
                act = "REBALANCE_UNRESOLVED"
            else:
                continue
            orders.append({
                "ticker": tk, "action": act,
                "shares": positions.get(tk, {}).get("shares", 0.0),
                "current_weight": None, "target_weight": b, "delta_weight": None,
                "current_value": positions.get(tk, {}).get("value"),
                "target_value": None, "delta_value": None,
            })

    actionable = any(o["action"] not in ("HOLD", "REBALANCE_UNRESOLVED") for o in orders)
    return {
        "schema": "brokerage_transition/1.1",
        "available": True,
        "as_of_statement": real_holdings.get("as_of_statement"),
        "market_as_of": str(df.index[as_of_idx].date()),
        "positions": positions,
        "positions_value": pos_value,
        "cash_amount": cash_amount,
        "nav": nav,
        "exact_weighting": bool(exact),
        "orders_computable": bool(exact),
        "current_weights": current_weights,
        "cash_weight": cash_weight,
        "target_weights": {k: float(v) for k, v in target.items()},
        "target_cash_weight": target_cash,
        "orders": orders,
        "turnover_one_way": one_way,
        "actionable": actionable,
        "unresolved": sorted(set(unresolved)),
        "note": ("실보유 shares 가 주문 출발점. cash.amount 부재 시 포트 비중·달러 주문·회전율은 "
                 "fail-closed 로 미산출한다."),
    }


def prepare_alignment(df, holdings, target, cash, result):
    """표시하는 목표와 실보유를 직접 비교한다. 원장·전이 결과는 입력으로 받지 않는다."""
    _ALIGNMENT.clear()
    try:
        if not holdings or not _BROKER_STATUS.get("grounded"):
            raise ValueError("holdings_unverified")
        if not target_contract_valid(target, cash):
            raise ValueError("target_invalid")
        data = df.copy()
        if "Date" in data.columns:
            data = data.set_index(pd.to_datetime(data.pop("Date")))
        if not data.index.is_monotonic_increasing or data.index.has_duplicates:
            raise ValueError("market_dates_invalid")
        for tk in set(holdings["positions"]) | {k for k,v in target.items() if v > 0}:
            col = _broker_price_col(data, tk)
            if col is None or not np.isfinite(float(data.iloc[-1][col])) or float(data.iloc[-1][col]) <= 0:
                raise ValueError(f"{tk}.current_price_invalid")
        b = build_brokerage_transition(data, holdings, target)
        if any(x != "cash.amount" for x in b.get("unresolved", [])):
            raise ValueError("brokerage_inputs_invalid:" + str(b["unresolved"]))
        b["blocked_orders"] = []
        # 목표 편입과 지금 진입 허용은 다르다. 최신 엔진 평가로 매수 후보를 다시 제한한다.
        ticker_info = result.get("tickers") or {}
        for order in b["orders"]:
            if order["action"] in ("NEW_BUY", "ADD"):
                info = ticker_info.get(order["ticker"]) or {}
                allowed = (info.get("entry_ok") is True and info.get("gate_blocked") is False
                           and (info.get("entry_guard") or {}).get("blocked") is False)
                if not allowed:
                    b["blocked_orders"].append(dict(order, reason="진입 게이트 또는 점수 조건 미충족·미확인"))
                    order["action"] = "BUY_BLOCKED"
                    order["delta_value"] = None
        b["actionable"] = any(o["action"] in ("SELL_ALL","NEW_BUY","ADD","REDUCE") for o in b["orders"])
        if b["blocked_orders"]:
            b["orders_computable"] = False
            b["unresolved"].append("buy_gate_or_score_blocked")
        _ALIGNMENT.update(b)
        _ALIGNMENT["valid"] = not bool(b["blocked_orders"])
        if b["blocked_orders"]:
            _ALIGNMENT["error"] = "매수 조건 미달·미확인 종목이 있어 전체 계좌 조정 계획을 차단합니다"
    except Exception as exc:
        _ALIGNMENT.update(valid=False, available=False, error=f"{type(exc).__name__}: {exc}")
    return _ALIGNMENT


def compute_action_ready(data_date, engine_ok, transition=None):
    """🚨 실행 행동 하드 게이트.

        ACTION_READY = DATA_FRESH ∧ HOLDINGS_GROUNDED ∧ ENGINE_VALID ∧ ALIGNMENT_VALID

    이 값은 정확 주문 금액/주수를 계산할 수 있는가가 아니다.
    정확 주문 산출 가능 여부는 brokerage.orders_computable가 담당한다.
    """
    fresh, lag, expected, now_utc, fresh_err = _xnys_freshness(data_date)
    grounded, holding_issues = _broker_holdings_grounded(transition)
    tr = transition or {}
    tr_date = str(tr.get("as_of") or "")[:10]
    target = tr.get("target")
    engine_valid = bool(engine_ok and _TARGET_STATUS.get("target_valid")
                        and _TARGET_STATUS.get("data_date") == str(data_date)[:10]
                        and _CONTRACT_READINESS.get("engine_valid", False))
    transition_valid = bool(engine_valid and isinstance(target, dict)
                            and target_contract_valid(target, tr.get("cash"))
                            and tr_date == str(data_date)[:10])
    ledger_status = _TARGET_STATUS.get("ledger") or ledger_transition_status(tr.get("ledger_as_of"), data_date)
    alignment_valid = bool(_ALIGNMENT.get("valid") and _ALIGNMENT.get("market_as_of") == str(data_date)[:10])
    _ACTION_READY.clear()
    _ACTION_READY.update({
        "data_fresh": bool(fresh),
        "market_lag": lag,
        "expected_session": expected,
        "freshness_error": fresh_err,
        "holdings_grounded": bool(grounded),
        "holding_issues": holding_issues,
        "engine_valid": bool(engine_valid),
        "transition_valid": transition_valid,
        "alignment_valid": alignment_valid,
        "ledger_contiguous": ledger_status["valid"],
        "ledger_status": ledger_status,
        "transition_date": tr_date or None,
        "data_date": str(data_date)[:10],
        "now_utc": now_utc,
        "inputs_complete": bool(_CONTRACT_READINESS.get("inputs_complete", False)),
        "missing_inputs": _CONTRACT_READINESS.get("missing_inputs", []),
        "contract_reasons": _CONTRACT_READINESS.get("reasons", []),
        "ready": bool(fresh and grounded and engine_valid and alignment_valid
                      and _CONTRACT_READINESS.get("action_ready", False)),
    })
    print("🚨 ACTIONGATE:"
          f" DATA_FRESH {'O' if fresh else 'X'} (lag={lag}, expected={expected}) ·"
          f" HOLDINGS_GROUNDED {'O' if grounded else 'X'} ·"
          f" ENGINE_VALID {'O' if engine_valid else 'X'}"
          f" → ACTION_READY {'O' if _ACTION_READY['ready'] else 'X'}")
    return _ACTION_READY


def _crown_safe(s):
    """🆕 v9.2.68 [CROWNSAFE] 엔진에서 받은 문자열의 Crown 토큰을 표시 규약에 맞춘다.

    v9.2.38 규약: 산출 HTML 의 `Crown #NN` 은 서빙 버전 표기 전용이고
    설계 계보 인용은 `Crown NN`(# 없음)이다. CROWNGUARD 가 빌드 타임에 강제한다.
    엔진의 `transition` 문자열은 `Crown #106 공급발 대체 ...` 처럼 # 형태를 쓰므로
    **그대로 실으면 빌드가 멈춘다** (2026-09-21 실사고).
    엔진 표기를 바꾸지 않고 표시 직전에만 정규화한다 — 제약은 제약을 가진 쪽이 진다.
    """
    try:
        return re.sub(r"Crown\s*#(\d+)", r"Crown \1", str(s))
    except Exception:
        return str(s)


def _canonical_score(tk, scored, ps):
    """🆕 v9.2.66 [CANONSCORE] 엔진 정본 점수와 per_signal 재합산을 함께 돌려준다.

    반환: (add, sub, sig_total, canon, blocked, kind)
      add/sub/sig_total — 화면 신호 목록의 가산·감산·합 (억제 신호 제외, 기존 계산 그대로)
      canon             — 엔진 정본. Gate OPEN 이면 entry_score, BLOCKED 면 pot_total(해제 잠재)
      kind              — canon 의 정체를 사람이 읽을 문자열

    🔴 왜 둘이 다를 수 있는가 (실측 근거):
      · 조기 반환 — `entry_TLT` 는 DXY>100 이면 첫 줄에서 `return False, 0` 한다.
        그 뒤 신호는 엔진 안에서 **평가된 적이 없다**. 화면 목록은 독립 계산이라 켜져 보인다.
      · 재분배 배수 — `entry_XLE` 의 vix16 항은 DXY_RGHI 에 따라 -3.3 이 -4.95 가 된다.
        화면 목록의 raw_pts 는 기본값 -3.3 이다.
    둘이 어긋나는 것 자체가 정보다. 감추지 않고 표시한다.
    """
    _sig = ps.get(tk, {}) or {}
    _sup = _compute_suppressed(_sig)
    _act = [v['raw_pts'] for k, v in _sig.items()
            if v.get('is_active') and k not in _sup]
    add = sum(p for p in _act if p > 0)
    sub = sum(p for p in _act if p < 0)
    sig_total = add + sub
    row = next((t for t in (scored or []) if t.get('tk') == tk), None)
    if row is None:
        # 엔진 행이 없으면 재합산이 유일한 근거다 — 그렇다고 명시한다.
        return add, sub, sig_total, sig_total, False, '신호 재합산(엔진 행 부재)'
    blocked = bool(row.get('blocked'))
    canon = float(row.get('eff_total') or 0.0)
    kind = 'Gate 차단 해제 시 잠재(pot_total)' if blocked else '엔진 entry_score'
    return add, sub, sig_total, canon, blocked, kind


def entry_display_status(info, tk=None, transition=None, inputs_complete=None):
    """입력 검증과 전일 비교를 먼저 판정하고 당일 신호를 표시한다."""
    complete = _CONTRACT_READINESS.get('inputs_complete', False) if inputs_complete is None else inputs_complete
    if complete is not True:
        return '🟡 입력 검증 미완료 — 점수·ratio는 미검증 계산값'
    if info.get('gate_blocked'):
        return '🔒 진입 게이트 차단 — 해제 후 전체 조건 재평가'
    if info.get('entry_ok') is True:
        return '🟢 당일 신호 조건 충족 — 슬롯·전이·계좌 검증 별도'
    if info.get('entry_ok') is not False:
        return '🟡 당일 신호 판정 미확인'
    if tk is None:
        return '🟡 당일 신호 조건 미달'
    if ((transition or {}).get('comparison_status') or {}).get('valid') is not True:
        return '🟡 당일 신호 조건 미달 · 전일 비교 불가 — 신규 편입 여부 미확정'
    if tk not in ((transition or {}).get('prev') or {}):
        return '🟡 모형 신규 편입 · 당일 신호 조건 미달 — 신규매수 근거 없음'
    return '🟡 모형 목표 유지 · 당일 신호 조건 미달 — 추가매수 근거 없음'


def allocation_explanation_html():
    """실제 배분 함수 설명을 본문과 부록이 함께 사용한다."""
    k = _ENGINE_CONST.get('DS_K', 5.0)
    km = _html.escape(str(_ENGINE_CONST.get('DS_K_MAP', {})))
    cap = _ENGINE_CONST.get('SOFT_SINGLE_W', .7) * 100
    return (f'<div class="allocation-explanation">'
            '<div>• 표의 ratio = 오늘 평가 점수 ÷ 종목별 임계. 배분에 저장된 진입 점수와 다를 수 있습니다.</div>'
            '<div>• 배분 입력 r = 저장 진입 점수 × 잔존계수(weight_factor) ÷ max(종목별 임계, 0.5) × 사이징배수.</div>'
            '<div>• 원시 가중 = max(r, 0)<sup>종목별 지수</sup> × 잔존계수. COPX는 NFCI_UP=1이면 추가 배수를 곱합니다.</div>'
            f'<div>• 종목별 지수는 DS_K_MAP 적용, 미지정 기본값 {k:g}. 현재 개별값: {km}. 거듭제곱 배분이 적용 중입니다.</div>'
            '<div>• 원시 가중 합이 양수이면 정규화하고, 합이 0 이하이면 보유 종목에 균등 배분합니다.</div>'
            f'<div>• 정규화 후 유효 상한 = max({cap:g}%, 100% ÷ 보유 종목 수). 보유 1종이면 상한 100%이며 초과분은 나머지 종목에 재분배합니다.</div>'
            '<div>• 이후 위험 관리에 따른 노출 축소·현금 반영과 주수 실행을 적용합니다. 빈 슬롯 수만으로 현금 비중을 정하지 않습니다.</div>'
            '<div>• 사이징배수는 거듭제곱 안에 적용되므로 최종 비중이 그 배수만큼 변한다는 뜻이 아닙니다.</div></div>')


def _score_box_html(tk, scored, ps, th_val):
    """🆕 v9.2.66 [CANONSCORE] 카드 하단 '최종 점수' 박스 — 보유·후보 공용 단일 산출.

    종전에는 같은 코드가 두 곳에 복제돼 있었다. 한쪽만 고치면 언젠가 갈린다.
    """
    add, sub, sig_total, canon, blocked, kind = _canonical_score(tk, scored, ps)
    _thr = th_val or 1
    h = ('<div style="display:flex;justify-content:space-between;padding:6px 10px;'
         'background:#0f172a;border-radius:6px;margin-top:8px;font-size:11px">')
    h += '<span style="color:#94a3b8;font-weight:600">' + ('최종 점수' if _CONTRACT_READINESS.get('inputs_complete', False) else '미검증 계산 점수') + '</span><span>'
    h += f'<span style="color:#4ade80">가산 +{add:.1f}</span>'
    if sub:
        h += f' · <span style="color:#ff8a8a">감산 {sub:.1f}</span>'
    h += f' = <span style="font-size:13px;font-weight:900">{canon:.2f}</span>'
    h += f' <span style="color:#94a3b8">({canon/_thr:.2f}x)</span></span></div>\n'
    if abs(sig_total - canon) > 0.005:
        h += ('<div style="font-size:9px;color:#fbbf24;font-weight:700;margin-top:4px;'
              'padding:4px 8px;background:rgba(251,191,36,0.08);border-radius:4px">'
              f'🔴 신호 합산 {sig_total:.2f} ≠ {_html.escape(kind)} {canon:.2f} '
              f'(차 {sig_total - canon:+.2f}) — 위 신호 목록은 엔진의 조기 반환·재분배 배수를 '
              '재현하지 않는다. 표시 정본은 엔진 값이다.</div>\n')
    return h


def _action_gate_reason_lines(data_date):
    A = _ACTION_READY
    E = _html.escape
    rows = []
    if not A.get("data_fresh"):
        lag = "?" if A.get("market_lag") is None else str(A.get("market_lag"))
        exp = A.get("expected_session") or "?"
        extra = f" · {E(str(A.get('freshness_error')))}" if A.get("freshness_error") else ""
        rows.append(f"🔴 <b>DATA_FRESH = False</b> — MARKET LAG {lag} sessions · "
                    f"data {E(str(data_date)[:10])} / expected {E(str(exp))}{extra}")
    if not A.get("holdings_grounded"):
        issues = ", ".join(A.get("holding_issues") or []) or "real holdings unavailable"
        rows.append("🔴 <b>HOLDINGS_GROUNDED = False</b> — " + E(issues)
                    + ". 실제 보유를 확정할 수 없어 매수/매도 방향을 표시하지 않습니다.")
    if not A.get("engine_valid"):
        rows.append("🔴 <b>ENGINE_VALID = False</b> — 최신 입력의 목표 산출 또는 목표 합계 검증이 완료되지 않았습니다.")
    if not A.get("inputs_complete"):
        rows.append("🔴 필수 입력 미확인 — " + E(str(A.get("missing_inputs") or A.get("contract_reasons") or "입력 검증 미완료")))
    if not A.get("alignment_valid"):
        reason = "실제 계좌 검증 후 계산합니다." if not A.get("holdings_grounded") else str(_ALIGNMENT.get("error") or "alignment_unavailable")
        rows.append("🔴 계좌 비교 계산 대기 — " + E(reason))
    return rows


def render_action_ready_banner(data_date):
    A = _ACTION_READY
    if not A:
        return ""
    if A.get("ready"):
        return ('<div class="hbox" style="border-color:#4ade80;background:rgba(74,222,128,0.10)">'
                '<span style="font-weight:900;color:#4ade80">🟢 최신 목표·계좌 비교 가능</span>'
                '<span style="font-size:11px;color:#86efac"> — 데이터 신선 · 실보유 shares 확인 · '
                '최신 목표와 계좌 비교 유효. 종목별 진입 제한을 별도로 적용합니다. 정확 주문 금액/수량은 '
                'orders_computable이 별도로 결정합니다.</span></div>')
    rows = _action_gate_reason_lines(data_date)
    return ('<div class="hbox" style="border-color:#f87171;background:rgba(248,113,113,0.16);'
            'display:block;padding:10px 12px">'
            '<div style="font-weight:900;color:#f87171;font-size:13px;margin-bottom:6px">'
            '🚨 ACTION_READY = False — 행동 지시 차단</div>'
            '<div style="font-size:11px;line-height:1.9;color:#fca5a5">%s</div>'
            '<div style="font-size:10px;color:#94a3b8;margin-top:6px">'
            '목표 비중(Target)은 정보로 계속 표시할 수 있지만 SELL/BUY 방향은 숨깁니다.</div></div>'
            % ("<br>".join(rows) if rows else "원인 미확정"))


def render_phantom_banner(portfolio, transition):
    """ACTION_READY가 닫힌 상태의 실보유/표시목표 종목집합 불일치 경고."""
    if _ACTION_READY.get("ready"):
        return ""
    b = (transition or {}).get("brokerage") or {}
    pos = b.get("positions") or {}
    if not b.get("available") or not isinstance(pos, dict) or not portfolio:
        return ""
    actual = {str(t) for t, p in pos.items() if float((p or {}).get("shares") or 0) > 0}
    target = {str(t) for t, w in (portfolio or {}).items() if float(w or 0) > 0}
    if actual == target:
        return ""
    overlap = len(actual & target)
    sev = "#f87171" if overlap == 0 else "#fbbf24"
    head = "종목 전면 불일치" if overlap == 0 else "종목 부분 불일치"
    act_txt = " / ".join(
        f"{_html.escape(str(t))} {_fmt_shares((pos.get(t) or {}).get('shares', 0))}주"
        for t in sorted(actual)) or "(없음)"
    tgt_txt = " / ".join(sorted(target)) or "(현금)"
    return ('<div class="hbox" style="border-color:%s;background:rgba(248,113,113,0.12);'
            'display:block;padding:10px 12px">'
            '<div style="font-weight:900;color:%s;font-size:13px;margin-bottom:6px">'
            '👻 Phantom Portfolio Guard — %s</div>'
            '<div style="font-size:11px;line-height:1.9;color:#fca5a5">'
            '실제 브로커 보유: <b>%s</b><br>표시 목표: <b>%s</b><br>공통 종목 %d개</div>'
            '<div style="font-size:10px;color:#94a3b8;margin-top:6px">'
            '현재 ACTION_READY가 닫혀 있으므로 이 불일치를 매매 지시로 변환하지 않습니다.</div></div>'
            % (sev, sev, head, act_txt, _html.escape(tgt_txt), overlap))


def load_engine(engine_path=None):
    """명시 설정된 엔진만 읽고 채점 규칙을 표시기에 연결한다."""
    mod = _contract_load_engine(engine_path)
    eng_path = mod.__file__
    _ENGINE_SIG_RULES.clear()
    _ENGINE_SIG_RULES.update(getattr(mod, 'SIGNAL_RULES', {}) or {})
    return mod, eng_path


def fetch_live_data():
    """데이터 로드: BT_LONG + argus_data (BT_LONG 없으면 argus_data 단독)
    🔒 v9.2.32 (S284): argus-public-data 하드코딩 — 로컬 경로 후보 제거."""
    snapshot = os.environ.get("ARGUS_COMBINED_DATA")
    if snapshot:
        return normalize_data(pd.read_csv(snapshot))
    print("📂 데이터 로드...")
    ad = pd.read_csv(_fetch_public_csv("argus_data.csv"), parse_dates=['Date'])
    print(f"  argus_data: {len(ad)}행 ({ad['Date'].min().date()}~{ad['Date'].max().date()})")

    try:
        # 🔴 v9.2.54 [BTV6]: 판본을 상수 단일 원천으로 — LIVE 와 §40v3 BT 가 같은 판본을 본다.
        bt = pd.read_csv(_fetch_public_csv(BT_LONG_NAME), parse_dates=['Date'])
        bt_last = bt['Date'].max()
        ad_new = ad[ad['Date'] > bt_last].copy()
        df = pd.concat([bt, ad_new], ignore_index=True, sort=False)
        print(f"  BT_LONG 결합: {len(df)}행 ({BT_LONG_NAME} 말미 {bt_last.date()} + argus_data {len(ad_new)}행)")
        # 🔴 v9.2.65 [FEATBASE] 열 수준 무성 강등 차단.
        #   `common` 은 교집합이므로 한쪽에만 있는 열은 **최근 구간의 값까지** 사라진다.
        #   v9.2.54 의 강등 차단은 행수에만 걸려 있어 이 경로를 잡지 못했다.
        #   Crown 자본 규칙이 소비하는 열이 결합에서 빠지면 규칙이 조용히 identity 가 된다
        #   (실측 2026-09-21: KIL_SUP·GPR_HIGH 탈락 → sizing_mult('EWZ') 0.3 → 1.0).
        #   빌드를 막지는 않는다 — 레인은 살리고 사실을 크게 남긴다.
        _CAPITAL_FEATURE_COLS = ("KIL_SUP", "GPR_HIGH")
        _missing_feat = [c for c in _CAPITAL_FEATURE_COLS if c not in df.columns]
        if _missing_feat:
            print(f"::error::결합본에 자본 규칙 소비 열 누락 {_missing_feat} — "
                  f"Crown #106/#108 이 identity 가 된다. 입력 판본이 FEAT 계열인지 확인할 것 "
                  f"(현재 {BT_LONG_NAME}, 결합 {len(df.columns)}열).")
        else:
            _fv = {c: int(pd.to_numeric(df[c], errors='coerce').eq(1).sum())
                   for c in _CAPITAL_FEATURE_COLS}
            print(f"  ✅ v9.2.65 자본 피처 도달: {_fv} (결합 {len(df.columns)}열)")
    except Exception as _ex:
        raise RuntimeError("장기 입력 회수·결합 실패: 짧은 입력으로 강등하지 않습니다") from _ex

    df = df.sort_values('Date').reset_index(drop=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    print(f"  최종: {len(df)}행 (~{df['Date'].iloc[-1]})")
    return normalize_data(df)


def load_daily_diff(data_date=None, target=None):
    """같은 날짜·계약·목표의 동결 관측 기록만 읽는다."""
    path = os.environ.get('ARGUS_DAILY_DIFF', os.path.join(SCRIPT_DIR, 'prima_daily_output_causal_diff.json'))
    try:
        with open(path, encoding='utf-8') as f:
            record = json.load(f)
        if record.get('schema') != 'causal_target_diff/1.0' or record.get('src') != 'causal_engine_target':
            return None
        if str(record.get('date', ''))[:10] != str(data_date)[:10] or record.get('positions') != target:
            return None
        return record
    except (OSError, ValueError, TypeError):
        return None


def build_change_section_html(diff):
    """📊 전일 대비 변경 섹션 HTML. diff=None → 빈 문자열(섹션 생략).
       사유 출처 = 엔진 trade_log (진입/청산). 비중변화 = 리밸런싱."""
    if not diff:
        return ""
    if diff.get('src') == 'causal_engine_target':
        observations = diff.get('observations') or []
        rows = ''.join('<div>%s: %.2f%% → %.2f%% (%+.2f%%p)</div>' %
            (_html.escape(str(row['ticker'])), row['previous_target']*100,
             row['target']*100, row['delta']*100) for row in observations)
        if not rows:
            rows = _html.escape(str(diff.get('change_reason') or '비교 가능한 변경 기록 없음'))
        return ('<div class="card al"><div class="ct">📊 동결 목표 변경 관측</div>' + rows
                + '<div>실제 증권사 체결이나 매매 지시가 아닙니다.</div></div>')
    date = diff.get("date", "?")
    if not diff.get("changed", False):
        reason = diff.get("change_reason", "전일과 동일")
        is_init = "초기" in reason
        label = "🆕 초기 기록" if is_init else "✅ 전일과 동일"
        color = "#60a5fa" if is_init else "#4ade80"
        rgba  = "96,165,250" if is_init else "34,197,94"
        return (f'<div class="card al"><div class="ct">📊 전일 대비 변경</div>'
                f'<div class="hbox" style="border-color:{color};background:rgba({rgba},0.06);font-size:11px">'
                f'<span style="font-weight:700;color:{color}">{label}</span> '
                f'<span style="color:#64748b">— {reason} ({date})</span></div></div>\n')
    rows = []
    for e in diff.get("exited", []):
        rows.append(f'<div style="font-size:11px;margin:3px 0">🔴 <b>청산 {e.get("ticker")}</b> '
                    f'<span style="color:#94a3b8">— {e.get("reason","")}</span></div>')
    for e in diff.get("entered", []):
        w = (e.get("weight") or 0) * 100
        rows.append(f'<div style="font-size:11px;margin:3px 0">🟢 <b>진입 {e.get("ticker")}</b> '
                    f'({w:.1f}%) <span style="color:#94a3b8">— {e.get("reason","")}</span></div>')
    for r in diff.get("reweighted", []):
        fr = (r.get("from") or 0) * 100
        to = (r.get("to") or 0) * 100
        rows.append(f'<div style="font-size:11px;margin:3px 0">🔄 리밸 {r.get("ticker")} '
                    f'<span style="color:#94a3b8">{fr:.1f}% → {to:.1f}%</span></div>')
    body = "".join(rows) or '<div style="font-size:11px">변경 감지</div>'
    return (f'<div class="card al"><div class="ct">📊 전일 대비 변경 '
            f'<span style="color:#64748b;font-size:10px">({date})</span></div>'
            f'<div class="hbox" style="border-color:#fb923c;background:rgba(251,146,60,0.06)">'
            f'{body}</div></div>\n')


# 🔒 L2 HARDLOCK (S284): 트레일링 산출원 = 실보유 장부 실현 수익률로 고정.
#   구버전(v1, 소급 BT 기반) 모듈이 남아 있으면 **BT 수치를 쓰지 않고** 오류 카드로 대체한다.
#   하드 import 는 배포 순서 사고 시 브리핑 전체를 중단시키므로(S284 실사고) 방어적으로 처리하되,
#   "조용한 BT 회귀"는 여전히 불가능하다 — v1 함수를 호출하지 않고 차단 카드를 반환하기 때문.
try:
    from briefing_trailing_returns import format_trailing_html, assert_realized_policy
    assert_realized_policy(where="argus_brief_html_v2")
    _TRAILING_LOCK_OK, _TRAILING_LOCK_ERR = True, ""
except (ImportError, RuntimeError, AttributeError) as _tl_ex:
    _TRAILING_LOCK_OK, _TRAILING_LOCK_ERR = False, f"{type(_tl_ex).__name__}: {_tl_ex}"
    print(f"  🔒 트레일링 HARDLOCK 미충족 — 성과 섹션 차단: {_TRAILING_LOCK_ERR}")

    def format_trailing_html(*_a, **_k):
        """구버전/부재 모듈 폴백 — 소급 BT 표시 금지, 차단 사유만 노출(fail-loud)."""
        return ('<div class="card al"><div class="ct">📈 트레일링 성과</div>'
                '<div style="color:#fb923c;font-size:11px">⚠️ 표시 차단 — '
                'briefing_trailing_returns 모듈이 실현수익률 정본(v2.1+)이 아닙니다.<br>'
                f'사유: {_TRAILING_LOCK_ERR}<br>'
                '소급 백테스트 대체 금지 (Commander 지시 S284)</div></div>')


def build_holdings_chart_html(df_prices):
    """v9.1.9: 6개월 보유 차트 — 6M 수익률 내림차순 정렬 + 보유일수 표기 + 현금(RP) 별도 행. From-entry 제거.
    데이터 = LIVE ledger(argus_daily_holdings.csv) + 가격 df. 순수 SVG(matplotlib 불요).
    실패(네트워크 등) 시 빈 문자열 반환(브리핑 무손상)."""
    try:
        led = pd.read_csv(_fetch_public_csv("argus_daily_holdings.csv"))
        led["Date"] = pd.to_datetime(led["Date"])
        dfp = df_prices.copy(); dfp["Date"] = pd.to_datetime(dfp["Date"])
        df = pd.merge(led, dfp, on="Date", how="inner").sort_values("Date").reset_index(drop=True)
        M = len(df)
        if M < 2: return ""
        end = df["Date"].iloc[-1]; wstart = end - pd.DateOffset(months=6)
        _idx = df.index[df["Date"] >= wstart]
        if len(_idx) == 0: return ""
        wsi = int(_idx[0])
        assets = [c for c in led.columns if c not in ("Date", "RP")]
        COL = {'GLD': '#fde047', 'SLV': '#f1f5f9', 'COPX': '#fb923c', 'XLE': '#ff6b6b', 'EWZ': '#22c55e',
               'ITA': '#a78bfa', 'SMH': '#3b82f6', 'CQQQ': '#ef4444', 'VNM': '#e879f9', 'NLR': '#a3e635',
               'TLT': '#38bdf8', 'QQQM': '#60a5fa', 'XLU': '#facc15', 'PAVE': '#fbbf24'}
        RP_COL = '#94a3b8'  # 현금 = 회색 계열(별도 식별)

        def _runs(mask):
            out = []; s = None
            for i, v in enumerate(mask):
                if v and s is None: s = i
                elif not v and s is not None: out.append((s, i - 1)); s = None
            if s is not None: out.append((s, M - 1))
            return out

        def _winret(price, rl_all):
            comp = 1.0
            for s, e in rl_all:
                if e < wsi: continue
                seg = price[max(s, wsi):e + 1]
                if len(seg) >= 2: comp *= seg[-1] / seg[0]
            return (comp - 1.0) * 100

        rows = []
        for a in assets:
            pc = f"{a}_Close"
            if a not in COL or pc not in df.columns: continue
            held = (df[a].fillna(0) > 1e-6).values
            hd = int(held[wsi:].sum())
            if hd == 0: continue
            rl_all = _runs(held)
            disp = [(max(s, wsi), e) for s, e in rl_all if e >= wsi and ((e - s + 1) >= 3 or e == M - 1)]
            if not disp: continue  # 표시 run 없음(단기·비현재) → 제외
            rows.append({"a": a, "hd": hd, "ret": _winret(df[pc].values, rl_all),
                         "cur": bool(held[M - 1]), "runs": disp, "col": COL[a]})
        # 현금(RP) — SGOV 기준
        if "RP" in led.columns and "SGOV_Close" in df.columns:
            held = (df["RP"].fillna(0) > 1e-6).values
            hd = int(held[wsi:].sum())
            if hd > 0:
                rl_all = _runs(held)
                disp = [(max(s, wsi), e) for s, e in rl_all if e >= wsi and ((e - s + 1) >= 3 or e == M - 1)]
                if disp:
                    rows.append({"a": "현금(RP)", "hd": hd, "ret": _winret(df["SGOV_Close"].values, rl_all),
                                 "cur": bool(held[M - 1]), "runs": disp, "col": RP_COL})
        if not rows: return ""
        rows.sort(key=lambda r: -r["ret"])  # 6M 수익률 내림차순

        # ---------- SVG ----------
        RH = 26; top = 46; lab_w = 150; tl0 = 162; tl1 = 560; tlw = tl1 - tl0; ret_x = 712
        H = top + len(rows) * RH + 22
        den = max(M - 1 - wsi, 1)
        def X(i): return tl0 + (i - wsi) / den * tlw
        S = [f'<svg viewBox="0 0 728 {H}" xmlns="http://www.w3.org/2000/svg" '
             f'font-family="-apple-system,Segoe UI,Roboto,sans-serif" style="min-width:728px">']
        S.append('<text x="0" y="22" fill="#c9d1d9" font-size="12" font-weight="700">자산 · 보유일</text>')
        S.append(f'<text x="{tl0}" y="22" fill="#8b949e" font-size="11">{wstart.strftime("%Y-%m-%d")}</text>')
        S.append(f'<text x="{tl1}" y="22" fill="#8b949e" font-size="11" text-anchor="end">{end.strftime("%Y-%m-%d")}</text>')
        S.append(f'<text x="{ret_x}" y="22" fill="#c9d1d9" font-size="12" font-weight="700" text-anchor="end">6M 수익률</text>')
        S.append(f'<line x1="{tl0}" y1="{top-8}" x2="{tl1}" y2="{top-8}" stroke="#30363d" stroke-width="1"/>')
        for i, r in enumerate(rows):
            y = top + i * RH; cy = y + RH / 2
            mark = ' ●' if r["cur"] else ''
            nm_col = r["col"] if r["col"] != '#f1f5f9' else '#e6edf3'
            S.append(f'<text x="0" y="{cy+4:.0f}" fill="{nm_col}" font-size="13" font-weight="700">{r["a"]}{mark}</text>')
            S.append(f'<text x="{lab_w}" y="{cy+4:.0f}" fill="#8b949e" font-size="11" text-anchor="end">{r["hd"]}d</text>')
            for s, e in r["runs"]:
                x0 = X(s); x1 = X(e); w = max(x1 - x0, 2.0)
                op = '0.95' if r["cur"] else '0.65'
                S.append(f'<rect x="{x0:.1f}" y="{y+6:.1f}" width="{w:.1f}" height="{RH-12}" rx="3" fill="{r["col"]}" opacity="{op}"/>')
            rc = '#4ade80' if r["ret"] >= 0 else '#ff8a8a'
            S.append(f'<text x="{ret_x}" y="{cy+4:.0f}" fill="{rc}" font-size="13" font-weight="700" text-anchor="end">{r["ret"]:+.2f}%</text>')
        S.append('</svg>')
        svg = "".join(S)
        return ('<div class="card al">'
                '<div class="card-title">📊 6-Month Holdings</div>'
                f'<div style="overflow-x:auto">{svg}</div>'
                '<div style="color:#8b949e;font-size:11px;margin-top:6px">'
                '막대 = 6M 윈도우 내 보유구간 · 보유일 = 윈도우 내 총 보유일수 · '
                '6M 수익률 = 보유구간 곱연결(윈도우 기준) · ● = 현재 보유 · 현금(RP) = SGOV 기준'
                '</div></div>')
    except Exception as _e:
        print(f"  ⚠️ 보유 차트 생성 실패: {_e}")
        return ""


def build_return_rank_html(df, eng=None):
    """v9.2.5 신설: 1개월 누적 수익률순위 (전체종목중).
    전 종목 유니버스(ENTRY_FUNCTIONS 키) 달력 1개월 누적수익률 = 최근 종가 / 약 1개월 전 종가 - 1.
    Top5 강조 + 전체 유니버스 제로 기준 발산 막대. 실패 시 빈 문자열(브리핑 무손상).
    표시 전용 · 진입신호 아님(신호 채택 != 자본 반영, 격언 #15).
    🆕 v9.2.22 (S280): UNIV를 엔진 ENTRY_FUNCTIONS 키에서 도출(자가치유) — 21종 편입·향후 신규 티커 자동 반영."""
    try:
        # 🆕 v9.2.22: 엔진 ENTRY_FUNCTIONS 키 = 단일 원천 (PDBC 등 신규 티커 자동 포함)
        if eng is not None and hasattr(eng, 'ENTRY_FUNCTIONS'):
            UNIV = sorted(eng.ENTRY_FUNCTIONS.keys())
        else:
            UNIV = ['CIBR','COPX','CQQQ','EWZ','GLD','INDA','ITA','IWM','NLR','PAVE',
                    'PDBC','QQQM','SLV','SMH','TLT','VEA','VNM','XLE','XLF','XLU','XLV']
        d = df
        dates = list(d['Date'])
        last_date = dates[-1]
        y, m, dd = [int(x) for x in last_date.split('-')]
        pm_y, pm_m = (y, m - 1) if m > 1 else (y - 1, 12)
        target = "%04d-%02d-%02d" % (pm_y, pm_m, dd)  # 달력 1개월 전 목표일
        base_i = 0
        for i, ds in enumerate(dates):
            if ds <= target:
                base_i = i
        base_date = dates[base_i]
        last = d.iloc[-1]; base = d.iloc[base_i]
        res = []
        for tk in UNIV:
            c = tk + '_Close'
            if c not in d.columns:
                continue
            p0 = float(base[c]); p1 = float(last[c])
            if p0 <= 0:
                continue
            res.append((tk, (p1 / p0 - 1.0) * 100.0))
        if not res:
            return ""
        res.sort(key=lambda x: -x[1])
        maxabs = max(abs(r) for _, r in res) or 1.0
        GAIN = "#4ade80"; LOSS = "#f87171"
        # 전체 20 발산 막대
        rows = []
        for rk, (tk, ret) in enumerate(res, 1):
            pos = ret >= 0
            w = abs(ret) / maxabs * 44.0
            col = GAIN if pos else LOSS
            sign = "+" if pos else "−"
            lbar = "" if pos else ('<span style="display:inline-block;height:7px;width:%.2f%%;background:%s;border-radius:2px;float:right"></span>' % (w, LOSS))
            rbar = ('<span style="display:inline-block;height:7px;width:%.2f%%;background:%s;border-radius:2px"></span>' % (w, GAIN)) if pos else ""
            _hl = 'background:rgba(74,222,128,0.05)' if rk <= 5 else ''
            _rc = '#fbbf24' if rk <= 5 else '#64748b'
            _tw = '800' if rk <= 5 else '700'
            rows.append(
                '<tr style="%s">'
                '<td style="color:%s;font-family:ui-monospace,monospace;font-size:10px;width:22px">%02d</td>'
                '<td style="font-weight:%s;font-size:11px;width:74px;white-space:nowrap">%s %s</td>'
                '<td style="width:46%%;text-align:right;padding-right:2px">%s</td>'
                '<td style="width:2px;background:#233047"></td>'
                '<td style="width:46%%">%s</td>'
                '<td style="font-family:ui-monospace,monospace;font-size:11px;font-weight:700;color:%s;text-align:right;width:66px">%s%.2f%%</td>'
                '</tr>' % (_hl, _rc, rk, _tw, EMOJIS.get(tk, ""), tk, lbar, rbar, col, sign, abs(ret)))
        table = '<table style="width:100%;border-collapse:collapse">' + "".join(rows) + '</table>'
        note = ('<div style="font-size:10px;color:#64748b;margin-top:8px;line-height:1.5">'
                '구간 %s → %s (달력 1개월) · 전체 %d종목 실측 · '
                '표시 전용 · 진입신호 아님(신호 채택 != 자본 반영, 격언 #15) · '
                'Top5 미진입 = 신호 실패 아님</div>') % (base_date, last_date, len(res))
        return ('<div class="card al"><div class="ct">\U0001F4C8 1개월 누적 수익률순위 (전체종목중)</div>'
                + table + note + '</div>\n')
    except Exception as _e:
        print("  ⚠️ 수익률순위 섹션 생성 실패: %s" % _e)
        return ""


# \U0001F195 [S277 Risk Board] 보유 ExSn 임박 + 실계좌 드리프트
_ENGINE_EXSN_FALLBACK = {
    "WTI": {"XLE":110,"SLV":80,"GLD":90,"ITA":90,"NLR":90,"EWZ":90,"XLU":90,"XLF":90,"COPX":90,"QQQM":90,"SMH":90,"IWM":90,"PAVE":90,"CQQQ":90,"VEA":90,"VNM":90,"INDA":90,"XLV":90,"CIBR":90,"PDBC":100,"TLT":None},
    "VIX": {"GLD":None,"TLT":None,"SLV":40,"XLV":45,"ITA":35,"NLR":35,"EWZ":35,"XLE":35,"XLU":35,"XLF":35,"COPX":35,"QQQM":35,"SMH":35,"IWM":35,"PAVE":35,"CQQQ":35,"VEA":35,"VNM":35,"INDA":35,"CIBR":35,"PDBC":None},
}

def load_real_account():
    """real_account.json 실계좌 비중. 없으면 None -> 모델 포지션 폴백."""
    import json, os
    p = os.environ.get("REAL_ACCOUNT_JSON", "real_account.json")
    try:
        with open(p, encoding="utf-8") as f: d = json.load(f)
        w = d.get("weights") or {}
        return {k: float(v) for k, v in w.items() if v} or None
    except Exception:
        return None

def render_next_scan_note(final_positions, portfolio):
    """🆕 v9.2.39: 다음 진입 스캔까지 남은 거래일 안내 (표시 전용).

    엔진은 `(i - ls) >= rebal_freq ∩ 슬롯 여유` 일 때만 신규 진입을 스캔한다.
    ls(마지막 스캔 인덱스)는 엔진 내부 지역변수라 노출되지 않으므로, 보유 종목의
    **최소 held_days**(= 마지막 진입 이후 경과 거래일)를 사용한다.
    ls >= 마지막 진입 시점이므로 이 값은 대기일의 **하한**이다 — 문구로 명시한다.
    슬롯이 만석이면 스캔 자체가 돌지 않으므로 별도 표기.
    """
    rf = int(_ENGINE_CONST.get('REBAL_FREQ', 5))
    mp = int(_ENGINE_CONST.get('MAX_POS', 5))
    n_held = len(portfolio or {})
    if n_held >= mp:
        return ('<div style="font-size:11px;color:#94a3b8;text-align:center;margin-bottom:4px">'
                '🎰 <span style="color:#64748b">슬롯 만석 %d/%d — 신규 진입 스캔 미가동</span>'
                '(청산 발생 시 재가동)</div>' % (n_held, mp))
    hd = [int(v.get('held_days', 0) or 0) for v in (final_positions or {}).values()]
    if not hd:
        return ''
    since = min(hd)
    wait = rf - since
    if wait <= 0:
        return ('<div style="font-size:11px;color:#cbd5e1;text-align:center;margin-bottom:4px">'
                '🔎 <b style="color:#4ade80">진입 스캔 가동 구간</b> '
                '<span style="color:#64748b">— 마지막 진입 후 %d거래일 경과 (주기 %d) · 빈 슬롯 %d칸</span></div>'
                % (since, rf, mp - n_held))
    return ('<div style="font-size:11px;color:#cbd5e1;text-align:center;margin-bottom:4px">'
            '🔎 다음 진입 스캔 <b style="color:#fbbf24">빠르면 %d거래일 후</b> '
            '<span style="color:#64748b">— 마지막 진입 후 %d거래일 · 주기 %d거래일 · 빈 슬롯 %d칸 '
            '(하한 추정: 엔진 스캔 시점 미노출)</span></div>'
            % (wait, since, rf, mp - n_held))


def render_slot_proximity(scored, portfolio, max_slots=5):
    """🆕 v9.2.26 [S281 Commander 정의]: Top5 슬롯 경쟁 근접 카드.
    ⚠️ '근접' = 신호 문턱 근접이 아니라 **Top5 진입/탈락 가능성 근접**.
      구 v9.2.25 는 신호 문턱 근접(EWZ pmi50 73%)을 표시했으나, 그 신호가 켜져도
      ratio 1.08 로 Top5 근처에도 못 가므로 노이즈였다. Commander 정의로 재설계.

    판정 기준 (eff_total/thresh = ratio 기준, DS_K 비중과 동일 서열):
      · 컷오프 = 슬롯 경쟁 5위 ratio (후보<5 이면 0 → 빈 슬롯 존재)
      · 🎯 진입 근접 = 미보유 ∩ ratio 가 컷오프의 0.8~1.0배 (조금만 오르면 진입)
      · ⚠️ 탈락 근접 = 보유   ∩ ratio 가 컷오프의 1.0~1.25배 (조금만 내리면 밀림)
    표시 전용 · 진입/청산 지시 아님(격언 #15)."""
    held = set(portfolio.keys()) if portfolio else set()
    cands = []
    for it in scored:
        th = it.get('thresh') or 0
        if th <= 0:
            continue
        r = (it.get('eff_total') or 0) / th
        if r <= 0:
            continue
        cands.append((it['tk'], r, it.get('blocked', False)))
    cands.sort(key=lambda x: -x[1])

    # 컷오프: 5위 ratio. 후보가 5 미만이면 빈 슬롯 → 컷오프 0
    cutoff = cands[max_slots - 1][1] if len(cands) >= max_slots else 0.0
    open_slots = max(0, max_slots - len(cands))

    cards = []
    if open_slots > 0 and cands:
        cards.append((99.0,
            '<div class="hbox" style="border-color:#4ade80;background:rgba(74,222,128,0.06)">'
            '<div>🎰 <span style="font-size:13px;font-weight:800">빈 슬롯 %d개</span> '
            '<span style="color:#4ade80;font-weight:700;font-size:11px">경쟁 부재</span></div>'
            '<div style="font-size:10px;margin-top:4px">후보 %d종 &lt; 슬롯 %d — '
            '양수 점수는 감시 후보 · 입력·신호·게이트·슬롯·계좌 검증 별도</div></div>' % (open_slots, len(cands), max_slots)))

    for tk, r, blk in cands:
        ratio_c = (r / cutoff) if cutoff > 0 else None
        if tk in held:
            # 🆕 v9.2.39 ① 이탈권: 보유인데 이미 컷오프 아래 — 근접이 아니라 확정 열위
            if ratio_c is not None and ratio_c < 1.0:
                short = (1.0 - ratio_c) * 100
                cards.append((300 + short,
                    '<div class="hbox" style="border-color:#f87171;background:rgba(248,113,113,0.08)">'
                    '<div>🔴 <span style="font-size:13px;font-weight:800">%s %s</span> '
                    '<span style="color:#f87171;font-weight:700;font-size:11px">⛔ 이탈권 (Top%d 밖)</span></div>'
                    '<div style="font-size:10px;margin-top:4px">ratio <b>%.2fx</b> · 컷오프 %.2fx '
                    '· 부족 <b>%.0f%%</b> — 다음 진입 스캔 시 교체 대상</div></div>'
                    % (EMOJIS.get(tk, ''), tk, max_slots, r, cutoff, short)))
            # 탈락 근접: 컷오프 대비 1.0~1.25배 (아래로 밀리기 직전)
            elif ratio_c is not None and 1.0 <= ratio_c <= 1.25:
                margin = (ratio_c - 1.0) * 100
                cards.append((100 - margin,
                    '<div class="hbox" style="border-color:#f39c12;background:rgba(243,156,18,0.06)">'
                    '<div>⚠️ <span style="font-size:13px;font-weight:800">%s %s</span> '
                    '<span style="color:#f39c12;font-weight:700;font-size:11px">🔻 탈락 근접</span></div>'
                    '<div style="font-size:10px;margin-top:4px">ratio <b>%.2fx</b> · 컷오프 %.2fx '
                    '· 여유 <b>+%.0f%%</b> — 소폭 하락 시 Top%d 이탈</div></div>'
                    % (EMOJIS.get(tk, ''), tk, r, cutoff, margin, max_slots)))
        else:
            # 🆕 v9.2.39 ② 진입 자격 충족: 미보유인데 이미 컷오프 이상 — 스캔만 기다리는 상태
            if ratio_c is not None and ratio_c >= 1.0:
                over = (ratio_c - 1.0) * 100
                cards.append((200 + over,
                    '<div class="hbox" style="border-color:#4ade80;background:rgba(74,222,128,0.10)">'
                    '<div>🟢 <span style="font-size:13px;font-weight:800">%s %s</span> '
                    '<span style="color:#4ade80;font-weight:700;font-size:11px">✅ 진입 자격 충족 (Top%d 권)</span></div>'
                    '<div style="font-size:10px;margin-top:4px">ratio <b>%.2fx</b> · 컷오프 %.2fx '
                    '· 초과 <b>+%.0f%%</b> — 다음 진입 스캔 시 편입 유력%s</div></div>'
                    % (EMOJIS.get(tk, ''), tk, max_slots, r, cutoff, over,
                       ' · 🔒 Gate 차단(잠재 기준)' if blk else '')))
            # 진입 근접: 컷오프 대비 0.8~1.0배 (조금만 오르면 진입)
            elif ratio_c is not None and 0.80 <= ratio_c < 1.0:
                gap = (1.0 - ratio_c) * 100
                cards.append((50 - gap,
                    '<div class="hbox" style="border-color:#4ade80;background:rgba(74,222,128,0.06)">'
                    '<div>🎯 <span style="font-size:13px;font-weight:800">%s %s</span> '
                    '<span style="color:#4ade80;font-weight:700;font-size:11px">🔺 진입 근접</span></div>'
                    '<div style="font-size:10px;margin-top:4px">ratio <b>%.2fx</b> · 컷오프 %.2fx '
                    '· 부족 <b>%.0f%%</b>%s</div></div>'
                    % (EMOJIS.get(tk, ''), tk, r, cutoff, gap,
                       ' · 🔒 Gate 차단(잠재 기준)' if blk else '')))

    if not cards:
        return ('<div class="hbox" style="border-color:#4ade80;background:rgba(34,197,94,0.06)">'
                '<div>✅ <span style="font-size:12px">Top%d 진입·탈락 근접 없음</span></div>'
                '<div style="font-size:10px;margin-top:4px;color:#64748b">컷오프 %.2fx · 후보 %d종</div></div>'
                % (max_slots, cutoff, len(cands)))
    cards.sort(key=lambda x: -x[0])
    return ''.join(c for _, c in cards[:5])   # 🆕 v9.2.39 상한 3→5 (신설 2종 수용)


def render_risk_board_holdings(portfolio, macro, real_account=None):
    """[S277] 보유 종목 최근접 ExSn(청산) 트리거 임박 카드. 전부 매도 트리거(매수 아님).
    real_account 있으면 실보유 기준, 없으면 모델 포지션. 근접(>=0.70)만 노출."""
    def _f(k):
        try: return float(macro.get(k))
        except Exception: return None
    WTI, VIX, TNX, DXY = _f("WTI"), _f("VIX"), _f("TNX"), _f("DXY")
    EXW = (_ENGINE_EXSN.get("WTI") or _ENGINE_EXSN_FALLBACK["WTI"])
    EXV = (_ENGINE_EXSN.get("VIX") or _ENGINE_EXSN_FALLBACK["VIX"])
    NEAR, STRONG = 0.70, 0.90
    FULL = " → 전량청산(매도)"
    HALF = " → 50% 부분청산(매도)"
    def _st(px):
        if px >= STRONG: return ("\U0001F534 발동" if px >= 1.0 else "\U0001F534 임박"), "#e74c3c"
        if px >= NEAR: return "\U0001F7E1 근접", "#f39c12"
        return "\U0001F7E2 여유", "#4ade80"
    holds = real_account if real_account else portfolio
    src_lbl = "실계좌" if real_account else "모델"
    cards = []
    for tk, w in sorted(holds.items(), key=lambda x: -x[1]):
        try: wv = float(w)
        except Exception: continue
        if wv <= 0: continue
        rows = []
        wt = EXW.get(tk)
        if wt and WTI: rows.append(("WTI&gt;%d%s" % (int(wt), FULL), WTI, wt, WTI/wt))
        vt = EXV.get(tk)
        if vt and VIX: rows.append(("VIX&gt;%d%s" % (int(vt), FULL), VIX, vt, VIX/vt))
        if tk == "SLV" and TNX: rows.append(("TNX&gt;4.8%s" % HALF, TNX, 4.8, TNX/4.8))
        if tk == "EWZ" and DXY: rows.append(("DXY&gt;105%s" % HALF, DXY, 105, DXY/105))
        if tk == "TLT" and DXY: rows.append(("DXY&gt;100%s" % HALF, DXY, 100, DXY/100))
        if not rows: continue
        nm, v, thr, px = max(rows, key=lambda x: x[3])
        if px < NEAR: continue
        lbl, col = _st(px)
        cards.append(
            '<div class="hbox" style="border-color:%s;background:rgba(248,113,113,0.06)">'
            '<div>⚠️ <span style="font-size:14px;font-weight:900">%s %.1f%%</span> '
            '<span style="color:%s;font-weight:700;font-size:11px">%s</span></div>'
            '<div style="font-size:10px;margin-top:4px">%s · 현재 %.4g / 임계 %.4g = <b>%.1f%%</b></div></div>'
            % (col, tk, wv, col, lbl, nm, v, thr, px*100))
    if not cards:
        return '<div class="hbox" style="border-color:#4ade80;background:rgba(34,197,94,0.06)"><div style="font-size:11px">✅ %s 보유 청산 트리거 근접 없음</div></div>' % src_lbl
    return "".join(cards)

def render_risk_board_concentration(portfolio, cap_pct=70.0):
    """🆕 v9.2.35 [S285 #3]: 단일종목 집중도 카드 — 소프트캡(Crown #98 water-filling) 상태 가시화.
    portfolio 값은 % 단위. 캡 발동 시 성격(설계 산출 + 검증 근거)을 명시해
    편중 재질문·오독을 차단하고, 미발동 시 여유를 표시한다. 표시 전용."""
    try:
        if not portfolio:
            return ""
        tk, wv = max(portfolio.items(), key=lambda kv: float(kv[1]))
        wv = float(wv)
    except Exception:
        return ""
    if wv >= cap_pct - 0.5:   # 캡 발동 (반올림 여유 0.5p)
        return ('<div class="hbox" style="border-color:#f59e0b;background:rgba(245,158,11,0.06)">'
                '<div>⚖️ <span style="font-size:14px;font-weight:900">집중도 %s %.1f%%</span> '
                '<span style="color:#fbbf24;font-weight:700;font-size:11px">소프트캡 %.0f%% 발동</span></div>'
                '<div style="font-size:10px;margin-top:4px">Crown 98 water-filling 설계 산출 · '
                '캡 스윕 5점 중 0.70만 RULE29+STRESS 14/14 통과 · '
                '초과분은 잔여 종목 재배분</div></div>'
                % (tk, wv, cap_pct))
    return ('<div class="hbox" style="border-color:#4ade80;background:rgba(34,197,94,0.06)">'
            '<div>⚖️ <span style="font-size:12px;font-weight:700">집중도 여유</span> '
            '<span style="font-size:10px;color:#94a3b8">최대 %s %.1f%% &lt; 캡 %.0f%%</span></div></div>'
            % (tk, wv, cap_pct))

def load_position_ledger_full():
    """🆕 v9.2.49: 원장 전문 로드 (meta 가 아니라 positions/fills 포함).
    부재 시 None — 종전 재현값 동작으로 폴백한다(위조 0)."""
    try:
        import json as _json
        p = os.environ.get("ARGUS_POSITION_LEDGER", os.path.join(SCRIPT_DIR, "argus_position_ledger_causal.json"))
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            j = _json.load(f)
        return j if isinstance(j, dict) and isinstance(j.get("positions"), dict) else None
    except Exception as e:
        print(f"  ⚠️ 원장 로드 실패({type(e).__name__}) — 재현값 폴백")
        return None


def load_transition_module():
    """🆕 v9.2.49: 전이 레인 로드. 규칙 사본을 만들지 않고 판정을 위임하기 위함."""
    import importlib.util as _il
    p = os.path.join(SCRIPT_DIR, "argus_position_transition.py")
    if not os.path.exists(p):
        return None
    try:
        sp = _il.spec_from_file_location("argus_position_transition", p)
        m = _il.module_from_spec(sp)
        sp.loader.exec_module(m)
        return m
    except Exception as e:
        print(f"  ⚠️ 전이 레인 로드 실패({type(e).__name__}) — 재현값 폴백")
        return None


def ledger_recent_fills(ledger, dates):
    """🆕 v9.2.49: 전일 대비 실제 체결 — 직전 거래일 이후의 fills 만."""
    if not ledger or len(dates) < 2:
        return []
    prev = str(dates[-2])[:10]
    return [f for f in (ledger.get("fills") or []) if str(f.get("date", ""))[:10] > prev]


def display_target_percent(weights, cash):
    """합계가 정확히 100이 되도록 표시 반올림 잔차만 배분한다."""
    values = {**weights, '__cash__': cash}
    scaled = {k: float(v) * 10000 for k, v in values.items()}
    units = {k: int(np.floor(v + 1e-10)) for k, v in scaled.items()}
    remaining = 10000 - sum(units.values())
    if remaining < 0 or remaining > len(units):
        raise ValueError('목표 표시 합계 오류')
    for key in sorted(units, key=lambda k: -(scaled[k] - units[k]))[:remaining]:
        units[key] += 1
    return ({k: units[k] / 100 for k in weights}, units['__cash__'] / 100)


def render_simulated_holdings():
    """체결된 모의수량 평가비중을 판단 목표와 별도로 표시한다."""
    if not _SIMULATED_STATE:
        return ''
    rows = ''.join('<tr><td>%s</td><td>%.2f%%</td></tr>' % (_html.escape(t), w*100)
                   for t, w in sorted(_SIMULATED_STATE['weights'].items(), key=lambda x: -x[1]))
    rows += '<tr><td>현금</td><td>%.2f%%</td></tr>' % (_SIMULATED_STATE['cash']*100)
    return ('<div style="margin-top:10px"><b>체결 후 모의보유 비중</b>'
            '<div>수정주가 단위의 모의수량 평가 결과이며 실제 증권사 보유가 아닙니다.</div>'
            '<table><tr><th>종목</th><th>모의보유</th></tr>' + rows + '</table></div>')


def render_repro_footnote(repro, target):
    """🆕 v9.2.49: 재현값 대조 각주 — 강등된 참고 정보.

    엔진 재현값은 실계좌가 밟은 적 없는 경로의 종착점이다. 지시 근거가 아니며,
    원장 기준과 얼마나 벌어져 있는지를 보여주는 용도로만 남긴다.
    """
    if not repro:
        return ""
    E = _html.escape
    keys = sorted(set(repro) | set(target), key=lambda k: -max(repro.get(k, 0), target.get(k, 0)))
    rows, maxd = [], 0.0
    for k in keys:
        a = float(target.get(k, 0.0)); b = float(repro.get(k, 0.0))
        maxd = max(maxd, abs(a - b))
        col = "#f87171" if abs(a - b) >= 5 else ("#fbbf24" if abs(a - b) >= 1 else "#4ade80")
        rows.append('<span style="color:%s;white-space:nowrap">%s %.1f→%.1f (%+.1fp)</span>'
                    % (col, E(k), a, b, b - a))
    return ('<details style="margin-top:8px"><summary style="cursor:pointer;color:#64748b;font-size:11px">'
            '\U0001F9EE 판단 목표와 모의보유 대조 (실계좌 아님) · 최대 괴리 %.1f%%p</summary>'
            '<div style="font-size:11px;line-height:2.0;padding:6px 2px">%s</div>'
            '<div style="font-size:10px;color:#94a3b8;margin-top:4px">'
            '재현값 = run_prima4 final_weights. 보유 상태를 입력받는 파라미터가 없어 '
            '"처음부터 이 규칙으로 굴렸다면" 의 종착점이며, Crown 격상마다 과거 경로째 다시 그려진다. '
            '표기 순서는 판단 목표 → 모의보유. 실제 증권사 계좌 비중이 아닙니다.</div></details>'
            % (maxd, " · ".join(rows)))


def load_position_ledger_meta():
    """🔴 v9.2.53 [LEDGERDAILY]: 원장 메타 로드 — 스키마 v2.0 필드를 1순위로 읽는다.

    v2.0 원장 = 당일 엔진 산출을 동결한 기록(백필 차단). 브로커리지 장부가 아니다.
    v1.0 의 last_reconciled 는 v2.0 에 존재하지 않으므로 폴백으로만 유지한다 —
    종전 코드는 이 키를 무조건 읽어 빈 문자열을 조용히 출력했다.
    부재/파싱 실패 = None (N/A 표시, 위조 금지)."""
    try:
        import json as _json
        p = os.environ.get("ARGUS_POSITION_LEDGER", os.path.join(SCRIPT_DIR, "argus_position_ledger_causal.json"))
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            j = _json.load(f)
        # 🔴 v9.2.70 LEDGERCOVER: 머리 행만 읽으면 누적 결손이 보이지 않는다.
        #   history 의 as_of 집합과 gap_note 를 함께 실어 커버리지 판정을 가능하게 한다.
        _hist = [r for r in (j.get("history") or []) if isinstance(r, dict)]
        _sess = set()
        for _r in [j] + _hist:
            _a = str(_r.get("as_of", ""))[:10]
            if _a:
                _sess.add(_a)
        _gaps = [g for g in (j.get("gap_note") or []) if isinstance(g, dict)]
        return {
            "as_of":  str(j.get("as_of", "")),
            "schema": str(j.get("schema_version", "") or "?"),
            "recorded_at": str(j.get("recorded_at", "") or ""),
            "crown":  str(j.get("crown", "") or ""),
            "rule_change": bool(j.get("rule_change", False)),
            # 구 스키마 폴백 — v2.0 에는 없는 키다
            "recon":  str(j.get("last_reconciled", "") or ""),
            # 🆕 v9.2.70 — 커버리지 판정 입력. 값을 만들어내지 않고 원장에 있는 것만 싣는다.
            "sessions": sorted(_sess),
            "first_as_of": (min(_sess) if _sess else ""),
            "rows": len(_sess),
            "gap_notes": _gaps,
            "gap_count": len(_gaps),
            "gap_bdays": sum(int(g.get("missing_bdays") or 0) for g in _gaps),
        }
    except Exception:
        return None


def ledger_coverage(meta, src_date):
    """🔴 v9.2.70 [LEDGERCOVER]: 원장 개시일~기준일 구간의 세션 커버리지.

    원장 스키마 R1 은 '각 영업일의 산출을 그날 동결'이다. 따라서 완전성은
    머리 행의 신선도가 아니라 **구간 전체의 세션 충족률**로만 판정된다.
    v9.2.53~v9.2.69 의 배지는 머리 행과 기준일만 비교해 gap 0 → 🟢 였고,
    그 사이 결손 9세션(실측 2026-08-13~09-18)을 한 번도 표시하지 않았다.

    반환: dict(recorded, total, missing, missing_days) · 판정 불가 시 None.
    누락일은 원장이 이미 아는 사실만 쓴다 — 달력 조회가 실패하면 판정하지 않는다.
    """
    try:
        import exchange_calendars as xcals
        if not meta or not meta.get("first_as_of"):
            return None
        cal = xcals.get_calendar("XNYS")
        d0 = pd.Timestamp(meta["first_as_of"])
        d1 = pd.Timestamp(src_date)
        if pd.isna(d0) or pd.isna(d1) or d0 > d1:
            return None
        sess = [str(x)[:10] for x in cal.sessions_in_range(d0, d1)]
        if not sess:
            return None
        have = set(meta.get("sessions") or ())
        miss = [x for x in sess if x not in have]
        return {"recorded": len(sess) - len(miss), "total": len(sess),
                "missing": len(miss), "missing_days": miss}
    except Exception:
        return None

def ledger_missing_bdays(as_of, src_date):
    """🔴 v9.2.53 [LEDGERDAILY]: 원장에 기록되지 않은 영업일 수.

    스키마 v2.0 R1/R3 — 원장은 매 영업일 그날의 엔진 산출을 동결한다.
    데이터 기준일 D 를 렌더할 때 원장 최신 행은 D(당일 기록 완료) 또는
    D 의 직전 영업일(R3 의 '직전 영업일 행')이면 정상이다.
    그보다 오래되면 그 사이 영업일에 기록이 없었다는 뜻이다.

      gap     = as_of 다음 영업일부터 D 까지의 영업일 수
      missing = max(gap - 1, 0)   # 건너뛴 영업일 수

    반환: (missing, gap) · 파싱 실패 시 (None, None)
    """
    try:
        import exchange_calendars as xcals
        cal = xcals.get_calendar("XNYS")
        d0 = pd.Timestamp(as_of)
        d1 = pd.Timestamp(src_date)
        if pd.isna(d0) or pd.isna(d1) or d0 > d1:
            return None, None
        if not cal.is_session(d0) or not cal.is_session(d1):
            return None, None
        gap = len(cal.sessions_in_range(d0, d1)) - 1
        return max(gap - 1, 0), gap
    except Exception:
        return None, None


def render_ledger_badge(_src_date):
    """🔴 v9.2.53 [LEDGERDAILY]: 원장 일일 기록 배지.

    종전(v9.2.35~v9.2.52)은 '5영업일 초과 지연' 만 경고했다. 그 임계는 원장을
    정기 대사 장부로 보던 시절 설계이며, 스키마 v2.0 의 일일 동결 기록에는
    맞지 않는다. 1영업일만 건너뛰어도 R3 의 '직전 영업일 행'이 성립하지 않아
    전이 지시가 누적 차이로 부풀고, 같은 지시가 매일 재방출된다.
    부재 시 회색 N/A (위조 금지)."""
    meta = load_position_ledger_meta()
    if not meta or not meta.get("as_of"):
        return '<span style="color:#64748b">\U0001F4D2 원장 N/A (로컬 미배치)</span>'
    missing, _gap = ledger_missing_bdays(meta["as_of"], _src_date)
    # 🔴 v9.2.70 LEDGERCOVER: 머리 지연(head)과 누적 결손(cover)을 둘 다 판정에 넣는다.
    cov = ledger_coverage(meta, _src_date)
    _cov_miss = None if cov is None else int(cov["missing"])
    if missing is None:
        col, mark = "#64748b", "? 판정 불가(날짜·거래소 달력 확인 필요)"
    elif missing == 0 and _cov_miss is None:
        col, mark = "#64748b", "머리 행 최신 · 누적 커버리지 판정 불가"
    elif missing == 0 and _cov_miss == 0:
        col, mark = "#4ade80", "✅ 일일 기록"
    elif missing == 0:
        col = "#f87171" if _cov_miss > 2 else "#fbbf24"
        mark = ("\U0001F534 머리 행 최신이나 누적 결손 %d세션 (R1 일일 동결 미이행)"
                % _cov_miss)
    elif missing <= 2:
        col, mark = "#fbbf24", "\U0001F7E1 기록 결손 %d영업일" % missing
    else:
        col, mark = "#f87171", "\U0001F534 기록 결손 %d영업일 (R1 일일 동결 미이행)" % missing
    _schema = meta.get("schema") or "?"
    _rec = meta.get("recorded_at") or meta.get("recon") or "?"
    _crown = (" · %s" % meta["crown"]) if meta.get("crown") else ""
    _rc = ' · <span style="color:#fbbf24">규칙변경일</span>' if meta.get("rule_change") else ""
    _warn = ""
    if missing and missing > 0:
        _warn = ('<div style="font-size:10px;color:#f87171;margin-top:3px">'
                 '원장 머리 날짜 %s의 지연이 확인됐습니다 — '
                 '유효한 직전 거래일 기록이 없으면 목표 변화 비교를 보류합니다.</div>' % meta["as_of"])
    # 🆕 v9.2.70 — 커버리지 실측을 화면에 남긴다. 결손은 backfill 금지(DIR-S289_2 P6)
    #   대상이므로 '앞으로 안 생기게' 만드는 것 외에 복구 경로가 없다. 그러니 보이게 한다.
    if cov is not None:
        _pct = (cov["recorded"] / cov["total"] * 100.0) if cov["total"] else 0.0
        _cc = "#4ade80" if cov["missing"] == 0 else "#f87171"
        _last = ", ".join(cov["missing_days"][-6:])
        _gn = ""
        if meta.get("gap_count"):
            _gn = (" · gap_note %d건 / 누적 %d영업일"
                   % (meta["gap_count"], meta["gap_bdays"]))
        _warn += ('<div style="font-size:10px;color:%s;margin-top:3px">'
                  '선택된 원장 개시 이후 커버리지 %d/%d 세션 (%.1f%%) · 미기록 %d세션%s%s</div>'
                  % (_cc, cov["recorded"], cov["total"], _pct, cov["missing"], _gn,
                     ('<br><span style="color:#94a3b8">최근 미기록: %s — 소급 기록은 '
                      'DIR-S289_2 P6 로 금지되므로 복구되지 않는다</span>'
                      % _html.escape(_last)) if cov["missing"] else ""))
    _warn += ('<div style="font-size:10px;color:#94a3b8">측정 시작: '
              + _html.escape(str(meta.get('first_as_of') or '미확인'))
              + ' · 선택된 원장 범위만 측정하며 이전 원장 전체의 복구를 의미하지 않습니다.</div>')
    return ('<span style="color:%s">\U0001F4D2 원장 as_of %s · schema %s · 기록 %s%s%s %s</span>%s'
            % (col, meta["as_of"], _schema, _rec, _crown, _rc, mark, _warn))

def render_risk_board_drift(portfolio, real_account):
    """[S277] 실계좌 -> 모델 목표 드리프트 카드. real_account 없으면 미표시."""
    if not real_account: return ""
    tickers = sorted(set(real_account) | set(portfolio), key=lambda t: -(float(real_account.get(t,0))+float(portfolio.get(t,0))))
    items = []
    for t in tickers:
        a = float(real_account.get(t,0)); mo = float(portfolio.get(t,0)); d = mo - a
        if abs(d) >= 10: col, mk = "#e74c3c", "\U0001F534"
        elif abs(d) >= 5: col, mk = "#f39c12", "\U0001F7E1"
        else: col, mk = "#4ade80", "\U0001F7E2"
        items.append('<span style="color:%s;white-space:nowrap">%s %s %.1f→%.1f (%+.1fp)</span>' % (col, mk, t, a, mo, d))
    return ('<div class="card" style="border-left:4px solid #f59e0b;padding-left:14px">'
            '<div class="ct" style="color:#fbbf24">\U0001F4CA 리밸런싱 드리프트 (실계좌 → 모델 목표)</div>'
            '<div style="font-size:11px;line-height:2.0">' + " · ".join(items) + '</div>'
            '<div style="font-size:10px;color:#94a3b8;margin-top:4px">\U0001F534 |Δ|≥10p 리밸필요 · \U0001F7E1 ≥5p 근접 · real_account.json</div>')



def _fmt_shares(v):
    """브로커 주수 표시 — 정수 주수는 소수점 없이, 분할주면 최대 4자리."""
    try:
        x = float(v)
        if not np.isfinite(x):
            return "?"
        if abs(x - round(x)) < 1e-9:
            return f"{int(round(x)):,}"
        return f"{x:,.4f}".rstrip('0').rstrip('.')
    except Exception:
        return "?"


def render_broker_alignment(transition):
    """🆕 v9.2.57: 실제 브로커 보유 → 엔진 목표 정렬 카드.

    규칙/주문 판단을 여기서 재계산하지 않는다. argus_position_transition.py가 만든
    brokerage_transition/1.1을 **표시만** 한다. cash.amount=null이면 구조적으로 확정 가능한
    SELL_ALL/NEW_BUY만 표시하고, 금액·매수 주수·정확 비중은 잠근다.
    ACTION_READY=False이면 카드 전체를 차단 블록으로 대체해 SELL/BUY 항목을 렌더하지 않는다.
    """
    if not _ACTION_READY or not _ACTION_READY.get("ready"):
        _dd = _ACTION_READY.get("data_date") or "?"
        reason = "<br>".join(_action_gate_reason_lines(_dd))
        return (
            '<div class="card al" style="border-left-color:#f87171">'
            '<div class="ct">💼 Broker Alignment '
            '<span style="font-size:10px;color:#64748b">실제 브로커 보유 → 엔진 목표</span></div>'
            '<div class="hbox" style="border-color:#f87171;background:rgba(248,113,113,0.14)">'
            '<div style="font-weight:900;color:#f87171;font-size:13px">🚫 행동 지시 차단</div>'
            '<div style="font-size:11px;color:#fca5a5;line-height:1.9;margin-top:5px">%s</div>'
            '<div style="font-size:10px;color:#94a3b8;margin-top:6px">'
            'ACTION_READY=False 동안 SELL/BUY 방향과 주문 항목은 화면에 존재하지 않습니다.</div>'
            '</div></div>' % (reason or "ACTION_READY 미확정"))

    b = _ALIGNMENT
    if not b.get('available'):
        return ('<div class="card al" style="border-left-color:#64748b">'
                '<div class="ct">💼 Broker Alignment</div>'
                '<div class="hbox" style="border-color:#64748b;background:rgba(100,116,139,0.08)">'
                '<span style="font-weight:800;color:#94a3b8">⚪ 실보유 SSOT 미연결</span> '
                '<span style="color:#64748b;font-size:11px">— argus_real_holdings.json 기반 brokerage transition 없음. '
                '엔진 상태와 실제 계좌 정렬 여부를 이 카드에서 판정하지 않습니다.</span></div></div>')

    orders = [o for o in (b.get('orders') or []) if str(o.get('action')) != 'HOLD']
    unresolved = list(b.get('unresolved') or [])
    actionable = bool(b.get('actionable'))
    orders_computable = bool(b.get('orders_computable'))
    only_cash_lock = bool(unresolved) and set(unresolved) == {'cash.amount'}

    # REBALANCE_UNRESOLVED는 현금 미확정으로 방향까지 잠긴 상태다.
    hard_orders = [o for o in orders if str(o.get('action')) != 'REBALANCE_UNRESOLVED']
    locked_orders = [o for o in orders if str(o.get('action')) == 'REBALANCE_UNRESOLVED']
    n = len(orders)
    if b.get('blocked_orders'):
        status = f'⚠️ 계좌 차이 {n}건 · 매수 제한 {len(b["blocked_orders"])}건'
        scol, sbg = '#fbbf24', 'rgba(251,191,36,0.08)'
    elif actionable:
        status = f'🚨 정렬 필요 {n}건'
        scol, sbg = '#f87171', 'rgba(248,113,113,0.10)'
    elif locked_orders:
        status = f'⚠️ 정렬 방향 잠금 {len(locked_orders)}건'
        scol, sbg = '#fbbf24', 'rgba(251,191,36,0.08)'
    elif n == 0:
        status = '✅ 정렬 완료'
        scol, sbg = '#4ade80', 'rgba(74,222,128,0.08)'
    else:
        status = f'ℹ️ 정렬 확인 {n}건'
        scol, sbg = '#94a3b8', 'rgba(148,163,184,0.08)'

    h = ('<div class="card al" style="border-left-color:%s">'
         '<div class="ct">💼 Broker Alignment <span style="font-size:10px;color:#64748b">실제 브로커 보유 → 엔진 목표</span></div>'
         '<div class="hbox" style="border-color:%s;background:%s">'
         '<span style="font-size:16px;font-weight:900;color:%s">%s</span></div>'
         % (scol, scol, sbg, scol, status))

    if orders:
        h += '<div style="font-size:11px;line-height:1.9;margin:3px 0 8px">'
        for o in orders:
            tk = _html.escape(str(o.get('ticker', '')))
            act = str(o.get('action') or '')
            sh = _fmt_shares(o.get('shares', 0))
            tw = o.get('target_weight')
            twp = (float(tw) * 100.0) if tw is not None else None
            if act == 'BUY_BLOCKED':
                h += f'<div>🔒 <b>{tk} 매수 제한</b> · 목표와 계좌 차이는 있으나 진입 조건 미충족·미확인</div>'
            elif act == 'SELL_ALL':
                h += (f'<div>🔴 <b>청산 {tk}</b> · 실보유 {sh}주 '
                      f'<span style="color:#94a3b8">— 엔진 목표 0%</span></div>')
            elif act == 'NEW_BUY':
                tgt = f'{twp:.1f}%' if twp is not None else '?'
                h += (f'<div>🟢 <b>신규매수 {tk}</b> · 목표 {tgt} '
                      f'<span style="color:#94a3b8">— 실보유 0주 → 엔진 목표</span></div>')
            elif act == 'ADD':
                cw = o.get('current_weight'); dw = o.get('delta_weight')
                cwp = f'{float(cw)*100:.1f}%' if cw is not None else '?'
                tgt = f'{twp:.1f}%' if twp is not None else '?'
                h += f'<div>🟢 <b>추가매수 {tk}</b> · {cwp} → {tgt}</div>'
            elif act == 'REDUCE':
                cw = o.get('current_weight')
                cwp = f'{float(cw)*100:.1f}%' if cw is not None else '?'
                tgt = f'{twp:.1f}%' if twp is not None else '?'
                h += f'<div>🟠 <b>부분매도 {tk}</b> · {cwp} → {tgt}</div>'
            elif act == 'REBALANCE_UNRESOLVED':
                tgt = f'{twp:.1f}%' if twp is not None else '?'
                h += (f'<div>⚪ <b>재조정 {tk}</b> · 실보유 {sh}주 · 목표 {tgt} '
                      f'<span style="color:#fbbf24">— 현금 미확정으로 증감 방향 잠금</span></div>')
            else:
                h += f'<div>⚪ <b>{tk}</b> · {_html.escape(act)}</div>'
        h += '</div>'

    pos = b.get('positions') or {}
    if pos:
        ph = ' / '.join(f'{_html.escape(str(tk))} {_fmt_shares(p.get("shares",0))}주'
                        for tk, p in sorted(pos.items()))
        h += (f'<div style="font-size:11px;color:#94a3b8;margin-top:5px">'
              f'<span style="color:#64748b">실제 브로커 보유 </span>{ph}</div>')

    target = b.get('target_weights') or {}
    if target:
        th = ' / '.join(f'{_html.escape(str(tk))} {float(w)*100:.1f}%'
                        for tk, w in sorted(target.items(), key=lambda kv: -float(kv[1])) if float(w) > 0)
        h += (f'<div style="font-size:11px;color:#94a3b8;margin-top:3px">'
              f'<span style="color:#64748b">엔진 목표 </span>{th}</div>')

    if not orders_computable:
        if only_cash_lock:
            h += ('<div class="hbox" style="margin-top:8px;border-color:#fbbf24;background:rgba(251,191,36,0.06);font-size:11px">'
                  '<span style="font-weight:800;color:#fbbf24">🔒 주문 금액·매수 수량 계산 잠금</span> '
                  '<span style="color:#94a3b8">— 실계좌 금액은 Commander 관리. cash.amount=null 정책을 유지하며 '
                  'ARGUS는 확정 가능한 매도 주수와 매수 방향만 표시합니다.</span></div>')
        else:
            h += ('<div class="hbox" style="margin-top:8px;border-color:#fbbf24;background:rgba(251,191,36,0.06);font-size:11px">'
                  '<span style="font-weight:800;color:#fbbf24">🔒 정확 주문 산출 잠금</span> '
                  '<span style="color:#94a3b8">— 미확정: %s</span></div>'
                  % _html.escape(', '.join(str(x) for x in unresolved) or 'unknown'))

    stmt = _html.escape(str(b.get('as_of_statement') or '?'))
    market = _html.escape(str(b.get('market_as_of') or '?'))
    h += (f'<div style="font-size:9px;color:#475569;margin-top:6px">'
          f'실보유 statement {stmt} · 시장 기준 {market} · brokerage_transition/1.1 · '
          f'실계좌 금액 추정 금지</div></div>')
    return h

def generate_html(result, portfolio, engine_name, crown_num, cash_pct=0.0, aaqg=None, final_positions=None, equity=None, chart_html="", return_rank_html="", engine_ok=True, data_date=None, transition=None, repro=None, ledger=None):
    _RATIONALE_CONTEXT.clear()
    _RATIONALE_CONTEXT.update(result)
    final_positions = final_positions or {}  # 🆕 v9.1.1: run_prima4 final_positions (보유일/잔여일)
    # 🆕 v9.1.3: equity = run_prima4 equity 시리즈 (트레일링 성과용). result(evaluate_all)에는 equity 없음
    aaqg_grades = aaqg[0] if aaqg else {}
    aaqg_marks = aaqg[4] if aaqg and len(aaqg) > 4 else {}
    aaqg_cat = aaqg[5] if aaqg and len(aaqg) > 5 else {}
    """evaluate_all 결과 → v2 HTML"""
    macro = result.get('macro', {})
    gates = result.get('gates', {})
    tks = result.get('tickers', {})
    ps = result.get('per_signal', {})
    wk_blocked = gates.get('general', {}).get('blocked', False)
    eval_date = result.get('evaluated_at_date', '?')
    # 🔧 v9.2.15 [SRCDATE-FIX]: 데이터 기준일은 df 마지막 행 실제 날짜(data_date)로 산정.
    #   v9.2.14 결함 — result['evaluated_at_date']는 시퀀스 번호(예: 393)라
    #   날짜 라벨/신선도 파싱 불가 → '기준일 불명' 폴백. df['Date'] 실제 날짜를 단일 원천으로 사용.
    _src_date = str(data_date)[:10] if data_date is not None else str(eval_date)
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")  # GHA UTC 러너에서도 KST 정확 표기
    held_tickers = list(portfolio.keys())

    # 전종목 점수 정렬
    scored = []
    for tk, info in tks.items():
        sc = info.get('entry_score', 0) or 0
        th = info.get('entry_threshold', 1) or 1
        ratio = sc / th if th else 0
        grade = aaqg_grades.get(tk) or ('S' if ratio >= 3 else 'A' if ratio >= 2 else 'B' if ratio >= 1.5 else 'C' if ratio >= 1 else 'D')  # AAQG 우선
        blocked = info.get('gate_blocked', False)
        active_sigs = ps.get(tk, {})
        # 🔴 REG-S268_3 처방 (S268): elif 배타(⊘) 억제 신호가 재가산되던 결함 차단.
        #   build_signals_html()의 화면 렌더(cum)는 _compute_suppressed()로 이미 정확하나,
        #   본 pot_total은 is_active만으로 전체 재합산 → 억제 신호 이중 계상
        #   (실측: GLD +9.9→오표시 +12.9, SLV +11.0→+15.0, S268 evaluate_all() 직접 대조 확인).
        #   기존 검증된 억제기(_compute_suppressed) 재사용 — 신규 로직 없음, 단일 원천 정합.
        _sup_pt = _compute_suppressed(active_sigs)
        pot_plus = sum(v['raw_pts'] for k, v in active_sigs.items()
                       if v.get('is_active') and k not in _sup_pt and v['raw_pts'] > 0)
        pot_minus = sum(v['raw_pts'] for k, v in active_sigs.items()
                        if v.get('is_active') and k not in _sup_pt and v['raw_pts'] < 0)
        # 🔴 REG-S268_2 처방 (S271): Gate OPEN 종목은 엔진 정본 entry_score(sc) 표시.
        #   pot_total(per_signal 재합산)은 인터랙션 배타(VNM DFII10∩BullStack 등)를
        #   _compute_suppressed가 그룹화 제외(interaction 보존)하여 이중 계상 → 표시 부풀림
        #   (실측 S271: VNM entry_score 4.0 ↔ pot_total 6.0). Gate BLOCKED만 pot_total(해제 잠재).
        _pt = pot_plus + pot_minus
        eff_total = _pt if blocked else sc
        scored.append({'tk': tk, 'score': sc, 'thresh': th, 'ratio': ratio, 'grade': grade,
                       'blocked': blocked, 'info': info, 'pot_plus': pot_plus, 'pot_minus': pot_minus,
                       'pot_total': _pt, 'eff_total': eff_total})
    scored.sort(key=lambda x: -x['eff_total'])

    gc_map = {"SS":"#f472b6","S":"#facc15","A":"#22d3ee","B":"#4ade80","C":"#94a3b8","D":"#475569","F":"#475569"}
    rc = lambda v: "#4ade80" if v and v > 0 else "#f87171" if v and v < 0 else "#94a3b8"

    h = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="data-date" content="{_src_date}">
<meta name="crown" content="{crown_num}">
<meta name="renderer" content="{RENDERER_VER}">
<title>🦅 ARGUS Brief — {_src_date}</title>
<style>{CSS}</style></head><body>
"""

    # 데이터 기준일(source date) + 신선도 배지 — 데이터 정체 가시화 (Commander 지시)
    #   _src_date는 상단에서 df 마지막 행 실제 날짜(data_date)로 산정(v9.2.15 SRCDATE-FIX).
    #   기준일 대비 경과 영업일(Mon-Fri)로 신선도 배지 색상 결정 → stale 시 즉시 식별.
    # 🛡️ v9.2.27 FRESHGUARD 층 2(보조): 빌드 시점 정본 대조.
    #   여기서 계산한 배지는 '생성 시점의 사실'이며 열람 시점에는 무효화될 수 있다.
    #   그래서 '(생성시)' 접미를 붙여 시점을 명시하고, 층 1(FRESHGUARD_JS)이
    #   브라우저에서 이 배지를 열람 시점 기준으로 덮어쓴다.
    _canon = _read_canonical_date()
    try:
        _y, _m, _d = map(int, _src_date.split('-'))
        _dd = datetime(_y, _m, _d).date()
        _td = datetime.now(KST).date()
        _gap, _cur = 0, _dd + timedelta(days=1)
        while _cur <= _td:
            if _cur.weekday() < 5:
                _gap += 1
            _cur += timedelta(days=1)
        if _canon and _canon == _src_date:
            _fresh = ('#94a3b8', '정본 날짜 일치 (생성시) · 최신성 별도 확인')
        elif _canon and _canon != _src_date:
            # 빌드 시점에 이미 정본보다 뒤처짐 = 워크플로 경쟁 상태 의심.
            _fresh = ('#f87171', f'🔴 STALE · 정본 {_canon}')
            print(f"🔴 FRESHGUARD(빌드): 산출 기준일 {_src_date} != 정본 {_canon}"
                  f" — fetcher 커밋 전 curl 경쟁 의심")
        else:
            _fresh = ('#94a3b8', f'⚪ 미검증 (생성시 · {_gap}영업일)')
            print("⚠️ FRESHGUARD(빌드): 정본 회수 실패 — 미검증 표기")
    except Exception:
        _fresh = ('#94a3b8', '⚪ 기준일 불명')

    # ── HEADER ──
    h += _SECT("header")
    h += f'''<div class="hdr">
<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;min-width:0;max-width:100%"><span style="font-size:22px">🦅</span>
<h1>ARGUS Daily Brief</h1>
<span class="badge bb">Crown {crown_num}</span>
<span class="badge bv">{RENDERER_VER}</span></div>
<div style="color:#94a3b8;font-size:10px;text-align:right;line-height:1.6">
📅 데이터 기준일 <b style="color:#e2e8f0">{_src_date}</b>
<span id="fg-badge" data-src="{_src_date}" data-gen="{now}" style="color:{_fresh[0]};font-weight:700">{_fresh[1]}</span><br>
🕐 생성 {now}<br>
{render_ledger_badge(_src_date)}</div></div>''' + FRESHGUARD_JS + f'''
'''

    # ── 전일 대비 변경 diff (단일 소스: Action Board 결론·의무매도 + 변경 섹션 공용) ──
    # 🔴 v9.2.49 LEDGERSRC: 전일 대비 변경 = 원장 fills 기준 실제 체결.
    #   종전에는 prima_daily_output_diff.json(재현값 diff)을 읽어, 실계좌가 움직이지
    #   않은 날에도 "청산 2건·진입 2건"이 표시됐다. 그것은 어제 재현본과 오늘 재현본의
    #   차이일 뿐 계좌에서 일어난 일이 아니다. UNIFIED부터 이 블록은 Engine State 전용이다.
    _diff = load_daily_diff(data_date, _TARGET_STATUS.get("target_weights"))
    _fill_sell, _fill_buy = [], []
    if transition is not None:
        _fills = transition.get('recent_fills') or []
        # Engine State 배지 = 엔진 원장 전일→당일 변화
        #   소비부 규약(dict 리스트: ticker/from/to)을 그대로 따른다 — 표시 코드 무수정.
        _ex_k = sorted((transition.get('exits') or {}).keys())
        _en_k = sorted((transition.get('entries') or {}).keys())
        _exited     = [{"ticker": t} for t in _ex_k]
        _entered    = [{"ticker": t} for t in _en_k]
        _reweighted = [{"ticker": o['ticker'], "from": o['current'], "to": o['target']}
                       for o in (transition.get('orders') or [])
                       if o['action'] not in ('유지',)
                       and o['ticker'] not in _en_k and o['ticker'] not in _ex_k]
        if transition.get('source') == 'causal_engine_target':
            _reweighted = [{'ticker': o['ticker'], 'from': o['previous_target'], 'to': o['target']}
                           for o in transition.get('observations', [])]
        _changed    = bool(_exited or _entered or _reweighted)
        _must_sell  = len(_exited)
        # 전일 대비 변경 카드 = 원장 fills 기준 실제 체결 (별도)
        _fill_sell  = [f for f in _fills if str(f.get('action','')).upper() == 'SELL']
        _fill_buy   = [f for f in _fills if str(f.get('action','')).upper() == 'BUY']
    else:
        # 원장 연속성을 확인하지 못한 경우 이전 산출 파일로 변경내역을 대신하지 않는다.
        _exited, _entered, _reweighted = [], [], []
        _changed, _must_sell = False, 0
    if transition is not None:
        # 엔진 상태 결론 = 동결 원장→당일 목표 변화. 브로커 실제 행동과 분리.
        _n_ex = len(transition.get('exits') or {})
        _n_en = len(transition.get('entries') or {})
        _n_rw = len(transition.get('observations', [])) + sum(1 for o in (transition.get('orders') or [])
                    if o['action'] not in ('유지',) and o['ticker'] not in (transition.get('entries') or {}))
        if _n_ex:
            _verdict, _v_color = "청산", "#f87171"
        elif _n_en or _n_rw:
            _verdict, _v_color = "조정", "#fb923c"
        else:
            _verdict, _v_color = "유지", "#4ade80"
    elif not _changed:
        _verdict, _v_color = "유지", "#4ade80"   # 무변경 → 유지(녹색)
    elif _exited:
        _verdict, _v_color = "청산", "#f87171"   # 청산 포함 → 청산(적색)
    else:
        _verdict, _v_color = "조정", "#fb923c"   # 진입·리밸만 → 조정(주황)
    _ms_color = "#f87171" if _must_sell > 0 else "#4ade80"

    # 🚨 v9.2.57 UNIFIED ACTIONGATE — stale/ungrounded/invalid 상태에서 행동 결론을 정상처럼 보이지 않는다.
    _ar = compute_action_ready(data_date, engine_ok, transition)
    h += render_target_source(data_date, engine_ok, transition)
    h += render_action_ready_banner(data_date)
    h += render_phantom_banner(portfolio, transition)
    if not (_ar.get("transition_valid") and _ar.get("ledger_contiguous")):
        _verdict, _v_color = "전일 비교 불가" if engine_ok else "목표 산출 실패", "#64748b"
        _must_sell_txt, _ms_color = "미확정", "#64748b"
        if engine_ok and (_ar.get("ledger_status") or {}).get("error") == "previous_session_missing":
            _verdict = "이전 거래일 기록 대기"
    else:
        _must_sell_txt = f"{len((transition or {}).get('observations', []))}건"

    # ── ENGINE STATE — 엔진 원장 전일→당일 상태 변화만 표시 ──
    # 🆕 UNIFIED: 실제 브로커 정렬과 의미를 분리한다.
    h += _SECT("action")
    h += f'''<div class="card al">
<div class="ct">⚙️ Engine State <span style="font-size:10px;color:#64748b">동결 엔진 원장 → 당일 엔진 목표</span></div>
<div class="g3" style="margin-bottom:10px">
<div class="stat"><div class="stat-val" style="color:{_v_color}">{_verdict}</div><div class="stat-lbl">엔진 상태</div></div>
<div class="stat"><div class="stat-val" style="color:{_ms_color}">{_must_sell_txt}</div><div class="stat-lbl">목표 변경</div></div>
<div class="stat"><div class="stat-val" style="color:#94a3b8">{cash_pct:.1f}%</div><div class="stat-lbl">엔진 현금</div></div>
</div>'''

    # 🔴 v9.2.19 fail-loud → 🆕 v9.2.21: engine_ok로 "실패"와 "정상+0종"을 분리.
    if not engine_ok:
        h += '''<div class="hbox" style="border-color:#f87171;background:rgba(248,113,113,0.14)">
<span style="font-weight:900;color:#f87171">⚠️ 데이터 없음</span>
<span style="font-size:11px;color:#fca5a5"> — run_prima4 실시간 포트폴리오 미산출. 아래 목표비중·보유상세·Risk Board 수치는 신뢰 불가(빈 상태).</span></div>'''
    elif not portfolio:
        h += f'''<div class="hbox" style="border-color:#38bdf8;background:rgba(56,189,248,0.12)">
<span style="font-weight:900;color:#38bdf8">🟦 전량 현금 (보유 0종)</span>
<span style="font-size:11px;color:#7dd3fc"> — run_prima4 정상 산출. 전 종목 청산 조건 충족으로 목표 보유가 없습니다 (현금 {cash_pct:.1f}%). 데이터 결함이 아닙니다.</span></div>'''

    # ── v9.2.20: Action Board 충전 — 변경 배지 + 변경 상세 + 현재 보유 (여백 알차게) ──
    if engine_ok and _ar.get("ready"):  # 목표 카드는 별도 유지. 미검증 변경 방향만 숨긴다.
        def _ab_badge(txt, col, bg):
            return (f'<span style="display:inline-block;padding:3px 10px;border-radius:12px;'
                    f'font-size:11px;font-weight:700;color:{col};background:{bg};margin:2px 3px 2px 0">{txt}</span>')
        h += '<div style="text-align:center;margin:0 0 8px">'
        h += _ab_badge(f"🟢 엔진 진입 {len(_entered)}", "#4ade80", "rgba(74,222,128,0.14)")
        h += _ab_badge(f"🔴 엔진 청산 {len(_exited)}",  "#f87171", "rgba(248,113,113,0.14)")
        h += _ab_badge(f"🔄 목표 변경 {len(_reweighted)}", "#fb923c", "rgba(251,146,60,0.14)")
        h += _ab_badge(f"🎰 슬롯 {len(portfolio)}/5", "#a78bfa", "rgba(167,139,250,0.14)")
        h += '</div>'
        # 변경 상세 라인 (조정 사유 자명화) — 변경 있을 때만
        if _changed:
            _p = []
            if _entered:
                _p.append("진입 " + ", ".join(e.get("ticker","") for e in _entered))
            if _exited:
                _p.append("청산 " + ", ".join(e.get("ticker","") for e in _exited))
            if _reweighted:
                _rw = []
                for r in _reweighted:
                    _fr, _to = (r.get("from") or 0) * 100, (r.get("to") or 0) * 100
                    _rw.append(f'{r.get("ticker","")}{"↓" if _to < _fr else "↑"}')
                _p.append("리밸 " + " ".join(_rw))
            if _p:
                h += (f'<div style="font-size:11px;color:#cbd5e1;text-align:center;'
                      f'margin-bottom:8px;line-height:1.6">🔀 {" · ".join(_p)}</div>')
        # 현재 보유 라인 (비중) — "지금 무엇을 들고 있나" 그라운딩
        if portfolio:   # 🆕 v9.2.21: 0종이면 생략 (위 전량현금 배너가 대체)
            # 🔴 v9.2.50 HOLDLABEL: '보유' 는 원장 실보유만. portfolio 는 목표이므로
            #   그대로 쓰면 아직 사지 않은 종목이 보유로 표기된다(v9.2.49 결함).
            if transition is not None:
                _cur = {k: v*100 for k, v in (transition.get('prev') or {}).items() if v > 0}
                _cur = dict(sorted(_cur.items(), key=lambda x: -x[1]))
                _hold = " · ".join(f'{EMOJIS.get(tk,"")} <b>{tk}</b> {w:.1f}%' for tk, w in _cur.items())
                h += (f'<div style="font-size:11px;color:#94a3b8;text-align:center;'
                      f'margin-bottom:4px;line-height:1.8"><span style="color:#64748b">전일 산출(원장) </span>{_hold}</div>')
                _tgt = " · ".join(f'{EMOJIS.get(tk,"")} <b>{tk}</b> {w:.1f}%' for tk, w in portfolio.items())
                _new = [t for t in portfolio if t not in _cur]
                _nb = (f' <span style="color:#4ade80">(신규 {", ".join(_new)} — 미보유)</span>' if _new else '')
                h += (f'<div style="font-size:11px;color:#94a3b8;text-align:center;'
                      f'margin-bottom:4px;line-height:1.8"><span style="color:#64748b">목표 </span>{_tgt}{_nb}</div>')
            else:
                _hold = " · ".join(f'{EMOJIS.get(tk,"")} <b>{tk}</b> {w:.1f}%' for tk, w in portfolio.items())
                h += (f'<div style="font-size:11px;color:#94a3b8;text-align:center;'
                      f'margin-bottom:4px;line-height:1.8"><span style="color:#64748b">보유 </span>{_hold}</div>')
        # 🆕 v9.2.39: 다음 진입 스캔 잔여 — "왜 강한 후보가 아직 안 들어왔나"의 답
        h += render_next_scan_note(final_positions, portfolio)

    # 🔴 v9.2.67 [GATEREASON] 사유는 엔진이 정한다 — 표시가 재서술하지 않는다 (결함 S291-9b)
    _gg = gates.get('general', {}) or {}
    _c106 = bool(_gg.get('kilian_override'))
    _kthr = _gg.get('kilian_wti_thr')
    _gtrans = _gg.get('transition')
    _has_diag = ('kilian_override' in _gg)
    if wk_blocked:
        if _c106 and _kthr is not None:
            _why = (f'Crown 106 공급발 대체 — KIL_SUP=1 국면에서 판정이 '
                    f'WTI&gt;{float(_kthr):.0f} 으로 <b>대체</b>된다. '
                    f'현 WTI={V(macro,"WTI")} · VIX={V(macro,"VIX")} (스톰 임계 18.5 미달, '
                    f'즉 스톰이 아니라 공급발이 차단 사유다).')
            _rel = f'해제: WTI ≤ {float(_kthr):.0f} (KIL_SUP=1 지속 시) — VIX 로는 풀리지 않는다.'
        elif _has_diag:
            _why = (f'스톰 게이트 — WTI={V(macro,"WTI")} &gt; 90 ∩ VIX={V(macro,"VIX")} ≥ 18.5 '
                    f'→ TLT 제외 전 종목 차단.')
            _rel = '해제: WTI≤89 or VIX&lt;17.5'
        else:
            _why = (f'WTI={V(macro,"WTI")} · VIX={V(macro,"VIX")} → 차단. '
                    f'⚠️ 엔진이 사유 진단 키를 내보내지 않는 판본이라 상세 사유를 확정하지 못했다.')
            _rel = '해제 조건: 엔진 판본 확인 필요'
        _tr = (f'<div style="font-size:10px;color:#94a3b8;margin-top:4px">엔진 사유: '
               f'{_html.escape(_crown_safe(_gtrans))}</div>') if _gtrans else ''
        h += (f'<div class="hbox" style="border-color:#ff8a8a;'
              f'background:rgba(248,113,113,0.06);font-size:11px">'
              f'<span style="font-weight:700;color:#ff8a8a">🔒 _wk Gate BLOCKED:</span> '
              f'{_why}<br>{_rel}{_tr}</div>')

    # 🔴 v9.2.67 [GATEREASON] 해제 조건도 실제 사유를 따라간다.
    #   종전은 blocked 이면 무조건 "VIX < 17.5 → Gate 해제" 였다. Crown #106 차단에서는 거짓이다.
    if not wk_blocked:
        _next_gate_txt = "리밸런싱 대기"
    elif _c106 and _kthr is not None:
        _next_gate_txt = (f"WTI ≤ {float(_kthr):.0f} → Gate 해제 "
                          f"(현 {V(macro,'WTI')} · Crown 106 공급발)")
    elif _has_diag:
        _next_gate_txt = "VIX &lt; 17.5 → Gate 해제"
    else:
        _next_gate_txt = "Gate 해제 조건 미확정 (엔진 진단 키 부재)"
    h += f'''<div class="hbox" style="border-color:#3b82f6;background:rgba(59,130,246,0.06);font-size:11px">
<span style="font-weight:700;color:#3b82f6">📡 Next Trigger:</span>
{_next_gate_txt} ·
TLT ExSn T10YIE&gt;2.5 감시(현 {V(macro,"T10YIE")}) ·
DXY&gt;100 TLT 50%청산 + 진입차단(Crown 102) (현 {V(macro,"DXY")})</div>
</div>'''

    # ── BROKER ALIGNMENT — 실제 브로커 보유 → 엔진 목표 (S290_14) ──
    h += render_broker_alignment(transition)

    # ── 엔진 상태 전일 대비 — 브로커 체결과 분리 (UNIFIED) ──
    h += _SECT("change")
    if not _ar.get("ready"):
        h += '<div class="card al"><div class="ct">전일 대비 변경 미확정</div>목표비중은 계속 표시합니다. 검증되지 않은 원장 차이와 매매 방향은 표시하지 않습니다.</div>'
    elif transition is not None:
        h += '<div class="card al"><div class="ct">📊 엔진 상태 전일 대비 <span style="font-size:10px;color:#64748b">(동결 원장 → 오늘 목표)</span></div>\n'
        if _changed:
            if _exited:
                h += ('<div style="font-size:11px;line-height:1.8;color:#f87171">🔴 엔진 청산 '
                      + ', '.join(_html.escape(str(e.get('ticker',''))) for e in _exited) + '</div>')
            if _entered:
                h += ('<div style="font-size:11px;line-height:1.8;color:#4ade80">🟢 엔진 진입 '
                      + ', '.join(_html.escape(str(e.get('ticker',''))) for e in _entered) + '</div>')
            for r in _reweighted:
                _fr, _to = (r.get('from') or 0) * 100, (r.get('to') or 0) * 100
                h += ('<div style="font-size:11px;line-height:1.8;color:#fb923c">🔄 엔진 리밸 %s '
                      '<span style="color:#94a3b8">%.1f%% → %.1f%%</span></div>'
                      % (_html.escape(str(r.get('ticker',''))), _fr, _to))
        else:
            h += ('<div style="font-size:12px;color:#4ade80;padding:6px 2px">'
                  '● 엔진 상태 변화 없음 — 직전 동결 원장과 오늘 목표가 동일합니다.</div>')
        h += ('<div style="font-size:9px;color:#475569;margin-top:5px">'
              '※ 실제 브로커 보유와의 차이는 위 Broker Alignment 카드가 별도 SSOT로 표시합니다.</div></div>\n')
    else:
        h += build_change_section_html(_diff)

    # ── RISK BOARD ──
    h += _SECT("risk")
    # 🆕 UNIFIED: brokerage SSOT가 연결되면 stale legacy real_account.json을 Risk Board에서 억제.
    # 정확 실계좌 비중은 cash.amount=null 정책상 계산하지 않으므로 모델 목표 리스크만 표시하고,
    # 실제 보유→목표 정렬은 Broker Alignment가 담당한다.
    _broker_ok = bool(_ALIGNMENT.get('available'))
    _ra = None if _broker_ok else load_real_account()
    _rb_holds = render_risk_board_holdings(portfolio, macro, _ra)
    _rb_entry = render_slot_proximity(scored, portfolio)  # 🆕 v9.2.26 Top5 슬롯 경쟁 근접
    _rb_drift = "" if _broker_ok else render_risk_board_drift(portfolio, _ra)
    h += f'''<div class="card" style="border-left:4px solid #f87171;padding-left:14px">
<div class="ct" style="color:#ff8a8a">🔴 Risk Board</div>
<div class="g2">
<div class="hbox" style="border-color:#ff8a8a;background:rgba(248,113,113,0.06)">
<div>📈 <span style="font-size:14px;font-weight:900">TLT {portfolio.get("TLT",0)}%</span></div>
<div style="font-size:10px;margin-top:4px">duration ~17년 · 1bp↑→-0.17% · T10YIE={V(macro,"T10YIE")}(임계 2.5)</div>
</div>
<div class="hbox" style="border-color:{"#f87171" if wk_blocked else "#4ade80"};background:rgba({"248,113,113" if wk_blocked else "34,197,94"},0.06)">
<div>{"🔒" if wk_blocked else "🔓"} <span style="font-size:14px;font-weight:900">Gate {"BLOCKED" if wk_blocked else "OPEN"}</span></div>
<div style="font-size:10px;margin-top:4px">WTI {V(macro,"WTI")} · VIX {V(macro,"VIX")} → {"차단" if wk_blocked else "통과"}</div>
</div>{render_risk_board_concentration(portfolio)}{_rb_holds}{_rb_entry}</div></div>{_rb_drift}
'''
    # ── TARGET WEIGHTS (청산조건·보유일 복원) ──
    h += _SECT("target")
    h += '<div class="card al"><div class="ct">📊 목표비중</div>'
    if not _CONTRACT_READINESS.get('inputs_complete', False):
        h += '<div style="color:#fbbf24">필수 센서 미확인: 점수는 확보 입력의 계산값이며, 0점만으로 유효한 진입 미달을 확정하지 않습니다.</div>'
    h += '<div class="td"><table>\n'
    h += '<tr><th>종목</th><th>비중</th><th>ratio</th><th>등급</th><th>Gate</th><th>청산조건</th><th>연속 모의보유일</th><th>전략 잔여일</th><th>1M</th><th>3M</th><th>점수</th></tr>\n'
    _sz_notes = []  # 🆕 [T3-SIZEMULT 설명 S277] 사이징 마커 있을 때 카드 하단 설명줄용 수집
    for tk, w in portfolio.items():
        info = tks.get(tk, {})
        m1 = info.get('m1_return_pct', 0) or 0
        m3 = info.get('m3_return_pct', 0) or 0
        sc = info.get('entry_score')
        th_val = info.get('entry_threshold')
        _score_valid = isinstance(sc, (int, float)) and np.isfinite(sc)
        _threshold_valid = isinstance(th_val, (int, float)) and np.isfinite(th_val) and th_val > 0
        ratio_v = sc / th_val if _score_valid and _threshold_valid else float('nan')
        ratio_text = f'{ratio_v:.2f}x' if np.isfinite(ratio_v) else '미확인'
        score_text = f'{sc:+g}/{th_val:g}' if _score_valid and _threshold_valid else '미확인'
        g = aaqg_grades.get(tk) or info.get('grade', '?')  # AAQG 우선
        # 🌊 v9.2.41 (Crown 102): TLT 는 _wk 면제이나 DXY>100 진입차단이 신설됨 → 무조건 "면제" 표기 금지
        if tk == "TLT":
            _dxy_v = macro.get("DXY")
            _dxy_blk = (_dxy_v is not None) and (not np.isnan(_dxy_v)) and (_dxy_v > 100)
            gate_str = "🔒 DXY>100" if _dxy_blk else "🔓 면제"
        else:
            gate_str = "🔓 OPEN" if not info.get('gate_blocked') else "🔒"
        g_cls = f'gb-{g}' if g in ("S","A","B","C") else ""
        # 🆕 v9.1.1: 보유일/잔여일 = run_prima4 final_positions (held_days, target_days) 우선 (격언 #47)
        _pos = final_positions.get(tk, {})
        _held = _pos.get('strategy_held_days', _pos.get('held_days'))
        _actual_held = _pos.get('actual_held_days')
        _tgt = _pos.get('target_days') or info.get('target_days')  # final_positions 우선, evaluate_all 폴백
        _remain = max(0, int(_tgt) - int(_held)) if isinstance(_tgt, (int, float)) and isinstance(_held, (int, float)) else None
        _held_cell = f"{int(_actual_held)}d" if isinstance(_actual_held, (int, float)) else "—"
        _remain_cell = f"{_remain}d" if (_remain is not None and _pos) else "—"
        _n1m = ('<div style="font-size:9px;color:#fbbf24;margin-top:2px">'
                + entry_display_status(info, tk, transition) + '</div>')
        if not _CONTRACT_READINESS.get('inputs_complete', False):
            ratio_text += ' (미검증)'
        h += f'<tr><td>{EMOJIS.get(tk,"")} <b>{tk}</b></td><td style="font-size:13px;font-weight:900">{w}%{_n1m}</td>'
        _catw = aaqg_cat.get(tk, "")
        _catspan = f'<span style="color:#64748b;font-size:9px"> {_catw}</span>' if _catw else ""
        # 🆕 [T3-SIZEMULT S277] 사이징 배수 마커 — ratio 열이 SLV 절반(×0.5)·COPX 배수를 표시(격언 #80 정합)
        #   size_mult = final_positions(엔진 단일 원천). 미노출(구엔진) 시 1.0 폴백 → 마커 없음.
        _sz = _pos.get('size_mult', 1.0) or 1.0
        _sz_mark = ""
        if abs(_sz - 1.0) > 1e-9:
            _frac = "½" if abs(_sz - 0.5) < 1e-9 else f"{_sz:g}"
            _clr = "#f87171" if _sz < 1.0 else "#4ade80"   # 감산 적색 / 가산 녹색
            _arrow = "↓" if _sz < 1.0 else "↑"
            _sz_mark = f'<span style="color:{_clr};font-size:9px;font-weight:700"> ×{_frac}{_arrow}</span>'
            # 🆕 [T3-SIZEMULT 설명] 마커 사유 수집 — 카드 하단 설명줄 (평문, HTML 이스케이프)
            if tk == 'SLV':
                _rsn = "은(SLV)이 금(GLD) 대비 최근 20일 약세(RS_20d&le;0) → 손실 제한 위해 사이징 절반. ratio는 오늘 평가값이며, ×0.5는 거듭제곱 이전의 배분 입력에 적용됩니다"
            elif tk == 'COPX':
                _rsn = ("위안 약세(USD_CNY&gt;7.0) → 중국 경기부양 기대, 구리 모멘텀 강화 사이징" if abs(_sz-1.2)<1e-9
                        else "위안 강세(USD_CNY&lt;6.5) → 구리 모멘텀 약화 사이징" if abs(_sz-0.8)<1e-9
                        else "위안 1개월 강세(chg20&lt;-1%) → 구리 동행 확인 사이징" if abs(_sz-1.1)<1e-9
                        else "모멘텀 사이징 배수 적용")
            else:
                _rsn = "자산별 사이징 배수 적용"
            _sz_notes.append((tk, _frac, _arrow, _clr, ratio_v, _sz, _rsn))
        h += f'<td>{ratio_text}{_sz_mark}</td><td><span class="gb {g_cls}" style="color:{gc_map.get(g,chr(35)+"94a3b8")}">{g}급{aaqg_marks.get(tk,"")}</span>{_catspan}</td>'
        h += f'<td style="color:#4ade80">{gate_str}</td><td>없음</td><td>{_held_cell}</td><td>{_remain_cell}</td>'
        h += f'<td style="color:{rc(m1)}">{m1:+.1f}%</td><td style="color:{rc(m3)}">{m3:+.1f}%</td>'
        h += f'<td>{score_text}</td></tr>\n'
    if not engine_ok:  # 🔴 fail-loud: 엔진 미산출
        h += '<tr style="color:#f87171"><td colspan="11">⚠️ 데이터 없음 — run_prima4 실시간 포트폴리오 미산출</td></tr>\n'
    elif not portfolio:  # 🆕 v9.2.21: 엔진 정상 + 보유 0종 = 전량 현금 (정상 상태)
        h += '<tr style="color:#38bdf8"><td colspan="11">🟦 목표 보유 0종 — 전 종목 청산 조건 충족 (전량 현금)</td></tr>\n'
    h += f'<tr style="color:#475569"><td>💵 RP (현금)</td><td>{cash_pct:.2f}%</td><td colspan="9">SGOV gsr 수익률 적용</td></tr>\n'
    h += '</table>\n'
    h += render_simulated_holdings()
    # 🆕 [T3-SIZEMULT S277] 비중 산정 안내 — Commander "모든 종목 해당": 공통 안내(항상) + 종목별 배수(조건부)
    h += '<div style="margin-top:7px;padding:7px 9px;font-size:10px;color:#94a3b8;line-height:1.6">'
    h += '<div>ℹ️ 비중 산정 안내 (모든 종목 공통)</div>'
    h += allocation_explanation_html()
    if _sz_notes:
        h += '<div style="color:#64748b;font-weight:700;margin:4px 0 3px">▸ 종목별 추가 사이징 배수</div>'
        for (tk, frac, arrow, clr, rv, sz, rsn) in _sz_notes:
            h += f'<div><b style="color:{clr}">{tk} ×{frac}{arrow}</b> <span style="color:#64748b">(당일 ratio {rv:.2f}x · 배분 입력 배수 {sz:g})</span> : {rsn}</div>'
    # 🆕 v9.2.55 (S290): 진입 차단 내역 표시 — transition v2.4.0 gate_blocked 소비.
    #   결함: v2.3.0 이 당일 청산분 재진입을 이미 막고 있었으나 그 사실이 로그에만 있어
    #   화면에는 "진입 X · 청산 X" 동시 표기만 남았다 — Commander 가 매일 같은 모순을 중재해야 했다.
    #   차단이 작동했다는 사실을 표시하면 중재 대상이 아니라 해소된 항목으로 읽힌다.
    _gb_list = (transition or {}).get('gate_blocked') or []
    if _gb_list:
        h += ('<div style="margin-top:7px;padding:7px 9px;background:rgba(74,222,128,0.08);'
              'border-left:3px solid #4ade80;border-radius:6px;font-size:10px;color:#94a3b8;line-height:1.6">')
        h += ('<div style="color:#4ade80;font-weight:700;margin-bottom:3px">'
              f'진입 제한 확인 {len(_gb_list)}종목 — 조건별 재평가 필요</div>')
        for _gb in _gb_list:
            _reason = _gb.get('reason', '')
            if isinstance(_reason, dict):
                _reason = ', '.join(map(str, _reason.get('reasons') or [])) or '진입 제한 조건 확인'
            h += ('<div>⛔ <b>' + _html.escape(str(_gb.get('ticker', '?'))) + '</b> : '
                  + _html.escape(str(_reason)) + '</div>')
        h += '<div style="color:#64748b;margin-top:3px">조건에 따른 진입 제한 목록이며, 실제 주문 시도나 당일 왕복 거래 발생 건수를 뜻하지 않습니다.</div>'
        h += '</div>'
    # 🆕 v9.2.36 (S286, Commander 지시): 슬롯 선정 종목 한정 매수 논리 각주.
    #   미보유 종목은 출력 0건 — 목표비중 표에 오른 종목만 "왜 샀는가"를 설명한다.
    # 🆕 v9.2.48: 보유 종목 논리만 — 후보 감시 논리는 Candidate Watch 카드로 이관
    # 🔴 v9.2.49: 전이 지시(원장 → 목표) + 재현값 대조 각주
    if transition is not None and _ar.get("ready"):
        _od = [o for o in (transition.get('orders') or []) if o['action'] != '유지']
        if _od:
            _it = ['<span style="white-space:nowrap">%s <b>%s</b> (%+.1fp)</span>'
                   % (o['action'], _html.escape(o['ticker']), o['delta'] * 100) for o in _od]
            h += ('<div style="font-size:11px;color:#cbd5e1;margin:8px 0 4px">'
                  '\U0001F501 <b style="color:#fbbf24">전이 지시</b> '
                  '<span style="color:#64748b">(전일 산출 → 당일 산출 · 편도 회전 %.1f%%)</span><br>'
                  '<span style="line-height:2.0">%s</span></div>'
                  % (transition.get('turnover', 0.0) * 100, " · ".join(_it)))
            # 🆕 v9.2.52: 격상일 규칙 변경분 표기 — 신호 변화와 구분
            if (ledger or {}).get('rule_change'):
                _pc = (ledger or {}).get('prev_crown') or '?'
                h += ('<div style="font-size:11px;color:#fbbf24;margin:2px 0 4px">'
                      '\u26a0\ufe0f <b>Crown 격상일</b> — 전일 대비 차이에 규칙 변경분(%s → %s)이 섞여 있다. '
                      '신호 변화만은 아니다.</div>'
                      % (_html.escape(str(_pc)), _html.escape(str(crown_num))))
    h += render_entry_rationale(portfolio)
    if transition is not None and repro:
        h += render_repro_footnote(repro, {k: v * 100 for k, v in transition['target'].items()})
    h += '</div>\n'
    h += '</div></div>\n'
    h += _SECT("trailing")
    # 🆕 v9.1.3: 트레일링 성과 표 — equity 인자 사용 (result는 evaluate_all이라 equity 없음 → KeyError 방지)
    try:
        h += format_trailing_html()  # 🔒 equity 미전달 — 실보유 장부에서 직접 산출(S284 HARDLOCK)
    except Exception as _e:
        print(f"  ⚠️ 트레일링 표 생성 실패: {_e}")   # silent pass 금지 — 오류 표면화
    h += _SECT("chart6m")
    if chart_html:
        h += chart_html   # 🆕 v9.1.6: 6개월 보유 차트
    h += _SECT("rank1m")
    if return_rank_html:
        h += return_rank_html   # 🆕 v9.2.5: 1개월 누적 수익률순위(전체종목중)
    h += _SECT("capture")
    h += render_capture_gauge()   # 🆕 v9.2.40: 21종 1Y 포착률 계기판 (표시 전용)


    # ── STORM v2 (4조건 상세) + Shadow Slot + 매크로 ──
    h += _SECT("storm_shadow")
    # STORM 조건 계산
    oas_hy = macro.get('OAS_HY')
    move_v = macro.get('MOVE')
    vix_v = macro.get('VIX')
    c1 = oas_hy is not None and oas_hy > 4.0
    c2 = False  # HYG 약세 — 별도 데이터 필요, 기본 OFF
    b3 = move_v is not None and move_v > 120
    l2 = False  # SMH 압착 — 별도 데이터 필요, 기본 OFF
    pss = sum([c1, c2, b3, l2])
    pss_color = "#4ade80" if pss == 0 else "#fbbf24" if pss <= 1 else "#f87171"
    exposure = {0: 100, 1: 100, 2: 90, 3: 70, 4: 50}.get(pss, 50)

    h += '<div class="g2">\n'
    h += f'<div class="card al"><div class="ct">🛡️ STORM v2</div>'
    h += f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:8px">'
    h += f'<span style="font-size:28px;font-weight:900;color:{pss_color}">PSS {pss}/4</span>'
    h += f'<div><div style="font-size:11px">노출 <b style="color:{pss_color}">{exposure}%</b></div>'
    h += f'<div style="color:#64748b">방어현금 {100 - exposure:.0f}%</div></div></div>'
    h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:10px">'
    for label, active, val in [
        ("C1 · HY 신용↑", c1, f"OAS_HY={V(macro,'OAS_HY')}"),
        ("C2 · HYG 약세", c2, "—"),
        ("B3 · MOVE 확대", b3, f"MOVE={V(macro,'MOVE')}"),
        ("L2 · SMH 압착", l2, "—"),
    ]:
        dot_cls = "background:#f87171" if active else "background:#1e293b"
        status = "ON" if active else "OFF"
        h += f'<div><span style="width:9px;height:9px;border-radius:50%;display:inline-block;border:1px solid #334155;{dot_cls}"></span> {label} {status} <span style="color:#475569;font-size:9px">{val}</span></div>'
    h += '</div></div>\n'

    # Shadow Slot
    best_ext = None
    worst_held = None
    for t in scored:
        if t['tk'] not in held_tickers and not t['blocked'] and t['eff_total'] > 0:
            if best_ext is None or t['eff_total'] > best_ext['eff_total']:
                best_ext = t
    for tk in held_tickers:
        info = tks.get(tk, {})
        sc = info.get('entry_score', 0) or 0
        th_v = info.get('entry_threshold', 1) or 1
        r = sc / th_v if th_v else 0
        if worst_held is None or r < worst_held[1]:
            worst_held = (tk, r)

    h += '<div class="card al"><div class="ct">🧭 Shadow Slot</div>'
    h += '<div class="kv">'
    if best_ext:
        h += f'<span class="k">최강 외부</span><span class="v">{EMOJIS.get(best_ext["tk"],"")} {best_ext["tk"]} <span style="color:#4ade80;font-weight:700">{best_ext["eff_total"]:.2f}</span></span>'
    else:
        h += f'<span class="k">최강 외부</span><span class="v" style="color:#475569">Gate BLOCKED — 외부 후보 없음</span>'
    if worst_held:
        h += f'<span class="k">최약 보유</span><span class="v">{EMOJIS.get(worst_held[0],"")} {worst_held[0]} <span style="color:#fbbf24;font-weight:700">{worst_held[1]:.2f}x</span></span>'
    edge = (best_ext["eff_total"] - worst_held[1]) if best_ext and worst_held else 0
    h += f'<span class="k">우위</span><span class="v" style="color:#a78bfa">{edge:+.2f}p</span>'
    h += f'<span class="k">SCF</span><span class="v" style="color:#475569">표본 부재</span>'
    verdict = "교체 안 함 (예측우위 미측정 REG-S132)" if wk_blocked else "교체 안 함 (예측우위 미측정)"
    h += f'<span class="k">판정</span><span class="v">{verdict}</span>'
    h += '</div></div>\n'
    h += '</div>\n'  # g2

    # ── 매크로 스냅샷 ──
    h += _SECT("macro")
    h += '<div class="card al"><div class="ct">📡 매크로 스냅샷</div>'
    h += '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px;font-size:10px">'
    for k in ['VIX','WTI','TNX','TYX_30Y','DXY','NFCI','DFII10','T10YIE','MOVE','OAS_IG','OAS_HY','PMI']:
        _bc = macro_band_color(k, macro)  # 🆕 v9.2.0: 신호등 색
        _bs = f' style="color:{_bc}"' if _bc else ''
        h += f'<div><span style="color:#64748b">{k}</span> <b{_bs}>{V(macro,k)}</b></div>'
    h += '</div>'
    h += '<div style="font-size:9px;color:#475569;margin-top:4px">🟢 안전 · 🟡 경계 · 🟠 위험 (지표별 임계)</div>'
    h += '</div>\n'

    # ── Driver Cluster (3열 + 영향종목) ──
    h += _SECT("driver")
    h += '<div class="card al"><div class="ct">📡 Driver Cluster</div><div class="td"><table>'
    h += '<tr><th></th><th>클러스터</th><th>매크로 (오늘)</th><th>현재 방향</th><th>과거 BT 기여</th><th>영향 종목</th></tr>'
    tnx = macro.get('TNX') or 0
    tyx = macro.get('TYX_30Y') or 0
    wti = macro.get('WTI') or 0
    oas = macro.get('OAS_IG') or 0
    nfci = macro.get('NFCI') or 0
    dxy = macro.get('DXY') or 0
    clusters = [
        ("🟢","금리 고점", f"TNX {V(macro,'TNX')} · TYX {V(macro,'TYX_30Y')}", tnx>4, "↑ 고점 지속","+18.0%","#4ade80","CQQQ EWZ GLD ITA SLV TLT VEA VNM"),
        ("🟢","고유가 감산", f"WTI {V(macro,'WTI')}", wti>85, "↑ 고유가","-7.0%","#f87171","CIBR COPX GLD ITA IWM SMH VEA VNM"),
        ("🟢","신용 완화", f"OAS_IG {V(macro,'OAS_IG')} · NFCI {V(macro,'NFCI')}", oas<0.9, "↓ 스프레드 축소","+12.0%","#4ade80","GLD SLV XLV"),
        ("⚫","달러 활성", f"DXY {V(macro,'DXY')}", dxy>100, "— 미활성" if dxy<100 else "↑ 강달러","+5.0%","#4ade80",""),
        ("🟢","VIX 상승", f"VIX {V(macro,'VIX')}", vix_v and vix_v>20, "↑ 불안","","",""),
    ]
    for icon, name, mac, active, direction, impact, imp_col, tickers_str in clusters:
        op = "" if active else ' style="opacity:0.45"'
        dc = "#4ade80" if "↓" in direction or "고점" in direction else "#f87171" if "↑" in direction and "감산" in name else "#94a3b8"
        h += f'<tr{op}><td>{icon}</td><td style="font-weight:700">{name}</td><td>{mac}</td>'
        h += f'<td style="color:{dc}">{direction}</td>'
        h += f'<td style="color:{imp_col};font-weight:700">{impact}</td>'
        h += f'<td style="font-size:9px">{tickers_str}</td></tr>'
    h += '</table></div>'
    h += '<div style="font-size:9px;color:#475569;margin-top:4px">※ "과거 BT 기여" = ablation 추정치(역대). 오늘 이후 예측값 <b style="color:#ff8a8a">아님</b>.</div>'
    h += '</div>\n'

    # ── 보유종목 상세 (Exit 신호 포함) ──
    h += _SECT("holdings")
    # Exit 신호 정의 (종목별)
    EXIT_DEFS = {
        "TLT": [
            ("WTI∩인플레 즉청산","WTI>90 ∩ T10YIE>2.5", lambda m: (m.get('WTI') or 0)>90 and (m.get('T10YIE') or 0)>2.5),
            ("DXY 50% 부분청산","DXY≥100 → 50% 청산", lambda m: (m.get('DXY') or 0)>=100),
            ("손절","수익률≤−15%", lambda m: False),
            ("보유만기","보유≥126d", lambda m: False),
        ],
        "XLE": [
            ("XLE WTI 게이트","WTI>110 (XLE 전용)", lambda m: (m.get('WTI') or 0)>110),
            ("STORM 방어","PSS≥2", lambda m: False),
            ("손절","수익률≤−15%", lambda m: False),
            ("보유만기","보유≥63d", lambda m: False),
        ],
    }
    # 일반 종목 기본 Exit
    DEFAULT_EXITS = [
        ("WTI/VIX 스톰게이트","WTI>90 ∩ VIX≥18.5 (히스테리시스)", lambda m: (m.get('WTI') or 0)>90 and (m.get('VIX') or 0)>=18.5),
        ("STORM 방어","PSS≥2", lambda m: False),
        ("손절","수익률≤−15%", lambda m: False),
        ("보유만기","보유≥63d", lambda m: False),
    ]

    def exit_rows_html(tk, macro_vals):
        exits = EXIT_DEFS.get(tk, DEFAULT_EXITS)
        rows = '<div style="font-size:10px;font-weight:700;color:#fb923c;padding:4px 8px;margin:4px 0">📤 청산신호 (ExSn)</div>\n'
        for name, cond, check_fn in exits:
            fired = check_fn(macro_vals)
            icon = "🔴" if fired else "🟢"
            status = "FIRED" if fired else "safe"
            # 현재값 표시
            cur_parts = []
            for k in ['WTI','VIX','DXY','TNX','T10YIE','OAS_HY']:
                if k.lower() in cond.lower():
                    cur_parts.append(f"{k}={V(macro_vals, k)}")
            cur_str = " · ".join(cur_parts) if cur_parts else "—"
            rows += f'<div class="sr"><span class="si">{icon}</span><span class="sn" style="color:#94a3b8">📤 {name}</span><span class="sc">{cond}</span><span class="sv">{cur_str}</span><span class="sp"></span><span class="su"></span></div>\n'
        return rows

    h += '<div class="card al"><div class="ct">💼 보유 종목 상세</div>\n'
    for tk in held_tickers:
        info = tks.get(tk, {})
        gc = gc_map.get(aaqg_grades.get(tk) or info.get('grade', ''), '#475569')  # AAQG 우선
        m1 = info.get('m1_return_pct', 0) or 0
        m3 = info.get('m3_return_pct', 0) or 0
        close = info.get('current_close', 0) or 0
        sc = info.get('entry_score', 0) or 0
        th_val = info.get('entry_threshold', 1) or 1

        h += f'<details><summary>{EMOJIS.get(tk,"")} <b>{tk}</b> {portfolio[tk]}% · +{sc}/{th_val}</summary>\n'
        h += f'<div style="padding:4px 8px">\n'
        if tk == "TLT":
            h += '<div class="warn">⚠️ duration ~17년 / 1bp↑→-0.17% / 안전자산 아님</div>\n'
        h += f'<div class="am"><span>종가 ${close:.2f}</span>'
        h += f'<span style="color:{rc(m1)}">{m1:+.1f}%</span>'
        h += f'<span style="color:{rc(m3)}">{m3:+.1f}%</span></div>\n'
        h += '<div class="sr sh"><span class="si"></span><span class="sn">시그널</span><span class="sc"></span><span class="sv">현재값</span><span class="sp">기여</span><span class="su">누적</span></div>\n'
        srows, final_cum = build_signals_html(tk, ps, tks, macro, gates)
        h += srows
        # Exit 신호
        h += exit_rows_html(tk, macro)
        # 카드 정본은 엔진 점수이며 신호 합산 차이는 별도로 표시한다.
        h += _score_box_html(tk, scored, ps, th_val)
        h += '</div></details>\n'
    h += '</div>\n'

    # ── Candidate Watch 요약 (ratio > 0 만) ──
    h += _SECT("candwatch")
    cand_visible = [t for t in scored if t['tk'] not in held_tickers and t['eff_total'] > 0]
    h += '<div class="card al"><div class="ct">📋 Candidate Watch (Top5 밖 감시)</div>\n'
    if cand_visible:
        h += '<div class="td"><table>\n'
        h += '<tr><th>종목</th><th>ratio</th><th>점수/임계</th><th>등급</th><th>상태</th></tr>\n'
        for t in cand_visible:
            tk = t['tk']
            info = t['info']
            blocked = t['blocked']
            total = t['eff_total']
            th_val = info.get('entry_threshold', 1) or 1
            ratio_v = total / th_val if th_val and total else 0
            grade = aaqg_grades.get(tk) or ('S' if ratio_v >= 3 else 'A' if ratio_v >= 2 else 'B' if ratio_v >= 1.5 else 'C' if ratio_v >= 1 else '—')  # AAQG 우선
            g_cls = f'gb-{grade}' if grade in ("S","A","B","C") else ""
            gate_str = "🔒 BLOCKED" if blocked else "🔓 OPEN"
            gate_col = "#f87171" if blocked else "#4ade80"
            status_extra = ' · ' + entry_display_status(dict(info, gate_blocked=blocked))
            h += f'<tr><td>{EMOJIS.get(tk,"")} <b>{tk}</b></td>'
            h += f'<td style="font-weight:700">{ratio_v:.2f}x</td>'
            h += f'<td>+{total:.1f}/{th_val}</td>'
            if grade in ("SS","S","A","B","C","D"):
                _cw = aaqg_cat.get(tk, "")
                _cwspan = f'<span style="color:#64748b;font-size:9px"> {_cw}</span>' if _cw else ""
                h += f'<td><span class="gb {g_cls}" style="color:{gc_map.get(grade,chr(35)+"94a3b8")}">{grade}급{aaqg_marks.get(tk,"")}</span>{_cwspan}</td>'
            else:
                h += f'<td style="color:#475569">{grade}</td>'
            h += f'<td style="font-size:9px"><span style="color:{gate_col}">{gate_str}</span>{status_extra}</td></tr>\n'
        h += '</table></div>\n'
    else:
        h += '<div style="font-size:11px;color:#475569;padding:8px">확보 입력에서 양수 점수 후보 없음 · 입력 검증 여부는 별도</div>\n'
    # 🆕 v9.2.48: 후보 감시 매수·매도 논리 각주 — 카드와 그 설명을 같은 자리에 둔다.
    _wc = _watch_candidates(scored, portfolio)
    if _wc:
        h += render_entry_rationale({}, _wc)
    h += '</div>\n'

    # ── 매수후보 ──
    h += _SECT("buycand")
    h += '<div class="card al"><div class="ct">🔍 매수 후보 상세</div>\n'
    for t in scored:
        if t['tk'] in held_tickers:
            continue
        tk = t['tk']
        info = t['info']
        blocked = t['blocked']
        gc = gc_map.get(t['grade'], '#475569') if not blocked else '#475569'
        blocked_str = "🔒 BLOCKED" if blocked else "🔓 OPEN"
        blocked_col = "#f87171" if blocked else "#4ade80"
        total = t['eff_total']
        total_str = ""
        if total != 0:
            total_str = f' · <span style="color:{"#4ade80" if total>0 else "#f87171"};font-weight:700">잠재 {total:+.1f}</span>'

        # 모두 기본 접힘 (사용자가 직접 펼침)
        open_attr = ""
        th_val = info.get('entry_threshold', 1) or 1

        block_reason = '<span style="color:#fbbf24;font-size:9px"> · ' + entry_display_status(dict(info, gate_blocked=blocked)) + '</span>'

        h += f'<details{open_attr}><summary>{EMOJIS.get(tk,"")} <b>{tk}</b> '
        h += f'<span style="color:{blocked_col}">{blocked_str}</span>'
        h += f' <span style="color:#64748b;font-size:9px">임계 {th_val}</span>'
        h += f'{total_str}{block_reason}</summary>\n'
        h += '<div style="padding:4px 8px">\n'

        # 메타 정보 (m1, m3, 종가, dev120)
        m1 = info.get('m1_return_pct', 0) or 0
        m3 = info.get('m3_return_pct', 0) or 0
        close = info.get('current_close', 0) or 0
        dev = info.get('dev120_pct', 0) or 0
        h += f'<div class="am"><span>종가 ${close:.2f}</span>'
        h += f'<span style="color:{rc(m1)}">1M {m1:+.1f}%</span>'
        h += f'<span style="color:{rc(m3)}">3M {m3:+.1f}%</span>'
        h += f'<span style="color:#64748b">DEV120 {dev:+.1f}%</span></div>\n'

        if blocked:
            h += f'<div style="font-size:10px;color:#fb923c;padding:2px 8px;margin-bottom:4px">'
            h += f'⚡ Gate 해제 시 잠재 점수 = <b>{total:+.1f}</b> (임계 {th_val} → ratio {total/th_val:.2f}x)</div>\n'

        # 전체 신호 (Gate 상태와 무관하게 전수 표시)
        h += '<div class="sr sh"><span class="si"></span><span class="sn">시그널</span><span class="sc"></span><span class="sv">현재값</span><span class="sp">기여</span><span class="su">누적</span></div>\n'
        srows, _ = build_signals_html(tk, ps, tks, macro, gates)
        h += srows
        # Exit 신호
        h += exit_rows_html(tk, macro)
        # 카드 정본은 엔진 점수이며 신호 합산 차이는 별도로 표시한다.
        h += _score_box_html(tk, scored, ps, th_val)
        h += '</div></details>\n'
    h += '</div>\n'

    # ── Gate 해제 후보 ──
    h += _SECT("gaterelease")
    gate_candidates = [t for t in scored if t['blocked'] and t['eff_total'] > 0 and t['tk'] not in held_tickers]
    if gate_candidates:
        h += '<div class="card al"><div class="ct">🚦 Gate 해제 후 재평가 후보</div>'
        h += '<div style="display:flex;flex-wrap:wrap;gap:8px;font-size:11px">'
        for t in gate_candidates:
            h += f'<span>{EMOJIS.get(t["tk"],"")} {t["tk"]} <span style="color:#4ade80;font-weight:700">+{t["eff_total"]:.1f}</span></span>'
        h += '</div></div>\n'

    # ── Appendix 약어사전 (접이식) ──
    h += _SECT("appendix")
    h += '''<div class="card al">
<div class="ct">📖 Appendix — 약어사전</div>

<details><summary>D-1. 매매 일정</summary>
<div style="padding:4px 8px"><table>
<tr><td><b>증시 매수</b></td><td>강한 신호 후보 · 입력·신호·게이트·슬롯·전이 조건 확인</td></tr>
<tr><td><b>완료일 매수</b></td><td>정기 평가 후보 · 엔진 진입 조건과 계좌 검증 별도</td></tr>
<tr><td><b>Gate 해제 후</b></td><td>Gate 해제 → 전체 진입 조건 재평가</td></tr>
<tr><td><b>보류</b></td><td>Gate BLOCKED (점수 충족이나 진입 부재)</td></tr>
</table></div></details>

<details><summary>D-2. 비중 산정 규칙 (현재 엔진)</summary>
''' + allocation_explanation_html() + '''
</details>

<details><summary>D-3. STORM v2 PSS 단계</summary>
<div style="padding:4px 8px"><table>
<tr><td style="color:#4ade80"><b>PSS 0</b></td><td>100%</td><td>정상</td></tr>
<tr><td><b>PSS 1</b></td><td>100%</td><td>단일 경보</td></tr>
<tr><td style="color:#fb923c"><b>PSS 2</b></td><td>90%</td><td>팽팽 진입 (-10%)</td></tr>
<tr><td style="color:#f97316"><b>PSS 3</b></td><td>70%</td><td>팽팽 심화 (-30%)</td></tr>
<tr><td style="color:#ff8a8a"><b>PSS 4</b></td><td>50%</td><td>최대 팽팽 (-50%)</td></tr>
</table></div></details>

<details><summary>D-4. Gate 본질</summary>
<div style="padding:4px 8px"><table>
<tr><td><b>WTI/VIX (일반)</b></td><td>WTI>$90 ∩ VIX≥18.5 → BLOCKED · VIX<17.5 해제</td></tr>
<tr><td><b>WTI-XLE</b></td><td>WTI>$110 차단 (XLE 전용)</td></tr>
<tr><td><b>DFII-Hard</b></td><td>DFII10>1% hard (VNM 전용)</td></tr>
<tr><td><b>OAS-HY</b></td><td>OAS_HY>7 → XLU 포함 차단</td></tr>
<tr><td><b>VIX-Hyst</b></td><td>18.5 차단 / 17.5 해제 (마진 1.0)</td></tr>
</table></div></details>
'''

    # ── AAQG v4.1 등급 선정기준 — 접힘 각주 (Commander 지시: 종목별 선정기준 명시) ──
    h += _SECT("aaqg")
    if aaqg:
        _gr, _rows, _asof, _nxt = aaqg[0], aaqg[1], aaqg[2], aaqg[3]
        h += '<details><summary>📐 종목 등급(AAQG v4.1) — 결정 우선순위 + 선정기준 · ' + str(_asof) + ' 평가 · 차기 갱신 ' + str(_nxt) + '</summary>\n'
        h += '<div style="padding:4px 8px;font-size:10px;line-height:1.7">'
        h += ('<b>① 표시 등급 결정</b> = 1순위 <b>AAQG</b>(19년 백테스트 실적 종합 · %d종 채점) → 미수록 종목만 2순위 <b>ratio</b> fallback(=score/threshold) · 신규 종목 도입 시에만 발동 <span style="color:#94a3b8">(⚠️ PDBC=S280 신규 편입 · 19년 백테스트 채점 대기 → 차기 aaqg_quarterly_update 갱신 시 등재, 현재 ratio fallback)</span><br>') % len(_rows)
        h += '<b>② AAQG 산정</b> = 19년 백테스트 실적 종합. <b>Q = 평균 예상 수익률(E) 60% + 표본 신뢰도(R) 20% + 안정성(S) 20%</b><br>'
        h += '· <b>E(핵심)</b> = <b>1회당 평균수익 50% + 63d 페이스(Σ수익÷Σ보유일×63일) 50%</b> — 장기 누적형과 단기 폭발형의 중간 잣대. '
        h += '각각 shrinkage(w=n/(n+30), 소표본 수렴) + 최근 8분기 30% 블렌드 (v4.1)<br>'
        h += '· <b>R</b> = 신뢰도 50(에피소드+era) + 기여도 50(기여비중%+참여일) <i>(v4.1)</i> / <b>S</b> = era일관 35 + 승률 20 + payoff 20 + 손실꼬리 15 + 게이트궁합 10<br>'
        h += '· <b>등급 밴드</b>: AAQG 백분위 SS≥85·S≥75·A≥62·B≥45·C / ratio fallback S≥3.0·A≥2.0·B≥1.5·C≥1.0·D&lt;1.0 — <b>역할군 내 순위 병기</b>: 군내 표본(3~6종)이 작아 군내 등급 대신 순위가 정직<br>'
        h += '· <b>역할군 5종</b>(Core 누적 · Burst 폭발 · Hedge 방어 · Growth 성장 · External 외부민감) — 배정은 반기 검토, 등급은 분기 갱신(변동 1단계 제한)<br>'
        h += '· <b>Pace</b> = 수익 속도 보조등급 / 상한 캡: 에피소드&lt;10 → B · era≤2 → B · 둘 다 → C<br>'
        h += '· 라벨: <b>⚠️GC</b>=게이트 충돌(whipsaw — 자산 품질 아닌 게이트 마찰) · <b>⚠️↓</b>=최근 8분기 악화 · <b>표본</b>=표본 제한<br>'
        h += '· 헤지·방어 가치는 등급 숫자에 미반영 — Hedge군·태그로 해석 (예: TLT) · <b>표시 전용</b> — 비중 산정(D-2)·PRIMA 자본 가중과 분리</div>'
        h += '<div style="padding:4px 8px"><table>\n'
        h += '<tr><th>종목</th><th>등급</th><th>역할군</th><th>Pace</th><th>1회당·63d</th><th>승률</th><th>payoff</th><th>표본</th><th>태그 · 라벨</th></tr>\n'
        # v9.2.4: D-2 종목 나열 = 등급 우선(SS>S>A>B>C) + 등급 내 Q 내림차순
        _gord = {'SS':0,'S':1,'A':2,'B':3,'C':4,'D':5}
        _rows = sorted(_rows, key=lambda r: (_gord.get(str(r[1]),9), -float(r[2])))
        for _r in _rows:
            _tk, _g, _q, _e63, _e1, _pace, _cat, _nep, _era, _wr, _po, _tag, _lab, _arrow = _r
            _gcol = {"SS": "#f472b6", "S": "#facc15", "A": "#22d3ee", "B": "#4ade80", "C": "#94a3b8"}.get(str(_g), "#475569")
            _ar = '' if _arrow in ('신규기준', '신규', 'nan') else (' ' + _arrow)
            _labtxt = (' <span style="color:#fb923c">' + _lab + '</span>') if _lab else ''
            h += ('<tr><td>' + EMOJIS.get(_tk, "") + ' <b>' + str(_tk) + '</b></td>'
                  + '<td style="color:' + _gcol + ';font-weight:900">' + str(_g) + '급' + _ar + '</td>'
                  + '<td style="font-size:9px">' + str(_cat) + '</td>'
                  + '<td>' + str(_pace) + '</td>'
                  + '<td>' + ('%+.1f · %+.1f%%' % (_e1, _e63)) + '</td>'
                  + '<td>' + str(_wr) + '%</td><td>' + str(_po) + '</td>'
                  + '<td>' + str(_nep) + 'ep·' + str(_era) + 'era</td>'
                  + '<td style="font-size:9px">' + str(_tag) + _labtxt + '</td></tr>\n')
        h += '</table></div></details>\n'

    h += '''
</div>
'''

    h = _reorder_sections(h)   # 🆕 v9.2.48 CARDORDER

    # ── FOOTER ──
    h += f'''<div class="footer">
{RENDERER_VER} / Crown {crown_num} / {engine_name} / {now}<br>
<span style="color:#475569">격언 #80: Phase A fwd60 ≠ portfolio BT alpha</span>
</div>
'''
    h += '</body></html>'
    return h




# ═══════════════════════════════════════════════════════════════════
# 🛡️ v9.2.12-VGUARD: 버전 표기 무결성 게이트 (빌드 타임 self-audit)
#    원리: 산출 HTML의 렌더러 버전 패턴(v9.x.x-*)은 RENDERER_VER 단일값만 허용.
#    위반 시 exit(1) → GHA FAIL → 결함 배포 물리적 차단 (격언 #134 패턴·배지 결함 S273 재발 방지)
# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════
# 🆕 v9.2.48 CARDORDER — 카드 배열 재정의 (sentinel 재조립)
#   블록을 직접 옮기지 않는다. 각 섹션 산출 직전에 sentinel 을 심고,
#   FOOTER 직전에 SECTION_ORDER 대로 다시 이어 붙인다.
#   계산 순서는 불변이므로 변수 의존·역참조 사고가 생기지 않으며,
#   SECTION_ORDER 에 없는 섹션도 원래 순서대로 보존된다(내용 소실 0).
# ═══════════════════════════════════════════════════════════════════
SECTION_ORDER = [
    "header",        # 🦅 헤더
    "action",        # 🎯 Action Board
    "change",        # 📊 전일 대비 변경
    "target",        # 🎯 목표비중 (+ 보유 5종 매수 논리 각주)
    "candwatch",     # 📋 Candidate Watch (+ 후보 감시 매수·매도 논리 각주)
    "risk",          # ⚠️ Risk Board
    "macro",         # 🌐 매크로 스냅샷
    "trailing",      # 📈 트레일링 성과
    "chart6m",       # 📊 6-Month Holdings
    "rank1m",        # 📈 1개월 누적 수익률순위
    "capture",       # 📡 포착률 계기판
    "storm_shadow",  # 🛡️ STORM v2 + 🧭 Shadow Slot
    "driver",        # 📡 Driver Cluster
    "holdings",      # 💼 보유 종목 상세
    "buycand",       # 🔍 매수 후보 상세
    "gaterelease",   # Gate 해제 후보
    "aaqg",          # AAQG 등급 선정기준 각주
    "appendix",      # 📖 Appendix — 약어사전
]

_SECT_RE = re.compile(r"<!--\u00a7SECT:([A-Za-z0-9_]+)\u00a7-->")


def _SECT(key):
    """섹션 경계 sentinel. 재조립 시 소비되어 산출 HTML 에는 남지 않는다."""
    return "<!--\u00a7SECT:%s\u00a7-->" % key


def _reorder_sections(h):
    parts = _SECT_RE.split(h)
    if len(parts) < 3:
        print("  \u26a0\ufe0f CARDORDER SKIP: sentinel 미검출 — 원 순서 유지")
        return h
    prefix = parts[0]
    blocks, seen = {}, []
    for i in range(1, len(parts) - 1, 2):
        k, body = parts[i], parts[i + 1]
        if k not in blocks:
            blocks[k] = ""
            seen.append(k)
        blocks[k] += body
    out, used = [prefix], set()
    for k in SECTION_ORDER:
        if k in blocks:
            out.append(blocks[k])
            used.add(k)
    orphan = [k for k in seen if k not in used]
    for k in orphan:
        out.append(blocks[k])
    if orphan:
        print(f"  \u26a0\ufe0f CARDORDER: SECTION_ORDER 미등재 {orphan} — 원 순서로 말미 배치")
    print(f"  \U0001f9e9 CARDORDER: {len(blocks)}개 섹션 재조립 (누락 0)")
    return "".join(out)


def _version_integrity_check(html: str, crown_num: str = None) -> None:
    # 🛡️ v9.2.31 (S284): 문자 클래스에 '_' 추가 — 종전 [A-Za-z0-9\-] 는 언더스코어를
    #   버전 토큰의 일부로 보지 않아, RENDERER_VER 에 '_' 가 들어가면 토큰이 중간에서
    #   잘려(예: 'v9.2.30-TRAILLOCK_SAFE' → 'v9.2.30-TRAILLOCK') 정상 배포를 FAIL 처리했다.
    #   (실사고: v9.2.30-TRAILLOCK_SAFE 빌드 GHA exit 1 — 렌더러·HTML 모두 정상이었으나 오탐)
    #   접미사 명명 규칙을 우회로 바꾸는 대신 스캐너의 토큰 정의를 RENDERER_VER 이 취할 수
    #   있는 문자 집합과 일치시킨다.
    # 🛡️ v9.2.41 HDRGUARD (S288 재발방지): 헤더 선언 ↔ RENDERER_VER 상수 대조.
    #   사고 배경: 파일 헤더가 'VERSION : v9.2.39-SLOTVIS' 인데 상수는 'v9.2.40-CAPTURE' 로
    #   장기간 불일치 상태였고, 이를 모른 채 헤더만 올리자 같은 번호(v9.2.40)가 두 접미사로
    #   갈라지는 네임스페이스 충돌이 발생할 뻔했다. 헤더는 사람이, 상수는 기계가 읽는 이중
    #   원천이므로 빌드 타임에 강제 대조한다.
    #   🔒 UNIFIED 이후 동일 숫자 버전의 복수 접미사 포크를 금지한다. _renderer_namespace_guard()가
    #   같은 숫자 버전의 다른 RENDERER_VER 파일이 공존하면 렌더 전에 hard fail 한다.
    try:
        _self_src = open(os.path.abspath(__file__), 'r', encoding='utf-8').read()
        _m_hdr = re.search(r'^#\s*VERSION\s*:\s*(\S+)', _self_src, re.MULTILINE)
        _hdr_ver = _m_hdr.group(1) if _m_hdr else None
        if _hdr_ver != RENDERER_VER:
            print(f"🔴 HDRGUARD FAIL: 헤더 선언 '{_hdr_ver}' != RENDERER_VER '{RENDERER_VER}'")
            print("   처방: 파일 헤더 'VERSION :' 줄과 RENDERER_VER 상수를 동시 갱신.")
            sys.exit(1)
        print(f"🛡️ HDRGUARD PASS: 헤더 = 상수 = {RENDERER_VER}")
    except SystemExit:
        raise
    except Exception as _e:
        print(f"⚠️ HDRGUARD SKIP (자기소스 판독 불가): {type(_e).__name__}")

    tokens = set(re.findall(r'v9\.\d+\.\d+[A-Za-z0-9_\-]*', html))
    ok = (tokens == {RENDERER_VER})
    cnt = html.count(RENDERER_VER)
    if not ok:
        print(f"🔴 VGUARD FAIL: 렌더러 버전 표기 불일치 — 발견 {sorted(tokens)} / 허용 ['{RENDERER_VER}']")
        sys.exit(1)
    if cnt < 2:
        print(f"🔴 VGUARD FAIL: RENDERER_VER 출현 {cnt}회 (<2 — 배지·푸터 결손 의심)")
        sys.exit(1)
    print(f"🛡️ VGUARD PASS: 버전 단일 {RENDERER_VER} · 출현 {cnt}회")

    # 🛡️ v9.2.38 CROWNGUARD: Crown 토큰 네임스페이스 무결성.
    #   서빙 HTML 의 `Crown #NN` 은 **서빙 버전 표기 전용**이어야 한다. 설계 계보 인용은
    #   `Crown NN`(# 없음)으로 쓴다 — 외부 감시가 문서에서 Crown 을 수집할 때
    #   계보 각주를 서빙 버전으로 오인하는 사고(G2 Crown Stale Gate 오탐)를 원천 차단.
    #   누구든 계보 인용을 `#` 형태로 되돌리면 여기서 빌드가 멈춘다.
    if crown_num:
        ctok_all = re.findall(r'Crown\s*#\d+', html)
        ctok = set(ctok_all)
        want = {f"Crown {crown_num}"}
        if ctok != want:
            print(f"🔴 CROWNGUARD FAIL: Crown 토큰 오염 — 발견 {sorted(ctok)} / 허용 {sorted(want)}")
            print("   처방: 계보 인용은 'Crown NN'(# 제거) 형태로 표기. 버전 표기는 헤더·푸터 2개소만.")
            sys.exit(1)
        print("🛡️ CROWNGUARD PASS: Crown 토큰 단일 %s · 출현 %d회" % (crown_num, len(ctok_all)))

def main():
    parser = argparse.ArgumentParser(description="🦅 ARGUS Brief HTML v2")
    parser.add_argument('--output', default='index.html', help='출력 파일')
    parser.add_argument('--engine', default=None, help='명시 엔진 경로')
    parser.add_argument('--input', default=None, help='검증할 결합 데이터 CSV')
    args = parser.parse_args()

    print("🦅 ARGUS Brief HTML v2 생성")
    print("=" * 50)

    # 0. v9.2.57 PREFLIGHT — 무성 폴백/버전 포크 차단
    preflight_assets()

    # 1. 데이터
    df = normalize_data(pd.read_csv(args.input)) if args.input else fetch_live_data()
    df["Date"] = df.index.strftime("%Y-%m-%d")
    df.index.name = None

    # 2. 엔진
    print("⚙️ 엔진 로드...")
    eng, eng_path = load_engine(args.engine)
    engine_name = os.path.basename(eng_path).replace('.py', '')
    _ENGINE_SIG_RULES.update(getattr(eng, 'SIGNAL_RULES', {}) or {})  # 🆕 v9.1.2: elif 억제용 엔진 권위 규칙 주입
    _ENGINE_CONST['DS_K_MAP'] = dict(getattr(eng, 'DS_K_MAP', {}))
    _ENGINE_CONST['DS_K'] = float(getattr(eng, 'DS_K', 4.0))            # 🆕 [S277] 비중 안내 단일 원천
    _ENGINE_CONST['SOFT_SINGLE_W'] = float(getattr(eng, 'SOFT_SINGLE_W', 0.4))
    _ENGINE_CONST['REBAL_FREQ'] = int(getattr(eng, 'DEFAULT_RF', 5))   # 🆕 v9.2.39 진입 스캔 주기
    _ENGINE_CONST['MAX_POS'] = int(getattr(eng, 'DEFAULT_MP', 5))      # 🆕 v9.2.39 슬롯 수
    _ENGINE_TICKER_SPEC.update(dict(getattr(eng, 'TICKER_SPEC', {}) or {}))  # 🆕 v9.2.42 하드 게이트 단일 원천
    _ENGINE_EXSN['WTI'] = dict(getattr(eng, 'EXSN_WTI', {}) or {})
    _ENGINE_EXSN['VIX'] = dict(getattr(eng, 'EXSN_VIX', {}) or {})

    # Crown 번호 추출 — 1순위 ENGINE_METADATA.crown_number(격언 #127 엔진-내성) /
    # 2순위 파일명 'CROWN\d+' 파싱 / 3순위 '?' (하드코딩 fallback 폐지 → 격상 시 stale 원천 차단)
    crown_num = None
    if hasattr(eng, 'ENGINE_METADATA'):
        crown_num = eng.ENGINE_METADATA.get('crown_number')
    _m_fn = re.search(r'CROWN(\d+)', engine_name, re.IGNORECASE)
    if not crown_num:
        crown_num = f"#{_m_fn.group(1)}" if _m_fn else "?"

    # 🛡️ v9.2.47 CROWNXCHK: 엔진 자기신고 ↔ 배포 파일명 교차 대조.
    #   1순위(ENGINE_METADATA.crown_number)는 엔진이 스스로 신고하는 값이라,
    #   격상 시 _CROWN_NUM 갱신을 빠뜨리면 낡은 번호가 그대로 배지에 실린다.
    #   엔진 내부 자가검사(CU5)는 ENGINE_METADATA == _CROWN_NUM 일치만 보므로
    #   두 값이 함께 낡으면 통과한다 — 같은 원천 안에서는 검출이 불가능하다.
    #   배포 파일명은 Commander 가 격상 시점에 부여하는 독립 축이므로 이를 대조축으로 쓴다.
    #   파일명에 CROWN 토큰이 없으면 대조 불가로 SKIP (오탐 방지).
    if _m_fn:
        _fn_crown = f"#{_m_fn.group(1)}"
        if crown_num != _fn_crown:
            print(f"🔴 CROWNXCHK FAIL: 엔진 자기신고 '{crown_num}' != 배포 파일명 '{_fn_crown}'")
            print(f"   엔진 파일: {engine_name}")
            print("   처방: 엔진의 _CROWN_NUM 과 ENGINE_METADATA['crown_number'] 를")
            print("         파일명 Crown 번호에 맞춰 동시 갱신한 뒤 재배포.")
            sys.exit(1)
        print(f"🛡️ CROWNXCHK PASS: 자기신고 = 파일명 = Crown {crown_num}")
    else:
        print(f"⚠️ CROWNXCHK SKIP: 파일명에 CROWN 토큰 없음 ({engine_name}) — 대조 불가")

    # 3. evaluate_all
    print("🔍 evaluate_all 실행...")
    result = eng.evaluate_all(df)
    eval_date = str(df.index[-1].date())
    print(f"  평가 시점: {eval_date}")

    # 3b. run_prima4 → 실제 현 포트폴리오 (STORM 보정 effective weights + 현금)
    #     evaluate_all은 점수만 반환 → 가중 Top5는 run_prima4 final_weights에서 취득(엔진 자체 산출)
    _TARGET_STATUS.clear()
    _BROKER_STATUS.clear()
    _ALIGNMENT.clear()
    print("📊 run_prima4 실제 비중 산출...")
    portfolio, cash_pct, fpos, equity = {}, 0.0, {}, None  # 🔴 v9.2.19 fail-loud: 실패 시 빈 포트 → loud 배너
    _tr, _repro_portfolio, _ledger = None, {}, None
    _CONTRACT_READINESS.clear()
    _SIMULATED_STATE.clear()
    engine_ok = False  # 🆕 v9.2.21: run_prima4 실행 성공 여부 (보유 종목 수와 분리)
    try:
        bt = eng.run_prima4(df)
        if not isinstance(bt, dict) or bt.get("error"):
            raise ValueError("engine_result_invalid")
        view = engine_view(bt)
        eff = view['target_weights']
        target_cash = view['target_cash_weight']
        if not target_contract_valid(eff, target_cash):
            raise ValueError('engine_target_contract_invalid')
        # 전략 만기와 실제 연속 모의보유 시계를 따로 보존한다.
        fpos = {}
        for ticker in set(view['positions']) | set(view['strategy_positions']):
            actual = view['positions'].get(ticker) or {}
            raw = view['strategy_positions'].get(ticker) or {}
            strategy = dict(raw) if isinstance(raw, dict) else dict(vars(raw))
            actual = dict(actual) if isinstance(actual, dict) else dict(vars(actual))
            fpos[ticker] = {**strategy, **actual}
            fpos[ticker]['strategy_held_days'] = strategy.get('held_days', actual.get('strategy_held_days'))
            fpos[ticker]['actual_held_days'] = actual.get('actual_held_days')
            fpos[ticker]['target_days'] = strategy.get('target_days', actual.get('target_days'))
        _SIMULATED_STATE.update(weights=view['simulated_weights'], cash=view['simulated_cash_weight'])
        # 공통 평가 도우미가 같은 날 위험 청산과 보유 문맥을 복원한다.
        result = evaluate_engine(eng, df, bt)
        equity = bt.get('equity')  # 🆕 v9.1.3: 트레일링 성과용 (run_prima4 equity 시리즈)
        # 🆕 v9.1.4: run_prima4 equity 는 df.index 기반 → df 가 정수 인덱스면 equity 도 정수 인덱스.
        #            트레일링 날짜 슬라이싱을 위해 df['Date'] 실제 날짜로 재인덱싱.
        if equity is not None and not isinstance(equity.index, pd.DatetimeIndex):
            _d = pd.to_datetime(df['Date'])
            if len(equity) == len(_d):
                equity = pd.Series(equity.values, index=_d.values)
            else:
                print(f"  ⚠️ equity 재인덱싱 불가 (len {len(equity)}≠{len(_d)}) — 트레일링 생략")
                equity = None
        # 🆕 v9.2.21: 예외 없이 dict 반환 + error 키 부재 = 실행 성공. 보유 0종도 정상 결과.
        if isinstance(bt, dict) and not bt.get('error'):
            engine_ok = True
        # 🆕 v9.2.40: 21종 1Y 포착률 계산 (표시 전용 · 실패해도 브리핑 정상)
        try:
            _CAPTURE_ROWS[:] = _compute_capture_1y(eng, df, bt)
            print(f"  📡 포착률 계기판: {len(_CAPTURE_ROWS)}종 산출")
        except Exception as _ce:
            _CAPTURE_ROWS[:] = []
            print(f"  ⚠️ 포착률 계산 실패({_ce}) — 계기판 생략")
        portfolio, cash_pct = display_target_percent(
            dict(sorted(eff.items(), key=lambda x: -x[1])), target_cash)
        _repro_portfolio = {t: round(w * 100, 2) for t, w in view['simulated_weights'].items()}
        _full_ledger = load_position_ledger_full()
        _ledger, _ls = select_previous_ledger(_full_ledger, eval_date)
        _real_holdings = read_broker_status(eval_date, df)
        # 목표는 최신 엔진 판단만 소비한다. 원장은 전일 비교의 가용성만 결정한다.
        _TARGET_STATUS.update(source="engine_decision", ledger=_ls,
                              data_date=eval_date, target_valid=True, target_weights=dict(eff))
        # 최신 전이는 항상 계산하고, 실제 이전 기록이 있을 때만 전일 차이를 만든다.
        _tmod = load_transition_module()
        if _tmod is not None:
            try:
                _tr = _tmod.compute_transition(eng, df, _full_ledger, signal_only=True,
                    real_holdings=_real_holdings, engine_result=bt, evaluation=result)
                if str(_tr.get('as_of', ''))[:10] != eval_date or _tr.get('target') != eff:
                    raise ValueError('전이 날짜 또는 목표가 최신 엔진과 불일치')
            except Exception as exc:
                _tr = None
                print(f"  전이 확인 불가: {type(exc).__name__}: {exc}")
        prepare_alignment(df, _real_holdings, eff, target_cash, result)
        _CONTRACT_READINESS.update(assess_readiness(df, bt, evaluation=result,
            holdings_grounded=bool(_BROKER_STATUS.get('grounded'))))
        if portfolio:
            print("  엔진 목표: " + " / ".join(f"{t} {w}%" for t, w in portfolio.items()) + f" · 현금 {cash_pct}%")
        else:
            print(f"  run_prima4 보유 0종 (전 종목 청산 조건 충족) — 전량 현금 {cash_pct}% · engine_ok={engine_ok}")
    except Exception as ex:
        engine_ok = False
        portfolio, cash_pct, fpos = {}, 0.0, {}
        _SIMULATED_STATE.clear()
        _CONTRACT_READINESS.clear()
        print(f"  run_prima4 실패({ex}) — 빈 포트 유지 (fail-loud 배너 출력)")

    # 3c. AAQG 등급 로드 (분기 갱신 CSV 우선, 부재 시 내장 fallback)
    print("📐 AAQG 등급 로드...")
    aaqg = load_aaqg()

    # 4. HTML 생성
    print("📄 HTML 생성...")
    chart_html = build_holdings_chart_html(df)  # 🆕 v9.1.6: 6개월 보유 차트
    rank_html = build_return_rank_html(df, eng)  # 🆕 v9.2.5: 1개월 누적 수익률순위(전체종목중) · v9.2.22 eng 전달(자가치유 UNIV)
    html = generate_html(result, portfolio, engine_name, crown_num, cash_pct, aaqg, fpos, equity, chart_html, rank_html, engine_ok=engine_ok, data_date=eval_date, transition=_tr, repro=_repro_portfolio, ledger=_ledger)

    _version_integrity_check(html, crown_num)  # 🛡️ v9.2.12 VGUARD + v9.2.38 CROWNGUARD: 실패 시 여기서 exit(1) — 결함 파일 미출력

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  출력: {args.output} ({os.path.getsize(args.output) / 1024:.1f} KB)")
    print("✅ 완료")


if __name__ == '__main__':
    main()
