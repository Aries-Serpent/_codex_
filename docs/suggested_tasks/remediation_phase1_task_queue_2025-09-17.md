# Codex Remediation Task Queue – Phase 1 Execution Packet (2025-09-17)

## 0. Orientation & Linkage

This execution packet translates the phased remediation outline recorded in `docs/suggested_tasks/remediation_plan_status_update_2025-09-17.md` into immediately actionable work items. The focus is on the first remediation phase, covering the top five urgent gates (U1–U5) and the top five quick wins (Q1–Q5) that were enumerated in the foundational plan. Each task card below preserves the traceability back to the source findings (status update, capability audit, outstanding questions) while spelling out concrete steps, deliverables, instrumentation requirements, and forward-looking queue triggers that will cascade into the next remediation phase as soon as Phase 1 closes out.

Key conventions used in this packet:

- **Owner** denotes the accountable individual or automation loop for the task. If not yet assigned, set to `TBD` and capture assignment in `.codex/session_logs.db` before work commences.
- **Logging** spells out the required updates to `.codex/session_logs.db`, NDJSON session traces, or supplemental registers (e.g., `docs/status_update_outstanding_questions.md`).
- **Queue trigger** documents precisely which follow-on task (usually from Phase 2 or later) should be placed on deck once the current card’s exit criteria are satisfied, ensuring the iterative workflow keeps flowing without manual backlog grooming.

## 1. Execution Cadence for Phase 1

1. Kick off with the Urgent Gate series (U1 through U5) because failing gates block every downstream improvement.
2. As each urgent gate closes, immediately enqueue the paired quick-win remediation (see "Queue trigger" on each urgent task card). This keeps high-leverage polish items ready for batched execution once stability is restored.
3. When all five urgent gates are marked complete and their queue triggers have been issued, begin executing the quick-win cards (Q1 through Q5) in numerical order.
4. After each quick win is verified, push the explicitly named successor tasks (mostly Phase 2+ backlog items from Appendix A of the master plan) into the active queue. Document the queuing activity in both the task card and `.codex/session_logs.db`.
5. When all ten Phase 1 cards have met their exit criteria and their queue triggers have been dispatched, compile a completion digest summarizing outcomes, metrics, and links to artifacts. Store the digest at `docs/suggested_tasks/remediation_phase1_completion_report_2025-09-17.md` (new file) and mark Phase 2 as unblocked.

## 2. Phase 1A – Urgent Gate Activation (Top Five Urgent Tasks)

### Task U1 – Restore Gate Tooling for `pre-commit`
- **Source references**: Phase 1/U1 in remediation plan; outstanding questions table entries dated 2025-09-13 and 2025-09-17 concerning missing `pre-commit` gating.
- **Objective**: Guarantee that `pre-commit` is installed, discoverable, and enforced in all dev/automation contexts, eliminating false negatives in gate validation.
- **Preconditions**: Fresh Python environment prepared; access to `requirements-dev.txt`, `scripts/`, `codex_setup.py`, and `.codex/session_logs.db`.
- **Actions**:
  1. Update `requirements-dev.txt` and any bootstrap scripts to declare `pre-commit` explicitly (pin to version compatible with existing hooks).
  2. Modify `noxfile.py` so that the `tests` session installs and runs `pre-commit run --all-files` prior to pytest execution, capturing success/failure output.
  3. Document the enforced gate in `docs/question_handling_reference.md` and the remediation plan (cross-reference Section 5, Local Tests & Gates).
  4. Execute the updated nox session inside a clean environment to verify the gate, storing the command transcript in `.codex/session_logs.db` with a `tool` role entry.
  5. Update the relevant rows in `docs/status_update_outstanding_questions.md`, flipping "Still Valid?" to "No" once verified.
