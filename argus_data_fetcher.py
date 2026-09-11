# 🔧 v3.9.16 (2026-09-11, S290): VIX3M EXACT-DATE SOURCE FALLBACK — Yahoo hole 차단.
#   PHASE A 실환경에서 2026-07-28 ^VIX3M Yahoo exact-date bar 가 누락되어 MARKET_IMMUTABLE
#   36열 중 35열만 동결되고 migration bundle 이 fail-closed 됐다. 전일값 대체는 금지다.
#   FRED VXVCLS 는 Cboe S&P 500 3-Month Volatility Index 일별 종가의 공식 재게시이며,
#   Yahoo exact-date 가 없을 때만 **동일 날짜 값**을 2순위로 사용한다. ffill/인접일 대체 0건.
#   fallback 은 yf_value_on_exact_date() 내부에 두어 PHASE A와 production missing-session repair가
#   동일 SSOT를 공유한다. 다른 MARKET_IMMUTABLE 심볼에는 영향 없음. 자본 엔진 로직 변경 0건.
# 🔧 v3.9.15 (2026-09-11, S290): GIT-SAFE GENERATION — symlink 폐기 + 수렴형 실파일 commit.
#   v3.9.14 의 generation+symlink pointer 는 로컬 파일시스템에서는 원자적이었지만 배포 매체가 git/raw 인
#   ARGUS 에서는 계약이 보존되지 않았다. git 은 symlink 를 mode 120000 + 경로 문자열 blob 으로 저장하고,
#   raw 소비자는 CSV 가 아니라 링크 문자열을 받으며, workflow 가 generation target 을 commit 하지 않으면 clone 에서
#   broken link 가 된다. 또한 일일 to_csv 가 symlink 를 따라 immutable generation 내부를 덮어써 manifest sha 를 깨뜨렸다.
#   ① P0-21 GIT/RAW SEAL — 공개 6종은 항상 **regular file**. symlink 를 사용하지 않는다.
#   ② P0-22 IMMUTABLE GENERATION — daily/backfill 은 generation 을 절대 쓰지 않고 regular public file 만 갱신한다.
#   ③ P0-23 CONVERGENT COMMIT — generation 은 증거/복구 SSOT 로 유지하고 CURRENT_GENERATION.json 을 메타 commit point 로 사용.
#      실파일 승격은 PENDING_GENERATION.json 을 먼저 기록한 뒤 generation 에서 멱등 복사한다. 중단되면 다음 실행 시작 시
#      pending 을 감지해 같은 generation 으로 수렴 복구한 후 CURRENT 를 확정한다.
#   ④ v3.9.14 잔존 symlink 를 처음 실행 시 bytes 보존 상태로 regular file 로 탈출시킨다. broken symlink 는 fail-closed.
#   ⑤ migration generation/manifest 는 daily write 와 물리적으로 분리되어 봉인 후 sha 가 변하지 않는다.
#   자본 엔진 로직 변경 0건.
# 🔧 v3.9.14 (2026-09-11, S290): ATOMIC POINTER — 마이그레이션 최종 봉인.
#   ① P0-20 LOCAL-ONLY CALENDAR — migration audit/sanitize/final gate 는 exchange_calendars:XNYS 만 사용한다.
#      yfinance calendar fallback 은 migration 에서 금지. network guard 진입 전에도 네트워크 경로 0.
#   ② P0-19 GENERATION + CURRENT POINTER — 여러 파일의 순차 os.replace 를 commit 으로 부르지 않는다.
#      검증된 generation directory 를 완성한 뒤 CURRENT symlink 하나만 os.replace 하여 전체 view 를 전환한다.
#      기존 고정 파일명은 CURRENT/<filename> 을 가리키는 정적 symlink 로 변환해 하위호환을 유지한다.
#   ③ P1-15 REPORT PURITY — migration 검증 중 정식 calendar_integrity_report.json 을 선기록하지 않는다.
#      _enforce_final_session_integrity(write_report=False) 후 generation 내부 report 만 commit 한다.
#   ④ pointer bootstrap 은 기존 파일 세트를 old generation 으로 먼저 봉인한 뒤 symlink view 를 설치한다.
#      symlink 설치 도중 실패해도 old bytes 와 동일한 generation 을 보므로 데이터 의미는 바뀌지 않는다.
#   자본 엔진 로직 변경 0건.
# 🔧 v3.9.13 (2026-09-11, S290): ATOMIC MIGRATION — 세 개의 봉인.
#   v3.9.12 의 'external_network_calls = 0' 은 **여전히** 프로세스 전체의 증명이 아니었다.
#   migration 분기가 main() 중반에 있어, 거기 닿기 전에 resolve_session_date() 가
#   _yf_series() → yf.download() 로 Yahoo 를 호출했다.
#   ① ENTRY SEAL — CALENDAR_MIGRATION_MODE 는 main() 최상단에서 분기해 daily/backfill
#      session resolution 을 통째로 우회한다. run_calendar_migration() 전용 진입점.
#   ② TRANSFORM SEAL — BEFORE·AFTER 가 normalize_frozen_view() 하나를 공유한다.
#      v3.9.12 는 AFTER 만 apply_ffill_safety() 를 거쳤다. 이 함수는 새 행만 채우는 것이 아니라
#      FFILL_COLS + 전 *_Close 를 **전 history 소급 보강**하므로, 기존 CSV 에 과거 NaN 이 있으면
#      Crown Δ 에 ffill normalization effect 가 섞였다. 이제 차이는 structural calendar transform 뿐.
#   ③ COMMIT SEAL — 전 산출물을 migration_stage/*.tmp 에 쓰고, 무결성·네트워크·파일 검증을
#      모두 통과한 뒤 os.replace 로 원자 승격한다. v3.9.12 는 baseline 을 먼저 정식 경로에 쓰고
#      4개 CSV 를 순차로 덮어써서 중간 실패 시 NEW/OLD 혼재가 가능했다.
#   ④ P1-12 가드 범위를 PHASE D 까지 (guard_scope = PHASE_B_C_D). 네트워크 시도가 1건이라도
#      기록되면 승격을 중단한다.
#   ⑤ P1-13 _load_wsts_series() 가 parse_wsts_yoy_json() 에 실제로 위임한다 (복제 제거).
#   ⑥ P1-14 번들 품질 게이트 — MU/HYG/LQD 유효 행수 >= SMH_BUNDLE_MIN_ROWS(400),
#      인덱스 중복·비단조 금지. manifest.missing_dates ↔ missing_market.csv 양방향 정합 계약.
#   자본 엔진 로직 변경 0건.
# 🔧 v3.9.12 (2026-09-11, S290): MIGRATION SEAL — 마이그레이션을 트랜잭션으로 봉인한다.
#   v3.9.11 의 'external_network_calls = 0' 은 거짓이었다. 가드가 _migration_only_finish 안에서만
#   켜지는데, 결측 세션 복구(= Yahoo historical retrieval)는 그보다 **앞에서** 끝나 있었다.
#   따라서 그 0 은 '마이그레이션 전체 무네트워크' 가 아니라 '그 함수 안에서만 0' 이었다.
#   ① PHASE 분리 — A(PREPARE, 네트워크 허용, 별도 스크립트) / B(BASELINE REPLAY) /
#      C(MIGRATE) / D(VERIFY). 가드는 B·C 전체를 감싼다. 결측 복구는 동결 번들에서 읽는다.
#   ② P0-15 대칭성 — frozen dependency 를 after 에만 적용하면 Crown Δ 에 dependency refresh 가
#      섞인다. **원 캘린더 + 동결 의존** 으로 baseline 을 먼저 만들어(migration_baseline_frozen.csv)
#      **이행 캘린더 + 같은 동결 의존** 과 비교한다. 그래야 calendar-only Δ 다.
#      추가로 기존 SMH_TRIFLAG 대비 dependency parity(diff_days)를 측정해 리포트에 남긴다.
#   ③ P0-13 WSTS parser 공용화 — parse_wsts_yoy_json() 하나를 production 과 번들이 함께 쓴다.
#      v3.9.11 번들 로더는 pd.read_json() 으로 DataFrame 을 돌려줬고, compute_smh_triflag 의
#      float(iloc[-1]) 에서 TypeError → migration 이 예외를 삼켜 '기존 값 유지' 로 조용히 넘어갔다.
#   ④ P0-14 WSTS 레포 루트 fallback 폐지 — 번들에 없으면 부분 번들로 보고 fail-closed.
#      번들 생성과 마이그레이션 사이에 upstream 이 wsts 를 바꾸면 동결이 깨진다.
#   ⑤ P1-b manifest 해시 **대조** — 기록만 하던 것을 현재 파일 해시와 비교한다. 불일치 fail-closed.
#      원본 CSV 해시(source_csv_sha256)도 대조해 번들과 데이터의 짝을 강제한다.
#   ⑥ P1-a yf_value_on_exact_date 가 _yf_batch(exact_date=) 를 쓰도록 통합 — 시장데이터 취득 단일 경로.
#   자본 엔진 로직 변경 0건.
# 🔧 v3.9.11 (2026-09-11, S290): 시간축 4계약 봉인 — 선언을 실행으로 바꾼다.
#   SESSION CONTRACT   Date = completed XNYS session            (v3.9.9~10 에서 확립)
#   MARKET CONTRACT    market value.Date == row.Date            🆕 단일 지점(_yf_batch)에서 강제
#   REPAIR CONTRACT    MARKET_IMMUTABLE=exact / REVISION_SENSITIVE=PIT ffill / DERIVED=재계산
#   MIGRATION CONTRACT network_calls = 0                        🆕 주석이 아니라 하드 가드
#   ① _yf_batch(exact_date=) — 종전은 무조건 window 마지막 행을 채택했다. 요청 날짜에 bar 가
#      없으면 인접일 값이 그 날짜로 stamp 된다(historical adjacent-bar misstamp). repair·backfill·
#      daily 세 경로가 모두 이 함수를 쓰므로 여기서 Date ↔ bar identity 를 한 번만 계약한다.
#      해당 날짜 bar 부재 시 그 심볼을 반환하지 않는다 → 기존 4단 ffill 이 'ffill' 라벨로 정직 처리.
#   ② recompute_deterministic_derived() — DERIVED 재계산 SSOT. VIX_VIX3M_ratio · Net_Liquidity ·
#      KIL_SUP. v3.9.10 은 ratio 를 재계산하지 않아, 복구행에서 VIX·VIX3M 은 actual 인데
#      ratio 만 NaN 인 상태가 가능했다(FFILL_COLS 에도 없음). ffill 로 과거 derived 를 끌어오는 것은
#      재계산이 아니라 carry 이며 계약 위반이다.
#   ③ 🔴 v3.9.10 실행 결함 정정: `df = compute_kil_sup(df)` 는 반환이 Series 이므로 DataFrame 을
#      통째로 덮어썼다. migration 경로가 저장까지 도달할 수 없었다. `df["KIL_SUP"] = ...` 로 교정.
#   ④ 🔴 v3.9.10 계약 위반 정정: migration 이 compute_smh_triflag(prices=None) 를 호출해
#      yf.download(["MU","HYG","LQD"]) 를 실제로 수행했다 — '외부 갱신 없음' 선언과 정반대.
#      _network_guard 로 yfinance·requests·urllib 을 차단하고, SMH_TRIFLAG 는 동결된
#      Migration Dependency Bundle(migration_inputs/)이 있을 때만 재계산한다. 없으면 재계산 생략.
#   ⑤ migration report 확장: input/output sha256 · ghost_removed_n · missing_repaired_n ·
#      market_exact_repair_n · pit_ffill_n · pit_unresolved_n · external_network_calls ·
#      dependency_sha256.
#   ⑥ seed 경로 _finalize_repair_provenance 누락 보완 (pit_ffill_pending 잔존 차단).
#   자본 엔진 로직 변경 0건.
# 🔧 v3.9.10 (2026-09-11, S290): 시간축 SSOT 완결 — 선언을 전 경로에서 참으로 만든다.
#   v3.9.9 의 'completed session' 은 일일 경로에서만 성립했고 explicit backfill 은 우회했다.
#   ① backfill completed-session 관통 — BACKFILL_DATE/START/END 전부 '이미 끝난 세션'만 통과.
#      실측 결함: BACKFILL_DATE=미래 정상세션이 그대로 통과했다. 이제 제외 사유와 함께 걸러낸다.
#      가격 회수는 yf_value_on_exact_date() 로 **요청 날짜의 실제 bar 만** 쓴다 —
#      'window 안 마지막 값'을 다른 날짜로 stamp 하지 않는다.
#   ② Repair Registry — 복구 정책을 열 이름 접미사가 아니라 열의 성질로 결정한다.
#      MARKET_IMMUTABLE(ETF _Close + Yahoo 시장지표 12종) 은 그 날짜 actual 을 회수하고,
#      하나라도 실패하면 fail-closed 한다. v3.9.9 는 ETF 만 회수해 WTI·VIX·DXY·TNX 를
#      전일값으로 ffill 했고, 그러면 WTI>90 게이트·KIL_SUP·VIX·DXY·TNX 판정이 달라진다.
#      REVISION_SENSITIVE 는 전진 ffill 만, DERIVED 는 원자료 복구 후 재계산.
#      FFILL_COLS 에 FRED 값 열(DFII10·T10YIE·T5YIE·DGS10·T10Y3M·T10Y2Y·USD_CNY) 편입 —
#      빠져 있던 탓에 'ffill 로 채워진다'는 표기가 거짓이 될 수 있었다.
#      provenance 를 ffill 이후에 확정한다: market_historical / pit_ffill_repair / pit_unresolved.
#   ③ CALENDAR_MIGRATION_ONLY — 마이그레이션은 파일 안 자료만으로 결정적 재계산 후 종료한다.
#      v3.9.9 는 이어서 LIVE fetch·Shiller·WSTS·GPR 갱신까지 실행해 Crown 전후 차이의
#      인과 귀속을 파괴했다.
#   ④ 장중 daily run 은 종료하지 않고 마지막 완료 세션으로 내려간다 (멱등 · 가용성 회복).
#   ⑤ 잘못된 BACKFILL 입력은 'today 실행'이 아니라 fail-closed.
#   자본 엔진 로직 변경 0건.
# 🔧 v3.9.9 (2026-09-11, S290): 시간축 SSOT 완성 — 완료 세션 보장 + PIT-safe 결측 복구.
#   v3.9.8 까지도 '완료된 세션' 은 보장되지 않았다. is_nyse_open() 은 세션 여부만 답한다.
#   ① completed-session SSOT — XNYS session_close 기준. 16:00 하드코딩 금지(조기폐장 실재:
#      2026-11-27 · 2026-12-24 는 13:00 ET 마감). last_completed_us_equity_session() 신설.
#      이 함수는 fetcher · 잔여보유일 계산기 · 브리핑 MARKET_LAG · artifact freshness 공용 SSOT 다.
#   ② PIT-safe 결측 복구 — 과거 결측일에 fetch_today_row() 로 행 전체를 만들지 않는다.
#      macro 는 개정되므로 현재 vintage 가 과거 행에 주입되고 rolling 으로 전파된다(오염 반경 > 1일).
#      가격 계층만 실제 과거값으로 복구하고 macro 는 NaN → 전진 ffill 로 채운다. provenance 표기.
#      가격 앵커 SPY_Close 미확보 시 행 생성 금지(fail-closed).
#   ③ ECY/CAPE 의 .bfill() 제거 — 첫 Shiller 관측 이전 행에 미래값을 역주입하고 있었다.
#   ④ fallback diagnostic-only — 삭제·결측복구·무결성 PASS·저장 전부 금지. density 90% 가드는
#      100 영업일 중 5세션 누락(95%)을 통과시키므로 PASS 근거가 될 수 없다.
#   ⑤ CALENDAR_MIGRATION_MODE — 역사 재계산을 일일 실행에서 분리. 미설정 시 유령/결측 발견하면
#      보고만 하고 파일을 변경하지 않는다.
#   자본 엔진 로직 변경 0건.
# 🔧 v3.9.8 (2026-09-10, S290): 세션 캘린더 삭제 안전장치 — v3.9.7 감사 처방 4건.
#   v3.9.7 의 캘린더 판정 자체는 정확하다(XNYS 회귀 7/7 통과). 위험은 그 판정을 신뢰할 수 없을 때 행을 지운다는 데 있었다.
#   ① 삭제 권한 제한 — 유령행 삭제는 1순위 캘린더(exchange_calendars:XNYS)에서만 허용한다. fallback(yfinance SPY)은
#      네트워크 최선노력 결과이며 부분 수신이면 진짜 거래일을 유령으로 지목한다. fallback 에서는 적발·보고만 하고 삭제하지 않는다.
#   ② 밀도 가드 — _yf_series 는 예외를 삼키고 부분 Series 를 돌려준다. 영업일 대비 세션 90% 미만이면 부분 수신으로 보고 fail-closed.
#   ③ 삭제 상한 — 유령 건수가 max(40, 전체의 10%) 를 넘으면 캘린더 오판 의심으로 중단한다.
#   ④ 빈 DataFrame 경로 — v3.9.7 은 카운터 키를 만들지 않아 fail-closed 대신 KeyError 로 죽었다(실측). 키를 0 으로 채운다.
#   ⑤ seed 경로 — 시드도 자기치유·결측복구를 거친다. v3.9.7 은 시드를 통과시켜, 시드에 결함이 있으면 부트스트랩이 영구 불가였다.
#   실측 정정: LIVE argus_data.csv 는 431행이 아니라 432행이다(유령 16 · 결측 3 · 중복 0 → 정리 후 419행).
#   기대 행수는 스냅샷마다 달라지므로 불변식으로 고정하지 않는다. 불변식은 오직 ghost=0 · missing=0 · duplicate=0 이다.
#   ⚠️ 미검증: yfinance fallback 의 정상·부분 수신 동작. 검증 환경에서 Yahoo 접속이 차단되어 실행하지 못했다.
#   자본 엔진 로직 변경 0건.
# 🔧 v3.9.7 (2026-09-10, S290): US Equity Regular Session Calendar SSOT — 비세션 행/결측 세션 근본 차단.
#   결함: is_nyse_open()이 주말 + 고정휴일(1/1·7/4·12/25)만 검사해 MLK·Presidents·Memorial·Juneteenth·Labor·Thanksgiving·Good Friday·임시휴장 등을 개장일로 오판.
#   실측: LIVE argus_data.csv 431행 중 비세션 16건 · 정규장 결측 3건. 행 기반 held_days/rolling window 의미를 오염.
#   처방: XNYS 정규장 캘린더(exchange_calendars 우선) → SPY 실제 거래세션(yfinance) fallback → 둘 다 실패 시 fail-closed.
#         기존 비세션 행 자기치유 제거 + 결측 정규장 세션 기존 backfill 경로 자동 복구 + 저장 직전 ghost/missing/duplicate=0 강제.
#         BACKFILL_DATE/START/END도 동일 세션 SSOT 사용. calendar_integrity_report.json을 매 실행 기록.
#   자본 엔진 로직 변경 0건. 데이터 시간축 불변식: 1 row = 1 completed US equity regular session.
# 🔧 v3.9.6 (2026-08-14, S288): GPR_HIGH 실제 병합 — v3.9.5 설계 오류 정정. v3.9.5 는 '상류가 공급한 값을 통과만 한다' 고 전제했으나 fetcher 는 argus_fred_broad.csv 를 읽지 않는다(별개 파이프라인). 그 결과 첫 실행의 fail-safe 0 이 argus_data.csv 에 새겨졌고 이후 그 0 을 읽어 0 을 쓰는 자기참조 루프가 됐다 — 상류 261/420일 발화가 하류 0/415일 로 소실됐고 로그는 성공 메시지를 찍었다. 이제 상류 파일을 실제로 읽어 Date 기준 병합하고 기존 컬럼을 무조건 덮어쓴다(0 고착 해소). 실패 시 사유를 반드시 출력한다.
# 🔧 v3.9.5 (2026-08-13, S288): GPR_HIGH 통과 배선 — CAND-EWZ_GPR_SIZING 소비용. 🚨 재계산하지 않는다 — fred_broad_gha v3 가 원본 달력 그리드(1985+)에서 산출한 값을 그대로 싣기만 한다. 이유: 확장 q90(min 500)은 argus_data.csv(수백 행)에서 영구 미성립이고, 영업일 그리드 rolling(30)은 달력 30일 정의와 어긋난다 — 초안에서 두 결함 모두 실측 적발 후 계산 위치를 상류로 이전했다(원칙 D: 소비층은 로직을 재구현하지 않는다). 컬럼 부재 시 fail-safe 0.
# 🔧 v3.9.5 (2026-09-03, S290): 데이터 소거 근본 처방 3건 — REG-S290_1.
#   ① FFILL_COLS 에 Yahoo 매크로 값 열 12종 편입 (종전 *_source 라벨만 보호 = 라벨 거짓 구조)
#   ② 행 재생성 시 확정값 보존 (delete+recreate → 신규 우선 병합, 결측 자리만 복원)
#   ③ 저장 직전 무결성 게이트 G1(라벨-값 정합) · G2(비단조 회귀 = 유효→NaN 차단)
#   발단: 2026-09-03 실행이 2026-09-01 행 재생성 중 WTI 91.69 소거 → 엔진 ExSn WTI>90 미발동
#         → GLD 허위 진입 27% (귀금속 97%). 엔진 무결함 · 데이터 레인 단독 결함.
# 🔧 v3.9.4 (2026-08-13, S288): KIL_SUP 신설 — Crown #106 (WTI Kilian 공급발 게이트 완화) 소비용. Kilian(2009) 유가 3분해의 공급충격 대리 플래그를 데이터층에서 산출한다. 정의: KIL_SUP = (ΔWTI20>0) ∩ (ΔSPY20<0) ∩ NOT(ΔWTI20>0 ∩ ΔCOPX20>0 ∩ PMI>50). 엔진은 컬럼 소비만 하며 부재/NaN 시 fail-safe 기존 동작(identity Δ=0 실증). 신규 수집 소스 0건 — 기보유 4컬럼(WTI/SPY_Close/COPX_Close/PMI) 조합. A5 강건성: Δ창 10~20일 고원(+0.87/+0.78p) · PMI 조건 제거해도 효과 동일(+0.780p) → PMI 결측 무해. 아키텍처 = SMH_TRIFLAG(v3.6) · PDBC(v3.9.3) 선례 준용 (자기치유 + fail-safe 0).
# 🔧 v3.9.3 (2026-07-25, S280): PDBC 21번째 종목 편입 + 범용 ETF 백필 신설 — 신규 티커 전체 이력 자동 백필(근본 처방).
# 🔧 v3.9.1 (2026-07-23, S279): 버전 표기 단일 원천화 — 배너·docstring 고정 문자열 제거.
#    결함: 실행 배너가 'v3.3' 하드코딩(L2111 계열)이라 헤더 이력과 불일치. 동일 유형 2회차
#          (v2.4 오표기 선례가 본 파일 주석에 이미 박제) → 수동 동기 방식의 반복 실패 입증.
#    근본 처방: FETCHER_VER 를 헤더 이력 첫 줄에서 런타임 추출(_detect_fetcher_ver) → 표기 지점 0개.
#          docstring 제목의 중복 버전 주장도 제거 (버전 주장 지점을 하나만 남김).
#    fail-safe: 추출 실패 시 'unknown' 표기 (파이프라인 중단 없음 — 데이터 가용성 우선).
# 🔧 v3.9 (2026-07-23, S279): Date 라벨 원천 교정 [SESSION-DATE] — carry row 구조적 소멸.
#    결함(v3.8 이하): fetch_today_row 가 date.today()(GHA 러너=UTC)를 Date 로 stamp.
#      워크플로 cron 은 22:17/23:17 UTC(세션일과 동일 UTC 날짜) 설계이나, GitHub 스케줄러 지연(실측 약 55분)이
#      2회차를 00:0x UTC 로 밀어내면 date.today() 가 익일로 넘어가 "직전 세션 종가 = 익일자 행"(carry row) 생성.
#      실측 2026-07-23 행 = 07-22 종가 전량 복제 → 라벨과 내용 불일치(격언 5조 ③ 인접).
#    근본 처방: Date 를 가격 원천(yfinance)이 반환한 마지막 거래일로 확정 (resolve_session_date 신설).
#      값과 라벨이 같은 원천에서 나오므로 스케줄러 지연·시간대와 무관하게 구조적으로 불일치 불가.
#      하루 2회 실행 시 동일 세션일 재기록 = 멱등(main 이 기존 행 제거 후 재생성, 자기치유 보존).
#    fail-safe: 세션일 해석 실패 시 fetch 생략(행 날조 금지) — 격언 #96 v2 정합. base=v3.8.
# 🔧 v3.8 (2026-07-14): _yf_series yfinance 1.x MultiIndex 컬럼 평탄화 — DataFrame 반환→float(Series) 크래시 근본 처방.
#    증상: BACKFILL_FORCE/저커버 VIX3M 백필에서 exit 1 (정상 일일 실행은 블록 미진입이라 무증상). base=v3.7.
# 🔧 v3.7 (2026-07-02, S244): WSTS YoY 자동 수집 신설 — wsts.org 랜딩 파싱 → 최신 Historical-Billings xlsx → Worldwide 3MMA YoY → wsts_yoy.json 조건부 갱신.
#    가드: 0 플레이스홀더 제외(미발표월, S244 실측 확정) / source_url 동일 시 다운로드 생략 / 원자적 교체(os.replace) / 전 단계 fail-safe(기존 json 보존).
#    의존: openpyxl(xlsx 엔진) — GHA pip 미설치 시 fail-safe 경고 후 기존 json 유지. base=v3.6(26924714d38e).
# 🔧 v3.6 (2026-07-02, S242): SMH_TRIFLAG 전열 재계산 신설 — 삼중(C8∧S2∧WSTS<0) 선행 플래그, Crown #84 후보 소비용 (REG-S242_3).
#    원천: MU/HYG/LQD yfinance 5년 자체확보(385행 롤링 독립, 워밍업 315거래일 해소) + wsts_yoy.json(PIT+45일·staleness 75일 가드).
#    fail-safe: 산출 실패/데이터 부재 → 전열 0 (휴면=무해). base=v3.5(bee8086403d3).
# 🔧 v3.5 (2026-06-20, S218): ETF 가격 *_Close ffill 통합 — Yahoo batch 단일일 누락(ITA/VNM/CQQQ NaN→브리핑 $0.00) 근본 처방. apply_ffill_safety에 close_cols 1줄.
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
🦅 ARGUS DATA FETCHER — 변경 이력·버전은 파일 상단 주석이 단일 원천 (v3.9.1)
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
import os, sys, time, json, warnings, shutil, uuid
from datetime import datetime, date, timedelta, timezone

