# Asset-Driven Instruction Playbook

**Last Updated:** 2026-06-22

This playbook codifies how to turn the Repo Map, Fix folder cadence, and Security Sweep prompts into reproducible instructions that lean on the repository's existing artefacts.

## 1. Repo Map & Quick Wins
1. Refresh the repository map so the file index is current:
   - Run `tree -a -L 2 > reports/repo_map.md` (or the equivalent scripted task in `cli/workflow.py`) to capture the top-level structure.
   - Skim `reports/repo_map.md` for directories with sparse test/docs coverage and note candidates for quick wins.【F:reports/repo_map.md†L1-L29】
2. Cross-reference open opportunities:
   - Read `docs/troubleshooting/open_questions.md` and highlight unresolved menu items or questions that align with the candidate directories.【F:docs/troubleshooting/open_questions.md†L1-L28】
   - Capture the chosen quick wins in your run notes and update `docs/troubleshooting/open_questions.md` once you ship the improvement.
3. Summarize the mapping outcome by appending a short bullet list of “next touch” targets to `reports/branch_analysis.md` so the next run inherits the context.

## 2. Fix Folder Flow
1. Scope one atomic fix at a time. Start from the quick-win list above and open the relevant code/tests before editing so the resulting diff stays focused.
2. Capture the fix as a single patch under `patches/pending/<date>_<slug>.patch` using `git diff > patches/pending/...`.
3. Validate locally before promoting the patch:
   - Run `pre-commit run --files <touched files>` to satisfy the lint/format gates defined in `.pre-commit-config.yaml`.
   - Execute the required nox sessions (`nox -s audit` and `nox -s fence_tests`) to mirror the CI-quality checks stored in `nox_sessions/` scripts.【F:nox_sessions/audit.py†L1-L15】【F:nox_sessions/fence_tests.py†L1-L13】
4. When the gates pass, move the patch from `patches/pending/` into a branch commit and document the outcome in the relevant changelog or report.

## 3. Security Sweep Protocol
1. Run Semgrep with the maintained rule packs:
   - Invoke `semgrep --config semgrep_rules/python-security.yaml --json > reports/security_findings.json` (repeat for other packs if needed) so the results retain rule IDs like `py-requests-verify-disabled` for traceability.【F:semgrep_rules/python-security.yaml†L1-L32】
2. Prioritize findings by mapping each rule ID to the STRIDE category documented in `ops/threat_model/STRIDE.md`. Log the mapping and residual risk in `reports/gap_risk_resolution.md` under the security capability.【F:ops/threat_model/STRIDE.md†L1-L8】
3. Convert high-risk findings into mitigations:
   - Draft a patch per finding (following the Fix Folder flow above) and note containment steps or compensating controls.
   - Reference the Semgrep rule ID and the corresponding STRIDE threat in the mitigation notes so reviewers can trace the rationale end-to-end.
4. Close the loop by updating `docs/troubleshooting/open_questions.md` with any remaining security follow-ups and by appending a summary line to the weekly status update (`reports/_codex_status_update-YYYY-MM-DD.md`).