- **Deliverables**: Updated requirement manifests, revised nox session, refreshed documentation, and a session log entry confirming gate execution.
- **Exit criteria**: `nox -s tests` finishes with `pre-commit` execution recorded; outstanding question rows resolved; documentation updated.
- **Logging**: Append a row to `.codex/session_logs.db` indicating gate restoration, plus add a changelog bullet to `CHANGELOG_SESSION_LOGGING.md`.
- **Queue trigger**: Upon completion, enqueue Quick Win **Q1 – Remove Duplicate `training.py01`** to kick off codebase cleanup reliant on functioning gates.

### Task U2 – Ensure `nox` Availability Across Phases
- **Source references**: Phase 1/U2; outstanding validation rows citing missing `nox` binary.
- **Objective**: Make `nox` a guaranteed dependency for developers and automation, ensuring test orchestration consistency.
- **Preconditions**: Access to `requirements-dev.txt`, `codex_workflow.py`, and logging databases.
- **Actions**:
  1. Amend `requirements-dev.txt` (and any setup scripts) to include `nox` with an explicit version guard.
  2. Extend `codex_workflow.py` or equivalent orchestration script to probe for `nox --version`, logging results to `.codex/session_logs.db` with severity levels.
  3. Update `docs/suggested_tasks/status_update_2025-09-17.md` Section 5 to reflect the enforced availability and provide offline installation steps.
  4. Run the probe in both a fresh environment and the baseline environment, capturing outputs in the session datablot.
  5. Close out outstanding question entries tied to `nox` availability.
- **Deliverables**: Updated requirement files, orchestration scripts, documentation, and log entries verifying `nox` availability checks.
- **Exit criteria**: Automated probe reports success; documentation cross-references updated; outstanding entries closed.
- **Logging**: Record both the probe attempt and its success/failure in `.codex/session_logs.db`; add a `system` role entry summarizing the remediation.
- **Queue trigger**: Once `nox` availability is confirmed, queue Quick Win **Q2 – Implement `load_latest` in Checkpointing** (requires stable tooling).

### Task U3 – Stabilize Coverage Session (`pytest-cov` / gating)
- **Source references**: Phase 1/U3; capability audit notes on evaluation and coverage deficits.
- **Objective**: Reinstate deterministic coverage enforcement via `pytest-cov`, ensuring `nox -s tests` enforces agreed thresholds.
- **Preconditions**: Access to `noxfile.py`, `requirements-dev.txt`, coverage configuration, and test infrastructure.
- **Actions**:
  1. Verify/install `pytest-cov` and related plugins within the testing environment manifest.
  2. Update the `tests` session in `noxfile.py` to run pytest with `--cov=src --cov-report=term-missing --cov-fail-under=<target>` (align target with remediation plan suggestions).
  3. Add structured JSON coverage output writing (e.g., `coverage_summary.json`) and ingest path references into `.codex/session_logs.db`.
  4. Document fallback behaviour for constrained environments (e.g., skip coverage with explicit log note) in README and question-handling docs.
  5. Execute the session, confirm coverage gating, and archive the produced coverage JSON under `artifacts/coverage/`.
- **Deliverables**: Updated automation scripts, coverage report artifacts, documentation updates, and log records.
- **Exit criteria**: Coverage gate enforced with recorded metrics; documentation instructs remediation steps; outstanding rows resolved.
- **Logging**: Log coverage metrics and file paths in `.codex/session_logs.db` using `assistant` role entries for computed data.
- **Queue trigger**: After stabilizing coverage, queue Quick Win **Q3 – Deterministic Dataset Loader & Manifest** (which depends on reliable tests).

