# Test Coverage Baseline Report for _codex_ Repository
**Generated:** 2026-01-18  
**Analysis Type:** Repository-Wide Coverage Gap Analysis  
**Target Coverage:** 70% (Aspirational: 100%)

---

## Executive Summary

### Current Coverage State
- **Overall Coverage:** 27.45% (196/714 files with tests)
- **Untested Modules:** 518 files
- **Coverage Gap:** 42.55% to reach 70% target
- **Test Files:** 1,712 test files
- **Source Files:** 1,042 Python files

### Component Breakdown

| Component | Total Files | Files with Tests | Coverage % |
|-----------|-------------|------------------|------------|
| src/codex_ml/ | 439 | ~120 | 27.3% |
| src/codex/ | 229 | ~62 | 27.1% |
| agents/ | 33 | ~9 | 27.3% |
| training/ | 13 | ~5 | 38.5% |
| **TOTAL** | **714** | **196** | **27.45%** |

---

## Top 20 Priority Untested Modules

### Tier 1: Critical Priority (Score: 90-100)

#### 1. **src/codex_ml/cli/main.py** - Score: 100
- **Size:** 28,703 bytes
- **Priority:** CRITICAL
- **Rationale:** Main CLI entry point for ML operations
- **Impact:** High - Core user interface
- **Effort:** 3-5 days

#### 2. **src/codex_ml/training/unified_training.py** - Score: 100
- **Size:** 22,006 bytes
- **Priority:** CRITICAL
- **Rationale:** Central training orchestration logic
- **Impact:** High - Training pipeline stability
- **Effort:** 4-6 days

#### 3. **src/codex_ml/data/loader.py** - Score: 90
- **Size:** 17,897 bytes
- **Priority:** HIGH
- **Rationale:** Data loading infrastructure
- **Impact:** High - Data pipeline reliability
- **Effort:** 3-4 days

#### 4. **src/codex_ml/data/validation.py** - Score: 90
- **Size:** 16,778 bytes
- **Priority:** HIGH
- **Rationale:** Data validation and quality checks
- **Impact:** High - Data integrity
- **Effort:** 3-4 days

#### 5. **src/codex_ml/safety/moderation.py** - Score: 90
- **Size:** 10,865 bytes
- **Priority:** HIGH
- **Rationale:** Safety and content moderation
- **Impact:** High - Security & compliance
- **Effort:** 2-3 days

#### 6. **src/codex/cli/main.py** - Score: 90
- **Size:** 11,039 bytes
- **Priority:** HIGH
- **Rationale:** Main CLI for codex operations
- **Impact:** High - User-facing interface
- **Effort:** 2-3 days

#### 7. **src/codex/auth/oauth_manager.py** - Score: 90
- **Size:** 13,402 bytes
- **Priority:** HIGH
- **Rationale:** OAuth authentication management
- **Impact:** High - Security critical
- **Effort:** 3-4 days

#### 8. **src/codex/security/storage.py** - Score: 90
- **Size:** 11,351 bytes
- **Priority:** HIGH
- **Rationale:** Secure storage implementation
- **Impact:** High - Security critical
- **Effort:** 2-3 days

### Tier 1: High Priority (Score: 80-89)

#### 9. **src/codex_ml/training/legacy_api.py** - Score: 80
- **Size:** 60,999 bytes (LARGEST)
- **Priority:** HIGH
- **Rationale:** Legacy training API compatibility
- **Impact:** Medium - Backward compatibility
- **Effort:** 8-10 days (complex)

#### 10. **src/codex_ml/config/__init__.py** - Score: 80
- **Size:** 33,679 bytes
- **Priority:** HIGH
- **Rationale:** Configuration management
- **Impact:** High - System-wide impact
- **Effort:** 5-7 days

#### 11. **src/codex_ml/monitoring/codex_logging.py** - Score: 80
- **Size:** 29,696 bytes
- **Priority:** HIGH
- **Rationale:** Logging infrastructure
- **Impact:** Medium - Observability
- **Effort:** 4-5 days

#### 12. **src/codex_ml/security/cve_monitor.py** - Score: 80
- **Size:** 6,417 bytes
- **Priority:** HIGH
- **Rationale:** CVE monitoring and alerting
- **Impact:** High - Security critical
- **Effort:** 2 days

#### 13. **src/codex_ml/data/loaders/hdf5_loader.py** - Score: 80
- **Size:** 5,929 bytes
- **Priority:** HIGH
- **Rationale:** HDF5 data loading
- **Impact:** Medium - Data format support
- **Effort:** 1-2 days

#### 14. **src/codex_ml/data/loaders/parquet_loader.py** - Score: 80
- **Size:** 5,809 bytes
- **Priority:** HIGH
- **Rationale:** Parquet data loading
- **Impact:** Medium - Data format support
- **Effort:** 1-2 days

