# bfe2456b recovery context

This compact context accompanies [`nonworkflow-manifest.md`](nonworkflow-manifest.md).
It is provenance and handoff context, not a test artifact or a release-readiness
claim.

## Recovery scope

- Original source tip: `5980258483d8f03b6385562fc0940c52e183fb87`.
- Recovered non-workflow snapshot: `053409ad98ff3dc40243d1e132a1139e83ffaef7`
  (332 copied paths; source history need not be an ancestor).
- Base: `71613ee000808ab758cc2f8ddb07a05c5101f731` (`0D_base_`).
- Four held workflow paths remain unchanged from base:
  `copilot-setup-steps.yml`, `deferral-language-gate.yml`,
  `pypi-publish.yml`, and `strict-no-deferral-security.yml`.
- Recovered runtime fixes and regression tests are retained. Recovery evidence
  is retained historically at pre-cleanup PR commit
  `e15df253c7f0facc2bbeda1e552ada1f0e050360`; its complete inventory and
  independent retrieval verification are recorded in the manifest.

## Current disposition

| Finding | Status |
|---|---|
| R1 held-workflow advisory assertions | Blocked: the checked-in workflows lack `--warn-only`; the required selector reports 67 passed and 2 failed on these assertions. No workflow was changed or acceptance assertion weakened. Reviewer @mbaetiong must authorize workflow-owner integration; this session has no workflow write/approval tool. |
| R2 recovery evidence payload | Cleanup is pushed. A second independent fetch verified the pre-cleanup evidence commit remains an ancestor and matched all 1,425 paths, modes, blob IDs, sizes, and SHA-256 values. The final tree contains only this file and the manifest. Retention is historical Git reachability, not an independent archive. |
| R3 generated pytest telemetry and startup timestamp | The 16 synthetic campaign records are absent relative to base; campaign tests passed twice (43 per run). The later `3eb98e9` commit added only `generated_at` churn; corrective commit `2a1a297…` removed it from the PR tree. The exact session-entry working-copy bytes (SHA-256 `cd4a86487f27a8b69e120ffa1d4ea72b10453b2957026ff732b4e4607b836cb2`) remain in `/tmp/pr5708-session-startup-dirty-3eb.json` and must be restored uncommitted after the documentation push. The older stated `8138605f…` copy was not present at session entry. |
| R4 bootstrap validator | Ordinary retained-workflow compatibility is reported separately from hosted setup validation. The retained filtered environment listing remains an explicit legacy finding; added broad dumps are rejected by non-executing mutation tests. Cloud-setup consumers remain deferred to the held workflow integration. |

## Latest execution handoff (2026-10-24)

- Session-entry PR head: `3eb98e97ae071f9852adc6384c6dec894e18204e`;
  base: `71613ee000808ab758cc2f8ddb07a05c5101f731`. The timestamp-only packet
  change was removed in commit `2a1a2970e24182c9975e585abb032dad13255ef8`;
  the packet now matches base in the committed tree.
- Current PR label `wec:auto-approve` is present (persistent). WEC always-required
  boxes are checked; every opt-in box, including Nox and security, is unchecked.
  Do not treat the label or checkbox as permission to approve all pending runs.
- Latest verified head is `2a1a2970e24182c9975e585abb032dad13255ef8`;
  Nox `40067630698`, Auto-Approve `40067631029`, WEC `40067630731`, Security
  `40067630695`, Enterprise Compliance/CodeQL `40067630782`, and Code
  Quality/Coverage `40067630704` are all completed `action_required`, attempt 1.
  Validation Pipeline `40067630693` and Setup Validation `40067630723` are also
  `action_required`. Queried jobs for Validation Pipeline, Nox, Code Quality &
  Coverage, Enterprise Compliance/CodeQL, WEC, Auto-Approve, Security, and
  Setup Validation are all empty. Queried artifacts for Validation Pipeline,
  Nox, Code Quality & Coverage, Enterprise Compliance/CodeQL, and Security are
  empty; failed-job log queries for Validation Pipeline and Nox report zero
  jobs. Thus no current-head hosted diagnostics/artifacts are available.
- The default-branch registered workflows exist: Nox, Workflow Execution Gate,
  and Auto-Approve. Nox supports `pull_request` and `workflow_dispatch`, but its
  single 60-minute job runs workflow-policy, lint, typecheck, tests, and security
  sequentially. The gate's success is only initialization; it does not prove
  dispatch or approval. Auto-Approve supports a run target, but no safe
  PR-scoped dispatch/approval has occurred.
- Runs for head `3eb98e9` (all completed `action_required`, attempt 1, zero jobs):
  Nox `40065023097`, Auto-Approve `40065023096`, Workflow Execution Gate
  `40065023219`, Security `40065023089`, Enterprise Compliance/CodeQL
  `40065023081`, and Code Quality/Coverage `40065023065`. Artifact listings
  returned zero for Nox, Security, Enterprise Compliance, Code Quality/Coverage,
  WEC, and Auto-Approve. No hosted logs or test artifacts exist to retrieve.
- Previous local full-suite attempts are not acceptance: Nox collection at
  `a76c9fb` stopped with 37 errors; a separate raw pytest attempt in a mismatched
  environment had 133 collection errors. The repository CI environment lacked
  NumPy and real torch/transformers installs; root-local optional-dependency
  shims were found on the import path. These runs do not isolate source
  regressions. No complete inventory or coverage was produced. Do not restart
  a monolithic local scan; validate in the supported hosted environment after
  approval.
- Full-source mypy: 855 errors in 278 files; the base run fails during package
  discovery on invalid package name `self-healing`, so no matched delta exists.
  The required selector remains 67 passed, 2 R1 failures. Pre-commit has five
  AST class-size findings; CodeQL was skipped due database size.
- Next authorized operations: reviewer @mbaetiong must arrange workflow-owner
  review/integration of the two `--warn-only` workflow changes; an authorized
  maintainer must explicitly choose selected validation workflows and approve
  the specific action-required runs or use a run-scoped controller. Do not
  trigger the persistent all-pending approval path. Retrieve artifacts only
  after a run with jobs/artifacts exists.

Do not claim merge readiness while R1, the full-suite/coverage gate, required
type acceptance, and required hosted checks lack an accepted disposition.

No workflows were activated, approved, dispatched, or modified. No release or
publication is authorized by this recovery.
