# HOTFIX Resumption Prompt — Post W-142 Merge (S116)

> **Use this prompt after @mbaetiong squash-merges PR #3503 into `main`.**  
> Paste this entire block as a new comment on the next PR, or as the first message  
> in a new Copilot session. Replace `<RUN_ID>` with the actual run IDs.

---

## Context

PR #3503 (`copilot/implement-user-authentication`, W-142) was squash-merged into `main`.
The merge triggered several workflows that need verification and possible hotfixes.

**Branch state at merge:**
- 105/105 serving tests pass
- 29/29 chaos+perf tests pass
- All 10 W-142 reviewer threads resolved
- 4 recurring CI failure patterns resolved (see issue #3507)
- 30 workflows in `action_required` (approval gate) at SHA `8a1e069`

---

## Immediate Tasks (S116 — must complete first session)

### 🔴 P1 — Verify GHCR Build Triggered

```
@copilot Check workflow run for `.github/workflows/build-preview-image.yml` on
`main` after merge. Confirm:
  1. Run triggered automatically (push to main)
  2. Both matrix targets (preview, preview-dev) built successfully
  3. Images published to ghcr.io/aries-serpent/_codex_/preview:latest
     and ghcr.io/aries-serpent/_codex_/preview-dev:latest
If either job failed, retrieve logs with get_job_logs(failed_only=True)
and apply targeted fix on a hotfix branch.
```

### 🔴 P1 — Confirm All Required CI Checks Green on main

```
@copilot List the most recent workflow runs on `main` branch after merge.
For any workflow in state != 'success':
  1. Retrieve failure logs
  2. Identify root cause
  3. Apply fix on hotfix branch `hotfix/post-w142-<slug>`
  4. Open PR targeting main
Priority order: Resilient Validation Suite > pre-flight-validation >
  actionlint-audit > agent-registry-validation > Pre-Merge Validation
```

### 🟡 P2 — Wire 51 Python Workflows to setup-python-cached

```
@copilot Wire the `setup-python-cached` composite action (with cache-tier: common)
to the 51 Python workflows listed in `docs/ops/CACHE_SHARED_DATASETS.md §7` that
still call `actions/setup-python@v5` directly.

Pattern for each workflow:
  BEFORE:
    - uses: actions/setup-python@v5
      with:
        python-version: '3.12'
  AFTER:
    - uses: ./.github/actions/setup-python-cached
      with:
        python-version: '3.12'
        cache-tier: common
        cache-version: ${{ vars.CODEX_CACHE_VERSION || 'v2' }}

Batch into groups of 10 per commit. Run actionlint after each batch.
```

### 🟡 P2 — Confirm COPILOT_ACCESS_TEST Variable

```
@copilot Verify that the repo variable `COPILOT_ACCESS_TEST` was auto-created
by `post-start.sh` on the first Codespace start after merge, or create it manually:
  gh variable set COPILOT_ACCESS_TEST --body "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

### 🟡 P2 — Remove Duplicate Policy Variable

```
@copilot Check for duplicate between `D365_SLA_POLICY_PATH` and
`CODEX_D365_POLICIES_PATH` in repo variables. Keep whichever is referenced
in more workflow files; delete the other; update all callers.
```

### 🟢 P3 — SAR-G01: Request 7 Codespace Secrets (human-admin dependency)

```
File GitHub issue tagged `admin-request` with title:
"[Admin] Set 7 Codespace org-level secrets (SAR-G01)"
Body:
  The following 7 secrets need to be set at the organization level so
  Codespace sessions can authenticate:
    - CODEX_BACKUP_KEY
    - CODEX_ADMIN_KEY
    - _GITHUB_APP_ID
    - _GITHUB_APP_PRIVATE_KEY
    - _GITHUB_APP_INSTALLATION_ID
    - _GITHUB_APP_CLIENT_SECRET
    - WEBHOOK_SECRET
  See docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md §8 for values + instructions.
Assign to @mbaetiong. Label: admin-required, codespace, P1.
```

### 🟢 P3 — Level 4 MLOps Score Update

```
@copilot Review `docs/archive/LEVEL_4_MLOPS_ASSESSMENT.md`. Update SAR-G02
(feast_compat.py PoC → production Feast backend), SAR-G03 (model-drift-retrain
confirmed wired), SAR-G05 (OTel stub → real OTLP endpoint if configured).
Target: reach 90/100 on all SAR items.
```

---

## Recurring Failure Patterns — Prevention Guide

The following patterns have been resolved in W-142 and must not regress:

| Pattern | Root Cause | Prevention |
|---------|------------|-----------|
| `ModelLoader.load_model` wrong patch | `InferenceServer` never calls `ModelLoader`; correct target is `ModelServer.predict` | Grep new tests for `model_loader.ModelLoader` before merge |
| Template expr in action description | `${{ }}` inside `description:` field of composite action inputs is evaluated by runner | Use plain text in `description:` fields; keep `${{ }}` only in `key:`, `run:`, `with:` |
| `SHORT_SHA` actionlint error | `inputs.image_tag` used on non-`workflow_dispatch` triggers | Always use `github.event.inputs.*` for WD-only inputs |
| Redundant pip cache | `actions/setup-python` `cache: pip` + separate `actions/cache` for same path | Use only one cache mechanism per path |
| Agent Registry `handoff_protocol` missing | New agent entry added without required field | Schema validation in `agent-registry-validation.yml` catches this on PR |

---

## Files to Check Post-Merge

```bash
# Verify all serving tests still pass on main
python -m pytest tests/serving/ -q --timeout=20

# Verify agent registry valid
python3 -c "
import yaml, json, jsonschema
schema = json.load(open('.codex/schemas/AgentRegistrySchema.json'))
data = yaml.safe_load(open('.github/agents/AGENT_REGISTRY.yaml'))
agent_schema = schema['definitions']['AgentEntry']
errors = []
for a in data.get('agents', []):
    try: jsonschema.validate(a, agent_schema)
    except jsonschema.ValidationError as e: errors.append(f\"{a['id']}: {e.message}\")
print('PASS' if not errors else errors)
"

# Verify no ModelLoader wrong-patch remains
grep -r 'model_loader.ModelLoader.load_model' tests/ && echo 'FAIL: wrong patch found' || echo 'PASS'

# Verify actionlint clean
actionlint .github/workflows/*.yml
```

---

## Session Metrics at Merge

```
Session:          S115 (W-142)
PR:               #3503
Commits this PR:  31
Tests passing:    105/105 serving, 22/22 genesis integration, 37/37 variable-audit
Auth tests:       111/111 (92% coverage)
Workflows fixed:  4 recurring patterns
Threads closed:   10/10 W-142 reviewer threads
```

---

## CHANGELOG Entry for S116

Add to `CHANGELOG.md` under `## [Unreleased]`:

```markdown
### Fixed (post-merge hotfix)
- Verified GHCR preview image build on first push to `main` (S116)
- Wired N/51 remaining Python workflows to `setup-python-cached` composite action
- Confirmed `COPILOT_ACCESS_TEST` repo variable present
- Removed duplicate D365 policy variable (if applicable)
```
