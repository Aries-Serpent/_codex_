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
| `scripts/pr3248_agent_task_spec.py` <!-- pragma: allowlist secret --> | 82 |
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

## Implementation Status — 2026-06-12

- **Status:** Scoped source-path triage executed for the requested high-signal files.
- **Touched files:** `scripts/pr3248_agent_task_spec.py`, `scripts/pr3248_mcp_collection_helper.py`, `scripts/populate_pr3248_checks.py`, `scripts/pr3248_comprehensive_collector.py`, `scripts/process_workflow_runs.py`, `.github/agents/scripts/validate_patterns.py`.
- **Outcome:** no true secrets were found in the scoped source files; only verified false positives were retained, and each was handled with exact-line allowlist pragmas.
- **Targeted validation:** the scoped secret-detection lane reported a clean targeted secret scan after the allowlist adjustments.
- **Baseline handling:** no `.secrets.baseline` content change was required for this scoped source-path remediation because the targeted files were made clean without introducing new baseline entries.

## Implementation Status — 2026-06-13 (extended source triage)

- **Status:** Extended source-path triage completed for all remaining non-generated, non-vendor, non-previously-reviewed baseline entries.
- **Findings triaged:** 37 baseline entries across 17 source/config/workflow files, all confirmed as **false positives**. No true secrets found.
- **Files receiving exact-line allowlist pragmas (Python):**
  - `tests/security/test_providers.py` — 15 lines: test-fixture secret values (fake AWS keys, GitHub tokens, env var assignments used in provider unit tests)
  - `tests/ci/test_post_rescue_comment.py` — 4 lines: hardcoded Git SHA test fixtures flagged as Hex High Entropy
  - `tests/api/test_auth_mfa_expiry.py` — 1 line: `"password": "Str0ngPass!"` in auth test fixture
  - `tests/auth/test_mfa_provider.py` — 1 line: `secret="JBSWY3DPEHPK3PXP"` (standard IETF RFC 6238 TOTP test seed)
  - `tests/auth/test_token_manager.py` — 1 line: `secret = "test_secret_key_123"` test fixture
  - `tests/branch_coverage/test_branch_coverage_config.py` — 1 line: env-var dict literal used in test
  - `tests/agents/test_msp_client_phase9_1.py` — 1 line: `api_key="test"` in unit test
  - `coverage_tests/test_security_providers_unittest.py` — 1 line: mock `get_secret_value` return in unittest
  - `tests/unit/test_alerting.py` — 1 line: SMTP port assertion (keyword over-match)
  - `tests/unit/utils/test_reproducibility_hardening.py` — 1 line: `mock_git_commit` fixture value
  - `tests/unit/utils/test_safe_pickle.py` — 1 line: `b"env_secret"` assertion string
  - `tests/services/test_api_main_phase_e.py` — 1 line: `monkeypatch.setenv("DISABLE_SECRET_FILTER", ...)` test setup
  - `tests/test_fast_forward_safe_files.py` — 1 line: `"abc123def456"` SHA fixture (peer of the already-pragmaed line 118)
  - `scripts/space_traversal/viz_html.py` — 1 line: `integrity="sha384-..."` SRI hash attribute in HTML template
  - `tools/codex_apply_modeling_monitoring_api.py` — 1 line: `API_KEY_ENV = "CODEX_API_KEY"` env-var name constant
- **Files receiving exact-line allowlist pragmas (YAML workflow):**
  - `.github/workflows/codeql-alert-fetcher.yml` — 1 line: `CODEX_MASTER_KEY: ${{ secrets.CODEX_MASTER_KEY || secrets.CODEX_BACKUP_KEY }}` (GitHub Actions secret reference, not a credential value)
  - `.github/workflows/security-scanning-suite.yml` — 1 line: `id: detect-secrets` step identifier (keyword over-match)
- **Files covered by baseline only (JSON — no inline comment support):**
  - `.codex/webhook_config.json` — lines 7, 85: `"secret_env"` key and `"WEBHOOK_SECRET"` key are env-var name references, not values
  - `.codex/agent_context.json` — line 14: `CODEX_CI_LAST_GREEN_SHA` is a CI tracking Git SHA, not a credential
  - `CODEX_MANIFEST.json` — line 2248: SHA256 integrity hash flagged as Hex High Entropy (also has an unresolved merge conflict marker; out of scope for secret triage)
  - `.codex/aftermath/pda_iterations.jsonl` — lines 3, 4, 57, 231: JSONL with Git SHAs / iteration identifiers as hex entropy
- **Baseline handling:** no `.secrets.baseline` regeneration performed; existing baseline entries for covered findings remain as tracked known issues until a full baseline regeneration pass is executed after triage is complete.
