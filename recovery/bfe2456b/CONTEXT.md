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
| R1 held-workflow advisory assertions | Blocked: the checked-in workflows lack `--warn-only`; the required selector reports 67 passed and 2 failed on these assertions. No workflow was changed or acceptance assertion weakened. Requested reviewer @mbaetiong must confirm the workflow owner and authorize companion integration before R1 can close. |
| R2 recovery evidence payload | Cleanup is pushed. A second independent fetch verified the pre-cleanup evidence commit remains an ancestor and matched all 1,425 paths, modes, blob IDs, sizes, and SHA-256 values. The final tree contains only this file and the manifest. Retention is historical Git reachability, not an independent archive. |
| R3 generated pytest telemetry and startup timestamp | The 16 synthetic campaign records and timestamp-only startup diff are absent relative to base. Campaign tests use a temporary metrics path and passed twice (43 tests per run); the original local startup-packet bytes remain separately preserved at `/tmp/session_startup_packet.r1r4-preserved.json` (SHA-256 `8138605f314633fb35efe676edf8da4c92cda9c5dfcdd7a7552c7fb07b82e27e`). |
| R4 bootstrap validator | Ordinary retained-workflow compatibility is reported separately from hosted setup validation. The retained filtered environment listing remains an explicit legacy finding; added broad dumps are rejected by non-executing mutation tests. Cloud-setup consumers remain deferred to the held workflow integration. |

At the current recovery validation snapshot, full-source mypy reports 855
errors in 278 files (1,972 checked, exit 1). The attempted base comparison
exits 2 during package discovery because `self-healing` is not a valid Python
package name; therefore the current count is not a measured regression delta.
Ruff, source Black, targeted validator mypy, and the 57-test
Chronicle/auth/memory selection pass. The required bootstrap/instruction
selection is 67 passed and 2 failed (R1). Pre-commit exits 1 on five existing
AST class-size findings; all other applicable hooks pass. CodeQL analysis was
skipped because the database is too large. Hosted checks on the pushed commit
are `action_required`; Validation Pipeline, Copilot Setup Steps Validation,
and Nox have zero jobs, not passing results. Focused tests do not establish
complete-suite coverage. Do not claim merge readiness while R1, the full-suite
and coverage gate, required type acceptance, or required hosted checks lack an
accepted disposition.

No workflows were activated, approved, dispatched, or modified. No release or
publication is authorized by this recovery.
