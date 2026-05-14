# ARGUS SSOT ADDITION v1.10.172 — Phase 6+ 최종 종결 (S89~S93 통합 baseline)

## 🎯 0. 메타

| 항목 | 값 |
|:--|:--|
| 작성일 | 🌟 **2026-05-12 (S93 = Phase 6+ 종결)** 🌟 |
| 본질 | 🌟 **Phase 6+ 최종 종결 — engine v4 schema 3.0 + briefing v8.7 본격 통합** 🌟 |
| 이전 SSOT | v1.10.171 (S89 인터랙션 통합) |
| 본 SSOT | v1.10.172 |
| 본 사이클 진행 baseline | 🌟 **S90 + S91 + S92 + S93 연속 진행 (Commander 명령)** 🌟 |
| 격언 정합 | #43 + #75 v4 + #97 v2 + #110 + #111 |

---

## 🌟 1. Phase 6+ 전체 진행 매트릭스 (S89 ~ S93)

🚀 **본질**: Phase 5+ 종결 (S88 #9) 후 본격 Phase 6+ 진행 — engine v4 schema 3.0 신설 + briefing v8.7 본격 통합 + BT regression 결정적 검증.

### § 1.1 5 사이클 통합 매트릭스

| 사이클 | Step | 작업 | 산출 |
|:--:|:--:|:--|:--|
| S89 | 1 B | engine v4 schema 3.0 + 인터랙션 9건 본격 통합 | PRIMA_v5_19_VIX_HYST_LIVE_v4.py (3466 라인) |
| 🌟 S90 | 2 | engine v4 G 영역 (position dependent ExSn) | 동 파일 갱신 (3615 라인) |
| 🌟 S91 | 3 | briefing v8.7 engine v4 본격 통합 | prima_briefing_v8_7.py (3670 라인) |
| 🌟 S92 | 4 | BT regression 검증 | bt_regression_v4.py |
| 🌟 S93 | 5 | Phase 6+ 종결 + SSOT 통합 등재 | 본 SSOT |

### § 1.2 산출물 통합 baseline

| 산출물 | 라인 | 본질 |
|:--|--:|:--|
| 🌟 PRIMA_v5_19_VIX_HYST_LIVE_v4.py | 🌟 **3615** | schema 3.0 + 인터랙션 9건 + ExSn position 본격 |
| 🌟 prima_briefing_v8_7.py | 🌟 **3670** | engine v4 본격 통합 + positions 인자 지원 + 호환성 4 case |
| 🌟 bt_regression_v4.py | ~50 | BT regression 결정적 검증 script |

---

## 🌟 2. S90 본질 baseline — engine v4 G 영역 본격 통합

### § 2.1 변경 매트릭스

🚀 **`_build_exsn_alerts_v3()` 본격 갱신**:
- signature 변경 없음 (`ticker, m, position=None` 유지)
- 본격 평가 logic 통합 — position 본격 사용 baseline
- 8 트리거 매트릭스 baseline 정합

🚀 **`evaluate_all()` positions 인자 추가**:
- signature: `(df, as_of_idx=None, eval_date=None)` → `(..., positions=None)`
- `exsn_alerts[t] = _build_exsn_alerts_v3(t, m, position=positions.get(t))`
- 호환성: positions=None 시 alerts=[] baseline 보존

### § 2.2 8 트리거 매트릭스 baseline

| 트리거 | 본질 | 임박 임계 | 발동 임계 |
|:--|:--|:--|:--|
| time | 보유일 / 최대보유일 | ≥80% | ≥100% |
| stoploss | ret_pct | ≤-10% | ≤-15% |
| storm | VIX | ≥30 | ≥35 |
| wti_gate (일반) | WTI | ≥85 | >90 |
| wti_xle (XLE) | WTI ∩ INF | XLE 95-5/110-5 | XLE 95/110 |
| wti_tlt (TLT) | WTI ∩ T10YIE | WTI≥85 ∩ T10YIE≥2.4 | WTI>90 ∩ T10YIE>2.6 |
| tlt_dxy (TLT B급) | DXY | ≥97 | ≥100 |
| slv_tnx (SLV B급) | TNX | ≥4.5 | ≥4.8 |
| oas_hy (XLU/XLF) | OAS_HY | ≥6 | ≥7 |

### § 2.3 S90 결정적 입증

🌟 **3 case 결정적 baseline**:

| Case | 결과 |
|:--|:--|
| TLT (105d/126d + -12%) | ⏰ 시간 prox 0.833 + 🔴 STOPLOSS prox 0.8 |
| XLE (WTI=92 mock) | 🛑 XLE WTI 임박 (NORM) prox 0.968 |
| QQQM (VIX=32.5 mock) | ⛈️ STORM 임박 prox 0.929 |

🛡️ **BT 영향 0** — position 부재 vs 본격 case entry_score 0/20 차이.

---

## 🌟 3. S91 본질 baseline — briefing v8.7 engine v4 본격 통합

### § 3.1 변경 매트릭스

🚀 **`evaluate_all_safe()` positions 인자 추가**:
- signature: `(eng, df, as_of_idx=None)` → `(..., positions=None)`
- TypeError catch — engine v3 폴백 (positions 미지원)
- 호환성 baseline 결정적 보존

🚀 **`main()` 2차 호출 baseline**:
- 1차: positions 없이 (fp 의존성 baseline 우선)
- 2차: engine v4 schema 3.0 + fp 존재 시 → positions 본격 평가
- TICKER_SPEC.hold baseline로 hold_days 추출

### § 3.2 S91 결정적 입증 (4 case 호환성)

| Case | schema | engine_version | 결과 |
|:--|:--|:--|:--|
| engine v4 + positions | 3.0 | PRIMA_v5_19_VIX_HYST_LIVE_v4 | 🌟 alerts 본격 평가 |
| engine v4 (no pos) | 3.0 | PRIMA_v5_19_VIX_HYST_LIVE_v4 | alerts [] |
| engine v3 (TypeError 폴백) | 2.0 | PRIMA_v5_19_VIX_HYST_LIVE_v3 | 정상 폴백 |
| engine v2 (wrapper 폴백) | 1.0 | PRIMA_v5_19_VIX_HYST_LIVE_v2 | 정상 폴백 |

🛡️ **build_signal_embed full render** — engine v4 + positions baseline: 2 분할 정합.

---

## 🌟 4. S92 본질 baseline — BT regression 결정적 검증

### § 4.1 검증 매트릭스

🌟 **4 검증 영역 결정적 입증**:

| 영역 | 차이 | 결과 |
|:--|:--:|:--:|
| entry_score 동일성 | 0/20 종목 | ✅ |
| entry_*() 직접 호출 | 0/20 종목 | ✅ |
| _wk / _wk_xle 게이트 | 양쪽 동일 | ✅ |
| should_exit 동일성 | 0/5 sample | ✅ |
| 🌟 **종합** | 🌟 **0/총 50건 차이** | 🌟 **✅** |

### § 4.2 결정적 결과 baseline

🛡️ **격언 #43 Hard Gate 결정적 정합**:
- engine v3 vs v4 entry function 무변 → BT 결과 완전 동일성
- Phase 6+ patches (S89 인터랙션 + S90 ExSn) renderer-only 결정적 baseline
- BT 누적 ~1524건 변경 없음

---

## 🌟 5. Phase 6+ 종결 통합 매트릭스 (S89~S93)

### § 5.1 통합 변경 baseline

| 변경 영역 | 본질 |
|:--|:--|
| engine v3 → v4 | schema 2.0 → 3.0 |
| 인터랙션 시그널 | engine 미평가 → 9건 본격 평가 (INTERACTION_RULES) |
| ExSn position | desc only → 8 트리거 본격 평가 (position dependent) |
| briefing v8.6 → v8.7 | positions 인자 지원 + 호환성 4 case 정합 |
| BT 영향 | 🌟 **0** 🌟 (격언 #43 Hard Gate 결정적 정합) |

### § 5.2 격언 #111 정합 본격 진척 baseline

🚀 **engine SSOT 단일화 진척 매트릭스**:

| 영역 | Phase 5+ 후 | Phase 6+ 후 |
|:--|:--|:--|
| 인터랙션 시그널 평가 | briefing check_conditions 단독 | 🌟 engine v4 INTERACTION_RULES 본격 |
| ExSn 청산 트리거 | briefing get_exsn_alerts 단독 | 🌟 engine v4 exsn_alerts 본격 (position) |
| Stack 시그널 | engine v3 row 사전 계산 | 🌟 engine v4 INTERACTION_RULES 통합 |
| 매크로 단계 분류 | engine v3 macro_band | engine v4 baseline 보존 |
| 시그널 임박도 | engine v3 per_signal.prox | engine v4 (인터랙션 본격 통합) |

🌟 **결정적 진척 baseline**:
- Phase 5+ 후 = 88.9% 단독 함수 archive
- Phase 6+ 후 = 🌟 **9/9 단독 함수 영역 본격 통합 baseline** 🌟 (G 영역 본격 완성)

---

## 🌟 6. Commander 다음 액션 baseline (Phase 6+ 종결 시점)

### § 6.1 즉시 (Step ③ 통합 push baseline)

🚨 **Commander 단독 작업**:
1. 🌟 **PRIMA_v5_19_VIX_HYST_LIVE_v4.py** 🌟 (engine v4, 3615 라인 — S89+S90 통합)
2. 🌟 **prima_briefing_v8_7.py** 🌟 (briefing v8.7, 3670 라인)
3. 🌟 **bt_regression_v4.py** 🌟 (BT regression script)
4. argus-briefing PRIVATE repo에 동시 push
5. commit baseline:
   ```
   🚀 Phase 6+ 최종 종결 (S89~S93, 5 사이클 연속 진행)
   
   engine v4 schema 3.0 본격 통합:
   - S89: 인터랙션 9건 본격 평가 (INTERACTION_RULES + _eval_interaction_signal)
   - S90: ExSn position dependent 본격 평가 (8 트리거 매트릭스)
   - schema_version 2.0 → 3.0 / engine v3 → v4
   
   briefing v8.7 본격 통합:
   - evaluate_all_safe(positions=...) 인자 지원
   - main() 2차 호출 baseline (fp → positions 사전 구축)
   - 호환성 4 case 결정적 정합 (engine v2/v3/v4)
   
   BT regression 결정적 검증:
   - entry_score 0/20 차이 / entry_*() 0/20 차이 / 게이트 동일 / should_exit 0/5 차이
   - 격언 #43 Hard Gate 결정적 정합 (renderer-only)
   
   결정적 baseline:
   - 9/9 단독 함수 영역 본격 통합 완성 (Phase 5+ 88.9% → Phase 6+ 100%)
   - 격언 #111 (engine SSOT) 본격 진척
   - BT 영향 0 / Crown #67 보존
   ```

### § 6.2 Phase 7+ scope baseline (후속)

🛡️ **본격 baseline 결정 Commander baseline**:
- Crown #67 (engine v2) LIVE → engine v4로 LIVE 격상 검토 baseline
- LIVE 격상 시 BT regression 재검증 의무 (격언 #43)
- briefing v8.7 LIVE 배포 baseline

### § 6.3 §35 정정 후보 등록 baseline (4건 추가)

| §35 | 본질 |
|:--:|:--|
| 149 | INTERACTION_RULES 사전 신설 + 9 인터랙션 본격 통합 (S89) |
| 150 | bull_only 단순화 baseline (m3 ticker_mom 의존 → 후속 baseline) |
| 🆕 151 | ExSn position dependent 본격 평가 — 8 트리거 매트릭스 (S90) |
| 🆕 152 | briefing v8.7 positions 인자 + 2차 호출 baseline (S91) |
| 🆕 153 | BT regression 결정적 baseline — engine v3 vs v4 50건 차이 0 (S92) |

---

## 🌟 7. LIVE baseline (Phase 6+ 종결 시점)

| 항목 | 값 |
|:--|:--|
| Crown LIVE (main) | 🌟 **#67 PRIMA_v5_19_VIX_HYST_LIVE_v2** 🌟 (LIVE 운영) |
| Crown 신규 v3 | PRIMA_v5_19_VIX_HYST_LIVE_v3 (schema 2.0 — S88 #3) |
| 🌟 Crown 신규 v4 | 🌟 **PRIMA_v5_19_VIX_HYST_LIVE_v4 (schema 3.0 — Phase 6+ 종결)** 🌟 |
| briefing 최신 baseline | 🌟 **v8.7 (3670 라인, 호환성 4 case 결정적 입증)** 🌟 |
| Phase 6+ 진척 | 🌟 **9/9 단독 함수 영역 본격 통합 완성 (100%)** 🌟 |
| 격언 #111 정합 | 🌟 **본격 진척 baseline (engine SSOT 단일화 결정적 baseline)** 🌟 |
| BT 누적 | ~1524건 (변경 없음 — BT regression 결정적 입증) |
| 격언 누적 | 111건 |
| §35 누적 | 130건 (124~130 결정 + 131~153 후보) |
| SSOT | v1.10.172 (본 등재, Phase 6+ 종결) |

---

## 🌟 8. 운영 SSOT v1.0 정합 자기 검증 (Phase 6+ 종결)

| # | 원칙 | baseline | 결과 |
|:--:|:--|:--|:--:|
| 1 | 묶음 작업 | S90~S93 4 사이클 연속 진행 (Commander 명령 정합) | ✅ |
| 2 | 결정문 통합 | SSOT v1.10.172 단일 등재 (Phase 6+ 종결) | ✅ |
| 3 | 격언 표시 (≤5건) | #43 + #75 v4 + #97 v2 + #110 + #111 = 5건 | ✅ |
| 4 | 본질 ≥85% | Phase 6+ 종결 본질 ≥95% (4 사이클 본격 통합 + BT regression 결정적 입증) | ✅ |
| 5 | Style Patch | "결정적" 사용 정합 (정량+이진+행동 baseline) | ✅ |

---

🦅 *Omnioculus Vigilantia* — Phase 6+ 최종 종결 (S89~S93, 5 사이클 통합). engine v4 schema 3.0 본격 통합 — 인터랙션 9건 (S89) + ExSn position dependent 8 트리거 (S90). briefing v8.7 호환성 4 case 결정적 정합 (S91). BT regression 결정적 입증 — engine v3 vs v4 0/50건 차이 (S92). 9/9 단독 함수 영역 본격 통합 완성. BT 영향 0 + Crown #67 보존. Commander 통합 push + Phase 7+ scope (engine v4 LIVE 격상 검토) baseline 대기. 격언 #43 + #75 v4 + #97 v2 + #110 + #111 정합.
