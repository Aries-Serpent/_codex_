# Tools Overview

This directory contains small, local-only utilities to standardize message gating and structural checks.

## Commands

### Fence Integrity
```bash
python tools/validate_fences.py
```
Validates balanced fences, prohibits mixed fence types within a block, and reports failures with file:line hints.

### Evaluator
```bash
python tools/codex_evaluator.py --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json
```
Scores messages/summaries against the rubric, returning non-zero on hard fails (e.g., CI cues).

### CLI Wrapper
```bash
python tools/cli/codex_tools.py gate --rules manifests/codex_eval_rules.v3.json --input samples/assistant_message_summary.sample.json
```
Runs both checks (fences → evaluator). See `codex_tools.py --help` for subcommands.

## Pre-commit
Hooks are declared in `.pre-commit-config.yaml`. Install and run:
```bash
pre-commit install
pre-commit run --all-files
```

## Notes
- All tools are **local-only**; no GitHub Actions are created or required.
- For MkDocs navigation, see `docs/ops/mkdocs_nav_snippet.yaml`.
