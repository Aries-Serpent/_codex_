# [Prompt]: Offline Audit Execution Runner

> Generated: 2025-09-22 | Maintainer: audit-refresh

## Repository Context

- Repository: `Aries-Serpent/_codex_`
- Primary language: Python (≈94%) with supporting Shell scripts.
- Default/active branch discovery (local only):
  - `git status -sb`
  - `git branch --sort=-committerdate`
  - Document the focus branch and justify it in `reports/branch_analysis.md`.
- Remote access is disabled. **Do not** run network operations (`git fetch`, curl to GitHub, etc.).

## Guardrails & Cadence

- **Offline only.** No GitHub Actions, remote APIs, or cost-incurring services.
- **Audit-first workflow.** Each run selects exactly **three** Menu items and produces 1–3 atomic diffs plus matching docs/tests.
- **Fence discipline.** Every payload emitted by this workflow is a single fenced block with a language tag. Unified diffs use ```diff fences.
- **Local gates.** Use the provided commands; pre-commit and pytest must pass locally.

## Menu (Select 3 per Run)

1. Repo map
2. Fix folder
3. Quality gates
4. Security
5. Observability
6. Performance
7. Docs polish
8. Self-management

Record the chosen items and future picks in `OPEN_QUESTIONS.md`.

## Execution Phases

1. **Preparation**
   - Detect repo root (`git rev-parse --show-toplevel`).
   - Inspect available branches; confirm offline mode; activate `.venv` if present.
   - Install or verify tooling (`pip install -r requirements-dev.txt`).
2. **Search & Mapping**
   - Update `reports/repo_map.md` and `reports/branch_analysis.md` with new observations.
   - Capture notable directories, risks, and quick wins.
3. **Best-Effort Construction**
   - For the selected Menu items, implement improvements with minimal, reviewable diffs.
   - Align `AUDIT_PROMPT.md` sections with current workflow expectations.
4. **Controlled Pruning**
   - Only defer items after exploring options; log rationale in `reports/deferred.md`.
5. **Error Capture**
   - On any failure, append a question block to `Codex_Questions.md` (format below).
6. **Finalisation**
   - Produce 1–3 atomic diffs with tests/docs.
   - Run local gates and update `CHANGELOG.md` and `OPEN_QUESTIONS.md`.

## Required Artefacts

| File | Purpose |
| --- | --- |
| `AUDIT_PROMPT.md` | Up-to-date audit instructions and templates. |
| `reports/repo_map.md` | Current repo topology and quick wins. |
| `reports/branch_analysis.md` | Branch focus justification. |
| `reports/capability_audit.md` | Capability status table with risks and plans. |
| `reports/high_signal_findings.md` | Prioritised gaps/quick wins. |
| `reports/local_checks.md` | Commands and tooling status. |
| `reports/reproducibility.md` | Checklist for deterministic runs. |
| `reports/deferred.md` | Logged deferrals with rationale. |
| `Codex_Questions.md` | Error capture backlog. |
| `CHANGELOG.md` | Log of shipped changes per run. |
| `OPEN_QUESTIONS.md` | Outstanding next steps (including Menu selections). |

Consult `reports/report_templates.md` for copy/paste-ready placeholders covering each artefact. Update the template library alongside substantive changes so future runs stay consistent.

## Atomic Diff Template

For each diff, document:

````diff
# why
# risk
# rollback
# tests/docs
````

When multiple files change in one diff, keep the rationale cohesive and reference the relevant reports.

## Local Commands Reference

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
python tools/validate_fences.py --strict-inner
pytest -q
```

Extend with targeted pytest selections or nox sessions as needed.

## Error Capture Format

Record failures in `Codex_Questions.md` using:

```text
Question for ChatGPT @codex {{TIMESTAMP}}:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

## Reproducibility Expectations

- Capture interpreter version (`python --version`) and pip freeze snapshot when relevant.
- Note Hydra overrides or CLI flags used for reproducing experiments.
- Reference seed-setting strategy in reports/tests to maintain determinism.

## Deferred Work Log

- Summarise deferred decisions in `reports/deferred.md` with reason and proposed follow-up Menu items.
- Carry forward unresolved questions to `OPEN_QUESTIONS.md` and close them when resolved.
