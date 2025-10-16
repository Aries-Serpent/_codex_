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
Supplied Task Prompts
- Implement the tokenizer protocol guard, bf16 capability detection, and NDJSON schema versioning while maintaining offline-friendly defaults and updating associated tests.
- Extend logging telemetry and dataset provenance tooling to capture fallback metrics and checksum manifests without introducing external service dependencies.
- Harden security scanning by supporting archive formats and ensure documentation/tests reflect the expanded coverage, coordinating updates to changelogs and developer guides.
````
