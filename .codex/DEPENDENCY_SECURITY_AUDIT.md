# DEPENDENCY_SECURITY_AUDIT

Date: 2026-07-07
Source: lane2-depsec (dependency-security-review-agent)

## High/Medium Findings

| Severity | Finding | Evidence |
|---|---|---|
| High | `sqlitedict==2.1.0` vulnerable (`CVE-2024-35515`) with no upstream fix | `requirements/lock-eval.txt` |
| High | `torch==2.11.0` flagged in current security backlog | `requirements/lock*.txt`, `docs/security-open-findings-matrix.md` |
| Medium | pip-audit suppressions need ownership/expiry governance | `pyproject.toml` ignore entries |
| Medium | Lock exports use `--no-hashes`, lowering install integrity guarantees | `requirements/lock*.txt` headers |
| Medium | Build tool minimums vary across dependency surfaces | `pyproject.toml`, requirements sets |

## Packaging Risk Posture

- Base pinning is strong on lock files.
- Reproducibility can be improved with hash-locked release exports.
- External release should gate on explicit vulnerability policy exceptions.

## Recommended Actions

1. Add ownership + expiry for each ignored vulnerability ID.
2. Publish hash-verified dependency manifests for release artifacts.
3. Keep risky optional surfaces isolated from default installs.
4. Attach SBOM + vulnerability attestation to release outputs.
