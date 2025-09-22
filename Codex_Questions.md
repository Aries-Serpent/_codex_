# Codex Questions Backlog

_No questions captured during Run 1 (2025-09-22)._  Update this file whenever an error occurs following the template in `AUDIT_PROMPT.md`.

Question for ChatGPT @codex 2025-09-22T21:52:08+00:00:
While performing [STEP_6:Finalisation - run pytest], encountered the following error:
ModuleNotFoundError: No module named 'hydra.extra'
Context: `pytest -q tests/tools/test_validate_fences.py` triggered plugin auto-discovery pulling missing optional dependencies.
What are the possible causes, and how can this be resolved while preserving intended functionality?

Question for ChatGPT @codex 2025-09-22T21:53:20+00:00:
While performing [STEP_6:Finalisation - run pre-commit], encountered the following error:
`pre-commit run --all-files` triggered legacy lint failures across the repository (ruff/black) and was interrupted after reporting thousands of issues.
Context: Need guidance on scoping pre-commit to new audit artefacts without refactoring the entire codebase.
What are the possible causes, and how can this be resolved while preserving intended functionality?

Question for ChatGPT @codex 2025-09-22T22:13:37+00:00:
While performing [STEP_6:Finalisation - run pre-commit], encountered the following error:
bash: command not found: pre-commit
Context: Running `pre-commit run --files AUDIT_PROMPT.md CHANGELOG.md OPEN_QUESTIONS.md reports/report_templates.md reports/security_audit.md reports/observability_runbook.md` on a fresh container without pre-commit installed.
What are the possible causes, and how can this be resolved while preserving intended functionality?

Question for ChatGPT-5 @codex 2025-09-22T22:56:02Z:
While performing [STEP_6:Finalisation - run pre-commit], encountered the following error:
bash: command not found: pre-commit
Context: Running `pre-commit run --files AUDIT_PROMPT.md CHANGELOG.md OPEN_QUESTIONS.md reports/local_checks.md reports/reproducibility.md docs/validation/Offline_Audit_Validation.md scripts/codex_local_audit.sh scripts/codex-audit` on a fresh container before installing pre-commit.
What are the possible causes, and how can this be resolved while preserving intended functionality?

Question for ChatGPT @codex 2025-09-22T23:43:45Z:
While performing [STEP_6:Finalisation - run nox coverage], encountered the following error:
ModuleNotFoundError: No module named 'hydra.extra'
Context: `nox -s tests` triggers the coverage session which auto-discovers pytest plugins and fails when optional Hydra extras are absent.
What are the possible causes, and how can this be resolved while preserving intended functionality?

