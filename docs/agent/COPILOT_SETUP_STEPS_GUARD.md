# Copilot setup contract and regression guard

Updated: 2026-10-22.

Reviewed changes to `.github/workflows/copilot-setup-steps.yml` are permitted.
The guard enforces actual preparation behavior, not an old blob, line count,
blanket no-refactor rule, or repository compatibility flag values.

## Automatic bootstrap versus ordinary Actions

Keep exactly one job named `copilot-setup-steps`. Supported job settings are
`steps`, `permissions`, `runs-on`, `services`, `snapshot`, and
`timeout-minutes` (maximum 59). Use explicit step inputs/environment; do not
depend on unsupported job settings, sibling resource jobs, or rescue jobs.
Complex shell scripts use block scalar `run: |`.

The runner is chosen by `runs-on` **before steps execute**. The default is
`ubuntu-latest`; `vars.COPILOT_RUNNER_PROFILE` must refer to an already available,
authorized runner. Resource probing exports bounded limits to subsequent setup
processes; it does not migrate the job or prove larger-runner entitlement.
`COPILOT_AGENT_WORKERS` bounds the repository concurrent executor, not GitHub's
own agent scheduler. Build-tool limits affect only tools that honor them.

## Required behavior

1. Checkout with LFS disabled; preserve a no-download baseline.
2. Probe resources inside the actual setup job and consume exported worker limits.
3. Classify the environment without treating an ML keyword as asset authorization.
4. Resolve explicit required narrow paths before bounded LFS fetch/verification.
5. Bootstrap Python through the shared cached action; report dependency failures.
6. Produce optional bounded context for explicit reading, not claimed host prompt
   injection. Failure cannot promote a stale artifact to available status.
7. Always write `.codex/agent_setup_status.json`: `ready`, `partial`, or
   `not-ready`, with the observed scope and unverified platform access.

GitHub may start the agent after a failed setup step. A setup error therefore
does **not** prove the agent was prevented from starting. Tasks requiring assets
must also run the LFS helper's `--verify-only` check or equivalent task tests.

Repository evolution compatibility flags do not pin GitHub's CCA runtime, grant
permissions, intercept upstream payloads, or bypass approvals. Their local
deduplication/turn-state implementations and tests remain independent.

## Secrets, variables and unknown settings

Current platform documentation uses dedicated **Agents secrets and variables**,
replacing legacy advice to configure the Actions `copilot` environment. Inventories
and hosted networking/runner/approval settings were inaccessible in this audit;
neither checked-in snapshots nor variable names establish their live values.
Setup uses only `contents: read`; this does not configure the agent's separate
token. Never dump the environment or log credentials.

## Validation before publication

```bash
python scripts/ci/validate_copilot_bootstrap.py .github/workflows/copilot-setup-steps.yml
bash scripts/ci/validate_setup_steps_yaml.sh
actionlint .github/workflows/copilot-setup-steps.yml
```

Run scoped secret checks and the LFS/resource/readiness tests. Use local tiny
fixtures and mocked transport; do not perform broad remote downloads just to
validate setup. YAML/schema checks are not hosted-runner or authorization proof.
No workflow/settings writes, dispatch, or publication is implied by these checks.
