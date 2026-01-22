# Phase 3 Implementation Promptset
# Autonomous Execution Instructions
# Version: 1.0.0
# Date: 2026-01-22

---

## Purpose

This promptset provides ready-to-use prompts for autonomous execution of Phase 3 implementation. Each prompt is designed for independent execution with clear objectives, context, and success criteria.

---

## Master Prompt (Full Phase 3 Execution)

```markdown
@copilot Execute Phase 3 of the CI Prevention System following the comprehensive planset at `.codex/plans/phase3_implementation_planset.md`.

**Context**: Phases 1 & 2 are complete with:
- Rust validation script with TOML parser
- 5-language multi-validator (Rust/Python/Node.js/Go/C++)
- Custom Rust Configuration Validator agent
- Metrics dashboard with JSONL storage
- Pre-commit hooks and CI integration

**Objective**: Extend system with alerting, ML, 4 new languages, API, and analytics

**Requirements** (following AI Agency Policy):
1. Complete all tasks autonomously end-to-end
2. Apply iterative self-healing (5 iterations)
3. Address ALL issues including out-of-scope
4. Update cognitive brain and agents
5. Post follow-up prompts as needed
6. Continue until 100% complete

**Priority Order**:
1. GitHub Issues alerting with deduplication
2. ML anomaly detection (Isolation Forest)
3. Language expansion (Java/Swift/Ruby/PHP)
4. REST API for metrics access
5. Trend analysis & regression detection
6. Auto-fix confidence refinement
7. Pattern library expansion
8. Agent updates (3 agents)
9. Cognitive brain documentation

**Success Criteria**:
- All 16 modules implemented and tested
- All tests passing (unit + integration)
- Documentation complete
- Agents updated
- Cognitive brain reflects Phase 3

**Deliverables**:
- 16 new Python modules
- 4 new language validators
- FastAPI server + endpoints
- Updated agents (3)
- Pattern database (YAML)
- Test suite (8 test files)
- Comprehensive documentation

**Execution Mode**: Autonomous with progress reports after each session

**Estimated Time**: 4-6 hours across multiple sessions

Begin with Session 1: Alerting Infrastructure & ML Foundation.
```

---

## Session 1 Prompt: Alerting & ML Foundation (2 hours)

```markdown
@copilot Implement Session 1 of Phase 3: Alerting Infrastructure & ML Foundation

**Objective**: Create GitHub Issues alerting system and basic ML anomaly detection

**Tasks**:
1. Create `scripts/ci/alerts/github_issues_alerter.py`
   - Implement GitHubIssuesAlerter class
   - Deduplication with fingerprinting (24h window)
   - Severity classification
   - Auto-close on resolution
   - Use gh CLI for issue creation

2. Create `scripts/ci/ml/feature_extractor.py`
   - Extract features from validation metrics JSONL
   - Time-series features: frequency, trends
   - Context features: language, file type

3. Create `scripts/ci/ml/anomaly_detector.py`
   - Implement IsolationForest model
   - Train on historical data
   - Confidence scoring
   - Incremental learning

4. Integrate alerting with validators
   - Modify `validate_cargo_features.py`
   - Modify `validate_multi_language_config.py`
   - Trigger alerts on failures

5. Test end-to-end
   - Create test validation failure
   - Verify issue created
   - Verify deduplication works
   - Verify ML predictions

**Dependencies**: Phase 1 & 2 complete (✅)

**Success Criteria**:
- Alerter creates GitHub issues successfully
- Deduplication prevents duplicate issues
- ML model trains and predicts
- Integration with validators works
- All tests pass

**Deliverables**:
- `scripts/ci/alerts/github_issues_alerter.py`
- `scripts/ci/ml/feature_extractor.py`
- `scripts/ci/ml/anomaly_detector.py`
- `scripts/ci/ml/ml_validator.py`
- `.codex/alerts/alert_config.yaml`
- Tests for alerting and ML

Report progress after implementation and testing.
```

---

## Session 2 Prompt: Language Expansion (2 hours)

