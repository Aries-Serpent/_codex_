# _codex_: Status Update (2025-09-30) ? Branch: main @ 9883d9bc4485a5aad11bf34907b56a397cb841f5

## Audit Scope & Provenance
- Default branch `main`; selected branch `main` at `9883d9bc4485a5aad11bf34907b56a397cb841f5` (parents `17392b43cff5160cce3aec941864b1a9279b3cab`, `8f25d33ce264fcb975e229c8a0692a37519426e2`) (`.codex/status/provenance.json`).
- GitHub Events API exposed no recent `PushEvent`s; selection defaulted to branch HEAD (recorded in `.codex/errors.ndjson`).
- Commit timestamp `2025-09-30T12:59:33-05:00`; repo `pushed_at` `2025-09-30T17:59:41Z`.
- Source metadata recorded from GitHub REST repo/commit/branch endpoints; report generated `2025-09-30T19:30:18Z`.

## Repo Map
- `src/` ? 34,268 LOC across 223 files, dominated by `codex_ml`, `tokenization`, and `utils` modules (`artifacts/metrics/loc_by_dir.csv`).
- `tests/` ? 24,559 LOC spanning 465 files with deep coverage for tokenization, training, and registry behaviours (`artifacts/metrics/loc_by_dir.csv`).
- `docs/` ? 7,780 LOC (119 files) for guides and pipeline primers; notebooks now validate after GPU example fix (`artifacts/notebook_checks/summary.json`).
- `tools/` ? 22,875 LOC (129 files) housing offline automation such as `tools/pip_audit_wrapper.py:1`.
- Generated assets under `.codex/` and `artifacts/` account for >300k LOC; audit artifacts from this run preserved for reproducibility.
- Tests-to-code LOC ratio: 66.74% (`artifacts/metrics/test_to_code.json`).
- Docstring coverage: 24.82% overall (`artifacts/metrics/docstring_coverage.json`).
- Stub sweep highlights TODO clusters in analysis utilities (`artifacts/metrics/stub_summary.json`).

## Capability Audit Table
| Capability | Status | Existing artefacts | Gaps | Risks | Minimal patch plan | Rollback plan |
| --- | --- | --- | --- | --- | --- | --- |
| Tokenization | Implemented | `src/codex_ml/tokenization/__init__.py:60`; `src/tokenization/cli.py:1`; `tests/tokenization/test_sentencepiece_tokenizer.py:98` | Optional deps (`sentencepiece`, `tokenizers`) skip key tests and CLI encode paths; fallback `SentencePieceAdapter.encode` raises without fast backend | Silent regressions on vocab/config changes when extras absent | Bundle tiny SentencePiece fixture and add offline CLI round-trip test; extend fallback to emit IDs for smoke mode | Revert fixture/test and CLI update |
| ChatGPT Codex Modeling | Implemented | `src/codex_ml/models/registry.py:1`; `src/codex_ml/models/utils/peft.py:10` | No automated check of offline `local_files_only` flows; accelerate warnings unchecked | Offline bootstrap may fail unexpectedly when caches missing | Add pytest covering `gpt2-offline` path with dummy weights and assert helpful error messaging | Remove test and dummy assets |
| Training Engine | Implemented | `src/codex_ml/training/functional_training.py:41`; `tests/training/test_run_functional_training_resume.py:96` | `_prepare` materialises iterables, blocking streaming; grad accumulation untested | Memory pressure on large corpora undermines reproducibility claims | Add generator-aware path leveraging `codex_ml.data.jsonl_stream` and regression test exercising accumulation | Revert streaming branch and test |
| Config Management | Implemented | `src/codex_ml/cli/config.py:15`; `conf/config.yaml:1` | Hydra defaults list undocumented, overrides ordering implicit | Misconfigured experiments drift silently | Publish `docs/config/defaults.md` detailing defaults list and link from README | Drop doc and backlink |
| Evaluation & Metrics | Implemented | `src/codex_ml/metrics/registry.py:39`; `src/codex_ml/training/eval.py:37` | Offline metric asset resolution lacks guardrails; NDJSON logging absent | Evaluation aborts mid-run with opaque `FileNotFoundError` | Add preflight logging + NDJSON summaries under `metrics_out` | Revert preflight and logging |
| Logging & Monitoring | Implemented | `src/codex_ml/utils/experiment_tracking_mlflow.py:39`; `src/codex_ml/monitoring/system_metrics.py:32` | No regression test for MLflow guard; NVML disablement only logged at warning level | Remote tracking URIs may sneak in if guard regresses | Add pytest verifying remote URI fallback and surface NVML disablement in CLI summary | Remove tests/logs if noisy |
| Checkpointing & Resume | Hardened | `src/codex_ml/utils/checkpointing.py:1`; `tests/training/test_run_functional_training_resume.py:104` | Symlink markers on Windows unverified; pickle fallback lacks checksum | Resume may point to stale snapshot on Windows | Add Windows-aware test and checksum validation before pickle restore | Revert checksum check if incompatibilities observed |
| Data Handling | Implemented | `src/codex_ml/data/loader.py:1`; `codex_ml/utils/seeding.py:70` | Safety filters rely on optional `datasets`; cache manifest lacks shard hashes | Mutated shards pass silently in offline mode | Persist SHA256 per shard and fallback to pure-Python filters | Undo hashing if storage overhead unacceptable |
| Security & Safety | Partially Implemented | `tools/pip_audit_wrapper.py:1`; semgrep/bandit configs | Safety CLI requires login; bandit findings pending triage | Vulnerabilities unnoticed in offline runs | Adopt pip-audit SBOM flow and ticket bandit highs | Revert wrapper if SBOM path flaky |
| Internal CI/Test | Partially Implemented | `noxfile.py:13`; `pytest.ini` | `nox` missing from toolchain; coverage run hit 8.22% | Contributors lack turnkey gating | Document bootstrap and add smoke nox session covering CLI fallbacks | Drop session if burdensome |
| Deployment | Partially Implemented | `pyproject.toml:37`; `Dockerfile` | No packaging smoke or Docker dry-run | Release artefacts may drift from repo defaults | Add `nox -s package_smoke` to build/install wheel offline | Remove session if cost outweighs value |
| Documentation & Examples | Implemented | `README.md:261`; `docs/`; notebooks validated (`artifacts/notebook_checks/summary.json`) | Docstring coverage only 24.82% ; docs link audit flags stale `.codex` references | API unfamiliar to new contributors; stale links erode trust | Add `pydocstyle` gate and refresh/retire archived docs | Revert lint if noisy |
| Experiment Tracking | Implemented | `src/codex_ml/utils/experiment_tracking_mlflow.py:39`; `codex_ml/monitoring/mlflow_utils.py` | `_as_flat_params` untested for nested Hydra configs; MLflow URI not captured in provenance | Loss of hyperparam traceability if flattening regresses | Add flattening test and persist effective tracking URI alongside provenance | Remove additions if unnecessary |
| Extensibility | Hardened | `src/codex_ml/registry/base.py:1`; entry points in `pyproject.toml:64` | Import-cycle checks manual; plugin load failures not surfaced early | Broken plugin entry crashes import with opaque error | Automate import graph cycle check (e.g., via `artifacts/metrics/import_graph.json`) and surface load errors | Drop check if false positives high |


