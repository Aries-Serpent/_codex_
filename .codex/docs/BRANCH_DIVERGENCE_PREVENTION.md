# Branch Divergence Prevention — Runbook

**Policy:** `.codex/CODEBASE_AGENCY_POLICY.md`
**Related workflows:** `forward-sync-autogen.yml`, `branch-divergence-monitor.yml`
**Last updated:** 2026-03-29 (S146-CONT — PR #3782, Gemini review fixes + OBJ-002-H/I/J)

---

## Why This Divergence Happens

The repository uses a **staging integration branch model**:

```
sub-PR (copilot/...) ──► 0D_base_ ──► main
```

Agent sessions work on feature branches, merge into `0D_base_` (the staging gate), and
`0D_base_` is periodically merged into `main` via a reviewed staging-gate PR.

### The Chicken-and-Egg Cycle

1. **Scheduled auto-gen workflows always run on `main`** (GitHub's rule: `schedule:` events
   always execute the workflow file from the repository's *default branch*, which is `main`).

2. The auto-gen workflows have routing logic (`if 0D_base_ exists → push there; else → push to main`).
   This routing fix was shipped via agent sessions and merged into `0D_base_`.

3. **Until `0D_base_` merges into `main`**, `main`'s workflow files are the *pre-fix* versions
   that push auto-gen commits directly to `main`.

4. Each auto-gen run creates a commit on `main` that is NOT in `0D_base_`, widening divergence.

5. Widening divergence creates more conflicts in the staging-gate PR → harder to merge →
   longer window → even more auto-gen leaks → more conflicts. **Self-reinforcing cycle.**

### Visual Timeline

```
  Divergence point (merge-base)
         │
         ├──► main:     auto-gen-1 → auto-gen-2 → ... → auto-gen-10  (10 leaked)
         │
         └──► 0D_base_: S164 → S165 → S166 → S167 → S168 → S169 → S170  (17 staged)
```

The 10 auto-gen commits leaked to `main` because:
- `cognitive-analysis-feed.yml` pushed `metadata.json` + `workflow_patterns.jsonl` to `main`
- `embedding-index-rebuild.yml` pushed `codex_index_meta.json` to `main`
- `repo-var-sync-schedule.yml` pushed `agent_context.json` to `main`
- `vars-guide-sync.yml` pushed `variable_audit_latest.md` + `GITHUB_VARIABLES_MASTER_GUIDE.md` to `main`

All authored by `github-actions[bot]`, all `[skip ci]` or `[automated]`.

---

## Divergence Taxonomy

| Type | Description | Detection | Corrective Action |
|------|-------------|-----------|-------------------|
| **EXPECTED** | `0D_base_` ahead of `main` with staged reviewed work | `git log origin/main..origin/0D_base_` | Normal — promotion PR still in flight |
| **PIPELINE-MERGE** | `main` ahead via `Merge pull request #N from Aries-Serpent/0D_base_` | subject match on `git log origin/0D_base_..origin/main` | Auto-correct fast-forwards or merges `main` back into `0D_base_` |
| **AUTO-GEN** | `main` ahead via `github-actions[bot]` auto-gen | author + subject match on `git log origin/0D_base_..origin/main` | Auto-correctable → trigger `forward-sync-autogen.yml` |
| **AGENT-COMMIT** | `main` ahead via Copilot bot commits or empty commits | bot author or 0 file-tree changes | Auto-absorbed by the same fast-forward/merge path as PIPELINE-MERGE |
| **CODE-LEAK** | `main` ahead via human/code commits with no absorbers present | everything else in `git log origin/0D_base_..origin/main` | Requires @copilot session to cherry-pick onto `0D_base_` or otherwise investigate |

### Steady-State Target

The repository does **not** treat `ahead=0 / behind=0` as the continuous healthy state.

- `0D_base_ ahead of main` is **expected** while reviewed staging work waits for the
  promotion PR.
- `0D_base_ behind main` by bot `[skip ci]` commits can also be **temporarily acceptable**
  under REQ-10 and the branch-divergence monitor, because auto-correction absorbs
  pipeline-merge, agent-commit, and workflow-generated drift.
- The practical health target is: **no unresolved `main`-only divergence requiring human
  action** (`severity=healthy`, `codeleak_count=0`, and no remaining unabsorbed drift).

---

## Detection (Automated)

**`branch-divergence-monitor.yml`** runs every 6 hours and:

1. Checks if `0D_base_` exists.
2. Computes `git merge-base origin/main origin/0D_base_`.
3. Lists all commits that `main` has beyond the merge base.
4. Classifies each into 4 tiers: pipeline-merge / auto-gen / agent-commit / code-leak.
5. Emits severity: `healthy` / `low` / `high` / `critical`.
6. Opens or updates a `branch-divergence` tracking issue with full report.
7. Posts `@copilot` escalation only for unabsorbed code-leaks.

**To run manually:**
```bash
gh workflow run branch-divergence-monitor.yml
# Or dry-run (no changes applied):
gh workflow run branch-divergence-monitor.yml -f dry_run=true
```

---

## Auto-Correction (Automated)

When divergence is self-correctable, `branch-divergence-monitor.yml` automatically:

1. Checks out `0D_base_`.
2. Fetches `main`.
3. Copies each auto-gen file from `main` to `0D_base_` (if `main`'s version is different)
   when AUTO-GEN drift is present.
4. Applies the **slim-format rule** for `codex_index_meta.json` — strips the `chunks` array
   (per `scripts/ci/build_embeddings.py`: "git-tracked, slim header only — no chunks").
5. Fast-forwards or merges `main` back into `0D_base_` when PIPELINE-MERGE / AGENT-COMMIT
   commits are the absorber path.
6. Pushes with a **rebase guard** (`git pull --rebase origin 0D_base_`) to prevent
   non-fast-forward failures when `0D_base_` received commits since checkout.

**`forward-sync-autogen.yml`** provides real-time correction on every auto-gen `push` to `main`:

- Triggered by: `push` to `main` on auto-gen file paths.
- Same file list, same slim-format rule, same rebase guard.
- Acts within seconds of a leak occurring — the scheduled monitor is a backstop.

---

## Manual Correction Procedure

If automated correction fails or if there are code-leaks, follow these steps:

### Step 1 — Measure divergence
```bash
git fetch origin main 0D_base_
MERGE_BASE=$(git merge-base origin/main origin/0D_base_)
echo "Merge base: $MERGE_BASE"

echo "=== Commits on main NOT in 0D_base_ ==="
git log --format="%h %an: %s" origin/0D_base_..origin/main

echo "=== Commits on 0D_base_ NOT in main (expected staged work) ==="
git log --format="%h %an: %s" origin/main..origin/0D_base_
```

### Step 2 — Classify leaked commits
```bash
# Auto-gen (safe to forward): authored by github-actions[bot]
git log --format="%h %an" origin/0D_base_..origin/main | grep "github-actions\[bot\]"

# Code-leaks (need investigation): everyone else
git log --format="%h %an: %s" origin/0D_base_..origin/main | grep -v "github-actions\[bot\]"
```

### Step 3a — Forward auto-gen files (if only auto-gen leaks)
```bash
# Trigger the built-in workflow
gh workflow run forward-sync-autogen.yml

# Or manually:
git checkout -B _fix_autogen_ origin/0D_base_
git fetch origin main --depth=1

FILES=(
  ".codex/agent_context.json"
  ".codex/cognitive_brain/metadata.json"
  ".codex/cognitive_brain/workflow_patterns.jsonl"
  ".codex/embeddings/codex_index_meta.json"
  "docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md"
  "docs/admin/variable_audit_latest.md"
)

for f in "${FILES[@]}"; do
  git show origin/main:"$f" > /tmp/fwd 2>/dev/null && cp /tmp/fwd "$f" && git add "$f"
done

# Slim-format enforcement for codex_index_meta.json:
python3 -c "
import json
d = json.load(open('.codex/embeddings/codex_index_meta.json'))
open('.codex/embeddings/codex_index_meta.json','w').write(
    json.dumps({k:v for k,v in d.items() if k!='chunks'}, indent=2) + '\n')
"
git add .codex/embeddings/codex_index_meta.json

git commit -m "chore(divergence-fix): forward auto-gen files from main [skip ci]"
git pull --rebase origin 0D_base_
git push origin HEAD:0D_base_
```

### Step 3b — Handle code-leaks
Code-leaks require judgment. Options:

1. **Cherry-pick onto `0D_base_`** (if the commit belongs in the staging flow):
   ```bash
   git checkout 0D_base_
   git cherry-pick <SHA>
   git push origin 0D_base_
   ```

2. **Revert from `main`** (if the commit was a mistake on `main`):
   ```bash
   git checkout main
   git revert <SHA>
   git push origin main
   ```

3. **Leave it and merge staging-gate PR** (if the code-leak is harmless and
   the staging-gate PR covers it): resolve conflicts and merge `0D_base_` → `main`.

### Step 4 — Verify
```bash
git fetch origin main 0D_base_
BEHIND=$(git rev-list --count origin/0D_base_..origin/main)
echo "main still ahead by: $BEHIND (should be 0 after fix)"
```

---

## Conflict Resolution Rules

When resolving file conflicts between `main` and `0D_base_`:

| File | Rule | Rationale |
|------|------|-----------|
| `*.jsonl` (patterns, logs) | Take `main` if it's a superset; verify with `comm -23 <sorted IDs>` | Append-only data — always take the richer dataset |
| `metadata.json` | Take `main` (newer timestamp, more patterns) | Auto-generated; main has newer stats |
| `codex_index_meta.json` | **Slim format only** (no `chunks` key) + newer metadata values | `build_embeddings.py` line 8: "git-tracked, slim header only — no chunks" |
| `variable_audit_latest.md` | Take `main` content; ensure NOT in `.gitignore` | Auto-generated report; should remain tracked |
| Workflow `.yml` files | Merge carefully; `0D_base_` routing fixes take priority | Manual review required |

---

## Prevention Checklist

After any agent session that touches auto-gen workflows:

- [ ] Verify the workflow's push target has `if git ls-remote ... 0D_base_` routing guard
- [ ] Verify `forward-sync-autogen.yml` `paths:` includes all files the workflow writes
- [ ] Verify `forward-sync-autogen.yml` `FILES=(...)` array matches `paths:` entries
- [ ] Check `codex_index_meta.json` handling strips `chunks` before committing

After any staging-gate merge (`0D_base_` → `main`):

- [ ] Run `branch-divergence-monitor.yml` manually to confirm `behind_count=0` and `severity=healthy` (ahead_count may remain > 0 if new staged work already landed on `0D_base_`)
- [ ] Verify next scheduled auto-gen run pushes to `0D_base_` (not `main`)

---

## Glossary

| Term | Meaning |
|------|---------|
| `0D_base_` | Staging integration branch. All agent sub-PRs merge here first. |
| Staging-gate PR | The PR from `0D_base_` → `main` reviewed by a human. |
| Auto-gen commit | Commit by `github-actions[bot]` containing only auto-generated files. |
| Code-leak | Human-authored commit that bypassed `0D_base_` and landed directly on `main`. |
| Forward-sync | Copying auto-gen file content from `main` to `0D_base_`. |
| Slim format | `codex_index_meta.json` with only header fields (no `chunks` array). |
| Rebase guard | `git pull --rebase origin 0D_base_` before push to prevent non-fast-forward errors. |

---

## S237 Root Cause Taxonomy (added 2026-03-28)

The following root causes were identified in triage report #3737 and fixed in S237 (PR #3770).
They represent the most common failure patterns in branch divergence workflows.

### RC-1 — `grep -c . || echo 0` Double-Output Bug ✅ FIXED (S237)

**Affected workflows:** `branch-divergence-monitor.yml`, `doc-freshness-check.yml`

**Pattern:**
```bash
COUNT=$(echo "$VAR" | grep -c . || echo 0)
```

**Failure mode:** `grep -c .` outputs `0` AND exits 1 when input is empty. The `|| echo 0`
clause then appends a second `0` to stdout. `COUNT` becomes `"0\n0"`.

**Downstream effects:**
- `echo "behind_count=$BEHIND_COUNT"` → writes `behind_count=0\n0` to `$GITHUB_OUTPUT`
- GitHub rejects the bare `0` line: `##[error]Invalid format '0'`
- Python heredoc sees `"behind_count": 0\n0,` → `SyntaxError: invalid syntax`

**Fix:** Replace `|| echo 0` with `|| true`. `grep -c` already outputs `0` on no-match; the
fallback is redundant and harmful. Defensive Python casts added:
```python
int("$VAR".strip() or "0")
```

---

### RC-2 — `git checkout -B` Without `-f` in Commit-Step Workflows ✅ FIXED (S237)

**Affected workflows:** `cognitive-analysis-feed.yml`, `repo-var-sync-schedule.yml`,
`embedding-index-rebuild.yml`, `vars-guide-sync.yml`

**Failure mode:** Workflow generates local file changes, copies them to `/tmp`, then runs:
```bash
git checkout -B _autogen_sync_ origin/$TARGET
```
Git refuses the branch switch because uncommitted changes would be overwritten.

**Why force is safe:** All modified files are already preserved in `/tmp` before the
checkout. No data is lost by using `-f`.

**Fix:**
```bash
git checkout -fB _autogen_sync_ origin/"$TARGET"
```

---

### RC-3 — Chicken-and-Egg Auto-Gen Routing 🔄 SELF-RESOLVING

**Root cause:** Scheduled workflows always run on `main`. The routing fix
(`if 0D_base_ exists → push there; else → push to main`) lives on `0D_base_` but not yet
on `main`. Until the staging-gate PR merges, `main`'s workflow files use the old, pre-fix
versions and leak auto-gen commits directly to `main`.

**Resolution:** RC-2 fix (S237) allows successful routing commits to reach `0D_base_`.
Once the staging-gate PR merges, `main` gains the routing fix and divergence accumulation
drops to near zero.

---

### RC-4 — Branch Divergence Monitor Does Not Alert on Its Own Failure 📋 BACKLOG

**Problem:** When `branch-divergence-monitor.yml` fails internally (RC-1, syntax errors,
API rate limits), there is no rescue comment posted and the failure is silent.

**Planned fix (OBJ-002-I/J):** Add `rescue-comment-push` job + `continue-on-error: true`
on count/analysis steps. Tracked as OBJ-002 sub-task I + J.

---

### RC-5 — Non-Fast-Forward Rejection in `forward-sync-autogen.yml` ✅ ALREADY HANDLED

**Situation:** `forward-sync-autogen.yml` may fail with "non-fast-forward" if `0D_base_`
receives commits between the workflow's checkout and its push.

**Existing fix (pre-S237):** The workflow already contains a rebase guard:
```bash
git pull --rebase origin "${TARGET}" || {
  echo "⚠️  Rebase failed — re-applying files on top of latest ${TARGET}"
  git rebase --abort 2>/dev/null || true
  git fetch origin "${TARGET}" --depth=5
  git reset --hard origin/"${TARGET}"
  # Re-apply all files and recommit
}
```
This pattern was verified by OBJ-002-K investigation in S242. No code change required.

---

## Agent Execution Protocol (S237)

When the S221 missed-trigger guard or CI rescue posts an alert about branch divergence:

```
Detect → Classify → Remediate → Verify
```

| Phase | Action |
|-------|--------|
| **Detect** | Check `branch-divergence-monitor.yml` last run output. Identify `severity` and `behind_count`. |
| **Classify** | `git log origin/0D_base_..origin/main` — classify as PIPELINE-MERGE / AUTO-GEN / AGENT-COMMIT / CODE-LEAK. |
| **Remediate** | PIPELINE-MERGE / AGENT-COMMIT: let auto-correct absorb. AUTO-GEN: `gh workflow run forward-sync-autogen.yml`. CODE-LEAK: cherry-pick onto `0D_base_` or open investigation session. |
| **Verify** | Re-run `branch-divergence-monitor.yml --dry-run`. Confirm `behind_count=0` and `severity=healthy` (ahead_count may still be > 0). |

**AfterMath patterns stored:**
- `.codex/cognitive_brain/patterns/branch_divergence_grep_c_20260327.json` (RC-1)
- `.codex/cognitive_brain/patterns/git_checkout_without_force_20260327.json` (RC-2)

---

### RC-6 — Staging-Gate Merge Commit Misclassified as CODE-LEAK ✅ FIXED (S146)

**Root cause:** After a `0D_base_` → `main` staging-gate PR merges, GitHub creates
a merge commit authored by the human reviewer (e.g., `Merge pull request #3777 from
Aries-Serpent/0D_base_`). The `IS_AUTOGEN` classifier only accepts `github-actions[bot]`,
so this normal pipeline commit was classified as **CODE-LEAK** → `severity=CRITICAL`.
This triggered spurious @copilot rescue sessions after every staging-gate merge.

**Fix (S146):** Added **PIPELINE-MERGE** classification tier:
```bash
if echo "$SUBJECT" | grep -qE '^Merge pull request #[0-9]+ from Aries-Serpent/0D_base_$'; then
  IS_PIPELINE_MERGE=true
fi
```
Severity when only PIPELINE-MERGE: `low`. Auto-correct fast-forwards `0D_base_` to include
all of `main`'s history (absorbing any associated commits).

---

### RC-7 — Copilot Agent Commits Misclassified as CODE-LEAK ✅ FIXED (S146)

**Root cause:** Commits authored by `copilot-swe-agent[bot]` or `github-copilot[bot]`
are the product of reviewed PR work. They arrive on `main` through the normal staging-gate
path and are not true code bypasses. However, the original classifier only trusted
`github-actions[bot]`, so every agent session's commits were flagged as CODE-LEAK.

Additionally, **empty commits** (no file changes) — such as "Initial plan" placeholder
commits created by the Copilot agent session bootstrap — were also flagged, creating
false CRITICAL alerts for every PR that contained them.

**Fix (S146):** Added **AGENT-COMMIT** classification tier:
```bash
# Known agent bot identities that produce reviewed PR commits (not leaks)
AGENT_BOT_AUTHORS="copilot-swe-agent[bot] github-copilot[bot] copilot[bot]"

for BOT in $AGENT_BOT_AUTHORS; do
  [ "$AUTHOR" = "$BOT" ] && IS_AGENT_COMMIT=true && break
done
# Empty commits (no file changes) are always agent-commit regardless of author
[ "$TREE_CHANGES" -eq 0 ] && IS_AGENT_COMMIT=true
```
AGENT-COMMIT is absorbed by the pipeline-merge fast-forward (same auto-correct step).

**Severity rule:** `CODE-LEAK + (PIPELINE-MERGE or AGENT-COMMIT) → low` (not critical).
`@copilot` escalation only fires when `codeleak > 0 AND absorbers === 0`.

---

### RC-8 — report_progress Rebase Re-introduces Dropped Commits ⚠️ PROCESS NOTE

**Situation:** The `report_progress` tool fetches and rebases the remote branch on top
of local changes before pushing. If a commit was removed via `git rebase -i` locally
but the remote still has it, the fetch+rebase re-applies it from the remote.

**Root cause:** This is correct git behavior — the remote is the source of truth. Once
a commit is pushed to the remote, it cannot be removed without a force-push, which
`report_progress` does not perform.

**Correct workflow for dropping commits:**
1. **Before pushing**: drop the commit with `git rebase -i` and immediately call
   `report_progress` in the same response (no other git operations in between).
2. **After pushing**: the commit is permanent on the remote. Use the AGENT-COMMIT
   classifier (RC-7 fix) to ensure it is non-alarming. Document it as a known artifact.
3. **Never use empty commits**: agent sessions should never call `git commit --allow-empty`
   or create placeholder "Initial plan" commits. The cognitive-preflight REQ-3b check
   (S146) now warns on empty commits in PRs.

**Lesson (S146):** The negative (irreversible empty commit on remote) became a positive:
it drove us to add the AGENT-COMMIT classification tier that permanently prevents ALL
future copilot agent session commits from triggering false CODE-LEAK alerts.

---

## Updated Agent Execution Protocol (S146 — 4-tier classification)

```
Detect → Classify → Remediate → Verify
```

| Phase | Action |
|-------|--------|
| **Detect** | Check `branch-divergence-monitor.yml` last run output. Identify `severity`, `behind_count`, `codeleak_count`. |
| **Classify** | 4 tiers: PIPELINE-MERGE / AUTO-GEN / AGENT-COMMIT / CODE-LEAK |
| **Remediate** | PIPELINE-MERGE or AGENT-COMMIT: auto-correct handles it. AUTO-GEN: `gh workflow run forward-sync-autogen.yml`. CODE-LEAK (no absorbers): cherry-pick onto `0D_base_` or open investigation. |
| **Verify** | Re-run `branch-divergence-monitor.yml --dry-run`. Confirm `codeleak_count=0` and `severity=healthy` (ahead_count may still be > 0 while staged work is waiting for promotion). |

### Classification Quick Reference

```
SUBJECT matches "Merge pull request #N from Aries-Serpent/0D_base_"
  → PIPELINE-MERGE (auto-fwd 0D_base_)

AUTHOR = github-actions[bot] AND SUBJECT matches [skip ci]/[automated]/etc.
  → AUTO-GEN (forward-sync files)

AUTHOR = copilot-swe-agent[bot] OR github-copilot[bot] OR copilot[bot]
  OR commit has 0 file-tree changes (empty commit)
  → AGENT-COMMIT (absorbed by pipeline-merge fast-forward)

Everything else
  → CODE-LEAK (escalate @copilot ONLY when no absorbers present)
```