```markdown
@copilot Implement Session 2 of Phase 3: Language Expansion

**Objective**: Add validators for Java, Swift, Ruby, and PHP

**Tasks**:
1. Create Java validator (`scripts/ci/validators/java_validator.py`)
   - Parse pom.xml (Maven) and build.gradle (Gradle)
   - Validate optional dependencies
   - Check profiles and variants
   - Cross-reference with Java imports

2. Create Swift validator (`scripts/ci/validators/swift_validator.py`)
   - Parse Package.swift
   - Validate conditional dependencies
   - Check platform-specific packages
   - Cross-reference with Swift imports

3. Create Ruby validator (`scripts/ci/validators/ruby_validator.py`)
   - Parse Gemfile
   - Validate groups (development, test, etc.)
   - Check platform-specific gems
   - Cross-reference with require statements

4. Create PHP validator (`scripts/ci/validators/php_validator.py`)
   - Parse composer.json
   - Validate require vs require-dev
   - Check platform requirements
   - Cross-reference with use statements

5. Integrate into multi-language validator
   - Update `validate_multi_language_config.py`
   - Add detection for new languages
   - Unified error reporting

6. Test each validator
   - Create sample configs for each language
   - Test validation passes and failures
   - Verify cross-referencing works

**Dependencies**: Session 1 complete

**Success Criteria**:
- All 4 language validators functional
- Detection working in multi-language validator
- Tests passing for each language
- Documentation for each validator

**Deliverables**:
- 4 new language validators
- Updated multi-language validator
- Test configs for each language
- Tests for each validator
- Documentation (4 files)

Report progress after all languages implemented and tested.
```

---

## Session 3 Prompt: API & Analytics (1.5 hours)

```markdown
@copilot Implement Session 3 of Phase 3: REST API & Analytics

**Objective**: Create metrics API and build analytics capabilities

**Tasks**:
1. Create FastAPI metrics server (`scripts/ci/api/metrics_api.py`)
   - Implement endpoints:
     * GET /metrics/summary
     * GET /metrics/by-language/{lang}
     * GET /metrics/trends
     * GET /metrics/recent
     * POST /metrics/validate
   - Add authentication (API key)
   - Implement rate limiting
   - CORS support

2. Create trend analyzer (`scripts/ci/analytics/trend_analyzer.py`)
   - Time-series analysis
   - Mann-Kendall trend test
   - Seasonality detection
   - Anomaly thresholds

3. Create regression detector (`scripts/ci/analytics/regression_detector.py`)
   - Compare current to baseline
   - Detect sudden changes
   - Severity classification
   - Root cause suggestions

4. Create weekly report generator (`scripts/ci/reporting/weekly_report.py`)
   - Generate comprehensive reports
   - Multiple formats (Markdown, HTML, JSON)
   - Auto-post to GitHub

5. Test API and analytics
   - Test each endpoint
   - Verify authentication
   - Test trend detection
   - Generate sample reports

**Dependencies**: Sessions 1 & 2 complete

**Success Criteria**:
- API serves metrics with <100ms latency
- All endpoints functional
- Trend analysis detects patterns
- Regression detection works
- Reports generate successfully
- Tests pass

**Deliverables**:
- FastAPI server implementation
- Trend analyzer module
- Regression detector module
- Weekly report generator
- API documentation
- Dockerfile for API
- Tests for API and analytics

Report progress after API and analytics operational.
```

---

## Session 4 Prompt: Finalization (0.5 hour)

```markdown
@copilot Complete Session 4 of Phase 3: Finalization

**Objective**: Refine auto-fix, expand patterns, update agents, finalize documentation

**Tasks**:
1. Auto-fix refinement
   - Implement feedback collector
   - Analyze success rates
   - Tune confidence thresholds
   - Update validators with new thresholds

2. Pattern library expansion
   - Create edge case collector
   - Build pattern database (YAML)
   - Implement pattern-based fixer
   - Document 20+ patterns

3. Update Custom Copilot agents
   - Update Rust Configuration Validator agent
   - Create Multi-Language Config Validator agent
   - Create CI Metrics Analyzer agent
   - Full integration with Phase 3

4. Cognitive brain documentation
   - Create phase3_completion_2026_01_22.md
   - Register new cognitive patterns
   - Update agent evolution map
   - Document integration points

5. Final validation
   - Run full test suite
   - Validate all integrations
   - Check documentation completeness
   - Verify cognitive brain updated

**Dependencies**: Sessions 1, 2, 3 complete

**Success Criteria**:
- Auto-fix precision >90%
- Pattern library has 20+ patterns
- 3 agents updated/created
- Cognitive brain complete
- All tests passing
- Documentation comprehensive

**Deliverables**:
- Auto-fix collector and tuner
- Pattern database (YAML)
- Pattern-based fixer
- 3 agent specifications
- Cognitive brain documentation
- Phase 3 completion summary

After completion, run final code review and report Phase 3 100% complete.
```

