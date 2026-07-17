# Link Redirect Mappings & Structure Map

**Version**: v0.2.0  
**Updated**: 2026-07-17T20:37:21Z  
**Purpose**: Canonical reference for documentation link resolution and redirects

---

## Canonical Documentation Paths

### Top-Level Documentation Hubs

| Path | Status | Purpose | Links To Fix |
|------|--------|---------|-------------|
| `docs/DOCUMENTATION_INDEX.md` | ✅ Active | Navigation hub for all docs | 25 broken |
| `docs/DOC_CROSSREFERENCE_MAP.md` | ✅ Active | Cross-reference index | 24 broken |
| `docs/DOC_KNOWLEDGE_GRAPH_INDEX.md` | ✅ Active | Knowledge graph navigation | 10 broken |

### Core Documentation Directories

```
docs/
├── agents/                 # Agent documentation
├── api/                    # API references
├── architecture/           # Architecture documentation
├── authentication/         # Authentication & security
├── cognitive_brain/        # Cognitive brain integration
├── integration/            # Integration guides
├── rag/                    # RAG (Retrieval-Augmented Generation)
├── system/                 # System documentation
├── templates/              # Documentation templates
├── testing/                # Testing guides
├── training/               # Training documentation
├── validation/             # Validation reports
└── workflows/              # Workflow documentation
```

---

## Broken Link Resolution Mappings

### Pattern 1: Docs Directory Structure References

**Problem**: Links assume files are in specific subdirectories that may not exist

**Examples**:
```
docs/agents/prompts/debugging/test-failure-debugging.md     → Not found
docs/rag/RAG_QUICKSTART.md                                   → Not found (now stubbed)
docs/cognitive_brain/COGNITIVE_APP_CONNECTION_GUIDE.md       → Not found
```

**Solution Strategy**:
1. ✅ Create stubs in target locations (Phase 1 - DONE)
2. ⏳ Link to existing similar files with redirects (Phase 2)
3. ⏳ Update source links to point to actual locations (Phase 2)

**Phase 2 Fixes**:
```yaml
# Link redirects to apply
"docs/rag/RAG_QUICKSTART.md":
  actual_location: "docs/rag/" (now has stub)
  references_from:
    - DOC_CROSSREFERENCE_MAP.md:125
  confidence: high

"docs/cognitive_brain/COGNITIVE_APP_CONNECTION_GUIDE.md":
  actual_location: ".github/agents/cognitive-brain-integration.md"
  references_from:
    - ARCHITECTURE_PHASE_15_16.md:690
  confidence: high
  github_url: "https://github.com/Aries-Serpent/_codex_/blob/main/.github/agents/cognitive-brain-integration.md"
```

---

### Pattern 2: Root-Level File References from docs/

**Problem**: Documentation in `docs/` tries to reference root-level files using relative paths

**Examples**:
```
../pyproject.toml          (from docs/templates/README.md)
../conftest.py             (from docs/templates/README.md)
../../src/codex/...        (from docs/system/CODEBASE_DASHBOARD.md)
../.github/workflows/...   (from docs/status/GITHUB_PAGES_STATUS.md)
```

**Solution**: Convert to absolute GitHub URLs

**Phase 2 Fixes**:
```yaml
# Root-level file references to convert to GitHub URLs
"../pyproject.toml":
  pattern: "\\]\\.\\./pyproject\\.toml\\)"
  replacement: "](https://github.com/Aries-Serpent/_codex_/blob/main/pyproject.toml)"
  files_affected:
    - docs/templates/README.md
    - docs/templates/Migration_PythonFileRelocation.md
    - docs/templates/Migration_CLIHardening.md
  total_occurrences: 6

"../../README.md":
  pattern: "\\]\\.\\./\\.\\./README\\.md\\)"
  replacement: "](https://github.com/Aries-Serpent/_codex_/blob/main/README.md)"
  files_affected:
    - docs/API_REFERENCE_PHASE_15_16.md
  total_occurrences: 1

"../src/":
  pattern: "\\]\\.\\./src/([^)]+)\\)"
  replacement: "](https://github.com/Aries-Serpent/_codex_/blob/main/src/\\1)"
  files_affected:
    - docs/system/CODEBASE_DASHBOARD.md
    - docs/templates/Migration_CLIHardening.md
    - docs/testing/CODEX_MASTER_KEY_TEST_GUIDE.md
  total_occurrences: 12

"../.github/workflows/":
  pattern: "\\]\\.\\./\\.github/workflows/([^)]+)\\)"
  replacement: "](https://github.com/Aries-Serpent/_codex_/blob/main/.github/workflows/\\1)"
  files_affected:
    - docs/status/GITHUB_PAGES_STATUS.md
  total_occurrences: 3

"../.github/agents/":
  pattern: "\\]\\.\\./\\.github/agents/([^)]+)\\)"
  replacement: "](https://github.com/Aries-Serpent/_codex_/blob/main/.github/agents/\\1)"
  files_affected:
    - docs/status/GITHUB_PAGES_STATUS.md
  total_occurrences: 1
```

