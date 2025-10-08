# CLI Guide (package-style)

Use the package-style CLI to avoid import coupling and keep the surface stable:

```bash
python -m codex_ml.cli --help
python -m codex_ml.cli <subcommand> [args]
```

Common examples:

```bash
# Show versions / quick sanity
python -m codex_ml.cli --version

# NDJSON summary of a metrics file
python -m codex_ml.cli ndjson-summary --input artifacts/metrics.ndjson

# (P3) Manifest: compute digest and update README badge (after P3 lands)
python -m codex_ml.cli manifest hash --path path/to/manifest.json --update-readme README.md
```

Notes:
- This layout replaces any single-file `cli.py` entry surface.
- Scripts in `tools/` should call into the package CLI where possible.
