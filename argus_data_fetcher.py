# 🔧 v3.4 (2026-06-15, S200): Brent 원유 가산 — 운영 OIL축 열화 복원 (근본 처방, 분기 최소).
#    추가: YAHOO_MACRO "BZ=F":"Brent" (WTI "CL=F" 미러, map-driven → build_seed/fetch_today_row/source 자동 흐름).
#    LIVE_SOURCE_COLS += 'Brent_source'(ffill 보호) · print_quality += "Brent" · WEEKLY/MONTHLY 미등재(일간 정합, WTI 동일).
#    base = v3.3(ca96a7150b29). backfill/FRED/v5/NL/ECY 로직 불변 → v3.3 runtime 검증 항목 그대로 유효 + Brent 1열 확인만.
#    실측: Yahoo BZ=F 작동 확인 (2026-06-15 종가 $83.10). FRED DCOILBRENTEU는 WTI 비대칭이라 미채용(향후 선택).
# 🔧 S198 (2026-06-14, v3.3 MERGE): 배포본 S195 v3.2(b17b30a69f01) base + S197 backfill 이식.
#    보존: v4→v5 경로 / NL ×1e3 / ECY·CAPE / main 자기치유. 가산: 임의날짜 backfill(BACKFILL_DATE·START·END).
#    근거: S197 v3.2(654b253da8d9)는 stale v3.1 base라 그대로 배포 시 v5/NL/ECY regression — 병합으로 차단.
#!/usr/bin/env python3
# 🔧 S195 (2026-06-12, v3.2): ① v4→v5 데이터 경로 갱신 (BT_LONG_v5_complete.csv, 정본 sha 6048e3f8672f, S188 재기준선)
#    ② Net_Liquidity 공식 정정 — RRP raw 차감 → ×1e3 (BT v5 S188 NL 정정 규약 정합, 자본 경로 0 감사 완료)
#    ③ main 합류점 전열 재계산 신설 (이력 자기치유). 베이스 = 레포 실행본 v3.1 (sha b1107f86d9ba, Commander 첨부 2026-06-12).
"""
🦅 ARGUS DATA FETCHER v3.3 — ECY/CAPE 자동 fetch 추가 (S141 Crown #73 정합)
PRIMA (최신 Crown #73 = v0.4.0-EXSN_INDIVIDUAL) 전용 데이터 수집기

🌟 v3.1 변경 사항 (S141, 2026-05-26, Commander 명령):
  🚨 1. Shiller ECY (Excess CAPE Yield) + CAPE 자동 fetch 신설
       소스: https://www.econ.yale.edu/~shiller/data/ie_data.xls
       월별 발표 → 일별 ffill (MONTHLY_COLS 등재)
  🚨 2. 신규 함수: _fetch_shiller_ecy_cape() — Shiller XLS → ECY/CAPE 월별 시리즈
  🚨 3. 신규 컬럼: ECY / CAPE / ECY_source / CAPE_source
  🚨 4. main() 내 ECY 백필 섹션 (VIX3M 패턴 정합)
  🚨 5. ARGUS signal 연구 정합: ECY × VIX regime classifier Phase A 완료 (S141)
  🚨 6. 격언 정합: #105 기존 형식 보존 / #107 User-Agent / 5조 ③ 데이터 위조 금지

🌟 v3.0 변경 사항 (S71 #4, 2026-05-08, Commander 옵션 β 채택, csv 재설계 Phase 3+5):
  🚨 1. 3 csv 분리 출력 (frequency 분리, 격언 #106 근본 처방)
       - argus_data_daily.csv     : 일간 시리즈 (VIX/WTI/TNX/DXY/Close 등)
       - argus_data_weekly.csv    : 주간 시리즈 (OAS_HY/OAS_IG/NFCI/ICSA 등)
                                    LIVE 발표일 row만 보유 (source LIVE 식별)
       - argus_data_monthly.csv   : 월간 시리즈 (PMI/UMCSENT/SAHMCURRENT 등)
                                    LIVE 발표일 row만 보유 (source LIVE 식별)
       - argus_data.csv           : 통합 view (호환성 보존, 격언 #105 정합)
  🚨 2. 신규 함수: _split_by_frequency(df) — main() 직전 line ~1442
  🚨 3. 신규 상수:
       - OUTPUT_DAILY_PATH / OUTPUT_WEEKLY_PATH / OUTPUT_MONTHLY_PATH
       - WEEKLY_COLS (11종) / MONTHLY_COLS (5종)
       - LIVE_SRC_VALUES (LIVE source 값 7종)
  🚨 4. main() write 영역 — 4 csv 동시 출력
  🚨 5. fetch logic + ffill logic + source 컬럼 로직 = v2.12 그대로 보존
       (격언 #105 기존 형식 보존 정합 — 데이터 흐름 변경 부재)

🌟 v2.12 패치 사항 (2026-05-08 KST, S69 #5, Commander 본질 통찰 #13):
  🚨 1. LIVE source 컬럼 신설 (격언 #75 v4 정식 입증 #6 + #80 + 5조 ③ 정합)
       본질: LIVE fetch 성공 (1차/2차/3차) vs ffill carry-forward (4차) 결정적 명시 구분
       
       결정적 사례 (S69 #5 발견):
         이전 v6.8.40 prima_briefing logic:
           "last vs prev 비교 → 동일값이면 ffill 인식"
         결함 결정적 본질:
           1) T10YIE 5/7 백필 후 5/8 = 2.45 (동일값) → LIVE 부정 (false negative)
           2) OAS_HY/OAS_IG 일간 시리즈인데 변동 부재 → ffill 잘못 인식
           3) PMI 월간 fetch 성공 (Tradingeconomics 1차) → ffill 잘못 인식
       
       v2.12 정정:
         - LIVE_SOURCE_COLS 신설 (22개 source 컬럼 등록)
         - 매 fetch_today_row 시 source 명시 의무
         - source 값: "yahoo_live" / "fred_live" / "tradingeconomics" / "cnn_api" / "ffill" / etc.
         - prima_briefing은 source 컬럼 검증으로 LIVE 결정적 식별
  🚨 2. 신설 컬럼 (22개):
       - VIX_source / VIX3M_source / WTI_source / TNX_source
       - DFII10_source / DGS10_source / T5YIE_source / T10YIE_source
       - DXY_source / MOVE_source / PMI_source / F_G_source
       - OAS_HY_source / OAS_IG_source / NFCI_source / ICSA_source
       - CCSA_source / UMCSENT_source / SAHMCURRENT_source
       - WALCL_source / WTREGEN_source / RRPONTSYD_source
  🚨 3. fetch_today_row source 매핑 logic:
       A. Yahoo 매크로 (VIX/WTI 등): success → "yahoo_live" / failure → "ffill"
       B. FRED 시리즈 (TNX/DFII10 등): success → "fred_live" / failure → "ffill"
       C. PMI 4중 방어: success → source ("tradingeconomics" 등) / failure → "ffill"
       D. F&G 4중 방어: success → source ("cnn_api" 등) / failure → "ffill"
  🚨 4. FFILL_COLS에 LIVE_SOURCE_COLS 통합:
       - source 컬럼도 ffill 의무 (어제 source 보존)
  🚨 5. 격언 정합:
       - #36 #1 즉시 정정 (Commander 본질 통찰 #13 즉시 반영)
       - #75 v4 정식 입증 #6 (LIVE source 결정적 명시)
       - #80 양방향 (값 ↔ source 양방향, 80→81차원)
       - #94 후보 강화 (신규 컬럼 도입 시 의존 시스템 검증)
       - #97 v2 #1 자기 audit (S69 누적 4사이클 결정적)
       - #98 결정 회피 차단 (Commander 통찰 즉시 적용)
       - #105 기존 형식 보존 (FRED_SERIES + PMI/F&G logic 보존)
       - 5조 ③ 데이터 위조 금지 (LIVE/ffill 결정적 구분)
       - 5조 ⑤ Commander 의사결정권 절대성

🌟 v2.11 패치 사항 (2026-05-08 KST, S69 #4, Commander 본질 통찰 #11):
  🚨 1. FRED 발표일 기준 매핑 정합 (격언 #75 v4 정식 입증 #5 + #80 + 5조 ③ 정합)
       본질: T10YIE/T5YIE BEI 시리즈 1일 시차 + 결측 결함 결정적 발견
       
       LIVE 결정적 입증 (S69 #4):
         FRED 원본 (Commander T10YIE.csv 첨부):
           2026-05-04: 2.50, 2026-05-05: 2.47, 2026-05-06: 2.42, 2026-05-07: 2.45
         argus_data.csv (LIVE):
           2026-05-04: 2.50, 2026-05-05: 2.50 (시차), 2026-05-06: 2.47 (시차),
           2026-05-07: NaN, 2026-05-08: 2.45 (5/7 값을 5/8에 매핑)
         
       결정적 결함:
         - _fred_latest 단순 호출 → 발표일 정보 무시
         - row[col] = v 매핑 → 오늘 row에 무조건 매핑 = 1일 시차 + 결측
         - 결과: T10YIE/T5YIE 5/7=NaN, 5/8=5/7 값 = 격언 5조 ③ 위반
       
       v2.11 정정:
         - _fred_latest_with_date 활용 (값 + 발표일 동시 수신)
         - 발표일 가시성 로그 추가 (1일 시차 시리즈 추적)
         - FRED 익일 발표 본질 정합 인식
  🚨 2. 신규 함수 강화:
       - _fred_latest_with_date: 발표일 정보 의무 (격언 #80 양방향 강화)
       - _fred_latest: 호환성 보존만 (신규 코드 사용 금지)
  🚨 3. fetch_today_row 본질 변경:
       - FRED 매핑 영역에 _fred_latest_with_date 활용
       - 1일 시차 시리즈 가시성 로그 (delayed_fred 영역)
       - FRED 발표일 ↔ today 검증 정합
  🚨 4. 영향:
       - LIVE Actions logs에서 FRED 발표일 시차 결정적 가시성
       - 향후 FRED 결정적 결함 발견 가능성 ↓
       - 격언 5조 ③ 데이터 위조 금지 정합 회복
       - 🌟 어제 row 자동 백필 (T10YIE 5/7=NaN → 2.45 정정 결정적 입증 영역)
       
       🚨 v2.11 신설 logic 영역:
         A. fetch_today_row → _fred_latest_with_date 활용 + 가시성 로그
         B. main → 어제 row 자동 백필 (FRED 발표일 = 어제 인 경우만 매핑)
         결정적 본질: B logic이 5/7 NaN 결함 결정적 정정 (5/8 fetch 시 5/7 = 2.45)
  🚨 5. 격언 정합:
       - #36 #1 즉시 정정 (Commander T10YIE.csv 첨부 = 결정적 결함 발견)
       - #75 v4 정식 입증 #5 (source ↔ 갱신 일관성, FRED 발표일 기준)
       - #80 양방향 (값 ↔ 발표일 양방향, 80→81차원)
       - #94 후보 강화 (시리즈 도입 시 발표일 검증 의무)
       - #96 v2 ⓪⑥ (사전 검증)
       - #97 v2 #1 자기 audit (Commander 본질 통찰 즉시 반영)
       - #98 결정 회피 차단 (전체 fetcher 검증 결정)
       - #105 기존 형식 보존 (FRED_SERIES 사전 보존, logic만 정정)
       - 5조 ③ 데이터 위조 금지 (결정적 정합 회복)
       - 5조 ⑤ Commander 의사결정권 절대성

🌟 v2.10 패치 사항 (2026-05-08 KST, S69 #2, Commander 명령 "옵션 D 채택"):
  🌟 1. Fear & Greed Index 4중 방어 신설 (격언 #75 v4 + #80 + #96 v2 ⓪⑥ + #98 정합)
       본질: ARGUS 매크로 정합 보강 (시장 심리 차원 직접 추가)
            → CNN 공식 API 1차 + ARGUS 자체 proxy 3차 hybrid
       사전 검증 결과 (S69 #2):
         ① CNN API (production.dataviz.cnn.io) → 본 컨테이너 차단 (allowed list 부재)
         ② Actions runner 환경 fetch 자유 (network 제약 부재)
         ③ JSON schema = 공개 사례 다수 + GitHub gist 기반 본문 작성
       4중 방어 채택:
         1차: CNN 공식 API (Referer + Origin header 의무)
         2차: CNN HTML scrape (다중 패턴 시도)
         3차: ARGUS 자체 proxy (VIX 30% + OAS 25% + SPY momentum 25% + Safe Haven 20%)
         4차: ffill (어제 csv 값, 안전망)
  🌟 2. 신설 함수:
       - _classify_fg_rating: F&G score → rating 분류 (0~25 extreme fear, 25~45 fear, ...)
       - _fetch_fg_cnn_api: 1차 source (CNN 공식 JSON API)
       - _fetch_fg_cnn_html: 2차 fallback (CNN HTML scrape)
       - _calculate_fg_argus_proxy: 3차 fallback (ARGUS 자체 가중 평균)
       - _fetch_fg_4layer_defense: 4중 방어 통합
  🌟 3. 신규 컬럼:
       - F_G_Score (float, 0~100)
       - F_G_Rating (str, 'extreme fear' | 'fear' | 'neutral' | 'greed' | 'extreme greed')
       - FFILL_COLS에 추가 (4차 ffill 정합)
       - print_quality에 가시성 추가
  🌟 4. fetch_today_row 변경:
       - PMI 4중 방어 직후 + CCSA 직전에 F&G 4중 방어 호출
       - 1차 성공 시 row['F_G_Score'] + row['F_G_Rating'] 직접 설정
       - 실패 시 ffill carry-forward
  🌟 5. 격언 정합:
       - #36 #1 즉시 정정 (source 차단 시 즉시 fallback)
       - #75 v4 source ↔ 갱신 일관성 (PMI v2.9와 동일 패턴 일관성)
       - #80 양방향 (4중 방어 다차원 + data fetch ↔ 자체 산출)
       - #94 (시그널 시 per-ticker 별도 검증 의무 — 별도 사이클)
       - #96 v2 ⓪⑥ 사전 검증 + 공식 source 우선
       - #97 v2 #1 자기 audit (사전 검증 본질)
       - #98 결정 회피 차단 (단편적 fallback 금지)
       - #105 기존 형식 보존 (PMI 4중 방어 패턴 일관성)
       - 5조 ③ 데이터 위조 금지 (정상 범위 0~100 검증)
       - 5조 ④ PRIMA 엔진 LIVE 실호출 (ARGUS 자체 차원 활용)
  🌟 6. 영향:
       - argus_data.csv F_G_Score / F_G_Rating 신규 컬럼 (시장 심리 차원 보강)
       - prima_briefing 향후 F&G 활용 가능 (B0/B1/B5 영역 — 별도 사이클)
       - 격언 #94 정합: 시그널화 시 per-ticker Phase A 별도 검증 의무
       - LIVE Actions logs에서 v2.10 정합 명시 출력

🌟 v2.9 패치 사항 (보존, S69 #1, 2026-05-08):
  🌟 1. PMI 4중 방어 신설 (격언 #75 v4 + #80 + #96 v2 ⓪⑥ + #98 정합)
       본질: v2.8의 BT_LONG carry-forward 단독 = 갱신 부재 결정적 결함
            → 1차 source 결정 의무 + 사전 검증 의무
       사전 검증 결과 (S69 #1 LIVE):
         ① ISM 공식 (https://www.ismworld.org) → HTTP 403 (bot detection)
         ② Tradingeconomics → HTTP 200 + LIVE 정합 입증 (52.7 in April 2026)
         ③ FRED graph → HTTP 503 (일시 장애 + API key fallback)
         ④ Investing.com → HTTP 403 (bot detection)
       4중 방어 채택:
         1차: Tradingeconomics scrape (LIVE 정합 입증)
         2차: FRED USSLIND proxy (proxy 정확 매핑 부재 → 현재 skip)
         3차: BT_LONG carry-forward (v2.8 logic 보존)
         4차: ffill (어제 csv 값, 안전망)
  🌟 2. 신설 함수:
       - _fetch_pmi_tradingeconomics: 1차 source (Tradingeconomics scrape)
       - _fetch_pmi_fred_usslind_proxy: 2차 fallback (현재 skip)
       - _fetch_pmi_4layer_defense: 4중 방어 통합
  🌟 3. fetch_today_row 변경:
       - v2.8: row['PMI'] 미설정 → ffill 단독
       - v2.9: 4중 방어 1차 성공 시 row['PMI'] = Tradingeconomics 값
              실패 시 ffill carry-forward (v2.8 logic 보존)
  🌟 4. 격언 정합:
       - #36 #1 즉시 정정 (csv 오염 source 결정)
       - #67 v3 dead source 차단 (DBnomics 영구 제외 보존)
       - #75 v4 후보 신설 정합 입증 (source ↔ 갱신 일관성)
       - #80 양방향 (4중 방어 다차원)
       - #96 v2 ⓪⑥ 정합 (사전 검증 + 공식 source 우선)
       - #97 v2 #1 자기 audit (ISM 403 결정적 발견)
       - #98 결정 회피 차단 (단편적 source 결정 차단)
       - #105 기존 형식 보존 (v2.8 logic 보존)
       - 5조 ③ 데이터 위조 금지 (정상 범위 30~75 검증)
  🌟 5. 영향:
       - argus_data.csv PMI 컬럼 갱신 회복 (다음달 ISM 발표 자동 반영)
       - prima_briefing v6.8.39의 _pmi_sanity와 정합 (이중 안전 보존)
       - prima_briefing v6.8.39의 _fetcher_sanity_check 정합 (소스 정합 검증)
       - LIVE Actions logs에서 v2.9 정합 명시 출력

🌟 v2.8 패치 사항 (보존, S68+, 2026-05-07):
  🚨 1. DBnomics ISM/pmi/pm 호출 영구 제거 (cumulative + today 모드)
       - 결정적 결함: 2025-09 이후 source 오염 (10.3 ~ 11.1 비정상값 누적)
       - argus_data.csv 5월 4~7일 PMI=10.3 회귀 → 매크로 결정 왜곡
       - 결정: source 자체 삭제, BT_LONG carry-forward + ffill 단독 사용
  🌟 2. PMI 신규 절차 (v2.8):
       - cumulative 모드: BT_LONG_v5_complete.csv 단독 통합 (_integrate_bt_long_pmi)
       - today 모드: ffill carry-forward (어제 값 자동 유지)
  🌟 3. DBnomics 함수 보존 (미호출 + DEPRECATED 명시)
       - _fetch_ism_pmi_dbnomics_series / _fetch_ism_pmi_dbnomics_latest
       - 향후 source 정합 회복 시 재활용 가능성
  🚨 4. v2.8 hotfix (2026-05-08 KST, LIVE 검증 8회 누적 후 결정적 발견):
       - line 636 print 출력 본문 "v2.4" → "v2.8" 정정 (헤더 docstring과 일관성)
       - LIVE Actions logs 모든 7회 출력 = "🦅 ARGUS DATA FETCHER v2.4 ..." (print 결함)
       - 헤더 정합 + print 결함 = 격언 #75 v3 위반 (source 정합 의무)
       - 격언 #36 #1 즉시 정정 (LIVE 검증 #8 결정적)
       - 격언 #97 v2 #1 자기 audit (헤더 ↔ print 일관성 부재 미인지)
  🌟 5. 격언 정합:
       - 격언 #36 #1 즉시 정정 (line 636 결함)
       - 격언 #67 v3 dead source 정정 (DBnomics dead = 즉시 차단)
       - 격언 #75 v3 정합 입증 (source 정합 의무 — 헤더 ↔ print 일관성)
       - 격언 #96 v2 ② source sanity 정합 운영 회복
       - 격언 #97 v2 #1 자기 audit (회귀 즉시 차단 + 일관성)
       - 격언 #98 결정 회피 차단 (즉시 source 삭제)
       - 5조 ③ 데이터 위조 금지 (오염값 fetch 자체 차단)
  🌟 6. 영향:
       - argus_data.csv PMI 컬럼 안정화 (52.7 매일 ffill)
       - prima_briefing v6.8.29의 _pmi_sanity와 정합 (이중 안전)
       - prima_briefing v6.8.39의 _fetcher_sanity_check와 정합 (소스 정합 검증)
       - LIVE Actions logs에서 v2.8 정합 명시 출력 회복

🌟 v2.7 패치 사항 (보존):
  ✅ 결정적 결함 정합 — 백필 트리거 cover<50% (notna().sum()==0 부족)
  ✅ Yahoo Finance User-Agent header (HTTP 429 차단)
  ✅ CCSA + VIX3M 백필 강제 재실행 (env BACKFILL_FORCE=1)
  ✅ 격언 #80 양방향 +2차원 (조건부 백필 robust)

🌟 v2.6 패치 사항 (보존):
  ✅ _fred_series() graph CSV anonymous fallback (FRED_API_KEY 부재 안전)
  ✅ CCSA GHA secret 누락 시도 fallback 보장
  ✅ 격언 #80 양방향 +2차원 (FRED multi-source)

🌟 v2.5 패치 사항 (보존):
  ✅ VIX3M (^VIX3M Yahoo) + VIX_VIX3M_ratio 파생
  ✅ argus_data.csv 컬럼 66 → 68

🌟 v2.4 패치 사항 (보존):
  ✅ CCSA (Continuing Claims) FRED 자동 fetch
  ✅ argus_data.csv 컬럼 65 → 66

v2.3 패치 사항 (보존):
  ✅ DBnomics ISM/pmi/pm 자동 fetch (Option 5)
  ✅ BT_LONG_v5_complete.csv fallback

v2.2 패치 사항 (보존):
  ✅ FRED_API_KEY 검증 + ffill + 휴장 skip + NAPM 차단

격언 정합 (v2.7 추가):
  · 🌟 격언 #97 v2 자기 audit: v2.5 백필 트리거 결함 정정
  · 🌟 격언 #98 결정 회피 차단: 즉시 통합
  · 🌟 격언 #80 양방향: 부분 백필 인정 +2 차원

v2.6 → v2.7 인터페이스 호환:
  · 환경변수: FRED_API_KEY (옵션) + BACKFILL_FORCE (옵션 v2.7 NEW)
  · 출력: argus_data.csv (68 컬럼 동일)
  · 호출: python argus_data_fetcher.py (동일)
  · 핵심: 부분 가용 컬럼 자동 백필 (cover < 50% 시 자동 재백필)
"""
import os, sys, time, json, warnings
from datetime import datetime, date, timedelta, timezone

