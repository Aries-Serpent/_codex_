# CLI Guide (package-style)

Use the package-style CLI to avoid import coupling and keep the surface stable:

```bash
python -m codex_ml --help
python -m codex_ml.cli --help
python -m codex_ml.cli <subcommand> [args]
```

Examples:
```bash
# Version/help examples (when exposed)
python -m codex_ml
python -m codex_ml.cli --help
```

Notes:
- This layout replaces one-off script entrypoints.
- Prefer subcommands under `codex_ml.cli` for tooling and ops.
