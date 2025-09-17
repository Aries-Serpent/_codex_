# Codex Remediation Plan – Phased Outline (2025-09-17)

## Purpose & Inputs

This plan synthesizes the open items recorded in:

- `docs/status_update_outstanding_questions.md`
- `docs/question_handling_reference.md`
- `docs/suggested_tasks/status_update_2025-09-17.md`

Its goal is to provide a self-manageable roadmap that keeps the codebase queryable, the logging substrate healthy (including the `.codex/session_logs.db` datablot), and the documentation/configuration layers in sync.

## Phase 0 – Foundation & Instrumentation

1. **Refresh inventory of automation artefacts**
   - Export current `.codex/notes`, `ERROR_LOG.md`, `CODEBASE_AUDIT_*`, and session NDJSON files into a dated bundle.
   - Confirm that `.codex/session_logs.db` has the expected schema; vacuum or migrate if needed.
2. **Baseline repository introspection**
   - Run `rg`/`find` scans to ensure duplicate or orphaned files (e.g., `training.py01`) are mapped.
   - Regenerate repository maps (`docs/suggested_tasks/status_update_2025-09-17.md` §1) to compare against the live tree.
3. **Toolchain preflight**
   - In a fresh virtualenv, execute `pre-commit --version`, `nox --version`, `pytest --version`, `mkdocs --version`, and log into `.codex/session_logs.db` for traceability.
   - Capture the environment snapshot (Python, CUDA, extras installed) in `docs/suggested_tasks/telemetry_2025-09-17.md` (new file) for downstream runs.

## Phase 1 – Urgent Remediations (Top 5)

### U1 – Restore Gate Tooling for `pre-commit`
- **Source gaps**: Outstanding table rows for Phase 6 & validation failures (multiple timestamps).
- **Impacted components**: `requirements-dev.txt`, `noxfile.py`, CI/local setup docs, `.codex/pre_manifest.json` allowlists, `.codex/session_logs.db` instrumentation.
- **Actions**:
  1. Add an explicit `pre-commit` dependency in the validation environment bootstrap scripts (`scripts/` or `codex_setup.py`).
  2. Extend `nox -s tests` to install/verify `pre-commit`; log success/failure into session datablot.
  3. Update `docs/question_handling_reference.md` to reflect the gate requirement.
- **Exit criteria**: Validation logs show `pre-commit` present; outstanding question rows marked "No" under "Still Valid?".

### U2 – Ensure `nox` Availability Across Phases
- **Source gaps**: Outstanding table (`Validation: nox` and related Phase 6 rows).
- **Impacted components**: `requirements-dev.txt`, `CHANGELOG_SESSION_LOGGING.md`, `docs/status_update_outstanding_questions.md` (follow-up entry).
- **Actions**:
  1. Bundle `nox` into developer and automation requirements; document offline installation instructions.
  2. Add a bootstrap check in `codex_workflow.py` that records presence/absence in `.codex/session_logs.db`.
  3. Mirror the remediation in `docs/suggested_tasks/status_update_2025-09-17.md` §5 (Local Tests & Gates).
- **Exit criteria**: `nox -s tests` succeeds in clean environments; outstanding entries retired.

### U3 – Stabilize Coverage Session (`pytest-cov` / gating)
- **Source gaps**: Outstanding table row for `nox -s tests` coverage failures; capability audit (Evaluation & Metrics) referencing coverage gaps.
- **Impacted components**: `noxfile.py`, `requirements-dev.txt`, `docs/suggested_tasks/status_update_2025-09-17.md` (Diff 5 discussion), `.codex/session_logs.db` for metrics.
- **Actions**:
  1. Detect whether `pytest-cov` is installed; if absent, install or gracefully degrade coverage thresholds.
  2. Update `nox` session definitions with deterministic coverage targets and log results into session datablot.
  3. Document fallback behaviour in README/testing appendix.
- **Exit criteria**: `nox -s tests` completes with coverage recorded and session log entry referencing the coverage JSON.

### U4 – Harden Test Suite Against Optional Dependency Drift
- **Source gaps**: Outstanding table rows for pytest failures; capability audit items on optional dependency pitfalls.
- **Impacted components**: `pyproject.toml` extras, `requirements/` manifests, `tests/` fixtures, `.codex/notes/Codex_Questions.md` (answer log), `.codex/session_logs.db` for error tracking.
- **Actions**:
  1. Identify each failing module (Hydra, MLflow, locale) and create a deterministic dependency shim in `requirements-tests-optional.txt`.
  2. Introduce skip markers or stub adapters for when the dependency is intentionally absent; document the logic in `docs/question_handling_reference.md`.
  3. Append gating instructions to `docs/suggested_tasks/status_update_2025-09-17.md` §5.