## High-Signal Findings
- Hydra-based CLI now short-circuits with actionable guidance when `hydra-core` is missing (`src/codex_ml/cli/main.py:156`).
- `codex_ml.cli.hydra_main` mirrors the fallback so `codex-train --help` succeeds prior to Hydra installation (`src/codex_ml/cli/hydra_main.py:53`).
- GPU training example notebook is valid JSON again; notebook checks report 6/6 load success (`artifacts/notebook_checks/summary.json`).
- System metrics guardrails defer psutil/NVML sampling via environment feature flags with structured warnings (`src/codex_ml/monitoring/system_metrics.py:32`).
- MLflow tracking guard forces local `file:` URIs unless opt-in override (`src/codex_ml/utils/experiment_tracking_mlflow.py:39`).
- Checkpointing utility standardises RNG snapshots and symlink markers for resume flows (`src/codex_ml/utils/checkpointing.py:1`).
- Data loader seeds shuffles and caches manifests with provenance hooks, though shard hashing remains pending (`src/codex_ml/data/loader.py:49`).
- Docstring coverage sits at 24.82% overall (`artifacts/metrics/docstring_coverage.json`).
- Tests-to-code LOC ratio is 66.74% yet coverage run only reached 8.22% (`artifacts/coverage/summary.txt`).
- Bandit emitted findings requiring triage; Safety CLI login blocks offline vulnerability scans (`artifacts/security/bandit.txt`).

## Atomic Diffs
1. Hydra CLI offline fallback
   - Why: Ensure `codex-ml-cli` and `codex-train` provide actionable guidance when Hydra is absent (`src/codex_ml/cli/main.py:156`; `src/codex_ml/cli/hydra_main.py:53`; `README.md:261`; `tests/cli/test_codexml_cli_fallback.py`).
   - Risk: Help guard may mask genuine runtime failures if Hydra is unexpectedly absent; mitigated by retaining ImportError for non-help invocations.
   - Rollback: `git checkout -- src/codex_ml/cli/main.py src/codex_ml/cli/hydra_main.py README.md tests/cli/test_codexml_cli_fallback.py`.
   - Tests: `pytest tests/cli/test_codexml_cli_fallback.py -q`.