---

## Component-Specific Prompts

### Alerting Prompt

```markdown
@copilot Implement GitHub Issues alerting for validation failures

Create `scripts/ci/alerts/github_issues_alerter.py` with:
- GitHubIssuesAlerter class
- Fingerprint-based deduplication (SHA256)
- 24-hour dedup window
- Severity classification (critical/high/medium/low)
- Auto-close on resolution
- Use gh CLI for issue operations
- Cache management (JSON)

Include:
- Alert configuration (YAML)
- Integration with validators
- Tests for deduplication

Reference: `.codex/plans/phase3_implementation_planset.md` Section 3.1
```

### ML Anomaly Detection Prompt

```markdown
@copilot Implement ML-based anomaly detection for configs

Create ML modules:
1. `scripts/ci/ml/feature_extractor.py` - Extract features from metrics
2. `scripts/ci/ml/anomaly_detector.py` - IsolationForest model
3. `scripts/ci/ml/ml_validator.py` - Integration with validators

Requirements:
- Train on historical validation data
- Detect unusual patterns
- Confidence scoring
- Incremental learning
- >85% accuracy target

Include tests and example usage.

Reference: `.codex/plans/phase3_implementation_planset.md` Section 3.2
```

### Language Validator Prompt (Java)

```markdown
@copilot Create Java configuration validator

Implement `scripts/ci/validators/java_validator.py` with:
- Parse pom.xml (Maven) using xml.etree
- Parse build.gradle (Gradle) using regex/ast
- Validate optional dependencies
- Check profiles and build variants
- Cross-reference with Java imports

Test with sample Maven and Gradle projects.

Reference: `.codex/plans/phase3_implementation_planset.md` Section 3.3.1
```

### REST API Prompt

```markdown
@copilot Create REST API for validation metrics

Implement `scripts/ci/api/metrics_api.py` using FastAPI:

Endpoints:
- GET /metrics/summary - Overall stats
- GET /metrics/by-language/{lang} - Per-language
- GET /metrics/trends - Time-series
- GET /metrics/recent - Recent validations
- POST /metrics/validate - Trigger validation

Features:
- API key authentication
- Rate limiting
- CORS support
- <100ms latency target

Include Dockerfile and documentation.

Reference: `.codex/plans/phase3_implementation_planset.md` Section 3.4
```

### Trend Analysis Prompt

```markdown
@copilot Implement trend analysis and regression detection

Create analytics modules:
1. `scripts/ci/analytics/trend_analyzer.py` - Time-series analysis
2. `scripts/ci/analytics/regression_detector.py` - Detect regressions
3. `scripts/ci/reporting/weekly_report.py` - Generate reports

Use Mann-Kendall test for trends.
Compare current metrics to baseline.
Generate Markdown/HTML/JSON reports.

Reference: `.codex/plans/phase3_implementation_planset.md` Section 3.5
```

### Agent Update Prompt

```markdown
@copilot Update custom Copilot agents for Phase 3

Tasks:
1. Update `.github/agents/rust-config-validator.md`
   - Add alerting capabilities
   - Include ML anomaly detection
   - Reference new patterns

2. Create `.github/agents/multi-language-config-validator.md`
   - Specializes in 9 language ecosystems
   - Cross-language validation
   - Best practices

3. Create `.github/agents/ci-metrics-analyzer.md`
   - Analyzes trends and anomalies
   - Provides recommendations
   - Queries REST API

Include activation examples and integration docs.

Reference: `.codex/plans/phase3_implementation_planset.md` Section 3.8
```

---

## Troubleshooting Prompts

### If Tests Fail

```markdown
@copilot Debug and fix Phase 3 test failures

Context: Phase 3 implementation has test failures.

Tasks:
1. Identify failing tests: `pytest tests/ci/ -v --tb=short`
2. Analyze error messages and stack traces
3. Fix issues systematically
4. Re-run tests to verify fixes
5. Iterate until all tests pass

Report: What failed, why it failed, how you fixed it.
```

