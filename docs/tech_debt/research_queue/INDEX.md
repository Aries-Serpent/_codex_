# Research Queue Index — PR #3344 (S66)

**Last Updated**: 2026-06-22
**Total Questions**: 5
**Resolved**: 0
**Awaiting Research**: 5

---

## By Priority

### 🔴 High Priority
| ID   | Title                                         | Impact | Status               |
|------|-----------------------------------------------|--------|----------------------|
| Q001 | `_emit_provenance_summary` stdout vs stderr   | High   | ⏳ Awaiting Research |
| Q002 | `TestManageTenantIndices` root cause          | High   | ⏳ Awaiting Research |

### 🟡 Medium Priority
| ID   | Title                                              | Impact | Status               |
|------|----------------------------------------------------|--------|----------------------|
| Q003 | `IncrementalSyncDecider` 95% change ratio          | Medium | ⏳ Awaiting Research |
| Q004 | Multi-output CLI JSON testing pattern              | Medium | ⏳ Awaiting Research |
| Q005 | `audit_runner.py` full vs minimal output env flags | Medium | ⏳ Awaiting Research |

---

## By Category

| Category             | Questions        |
|----------------------|------------------|
| Bug Root Cause       | Q002, Q003       |
| API Design/Contract  | Q001, Q004       |
| Compatibility        | Q005             |

---

## Related Deep Research Patterns (DRQ)
See `.codex/plans/deep_research_ci_failure_patterns_S58_S66.md` for systemic patterns:
- DRQ-001: API drift (affects Q002)
- DRQ-005: Multi-output CLI parsing (affects Q001, Q004)
- DRQ-007: Integration tests assume full subprocess output (affects Q005)
