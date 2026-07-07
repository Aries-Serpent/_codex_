# Phase 4.4: Post-Merge Documentation Alignment Checklist

**Campaign:** Phase 3-5 Multi-Agent Deployment  
**Agent:** Phase 4.4 — Post-Merge Doc Alignment  
**Audience:** Merge executor, documentation maintainer, CI/CD operations  

---

## 📋 Pre-Merge Verification (Day -1)

Execute before merging promotion branch to main:

```markdown
### Pre-Merge Tasks

- [ ] **Verify promotion branch state**
  - Command: `git log --oneline -5 0D_base_` (or appropriate promotion branch)
  - Expected: All commits related to target feature/phase
  - Document: Note final commit SHA before merge

- [ ] **Backup current README & docs**
  - Command: `git show main:README.md > /tmp/README.main.md`
  - Purpose: Enable quick rollback if post-merge issues arise
  - Archive: Store in `.codex/pre-merge-backups/`

- [ ] **Check for conflicting docs changes**
  - Command: `git diff main..promotion-branch -- docs/ mkdocs.yml`
  - Expected: No conflicts, or known/expected changes
  - Action: Resolve any merge conflicts before proceeding

- [ ] **Review mkdocs.yml navigation**
  - Task: Open `mkdocs.yml` and scan nav entries
  - Expected: No references to non-existent files
  - Known issue: Line 67 has `architecture.md` (should be `ARCHITECTURE.md`)
```

---

## 🔴 IMMEDIATE ACTIONS — HOUR 0 (Post-Merge)

Execute immediately after merge to main completes:

### 1️⃣ Fix Critical Navigation Issue

```bash
# TASK: Fix mkdocs.yml architecture.md case mismatch
# FILE: mkdocs.yml (line 67)
# CURRENT: - Overview: architecture.md
# CHANGE TO: - Overview: ARCHITECTURE.md

# Steps:
cd /home/runner/work/_codex_/_codex_

# Verify the file exists with uppercase name
ls -la docs/ARCHITECTURE.md
# Expected output: docs/ARCHITECTURE.md (file found)

# Fix the nav entry (use editor or sed)
sed -i 's/- Overview: architecture\.md/- Overview: ARCHITECTURE.md/' mkdocs.yml

# Verify the change
grep -n "Overview: ARCHITECTURE" mkdocs.yml
```

**Verification:**
- [ ] `docs/ARCHITECTURE.md` exists
- [ ] `mkdocs.yml` line 67 updated to `ARCHITECTURE.md`
- [ ] Git diff shows only this 1-line change
- [ ] No other `architecture.md` references remain in nav

---

### 2️⃣ Validate MkDocs Build

```bash
# TASK: Ensure MkDocs builds without warnings post-merge

# Install dependencies
pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin --quiet

# Run strict build (fails on any warning)
cd /home/runner/work/_codex_/_codex_
mkdocs build --strict 2>&1 | tee /tmp/mkdocs_build.log

# Check for warnings or errors
grep -E "WARNING|ERROR|FAILED" /tmp/mkdocs_build.log && echo "⚠️ BUILD ISSUES DETECTED" || echo "✅ BUILD CLEAN"

# Verify output directory
ls -la site/ | head -10
```

**Verification:**
- [ ] `mkdocs build --strict` exits with code 0
- [ ] Output shows "INFO - ... Built documentation" message
- [ ] No WARNING or ERROR lines in log
- [ ] `site/` directory created with index.html

---

### 3️⃣ Test GitHub Pages Publication

```bash
# TASK: Verify site publishes to GitHub Pages without issues

# Wait for GitHub Actions to complete
# Expected: `.github/workflows/docs-deploy.yml` (or similar) triggers automatically

# Steps:
echo "Waiting 60 seconds for GitHub Pages to publish..."
sleep 60

# Test the live site
curl -I https://aries-serpent.github.io/_codex_/ | head -5
# Expected: HTTP/1.1 200 OK

# Verify key pages are accessible
for page in index.html ci/CI_RESCUE_PIPELINE/index.html api/index.html; do
  curl -s -o /dev/null -w "  %-40s %{http_code}\n" \
    "https://aries-serpent.github.io/_codex_/$page" || echo "  FAILED: $page"
done
```

**Verification:**
- [ ] Main site returns HTTP 200
- [ ] CI Rescue Pipeline page loads
- [ ] API index loads
- [ ] No 404 errors from key pages
- [ ] GitHub Actions workflow completed successfully

