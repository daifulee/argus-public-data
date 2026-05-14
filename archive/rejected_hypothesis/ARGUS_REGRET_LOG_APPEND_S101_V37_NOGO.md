# 🦅 ARGUS REGRET LOG APPEND S101 — v37 COPX DD8 COOL5 NO-GO

| 항목 | 내용 |
|---|---|
| 등록 시각 | 🌟 **2026-05-13 KST** 🌟 |
| Session | S101 #1 + S101 #2 종결 |
| 후보 | `COPX_DEV200_GT50_DD8_COOL5_HALF` (v37) |
| 후보 파일 | `PRIMA_v5_20_COPX_DD8_COOL5_CANDIDATE.py` |
| 단계 | 외부 FA cold audit / Crown 후보 격상 시도 |
| 판정 | 🔴 **NO-GO** (Crown 채택) |
| 추가 판정 | 🟡 외부 FA 제출 GO with caveat / 🟡 연구 생존 |

## 🎯 1. 기각 사유 (4건)

### ① 격언 #91 ② Cliff (P0)
P2 기간에서 (47.5, -7) 인접 cell ΔCAGR **-1.556%p** — 현재 cell (50, -8) +0.351%p 대비 **cell jump -1.907%p**.
(45, -7) cell = **-5.963%p** — 2단계 인접 cell에서 거의 6%p P2 CAGR 손실.
→ 현재 (50, -8) cell은 **plateau가 아니라 narrow ridge**. 격언 #76 (sweep plateau required) 위반.

### ② 격언 #52 Slot Cascade (P0)
CRASH10D STRESS 시나리오에서:
- idx 181: COPX HALF → **GLD substitute 진입** (slot 점유)
- idx 191: baseline의 **COPX SC7.0\|C 재진입 신호 누락** (slot 차서)
- idx 244 (최종): equity **-0.46% vs baseline**

→ Conviction Concentration alpha 메커니즘 (격언 #73) 손상.

### ③ 격언 #88 ExSn Asymmetry 위반 (P0)
candidate 설계에 **cooldown override 메커니즘 부재**.
- idx 269 (P2): COPX SC21.1|S BUY 신호 (high-conviction) — cooldown 5d로 차단
- idx 1538 직전 (P2 2026): 동일 패턴 의심
→ exit invariant (cooldown) 이 entry invariant (high-conviction signal) 를 무차별 차단.

### ④ n=4 Small Sample (P1)
P2 4 HALF 표본:
- 2021-02-26 (idx 290): T+40d **+9.82%** → alpha 약함
- 2021-03-05 (idx 295): T+5d **+4.62%** 즉시 반등 → alpha negative
- 2026-02-17 (idx 1538): T+20d **-8.10%** → alpha positive
- 2026-02-18 (idx 1539): T+20d **-13.54%** → alpha positive
→ **50%만 alpha-positive** (2026), 2021은 alpha-negative ~ neutral. 통계적 유의성 미달.

## 🚨 2. 학습 — 6건

### 학습 ① — 단순 4기간 BT + STRESS 14 통과 ≠ 채택 자격
보고서의 RULE 29 rough check (7개 기준) PASS 였으나, **격언 #91 ② cliff sweep + cooldown-aware**가 누락되면 narrow ridge 채택 위험.

### 학습 ② — 임계값 sweep 은 2-axis 가 아니라 3-axis 가 필요
threshold₁ × threshold₂ 의 2-axis sweep 만으로는 cooldown window 위치 변화 영향을 감지 못함. **cooldown_days 까지 포함한 3-axis sweep 의무** (격언 #112 후보 정합).

### 학습 ③ — Single day micro-edge 가 cumulative 손해 결정 가능
idx 267 단 하루의 DEV200 +49.66 / DD20 -7.56 가 5년치 P2 ΔCAGR cliff 결정. **임계값 sensitivity 가 적어도 trade-by-trade forensic 의무**.

### 학습 ④ — 보고서 자체 정직성 OK, audit 발견은 추가 layer
원본 보고서 (S101 #1 input) 는 정직했음. cold audit 발견 = 보고서가 이미 경고한 "표본 수 작음" / "CRASH10D 손상" 영역의 정량적 깊이를 확인한 것. **deception 위험 없음**.

### 학습 ⑤ — 격언 #88 (ExSn Asymmetry) 의 새로운 차원
exit invariant (cooldown) 이 entry invariant (high-conviction signal) 를 차단하는 패턴은 **격언 #88의 확장 사례**. 향후 모든 cooldown-bearing 설계에 override 메커니즘 의무 검토.

### 학습 ⑥ — 메모리 외 SSOT 정합 의무
세션 시작 시 메모리 (v1.10.141) vs 실측 SSOT (v1.10.178) **~37 버전 outdated**. **격언 #11 정합 self-correction** 필요.

## 🎯 3. v38 후속 P0 권고

| 우선순위 | 항목 |
|:---:|---|
| 🚨 P0 | Cooldown override 메커니즘 추가 (SC ≥ 20 / STORM_BUY 직후 cooldown 무시) |
| 🚨 P0 | 3-axis sweep (DEV200 × DD20 × cooldown_days) 의무 |
| 🔴 P1 | DEV200>50 hard cliff → soft trigger (50~60 linear weight) 검토 |
| 🟡 P2 | P2 2021 vs 2026 alpha asymmetry 의 macro regime 의존성 분석 |

## 🟡 4. 연구 생존 판정

v37 후보 방향성 (COPX overheat HALF) 자체는 유효:
- 2026년 2건 (idx 1538/1539) alpha-positive (T+20d **-8.10% / -13.54%**)
- CRASH10D 단기 회피 효과 (T+5d -4.37%, T+10d -6.01%)
- 4기간 BT 평균 ΔCAGR **+0.178%p** / ΔSharpe **+0.0076** 양수

→ threshold robustness 향상 + cooldown override + slot interaction 정합 후 **v38 재시도 권고**.

## 📁 5. 참조 산출물

| 파일 | 내용 |
|---|---|
| ARGUS_V37_EXTERNAL_FA_AUDIT_S101.md | S101 #1 cold audit |
| ARGUS_V37_CLIFF_ROOT_CAUSE_S101_2.md | S101 #2 cliff forensic |
| REG-S101_1_V37_EXTERNAL_FA_AUDIT.md | REG-S101_1 등록 |
| REG-S101_2_CLIFF_ROOT_CAUSE.md | REG-S101_2 등록 |
| ARGUS_MANIFESTO_APPEND_S101_2_AXIOM_112_CANDIDATE.md | 격언 #112 후보 |
| ARGUS_SSOT_ADDITION_v1_10_179.md | SSOT 본 ADDITION |
