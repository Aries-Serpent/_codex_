## [Unreleased] - 2025-09-02
- Format `src/codex_ml/safety/risk_score.py` with Black.
- Correct README typos and complete environment description.
- Pin `peft` dependency to ensure `nox -s tests` passes.
- Applied fallback_patch_4.1-4.8 with safe sanitize→apply fallbacks; preserved intended functionality.
- Normalized line endings/BOM; stripped markdown/email artifacts from patch.
- Conformed to local gates (pre-commit/Black/isort/tests), Codex-only (no GitHub Actions). - Ensure test dependencies (including `langchain`) are installed so `nox -s tests` passes.
- Add runbook for offline wheelhouse usage at `docs/runbooks/offline_wheelhouse.md`.
- Add smoke test proving `nox -s tests` delegates to `coverage`.
- Add `wheelhouse` alias in `Makefile` for bootstrap script.
- Expand `noxfile.py` with `tests_sys` and `tests_ssp` sessions, optional `uv|virtualenv` backend, `PIP_CACHE_DIR` default.
- **feat(gates):** Add black/isort/bandit/detect-secrets/safety hooks; nox `sec_scan`; Make `sys-tests`/`ssp-tests`.
- **feat(deps):** Introduce `tools/uv_lock_refresh.sh` to generate `uv.lock` and compiled requirements.
- **feat(trainer):** Early stopping + scheduler selection wired into `Trainer`.
- **feat(logging):** Rotating file handler with sane defaults.
- **feat(tokenization):** SentencePiece adapter padding/truncation shims + `__all__`.
- **tests(tokenization):** Edge-case test gated by `SPM_TINY_MODEL`.

- Introduced general `TokenizerAdapter` with HuggingFace and whitespace implementations; added basic round-trip tests.
- Added simple dataset loader supporting text/NDJSON/CSV with caching and safety hooks, plus deterministic split utilities.

### Unreleased - 2025-09-07
- Updated README references to current configuration structure.
- Generated gaps report for TODOs and stubs.
- Executed pre-commit and nox quality gate sessions.
- Added telemetry module with Prometheus metrics and metrics server CLI.
- Introduced multilingual tokeniser config and dataset language filtering.
- Integrated optional differential privacy via Opacus.
- Added connector abstraction with local filesystem implementation.
- Introduced Click-based CLI with common subcommands.
