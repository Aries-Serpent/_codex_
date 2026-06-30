# Archive Policy for _codex_ Documentation

**Authority:** Phase 5 Execution Mandate (@mbaetiong)  
**Effective Date:** 2026-07-03  
**Version:** 1.0 (Phase 2 Initial)  
**Status:** Active

---

## 1. Introduction & Scope

This policy defines the criteria, procedures, and governance for archiving documentation and historical content in the _codex_ repository. It ensures that:

- **Active documentation** remains current, discoverable, and relevant
- **Historical content** is preserved for reference without cluttering the active codebase
- **Phase transitions** proceed smoothly with clear archival markers
- **Link validity** is maintained at 97.5%+ as broken archives are properly marked

### Applicable Content

- Phase-completed planning and specification documents
- Superseded implementation guides
- Historical CI/CD workflows and agent artifacts
- Deprecated code examples and tutorials
- Meeting notes and retrospectives

---

## 2. Archive Criteria

### 2.1 Automatic Archival Triggers

Content **MUST** be archived when:

| Criterion | Timeline | Action |
|-----------|----------|--------|
| **Phase Completion** | Upon phase closure | Move all phase-specific planning docs to `archive/phases/` |
| **Superseded Documentation** | Upon replacement | Move old version to `archive/superseded_docs/` with link redirect |
| **Deprecated Features** | Upon deprecation notice (30 days) | Move to `archive/deprecated/` with migration guide |
| **Historical Records** | 6+ months old AND no recent references | Move to `archive/historical/` |
| **Stale Planning Docs** | No updates in 90 days AND phase not active | Review for archival |

### 2.2 Archive Exemptions (Keep Active)

The following content is **NEVER archived** (always active):

- `README.md` and critical path documentation (100% validity maintained)
- `docs/index.md` and navigation structure
- Current phase planning (Phases 1-3 in active work)
- Security and compliance documentation
- Architecture and design patterns (evergreen)
- API documentation for public interfaces

---

## 3. Archive Directory Structure

All archived content uses this hierarchical structure under `.codex/archive/`:

```
.codex/archive/
├── phases/
│   ├── phase_1/
│   ├── phase_2/
│   ├── phase_3/
│   ├── phase_4/
│   └── [completed_phases]/
├── superseded_docs/
│   ├── README.md (index of what was superseded)
│   └── [old_version_files]/
├── deprecated/
│   ├── deprecated_features.md (master index)
│   └── [feature_specific_docs]/
├── historical/
│   ├── historical_index.md
│   ├── meetings/
│   ├── retros/
│   └── experiments/
├── sessions/
│   └── [session_artifacts]/
└── index.md (master archive registry)
```

---

## 4. Archive Procedures

### 4.1 Pre-Archive Checklist

Before archiving any content:

- [ ] Update all inbound links to point to new archive location (or redirect)
- [ ] Create `<!-- NOTE: Archived on [DATE] - See .codex/archive/... -->` marker in original
- [ ] Add entry to appropriate archive index file
- [ ] Update `.codex/archive/index.md` with new entry
- [ ] Run link validator to confirm no broken links introduced
- [ ] Verify critical path documents still 100% valid

### 4.2 Archival Steps

1. **Create redirects** in source file:
   ```markdown
   <!-- ARCHIVED: This document has been moved to .codex/archive/phases/phase_11/ -->
   <!-- Last active: 2026-06-30 -->
   <!-- See: .codex/archive/index.md for archive navigation -->
   ```

2. **Move the file** to appropriate archive directory:
   ```bash
   mv docs/archive/phases/PHASE_11_X.md .codex/archive/phases/phase_11/PHASE_11_X.md
   ```

3. **Update archive index** (see Section 5 for index formats)

4. **Update any active references** to redirect to archive location:
   - In other docs: Change links to point to archive
   - In navigation: Remove from active nav, add to archive nav

5. **Validate** no broken links introduced:
   ```bash
   python3 link_validator_v2.py
   # Confirm: link_validity >= 97.5%
   ```

### 4.3 Bulk Archival (Phase Transitions)

When completing a phase, use bulk archival:

```bash
# Phase completion example (Phase 11 → Archive)
mkdir -p .codex/archive/phases/phase_11/

# Move all phase docs
find docs/archive/phases/ -name "PHASE_11*" -exec mv {} .codex/archive/phases/phase_11/ \;

# Add manifest
echo "# Phase 11 Archive - Completed [DATE]" > .codex/archive/phases/phase_11/MANIFEST.md

# Update master index
# (append entry to .codex/archive/index.md)
```

---

## 5. Recovery Procedures

### 5.1 Finding Archived Content

Users can discover archived content through:

1. **Master Archive Index** (`.codex/archive/index.md`)
   - Searchable list of all archived content
   - Organized by category (phases, deprecated, historical)
   - Links to specific archive subdirectories

2. **Archive Category Indexes**
   - `.codex/archive/phases/README.md` — Phase archives
   - `.codex/archive/superseded_docs/README.md` — Superseded versions
   - `.codex/archive/deprecated/deprecated_features.md` — Deprecated features
   - `.codex/archive/historical/historical_index.md` — Historical content

3. **Git history** (fallback)
   ```bash
   git log --follow -- docs/old_file.md
   git show COMMIT:docs/old_file.md > recovered_file.md
   ```

### 5.2 Restoring Archived Content

If archived content is needed again:

1. **Review restoration criteria:**
   - Is there an updated/replacement version? Use that instead.
   - Is this for historical/compliance purposes? Link from archive.
   - Is this feature being re-implemented? Copy from archive and update.

