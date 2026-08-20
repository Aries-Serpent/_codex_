# Investigation Report: Copilot Agent Session Setup Failure

Generated: 2026-08-20T00:00:00Z | Author: mbaetiong

## Summary

| Item | Finding |
|---|---|
| Failure type | GitHub Actions workflow validation failure during Copilot environment setup |
| Failing step | `Validate CCA lock variables` in `.github/workflows/copilot-setup-steps.yml` |
| Root cause | Required repository Actions variables were empty at runtime (`vars.COPILOT_AGENT_CCA_VERSION_LOCK`, `vars.COPILOT_AGENT_DEDUPLICATION_ENABLED`, `vars.COPILOT_AGENT_TURN_ISOLATION_ENABLED`) |
| Runtime values observed | `stable` expected, got empty string; `true` expected, got empty string |
| Result | Job exits with code 1 before Copilot session can start |
| Recommended action | Configure the three required repository/org variables or make workflow defaults explicit and safe |
| Priority | FIX |

## Evidence and exact log excerpts

The failing run provided the following exact terminal errors:

```text
Error: COPILOT_AGENT_CCA_VERSION_LOCK must be 'stable' (got '')
Error: COPILOT_AGENT_DEDUPLICATION_ENABLED must be 'true' (got '')
Error: COPILOT_AGENT_TURN_ISOLATION_ENABLED must be 'true' (got '')
Error: Process completed with exit code 1.
```

These correspond to the validation logic in the workflow step:

```yaml
- name: "🔒 Validate CCA lock variables"
  shell: bash
  env:
    LOCK: ${{ vars.COPILOT_AGENT_CCA_VERSION_LOCK }}
    DEDUP: ${{ vars.COPILOT_AGENT_DEDUPLICATION_ENABLED }}
    ISO: ${{ vars.COPILOT_AGENT_TURN_ISOLATION_ENABLED }}
  run: |
    fail=0
    if [[ "${LOCK}" != "stable" ]]; then
      echo "::error::COPILOT_AGENT_CCA_VERSION_LOCK must be 'stable' (got '${LOCK}')"; fail=1
    fi
    if [[ "${DEDUP}" != "true" ]]; then
      echo "::error::COPILOT_AGENT_DEDUPLICATION_ENABLED must be 'true' (got '${DEDUP}')"; fail=1
    fi
    if [[ "${ISO}" != "true" ]]; then
      echo "::error::COPILOT_AGENT_TURN_ISOLATION_ENABLED must be 'true' (got '${ISO}')"; fail=1
    fi
    exit $fail
```

Source: `.github/workflows/copilot-setup-steps.yml` lines 106-123.
GitHub permalink: https://github.com/Aries-Serpent/_codex_/blob/main/.github/workflows/copilot-setup-steps.yml#L106-L123

## Files and references inspected

| File | Purpose | Evidence |
|---|---|---|
| `.github/workflows/copilot-setup-steps.yml` | Defines the failing validation gate | Reads `vars.COPILOT_AGENT_*` and enforces exact values |
| `.github/workflows/copilot-agent-vars-bootstrap.yml` | Bootstraps/validates CCA variables | Calls validation script and reports status |
| `.codex/POST_MERGE_NEXT_SESSION_PROMPT.md` | Documents expected validation gate state | Explicitly expects all three variables to be present and valid |

Relevant references:

- `.github/workflows/copilot-setup-steps.yml#L66-L72` sets environment variables at the job level
- `.github/workflows/copilot-setup-steps.yml#L106-L123` validates them and fails when unset/incorrect
- `.github/workflows/copilot-agent-vars-bootstrap.yml#L32-L41` confirms bootstrap validation is expected at runtime
- `.codex/POST_MERGE_NEXT_SESSION_PROMPT.md#L24-L40` states the gate must show all three CCA variables present and valid

## Search queries executed

