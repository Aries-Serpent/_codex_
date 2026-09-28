# Outstanding Codex Automation Questions
**Last Updated:** 2026-07-11
**Version:** v0.2.0

This log tracks every open Codex automation question or gate failure that still needs visibility in status updates. When a disposition changes, update both this canonical list and the latest status report. Every Codex status update must include this table (or a direct copy of it) so that outstanding remediation items remain visible.

No-deferral compliance gate: unresolved items are required to carry an owner, explicit reason, concrete remediation plan, and verification steps. Deferral language is allowed only when the record names the owner, states the reason, defines the remediation path, and lists the validation command or artifact that proves closure.

_Last updated: 2026-06-22

> 2025-09-18: Base and optional extras now use strict version pins in `pyproject.toml` and the
> refreshed lock files. Use `uv sync --frozen` (or `uv pip sync requirements/lock.txt`) and avoid
> `pip install -U ...` when preparing environments so the gates run against the pinned toolchain.

| Timestamp(s) | Step / Phase | Recorded blocker | Status | Still Valid? | Owner | Reason | Plan | Validation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2025-08-26T20:36:12Z | Audit bootstrap (STEP_1:REPO_TRAVERSAL) | Repository snapshot unavailable inside the Copilot session. | Documented resolution | No – environment limitation | repo-maintainers | Workspace access was unavailable during the original audit; current workspace direct access resolves the gap. | Use `tools/offline_repo_auditor.py` or attach the repo before auditing; keep direct workspace access for follow-up scans. | Verify the repository is mounted and rerun the repo audit with a clean manifest diff. |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | Hook execution failed because `yamllint`, `mdformat`, and `detect-secrets-hook` were missing. | Retired | No – hooks removed | devex-maintainers | The original hook bundle targeted tools no longer required by the active local workflow. | Keep only the active local commands and document any optional external hook dependencies. | `pre-commit --version` plus `pre-commit run --all-files` on a clean checkout. |
| 2025-08-28T03:55:32Z | PH6: Run pytest with coverage | `pytest` rejected legacy `--cov=src/codex_ml` arguments. | Retired | No – command updated | qa-maintainers | Legacy coverage flags no longer match the active package layout. | Remove stale coverage arguments and rely on the current `src/codex` targets. | Run `pytest -q` with the active `pytest.ini` config and confirm zero legacy-flag failures. |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | `check-merge-conflicts` and ruff flagged merge markers / unused imports. | Retired | No – tooling simplified | repo-maintainers | The active hook set moved to the supported lint path and the merge-marker issue was superseded. | Keep lint enforcement on the maintained hook set and remove dead checks when they become obsolete. | `ruff check .` and `git grep -n '<<<<<<<\|>>>>>>>\|======='` on edited files. |
| 2025-09-10T05:02:28Z; 2025-09-13 | `nox -s tests` | Coverage session failed because `pytest-cov` (or equivalent coverage plugin) was missing. | Action required | No | devex-qa | The pinned coverage plugin was absent from the environment, which blocked the coverage gate. | Re-pin `pytest-cov` and enforce the coverage configuration in the nox bootstrap. | `python -m pip install pytest-cov==7.0.0` and `nox -s tests` with the generated coverage artifact. |
| 2025-09-10T05:45:43Z; 08:01:19Z; 08:01:50Z; 08:02:00Z | Phase 4: `file_integrity_audit compare` | Compare step reported unexpected file changes. | Resolved | No – gate clean | repo-maintainers | Manifest drift from generated and migrated workflow files required a narrowed allowlist. | Keep the allowlist current and regenerate manifests before comparing. | Run `file_integrity_audit compare pre post --allow-*` and verify zero unexpected entries. |
| 2025-09-10T05:46:35Z; 08:02:12Z; 13:54:41Z; 2025-09-13 | Phase 6: pre-commit | `pre-commit` command missing in the validation environment. | Action required | No | devex-qa | The validation image did not bootstrap `pre-commit`, causing the gate to fail before checks executed. | Pin `pre-commit==4.0.1` and validate availability during bootstrap. | `pre-commit --version` and `pre-commit run --all-files` in the agent environment. |
| 2025-09-10T05:46:47Z; 08:02:25Z; 13:55:11Z; 2025-09-13 | Phase 6: pytest | Test suite failed under the gate because optional dependencies were missing and locale/encoding issues surfaced. | Documented resolution | No | qa-maintainers | Optional ML stacks were not guarded, which caused import failures and locale-sensitive test issues. | Guard optional integrations with `pytest.importorskip` and keep the default test path deterministic. | `pytest -q` on the minimal environment and targeted import checks for `torch`, `transformers`, `accelerate`, and `datasets`. |
| 2025-09-10T05:46:52Z; 07:14:07Z; 08:02:32Z | Phase 6 & Validation: MkDocs | MkDocs build aborted (strict mode warnings / missing pages). | Mitigated / deferred | Deferred | docs-owners | The strict build was failing due to navigation and doc quality issues that needed a path to stable docs health. | Keep `mkdocs` in non-strict mode until nav and missing pages are resolved, then re-enable strict mode. | `mkdocs build` and a docs-link audit after any nav update; re-run with strict mode once the nav is clean. |
| 2025-09-10T07:13:54Z; 11:12:28Z | Validation: pre-commit | `pre-commit` command not found during validation. | Action required | No | devex-qa | Pre-commit was unavailable before checks and caused the gate to fail early. | Pin the tool and detect startup errors during bootstrap. | `pre-commit --version` and `pre-commit run --all-files` in the validation shell. |
| 2025-09-10T07:14:03Z; 11:12:36Z | Validation: pytest | Legacy `--cov=src/codex_ml` arguments rejected. | Retired | No – command updated | qa-maintainers | The repo had stale coverage arguments in the validation wrapper. | Adopt the current `src/codex` target and retire all `codex_ml` references in the coverage config. | Run `pytest -q` using the active nox/pytest settings and ensure no legacy flags remain. |
| 2025-09-10T08:01:17Z | Phase 4: `file_integrity_audit compare` | `file_integrity_audit.py` rejected argument order. | Documented resolution | No – documented | repo-maintainers | The CLI contract for file-integrity compare was not fully documented at the time of the failure. | Keep the documented invocation aligned with the real CLI signature and test it on every workflow change. | `file_integrity_audit compare pre post --allow-*` with a clean fixture and diff output. |
| 2025-09-10 (`$ts`) | `tests_docs_links_audit` | Script crashed with `NameError: name 'root' is not defined`. | Documented resolution | No – fixed | docs-owners | The audit script initialised the repo root incorrectly and failed before validating links. | Initialise the repository root explicitly and expose the CLI contract in docs. | `python -m analysis.tests_docs_links_audit --repo .` and confirm link audit output is populated. |
| 2025-09-10T21:10:43Z; 2025-09-13 | Validation: nox | `nox` command not found. | Action required | No | devex-qa | The environment lacked the pinned `nox` dependency required by the bootstrap script. | Pin `nox==2024.5.1` and add startup detection to the workflow. | `nox --version` and `nox -s tests` in a clean environment. |
| 2025-09-13 | Training CLI (`python -m codex_ml.cli train-model`) | `ModuleNotFoundError: No module named "torch"`. | Documented resolution | No | ml-owners | The CLI did not fail gracefully when an optional ML stack was missing. | Add runtime checks and clear install guidance instead of crashing. | Re-run the CLI with the torch dependency absent and confirm the user-facing guidance is emitted. |
| Undated (docs/reference/codex_questions.md) | Metrics generation (`analysis_metrics.jsonl`) | `ModuleNotFoundError: No module named 'codex_ml.cli'`. | Documented resolution | No – resolved | docs-owners | The metrics doc referenced the stale package path. | Point the docs to the active `codex.cli` entry point and keep the path aligned with the installed package. | Run the metrics generator in editable mode and verify the CLI resolves the package. |
| 2025-09-17 | Training CLI (resume) | CLI resume workflows relied on manual checkpoint selection and lacked documentation. | Documented resolution | No – feature implemented | ml-owners | Resume automation was undocumented and required manual selection. | Retain the automatic `load_latest` path and document `--resume-from` in the CLI usage. | Invoke `--resume-from` on a synthetic checkpoint and confirm the latest checkpoint is selected automatically. |

## Dependency policy update

Runtime and tooling dependencies are now pinned in `pyproject.toml` to match the
published `requirements/lock.txt`/`uv.lock` pair. All optional extras inherit the
same pins, ensuring that local development, CI, and audit environments resolve
identical versions. Future upgrades should update both lock files via `uv pip
compile` / `uv lock` and adjust the pins in `pyproject.toml` so drift cannot
reappear.

## Dependency policy update

Runtime and tooling dependencies are now pinned in `pyproject.toml` to match the
published `requirements/lock.txt`/`uv.lock` pair. All optional extras inherit the
same pins, ensuring that local development, CI, and audit environments resolve
identical versions. Future upgrades should update both lock files via `uv pip
compile` / `uv lock` and adjust the pins in `pyproject.toml` so drift cannot
reappear.
