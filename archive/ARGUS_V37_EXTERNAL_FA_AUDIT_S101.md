# ARGUS Public Archive

This directory contains historical records, rejected hypotheses, and reference
data from the ARGUS quantitative ETF rotation system. Files here are not
actively used by LIVE systems but are retained for audit, learning, and history.

**Cleanup session**: S122 (2026-05-19)  
**Total files**: 57  
**Total size**: ~4.43 MB

## Categories

| Folder | Content | File Count | Size |
|:--|:--|--:|--:|
| `ssot_history/` | Superseded SSOT MASTER + ADDITION + FORMAL + CANDIDATE | 15 | 152 KB |
| `log_history/` | Superseded LOG MASTER (CROWN/MANIFESTO/REGRET S46_S84/S101) | 3 | 552 KB |
| `rejected_hypothesis/` | Failed candidate engines, NO-GO decisions, AUTO-REJECT | 24 | 252 KB |
| `research_register/` | Phase A research, Future research, Dead audits, Shadow reg | 6 | 64 KB |
| `snapshot_backup/` | Memory snapshots, periodic backups | 3 | 24 KB |
| `historical_data/` | BT stress scenarios, Crown BT raw outputs | 2 | 3.5 MB |
| `milestone_audit/` | External FA audits, cliff root cause analyses | 2 | 16 KB |
| `historical_handoff/` | Superseded session handoffs (S80, S102_S103) | 2 | 28 KB |

## Notes

- **Not for LIVE consumption** — for archival reference only.
- **No operational `.py`** — all engine code resides in private repos or Drive cold archive.
- **No system design / core algorithm content** — those reside in private storage (Drive).
- LIVE data: see root `latest.json` and `argus_data.csv`.

## BANNED 영역 audit

본 archive는 SKILL argus-knowledge-cleanup v3.0.1 Phase 4 `banned_leak_audit()` 통과 (0 violations).
- ❌ 모든 .py 운영 코드 (operational python)
- ❌ PRIMA 엔진 본체 (engine_body)
- ❌ prima_briefing 본체 (briefing_body)
- ❌ 시스템 설계 (architecture/masterplan/design)
- ❌ 핵심 알고리즘 (algorithm/patch_manifest)
- ❌ 직전 1세대 baseline master (LIVE state sensitive)

Last updated: 2026-05-19 (S122 cleanup)