#### 15. **src/codex/security/log_sanitizer.py** - Score: 80
- **Size:** 6,609 bytes
- **Priority:** HIGH
- **Rationale:** Log sanitization for PII
- **Impact:** High - Privacy compliance
- **Effort:** 2 days

#### 16. **src/codex/security/__init__.py** - Score: 80
- **Size:** 7,119 bytes
- **Priority:** HIGH
- **Rationale:** Security module initialization
- **Impact:** High - Security critical
- **Effort:** 2 days

### Tier 2: Important (Score: 70-79)

#### 17. **src/codex_ml/training/fsdp_wrapper.py** - Score: 70
- **Size:** 18,830 bytes
- **Priority:** HIGH
- **Rationale:** FSDP distributed training
- **Impact:** Medium - Distributed training
- **Effort:** 3-4 days

#### 18. **src/codex_ml/training/strategies.py** - Score: 70
- **Size:** 18,099 bytes
- **Priority:** HIGH
- **Rationale:** Training strategies
- **Impact:** Medium - Training flexibility
- **Effort:** 3-4 days

#### 19. **src/codex_ml/cli/metrics_cli.py** - Score: 70
- **Size:** 19,745 bytes
- **Priority:** HIGH
- **Rationale:** Metrics CLI interface
- **Impact:** Medium - Monitoring
- **Effort:** 3 days

#### 20. **src/codex_ml/cli/train.py** - Score: 70
- **Size:** 17,667 bytes
- **Priority:** HIGH
- **Rationale:** Training CLI commands
- **Impact:** High - User interface
- **Effort:** 3 days

---

## Quick Wins Analysis

### Low Effort, High Impact (1-2 days, Score 70+)

1. **src/codex_ml/security/cve_monitor.py** (6,417 bytes, Score: 80)
   - **Why:** Small, focused module with clear API
   - **Tests Needed:** 15-20 unit tests
   - **Estimated LOC:** 500-700 test lines

2. **src/codex_ml/data/loaders/hdf5_loader.py** (5,929 bytes, Score: 80)
   - **Why:** Well-defined data loading interface
   - **Tests Needed:** 10-15 unit tests
   - **Estimated LOC:** 400-600 test lines

3. **src/codex_ml/data/loaders/parquet_loader.py** (5,809 bytes, Score: 80)
   - **Why:** Similar to HDF5 loader
   - **Tests Needed:** 10-15 unit tests
   - **Estimated LOC:** 400-600 test lines

4. **src/codex/security/log_sanitizer.py** (6,609 bytes, Score: 80)
   - **Why:** Input/output transformation logic
   - **Tests Needed:** 20-25 unit tests
   - **Estimated LOC:** 600-800 test lines

5. **src/codex_ml/safety/sandbox.py** (2,887 bytes, Score: 70)
   - **Why:** Small sandbox implementation
   - **Tests Needed:** 8-12 unit tests
   - **Estimated LOC:** 300-400 test lines

### Medium Effort, High Impact (3-5 days, Score 90+)

6. **src/codex_ml/data/loader.py** (17,897 bytes, Score: 90)
   - **Why:** Core data infrastructure
   - **Tests Needed:** 40-50 unit tests
   - **Estimated LOC:** 1,500-2,000 test lines

7. **src/codex_ml/data/validation.py** (16,778 bytes, Score: 90)
   - **Why:** Critical for data quality
   - **Tests Needed:** 35-45 unit tests
   - **Estimated LOC:** 1,200-1,800 test lines

8. **src/codex/auth/oauth_manager.py** (13,402 bytes, Score: 90)
   - **Why:** Security critical, well-scoped
   - **Tests Needed:** 30-40 unit tests
   - **Estimated LOC:** 1,000-1,500 test lines

---

## Coverage by Major Component

### src/codex_ml/ - ML Components (439 files)

| Subcomponent | Files | Est. Coverage | Priority |
|--------------|-------|---------------|----------|
| training/ | 20 | 15% | CRITICAL |
| data/ | 20 | 20% | CRITICAL |
| cli/ | 30 | 25% | HIGH |
| safety/ | 5 | 10% | CRITICAL |
| security/ | 4 | 15% | CRITICAL |
| monitoring/ | 12 | 30% | MEDIUM |
| utils/ | 45 | 35% | MEDIUM |
| models/ | 8 | 25% | HIGH |
| eval/ | 7 | 20% | HIGH |
| metrics/ | 12 | 30% | MEDIUM |
| Other | 276 | 28% | VARIES |

### src/codex/ - Core Components (229 files)