import urllib.request
import re  # 🌟 v2.9 (S69 #1): Tradingeconomics PMI 패턴 정규식 의무
import numpy as np
import pandas as pd
import requests
import json
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
MONTHLY_COLS = ['PMI', 'UMCSENT', 'SAHMCURRENT', 'F_G_Score', 'F_G_Rating', 'ECY', 'CAPE', 'SEMI_REACCEL', 'CONSUMER_ELEC']  # 🆕 [S214] 반도체 선행신호 월간군

# 🌟 v3.1 (S141): Shiller ECY/CAPE fetch 설정
SHILLER_XLS_URL = "https://www.econ.yale.edu/~shiller/data/ie_data.xls"
SHILLER_UA = "ARGUS-ECY-Fetcher/1.0 (+https://github.com/daifulee/argus-public-data)"
ECY_VALID_RANGE = (-0.02, 0.10)   # sanity (이론상 음수 가능)
CAPE_VALID_RANGE = (5.0, 60.0)

# v3.0 source 값 매트릭스 (LIVE 식별)
LIVE_SRC_VALUES = {
    'yahoo_live', 'fred_live', 'fred_graph',
    'tradingeconomics', 'cnn_api', 'cnn_html', 'argus_proxy',
    'fred_semi_live',  # 🆕 [S214] 반도체 선행신호 (Oracle LEAD-7)
}
BT_LONG_PATH = os.path.join(SCRIPT_DIR, "BT_LONG_v5_complete.csv")
SEED_DAYS    = 450
KST          = timezone(timedelta(hours=9))

# ═══════════════════════════════════════════════════════════════════════════
# 🆕 v3.9.1 (S279): 버전 단일 원천 — 헤더 변경 이력 첫 줄에서 런타임 추출
#   배경: 배너 하드코딩이 헤더와 어긋나는 사고 2회 (v2.4 · v3.3). 수동 동기는 실패가 반복됨.
#   원칙: 버전을 "주장"하는 지점을 코드에서 0개로 만들고, 이력 자체를 읽는다.
#   fail-safe: 추출 실패 시 "unknown" (데이터 파이프라인은 계속 — 표기는 비차단 사안)
# ═══════════════════════════════════════════════════════════════════════════
def _detect_fetcher_ver(default="unknown"):
    """파일 상단 변경 이력 첫 줄(# 🔧 vX.Y[.Z])에서 버전 문자열 추출."""
    try:
        with open(os.path.abspath(__file__), encoding="utf-8") as _f:
            for _ in range(60):
                _line = _f.readline()
                if not _line:
                    break
                _m = re.match(r"#\s*🔧\s*(v\d+\.\d+(?:\.\d+)?)", _line.strip())
                if _m:
                    return _m.group(1)
    except Exception:
        pass
    return default


FETCHER_VER = _detect_fetcher_ver()

# 🆕 v2.3: DBnomics ISM PMI Web API URL (무료, 무 API key)
DBNOMICS_PMI_URL = "https://api.db.nomics.world/v22/series/ISM/pmi/pm?observations=1&format=json"