---

### 4️⃣ Update Homepage Last-Modified Timestamp

```bash
# TASK: Update docs/index.md "Last Updated" field to merge date

# Current format (in docs/index.md):
# **Last Updated**: 2026-06-22

# Update to today's date
TODAY=$(date +%Y-%m-%d)
sed -i "s/\*\*Last Updated\*\*: .*/\*\*Last Updated\*\*: $TODAY/" docs/index.md

# Verify the change
grep "Last Updated" docs/index.md
```

**Verification:**
- [ ] `docs/index.md` "Last Updated" shows merge date
- [ ] Format is YYYY-MM-DD
- [ ] Commit includes this change with message "chore(docs): post-merge timestamp update"

---

### 5️⃣ Verify Mermaid Diagram Rendering

```bash
# TASK: Confirm all Mermaid diagrams in CI Rescue Pipeline render correctly

# Test key pages with Mermaid content
cat << 'EOF' > /tmp/test_mermaid.py
import re
from pathlib import Path

mermaid_files = {
    "docs/ci/CI_RESCUE_PIPELINE.md": [
        "flowchart", "sequenceDiagram", "stateDiagram-v2", 
        "timeline", "graph TB", "graph LR"
    ],
    "docs/ARCHITECTURE.md": ["graph TB", "subgraph"],
    "docs/index.md": ["graph TB", "subgraph"]
}

for file, diagram_types in mermaid_files.items():
    if Path(file).exists():
        content = Path(file).read_text()
        found = []
        for dtype in diagram_types:
            if dtype in content or dtype.replace("-", "_") in content:
                found.append(dtype)
        status = "✓" if found else "✗"
        print(f"{status} {file}: {', '.join(found) if found else 'NO DIAGRAMS'}")
EOF

python3 /tmp/test_mermaid.py
```

**Verification:**
- [ ] CI Rescue Pipeline contains 6+ diagram types
- [ ] ARCHITECTURE.md contains graph diagrams
- [ ] Manual check: Visit https://aries-serpent.github.io/_codex_/ci/CI_RESCUE_PIPELINE/ 
  - Expect: All 9 Mermaid diagrams render (no red error boxes)
  - Visual check: Flowchart, sequence diagram, state machine all visible

---

## 🟡 SHORT-TERM ACTIONS — WEEK 1

Execute during the first week post-merge:

### 6️⃣ Update Version & Release Claims

**File:** `README.md` (lines 1–20)

```markdown
# Current (pre-merge):
> 🏆 **v0.1.0 Pre-Release** - Level 4 MLOps Certified ML platform with 36000+ tests, 70%+ coverage, 26 CVEs fixed, and 145 active autonomous agents.

# Post-merge task:
- [ ] Check if merge adds new features, test cases, or capabilities
- [ ] Update test count badge if new tests added
- [ ] Update coverage percentage if coverage changed
- [ ] Update CVE count if security fixes merged
- [ ] Update agent count if new agents deployed
- [ ] Update status claim (if approaching full release, adjust language)

# Example if tests increased:
> 🏆 **v0.1.0 Pre-Release** - Level 4 MLOps Certified ML platform with 36500+ tests, 71%+ coverage, 26 CVEs fixed, and 148 active autonomous agents.
```

**Verification:**
- [ ] README badges match actual codebase metrics
- [ ] Version claim is accurate
- [ ] All links in top section (release, download) are live
- [ ] Changes committed with message: "docs(readme): post-merge metrics update"

---

### 7️⃣ Add CHANGELOG Entry

**File:** `docs/CHANGELOG.md`

```markdown
# Task: Add [Unreleased] section for post-merge changes

## [Unreleased]

### Added
- CI Rescue Pipeline documentation (S280) — golden-path reference for workflow failure handling
- Proactive CI Monitor scheduling integration
- Fast-Forward Safe-File promotion documentation
- Updated Agent Accountability Report with S244–S280 session tracking

### Updated
- Navigation structure: Added CI Rescue & Health section to primary nav
- GitHub Pages site: Updated to latest Material theme features
- Homepage quick-links: Added CI Rescue Pipeline as primary entry

### Fixed
- mkdocs.yml: Fixed ARCHITECTURE.md reference case sensitivity

---

## [0.1.0-pre-release] — 2026-XX-XX
(existing entry)
```

