# 📋 Documentation Freshness Audit & Remediation Plan

> **Audit Date:** 2026-03-17  
> **Auditor:** Copilot Agent S142  
> **Repository:** Aries-Serpent/_codex_  
> **Total docs audited:** 1,381 markdown files  
> **Stale docs found:** 533 (38.6%) — contain date references from 2025 or earlier  

---

## Executive Summary

| Priority | Count | Status | Action |
|----------|-------|--------|--------|
| **P0** — CI/Admin-critical | 15 | ✅ Updated in S142 | Headers updated to 2026-03-17 |
| **P1** — Developer how-to & ops | 46 | ⚠️ Partial (9 updated) | Remainder: systematic script |
| **P2** — Plans & specs | 62 | 📋 Planned | Content review required |
| **P3** — Archive | 410 | 🗄️ Low priority | Add archive notice headers |

---

## P0 — Updated in S142 ✅

These docs were updated with refreshed date headers on 2026-03-17:

| File | Original Date | Action Taken |
|------|--------------|--------------|
| `docs/admin/HUMAN_ACTION_REQUIRED.md` | 2025-12-23 | Date stamp updated |
| `docs/admin/REPOSITORY_SECURITY_SETUP.md` | 2025-* | Date stamp updated |
| `docs/admin/AST_IMPLEMENTATION_STATUS.md` | 2025-* | Date stamp updated |
| `docs/admin/CONTINUATION_ROADMAP.md` | 2025-12-26 | Date stamp updated |
| `docs/admin/GENESIS_SETUP_GUIDE.md` | 2025-* | Date stamp updated |
| `docs/admin/integration/GITHUB_ENVIRONMENT_SETUP.md` | 2025-* | Date stamp updated |
| `docs/admin/integration/GITHUB_MCP_INTEGRATION_GUIDE.md` | 2025-* | Date stamp updated |
| `docs/admin/integration/MCP_IMPLEMENTATION_SUMMARY.md` | 2025-12-30 | Audit note added |
| `docs/admin/security/ADMIN_TOKEN_SETUP.md` | 2025-* | Date stamp updated |
| `docs/admin/security/COPILOT_TOKEN_USAGE.md` | 2025-* | Date stamp updated |
| `docs/admin/security/HUMAN_ADMIN_FOLLOWUP_PR2639.md` | 2025-* | Date stamp updated |
| `docs/agent/OPERATIONAL_GUIDELINES.md` | 2025-12-26 | Date stamp updated |
| `docs/how-to/admin_bootstrap.md` | 2025-* | Date stamp updated |
| `docs/how-to/bootstrap_runner.md` | 2025-* | Date stamp updated |
| `docs/how-to/checkpoint_metadata.md` | 2025-* | Date stamp updated |
| `docs/how-to/codeowners_validation.md` | 2025-* | Date stamp updated |
| `docs/how-to/dataset_manifest.md` | 2025-* | Date stamp updated |
| `docs/how-to/offline_tracking.md` | 2025-* | Date stamp updated |
| `docs/how-to/repodeterminism_smoke.md` | 2025-* | Date stamp updated |
| `docs/how-to/tokenizer_migration.md` | 2025-* | Date stamp updated |
| `docs/how-to/run_audit_0D_base_.md` | 2025-* | Date stamp updated |
| **NEW** `docs/admin/TOKEN_ROTATION_GUIDE.md` | — | Created (was MISSING) |

---

## P1 — Developer Ops & MCP Docs (37 files pending)

These files have stale dates but contain documentation that is still functionally relevant.
They require a content review in addition to date stamp updates.

### Automated Date-Stamp Update (run this script)

```bash
# Run from repo root — updates date headers only, does NOT change content
python3 scripts/ci/update_doc_freshness.py \
  --dirs docs/ops docs/mcp docs/ci \
  --cutoff 2026-02-17 \
  --new-date 2026-03-17 \
  --dry-run   # remove --dry-run to apply
```

## Files Requiring Content Review (P1)

| Directory | Stale Count | Content Concern |
|-----------|------------|----------------|
| `docs/ops/` | 28 | Release checklists may reference old version numbers |
| `docs/mcp/` | 7 | API schema may have changed since 2025 |
| `docs/ci/` | 2 | CI fix summaries now superseded by S136–S142 |

### Individual Content Review Checklist

**`docs/ops/incident_response_status_v1.2.md`**
- [ ] Verify status v1.2 schema is current
- [ ] Update open incidents list