### Task U4 – Harden Test Suite Against Optional Dependency Drift
- **Source references**: Phase 1/U4; outstanding question entries referencing Hydra/MLflow import failures; capability audit (Optional Dependency Pitfalls).
- **Objective**: Make tests resilient whether optional dependencies are installed, avoiding spurious failures during gating.
- **Preconditions**: Insight into failing tests, access to test fixtures, ability to modify requirements and docs.
- **Actions**:
  1. Catalogue failing modules by running pytest with logging to capture `ModuleNotFoundError` instances; store the traceback digest in `artifacts/test_failures/`.
  2. For each optional dependency, introduce deterministic shims: (a) add extras to `requirements-tests-optional.txt`, (b) add pytest skip markers or stubs when dependencies are absent.
  3. Update test fixtures to gracefully handle missing libraries, ensuring explanatory warnings are emitted instead of raw tracebacks.
  4. Document the shim/skip strategy in `docs/question_handling_reference.md` and the remediation plan.
  5. Re-run the test suite with and without the optional packages installed, capturing both results in `.codex/session_logs.db`.
- **Deliverables**: Updated test infrastructure, documentation, failure archives, and dual-run logs.
- **Exit criteria**: Test suite passes in both dependency states; outstanding question entries are marked resolved with notes referencing the shim approach.
- **Logging**: Store both run outputs and a summary of dependency states in `.codex/session_logs.db`; annotate `artifacts/test_failures/README.md` with reproduction steps.
- **Queue trigger**: Once dependency drift hardening is verified, queue Quick Win **Q4 – Introduce System Metrics Logger** (relies on stable test harness for new monitoring).

### Task U5 – Guard the Training CLI Against Missing `torch`
- **Source references**: Phase 1/U5; outstanding question entry dated 2025-09-13 for `ModuleNotFoundError: torch`.
- **Objective**: Provide a clear, user-friendly guard that instructs operators how to install torch extras and offers a CPU-only fallback.
- **Preconditions**: Ability to modify training CLI modules, docs, and tests.
- **Actions**:
  1. Add runtime detection in the training CLI that checks for `torch` availability before main execution, emitting actionable instructions and returning non-zero exit codes without stack traces.
  2. Provide a `--dry-run` or `--cpu-only` flag that simulates execution without requiring `torch`, enabling smoke tests.
  3. Update README quickstart and outstanding question ledger with remediation details.
  4. Log both the guard invocation (with missing torch) and a successful dry-run to `.codex/session_logs.db`.
  5. Write regression tests validating the guard behaviour and dry-run path, ensuring they run inside the coverage session introduced in Task U3.
- **Deliverables**: Enhanced CLI guard, documentation updates, regression tests, and log records.
- **Exit criteria**: Missing `torch` scenario surfaces a helpful remediation message; dry-run executes without error; outstanding question marked resolved.
- **Logging**: Capture guard activation (error path) and dry-run success as separate entries in `.codex/session_logs.db` with references to generated artifacts.
- **Queue trigger**: Once the training CLI guard is live, queue Quick Win **Q5 – Patch `tests_docs_links_audit` Script**, which benefits from stabilized tooling and CLI behaviour.

## 3. Phase 1B – Quick Win Activation (Top Five Quick Wins)

Begin executing these cards once all urgent gate tasks have been completed and their queue triggers have been issued. Maintain strict logging parity with the urgent tasks to keep the remediation history queryable.

### Task Q1 – Remove Duplicate `training.py01`
- **Source references**: Phase 2/Q1 of remediation plan; high-signal finding #1.
- **Objective**: Eliminate the redundant `training.py01` file after verifying no code paths rely on it, reducing confusion.
- **Preconditions**: Completion of Task U1 (ensures gate tooling is operational) and confirmation via `rg` scans.
- **Actions**:
  1. Execute `rg "training.py01" -n` to confirm absence of imports or references.
  2. Delete `src/codex/training.py01` and update changelog entries (`CHANGELOG_CODEX.md`) to record removal.
  3. Run full test suite (`nox -s tests`) to confirm no regressions; archive the run log in `artifacts/test_runs/`.
  4. Update documentation referencing duplicate files to note resolution (e.g., capability audit section in the status update).
  5. Log the deletion event and validation run into `.codex/session_logs.db` with artifact pointers.