| Query | Result |
|---|---|
| `COPILOT_AGENT_CCA_VERSION_LOCK|COPILOT_AGENT_DEDUPLICATION_ENABLED|COPILOT_AGENT_TURN_ISOLATION_ENABLED` in `Aries-Serpent/_codex_` | Found only in the workflow validation logic |
| `validate_copilot_setup_steps` | No matching script file found in repo tree; bootstrap workflow points to validation but the exact implementation file is not present in the checked-out tree inspected here |

## Counts and cross-checks

| Check | Count / status |
|---|---|
| Required validation variables | 3 |
| Variable names in workflow | 3 |
| Variables that must match exact values | 3 |
| Observed runtime values | all empty strings |
| Validation rule result | all three checks fail |
| Workflow exit status | `1` |
| Fix path | required repo or org variables must be set |

Cross-check: the documentation and workflow agree. The repository policy prompt explicitly lists the gate as expected to pass when the variables are present, and the workflow itself enforces the check; the failure is consistent with missing configuration, not with application code.

## Step-by-step root-cause analysis

1. The failing job is the `copilot-setup-steps` workflow.
2. The workflow defines `env` values at the job level and then reads repo/org variables using `${{ vars.* }}`.
3. The step `Validate CCA lock variables` reads:
   - `LOCK: ${{ vars.COPILOT_AGENT_CCA_VERSION_LOCK }}`
   - `DEDUP: ${{ vars.COPILOT_AGENT_DEDUPLICATION_ENABLED }}`
   - `ISO: ${{ vars.COPILOT_AGENT_TURN_ISOLATION_ENABLED }}`
4. When variables are not defined in GitHub repository/org settings, `${{ vars.* }}` resolves to an empty string.
5. The shell compares those values to required literals:
   - `LOCK` must equal `stable`
   - `DEDUP` must equal `true`
   - `ISO` must equal `true`
6. Each check fails and the step exits non-zero.
7. Because this happens before the rest of session setup, Copilot agent session startup is blocked.

This is therefore a configuration failure, not a runtime code bug in the application itself.

## Impact assessment

| Area | Impact |
|---|---|
| Copilot sessions | Blocked before environment prep completes |
| CI / automation | Workflow fails early and prevents downstream setup |
| Developer workflow | Prevents any Copilot agent session from starting in this repo |
| Scope | Repository-level configuration, not application code |

## High-level remediation outline

### FIX

Set these repository or organization Actions variables in GitHub before rerunning the workflow:

| Variable | Required value |
|---|---|
| `COPILOT_AGENT_CCA_VERSION_LOCK` | `stable` |
| `COPILOT_AGENT_DEDUPLICATION_ENABLED` | `true` |
| `COPILOT_AGENT_TURN_ISOLATION_ENABLED` | `true` |

If the repo is intentionally configured to provide these via environment or dynamic defaults, ensure they resolve to the same values. Otherwise, add explicit defaults in the workflow to fail fast with clear diagnostics or to choose safe values.

### MIGRATE only if needed

If the repo wants to standardize naming or centralize config, migrate to a single source of truth for those variables, but the required runtime values still must be `stable` / `true` / `true`.

### REMOVE

Not recommended. This validation is intentionally enforced and there are active references in the workflow and documentation. Removing it would bypass a hard safety gate.

## Important considerations when implementing FIX

- Repository variables are different from secrets; the workflow specifically reads `vars.*`, not `secrets.*`.
- Empty strings are treated as failure, and strict equality is intentional.
- The validation is in a setup workflow that runs before session initialization, so setting the variables is the correct fix.
- Prefer repository variables if this workflow is intended to be shared across branches or organizations; if needed, use org-level variables.
- If a fallback is added, it should be explicit and documented; do not silently allow empty values.

## Verification steps

1. In GitHub repository settings, create or update these Actions variables:
   - `COPILOT_AGENT_CCA_VERSION_LOCK=stable`
   - `COPILOT_AGENT_DEDUPLICATION_ENABLED=true`
   - `COPILOT_AGENT_TURN_ISOLATION_ENABLED=true`