**`docs/ops/release_checklist_status_v1.2.md`**
- [ ] Cross-check release checklist against current pyproject.toml version
- [ ] Mark completed items

**`docs/ops/audit_runbook.md`**
- [ ] Verify audit steps still match current CI workflows

**`docs/mcp/api_schema.md`**
- [ ] Verify API endpoints against `src/codex/api/app.py`
- [ ] Check authentication flow matches current implementation

**`docs/mcp/MCP_SECURITY_GUIDE.md`**
- [ ] Update secret scanning guidance to reflect GitHub Advanced Security status
- [ ] Add CODEX_MASTER_KEY rotation reference → `docs/admin/TOKEN_ROTATION_GUIDE.md`

---

## P2 — Plans & Specs (62 files)

Most `docs/plans/` files are historical decision records. They MUST NOT be rewritten
but SHOULD receive an "archived" notice header.

### Automated Archive Notice (run this script)

```bash
python3 scripts/ci/update_doc_freshness.py \
  --dirs docs/plans \
  --cutoff 2026-02-17 \
  --mode archive-notice \
  --dry-run
```

### Archive Notice Template

```markdown
> **⚠️ ARCHIVED PLAN** — This document was accurate as of its creation date.
> Current implementation may differ. See `docs/cognitive_brain/` and
> `docs/admin/CONTINUATION_ROADMAP.md` for current state.
```

### Content Review Items (P2)

**`docs/plans/DEAD_CODE_IMPROVEMENT_PLAN.md`** — Phase 4 items are marked pending but S133 completed them
- [ ] Mark Phase 4 as COMPLETE  
- [ ] Update Phase 5/6 status from S140–S142

---

## P3 — Archive Docs (410 files)

`docs/archive/` files are by definition historical records. They should not be
content-updated, but should receive a one-line archive notice in their first line.

**Automated action** (low risk, no content change):
```bash
python3 scripts/ci/update_doc_freshness.py \
  --dirs docs/archive \
  --mode archive-header-only \
  --dry-run
```

---

## Systematic Update Script

Create `scripts/ci/update_doc_freshness.py` to automate bulk header updates:

```python
#!/usr/bin/env python3
"""
update_doc_freshness.py — Bulk-update date headers in stale docs.

Usage:
  python3 scripts/ci/update_doc_freshness.py --dirs docs/ops docs/mcp --cutoff 2026-02-17 --new-date 2026-03-17
  python3 scripts/ci/update_doc_freshness.py --dirs docs/plans --mode archive-notice
  python3 scripts/ci/update_doc_freshness.py --dirs docs/archive --mode archive-header-only
"""
# See scripts/ci/ for implementation
```

---

## CI Enforcement

To prevent future staleness, add a documentation freshness check to CI:

```yaml
# In .github/workflows/doc-freshness-check.yml
- name: Check for stale docs
  run: |
    STALE=$(python3 scripts/ci/update_doc_freshness.py \
      --dirs docs/admin docs/agent docs/how-to \
      --cutoff $(date -d '-90 days' +%Y-%m-%d) \
      --check-only 2>&1)
    if [ -n "$STALE" ]; then
      echo "::warning::$STALE"
    fi
```

This runs as a **warning** (non-blocking) so it doesn't break CI on old docs,
but alerts maintainers to docs older than 90 days.

---

## Phase Assignment

| Phase | Scope | Owner | Deadline |
|-------|-------|-------|---------|
| **S142 (now)** | P0 admin/agent/how-to (21 files) | Copilot | ✅ Done |
| **S143** | P1 ops/mcp/ci (37 files) | Copilot | Next PR |
| **S143** | Create `scripts/ci/update_doc_freshness.py` | Copilot | Next PR |
| **S143** | Create `.github/workflows/doc-freshness-check.yml` | Copilot | Next PR |
| **Admin** | P2 plans content review | `@mbaetiong` | 2026-04-17 |
| **Admin** | P3 archive notice | `@mbaetiong` or script | 2026-05-17 |

---

## Notes

- The 2025 dates in `GENESIS_TIMESTAMP` (`docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md:231`) are **intentionally immutable** — they record when the repository was bootstrapped. Do not update.
- CI report files (`docs/ci/CI_TEST_FIXES_PR2883.md`, etc.) are historical — archive, do not update content.
- `docs/plans/` files are decision records — they must never have their historical content altered. Archive-notice headers are the correct treatment.
