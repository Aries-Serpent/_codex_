## Zero-Conflict Wrap-Up Policy

> **Status:** ✅ ACTIVE — enforced from PR #4323 S30 (2026-05-07)
> **Scope:** ALL Copilot Cloud Agent sessions in this repository

## 🚨 MANDATORY — Run Before Every Session Close

Before calling `report_progress` (which pushes to GitHub), every agent session **MUST** execute this exact verification sequence:

```bash
# Step 1 — Fetch latest remote state
git fetch origin main

# Step 2 — Detect any merge conflicts with main (AUTHORITATIVE CHECK)
CONFLICTS=$(git diff --name-only --diff-filter=U)
if [ -n "$CONFLICTS" ]; then
  echo "❌ CONFLICT GATE FAILED — resolve before pushing:"
  echo "$CONFLICTS"
  exit 1
fi
echo "✅ Zero conflicts confirmed (git diff --diff-filter=U is empty)"

# Step 3 — Check for conflict markers ONLY in files git reports as conflicted
# (Do NOT grep docs/templates — they legitimately contain conflict syntax examples)
if git diff --name-only --diff-filter=U | xargs -I{} grep -ln "^<<<<<<< " {} 2>/dev/null; then
  echo "❌ CONFLICT MARKERS found in staged conflict files — resolve before pushing"
  exit 1
fi

echo "✅ Zero-conflict gate PASSED — safe to push"
```

> **Primary gate is always `git diff --name-only --diff-filter=U`.**
> Do NOT use broad `grep -r "<<<<<<< "` — documentation and workflow files
> legitimately contain conflict-marker syntax as examples (e.g. `resolve-merge-conflicts.md`).

## Why This Policy Exists

| Incident | Date | Root Cause |
|----------|------|------------|
| `.secrets.baseline` conflict | 2026-05-07 (S30) | `origin/main` auto-push (`codebase-health-sweep.yml`) diverged while PR was active, leaving unresolved conflict markers in `.secrets.baseline` JSON. This caused silent JSON parse failures in `sync_tracked_files`. |

## Full Session Close Checklist (Non-Negotiable)

Run **in this exact order** before every `report_progress`:

1. **[ ] `git fetch origin main`** — pull latest remote state
2. **[ ] `git diff --name-only --diff-filter=U`** — must return EMPTY (zero conflicts)
3. **[ ] `python -m ruff check src/ tests/`** — must exit 0
4. **[ ] `python3 scripts/ci/sync_tracked_files.py --fix`** — must exit 0 with all ✅
5. **[ ] `CHANGELOG.md` updated** — `## [Unreleased]` section has today's entry
6. **[ ] `AGENT_ACCOUNTABILITY_REPORT.md` updated** — most-recent session entry is today (Pattern 25)
7. **[ ] `report_progress`** — only after ALL above pass

## What To Do If Conflicts Are Found

1. Identify conflicted files: `git diff --name-only --diff-filter=U`
2. For each file, resolve: keep HEAD for branch-specific changes, or take main for auto-generated files (manifests, baselines)
3. For `.secrets.baseline`: keep HEAD hashed_secret; then run `sync_tracked_files --fix` to recompute if stale
4. Stage resolved files: `git add <file>`
5. Re-verify: `git diff --name-only --diff-filter=U` → must be empty
6. Continue with standard close checklist above

## Automated Enforcement

This policy is recorded in `.codex/permanent_facts.md` (P-045) and will be loaded at every session start via the mandatory pre-load protocol in `AGENTS.md §0`.

> **Every agent session ends with zero merge conflicts. No exceptions.**


> **Status:** ✅ ACTIVE — enforced from PR #4323 S30 (2026-05-07)
> **Scope:** ALL Copilot Cloud Agent sessions in this repository

## 🚨 MANDATORY — Run Before Every Session Close

Before calling `report_progress` (which pushes to GitHub), every agent session **MUST** execute this exact verification sequence:

```bash
# Step 1 — Fetch latest remote state
git fetch origin main

# Step 2 — Detect any merge conflicts with main
CONFLICTS=$(git diff --name-only --diff-filter=U)
if [ -n "$CONFLICTS" ]; then
  echo "❌ CONFLICT GATE FAILED — resolve before pushing:"
  echo "$CONFLICTS"
  exit 1
fi

# Step 3 — Check for unresolved conflict markers in tracked files
if grep -rn "<<<<<<< \|======= \|>>>>>>> " --include="*.py" --include="*.md" --include="*.json" --include="*.yaml" --include="*.yml" . 2>/dev/null | grep -v ".git/"; then
  echo "❌ CONFLICT MARKERS found in working tree — resolve before pushing"
  exit 1
fi

echo "✅ Zero conflicts confirmed — safe to push"
```

## Why This Policy Exists

| Incident | Date | Root Cause |
|----------|------|------------|
| `.secrets.baseline` conflict | 2026-05-07 (S30) | `origin/main` auto-push (`codebase-health-sweep.yml`) diverged while PR was active, leaving unresolved conflict markers in `.secrets.baseline` JSON. This caused silent JSON parse failures in `sync_tracked_files`. |

## Full Session Close Checklist (Non-Negotiable)

Run **in this exact order** before every `report_progress`:

1. **[ ] `git fetch origin main`** — pull latest remote state
2. **[ ] `git diff --name-only --diff-filter=U`** — must return EMPTY (zero conflicts)
3. **[ ] Check conflict markers**: `grep -rn "<<<<<<< " . --include="*.py" --include="*.md" --include="*.json"` — must return EMPTY
4. **[ ] `python -m ruff check src/ tests/`** — must exit 0
5. **[ ] `python3 scripts/ci/sync_tracked_files.py --fix`** — must exit 0 with all ✅
6. **[ ] `CHANGELOG.md` updated** — `## [Unreleased]` section has today's entry
7. **[ ] `AGENT_ACCOUNTABILITY_REPORT.md` updated** — most-recent session entry is today (Pattern 25)
8. **[ ] `report_progress`** — only after ALL above pass

## What To Do If Conflicts Are Found

1. Identify conflicted files: `git diff --name-only --diff-filter=U`
2. For each file, resolve: keep HEAD for branch-specific changes, or take main for auto-generated files (manifests, baselines)
3. For `.secrets.baseline`: keep HEAD hashed_secret; then run `sync_tracked_files --fix` to recompute if stale
4. Stage resolved files: `git add <file>`
5. Re-verify: `git diff --name-only --diff-filter=U` → must be empty
6. Continue with standard close checklist above

## Automated Enforcement

This policy is recorded in `.codex/permanent_facts.md` and will be loaded at every session start via the mandatory pre-load protocol in `AGENTS.md §0`.

> **Every agent session ends with zero merge conflicts. No exceptions.**
