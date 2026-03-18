# Sync+New-Work Rebase Conflict Prevention

**Status:** ✅ GROUNDED (enforced by `scripts/ci/prevent_sync_commit_conflict.py`)  
**Added:** S154 — 2026-03-18 | PR #3628  
**Root Cause Session:** S154 — see `.codex/sessions/S154_aftermath.md`

---

## The Anti-Pattern (What Went Wrong in S154)

### Pattern Name: "Sync+New-Work Commit"

A single commit contains **both**:
1. **Sync changes** — content copied from remote auto-generated commits (e.g., the
   `### Fixed (auto-update — PR #N)` section that `session_wrapup_autofix.py` wrote
   to the remote branch after the base commit)
2. **Development changes** — new S-session work (Phase 5 fixes, agent updates, etc.)

### Why It Causes a Rebase Conflict

```
Remote history:
  c20e833 (base) ──► 8f1932a (adds [auto-update] to CHANGELOG) ──► 49b1278 (HEAD)

Local history:
  c20e833 (base) ──► cc02675 (adds [auto-update] + [S154] to CHANGELOG)

When report_progress rebases cc02675 onto 49b1278:
  ┌─────────────────────────────────────────────────────────────┐
  │ 3-way merge for CHANGELOG.md:                               │
  │   Base (c20e833):  no [auto-update] section                 │
  │   Theirs (49b1278): has [auto-update] section               │
  │   Ours   (cc02675): has [auto-update] + [S154] sections     │
  │                                                             │
  │ Both sides ADD content at the same location → CONFLICT ❌   │
  └─────────────────────────────────────────────────────────────┘
```

Git cannot auto-resolve "both sides added content at the same position" even when the
additions are nearly identical, because ours adds MORE content than theirs.

### Files Affected in S154

| File | Conflict Type | Root Cause |
|------|---------------|------------|
| `CHANGELOG.md` | Both sides added `### Fixed (auto-update — PR #3628)` | Sync'd remote auto-commit |
| `CODEX_MANIFEST.json` | Different `generated_at` timestamps | Both sides updated timestamp |
| `.codex/session_context_latest.md` | Different content updates | Both sides modified |
| `.codex/agent_auth_session.json` | Different token/session values | Both sides modified |

---

## Prevention Rules

### Rule 1: Never sync-copy remote auto-commit content into a development commit

❌ **WRONG** — fetching remote CHANGELOG and then committing both sync + new work:
```bash
# DON'T: This copies remote auto-update section AND adds S154 work in same commit
curl https://raw.githubusercontent.com/.../CHANGELOG.md > CHANGELOG.md
# (edit to add S154 section)
# report_progress → CONFLICT
```

✅ **CORRECT** — only commit your new development work:
```bash
# DO: Use MCP to READ the remote state but DON'T write it back
# Only add S154 section BELOW existing content that is in c20e833 already
# The auto-update section is already handled by the remote workflow
```

### Rule 2: Place new CHANGELOG entries BELOW all existing `[Unreleased]` sections

The remote auto-update workflow inserts new entries at the **TOP** of `[Unreleased]`.
Your development entries must go **BELOW** any section that the remote might also touch.

❌ **WRONG** — inserting between `[Unreleased]` header and `### Fixed (S153...`:
```markdown
## [Unreleased]

### Fixed (auto-update — PR #N)   ← REMOTE ALSO INSERTS HERE → CONFLICT
### Fixed (S154 — PR #N)          ← your entries
### Fixed (S153 — PR #N-2)
```

✅ **CORRECT** — inserting AFTER all existing c20e833 sections:
```markdown
## [Unreleased]
                                   ← remote inserts auto-update here (different hunk)
### Fixed (S153 — PR #N-2)        ← existing in c20e833
### Added (S153 — PR #N-2)        ← existing in c20e833
### Fixed (S154 — PR #N)          ← your entries go HERE (different hunk)
### Added (S154 — PR #N)
```

### Rule 3: Exclude auto-generated files from development commits

These files are **always** managed by CI workflows and should NOT be included in
development commits:

```
.codex/session_context_latest.md   ← managed by cognitive-preflight workflow
.codex/agent_auth_session.json     ← managed by agent-auth-delegation workflow
CODEX_MANIFEST.json                ← managed by codex-manifest-refresh workflow
```

To exclude them from your working tree before committing:
```bash
# Read their current state via MCP server (for reference only)
# Do NOT write remote auto-commit content back to working tree files
# These files will be handled by their respective CI workflows automatically
```

### Rule 4: Use `.git/info/attributes` as emergency recovery (not prevention)

When a sync+new-work commit has already been created and you need to push:

```bash
# Configure emergency merge driver
git config merge.keepcommit.driver "cp %B %A"
git config merge.keepcommit.name "Keep the commit being applied"

# Set local (non-committed) attributes override
cat > .git/info/attributes << 'ATTR'
CHANGELOG.md merge=keepcommit
CODEX_MANIFEST.json merge=keepcommit
.codex/session_context_latest.md merge=keepcommit
.codex/agent_auth_session.json merge=keepcommit
ATTR

# Now report_progress will auto-resolve conflicts using cc02675's content
```

**⚠️ This is recovery only** — it means your cc02675 content wins over the remote's
auto-commits for those files. Only correct if cc02675 has the desired final state.

---

## Detection: `prevent_sync_commit_conflict.py`

The script `scripts/ci/prevent_sync_commit_conflict.py` detects this anti-pattern
in staged changes before they are committed:

```bash
# Run before report_progress (or add to pre-commit hooks)
python scripts/ci/prevent_sync_commit_conflict.py

# Exit codes:
# 0 = clean (no sync+new-work anti-pattern detected)
# 1 = anti-pattern detected (warning, with remediation steps)
```

The script checks:
1. Whether staged CHANGELOG.md changes include auto-generated markers (`[auto-generated]`)
   AND new development section markers (`### Fixed (S1\d\d`) in the same diff
2. Whether auto-generated files (CODEX_MANIFEST, session_context, agent_auth) are staged
   alongside development files
3. Whether the staged CHANGELOG diff inserts content at the same location as where
   `session_wrapup_autofix.py` inserts auto-update entries

---

## CI Integration

Add to `.github/workflows/pre-merge-validation.yml` (optional check):

```yaml
- name: Check for sync+new-work anti-pattern
  run: python scripts/ci/prevent_sync_commit_conflict.py --ci-mode
  continue-on-error: true  # warning only, not blocking
```

---

## Local Merge Attributes for Auto-Generated Files

For personal clones, add to your global `.gitattributes_global` (optional):

```
# Auto-generated files: always prefer the newer/incoming version
CODEX_MANIFEST.json merge=ours
.codex/session_context_latest.md merge=ours
.codex/agent_auth_session.json merge=ours
```

**Note:** `merge=ours` in a regular `git merge` = use current branch version.
In `git rebase` the semantics are **reversed** (`ours` = the base, not your commits).
Use `.git/info/attributes` with the custom `keepcommit` driver for rebase recovery.

---

## References

- S154 session aftermath: `.codex/sessions/S154_aftermath.md`
- Pattern P-031 in `ci-auto-healer-agent.md`
- Recovery commit: `cc02675fd` (S154 — PR #3628)
- Related: `GROUNDED_VS_SOFT_ENFORCEMENT.md` G-NEW-3 (Phase 5 autonomous loop)
