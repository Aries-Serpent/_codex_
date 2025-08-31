# Deferred Items

- CLI entry point using Hydra: deferred due to time constraints.
- Metrics callback NDJSON support: deferred, requires broader monitoring overhaul.
- Nox coverage gate (<80%): not implemented to avoid disrupting existing tooling.
- Automated tests for new features: deferred; existing suite unchanged.
- `pip-compile --generate-hashes` lockfile refresh: skipped to avoid large dependency download.
- Gradient accumulation exposure in config objects: requires refactor of configuration system.