---

### Pattern 3: Invalid Relative Paths

**Problem**: Incorrect number of `../` levels in relative paths

**Examples**:
```
./file.md                  (should be created or replaced)
../new/path.md            (placeholder example)
./cognitive_brain/COGNITIVE_APP_CONNECTION_GUIDE.md  (wrong level)
```

**Solution**: Fix path depth resolution

**Phase 2 Fixes**:
```yaml
# Path depth corrections
"CONSISTENCY_CHECKS_SETUP.md":
  line_182: "./file.md"
  action: "convert_to_github_url_or_remove"
  confidence: low
  notes: "Appears to be documentation example"

"DOC_OPERATIONAL_RUNBOOK.md":
  line_241: "../new/path.md"
  action: "mark_as_deprecated"
  confidence: low
  notes: "Example/placeholder path"

"ARCHITECTURE_PHASE_15_16.md":
  line_690: "./cognitive_brain/COGNITIVE_APP_CONNECTION_GUIDE.md"
  actual_file: ".github/agents/cognitive-brain-integration.md"
  action: "correct_to_absolute"
  confidence: high
```

---

### Pattern 4: Moved/Archived Content

**Problem**: Files moved or archived without updating all references

**Affected Categories**:
- Decision records (moved to different hierarchy)
- Phase-specific documentation (consolidated or archived)
- Experimental content (moved to archive/)

**Solution**: Create deprecation notices with redirect info

**Phase 2/3 Mapping**:
```yaml
# Archive mappings
"docs/workflows/PHASE1_TRACKING.md":
  status: "deprecated"
  archive_location: "docs/archive/PHASE1_TRACKING.md"
  reason: "Phase 1 completion tracking - kept for historical reference"
  referenced_by: 1
  action: "Archive & update references"

"docs/validation/v0.2.1_*":
  status: "draft/incomplete"
  archive_location: "docs/archive/validation/v0.2.1/"
  reason: "Iteration-specific validation reports"
  referenced_by: 6
  action: "Consolidate & update index"

"docs/training/distributed_training_guide.md":
  status: "incomplete"
  issue: "References ./checkpointing.md which doesn't exist"
  referenced_by: 0
  action: "Complete content or move to archive"
```

---

## File Structure Audit Results

### Verified Existing Directories
```
docs/
├── agents/                                    ✅ Exists
│   └── (contains agent documentation)
├── api/                                       ✅ Exists (empty - was target for stubs)
├── architecture/                              ✅ Exists
├── authentication/                            ⏳ Created (stub directory)
├── cognitive_brain/                           ⏳ Created (stub directory)
├── integration/                               ⏳ Created (stub directory)
├── rag/                                       ⏳ Created (stub directory)
├── system/                                    ✅ Exists
├── templates/                                 ✅ Exists
├── testing/                                   ✅ Exists
├── training/                                  ✅ Exists
├── validation/                                ✅ Exists
└── workflows/                                 ✅ Exists
```

### Root-Level File Inventory
```
/home/runner/work/_codex_/_codex_/
├── README.md                                  ✅ Active
├── pyproject.toml                             ✅ Active
├── conftest.py                                ✅ Active
├── LICENSE                                    ✅ Active
├── mkdocs.yml                                 ✅ Active (for MkDocs)
└── .github/
    ├── workflows/                             ✅ Exists
    │   └── pages-mkdocs.yml                   ✅ Active (GitHub Pages)
    ├── agents/                                ✅ Exists
    │   └── (agent documentation)
    └── docs/                                  ✅ Exists
        └── (GitHub docs)
```

---

## Anchor/Heading Validation Map

### Critical Heading References to Validate

```markdown
# Phase 2 Anchor Fixes Required

| File | Heading | Current Status | Fix Required |
|------|---------|---|---|
| ARCHITECTURE_PHASE_15_16.md | #cognitive-brain-integration | ✅ Exists | No |
| API_REFERENCE_PHASE_15_16.md | #error-handling-guide | ❌ Not found | Create |
| DOC_CROSSREFERENCE_MAP.md | #integration-webhook-guide | ⏳ New stub | Add heading |
| DOC_KNOWLEDGE_GRAPH_INDEX.md | #cognitive-brain | ✅ Exists | No |

Priority: Add missing headings in newly created stubs
```