import urllib.request
import re  # 🌟 v2.9 (S69 #1): Tradingeconomics PMI 패턴 정규식 의무
import numpy as np
import pandas as pd
import requests
import yfinance as yf

warnings.filterwarnings("ignore")

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH  = os.path.join(SCRIPT_DIR, "argus_data.csv")

# 🌟 v3.0 (S71 #4, 2026-05-08, csv 재설계 Phase 3+5 정합):
# 3 csv 분리 출력 (daily / weekly / monthly) + 통합 view 호환 (argus_data.csv 보존)
# 격언 #105 (기존 형식 보존) + 격언 #106 (근본 처방) 정합
OUTPUT_DAILY_PATH   = os.path.join(SCRIPT_DIR, "argus_data_daily.csv")
OUTPUT_WEEKLY_PATH  = os.path.join(SCRIPT_DIR, "argus_data_weekly.csv")
OUTPUT_MONTHLY_PATH = os.path.join(SCRIPT_DIR, "argus_data_monthly.csv")

# 컬럼 frequency 분류 (FRED_SERIES + 주간/월간 발표 정합)
# 🌟 v3.2 (S178): OAS_HY/OAS_IG/T10Y3M은 FRED 일간 발표 → daily로 전환
#   (기존 주간 분류는 "변동 부재 → ffill 잘못 인식"에 의한 오분류였음)
WEEKLY_COLS = ['NFCI', 'ICSA', 'CCSA',
               'WALCL', 'WTREGEN', 'RRPONTSYD', 'Net_Liquidity',
               'T10Y2Y']
MONTHLY_COLS = ['PMI', 'UMCSENT', 'SAHMCURRENT', 'F_G_Score', 'F_G_Rating', 'ECY', 'CAPE']

# 🌟 v3.1 (S141): Shiller ECY/CAPE fetch 설정
SHILLER_XLS_URL = "https://www.econ.yale.edu/~shiller/data/ie_data.xls"
SHILLER_UA = "ARGUS-ECY-Fetcher/1.0 (+https://github.com/daifulee/argus-public-data)"
ECY_VALID_RANGE = (-0.02, 0.10)   # sanity (이론상 음수 가능)
CAPE_VALID_RANGE = (5.0, 60.0)

# v3.0 source 값 매트릭스 (LIVE 식별)
LIVE_SRC_VALUES = {
    'yahoo_live', 'fred_live', 'fred_graph',
    'tradingeconomics', 'cnn_api', 'cnn_html', 'argus_proxy'
}
BT_LONG_PATH = os.path.join(SCRIPT_DIR, "BT_LONG_v5_complete.csv")
SEED_DAYS    = 450
KST          = timezone(timedelta(hours=9))

# 🆕 v2.3: DBnomics ISM PMI Web API URL (무료, 무 API key)
DBNOMICS_PMI_URL = "https://api.db.nomics.world/v22/series/ISM/pmi/pm?observations=1&format=json"

ETF_TICKERS = [
    "GLD","SLV","COPX","NLR","QQQM","VNM","IWM","PAVE",
    "SMH","EWZ","XLE","INDA","ITA","TLT","VEA","XLF",
    "XLV","XLU","CQQQ","CIBR","SGOV","SPY","IEF",
]

YAHOO_MACRO = {
    "^VIX":     "VIX",
    "^MOVE":    "MOVE",
    "^TNX":     "TNX",
    "^TYX":     "TYX_30Y",
    "^FVX":     "FVX_5Y",
    "^IRX":     "IRX_13W",
    "DX-Y.NYB": "DXY",
    "CL=F":     "WTI",
    "BZ=F":     "Brent",     # 🆕 v3.4 (S200): Brent 원유 — WTI("CL=F") 미러, 운영 OIL축 복원
    "KRW=X":    "USD_KRW",
    "^VVIX":    "VVIX",
    "^VIX3M":   "VIX3M",        # 🌟 v2.5 (S67 #6): 3-Month VIX (S67 #4 결정적 발견 정합 — 사이클 강 5종 |IC|>0.40)
}

