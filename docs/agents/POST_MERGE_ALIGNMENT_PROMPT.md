# Post-Merge Documentation Alignment — Copilot Session Prompt

> **USE AFTER:** PR #3818 (`0D_base_` → `main`) is merged
> **INVOKE WITH:** `@copilot Execute docs/agents/POST_MERGE_ALIGNMENT_PROMPT.md`
> **AGENT DEFINITION:** `.github/agents/post-merge-doc-alignment-agent.md`
> **ESTIMATED DURATION:** 1 session (~45 min)

---

## Mission

You are performing a **post-merge documentation alignment pass** for the `_codex_` repository.

PR #3818 has just been merged from `0D_base_` into `main` (sessions S233–S244). This brought 8 new/updated CI scripts, 5 new docs, a new test file, and 5 updated workflows. The live GitHub Pages site at **https://aries-serpent.github.io/_codex_/** must now reflect the merged state.

Your job is to traverse the live site, compare each page to its source, find every piece of stale or missing content, fix it, and verify the MkDocs build is clean.

**You must not defer any issue found. Fix everything in this session.**

---

## Pre-Flight (Run First)

```bash
# 1. Confirm you are on main
git checkout main && git pull origin main
git log --oneline -3

# 2. Confirm the PR #3818 commit is present
git log --oneline | grep "S244"

# 3. Verify MkDocs builds without errors BEFORE your changes
pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin pymdownx --quiet 2>/dev/null
mkdocs build --strict 2>&1 | grep -E "WARNING|ERROR|Done" || echo "Build check complete"

# 4. Run link validator baseline
python scripts/validate_docs_links.py --check 2>/dev/null | tail -5 || echo "Link validator not available"

# 5. Sync tracked files
python3 scripts/ci/sync_tracked_files.py --check
```

---

## Phase 1 — Traverse Live Site

Navigate the live GitHub Pages site and verify each section. Use `web_fetch` for content and `playwright-browser_navigate` + `playwright-browser_snapshot` to check rendering.

### 1A. Verify New Pages Render Correctly

**Page 1: CI Rescue Pipeline**

```
URL: https://aries-serpent.github.io/_codex_/ci/CI_RESCUE_PIPELINE/
```

Check ALL of the following:

- [ ] Page loads (HTTP 200, not 404)
- [ ] Title: "CI Rescue Pipeline — Golden Path Documentation"
- [ ] All 9 Mermaid diagrams render as SVG (not raw text blocks):
  - [ ] §2 `flowchart TD` — Complete Pipeline Flowchart
  - [ ] §3 `graph LR` — Comment Channel Architecture
  - [ ] §4 `stateDiagram-v2` — Deduplication State Machine
  - [ ] §5 `sequenceDiagram` — Golden Path Sequence Diagram
  - [ ] §6 `timeline` — Rescue Comment Lifecycle
  - [ ] §7 `graph TD` — Workflow Dependency Graph
  - [ ] §8 `graph LR` — Anti-Pattern Map 1 (RP-004 loop)
  - [ ] §8 `graph LR` — Anti-Pattern Map 2 (duplicate retriggers)
  - [ ] §10 `flowchart LR` — New Channel Checklist
- [ ] Table of Contents sidebar shows all 10 sections
- [ ] All internal links work (§7 file table links, §9 marker reference table)
- [ ] Code blocks are syntax-highlighted

**If any Mermaid diagram renders as raw text:** The `mermaid2` plugin or CDN is not loading. Check `mkdocs.yml` plugin config and `docs/_config.yml`. The fix is documented in `.github/agents/github-pages-manager.md §Mermaid CDN`.

**Page 2: CI/CD Index**
```
URL: https://aries-serpent.github.io/_codex_/ci/INDEX/
   OR https://aries-serpent.github.io/_codex_/ci/
```
- [ ] "CI Rescue Pipeline" entry appears at the top under "🚨 CI Rescue Pipeline (Golden Path)"
- [ ] Link to `CI_RESCUE_PIPELINE.md` resolves correctly

**Page 3: Homepage**
```
URL: https://aries-serpent.github.io/_codex_/
```
- [ ] "🚨 CI Rescue & Health" section visible in nav sidebar
- [ ] "🔄 CI Rescue Pipeline" quick-link present under "🚀 Quick Links → 🚨 CI Rescue & Health"
- [ ] No broken links in the quick-links section

### 1B. Verify Site Navigation

Fetch the nav sidebar on any page and confirm these entries exist:

