````yaml
**Codex-ready Task Sequence**
1. Preparation
   - Activate the project venv if available; otherwise create one with `python -m venv .venv && source .venv/bin/activate`.
   - Install editable package with extras needed for tooling: `pip install -e .[dev,logging,ml]`.
   - Export `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `PYTHONHASHSEED=0`, and set `CODEX_ENV=session-2025-10-16` for determinism.
   - Run `git status` to ensure a clean working tree and capture baseline diff for rollback notes.

2. Search & Mapping
   - Inspect tokenizer interfaces (`src/codex_ml/interfaces/tokenizer.py`) for abstract methods that still raise `NotImplementedError` and cross-reference registry usage in `src/codex_ml/tokenization/adapter.py`.
   - Review modeling dtype/device resolution in `src/modeling.py` alongside training config flags under `configs/train/default.yaml` to confirm requirements for bf16 capability checks.
   - Examine NDJSON writer (`src/evaluation/writers.py`) and logging utilities (`src/logging_utils.py`) to plan schema versioning and fallback telemetry additions.
   - Map dataset provenance utilities in `src/codex_ml/data/split_utils.py` and reproducibility helpers (`src/codex_ml/utils/repro.py`) for checksum integration.
   - Audit secrets scanner coverage (`tools/scan_secrets.py`, `tests/test_secrets_scanner.py`) to understand extension points for archive parsing.

3. Best-Effort Construction
   - Implement informative runtime guard for `TokenizerProtocol` methods or register default adapter fallback; update compatibility tests accordingly.
   - Add CUDA/bf16 capability detection in modeling, ensuring unit tests exercise error paths without requiring GPU hardware via mocks.
   - Extend NDJSON writer to embed schema metadata and update dependent evaluation tests.
   - Introduce fallback metrics JSONL writer invoked when psutil/pynvml unavailable, documenting path and adding smoke coverage.
   - Emit dataset split checksum manifest after deterministic split generation, wiring to reproducibility helpers.
   - Enhance secrets scanner to inspect ZIP/TAR archives while respecting skip lists and maintain CLI ergonomics.
   - Update documentation/CHANGELOG to reflect new safeguards and telemetry behaviour.

4. Controlled Pruning
   - If adapter guard conflicts with downstream plugin expectations after tests, document rationale and revert to abstract methods while logging warning instead.
   - Should GPU capability detection break CPU-only workflows, gate the check behind `training.reproducibility.bf16_require_capability` flag and record open question.
   - If archive parsing significantly slows scans, restrict to explicitly provided archives and note follow-up performance work.

5. Error Capture
   - For each blocking failure, emit a log entry and append to `error_log.md` using the format:
     > Question from ChatGPT @codex {{timestamp}}:\n     > While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error: [ERROR_MESSAGE] Context: [BRIEF_CONTEXT]. What are the possible causes, and how can this be resolved while preserving intended functionality?
   - Include environment details (python version, extras installed) and relevant stack traces truncated to 20 lines.

6. Finalization
   - Run targeted tests: `pytest tests/test_interfaces_compat.py tests/test_modeling_utils.py tests/test_ndjson_writer.py tests/test_logging_utils.py tests/test_dataset_manifest.py tests/test_secrets_scanner.py`.
   - Execute `nox -s coverage -- tests/test_trainer_extended.py` to ensure trainer regressions are caught.
   - Format code with `ruff check --fix`, `black`, and `isort` on modified files; run `mypy` for type safety.
   - Update documentation snippets (README, LOGGING.md) and changelog entries summarising improvements.
   - Commit with message summarising bf16 guard, telemetry fallback, tokenizer guard, dataset manifest, and scanner enhancements.
   - Prepare PR body referencing High-Signal Findings addressed and attach test outputs.
````

````yaml
Execution Evidence — `scripts/codex_ready_execution.py`
timestamp: "2025-10-16T14:16:27.555370+00:00"
command: "python scripts/codex_ready_execution.py"
readme:
  path: README.md
  placeholders_found:
    - "](#)"
  sanitized_copy: null
change_log: artifacts/codex_ready/change_log.jsonl
search_results_count: 50
search_results:
  - path: codex_task_sequence.py
    line_no: 222
    line: "patterns = [\"TODO\", \"NotImplementedError\"]"
  - path: codex_update_runner.py
    line_no: 130
    line: "stub_markers = (\"TODO\", \"NotImplementedError\", \"pass  # TODO\")"
  - path: codex_script.py
    line_no: 657
    line: "{\"cell_type\":\"markdown\",\"metadata\":{},\"source\":[\"# GPU Training Example (Stub)\\n\",\"TODO: Fill with end-to-end training demo.\"]},"
  - path: .codex/codex_repo_scout.py
    line_no: 238
    line: "r\"\\b(TODO|FIXME|WIP|TBD|XXX|NotImplemented)\\b\", txt, flags=re.IGNORECASE"
  - path: .codex/codex_repo_scout.py
    line_no: 266
    line: "r\"\\b(TODO|FIXME|WIP|TBD|XXX|NOT\\s*IMPLEMENTED|NotImplemented)\\b\", re.IGNORECASE"
  - path: .codex/codex_repo_scout.py
    line_no: 268
    line: "PY_NOTIMPL_PAT = re.compile(r\"raise\\s+NotImplementedError\\b\")"
  - path: .codex/codex_repo_scout.py
    line_no: 315
    line: "if \"NotImplementedError\" in line:"
  - path: .codex/codex_repo_scout.py
    line_no: 335
    line: "if \"exit 1\" in line and (\"TODO\" in line or \"TBD\" in line):"
  - path: .codex/run_repo_scout.py
    line_no: 236
    line: "r\"\\bTODO\\b\","
  - path: .codex/run_repo_scout.py
    line_no: 248
    line: "r\"raise\\s+NotImplementedError\","
  - path: .codex/run_repo_scout.py
    line_no: 253
    line: "r\"throw\\s+new\\s+Error\\(['\\\"]TODO\","
  - path: .codex/run_repo_scout.py
    line_no: 258
    line: "r\"throw\\s+new\\s+Error\\(['\\\"]TODO\","
  - path: .codex/run_repo_scout.py
    line_no: 263
    line: "\"sql\": [r\"--\\s*TODO\", r\"/\\*\\s*TODO\"],"
  - path: .codex/run_repo_scout.py
    line_no: 264
    line: "\"html\": [r\"<!--\\s*TODO\"],"
  - path: tools/apply_interfaces.py
    line_no: 95
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 104
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 109
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 114
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 119
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 135
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 148
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 164
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 169
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 174
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 179
    line: "raise NotImplementedError"
  - path: tools/apply_interfaces.py
    line_no: 329
    line: "path: yourpkg.tokenizers.hf:HFTokenizer   # TODO: replace with actual module:class"
  - path: tools/apply_stack_polish.py
    line_no: 553
    line: "{\"cell_type\":\"markdown\",\"metadata\":{},\"source\":[\"# GPU Training Example (Stub)\\n\",\"TODO: Fill with end-to-end training demo.\"]},"
  - path: tools/offline_repo_auditor.py
    line_no: 8
    line: "- Detects stubs (TODO/FIXME/TBD, NotImplementedError, pass placeholders)"
  - path: tools/offline_repo_auditor.py
    line_no: 75
    line: "re.compile(r\"\\bTODO\\b\"),"
  - path: tools/offline_repo_auditor.py
    line_no: 78
    line: "re.compile(r\"NotImplementedError\"),"
  - path: tools/offline_repo_auditor.py
    line_no: 79
    line: "re.compile(r\"\\braise\\s+NotImplementedError\\b\"),"
  - path: tools/codex_workflow_executor.py
    line_no: 61
    line: "FOLLOW_UP_LINE = re.compile(r\"^.*\\bTODO\\b.*$\", re.I)"
  - path: tools/post_check_validation.py
    line_no: 66
    line: "_DEF_STUB_MARKER = \"raise NotImplementedError\""
  - path: tools/post_check_validation.py
    line_no: 314
    line: "markers = (\"TODO\", \"NotImplemented\", \"pass\")"
  - path: tools/codex_exec.py
    line_no: 90
    line: "out = sh([\"bash\", \"-lc\", 'rg -n \"TODO|NotImplementedError\" || true'], \"Phase 2: scan TODOs\")"
  - path: tools/codex_exec.py
    line_no: 92
    line: "append_changelog(\"- scan: TODO/NotImplemented present; see ripgrep output in local logs\")"
  - path: tools/codex_patch_session_logging.py
    line_no: 182
    line: "{indent2}if isinstance(e, (ImportError, AttributeError, NotImplementedError)):"
  - path: tools/codex_patch_session_logging.py
    line_no: 281
    line: "\"(ImportError/AttributeError/NotImplementedError) and otherwise fail.\""
  - path: tools/apply_ci_precommit.py
    line_no: 14
    line: "- README.md (badges with TODO repo slug)"
  - path: tools/apply_hydra_scaffold.py
    line_no: 153
    line: "# TODO: Implement real step handlers; here we simulate success"
  - path: scripts/repo_audit.py
    line_no: 25
    line: "r\"\\bTODO\\b\","
  - path: scripts/repo_audit.py
    line_no: 27
    line: "r\"NotImplementedError\","
  - path: scripts/repo_audit.py
    line_no: 28
    line: "r\"\\bpass\\s*#\\s*TODO\\b\","
  - path: scripts/codex_ready_execution.py
    line_no: 26
    line: "r\"NotImplementedError\","
  - path: scripts/codex_ready_execution.py
    line_no: 27
    line: "r\"TODO\","
  - path: scripts/codex_ready_execution.py
    line_no: 28
    line: "r\"pass\\s+#\\s*TODO\","
  - path: scripts/run_codex_tasks.py
    line_no: 9
    line: "2. Scanning the repository for TODOs, stubs, and missing implementations."
  - path: scripts/run_codex_tasks.py
    line_no: 60
    line: "\"\"\"Scan repository files for TODOs, NotImplementedError, and pass statements.\"\"\""
  - path: scripts/run_codex_tasks.py
    line_no: 61
    line: "patterns = [r\"TODO\", r\"NotImplementedError\", r\"pass  # TODO\"]"
  - path: scripts/run_codex_tasks.py
    line_no: 100
    line: "\"- Generated gaps report for TODOs and stubs.\\n\""
````

````yaml
Supplied Task Prompts
- Implement the tokenizer protocol guard, bf16 capability detection, and NDJSON schema versioning while maintaining offline-friendly defaults and updating associated tests.
- Extend logging telemetry and dataset provenance tooling to capture fallback metrics and checksum manifests without introducing external service dependencies.
- Harden security scanning by supporting archive formats and ensure documentation/tests reflect the expanded coverage, coordinating updates to changelogs and developer guides.
````
