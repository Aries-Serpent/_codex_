## [Unreleased] - 2025-09-02
- Format `src/codex_ml/safety/risk_score.py` with Black.
- Correct README typos and complete environment description.
- Pin `peft` dependency to ensure `nox -s tests` passes.
- Applied fallback_patch_4.1-4.8 with safe sanitize→apply fallbacks; preserved intended functionality.
- Normalized line endings/BOM; stripped markdown/email artifacts from patch.
- Conformed to local gates (pre-commit/Black/isort/tests), Codex-only (no GitHub Actions).
