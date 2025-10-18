# Packaging & Release — codex-ml

This guide covers local, offline-friendly packaging for the Codex ML project.

## Project Identity
| Field | Value |
|------|-------|
| Name | codex-ml |
| Build backend | setuptools.build_meta |
| Layout | src/ |
| Python | >=3.10 |
| Console scripts | codex-train, codex-eval, codex-list-plugins |
| License | MIT (SPDX) with license-files (LICENSE, LICENSES/*) |
| Wheel builder | ./scripts/build_wheel.sh |

## Prerequisites
- Python 3.10+
- pip, build, wheel (pip install build wheel)
- Optional: twine (for metadata checks)

## Build
```bash
./scripts/build_wheel.sh
```
If missing, create it from patches/PS-1h_packaging_wheel_manifest_tests.patch (adds checksums).
Artifacts are written to dist/. SHA256SUMS is generated if sha256sum/shasum is available.

## Verify Metadata
```bash
twine check dist/*
```

## Install Locally
```bash
pip install dist/*.whl
```

## Quick Sanity (pyproject)
```bash
python - <<'PY'
import sys

try:
    import tomllib as _toml  # Python 3.11+
except Exception:
    try:
        import tomli as _toml
    except Exception:  # pragma: no cover - docs snippet
        sys.exit("tomllib/tomli not available; install tomli or use Python 3.11+")

data = _toml.load(open('pyproject.toml','rb'))
assert data['project']['license']=='MIT'
assert data['project']['requires-python'].startswith('>=3.10')
print('ok: license & python floor')
PY
```

## Quick Sanity (scripts)
```bash
python - <<'PY'
import sys
try:
    import tomllib as _toml
except Exception:
    import tomli as _toml  # pip install tomli on Python <3.11
data = _toml.load(open('pyproject.toml','rb'))
scripts = data['project'].get('scripts',{})
assert scripts.get('codex-train') == "codex_ml.cli.entrypoints:train_main"
assert scripts.get('codex-eval') == "codex_ml.cli.entrypoints:eval_main"
assert scripts.get('codex-list-plugins') == "codex_ml.cli.list_plugins:main"
print('ok: console scripts wired')
PY
```

## Troubleshooting (pyproject duplicates)
| Symptom | Cause | Fix |
|---------|-------|-----|
| pre-commit: Black/Ruff TOML parse error | Duplicate [project].dependencies or [project.optional-dependencies] | Run: python tools/apply_pyproject_packaging.py (repairs duplicates non-destructively) |
| pytest TOMLDecodeError | Duplicate keys in pyproject | Use the normalizer above or manually remove the later duplicate blocks |
| Normalizer aborts write | Produced invalid TOML (parser error) | Check stderr hints (duplicate blocks or trailing comma); fix and re-run normalizer |
| Scripts missing after install | Incomplete [project.scripts] section | Re-run normalizer to restore canonical scripts |

## Offline Wheelhouse (Optional)
When preparing an offline environment, pre-build wheels including dependencies (pin as needed) and host them on a local index or folder.

High-level flow:
1) Resolve and pin (constraints.txt)
2) Download wheels for all dependencies into wheelhouse/
3) Install with `pip install --no-index --find-links wheelhouse/ codex-ml`

## Packaging Hygiene
MANIFEST.in ensures:
- license files (LICENSE, LICENSES/*) and README ship
- source (src/) and templates/ are included
- notebooks/*.ipynb, torch stubs, tests/, audit artifacts, and .codex/ are excluded

pyproject.toml ensures:
- name = "codex-ml" (hyphen)
- console scripts map to codex_ml.cli.*
- setuptools package discovery covers src/ packages

## Quick Checklist
- [ ] Build succeeds
- [ ] twine check passes
- [ ] Wheel does not contain torch/ nor tests/stub_packages/*
- [ ] codex-train and codex-eval run `--help` successfully after install
