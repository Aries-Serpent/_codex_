# Security Scan Suppressions Registry

## Purpose

This document tracks all security scan suppressions with rationale for audit purposes.
Suppressions are required when:
1. A security finding is a **false positive** that cannot be resolved
2. A pattern is **intentionally needed** for functionality (e.g., ML model loading)
3. The risk is **mitigated** through other means documented here

## Bandit Suppressions

### Global Skips (`.bandit.yaml`)

| Test ID | Rule Name | Rationale |
|---------|-----------|-----------|
| B101 | `assert_used` | Assertions OK in tests; test directories excluded from scanning |
| B404 | `import_subprocess` | Subprocess imports required for git/build tooling |
| B603 | `subprocess_without_shell_equals_true` | We use explicit command lists with `shell=False` |

### In-Code Suppressions

#### Cryptographic Hash Functions (B324)

| File | Line | Rationale | Reviewer | Date |
|------|------|-----------|----------|------|
| `src/codex/metrics/duplication.py` | 220 | MD5 used for deduplication hashing, not security purposes | Copilot | 2024-12-10 |
| `src/codex_bridge/github_client.py` | 28 | SHA1 used for cache key generation, not security purposes | Copilot | 2024-12-10 |
| `src/codex_ml/data/splits.py` | 26 | SHA1 used for deterministic data splitting, not security | Copilot | 2024-12-10 |

#### Subprocess Security (B602)

| File | Line | Rationale | Reviewer | Date |
|------|------|-----------|----------|------|
| `src/codex/utils/context_discovery.py` | 32 | **FIXED**: Converted to `shell=False` with `shlex.split()` | Copilot | 2024-12-10 |

#### Pickle/Deserialization (B301, B403)

| File | Line | Issue | Rationale | Reviewer | Date |
|------|------|-------|-----------|----------|------|
| `src/codex_ml/utils/checkpoint_manager.py` | import | B403 | Required for ML checkpoint serialization | Copilot | 2024-12-10 |
| `src/codex_ml/utils/checkpoint_manager.py` | 59, 64 | B301 | Checkpoint loading from trusted local sources | Copilot | 2024-12-10 |
| `src/codex_ml/utils/checkpoint_core.py` | import | B403 | Required for ML checkpoint serialization | Copilot | 2024-12-10 |
| `src/codex_ml/utils/checkpoint_core.py` | 364 | B301 | Checkpoint loading from trusted local sources | Copilot | 2024-12-10 |
| `src/codex_ml/utils/checkpointing.py` | import | B403 | Required for ML checkpoint serialization | Copilot | 2024-12-10 |
| `src/codex_ml/utils/checkpointing.py` | 360, 1233 | B301 | Checkpoint loading from trusted local sources | Copilot | 2024-12-10 |
| `src/codex_ml/data/loader.py` | import | B403 | Required for dataset caching | Copilot | 2024-12-10 |
| `src/codex_ml/data/loader.py` | 367 | B301 | Loading cached dataset from local trusted cache | Copilot | 2024-12-10 |
| `src/utils/checkpoint.py` | import | B403 | Legacy checkpoint support (deprecated) | Copilot | 2024-12-10 |
| `src/utils/checkpoint.py` | 367 | B301 | Legacy checkpoint loading from trusted sources | Copilot | 2024-12-10 |

#### PyTorch Load (B614)

| File | Line | Rationale | Reviewer | Date |
|------|------|-----------|----------|------|
| `src/codex_ml/checkpointing/checkpoint_core.py` | 92, 96 | torch.load required for ML checkpoint loading | Copilot | 2024-12-10 |
| `src/codex_ml/utils/checkpoint_manager.py` | 55 | torch.load required for ML checkpoint loading | Copilot | 2024-12-10 |
| `src/codex_ml/utils/checkpointing.py` | 351, 1156 | torch.load required for ML checkpoint loading | Copilot | 2024-12-10 |
| `src/codex_ml/training/fsdp_wrapper.py` | 460, 488 | torch.load required for distributed checkpoint loading | Copilot | 2024-12-10 |

#### HuggingFace Hub Loading (B615)

| File | Line | Rationale | Reviewer | Date |
|------|------|-----------|----------|------|
| `cli/train_codex.py` | 87 | Model loading with `local_files_only` control | Copilot | 2024-12-10 |
| `src/codex/api/app.py` | 82 | Model loading with `local_files_only` control | Copilot | 2024-12-10 |
| `src/hhg_logistics/model/peft_utils.py` | 63, 74, 80, 89 | Model loading with explicit `trust_remote_code` parameter | Copilot | 2024-12-10 |
| `src/modeling.py` | 242, 342 | Model loading with explicit `trust_remote_code` parameter | Copilot | 2024-12-10 |
| `src/tokenizer/fast_tokenizer.py` | 112 | Tokenizer loading with `trust_remote_code=False` | Copilot | 2024-12-10 |
| `src/codex_ml/serving/model_loader.py` | 288 | Config loading with explicit `trust_remote_code` parameter | Copilot | 2024-12-10 |
| `src/codex_ml/eval/eval_runner.py` | 93 | **False positive**: Local `load_dataset`, not HuggingFace | Copilot | 2024-12-10 |

#### SQL Injection (B608)

All SQL injection findings are **false positives** because:
1. Table and column names come from internal schema introspection or validated constants
2. User-supplied values are always parameterized using `?` placeholders

| File | Line | Rationale | Reviewer | Date |
|------|------|-----------|----------|------|
| `src/codex/logging/export.py` | 78 | Table/column from schema introspection, input parameterized | Copilot | 2024-12-10 |
| `src/codex/logging/query_logs.py` | 84, 160 | Table name is hardcoded, input parameterized | Copilot | 2024-12-10 |
| `src/codex/logging/session_query.py` | 147-165 | Table/column from schema introspection, input parameterized | Copilot | 2024-12-10 |
| `src/codex_ml/cli/metrics_cli.py` | 158-169, 203-217 | Table name validated by `_validate_table()` | Copilot | 2024-12-10 |
| `src/codex_ml/metrics/api.py` | 343, 348 | Table/column from validated NDJSON schema | Copilot | 2024-12-10 |

#### Exec Usage (B102)

| File | Line | Rationale | Reviewer | Date |
|------|------|-----------|----------|------|
| `src/codex_ml/plugins/registry.py` | 85 | Exec for `.pth` bootstrap, input from trusted local files | Copilot | 2024-12-10 |

#### Binding to All Interfaces (B104)

| File | Line | Rationale | Reviewer | Date |
|------|------|-----------|----------|------|
| `src/codex_ml/telemetry/server.py` | 17 | Telemetry server for container/cluster deployments needs external access | Copilot | 2024-12-10 |

## pip-audit Vulnerabilities

**Status**: No vulnerable packages detected in latest scan (2024-12-10).

All dependencies are up-to-date with no known CVEs.

## detect-secrets Baseline

The `.secrets.baseline` file tracks known false positives. All entries are:
- Git commit hashes in changelog and status files
- SHA256 checksums in artifact manifests
- Test fixture data

---

**Last Updated**: 2024-12-10
**Next Review**: 2025-01-10

## Review Process

1. Security suppressions must be reviewed during PR review
2. New suppressions require documented rationale
3. This registry is updated when suppressions are added/removed
4. Quarterly review to ensure suppressions remain valid
