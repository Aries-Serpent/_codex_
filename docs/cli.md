# CLI Guide (package-style)

Use the package-style CLI to avoid import coupling and keep the surface stable:

```bash
python -m codex_ml --help
python -m codex_ml <subcommand> [args]
```

Examples:

```bash
python -m codex_ml ndjson-summary --input artifacts/metrics.ndjson
python -m codex_ml ndjson-summary --help
```

Notes:
- This layout replaces one-off script entrypoints.
- Prefer subcommands exposed by `codex_ml` for tooling and ops.

Output includes total rows and compact aggregates:

    {"rows": 1234, "metrics": {"loss": {"count": 1234, "min": 0.37, "max": 2.11}}}