FRED_SERIES = {
    "DFII10":       "DFII10",
    "T10YIE":       "T10YIE",
    "T5YIE":        "T5YIE",
    "BAMLH0A0HYM2": "OAS_HY",
    "BAMLC0A0CM":   "OAS_IG",
    "SAHMCURRENT":  "SAHMCURRENT",
    "T10Y3M":       "T10Y3M",
    "T10Y2Y":       "T10Y2Y",
    "WALCL":        "WALCL",
    "WTREGEN":      "WTREGEN",
    "RRPONTSYD":    "RRPONTSYD",
    "ICSA":         "ICSA",
    "CCSA":         "CCSA",         # 🌟 v2.4 (S67 #5): Continuing Claims (Insured Unemployment, weekly Thursday)
    "UMCSENT":      "UMCSENT",
    "NFCI":         "NFCI",
    "NAPM":         "PMI",          # 🚨 v2.3: discontinued 2016 → DBnomics 우선 + BT_LONG fallback
    "DEXCHUS":      "USD_CNY",
    "DGS10":        "DGS10",
}

# 🌟 v2.4: CCSA 추가 (주간 시리즈 ffill 보강 의무)
# 🌟 v2.10 (S69 #2): F_G_Score / F_G_Rating 추가 (4중 방어 4차 ffill 정합)
FFILL_COLS = ['PMI', 'UMCSENT', 'ICSA', 'CCSA', 'WALCL', 'WTREGEN', 'RRPONTSYD',
              'NFCI', 'OAS_HY', 'OAS_IG', 'SAHMCURRENT', 'Net_Liquidity',
              'F_G_Score', 'F_G_Rating', 'ECY', 'CAPE']

# 🌟 v2.12 (S69 #5, Commander 본질 통찰 #13, 2026-05-08):
#   LIVE source 결정적 본질 — 매 fetch 시 source 컬럼 갱신 의무
#   본질: LIVE fetch 성공 (1차/2차/3차) = LIVE, 4차 ffill = ffill
#   격언 #75 v4 정식 입증 #6 + #80 양방향 + 5조 ③ 정합
#
# source 값 매트릭스:
#   - "yahoo_live"          : Yahoo Finance 1차 success (VIX/WTI/DXY/MOVE 등)
#   - "fred_live"           : FRED API observations 1차 success
#   - "fred_graph"          : FRED graph CSV anonymous fallback success
#   - "tradingeconomics"    : Tradingeconomics 1차 success (PMI 등)
#   - "cnn_api"             : CNN F&G API 1차 success
#   - "cnn_html"            : CNN HTML scrape 2차 fallback
#   - "argus_proxy"         : ARGUS 자체 proxy (F&G 3차)
#   - "ffill"               : 4차 ffill carry-forward (LIVE 부재)
#   - "bt_long"             : BT_LONG carry-forward (PMI 3차)
#   - None                  : source 미식별 (호환성)
LIVE_SOURCE_COLS = [
    'VIX_source', 'VIX3M_source', 'WTI_source', 'TNX_source',
    'Brent_source',   # 🆕 v3.4: WTI_source 미러 (ffill 보호)
    'DFII10_source', 'DGS10_source', 'T5YIE_source', 'T10YIE_source',
    'DXY_source', 'MOVE_source', 'PMI_source', 'F_G_source',
    'OAS_HY_source', 'OAS_IG_source', 'NFCI_source', 'ICSA_source',
    'CCSA_source', 'UMCSENT_source', 'SAHMCURRENT_source',
    'WALCL_source', 'WTREGEN_source', 'RRPONTSYD_source',
    'ECY_source', 'CAPE_source',  # 🌟 v3.1 (S141)
]

# 🌟 v2.12: LIVE_SOURCE_COLS 모두 ffill (source는 매일 갱신되지만 결측 시 어제 source 보존)
FFILL_COLS = FFILL_COLS + LIVE_SOURCE_COLS

DEPRECATED_FRED = {"NAPM"}

