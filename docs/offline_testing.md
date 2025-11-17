# Offline Testing Matrix

This matrix documents which test targets run in a completely offline developer
environment and which suites require optional dependencies or GPU support.
It builds on the audit in [Optional Dependencies](optional_dependencies.md).

## Tier 1 — Core (Always Runs)

These commands rely only on the standard library and packages installed from
`pip install -e '.[test-core]'`.

* Data loaders
  ```bash
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/codex_ml/data/test_jsonl_loader.py -q
  ```
* Monitoring fallbacks
  ```bash
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/codex_ml/monitoring/test_system_metrics_nvml_missing.py -q
  ```
* Config smoke checks
  ```bash
  nox --noxfile configs/development/noxfile.py -s coverage -- --maxfail=1 --disable-warnings
  ```

## Tier 2 — Optional Extras (Skip When Missing)

Install extras selectively or expect the listed suites to skip.

| Area | Command | Required Extras | Skip Signal |
| --- | --- | --- | --- |
| Tokeniser CLI | `pytest tests/cli/test_tokenizer_cli.py -q` | `.[test,tokenizers]` | `Skipped: could not import 'transformers'` |
| Functional trainer | `pytest tests/training/test_functional_training_main.py -q` | `.[test,ml]` | `Skipped: torch not installed` |
| Experiment tracking | `pytest tests/tracking/test_mlflow_offline_guard.py -q` | `.[test,tracking]` | `Skipped: could not import 'mlflow'` |
| Monitoring dashboards | `pytest tests/monitoring/test_codex_logging_bootstrap.py -q` | `.[test,tracking]` | `Skipped: could not import 'wandb'` |
| Differential privacy | `pytest tests/privacy/test_dp_training.py -q` | `opacus` (manual install) | `Skipped: could not import 'opacus'` |

Running Tier 2 without staging extras is acceptable—the skips confirm that
fallback paths are functioning.

## Tier 3 — Full Suite (Online / GPU)

Requires CUDA-enabled wheels or the GPU Docker image plus all optional
extras. Expect long runtimes.

```bash
pip install -e '.[all]'
pytest -q
```text

Additional notes:

* Use `nox --noxfile configs/development/noxfile.py -s offline_check` to verify that a full
  `nox -s tests` run completes without contacting the network.
* GPU validation commands:
  ```bash
  nox --noxfile configs/development/noxfile.py -s tests -- python -m pytest tests/test_eval_loop_cpu.py -k cuda
  ```
* When running inside Docker, mount cached model artefacts into `/app/models`
  and set `CODEX_OFFLINE=1`.
