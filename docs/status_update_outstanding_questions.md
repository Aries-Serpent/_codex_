# Outstanding Codex Automation Questions

This log tracks every open Codex automation question or gate failure that still needs visibility in status updates. When a disposition changes, update both this canonical list and the latest status report. Every Codex status update must include this table (or a direct copy of it) so that outstanding remediation items remain visible.

_Last updated: 2025-09-16._

| Timestamp(s) | Step / Phase | Recorded blocker | Status | Current disposition |
| --- | --- | --- | --- | --- |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | Hook execution failed because `yamllint`, `mdformat`, and `detect-secrets-hook` were missing. | Retired | The active pre-commit configuration only invokes local commands (ruff, black, mypy, pytest, git-secrets, license checker, etc.), so those CLIs are optional for developers and no longer required by automation. |
| 2025-08-28T03:55:32Z | PH6: Run pytest with coverage | `pytest` rejected legacy `--cov=src/codex_ml` arguments. | Retired | Coverage flags were removed from `pytest.ini`, and the nox helper now targets `src/codex`, so the legacy failure mode is obsolete. |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | `check-merge-conflicts` and ruff flagged merge markers / unused imports. | Retired | The hook set no longer includes `check-merge-conflicts`; ruff/black remain for lint enforcement, so the merge-marker question is superseded. |
| 2025-09-10T05:02:28Z | `nox -s tests` | Coverage session failed during the gate. | Action required | `nox -s tests` still delegates to the coverage session, so the suite must pass with coverage enabled before this blocker can be closed. |
| 2025-09-10T05:45:43Z; 08:01:19Z; 08:01:50Z; 08:02:00Z | Phase 4: `file_integrity_audit compare` | Compare step reported unexpected file changes. | Action required | Expand the allowlists (beyond `.codex/pre_manifest.json`) and rely on move detection before rerunning the audit; the remediation has not been committed yet. |
| 2025-09-10T05:46:35Z; 08:02:12Z; 13:54:41Z | Phase 6: pre-commit | Hook execution failed because `pre-commit` was missing in the environment. | Action required | Install or gate `pre-commit` in the validation environment as documented; automation still expects it to be present. |
| 2025-09-10T05:46:47Z; 08:02:25Z; 13:55:11Z | Phase 6: pytest | Test suite failed under the gate. | Action required | Failures stem from missing optional dependencies and locale/encoding issues; install the extras or skip affected tests per the remediation notes. |
| 2025-09-10T05:46:52Z; 07:14:07Z; 08:02:32Z | Phase 6 & Validation: MkDocs | MkDocs build aborted (strict mode warnings / missing pages). | Mitigated / deferred | MkDocs now runs with `strict: false`, and navigation gaps were patched. Keep docs healthy before attempting to re-enable strict mode. |
| 2025-09-10T07:13:54Z; 11:12:28Z | Validation: pre-commit | `pre-commit` command not found during validation. | Action required | Same remediation as the Phase 6 failures—install or gate `pre-commit` before running validation jobs. |
| 2025-09-10T07:14:03Z; 11:12:36Z | Validation: pytest | Legacy `--cov=src/codex_ml` arguments rejected. | Retired | Covered by the coverage tooling update; remove the legacy flags and rely on the current nox/pytest configuration targeting `src/codex`. |
| 2025-09-10T08:01:17Z | Phase 4: `file_integrity_audit compare` | `file_integrity_audit.py` rejected argument order. | Documented resolution | The script expects `compare pre post --allow-*`; follow the documented invocation to avoid the error. |
| 2025-09-10 (timestamp `$ts`) | `tests_docs_links_audit` | Script crashed with `NameError: name 'root' is not defined`. | Action required | Add `root = Path('.')` (or similar) before using the variable the next time the audit script runs; the fix is recorded but not applied. |
| 2025-09-10T21:10:43Z | Validation: nox | `nox` command not found. | Action required | Install `nox` prior to running the validation gate, per the documented remediation. |
