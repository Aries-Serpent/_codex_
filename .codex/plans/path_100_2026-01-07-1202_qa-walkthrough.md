# Path to 100% Coverage: QA Walkthrough Deepening (2026-01-07-1202)

## Objective
Reach full repo-wide QA walkthrough coverage with deterministic, file-level sampling per domain and a documented follow-up plan for deeper inspections.

## Current coverage status
- Directory-level traversal complete across top-level domains.
- File-level sampling completed for each domain with ≥3 file checks.
- Target minimum coverage for this pass: ≥70% of domains with explicit risks/concerns (achieved).

## Plan (deterministic)
1. **Inventory support tooling**
   - Use `scripts/generate_ai_index.py` for indexed repo scanning to reduce manual misses.
   - Use `tools/docs/scan_links.py` to validate documentation references as needed.
2. **Deep file-level sampling (next iteration)**
   - For each domain, select 3–5 additional files beyond the current sampling set.
   - Capture: purpose, dependencies, potential side effects, and risk notes.
3. **Edge case coverage**
   - Identify files with optional dependency guards (e.g., stubs) and confirm expected behavior.
   - Document any environment-specific concerns (GPU, optional libs, offline constraints).
4. **Verification**
   - Run targeted agent tests and document outputs in `.codex/results.md`.
   - If feasible, run a broader smoke suite (`pytest -m smoke`) to improve coverage signal.

## Risks / Remediation strategies
- **Risk:** Optional dependency shims can mask missing modules in production.
  - **Mitigation:** Track optional deps in docs and add checks in deployment scripts.
- **Risk:** Legacy configs and Dockerfiles may drift from canonical paths.
  - **Mitigation:** Add explicit migration notes in docs and deprecate old paths in tooling.

## Next verification commands
- `python -m pytest -q tests/agents/test_mental_mapping_core_flows.py tests/agents/test_quantum_game_core_flows.py`
- `pytest -m smoke` (if environment supports optional deps)

## Progress update (2026-01-07)
- File-level sampling expanded with 3 additional files per domain and risks documented.
- Tooling runs:
  - `scripts/generate_ai_index.py` generated 5,353 file indices, 22,151 entities, 19,889 semantic mappings.
  - `tools/docs/scan_links.py` produced `artifacts/docs_link_audit/links.json` with 20,364 links (4,963 relative, 766 missing).

## Smoke test failures observed (2026-01-07)
- `tests/deployment/test_k8s_manifests.py::test_deployment_parse_manifests_if_present` expects `kind` in Helm chart metadata.
- `tests/smoke/test_config_validate_cli.py` failing CLI invocation (`codex_ml.cli.validate`) due to Typer subcommand parsing.
- `tests/specs/test_audit_*` failures due to audit runner CLI args (`stage S1`) and missing optional deps (hydra/mlflow).

### Remediation path (next iteration)
1. Review `scripts/space_traversal/audit_runner.py` CLI args and align with tests for `stage` subcommand.
2. Ensure `codex_ml.cli.validate` exposes `file` subcommand that accepts path argument correctly.
3. Clarify k8s manifest parsing expectations for Helm `Chart.yaml` vs deployment manifests.
