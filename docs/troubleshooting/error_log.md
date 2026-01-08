# Error Log

This consolidated log merges historical incident notes from `ERROR_LOG.md` and `error_log.md`. Each entry documents a failure
state, its root cause, and the remediation that preserves intended behaviour.

## Missing `pre-commit` binary (2025-09-13)
- **Context**: `pre-commit run --files ...` failed with `command not found: pre-commit`.
- **Cause**: Development extras were not installed, so `pre-commit` was absent from `PATH`.
- **Resolution**: Ensure `pip install -e .[dev]` (or run `scripts/codex_local_gates.sh`) before invoking hooks. The dev extra pins
  `pre-commit==4.0.1`, guaranteeing availability.

## Missing `nox` binary (2025-09-13)
- **Context**: `nox -s tests` exited with `command not found: nox`.
- **Cause**: The development extras that supply `nox==2024.5.1` were not installed.
- **Resolution**: Install `.[dev]` extras or use the local gates script so `nox` is provisioned prior to running automated checks.

## `pytest` coverage argument rejected (2025-09-13)
- **Context**: `pytest --cov=src/codex_ml` raised `unrecognized arguments: --cov=...`.
- **Cause**: The `pytest-cov` plugin was not installed.
- **Resolution**: Include `pytest-cov==7.0.0` via the dev extras; shared helpers now verify availability and emit a guided error if
  the plugin is missing.

## Optional dependency import explosions (2025-09-13)
- **Context**: `pytest -m "not slow"` produced numerous import errors for Hydra, Torch, Transformers, etc.
- **Cause**: Optional libraries were absent and tests imported them unconditionally.
- **Resolution**: Guard optional imports with `pytest.importorskip`. Suites now skip gracefully when dependencies are unavailable.

## Training CLI missing Torch (2025-09-13)
- **Context**: `python -m codex_ml.cli train-model ...` failed with `ModuleNotFoundError: No module named "torch"`.
- **Cause**: The `[torch]` optional extra was not installed.
- **Resolution**: The CLI now probes for Torch, logs a structured error, and instructs users to install `codex_ml[torch]` before
  retrying.

## Missing PyYAML (2025-09-15)
- **Context**: Importing YAML utilities raised `ModuleNotFoundError: No module named "yaml"`.
- **Cause**: PyYAML is optional and was not installed in lean environments.
- **Resolution**: New wrappers in `codex_ml.utils.yaml_support` raise a descriptive `MissingPyYAMLError` and surface remediation
  guidance; install PyYAML when YAML pipelines are required.

## Optional dependency gate failures (2025-09-15)
- **Context**: `pytest -q` failed because optional dependencies (torch, numpy, pydantic, transformers) were missing.
- **Cause**: Collection touched modules that require the extras before applying skips.
- **Resolution**: `tests/config/test_validate_config.py` and related suites now call `pytest.importorskip("pydantic")`, letting the
  fast gate skip cleanly when heavy dependencies are absent.

## Torch stub lacks `torch.utils` (2025-09-23)
- **Context**: `nox -s tests -> coverage` crashed with `AttributeError: module 'torch' has no attribute 'utils'`.
- **Cause**: A stub `torch` package was installed.
- **Resolution**: The local gates script detects stub installs, prints reinstall guidance, and pytest treats the stub as missing so
  Torch-specific suites skip.

## GitHub API 401 unauthenticated probes (2025-10-15/16)
- **Context**: Offline logging exercises attempted to query the GitHub REST API without authentication, returning HTTP 401.
- **Cause**: Requests lacked tokens in a restricted sandbox.
- **Resolution**: Document the limitation and avoid unauthenticated GitHub calls during offline exercises.

## Torch DataLoader import failures (2025-10-15)
- **Context**: Sample scripts raised `cannot import name 'DataLoader' from 'torch.utils.data'`.
- **Cause**: Partial Torch installations omitted the `torch.utils.data` module.
- **Resolution**: Install full Torch wheels or skip DataLoader-dependent paths when running without the full stack.
