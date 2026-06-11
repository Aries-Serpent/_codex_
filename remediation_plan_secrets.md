# remediation_plan_secrets.md

- Generated: 2026-06-05T05:16:00Z
- Source artifacts: `security-suite-secrets/detect-secrets-summary.json`, `.secrets.baseline`

## Executive Summary

- Files with findings: **667**
- Detector plugins enabled: **27**
- Observation: the majority of hits are in archived/generated/vendor or evidence files and likely include many false positives.

## Highest-Volume Files

| File | Finding count |
|---|---:|
| `.codex/validation/20250910T151757Z/post_manifest.json` | 1394 |
| `.codex/validation/20250910T151757Z/pre_manifest.json` | 1392 |
| `assets/manifest.json` | 1258 |
| `.codex/validation/post_manifest.json` | 1053 |
| `.codex/validation/pre_manifest.json` | 1052 |
| `.codex/validation/20250910T210555Z/post_manifest.json` | 870 |
| `.codex/validation/20250910T210555Z/pre_manifest.json` | 870 |
| `.codex/validation/20250910T135035Z/post_manifest.json` | 853 |
| `.codex/validation/20250910T135035Z/pre_manifest.json` | 848 |
| `.codex/validation/20250910T113918Z/post_manifest.json` | 844 |
| `.codex/validation/20250910T113918Z/pre_manifest.json` | 842 |
| `.codex/status/_codex_status_update-2025-09-07.md` | 491 |
| `.venv_ci/lib/python3.12/site-packages/ruff-0.15.16.dist-info/sboms/ruff.cyclonedx.json` | 288 |
| `.venv_ci/lib/python3.12/site-packages/hf_xet-1.5.0.dist-info/sboms/hf_xet.cyclonedx.json` | 247 |
| `.venv_ci/lib/python3.12/site-packages/torch/_inductor/autoheuristic/artifacts/_MMRankingH100.py` | 201 |
| `.venv_ci/evidently/legacy/ui/assets/static/js/WidgetsContent-CyU7szGA.js` | 198 |
| `.venv_ci/evidently/nbextension/static/index.js` | 198 |
| `.venv_ci/evidently/ui/service/assets/static/js/snapshot-view-main-DBpHJmd8.js` | 198 |
| `.venv_ci/lib/python3.12/site-packages/evidently/legacy/ui/assets/static/js/WidgetsContent-CyU7szGA.js` | 198 |
| `.venv_ci/lib/python3.12/site-packages/evidently/nbextension/static/index.js` | 198 |
| `.venv_ci/lib/python3.12/site-packages/evidently/ui/service/assets/static/js/snapshot-view-main-DBpHJmd8.js` | 198 |
| `.venv_ci/lib/python3.12/site-packages/torch/_inductor/autoheuristic/artifacts/_MMRankingA100.py` | 197 |
| `.venv_ci/lib/python3.12/site-packages/py_spy-0.4.2.dist-info/sboms/py-spy.cyclonedx.json` | 114 |
| `.venv_ci/lib/python3.12/site-packages/pydantic_core-2.46.4.dist-info/sboms/pydantic-core.cyclonedx.json` | 103 |
| `scripts/pr3248_agent_task_spec.py` | 82 | <!-- pragma: allowlist secret -->
| `scripts/pr3248_mcp_collection_helper.py` | 82 |
| `scripts/populate_pr3248_checks.py` | 81 |
| `scripts/pr3248_comprehensive_collector.py` | 81 |
| `.venv_ci/lib/python3.12/site-packages/ast_serialize-0.5.0.dist-info/sboms/mypy_parser.cyclonedx.json` | 78 |
| `.venv_ci/lib/python3.12/site-packages/sacrebleu/dataset/__init__.py` | 61 |
| `scripts/process_workflow_runs.py` | 56 |
| `.venv_ci/lib/python3.12/site-packages/cryptography-48.0.0.dist-info/sboms/cryptography-rust.cyclonedx.json` | 32 |
| `.venv_ci/lib/python3.12/site-packages/orjson-3.11.9.dist-info/sboms/orjson.cyclonedx.json` | 28 |
| `.venv_ci/lib/python3.12/site-packages/watchfiles-1.2.0.dist-info/sboms/watchfiles_rust_notify.cyclonedx.json` | 27 |
| `.codex/evidence/archive_ops.jsonl` | 24 |
| `.github/agents/scripts/validate_patterns.py` | 21 |
| `.venv_ci/lib/python3.12/site-packages/numpy/random/tests/test_randomstate.py` | 21 |
| `.venv_ci/lib/python3.12/site-packages/torch/_inductor/autoheuristic/artifacts/_MixedMMA100.py` | 21 |
| `.venv_ci/lib/python3.12/site-packages/torch/_inductor/autoheuristic/artifacts/_MixedMMH100.py` | 20 |
| `.venv_ci/lib/python3.12/site-packages/rpds_py-2026.5.1.dist-info/sboms/rpds-py.cyclonedx.json` | 18 |

## Baseline Update Strategy

1. Prioritize triage on non-generated source paths (`src/`, `scripts/`, `.github/workflows/`, config files).
2. For markdown/docs false positives, use inline allowlist pragmas on the exact flagged line: `<!-- pragma: allowlist secret -->`.
3. Keep bulky generated/vendor directories out of ad-hoc scans where policy allows, while preserving CI baseline enforcement.
4. For any true secret, rotate immediately, purge from history if policy-approved, and add detector-specific tests.
5. Regenerate `.secrets.baseline` only after triage to avoid masking regressions.
