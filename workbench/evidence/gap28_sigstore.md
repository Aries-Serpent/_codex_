# Gap 28 — Sigstore Verification for Critical Dependencies

**Status**: ✅ Implemented
**Date**: 2025-01-31
**Branch**: `copilot/explore-codebase-and-create-plan`

---

## Overview

Implements Sigstore / cosign-compatible signature verification for critical PyPI
packages.  The solution is forward-compatible: it works today (structured warning
mode when no Sigstore bundle exists on PyPI) and will automatically start
performing real cryptographic verification once packages publish attestations.

---

## Artifacts Created

| Path | Description |
|------|-------------|
| `scripts/security/sigstore_verify.py` | Verification script (executable) |
| `.github/workflows/sigstore-verify.yml` | CI workflow |
| `tests/security/test_sigstore_verify.py` | Unit tests (21 tests) |

---

## Script: `scripts/security/sigstore_verify.py`

### Features

- **Dual-mode operation**:
  - *SDK present*: Queries PyPI JSON API for `provenance` field; if present,
    downloads the Sigstore bundle and delegates to `sigstore.verify.Verifier`.
  - *SDK absent*: Emits a structured warning and marks packages `"unverified"`
    (no crash, no false positive).
- **Requirements parsing**: Supports `pip-compile` lock files (`requirements/lock.txt`)
  and `uv.lock` (TOML-ish format).
- **Critical package list**: 13 packages (`cryptography`, `requests`, `urllib3`,
  `certifi`, `pip`, `setuptools`, `wheel`, `sigstore`, `pyopenssl`, `pyjwt`,
  `bcrypt`, `pynacl`, `paramiko`).