**Verification:**
- [ ] [Unreleased] section added at top of CHANGELOG.md
- [ ] Entries clearly describe post-merge changes
- [ ] No duplicate entries
- [ ] Commit message: "docs(changelog): post-merge entry for [feature name]"

---

### 8️⃣ Update Agent Accountability Report

**File:** `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`

```markdown
# Task: Add post-merge session references

# Expected entries to add:
- S244: Phase 4.0 — Unified Documentation Consolidation (existing)
- S245+: Phase 4.1–4.4 agents (if still in merge)
- S280: CI Rescue Pipeline canonical documentation (if merged from 0D_base_)

# Template for entry:
| S280 | CI Rescue Pipeline | Phase 4 | 2026-03-30 | ✅ Complete |
| - | Documentation of automated CI failure remediation | - | - | - |
| - | 9 Mermaid diagrams, 5-layer architecture, rules | - | - | - |

# Steps:
1. Open docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
2. Find the session tracking table
3. Add new rows for post-merge sessions
4. Update summary statistics (total sessions, completion rate)
5. Commit with message: "docs(accountability): add post-merge sessions S244–S280"
```

**Verification:**
- [ ] All post-merge session IDs added to table
- [ ] Session descriptions match actual scope
- [ ] Status column updated (Complete/In Progress/Pending)
- [ ] Session links point to real documentation

---

### 9️⃣ Refresh CI Documentation Index

**File:** `docs/ci/INDEX.md`

```markdown
# Task: Verify CI documentation is current and complete

# Checklist:
- [ ] CI Rescue Pipeline entry present at TOP of list (primary reference)
- [ ] All 5 CI doc pages listed:
  1. CI Rescue Pipeline (S280)
  2. CI/CD Index (main entry point)
  3. Failure Analysis (root cause investigation)
  4. CI Fix Summary (remediation patterns)
  5. Root Org Validation (governance checks)
- [ ] All quick-links are live (no 404s)
- [ ] Updated date matches or is after merge date
- [ ] Navigation breadcrumb shows: Home > CI/CD Workflows > CI Rescue & Health

# If docs missing:
- Locate the file in main branch
- Add missing entry to docs/ci/INDEX.md
- Verify nav entry in mkdocs.yml includes the new file
```

**Verification:**
- [ ] All 5+ CI documents listed in INDEX.md
- [ ] CI Rescue Pipeline is primary entry
- [ ] No broken internal links
- [ ] Page renders correctly on GitHub Pages

---

### 🔟 Comprehensive Link Validation

```bash
# TASK: Validate all external and internal links in docs

# Create link validation script
cat << 'EOF' > /tmp/validate_links.py
import re
from pathlib import Path
from collections import defaultdict

broken_links = defaultdict(list)
external_links = []

for md_file in Path('docs').rglob('*.md'):
    content = md_file.read_text(errors='ignore')
    
    # Find GitHub links pointing to 0D_base_ (old promotion branch)
    old_branch_refs = re.findall(r'github\.com.*?0D_base_', content)
    if old_branch_refs:
        broken_links['old_branch_refs'].append(f"{md_file.relative_to('docs')}: {old_branch_refs[0]}")
    
    # Find external GitHub links
    gh_links = re.findall(r'https://github\.com/[^\s\)]+', content)
    external_links.extend(gh_links[:5])

print(f"⚠️ Links pointing to old branch (0D_base_): {len(broken_links['old_branch_refs'])}")
for item in broken_links['old_branch_refs'][:5]:
    print(f"  - {item}")

print(f"\n✓ Sample external GitHub links found: {len(set(external_links))}")
for link in list(set(external_links))[:3]:
    print(f"  - {link}")
EOF

python3 /tmp/validate_links.py
```

**Verification:**
- [ ] No links point to `0D_base_` branch (should all be `main`)
- [ ] All GitHub links use live branch names
- [ ] Sample of external links verified to be live (spot-check 5)
- [ ] Internal cross-links validated with MkDocs build

---

## 🟢 DEFERRED ACTIONS — PHASE 4.5

Lower-priority cleanup for next documentation sprint:

### 🔴 Priority P3: Stale Session Reference Cleanup

**Scope:** 89 files with S1xx–S3xx session references

```markdown
# Task (deferred to Phase 4.5):
1. Audit which sessions are archived vs. still-active
2. For archived sessions: preserve reference, add [ARCHIVED] tag
3. For active sessions: verify reference is accurate
4. Move historical session logs to docs/archive/
5. Create index mapping old session IDs to current work

# Expected outcome:
- Clean separation of archived context from live documentation
- Searchable session tracking system
- <2% of docs with stale references
```