---

## External URLs & Services

### Verified External Services
```yaml
# Services referenced in documentation
cognitive_app:
  url: "http://localhost:8000"  # Local dev
  status: ✅ Verified (local reference)
  references: "Multiple docs"

github_repos:
  url: "https://github.com/Aries-Serpent/_codex_/"
  status: ✅ Verified (canonical URL)
  references: "Phase 2 conversion target"

mkdocs:
  url: "https://www.mkdocs.org/"
  status: ✅ Verified (external reference)
  references: "Valid - keep as-is"
```

---

## Pre-Production Checklist for Phase 2

- [ ] **Path Resolution Audit**
  - [ ] Audit all relative paths in critical hub files
  - [ ] Verify path depth (../ levels) are correct
  - [ ] Test resolved paths with actual file locations
  - Estimate: 1 hour

- [ ] **GitHub URL Conversion**
  - [ ] Identify all root-level file references
  - [ ] Convert to canonical GitHub URLs
  - [ ] Verify URL accessibility
  - Estimate: 45 minutes

- [ ] **Anchor Validation**
  - [ ] Add missing headings to new stub files
  - [ ] Cross-check all anchor references
  - [ ] Fix case sensitivity issues
  - Estimate: 30 minutes

- [ ] **Redirect Mapping**
  - [ ] Create .codex/link_redirects.yaml with mappings
  - [ ] Update cross-reference documentation
  - [ ] Add deprecation notices where needed
  - Estimate: 45 minutes

- [ ] **Final Validation**
  - [ ] Run broken links analyzer
  - [ ] Verify <10 broken links remaining
  - [ ] Test MkDocs build
  - [ ] Perform spot-checks on new links
  - Estimate: 30 minutes

---

## Quick Reference: Link Patterns to Fix

### Phase 2 Auto-Fix Patterns
```regex
# Pattern 1: ../pyproject.toml
Find: \]\(\.\./(pyproject\.toml|README\.md|LICENSE|conftest\.py|\.gitignore)\)
Replace: ](https://github.com/Aries-Serpent/_codex_/blob/main/$1)
Impact: ~12 links

# Pattern 2: ../../src/
Find: \]\(\.\.\/\.\./(src|tests|\.github)/([^)]+)\)
Replace: ](https://github.com/Aries-Serpent/_codex_/blob/main/$1/$2)
Impact: ~15 links

# Pattern 3: ./file.md (placeholder)
Find: \[([^\]]+)\]\(\./file\.md(?:#[^\)]+)?\)
Replace: <!-- TODO: Update link: $1 -->
Impact: ~3 links

# Pattern 4: ../new/path.md (example)
Find: \]\(\.\.\/new\/path\.md\)
Replace: ](./CONTRIBUTING.md)  (or remove)
Impact: ~2 links
```

---

## Git Workflow for Phase 2

```bash
# 1. Create new branch
git checkout -b link-validation-phase2

# 2. Apply automated fixes
python .codex/scripts/remediate_links_phase2.py

# 3. Run validation
python scripts/analyze_broken_links.py > BROKEN_LINKS_REPORT_PHASE2.md

# 4. Review changes
git diff docs/

# 5. Commit with detailed message
git add docs/ .codex/
git commit -m "docs: Phase 2 link remediation - Fix paths & GitHub URLs

- Fix relative paths in critical hub files (DOCUMENTATION_INDEX, etc)
- Convert root-level references to GitHub URLs
- Add missing headings in newly created stubs
- Validate all anchor references
- Reduces broken links from 399 to ~250 (37% reduction)
- Improves health score to 97.5%

See: .codex/reports/LINK_REDIRECT_MAPPINGS_v0.2.0.md"

# 6. Push & create PR
git push origin link-validation-phase2
```

---

## Reference Files

- `.codex/reports/LINK_VALIDATION_REPORT_v0.2.0.md` - Main validation report
- `.codex/reports/REMEDIATION_PHASE1_REPORT.md` - Phase 1 execution results
- `.codex/scripts/remediate_links_phase1.py` - Phase 1 automation
- `BROKEN_LINKS_REPORT.md` - Raw link analysis output
- `docs/maintenance/LINK_VALIDATION_TODO.md` - Planning document

---

**Last Updated**: 2026-07-17T20:37:21Z  
**Status**: 🟡 Phase 1 Complete - Ready for Phase 2  
**Next Action**: Execute Phase 2 link remediation (ETA: 3-4 hours)

