# Copilot setup guidance and compatibility guard

Updated: 2026-10-22.

This recovery branch retains the base ordinary Actions workflow. The local
validator checks that retained baseline only; it is not evidence that GitHub's
hosted Copilot setup protocol supports the workflow or that a setup job ran.
Workflow edits remain subject to the separate workflow-owner review boundary.

## Retained ordinary Actions baseline

The current baseline has `resource-profile`, `copilot-setup-steps`, and
`rescue-comment` jobs, with their existing per-job permissions and timeouts.
`validate_copilot_bootstrap.py` checks this ordinary workflow shape, its
resource-profile command/output, the environment-preflight consumer, and
checkout with LFS disabled. It reports the existing filtered environment
listing as a legacy finding and rejects new broad `env`/`printenv` output.

These are compatibility checks, not a claim of hardened cloud bootstrap.
The validator does not widen permissions or prove that runner labels are
available. A resource-profile job cannot migrate an already-running setup job.

## Deferred hardened cloud-setup contract

The candidate cloud-setup changes remain held back with the other workflow
changes. Their intended contract includes resource detection in the actual
setup job, bounded environment classification, explicitly requested LFS
fetch/verification, optional context preparation, and an always-run readiness
report. These consumers are reported as deferred, not required of the retained
baseline and not considered validated here.

GitHub may start the agent after a failed setup step. A setup error therefore
does **not** prove the agent was prevented from starting. Tasks requiring assets
must also run the LFS helper's `--verify-only` check or equivalent task tests
after the companion workflow contract is reviewed and integrated.

Repository evolution compatibility flags do not pin GitHub's CCA runtime, grant
permissions, intercept upstream payloads, or bypass approvals. Their local
deduplication/turn-state implementations and tests remain independent.

## Secrets, variables and unknown settings

Current platform documentation uses dedicated **Agents secrets and variables**,
replacing legacy advice to configure the Actions `copilot` environment. Inventories
and hosted networking/runner/approval settings were inaccessible in this audit;
neither checked-in snapshots nor variable names establish their live values.
The retained workflow grants differ by job; the local compatibility check does
not change them or establish hosted authorization. Never add broad environment
dumps or log credentials.

## Validation before publication

```bash
python scripts/ci/validate_copilot_bootstrap.py .github/workflows/copilot-setup-steps.yml
bash scripts/ci/validate_setup_steps_yaml.sh
actionlint .github/workflows/copilot-setup-steps.yml
```

Run the validator, focused mutation tests, scoped secret checks, and ordinary
YAML lint locally. Run LFS/resource/readiness tests against the reviewed
companion contract when integrated. Use local fixtures and mocked transport;
do not perform broad remote downloads just to validate setup. YAML/schema and
baseline compatibility checks are not hosted-runner or authorization proof.
No workflow/settings writes, dispatch, approval, or publication is implied.
