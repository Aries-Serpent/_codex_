# Codex Changelog

## 2025-08-29 – Phase 2 implementations

### WHY
- Add label policy lint helper and tests for self-hosted runner labels.
- Harden git tag decoding and expose SentencePiece model_prefix setter.
- Correct EarlyStopping patience, deterministic data streaming, and minimal risk scoring.
- Provide registry coverage tests.

### RISK
- Low: changes are small utilities with minimal external dependencies.

### ROLLBACK
- Revert this commit to restore previous behavior.
