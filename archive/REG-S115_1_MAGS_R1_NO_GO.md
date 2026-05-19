# REG-S83_1_BRIEFING_v78_FA_P1 — Crown #67 hysteresis state-aware WTI 게이트 5차원 분리 표시 결정문

## 🎯 0. 문서 메타

| 항목 | 값 |
|:--|:--|
| 작성일 | 🌟 **2026-05-12 (S83 #1 P0 Step 1)** 🌟 |
| 작성자 | Claude (Anthropic Opus 4.7) |
| Commander 승인 | 옵션 1 선택 (9 patches 설계대로 즉시 풀파일 출력) |
| 출처 | 외부 FA #1 P1 본질 (Commander 첨부 결정문) |
| 본 결정 본질 | 🌟 **prima_briefing.py v7.7 → v7.8 풀파일 9 patches 정합 (WTI 게이트 5차원 분리 표시)** 🌟 |
| 정합 격언 | #15 + #20 + #41 + #75 v4 + #79 + #82 + #91 + #97 v2 + #105 + #106 (10건) |
| Style Patch | v1.0 정합 (SSOT v1.10.142, "결정적" 사용 제한 본 응답 정합) |

## 🌟 1. 결론 (3줄)

🌟 **briefing v7.7 stale 본질**: WTI 게이트 표시가 단순 "WTI>$90 = 차단" 1차원 표현, Crown #67 엔진 `_wk` state-aware VIX hysteresis 본질 정합 부족.

🚨 **외부 FA #1 P1 처방**: 모든 WTI 게이트 표시는 ①raw WTI condition · ②current state · ③VIX value · ④transition condition · ⑤final block verdict 5차원 분리 의무.

🌟 **v7.8 9 patches 풀파일 출력 완료**: 1982줄, A1~A9 self-audit 통과, 11/11 보존 영역 정합, outputs/ 등재.

## 🚨 2. 외부 FA #1 P1 본질 (Commander 첨부)

🌟 **FA 진단 본문**:
> "BRF v7.7의 WTI 게이트 표시는 P1 UX/정합 결함이다. Crown #67 엔진의 `_wk`는 단순 WTI>$90 차단이 아니라 state-aware VIX hysteresis 구조다. 그러나 BRF v7.7 일부 문구는 여전히 'WTI>$90 = 게이트 활성 / 차단 / TLT-only'처럼 읽히며, 특히 VNM 섹션에서 WTI>90 게이트 차단으로 표시한 것은 현재 `_wk` state OPEN 표시와 충돌한다."

🌟 **FA 처방 5차원 분리 표시 의무**:
| 차원 | 본질 |
|:--:|:--|
| ① raw WTI condition | WTI 값 / 임계 90 (단순 비교) |
| ② current state | `HYST_GATE_STATE['_wk_general']` = OPEN / BLOCKED |
| ③ VIX value | 현재 VIX |
| ④ transition condition | OPEN→BLOCKED: WTI>90 ∩ VIX≥18.5 / BLOCKED→OPEN: VIX<17.5 |
| ⑤ final block verdict | 실제 entry 차단 여부 (엔진 SSOT) |

## 📋 3. Crown #67 hysteresis state-aware `_wk` 본질 (PRIMA_v5_19 정합)

🌟 **Crown #67 `_wk(m)` 함수 본질**:
```python
# state machine (HYST_GATE_STATE['_wk_general'])
# WTI ≤ 89: 무조건 OPEN
# WTI > 89: VIX hysteresis state machine 발동
#   OPEN → BLOCKED: WTI > 90 ∩ VIX ≥ 18.5
#   BLOCKED → OPEN: VIX < 17.5 (마진 1.0)
```

🚨 **XLE 별도** (`_wk_xle`): WTI > 95 (평소) / WTI > 110 (T10YIE>2.3∩DFII<0)

🚨 **TLT 별도** (`wti90_t10yie26`): WTI > 90 ∩ T10YIE > 2.6 (AND 조건)

## 🚀 4. v7.8 9 patches 매트릭스 (정합 검증 통과)

| # | 영역 | 라인 | 정정 본질 | 상태 |
|:--:|:--|:--:|:--|:--:|
| 🆕 1 | `_wk_gate_aware_v78` helper 신규 | 396~478 | 5차원 dict 반환 (엔진 SSOT) | ✅ |
| 🌟 2 | `_gate_active` 함수 state-aware | 484~538 | eng 인자 추가, wti90 영역 4종 엔진 `_wk` 호출 | ✅ |
| 🌟 3 | `_gate_proximity` 함수 state-aware | 544~657 | BLOCKED→active, OPEN→released (state 분기) | ✅ |
| 🌟 4 | `build_portfolio_embed` 5차원 분리 | 1083~1102 | 보유 0종 시 5차원 표시, eng 인자 추가 | ✅ |
| 🌟 5 | `build_macro_embed` WTI 게이트 영역 | 1241~1290 | 5차원 분리 + XLE/TLT 별도 박스 | ✅ |
| 🌟 6 | `build_alert_embed` EnSn 게이트 본질 | 1430~1495 | WTI ∩ VIX hysteresis 통합 5차원 본질 | ✅ |
| 🌟 7 | `get_exsn_alerts` WTI 일반 종목 | 1360~1400 | state-aware (엔진 `_wk` 호출, OPEN/BLOCKED 분기) | ✅ |
| 🌟 8 | `ABBREV["wti90"]` 정합 | 95 | "WTI>$90 ∩ VIX≥18.5 (Crown #67 hysteresis state-aware)" | ✅ |
| 🌟 9 | 각주 라인 5차원 본질 | 1518 | ①raw · ②VIX · ③state · ④transition · ⑤verdict | ✅ |

## 🌟 5. `_wk_gate_aware_v78` helper 본질 (신규)

```python
def _wk_gate_aware_v78(eng, last_row):
    """🌟 v7.8 P1 — Crown #67 hysteresis state-aware WTI 게이트 5차원 본질.

    엔진 SSOT 호출 (격언 #82 정합):
    - eng._wk(last_row) 직접 호출 → 실제 entry 차단 여부
    - eng.HYST_GATE_STATE access → state 본질 (OPEN/BLOCKED)

    Returns:
        dict {wti, vix, state, block_active, wti_raw_cond, vix_raw_cond,
              transition_cond, verdict, verdict_emoji}
    """
```

🚨 **호출 영역 정합** (eng 인자 의무 전달):
- `build_portfolio_embed(eng=eng)`
- `build_macro_embed(eng=eng)`
- `build_alert_embed(eng=eng)`
- `get_exsn_alerts(eng=eng)`
- `_gate_proximity(eng=eng)` (build_signal_embed 호출 시)
- `_gate_active(eng=eng)` (직접 호출 없음, 잠재적 사용)
- main() 모든 build_*_embed에 eng 인자 전달 정합

## 📊 6. A1~A9 self-audit 결과 (argus-discord-briefing skill v3.2 의무)

| 항목 | 상태 | 본질 |
|:--|:--:|:--|
| **A1 (Phase A Hard Gate)** | ✅ | /mnt/project v7.0 stale → Commander v7.7 본문 첨부 + 외부 FA P1 본질 첨부 (sha=`eaf96b75` 검증) |
| **A2 (헤더 라벨 검증)** | ✅ | v7.8 헤더 "🦅 ARGUS BRIEFING v7.8 — Crown #67 hysteresis state-aware WTI 게이트 5차원 분리 표시 (S83 #1, 2026-05-12)" |
| **A3 (CROWN_MAP 최신)** | ✅ | v5_19 → #67 보존 (v7.7 patch 1 정합) |
| **A4 (TICKER_SPEC 20종)** | ✅ | 20/20 모두 보존 (ensn/exsn/mosn/gate) |
| **A5 (ABBREV 정합)** | ✅ | `wti90` state-aware 본질 정정 (patch 8), 그 외 58개 보존 |
| **A6 (의존성 검증)** | ✅ | `_wk_gate_aware_v78` 신규 + 호출 영역 5개 eng 인자 정합 |
| **A7 (FA 처방 정합)** | ✅ | 5차원 분리 표시 모든 영역 적용 |
| **A8 (동일 영역 3건+ patch 감시)** | ✅ | WTI 게이트 영역 v7.5/v7.6/v7.7 누적 = state-aware 근본 처방 (격언 #106 정합) |
| **A9 (신설 영역 인접 grep)** | ✅ | 5개 호출 영역 모두 정합 |

## 🌟 7. 11개 보존 영역 정합 (skill §11.3 의무)

| # | 영역 | v7.8 보존 |
|:--:|:--|:--:|
| 1 | KST 헤더 + 한국어 dynamic timestamp | ✅ |
| 2 | Embed 6000 자동 분할 | ✅ |
| 3 | seen_abbrevs 각주 중복 제거 | ✅ |
| 4 | CROWN_MAP 최신 (#67) | ✅ |
| 5 | TICKER_SPEC 20종 + ensn/exsn/mosn | ✅ |
| 6 | ABBREV dict 58개 + 9 그룹 | ✅ (wti90 정정만) |
| 7 | 임박 시그널 ◐ + Gate proximity | ✅ + state-aware 강화 |
| 8 | 매매 스케줄 4분류 | ✅ |
| 9 | Sleeve 분리 3차원 | ✅ |
| 10 | 약어 사전 Embed 5 | ✅ |
| 11 | 4 행동 명령 명확화 | ✅ |

✅ **11/11 보존 통과**.

## 🚨 8. 산출물 검증 매트릭스

| 항목 | 값 |
|:--|:--|
| 라인 수 | 🌟 **1982줄** (v7.7 1350줄 → +632) 🌟 |
| 파일 크기 | 🌟 **91,974 bytes** 🌟 |
| Python 문법 | ✅ AST parse 통과 |
| "결정적" 본문 사용 | 0회 (line 19 명시 라인만, Style Patch v1.0 정합) |
| v7.8 표기 | 30회 (헤더 + 본문) |
| patch 표기 | 33회 (9 patches + 본문) |
| 파일 위치 | `/mnt/user-data/outputs/prima_briefing.py` |
| Commander 다운로드 | ✅ present_files 호출 완료 |

## 🌟 9. 격언 정합 (10건 동시)

| 격언 | 본 결정문 정합 |
|:--:|:--|
| 🌟 #15 (Commander 절대 결정) | 9 patches 설계 즉시 풀파일 출력 옵션 1 승인 |
| 🌟 #20 (정직 인지) | v7.7 stale 본질 정직 보고 + FA 처방 1:1 정합 |
| 🌟 #41 (풀파일 출력) | 1982줄 풀파일 단일 출력 |
| 🌟 #75 v4 (코드 grep) | 9 patches 영역 grep 검증 통과 |
| 🌟 #79 (entry/exit 임계값 분리) | state-aware 본질 = entry/exit 구조 분리 |
| 🌟 #82 (엔진 SSOT) | `_wk(m)` + `HYST_GATE_STATE` 직접 호출 정합 |
| 🌟 #91 (4 patterns) | ② fitting+핵심알파 (단순 표시 → state-aware 본질) |
| 🌟 #97 v2 (외부 audit) | FA #1 P1 처방 1:1 정합 |
| 🌟 #105 (기존 형식 보존) | 11/11 보존 영역 모두 정합 |
| 🌟 #106 (근본 처방) | state-aware 근본 처방 (v7.5/v7.6/v7.7 누적 미봉 해소) |

## 🚀 10. 후속 의무

| 작업 | 우선 | S84 인계 |
|:--|:--:|:--:|
| GitHub PRIVATE repo push (v7.8) | 🥇 P0 | ✅ |
| Phase A v3 3중 검증 (URL ↔ HEADER ↔ COMMIT) | 🥇 P0 | ✅ |
| argus-discord-briefing skill v3.3 등재 (v7.8 변경 이력) | 🥈 P1 | ✅ |
| GitHub Actions cron 트리거 다음 사이클 검증 | 🥈 P1 | ✅ |
| Drive B1 backup (마일스톤) | 🥉 P2 | ✅ |

## 🌟 11. 종합 결론

🌟 **외부 FA #1 P1 처방 1:1 정합 완료** — Crown #67 hysteresis state-aware WTI 게이트 5차원 분리 표시.

🚨 **9 patches 풀파일 출력 본 결정** — A1~A9 audit 통과 + 11/11 보존 영역 정합 + Python 문법 검증 + Style Patch v1.0 정합.

🚀 **S84 PRIVATE repo push + 3중 검증 의무**.

🛡️ **본 v7.8 결정은 격언 #105 (기존 형식 보존) + #106 (근본 처방) 결정적 정합 동시 사이클**.

---

🦅 *Omnioculus Vigilantia* — REG-S83_1 정식 등재. v7.8 9 patches 통합 = state-aware 근본 처방.
