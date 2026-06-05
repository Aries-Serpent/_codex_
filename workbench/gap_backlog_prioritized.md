# Prioritized Gap Remediation Backlog
**Generated:** 2025-12-06 03:42:00
**Re-baselined:** [rebaseline-date] (S-gap-resolution kickoff — PR #4783)

[rebaseline-date]: 2026-06-05

This document provides a complete, prioritized backlog of all identified gaps, organized by:
- Priority (P0-P3)
- Effort (Small/Medium/Large)
- Impact (Low/Medium/High/Critical)
- Category (Capability domain)

**Status legend:**
- 🔴 Not Started
- 🟡 In Progress
- ✅ Implemented
- 🔎 Needs Verification

## Priority Definitions
- **P0 (Critical):** Blocking production deployment, must fix immediately
- **P1 (High):** Required for production readiness, fix within 2 phases
- **P2 (Medium):** Important for operational excellence, fix within 1 month
- **P3 (Low):** Nice to have, enhances quality, fix within 1 quarter

## Effort Definitions
- **Small:** 1-2 iterations
- **Medium:** 3-5 iterations
- **Large:** 1-2 weeks
- **XLarge:** 3+ weeks

---

## P0: Critical Priority (Must Do Now)

### Security & Compliance
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 1 | Run pip-audit on all requirements and remediate critical CVEs | Small | Critical | Security | 🔴 Not Started |
| 2 | Run bandit/semgrep and fix all high-severity findings | Small | Critical | Security | 🔴 Not Started |
| 3 | Verify all secrets in .secrets.baseline are false positives | Small | High | Security | 🔴 Not Started |

### Operations & Monitoring
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 4 | Implement health check endpoints (readiness/liveness) | Medium | Critical | Ops | ✅ Implemented — `monitoring/dashboard_api.py` `/readiness`+`/liveness` probes added (PR #4783) |
| 5 | Add coverage gate enforcement (≥80% threshold) | Small | High | QA | 🟡 In Progress — `pyproject.toml` floor at 10; roadmap targets 80%; raised incrementally per S-session plan |

---

## P1: High Priority (Do Within 2 phases)

### Reproducibility & Determinism
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 6 | Save and restore RNG state in checkpoints | Medium | High | ML | ✅ Implemented — `src/codex_ml/utils/checkpointing.py` `dump_rng_state`/`load_rng_state`; `training/checkpoint_manager.py` uses it |
| 7 | Enforce torch.use_deterministic_algorithms(True) | Small | High | ML | ✅ Implemented — `src/codex_ml/utils/determinism.py` `set_deterministic()` calls `torch.use_deterministic_algorithms(True)` |
| 8 | Capture and log Python/CUDA/hardware versions | Small | High | Ops | ✅ Implemented — `src/codex_ml/utils/env.py` `EnvironmentFingerprint` dataclass with CUDA driver, GPU device info, RAM (PR #4783) |
| 9 | Pin Docker base images to specific digests | Small | Medium | Ops | 🔴 Not Started |

### Autonomy & Self-Healing
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 10 | Implement config drift detection | Medium | High | Platform | ✅ Implemented — `src/codex_ml/utils/config_drift.py` `ConfigDrift.has_drift()` and `detect_config_drift()` |
| 11 | Add automated dependency vulnerability scanning to CI | Small | High | Security | 🔴 Not Started |
| 12 | Set up alerting for training failures | Medium | High | Ops | 🔴 Not Started |
| 13 | Add performance degradation alerts | Medium | High | Ops | 🔴 Not Started |

### Monitoring & Observability
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 14 | Set up Prometheus metrics collection | Medium | High | Ops | 🔎 Needs Verification — `tests/monitoring/test_prometheus_metrics_registry.py` and `test_prometheus_fallback.py` exist; integration wiring TBD |
| 15 | Create Grafana dashboards for key metrics | Medium | Medium | Ops | 🔴 Not Started |
| 16 | Add distributed tracing (optional) | Large | Medium | Ops | 🔴 Not Started |

---

## P2: Medium Priority (Do Within 1 Month)

### Data & Model Management
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 17 | Implement data drift monitoring | Large | Medium | ML | 🔴 Not Started |
| 18 | Add model drift detection | Large | Medium | ML | 🔴 Not Started |
| 19 | Set up DVC for active data versioning | Medium | Medium | ML | 🔎 Needs Verification — `dvc.yaml` exists; needs CI pipeline wiring |
| 20 | Implement deterministic data splits | Small | Medium | ML | 🔴 Not Started |

### Testing & Quality
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 21 | Build comprehensive regression test suite | Large | High | QA | 🔴 Not Started |
| 22 | Add mutation testing with mutmut | Medium | Medium | QA | 🔴 Not Started |
| 23 | Implement automated integration tests | Large | Medium | QA | 🔴 Not Started |
| 24 | Add performance benchmarking suite | Medium | Medium | QA | 🔴 Not Started |

### Security & Supply Chain
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 25 | Generate SBOM for all releases | Small | Medium | Security | ✅ Implemented — `scripts/sbom_cyclonedx.py` generates CycloneDX SBOM from `requirements/lock.txt`/`uv.lock` |
| 26 | Add container scanning with Trivy/Grype | Small | Medium | Security | 🔴 Not Started |
| 27 | Implement input sanitization for LLM prompts | Medium | High | Security | 🔎 Needs Verification — `src/codex_ml/safety/moderation.py` `ModerationAdapter` provides prompt sanitization |
| 28 | Add Sigstore verification for critical dependencies | Medium | Medium | Security | 🔴 Not Started |

### Error Handling & Resilience
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 29 | Implement circuit breakers for external services | Medium | Medium | Platform | 🔴 Not Started |
| 30 | Add exponential backoff retry logic | Small | Medium | Platform | 🔴 Not Started |
| 31 | Build graceful degradation mechanisms | Medium | Medium | Platform | 🔴 Not Started |

---

## P3: Low Priority (Do Within 1 Quarter)

### Code Quality & Maintenance
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 32 | Clean up 1,152 TODOs/FIXMEs/stubs | XLarge | Medium | Team | 🔴 Not Started |
| 33 | Add mypy to pre-commit hooks | Small | Low | QA | 🔴 Not Started |
| 34 | Implement automated docstring generation | Medium | Low | Docs | 🔴 Not Started |
| 35 | Add schema validation to pre-commit | Small | Low | QA | 🔴 Not Started |

### Advanced Features
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 36 | Build continuous learning pipeline | XLarge | Low | ML | 🔴 Not Started |
| 37 | Implement A/B testing framework | Large | Low | ML | 🔴 Not Started |
| 38 | Add automated model retraining | Large | Low | ML | 🔴 Not Started |
| 39 | Build feedback loop integration | Large | Low | ML | 🔴 Not Started |

### Testing & Validation
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 40 | Add fuzzing for critical code paths | Large | Low | QA | 🔴 Not Started |
| 41 | Implement property-based testing expansion | Medium | Low | QA | 🔴 Not Started |
| 42 | Add chaos engineering tests | Large | Low | QA | 🔴 Not Started |

### Documentation & Onboarding
| # | Gap | Effort | Impact | Owner | Status |
|---|-----|--------|--------|-------|--------|
| 43 | Create video tutorials for key workflows | Medium | Low | Docs | 🔴 Not Started |
| 44 | Build interactive documentation with examples | Large | Low | Docs | 🔴 Not Started |
| 45 | Add architecture decision records (ADRs) | Medium | Low | Arch | 🔴 Not Started |

---

## Summary Statistics

**Total Gaps Identified:** 45
**Re-baselined:** [rebaseline-date] (S-gap-resolution kickoff — PR #4783)

| Priority | Total | ✅ Implemented | 🔎 Needs Verification | 🟡 In Progress | 🔴 Not Started |
|----------|-------|---------------|----------------------|----------------|----------------|
| P0 | 5 | 1 (gap 4) | 0 | 1 (gap 5) | 3 |
| P1 | 11 | 4 (gaps 6,7,8,10) | 1 (gap 14) | 0 | 6 |
| P2 | 14 | 1 (gap 25) | 2 (gaps 19,27) | 0 | 11 |
| P3 | 15 | 0 | 0 | 0 | 15 |

> *Gap 14 (Prometheus) has test scaffolding but needs integration wiring verification.

**Estimated Total Effort:**
- Small tasks: ~15 (15-30 iterations)
- Medium tasks: ~18 (54-90 iterations)
- Large tasks: ~10 (50-100 iterations)
- XLarge tasks: ~2 (20-40 iterations)

**Total: ~140-260 iterations of engineering effort** (3-6 months with a team of 2-3 engineers)

---

## Recommended Execution Strategy

### Phase 1: Foundation
Focus: Security, Monitoring, Basic Autonomy
- Complete all P0 tasks (gaps 1-5)
- Complete P1 autonomy tasks (gaps 10-13)
- Complete P1 observability tasks (gaps 14-16)

### Phase 2: Reproducibility & Quality
Focus: Determinism, Testing, Supply Chain
- Complete P1 reproducibility tasks (gaps 6-9)
- Complete P2 testing tasks (gaps 21-24)
- Complete P2 security tasks (gaps 25-28)

### Phase 3: Advanced Autonomy
Focus: Drift Detection, Error Handling, Data Management
- Complete P2 data/model tasks (gaps 17-20)
- Complete P2 resilience tasks (gaps 29-31)
- Start P3 code quality cleanup (gap 32)

### Phase 4: Excellence & Innovation
Focus: Advanced Features, Documentation, Long-term Quality
- Complete remaining P3 tasks
- Build continuous improvement systems
- Establish measurement and monitoring for ongoing health

---

*Generated: 2025-12-06 03:42:00*
