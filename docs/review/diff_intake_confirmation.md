# [Review]: Diff Intake Confirmation for 0A_base_  
> Generated: 2025-10-09 20:32:46 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose
- Confirm readiness of the listed scripts/docs to land on branch 0A_base_.
- Capture dependencies, offline-safety, and immediate post-merge validation focus.

Scope Reviewed (All items OK to add)
| Path | Type | Status | Notes / Dependencies |
|------|------|--------|----------------------|
| src/codex_ml/utils/atomic_io.py | code | Ready | Pure stdlib; atomic tmp+fsync+os.replace |
| src/codex_ml/utils/checkpoint_core.py | code | Ready | Optional: torch, numpy; falls back to pickle |
| tests/training/test_checkpoint_integrity.py | test | Ready | CPU-only; no network |
| src/codex_utils/tracking/guards.py | code | Ready | Pure stdlib; env-based guards |
| tests/tracking/test_tracking_guards.py | test | Ready | CPU-only; no network |
| src/data/manifest.py | code | Ready | Pure stdlib; sha256; atomic write |
| tests/data/test_shard_integrity.py | test | Ready | CPU-only; no network |
| src/tokenization/api.py | code | Ready | Deprecation shim; optional downstream imports |
| tests/tokenization/test_deprecation.py | test | Ready | Skips gracefully if adapters missing |
| docs/how-to/offline_tracking.md | doc | Ready | Offline guard usage |
| docs/how-to/dataset_manifest.md | doc | Ready | Manifest schema/usage |
| docs/how-to/checkpoint_metadata.md | doc | Ready | Metadata, index, retention |
| docs/ops/repo_rulesets_vs_protection.md | doc | Ready | Primer; concept only |
| docs/index.md | doc | Ready | Includes new links |
| src/tools/codeowners_validate.py | tool | Ready | Offline CODEOWNERS validator |
| tests/ops/test_codeowners_validation.py | test | Ready | CPU-only |
| docs/how-to/codeowners_validation.md | doc | Ready | Validator how-to |
| docs/specs/FORMAL_ARTIFACTS.md | doc | Ready | Specs (PEG/JSON/Regex/SMT/Typing) |
| docs/how-to/admin_bootstrap.md | doc | Ready | Online opt-in runbook |
| docs/how-to/tokenizer_migration.md | doc | Ready | Deprecation shim guide |
| configs/examples/online.env.example | config | Ready | Example env |
| tests/training/test_checkpoint_rng_restore.py | test | Ready | RNG restore (python random) |
| src/codex_ml/utils/__init__.py | code | Ready | Exposes utils |
| src/codex_utils/tracking/__init__.py | code | Ready | Exposes guards |
| src/data/__init__.py | code | Ready | Exposes manifest |
| docs/how-to/repodeterminism_smoke.md | doc | Ready | Fast smoke how-to |
| src/integrations/github_app_auth.py | code | Ready | Optional: pyjwt; network OFF by default |
| scripts/ops/bootstrap_self_hosted_runner.py | script | Ready | Online opt-in; uses App auth |
| docs/how-to/bootstrap_runner.md | doc | Ready | Runner setup how-to |
| schemas/metrics-ndjson-v0.3.json | schema | Ready | JSON Schema 2020-12 |
| tests/specs/test_metrics_schema.py | test | Ready | Optional: jsonschema; skips otherwise |
| tests/specs/test_cli_normalization.py | test | Ready | argparse-only |
| tests/specs/test_regex_props.py | test | Ready | ReDoS-safe regex perf caps |
| tools/smt/policy_constraints.smt2 | spec | Ready | SMT (no runtime) |
| tests/specs/test_smt_policy.py | test | Ready | Optional: z3; skips otherwise |
| templates/github_repo_baseline/CODEOWNERS | template | Ready | Hygiene baseline |
| templates/github_repo_baseline/PULL_REQUEST_TEMPLATE.md | template | Ready | Hygiene baseline |
| templates/github_repo_baseline/ISSUE_TEMPLATE/bug_report.md | template | Ready | Hygiene baseline |
| templates/github_repo_baseline/ISSUE_TEMPLATE/feature_request.md | template | Ready | Hygiene baseline |
| templates/github_repo_baseline/ISSUE_TEMPLATE/config.yml | template | Ready | Hygiene baseline |

Offline-first Compliance
- All code/tests run offline by default.
- Online-only scripts (bootstrap_self_hosted_runner.py) are opt-in via CODEX_NET_MODE=online_allowlist.

Optional Dev Dependencies (auto-skip in tests)
- jsonschema (for tests/specs/test_metrics_schema.py)
- z3-solver (for tests/specs/test_smt_policy.py)
- pyjwt, requests (for src/integrations/github_app_auth.py; only needed if you run bootstrap script)
- torch, numpy (optional performance/state integrations; checkpoint core falls back to pickle)

Post-Merge Smoke (see prompt file in /docs/prompts)
- Run the fast pytest subset, then broaden incrementally.
- Verify docs links via docs/index.md local reads (no network required).
- Validate CODEOWNERS file via validator tool.

Risks & Mitigations
- Filesystem semantics: fsync/replace differences across platforms (low risk; tests avoid strict FS timing).
- Deprecation shim: warns by design; tests assert presence of DeprecationWarning, skip adapters if absent.
- Admin bootstrap: online-only, gated; docs clearly separate runbook.

Conclusion
- All listed artifacts are clear to add to 0A_base_. Use the tailored prompt to validate integration end-to-end post-merge.

*End of Confirmation*