- **Deliverables**: Cleaned source tree, changelog entry, archived test log, documentation adjustments.
- **Exit criteria**: Tests pass post-removal; documentation no longer references the duplicate file; logs captured.
- **Logging**: Document the removal in session DB and update `docs/status_update_outstanding_questions.md` to mark the associated finding resolved.
- **Queue trigger**: Queue Phase 2 backlog item **B1 – Consolidate Training Documentation and CLI Flags** (from Appendix A) for subsequent iteration once Q1 closes.

### Task Q2 – Implement `load_latest` in Checkpointing
- **Source references**: Phase 2/Q2; Atomic Diff 1.
- **Objective**: Provide resume functionality by adding `load_latest` (or similar) to `CheckpointManager` and wiring CLI support.
- **Preconditions**: Task U2 completion (ensuring tooling stability) and accessible testing harness.
- **Actions**:
  1. Implement `load_latest` with robust error handling (glob pattern search, checksum validation if available).
  2. Add CLI support (`--resume-from`) to the training interface, updating help text and documentation.
  3. Create unit/integration tests that save a checkpoint and ensure `load_latest` restores the state correctly.
  4. Document usage in README and outstanding question ledger; add manifest references to `.codex/session_logs.db`.
  5. Archive a demonstration run (save + resume) with logs under `artifacts/checkpoint_resume/`.
- **Deliverables**: Updated checkpointing module, CLI flag, tests, documentation, and demonstration artifacts.
- **Exit criteria**: Tests pass; CLI resume path validated; documentation updated; outstanding entries resolved.
- **Logging**: Capture demonstration runs and test results in `.codex/session_logs.db` with pointers to artifacts.
- **Queue trigger**: Queue Phase 2 backlog item **B2 – Introduce Checkpoint Retention Policies** upon completion.

### Task Q3 – Deterministic Dataset Loader & Manifest
- **Source references**: Phase 2/Q3; Atomic Diff 5.
- **Objective**: Ensure dataset loaders perform seeded shuffling and emit manifest files for reproducibility.
- **Preconditions**: Task U3 completion (stable coverage gating) and accessible dataset samples.
- **Actions**:
  1. Modify the loader to perform seeded shuffling and manifest emission, with configuration hooks for seed override and manifest directory.
  2. Write tests verifying determinism (same seed -> same order, different seed -> different order) and manifest contents.
  3. Update documentation detailing manifest format, storage location, and integration with `.codex/session_logs.db`.
  4. Generate sample manifests for canonical datasets, storing them under `artifacts/data_manifests/` with checksums.
  5. Log test results and manifest paths in `.codex/session_logs.db`, linking to reproduction instructions.
- **Deliverables**: Enhanced loader, tests, documentation, sample manifests, and logs.
- **Exit criteria**: Tests demonstrate determinism; manifests archived; documentation and outstanding entries updated.
- **Logging**: Record both deterministic test outcomes and sample manifest generation in session DB.
- **Queue trigger**: Queue Phase 2 backlog item **B3 – Evaluate Streaming Data Loader Options** after Q3 closes.

### Task Q4 – Introduce System Metrics Logger
- **Source references**: Phase 2/Q4; Atomic Diff 4.
- **Objective**: Provide psutil-based system metrics logging integrated into training workflows.
- **Preconditions**: Task U4 completion (stable test harness) and psutil availability in environment (document fallback if absent).
- **Actions**:
  1. Implement `system_metrics.py` with configurable sampling interval and output path.
  2. Wire the logger into the training CLI via a `--system-metrics` flag, ensuring the process lifecycle handles start/stop cleanly.
  3. Write tests (unit or integration) verifying log file creation and content schema.
  4. Document usage, retention, and ingestion instructions in README and monitoring docs; update outstanding ledger accordingly.
  5. Execute a demonstration run capturing metrics, storing the JSONL output in `logs/system_metrics/` and referencing it in `.codex/session_logs.db`.
