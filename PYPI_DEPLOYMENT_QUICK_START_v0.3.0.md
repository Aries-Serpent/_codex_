# Quick Start: Deploy codex-ml v0.3.0 to PyPI

**Version:** 0.3.0  
**Status:** Ready for Deployment  
**Date:** 2026-07-20

---

## TL;DR

All validation passed. Deploy as v0.3.0 (NOT 2.0.0 or 3.0.0). Use GitHub web interface to create release.

---

## Why v0.3.0?

- No breaking API changes (infrastructure/security only)
- Follows semver: 0.2.2 → 0.3.0 (minor bump)
- 2.0.0/3.0.0 inappropriate for non-breaking changes

---

## 1-Minute Deploy

### Step 1: Create Release

Visit: https://github.com/Aries-Serpent/_codex_/releases/new

```
Tag: v0.3.0
Target: copilot/fix-pypi-upload-error
Title: v0.3.0 - Security and Infrastructure Release

Description:
Release v0.3.0 with 6 security fixes (CWE-89, 79, 502, 798, 22) and workflow improvements.

Installation: pip install codex-ml==0.3.0
```

### Step 2: Monitor

Watch: https://github.com/Aries-Serpent/_codex_/actions/workflows/pypi-publish.yml

Expected duration: 6-10 minutes

### Step 3: Verify

```bash
curl -s https://pypi.org/pypi/codex-ml/json | python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])"
# Expected: 0.3.0
```

---

## Pre-Deployment Validation ✅

- [x] Security: 6 CWE fixes committed
- [x] Build: Package builds successfully (3.7 MB wheel, 7.7 MB sdist)
- [x] Config: Token auth configured (secrets.PYPI_TOKEN)
- [x] Version: pyproject.toml = 0.3.0
- [x] Docs: CHANGELOG.md updated

---

## Troubleshooting

**Workflow fails at publish:**
- Check secrets.PYPI_TOKEN is set and valid

**Package not visible:**
- Wait 2-5 minutes for PyPI propagation

**Need rollback:**
- Yank release: https://pypi.org/manage/project/codex-ml/release/0.3.0/

---

## Full Documentation

See: `PYPI_DEPLOYMENT_REPORT_v0.3.0.md` for complete details.

---

**Ready to Deploy:** YES