- **Exit criteria**: Test runs succeed regardless of optional dependency presence, with logs referencing the fallback decisions.

### U5 – Guard the Training CLI Against Missing `torch`
- **Source gaps**: Outstanding table row (2025-09-13) for `ModuleNotFoundError`; capability audit (Training Engine, ChatGPT Modeling).
- **Impacted components**: `src/codex_ml/cli/train_model.py` (or equivalent), `pyproject.toml` extras, `docs/suggested_tasks/status_update_2025-09-17.md` (Diff 3), README quickstart, `.codex/session_logs.db` run metadata.
- **Actions**:
  1. Add a runtime guard that surfaces a clear remediation (`pip install codex_ml[torch]`) and records the incident in session logs.
  2. Provide a CPU-only dry-run path for smoke tests; capture expected behaviour in docs.
  3. Update outstanding question ledger after verifying fix.
- **Exit criteria**: CLI emits actionable message without traceback when `torch` is missing; outstanding entry marked resolved.

## Phase 2 – Quick Wins (Top 5)

### Q1 – Remove Duplicate `training.py01`
- **Components**: `src/codex/training.py01`, audit references, `docs/suggested_tasks/status_update_2025-09-17.md` (High-Signal Finding #1).
- **Steps**:
  1. Confirm no import references remain using `rg "training.py01"`.
  2. Delete the duplicate file; note in `CHANGELOG_CODEX.md` and session datablot.
  3. Update documentation to prevent reintroduction.

### Q2 – Implement `load_latest` in Checkpointing
- **Components**: `src/codex_ml/utils/checkpointing.py`, tests, docs.
- **Steps**:
  1. Add the load helper (per Atomic Diff 1); write integration tests.
  2. Document CLI usage (`--resume-from`) in README and outstanding ledger.
  3. Store last resume metadata in `.codex/session_logs.db` for reproducibility.

### Q3 – Deterministic Dataset Loader & Manifest
- **Components**: `src/codex_ml/data/registry.py`, dataset manifests, docs.
- **Steps**:
  1. Implement seeded shuffling with manifest emission (Atomic Diff 5).
  2. Archive manifests under `artifacts/data_manifests/` and record in session datablot.
  3. Update documentation with usage instructions and reproduction steps.

### Q4 – Introduce System Metrics Logger
- **Components**: `src/codex_ml/monitoring/system_metrics.py`, CLI flags, docs, logs directory.
- **Steps**:
  1. Create psutil-based logger (Atomic Diff 4) with JSONL output into `logs/system_metrics/`.
  2. Wire optional flag into training CLI and document expected outputs.
  3. Index generated metric files inside `.codex/session_logs.db` for quick lookup.

### Q5 – Patch `tests_docs_links_audit` Script
- **Components**: `analysis/tests_docs_links_audit.py` (or equivalent), docs, outstanding ledger.
- **Steps**:
  1. Add missing `root = Path(".")` initialization; ensure script logs success.
  2. Update `docs/question_handling_reference.md` quick response checklist to reference the fix.
  3. Close corresponding outstanding entry.

## Phase 3 – Continuous Coverage of Missing Components

To guarantee that every incomplete/missing element is tracked, execute the following cycle each sprint:

1. **Files & Code** – Use Appendix A to verify each gap (monkeypatch/search placeholders, optional dependency fallbacks, evaluation stubs). Log remediation status in `.codex/session_logs.db`.
2. **Documentation** – Sync README, MkDocs, and quick references whenever plan tasks land; rerun `mkdocs build --strict=false` until strict mode can be safely restored.
3. **Configuration** – Audit Hydra configs (`configs/`) to ensure new features (resume, monitoring) have base + override entries.
4. **Artifacts** – Rotate logs/metrics/manifests into `artifacts/` with checksums; maintain `.codex/pre_manifest.json` allowlists.
5. **Database & Session Datablot** – Record every remediation attempt/result in `.codex/session_logs.db` and NDJSON logs; vacuum monthly.
6. **Queryable Repo State** – Keep `docs/status_update_outstanding_questions.md` and `.codex/notes/Codex_Questions.md` synchronized to preserve searchability.

## Phase 4 – Automation & Feedback Loop

1. **Automated dashboards** – Generate a weekly summary from `.codex/session_logs.db` showing progress across urgent/quick-win tasks.
2. **PR gating** – Require that pull requests touching plan items reference the relevant Appendix A line for traceability.
3. **Error capture** – Continue using the standard "Question for ChatGPT" template; ingest entries into the outstanding ledger and update Appendix A statuses.
4. **Retrospectives** – At the end of each iteration, diff the outstanding ledger and Appendix A to ensure no regressions; schedule work accordingly.

## Appendix A – Inventory of Incomplete / Missing Components & Plan Coverage

| Gap (from status update) | Category | Plan coverage | Notes |
| --- | --- | --- | --- |
| Empty `monkeypatch` module | Files/Code | Phase 3 (Files & Code) – backlog after quick wins | Requires clarified requirements before implementation. |
| Empty `search` module | Files/Code | Phase 3 – backlog | Same as above; document intent or remove. |
| Sparse `safety` implementation | Code/Docs | Phase 3 + Phase 4 dashboards | Expand filters post-urgent fixes. |
| Metrics returning dummy values | Code | Phase 3 (Files & Code) | Implement real metrics once dependency strategy finalized. |
| Stub connectors | Code | Phase 3 | Document expectations and assign ownership. |
| Skeleton `deploy` assets | Docs/Config | Phase 3 | Defer until deployment roadmap defined. |
| Duplicate `training.py01` | Code | Phase 2 – Q1 | Quick win removal. |
| Optional dependency fallbacks raising generic errors | Code | Phase 1 – U4 | Harden messaging and fallbacks. |
| Placeholder directories in configs | Config | Phase 3 | Populate as features mature. |
| Missing resume functionality | Code | Phase 2 – Q2 | Implement load helper. |
| Logging gaps / lack of system metrics | Artifacts/Monitoring | Phase 2 – Q4 | Add psutil logger. |
| Checkpoint resume absent | Code | Phase 2 – Q2 | Covered via load helper. |
| Dataset reproducibility lacking | Data/Artifacts | Phase 2 – Q3 | Manifest + deterministic shuffle. |
| Safety & secrets scanning minimal | Docs/Code | Phase 3 | Integrate scanning in follow-up iteration. |
| Evaluation limited to token metrics | Code | Phase 3 | Expand after urgent gating tasks. |
| Monitoring optional / NDJSON growth | Artifacts | Phase 2 – Q4 + Phase 3 rotation | Add structured metrics + retention policy. |
| No Docker/CI pipeline | Config/Deploy | Phase 3 backlog | Document requirement and schedule later sprint. |
| Plugin registries empty | Code | Phase 3 backlog | Encourage sample implementations. |
| Seeds & environment capture partial | Config/Artifacts | Phase 3 – configuration audits | Document seeds, capture environment snapshots. |
| Dataset versioning missing | Data | Phase 2 – Q3 (manifest) | Evaluate DVC after manifest adoption. |
| RNG state not saved | Code | Phase 3 backlog | Add to checkpoint manager in future iteration. |
| `.env` committed | Docs/Safety | Phase 3 backlog | Replace with `.env.example` only. |
| Large logs unchecked into repo | Artifacts | Phase 3 rotation | Purge/move to git-ignored paths. |
| CLI scripts lacking tests | Code/Tests | Phase 3 backlog | Prioritize after gating stable. |
| No automated release process | Deploy | Phase 3 backlog | Introduce when CI is ready. |
| Potential license conflicts | Docs/Legal | Phase 3 backlog | Audit `LICENSES` directory. |
| Mixed dependency pinning | Config | Phase 3 | Align `pyproject` vs lockfiles. |
| Tests for docs links failing (`root` undefined) | Code | Phase 2 – Q5 | Quick fix. |
| `file_integrity_audit` allowlists outdated | Tooling | Phase 1 – U1 (allowlist updates) & Phase 3 artifacts | Expand allowlists alongside gating fixes. |
| MkDocs strict mode disabled | Docs | Phase 3 – documentation sync | Revisit once docs coverage improves. |
| Training CLI torch missing | Code | Phase 1 – U5 | Guard and document fallback. |
| Session logging automation improvements | Database | Phase 0 instrumentation + Phase 3 loops | Maintain datablot health. |

This phased plan keeps urgent blockers front-loaded, delivers fast wins to increase momentum, and methodically iterates across every identified gap—ensuring the Codex environment remains organized, queryable, and well-instrumented for future automation sessions.