2. **If restoration is appropriate:**
   ```bash
   # Copy from archive to active docs
   cp .codex/archive/deprecated/old_feature.md docs/reference/old_feature.md
   
   # Update the reference in archive as "restored" with pointer
   ```

3. **Update indexes** to reflect restoration

### 5.3 Archive Retention Policy

- **Phase archives**: Keep indefinitely (compliance/audit trail)
- **Superseded docs**: Keep 2+ versions for comparison
- **Deprecated features**: Keep 1 year past deprecation date
- **Historical records**: Keep 2-3 years minimum

---

## 6. Index Maintenance Templates

### 6.1 Master Archive Index Template

File: `.codex/archive/index.md`

```markdown
# _codex_ Archive Master Index

**Last Updated:** [DATE]  
**Total Archived Items:** [COUNT]  
**Archive Size:** [SIZE] (git du)

## By Category

### Phase Archives
| Phase | Archived | Items | Link |
|-------|----------|-------|------|
| Phase 11 | 2026-07-15 | 28 | [archive/phases/phase_11/](phases/phase_11/) |

### Superseded Documentation
[List of versioned docs]

### Deprecated Features
[List of deprecated features]

### Historical Records
[Meeting notes, retros, experiments]
```

### 6.2 Phase Archive Manifest Template

File: `.codex/archive/phases/phase_N/MANIFEST.md`

```markdown
# Phase N Archive Manifest

**Phase:** N  
**Completed:** [DATE]  
**Status:** ✅ ARCHIVED  
**Duration:** [START] to [END]

## Contents (N items)
- PHASE_N_MASTER_PLAN.md
- PHASE_N_WEEKLY_REPORT.md
- [Other docs...]

## Key Achievements
- [Achievement 1]
- [Achievement 2]

## Restoration
See parent: `.codex/archive/phases/README.md`
```

---

## 7. Quarterly Maintenance Schedule

| Quarter | Task | Owner | Effort |
|---------|------|-------|--------|
| Q1/Q3 | Review phase archives for compliance | Archive Guardian | 30 min |
| Q2/Q4 | Audit link validity in active + archive | Doc Agent | 1 hour |
| Monthly | Review newly deprecated features | Feature Owners | 15 min |
| Every 6mo | Review historical record retention | Archive Guardian | 30 min |

---

## 8. Examples & Use Cases

### Example 1: Phase 11 Completion

**Scenario:** Phase 11 completes on 2026-07-15

**Actions:**
1. Create directory: `.codex/archive/phases/phase_11/`
2. Move all `PHASE_11_*.md` files from `docs/archive/phases/` to new directory
3. Add manifest explaining what was in Phase 11
4. Update `.codex/archive/index.md` with entry:
   ```
   | Phase 11 | 2026-07-15 | 28 files | AI Architect + Governance | archive/phases/phase_11/ |
   ```
5. Update any active docs that reference Phase 11 planning to link to archive
6. Run link validator: confirm ≥97.5% validity

### Example 2: Superseding a Guide

**Scenario:** Old API guide replaced by new comprehensive guide

**Actions:**
1. Rename old file: `docs/api/API_GUIDE_V1.md` → `docs/api/API_GUIDE_CURRENT.md`
2. Move old to archive: `mv docs/api/API_GUIDE_V1.md .codex/archive/superseded_docs/API_GUIDE_V1.md`
3. Add redirect comment in original location:
   ```
   <!-- This document has been superseded by docs/api/API_GUIDE_CURRENT.md -->
   <!-- Archive: .codex/archive/superseded_docs/API_GUIDE_V1.md -->
   ```
4. Update any links in docs to point to new guide, not old
5. Add entry to superseded_docs index

### Example 3: Deprecating a Feature

**Scenario:** Old feature marked for deprecation

**Actions:**
1. Add deprecation notice to feature docs:
   ```
   ⚠️ **DEPRECATED (2026-06-01):** This feature is deprecated as of Phase X.
   [Replacement feature / migration guide]
   ```
2. Schedule archival for 2026-09-01 (90 days)
3. On deprecation date + 90 days: Move to `.codex/archive/deprecated/`
4. Update deprecated_features index with deprecation info

---

## 9. Governance & Escalation

### 9.1 Archive Guardian Role

Responsibilities:
- Quarterly maintenance of archive structure
- Evaluation of archival candidates
- Ensuring archive indexes stay current
- Link validation in archived content

### 9.2 Escalation Path

**Escalate to @mbaetiong if:**
- Archive becomes >50% of `docs/` size (space management issue)
- More than 3 items require restoration (suggests over-archival)
- Archive link validity drops below 95% (recovery procedures not working)
- Policy needs major revision

---

## 10. Success Metrics

| Metric | Target | Review Freq |
|--------|--------|-------------|
| **Active doc freshness** | 100% of active docs ≤90 days old | Monthly |
| **Archive link validity** | 97.5%+ | Monthly |
| **Critical path validity** | 100% always | Every push |
| **Archive discoverability** | <2 minutes to find any archived item | Quarterly |
| **Restoration time** | <5 minutes if needed | Ad-hoc |

---

## 11. Change Log

| Version | Date | Changes | Authority |
|---------|------|---------|-----------|
| 1.0 | 2026-07-03 | Initial policy document | Phase 5 Mandate |

---

## References

- Phase 5 Brief: `.codex/PHASE_5_DOC_AGENT_BRIEF_PHASE2.md`
- Link Validation Reports: `.codex/PHASE_5_LINK_STATUS_*.md`
- Archive Index: `.codex/archive/index.md`

---

**Policy Owner:** Unified Documentation Agent v1.0 (M-02 Merge)  
**Last Reviewed:** 2026-07-03  
**Next Review:** 2026-10-03 (Q4 checkpoint)
