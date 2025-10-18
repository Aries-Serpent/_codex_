# Evaluation CLI — Dispatcher & Contracts

This document describes the evaluation entrypoints and expected IO behavior.

## Entrypoints
| Command | Target | Notes |
|---------|--------|-------|
| codex-eval | codex_ml.cli.entrypoints:eval_main | Primary evaluation entrypoint |
| python -m codex_ml.cli.evaluate | Module invocation | Equivalent functionality |
| python -m codex_ml.eval.run_eval | Low-level Typer/CLI runner | For direct scripting |

## IO Contracts
- JSON/NDJSON modes: stdout only, no stderr except on errors
- Human text mode: progress and warnings may go to stderr
- Exit codes: 0 on success; non-zero on parameter or runtime errors

## Examples
JSON summary:
```bash
codex-eval --format json --task perplexity --model foo --data bar
```

NDJSON streaming:
```bash
codex-eval --format ndjson --task perplexity --stream --model foo --data bar
```

Help:
```bash
codex-eval --help
python -m codex_ml.eval.run_eval --help
```

## Environment Controls
| Variable | Meaning | Default |
|----------|---------|---------|
| CODEX_EVAL_ENTRY | Override evaluation entry module | autodetect |
| CODEX_LOG_FORMAT | Logging format (text/json/ndjson) | text |

## Testing Guidance
- tests/eval/test_eval_runner_smoke.py should pass unchanged
- Add tests to assert stderr is empty in JSON mode where applicable

*End of doc*
