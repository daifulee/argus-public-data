# ARGUS SSOT v1.10.207 ADDITION — 자동 회피 #10 후보 신설

**Session**: S112 #1  
**Date**: 2026-05-17 KST  
**Baseline**: SSOT v1.10.206 (S110#2 ACTIVE)  
**Status**: 🌟 ADDITION 등재 — 자동 회피 #10 후보 + 격언 #91 v2 패턴 ④ baseline 첫 입증

---

## §1. 본 ADDITION 본질

S112 #1 (VRC v0.1 cycle) NO-GO 결정 결과 도출된 **3 결정적 baseline**의 SSOT 정착:

1. 🆕 **자동 회피 #10 후보** — Cross-Asset Overlay 등재 前 Crown 內 mechanism cross-check 의무
2. 🆕 **격언 #91 v2 패턴 ④ 첫 baseline** — Temporal Heterogeneity 결정적 입증 사례
3. 🆕 **메타 학습 3건** — Crown 內 mechanism 重복 차단 / Temporal Heterogeneity / Cross-Asset Overlay protocol

---

## §2. 🆕 자동 회피 #10 후보 (정식 등재)

### 2.1 제목
🌟 **"Cross-Asset Overlay 등재 前 Crown 內 mechanism cross-check 의무"** 🌟

### 2.2 정의
Cross-Asset Risk Allocation 또는 Portfolio Target Overlay 후보는 Single-Asset Boost가 아니더라도, 기존 Crown 內部에 동일하거나 유사한 risk-control mechanism이 이미 내장되어 있을 경우 **重복 적용으로 alpha를 훼손할 수 있다**.

### 2.3 S112 #1 결정적 근거

**VRC v0.1 설계**:
- VVIX > 110 / < 105 hysteresis (margin 5, Crown #67 VIX hysteresis 정합)
- 4-ticker active defensive sleeve (TLT / GLD / XLU / XLV)
- α ∈ {0.25, 0.5, 0.75, 1.0} Portfolio Target Overlay

**Phase A 결정적 결과** (BT_LONG 4843일):
- def-agg sleeve spread: +0.32%/day (전체), +0.13%/day (4-ticker active)
- t-stat: +7.00 (전체), +4.06 (4-ticker active)
- 패턴 ③ Robust Plateau (thr 98~130 모든 구간 t > +5.14)
- SPY baseline 대비 Sharpe +0.597 → +0.854 (α=0.5)

**Phase B BT 결정적 결과** (PRIMA v5.25 통합):

| α | avg ΔCAGR | min ΔCAGR | 결과 |
|---|----------|----------|------|
| 0.25 | -0.789p | -2.339p | 🚨 NO-GO |
| 0.50 | -1.647p | -4.701p | 🚨 NO-GO |
| 0.75 | -2.573p | -7.083p | 🚨 NO-GO |
| 1.00 | -3.565p | -9.483p | 🚨 NO-GO |

### 2.4 결정적 의무 (Cross-Asset Overlay 후보 §B.9 v2 진입 前)

다음 5 검증 의무:

1. **Crown 內 동일 signal 활용 여부 grep**
   - VVIX / VIX / WTI / DXY / OAS 등 후보 시그널이 Crown 內 existing usage 검증
2. **유사 risk-control mechanism 重복 여부**
   - VIX hysteresis / WTI gate / entry_TLT 면제 / WALCL ffill 등 cross-check
3. **Crown mechanism 비활성화 後 isolated alpha 존재 여부**
   - Crown 영역 제거 後 신규 overlay의 effective alpha 측정
4. **P1 / P2 / MID temporal heterogeneity 검증**
   - 단일 period 결정적 alpha 의존 ❌ → 모든 period 정합 의무
5. **Overlay가 Crown #67 Top5 alpha를 대체하는지, 보완하는지**
   - 보완(complement) ✅ vs 대체(replace) ❌ 결정적 식별

### 2.5 격언 정합

- **격언 #52** baseline 6번째 사례 (Phase A vs Phase B 정합)
- **격언 #91 v2** 패턴 ④ Temporal Heterogeneity 첫 baseline
- **격언 #97 v2** (외부 audit 결정적 우위)
- **격언 #112 v2 #9 v2 룰 7** (Cross-Asset Risk Allocation 패러다임 정착 의무) 정합
- **격언 #112 v2 #9 v2 룰 8** (후속 연구 큐 보존 의무) 정합

---

## §3. 🆕 격언 #91 v2 패턴 ④ 첫 baseline 등재

### 3.1 패턴 ④ Temporal Heterogeneity 정의
**Phase A 평균 alpha (전체 기간)는 결정적 ≠ Phase B 슬롯 경쟁 alpha (특정 기간)**. 같은 시그널이라도 시기에 따라 alpha 방향이 결정적 反対로 나타나는 패턴.

### 3.2 S112 #1 결정적 입증 데이터

| α | P1 (2007-2016) ΔCAGR | P2 (2017-2021) ΔCAGR | MID (2022-2026) ΔCAGR |
|---|---------------------|---------------------|---------------------|
| 0.25 | **+1.188p** ✅ | -1.732p ❌ | -2.339p ❌ |
| 0.50 | **+2.331p** ✅ | -3.592p ❌ | -4.701p ❌ |
| 0.75 | **+3.428p** ✅ | -5.576p ❌ | -7.083p ❌ |
| 1.00 | **+4.479p** ✅ | -7.676p ❌ | -9.483p ❌ |

### 3.3 결정적 본질
P1 (GFC era) 결정적 alpha + P2/MID 결정적 negative → **단일 시그널의 시기별 결정적 反転** = 격언 #91 v2 4 패턴 中 ④번째 결정적 baseline 사례.

### 3.4 결정적 메커니즘 진단
- Crown #67 점진적 발전 과정에서 이미 VVIX 시그널 효과 **embedded capture**
- P1: GFC era에서 Crown 이전 메커니즘 부족 → VRC overlay 결정적 alpha
- P2/MID: Crown #67 자체가 cross-asset risk allocation 내장 → VRC 重복 negative

---

## §4. 🆕 메타 학습 3건 결정적 등재

### 4.1 메타 1: Crown 內 mechanism 重복 차단 결정적 의무

**본질**: Crown #67 baseline 자체가 이미 cross-asset risk allocation 내장
- VIX hysteresis (margin 1.0, 17.5/18.5)
- WTI gate (WTI>90 모든 자산 차단)
- entry_TLT WTI 면제 (격언 #48)
- WALCL/OAS ffill 등

→ 신규 overlay 형식의 effective alpha = 0 (또는 음수, 重복 차단)

### 4.2 메타 2: Temporal Heterogeneity 결정적 입증

**본질**: 시그널 alpha의 시기별 결정적 反転
- P1 결정적 + P2/MID 결정적 negative
- Phase A 평균값 의존 위험성 결정적 입증
- §B.9 v2 framework Phase 5 (α Sweep BT)에 P1/P2/MID 분리 검증 의무 신설

### 4.3 메타 3: Cross-Asset Overlay protocol 신설 의무

**본질**:
- Single-Asset Boost ❌ 패러다임 (격언 #112 v2 #9 v2 룰 4) 옳음
- 그러나 Cross-Asset Overlay도 Crown 內 重복 mechanism 차단 결정적 의무
- 신규 패러다임 등재 의무: **Crown 內 미存 mechanism만 채택**

---

## §5. 🆕 §B.9 v2 검증 framework 정합 등재

### 5.1 §B.9 v2 7-Phase framework (Cross-Asset Overlay 정합)

| Phase | 검증 | 결정적 기준 |
|-------|------|----------|
| 1 | VRC State Accuracy | t-stat > +5, transitions < 200회 |
| 2 | Defensive Sleeve Alpha | def-agg spread > +0.1%/day, t > +3.0 |
| 3 | Crown #67 Compatibility | overlay OFF → BT 동일 (변동 < 0.01p) |
| 4 | Alpha Preservation | avg ΔCAGR ≥ -0.5p (RULE 29 v2 룰 ①) |
| 5 | α Sweep + P1/P2/MID 분리 | 패턴 ③ robust plateau + temporal homogeneity |
| 6 | STRESS 14 Side Effect | 모든 시나리오 영향 < +1.0p |
| 7 | Final RULE 29 v2 Verdict | 6/6 PASS → 후보 / 1+ FAIL → REG NO-GO |

### 5.2 단일 자산 BT vs Cross-Asset Overlay 결정적 차이

| 차원 | 단일 자산 BT (§B.9 v1) | Cross-Asset Overlay (§B.9 v2) |
|------|---------------------|------------------------------|
| 변경 본질 | entry function 1개 | portfolio sleeve target 전환 |
| 영향 자산 | 1 ticker | 4+ defensive + 16+ aggressive sleeve |
| Slot 경쟁 | Top5 ranking 內 1자리 | sleeve 가중치 재분배 |
| Crown alpha 보존 | 변경 자산 外 영향 ❌ | Crown #67 Top5 alpha 重복 위험 |
| 검증 의무 | RULE 29 v2 | RULE 29 v2 + alpha 보존 + regime accuracy |

---

## §6. 결정적 후속 연구 큐 (격언 #112 v2 #9 v2 룰 8 정합)

| # | 작업 | 우선순위 | 근거 |
|---|------|--------|------|
| 1 | VRC + Crown #67 V_HYST 중복 제거 後 isolated alpha 측정 | 🟢 다음 cycle | VRC signal 자체 가치 분리 |
| 2 | 후보 #2 (Risk Budget Overlay continuous formula) 재검토 | 🟢 유망 | discrete overlay보다 덜 파괴적 구조 탐색 |
| 3 | Cross-Asset Overlay protocol v2 설계 | 🟡 후속 | 자동 회피 #10 반영 framework |
| 4 | Phase A causal v2.1 + Crown 內 mechanism cross-check protocol | 🟡 후속 | 메타 1 결정적 baseline |

---

## §7. SSOT 영구 등재 사항

### 7.1 자동 회피 목록 갱신
```
자동 회피 #1: ... (기존)
...
자동 회피 #9 v3: Single-Asset Boost 위험 (격언 #112 v2 #9 v2, S110#2)
🆕 자동 회피 #10 후보: Cross-Asset Overlay 등재 前 Crown 內 mechanism cross-check 의무
```

### 7.2 격언 #91 v2 baseline 사례 누적
```
패턴 ① noise: ... (기존 사례)
패턴 ② fitting + core-alpha: ... (기존 사례)
패턴 ③ robust plateau: ... (기존 사례)
🆕 패턴 ④ Temporal Heterogeneity: REG-S112_1 (VRC v0.1 P1 vs P2/MID 결정적 反転)
```

### 7.3 격언 #52 baseline 사례 누적
```
사례 1~5: (기존 5건)
🆕 사례 6: REG-S112_1 (VRC v0.1 Phase A t=+7.00 vs Phase B 모든 α NO-GO)
```

---

## §8. VRC signal 자체 보존 결정

🌟 **VRC signal 자체는 폐기하지 않음** — isolated alpha 연구 후보로 보존 🌟

근거:
1. Phase A 결정적 강도 (t=+7.00) 결정적 유의
2. P1 결정적 alpha (+1.19~+4.48p) 결정적 입증
3. Crown 內 V_HYST 重복 제거 後 isolated alpha 측정 cycle (후속 연구 큐 #1)

VRC v0.1 patch만 NO-GO — signal 본질은 후속 연구 cycle에서 isolated 검증 의무.

---

## §9. SSOT 정합 갱신 사항

| 항목 | 갱신 |
|------|------|
| SSOT 버전 | v1.10.206 → **v1.10.207** |
| 자동 회피 목록 | +#10 후보 신설 |
| 격언 #91 v2 baseline | 패턴 ④ 첫 사례 등재 |
| 격언 #52 baseline | 6번째 사례 등재 |
| §B.9 v2 framework | 7-Phase 정합 등재 |
| 메타 학습 | 3건 신설 |
| 후속 연구 큐 | 4건 신설 |

🌟 **Crown #67 LIVE 변경: 없음** (NO-GO, baseline 정합 보존)

---

## §10. 결정적 한 줄 결산 🦅

🌟 **"SSOT v1.10.207 ADDITION 결정적 등재 — S112 #1 (VRC v0.1 NO-GO) 결과 결정적 baseline 정착: 자동 회피 #10 후보 (Cross-Asset Overlay 等재 前 Crown 內 mechanism cross-check 의무) + 격언 #91 v2 패턴 ④ Temporal Heterogeneity 첫 baseline (P1 alpha ✅ vs P2/MID negative ❌) + 격언 #52 baseline 6번째 사례 (Phase A t=+7.00 vs Phase B 모든 α NO-GO) + §B.9 v2 7-Phase framework + 메타 학습 3건 + 후속 연구 큐 4건. VRC signal 자체 폐기 ❌ → isolated alpha 연구 후보 결정적 보존. Crown #67 LIVE 변경 없음 (TLT 100% 유지)."** 🦅

---

**Status**: ✅ SSOT v1.10.207 ACTIVE  
**Files 추가 등재**:
- `REG-S112_1_VRC_NO_GO.md` (결정적 NO-GO 등재)
- `PRIMA_v5_25_VRC.py` (NO-GO baseline 영구 보존)
- `PRIMA_VRC_OVERLAY_v0_1.py` (prelim 코드)
- `phase3_alpha_sweep_results.json` (실측 BT raw data)
- 본 문서 (`ARGUS_SSOT_ADDITION_v1_10_207.md`)
