# [Explain Set]: Capability Component Breakdowns  
> Generated: 2025-12-06 04:45:00Z | Author: Comprehensive Audit System  
> 🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

This document presents component contributions for critical capabilities (top gaps and core systems).

## 1) safety-security (LOWEST SCORE)
| Component | Value | Weight | Contribution |
|-----------|------:|-------:|-------------:|
| functionality | 0.50 | 0.25 | 0.1250 |
| consistency | 0.85 | 0.20 | 0.1700 |
| tests | 0.40 | 0.25 | 0.1000 |
| safeguards | 0.50 | 0.15 | 0.0750 |
| documentation | 0.40 | 0.15 | 0.0600 |
| **Total** | — | — | **0.6100** |

**Notes:**
- Functionality and tests are limiting factors; prompt sanitization default and vendor checks would raise both.
- Consistency is good (0.85) but insufficient to compensate for weak functionality.

**Recommendations:**
- Default prompt sanitization to True
- Add weekly vendor evidence scans
- Implement automated security scanning in CI
- Expand test coverage for security features

## 2) data-pipeline
| Component | Value | Weight | Contribution |
|-----------|------:|-------:|-------------:|
| functionality | 0.65 | 0.25 | 0.1625 |
| consistency | 0.80 | 0.20 | 0.1600 |
| tests | 0.45 | 0.25 | 0.1125 |
| safeguards | 0.33 | 0.15 | 0.0495 |
| documentation | 0.55 | 0.15 | 0.0825 |
| **Total** | — | — | **0.7200** |

**Notes:**
- Increase tests (streaming, caching) and safeguards (dataset checksums) to lift maturity.
- Add Great Expectations for data quality validation.

**Recommendations:**
- Add streaming determinism tests
- Implement dataset hash manifest
- Add schema validation
- Expand data quality checks

## 3) evaluation-metrics
| Component | Value | Weight | Contribution |
|-----------|------:|-------:|-------------:|
| functionality | 0.60 | 0.25 | 0.1500 |
| consistency | 0.85 | 0.20 | 0.1700 |
| tests | 0.50 | 0.25 | 0.1250 |
| safeguards | 0.33 | 0.15 | 0.0495 |
| documentation | 0.58 | 0.15 | 0.0870 |
| **Total** | — | — | **0.7400** |

**Notes:**
- Add NDJSON sync and CLI flags (`--limit`, `--batch-size`) for robustness; expand test breadth.
- Metric determinism not enforced.

**Recommendations:**
- Sync NDJSON output with training
- Add CLI control flags
- Enforce metric determinism
- Expand test regression suites

## 4) checkpointing (HIGHEST SCORE)
| Component | Value | Weight | Contribution |
|-----------|------:|-------:|-------------:|
| functionality | 1.00 | 0.25 | 0.2500 |
| consistency | 0.88 | 0.20 | 0.1760 |
| tests | 0.60 | 0.25 | 0.1500 |
| safeguards | 0.67 | 0.15 | 0.1005 |
| documentation | 0.70 | 0.15 | 0.1050 |
| **Total** | — | — | **0.8400** |

**Notes:**
- Enforce RNG sidecar and checksum strictness; add scheduler resume tests to push tests component.
- Functionality is maximal but tests could be strengthened.

**Recommendations:**
- Add --strict-resume flag
- Enforce checksum validation
- Add scheduler state resume tests
- Document deterministic resume procedures

## 5) tokenization
| Component | Value | Weight | Contribution |
|-----------|------:|-------:|-------------:|
| functionality | 0.83 | 0.25 | 0.2075 |
| consistency | 0.90 | 0.20 | 0.1800 |
| tests | 0.55 | 0.25 | 0.1375 |
| safeguards | 0.33 | 0.15 | 0.0495 |
| documentation | 0.65 | 0.15 | 0.0975 |
| **Total** | — | — | **0.8300** |

**Notes:**
- Safeguard signals can be improved via manifest hashes and model pointer integrity checks.
- Add fast tokenizer selection flag.

**Recommendations:**
- Add --use-fast flag
- Implement vocab/version pinning
- Add checksum validation
- Expand multilingual tokenizer tests

*End of Explain Set*
