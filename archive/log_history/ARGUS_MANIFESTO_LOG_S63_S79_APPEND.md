# 📜 ARGUS MANIFESTO LOG — S63~S79#1 APPEND

**작성일**: 2026-05-11 (S80 #1 cleanup)
**범위**: S63 ~ S79 #1
**원본 마스터 인계**: ARGUS_MANIFESTO_LOG_MASTER_S46_S62.md
**§41 정합**: 풀파일 통합 (정보 손실 0)
**격언 #47 정합**: 본 APPEND가 S63~S79 MANIFESTO SSOT

## 📑 신규 격언 등재 매트릭스 (S63~S79)

| 격언 # | 등재일 | 본질 | 세션 |
|:--:|:--:|:--|:--:|
| 🌟 #96 v2 | S63 | 데이터 fetch 6단계 의무 (FRED→CSV→ALFRED→TradingView→첨부→한계) | S63 #4 |
| 🌟 #97 v2 | S63 | 자기 audit (12 패턴) + 외부 audit (조건부) | S63 #4 |
| 🌟 #98 | S63 | 결정 지연 ≠ 중립 (선택적 회피 차단) | S63 #4 |
| 🌟 #99~#105 | S65~S71 | (메모리 #25 등재 격언들, 세부는 master 통합 시) | S65~S71 |
| 🌟 **#106** | 🌟 **S71** | 🌟 **근본 처방 우선 (미봉책 차단), S71 5건 record** | S71 |
| 🌟 **#107** | 🌟 **S70** | 🌟 **GHA→외부API User-Agent 필수 (Cloudflare 1010 회피)** | S70 |
| 🌟 #108 | S71+ | (TBD) | S71+ |
| 🌟 **#109** | 🌟 **S79 #1** | 🌟 **BT 기간 SSOT (4기간 + STRESS 14 표준 인용 의무)** | S79 #1 |

## 📑 통합 인덱스 (3건)

| # | 파일 | 본질 | 세션 |
|:--:|:--|:--|:--:|
| 1 | REG-S69_BRIEFING_OVERWRITE | briefing 덮어쓰기 본질 정합 | S69 |
| 2 | REG-S76_PROTOCOL_D_METHOD | Protocol D 방법론 정식 등재 | S76 |
| 3 | ARGUS_AXIOM_107_GHA_USER_AGENT | 격언 #107 GHA User-Agent 정식 본문 | S70 |

---


═══════════════════════════════════════════════════════════════════
# 📦 REG-S69_BRIEFING_OVERWRITE (원본 풀파일)
═══════════════════════════════════════════════════════════════════

# 🚨 REG-S69_BRIEFING_OVERWRITE — prima_briefing.py 본문 덮어쓰기 사고

**세션**: S69 #3
**일시**: 2026-05-08 KST
**본질 결정**: 결정적 단일 root cause + 즉시 복구 결정적 성공
**격언 정합**: #36 #1 + #75 v4 + #80 + #94 + #97 v2 #1 + #98 + #105 + 5조 ⑤

---

## 1. 사고 본질

### 1.1 사고 발생 영역

🚨 **2026-05-08 S69 #3 사고**:

| 영역 | 본질 |
|:---|:---|
| 작업 | argus_data_fetcher.py v2.10 GitHub UI 업로드 |
| 사고 | prima_briefing.py 자리에 fetcher v2.10 본문 덮어쓰기 |
| 결과 | Discord 미발송 결정적 본질 |
| 발견 | LIVE Actions logs Step 4 6.8s = fetcher 재실행만 (prima_briefing 자체 출력 부재) |
| 단일 root cause | URL 명확화 부재 + 헤더 라벨 사전 검증 부재 |

### 1.2 LIVE Actions logs 결정적 증거

```
Run python prima_briefing.py
🦅 ARGUS DATA FETCHER v2.10 — 2026-05-08 12:09 KST  ← 🚨 fetcher 헤더!
   FRED_API_KEY: ✅ 설정됨
   ...
✅ 저장 완료 (6.8s)  ← 🚨 fetcher 본문 종료
[로그 종료]                                    ← 🚨 prima_briefing 자체 출력 완전 부재
```

본질: prima_briefing.py 파일 = fetcher v2.10 본문 (잘못된 업로드)
→ Step 4 = fetcher 재실행 + Discord 발송 logic 자체 부재

### 1.3 Commander 업로드 v6.8.39 본문 검증

Commander가 다음턴에 v6.8.39 본문 첨부 → 실제 본문 분석:

```
헤더: 🦅 ARGUS DATA FETCHER v2.10 — F&G 4중 방어 source 신설 (S69 #2, 2026-05-08)
함수: _fetch_ism_pmi_dbnomics_series, _fetch_pmi_tradingeconomics, _fetch_fg_cnn_api 등
prima_briefing 본질 함수 (load_data, run_prima, send_discord 등) 완전 부재
라인 수: 1,358 (fetcher v2.10과 동일)
```

→ **prima_briefing.py 파일이 fetcher v2.10 본문으로 덮어써짐 결정적 입증**

---

## 2. 본질 단일 root cause

### 2.1 결정적 본질

**Claude 누락 인정 #31 (역대 가장 결정적)**:

| 영역 | 누락 |
|:---|:---|
| GitHub UI 업로드 절차 안내 시 URL 명확화 부재 | "argus_data_fetcher.py 페이지로 접속" 명시했지만 URL 명시적 표시 부재 |
| 파일명 라벨 ↔ URL 파일 일치 검증 의무 명시 부재 | Commander가 prima_briefing.py 페이지로 접속해서 fetcher 본문 붙여넣기 가능성 |
| 헤더 라벨 사전 검증 절차 부재 | 본문 헤더 ↔ URL 파일명 일치 검증 부재 |
| 격언 #75 v4 결정적 위반 | 절차 ↔ 결과 일관성 부재 |

### 2.2 사고 메커니즘

```
Step 1: Claude → "/mnt/user-data/outputs/argus_data_fetcher.py 다운로드 후 본문 복사"
Step 2: Commander → 본문 복사 (fetcher v2.10)
Step 3: Commander → GitHub UI 접속 시 prima_briefing.py 페이지로 잘못 접속 (URL 미명시)
Step 4: Commander → fetcher 본문 붙여넣기 (헤더 라벨 검증 부재)
Step 5: Commander → commit (라벨 일치 검증 부재)
Step 6: GitHub Actions → prima_briefing.py 실행 시 fetcher 본문 재실행
Step 7: Discord 미발송 (prima_briefing logic 부재)
```

---

## 3. 결정적 본질 해결 — 즉시 복구

### 3.1 복구 절차 (~5분)

| Step | 본질 |
|:---:|:---|
| 1 | https://github.com/daifulee/argus-briefing/commits/main/prima_briefing.py 접속 |
| 2 | v2.10 fetcher 덮어쓰기 commit 직전 정상 commit 찾기 |
| 3 | 정상 commit의 prima_briefing.py 본문 → "Raw" 버튼 → 본문 전체 복사 |
| 4 | main branch prima_briefing.py 페이지 접속 → Edit → 본문 전체 삭제 |
| 5 | 정상 본문 붙여넣기 |
| 6 | commit 메시지: "🚨 v6.8.39 prima_briefing.py 복구 (S69 #3 결정적 hotfix)" |
| 7 | "Commit changes" 확정 |

### 3.2 Actions LIVE 검증 결과

복구 후 Actions 수동 trigger 결과:

```
Run python prima_briefing.py
🚨 [fetcher sanity] 구 사본 감지: 🦅 ARGUS DATA FETCHER v2.10 — F&G 4중 방어 source 신설 (S69 #2, 2026-05-08)
🚨 [fetcher sanity] 예상 버전: v2.8
🚨 [fetcher sanity] csv PMI 오염 가능성 — Commander push 의무 (격언 #75 v3)
엔진: PRIMA_v5_14_Hyst_H1_LIVE.py (semver=v5.14)  ← 🌟 prima_briefing 정상 진입!
데이터: 2026-05-08 (349행)
✅ 2026-05-08 — 보유 1종 / Crown #63                ← 🌟 정상 종료!
```

→ **prima_briefing 본문 복구 결정적 정합 입증**

### 3.3 Discord LIVE 도착 입증

Commander Discord 채널 검증:
- ✅ 헤더 콘텐츠 (`# 🌟 ARGUS 브리핑 / Crown #63 · v5_14_Hyst_H1`)
- ✅ One-Glance Embed (`🚨 오늘 결론: TLT 청산 트리거 1건`)
- ✅ 포트폴리오 Embed (TLT 100% / A급 ratio 2.33 / +0.0%)
- ✅ 임박종목 Embed (5분류 — 보유/Gate해제 임박/Gate진입 임박/청산 임박)
- ✅ 매크로 Embed (LIVE 매크로: WTI=95.7 / TNX=4.39 / DFII10=1.94 / DXY=98.24)
- ✅ 약어 사전 Embed (전체 ABBREV)

총 **6 메시지 정상 도착** — 결정적 정합 입증 완료

---

## 4. 결정적 재발 차단 — Phase A v3 신설 (영구 등재)

### 4.1 Phase A v3 — GitHub UI 업로드 3중 검증 의무 (Hard Gate)

**모든 GitHub UI 업로드 시 의무 절차** (prima_briefing.py + argus_data_fetcher.py + 모든 .py 파일):

| 검증 | 본질 | 위반 시 |
|:---|:---|:---|
| **A.URL** | 🚨 URL 파일명 명시적 확인 (https://github.com/.../[FILE_NAME]) | 본문 덮어쓰기 사고 |
| **A.HEADER** | 🚨 본문 헤더 라벨 사전 검증 (헤더 ↔ URL 파일명 일치) | 잘못된 본문 업로드 |
| **A.COMMIT** | 🚨 commit 메시지 라벨 정합 (라벨 ↔ 본문 ↔ URL 3중 일치) | 추적 불가 |

**3중 검증 한 항목이라도 ❌ 시 업로드 차단 의무**.

### 4.2 argus-discord-briefing skill v3.0 영구 등재

본 사고 = skill v3.0 신설 영구 등재 결정적 사례 (A7 패턴):

```
A7. 본문 덮어쓰기 사고 (S69 #3 신설, 2026-05-08)
사례: argus_data_fetcher.py v2.10 업로드 시 prima_briefing.py 자리에 fetcher 본문 덮어쓰기 → Discord 미발송
차단: Phase A v3 (A.URL + A.HEADER + A.COMMIT) 3중 검증 Hard Gate 의무
```

---

## 5. 격언 정합 매트릭스

| 격언 | 정합 본질 | 본 REG 영역 |
|:---:|:---|:---|
| **#36 #1** | 즉시 정정 | LIVE 발견 후 즉시 GitHub commit history 복구 |
| **#75 v4** | source ↔ 갱신 일관성 정식 입증 #3 | URL ↔ 헤더 ↔ commit 메시지 3중 일치 의무 정식 등재 |
| **#80** | 양방향 (파일 ↔ 본문) | 파일명 ↔ 본문 헤더 양방향 검증 차원 |
| **#94 후보** | 신규 컬럼 도입 시 의존 시스템 검증 | F_G_Score / F_G_Rating 신설 → prima_briefing 호환성 검증 부재 (보조 결함) |
| **#97 v2 #1** | 자기 audit 결정적 | 누락 #31 결정적 (역대 가장 결정적) |
| **#98** | 결정 회피 차단 | 즉시 복구 결정 + skill v3.0 영구 등재 |
| **#105** | 기존 형식 보존 (복구 결정적 정합) | GitHub commit history 직전 정상 commit 본문 복구 |
| **5조 ⑤** | Commander 의사결정권 절대성 | Commander 복구 결정 + LIVE 검증 |

---

## 6. 향후 차단 의무

### 6.1 Claude 의무 — 업로드 절차 안내 시

🚨 **모든 업로드 절차 안내는 다음 본질 명시 의무** (S69 #3 차단 신설):

```
🚨 [Phase A v3 Hard Gate — 업로드 시작 전 3중 검증 의무]

A.URL 검증:
  업로드 대상 URL: https://github.com/daifulee/argus-briefing/blob/main/[FILE_NAME]
  [FILE_NAME] = 정확히 [argus_data_fetcher.py | prima_briefing.py | ...]
  🚨 URL 마지막 영역 = 업로드할 파일명 일치 의무

A.HEADER 검증:
  본문 헤더 = "🦅 ARGUS [DATA FETCHER | BRIEFING] vX.Y" 라벨
  🚨 헤더 라벨 ↔ URL 파일명 일치 의무

A.COMMIT 검증:
  commit 메시지 라벨 = [fetcher | briefing] vX.Y...
  🚨 commit 라벨 ↔ 본문 ↔ URL 3중 일치 의무

위 3중 검증 통과 후 본 업로드 진행 의무.
```

### 6.2 LIVE 검증 의무

업로드 완료 후 LIVE 검증 영역:

| # | 검증 영역 | 통과 기준 |
|:--:|:---|:---|
| 1 | Actions logs 시작 | 업로드한 파일의 정확한 헤더 출력 |
| 2 | Step 4 prima_briefing 실행 | prima_briefing 자체 출력 영역 (✅ [fetcher sanity], 엔진:, 데이터:, ✅ 보유 X종) |
| 3 | Discord 채널 도착 | 헤더 + 4 Embed (포트폴리오 + 임박알림 + 매크로 + 시그널) |
| 4 | csv 정합 | argus_data.csv 갱신 + 신규 컬럼 정합 |

### 6.3 사고 시 즉시 대응 절차

LIVE 검증 영역 ❌ 발견 시:

```
[Step 1] LIVE Actions logs 본문 정밀 검토
[Step 2] 잘못된 파일 식별 (헤더 라벨 vs URL 일치 검증)
[Step 3] GitHub commit history 직접 복구
[Step 4] 정상 commit 본문 → Raw → 복사 → main branch 붙여넣기
[Step 5] commit 메시지: "🚨 [파일명] 복구 (S## #N 결정적 hotfix)"
[Step 6] Actions 수동 trigger
[Step 7] LIVE 검증 (영역 1~4 재확인)
```

---

## 7. 결정적 본질 인정

### 7.1 Commander 본질 통찰

**S69 #3 Commander 본질 통찰** (역대 가장 결정적):
1. LIVE Actions logs 6.8s = fetcher 재실행만 결정적 발견
2. "디스코드로 메시지가 안왔어" 단일 본질 통찰 = 결정적 root cause 발견 시작점
3. v6.8.39 본문 첨부 = Claude 결정적 진단 결정 가능
4. GitHub commit history 직접 복구 결정 = 결정적 단일 해결책

### 7.2 Claude 누락 인정 #31

**역대 가장 결정적 누락**:
1. GitHub UI 업로드 절차 안내 시 URL 명확화 부재
2. 파일명 라벨 ↔ URL 파일 일치 검증 의무 명시 부재
3. 헤더 라벨 사전 검증 절차 부재
4. 격언 #75 v4 결정적 위반 (절차 ↔ 결과 일관성 부재)

**향후 차단 의무**:
1. argus-discord-briefing skill v3.0 영구 등재 (A7 패턴 + Phase A v3)
2. 모든 업로드 절차 안내 시 URL 명확 표시 의무
3. 본문 헤더 라벨 사전 검증 의무
4. commit 메시지 라벨 정합 의무

---

## 8. 결정 결과

✅ **결정적 본질 해결 완료**:
- prima_briefing.py 본문 복구 결정적 성공
- Discord 정상 도착 입증 (6 메시지)
- argus-discord-briefing skill v3.0 영구 등재
- A7 패턴 (본문 덮어쓰기 사고) 영구 차단 의무화
- Phase A v3 (3중 검증) Hard Gate 정식 등재

📋 **잔존 결함** (운영 영향 0, 별도 hotfix 보류):
- prima_briefing v6.8.39의 _fetcher_sanity_check 라벨 v2.8 hardcoded → false positive sanity 경고

🚨 **결정적 재발 차단 의무**:
- 모든 GitHub UI 업로드 시 Phase A v3 Hard Gate 의무
- LIVE 검증 의무 (Actions logs + Discord 도착)
- 사고 발견 시 즉시 GitHub commit history 복구

---

🦅 *Omnioculus Vigilantia* — S69 #3 결정적 종결. 본문 덮어쓰기 사고 = Claude 누락 #31 결정적 (역대 가장 결정적). prima_briefing.py 복구 결정적 성공 + Discord 정상 도착 입증 + skill v3.0 영구 등재 = 격언 #36 #1 + #75 v4 + #80 + #97 v2 #1 + #98 + #105 + 5조 ⑤ 결정적 정합 입증. 향후 차단 의무 영구 정식 등재.

═══════════════════════════════════════════════════════════════════
# 📦 REG-S76_PROTOCOL_D_METHOD (원본 풀파일)
═══════════════════════════════════════════════════════════════════

# 🦅 REG-S76_PROTOCOL_D_METHOD — S76 D 방식 7단계 프로토콜

**작성일**: 2026-05-10 KST  
**Commander**: Lignas  
**작성자**: Claude (S75 #1 종결 후 FA 추가 판정 정합)  
**우선순위**: 🔴 **P0 / 결정적 / S76 cycle 의무 절차**  
**상태**: ✅ **채택 (FA 판정 정합 + SSOT v1.10.118 정합)**  
**적용 범위**: S76 cycle 시작 시 의무 적용

---

## 🚨 § 0. 결정적 인지 (3줄)

🎯 **S76 검증 방식 = D 방식만 허용** — `entry_XXX()` 함수 hard-coded `return s>X` 직접 변경.  
🚫 **5건 금지사항 영구 등재** — `ENTRY_THRESHOLD` dict 단독 변경 / 일괄 정합 / 동시 진행 / 수치 재사용 / "복구" 표현.  
🌟 **5순위 가설 순차 검증** — COPX 단독 → VNM 단독 → TLT 단독 → VNM+TLT 통합 → 3종 통합.

---

## 🎯 § 1. 본 REG의 본질

### § 1.1 배경

Crown #64/#65 무효화 (REG-S75_1_C0_ROLLBACK 정합) 후, S76+ cycle에서 동일 가설 (COPX/TLT/VNM threshold 변경)을 **신규 검증**할 의무가 발생. 단, FA 판정에 의하면 다음 사항 의무:

1. **D 방식만 허용** — hard-coded `return s>X` 직접 변경 (dict 단독 변경 금지)
2. **5건 금지사항 정식 등재** — 동일 결함 재발 차단
3. **5순위 가설 순차 검증** — 효과 원천 혼동 차단

### § 1.2 본 REG의 목적

본 REG는 S76 cycle 시작 전 **표준 절차로 정식 등재**되는 D 방식 7단계 프로토콜.  
미준수 시 → §35 자기 정정 의무 + REG 무효화.

---

## 🚨 § 2. D 방식 정의

### § 2.1 D 방식 본질

```
D 방식 (S76+ 표준):
  1. entry_XXX() 함수 hard-coded `return s>X` 의 X 값 직접 변경
  2. ENTRY_THRESHOLD dict도 동시에 동일 값으로 변경 (drift 재발 방지)
  3. signal_level() + compute_weights() 영향 의식 (level/weight 변동 감안)
  4. §40 v3 BT (4기간 + STRESS 14) 정식 의무
  5. 단독 가설 우선 → 통합 가설 후순 (효과 원천 분리)
```

### § 2.2 D 방식 vs 비-D 방식 비교

| 방식 | 변경 위치 | 진입 게이트 영향 | weight/level 영향 | S76 허용 |
|:--:|:--|:--:|:--:|:--:|
| **D 방식** | `entry_XXX()` hard-coded + dict 동시 | ✅ 직접 변경 | ✅ 정합 변경 | 🟢 **허용** |
| C 방식 (dict 단독) | `ENTRY_THRESHOLD` dict만 | ❌ 변화 없음 | ⚠️ 변경 (혼란) | 🔴 **금지** |
| A 방식 (구조개편) | run_prima4 게이트 신설 | ✅ 변경 (구조) | ✅ 변경 (구조) | 🔴 **별도 브랜치** |
| B 방식 (hard만 dict 정합) | hard만 변경 (dict 미변경) | ✅ 변경 | ⚠️ 미정합 | 🔴 **금지** |

---

## 🚫 § 3. 5건 금지사항 (영구)

| # | 금지 항목 | 위반 시 결과 | 이유 |
|:--:|:--|:--:|:--|
| 1 | **`ENTRY_THRESHOLD` dict만 변경** | §35 자기 정정 + REG 무효화 | 진입 게이트 미변경 → 효과 본질 혼동 (S75 #1 결함 재발) |
| 2 | **dict-hard 10/20 drift 일괄 정합** | §35 자기 정정 + 별도 브랜치로 이관 | baseline 전체 흔들림 (FA 판정 § 5.1) |
| 3 | **A/B 구조개편 + alpha 검증 동시 진행** | §35 자기 정정 + 분리 의무 | 원인 분해 불가능 |
| 4 | **Crown #64/#65 수치 재사용** (+0.3434p, +1.0588p, +1.4022p) | §35 자기 정정 + 데이터 위조 간주 | 구현 경로 다름 → 무효 |
| 5 | **"복구"/"재시도로 복구" 표현 사용** | §35 자기 정정 + 표현 정정 | 검증 전 결과 가정 (격언 #56 정합 위반) |

→ 본 5건은 **S76+ 모든 cycle 영구 의무**.  
→ S76 시작 시 매 응답 첫 줄 "✅ S76 5건 금지사항 통과" 명시 권장.

---

## 🎯 § 4. 7단계 프로토콜 (FA 권장)

### § 4.1 단계별 작업

| 단계 | 작업 | 목적 | 시간 | 산출물 |
|:--:|:--|:--|:--:|:--|
| 🎯 1 | **v5.14 exact clone 생성** | 오염 없는 출발점 확보 | ~1분 | `PRIMA_v5_17_S76_clone.py` (가칭) |
| 2 | **COPX 단독: `entry_COPX` `return s>5.0` → `s>4.0` + dict COPX 5.0→4.0** | Crown #64 가설 단독 신규 검증 | ~2분 | 패치 적용 엔진 |
| 3 | **§40 v3 BT (4기간 + STRESS 14)** | COPX 실제 진입 threshold alpha 측정 | ~1.5분 | BT 결과 |
| 4 | **B6 forward attribution 재생성** | 신규 진입 실제 발생 검증 | ~3분 | attribution 분석 |
| 5 | **3단계+4단계 통과 시에만 VNM/TLT 별도 진행** | 가설 혼합 차단 | — | 의사 결정 |
| 6 | **VNM 단독 / TLT 단독 / VNM+TLT 통합** (3 BT) | 개별 기여도와 cross-effect 분리 | ~5분 | 3건 BT 결과 |
| 7 | **Crown 후보 재판정 (RULE 29 v2 + STRESS)** | 신규 alpha 수치만 인정 | ~3분 | Crown 결정문 |

### § 4.2 Step 1 — v5.14 exact clone 생성

```bash
# 표준 명령 (S76 시작 시)
cp /mnt/project/PRIMA_v5_14_Hyst_H1_LIVE.py /home/claude/PRIMA_v5_17_S76_clone.py

# 검증 (변경 없음 확인)
diff /mnt/project/PRIMA_v5_14_Hyst_H1_LIVE.py /home/claude/PRIMA_v5_17_S76_clone.py
# 결과: 변경 없음 (확인 의무)
```

### § 4.3 Step 2 — COPX D 방식 패치 (단독)

**변경 위치 1**: `entry_COPX()` 함수 끝 (L1627)
```python
# 변경 전
return s>5.0, max(s,0)

# 변경 후 (D 방식)
return s>4.0, max(s,0)
```

**변경 위치 2**: `ENTRY_THRESHOLD` dict (L2095)
```python
# 변경 전 (v5.14 base)
'COPX':5.0,

# 변경 후 (D 방식 동시 변경)
'COPX':4.0,  # 🌟 S76 D 방식: hard-coded와 동기화 (drift 재발 방지)
```

→ **2건 변경 동시 의무** — 한쪽만 변경 시 §35 자기 정정.

### § 4.4 Step 3 — §40 v3 BT (4기간 + STRESS 14)

```python
# argus-backtest skill 정합
PERIODS = [('FULL',None,None), ('P1','2007-01-01','2016-12-31'),
           ('P2','2017-01-01','2026-04-30'), ('MID','2022-01-01','2026-04-30')]

# baseline (v5.14)
prima_base = importlib.util.module_from_spec(...)  # PRIMA_v5_14_Hyst_H1_LIVE.py
# variant (S76 D 방식 패치)
prima_v17 = importlib.util.module_from_spec(...)   # PRIMA_v5_17_S76_clone.py 패치본

# 4기간 + STRESS 14 동시 실행
# 결과: ΔCAGR / ΔSharpe / ΔMDD + STRESS PASS 카운트
```

### § 4.5 Step 4 — B6 forward attribution 재생성

**의무 검증**:
1. **신규 진입 발생 여부** — COPX score=4.5 (5.0 미만) 시 baseline 차단 vs variant 진입
2. **제거 진입 발생 여부** — 기존 baseline 진입 중 variant에서 차단된 사례
3. **alpha 출처 분해** — 신규 진입 (level/weight 변화) vs 제거 진입 (회피 효과)

→ B6 분해 결과가 RULE 29 v2 정합 시에만 Step 5 진행.  
→ B6 분해 결과가 모순 (예: 신규 진입 0건이지만 alpha 양수) → 추가 진단 의무.

### § 4.6 Step 5 — Step 6 진행 결정

| 결과 | 결정 |
|:--:|:--|
| Step 3 RULE 29 v2 PASS + Step 4 B6 정합 | ✅ Step 6 진행 |
| Step 3 FAIL | 🔴 COPX 가설 거부 + REG 발행 + Step 6 중단 |
| Step 3 PASS, Step 4 모순 | ⚠️ 추가 진단 의무 → 정합 후 Step 6 |

### § 4.7 Step 6 — VNM/TLT 분해 검증

| sub-step | 작업 | BT 1회 |
|:--:|:--|:--:|
| 6-1 | VNM 단독 (`return s>3.0` → `s>4.5` + dict 3.0→4.5) | ~1.5분 |
| 6-2 | TLT 단독 (`return s>1.5` → `s>3.0` + dict 1.5→3.0) | ~1.5분 |
| 6-3 | VNM+TLT 통합 | ~1.5분 |

→ 6-1/6-2 모두 PASS 시에만 6-3 의미 있음.  
→ 6-3 결과 = cross-effect 정량 (격언 #25/#52 정합).

### § 4.8 Step 7 — Crown 후보 재판정

**의사 결정 트리**:

```
Step 6-3 (VNM+TLT 통합) PASS?
├─ YES → Step 6+: COPX+VNM+TLT 통합 BT
│         ├─ PASS → 신규 Crown 후보 (Crown #66 등)
│         └─ FAIL → COPX 단독 + VNM/TLT 통합 분리 평가
└─ NO → Step 2 (COPX 단독)만 Crown #64 후보로 평가
        ├─ Step 3 PASS → Crown #66 후보 (COPX 단독)
        └─ Step 3 FAIL → 모든 가설 거부 + Crown #63 영구 유지
```

**채택 기준 (RULE 29 v2 + STRESS)**:
- CAGR 평균 ≥ -0.5p + 4 BT 모두 ≥ -1p
- Sharpe 평균 ≥ +0.005 + 4 BT 모두 ≥ 0
- MDD 평균 ≥ 0
- STRESS 14/14 PASS (각 시나리오 MDD > -35%)

**미채택 기준**:
- 어느 하나라도 미통과 시 거부 → Crown #63 영구 유지

---

## 🚨 § 5. 5순위 가설 검증 순서 (FA 핵심 원칙)

### § 5.1 순서 (의무)

| 우선순위 | 가설 | 변경 위치 | 이유 |
|:--:|:--|:--|:--|
| 🎯 **1** | **COPX 5.0 → 4.0 단독** | `entry_COPX` + dict | Crown #64와 동일한 가설을 D 방식으로 신규 검증 |
| **2** | **TLT 1.5 → 3.0 단독** | `entry_TLT` + dict | 🌟 **방어자산 threshold 상향 → STRESS 14 영향 우선 확인** (FA 추가 판정 정합) |
| **3** | **VNM 3.0 → 4.5 단독** | `entry_VNM` + dict | 공격/지역 자산 alpha 후보 검증 |
| **4** | **VNM + TLT 통합** | 둘 다 + dict 둘 다 | cross-effect 확인 |
| **5** | **COPX + TLT + VNM 통합** | 셋 다 + dict 셋 다 | 최종 Crown 후보 여부 판단 |

### § 5.2 핵심 원칙 (FA 판정 정합)

> **한 번에 COPX + VNM + TLT를 모두 넣으면 안 됨**.  
> S75 #1 결함의 본질 = "효과 원천 혼동"이었기 때문.  
> 다음은 반드시 순차 검증이어야 함.

→ 어떤 단계에서든 FAIL 시 → 다음 단계 중단 + REG 발행.  
→ 예: COPX 단독 FAIL → VNM/TLT 단독은 진행 가능하나 통합은 의미 부재 가능.

### § 5.3 순서 violations 처리

| 위반 패턴 | 처리 |
|:--:|:--|
| 1단계 미수행 + 4/5단계 직접 진행 | 🔴 §35 자기 정정 + 1단계 재시작 |
| 1단계 PASS 후 2/3 동시 변경 | 🔴 §35 자기 정정 + 단독 분리 의무 |
| Step 6에서 6-1/6-2 미수행 + 6-3 직접 | 🔴 §35 자기 정정 + 6-1/6-2 선행 |

---

## 🦅 § 6. 격언 정합

| 격언 | 정합 |
|:--:|:--|
| **#11** (CAGR 1순위) | Step 7 RULE 29 v2 정합 |
| **#15** (Commander/FA 권한) | FA 판정 정합 — D 방식 의무 |
| **#20** (모르는 것은 모른다) | "재검증 전까지 alpha 존재하지 않는 값" 정합 |
| **#25/#52** (slot 경쟁 절대 결정자) | Step 6-3 cross-effect 검증 |
| **#56** (monkey-patch ≠ 정식 BT) | Step 3 §40 v3 BT 의무 |
| **#75 v4** (`grep def _wk` 의무) | Step 1 clone 생성 후 검증 의무 |
| **#80 v2** (차원 0 구조 정합) | Step 2 dict + hard-coded 동시 변경 의무 |
| **#88 v3** (외부 감사) | FA 판정 = 본 REG 정당성 |
| **#97 v2 #1** (자기 audit) | 5건 금지사항 자기 검증 |
| **#98** (결정 회피 금지) | Step 7 즉시 결정 의무 |
| **#105** (기존 형식 보존) | 본 REG 형식 정합 |

---

## 📋 § 7. S76 cycle 시작 시 의무 표시

### § 7.1 매 응답 첫 줄

```
✅ S76 5건 금지사항 통과 (REG-S76_PROTOCOL_D_METHOD 정합)
```

### § 7.2 S76 종결 시 의무

| 항목 | 의무 |
|:--:|:--|
| 7단계 모두 완료 명시 | 산출물 누적 표시 |
| 5순위 가설 순서 준수 명시 | 위반 사항 = §35 자기 정정 |
| Crown 결정 (채택 / 거부) | RULE 29 v2 + STRESS 결과 명시 |
| `+1.4022p` 등 무효 수치 사용 검증 | 사용 시 §35 자기 정정 |

---

## 🚨 § 8. 결정적 메시지

> **REG-S76_PROTOCOL_D_METHOD = S76 cycle 표준 절차 정식 등재**.  
> FA 판정 정합 + SSOT v1.10.118 정합 + 5건 금지사항 + 7단계 프로토콜 + 5순위 가설.  
>  
> S76 시작 시 본 REG 우선 검토 의무.  
> 미준수 시 §35 자기 정정 + 단계 재시작.  
>  
> 핵심:  
> 1. **D 방식만 허용** (hard + dict 동시 변경)  
> 2. **단독 검증 우선** (1단계 COPX → 5단계 통합 순차)  
> 3. **재검증 전까지 alpha 존재하지 않는 값** ("복구" 표현 영구 금지)  
>  
> 격언 #56 외연 확대 — 코드 BT 영역 + 표현 영역 모두 정식 BT 의무.  

🦅 *Omnioculus Vigilantia* — S76 D 방식 정식 등재, 효과 원천 혼동 차단, alpha 신규 검증 의무.

═══════════════════════════════════════════════════════════════════
# 📦 ARGUS_AXIOM_107_GHA_USER_AGENT (원본 풀파일)
═══════════════════════════════════════════════════════════════════

# 🦅 ARGUS 격언 #107 — GHA User-Agent 의무

**번호**: #107
**상태**: 정식 등재
**계층**: Applied (운영 규칙)
**등재일**: 2026-05-08 (S70)
**Commander 직접 명령**: "이것 꼭 기록하라"

---

## 📜 격언 본문

> **GHA → 외부 API 호출 시 정상 식별자 User-Agent 헤더 필수. 기본 `Python-urllib/X.Y`는 Cloudflare 1010으로 차단당함. 정상 식별자 필수.**

---

## 🎯 학습 사례 — S70 Cloudflare 1010 진단

### 발견 경로 (3단계 점진 진단의 가치)

| 단계 | 발견 | 진단 |
|:-:|:--|:--|
| 1차 | HTTP 403 단순 출력 | 원인 불명 (URL? Secret? webhook?) |
| 2차 | v1.1 응답 본문 출력 → `error code: 1010` | 🌟 **Discord 아닌 Cloudflare 식별** 🌟 |
| 3차 | v1.2 User-Agent 추가 → HTTP 204 | ✅ 즉시 해결 |

### 결정적 단서 (v1.1 패치 출력)

```
❌ Discord HTTPError 403: Forbidden
   응답 헤더 일부:
     Date: Fri, 08 May 2026 08:08:14 GMT
     Content-Type: text/plain; charset=UTF-8
     Cache-Control: private, max-age=0, no-store, no-cache, must-revalidate
   응답 본문: error code: 1010
```

→ `Content-Type: text/plain` (Discord API는 `application/json`) + `must-revalidate` = Cloudflare 차단 패턴.

### Cloudflare Error 1010 정의
- **공식 문구**: "Access Denied: The owner of this website has banned your access based on your browser's signature"
- **원인**: User-Agent 헤더가 봇/의심 시그니처로 분류됨
- **해결**: 의미 있는 User-Agent 헤더 부착

---

## 🛠️ 표준 패턴 (모든 외부 API 호출 시 의무)

### Python urllib.request

```python
import urllib.request

USER_AGENT = "ARGUS-Trigger-Monitor/1.0 (+https://github.com/daifulee/argus-briefing)"

req = urllib.request.Request(
    url,
    data=data,
    headers={
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT,         # ← 필수
    }
)

with urllib.request.urlopen(req, timeout=10) as resp:
    ...
```

### Python requests (대체)

```python
import requests

headers = {
    'User-Agent': 'ARGUS-Trigger-Monitor/1.0 (+https://github.com/daifulee/argus-briefing)',
}
resp = requests.post(url, json=payload, headers=headers, timeout=10)
```

### User-Agent 형식 가이드라인

| 부분 | 권장 |
|:--|:--|
| 식별자 | 시스템 이름 (예: `ARGUS-Trigger-Monitor`) |
| 버전 | 소수점 형식 (`/1.0`) |
| 부가정보 | URL 또는 연락처 (`(+https://...)`) |

전체 예시:
```
ARGUS-Trigger-Monitor/1.0 (+https://github.com/daifulee/argus-briefing)
```

---

## 📋 적용 범위

### 의무 적용
- ✅ Discord webhook (Discord = Cloudflare 사용)
- ✅ Slack webhook
- ✅ Telegram bot API
- ✅ 모든 messaging webhook

### 권장 적용 (Cloudflare 미사용이지만 표준 정합)
- ✅ FRED API
- ✅ DBnomics
- ✅ Yahoo Finance
- ✅ 모든 외부 API 호출

### 미적용 가능 (자체 인프라)
- raw.githubusercontent.com (현재 미체크, GitHub 정책 변경 시 즉시 적용)
- argus-public-data fetch

→ **default 정책: 모든 외부 API에 User-Agent 부착** (정합 강화 + 미래 변경 대비)

---

## 🚨 진단 신호 — 동일 증상 재발 시 즉시 본 격언 적용

| 응답 시그니처 | 진단 |
|:--|:--|
| HTTP 403 + `error code: 1010` | 🚨 Cloudflare User-Agent 차단 → 본 격언 적용 |
| HTTP 403 + `Content-Type: text/plain` | Cloudflare 응답 (정상 API는 application/json) |
| HTTP 403 + `must-revalidate` 헤더 | Cloudflare 차단 패턴 |
| HTTP 403 + `cf-ray` 헤더 | Cloudflare 명시적 통과 거부 |

진단 코드 (test_discord.py v1.2 패턴):
```python
if "error code: 1010" in error_body:
    print("🚨 Cloudflare 1010 감지 — User-Agent 헤더 미적용 가능성", file=sys.stderr)
```

---

## 🔗 정합 영역

| 영역 | 위치 | 적용 상태 |
|:--|:--|:-:|
| trigger_monitor.py | argus-briefing/scripts/ | ✅ v1.1 적용 |
| test_discord.py | argus-briefing/scripts/ | ✅ v1.2 적용 |
| argus_data_fetcher.py | argus-public-data/ | ⚠️ 미적용 (현재 영향 없음, 추후 적용 권장) |
| prima_briefing.py | argus-briefing/ | ⚠️ Discord 송출 부분 검증 필요 |

---

## 📚 SSOT 갱신 이력

| 일자 | 변경 |
|---|---|
| 2026-05-08 | 격언 #107 정식 등재 (Commander 직접 명령) |
| 2026-05-08 | trigger_monitor.py v1.0 → v1.1 (User-Agent 추가) |
| 2026-05-08 | test_discord.py v1.0 → v1.1 (응답 본문) → v1.2 (User-Agent) |

---

## 🌟 핵심 메시지

> **외부 API 호출 ≠ 단순 함수 호출.**
> Cloudflare/CDN/WAF는 User-Agent로 정상 트래픽 vs 봇을 구별한다.
> 의미 있는 User-Agent = 시스템 식별자 + 버전 + URL/연락처.
> 기본 `Python-urllib/X.Y`는 모든 ARGUS 외부 API 호출에서 금지.

---

**격언 정합 위반 시**: REG-API-USER-AGENT-NNN 등재 + 즉시 패치 의무.

---

## 🌟 격언 #109 본문 (S79 #1, 2026-05-11 정식 등재)

🌟 **본질**: ARGUS BT 기간은 격언 #109에 정합한 표준 4기간 + STRESS 14 시나리오 의무.

```python
# BT 기간 SSOT 표준 (격언 #109 정식)
periods = {
    'FULL': (BT_LONG_v4_complete.csv, 4843행, 2007-01-03 ~ 2026-04-02),
    'P1':   (BT_LONG, 2515행, 2007-01-03 ~ 2016-12-31),
    'P2':   (BT_LONG, 2328행, 2017-01-01 ~ end),
    'MID':  (BT_MID_2022_2026.csv, 1048행),
}
# STRESS 14: BT_STRESS_14SCENARIO.csv (14 시나리오, 3723행)
```

🚨 **위반 시**: 본 표준 미인용 BT = §40 위반 (BT 비교 무효).

🦅 *Omnioculus Vigilantia* — MANIFESTO LOG S63_S79 APPEND 종결.