2. Re-run the workflow `Copilot Agent Environment Setup`.
3. Confirm the step `Validate CCA lock variables` completes without error.
4. Confirm the run advances past step 27 and environment setup continues.

Example shell validation:

```bash
grep -E "COPILOT_AGENT_CCA_VERSION_LOCK|COPILOT_AGENT_DEDUPLICATION_ENABLED|COPILOT_AGENT_TURN_ISOLATION_ENABLED" .github/workflows/copilot-setup-steps.yml
```

And in GitHub Actions variable configuration, ensure the values are the literal strings:

```text
stable
true
true
```

## Dangerous options and risks

| Option | Why it is dangerous |
|---|---|
| Change the check to allow empty strings | Removes the same safety gate the workflow is designed to enforce |
| Replace vars with secrets | The workflow reads `vars.*`; secrets would not satisfy the same configuration path |
| Remove the validation step entirely | Creates inconsistent agent runtime behavior and can lead to unsupported session setup |
| Silently default to empty or false values | This would keep the workflow broken and produce unbounded drift across sessions |

## Explicit search queries and commands

```bash
# Workflow validation references
grep -E "COPILOT_AGENT_CCA_VERSION_LOCK|COPILOT_AGENT_DEDUPLICATION_ENABLED|COPILOT_AGENT_TURN_ISOLATION_ENABLED" .github/workflows/copilot-setup-steps.yml

# Confirm expected repo-level configuration instructions
grep -E "COPILOT_AGENT_CCA_VERSION_LOCK|COPILOT_AGENT_DEDUPLICATION_ENABLED|COPILOT_AGENT_TURN_ISOLATION_ENABLED" .codex/POST_MERGE_NEXT_SESSION_PROMPT.md
```

## Concluding interpretation

The job failed because the repository’s GitHub Actions variables were not set, and the workflow intentionally treats empty values as a hard error. This is a repository configuration issue, not a code defect. The correct resolution is to configure the required variables to the exact values the workflow requires and rerun the setup job.

This failure is deterministic, easily reproducible, and fully explained by the validation logic in `.github/workflows/copilot-setup-steps.yml`.

---

## Tailored prompt for Copilot agent session

```text
@copilot diagnose-and-fix-copilot-agent-config

We need to fix the failing GitHub Actions workflow for the Copilot agent session in Aries-Serpent/_codex_.

Problem summary:
- The workflow `copilot-setup-steps.yml` fails in the step `Validate CCA lock variables`.
- The failing run produced:
  - `COPILOT_AGENT_CCA_VERSION_LOCK must be 'stable' (got '')`
  - `COPILOT_AGENT_DEDUPLICATION_ENABLED must be 'true' (got '')`
  - `COPILOT_AGENT_TURN_ISOLATION_ENABLED must be 'true' (got '')`
- This means the workflow is reading empty `vars.*` values at runtime.

Required root-cause investigation:
- Inspect `.github/workflows/copilot-setup-steps.yml` and confirm the exact validation logic.
- Confirm which GitHub Actions variables are required and their expected values.
- Explain whether the failure is caused by missing repository/org variables, workflow defaults, or an invalid configuration path.
- Report the exact fix needed and show the minimal patch or config change.

Expected values:
- `COPILOT_AGENT_CCA_VERSION_LOCK=stable`
- `COPILOT_AGENT_DEDUPLICATION_ENABLED=true`
- `COPILOT_AGENT_TURN_ISOLATION_ENABLED=true`

Must follow repository policy:
- Must comply with `.codex/CODEBASE_AGENCY_POLICY.md`
- Do not defer the issue as “pre-existing” or “not my area”
- Root cause must be traceable to specific workflow lines and runtime evidence

Deliverables:
1. Explain why the job failed.
2. State the exact fix.
3. Provide code or workflow changes if needed.
4. Show verification steps to confirm the workflow passes.
5. Keep the response focused on the build fix and the root cause.
```
