# Packaging & Release — codex-ml

This guide covers local, offline-friendly packaging for the Codex ML project.

## Project Identity
| Field | Value |
|------|-------|
| Name | codex-ml |
| Build backend | setuptools.build_meta |
| Layout | src/ + selected top-level packages (training/, tokenization/, codex_utils/, interfaces/, tools/, codex_addons/, codex_digest/, hhg_logistics/) |
| Python | >=3.10 |
| Console scripts | codex-train, codex-eval, codex-list-plugins |
| License | MIT (SPDX) with license-files (LICENSE, LICENSES/*) |

## Prerequisites
- Python 3.10+
- pip, build, wheel (pip install build wheel)
- Optional: twine (for metadata checks)

## Build
```bash
./scripts/build_wheel.sh
```
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
import tomllib,sys
data = tomllib.load(open('pyproject.toml','rb'))
assert data['project']['license']=='MIT'
assert data['project']['requires-python'].startswith('>=3.10')
print('ok: license & python floor')
PY
```

## Offline Wheelhouse (Optional)
When preparing an offline environment, pre-build wheels including dependencies (pin as needed) and host them on a local index or folder.

High-level flow:
1) Resolve and pin (constraints.txt)
2) Download wheels for all dependencies into wheelhouse/
3) Install with `pip install --no-index --find-links wheelhouse/ codex-ml`

## Packaging Hygiene
MANIFEST.in ensures:
- test stubs (tests/stub_packages) are excluded
- any top-level torch/ stubs are excluded
- local audit artifacts (audit_artifacts/, reports/, audit_run_manifest.json) are excluded

pyproject.toml ensures:
- name = "codex-ml" (hyphen)
- console scripts map to codex_ml.cli.*
- setuptools package discovery covers both src/ and top-level packages

## Quick Checklist
- [ ] Build succeeds
- [ ] twine check passes
- [ ] Wheel does not contain torch/ nor tests/stub_packages/*
- [ ] codex-train and codex-eval run `--help` successfully after install

## Troubleshooting
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| ImportError codex_ml | src/ layout misconfigured | Ensure [tool.setuptools] package-dir and find include codex_ml* |
| Console script missing | scripts not set in pyproject | Run tools/apply_pyproject_packaging.py |
| Wheel contains test stubs | MANIFEST missing rules | Verify MANIFEST.in; rebuild |

## Maintenance
Run the normalizer when editing pyproject:
```bash
python tools/apply_pyproject_packaging.py
```