| Subcomponent | Files | Est. Coverage | Priority |
|--------------|-------|---------------|----------|
| cli/ | 3 | 20% | HIGH |
| auth/ | 2 | 5% | CRITICAL |
| security/ | 3 | 10% | CRITICAL |
| rag/ | 6 | 25% | HIGH |
| logging/ | 8 | 30% | MEDIUM |
| archive/ | 18 | 30% | MEDIUM |
| zendesk/ | 25 | 25% | MEDIUM |
| Other | 164 | 28% | VARIES |

### agents/ - Agent Systems (33 files)

| Subcomponent | Files | Est. Coverage | Priority |
|--------------|-------|---------------|----------|
| Core Agents | 15 | 20% | HIGH |
| Memory | 4 | 25% | HIGH |
| Interpretability | 2 | 15% | MEDIUM |
| Prompts | 12 | 35% | LOW |

### training/ - Training Scripts (13 files)

| Subcomponent | Files | Est. Coverage | Priority |
|--------------|-------|---------------|----------|
| Core Training | 8 | 40% | MEDIUM |
| Utilities | 5 | 35% | LOW |

---

## Phase 2 Test Generation Plan (Weeks 3-5)

### Week 3: Critical Path

**Target:** Add 80 test files (Tier 1 modules)

#### Days 1-2: Security Critical (20 tests)
- src/codex_ml/security/cve_monitor.py
- src/codex/security/storage.py
- src/codex/security/log_sanitizer.py
- src/codex/security/__init__.py
- src/codex_ml/safety/moderation.py

#### Days 3-4: Data Pipeline (25 tests)
- src/codex_ml/data/loader.py
- src/codex_ml/data/validation.py
- src/codex_ml/data/loaders/hdf5_loader.py
- src/codex_ml/data/loaders/parquet_loader.py
- src/codex_ml/data/loaders/arrow_loader.py