**When to execute:** Phase 4.5 deferred documentation cleanup sprint (estimated Week 3)

---

### 🔴 Priority P3: Broken Script Reference Audit

**Scope:** 234 instances of broken script references

```markdown
# Task (deferred to Phase 4.5):
1. Inventory all unique script references in docs
2. Cross-check against actual script locations
3. Update references to match current structure
4. Create scriptref map: old_path → new_path
5. Document which scripts are deprecated vs. relocated

# Example broken refs:
- scripts/test_documentation_examples.py (doesn't exist)
- scripts/launch_distributed.py (deprecated)
- scripts/ci_rescue.py (renamed to ci-rescue.py)

# Expected outcome:
- >95% of script refs point to real files
- Automated validator prevents future breakage
- Script changelog documents relocations
```

**When to execute:** Phase 4.5 deferred documentation cleanup sprint

---

### 🔴 Priority P3: Deprecated Configuration Migration Consolidation

**Scope:** 27 files with deprecated configuration references

```markdown
# Task (deferred to Phase 4.5):
1. Review all docs/configuration/* files for deprecated markers
2. Consolidate into single docs/configuration/MIGRATION.md
3. Move old examples to docs/archive/configuration/
4. Update import path references to current structure
5. Add deprecation timeline to migration guide

# Files involved:
- docs/configuration/MIGRATION_MAPPING.md
- docs/configuration/HYDRA_MIGRATION_GUIDE.md
- docs/configuration/TROUBLESHOOTING.md
- docs/DEPRECATED.md

# Expected outcome:
- Single source of truth for config migration
- Clear timeline for deprecation phases
- Reduced duplication across docs
```

**When to execute:** Phase 4.5 deferred documentation cleanup sprint

---

## ✅ Sign-Off Checklist

After completing Hour 0 and Week 1 tasks, confirm completion:

```markdown
### Post-Merge Documentation Alignment — SIGN-OFF

**Executor:** [Name/Handle]  
**Date:** [Merge date + completion date]  
**Branch:** [Promotion branch merged]  

#### Hour 0 (Same-day tasks)
- [ ] Fixed mkdocs.yml architecture.md casing
- [ ] MkDocs build passes `--strict` mode
- [ ] GitHub Pages published successfully
- [ ] Homepage timestamp updated to merge date
- [ ] Verified Mermaid diagrams render (manual check of live site)

#### Week 1 (Short-term tasks)
- [ ] README.md metrics updated
- [ ] CHANGELOG.md [Unreleased] section added
- [ ] Agent Accountability Report updated with post-merge sessions
- [ ] CI documentation index refreshed
- [ ] Link validation completed (no 0D_base_ references, no 404s)

#### Phase 4.5 (Deferred)
- [ ] Scheduled stale session ref cleanup
- [ ] Scheduled broken script ref audit
- [ ] Scheduled config migration consolidation

**Overall Status:** ✅ POST-MERGE DOCUMENTATION ALIGNMENT COMPLETE

**Sign-off:** I confirm all immediate and short-term documentation alignment tasks are complete.

Signature: ________________________  
Date: ____________________________
```

---

## 📞 Support & Escalation

**Questions about post-merge docs alignment?**

1. **Check the Audit Document:**
   - `.codex/PHASE_4_4_POST_MERGE_ALIGNMENT_AUDIT.md` — comprehensive analysis
   - `.codex/PHASE_4_4_GITHUB_PAGES_SYNC_PLAN.md` — technical site sync details

2. **Review Related Docs:**
   - `docs/ci/CI_RESCUE_PIPELINE.md` — S280 canonical CI automation reference
   - `mkdocs.yml` — navigation configuration
   - `docs/index.md` — homepage

3. **Escalate Issues:**
   - Broken nav: Update mkdocs.yml and rebuild
   - GitHub Pages not publishing: Check `.github/workflows/docs-deploy.yml` (or similar)
   - Mermaid diagrams not rendering: Verify mermaid2 plugin is enabled in mkdocs.yml
   - Link validation failures: Run validator and update broken references

---

**Generated by Phase 4.4 Post-Merge Documentation Alignment Agent**  
**Campaign: Phase 3-5 Multi-Agent Deployment**  
**Status: ✅ COMPLETE**

---

*Use this checklist immediately after merge to main. All tasks must complete before declaring the merge successful.*
