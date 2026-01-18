# API Docs Build Validation

> Dry-Run, Import Gating, Success Criteria

## Purpose

Provide a deterministic, offline-first procedure to validate the API documentation build before publishing.
Ensure import paths are correct, optional dependencies are gated, and the build completes successfully.

## Preconditions

- Python environment activated
- Repository root on PYTHONPATH or installed in editable mode (`pip install -e .`)
- pdoc3 installed locally (validator will try to import pdoc; otherwise prints "skipped" report)

## Commands (local, offline)

### 1. Dry-run build + validate

JSON report to stdout; artifacts under `artifacts/docs/api`:

```bash
python tools/validate_api_docs.py \
  --package codex.cli \
  --out artifacts/docs/api \
  --allow-optional "wandb" "tensorboard" "torch" \
  --summary
```text

### 2. Env-gated test (skip-safe)

```bash
CODEX_ENABLE_DOCS_TEST=1 pytest -q tests/docs/test_api_docs_build.py
```text

### 3. Nox session (single-runner)

```bash
# Validate core packages
nox -f nox_sessions/docs_validation.py -s docs_validate

# Validate full codex_ml (requires more dependencies)
nox -f nox_sessions/docs_validation.py -s docs_validate_full
```text

## What the validator checks

- **Programmatic pdoc build** completes without exceptions; outputs written to `artifacts/docs/api`
- **Import scan** across the specified package (codex.cli or codex_ml):
  - Hard failures are treated as "errors" unless the module matches an allowlisted optional dependency
  - Optional dependency failures are recorded as "optional_misses" for traceability
- **Generated outputs sanity**:
  - At least one index page exists (e.g., `codex/cli.html`)
  - Count of generated HTML files is >0
  - Summary JSON includes: `ok`/`errors`/`optional_misses`/`file_count`/`out_dir`

## Success criteria (pass conditions)

- ✅ Build completes (`ok: true` in report)
- ✅ No "errors" (hard import failures) reported
- ✅ Optional dependency misses only include allowlisted packages (e.g., wandb, tensorboard, torch)
- ✅ At least one HTML file present in the output directory

## Example JSON output

```json
{
  "build_report": {
    "built": true,
    "file_count": 13,
    "notes": "",
    "out_dir": "/path/to/artifacts/docs/api"
  },
  "env": {
    "cwd": "/path/to/repo",
    "python": "3.12.3 (main, Apr  9 2025, 08:09:14) [GCC 11.4.0]"
  },
  "import_report": {
    "errors": [],
    "optional_misses": [],
    "root_error": "",
    "root_import_ok": true
  },
  "ok": true,
  "out_dir": "/path/to/artifacts/docs/api",
  "package": "codex.cli"
}
```text

## Troubleshooting (common fixes)

### ImportError on optional dependencies

**Symptom**:
```text
"errors": ["codex_ml.peft: ImportError: No module named 'peft'"]
```text
**Fix**:
- Add to `--allow-optional` list: `--allow-optional "wandb" "tensorboard" "peft"`
- Or gate imports in code path via `try/except` + documentation

### Missing PYTHONPATH

**Symptom**:
```text
"root_import_ok": false,
"root_error": "ModuleNotFoundError: No module named 'codex'"
```text
**Fix**:
```bash
# Option 1: Install in editable mode
pip install -e .

# Option 2: Set PYTHONPATH
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
```text

### Stale artifacts

**Symptom**: Old documentation files still present

**Fix**:
```bash
# Remove and rebuild
rm -rf artifacts/docs/api/*
python tools/validate_api_docs.py --package codex.cli --out artifacts/docs/api --summary
```text

### Source layout changes not reflected

**Symptom**: Documentation doesn't match current code structure

**Fix**:
- Ensure pdoc entry package is correct (e.g., `codex.cli` vs `codex_ml`)
- Rebuild with fresh install: `pip install -e . --force-reinstall --no-deps`

## Publishing (local only)

On success, keep artifacts under `artifacts/docs/api` and link from README/docs index.

Optionally archive `artifacts/docs/api` with your release notes as a local deliverable.

## Notes

- The validator **always exits 0** to remain non-blocking
- Rely on `"ok"` and `"errors"` fields for gating decisions
- For strict gating, wrap the script call and assert `"ok": true` and `"errors": []`

## Strict gating example

```bash
#!/bin/bash
set -e

output=$(python tools/validate_api_docs.py --package codex.cli --out artifacts/docs/api)
ok=$(echo "$output" | jq -r '.ok')
errors=$(echo "$output" | jq -r '.import_report.errors | length')

if [ "$ok" != "true" ] || [ "$errors" != "0" ]; then
  echo "API docs validation failed"
  echo "$output" | jq .
  exit 1
fi

echo "✓ API docs validation passed"
```text

## Related Documentation

- [API Documentation Guide](../api/index.md)
- [Troubleshooting Guide](../troubleshooting/API_Docs_Troubleshooting.md)
- [Build Script](https://github.com/Aries-Serpent/_codex_/blob/main/tools/build_api_docs.py)
- [Validator Script](https://github.com/Aries-Serpent/_codex_/blob/main/tools/validate_api_docs.py)