#### Day 5: Authentication (15 tests)
- src/codex/auth/oauth_manager.py
- src/codex_ml/auth/* (if exists)

**Week 3 Target Coverage:** +8-10%

### Week 4: Core Infrastructure

**Target:** Add 100 test files (Tier 2 modules)

#### Days 1-2: Training Infrastructure (30 tests)
- src/codex_ml/training/unified_training.py
- src/codex_ml/training/strategies.py
- src/codex_ml/training/fsdp_wrapper.py
- src/codex_ml/training/scheduler_factory.py

#### Days 3-4: CLI & Configuration (35 tests)
- src/codex_ml/cli/main.py
- src/codex/cli/main.py
- src/codex_ml/config/__init__.py
- src/codex_ml/cli/train.py

#### Day 5: Monitoring & Logging (35 tests)
- src/codex_ml/monitoring/codex_logging.py
- src/codex/logging/session_logger.py
- src/codex/logging/viewer.py
- src/codex/logging/query_logs.py

**Week 4 Target Coverage:** +12-15%

### Week 5: Coverage Expansion

**Target:** Add 120 test files (Tier 3 modules + Integration)

#### Days 1-2: Agent Systems (40 tests)
- agents/physics_orchestrator.py
- agents/agent_memory.py
- agents/developer_orchestrator.py
- agents/workflow_navigator.py

#### Days 3-4: RAG & Retrieval (40 tests)
- src/codex/rag/indexer.py
- src/codex/rag/retriever.py
- src/codex/retrieval/stores/faiss_store.py
- src/codex/retrieval/stores/advanced_indexing.py

#### Day 5: Integration Tests (40 tests)
- End-to-end training workflows
- CLI integration tests
- Data pipeline integration
- Authentication flows

**Week 5 Target Coverage:** +10-12%

---

## Estimated Effort Summary

### By Priority Tier

| Tier | Files | Est. Days | Est. Coverage Gain |
|------|-------|-----------|-------------------|
| Tier 1 (Critical) | 50 | 15 days | 12-15% |
| Tier 2 (High) | 100 | 20 days | 15-18% |
| Tier 3 (Medium) | 150 | 25 days | 12-15% |
| Tier 4 (Low) | 218 | 30 days | 8-10% |
| **TOTAL** | **518** | **90 days** | **47-58%** |

### Phase 2 Focused Effort (Weeks 3-5)

| Week | Focus Area | Files Added | Est. Coverage Gain |
|------|-----------|-------------|-------------------|
| Week 3 | Critical Path | 60-80 | 8-10% |
| Week 4 | Core Infrastructure | 80-100 | 12-15% |
| Week 5 | Expansion | 100-120 | 10-12% |
| **TOTAL** | **Weeks 3-5** | **240-300** | **30-37%** |

**Expected Coverage After Phase 2:** 57-65%  
**Target Coverage:** 70%  
**Gap After Phase 2:** 5-13%

---

## Test Generation Strategy

### Testing Approach by Module Type

#### 1. CLI Modules (e.g., main.py files)
- **Strategy:** Argument parsing tests, command execution tests
- **Tools:** pytest, click.testing.CliRunner, argparse mocks
- **Coverage Target:** 75-85%
- **Estimated Tests per Module:** 25-40

#### 2. Data Loaders (e.g., hdf5_loader.py)
- **Strategy:** Format parsing, error handling, edge cases
- **Tools:** pytest, fixtures with sample files, tmpdir
- **Coverage Target:** 80-90%
- **Estimated Tests per Module:** 15-25

#### 3. Security Modules (e.g., oauth_manager.py)
- **Strategy:** Auth flows, token validation, error cases
- **Tools:** pytest, mocking (requests, responses), fixtures
- **Coverage Target:** 85-95%
- **Estimated Tests per Module:** 30-50

#### 4. Training Infrastructure
- **Strategy:** Training loops, distributed setup, checkpointing
- **Tools:** pytest, torch mocks, distributed test helpers
- **Coverage Target:** 70-80%
- **Estimated Tests per Module:** 35-60

#### 5. Agent Systems
- **Strategy:** Agent behavior, state management, integration
- **Tools:** pytest, async testing, agent fixtures
- **Coverage Target:** 65-75%
- **Estimated Tests per Module:** 20-40

---

## Recommendations for Phase 2

### Immediate Actions (Week 3, Days 1-2)

1. **Security Quick Wins** - Start with security modules for compliance
   - CVE monitor, log sanitizer, storage
   - ROI: High (critical paths secured)
   - Effort: 2 days, 35 tests

2. **Data Pipeline Foundation** - Build data reliability
   - loader.py, validation.py, format loaders
   - ROI: High (data quality gates)
   - Effort: 3 days, 60 tests

3. **Authentication Coverage** - Secure auth flows
   - oauth_manager.py
   - ROI: Critical (security requirement)
   - Effort: 1.5 days, 35 tests

### Automation Opportunities

1. **Template Generation** - Create test templates for common patterns
   - CLI test template
   - Data loader test template
   - Security test template

2. **Coverage Dashboard** - Real-time coverage monitoring
   - Daily coverage reports
   - Module-level tracking
   - Trend analysis

3. **Auto-test Generation** - Use AI to generate basic test scaffolds
   - Use test-coverage-guardian agent
   - Human review and enhancement
   - Focus on boilerplate reduction

---

## Risk Assessment

### High-Risk Untested Areas

1. **Security (CRITICAL)**
   - Authentication, authorization, secrets management
   - **Risk:** Security vulnerabilities, compliance failures
   - **Mitigation:** Prioritize security tests in Week 3

2. **Data Pipeline (HIGH)**
   - Data loading, validation, transformation
   - **Risk:** Data corruption, training failures
   - **Mitigation:** Prioritize data tests in Week 3-4

3. **Training Infrastructure (HIGH)**
   - Training loops, distributed training, checkpointing
   - **Risk:** Training failures, model corruption
   - **Mitigation:** Comprehensive testing in Week 4

4. **Agent Systems (MEDIUM)**
   - Agent orchestration, state management
   - **Risk:** Incorrect behavior, instability
   - **Mitigation:** Integration tests in Week 5

---

## Success Metrics

### Phase 2 Goals (Weeks 3-5)

| Metric | Current | Week 3 Target | Week 4 Target | Week 5 Target |
|--------|---------|---------------|---------------|---------------|
| Overall Coverage | 27.5% | 35-37% | 47-52% | 57-65% |
| Critical Modules | 10% | 60% | 75% | 85% |
| Test Files | 1,712 | 1,772 | 1,872 | 1,992 |
| High Priority Coverage | 20% | 50% | 70% | 85% |

### Quality Gates

- **Minimum Coverage per PR:** 70% for new code
- **Critical Modules:** 85% minimum
- **Security Modules:** 90% minimum
- **Test Stability:** <1% flaky test rate
- **CI Time:** <30 min for full test suite

---

## Appendix: Full Untested Module List

**Note:** See `.codex/qa_walkthrough/coverage_analysis.json` for complete list of 518 untested modules with priority scores and size metrics.

### Breakdown by Priority Score

- **Score 90-100 (Critical):** 8 modules
- **Score 80-89 (High):** 9 modules
- **Score 70-79 (Important):** 33 modules
- **Score 65-69 (Moderate-High):** 66 modules
- **Score 50-64 (Moderate):** 102 modules
- **Score 40-49 (Medium):** 150 modules
- **Score 25-39 (Low):** 150 modules

---

## Next Steps

1. **Review this baseline** with team and stakeholders
2. **Approve Phase 2 plan** for Weeks 3-5
3. **Assign test-coverage-guardian agent** to execute
4. **Set up coverage monitoring** dashboard
5. **Begin Week 3, Day 1** with security quick wins

**Report Generated By:** Test Coverage Monitor Agent  
**Date:** 2026-01-18  
**Version:** 1.0  
**Next Review:** End of Week 3
