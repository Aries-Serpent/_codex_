# Tools and Utilities

The project bundles a few command line helpers for working with conversation
logs and development workflows.

## Logging tools

- `python -m codex.logging.session_logger` – record structured session events.
- `python -m codex.logging.viewer` – inspect stored logs.
- `python -m codex.logging.query_logs` – search transcripts.

## Development utilities

- `pre-commit run --all-files` – run formatting, linting, and security checks.
- `pytest` – execute the unit test suite.
- `codex_script.py <file>` – example script demonstrating patch guards and
  post-run validation output under `.codex/results.md`.

See additional documentation in this directory for more advanced workflows.