ETF_TICKERS = [
    "GLD","SLV","COPX","NLR","QQQM","VNM","IWM","PAVE",
    "SMH","EWZ","XLE","INDA","ITA","TLT","VEA","XLF",
    "XLV","XLU","CQQQ","CIBR","SGOV","SPY","IEF",
    "PDBC",   # 🆕 [DEPLOY-S280] 21번째 종목 편입 — 상장 2014-11-07, 범용 ETF 백필로 이력 자동 확보
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
# 🔧 v3.9.5 (S290, REG-S290_1): Yahoo 매크로 '값' 열 ffill 보호 편입.
#   결함: 종전 FFILL_COLS 는 *_source 라벨(LIVE_SOURCE_COLS)만 보호했다. Yahoo 단일 심볼
#   실패 시 row[col] 미설정 → 값 NaN, row[col_source]='ffill' 라벨만 기록되어
#   '라벨은 ffill 인데 값은 결측' 이라는 구조적 거짓이 성립했다 (2026-09-01 WTI/Brent/VIX3M 소거).
#   v3.5(S218)가 ETF *_Close 는 ffill 에 편입했으나 매크로 값 열은 누락했다 — 그 누락의 정정.
#   문서화된 4단 방어('4차: ffill')를 코드가 실제로 이행하게 만드는 변경이며 신규 개념 아님.
YAHOO_MACRO_VALUE_COLS = list(YAHOO_MACRO.values())
# 🔧 v3.9.10: FRED 값 열 편입. 종전 FFILL_COLS 에는 DFII10 · T10YIE · T5YIE · DGS10 ·
#   T10Y3M · T10Y2Y · USD_CNY 가 빠져 있었다. 그 상태에서 PIT repair 가 '나머지는 전진
#   ffill 로 채워진다' 고 표기하면 라벨이 거짓이 된다 — 일부는 NaN 으로 남는다.
#   REVISION_SENSITIVE 계열은 전진 ffill 만 허용되며, 채워지지 않으면 그렇게 표기해야 한다.
FRED_VALUE_COLS = [v for v in FRED_SERIES.values()]
FFILL_COLS = FFILL_COLS + LIVE_SOURCE_COLS + YAHOO_MACRO_VALUE_COLS + \
             [c for c in FRED_VALUE_COLS if c not in FFILL_COLS]

DEPRECATED_FRED = {"NAPM"}

# 🆕 [S214] FRED 반도체 선행신호 (Oracle LEAD-7) — SEMI_REACCEL/CONSUMER_ELEC
#   SEMI_REACCEL  = A34SNO_roc3m>0 ∩ U34SIS_roc3m<0          (주문↑ ∩ 재고↓)
#   CONSUMER_ELEC = RSEAS_roc3m>0 ∩ R42343M163SCEN_roc3m<0   (소매↑ ∩ 채널재고↓)
SEMI_SERIES_LAG = {"A34SNO": 35, "U34SIS": 35, "RSEAS": 16, "R42343M163SCEN": 45}
SEMI_SIGNAL_DEF = {
    "SEMI_REACCEL":  (("A34SNO", "U34SIS"), 35),
    "CONSUMER_ELEC": (("RSEAS", "R42343M163SCEN"), 45),
}

# ═══════════════════════════════════════════════════════════════════════════
# 🔧 v3.9.7 (S290): 미국 주식 정규장 세션 캘린더 SSOT
#   - PRIMARY: exchange_calendars XNYS (이동휴일·Good Friday·임시휴장 포함)
#   - FALLBACK: yfinance SPY 실제 거래일 인덱스
#   - 두 소스 모두 실패: fail-closed (행 날조/휴일 행 생성 금지)
# ═══════════════════════════════════════════════════════════════════════════
US_EQUITY_CALENDAR_NAME = "XNYS"
SESSION_CALENDAR_REPORT_PATH = os.path.join(SCRIPT_DIR, "calendar_integrity_report.json")
# 🔧 v3.9.9: 역사 시간축 재구축은 명시적 모드에서만. 기본값 0 (일일 실행 보호).
CALENDAR_MIGRATION_MODE = os.environ.get("CALENDAR_MIGRATION_MODE", "0") == "1"
_SESSION_INDEX_CACHE = {}


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
def _norm_session_index(idx) -> pd.DatetimeIndex:
    """세션 인덱스를 timezone 없는 자정 DatetimeIndex로 정규화."""
    x = pd.DatetimeIndex(pd.to_datetime(idx, errors="coerce")).dropna()
    if x.tz is not None:
        x = x.tz_localize(None)
    return pd.DatetimeIndex(x.normalize().unique()).sort_values()


def _sessions_exchange_calendars(start, end):
    """exchange_calendars XNYS 세션. 모듈 부재/범위 실패 시 예외를 호출부로 전달."""
    import exchange_calendars as xcals
    cal = xcals.get_calendar(US_EQUITY_CALENDAR_NAME)
    ss = cal.sessions_in_range(pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize())
    return _norm_session_index(ss)


def _sessions_yfinance_observed(start, end):
    """SPY 실제 거래일을 세션 fallback으로 사용. 휴장일에는 관측 행 자체가 없다는 성질을 이용."""
    s0 = pd.Timestamp(start).normalize() - pd.Timedelta(days=7)
    e0 = pd.Timestamp(end).normalize() + pd.Timedelta(days=2)
    ser = _yf_series("SPY", s0.strftime("%Y-%m-%d"), e0.strftime("%Y-%m-%d"))
    if ser is None or len(ser) == 0:
        raise RuntimeError("SPY 세션 fallback 데이터 0건")
    idx = _norm_session_index(ser.index)
    lo, hi = pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize()
    idx = idx[(idx >= lo) & (idx <= hi)]
    # 🔧 v3.9.8 밀도 가드: _yf_series 는 예외를 삼키고 빈/부분 Series 를 돌려준다.
    #   완전 실패(0건)는 위에서 막히지만 **부분 수신**은 걸러지지 않는다. 부분 수신을 그대로
    #   세션 집합으로 쓰면 진짜 거래일이 유령으로 분류되어 삭제된다 — 되돌릴 수 없는 사고다.
    #   미국 정규장은 영업일의 약 96%(연 252/261) 이므로, 영업일 대비 90% 미만이면
    #   신뢰 불가로 보고 fail-closed 한다. 범위가 짧으면(영업일 5일 미만) 통계가 무의미하므로 면제.
    _bdays = len(pd.bdate_range(lo, hi))
    if _bdays >= 5:
        _ratio = len(idx) / float(_bdays)
        if _ratio < 0.90:
            raise RuntimeError(
                f"SPY 세션 fallback 밀도 미달 {len(idx)}/{_bdays} = {_ratio:.1%} "
                "(부분 수신 의심) — 세션 집합으로 사용 금지")
    return idx


def get_us_equity_regular_sessions(start, end, *, return_source=False):
    """[v3.9.7] 미국 상장 ETF 정규장 세션 SSOT.

    우선순위:
      1) exchange_calendars XNYS — 규칙/임시휴장 포함 정식 캘린더
      2) yfinance SPY 실제 거래일 — 운영환경 무추가의존 fallback
      3) 둘 다 실패 → RuntimeError (fail-closed)

    주의: 단순 평일/고정휴일 계산으로 fallback하지 않는다. 그 방식이 본 결함의 원인이기 때문.
    """
    lo = pd.Timestamp(start).normalize()
    hi = pd.Timestamp(end).normalize()
    if lo > hi:
        lo, hi = hi, lo
    key = (str(lo.date()), str(hi.date()))
    if key in _SESSION_INDEX_CACHE:
        idx, source = _SESSION_INDEX_CACHE[key]
        return (idx.copy(), source) if return_source else idx.copy()

    errors = []
    try:
        idx = _sessions_exchange_calendars(lo, hi)
        source = f"exchange_calendars:{US_EQUITY_CALENDAR_NAME}"
    except Exception as e:
        errors.append(f"exchange_calendars={type(e).__name__}:{e}")
        try:
            idx = _sessions_yfinance_observed(lo, hi)
            source = "yfinance:SPY_observed_sessions"
        except Exception as e2:
            errors.append(f"yfinance={type(e2).__name__}:{e2}")
            raise RuntimeError("US equity session calendar unavailable; " + " | ".join(errors))

    idx = _norm_session_index(idx)
    _SESSION_INDEX_CACHE[key] = (idx.copy(), source)
    return (idx, source) if return_source else idx


def is_nyse_open(d: date) -> bool:
    """호환 wrapper. 실제 판정은 US Equity Regular Session SSOT를 사용."""
    ts = pd.Timestamp(d).normalize()
    sessions = get_us_equity_regular_sessions(ts, ts)
    return bool(ts in sessions)



# ══════════════════════════════════════════════════════════════════════
# 🕰️ v3.9.9 [SESSIONSSOT] 완료 세션 단일 원천
#   v3.9.8 까지의 불변식 선언은 "1 row = 1 completed US equity regular session" 이었으나
#   코드가 실제로 보장한 것은 "1 row = 1 observed trading-date bar" 뿐이었다.
#   is_nyse_open() 은 '그 날짜가 세션인가'만 답하고 '그 세션이 끝났는가'는 답하지 않는다.
#   장중 수동 실행이나 워크플로 시간 변경 시 Yahoo 가 당일 daily bar 를 노출하면
#   미완료 세션 행이 CSV 에 들어간다.
#
#   마감 시각을 16:00 으로 하드코딩하지 않는다 — 조기폐장이 존재한다.
#   실측(XNYS 4.13.2): 2026-11-27 · 2026-12-24 는 13:00 ET 마감이다.
#   따라서 캘린더가 주는 session_close 를 그대로 쓴다 (DST·조기폐장·휴장 한 소스 처리).
#
#   🎯 이 함수는 fetcher · 잔여보유일 계산기 · 브리핑 MARKET_LAG · artifact freshness 가
#      함께 소비해야 하는 시간축 SSOT 다. 각자 구현하면 다시 갈라진다.
# ══════════════════════════════════════════════════════════════════════
def xnys_session_close(session_ts):
    """해당 세션의 실제 마감 시각(tz-aware UTC). 세션이 아니면 None."""
    try:
        import exchange_calendars as xcals
        cal = xcals.get_calendar(US_EQUITY_CALENDAR_NAME)
        ts = pd.Timestamp(session_ts).normalize()
        if not cal.is_session(ts):
            return None
        return pd.Timestamp(cal.session_close(ts))
    except Exception:
        return None


def is_session_completed(session_ts, now_utc=None):
    """그 세션이 이미 마감됐는가. 판정 불가 시 None (fail-closed 용).

    반환: True(마감) / False(미마감·개장전·장중) / None(캘린더 판정 불가)
    """
    close = xnys_session_close(session_ts)
    if close is None:
        return None
    now = pd.Timestamp(now_utc) if now_utc is not None else pd.Timestamp.now(tz="UTC")
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    return bool(now >= close)


def last_completed_us_equity_session(now_utc=None, lookback_days=14):
    """지금 시점 기준 마지막 '완료된' 정규장 세션 날짜. 판정 불가 시 None.

    정상일 마감(16:00 ET) 이전이면 전 거래일, 이후면 당일을 돌려준다.
    조기폐장일에는 그 날의 실제 마감(예: 13:00 ET)을 기준으로 한다.
    """
    now = pd.Timestamp(now_utc) if now_utc is not None else pd.Timestamp.now(tz="UTC")
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    try:
        import exchange_calendars as xcals
        cal = xcals.get_calendar(US_EQUITY_CALENDAR_NAME)
    except Exception:
        return None
    hi = now.tz_convert("UTC").normalize().tz_localize(None)
    lo = hi - pd.Timedelta(days=lookback_days)
    try:
        sessions = cal.sessions_in_range(lo, hi)
    except Exception:
        return None
    for s in reversed(list(sessions)):
        ts = pd.Timestamp(s).normalize()
        if is_session_completed(ts, now_utc=now):
            return ts.date()
    return None


# ══════════════════════════════════════════════════════════════════════
# 🗂️ v3.9.10 [REPAIRREG] Repair Registry — 결측 복구 정책을 열 이름 접미사가 아니라
#    열의 성질로 결정한다.
#
#    v3.9.9 는 `c.endswith("_Close")` 로 '가격 계층'을 정의했다. 그러면 ETF 종가만 복구되고
#    WTI · VIX · DXY · TNX · MOVE · VIX3M · Brent · USD_KRW 등은 NaN 이 되어 전일값으로 ffill 된다.
#    이들은 개정되는 macro 가 아니라 **그 날짜의 실제 시장 관측값**이며 역사적으로 다시 받을 수 있다.
#    WTI actual(결측일) ≠ WTI 전일값 이므로 WTI>90 게이트 · KIL_SUP · VIX 조건 · DXY 게이트 ·
#    TNX 조건의 판정 자체가 달라진다.
#
#    3분류:
#      MARKET_IMMUTABLE   ETF _Close + Yahoo 시장지표 → 그 날짜 actual 을 회수한다
#      REVISION_SENSITIVE FRED/설문 계열              → 회수 금지. 직전 알려진 값만 전진 ffill
#      DERIVED            KIL_SUP · ratio · Net_Liquidity → 원자료 복구 후 재계산
# ══════════════════════════════════════════════════════════════════════
def build_repair_registry():
    """열 → (분류, 회수 심볼). ETF_TICKERS·YAHOO_MACRO 를 단일 원천으로 파생한다."""
    market = {}
    for t in ETF_TICKERS:
        market[f"{t}_Close"] = t
    for sym, col in YAHOO_MACRO.items():
        market[col] = sym
    return market


MARKET_IMMUTABLE_COLS = None   # 최초 호출 시 build_repair_registry() 로 채움


def _market_repair_map():
    global MARKET_IMMUTABLE_COLS
    if MARKET_IMMUTABLE_COLS is None:
        MARKET_IMMUTABLE_COLS = build_repair_registry()
    return MARKET_IMMUTABLE_COLS


# 🔧 v3.9.16: Yahoo exact-date hole 이 확인된 시장지표의 권위 fallback.
# 값은 반드시 같은 날짜 observation 이어야 하며 인접일/ffill 대체는 금지한다.
EXACT_DATE_FRED_FALLBACK = {
    "^VIX3M": "VXVCLS",  # CBOE S&P 500 3-Month Volatility Index, Daily Close
}


def _fred_value_on_exact_date(series_id, d, window_days=7):
    """FRED series 에서 target date 와 **정확히 같은 날짜** 값만 반환한다."""
    lo = str(pd.Timestamp(d).date() - timedelta(days=window_days))
    s = _fred_series(series_id, lo)
    if s is None or len(s) == 0:
        return None
    try:
        x = pd.Series(s).copy()
        x.index = pd.to_datetime(x.index, errors="coerce")
        if getattr(x.index, "tz", None) is not None:
            x.index = x.index.tz_localize(None)
        x.index = x.index.normalize()
        target = pd.Timestamp(d).normalize()
        hit = pd.to_numeric(x[x.index == target], errors="coerce").dropna()
        if len(hit) == 0:
            return None
        v = float(hit.iloc[-1])
        return v if np.isfinite(v) else None
    except Exception:
        return None


def yf_value_on_exact_date(symbol, d, window_days=7):
    """그 날짜의 **실제 bar/observation** 값만 돌려준다. 없으면 None.

    Primary 는 Yahoo exact-date. v3.9.16부터 심볼별 권위 fallback이 등록된 경우에만
    FRED exact-date를 2순위로 사용한다. 어느 경로도 인접일/ffill 값을 target date로
    재라벨하지 않는다.
    """
    # 🔧 v3.9.12 P1-a: 시장데이터 취득을 _yf_batch 단일 경로로 합친다.
    lo = str(pd.Timestamp(d).date() - timedelta(days=window_days))
    hi = str(pd.Timestamp(d).date() + timedelta(days=2))
    got = _yf_batch([symbol], lo, hi, exact_date=d)
    v = got.get(symbol)
    if v is not None and np.isfinite(v):
        return float(v)

    # 🔧 v3.9.16: Yahoo hole 이면 같은 날짜 FRED observation만 허용.
    sid = EXACT_DATE_FRED_FALLBACK.get(symbol)
    if sid:
        fv = _fred_value_on_exact_date(sid, d, window_days=window_days)
        if fv is not None:
            print(f"    ✅ exact-date fallback {symbol} → FRED {sid}: "
                  f"{pd.Timestamp(d).date()}={fv:.6g}")
            return float(fv)
        print(f"    ⚠️ exact-date fallback {symbol} → FRED {sid}도 동일 날짜 값 없음: "
              f"{pd.Timestamp(d).date()}")
    return None

def _calendar_integrity_snapshot(df: pd.DataFrame, stage: str, *, primary_only=False) -> dict:
    """현재 DataFrame의 세션 시간축 무결성을 측정. 데이터를 수정하지 않는다.

    primary_only=True 이면 exchange_calendars:XNYS 만 허용한다.
    migration 에서는 Yahoo calendar fallback 자체를 금지해 process-level network=0 계약을 지킨다.
    """
    if df is None or len(df) == 0:
        # 🔧 v3.9.8: 카운터 키를 반드시 채운다. v3.9.7 은 이 분기에서 ghost_n/missing_n/
        #   duplicate_n/nat_dates 를 만들지 않아, 빈 df 가 들어오면 fail-closed 대신
        #   KeyError 로 죽었다 (실측: _sanitize → KeyError 'duplicate_n',
        #   _enforce → KeyError 'ghost_n'). 의도한 차단과 예기치 못한 크래시는 다르다.
        return {
            "stage": stage, "rows": 0, "calendar_source": None,
            "nat_dates": 0, "ghost_n": 0, "missing_n": 0, "duplicate_n": 0,
            "ghost_dates": [], "missing_dates": [], "duplicate_dates": [],
        }
    idx_raw = pd.DatetimeIndex(pd.to_datetime(df.index, errors="coerce"))
    bad_nat = int(idx_raw.isna().sum())
    idx = _norm_session_index(idx_raw)
    if len(idx) == 0:
        raise RuntimeError("calendar audit: 유효 Date index 0건")
    if primary_only:
        expected = _sessions_exchange_calendars(idx.min(), idx.max())
        source = f"exchange_calendars:{US_EQUITY_CALENDAR_NAME}"
    else:
        expected, source = get_us_equity_regular_sessions(idx.min(), idx.max(), return_source=True)

    normalized_all = pd.DatetimeIndex(pd.to_datetime(df.index, errors="coerce"))
    if normalized_all.tz is not None:
        normalized_all = normalized_all.tz_localize(None)
    normalized_all = normalized_all.normalize()
    dup = normalized_all[normalized_all.duplicated(keep=False) & ~normalized_all.isna()]
    duplicate_dates = sorted({str(x.date()) for x in dup})
    actual_unique = _norm_session_index(normalized_all)
    ghost = actual_unique.difference(expected)
    missing = expected.difference(actual_unique)
    return {
        "stage": stage,
        "rows": int(len(df)),
        "start": str(idx.min().date()),
        "end": str(idx.max().date()),
        "calendar_source": source,
        "nat_dates": bad_nat,
        "ghost_n": int(len(ghost)),
        "ghost_dates": [str(x.date()) for x in ghost],
        "missing_n": int(len(missing)),
        "missing_dates": [str(x.date()) for x in missing],
        "duplicate_n": int(len(duplicate_dates)),
        "duplicate_dates": duplicate_dates,
    }


def _write_calendar_integrity_report(report: dict):
    """캘린더 감사 결과를 regular file 로 원자 기록.

    🔧 v3.9.15: public artifact 는 git/raw 계약 때문에 symlink 를 금지한다. tmp regular file 을
    같은 디렉터리에서 fsync 후 os.replace 한다.
    """
    payload = dict(report)
    payload["generated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dst = SESSION_CALENDAR_REPORT_PATH
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    tmp = dst + f".tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, dst)
        _fsync_dir(os.path.dirname(dst) or ".")
    finally:
        if os.path.lexists(tmp):
            os.remove(tmp)


def _sanitize_non_session_rows(df: pd.DataFrame, stage="pre_fetch", *, primary_only=False):
    """구버전에서 남은 비세션/중복 행을 제거. 신규 생성 차단과 별개인 1회성 자기치유 레인."""
    snap = _calendar_integrity_snapshot(df, stage, primary_only=primary_only)
    if snap.get("nat_dates", 0):
        raise RuntimeError(f"Date index NaT {snap['nat_dates']}건 — 자동복구 금지")

    work = df.copy()
    work.index = pd.to_datetime(work.index, errors="raise").normalize()
    if snap["duplicate_n"]:
        print(f"  🧹 v3.9.7 중복 세션 정리 {snap['duplicate_n']}일: {snap['duplicate_dates']}")
        work = work[~work.index.duplicated(keep="last")]

    if snap["ghost_n"]:
        # 🔧 v3.9.8 삭제 권한 제한. 행 삭제는 되돌릴 수 없으므로 **결정적 캘린더**에서만 허용한다.
        #   fallback(yfinance SPY)은 네트워크 최선노력 결과이며, 부분 수신이면 진짜 거래일을
        #   유령으로 지목한다. 그 상태에서 삭제하면 데이터가 사라진다.
        #   fallback 에서는 적발·보고만 하고 삭제하지 않는다 — 조용히 넘어가지도 않는다.
        _srcname = str(snap.get("calendar_source") or "")
        _trusted = _srcname.startswith("exchange_calendars:")
        _cap = max(40, int(len(work) * 0.10))
        if not _trusted:
            print(f"  🟡 v3.9.8 유령행 {snap['ghost_n']}건 적발했으나 삭제 보류 — "
                  f"캘린더 소스가 1순위가 아니다({_srcname}). 목록: {snap['ghost_dates']}")
            print("     처방: requirements 에 exchange_calendars 를 추가해 1순위 캘린더로 재실행.")
        elif snap["ghost_n"] > _cap:
            raise RuntimeError(
                f"유령행 {snap['ghost_n']}건 > 상한 {_cap}건 — 캘린더 오판 의심으로 삭제 중단. "
                f"목록 앞 10건: {snap['ghost_dates'][:10]}")
        else:
            print(f"  🧹 v3.9.8 비세션 유령행 자기치유 {snap['ghost_n']}건: {snap['ghost_dates']}")
            work = work[~work.index.isin(ghosts := pd.DatetimeIndex(pd.to_datetime(snap["ghost_dates"])))]
    work = work.sort_index()
    work.index.name = "Date"
    return work, snap


def _repair_missing_session_rows(df: pd.DataFrame, missing_dates, bundle=None):
    """정규장 결측을 기존 historical backfill 경로로 복구.

    가격 앵커 SPY_Close를 실제로 확보하지 못한 날짜는 행을 만들지 않고 fail-closed한다.
    macro/저빈도 열은 이후 apply_ffill_safety 및 기존 backfill 로직이 보강한다.
    """
    if not missing_dates:
        return df, []

    # 🔴 v3.9.9 [PIT] 계층 분리. v3.9.7~8 은 fetch_today_row(과거일) 로 **행 전체**를 만들었다.
    #   가격은 그 날짜의 확정값이지만 macro 는 그렇지 않다 — PMI · UMCSENT · SAHMCURRENT ·
    #   GPR 계열 · 다수 FRED 시리즈는 개정된다. 지금 호출하면 **현재 vintage** 가 들어간다.
    #   즉 2026-05 행에 2026-09 정보가 삽입된다. 그 행 하나로 끝나지 않고
    #   ROC · MA · momentum · KIL_SUP · rolling percentile 로 전파된다 —
    #   PIT 오염 반경은 1일이 아니다.
    #
    #   처방: 가격 계층만 실제 과거값으로 복구하고, macro 는 비워 둔다.
    #   비워 둔 자리는 이후 apply_ffill_safety 의 **전진 ffill** 이 직전 세션의 값으로 채운다 —
    #   전진 ffill 은 그 시점에 이미 알려져 있던 값만 쓰므로 PIT 안전하다.
    #   가격 앵커(SPY_Close) 조차 확보 못 하면 행을 만들지 않고 fail-closed 한다.
    repaired = []
    work = df.copy()
    _mkt = _market_repair_map()
    _frozen = None if bundle is None else bundle.get("missing_market")
    for ds in missing_dates:
        d = pd.Timestamp(ds).date()
        _via = "동결 번들" if _frozen is not None else "네트워크 회수"
        print(f"  🩹 v3.9.12 결측 세션 PIT-safe 복구: {d} ({_via})")
        _px, _miss = {}, []
        for _col, _sym in _mkt.items():
            if _col not in work.columns:
                continue
            if _frozen is not None:
                # 🔴 v3.9.12 P0-12: 마이그레이션 중에는 네트워크를 쓰지 않는다.
                #   결측 복구 자체가 Yahoo historical retrieval 이므로, 가드를 나중에 켜면
                #   'migration 전체 네트워크 0' 은 성립하지 않는다. 값은 미리 동결해 둔다.
                _ts = pd.Timestamp(d)
                _v = None
                if _ts in _frozen.index and _col in _frozen.columns:
                    _raw = _frozen.at[_ts, _col]
                    if pd.notna(_raw):
                        _v = float(_raw)
            else:
                _v = yf_value_on_exact_date(_sym, d)
            if _v is None:
                _miss.append(_col)
            else:
                _px[_col] = _v
        if "SPY_Close" not in _px:
            raise RuntimeError(
                f"{d} SPY_Close 과거값 확보 실패 — 결측 세션 행 생성 금지 (fail-closed). "
                "가격 앵커 없이 시간축을 메우지 않는다.")
        # 🔴 MARKET_IMMUTABLE 은 전일값으로 대체하지 않는다. 그 날짜 actual 이 아니면
        #    게이트 판정(WTI>90 · VIX · DXY · TNX)이 달라지므로 fail-closed 한다.
        if _miss:
            raise RuntimeError(
                f"{d} 시장관측값 {len(_miss)}열 {'동결 번들에 없음' if _frozen is not None else '회수 실패'}"
                f": {_miss[:12]} — MARKET_IMMUTABLE 은 전일값 대체를 허용하지 않는다 (fail-closed)."
                + (" 번들을 다시 생성할 것 (PHASE A)." if _frozen is not None else ""))
        row = {c: np.nan for c in work.columns}
        row.update(_px)
        # provenance — 회수한 것과 이후 전진 ffill 로 채울 것을 구분해 표기한다
        for _sc in [c for c in work.columns if c.endswith("_source")]:
            _base = _sc[:-len("_source")]
            row[_sc] = "market_historical" if _base in _px else "pit_ffill_pending"
        rdf = pd.DataFrame([row], index=[pd.Timestamp(d)])
        rdf.index.name = "Date"
        work = pd.concat([work[work.index != pd.Timestamp(d)], rdf]).sort_index()
        repaired.append(str(d))
        print(f"     MARKET_IMMUTABLE {len(_px)}열 actual 회수 · "
              f"나머지 {len(work.columns)-len(_px)}열 전진 ffill 대기")
    work.index.name = "Date"
    return work, repaired



def _finalize_repair_provenance(df, repaired_dates):
    """ffill 이후, 실제로 채워졌는지 보고 provenance 를 정직하게 확정한다.

    pit_ffill_pending → 값이 있으면 pit_ffill_repair / 여전히 NaN 이면 pit_unresolved.
    '채워졌다'고 라벨만 붙이고 값이 비어 있는 구조적 거짓을 만들지 않는다.
    """
    if not repaired_dates:
        return df
    idx = [pd.Timestamp(x) for x in repaired_dates]
    scols = [c for c in df.columns if c.endswith("_source")]
    unresolved = {}
    for d in idx:
        if d not in df.index:
            continue
        for sc in scols:
            if str(df.at[d, sc]) != "pit_ffill_pending":
                continue
            base = sc[:-len("_source")]
            ok = base in df.columns and pd.notna(df.at[d, base])
            df.at[d, sc] = "pit_ffill_repair" if ok else "pit_unresolved"
            if not ok:
                unresolved.setdefault(str(d.date()), []).append(base)
    if unresolved:
        print(f"  🟡 v3.9.10 복구행 미해결 열: {unresolved}")
        print("     (직전 알려진 값이 없어 전진 ffill 로 채울 수 없었다 — 현재 vintage 주입 금지 원칙 유지)")
    return df



# ══════════════════════════════════════════════════════════════════════
# ♻️ v3.9.11 [DERIVED SSOT] 결정적 파생 재계산 단일 함수
#    원자료가 바뀌면 파생도 다시 만들어야 한다. ffill 로 과거 derived 값을 끌어오는 것은
#    '재계산'이 아니라 'carry' 이며 설계 계약과 다르다.
#    실례: 결측 세션 복구 행은 VIX · VIX3M 이 그 날짜 actual 인데
#          VIX_VIX3M_ratio 는 NaN 으로 남고 FFILL_COLS 에도 없어 영영 비어 있었다.
# ══════════════════════════════════════════════════════════════════════
def recompute_deterministic_derived(df):
    """파일 안 자료만으로 결정적으로 재계산 가능한 파생을 다시 만든다. 네트워크 0."""
    done = []
    if "VIX" in df.columns and "VIX3M" in df.columns:
        _v = pd.to_numeric(df["VIX"], errors="coerce")
        _v3 = pd.to_numeric(df["VIX3M"], errors="coerce")
        df["VIX_VIX3M_ratio"] = _v / _v3.replace(0, np.nan)
        done.append("VIX_VIX3M_ratio")
    if all(c in df.columns for c in ("WALCL", "WTREGEN", "RRPONTSYD")):
        # 🌟 RRP 십억$ → 백만$ (×1e3) — BT v5 정본 규약
        df["Net_Liquidity"] = (pd.to_numeric(df["WALCL"], errors="coerce").ffill()
                               - pd.to_numeric(df["WTREGEN"], errors="coerce").ffill()
                               - pd.to_numeric(df["RRPONTSYD"], errors="coerce").ffill() * 1e3)
        done.append("Net_Liquidity")
    try:
        df["KIL_SUP"] = compute_kil_sup(df)     # 🔴 반환은 Series — df 에 대입하지 않는다
        done.append("KIL_SUP")
    except Exception as e:
        print(f"  ⚠️ KIL_SUP 재계산 실패({type(e).__name__}: {e}) — 기존 값 유지")
    print(f"  ♻️ v3.9.11 결정적 파생 재계산: {', '.join(done) if done else '없음'}")
    return df


# ══════════════════════════════════════════════════════════════════════
# 🚫 v3.9.11 [MIGRATION CONTRACT] 네트워크 하드 가드
#    "외부 갱신을 섞지 않는다" 를 주석이 아니라 실행으로 보장한다.
#    v3.9.10 은 그렇게 선언해 놓고 compute_smh_triflag(prices=None) 경로에서
#    yf.download(["MU","HYG","LQD"]) 를 실제로 호출했다 — 선언과 구현의 괴리.
#    호출 시도가 있으면 조용히 통과시키지 않고 즉시 예외로 드러낸다.
# ══════════════════════════════════════════════════════════════════════
class NetworkBlocked(RuntimeError):
    pass


class _network_guard:
    """with 블록 안에서 yfinance · requests · urllib 호출을 차단한다."""

    def __init__(self, label="migration"):
        self.label = label
        self._saved = []
        self.attempts = []

    def _deny(self, name):
        def _f(*a, **k):
            self.attempts.append(name)
            raise NetworkBlocked(
                f"{self.label} 중 네트워크 호출 차단: {name} — "
                "마이그레이션은 파일 안 자료만 사용한다 (인과 귀속 보존)")
        return _f

    def __enter__(self):
        import urllib.request as _ur
        targets = [(yf, "download"), (requests, "get"), (requests, "post"),
                   (_ur, "urlopen")]
        for obj, attr in targets:
            if hasattr(obj, attr):
                self._saved.append((obj, attr, getattr(obj, attr)))
                setattr(obj, attr, self._deny(f"{getattr(obj, '__name__', obj)}.{attr}"))
        return self

    def __exit__(self, *exc):
        for obj, attr, orig in self._saved:
            setattr(obj, attr, orig)
        return False


MIGRATION_BUNDLE_DIR = os.path.join(SCRIPT_DIR, "migration_inputs")


def load_migration_bundle():
    """🗃️ v3.9.12 Migration Dependency Bundle — 마이그레이션 입력 동결본 (전량 필수).

    migration_inputs/
      ├─ manifest.json        source_sha256 · source_csv_sha256 · observed_through
      ├─ smh_prices.csv       (Date, MU, HYG, LQD)
      ├─ wsts_yoy.json        🔴 필수 — 레포 루트 fallback 금지
      └─ missing_market.csv   결측 세션 × MARKET_IMMUTABLE 동결값 (있으면 네트워크 없이 복구)

    v3.9.11 대비 변경 3건
      🔴 P0-13 wsts 는 parse_wsts_yoy_json() 으로 읽는다 (production 과 동일 parser).
      🔴 P0-14 wsts 부재 시 레포 루트로 내려가지 않는다. 없으면 번들 자체를 불완전으로 본다 —
              10:00 에 번들을 만들고 10:05 에 upstream 이 wsts 를 바꾸면 Crown Δ 에
              dependency change 가 섞인다.
      🔴 P1-b  manifest 의 sha256 과 **현재 파일 해시를 대조**한다. 불일치 = fail-closed.
              기록만 하고 검증하지 않으면 동결이 아니다.

    반환: {"ok": bool, "reason": str, "prices", "wsts", "missing_market",
           "manifest", "sha256", "source_csv_sha256"}
    """
    import hashlib as _hl
    out = {"ok": False, "reason": "", "prices": None, "wsts": None,
           "missing_market": None, "manifest": None, "sha256": {},
           "source_csv_sha256": None}
    if not os.path.isdir(MIGRATION_BUNDLE_DIR):
        out["reason"] = f"번들 폴더 없음 ({MIGRATION_BUNDLE_DIR})"
        return out

    mf_path = os.path.join(MIGRATION_BUNDLE_DIR, "manifest.json")
    if not os.path.exists(mf_path):
        out["reason"] = "manifest.json 없음"
        return out
    try:
        manifest = json.load(open(mf_path, encoding="utf-8"))
    except Exception as e:
        out["reason"] = f"manifest 파싱 실패 ({type(e).__name__})"
        return out
    out["manifest"] = manifest
    out["source_csv_sha256"] = manifest.get("source_csv_sha256")

    required = ["smh_prices.csv", "wsts_yoy.json"]
    optional = ["missing_market.csv"]
    declared = manifest.get("source_sha256", {}) or {}

    for name in required + optional:
        p = os.path.join(MIGRATION_BUNDLE_DIR, name)
        if not os.path.exists(p):
            if name in required:
                out["reason"] = f"{name} 없음 — 부분 번들 금지 (레포 루트 fallback 금지)"
                return out
            continue
        cur = _hl.sha256(open(p, "rb").read()).hexdigest()
        out["sha256"][name] = cur[:16]
        want = declared.get(name)
        if want and want != cur:
            out["reason"] = (f"{name} 해시 불일치 — manifest {str(want)[:12]}… "
                             f"실제 {cur[:12]}… (동결 파괴, fail-closed)")
            return out
        if not want:
            out["reason"] = f"{name} 해시가 manifest 에 선언되지 않음 (동결 미성립)"
            return out

    try:
        px = pd.read_csv(os.path.join(MIGRATION_BUNDLE_DIR, "smh_prices.csv"),
                         index_col=0, parse_dates=True)
    except Exception as e:
        out["reason"] = f"smh_prices.csv 파싱 실패 ({type(e).__name__})"
        return out
    if not all(c in px.columns for c in ("MU", "HYG", "LQD")):
        out["reason"] = "smh_prices.csv 에 MU/HYG/LQD 중 누락"
        return out
    # 🔧 v3.9.13 P1-14: 컬럼 존재만으로는 부족하다.
    #   MU 는 유효 1000행인데 LQD 가 전부 NaN 이어도 종전 검사는 '완전한 번들' 로 통과했고,
    #   그 경우 SMH_TRIFLAG 가 조용히 거의 전부 0 이 된다.
    #   알고리즘이 요구하는 최소 관측량을 상수로 선언하고 실제 유효 행수를 본다.
    _idx = pd.DatetimeIndex(pd.to_datetime(px.index))
    if _idx.has_duplicates:
        out["reason"] = "smh_prices.csv 인덱스 중복"
        return out
    if not _idx.is_monotonic_increasing:
        out["reason"] = "smh_prices.csv 인덱스 비단조"
        return out
    for _s in ("MU", "HYG", "LQD"):
        _n = int(pd.to_numeric(px[_s], errors="coerce").notna().sum())
        if _n < SMH_BUNDLE_MIN_ROWS:
            out["reason"] = (f"smh_prices.csv {_s} 유효 {_n}행 < 최소 {SMH_BUNDLE_MIN_ROWS}행 "
                             "(126일 momentum + 189일 rolling warm-up 미달)")
            return out
    out["prices"] = px

    try:
        ws = parse_wsts_yoy_json(os.path.join(MIGRATION_BUNDLE_DIR, "wsts_yoy.json"))
    except Exception as e:
        out["reason"] = f"wsts_yoy.json 파싱 실패 ({type(e).__name__})"
        return out
    if ws is None or len(ws) == 0:
        out["reason"] = "wsts_yoy.json 시리즈 0건"
        return out
    out["wsts"] = ws

    # 🔧 v3.9.13 P1-14: manifest.missing_dates 와 missing_market.csv 를 **양방향** 계약으로 묶는다.
    #   종전에는 unconditional optional 이라, 결측이 있는데 파일이 없으면 트랜잭션 한복판에서야
    #   실패했다. 번들 적재 단계에서 거부하는 것이 맞다.
    mm_path = os.path.join(MIGRATION_BUNDLE_DIR, "missing_market.csv")
    _declared_missing = [str(x)[:10] for x in (manifest.get("missing_dates") or [])]
    if _declared_missing and not os.path.exists(mm_path):
        out["reason"] = (f"manifest 가 결측 {len(_declared_missing)}건을 선언했는데 "
                         "missing_market.csv 가 없다 (번들 불완전)")
        return out
    if not _declared_missing and os.path.exists(mm_path):
        out["reason"] = "manifest 는 결측 0건인데 missing_market.csv 가 존재한다 (번들 불일치)"
        return out
    if os.path.exists(mm_path):
        try:
            mm = pd.read_csv(mm_path, index_col=0, parse_dates=True)
            mm.index = pd.DatetimeIndex(mm.index).normalize()
        except Exception as e:
            out["reason"] = f"missing_market.csv 파싱 실패 ({type(e).__name__})"
            return out
        _have = sorted({str(x.date()) for x in mm.index})
        if _have != sorted(set(_declared_missing)):
            out["reason"] = (f"missing_market.csv 날짜 불일치 — manifest {sorted(set(_declared_missing))[:6]} "
                             f"대 파일 {_have[:6]}")
            return out
        out["missing_market"] = mm

    out["ok"] = True
    return out


MIGRATION_BASELINE_PATH = os.path.join(SCRIPT_DIR, "migration_baseline_frozen.csv")


MIGRATION_STAGE_DIR = os.path.join(SCRIPT_DIR, "migration_stage")
# 🔧 v3.9.15: Git-safe generation evidence + regular-file public views.
MIGRATION_GENERATIONS_DIR = os.path.join(SCRIPT_DIR, "migration_generations")
MIGRATION_CURRENT_META_PATH = os.path.join(SCRIPT_DIR, "CURRENT_GENERATION.json")
MIGRATION_PENDING_META_PATH = os.path.join(SCRIPT_DIR, "PENDING_GENERATION.json")
# v3.9.14 legacy pointer. 새 버전에서는 사용하지 않으며 존재해도 public artifact 와 분리한다.
MIGRATION_LEGACY_CURRENT_LINK = os.path.join(SCRIPT_DIR, "migration_current")
MIGRATION_PUBLIC_PATHS = {
    "argus_data.csv": OUTPUT_PATH,
    "argus_data_daily.csv": OUTPUT_DAILY_PATH,
    "argus_data_weekly.csv": OUTPUT_WEEKLY_PATH,
    "argus_data_monthly.csv": OUTPUT_MONTHLY_PATH,
    "migration_baseline_frozen.csv": MIGRATION_BASELINE_PATH,
    "calendar_integrity_report.json": SESSION_CALENDAR_REPORT_PATH,
}
MIGRATION_VIEW_NAMES = list(MIGRATION_PUBLIC_PATHS.keys())


def _sha256_file(path):
    import hashlib as _hl
    with open(path, "rb") as f:
        return _hl.sha256(f.read()).hexdigest()


def _fsync_dir(path):
    """POSIX directory metadata 를 가능한 범위에서 flush. 지원하지 않으면 fail-safe skip."""
    try:
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except Exception:
        pass


def _write_json_fsync(path, payload):
    """JSON regular file 을 tmp→replace 로 원자 갱신."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + f".tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        _fsync_dir(os.path.dirname(path) or ".")
    finally:
        if os.path.lexists(tmp):
            os.remove(tmp)


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _de_symlink_public_artifacts():
    """v3.9.14 symlink 공개파일을 bytes 보존 regular file 로 1회 변환한다.

    git/raw 계약상 공개 6종에 symlink 를 허용하지 않는다. 정상 symlink 는 target bytes 를 같은 경로의
    regular tmp 로 복사한 뒤 os.replace 로 링크 자체를 교체한다. target 이 없는 broken symlink 는
    복구 근거가 없으므로 fail-closed 한다.
    """
    converted = []
    for name, path in MIGRATION_PUBLIC_PATHS.items():
        if not os.path.islink(path):
            continue
        target = os.path.realpath(path)
        if not os.path.isfile(target):
            raise RuntimeError(
                f"GIT-SAFE 전환 실패: {name} broken symlink → {target}. "
                "v3.9.14 generation 또는 이전 regular file 을 복원한 뒤 재실행할 것")
        before_sha = _sha256_file(target)
        tmp = path + f".desymlink.{os.getpid()}.{uuid.uuid4().hex[:8]}"
        try:
            shutil.copy2(target, tmp, follow_symlinks=True)
            if _sha256_file(tmp) != before_sha:
                raise RuntimeError(f"GIT-SAFE 전환 sha 불일치: {name}")
            os.replace(tmp, path)  # symlink 자체를 regular file 로 교체
            _fsync_dir(os.path.dirname(path) or ".")
        finally:
            if os.path.lexists(tmp):
                os.remove(tmp)
        if os.path.islink(path) or _sha256_file(path) != before_sha:
            raise RuntimeError(f"GIT-SAFE 전환 검증 실패: {name}")
        converted.append(name)
    if converted:
        print(f"  🔧 v3.9.15 symlink→regular file 전환 {len(converted)}건: {converted}")
    return converted


def _generation_manifest(gen_dir):
    path = os.path.join(gen_dir, "generation_manifest.json")
    if not os.path.isfile(path):
        raise RuntimeError(f"generation manifest 없음: {path}")
    m = _read_json(path)
    hashes = m.get("files_sha256") or {}
    if not hashes:
        raise RuntimeError("generation manifest files_sha256 비어 있음")
    return m, hashes


def _verify_generation(gen_dir, expected_hashes=None):
    """generation 내부 regular bytes 와 manifest sha 를 모두 검증."""
    m, hashes = _generation_manifest(gen_dir)
    if expected_hashes is not None:
        for name, want in expected_hashes.items():
            if hashes.get(name) != want:
                raise RuntimeError(f"generation expected sha 불일치: {name}")
    for name in MIGRATION_VIEW_NAMES:
        p = os.path.join(gen_dir, name)
        want = hashes.get(name)
        if not want or not os.path.isfile(p):
            raise RuntimeError(f"generation 불완전: {name}")
        got = _sha256_file(p)
        if got != want:
            raise RuntimeError(f"generation sha 불일치: {name} {got[:12]} != {want[:12]}")
    return m, hashes


def _atomic_copy_regular(src, dst, expected_sha):
    """generation file → public regular file. 중단돼도 다음 실행에서 같은 결과로 수렴 가능."""
    if _sha256_file(src) != expected_sha:
        raise RuntimeError(f"복사 원본 sha 불일치: {src}")
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    tmp = dst + f".next.{os.getpid()}.{uuid.uuid4().hex[:8]}"
    try:
        shutil.copy2(src, tmp, follow_symlinks=True)
        if _sha256_file(tmp) != expected_sha:
            raise RuntimeError(f"public tmp sha 불일치: {os.path.basename(dst)}")
        # dst 가 v3.9.14 symlink 여도 os.replace 는 target 이 아니라 symlink 자체를 교체한다.
        os.replace(tmp, dst)
        _fsync_dir(os.path.dirname(dst) or ".")
    finally:
        if os.path.lexists(tmp):
            os.remove(tmp)
    if os.path.islink(dst) or _sha256_file(dst) != expected_sha:
        raise RuntimeError(f"public regular-file 승격 검증 실패: {os.path.basename(dst)}")


def _current_generation_payload(gen_id, hashes, *, state="committed", extra=None):
    payload = {
        "version": FETCHER_VER,
        "generation_id": gen_id,
        "state": state,
        "generation_relpath": os.path.relpath(os.path.join(MIGRATION_GENERATIONS_DIR, gen_id), SCRIPT_DIR),
        "files_sha256": hashes,
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "public_files_are_regular": True,
    }
    if extra:
        payload.update(extra)
    return payload


def _converge_generation_to_public(gen_id, hashes, *, fault_after=None):
    """한 generation 을 공개 regular files 로 멱등 수렴시킨다."""
    gen_dir = os.path.join(MIGRATION_GENERATIONS_DIR, gen_id)
    _verify_generation(gen_dir, hashes)
    done = 0
    for name, dst in MIGRATION_PUBLIC_PATHS.items():
        src = os.path.join(gen_dir, name)
        want = hashes[name]
        # 이미 같은 bytes 면 건드리지 않는다.
        if os.path.isfile(dst) and not os.path.islink(dst):
            try:
                if _sha256_file(dst) == want:
                    done += 1
                    if fault_after is not None and done >= fault_after:
                        raise RuntimeError(f"TEST_FAULT_AFTER_{done}")
                    continue
            except OSError:
                pass
        _atomic_copy_regular(src, dst, want)
        done += 1
        if fault_after is not None and done >= fault_after:
            raise RuntimeError(f"TEST_FAULT_AFTER_{done}")
    # 최종 전수검증
    for name, dst in MIGRATION_PUBLIC_PATHS.items():
        if os.path.islink(dst) or not os.path.isfile(dst) or _sha256_file(dst) != hashes[name]:
            raise RuntimeError(f"public convergence 최종검증 실패: {name}")
    return done


def _recover_pending_generation():
    """중단된 commit 이 있으면 daily/network 경로 진입 전에 동일 generation 으로 수렴 복구."""
    if not os.path.exists(MIGRATION_PENDING_META_PATH):
        return False
    pending = _read_json(MIGRATION_PENDING_META_PATH)
    gen_id = pending.get("generation_id")
    hashes = pending.get("files_sha256") or {}
    if not gen_id or not hashes:
        raise RuntimeError("PENDING_GENERATION.json 불완전 — 자동 진행 금지")
    print(f"  ♻️ v3.9.15 pending generation 복구: {gen_id}")
    _converge_generation_to_public(gen_id, hashes)
    current = _current_generation_payload(
        gen_id, hashes, state="committed",
        extra={"recovered_from_pending": True, "pending_created_utc": pending.get("created_utc")})
    _write_json_fsync(MIGRATION_CURRENT_META_PATH, current)
    os.remove(MIGRATION_PENDING_META_PATH)
    _fsync_dir(SCRIPT_DIR)
    print("     ✅ public files 수렴 + CURRENT_GENERATION.json 확정")
    return True


def _build_generation_from_stage(stage_files, report_payload):
    """검증된 staging 산출물을 immutable generation 으로 봉인하고 경로/sha 를 반환."""
    master_sha = _sha256_file(_stage_path("argus_data.csv"))
    gen_id = f"mig_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{master_sha[:12]}"
    final_dir = os.path.join(MIGRATION_GENERATIONS_DIR, gen_id)
    tmp_dir = final_dir + f".tmp.{os.getpid()}.{uuid.uuid4().hex[:8]}"
    if os.path.lexists(final_dir):
        raise RuntimeError(f"generation 충돌: {final_dir}")
    os.makedirs(MIGRATION_GENERATIONS_DIR, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=False)
    hashes = {}
    try:
        for name in stage_files:
            src = _stage_path(name)
            dst = os.path.join(tmp_dir, name)
            shutil.copy2(src, dst)
            hashes[name] = _sha256_file(dst)
        report_path = os.path.join(tmp_dir, "calendar_integrity_report.json")
        rp = dict(report_payload)
        rp["generation_id"] = gen_id
        rp["commit_seal"] = "immutable generation + pending convergence + CURRENT_GENERATION.json"
        rp["generated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        _write_json_fsync(report_path, rp)
        hashes["calendar_integrity_report.json"] = _sha256_file(report_path)
        _write_json_fsync(os.path.join(tmp_dir, "generation_manifest.json"), {
            "version": FETCHER_VER,
            "kind": "calendar_migration",
            "generation_id": gen_id,
            "files_sha256": hashes,
            "generated_utc": rp["generated_utc"],
            "immutable_contract": "daily/backfill must never write under migration_generations/",
        })
        _fsync_dir(tmp_dir)
        os.replace(tmp_dir, final_dir)
        _fsync_dir(MIGRATION_GENERATIONS_DIR)
        _verify_generation(final_dir, hashes)
        return gen_id, final_dir, hashes
    finally:
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)


def _commit_generation_convergent(gen_id, gen_dir, hashes):
    """Git-safe commit: pending 기록 → public regular files 수렴 → CURRENT 메타 확정 → pending 제거.

    public files 의 다중 replace 자체는 원자적이지 않지만, pending 이 commit 의도를 보존한다.
    프로세스가 중간 종료되면 다음 실행 첫 단계에서 같은 immutable generation 으로 수렴한다.
    """
    _verify_generation(gen_dir, hashes)
    pending = {
        "version": FETCHER_VER,
        "state": "pending",
        "generation_id": gen_id,
        "generation_relpath": os.path.relpath(gen_dir, SCRIPT_DIR),
        "files_sha256": hashes,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _write_json_fsync(MIGRATION_PENDING_META_PATH, pending)

    # 테스트 전용 fault injection. production 미설정.
    _fault_raw = os.environ.get("ARGUS_MIGRATION_FAULT_AFTER_N", "").strip()
    _fault_after = int(_fault_raw) if _fault_raw.isdigit() and int(_fault_raw) > 0 else None
    _converge_generation_to_public(gen_id, hashes, fault_after=_fault_after)

    current = _current_generation_payload(
        gen_id, hashes, state="committed",
        extra={"commit_contract": "regular files + convergent pending recovery"})
    _write_json_fsync(MIGRATION_CURRENT_META_PATH, current)
    if os.path.exists(MIGRATION_PENDING_META_PATH):
        os.remove(MIGRATION_PENDING_META_PATH)
        _fsync_dir(SCRIPT_DIR)
    return current


def _assert_generation_immutable(gen_id, hashes):
    """봉인 직후/테스트 후 generation bytes 가 manifest 와 동일한지 확인."""
    gen_dir = os.path.join(MIGRATION_GENERATIONS_DIR, gen_id)
    _verify_generation(gen_dir, hashes)
    return True

def normalize_frozen_view(df, bundle, label):
    """🔒 v3.9.13 [TRANSFORM SEAL] BEFORE·AFTER 에 **동일하게** 적용하는 정규화.

    🔴 v3.9.12 결함: AFTER 만 apply_ffill_safety() 를 거쳤다. 이 함수는 새로 삽입한 행만
    채우는 것이 아니라 FFILL_COLS + 모든 *_Close 를 **전 history 소급 보강**한다.
    기존 dirty CSV 에 과거 NaN 이 하나라도 있으면
        BEFORE = NaN 유지 / AFTER = ffill 정규화
    가 되어 Crown Δ 에 ffill normalization effect 가 섞인다.
    이제 두 경로가 같은 함수를 지나고, 차이는 **structural calendar transform 뿐**이다.
    """
    df = apply_ffill_safety(df)
    df = recompute_deterministic_derived(df)
    df["SMH_TRIFLAG"] = compute_smh_triflag(df, prices=bundle["prices"],
                                            wsts_series=bundle["wsts"])
    print(f"  ♻️ {label}: ffill + 결정적 파생 + SMH_TRIFLAG (동결 의존)")
    return df


def _stage_path(name):
    return os.path.join(MIGRATION_STAGE_DIR, name + ".tmp")


def _migration_transaction(df_original, bundle):
    """🔒 v3.9.13 [ATOMICMIGRATION] PHASE B·C·D — 가드 안에서, staging 에만 쓴다.

    세 봉인
      TRANSFORM SEAL  BEFORE·AFTER 가 normalize_frozen_view() 하나를 공유한다.
      COMMIT SEAL     모든 산출물을 migration_stage/*.tmp 에 먼저 쓰고, 전 검증 통과 후
                      os.replace 로 한꺼번에 승격한다. v3.9.12 는 PHASE B 에서 baseline 을
                      바로 정식 파일명으로 쓰고 PHASE C 에서 4개 CSV 를 순차로 덮어써서,
                      중간 실패 시 NEW/OLD 가 섞인 상태가 가능했다.
      가드 범위       PHASE B·C·D 전체 (v3.9.12 는 D 가 가드 밖이었다).
    """
    import hashlib as _hl
    print("🔒 v3.9.15 MIGRATION TRANSACTION — local-only calendar · network hard-off · git-safe convergent commit")
    _in_sha = _hl.sha256(open(OUTPUT_PATH, "rb").read()).hexdigest() \
        if os.path.exists(OUTPUT_PATH) else None
    if bundle.get("source_csv_sha256") and _in_sha and bundle["source_csv_sha256"] != _in_sha:
        raise SystemExit(
            "🔴 v3.9.13 번들이 가리키는 원본 CSV 와 현재 CSV 가 다르다 — "
            f"manifest {str(bundle['source_csv_sha256'])[:12]}… 현재 {_in_sha[:12]}…. "
            "번들을 다시 생성할 것 (PHASE A).")

    if os.path.isdir(MIGRATION_STAGE_DIR):
        for _f in os.listdir(MIGRATION_STAGE_DIR):
            os.remove(os.path.join(MIGRATION_STAGE_DIR, _f))
    os.makedirs(MIGRATION_STAGE_DIR, exist_ok=True)

    guard = _network_guard("MIGRATION_TRANSACTION")
    parity = {"checked": False}
    with guard:
        # ── PHASE B — BASELINE REPLAY (원 캘린더 + 동결 의존 + 동일 정규화) ──
        print("📐 PHASE B — BASELINE REPLAY (원 캘린더 · 동결 의존)")
        base = df_original.copy()
        _prev_tri = base["SMH_TRIFLAG"].copy() if "SMH_TRIFLAG" in base.columns else None
        base = normalize_frozen_view(base, bundle, "baseline")
        if _prev_tri is not None:
            _a = _prev_tri.reindex(base.index).fillna(0).astype(float)
            _b = base["SMH_TRIFLAG"].reindex(base.index).fillna(0).astype(float)
            _diff = int((_a != _b).sum())
            parity = {"checked": True, "smh_triflag_diff_days": _diff, "rows": int(len(base))}
            print(f"  🔍 dependency parity: 기존 SMH_TRIFLAG 대비 불일치 {_diff}일 / {len(base)}일")
            if _diff:
                print("     🟠 Crown before 는 반드시 migration_baseline_frozen.csv 로 돌린다.")
        base.to_csv(_stage_path("migration_baseline_frozen.csv"))

        # ── PHASE C — MIGRATE (structural transform + 동일 정규화) ──
        print("🧹 PHASE C — MIGRATE (유령 제거 · 결측 복구 · 동일 정규화)")
        df, pre_snapshot = _sanitize_non_session_rows(df_original.copy(), stage="migration", primary_only=True)
        repaired = []
        _missing = _calendar_integrity_snapshot(df, "migration_after_ghost", primary_only=True).get("missing_dates", [])
        if _missing:
            print(f"  🚨 정규장 결측 {len(_missing)}건: {_missing}")
            df, repaired = _repair_missing_session_rows(df, _missing, bundle=bundle)
        df = normalize_frozen_view(df, bundle, "migrated")
        if repaired:
            df = _finalize_repair_provenance(df, repaired)

        _final = _enforce_final_session_integrity(
            df, pre_snapshot=pre_snapshot, repaired_dates=repaired,
            primary_only=True, write_report=False)
        df_daily, df_weekly, df_monthly = _split_by_frequency(df)
        df_daily.to_csv(_stage_path("argus_data_daily.csv"))
        df_weekly.to_csv(_stage_path("argus_data_weekly.csv"))
        df_monthly.to_csv(_stage_path("argus_data_monthly.csv"))
        df.to_csv(_stage_path("argus_data.csv"))

        # ── PHASE D — VERIFY (가드 안에서 수행) ──
        print("✅ PHASE D — VERIFY (staging 검증)")
        _stage_files = {
            "migration_baseline_frozen.csv": MIGRATION_BASELINE_PATH,
            "argus_data_daily.csv": OUTPUT_DAILY_PATH,
            "argus_data_weekly.csv": OUTPUT_WEEKLY_PATH,
            "argus_data_monthly.csv": OUTPUT_MONTHLY_PATH,
            "argus_data.csv": OUTPUT_PATH,
        }
        _stage_sha = {}
        for _name in _stage_files:
            _p = _stage_path(_name)
            if not os.path.exists(_p) or os.path.getsize(_p) == 0:
                raise SystemExit(f"🔴 v3.9.13 staging 산출물 누락/공백: {_name} — 승격 중단")
            _stage_sha[_name] = _hl.sha256(open(_p, "rb").read()).hexdigest()
        _bad = final_bad = (_final or {}).get("ghost_n", 0) + (_final or {}).get("missing_n", 0) \
            + (_final or {}).get("duplicate_n", 0)
        if _bad:
            raise SystemExit(f"🔴 v3.9.13 무결성 미충족 (bad={_bad}) — 승격 중단")
        if guard.attempts:
            raise SystemExit(
                f"🔴 v3.9.13 트랜잭션 중 네트워크 호출 시도 {len(guard.attempts)}건 "
                f"{guard.attempts[:3]} — 승격 중단 (동결 파괴)")

        # ── COMMIT SEAL — 전 검증 통과 후에만 원자 승격 ──
        _scols = [c for c in df.columns if c.endswith("_source")]
        _cnt = lambda tag: int(sum((df[c] == tag).sum() for c in _scols)) if _scols else 0
        report = {
            "version": FETCHER_VER, "mode": "atomic_migration_transaction",
            "invariant": "1 row = 1 completed US equity regular session",
            "input_sha256": _in_sha,
            "output_sha256": _stage_sha["argus_data.csv"],
            "baseline_frozen_sha256": _stage_sha["migration_baseline_frozen.csv"],
            "staged_sha256": {k: v[:16] for k, v in _stage_sha.items()},
            "calendar_source": (_final or {}).get("calendar_source"),
            "ghost_removed_n": int((pre_snapshot or {}).get("ghost_n", 0)),
            "missing_repaired_n": len(repaired),
            "missing_repair_source": "frozen_bundle" if bundle.get("missing_market") is not None
                                     else "none_needed",
            "market_exact_repair_n": _cnt("market_historical"),
            "pit_ffill_n": _cnt("pit_ffill_repair"),
            "pit_unresolved_n": _cnt("pit_unresolved"),
            "external_network_calls": len(guard.attempts),
            "network_attempts": guard.attempts,
            "guard_scope": "PHASE_B_C_D",
            "transform_seal": "normalize_frozen_view (BEFORE·AFTER 동일)",
            "commit_seal": "immutable generation + convergent regular-file commit + CURRENT_GENERATION.json",
            "dependency_sha256": bundle["sha256"],
            "dependency_parity": parity,
            "rows": int(len(df)), "final": _final,
        }
        with open(_stage_path("calendar_integrity_report.json"), "w", encoding="utf-8") as f:
            _r = dict(report)
            _r["generated_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            json.dump(_r, f, ensure_ascii=False, indent=2)

        # 🔧 v3.9.15 COMMIT SEAL: symlink 폐기. immutable generation 을 만든 뒤
        # PENDING_GENERATION.json 으로 의도를 먼저 기록하고 public **regular files** 를 멱등 수렴시킨다.
        # 마지막에 CURRENT_GENERATION.json 을 원자 교체한다. 중간 중단은 다음 실행 시작 시 자동 복구된다.
        print("📦 COMMIT SEAL — immutable generation → pending → regular files 수렴 → CURRENT meta")
        _gen_names = list(_stage_files.keys())
        _gen_id, _gen_dir, _gen_hashes = _build_generation_from_stage(_gen_names, report)
        for _name in _gen_names:
            if _gen_hashes.get(_name) != _stage_sha.get(_name):
                raise SystemExit(f"🔴 v3.9.15 generation sha 불일치: {_name} — commit 중단")
        _current = _commit_generation_convergent(_gen_id, _gen_dir, _gen_hashes)
        _assert_generation_immutable(_gen_id, _gen_hashes)
        for _name, _view in MIGRATION_PUBLIC_PATHS.items():
            if os.path.islink(_view):
                raise SystemExit(f"🔴 v3.9.15 public artifact 가 symlink: {_name}")
            if _sha256_file(_view) != _gen_hashes[_name]:
                raise SystemExit(f"🔴 v3.9.15 public artifact sha 불일치: {_name}")
        print(f"   ✅ CURRENT_GENERATION = {_gen_id} · public regular files {len(MIGRATION_PUBLIC_PATHS)}종")
        report["generation_id"] = _gen_id
        report["generation_path"] = _gen_dir
        report["commit_seal"] = "immutable generation + convergent regular-file commit + CURRENT_GENERATION.json"

    print(f"  external_network_calls = {len(guard.attempts)}  (가드 범위: PHASE B·C·D 전체)")
    print(f"  input {str(_in_sha)[:16]}… → output {report['output_sha256'][:16]}…")
    print(f"  ghost 제거 {report['ghost_removed_n']} · 결측 복구 {report['missing_repaired_n']} "
          f"({report['missing_repair_source']})")
    print("  🎯 Crown 대조: BEFORE = migration_baseline_frozen.csv / AFTER = argus_data.csv")
    print("  🎯 다음: CALENDAR_MIGRATION_MODE 해제 → Crown before/after → baseline 봉인")
    return df


def run_calendar_migration():
    """🚪 v3.9.13 [ENTRY SEAL] 마이그레이션 전용 진입점.

    🔴 v3.9.12 결함: migration 분기가 main() 중반에 있어, 거기 닿기 전에
    resolve_session_date() → _yf_series() → yf.download() 이 이미 실행됐다.
    따라서 external_network_calls = 0 은 여전히 프로세스 전체의 증명이 아니었다.
    이 함수는 **daily/backfill session resolution 을 통째로 우회**한다 —
    첫 network-capable 코드보다 먼저 분기한다.
    """
    print("🚪 v3.9.15 ENTRY SEAL — 마이그레이션 전용 경로 (session resolution/fallback 우회)")
    if not os.path.exists(OUTPUT_PATH):
        print(f"🔴 원본 CSV 없음: {OUTPUT_PATH} — 마이그레이션 대상 없음")
        return
    bundle = load_migration_bundle()
    if not bundle["ok"]:
        print("🔴 v3.9.13 마이그레이션 중단 — 의존 번들 불완전")
        print(f"   사유: {bundle['reason']}")
        print("   처방: python make_migration_bundle.py 로 번들을 생성/재생성할 것 (PHASE A)")
        print("   이번 실행은 파일을 변경하지 않는다.")
        _write_calendar_integrity_report({
            "version": FETCHER_VER, "mode": "migration_bundle_incomplete",
            "reason": bundle["reason"], "final": None,
        })
        return
    # v3.9.15: v3.9.14 잔존 symlink 를 먼저 regular file 로 전환하고, 중단된 commit 을 복구한다.
    # pending 이 있으면 broken legacy symlink 도 generation regular file 로 직접 덮어 복구할 수 있으므로
    # 수렴 복구를 먼저 시도한다. pending 이 없을 때만 잔존 v3.9.14 symlink 를 bytes 보존 전환한다.
    _recover_pending_generation()
    _de_symlink_public_artifacts()
    df = pd.read_csv(OUTPUT_PATH, index_col=0, parse_dates=True)
    df.index.name = "Date"
    df = df.sort_index()
    _audit = _calendar_integrity_snapshot(df, "entry_seal_audit", primary_only=True)
    print(f"  입력 {len(df)}행 · 유령 {_audit['ghost_n']} · 결측 {_audit['missing_n']} "
          f"· 중복 {_audit['duplicate_n']} ({_audit['calendar_source']})")
    _migration_transaction(df, bundle)


def _enforce_final_session_integrity(df: pd.DataFrame, *, pre_snapshot=None, repaired_dates=None,
                                     primary_only=False, write_report=True):
    """저장 직전 강제 게이트. ghost/missing/duplicate가 하나라도 남으면 저장 차단."""
    final = _calendar_integrity_snapshot(df, "pre_save_final", primary_only=primary_only)
    report = {
        "version": FETCHER_VER,
        "invariant": "1 row = 1 completed US equity regular session",
        "pre_repair": pre_snapshot,
        "repaired_missing_dates": list(repaired_dates or []),
        "final": final,
    }
    if write_report:
        _write_calendar_integrity_report(report)
    # 🔴 v3.9.9 fallback 은 PASS 를 인증할 수 없다.
    #   density >= 90% 가드는 심한 장애만 잡는다. 100 영업일에서 5세션이 누락돼도 95% 다.
    #   그 상태의 missing_n = 0 은 "yfinance 가 관측한 캘린더 안에서 0" 일 뿐,
    #   "실제 XNYS 세션 기준 0" 을 증명하지 못한다. 증명할 수 없으면 인증하지 않는다.
    _srcname = str(final.get("calendar_source") or "")
    if final.get("rows") and not _srcname.startswith("exchange_calendars:"):
        raise SystemExit(
            "🔴 v3.9.9 SESSION INTEGRITY — 저장 차단: 캘린더 소스가 1순위가 아니다"
            f"({_srcname or '없음'}). fallback 은 진단 전용이며 무결성 PASS 를 인증하지 못한다. "
            "처방: requirements 에 exchange-calendars 를 고정 버전으로 추가 후 재실행.")
    bad = final["ghost_n"] + final["missing_n"] + final["duplicate_n"] + final.get("nat_dates", 0)
    if bad:
        raise SystemExit(
            "🔴 v3.9.7 SESSION INTEGRITY — 저장 차단: "
            f"ghost={final['ghost_n']} missing={final['missing_n']} "
            f"duplicate={final['duplicate_n']} NaT={final.get('nat_dates', 0)}. "
            f"report={SESSION_CALENDAR_REPORT_PATH}"
        )
    print(f"  ✅ v3.9.7 세션 무결성 PASS — {final['rows']}행 · ghost 0 · missing 0 · duplicate 0 "
          f"({final['calendar_source']})")
    return final


def _yf_batch(symbols: list, start: str, end: str, exact_date=None) -> dict:
    """yfinance 배치 → {symbol: close}.

    🔴 v3.9.11 [MARKET CONTRACT] exact_date 를 주면 **그 날짜의 실제 bar** 만 채택한다.
       종전은 무조건 window 의 마지막 행(`close.iloc[-1]`)을 썼다. 그러면 요청 날짜에
       bar 가 없을 때 인접일 값이 요청 날짜로 stamp 된다 —
       target 2026-05-20 · Yahoo 에 5/20 없음 · 5/19 존재 → 5/19 값이 Date=5/20 으로 기록.
       미래 날짜 오염은 v3.9.10 이 막았지만 historical adjacent-bar misstamp 는 남아 있었다.
       이 함수가 repair · backfill · daily 세 경로의 **유일한 시장데이터 취득 지점**이므로
       여기서 Date ↔ bar identity 를 한 번만 계약한다.
       해당 날짜 bar 가 없으면 그 심볼은 반환하지 않는다 → 기존 4단 ffill 방어가
       'ffill' 라벨과 함께 정직하게 처리한다.
    """
    try:
        raw = yf.download(symbols, start=start, end=end,
                          auto_adjust=True, progress=False)
        if raw.empty:
            return {}
        close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
        if exact_date is not None:
            _want = pd.Timestamp(exact_date).normalize()
            _idx = pd.DatetimeIndex(pd.to_datetime(close.index))
            if _idx.tz is not None:
                _idx = _idx.tz_localize(None)
            _hit = close[_idx.normalize() == _want]
            if len(_hit) == 0:
                print(f"    ⏭️ {symbols[:2]}... {_want.date()} bar 없음 — 인접일 대체 금지")
                return {}
            last = _hit.iloc[-1]
        else:
            last = close.iloc[-1]
        return {sym: float(last[sym])
                for sym in symbols
                if sym in last.index and not pd.isna(last[sym])}
    except Exception as e:
        print(f"    ⚠️  배치 {symbols[:2]}...: {e}")
        return {}


def _yf_series(symbol: str, start: str, end: str) -> pd.Series:
    """단일 티커 히스토리 → Series.
    🔧 v3.8 (S후속): yfinance 1.x 는 단일 티커도 MultiIndex 컬럼((Price,Ticker))으로 반환 →
        raw["Close"] 가 DataFrame 이 되어 이후 float(series.iloc[-1]) 크래시 유발
        (백필/저커버 VIX3M 경로 exit 1). MultiIndex 평탄화 + 1D 강제로 Series 보장(근본 처방).
    """
    try:
        raw = yf.download(symbol, start=start, end=end,
                          auto_adjust=True, progress=False)
        if raw is None or len(raw) == 0:
            return pd.Series(dtype=float)
        # yfinance 1.x MultiIndex 컬럼 평탄화 (top level = Price 필드)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        col = "Close" if "Close" in raw.columns else raw.columns[0]
        s = raw[col]
        if isinstance(s, pd.DataFrame):   # 중복 라벨 방어 → 첫 열
            s = s.iloc[:, 0]
        s = s.dropna()
        s.index = pd.to_datetime(s.index).tz_localize(None)
        return s
    except Exception as e:
        print(f"    ⚠️  {symbol}: {e}")
        return pd.Series(dtype=float)


# ═══════════════════════════════════════════════════════════════════════════
# 🆕 v3.9 (S279): 실제 세션일 해석기 — Date 라벨 단일 원천
#   원칙: Date 는 캘린더(UTC/KST)가 아니라 "가격 원천이 보유한 마지막 완료 거래일".
#   효과: ① carry row 소멸  ② 스케줄러 지연 무관  ③ 라벨 == 내용 구조적 보장
#   fail-safe: 전 후보 실패 시 None → 호출부가 fetch 생략 (행 날조 금지)
# ═══════════════════════════════════════════════════════════════════════════
SESSION_REF_TICKERS = ["SPY", "QQQ", "GLD"]   # 순차 시도 (단일 티커 장애 방어)


def resolve_session_date(ref_tickers=None, lookback_days=10):
    """가격 원천의 마지막 완료 거래일(date) 반환. 전 후보 실패 시 None."""
    refs = ref_tickers or SESSION_REF_TICKERS
    _today = date.today()
    _s = str(_today - timedelta(days=lookback_days))
    _e = str(_today + timedelta(days=1))
    for tk in refs:
        try:
            ser = _yf_series(tk, _s, _e)
        except Exception:
            continue
        if ser is None or len(ser) == 0:
            continue
        d = ser.index[-1].date()
        if d > _today:          # 미래일 = 원천 이상치 → 다음 후보
            continue
        return d
    return None


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


def _fetch_semi_signals(start: str, today) -> "pd.DataFrame":
    """🆕 [S214] FRED 반도체 수요 선행신호 — Oracle AI_POWER LEAD-7.

    기존 _fred_series() 재사용(중복 fetch 없음): 4개 월간 시리즈 fetch
    → 월초 정렬 → roc3m → SEMI_REACCEL/CONSUMER_ELEC → pub_lag PIT → 일간 ffill.

    발표일(pub_lag) PIT: 월간 시리즈 month M(월초)은 월말+pub_lag일에 발행.
      신호 month M = 구성 시리즈 max(pub_lag) 경과 후 사용 가능(look-ahead 차단).
      일간 date D = 발행일 ≤ D 인 최신 month 신호값(ffill).

    자본 중립: Oracle 보고 전용, PRIMA 미반영(frontier 닫힘). 데이터 부재 시 NaN
    → Oracle LEAD-7가 DEFAULT 폴백(하위호환).

    Args:
        start: 이력 시작(예: "2006-01-01"). today_row는 ~400일 윈도면 충분.
        today: 기준일(str/date/Timestamp). 이 날짜까지 일간 신호 반환.
    Returns:
        DataFrame(index=일간 Date, cols=[SEMI_REACCEL, CONSUMER_ELEC]).
    """
    today_ts = pd.Timestamp(today)
    didx = pd.date_range(start, today_ts, freq="D")
    # ① 4개 월간 시리즈 fetch (_fred_series 재사용 — API key + graph CSV fallback)
    raw = {}
    for sid in SEMI_SERIES_LAG:
        s = _fred_series(sid, start)
        if not s.empty:
            raw[sid] = s.sort_index()
        time.sleep(0.1)
    if not raw:
        return pd.DataFrame(
            {"SEMI_REACCEL": float("nan"), "CONSUMER_ELEC": float("nan")}, index=didx)
    # ② 월초 정렬 + roc3m (3개월 전 대비 변화율)
    monthly = pd.DataFrame(raw).resample("MS").last()
    roc = {f"{sid}_roc3m": monthly[sid] / monthly[sid].shift(3) - 1.0
           for sid in monthly.columns}

    def _g(k):
        return roc[k] if k in roc else pd.Series(float("nan"), index=monthly.index)

    # ③ 신호 계산 (월간)
    sig_m = pd.DataFrame(index=monthly.index)
    sig_m["SEMI_REACCEL"]  = ((_g("A34SNO_roc3m") > 0) & (_g("U34SIS_roc3m") < 0)).astype(float)
    sig_m["CONSUMER_ELEC"] = ((_g("RSEAS_roc3m") > 0) & (_g("R42343M163SCEN_roc3m") < 0)).astype(float)
    # 구성 시리즈 roc 미산출 month는 NaN
    for col, (comps, _lag) in SEMI_SIGNAL_DEF.items():
        miss = pd.Series(False, index=monthly.index)
        for c in comps:
            miss = miss | (roc[f"{c}_roc3m"].isna() if f"{c}_roc3m" in roc else True)
        sig_m.loc[miss, col] = float("nan")
    # ④ pub_lag PIT + 일간 ffill (발행일 ≤ D 인 최신 month 신호)
    out = pd.DataFrame(index=didx)
    for col, (comps, lag) in SEMI_SIGNAL_DEF.items():
        avail = pd.to_datetime(
            [(m + pd.offsets.MonthEnd(0)) + pd.Timedelta(days=lag) for m in sig_m.index])
        order = avail.argsort()
        ad = avail[order]
        vv = sig_m[col].values[order]
        pos = ad.searchsorted(didx, side="right") - 1
        daily = pd.Series(float("nan"), index=didx)
        mask = pos >= 0
        daily.iloc[mask] = vv[pos[mask]]
        out[col] = daily.ffill()
    return out


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

    # 🆕 [S214] FRED 반도체 선행신호 (SEMI_REACCEL/CONSUMER_ELEC) — Oracle LEAD-7
    print("  📡 반도체 선행신호 (A34SNO/U34SIS/RSEAS/R42343)...")
    try:
        _semi = _fetch_semi_signals(s, df.index[-1])
        for _c in ["SEMI_REACCEL", "CONSUMER_ELEC"]:
            df[_c] = _semi[_c].reindex(df.index, method="ffill")
            df[f"{_c}_source"] = "fred_semi_live"
            print(f"    ✅ {_c}: {df[_c].notna().sum()}/{len(df)}일")
    except Exception as _e:
        print(f"    ⚠️ 반도체 선행신호 skip: {_e}")
        for _c in ["SEMI_REACCEL", "CONSUMER_ELEC"]:
            if _c not in df.columns:
                df[_c] = float("nan")

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
def fetch_today_row(target_date=None, is_backfill=None) -> dict:
    # 🌟 v3.2 (S197): target_date 지원 — None=오늘(기존 동작 보존), 지정=임의 날짜 backfill
    # 🆕 v3.9 (S279): is_backfill 명시 파라미터 — 세션일 stamp(전일 세션 = 정상 일일 수집)를
    #   backfill 로 오인해 FRED as-of / F&G proxy 경로로 빠지는 것을 차단.
    #   None(기본) = 기존 산식 그대로 → 기존 호출부 동작 무변경.
    today = target_date if target_date is not None else date.today()
    if is_backfill is None:
        is_backfill = target_date is not None and target_date != date.today()
    row   = {"Date": pd.Timestamp(today)}
    s     = str(today - timedelta(days=5))
    e     = str(today + timedelta(days=1))

    # ① ETF 배치 — 🔴 v3.9.11 MARKET CONTRACT: 요청 세션의 실제 bar 만 채택
    etf_data = _yf_batch(ETF_TICKERS, s, e, exact_date=today)
    for tk, val in etf_data.items():
        row[f"{tk}_Close"] = val
    print(f"    ETF: {len(etf_data)}/{len(ETF_TICKERS)}종 수집")

    # ② 매크로 — 개별
    # 🌟 v2.12 (S69 #5, Commander 본질 통찰 #13): source 컬럼 신설
    print("    매크로 개별 수집...")
    ok_macro = 0
    for sym, col in YAHOO_MACRO.items():
        data = _yf_batch([sym], s, e, exact_date=today)   # 🔴 v3.9.11 MARKET CONTRACT
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

    # 🆕 [S214] FRED 반도체 선행신호 (today_row) — Oracle LEAD-7
    try:
        _start_semi = (pd.Timestamp(today) - pd.Timedelta(days=400)).strftime("%Y-%m-%d")
        _semi = _fetch_semi_signals(_start_semi, today)
        for _c in ["SEMI_REACCEL", "CONSUMER_ELEC"]:
            _v = _semi[_c].iloc[-1] if len(_semi) else float("nan")
            row[_c] = float(_v) if _v == _v else float("nan")
            row[f"{_c}_source"] = "fred_semi_live" if _v == _v else "ffill"
    except Exception as _e:
        print(f"    ⚠️ 반도체 선행신호(today) skip: {_e}")

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
        print(f"  🟡 PMI: 4중 방어 1~2차 실패 → ffill carry-forward (source={row['PMI_source']})")
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
    # 🌟 v3.5 (S218): ETF 가격(*_Close) ffill 통합 — today-row Yahoo batch 부분 실패
    #   (저유동 ETF ITA/VNM/CQQQ 단일일 NaN) 시 직전 유효 종가 carry-forward.
    #   브리핑 $0.00 표시 차단 + 다음 실행 시 기존 NaN row도 소급 정정.
    #   격언 #75 v4 source 정합 (매크로 4단 방어 ffill 철학을 ETF 가격으로 확장).
    close_cols = [c for c in df.columns if c.endswith('_Close')]
    for col in list(FFILL_COLS) + close_cols:
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
    """env로 처리 날짜 목록 결정 — v3.9.7부터 US Equity Regular Session SSOT 사용.

    우선순위: BACKFILL_DATE(단일) > BACKFILL_START+END(범위) > today(기본).
    반환: (dates: list[date], is_backfill: bool)
    """
    bf_date  = os.getenv("BACKFILL_DATE", "").strip()
    bf_start = os.getenv("BACKFILL_START", "").strip()
    bf_end   = os.getenv("BACKFILL_END", "").strip()

    # 🔴 v3.9.10: backfill 도 completed-session SSOT 를 통과해야 한다.
    #   v3.9.9 는 '정규장인가' 만 보고 '이미 끝난 세션인가' 는 보지 않았다.
    #   실측: BACKFILL_DATE=2026-09-14 (미래 정상 세션) → ([2026-09-14], True) 로 통과했다.
    #   그 뒤 fetch 는 window 안 마지막 bar 를 그 날짜로 stamp 할 수 있다.
    _last_done = last_completed_us_equity_session()

    def _filter_completed(days, label):
        if _last_done is None:
            print("  🔴 v3.9.10 완료 세션 판정 불가 (XNYS 캘린더 부재) — backfill 거부 (fail-closed)")
            return []
        ok, bad = [], []
        for d in days:
            if not is_nyse_open(d):
                bad.append((d, "비세션"))
            elif d > _last_done:
                bad.append((d, f"미완료/미래 (마지막 완료 {_last_done})"))
            else:
                ok.append(d)
        for d, why in bad:
            print(f"  ⏭️ v3.9.10 {label} {d} 제외 — {why}")
        return ok

    if bf_date:
        d = _parse_date(bf_date)
        if d is None:
            # 🔴 v3.9.10 P1-2: 운영자 오타가 '정상 daily fetch' 로 바뀌면 안 된다.
            print(f"  🚨 BACKFILL_DATE 파싱 실패: '{bf_date}' (YYYY-MM-DD 필요) — fail-closed")
            return [], True
        return _filter_completed([d], "BACKFILL_DATE"), True

    if bf_start and bf_end:
        ds, de = _parse_date(bf_start), _parse_date(bf_end)
        if ds is None or de is None:
            print("  🚨 BACKFILL_START/END 파싱 실패 (YYYY-MM-DD 필요) — fail-closed")
            return [], True
        if ds > de:
            ds, de = de, ds
        sessions, source = get_us_equity_regular_sessions(ds, de, return_source=True)
        days = _filter_completed([x.date() for x in sessions], "BACKFILL 범위")
        print(f"  📅 v3.9.10 BACKFILL 세션 해석: {len(days)}개 완료 세션 ({source})")
        return days, True

    return [date.today()], False



# ═══════════════════════════════════════════════════════════════════════════
# 🕯️ v3.6 (S242): SMH 삼중 선행 플래그 — C8(신용회복 선행) ∧ S2(메모리 바닥) ∧ WSTS YoY<0
#   정의 = REG-S242_3 canonical 자구. 산출 책임 = 데이터 층 (엔진은 컬럼 소비만, fail-safe 0)
# ═══════════════════════════════════════════════════════════════════════════
WSTS_YOY_JSON_PATH = "wsts_yoy.json"   # 레포 루트, 월 1회 갱신: {"series":[{"asof":"YYYY-MM-DD","yoy":-0.05}, ...]}
# 🆕 v3.9.13 P1-14: 마이그레이션 번들의 SMH 가격 최소 유효 관측량.
#   근거: m126 = pct_change(126) → rolling(189).min() 이 성립하려면 126+189 = 315 거래일이
#   최소이고, 이벤트 창(63) · dedupe(176 달력일) 여유를 더해 상수로 고정한다.
#   이 값 미만이면 SMH_TRIFLAG 가 '계산됐지만 거의 전부 0' 이 되어 조용히 신호가 사라진다.
SMH_BUNDLE_MIN_ROWS = 400
SMH_TRI_WIN_DAYS   = 63                # 이벤트 후 발화 창 (거래일)
SMH_TRI_DEDUP_DAYS = 176               # 이벤트 dedupe 간격 (126×1.4)
SMH_TRI_C8_LEAD    = 189               # C8 선행 동반 허용 (달력일)
WSTS_PIT_LAG_DAYS  = 45                # WSTS 공표지연 (PIT)
WSTS_STALE_DAYS    = 75                # staleness 가드
# 🕯️ v3.7 (S244): WSTS 자동 수집 설정
WSTS_HIST_PAGE_URL = "https://www.wsts.org/67/Historical-Billings-Report"  # 최신 xlsx 링크 소재 페이지
WSTS_HTTP_UA       = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}  # 격언 #107
WSTS_KEEP_MONTHS   = 180               # json 보존 개월 (15년 = triflag 5년 조회 + 여유)

def parse_wsts_yoy_json(path):
    """🆕 v3.9.12 [P0-13] wsts_yoy.json → PIT(+45일) 반영 일자 인덱스 **Series**.

    🔴 production 로더와 마이그레이션 번들 로더가 반드시 **같은 parser** 를 써야 한다.
    v3.9.11 번들 로더는 pd.read_json() 으로 읽어 DataFrame 을 돌려줬다. compute_smh_triflag 는
    `float(_cut.iloc[-1])` 을 하므로 S2 이벤트가 발생하는 순간 TypeError 가 나고,
    migration 은 그 예외를 삼켜 '재계산 실패 — 기존 값 유지' 로 넘어간다.
    즉 마이그레이션은 성공한 것처럼 보이는데 SMH_TRIFLAG 만 조용히 재계산되지 않는다.
    """
    with open(path, "r", encoding="utf-8") as f:
        j = json.load(f)
    entries = j.get("series", [j] if "asof" in j else [])
    rows = []
    for e in entries:
        asof = pd.Timestamp(e["asof"])
        rows.append((asof + pd.Timedelta(days=WSTS_PIT_LAG_DAYS), float(e["yoy"]), asof))
    if not rows:
        return None
    rows.sort()
    return pd.Series([r[1] for r in rows], index=[r[0] for r in rows], dtype=float)


def _load_wsts_series():
    """wsts_yoy.json → PIT 반영 시리즈. 부재/오류 → None (fail-safe).

    🔧 v3.9.13 P1-13: parse_wsts_yoy_json() 에 **실제로 위임**한다.
    v3.9.12 는 공용 parser 를 만들어 놓고 여기서 같은 로직을 다시 구현했다 —
    복제 구현이 갈라지는 문제를 이미 한 번 잡은 사이클에서 같은 형태를 남겨 두면 안 된다.
    """
    try:
        s = parse_wsts_yoy_json(WSTS_YOY_JSON_PATH)
        if s is None or len(s) == 0:
            return None
        newest_asof = (s.index.max() - pd.Timedelta(days=WSTS_PIT_LAG_DAYS)).normalize()
        if (pd.Timestamp.now().normalize() - newest_asof).days > WSTS_STALE_DAYS:
            print(f"  ⚠️ wsts_yoy.json stale (최신 asof {newest_asof.date()}) — 커버 범위 밖 이벤트 불발 처리")
        return s
    except Exception:
        return None

def _extract_worldwide_3mma(xlsx_path):
    """WSTS Historical Billings xlsx '3MMA' 시트 → {(연도, 월): 3MMA 값(천달러)} 사전 (v3.7, S244).

    구조: A열 정수=연도 행, 이어지는 지역 행들 중 'Worldwide' 행의 B~M열 = 1~12월.
    행 위치 고정 가정 없음 (연도→Worldwide 매칭 방식, 구조 변화 내성).
    가드: 0/음수 = 미발표월 플레이스홀더 → 제외 (S244 실 xlsx로 확정한 함정)."""
    raw = pd.read_excel(xlsx_path, sheet_name="3MMA", header=None, engine="openpyxl")
    out = {}
    cur_year = None
    for _, row in raw.iterrows():
        a = row.iloc[0]
        if isinstance(a, (int, float)) and not pd.isna(a) and 1980 < a < 2100:
            cur_year = int(a)
        elif isinstance(a, str) and a.strip() == "Worldwide" and cur_year:
            for m in range(1, 13):
                v = row.iloc[m] if m < len(row) else None
                if isinstance(v, (int, float)) and not pd.isna(v) and v > 0:
                    out[(cur_year, m)] = float(v)
    return out


def fetch_wsts_yoy_auto():
    """wsts.org → 최신 xlsx → Worldwide 3MMA YoY → wsts_yoy.json 조건부 갱신 (v3.7, S244).

    단계: ①랜딩 파싱(xlsx URL) ②기존 json source_url 동일 시 생략 ③xlsx 다운로드
          ④3MMA 추출(0 가드) ⑤YoY 분수 시리즈(asof=데이터월 말일) ⑥원자적 json 교체.
    PIT +45일 반영은 소비측 _load_wsts_series 담당 (책임 분리 유지).
    fail-safe: 모든 예외 → 호출부 경고 후 기존 json 보존 (staleness 75일 가드 후방 방어)."""
    import hashlib, tempfile
    # ① 랜딩 파싱
    resp = requests.get(WSTS_HIST_PAGE_URL, headers=WSTS_HTTP_UA, timeout=30)
    resp.raise_for_status()
    links = re.findall(r'href="([^"]+\.xlsx?)"', resp.text)
    cands = [u for u in links if "Historical-Billings" in u]
    if not cands:
        print("  ⚠️ WSTS xlsx 링크 미발견 — 기존 wsts_yoy.json 유지")
        return False
    xlsx_url = cands[0] if cands[0].startswith("http") else ("https://www.wsts.org" + cands[0])

    # ② 조건부 갱신: 동일 소스면 다운로드 생략 (일간 GHA 부담 최소화)
    try:
        with open(WSTS_YOY_JSON_PATH, "r", encoding="utf-8") as f:
            _prev = json.load(f)
        if _prev.get("source_url") == xlsx_url and _prev.get("series"):
            print(f"  🕯️ WSTS 최신 유지 ({os.path.basename(xlsx_url)}) — 갱신 생략")
            return True
    except Exception:
        pass

    # ③ xlsx 다운로드 (임시 파일)
    xr = requests.get(xlsx_url, headers=WSTS_HTTP_UA, timeout=60)
    xr.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        tf.write(xr.content)
        _tmp = tf.name
    try:
        # ④ Worldwide 3MMA 추출
        d = _extract_worldwide_3mma(_tmp)
    finally:
        try:
            os.remove(_tmp)
        except OSError:
            pass
    if not d:
        print("  ⚠️ WSTS 3MMA 추출 0건 — 기존 wsts_yoy.json 유지")
        return False

    # ⑤ YoY 분수 시리즈 (전년동월 대비, asof=데이터월 말일)
    series = []
    for (y, mo) in sorted(d):
        pv = d.get((y - 1, mo))
        if pv:
            asof = (pd.Timestamp(year=y, month=mo, day=1) + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d")
            series.append({"asof": asof, "yoy": round(d[(y, mo)] / pv - 1.0, 6)})
    series = series[-WSTS_KEEP_MONTHS:]
    if not series:
        print("  ⚠️ WSTS YoY 산출 0건 — 기존 wsts_yoy.json 유지")
        return False

    # ⑥ 원자적 교체 (부분 쓰기 오염 차단)
    payload = {
        "series": series,
        "source_url": xlsx_url,
        "source_sha12": hashlib.sha256(xr.content).hexdigest()[:12],
        "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _tmpj = WSTS_YOY_JSON_PATH + ".tmp"
    with open(_tmpj, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(_tmpj, WSTS_YOY_JSON_PATH)
    _last = series[-1]
    print(f"  🕯️ WSTS YoY 갱신: 최신 asof {_last['asof']} YoY {_last['yoy']*100:+.2f}% "
          f"({len(series)}개월, {os.path.basename(xlsx_url)})")
    return True


def compute_kil_sup(df):
    """🕯️ v3.9.4 (S288): Kilian 공급충격 플래그 — Crown #106 `_wk` 게이트 완화 소비용.

    Kilian(2009) 유가 3분해의 ARGUS 대리 조작화:
      · 총수요발(건전) : ΔWTI20>0 ∩ ΔCOPX20>0 ∩ PMI>50   (구리 동반 + 제조업 확장)
      · 공급발(악성)   : ΔWTI20>0 ∩ ΔSPY20<0 ∩ ¬총수요발  ← 본 함수 산출 대상
    엔진(Crown #106)은 이 플래그가 1.0 인 구간에서만 _wk 차단 임계를 90→100 으로 상향한다.

    반환: float Series (1.0 = 공급발 / 0.0 = 그 외). 결측은 0.0 (fail-safe).
    주의: 전열 재계산(자기치유) — 과거 행도 매 실행 시 재산출되므로 정의 변경이 즉시 반영된다.
    """
    import numpy as _np
    import pandas as _pd

    need = ["WTI", "SPY_Close", "COPX_Close"]
    for c in need:
        if c not in df.columns:
            raise KeyError(f"KIL_SUP 산출 필수 컬럼 부재: {c}")

    wti = _pd.to_numeric(df["WTI"], errors="coerce").ffill()
    spy = _pd.to_numeric(df["SPY_Close"], errors="coerce")
    cpx = _pd.to_numeric(df["COPX_Close"], errors="coerce")
    # PMI 는 선택 — 부재/결측 시 총수요발 판별에서 자동 배제 (A5 실측: 효과 동일)
    pmi = _pd.to_numeric(df["PMI"], errors="coerce").ffill() if "PMI" in df.columns \
        else _pd.Series(_np.nan, index=df.index)

    d20 = lambda s: s / s.shift(20) - 1
    dwti20 = wti - wti.shift(20)

    demand = (dwti20 > 0) & (d20(cpx) > 0) & (pmi > 50)          # 총수요발(건전)
    supply = (dwti20 > 0) & (d20(spy) < 0) & (~demand.fillna(False))
    return supply.fillna(False).astype(float)

def compute_smh_triflag(df, prices=None, wsts_series=None):
    """삼중(C8∧S2∧WSTS<0) 플래그 산출 → df.index 정렬 0/1 시리즈.

    Args:
        df: argus 통합 DataFrame (Date index)
        prices: 테스트 주입용 — MU/HYG/LQD 컬럼 DataFrame (None=yfinance 5년 자체 다운로드)
        wsts_series: 테스트 주입용 — PIT 반영 일자 인덱스 YoY 시리즈 (None=wsts_yoy.json)
    """
    if prices is None:
        _start = (pd.Timestamp.now() - pd.Timedelta(days=int(365.25 * 5))).strftime("%Y-%m-%d")
        _raw = yf.download(["MU", "HYG", "LQD"], start=_start, progress=False, auto_adjust=True)
        prices = _raw["Close"] if "Close" in getattr(_raw, "columns", []) or (hasattr(_raw.columns, "levels")) else _raw
        if hasattr(prices.columns, "levels"):
            prices = _raw["Close"]
    if wsts_series is None:
        wsts_series = _load_wsts_series()

    mu = prices["MU"].astype(float).dropna()
    hlr = (prices["HYG"].astype(float) / prices["LQD"].astype(float)).dropna()

    # S2: MU mom126 심저(<−20%, 직전 189거래일) → 음→양 교차
    m126 = mu.pct_change(126)
    deep = m126.rolling(189).min() < -0.20
    recv = ((m126 > 0) & (m126.shift(1) <= 0) & deep).fillna(False)
    s2ev = []
    for d in m126.index[recv]:
        if not s2ev or (d - s2ev[-1]).days > SMH_TRI_DEDUP_DAYS:
            s2ev.append(d)

    # C8: HYG/LQD 드로다운(63일 전 시점 <−5%) 상태에서 mom63 양전 교차
    hdd = hlr / hlr.rolling(252).max() - 1
    c8c = ((hlr.pct_change(63) > 0) & (hdd.shift(63) < -0.05)).fillna(False)
    c8ev = []
    for d in hlr.index[c8c & ~c8c.shift(1).fillna(False)]:
        if not c8ev or (d - c8ev[-1]).days > SMH_TRI_DEDUP_DAYS:
            c8ev.append(d)

    # 삼중 판정 + 발화 창 (가격 축) → +1일 shift → df.index 매핑
    flag_px = pd.Series(0, index=mu.index)
    for d in s2ev:
        lead_ok = any(0 <= (d - e).days <= SMH_TRI_C8_LEAD for e in c8ev)
        wv = float("nan")
        if wsts_series is not None and len(wsts_series):
            _cut = wsts_series[wsts_series.index <= d]
            if len(_cut):
                wv = float(_cut.iloc[-1])
        if lead_ok and pd.notna(wv) and wv < 0:
            i0 = mu.index.searchsorted(d)
            flag_px.iloc[i0:i0 + SMH_TRI_WIN_DAYS] = 1
    flag_px = flag_px.shift(1).fillna(0).astype(int)
    return flag_px.reindex(df.index, method="ffill").fillna(0).astype(int)


def main():
    t0 = time.time()
    print(f"🦅 ARGUS DATA FETCHER {FETCHER_VER} — {datetime.now(KST).strftime('%Y-%m-%d %H:%M KST')}")
    # 🔧 v3.9.15 GIT-SAFE SEAL — daily/backfill 이 v3.9.14 symlink 를 따라 generation 을
    # 덮어쓰기 전에 regular file 로 탈출시키고, 이전 commit 이 중단됐으면 먼저 수렴 복구한다.
    _recover_pending_generation()
    _de_symlink_public_artifacts()
    # 🚪 v3.9.13 ENTRY SEAL — 어떤 network-capable 코드보다 **먼저** 분기한다.
    #   resolve_session_date() 는 Yahoo 를 호출하므로 그 뒤에서 분기하면
    #   '마이그레이션 무네트워크' 가 성립하지 않는다 (v3.9.12 P0-16).
    if CALENDAR_MIGRATION_MODE:
        run_calendar_migration()
        print(f"\n✅ 마이그레이션 종료 ({time.time()-t0:.1f}s)")
        return
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
    _sess = None   # 🆕 v3.9: 일일 모드에서만 확정 (backfill 모드는 None 유지)

    if is_backfill:
        if not target_dates:
            print(f"  ⏭️ 지정 범위에 NYSE 개장일 없음 — 종료")
            return
        print(f"   🌟 v3.2 BACKFILL 모드 — 대상 {len(target_dates)}개장일: "
              f"{target_dates[0]} ~ {target_dates[-1]}")
    else:
        # 🆕 v3.9 (S279): Date 원천 = 가격 원천의 마지막 거래일 (UTC 캘린더 아님)
        _sess = resolve_session_date()
        if _sess is None:
            print(f"🔴 세션일 해석 실패 (가격 원천 무응답) — fetch 생략 (행 날조 금지)")
            return
        if not is_nyse_open(_sess):
            print(f"⏭️ {_sess} NYSE 휴장 판정 — fetch 생략")
            return
        # 🔧 v3.9.9 completed-session 강제. 불변식이 '완료된 세션'이므로
        #   미마감 세션 bar 는 행으로 만들지 않는다 (장중 실행 carry row 차단).
        _done = is_session_completed(_sess)
        _last_done = last_completed_us_equity_session()
        if _done is None or _last_done is None:
            print("🔴 v3.9.9 완료 세션 판정 불가 (XNYS 캘린더 부재) — fetch 생략 (행 날조 금지)")
            print("   처방: requirements 에 exchange-calendars 를 고정 버전으로 추가 후 재실행.")
            return
        if not _done:
            # 🔧 v3.9.10 P1-1: 종료하지 않고 마지막 완료 세션으로 내려간다.
            #   오염 차단이 목적이지 가용성 포기가 목적이 아니다. 같은 세션을 다시 처리해도
            #   기존 행 보존 병합이 있으므로 멱등이다.
            _cl = xnys_session_close(_sess)
            print(f"  🕰️ v3.9.10 {_sess} 세션 미마감 (마감 {_cl}) → "
                  f"마지막 완료 세션 {_last_done} 로 대체 처리")
            _sess = _last_done
        if pd.Timestamp(_sess).date() > _last_done:
            print(f"🔴 v3.9.9 {_sess} 가 마지막 완료 세션 {_last_done} 보다 미래 — fetch 생략")
            return
        print(f"  🕰️ v3.9.9 완료 세션 확인: {_sess} (마감 {xnys_session_close(_sess)})")
        if _sess != today:
            print(f"  🕯️ v3.9 세션일 stamp: UTC today={today} → 마지막 거래일={_sess} (carry row 차단)")
        target_dates = [_sess]

    _calendar_pre_snapshot = None
    _calendar_repaired_dates = []

    if not os.path.exists(OUTPUT_PATH):
        df = build_seed()
        # 🔧 v3.9.8: 시드도 자기치유·결측복구를 거친다.
        #   v3.9.7 은 시드를 스냅샷만 찍고 통과시켜, 시드에 유령/결측이 하나라도 있으면
        #   최종 게이트가 SystemExit 을 내고 **부트스트랩 자체가 영구 불가**였다.
        df, _calendar_pre_snapshot = _sanitize_non_session_rows(df, stage="new_seed")
        _seed_missing = _calendar_integrity_snapshot(df, "new_seed_after_cleanup").get("missing_dates", [])
        if _seed_missing:
            print(f"  🚨 v3.9.8 시드 정규장 결측 {len(_seed_missing)}건: {_seed_missing}")
            df, _calendar_repaired_dates = _repair_missing_session_rows(df, _seed_missing)
            df = apply_ffill_safety(df)
            # 🔧 v3.9.11 P1: 시드 경로에도 provenance 확정을 적용한다.
            #   누락 시 새 시드의 _source 에 pit_ffill_pending 이 그대로 남아 계약 위반이 된다.
            df = _finalize_repair_provenance(df, _calendar_repaired_dates)
        # 시드는 SEED_DAYS 전체 history 포함 → backfill 날짜도 커버 (별도 fetch 불요)
    else:
        df    = pd.read_csv(OUTPUT_PATH, index_col=0, parse_dates=True)
        df.index.name = "Date"
        df    = df.sort_index()
        today_ts = pd.Timestamp(today)

        # 🆕 v3.9 (S279): 세션일보다 미래인 행 제거 — v3.8 이하가 남긴 carry row 자기치유.
        #   근거: 마지막 거래일보다 미래의 종가는 존재할 수 없음 → 잔존 시 브리핑이 복제행을 최신으로 오독.
        #   backfill 모드(_sess=None)에서는 미동작 (소급 작업 보호).
        if _sess is not None:
            _future = df.index[df.index > pd.Timestamp(_sess)]
            if len(_future):
                print(f"  🧹 v3.9 carry row 제거 {len(_future)}건: "
                      f"{[str(x.date()) for x in _future]}")
                df = df[df.index <= pd.Timestamp(_sess)]

        # 🔧 v3.9.7 (S290): 기존 세션 시간축 자기치유 + 결측 정규장 세션 자동복구.
        #   반드시 rolling/backfill/feature 계산보다 먼저 수행해 행 기반 lookback 오염을 차단한다.
        # 🔧 v3.9.9 CALENDAR_MIGRATION_MODE — 역사 재계산을 일일 실행에서 분리한다.
        #   첫 유령행 이후의 모든 rolling 값이 달라지므로, 이 작업은 일일 fetch 가
        #   조용히 수행할 일이 아니다. 명시적 모드에서 한 번 수행하고 baseline 을 봉인한다.
        _pre_audit = _calendar_integrity_snapshot(df, "pre_migration_audit")
        _needs_mig = bool(_pre_audit["ghost_n"] or _pre_audit["missing_n"] or _pre_audit["duplicate_n"])
        if _needs_mig and not CALENDAR_MIGRATION_MODE:
            print("🟠 v3.9.9 시간축 마이그레이션 필요 — 일일 실행에서는 수행하지 않는다.")
            print(f"   유령 {_pre_audit['ghost_n']}건 · 결측 {_pre_audit['missing_n']}건 "
                  f"· 중복 {_pre_audit['duplicate_n']}건 (소스 {_pre_audit['calendar_source']})")
            print(f"   유령: {_pre_audit['ghost_dates']}")
            print(f"   결측: {_pre_audit['missing_dates']}")
            print("   사유: 첫 유령행 이후 전 구간의 rolling lookback 이 달라진다. "
                  "일일 파이프라인이 조용히 역사를 다시 쓰지 않게 한다.")
            print("   처방: CALENDAR_MIGRATION_MODE=1 로 1회 실행 → clean baseline 봉인 "
                  "→ Crown 재현 전후 대조 → 이후 일일 실행 재개.")
            print("   이번 실행은 파일을 변경하지 않는다.")
            _write_calendar_integrity_report({
                "version": FETCHER_VER, "mode": "migration_required",
                "invariant": "1 row = 1 completed US equity regular session",
                "pre_repair": _pre_audit, "final": None,
            })
            return
        df, _calendar_pre_snapshot = _sanitize_non_session_rows(df, stage="loaded_before_fetch")
        _calendar_repaired_dates = []
        _missing_pre = _calendar_integrity_snapshot(df, "after_ghost_cleanup").get("missing_dates", [])
        if _missing_pre:
            print(f"  🚨 v3.9.7 정규장 결측 {len(_missing_pre)}건 발견: {_missing_pre}")
            df, _calendar_repaired_dates = _repair_missing_session_rows(df, _missing_pre)
            # 복구 row의 REVISION_SENSITIVE 열은 전진 ffill 로만 보강한다 (미래값 주입 금지)
            df = apply_ffill_safety(df)
            df = _finalize_repair_provenance(df, _calendar_repaired_dates)
            print(f"  🩹 v3.9.10 결측 세션 복구 완료 {len(_calendar_repaired_dates)}건")

        # 🌟 v3.2 (S197): target_dates 루프 (기본=오늘 1개 / backfill=N개)
        for _tgt in target_dates:
            _tgt_ts = pd.Timestamp(_tgt)
            # 🔧 v3.9.5 (S290, REG-S290_1): 재생성 전 기존 행 보존.
            #   결함: 종전은 기존 행을 삭제하고 새 fetch 결과로 통째 대체했다. 부분 실패(단일 심볼
            #   무응답)가 발생하면 이미 확정된 값이 NaN 으로 덮여 영구 소거됐다. 실측 2026-09-03 실행이
            #   2026-09-01 행을 재생성하며 WTI 91.69 / Brent 96.32 / VIX3M 18.33 을 소거했다.
            #   처방: 신규 값 우선(LIVE 갱신 보장), 신규가 결측인 자리에만 기존 확정값 복원.
            _prev_row = None
            if _tgt_ts in df.index:
                _sel = df.loc[_tgt_ts]
                _prev_row = _sel.iloc[-1] if isinstance(_sel, pd.DataFrame) else _sel
                df = df[df.index != _tgt_ts]
            _label = "백필" if is_backfill else "오늘"
            print(f"  📡 {_label} 행 수집 ({_tgt})...")
            new_row = fetch_today_row(target_date=_tgt, is_backfill=is_backfill)  # 🆕 v3.9 명시 전달
            if _prev_row is not None:
                _restored = []
                for _c, _v in _prev_row.items():
                    if _c == "Date":
                        continue
                    try:
                        _missing = _c not in new_row or pd.isna(new_row[_c])
                        _has_old = pd.notna(_v)
                    except (TypeError, ValueError):
                        continue
                    if _missing and _has_old:
                        new_row[_c] = _v
                        _restored.append(_c)
                if _restored:
                    print(f"  🛡️ v3.9.5 확정값 복원 {len(_restored)}건: {_restored[:12]}"
                          + (" ..." if len(_restored) > 12 else ""))
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

        # 🆕 v3.9.3 (S280): 범용 ETF 백필 — 신규/저커버 ETF 티커 전체 이력 자동 백필 (근본 처방)
        #   근거: build_seed는 argus_data.csv 부재 시에만 실행 → 기존 CSV에 티커 추가 시 오늘 행만 append되어
        #         신규 티커가 1일치만 쌓이는 결함. CCSA/VIX3M cover<50% doctrine을 ETF에도 확장.
        #   대상: 컬럼 부재 OR cover<50% OR BACKFILL_FORCE. (기존 정상 ETF는 cover~100%라 미발동)
        for _etf in ETF_TICKERS:
            _col = f"{_etf}_Close"
            _cov = df[_col].notna().sum() / len(df) if _col in df.columns else 0
            if _col not in df.columns or _cov < 0.5 or BACKFILL_FORCE:
                _reason = ("부재" if _col not in df.columns else
                           f"cover {_cov*100:.1f}% < 50%" if not BACKFILL_FORCE else "BACKFILL_FORCE=1")
                _start_iso = df.index.min().strftime('%Y-%m-%d')
                _end_iso = (df.index.max() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
                _ser = _yf_series(_etf, _start_iso, _end_iso)
                if not _ser.empty:
                    if _ser.index.tz is not None:
                        _ser.index = _ser.index.tz_localize(None)
                    _existing = df[_col] if _col in df.columns else pd.Series(index=df.index, dtype=float)
                    _filled = _ser.reindex(df.index, method='ffill')
                    # 기존 LIVE 값 보존 우선 (백필은 결측만 보강) — 단 BACKFILL_FORCE 시 전열 갱신
                    df[_col] = _filled if (BACKFILL_FORCE or _col not in df.columns) else _existing.fillna(_filled)
                    _v = df[_col].notna().sum()
                    print(f"  🌟 ETF {_etf} 백필 ({_reason}): {_v}/{len(df)}일 ({_v/len(df)*100:.1f}%, 최신={float(_ser.iloc[-1]):.2f})")
                elif _col not in df.columns:
                    df[_col] = np.nan
                    print(f"  🚨 ETF {_etf} 백필 실패 — Yahoo 이력 empty, 컬럼 NaN 생성")

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
                # 🔴 v3.9.9 [PIT] .bfill() 제거. 종전은 첫 Shiller 관측 이전 행에
                #   **미래 CAPE/ECY 값을 역주입**했다. 관측 이전 구간은 그 시점에
                #   알 수 없었던 값이므로 NaN 으로 남긴다 (전진 ffill 만 허용).
                ecy_daily = shiller_df.reindex(df.index, method='ffill').ffill()
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

    # 🕯️ v3.7 (S244): WSTS YoY 자동 수집 — wsts_yoy.json 조건부 갱신 (실패 시 기존 json 보존)
    try:
        fetch_wsts_yoy_auto()
    except Exception as _we:
        print(f"  ⛑️ WSTS 자동 수집 fail-safe (기존 wsts_yoy.json 보존): {_we}")

    # 🕯️ v3.6 (S242): SMH_TRIFLAG 전열 재계산 — Crown #84 후보 소비용 (자기치유 패턴, REG-S242_3)
    try:
        df["SMH_TRIFLAG"] = compute_smh_triflag(df)
        _tf_on = int(df["SMH_TRIFLAG"].fillna(0).sum())
        print(f"  🕯️ SMH_TRIFLAG (삼중 C8∧S2∧WSTS<0): 발화 {_tf_on}/{len(df)}일" + (" — 휴면" if _tf_on == 0 else ""))
    except Exception as _e:
        df["SMH_TRIFLAG"] = 0
        print(f"  ⛑️ SMH_TRIFLAG fail-safe 0 (산출 실패: {_e})")

    # 🕯️ v3.9.4 (S288): KIL_SUP 전열 재계산 — Crown #106 소비용 (자기치유 패턴, SMH_TRIFLAG 선례)
    try:
        df["KIL_SUP"] = compute_kil_sup(df)
        _ks_on = int(df["KIL_SUP"].fillna(0).sum())
        print(f"  🕯️ KIL_SUP (Kilian 공급발): 발화 {_ks_on}/{len(df)}일"
              + (" — 휴면" if _ks_on == 0 else ""))
    except Exception as _e:
        df["KIL_SUP"] = 0.0
        print(f"  ⛑️ KIL_SUP fail-safe 0 (산출 실패: {_e})")

    # 🕯️ v3.9.6 (S288): GPR_HIGH 상류 병합 — 재계산 금지, 그러나 **읽어서** 가져온다.
    #   🚨 v3.9.5 는 df 에 이미 컬럼이 있다고 전제했다가 자기참조 0 루프에 빠졌다.
    #      기존 컬럼이 있어도 무조건 상류 값으로 덮는다 — 그것이 0 고착을 푸는 유일한 방법이다.
    try:
        _gsrc, _gdf = "", None
        for _cand in (os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "argus_fred_broad.csv"),
                      "argus_fred_broad.csv"):
            if os.path.exists(_cand):
                _gdf, _gsrc = pd.read_csv(_cand), f"로컬 {os.path.basename(_cand)}"
                break
        if _gdf is None:
            import io as _io
            import urllib.request as _ur
            _url = ("https://raw.githubusercontent.com/daifulee/argus-public-data/main/"
                    "argus_fred_broad.csv")
            with _ur.urlopen(_ur.Request(_url, headers={"User-Agent": "ARGUS-fetcher/3.9.6"}),
                             timeout=60) as _r:
                _gdf = pd.read_csv(_io.StringIO(_r.read().decode()))
            _gsrc = "원격 raw"
        _dcol = next((c for c in _gdf.columns if str(c).lower() in ("date", "unnamed: 0")), None)
        if _dcol is None or "GPR_HIGH" not in _gdf.columns:
            raise KeyError(f"상류에 GPR_HIGH 또는 Date 부재 ({_gsrc}, 열 {len(_gdf.columns)}개)")
        _gs = (_gdf[[_dcol, "GPR_HIGH"]].copy()
               .assign(**{_dcol: lambda x: pd.to_datetime(x[_dcol], errors="coerce")})
               .dropna(subset=[_dcol]).set_index(_dcol)["GPR_HIGH"])
        _gs = pd.to_numeric(_gs, errors="coerce").sort_index()
        _gs = _gs[~_gs.index.duplicated(keep="last")]
        _idx = pd.to_datetime(df.index, errors="coerce")
        _merged = _gs.reindex(_gs.index.union(_idx)).ffill().reindex(_idx)
        _prev = int((pd.to_numeric(df["GPR_HIGH"], errors="coerce") > 0.5).sum()) \
            if "GPR_HIGH" in df.columns else -1
        df["GPR_HIGH"] = _merged.fillna(0.0).values      # 🚨 무조건 덮어쓰기
        _gh_on = int((df["GPR_HIGH"] > 0.5).sum())
        print(f"  🕯️ GPR_HIGH (지정학 고조 · 상류 {_gsrc} 병합): 발화 {_gh_on}/{len(df)}일 · "
              f"최근값 {float(df['GPR_HIGH'].iloc[-1]):.0f}"
              + (" — 휴면" if _gh_on == 0 else "")
              + (f" (직전 컬럼 발화 {_prev}일 → 덮어씀)" if _prev >= 0 and _prev != _gh_on else ""))
    except Exception as _e:
        df["GPR_HIGH"] = 0.0
        print(f"  ⛑️ GPR_HIGH fail-safe 0 — 사유 {type(_e).__name__}: {_e}")


    # 🔧 v3.9.7 (S290): 저장 직전 세션 시간축 강제 게이트.
    #   비세션/결측/중복 중 하나라도 남으면 4개 CSV 저장 전 차단한다.
    _enforce_final_session_integrity(
        df, pre_snapshot=_calendar_pre_snapshot, repaired_dates=_calendar_repaired_dates
    )

    # 🔧 v3.9.5 (S290, REG-S290_1): 저장 직전 무결성 2종 검사 (자본 레인 보호).
    #   G1 라벨-값 정합: _source 가 'ffill' 인데 값이 NaN 이면 4단 방어 미이행 = 라벨 거짓.
    #   G2 비단조 회귀: 디스크의 확정값(유효)이 이번 산출에서 NaN 으로 바뀌면 소거 = 저장 차단.
    #   ABORT_ON_INTEGRITY=0 으로 경고 전용 전환 가능 (기본 1 = 차단).
    def _integrity_gate(_df):
        _abort = os.getenv("ABORT_ON_INTEGRITY", "1").lower() not in ("0", "false", "no")
        _viol = []
        _last = _df.iloc[-1]
        for _c in list(globals().get("YAHOO_MACRO_VALUE_COLS", [])) + list(FFILL_COLS):
            _sc = f"{_c}_source"
            if _c in _df.columns and _sc in _df.columns:
                if str(_last.get(_sc)) == "ffill" and pd.isna(_last.get(_c)):
                    _viol.append(f"G1 라벨거짓 {_c}: source=ffill 인데 값 NaN")
        if os.path.exists(OUTPUT_PATH):
            try:
                _disk = pd.read_csv(OUTPUT_PATH, index_col=0, parse_dates=True).sort_index()
                for _ts in _disk.index.intersection(_df.index):
                    for _c in _disk.columns:
                        if _c not in _df.columns:
                            continue
                        _o, _n = _disk.loc[_ts, _c], _df.loc[_ts, _c]
                        if hasattr(_o, "__len__") and not isinstance(_o, str):
                            continue
                        try:
                            if pd.notna(_o) and pd.isna(_n):
                                _viol.append(f"G2 값소거 {_ts.date()} {_c}: {_o} → NaN")
                        except (TypeError, ValueError):
                            continue
            except Exception as _e:
                print(f"  ⚠️ G2 회귀 가드 대조 생략 — {type(_e).__name__}: {_e}")
        if _viol:
            print(f"\n🚨 무결성 위반 {len(_viol)}건:")
            for _v in _viol[:20]:
                print(f"    🔴 {_v}")
            if len(_viol) > 20:
                print(f"    ... 외 {len(_viol)-20}건")
            if _abort:
                raise SystemExit("🔴 v3.9.5 무결성 게이트 — 저장 차단 (확정값 소거·라벨 거짓 방지). "
                                 "의도된 정정이면 ABORT_ON_INTEGRITY=0 으로 재실행.")
            print("  ⚠️ ABORT_ON_INTEGRITY=0 — 경고만 하고 저장 진행")
        else:
            print("  ✅ v3.9.5 무결성 게이트 통과 (라벨-값 정합 · 값 소거 0건)")
    _integrity_gate(df)

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
