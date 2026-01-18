# [ARCHIVED] API Docs Build & View Guide

> **⚠️ ARCHIVED FILE**: This file has been merged into `docs/api/index.md`.
> Links in this file are preserved for reference only and may not work.
> For the current version, see [docs/api/index.md](../../api/index.md).

---

**Original content preserved below for reference:**

---

# API Documentation

## Modes

| Flag | Default | Effect |
|------|---------|--------|
| SKIP_OPTIONAL | 1 | Hint code to skip optional ML deps |
| FAIL_ON_MISSING | 0 | Strict import gate for doc build |

## Commands

```bash
# Safe local build
SKIP_OPTIONAL=1 bash scripts/docs_build.sh

# Strict build (use on main merges)
FAIL_ON_MISSING=1 SKIP_OPTIONAL=0 bash scripts/docs_build.sh
```

## Outputs

| Path | Description |
|------|-------------|
| artifacts/docs/ | Generated docs (pdoc if available) |
| artifacts/docs_manifest.sha | SHA256 list for determinism |

---

*Archived: 2026-01-17 - Content merged into docs/api/index.md*
