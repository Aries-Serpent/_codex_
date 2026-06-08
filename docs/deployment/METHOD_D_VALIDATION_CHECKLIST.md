# Method D — Post-Deployment Validation Checklist

Use this checklist after deploying the Method D patch to
`.github/workflows/copilot-setup-steps.yml` and before merging to `main`.

---

## Phase 1: Pre-Deployment Static Checks

Run locally before pushing the branch.

- [ ] **YAML syntax clean**
  ```bash
  yamllint .github/workflows/copilot-setup-steps.yml
  ```
  Expected: `0` errors, `0` warnings (exit 0)

- [ ] **Architecture test passes**
  ```bash
  pytest tests/architecture/test_layer_boundaries.py::test_copilot_setup_steps_session_preload_block_intact -v
  ```
  Expected: `1 passed`

- [ ] **Full canonical baseline script passes**
  ```bash
  bash scripts/ci/validate_setup_steps_yaml.sh .github/workflows/copilot-setup-steps.yml
  ```
  Expected: all 5 checks ✅, including `Check 3/5: session preload uses block scalar`

- [ ] **Guard comment present** — confirm a line near `"🧠 Session Context Pre-load"` step contains:
  `# ⚠️ DO NOT REFACTOR THIS STEP`

- [ ] **`id: session_preload` present** in the step

- [ ] **`continue-on-error: true` present** in the step

---

## Phase 2: Test Session Deployment

- [ ] Branch pushed: `chore/method-d-preload-deployment`
- [ ] PR created targeting `main`
- [ ] Copilot session triggered on the PR
- [ ] `copilot-setup-steps` job starts (visible in Actions tab)

---

## Phase 3: Live Log Verification

Open the job log and confirm each marker appears:

- [ ] `::group::Session Context Pre-load` — step started executing
- [ ] `::endgroup::` — step completed normally
- [ ] Step status: ✅ (green, or yellow with `continue-on-error`)
- [ ] No `YAML parse error` in the log
- [ ] `Session Access Probe` step starts after preload — proves preload didn't hard-fail

---

## Phase 4: Agent Regression Check

After the Copilot session completes, inspect all commits the agent made:

- [ ] Diff `copilot-setup-steps.yml` against the pushed patch
  ```bash
  git diff origin/main .github/workflows/copilot-setup-steps.yml | grep -A5 "Session Context Pre-load"
  ```
- [ ] Confirm agent did **NOT** simplify `|| { }` back to a flow scalar
- [ ] Confirm `run: |` is still present
- [ ] Confirm `::group::` markers are still present
- [ ] Confirm `SESSION_PRELOAD_STATUS=failed` export is still present

---

## Phase 5: Env Var Fallback Verification

- [ ] If preload succeeded: `SESSION_PRELOAD_STATUS` does **not** appear in env log
- [ ] If preload failed: `SESSION_PRELOAD_STATUS=failed` appears in the job log
  - Also visible in subsequent steps via `$SESSION_PRELOAD_STATUS`

---

## Phase 6: Downstream Step Health

- [ ] `Session Access Probe` step runs to completion
- [ ] `RAG Context Build` step starts
- [ ] All Phase 2+ setup steps complete (agent session is fully initialized)
- [ ] No step is blocked by preload failure

---

## Phase 7: Sign-Off

- [ ] All phases above completed with no failures
- [ ] Method D is **proven functional** in this environment
- [ ] PR approved and ready to merge to `main`
- [ ] Document: "Method D deployment validated — `<DATE>`"

---

## Failure Decision Tree

| Symptom | Diagnosis | Action |
|---------|-----------|--------|
| `YAML parse error` in log | Patch not applied correctly | Re-check `run: \|` indentation |
| No `::group::` marker | Step not executing | Check workflow YAML around step |
| Agent reverted `\|\| { }` | Regression | Strengthen guard comment; escalate |
| `session_preload.py failed` in log | Script error (non-blocking) | Investigate script separately |
| Downstream steps not running | Preload caused hard failure | Check `continue-on-error: true` |

---

## References

- YAML patch: `docs/deployment/METHOD_D_YAML_PATCH.md`
- Live monitoring: `docs/deployment/METHOD_D_SESSION_MONITORING_GUIDE.md`
- Guard doc: `docs/agent/COPILOT_SETUP_STEPS_GUARD.md`
