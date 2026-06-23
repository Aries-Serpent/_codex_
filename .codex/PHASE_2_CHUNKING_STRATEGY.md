# Phase 2.1 & 2.2: Accountability Report Chunking Strategy

**Status:** Active  
**Date:** 2026-06-23  
**Total Sessions:** 316 (S228-S543 equivalent range)  
**Chunk Target:** 10 sessions per chunk = 32 groups  
**GitHub Render Limit:** <256 KB per file

---

## 1. Chunking Design

### 1.1 Approach

Split the monolithic 66K-line `AGENT_ACCOUNTABILITY_REPORT.md` into:

- **32 chunks** (groups of 10 sessions per file)
- **Sequential numbering:** 01-32 (left-padded for sorting)
- **Storage:** `.codex/accountability_chunks/` directory
- **Index:** `.codex/AGENT_ACCOUNTABILITY_REPORT_INDEX.md` (root pointer)
- **Naming:** `AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_NN.md`

### 1.2 Session Grouping

| Group | Sessions | Range | File |
|-------|----------|-------|------|
| 01 | 10 sessions | 1-10 | `AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_01.md` |
| 02 | 10 sessions | 11-20 | `AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_02.md` |
| ... | ... | ... | ... |
| 31 | 10 sessions | 301-310 | `AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_31.md` |
| 32 | 6 sessions | 311-316 | `AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_32.md` |

**Total:** 316 sessions across 32 files

### 1.3 Session Ordering

- **Primary:** Chronological by `timestamp` field (oldest → newest)
- **Fallback:** Session ID lexicographic order if timestamps are missing
- **Preservation:** Maintain exact order from `sessions_index.json`

### 1.4 File Size Guarantee

Each chunk will:
- Contain exactly 10 sessions (except final chunk with 6)
- Include navigation headers/footers
- Stay well below GitHub 256 KB render limit (estimated ~20-30 KB per chunk)

---

## 2. Migration Path

### 2.1 Backup Strategy

Before migration:
1. Backup original report: `.codex/archive/AGENT_ACCOUNTABILITY_REPORT_BACKUP_20260623.md`
2. Maintain all session data verbatim
3. Preserve formatting and metadata

### 2.2 Directory Structure

```
.codex/
├── PHASE_2_CHUNKING_STRATEGY.md          # This document
├── AGENT_ACCOUNTABILITY_REPORT_INDEX.md  # Root index (replaces original)
├── accountability_chunks/                # New directory for chunks
│   ├── AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_01.md
│   ├── AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_02.md
│   ├── ...
│   └── AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_32.md
├── archive/
│   └── AGENT_ACCOUNTABILITY_REPORT_BACKUP_20260623.md
└── ...

docs/
├── accountability/
│   └── AGENT_ACCOUNTABILITY_REPORT.md  # Redirect stub to index
└── ...
```

### 2.3 Replacement Strategy

After chunks are generated:

1. Backup original to archive
2. Move chunk files to `.codex/accountability_chunks/`
3. Create index file at `.codex/AGENT_ACCOUNTABILITY_REPORT_INDEX.md`
4. Replace `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` with redirect stub
5. Update all internal cross-references to point to index

---

## 3. Naming Convention

### 3.1 Rationale

- **Sequential numbering:** Ensures consistent sorting across tools
- **Left-padding:** `01`, `02`, `...`, `32` for natural file system ordering
- **Clear boundaries:** Group 01 = Sessions 1-10, Group 02 = Sessions 11-20, etc.
- **Descriptive suffix:** `SESSION_GROUP_NN` makes purpose self-evident

### 3.2 Format

```
AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_NN.md
```

Where:
- `NN` = 01-32 (left-padded)
- Example: `AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_01.md`

---

## 4. Index File Structure

### 4.1 Location

- **File:** `.codex/AGENT_ACCOUNTABILITY_REPORT_INDEX.md`
- **Purpose:** Central navigation hub for all chunks
- **Access:** Quick link from docs and project root

### 4.2 Template

