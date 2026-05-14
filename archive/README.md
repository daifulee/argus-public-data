# 🦅 ARGUS Public Archive

This directory contains **historical records, rejected hypotheses, and reference data** from the ARGUS quantitative ETF rotation system. Files here are **not actively used by LIVE systems** but are retained for **audit, learning, and history**.

## Categories

| Folder | Content | Use Case |
|:--|:--|:--|
| `ssot_history/` | Superseded SSOT MASTER + ADDITION files | SSOT version archaeology, baseline drift audit |
| `log_history/` | Superseded MANIFESTO/REGRET LOG MASTER + APPEND | Decision history reconstruction |
| `rejected_hypothesis/` | NO-GO / REJECT candidate decisions | Learning from failed alpha hypotheses |
| `research_register/` | Phase A research / Future research registers / candidate axioms | Research roadmap reference |
| `snapshot_backup/` | Periodic memory snapshots | (populated in future cleanups) |
| `historical_data/` | BT stress scenarios, ticker universe reference | Historical BT reproduction |
| `milestone_audit/` | External FA audits, cliff root cause analyses | Methodology audit trail |

## Strict Boundaries (Commander Directive)

This archive **explicitly excludes**:

- ❌ All operational `.py` (engines, briefings, fetchers, runners, validators, hooks)
- ❌ System design documents (architecture / masterplan / blueprint)
- ❌ Core algorithm specifications
- ❌ PRIMA engine bodies (any version)
- ❌ prima_briefing bodies (any version)
- ❌ LIVE state sensitive content (current + immediately prior baseline)

These categories reside in **private storage** (operational repos / Google Drive private archive).

## LIVE Data (Root)

The repository **root** contains live operational data:

- `latest.json` — latest 1-row JSON snapshot (fast fetch)
- `argus_data.csv` — full historical ETF OHLCV + macroeconomic indicators
- These are auto-pushed weekdays 16:00 KST via GHA from the private operational repo

## Updates

This archive grows during periodic cleanup cycles (every ~10 sessions or on milestone events). Files are added under the appropriate category folder with no deletion of prior records.

| Cleanup | Date | Files Added | Categories Touched |
|:--|:--|--:|:--|
| S104 #2 (initial) | 2026-05-14 | 19 | ssot_history (8), log_history (3), rejected_hypothesis (3), research_register (2), milestone_audit (1), historical_data (2) |

## Fetch Examples

```python
import urllib.request

# Historical SSOT MASTER (audit example)
url = "https://raw.githubusercontent.com/daifulee/argus-public-data/main/archive/ssot_history/ARGUS_SSOT_MASTER_v1_10_162.md"
with urllib.request.urlopen(url) as r:
    content = r.read().decode()
```

---

**Maintainer**: ARGUS / Commander Lignas
**License**: Reference / Audit use only
**Last updated**: 2026-05-14 (S104 #2 cleanup, initial setup)