- **Deliverables**: Monitoring module, CLI integration, tests, documentation updates, demo artifacts.
- **Exit criteria**: Metrics logger produces structured JSONL; CLI flag documented; outstanding entries resolved.
- **Logging**: Add entries to `.codex/session_logs.db` summarizing demonstration runs and linking to artifacts.
- **Queue trigger**: Queue Phase 2 backlog item **B4 – Expand Monitoring to GPU Metrics & Retention Policies** post-completion.

### Task Q5 – Patch `tests_docs_links_audit` Script
- **Source references**: Phase 2/Q5; outstanding ledger entry for missing `root` definition in audit script.
- **Objective**: Repair the documentation link audit script so it runs cleanly inside validation pipelines.
- **Preconditions**: Task U5 completion (ensures CLI guard instrumentation) and access to analysis scripts.
- **Actions**:
  1. Open the audit script (`analysis/tests_docs_links_audit.py` or equivalent) and add the missing `root = Path(".")` initialization plus any related fixes.
  2. Run the script against the docs directory, capturing output and storing it under `artifacts/docs_link_audit/`.
  3. Update docs or README sections referencing the audit workflow to note the fix and usage pattern.
  4. Log both the code change and the successful audit run into `.codex/session_logs.db`.
  5. Update outstanding question ledger entries describing the script failure to indicate resolution.
- **Deliverables**: Fixed audit script, run log, documentation updates, outstanding ledger changes.
- **Exit criteria**: Audit script completes without error; documentation references updated; outstanding entry resolved.
- **Logging**: Document fix and run outputs in session DB, including artifact paths for future reference.
- **Queue trigger**: Queue Phase 2 backlog item **B5 – Automate Documentation Link Audit in Gating Sessions** once Q5 wraps.

## 4. Forward Queue Preparation (Phase 2 and Beyond)

To maintain momentum, prepare the following backlog items for immediate triage once Phase 1 completes. These originate from Appendix A of the remediation plan and are paired with the quick-win queue triggers above:

| Pending Backlog ID | Description | Prerequisite Completion | Notes |
| --- | --- | --- | --- |
| B1 | Consolidate training documentation and CLI flags | Q1 | Draft a unified training README section and CLI flag reference. |
| B2 | Introduce checkpoint retention policies | Q2 | Decide on retention count/TTL; integrate into CheckpointManager. |
| B3 | Evaluate streaming data loader options | Q3 | Prototype streaming ingestion with fallbacks to current loader. |
| B4 | Expand monitoring to GPU metrics & retention policies | Q4 | Extend system metrics logger to gather GPU info and rotate logs. |
| B5 | Automate documentation link audit in gating sessions | Q5 | Integrate audit script into `nox` or `pre-commit` workflow. |

When Phase 1 concludes, instantiate a new execution packet (e.g., `docs/suggested_tasks/remediation_phase2_task_queue_2025-09-24.md`) that elaborates each backlog item above with the same level of detail provided here. Ensure the completion digest for Phase 1 explicitly references the new packet so future sessions can navigate the remediation sequence without ambiguity.

## 5. Logging & Reporting Checklist

Before closing Phase 1, validate that the following logging actions have occurred for every task:

- Entries in `.codex/session_logs.db` for task start, key milestones, completion, and queue trigger dispatch.
- Updates to `docs/status_update_outstanding_questions.md` reflecting resolved questions with timestamps.
- Changelog entries (where applicable) in `CHANGELOG.md`, `CHANGELOG_CODEX.md`, and `CHANGELOG_SESSION_LOGGING.md` capturing substantive code/doc shifts.
- Artifact directories populated (`artifacts/test_runs/`, `artifacts/checkpoint_resume/`, etc.) with README files explaining contents and reproduction steps.
- Optional: snapshots of command outputs in NDJSON session logs for cross-session replay.

By following this detailed execution packet, the Codex automation workflow gains a deterministic, fully traceable roadmap for Phase 1 remediations, while simultaneously priming the queue for Phase 2 and subsequent iterations. Maintain meticulous records at each step to keep the repository self-manageable and query-ready for future Codex sessions.
