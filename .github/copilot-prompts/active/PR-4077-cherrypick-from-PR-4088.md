# Cherry-Pick Instructions: PR #4088 → PR #4077

**Source branch:** `dependabot/pip/responses-0.26.0` (PR #4088)  
**Target branch:** `copilot/create-implementation-plan-and-test-cases` (PR #4077)  
**Prepared by:** Copilot SWE agent, session S324, 2026-04-27  

---

## What to cherry-pick

Two commits from `dependabot/pip/responses-0.26.0` should be applied to PR #4077:

| # | Commit SHA | Subject | Files |
|---|-----------|---------|-------|
| 1 | `8749c00474af` | `deps(deps): bump responses from 0.25.8 to 0.26.0` | `pyproject.toml`, `requirements-dev.txt`, `requirements-test.txt` |
| 2 | `1c04a1953fad` | `fix(ci): RP-004 resync .secrets.baseline and add PDA entry for 2026-04-27` | `.secrets.baseline`, `.codex/aftermath/pda_iterations.jsonl` |

---

## Step-by-step instructions

```bash
# 1. Ensure you are on the PR #4077 branch
git checkout copilot/create-implementation-plan-and-test-cases
git pull origin copilot/create-implementation-plan-and-test-cases

# 2. Fetch the source branch
git fetch origin dependabot/pip/responses-0.26.0

# 3. Cherry-pick the responses version bump (apply cleanly — no conflicts expected)
git cherry-pick 8749c00474afc74aad4a30d71e40a3678e71c099

# 4. Cherry-pick the CI fix commit
#    NOTE: the .secrets.baseline hashes in this commit are specific to the
#    dependabot branch's CODEX_MANIFEST state. After cherry-picking, immediately
#    re-run sync to get the correct hashes for THIS branch.
git cherry-pick 1c04a1953fad33c58097863812e96b2d4a94a7fe

# 5. Re-sync .secrets.baseline for THIS branch's state (required after step 4)
python3 scripts/ci/sync_tracked_files.py --fix

# 6. Stage and amend the cherry-picked fix commit with the corrected hashes
git add .secrets.baseline
git commit --amend --no-edit

# 7. Verify everything is clean
python3 scripts/ci/sync_tracked_files.py --check
python3 -m ruff check src/
```

---

## What each cherry-pick does

### Commit 1 — `8749c00` — responses version bump

**Exact changes applied:**

`pyproject.toml` (line ~192):
```diff
-  "responses>=0.25.0",  # HTTP mocking for API tests (Zendesk, etc.)
+  "responses>=0.26.0",  # HTTP mocking for API tests (Zendesk, etc.)
```

`requirements-dev.txt` (line ~10):
```diff
-responses>=0.25.0,<1  # Mock HTTP for zendesk/API tests
+responses>=0.26.0,<1  # Mock HTTP for zendesk/API tests
```

`requirements-test.txt` (line ~21):
```diff
-responses==0.25.8
+responses==0.26.0
```

### Commit 2 — `1c04a19` — CI fix

**`.codex/aftermath/pda_iterations.jsonl`** — appends one new line:
```json
{"pattern_id": "RP-004-TRACKED-FILE-SYNC-DRIFT", "timestamp": "2026-04-27T10:56:56.800911+00:00", "session": "S324", "description": "PR #4088 (responses 0.25.8->0.26.0): .secrets.baseline had stale CODEX_MANIFEST and agent_context.json hashes. Fixed via sync_tracked_files.py --fix.", "resolution": ".secrets.baseline updated with correct hashes for CODEX_MANIFEST (line=2053) and agent_context.json (line=14)", "pr": 4088}
```

**`.secrets.baseline`** — two hash updates (values will differ on PR #4077's branch; step 5 above regenerates them correctly):
- `CODEX_MANIFEST.json` entry at line 2053
- `.codex/agent_context.json` entry at line 14

---

## Conflict notes

- **`pyproject.toml` / `requirements-dev.txt` / `requirements-test.txt`**: No conflicts expected. PR #4077 has `responses>=0.25.0` / `responses==0.25.8`; the cherry-pick updates them to `>=0.26.0` / `==0.26.0`.
- **`.secrets.baseline`**: The hashes from `1c04a19` are branch-specific. The re-run of `sync_tracked_files.py --fix` in step 5 is **mandatory** to produce correct values for PR #4077's CODEX_MANIFEST state.
- **`.codex/aftermath/pda_iterations.jsonl`**: Append-only; no conflict expected.

---

## Verification after applying

```bash
python3 scripts/ci/sync_tracked_files.py --check   # All 5 checks must pass ✅
python3 -m ruff check src/                          # 0 violations ✅
```
