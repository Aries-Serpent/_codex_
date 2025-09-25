# Doc: Offline Audit Validation
> Generated: 2025-09-22 22:15:51 | Author: mbaetiong  
> Updated: Offline Audit Validation alignment (offline-only, deterministic, local gates)

Overview
This document explains how to run and validate the offline repository audit locally, what artifacts are produced, and how to interpret outcomes.

Quick start
- Ensure Python 3.9+ and bash are available.
- From the repository root:

```bash
export PYTHONHASHSEED=0
scripts/codex_local_audit.sh
```
Expected artifacts

| Artifact | Path | Description |
|---|---|---|
| JSON report | reports/audit.json | Machine-readable inventory + README summary + hashes |
| Markdown report | reports/audit.md | Human-friendly audit summary and inventory sample |
| Prompt copy | reports/prompt_copy.md | Exact prompt used to drive the audit |
| Errors (optional) | .codex/errors.ndjson | NDJSON with structured failures and context |

Alternate: Python CLI (packaged)
Once installed in editable or wheel form, the audit pipeline is available via a console script.

```bash
codex-audit --root . --out reports/audit.json
```
Key flags and defaults

| Flag | Default | Purpose |
|---|---|---|
| --root | . | Repository path to scan |
| --external-search | disabled | Keep runs fully offline unless explicitly enabled |
| --external-search-endpoint | none | Override endpoint when external search is opted-in |
| --external-search-timeout | none | HTTP timeout override when external search is opted-in |
| --out | reports/audit.json | JSON output path for the structured auditor |

Troubleshooting
- If AUDIT_PROMPT.md is missing, the vendor builder will exit early; a default is now provided at repo root.
- Pre-commit hooks failing or hanging: the script cleans and retries automatically; consult `.codex/errors.ndjson` for details.
- Coverage gate: `pytest --cov-fail-under=70` enforces a baseline; on failure, a minimal fallback test run is attempted.
- Fence validation: if present, run `python3 tools/validate_fences.py --strict-inner` to ensure code block integrity in markdown artifacts.
- CI guard: do **not** enable GitHub Actions; all checks run locally within the Codex environment.