```
CI Rescue & Health                ← NEW (S244)
  ├── CI Rescue Pipeline          ← NEW (S244)
  ├── CI/CD Index
  ├── Failure Analysis
  ├── CI Fix Summary
  └── Root Org Validation
CI/CD Workflows                   ← EXISTING (should still be present)
  ├── Workflow Index
  ├── Consolidation Guide
  ├── Deprecation Plan
  ├── Optimization Summary
  └── Cache Architecture
```

### 1C. Spot-Check Existing Pages for Staleness

For each page below, fetch content and scan for the staleness patterns listed:

| Page URL (relative) | Staleness patterns to scan for |
|---------------------|-------------------------------|
| `/` (homepage) | `0D_base_` branch refs, session IDs < S233 in "What's New" |
| `/CHANGELOG/` | Verify S244 entry in Unreleased section |
| `/accountability/AGENT_ACCOUNTABILITY_REPORT/` | S244 session entry (2026-03-30) |
| `/ci/CI_RESCUE_PIPELINE/` | `0D_base_` where context should be `main` (see §2C below) |
| `/evolution/` family | No changes expected — skip unless build warns |

---

## Phase 2 — Detect and Fix Drift

Work through this checklist in order. For each item: detect → fix source file → verify.

### 2A. Branch Name References in Docs (High Priority)

After merge, `0D_base_` references in documentation should be updated to `main` **except** in:
- Historical golden-path sequence diagrams (they describe what happened on the branch)
- Accountability reports (historical record — preserve as-is)
- Session logs (historical — preserve)

**Files to check and update where appropriate:**

```bash
# Find 0D_base_ references in docs (excluding historical/accountability files)
grep -rn "0D_base_" docs/ \
  --include="*.md" \
  --exclude-dir="accountability" \
  --exclude="*SESSION*" \
  --exclude="*COGNITIVE_BRAIN_STATUS*" \
  --exclude="*aftermath*" \
  | grep -v "^Binary"
```

For each hit, determine: is this a **current instruction** (fix → `main`) or **historical record** (preserve)?

## 2B. Nav Entry Verification

Run this check to find any `mkdocs.yml` nav paths that don't resolve to real files:

```bash
python3 - << 'EOF'
import yaml, pathlib, sys
nav_yaml = yaml.safe_load(open("mkdocs.yml"))
docs_root = pathlib.Path("docs")
broken = []

def check_nav(node):
    if isinstance(node, dict):
        for k, v in node.items():
            check_nav(v)
    elif isinstance(node, list):
        for item in node:
            check_nav(item)
    elif isinstance(node, str) and not node.startswith("http"):
        p = docs_root / node
        if not p.exists():
            broken.append(node)

check_nav(nav_yaml.get("nav", []))
if broken:
    print("BROKEN NAV PATHS:")
    for b in broken:
        print(f"  {b}")
    sys.exit(1)
else:
    print("✅ All nav paths resolve to real files")
EOF
```

Fix any broken paths found.

### 2C. CI Rescue Pipeline — Contextual `0D_base_` Review

In `docs/ci/CI_RESCUE_PIPELINE.md`, review every occurrence of `0D_base_`:

1. **In Mermaid sequence diagram (§5):** Preserve — these describe what happened historically
2. **In golden-path step-by-step narrative (§5):** Preserve — historical account
3. **In "Related Files" table and rules sections:** Update to `main` where the instruction refers to the post-merge default branch
4. **In the "CI Rescue Pipeline - Golden Path Documentation" footer:** Update "Branch: 0D_base_" references that describe current state (not history)

### 2D. Verify Script References Are Accurate

These scripts are referenced in multiple docs. Confirm each actually exists at the stated path:

```bash
for f in \
  scripts/ci/generate_coverage_map.py \
  scripts/ci/ci_rescue.py \
  scripts/ci/auto_fix_common_issues.py \
  scripts/ci/sync_tracked_files.py \
  scripts/ci/check_cross_references.py \
  scripts/ci/check_pr_comments.py \
  scripts/ci/session_bootstrap.py; do
  [ -f "$f" ] && echo "✅ $f" || echo "❌ MISSING: $f"
done
```

If any are missing, find the correct path and update all docs referencing the old path.

### 2E. Verify New Test File Is Documented

`tests/ci/test_generate_coverage_map.py` was added in S244 but may not be referenced in testing documentation. Check:

```bash
grep -rn "test_generate_coverage_map" docs/ --include="*.md"
```

