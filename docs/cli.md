# CLI Guide (package-style)

Use the package-style CLI to avoid import coupling and keep the surface stable:

```bash
# Package-style (module-per-command)
python -m codex_ml.cli.manifest --help
python -m codex_ml.cli.detectors --help
```

Common examples:

```bash
# Show versions / quick sanity
python -m codex_ml.cli --version

# NDJSON summary of a metrics file
python -m codex_ml.cli.ndjson_summary --input artifacts/metrics.ndjson

# Manifest: compute digest and update README badge
python -m codex_ml.cli.manifest hash --path path/to/manifest.json --update-readme README.md
```

Notes:
- This layout replaces any single-file `cli.py` entry surface.
- Scripts in `tools/` should call into the package CLI where possible.

# Detectors
```bash
python -m codex_ml.cli.detectors run --help
```