```markdown
# Agent Accountability Report — Session Index

> **Note:** The monolithic AGENT_ACCOUNTABILITY_REPORT.md has been split into session 
> groups for GitHub rendering compatibility. All 316 sessions are preserved in 32 chunks.

## Quick Navigation

- **Latest Sessions:** [Group 32](accountability_chunks/AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_32.md) 
  (Sessions 311-316, 2026-06-22 to 2026-06-23)
- **Search Sessions:** Use [session_query.py](../../scripts/ci/session_query.py) for complex queries
- **Original Backup:** [Backup](archive/AGENT_ACCOUNTABILITY_REPORT_BACKUP_20260623.md)

## Session Groups (All 32)

| Group | Sessions | Link | Date Range | Status |
| --- | --- | --- | --- | --- |
| Group 32 | 311-316 | [View](accountability_chunks/AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_32.md) | 2026-06-22 to 2026-06-23 | Active |
| Group 31 | 301-310 | [View](accountability_chunks/AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_31.md) | 2026-06-20 to 2026-06-22 | Archived |
| Group 30 | 291-300 | [View](accountability_chunks/AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_30.md) | 2026-06-18 to 2026-06-20 | Archived |
| ... | ... | ... | ... | ... |
| Group 02 | 11-20 | [View](accountability_chunks/AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_02.md) | [Date] | Archived |
| Group 01 | 1-10 | [View](accountability_chunks/AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_01.md) | [Date] | Archived |

## Navigation by Date Range

Use this table to find sessions by date:

| Date | Group(s) |
| --- | --- |
| 2026-06-22 to 2026-06-23 | [32](accountability_chunks/AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_32.md) |
| 2026-06-20 to 2026-06-22 | [31](accountability_chunks/AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_31.md) |
| ... | ... |

## Migration Notes

- ✅ **Original file backed up** to `.codex/archive/AGENT_ACCOUNTABILITY_REPORT_BACKUP_20260623.md`
- ✅ **All session data preserved** — No modifications to session content
- ✅ **Backward compatibility** — Index provides central navigation point
- ✅ **Query support** — Use `session_query.py` for advanced searches

## Statistics

- **Total Sessions:** 316
- **Total Groups:** 32
- **Average Sessions per Group:** 10
- **Final Group Sessions:** 6 (Sessions 311-316)
- **Average File Size:** ~20-30 KB per chunk
- **Total Size:** ~750 KB (distributed across 32 files)

## Scripts & Utilities

| Script | Purpose |
| --- | --- |
| [generate_accountability_chunks.py](../../scripts/ci/generate_accountability_chunks.py) | Generate chunks from sessions_index.json |
| [session_query.py](../../scripts/ci/session_query.py) | Search and filter sessions |
| [validate_chunks.py](../../scripts/ci/validate_chunks.py) | Validate chunk integrity and coverage |

---

## 5. Chunk File Structure

### 5.1 Header

Each chunk file starts with navigation and metadata:

```markdown
# Agent Accountability Report — Session Group NN

**Group:** NN of 32  
**Sessions:** Session X to Session Y  
**Date Range:** YYYY-MM-DD to YYYY-MM-DD  
**Total Sessions in Group:** X  

---

## Navigation

| Direction | Link |
| --- | --- |
| **Previous Group** | [Group NN-1](AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_NN-1.md) |
| **Next Group** | [Group NN+1](AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_NN+1.md) |
| **Index** | [Full Index](../AGENT_ACCOUNTABILITY_REPORT_INDEX.md) |

---

## Sessions in This Group

| Session ID | PR | Status | Date | Summary |
| --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... |

---
```

### 5.2 Content

Session entries preserved exactly as in original report:

- Title and session ID
- Objective and changes applied
- Agent details and metadata
- Validation notes and governance info

### 5.3 Footer

Each chunk ends with navigation:

```markdown
---

## Navigation

| Direction | Link |
| --- | --- |
| **Previous Group** | [Group NN-1](AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_NN-1.md) |
| **Next Group** | [Group NN+1](AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_NN+1.md) |
| **Index** | [Full Index](../AGENT_ACCOUNTABILITY_REPORT_INDEX.md) |

**Generated by:** `generate_accountability_chunks.py`  
**Generated at:** 2026-06-23T02:34Z  
```

---

## 6. Backward Compatibility

### 6.1 Redirect Stub

Original location: `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`

Content:

```markdown
# Agent Accountability Report

