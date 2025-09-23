# Codex Questions Backlog

_No questions captured during Run 1 (2025-09-22)._  Update this file whenever an error occurs following the template in `AUDIT_PROMPT.md`.

Question for ChatGPT @codex 2025-09-22T21:52:08+00:00:
While performing [STEP_6:Finalisation - run pytest], encountered the following error:
ModuleNotFoundError: No module named 'hydra.extra'
Context: `pytest -q tests/tools/test_validate_fences.py` triggered plugin auto-discovery pulling missing optional dependencies.
What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-23):** The import failure stems from pytest discovering Hydra plug-ins when the optional Hydra extras are not installed. The test suite now guards Hydra and other heavy dependencies with `pytest.importorskip`, so affected modules cleanly skip instead of crashing when those packages are absent.【F:tests/test_cli_help.py†L1-L24】 In addition, the coverage and quality nox sessions install the pinned test extras (including the Hydra plug-ins) and verify availability before the run, surfacing an actionable error message if the extras are still missing.【F:noxfile.py†L521-L559】 Running the suite after installing the dev extras—or leaving them absent—now succeeds with skips rather than import errors.

Question for ChatGPT @codex 2025-09-22T21:53:20+00:00:
While performing [STEP_6:Finalisation - run pre-commit], encountered the following error:
`pre-commit run --all-files` triggered legacy lint failures across the repository (ruff/black) and was interrupted after reporting thousands of issues.
Context: Need guidance on scoping pre-commit to new audit artefacts without refactoring the entire codebase.
What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-23):** The original hook set invoked broad upstream configurations that reformatted unrelated files, producing the “lint storm.” The repository now relies on a single local repository in `.pre-commit-config.yaml` that runs only fast, offline-friendly tools (ruff, black, mypy, the security scans, and the markdown fence validator) against the files being committed.【F:.pre-commit-config.yaml†L1-L100】 Because the hooks no longer download remote configs or reformat untouched modules, `pre-commit run --all-files` is constrained to actionable checks on new work rather than rewriting the historical tree.

Question for ChatGPT-5 @codex 2025-09-22T22:56:02Z:
While performing [STEP_6:Finalisation - run pre-commit], encountered the following error:
bash: command not found: pre-commit
Context: Running `pre-commit run --files AUDIT_PROMPT.md CHANGELOG.md OPEN_QUESTIONS.md reports/local_checks.md reports/reproducibility.md docs/validation/Offline_Audit_Validation.md scripts/codex_local_audit.sh scripts/codex-audit` on a fresh container before installing pre-commit.
What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-23):** The hooks were launched in an environment that had not yet installed the development extras, so the `pre-commit` executable was missing from `PATH`. The development extra in `pyproject.toml` now pins `pre-commit==4.0.1`, and the local gates script installs the dev dependencies before invoking any hooks, falling back to a clear message if the command is still unavailable.【F:pyproject.toml†L37-L47】【F:scripts/codex_local_gates.sh†L1-L32】 Bootstrapping with `pip install -e .[dev]` (or running `scripts/codex_local_gates.sh`) ensures `pre-commit` is ready before the hooks run.

Question for ChatGPT @codex 2025-09-22T23:43:45Z:
While performing [STEP_6:Finalisation - run nox coverage], encountered the following error:
ModuleNotFoundError: No module named 'hydra.extra'
Context: `nox -s tests` triggers the coverage session which auto-discovers pytest plugins and fails when optional Hydra extras are absent.
What are the possible causes, and how can this be resolved while preserving intended functionality?

**Answer (2025-09-23):** The coverage gate previously assumed the Hydra extras were installed, so pytest crashed during plug-in discovery. The dev extras now pin `nox` and the test dependencies, while the `coverage` session explicitly installs `.[test,cli]`, runs a short Hydra import probe, and emits a targeted error if the extras are still missing.【F:pyproject.toml†L37-L47】【F:noxfile.py†L535-L551】 As a result, `nox -s tests` either installs the needed plug-ins automatically or aborts with guidance to install the Codex test extras, eliminating the surprise ModuleNotFoundError.