If no results, add a brief reference in `docs/ci/CI_RESCUE_PIPELINE.md` under "Related Files" table (already present) and optionally in `docs/TESTING.md` if that file lists CI test modules.

---

## Phase 3 — MkDocs Build Verification

```bash
# Full strict build — must produce zero warnings
mkdocs build --strict 2>&1 | tee /tmp/mkdocs_post_align.log

# Summary
echo "--- Build Summary ---"
grep -c "WARNING" /tmp/mkdocs_post_align.log && echo "warnings found" || echo "0 warnings ✅"
grep -c "ERROR" /tmp/mkdocs_post_align.log && echo "errors found" || echo "0 errors ✅"
grep "Done" /tmp/mkdocs_post_align.log
```

**Common warnings and fixes:**

| Warning | Fix |
|---------|-----|
| `Doc file 'ci/CI_RESCUE_PIPELINE.md' contains a relative link … does not exist` | Update the link target in the source file |
| `'CI_RESCUE_PIPELINE.md' is not included in the nav` | Verify mkdocs.yml nav entry path exactly matches filename |
| `Mermaid graph could not be parsed` | Check for unescaped HTML entities or pipe characters in node labels |
| `WARNING - Config value 'nav': … is not found` | File was renamed or deleted — update nav or create stub |

---

## Phase 4 — Commit and Report

### Commit Format

```bash
python3 scripts/ci/sync_tracked_files.py --fix
git add docs/ mkdocs.yml
git commit -m "docs: post-merge alignment — PR #3818 → main (S244-doc-align)

- Update branch refs 0D_base_ → main in non-historical docs
- Verify CI Rescue Pipeline Mermaid diagrams render on live site
- Fix any broken nav entries found
- MkDocs build: 0 warnings

Triggered by: docs/agents/POST_MERGE_ALIGNMENT_PROMPT.md"
```

### Final Report Comment

Post this summary as a comment on PR #3818 (or as a new issue if the PR is already merged):

```markdown
## 📚 Post-Merge Documentation Alignment Complete — S244

**Site:** https://aries-serpent.github.io/_codex_/
**Merged PR:** #3818 (0D_base_ → main, S233–S244)
**Alignment session:** S244-doc-align — {DATE}

### ✅ New Pages Verified on Live Site
- CI Rescue Pipeline: {STATUS} — {N}/9 Mermaid diagrams rendering
- CI/CD Index: {STATUS}
- Homepage quick-link: {STATUS}

### 📋 Drift Fixes Applied
| Fix | Files | Details |
|-----|-------|---------|
| Branch refs 0D_base_ → main | N | Only in non-historical sections |
| Nav entries | N | All paths verified |
| Script references | N | All exist at stated paths |
| Stale session IDs | N | Updated to S244 |

### 🔨 MkDocs Build
- Warnings: 0 ✅
- Errors: 0 ✅
- Pages built: N

### 🔗 Commit
fix(docs): post-merge alignment — PR #3818 → main · {SHORT_SHA}
```

---

## Escalation

If you find issues that cannot be fixed with source edits alone (e.g., the Mermaid CDN is blocked in the Pages environment, or a workflow change is needed), **do not defer**. Instead:

1. Fix what you can in source files
2. Open a GitHub Issue tagged `docs` + `ci-health-alert` describing the blocker
3. Post the issue link in your final report comment

---

## Checklist Summary

```
Phase 1 — Traverse Live Site
  [ ] CI Rescue Pipeline page: loads + 9 Mermaid diagrams render
  [ ] CI/CD Index page: Pipeline entry at top
  [ ] Homepage: quick-link + nav entry present
  [ ] Site nav: "CI Rescue & Health" section with 5 entries

Phase 2 — Fix Drift
  [ ] Branch refs audit: 0D_base_ → main (non-historical)
  [ ] Nav paths: all resolve to real files
  [ ] Script paths: all 7 CI scripts exist at documented locations
  [ ] test_generate_coverage_map.py referenced in docs

Phase 3 — Build
  [ ] mkdocs build --strict: 0 warnings, 0 errors

Phase 4 — Commit + Report
  [ ] sync_tracked_files.py --fix: all 5 checks ✅
  [ ] Commit pushed with fix(docs): prefix
  [ ] Report comment posted on PR #3818
```

---

*Created: S244 — 2026-03-30 · For use immediately after PR #3818 merges to main*
*Agent definition: `.github/agents/post-merge-doc-alignment-agent.md`*