### If Integration Breaks

```markdown
@copilot Fix Phase 3 integration issues

Context: Components aren't integrating properly.

Tasks:
1. Identify integration points that broke
2. Check interface compatibility
3. Verify data flow between components
4. Add compatibility shims if needed
5. Test end-to-end integration

Focus on: Validators → Alerter → ML → API flow
```

### If Performance Issues

```markdown
@copilot Optimize Phase 3 component performance

Context: Component performance below targets.

Tasks:
1. Profile slow operations
2. Identify bottlenecks
3. Optimize algorithms/queries
4. Add caching where appropriate
5. Verify performance targets met

Targets:
- Alert creation: <5s
- ML prediction: <1s
- API response: <100ms
- Validation: <500ms
```

---

## Validation Prompts

### Unit Test Validation

```markdown
@copilot Create comprehensive unit tests for Phase 3

For each module, create tests covering:
- Happy path functionality
- Error handling
- Edge cases
- Integration points

Target: >90% code coverage for new modules

Test files needed:
- tests/ci/test_github_alerter.py
- tests/ci/test_anomaly_detector.py
- tests/ci/test_java_validator.py
- tests/ci/test_swift_validator.py
- tests/ci/test_ruby_validator.py
- tests/ci/test_php_validator.py
- tests/ci/test_metrics_api.py
- tests/ci/test_trend_analyzer.py
```

### Integration Test Validation

```markdown
@copilot Create integration tests for Phase 3 system

Test complete workflows:
1. Validation failure → Alert creation → Issue opened
2. Multiple failures → Deduplication → Single issue
3. Validation pass → Alert resolution → Issue closed
4. Anomaly detected → Alert created → Issue with ML tag
5. API request → Metrics retrieved → Response returned

Create: tests/ci/test_phase3_integration.py
```

---

## Documentation Prompts

### API Documentation

```markdown
@copilot Create comprehensive API documentation

Document:
- All endpoints with examples
- Authentication flow
- Rate limits
- Error responses
- Example requests/responses with curl
- Client libraries (Python, JavaScript)

Create: `docs/api/METRICS_API.md`

Include OpenAPI/Swagger spec.
```

### Language Validator Documentation

```markdown
@copilot Document new language validators

For each language (Java, Swift, Ruby, PHP), create:
- Validation rules explained
- Configuration file structure
- Common issues and fixes
- Example valid/invalid configs
- Troubleshooting guide

Create:
- docs/development/JAVA_VALIDATION.md
- docs/development/SWIFT_VALIDATION.md
- docs/development/RUBY_VALIDATION.md
- docs/development/PHP_VALIDATION.md
```

---

## Completion Prompt

```markdown
@copilot Finalize Phase 3 implementation

Tasks:
1. Run final code review using code_review tool
2. Address any remaining issues
3. Update PR description with Phase 3 deliverables
4. Create comprehensive completion summary
5. Update cognitive brain with Phase 3 learnings
6. Post follow-up comment on PR
7. Mark Phase 3 as complete

Success Criteria:
- All tests passing
- Code review clean
- Documentation complete
- Cognitive brain updated
- PR ready for merge

Generate final summary report.
```

---

## Usage Notes

### For Autonomous Execution
1. Start with Master Prompt for full Phase 3
2. Or use Session prompts for incremental execution
3. Use component prompts for focused work
4. Use troubleshooting prompts if issues arise

### For Human-Guided Execution
1. Review planset first
2. Execute sessions one at a time
3. Validate each session before proceeding
4. Use component prompts for specific tasks

### For Testing/Validation
1. Use validation prompts after implementation
2. Run unit tests first, then integration tests
3. Use troubleshooting prompts if failures occur
4. Iterate until all tests pass

---

## Success Indicators

✅ All deliverables created
✅ Tests passing (unit + integration)
✅ Documentation complete
✅ Cognitive brain updated
✅ Agents deployed
✅ PR description updated
✅ Follow-up comment posted

---

**Document Status**: ✅ COMPLETE
**Ready for Use**: YES
**Version**: 1.0.0
**Date**: 2026-01-22