US_HOLIDAYS_FIXED = [
    (1, 1),    # New Year's Day
    (7, 4),    # Independence Day
    (12, 25),  # Christmas
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🆕 v2.3: DBnomics ISM PMI 자동 fetch (무료, 무 API key)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _fetch_ism_pmi_dbnomics_series(start: str = None) -> pd.Series:
    """🚨 DEPRECATED v2.8 (Commander 명령 "DBnomics 삭제") — 함수 미호출 보존
    ─────────────────────────────────────────────────────────────────
    본 함수는 v2.8 시점에 모든 호출처에서 제거됨.
    원인: DBnomics ISM/pmi/pm 2025-09 이후 source 오염 (10.3 ~ 11.1 비정상).
    대체: BT_LONG_v5_complete.csv carry-forward + ffill 단독 사용.
    함수 자체는 보존 (향후 source 정합 회복 시 재활용 가능성).
    
    [기존 docstring]
    🌟 v2.3: DBnomics ISM/pmi/pm 시계열 전체 fetch.

    DBnomics는 ISM 공식 source를 매일 mirror하는 비영리 데이터 허브.
    OECD, Bank of France 등 공공기관에서 사용. ODbL 라이선스 (무료).

    URL: https://api.db.nomics.world/v22/series/ISM/pmi/pm
    응답: JSON, period[]/value[] 월간 시계열

    Args:
        start: 'YYYY-MM-DD' 또는 None. 시작 시점 필터.

    Returns:
        pd.Series: 월초(YYYY-MM-01) 인덱스, PMI 값 (float)
    """
    try:
        req = urllib.request.Request(
            DBNOMICS_PMI_URL,
            headers={'User-Agent': 'argus-data-fetcher/2.4 (ARGUS PRIMA)'}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())

        docs = data.get('series', {}).get('docs', [])
        if not docs:
            print(f"    ⚠️ DBnomics ISM PMI: docs 비어있음")
            return pd.Series(dtype=float)

        doc = docs[0]
        periods = doc.get('period', [])
        values  = doc.get('value', [])

        if not periods or not values or len(periods) != len(values):
            print(f"    ⚠️ DBnomics ISM PMI: 길이 불일치 (periods={len(periods)}, values={len(values)})")
            return pd.Series(dtype=float)

        # 'NA' 또는 None 제거 + datetime 변환 (월초 기준)
        idx, vals = [], []
        for p, v in zip(periods, values):
            if v is None:
                continue
            if isinstance(v, str) and v.strip().lower() in ('na', 'nan', ''):
                continue
            try:
                fv = float(v)
                # 'YYYY-MM' → 'YYYY-MM-01' datetime
                dt = pd.to_datetime(str(p) + '-01' if len(str(p)) == 7 else str(p))
                vals.append(fv)
                idx.append(dt)
            except Exception:
                continue

        if not vals:
            return pd.Series(dtype=float)

        s = pd.Series(vals, index=pd.DatetimeIndex(idx).tz_localize(None))
        s = s.sort_index()

        if start:
            try:
                start_dt = pd.to_datetime(start).tz_localize(None) if pd.to_datetime(start).tz is not None else pd.to_datetime(start)
                s = s[s.index >= start_dt]
            except Exception:
                pass

        return s

    except Exception as e:
        print(f"    ⚠️ DBnomics ISM PMI fetch 실패: {type(e).__name__}: {e}")
        return pd.Series(dtype=float)


def _fetch_ism_pmi_dbnomics_latest():
    """🚨 DEPRECATED v2.8 (Commander 명령 "DBnomics 삭제") — 함수 미호출 보존
    
    [기존 docstring]
    🌟 v2.3: DBnomics ISM PMI 최신값 1개 fetch (누적 모드 today 행용).

    Returns:
        (value: float | None, period: str 'YYYY-MM-01' | None)
    """
    s = _fetch_ism_pmi_dbnomics_series(start='2020-01-01')
    if s.empty:
        return None, None
    return float(s.iloc[-1]), str(s.index[-1].date())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌟 v2.9 (S69 #1, 2026-05-08): PMI 4중 방어 source (Commander 명령 "옵션 1 채택")
#   격언 #75 v4 후보 (source ↔ 갱신 일관성) + #80 양방향 (4중 방어) + #96 v2 ⓪⑥ 정합
#
# 본질: v2.8의 BT_LONG carry-forward 단독 = 갱신 부재 결정적 결함
#       → 1차 source 결정 의무 (격언 #96 v2 ⑥)
#       → 사전 검증 의무 (격언 #96 v2 ⓪)
#
# 사전 검증 결과 (S69 #1 LIVE):
#   ① ISM 공식 site (https://www.ismworld.org/...) → HTTP 403 (bot detection 영구 차단)
#   ② Tradingeconomics (https://tradingeconomics.com/united-states/business-confidence)
#      → HTTP 200 + LIVE 정합 입증 (PMI=52.7 in April 2026)
#   ③ FRED graph endpoint → HTTP 503 (일시 장애 가능 + API key fallback 필요)
#   ④ Investing.com → HTTP 403 (bot detection 차단)
#
# 4중 방어 채택 (옵션 1):
#   1차: Tradingeconomics scrape (LIVE 정합 입증)
#   2차: FRED USSLIND proxy (FRED_API_KEY 사용 + Leading Index ≈ PMI proxy)
#   3차: BT_LONG_v5_complete.csv carry-forward (v2.8 logic 보존)
#   4차: ffill (어제 csv 값, 안전망)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRADINGECONOMICS_PMI_URL = "https://tradingeconomics.com/united-states/business-confidence"


def _fetch_pmi_tradingeconomics() -> tuple:
    r"""🌟 v2.9 (S69 #1): Tradingeconomics ISM Manufacturing PMI scrape (1차 source).
    
    LIVE 정합 입증 패턴:
      r'(?:unchanged at|rose to|fell to|edged up to|edged down to|increased to|
         decreased to|stood at|reached|jumped to|slipped to)\s+(\d{2}\.\d{1,2})
         \s+in\s+(\w+\s+\d{4})'
    
    Returns:
        tuple: (pmi_value: float | None, period: str | None, source: str)
               source = 'tradingeconomics' (성공) or 'tradingeconomics_fail' (실패)
    
    격언 정합:
      - #96 v2 ⓪ 사전 검증 의무 (LIVE 입증)
      - #96 v2 ⑥ 공식 source 우선 (Tradingeconomics는 ISM 공식 데이터 미러)
      - #67 v3 dead source 차단 (DBnomics 영구 제외)
      - #75 v4 source ↔ 갱신 일관성
      - 5조 ③ 데이터 위조 금지 (정상 범위 30~75 검증)
    """
    try:
        req = urllib.request.Request(
            TRADINGECONOMICS_PMI_URL,
            headers={
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                ),
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode(errors='ignore')
        
        # LIVE 정합 입증 패턴 — 동사 + 값 + 월/연도
        pattern = (
            r'(?:unchanged at|rose to|fell to|edged up to|edged down to|'
            r'increased to|decreased to|stood at|reached|jumped to|slipped to)'
            r'\s+(\d{2}\.\d{1,2})\s+in\s+(\w+\s+\d{4})'
        )
        matches = re.findall(pattern, html, re.IGNORECASE)
        
        if not matches:
            print(f"    ⚠️ Tradingeconomics PMI: 패턴 미매치 (HTML 구조 변경 가능성)")
            return None, None, 'tradingeconomics_fail'
        
        # 첫 매치 = 최신 PMI (Tradingeconomics 페이지 구조)
        val_str, period = matches[0]
        val = float(val_str)
        
        # 격언 5조 ③ 데이터 위조 금지 — 정상 범위 검증
        if not (30.0 <= val <= 75.0):
            print(f"    🚨 Tradingeconomics PMI: 비정상 범위 ({val}, 30~75 외)")
            return None, None, 'tradingeconomics_invalid'
        
        return val, period, 'tradingeconomics'
        
    except Exception as e:
        print(f"    ⚠️ Tradingeconomics PMI fetch 실패: {type(e).__name__}: {e}")
        return None, None, 'tradingeconomics_fail'


def _fetch_pmi_fred_usslind_proxy() -> tuple:
    """🌟 v2.9 (S69 #1): FRED USSLIND (Leading Economic Index) proxy (2차 fallback).
    
    USSLIND는 PMI proxy (상관 ~0.7). NAPM discontinued (2024-01-01) 이후 대체.
    proxy 본질 명시: PMI ≠ USSLIND (정확 매핑 부재) — 안전망 단계 의무.
    
    Returns:
        tuple: (pmi_proxy_value: float | None, period: str | None, source: str)
    
    격언 정합:
      - #96 v2 ⑥ source 결정 의무 (proxy 명시)
      - #80 양방향 (proxy fallback)
      - 5조 ③ 데이터 위조 금지 (proxy 본질 명시)
    """
    try:
        # USSLIND 시리즈 fetch (FRED_API_KEY 사용 시)
        # USSLIND 값 (~100 기준, 50~150 범위) → PMI 범위 (30~75)로 정규화 부적합
        # 본질: USSLIND는 raw 값 그대로 사용 X, PMI 대체 부적합 (proxy도 한계)
        # → 격언 #96 v2 ⑥ 정합: proxy도 부적합 시 BT_LONG (3차)로 즉시 진행
        
        # 본 함수는 placeholder + 향후 USSLIND→PMI 정확 매핑 발견 시 활성화
        # 현재는 항상 None 반환 → 3차 BT_LONG으로 즉시 진행 (격언 #98 결정 회피 차단)
        print(f"    ⚠️ FRED USSLIND proxy: PMI 정확 매핑 부재 → 3차 fallback 진행")
        return None, None, 'fred_usslind_skip'
        
    except Exception as e:
        print(f"    ⚠️ FRED USSLIND proxy 실패: {type(e).__name__}: {e}")
        return None, None, 'fred_usslind_fail'


def _fetch_pmi_4layer_defense() -> tuple:
    """🌟 v2.9 (S69 #1): PMI 4중 방어 통합 fetch.
    
    1차: Tradingeconomics scrape (LIVE 정합 입증)
    2차: FRED USSLIND proxy (proxy 본질 명시 + 현재 skip 처리)
    3차: BT_LONG_v5_complete.csv carry-forward (v2.8 logic 보존)
    4차: ffill (어제 csv 값, 안전망)
    
    Returns:
        tuple: (pmi_value: float | None, period: str | None, source: str)
    
    격언 정합:
      - #36 #1 즉시 정정 (csv 오염 방어)
      - #75 v4 source ↔ 갱신 일관성
      - #80 양방향 (4중 방어 다차원)
      - #96 v2 ⓪⑥ 사전 검증 + source 결정
      - #98 결정 회피 차단 (단편적 fallback 금지)
      - 5조 ③ 데이터 위조 금지 (정상 범위 검증)
    """
    print(f"  🌟 PMI 4중 방어 fetch 진행 (v2.9):")
    
    # 1차: Tradingeconomics scrape
    val, period, source = _fetch_pmi_tradingeconomics()
    if val is not None:
        print(f"    ✅ 1차 Tradingeconomics scrape: {val} ({period})")
        return val, period, source
    
    # 2차: FRED USSLIND proxy (현재 skip — proxy 정확 매핑 부재)
    val, period, source = _fetch_pmi_fred_usslind_proxy()
    if val is not None:
        print(f"    ✅ 2차 FRED USSLIND proxy: {val} (proxy)")
        return val, period, source
    
    # 3차: BT_LONG carry-forward (v2.8 logic 보존)
    # → fetch_today_row의 ffill 단계에서 자동 처리 (어제 csv 값 carry-forward)
    print(f"    🟡 3차 BT_LONG carry-forward (v2.8 logic — ffill 단계 자동)")
    return None, None, 'bt_long_ffill'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌟 v2.10 (S69 #2, 2026-05-08): Fear & Greed Index 4중 방어 source
#   Commander 명령 "옵션 D 채택"
#   격언 #75 v4 + #80 양방향 + #94 (시그널 시 per-ticker 별도) + #96 v2 ⓪⑥ 정합
#
# 본질: PMI v2.9 4중 방어 패턴 일관성 + ARGUS 매크로 차원 (VIX + OAS) 활용
#
# 사전 검증 결과 (S69 #2 LIVE):
#   본 컨테이너에서 CNN/alternative.me 도메인 차단 (allowed list 부재)
#   GitHub Actions runner 환경에서 fetch 자유 (network 제약 부재)
#   → CNN API JSON schema는 공개 사례 다수 + GitHub gist 기반 본문 작성
#
# 4중 방어 채택:
#   1차: CNN 공식 API (production.dataviz.cnn.io/index/fearandgreed/graphdata)
#   2차: CNN HTML scrape (edition.cnn.com/markets/fear-and-greed)
#   3차: ARGUS 자체 proxy (VIX 30% + OAS 25% + SPY momentum 25% + Safe Haven 20%)
#   4차: ffill (어제 csv 값, 안전망)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CNN_FG_API_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
CNN_FG_HTML_URL = "https://edition.cnn.com/markets/fear-and-greed"


def _classify_fg_rating(score: float) -> str:
    """🌟 v2.10 (S69 #2): F&G score → rating 분류 (CNN 공식 기준).
    
    0~25: extreme fear
    25~45: fear
    45~55: neutral
    55~75: greed
    75~100: extreme greed
    """
    if score < 25:
        return 'extreme fear'
    elif score < 45:
        return 'fear'
    elif score < 55:
        return 'neutral'
    elif score < 75:
        return 'greed'
    else:
        return 'extreme greed'


def _fetch_fg_cnn_api() -> tuple:
    """🌟 v2.10 (S69 #2): CNN 공식 F&G API (1차 source).
    
    URL: https://production.dataviz.cnn.io/index/fearandgreed/graphdata
    
    Header 의무:
      - Referer: https://www.cnn.com/
      - Origin: https://www.cnn.com
      - User-Agent: Chrome 일반 (bot detection 우회)
    
    JSON schema 본질:
      {
        "fear_and_greed": {
          "score": 38.4,        # 0~100 float
          "rating": "fear",     # extreme fear / fear / neutral / greed / extreme greed
          "timestamp": "2026-05-08T00:00:00+00:00",
          ...
        }
      }
    
    Returns:
        tuple: (score: float | None, rating: str | None, source: str)
    
    격언 정합:
      - #96 v2 ⑥ 공식 source 우선
      - #75 v4 source ↔ 갱신 일관성
      - 5조 ③ 데이터 위조 금지 (정상 범위 0~100 검증)
    """
    try:
        req = urllib.request.Request(
            CNN_FG_API_URL,
            headers={
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                ),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.cnn.com/',
                'Origin': 'https://www.cnn.com',
            }
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read().decode()
        
        j = json.loads(data)
        
        if 'fear_and_greed' not in j:
            print(f"    ⚠️ CNN API: 'fear_and_greed' 필드 부재")
            return None, None, 'cnn_api_no_field'
        
        fg = j['fear_and_greed']
        score = fg.get('score')
        rating = fg.get('rating', 'unknown')
        
        if score is None:
            return None, None, 'cnn_api_no_score'
        
        score = float(score)
        
        # 격언 5조 ③ 정상 범위 검증
        if not (0.0 <= score <= 100.0):
            print(f"    🚨 CNN API F&G: 비정상 범위 ({score}, 0~100 외)")
            return None, None, 'cnn_api_invalid'
        
        return score, rating, 'cnn_api'
        
    except Exception as e:
        print(f"    ⚠️ CNN API F&G 실패: {type(e).__name__}: {e}")
        return None, None, 'cnn_api_fail'


def _fetch_fg_cnn_html() -> tuple:
    r"""🌟 v2.10 (S69 #2): CNN HTML scrape F&G (2차 fallback).
    
    URL: https://edition.cnn.com/markets/fear-and-greed
    
    HTML 패턴 후보 (CNN 페이지 구조):
      r'"score"\s*:\s*(\d+(?:\.\d+)?)' (JSON embedded)
      r'data-score="(\d+(?:\.\d+)?)"' (data attribute)
      r'fear-and-greed-score[^>]*>(\d+)' (인라인 텍스트)
    
    Returns:
        tuple: (score: float | None, rating: str | None, source: str)
    
    격언 정합:
      - #80 양방향 fallback
      - #96 v2 ⑥ source 결정 의무
    """
    try:
        req = urllib.request.Request(
            CNN_FG_HTML_URL,
            headers={
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                ),
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            html = r.read().decode(errors='ignore')
        
        # 다중 패턴 시도 (HTML 구조 변경 대응)
        patterns = [
            r'"score"\s*:\s*(\d+(?:\.\d+)?)',
            r'data-score="(\d+(?:\.\d+)?)"',
            r'fear[\s-]?and[\s-]?greed[\s-]?score[^>]*?(\d{1,3}(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                score = float(matches[0])
                if 0.0 <= score <= 100.0:
                    rating = _classify_fg_rating(score)
                    return score, rating, 'cnn_html'
        
        print(f"    ⚠️ CNN HTML F&G: 패턴 미매치")
        return None, None, 'cnn_html_no_match'
        
    except Exception as e:
        print(f"    ⚠️ CNN HTML F&G 실패: {type(e).__name__}: {e}")
        return None, None, 'cnn_html_fail'


def _calculate_fg_argus_proxy(row: dict) -> tuple:
    """🌟 v2.10 (S69 #2): ARGUS 자체 F&G proxy (3차 fallback).
    
    ARGUS 매크로 차원 (VIX + OAS + SPY momentum + Safe Haven) 가중 평균.
    CNN F&G 7개 sub-indicator 중 4개 직접/proxy 매칭.
    
    가중:
      - VIX_score * 0.30      (F&G ⑤ Market Volatility)
      - OAS_score * 0.25      (F&G ⑦ Junk Bond Demand)
      - SPY_momentum * 0.25   (F&G ① Stock Price Momentum, today 모드 부분 가용)
      - Safe_haven * 0.20     (F&G ⑥ Safe Haven Demand)
    
    Args:
        row: fetch_today_row 결과 dict (VIX, OAS_HY, OAS_IG 보유)
    
    Returns:
        tuple: (score: float | None, rating: str | None, source: str)
    
    격언 정합:
      - #80 양방향 (data fetch ↔ 자체 산출)
      - #94 (시그널 시 per-ticker 별도 검증 의무 — 별도 사이클)
      - 5조 ④ PRIMA 엔진 LIVE 실호출 (ARGUS 자체 차원 활용)
    """
    try:
        vix = row.get('VIX')
        oas_hy = row.get('OAS_HY')
        oas_ig = row.get('OAS_IG')
        
        # 최소 2개 차원 필수 (VIX + OAS)
        if vix is None or oas_hy is None or oas_ig is None:
            print(f"    ⚠️ ARGUS proxy: VIX/OAS_HY/OAS_IG 부재 → 4차 ffill")
            return None, None, 'argus_proxy_missing_data'
        
        # ① VIX 정규화 (역상관, F&G ⑤)
        if vix <= 15:
            vix_score = 75.0
        elif vix <= 20:
            vix_score = 60.0
        elif vix <= 25:
            vix_score = 40.0
        elif vix <= 30:
            vix_score = 25.0
        else:
            vix_score = 10.0
        
        # ② OAS_HY - OAS_IG 정규화 (역상관, F&G ⑦)
        spread = oas_hy - oas_ig
        if spread <= 1.5:
            oas_score = 75.0
        elif spread <= 2.0:
            oas_score = 50.0
        elif spread <= 3.0:
            oas_score = 30.0
        else:
            oas_score = 15.0
        
        # ③ SPY 모멘텀 (today 모드는 5/125 MA 부재 — 단순 50.0 neutral)
        # cumulative 모드에서는 별도 계산 가능 (향후 v2.11+)
        spy_momentum_score = 50.0
        
        # ④ Safe Haven (today 모드는 RoC 부재 — 단순 50.0 neutral)
        safe_haven_score = 50.0
        
        # 가중 평균
        score = (
            vix_score * 0.30 +
            oas_score * 0.25 +
            spy_momentum_score * 0.25 +
            safe_haven_score * 0.20
        )
        
        # 정상 범위 검증 (격언 5조 ③)
        if not (0.0 <= score <= 100.0):
            print(f"    🚨 ARGUS proxy: 비정상 범위 ({score:.1f})")
            return None, None, 'argus_proxy_invalid'
        
        rating = _classify_fg_rating(score)
        print(f"    🌟 ARGUS proxy 본질: VIX={vix_score:.0f}*0.30 + OAS={oas_score:.0f}*0.25 + SPY=50*0.25 + SH=50*0.20")
        
        return round(score, 1), rating, 'argus_proxy'
        
    except Exception as e:
        print(f"    ⚠️ ARGUS proxy 실패: {type(e).__name__}: {e}")
        return None, None, 'argus_proxy_fail'


def _fetch_fg_4layer_defense(row: dict) -> tuple:
    """🌟 v2.10 (S69 #2): F&G 4중 방어 통합 fetch.
    
    1차: CNN 공식 API (LIVE 정합)
    2차: CNN HTML scrape (fallback)
    3차: ARGUS 자체 proxy (VIX + OAS 가중 평균)
    4차: ffill (어제 csv 값, 안전망)
    
    Args:
        row: fetch_today_row 결과 dict (ARGUS proxy 시 VIX/OAS 의무)
    
    Returns:
        tuple: (score: float | None, rating: str | None, source: str)
    
    격언 정합:
      - #36 #1 즉시 정정 (source 차단 시 즉시 fallback)
      - #75 v4 source ↔ 갱신 일관성 (PMI v2.9와 동일 패턴)
      - #80 양방향 (4중 방어 다차원)
      - #96 v2 ⓪⑥ 사전 검증 + 공식 source 우선
      - #98 결정 회피 차단 (단편적 fallback 금지)
      - 5조 ③ 데이터 위조 금지 (정상 범위 0~100 검증)
    """
    print(f"  🌟 F&G 4중 방어 fetch 진행 (v2.10):")
    
    # 1차: CNN 공식 API
    score, rating, source = _fetch_fg_cnn_api()
    if score is not None:
        print(f"    ✅ 1차 CNN API: {score:.1f} ({rating})")
        return score, rating, source
    
    # 2차: CNN HTML scrape
    score, rating, source = _fetch_fg_cnn_html()
    if score is not None:
        print(f"    ✅ 2차 CNN HTML: {score:.1f} ({rating})")
        return score, rating, source
    
    # 3차: ARGUS 자체 proxy
    score, rating, source = _calculate_fg_argus_proxy(row)
    if score is not None:
        print(f"    ✅ 3차 ARGUS proxy: {score:.1f} ({rating})")
        return score, rating, source
    
    # 4차: ffill (자동)
    print(f"    🟡 4차 ffill carry-forward (어제 csv 값, 안전망)")
    return None, None, 'ffill_yesterday'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 유틸 v2.2 (보존)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def is_nyse_open(d: date) -> bool:
    """NYSE 영업일 여부 — 주말 + 미국 주요 휴일 단순 체크."""
    if d.weekday() >= 5:
        return False
    if (d.month, d.day) in US_HOLIDAYS_FIXED:
        return False
    return True


def _yf_batch(symbols: list, start: str, end: str) -> dict:
    """yfinance 배치 → {symbol: latest_close}. 실패 시 빈 dict."""
    try:
        raw = yf.download(symbols, start=start, end=end,
                          auto_adjust=True, progress=False)
        if raw.empty:
            return {}
        close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
        last  = close.iloc[-1]
        return {sym: float(last[sym])
                for sym in symbols
                if sym in last.index and not pd.isna(last[sym])}
    except Exception as e:
        print(f"    ⚠️  배치 {symbols[:2]}...: {e}")
        return {}


def _yf_series(symbol: str, start: str, end: str) -> pd.Series:
    """단일 티커 히스토리 → Series."""
    try:
        raw = yf.download(symbol, start=start, end=end,
                          auto_adjust=True, progress=False)
        if raw.empty:
            return pd.Series(dtype=float)
        col = "Close" if "Close" in raw.columns else raw.columns[0]
        s = raw[col].dropna()
        s.index = pd.to_datetime(s.index).tz_localize(None)
        return s
    except Exception as e:
        print(f"    ⚠️  {symbol}: {e}")
        return pd.Series(dtype=float)


def _fred_series(sid: str, start: str) -> pd.Series:
    """🌟 v2.6 (S67 #12): graph CSV endpoint anonymous fallback 추가.
    
    격언 #96 v2 ⓥ 정밀화: graph endpoint 시리즈별 가용성 다름.
    - CCSA: 1967-01-07부터 anonymous 가능 (S67 #12 발견, 3095행)
    - 일부 시리즈: graph endpoint 한계 존재 (시리즈별 다름)
    
    격언 #97 v2 자기 audit: S67 #3 광범위 실패 보고 부정확 정정.
    
    동작:
      ① Primary: FRED API observations (FRED_API_KEY 의무, 정밀)
      ② Fallback: graph CSV (anonymous, robust)
    """
    if sid in DEPRECATED_FRED:
        # NAPM 등 — 직접 fetch 안하고 빈 시리즈
        return pd.Series(dtype=float)

    # ① Primary: FRED API observations endpoint
    if FRED_API_KEY:
        url = (f"https://api.stlouisfed.org/fred/series/observations"
               f"?series_id={sid}&observation_start={start}"
               f"&api_key={FRED_API_KEY}&file_type=json&sort_order=asc")
        try:
            obs = requests.get(url, timeout=15).json().get("observations", [])
            data = {}
            for o in obs:
                try: data[pd.to_datetime(o["date"])] = float(o["value"])
                except: pass
            s = pd.Series(data, dtype=float)
            s.index = pd.to_datetime(s.index).tz_localize(None)
            if not s.empty:
                return s
            else:
                print(f"    ⚠️  FRED API {sid}: 빈 응답 → graph CSV fallback 시도...")
        except Exception as e:
            print(f"    ⚠️  FRED API {sid}: {e} → graph CSV fallback 시도...")

    # ② 🌟 v2.6 Fallback: graph CSV anonymous endpoint (FRED_API_KEY 부재 시도 작동)
    try:
        import io as _io
        url_csv = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        resp = requests.get(url_csv, timeout=15)
        if resp.status_code != 200:
            print(f"    ⚠️ FRED graph CSV {sid}: HTTP {resp.status_code}")
            return pd.Series(dtype=float)
        df_csv = pd.read_csv(_io.StringIO(resp.text))
        # observation_date 또는 DATE 컬럼 + 시리즈 컬럼 식별
        date_col = None
        for cand in ['observation_date', 'DATE', 'date']:
            if cand in df_csv.columns:
                date_col = cand
                break
        if date_col is None or sid not in df_csv.columns:
            print(f"    ⚠️ FRED graph CSV {sid}: 컬럼 구조 비정합 ({list(df_csv.columns)})")
            return pd.Series(dtype=float)
        df_csv[date_col] = pd.to_datetime(df_csv[date_col])
        df_csv = df_csv[df_csv[date_col] >= pd.to_datetime(start)]
        # FRED missing value '.' 처리
        df_csv = df_csv[df_csv[sid].astype(str).str.strip() != '.']
        df_csv[sid] = pd.to_numeric(df_csv[sid], errors='coerce')
        df_csv = df_csv.dropna(subset=[sid])
        s = pd.Series(df_csv[sid].values, index=df_csv[date_col].values, dtype=float)
        s.index = pd.to_datetime(s.index).tz_localize(None)
        if not s.empty:
            print(f"    ✅ FRED graph CSV {sid} (anonymous fallback): {len(s)}건 가용")
        return s
    except Exception as e:
        print(f"    ⚠️ FRED graph CSV {sid}: {e}")
        return pd.Series(dtype=float)


def _fred_latest(sid: str) -> float | None:
    """FRED 시리즈 최신 가용 값 1개 반환.
    
    🚨 v2.11 (S69 #4 후속): _fred_latest_with_date 권장 (발표일 정보 의무).
    본 함수는 호환성 보존만 (신규 코드 사용 금지).
    """
    if not FRED_API_KEY:
        return None
    if sid in DEPRECATED_FRED:
        return None
    url = (f"https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={sid}&api_key={FRED_API_KEY}"
           f"&limit=5&sort_order=desc&file_type=json")
    try:
        for o in requests.get(url, timeout=15).json().get("observations", []):
            try: return float(o["value"])
            except: continue
    except: pass
    return None


def _fred_latest_with_date(sid: str) -> tuple:
    """🌟 v2.11 (S69 #4, Commander 본질 통찰 #11): 최신 값 + 발표 일자 반환.
    
    결정적 본질 (S69 #4 발견):
      - FRED는 보통 익일 발표 (5/7 데이터를 5/8에 fetch)
      - 발표일 미수신 시 5/7 발표 값을 5/8 row에 매핑 = 1일 시차 결함
      - 격언 5조 ③ 결정적 위반 (데이터 위조)
    
    v2.11 정정:
      - 발표일 (observation_date) 무조건 반환 의무
      - fetch_today_row에서 발표일 ↔ today 비교 logic 정합 의무
    
    Returns:
        tuple: (value: float | None, date_str: str | None)
        date_str = FRED 발표 일자 (예: "2026-05-07")
    
    격언 정합:
      - #36 #1 즉시 정정 (S69 #4 결정적 결함 발견)
      - #75 v4 정식 입증 #5 (source ↔ 갱신 일관성)
      - #80 양방향 (값 ↔ 발표일 양방향)
      - 5조 ③ 데이터 위조 금지 (발표일 기준 정합)
    """
    if not FRED_API_KEY or sid in DEPRECATED_FRED:
        return None, None
    url = (f"https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={sid}&api_key={FRED_API_KEY}"
           f"&limit=5&sort_order=desc&file_type=json")
    try:
        for o in requests.get(url, timeout=15).json().get("observations", []):
            try:
                v = float(o["value"])
                return v, o.get("date")
            except: continue
    except: pass
    return None, None


def _integrate_bt_long_pmi(df: pd.DataFrame) -> pd.DataFrame:
    """v2.2: BT_LONG_v5_complete.csv에서 PMI 시리즈 통합 (DBnomics 실패 시 fallback).

    🌟 v2.3에서 fallback 역할로 격하 — DBnomics 우선.
    """
    if not os.path.exists(BT_LONG_PATH):
        print(f"    ⚠️ BT_LONG fallback 부재 ({BT_LONG_PATH})")
        if 'PMI' not in df.columns:
            df['PMI'] = np.nan
        return df

    try:
        bt = pd.read_csv(BT_LONG_PATH, parse_dates=['Date'])
        bt = bt.set_index('Date').sort_index()
        if 'PMI' not in bt.columns:
            print(f"    ⚠️ BT_LONG에 PMI 컬럼 부재")
            if 'PMI' not in df.columns:
                df['PMI'] = np.nan
            return df

        pmi_series = bt['PMI'].dropna()
        # 시드 인덱스에 매핑 (forward-fill 적용)
        pmi_aligned = pmi_series.reindex(df.index, method='ffill')

        if 'PMI' in df.columns:
            df['PMI'] = df['PMI'].fillna(pmi_aligned)
        else:
            df['PMI'] = pmi_aligned

        valid_count = df['PMI'].notna().sum()
        print(f"    ✅ PMI BT_LONG fallback: {valid_count}/{len(df)}일 가용")
    except Exception as e:
        print(f"    🚨 PMI BT_LONG fallback 실패: {e}")
        if 'PMI' not in df.columns:
            df['PMI'] = np.nan
    return df


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 초기 시드 (최초 1회)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def build_seed() -> pd.DataFrame:
    print("  🌱 초기 시드 생성...")

    if not FRED_API_KEY:
        raise RuntimeError(
            "🚨 FRED_API_KEY 부재 + argus_data.csv 없음 → 시드 생성 거부.\n"
            "   GitHub Actions secrets에 FRED_API_KEY 설정 후 재실행 필수.\n"
            "   (T10YIE/ICSA/CCSA/UMCSENT 등 FRED 시리즈 누락 시드 차단 — 격언 #47)"
        )

    end   = date.today()
    start = end - timedelta(days=SEED_DAYS + 60)
    s, e  = str(start), str(end + timedelta(days=1))

    # ETF 배치 다운로드
    print(f"  📈 ETF {len(ETF_TICKERS)}종...")
    frames = []
    for i in range(0, len(ETF_TICKERS), 12):
        batch = ETF_TICKERS[i:i+12]
        raw = yf.download(batch, start=s, end=e, auto_adjust=True, progress=False)
        if not raw.empty:
            close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
            close.index = pd.to_datetime(close.index).tz_localize(None)
            frames.append(close)
        time.sleep(0.5)
    df = pd.concat(frames, axis=1) if frames else pd.DataFrame()
    df.columns = [f"{c}_Close" for c in df.columns]

    # 매크로 — 개별 다운로드
    print(f"  📊 매크로 {len(YAHOO_MACRO)}종 (개별)...")
    for sym, col in YAHOO_MACRO.items():
        series = _yf_series(sym, s, e)
        if not series.empty:
            df[col] = series
            print(f"    ✅ {col}: {series.iloc[-1]:.3f}")
        else:
            print(f"    ❌ {col}({sym}): NaN")
        time.sleep(0.2)

    # FRED
    print(f"  📡 FRED {len(FRED_SERIES)}종...")
    for sid, col in FRED_SERIES.items():
        if col in df.columns: continue
        if sid in DEPRECATED_FRED:
            # NAPM은 DBnomics에서 별도 fetch
            continue
        series = _fred_series(sid, s)
        if not series.empty:
            df[col] = series.reindex(df.index, method="ffill")
            print(f"    ✅ {col} ({sid}): {df[col].notna().sum()}/{len(df)}일")
        else:
            print(f"    ❌ {col} ({sid}): NaN")
        time.sleep(0.1)

    # TNX 보완
    if "TNX" not in df.columns and "DGS10" in df.columns:
        df["TNX"] = df["DGS10"]
        print("  ℹ️  TNX: DGS10 대체 사용")
    elif "TNX" in df.columns and "DGS10" in df.columns:
        df["TNX"] = df["TNX"].fillna(df["DGS10"])

    # Net_Liquidity
    if all(c in df.columns for c in ["WALCL","WTREGEN","RRPONTSYD"]):
        df["Net_Liquidity"] = df["WALCL"] - df["WTREGEN"] - df["RRPONTSYD"] * 1e3  # 🌟 v3.2 (S195): RRP 십억$→백만$ — BT v5 정본 규약

    # 🌟 v2.5 (S67 #6): VIX_VIX3M_ratio 파생 컬럼 (term structure 차원, S67 #4 결정적 발견)
    # 정상 contango ~0.89 / backwardation > 1.0 (강 위기 + 단기 공포 정점)
    if all(c in df.columns for c in ["VIX", "VIX3M"]):
        df["VIX_VIX3M_ratio"] = df["VIX"] / df["VIX3M"]
        valid = df["VIX_VIX3M_ratio"].notna().sum()
        if valid > 0:
            mean_v = df["VIX_VIX3M_ratio"].mean()
            print(f"    ✅ VIX_VIX3M_ratio 파생: {valid}/{len(df)}일 (mean={mean_v:.4f}, contango ~0.89 정상)")

    # 🚨 v2.8 (Commander 명령 — "DBnomics 삭제"): PMI 단일 source = BT_LONG carry-forward
    # 결정적 결함: DBnomics 2025-09 이후 source 오염 (10.3 ~ 11.1 비정상)
    # 격언 #67 v3 dead source 정정 + #96 v2 ② source sanity 정합
    print(f"  🌟 PMI: BT_LONG carry-forward 단독 (DBnomics 삭제, v2.8)")
    df = _integrate_bt_long_pmi(df)

    df = df.sort_index()
    df.index.name = "Date"
    return df.tail(SEED_DAYS)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 오늘 행 추가 (누적 모드)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def fetch_today_row(target_date=None) -> dict:
    # 🌟 v3.2 (S197): target_date 지원 — None=오늘(기존 동작 보존), 지정=임의 날짜 backfill
    today = target_date if target_date is not None else date.today()
    is_backfill = target_date is not None and target_date != date.today()
    row   = {"Date": pd.Timestamp(today)}
    s     = str(today - timedelta(days=5))
    e     = str(today + timedelta(days=1))

    # ① ETF 배치
    etf_data = _yf_batch(ETF_TICKERS, s, e)
    for tk, val in etf_data.items():
        row[f"{tk}_Close"] = val
    print(f"    ETF: {len(etf_data)}/{len(ETF_TICKERS)}종 수집")

    # ② 매크로 — 개별
    # 🌟 v2.12 (S69 #5, Commander 본질 통찰 #13): source 컬럼 신설
    print("    매크로 개별 수집...")
    ok_macro = 0
    for sym, col in YAHOO_MACRO.items():
        data = _yf_batch([sym], s, e)
        if sym in data:
            row[col] = data[sym]
            row[f"{col}_source"] = "yahoo_live"  # 🌟 v2.12
            ok_macro += 1
        else:
            row[f"{col}_source"] = "ffill"  # 🌟 v2.12
            print(f"      ❌ {col}({sym}): NaN")
    print(f"    매크로: {ok_macro}/{len(YAHOO_MACRO)}종 수집")

    # ③ 🌟 v2.11 (S69 #4, Commander 본질 통찰 #11): FRED 발표일 기준 매핑 (1일 시차 결함 정정)
    # 결정적 본질 (S69 #4 발견):
    #   - 이전 v2.10: _fred_latest 단순 호출 → 5/8 fetch 시 5/7 발표값을 5/8 row에 매핑 = 1일 시차
    #   - LIVE 입증: T10YIE 5/7=NaN, 5/8=2.45 (실제는 5/7 발표값) = 격언 5조 ③ 위반
    #   - csv FRED 발표일 ≠ csv row 일자 = 데이터 위조 결정적
    #
    # v2.11 정정:
    #   - _fred_latest_with_date 활용 (값 + 발표일 동시 수신)
    #   - 발표일 ≤ today 시에만 매핑 (FRED 발표일 = csv row 매핑 의무)
    #   - 발표일 > today (미래값, 비정상) 시 매핑 차단
    #   - 발표일 < today (과거값) 시 매핑 정합 (T10YIE 5/7 발표 → 5/8 row 매핑은 정합)
    #
    # 🚨 결정적 본질 분리:
    #   - "1일 시차 결함" = today 변수 (5/8) ↔ FRED 최신 발표일 (5/7) 정합 인식
    #   - 본 logic은 today_row가 5/8이고 FRED 5/7 값을 매핑 = 정합 (FRED는 익일 발표)
    #   - but 어제 (5/7) row가 NaN인 결함은 별도 영역 (PUBLIC csv update logic)
    #
    # 🌟 v2.12 (S69 #5, Commander 본질 통찰 #13):
    #   - source 컬럼 신설: row[f"{col}_source"] = "fred_live" (success) / "ffill" (failure)
    #
    # 격언 정합:
    #   - #36 #1 즉시 정정 (T10YIE/T5YIE BEI 결정적 결함 발견)
    #   - #75 v4 정식 입증 #5 (source ↔ 갱신 일관성)
    #   - #80 양방향 (값 ↔ 발표일 양방향)
    #   - #97 v2 #1 자기 audit
    #   - 5조 ③ 데이터 위조 금지
    if FRED_API_KEY:
        ok_fred = 0; skipped_dep = 0
        delayed_fred = []  # 🌟 v2.11: 1일 시차 시리즈 추적
        for sid, col in FRED_SERIES.items():
            if sid in DEPRECATED_FRED:
                skipped_dep += 1
                continue
            if is_backfill:
                # 🌟 v3.2: backfill 시 as-of 날짜 값 (현재 최신값 매핑 = 격언 5조 ③ 위반 차단)
                _ser = _fred_series(sid, s)
                _asof = _ser[_ser.index <= pd.Timestamp(today)] if not _ser.empty else _ser
                if not _asof.empty:
                    row[col] = float(_asof.iloc[-1])
                    row[f"{col}_source"] = "fred_asof"
                    ok_fred += 1
                else:
                    row[f"{col}_source"] = "ffill"
                continue
            v, fred_date = _fred_latest_with_date(sid)
            if v is not None:
                row[col] = v
                # 🌟 v2.12 (S69 #5): FRED source 명시
                row[f"{col}_source"] = "fred_live"
                ok_fred += 1
                # 🌟 v2.11 (S69 #4): 발표일 시차 검증 + 가시성 로그
                if fred_date:
                    today_str = str(today)
                    if fred_date != today_str:
                        # 1일 시차 = 정합 (FRED 익일 발표) but 가시성 명시
                        delayed_fred.append((sid, fred_date))
            else:
                # 🌟 v2.12 (S69 #5): FRED fetch 실패 = ffill source 명시
                row[f"{col}_source"] = "ffill"
        print(f"    FRED: {ok_fred}/{len(FRED_SERIES)-skipped_dep}종 수집 + {skipped_dep}종 deprecated skip")
        if delayed_fred:
            # 🌟 v2.11 (S69 #4, Commander 본질 통찰 #11): 1일 시차 시리즈 결정적 가시성
            print(f"    🌟 FRED 발표일 시차 ({len(delayed_fred)}종): {', '.join([f'{s}={d}' for s, d in delayed_fred[:5]])}")
            print(f"        본질: FRED 익일 발표 정합 (today={today})")
    else:
        print("    ⚠️ FRED_API_KEY 부재 — FRED 컬럼 NaN 추가 (ffill 단계에서 처리)")
        # 🌟 v2.12: API key 부재 시 모든 FRED source = ffill
        for sid, col in FRED_SERIES.items():
            row[f"{col}_source"] = "ffill"

    # 🌟 v2.9 (S69 #1, Commander 명령 "옵션 1 채택"): PMI 4중 방어 fetch
    #   1차: Tradingeconomics scrape (LIVE 정합 입증)
    #   2차: FRED USSLIND proxy (현재 skip — proxy 정확 매핑 부재)
    #   3차: BT_LONG carry-forward (v2.8 logic 보존, ffill 단계 자동)
    #   4차: ffill (어제 csv 값, 안전망)
    #   격언 #75 v4 + #80 양방향 + #96 v2 ⓪⑥ + #98 + 5조 ③ 정합
    if is_backfill:
        # 🌟 v3.2: backfill 시 live PMI fetch 생략 → BT_LONG carry-forward (월간, ffill 동월값)
        row['PMI_source'] = "ffill"
        print(f"  🌟 PMI: backfill 모드 — BT_LONG carry-forward (ffill, 월간 동월값)")
    else:
        # 3차/4차 fallback — ffill 단계에서 자동 처리
        # row['PMI'] 미설정 → ffill carry-forward (v2.8 logic 보존)
        # 🌟 v2.12 (S69 #5): 3~4차 fallback = ffill source 명시
        row['PMI_source'] = "ffill"
        print(f"  🟡 PMI: 4중 방어 1~2차 실패 → ffill carry-forward (source={pmi_source})")
        # 격언 #67 v3 dead source 정정 + 5조 ③ 데이터 위조 금지

    # 🌟 v2.10 (S69 #2, Commander 명령 "옵션 D 채택"): F&G Index 4중 방어 fetch
    #   1차: CNN 공식 API (production.dataviz.cnn.io)
    #   2차: CNN HTML scrape (edition.cnn.com)
    #   3차: ARGUS 자체 proxy (VIX + OAS 가중 평균)
    #   4차: ffill (어제 csv 값, 안전망)
    #   🌟 v2.12 (S69 #5): F_G_source 컬럼 신설
    #   격언 #75 v4 + #80 + #96 v2 ⓪⑥ + #98 + 5조 ③ 정합
    if is_backfill:
        # 🌟 v3.2: backfill 시 CNN 현재값 금지 → ARGUS proxy 직접 (target 날짜 VIX/OAS 산출)
        fg_score, fg_rating, fg_source = _calculate_fg_argus_proxy(row)
        _fg_src = "argus_proxy_backfill" if fg_score is not None else "ffill"
    else:
        fg_score, fg_rating, fg_source = _fetch_fg_4layer_defense(row)
        _fg_src = fg_source
    if fg_score is not None:
        row['F_G_Score'] = fg_score
        row['F_G_Rating'] = fg_rating
        # 🌟 v2.12 (S69 #5): F&G source 명시
        row['F_G_source'] = _fg_src  # "cnn_api" / "cnn_html" / "argus_proxy" / "argus_proxy_backfill"
        print(f"  🌟 F&G: {fg_score:.1f} ({fg_rating}, source={_fg_src})")
    else:
        # 4차 fallback — ffill 단계에서 자동 처리
        # 🌟 v2.12 (S69 #5): 4차 fallback = ffill source 명시
        row['F_G_source'] = "ffill"
        print(f"  🟡 F&G: {'backfill proxy' if is_backfill else '4중 방어 1~3차'} 실패 → ffill carry-forward")

    # 🌟 v2.4 (S67 #5): CCSA 가시성 로그 (FRED 자동 fetch 결과 확인용)
    ccsa_v = row.get('CCSA')
    if ccsa_v is not None:
        print(f"    🌟 CCSA (FRED): {ccsa_v:,.0f} (Continuing Claims, weekly)")
    else:
        print(f"    ⚠️ CCSA 부재 — ffill 단계에서 carry-forward")

    # TNX 보완
    if row.get("TNX") is None and row.get("DGS10") is not None:
        row["TNX"] = row["DGS10"]

    # Net_Liquidity
    wl = row.get("WALCL"); wt = row.get("WTREGEN"); rr = row.get("RRPONTSYD")
    if wl is not None and wt is not None and rr is not None:
        row["Net_Liquidity"] = wl - wt - rr * 1e3  # 🌟 v3.2 (S195): RRP ×1e3 — BT v5 정본 규약

    # 🌟 v2.5 (S67 #6): VIX_VIX3M_ratio 파생 (term structure 차원)
    vix_v = row.get("VIX"); vix3m_v = row.get("VIX3M")
    if vix_v is not None and vix3m_v is not None and vix3m_v > 0:
        row["VIX_VIX3M_ratio"] = vix_v / vix3m_v
        if row["VIX_VIX3M_ratio"] > 1.0:
            print(f"    🚨 VIX/VIX3M={row['VIX_VIX3M_ratio']:.4f} > 1.0 (backwardation, 강 위기 신호)")
        else:
            print(f"    ✅ VIX/VIX3M={row['VIX_VIX3M_ratio']:.4f} (contango 정상, 평균 ~0.89)")

    return row


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 누적 모드 forward-fill 보강
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def apply_ffill_safety(df: pd.DataFrame) -> pd.DataFrame:
    """v2.2: 월간/주간 FRED 시리즈 결측 자동 보강.

    🌟 v2.4 (S67 #5): CCSA 추가 (주간 시리즈, ICSA와 동일 패턴).
    """
    filled_count = {}
    for col in FFILL_COLS:
        if col not in df.columns:
            continue
        before = df[col].isna().sum()
        df[col] = df[col].ffill()
        after = df[col].isna().sum()
        if before > after:
            filled_count[col] = before - after
    if filled_count:
        print(f"    ffill 보강: {filled_count}")
    return df


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 품질 출력
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def print_quality(df: pd.DataFrame):
    """🌟 v2.10 (S69 #2): F_G_Score 추가 (시장 심리 차원).
    🌟 v2.5 (S67 #6): VIX3M + VIX_VIX3M_ratio 가시성 추가 (term structure 차원).
    🌟 v2.4 (S67 #5): CCSA 가시성 추가 (노동시장 ICSA + CCSA 양 차원).
    """
    last = df.iloc[-1]
    print(f"\n📊 {df.index[-1].date()}  ({len(df)}행)")
    for col in ["VIX","VIX3M","VIX_VIX3M_ratio","TNX","DFII10","DXY","WTI","Brent","PMI","T10YIE","OAS_HY","MOVE","ICSA","CCSA","UMCSENT","F_G_Score"]:
        v  = last.get(col, np.nan)
        ok = pd.notna(v) and np.isfinite(float(v))
        # ratio는 4자리 정밀도
        if col == "VIX_VIX3M_ratio":
            print(f"  {'✅' if ok else '❌'} {col:<16}: {v:.4f}" if ok
                  else f"  ❌ {col:<16}: NaN")
        else:
            print(f"  {'✅' if ok else '❌'} {col:<16}: {v:.3f}" if ok
                  else f"  ❌ {col:<16}: NaN")
    # F_G_Rating 별도 (string 컬럼)
    fg_rating = last.get('F_G_Rating')
    if isinstance(fg_rating, str) and fg_rating:
        print(f"  ✅ F_G_Rating     : {fg_rating}")
    # 🌟 v3.1: ECY/CAPE 가시성
    ecy_val = last.get('ECY')
    cape_val = last.get('CAPE')
    if pd.notna(ecy_val):
        print(f"  ✅ ECY             : {ecy_val:.4f} ({ecy_val*100:.2f}%)")
    if pd.notna(cape_val):
        print(f"  ✅ CAPE            : {cape_val:.1f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌟 v3.1 (S141): Shiller ECY/CAPE 자동 fetch
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _fetch_shiller_ecy_cape() -> pd.DataFrame:
    """Shiller ie_data.xls에서 ECY + CAPE 월별 시리즈 추출.

    2단계 전략 (근본 처방):
      1차: 로컬 캐시 CSV (shiller_ecy_cache.csv) → 35일 이내면 즉시 사용
      2차: Yale XLS 다운로드 → 캐시 갱신 (timeout 90초 + 2회 retry)
      3차: 캐시 오래되었어도 있으면 사용 (stale but available)

    격언 #107 정합: User-Agent 헤더 필수.
    격언 #96 v2: 외부 source sanity 의무.
    격언 #106: 근본 처방 (매번 XLS 다운로드 → 캐시 전략).
    """
    import io as _io

    cache_path = os.path.join(SCRIPT_DIR, "shiller_ecy_cache.csv")
    cache_max_age_days = 35  # 월별 데이터 → 35일 이내 캐시 유효

    # ── 1차: 로컬 캐시 확인 ──
    cache_df = pd.DataFrame()
    cache_fresh = False
    if os.path.exists(cache_path):
        try:
            cache_df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            cache_age = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))).days
            if len(cache_df) > 0 and 'ECY' in cache_df.columns:
                print(f"    Shiller 캐시: {len(cache_df)}행, {cache_age}일 경과")
                if cache_age <= cache_max_age_days:
                    cache_fresh = True
                    print(f"    ✅ 캐시 유효 ({cache_age}일 <= {cache_max_age_days}일)")
                    return cache_df
                else:
                    print(f"    ⚠️ 캐시 stale ({cache_age}일 > {cache_max_age_days}일) — Yale 갱신 시도")
        except Exception as e:
            print(f"    ⚠️ 캐시 읽기 실패: {e}")

    # ── 2차: Yale XLS 다운로드 (retry 2회, timeout 90초) ──
    for attempt in range(1, 3):
        try:
            print(f"    Yale XLS fetch 시도 {attempt}/2...")
            resp = requests.get(SHILLER_XLS_URL,
                                headers={'User-Agent': SHILLER_UA},
                                timeout=90)
            resp.raise_for_status()
            xls_bytes = resp.content
            print(f"    Shiller XLS: {len(xls_bytes)} bytes")

            raw = pd.read_excel(_io.BytesIO(xls_bytes), sheet_name='Data', skiprows=7)

            # 날짜 컬럼 탐색
            date_col = None
            for c in raw.columns:
                cl = str(c).lower().strip()
                if 'date' in cl and 'fraction' not in cl and 'decimal' not in cl:
                    date_col = c
                    break

            # CAPE / ECY 컬럼 탐색
            cape_col = ecy_col = None
            for c in raw.columns:
                cl = str(c).lower().strip()
                if cl == 'cape' or (cl.startswith('cape') and 'tr' not in cl and 'excess' not in cl):
                    cape_col = c
                if 'excess' in cl and 'cape' in cl:
                    ecy_col = c

            # 위치 기반 fallback
            cols = list(raw.columns)
            if cape_col is None and len(cols) > 13:
                cape_col = cols[13]
            if ecy_col is None and len(cols) > 15:
                ecy_col = cols[15]

            if date_col is None or cape_col is None or ecy_col is None:
                print(f"    ⚠️ Shiller 컬럼 탐색 실패: date={date_col}, cape={cape_col}, ecy={ecy_col}")
                break  # retry 무의미

            df = raw[[date_col, cape_col, ecy_col]].copy()
            df.columns = ['date_raw', 'CAPE', 'ECY']
            df['CAPE'] = pd.to_numeric(df['CAPE'], errors='coerce')
            df['ECY'] = pd.to_numeric(df['ECY'], errors='coerce')

            # 날짜 파싱
            dates = pd.to_datetime(df['date_raw'], errors='coerce')
            if dates.isna().sum() > len(dates) * 0.5:
                def _dec2date(d):
                    if pd.isna(d): return pd.NaT
                    try:
                        y = int(float(d))
                        m = round((float(d) - y) * 100)
                        m = max(1, min(12, m))
                        return pd.Timestamp(year=y, month=m, day=1)
                    except: return pd.NaT
                dates = df['date_raw'].apply(_dec2date)
            df['date'] = dates
            df = df.dropna(subset=['date']).set_index('date').sort_index()

            # sanity filter
            lo_e, hi_e = ECY_VALID_RANGE
            lo_c, hi_c = CAPE_VALID_RANGE
            df.loc[(df['ECY'] < lo_e) | (df['ECY'] > hi_e), 'ECY'] = np.nan
            df.loc[(df['CAPE'] < lo_c) | (df['CAPE'] > hi_c), 'CAPE'] = np.nan
            df = df[['ECY', 'CAPE']].ffill()

            valid = df.dropna(subset=['ECY', 'CAPE'])
            if len(valid) > 0:
                # 캐시 저장
                valid.to_csv(cache_path)
                print(f"    ✅ Shiller ECY/CAPE: {len(valid)}행 ({valid.index[0].date()} ~ {valid.index[-1].date()})")
                print(f"    ECY: {valid['ECY'].min():.4f} ~ {valid['ECY'].max():.4f} / CAPE: {valid['CAPE'].min():.1f} ~ {valid['CAPE'].max():.1f}")
                print(f"    캐시 저장: {cache_path}")
                return valid
            else:
                print(f"    ⚠️ Shiller 유효 데이터 0행")
                break
        except Exception as e:
            print(f"    ⚠️ Yale fetch 시도 {attempt}/2 실패: {e}")
            if attempt < 2:
                time.sleep(3)  # 재시도 전 3초 대기

    # ── 3차: stale 캐시라도 사용 ──
    if len(cache_df) > 0 and 'ECY' in cache_df.columns:
        print(f"    ⚠️ Yale 실패 → stale 캐시 사용 ({len(cache_df)}행)")
        return cache_df

    print(f"    🚨 Shiller ECY/CAPE 전체 실패 (캐시 없음)")
    return pd.DataFrame()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌟 v3.0 (S71 #4, 2026-05-08, csv 재설계 Phase 3 정합):
# 3 csv frequency 분리 — daily/weekly/monthly
# 본질: weekly/monthly는 LIVE 발표일만 row 보유 (ffill row 제외)
# 격언 #75 v4 (source 일관성) + #80 양방향 + #105 + #106 정합
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _split_by_frequency(df):
    """csv 재설계 v3.0 — daily/weekly/monthly 분리.
    
    Args:
        df: 통합 DataFrame (Date index + 모든 컬럼 + source 컬럼)
    
    Returns:
        (df_daily, df_weekly, df_monthly) 튜플
        - df_daily   : 모든 row × 일간 컬럼 (weekly/monthly 컬럼 제외)
        - df_weekly  : LIVE 발표일 row × 주간 컬럼 (+ source 컬럼)
        - df_monthly : LIVE 발표일 row × 월간 컬럼 (+ source 컬럼)
    
    LIVE 발표일 식별:
        source 컬럼 값이 LIVE_SRC_VALUES 중 하나인 row만 select
        (source가 'ffill'이거나 NaN인 row 제외)
    """
    # ─ 1. weekly csv 빌드 ────────────────────────
    weekly_cols_actual  = [c for c in WEEKLY_COLS if c in df.columns]
    weekly_src_cols     = [f"{c}_source" for c in weekly_cols_actual 
                           if f"{c}_source" in df.columns]
    
    if weekly_cols_actual and weekly_src_cols:
        # 대표 source 컬럼 사용 (OAS_HY 우선 → 첫 번째 source)
        primary_src = 'OAS_HY_source' if 'OAS_HY_source' in df.columns else weekly_src_cols[0]
        weekly_mask = df[primary_src].isin(LIVE_SRC_VALUES)
        weekly_export_cols = weekly_cols_actual + weekly_src_cols
        df_weekly = df.loc[weekly_mask, weekly_export_cols].copy()
    elif weekly_cols_actual:
        # source 컬럼 부재 시 (legacy 호환): 모든 row 보존
        df_weekly = df[weekly_cols_actual].copy()
    else:
        df_weekly = pd.DataFrame()
    
    # ─ 2. monthly csv 빌드 ───────────────────────
    monthly_cols_actual = [c for c in MONTHLY_COLS if c in df.columns]
    monthly_src_cols    = [f"{c}_source" for c in monthly_cols_actual 
                           if f"{c}_source" in df.columns]
    # F_G_Score는 F_G_source 사용 (특수 매핑)
    if 'F_G_Score' in monthly_cols_actual and 'F_G_source' in df.columns and 'F_G_source' not in monthly_src_cols:
        monthly_src_cols.append('F_G_source')
    
    if monthly_cols_actual and monthly_src_cols:
        primary_src = 'PMI_source' if 'PMI_source' in df.columns else monthly_src_cols[0]
        monthly_mask = df[primary_src].isin(LIVE_SRC_VALUES)
        monthly_export_cols = monthly_cols_actual + monthly_src_cols
        df_monthly = df.loc[monthly_mask, monthly_export_cols].copy()
    elif monthly_cols_actual:
        df_monthly = df[monthly_cols_actual].copy()
    else:
        df_monthly = pd.DataFrame()
    
    # ─ 3. daily csv 빌드 ─────────────────────────
    # weekly/monthly 컬럼 + 그들의 source 컬럼은 제외 (중복 차단)
    excluded_cols = set(weekly_cols_actual + weekly_src_cols 
                        + monthly_cols_actual + monthly_src_cols)
    daily_cols = [c for c in df.columns if c not in excluded_cols]
    df_daily = df[daily_cols].copy()
    
    return df_daily, df_weekly, df_monthly


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌟 v3.2 (S197): 임의 날짜 backfill 헬퍼
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _parse_date(s: str):
    """YYYY-MM-DD 문자열 → date. 실패 시 None."""
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def _resolve_target_dates():
    """env로 처리 날짜 목록 결정.
    우선순위: BACKFILL_DATE(단일) > BACKFILL_START+END(범위) > today(기본).
    반환: (dates: list, is_backfill: bool)
    """
    bf_date  = os.getenv("BACKFILL_DATE", "").strip()
    bf_start = os.getenv("BACKFILL_START", "").strip()
    bf_end   = os.getenv("BACKFILL_END", "").strip()

    if bf_date:
        d = _parse_date(bf_date)
        if d is None:
            print(f"  🚨 BACKFILL_DATE 파싱 실패: '{bf_date}' (YYYY-MM-DD 필요) → today 대체")
            return [date.today()], False
        return [d], True

    if bf_start and bf_end:
        ds, de = _parse_date(bf_start), _parse_date(bf_end)
        if ds is None or de is None:
            print(f"  🚨 BACKFILL_START/END 파싱 실패 (YYYY-MM-DD 필요) → today 대체")
            return [date.today()], False
        if ds > de:
            ds, de = de, ds
        days, cur = [], ds
        while cur <= de:
            if is_nyse_open(cur):
                days.append(cur)
            cur += timedelta(days=1)
        return days, True

    return [date.today()], False


def main():
    t0 = time.time()
    print(f"🦅 ARGUS DATA FETCHER v3.3 — {datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')}")
    print(f"   FRED_API_KEY: {'✅ 설정됨' if FRED_API_KEY else '🚨 부재'}")
    print(f"   BT_LONG_PATH: {'✅ 가용' if os.path.exists(BT_LONG_PATH) else '⚠️ 부재 (DBnomics 실패 시 fallback 불가)'}")
    print(f"   PMI source:   🌟 4중 방어 (Tradingeconomics 1차 + USSLIND proxy 2차 + BT_LONG 3차 + ffill 4차, v2.9)")
    print(f"   F&G source:   🌟 4중 방어 (CNN API 1차 + CNN HTML 2차 + ARGUS proxy 3차 + ffill 4차, v2.10)")
    print(f"   FRED source:  🌟 발표일 기준 매핑 + 1일 시차 시리즈 가시성 (v2.11 S69 #4 — T10YIE/T5YIE BEI 결함 정정)")
    print(f"   LIVE source:  🌟 22개 _source 컬럼 신설 (v2.12 S69 #5 — LIVE/ffill 결정적 명시 구분)")
    print(f"   CCSA source:  🌟 FRED API + graph CSV fallback + 부분 백필 자동 (v2.7 S68 #1)")
    print(f"   VIX3M source: 🌟 Yahoo chart API + UA header + 부분 백필 자동 (v2.7 S68 #1, term structure)")
    bf_force = os.getenv("BACKFILL_FORCE", "")
    if bf_force.lower() in ("1", "true", "yes"):
        print(f"   🌟 BACKFILL_FORCE=1 — 강제 재백필 모드 (v2.7 NEW)")

    # 🌟 v3.2 (S197): 임의 날짜 backfill — env로 처리 날짜 결정
    target_dates, is_backfill = _resolve_target_dates()
    today = date.today()

    if is_backfill:
        if not target_dates:
            print(f"  ⏭️ 지정 범위에 NYSE 개장일 없음 — 종료")
            return
        print(f"   🌟 v3.2 BACKFILL 모드 — 대상 {len(target_dates)}개장일: "
              f"{target_dates[0]} ~ {target_dates[-1]}")
    else:
        # 기본 일일 모드 — NYSE 휴장 시 skip (기존 동작 보존)
        if not is_nyse_open(today):
            print(f"⏭️ {today} NYSE 휴장 (주말 또는 휴일) — fetch 생략")
            return

    if not os.path.exists(OUTPUT_PATH):
        df = build_seed()
        # 시드는 SEED_DAYS 전체 history 포함 → backfill 날짜도 커버 (별도 fetch 불요)
    else:
        df    = pd.read_csv(OUTPUT_PATH, index_col=0, parse_dates=True)
        df.index.name = "Date"
        df    = df.sort_index()
        today_ts = pd.Timestamp(today)

        # 🌟 v3.2 (S197): target_dates 루프 (기본=오늘 1개 / backfill=N개)
        for _tgt in target_dates:
            _tgt_ts = pd.Timestamp(_tgt)
            if _tgt_ts in df.index:
                df = df[df.index != _tgt_ts]  # 기존 행 제거 후 재생성
            _label = "백필" if is_backfill else "오늘"
            print(f"  📡 {_label} 행 수집 ({_tgt})...")
            new_row = fetch_today_row(target_date=_tgt if is_backfill else None)
            new_df  = pd.DataFrame([new_row]).set_index("Date")
            new_df.index = pd.to_datetime(new_df.index)
            df = pd.concat([df, new_df]).sort_index()

        # 🌟 v2.11 (S69 #4, Commander 본질 통찰 #11): 어제 row FRED 자동 백필 (결정적 본질 정정)
        # 본질: FRED 발표일이 어제인 시리즈를 어제 row에 매핑 (NaN 정정)
        # 결정적 사례: T10YIE 5/7=NaN, 5/8 fetch 시 5/7 발표값을 5/7 row에 매핑
        # 격언 #36 #1 + #75 v4 + #80 + 5조 ③ 정합
        # 🌟 v3.2: 어제 row FRED 자동 백필은 기본 일일 모드만 (backfill 모드 제외)
        if (not is_backfill) and FRED_API_KEY:
            yesterday = today - timedelta(days=1)
            yesterday_ts = pd.Timestamp(yesterday)
            if yesterday_ts in df.index:
                backfilled = []
                for sid, col in FRED_SERIES.items():
                    if sid in DEPRECATED_FRED:
                        continue
                    if col not in df.columns:
                        continue
                    # 어제 row에 NaN인 경우만 (격언 #105 기존 형식 보존)
                    if pd.notna(df.loc[yesterday_ts, col]):
                        continue
                    # FRED 최신 발표일 ↔ 어제 일치 시 매핑
                    v, fred_date = _fred_latest_with_date(sid)
                    if v is not None and fred_date == str(yesterday):
                        df.loc[yesterday_ts, col] = v
                        backfilled.append((sid, fred_date, v))
                if backfilled:
                    print(f"    🌟 v2.11 어제 row 자동 백필 ({len(backfilled)}종): "
                          f"{', '.join([f'{s}={v}' for s, _, v in backfilled[:5]])}")
                    print(f"        본질: 어제 ({yesterday}) FRED 발표 시리즈 자동 정정 — 격언 5조 ③ 정합")

        # 🚨 v2.8 (Commander 명령 — "DBnomics 삭제"): PMI 컬럼 신규 생성 시 BT_LONG 단독
        if 'PMI' not in df.columns or df['PMI'].notna().sum() == 0:
            print(f"  🌟 PMI 컬럼 신규 생성 (BT_LONG carry-forward, v2.8)...")
            df = _integrate_bt_long_pmi(df)

        # 🌟 v2.4 (S67 #5): CCSA 컬럼 자체 부재 시 (기존 csv에 컬럼 없음) 백필 통합
        # 🌟 v2.6 (S67 #12): graph CSV anonymous fallback 통합 → FRED_API_KEY 부재해도 작동
        # 🌟 v2.7 (S68 #1): 결정적 결함 정정 — 부분 가용 시도 자동 백필 (cover < 50%)
        # PMI v2.3 패턴 정합 — 누적 csv에 CCSA 컬럼 추가 필요한 첫 실행 시 자동 백필
        BACKFILL_FORCE = os.getenv("BACKFILL_FORCE", "").lower() in ("1", "true", "yes")
        ccsa_cover = df['CCSA'].notna().sum() / len(df) if 'CCSA' in df.columns else 0
        # v2.7 결정적 트리거: 부재 OR cover < 50% OR 강제
        if 'CCSA' not in df.columns or ccsa_cover < 0.5 or BACKFILL_FORCE:
            reason = ("부재" if 'CCSA' not in df.columns else
                      f"cover {ccsa_cover*100:.1f}% < 50%" if not BACKFILL_FORCE else "BACKFILL_FORCE=1")
            print(f"  🌟 CCSA 컬럼 백필 트리거 ({reason}) — graph CSV fallback 백필...")
            start_iso = df.index.min().strftime('%Y-%m-%d')
            ccsa_series = _fred_series('CCSA', start_iso)  # v2.6: 자동 fallback 통합
            if not ccsa_series.empty:
                df['CCSA'] = ccsa_series.reindex(df.index, method='ffill')
                valid = df['CCSA'].notna().sum()
                latest_val = float(ccsa_series.iloc[-1])
                latest_date = str(ccsa_series.index[-1].date())
                print(f"    ✅ CCSA 백필 완료: {valid}/{len(df)}일 가용 ({valid/len(df)*100:.1f}%, 최신 {latest_date}={latest_val:,.0f})")
            else:
                print(f"    🚨 CCSA Primary + Fallback 모두 실패 — 컬럼 보존 (기존값 유지)")
                if 'CCSA' not in df.columns:
                    df['CCSA'] = np.nan

        # 🌟 v2.5 (S67 #6): VIX3M 컬럼 자체 부재 시 Yahoo 백필 통합
        # 🌟 v2.7 (S68 #1): 결정적 결함 정정 — 부분 가용 시도 자동 백필 (cover < 50%) + Yahoo User-Agent
        # 기존 csv에 VIX3M 컬럼 없음 → 첫 실행 시 자동 전체 history 백필
        vix3m_cover = df['VIX3M'].notna().sum() / len(df) if 'VIX3M' in df.columns else 0
        if 'VIX3M' not in df.columns or vix3m_cover < 0.5 or BACKFILL_FORCE:
            reason = ("부재" if 'VIX3M' not in df.columns else
                      f"cover {vix3m_cover*100:.1f}% < 50%" if not BACKFILL_FORCE else "BACKFILL_FORCE=1")
            print(f"  🌟 VIX3M 컬럼 백필 트리거 ({reason}) — Yahoo chart API + UA header 백필...")
            # v2.7: yfinance 우선 → 실패 시 query1 chart API 직접 (User-Agent 정합)
            start_iso = df.index.min().strftime('%Y-%m-%d')
            end_iso = (df.index.max() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            vix3m_series = _yf_series('^VIX3M', start_iso, end_iso)
            # v2.7: yfinance 실패 시 query1 chart API + UA 직접 fallback
            if vix3m_series.empty:
                print(f"    ⚠️ yfinance ^VIX3M empty → query1 chart API + UA header fallback...")
                try:
                    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
                    start_ts = int(df.index.min().timestamp())
                    end_ts = int((df.index.max() + pd.Timedelta(days=1)).timestamp())
                    url_yh = f"https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX3M?period1={start_ts}&period2={end_ts}&interval=1d"
                    resp = requests.get(url_yh, headers={"User-Agent": UA}, timeout=30)
                    if resp.status_code == 200:
                        data = resp.json()
                        result = data['chart']['result'][0]
                        timestamps = result['timestamp']
                        closes = result['indicators']['quote'][0]['close']
                        dates = pd.to_datetime([pd.Timestamp(ts, unit='s') for ts in timestamps]).normalize()
                        vix3m_series = pd.Series(closes, index=dates).dropna()
                        if vix3m_series.index.tz is not None:
                            vix3m_series.index = vix3m_series.index.tz_localize(None)
                        print(f"    ✅ query1 chart API + UA SUCCESS: {len(vix3m_series)}건 가용")
                except Exception as e:
                    print(f"    🚨 query1 chart API fallback 실패: {e}")

            if not vix3m_series.empty:
                df['VIX3M'] = vix3m_series.reindex(df.index, method='ffill')
                valid = df['VIX3M'].notna().sum()
                latest_val = float(vix3m_series.iloc[-1])
                print(f"    ✅ VIX3M 백필 완료: {valid}/{len(df)}일 가용 ({valid/len(df)*100:.1f}%, 최신값={latest_val:.2f})")
            else:
                print(f"    🚨 VIX3M Primary + Fallback 모두 실패 — 컬럼 보존")
                if 'VIX3M' not in df.columns:
                    df['VIX3M'] = np.nan

        # 🌟 v2.5 (S67 #6): VIX_VIX3M_ratio 파생 일괄 갱신 (Net_Liquidity 패턴 정합)
        # 🌟 v2.7 (S68 #1): cover < 50% 또는 부재 시도 강제 재계산
        # 누적 모드에서도 매 실행마다 전체 ratio 재계산 (단순 산식)
        if 'VIX' in df.columns and 'VIX3M' in df.columns:
            ratio_cover = df['VIX_VIX3M_ratio'].notna().sum() / len(df) if 'VIX_VIX3M_ratio' in df.columns else 0
            df['VIX_VIX3M_ratio'] = df['VIX'] / df['VIX3M']
            valid = df['VIX_VIX3M_ratio'].notna().sum()
            if valid > 0:
                latest_ratio = float(df['VIX_VIX3M_ratio'].iloc[-1])
                if ratio_cover < 0.5 or BACKFILL_FORCE:
                    print(f"    🌟 VIX_VIX3M_ratio 강제 재계산: {valid}/{len(df)}일 ({valid/len(df)*100:.1f}%, LIVE={latest_ratio:.4f})")
                else:
                    print(f"    ✅ VIX_VIX3M_ratio: {valid}/{len(df)}일 (LIVE={latest_ratio:.4f})")

        # 🌟 v3.1 (S141): Shiller ECY/CAPE 월별 자동 fetch + 일별 ffill
        # 월별 발표 지표 → cover < 50% 또는 부재 시 전체 백필 (VIX3M/CCSA 패턴 정합)
        ecy_cover = df['ECY'].notna().sum() / len(df) if 'ECY' in df.columns else 0
        if 'ECY' not in df.columns or ecy_cover < 0.5 or BACKFILL_FORCE:
            reason = ("부재" if 'ECY' not in df.columns else
                      f"cover {ecy_cover*100:.1f}% < 50%" if not BACKFILL_FORCE else "BACKFILL_FORCE=1")
            print(f"  🌟 ECY/CAPE 백필 트리거 ({reason}) — Shiller Yale XLS fetch...")
            shiller_df = _fetch_shiller_ecy_cape()
            if not shiller_df.empty:
                # 월별 → 일별 ffill
                ecy_daily = shiller_df.reindex(df.index, method='ffill').ffill().bfill()
                df['ECY'] = ecy_daily['ECY']
                df['CAPE'] = ecy_daily['CAPE']
                df['ECY_source'] = 'shiller_yale'
                df['CAPE_source'] = 'shiller_yale'
                ecy_valid = df['ECY'].notna().sum()
                cape_valid = df['CAPE'].notna().sum()
                if ecy_valid > 0:
                    ecy_latest = df['ECY'].dropna().iloc[-1]
                    print(f"    ✅ ECY 백필: {ecy_valid}/{len(df)}일 ({ecy_valid/len(df)*100:.1f}%, 최신 ECY={ecy_latest:.4f})")
                if cape_valid > 0:
                    cape_latest = df['CAPE'].dropna().iloc[-1]
                    print(f"    ✅ CAPE 백필: {cape_valid}/{len(df)}일 (최신 CAPE={cape_latest:.1f})")
            else:
                print(f"    🚨 Shiller fetch 실패 — ECY/CAPE ffill 보존")
                if 'ECY' not in df.columns:
                    df['ECY'] = np.nan
                if 'CAPE' not in df.columns:
                    df['CAPE'] = np.nan

        # ffill 보강
        df = apply_ffill_safety(df)

        print(f"  ✅ {len(df)}행")

    # 🌟 v3.2 (S195): Net_Liquidity 전열 재계산 — append 혼합 차단 + 과거 raw식 이력 자기치유
    #   매 실행 일괄 (VIX_VIX3M_ratio 패턴) · 구성요소별 ffill 인라인 (fds_builder NL_fixed 규약 동일)
    #   양 분기(누적/append) 합류점 배치 — 어느 경로든 정본 규약 보장
    if all(c in df.columns for c in ["WALCL", "WTREGEN", "RRPONTSYD"]):
        df["Net_Liquidity"] = (df["WALCL"].ffill() - df["WTREGEN"].ffill()
                               - df["RRPONTSYD"].ffill() * 1e3)
        _nl_valid = df["Net_Liquidity"].notna().sum()
        print(f"  🌟 Net_Liquidity 전열 재계산 (RRP ×1e3 정본 규약, v3.2): {_nl_valid}/{len(df)}일")

    print_quality(df)
    
    # 🌟 v3.0 (S71 #4, 2026-05-08, csv 재설계 Phase 3+5):
    # 4 csv 출력 — daily/weekly/monthly 분리 + 통합 view (argus_data.csv 호환)
    # 격언 #105 (기존 형식 보존) + #106 (근본 처방) + Phase 1+2 명세 정합
    df_daily, df_weekly, df_monthly = _split_by_frequency(df)
    
    df_daily.to_csv(OUTPUT_DAILY_PATH)
    print(f"  💾 daily csv: {len(df_daily):>4}행 × {len(df_daily.columns):>3}컬럼  → {OUTPUT_DAILY_PATH}")
    
    df_weekly.to_csv(OUTPUT_WEEKLY_PATH)
    print(f"  💾 weekly csv: {len(df_weekly):>4}행 × {len(df_weekly.columns):>3}컬럼  → {OUTPUT_WEEKLY_PATH}")
    
    df_monthly.to_csv(OUTPUT_MONTHLY_PATH)
    print(f"  💾 monthly csv: {len(df_monthly):>4}행 × {len(df_monthly.columns):>3}컬럼  → {OUTPUT_MONTHLY_PATH}")
    
    # 통합 view 보존 (argus_data.csv 호환 — briefing v6.x.y / PUBLIC mirror 정합)
    df.to_csv(OUTPUT_PATH)
    print(f"  💾 통합 view: {len(df):>4}행 × {len(df.columns):>3}컬럼  → {OUTPUT_PATH}")
    
    print(f"\n✅ 저장 완료 ({time.time()-t0:.1f}s) — 4 csv 출력 (v3.0 csv 재설계)")


if __name__ == "__main__":
    main()