2. GPU training notebook sanitised
   - Why: Replace invalid JSON that blocked nbformat validation (`notebooks/gpu_training_example.ipynb`; `artifacts/notebook_checks/summary.json`).
   - Risk: Removes prior placeholder metadata (the notebook was stub-only).
   - Rollback: `git checkout -- notebooks/gpu_training_example.ipynb`.
   - Tests: Notebook validation via updated notebook_checks script.
3. CLI documentation updated for Hydra dependency
   - Why: Surface explicit installation instructions for `hydra-core` before invoking training CLI (`README.md:272`).
   - Risk: None beyond minor doc churn.
   - Rollback: `git checkout -- README.md`.

## Local Tests & Gates
- `pytest tests/cli/test_codexml_cli_fallback.py -q` (pass) ? exercises CLI fallbacks (ML Test Score: regression/infra).
- `pytest tests/cli/test_codexml_cli_fallback.py --cov=src --cov-report=xml:artifacts/coverage/coverage.xml --cov-report=html:artifacts/coverage/html` (fail: coverage 8.22% < 80) ? highlights need for broader suite (ML Test Score: regression/infra).
- `bandit -r src -f txt -o artifacts/security/bandit.txt` (exit 1 with findings) ? static security scan (ML Test Score: security).
- `detect-secrets scan --all-files` (output in `artifacts/security/detect-secrets.txt`) ? secret detection (ML Test Score: security).
- `safety scan -r requirements.txt` (blocked by login) ? document offline limitation (ML Test Score: security).


## Reproducibility Checklist
- **Seeds**: `set_reproducible` seeds Python/NumPy/Torch and toggles deterministic flags plus CuBLAS env vars (`src/codex_ml/utils/seeding.py:65`).
- **Determinism**: PyTorch deterministic algorithms invoked when available (`src/codex_ml/utils/seeding.py:80`).
- **Environment capture**: Training exports provenance snapshots alongside checkpoints (`src/codex_ml/training/functional_training.py:112`; `src/codex_ml/utils/checkpointing.py:38`). Env capture stored under `artifacts/env/`.
- **Versioning**: Provenance pins branch, SHA, and parents (`.codex/status/provenance.json`).
- **Data manifests**: Loader manifests capture metadata for reproducibility (`src/codex_ml/data/loader.py:49`).
- **Checkpoints**: Standard layout with RNG snapshots and markers (`src/codex_ml/utils/checkpointing.py:1`).
- **Experiment tracking**: MLflow guard keeps tracking local unless explicitly overridden (`src/codex_ml/utils/experiment_tracking_mlflow.py:39`).


## Deferred Items
- Triage bandit findings in `artifacts/security/bandit.txt` and decide remediation backlog.
- Adopt an offline-friendly vulnerability scan to replace interactive Safety CLI.
- Provide lightweight `nox` smoke session so coverage gating surpasses 80% without heavy deps.
- Automate package/Docker smoke testing to detect drift before release.
- Resolve stale links called out in docs link audit under `.codex/` archives.


## Codex-Ready Task Sequence
1. Address security tooling gaps (bandit triage, Safety alternative).
2. Introduce streaming-aware path in `functional_training` with regression coverage.
3. Document Hydra defaults and bundle SentencePiece fixture for offline tokenization tests.
4. Add MLflow guard test + provenance logging for tracking URI.
5. Stand up minimal nox session or bootstrap docs to restore coverage gating.


## Error Capture Blocks
- `.codex/errors.ndjson` captures missing PushEvents, bandit exit code 1, Safety login prompt, coverage fail-under breach, missing `nox`, pip-freeze warning, and initial detect-secrets timeout.


## Diff-Addendum S0?S1
- Not provided (no base `S0` specified).

## References
[1]: https://hydra.cc/docs/advanced/defaults_list/
[2]: https://pytorch.org/docs/stable/generated/torch.use_deterministic_algorithms.html
[3]: https://pytorch.org/docs/stable/notes/randomness.html
[4]: https://mlflow.org/docs/latest/tracking.html
[5]: https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.set_tracking_uri
[6]: https://github.com/google/sentencepiece
[7]: https://psutil.readthedocs.io/
[8]: https://docs.nvidia.com/deploy/nvml-api/
[9]: https://nox.thea.codes/
[10]: https://bandit.readthedocs.io/
[11]: https://github.com/Yelp/detect-secrets
[12]: https://docs.pyup.io/docs/safety/
[13]: https://pytest-cov.readthedocs.io/
[14]: http://www.pydocstyle.org/