- **JSON report**: `{"verified": [...], "unverified": [...], "errors": [...]}`
- **Exit codes**:
  - `0` — all OK (verified or no attestation found — most packages don't have Sigstore yet)
  - `1` — actual signature *mismatch* on a **critical** package
  - `2` — script error (missing file, etc.)
- **`--critical-only`** flag to limit scan scope.

### Usage

```bash
# Default: checks requirements/lock.txt, prints JSON to stdout
python scripts/security/sigstore_verify.py

# With explicit requirements file and JSON output
python scripts/security/sigstore_verify.py \
  --requirements requirements/lock.txt \
  --output sigstore-report.json

# Critical packages only (faster)
python scripts/security/sigstore_verify.py --critical-only

# With sigstore SDK installed
pip install sigstore
python scripts/security/sigstore_verify.py --critical-only
```

### Smoke-test output (warning mode, no SDK)

```
INFO: Using requirements file: requirements/lock.txt
WARNING: sigstore SDK not installed. Install with: pip install sigstore
INFO: Found 6 packages to check
INFO: [1/6] Checking certifi==2026.1.4 …
...
{
  "sigstore_sdk_available": false,
  "summary": {"total": 6, "verified": 0, "unverified": 6, "errors": 0, "mismatches": 0},
  "verified": [],
  "unverified": [...],
  "errors": []
}
```

---

## Workflow: `.github/workflows/sigstore-verify.yml`

### Triggers

```yaml
on:
  workflow_dispatch:   # manual, with optional inputs
  pull_request:        # auto on requirements/lock/pyproject changes
    paths:
      - "requirements/**"
      - "uv.lock"
      - "pyproject.toml"
      - "scripts/security/sigstore_verify.py"
```

### Permissions

```yaml
permissions:
  contents: read   # minimal, read-only
```

### Artifacts

- Uploads `sigstore-report.json` as `sigstore-verification-report-<run_id>`
- Retained for 30 days
- `if-no-files-found: warn` — soft failure if script errored before writing

---

## Tests: `tests/security/test_sigstore_verify.py`

**21 tests** across 6 test classes, all passing:

```
tests/security/test_sigstore_verify.py::TestParseRequirements::test_parses_pinned_packages PASSED
tests/security/test_sigstore_verify.py::TestParseRequirements::test_skips_comment_and_blank_lines PASSED
tests/security/test_sigstore_verify.py::TestParseRequirements::test_deduplicates_packages PASSED
tests/security/test_sigstore_verify.py::TestParseRequirements::test_uv_lock_format PASSED
tests/security/test_sigstore_verify.py::TestVerifyPackageWithoutSigstore::test_returns_unverified_when_sdk_absent PASSED
tests/security/test_sigstore_verify.py::TestVerifyPackageWithoutSigstore::test_critical_flag_set_for_known_packages PASSED
tests/security/test_sigstore_verify.py::TestVerifyPackageWithoutSigstore::test_non_critical_flag_for_unknown_packages PASSED
tests/security/test_sigstore_verify.py::TestVerifyPackageWithoutSigstore::test_to_dict_contains_required_keys PASSED
tests/security/test_sigstore_verify.py::TestVerifyPackageWithSigstoreNoAttestation::test_no_attestation_returns_unverified PASSED
tests/security/test_sigstore_verify.py::TestVerifyPackageWithSigstoreNoAttestation::test_network_error_returns_error_status PASSED
tests/security/test_sigstore_verify.py::TestVerifyPackageWithAttestation::test_successful_attestation_returns_verified PASSED
tests/security/test_sigstore_verify.py::TestVerifyPackageWithAttestation::test_failed_attestation_returns_mismatch PASSED
tests/security/test_sigstore_verify.py::TestBuildReport::test_report_has_required_top_level_keys PASSED
tests/security/test_sigstore_verify.py::TestBuildReport::test_summary_counts_match_lists PASSED
tests/security/test_sigstore_verify.py::TestBuildReport::test_empty_package_list_returns_zeroes PASSED
tests/security/test_sigstore_verify.py::TestMainCLI::test_exit_0_when_no_mismatches PASSED
tests/security/test_sigstore_verify.py::TestMainCLI::test_exit_2_on_missing_file PASSED
tests/security/test_sigstore_verify.py::TestMainCLI::test_output_written_to_file PASSED
tests/security/test_sigstore_verify.py::TestMainCLI::test_critical_only_flag_filters_packages PASSED
tests/security/test_sigstore_verify.py::TestMainCLI::test_exit_1_on_critical_mismatch PASSED
tests/security/test_sigstore_verify.py::TestMainCLI::test_exit_0_on_non_critical_mismatch PASSED

21 passed, 1 warning in 0.99s
```

### Test coverage highlights

| Scenario | Test |
|----------|------|
| pip-compile lock file parsing | `test_parses_pinned_packages` |
| uv.lock TOML format | `test_uv_lock_format` |
| Comment/blank line skipping | `test_skips_comment_and_blank_lines` |
| Deduplication | `test_deduplicates_packages` |
| No SDK → unverified (not error) | `test_returns_unverified_when_sdk_absent` |
| Critical flag detection | `test_critical_flag_set_for_known_packages` |
| `to_dict()` contract | `test_to_dict_contains_required_keys` |
| No attestation → unverified | `test_no_attestation_returns_unverified` |
| Network error → error status | `test_network_error_returns_error_status` |
| SDK verifies bundle | `test_successful_attestation_returns_verified` |
| SDK mismatch → mismatch status | `test_failed_attestation_returns_mismatch` |
| Report structure | `test_report_has_required_top_level_keys` |
| Summary consistency | `test_summary_counts_match_lists` |
| Empty list | `test_empty_package_list_returns_zeroes` |
| CLI exit 0 (no mismatch) | `test_exit_0_when_no_mismatches` |
| CLI exit 2 (missing file) | `test_exit_2_on_missing_file` |
| CLI writes JSON file | `test_output_written_to_file` |
| `--critical-only` filtering | `test_critical_only_flag_filters_packages` |
| CLI exit 1 (critical mismatch) | `test_exit_1_on_critical_mismatch` |
| CLI exit 0 (non-critical mismatch) | `test_exit_0_on_non_critical_mismatch` |

---

## Design Decisions

1. **No hard fail on missing Sigstore bundle**: The PyPI ecosystem has very few
   packages with Sigstore attestations today (primarily `pip` itself and a handful
   of Google/Sigstore-org packages).  Failing on absence would make the check
   unusable.  Only a *verified-but-wrong* signature triggers exit 1.

2. **`urllib.request` (stdlib) only**: Avoids adding `httpx`/`requests` as a
   test-time dependency for the script itself.

3. **Critical package list**: Curated to packages where supply-chain compromise
   would have the highest impact (crypto, TLS, auth).

4. **Structured warning mode**: When the SDK is absent, the JSON report is still
   valid and uploadable as a CI artifact — useful for tracking adoption over time.

---

## Done Criteria

- [x] `scripts/security/sigstore_verify.py` present and executable (`chmod +x`)
- [x] `.github/workflows/sigstore-verify.yml` present with `workflow_dispatch` + `pull_request` triggers and `permissions: contents: read`
- [x] ≥3 unit tests pass: `pytest tests/security/test_sigstore_verify.py -v --tb=short` → **21 passed**
- [x] Evidence file at `workbench/evidence/gap28_sigstore.md`
- [x] `workbench/gap_backlog_prioritized.md` gap 28 → `✅ Implemented`
