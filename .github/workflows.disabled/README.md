# Workflows disabled

All GitHub Actions workflows are stored under `.codex/disabled_workflows/` and are disabled by default. To run CI, an owner must move the desired workflow back here and ensure each job uses `runs-on: self-hosted`.