> **Note:** This file has been restructured for GitHub rendering compatibility.
> 
> The accountability report is now split into session groups. Please refer to:
> 
> ## 👉 [Agent Accountability Report Index](.../../.codex/AGENT_ACCOUNTABILITY_REPORT_INDEX.md)

### Quick Links

- **All Groups:** [Session Group Index](.../../.codex/AGENT_ACCOUNTABILITY_REPORT_INDEX.md)
- **Latest Sessions:** [Group 32](.../../.codex/accountability_chunks/AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_32.md)
- **Original Backup:** [Full Report Backup](.../../.codex/archive/AGENT_ACCOUNTABILITY_REPORT_BACKUP_20260623.md)

### Search Sessions

Use the session query tool to search across all groups:

```bash
python scripts/ci/session_query.py --session S310
python scripts/ci/session_query.py --pr 5060
python scripts/ci/session_query.py --status complete
```

---

**Migration Date:** 2026-06-23
```

### 6.2 Reference Updates

Update these files to point to new index:

- `.github/docs/accountability/README.md` — If exists
- Links in `AGENTS.md` — Accountability section
- Links in `CONTRIBUTING.md` — Contribution tracking
- Links in `.codex/change_log.md` — Audit trail

---

## 7. Data Validation

### 7.1 Preservation Checks

After chunking, validate:

✓ All 316 sessions present  
✓ No duplicate sessions  
✓ Session content unchanged (verbatim copy)  
✓ Metadata preserved (timestamp, PR, status, etc.)  
✓ Chronological ordering maintained  
✓ No file size exceeds 256 KB  

### 7.2 Validation Script

Run `validate_chunks.py` to verify:

```bash
python scripts/ci/validate_chunks.py \
  --sessions-index .codex/sessions_index.json \
  --chunks-dir .codex/accountability_chunks/ \
  --report validation_report.json
```

Output includes:

- Session count per chunk
- File sizes
- Chronological ordering
- Data integrity checks
- Coverage report

---

## 8. Timeline & Implementation

### Phase 2.1 (This Document)
- ✅ Create chunking strategy document (PHASE_2_CHUNKING_STRATEGY.md)
- ✅ Define naming conventions and structure
- ✅ Plan migration path and backward compatibility

### Phase 2.2 (Next)
- ⏳ Create generator script (generate_accountability_chunks.py)
- ⏳ Test chunk generation
- ⏳ Validate all chunks and coverage
- ⏳ Create index file
- ⏳ Generate all 32 chunks
- ⏳ Backup original report
- ⏳ Update cross-references
- ⏳ Validation and verification

---

## 9. Success Criteria

✅ **Phase 2.1 Complete When:**
- Strategy document created and reviewed
- Naming conventions finalized
- Directory structure planned
- Migration path documented

✅ **Phase 2.2 Complete When:**
- Generator script functional
- All 32 chunks generated
- Index file created
- Validation passes 100%
- Original backed up
- All references updated
- No data loss verified

---

## 10. Rollback Plan

If issues occur during Phase 2.2:

1. Stop all chunk operations
2. Verify backup exists: `.codex/archive/AGENT_ACCOUNTABILITY_REPORT_BACKUP_20260623.md`
3. Restore original: `cp .codex/archive/...BACKUP_*.md docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
4. Delete partial chunks: `rm -rf .codex/accountability_chunks/*`
5. Investigate failure in validation script
6. Re-run Phase 2.2 after fix

---

## Appendix: File Size Estimates

**Original Report:** 66,071 lines (~2.5 MB uncompressed)

**Per Chunk Estimate:**
- Average session size: ~150 lines (~6 KB)
- 10 sessions per chunk: ~1,500 lines (~60 KB)
- With headers/navigation: ~70 KB per chunk
- Safety margin to 256 KB limit: ✓ **Plenty of headroom**

**Total Distributed:**
- 32 chunks × ~70 KB avg = ~2.2 MB distributed
- Better rendering performance than monolithic 66K-line file
- Each file independently renderable by GitHub

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-23T02:34:59Z  
**Status:** Ready for Phase 2.2 Implementation
