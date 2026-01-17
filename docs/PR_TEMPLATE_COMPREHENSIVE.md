# Comprehensive Pull Request Template - Checkbox Checklist Style

> **Version:** 2.0.0  
> **Generated:** 2025-11-17  
> **Purpose:** Complete PR checklist with all capability enhancements and quality gates

---

## 📋 PR OVERVIEW

### Basic Information
- [ ] **PR Title**: Clear, descriptive title following convention: `[Type]: Brief description`
- [ ] **Linked Issue(s)**: All related issues are linked (fixes #XXX, closes #XXX, relates to #XXX)
- [ ] **PR Type**: Select one or more:
  - [ ] 🐛 Bug Fix
  - [ ] ✨ New Feature
  - [ ] 🔧 Code Refactor
  - [ ] 📝 Documentation
  - [ ] ⚡ Performance Improvement
  - [ ] 🧪 Tests
  - [ ] 🔒 Security Fix
  - [ ] 🎨 Code Style/Formatting
  - [ ] 📦 Dependency Update
  - [ ] 🏗️ Infrastructure/Build

### Scope Summary
- [ ] **S-IDs Listed**: All affected system IDs documented (e.g., Retrieval, Inference, Metrics)
- [ ] **Areas Listed**: All affected areas documented (e.g., Vector stores, ML serving, CLI)
- [ ] **Impact Assessment**: High/Medium/Low impact documented for each area

---

## ⚠️ REQUIRED SAFETY CONFIRMATIONS

**These checkboxes MUST be confirmed before merge:**

### Network & Security
- [ ] **Network Safety Acknowledgment** - I confirm NO network operations (web scraping, API calls, external fetches) are performed by this PR
- [ ] **Offline Mode Confirmation** - I confirm all audit and test operations run in strict offline mode
- [ ] **No Credentials Committed** - I confirm no API keys, passwords, tokens, or secrets are committed
- [ ] **Security Scan Passed** - CodeQL or equivalent security scan passed with 0 vulnerabilities

### Data Safety
- [ ] **No PII Exposure** - No personally identifiable information is exposed or logged
- [ ] **Data Privacy Compliant** - Changes comply with data privacy requirements
- [ ] **No Data Loss Risk** - Changes do not risk data loss or corruption

### Code Quality
- [ ] **Breaking Changes Documented** - All breaking changes are documented (or N/A if none)
- [ ] **Backward Compatibility** - Changes are backward compatible OR migration path documented
- [ ] **No Debug Code** - No debug print statements, commented code, or temporary hacks remain

---

## 🧪 TESTING REQUIREMENTS

### Test Coverage
- [ ] **Unit Tests Added** - New unit tests added for all new functionality
- [ ] **Integration Tests Added** - Integration tests added for cross-component functionality
- [ ] **Tests Pass Locally** - All tests pass locally (`pytest` or equivalent)
- [ ] **Test Coverage >85%** - New code has >85% test coverage (run coverage report)
- [ ] **Edge Cases Tested** - Edge cases and error conditions are tested

### Test Quality
- [ ] **Test Names Descriptive** - All test names clearly describe what they test
- [ ] **Tests Are Independent** - Tests can run independently in any order
- [ ] **No Flaky Tests** - Tests are deterministic and not timing-dependent
- [ ] **Performance Tests** (if applicable) - Performance benchmarks added for optimization PRs

### Validation
- [ ] **Linting Passed** - `ruff check`, `black --check`, or equivalent passed
- [ ] **Type Checking Passed** - `mypy` or equivalent passed
- [ ] **Pre-commit Hooks Passed** - All pre-commit hooks passed
- [ ] **CI/CD Checks Passing** - All CI/CD pipeline checks are passing

---

## 📝 DOCUMENTATION REQUIREMENTS

### Code Documentation
- [ ] **Docstrings Added** - All new functions/classes have comprehensive docstrings
- [ ] **Docstring Format** - Docstrings follow repository convention (Google, NumPy, etc.)
- [ ] **Type Hints Added** - All functions have complete type hints
- [ ] **Inline Comments** - Complex logic has explanatory inline comments
- [ ] **TODO/FIXME Resolved** - No unresolved TODO or FIXME comments (or tracked in issues)

### User Documentation
- [ ] **README Updated** (if applicable) - README reflects new features/changes
- [ ] **User Guide Updated** (if applicable) - User-facing documentation updated
- [ ] **API Documentation Updated** (if applicable) - API docs updated for new/changed endpoints
- [ ] **Examples Added** (if applicable) - Code examples added for new features
- [ ] **Migration Guide** (if breaking changes) - Migration guide provided for breaking changes

### Technical Documentation
- [ ] **Architecture Docs Updated** (if applicable) - Architecture diagrams/docs updated
- [ ] **ADR Created** (if architectural change) - Architecture Decision Record created in `docs/arch/`
- [ ] **CHANGELOG Updated** - CHANGELOG.md updated with user-facing changes
- [ ] **Configuration Documented** - New configuration options documented

---

## 🚀 FEATURE-SPECIFIC REQUIREMENTS

### For New Features
- [ ] **Feature Complete** - Feature is complete and ready for production use
- [ ] **Feature Flags** (if applicable) - Feature flags implemented for gradual rollout
- [ ] **Performance Validated** - Performance impact measured and acceptable
- [ ] **Error Handling** - Comprehensive error handling implemented
- [ ] **Logging Added** - Appropriate logging added at INFO/DEBUG levels
- [ ] **Metrics/Telemetry** (if applicable) - Metrics collection implemented

### For Bug Fixes
- [ ] **Root Cause Identified** - Root cause of bug is identified and documented
- [ ] **Regression Test Added** - Test added to prevent regression
- [ ] **Related Issues Checked** - Related issues reviewed for similar problems
- [ ] **Fix Validated** - Fix validated in environment where bug was found

### For Performance Improvements
- [ ] **Benchmarks Provided** - Before/after benchmarks provided
- [ ] **Performance Gain Quantified** - Performance improvement quantified (e.g., 2x faster)
- [ ] **No Regressions** - No performance regressions in other areas
- [ ] **Resource Usage Checked** - Memory/CPU usage impact assessed

### For Refactoring
- [ ] **Behavior Unchanged** - External behavior is unchanged (verified by tests)
- [ ] **No New Features** - Refactoring does not introduce new features
- [ ] **Code Simplified** - Code complexity reduced (measured if possible)
- [ ] **Test Coverage Maintained** - Test coverage maintained or improved

---

## 🔧 IMPLEMENTATION QUALITY

### Code Quality
- [ ] **Follows Style Guide** - Code follows repository style guidelines
- [ ] **Self-Review Complete** - I have performed a thorough self-review
- [ ] **No Code Duplication** - Duplicated code extracted to reusable functions
- [ ] **Error Messages Clear** - Error messages are clear and actionable
- [ ] **Constants Named** - Magic numbers replaced with named constants

### Design Quality
- [ ] **Single Responsibility** - Functions/classes have single, clear responsibility
- [ ] **DRY Principle** - Don't Repeat Yourself principle followed
- [ ] **SOLID Principles** - SOLID principles followed (where applicable)
- [ ] **Minimal Interface** - Public APIs are minimal and well-designed
- [ ] **Future-Proof** - Design accommodates likely future changes

### Dependencies
- [ ] **Dependencies Justified** - New dependencies are necessary and justified
- [ ] **Dependencies Secure** - New dependencies scanned for vulnerabilities
- [ ] **Dependency Versions Pinned** - Dependency versions specified in requirements
- [ ] **License Compatible** - New dependencies have compatible licenses

---

## 📋 CAPABILITY-SPECIFIC CHECKLISTS

### A) Inference Serving & Model Management
**Check if this PR modifies inference serving, model loading, or embedding generation:**

#### Basic Inference Features
- [ ] **ModelConfig Implementation** - ModelConfig class properly configured with env vars/dict support
- [ ] **Multiple Backends Supported** - Stub, HuggingFace Transformers, and ONNX Runtime tested
- [ ] **Model Loading** - Models load successfully from configuration
- [ ] **Model Unloading** - Models properly unloaded to free resources
- [ ] **Error Handling** - Graceful error handling with ModelLoadError exception
- [ ] **Health Checks** - Health check endpoints return accurate model status
- [ ] **Device Management** - CPU/GPU device selection working correctly

#### Embedding Generation
- [ ] **Embed Endpoint** - POST /embed endpoint functional
- [ ] **L2 Normalization** - Embeddings are L2-normalized for cosine similarity
- [ ] **Batch Embedding** - Batch embedding support works correctly
- [ ] **Model-Specific Logic** - Stub, HuggingFace, and ONNX backends generate embeddings correctly
- [ ] **Output Format** - Standardized output format (text, embeddings, dimension, inference_time_ms)
- [ ] **Numpy Array Support** - Returns numpy arrays as expected

#### Prediction & Inference
- [ ] **Standardized Input** - Accepts List[str] as standardized input
- [ ] **Standardized Output** - Returns prediction with text, label, score, model fields
- [ ] **Rate Limiting** - Rate limiter integration working (if enabled)
- [ ] **Input Validation** - Batch size and length constraints enforced
- [ ] **Error Responses** - Clear error messages for invalid inputs

#### Configuration & Monitoring
- [ ] **Environment Variables** - CODEX_MODEL_NAME, CODEX_MODEL_TYPE, CODEX_MODEL_PATH work
- [ ] **Config Dictionary** - Dictionary-based configuration works
- [ ] **from_env() Factory** - ModelConfig.from_env() creates valid configuration
- [ ] **Configuration Validation** - Invalid configurations are rejected with clear errors
- [ ] **Monitoring** - Model type, device, and error tracking in health checks

---

### B) Vector Store & Retrieval
**Check if this PR modifies vector stores, indexing, search, or retrieval:**

#### VectorStore Interface & Base
- [ ] **Interface Compliance** - Implementation follows VectorStore abstract base class
- [ ] **9 Required Methods** - add(), search(), delete(), get(), count(), clear(), save(), load(), health_check()
- [ ] **Custom Exceptions** - DimensionMismatchError, VectorNotFoundError, IndexNotLoadedError used correctly
- [ ] **Type Hints** - All methods have proper type hints
- [ ] **Docstrings** - All methods documented with usage examples

#### FAISS Store Implementation
- [ ] **CRUD Operations** - Create, Read, Update, Delete operations tested
- [ ] **ID Management** - Auto-generated UUID and custom ID support working
- [ ] **Metadata Storage** - Arbitrary JSON-serializable metadata stored and retrieved
- [ ] **Metadata Persistence** - Metadata survives save/load cycles
- [ ] **Dimension Validation** - Vector dimension validation prevents mismatches
- [ ] **Safety Limits** - max_vectors, max_dimension, max_query_batch enforced
- [ ] **L2 Normalization** - Vectors normalized for cosine similarity
- [ ] **Checksum Validation** - Save/load includes checksums for data integrity

#### Vector Operations
- [ ] **Add Vectors** - Single and batch add operations work
- [ ] **Search Vectors** - k-NN search returns correct results
- [ ] **Delete Vectors** - Deletion by ID works correctly
- [ ] **Get Vectors** - Retrieval by ID returns vectors and metadata
- [ ] **Count Vectors** - Accurate count of stored vectors
- [ ] **Clear Index** - Complete index clearing works
- [ ] **Index Persistence** - Save/load preserves all data
- [ ] **ID Tracking** - ID mapping persists across save/load

#### Metadata Filtering (MongoDB-style)
- [ ] **Equality Operator** - `{"field": "value"}` filters work
- [ ] **Comparison Operators** - gt, gte, lt, lte, ne work correctly
- [ ] **In/Nin Operators** - in and nin array membership work
- [ ] **Exists Operator** - exists checks for field presence
- [ ] **AND Logic** - `{"$and": [...]}` combines filters correctly
- [ ] **OR Logic** - `{"$or": [...]}` combines filters correctly
- [ ] **Nested Filters** - Complex nested filter combinations work
- [ ] **Fetch Multiplier** - Automatic 3x/5x/10x fetch based on filter complexity
- [ ] **Score Ordering** - Results maintain score ordering after filtering
- [ ] **Empty Results** - Empty results and no matches handled gracefully
- [ ] **Optional Parameter** - filters parameter is optional (backward compatible)

#### Search & Retrieval
- [ ] **k-NN Search** - k-nearest neighbor search accurate
- [ ] **Configurable k** - k parameter controls result count
- [ ] **Result Format** - Returns IDs, scores, and metadata
- [ ] **Query Validation** - Invalid queries rejected with clear errors
- [ ] **Batch Queries** - Multiple queries processed efficiently

---

### C) Duplication Detection & Code Metrics
**Check if this PR modifies duplication detection, code quality metrics, or analysis:**

#### Detection Engine
- [ ] **Token-Based Detection** - pylint integration detects Type-1 clones
- [ ] **DuplicateBlock Class** - Proper hash, file paths, line ranges, severity
- [ ] **DuplicationRatio Class** - ratio, total_lines, duplicate_lines, files_with_duplicates, blocks
- [ ] **Configurable Threshold** - min_lines parameter works (default: 4)
- [ ] **Trivial Filtering** - Imports, docstrings, empty classes filtered out
- [ ] **Severity Levels** - Low/medium/high severity determination correct
- [ ] **Overlap Handling** - Set-based overlap calculation accurate
- [ ] **detect_duplicates()** - Convenience function works correctly

#### Metric Storage
- [ ] **Dual Storage** - Both JSON and SQLite storage working
- [ ] **JSON Format** - Timestamped JSON files with summary statistics
- [ ] **SQLite Schema** - metrics, duplicate_blocks, occurrences tables created
- [ ] **Transaction Safety** - Writes use transactions for integrity
- [ ] **Historical Queries** - Query by time range works
- [ ] **Load Latest** - Retrieve most recent metrics
- [ ] **Git SHA Tracking** - Commit SHA stored with metrics
- [ ] **Summary Statistics** - Block count, average size calculated

#### CLI Commands
- [ ] **codex duplication check** - Scans, calculates, validates threshold
- [ ] **Check Exit Codes** - Returns 0 on pass, 1 on threshold exceeded
- [ ] **Check --threshold** - Custom threshold parameter works
- [ ] **Check --min-lines** - Custom min_lines parameter works
- [ ] **Check --output** - JSON output file written correctly
- [ ] **codex duplication report** - Generates detailed reports
- [ ] **Report --format** - JSON and text formats work
- [ ] **Report --save-db** - Optional database storage works
- [ ] **Report --output** - Report file written correctly
- [ ] **codex duplication compare** - Baseline comparison works
- [ ] **Compare --baseline** - Baseline file loaded correctly
- [ ] **Compare --threshold-increase** - Threshold increase validation works
- [ ] **Compare Exit Codes** - Returns 1 if increase exceeds threshold
- [ ] **Colorized Output** - CLI output uses colors and emojis
- [ ] **Progress Indicators** - Progress shown during operations

#### Integration & Workflows
- [ ] **Full Workflow** - detect → calculate → store → report workflow tested
- [ ] **Baseline Workflow** - Create baseline → run check → compare workflow tested
- [ ] **CI/CD Integration** - Exit codes enable CI/CD gating
- [ ] **Metric Evolution** - Historical tracking enables trend analysis

---

### D) Performance Optimizations & Resilience
**Check if this PR modifies batching, caching, optimization, or resilience patterns:**

#### Request Batching
- [ ] **BatchingMiddleware** - Async batch accumulation working
- [ ] **max_batch_size** - Configurable batch size (default: 32) works
- [ ] **max_wait_time** - Configurable wait time (default: 100ms) works
- [ ] **Batch on Size** - Automatic flush when batch size reached
- [ ] **Batch on Timeout** - Automatic flush after timeout
- [ ] **Thread-Safe Queue** - Lock synchronization prevents race conditions
- [ ] **Async/Await** - asyncio.Future coordination works
- [ ] **Graceful Shutdown** - Queue flushing on shutdown
- [ ] **Error Handling** - Individual request errors don't break batch
- [ ] **PerformanceMetrics** - Latency and throughput tracked correctly
- [ ] **Percentiles** - p50, p95, p99 latency percentiles accurate
- [ ] **Throughput** - Requests/sec calculation correct
- [ ] **Batch Statistics** - Batch size stats collected
- [ ] **Memory Bounded** - Auto-trim old data (last 10K latencies)

#### Response Caching
- [ ] **LRU Cache** - OrderedDict-based LRU eviction works
- [ ] **TTL Support** - Time-to-live expiration works
- [ ] **Content-Based Keys** - SHA256 hash of input used as key
- [ ] **Deterministic Keys** - Same content → same key regardless of order
- [ ] **max_size** - Memory-bounded cache size enforced
- [ ] **Thread-Safe** - Lock prevents race conditions
- [ ] **CacheMetrics** - Hit/miss/eviction tracking accurate
- [ ] **Hit Rate** - Hit rate calculation correct
- [ ] **Memory Utilization** - Current size / max size tracking
- [ ] **Manual Operations** - put(), get(), clear(), remove_expired() work
- [ ] **Complex Types** - Lists, nested dicts cached correctly
- [ ] **Cache Invalidation** - Expired entries removed correctly

#### Retrieval Optimizations
- [ ] **OptimizedVectorStore** - Wrapper works with any VectorStore backend
- [ ] **Query Caching** - Search results cached correctly
- [ ] **Cache Invalidation** - Cache cleared on add/delete operations
- [ ] **Lazy Loading** - Deferred initialization works
- [ ] **Batch Queries** - Multiple queries processed efficiently
- [ ] **Method Delegation** - Delegates to underlying store correctly
- [ ] **RetrievalMetrics** - Search latency tracked
- [ ] **Query Throughput** - Queries/sec calculated
- [ ] **Index Size** - Index size tracked
- [ ] **Memory-Mapped Index** - Large index detection and recommendation
- [ ] **Pre-computation** - Index structure pre-loading works
- [ ] **Combined Metrics** - Retrieval + cache metrics merged

#### Resilience Patterns
- [ ] **CircuitBreaker** - CLOSED/OPEN/HALF_OPEN states work
- [ ] **Failure Threshold** - Opens after N failures
- [ ] **Success Threshold** - Half-open → closed after N successes
- [ ] **Timeout** - Auto-recovery after timeout period
- [ ] **Manual Reset** - reset() method works
- [ ] **Thread-Safe** - State transitions thread-safe
- [ ] **retry_with_backoff** - Exponential backoff works
- [ ] **Max Retries** - Retry limit enforced
- [ ] **Max Delay** - Maximum delay cap enforced
- [ ] **Selective Retry** - Only specified exceptions retried
- [ ] **FallbackHandler** - Primary → fallback transition works
- [ ] **Cache Fallback** - Fallback to cache on primary failure
- [ ] **Custom Fallback** - Custom fallback functions work
- [ ] **Graceful Degradation** - Service degrades gracefully

#### Performance Validation
- [ ] **Latency Reduction** - Measured latency improvement (target: 50-90% for cache, 30-70% for retrieval)
- [ ] **Throughput Increase** - Measured throughput improvement (target: 2-5x for batching)
- [ ] **Cache Hit Rate** - Measured cache hit rate (target: >60% for repeated queries)
- [ ] **Resource Usage** - Memory/CPU usage acceptable
- [ ] **No Regressions** - No performance regressions in uncached paths
- [ ] **Stress Tested** - High load scenarios tested
- [ ] **Concurrent Requests** - Concurrent request handling tested

---

### E) CLI & Command-Line Interface
**Check if this PR adds or modifies CLI commands:**

#### General CLI
- [ ] **Click Integration** - Uses Click framework consistently
- [ ] **Command Groups** - Commands organized in logical groups
- [ ] **Help Text** - All commands have --help documentation
- [ ] **Parameter Validation** - Invalid parameters rejected with clear errors
- [ ] **Exit Codes** - Correct exit codes (0 success, 1 failure)
- [ ] **Error Messages** - User-friendly error messages
- [ ] **Progress Indicators** - Long-running operations show progress
- [ ] **Colorized Output** - Uses colors/emojis appropriately
- [ ] **Dry Run Support** (if applicable) - --dry-run option works

#### Duplication CLI Commands
- [ ] **codex duplication check** - Command exists and functional
- [ ] **codex duplication report** - Command exists and functional
- [ ] **codex duplication compare** - Command exists and functional
- [ ] **Command Options** - All command options work correctly
- [ ] **Output Formats** - JSON and text output formats work
- [ ] **File I/O** - Input/output files handled correctly

---

### F) Documentation & Guides
**Check if this PR includes documentation:**

#### User Guides Created/Updated
- [ ] **INFERENCE_SERVING_GUIDE.md** - Comprehensive guide (12KB) with examples
- [ ] **VECTOR_STORE_INTEGRATION_GUIDE.md** - Complete guide (36KB) with API reference
- [ ] **DUPLICATION_METRICS_GUIDE.md** - Full guide (15KB) with CLI examples
- [ ] **PERFORMANCE_OPTIMIZATION_GUIDE.md** - Detailed guide (14.5KB) with benchmarks
- [ ] **Quick Start Sections** - Each guide has quick start
- [ ] **Configuration Examples** - Environment variables and config examples
- [ ] **Code Examples** - Working code examples (20+ per guide)
- [ ] **API Reference** - Complete API documentation
- [ ] **Troubleshooting** - Troubleshooting sections included
- [ ] **Best Practices** - Best practices documented

#### Technical Documentation
- [ ] **ACCEPTANCE_CRITERIA_VERIFICATION.md** - Research and verification (30KB)
- [ ] **NEXT_COPILOT_PROMPT.md** - Roadmap and future work (13KB)
- [ ] **Architecture Diagrams** (if applicable) - Diagrams updated
- [ ] **ADR Documents** (if architectural changes) - ADRs created

#### Code Documentation
- [ ] **Module Docstrings** - All modules have docstrings
- [ ] **Class Docstrings** - All classes documented
- [ ] **Method Docstrings** - All public methods documented
- [ ] **Parameter Documentation** - All parameters documented with types
- [ ] **Return Documentation** - Return values documented
- [ ] **Exception Documentation** - Exceptions documented
- [ ] **Example Usage** - Examples in docstrings

---

### G) Integration & End-to-End Workflows
**Check if this PR includes integration tests or workflows:**

#### Inference + Vector Store Integration
- [ ] **Embed + Index** - Generate embeddings and index in vector store
- [ ] **Search + Filter** - Search with metadata filtering
- [ ] **Model + Cache** - Model inference with response caching
- [ ] **Batch + Store** - Batch embedding and vector storage

#### Duplication + CI/CD Integration
- [ ] **Check in Pipeline** - Duplication check runs in CI/CD
- [ ] **Baseline Comparison** - Compare against baseline in pipeline
- [ ] **Report Generation** - Generate reports in pipeline
- [ ] **Threshold Gating** - Pipeline fails on threshold exceeded

#### Performance Integration
- [ ] **Batching + Caching** - Request batching with response cache
- [ ] **Retrieval + Optimization** - Optimized vector store with query cache
- [ ] **Circuit Breaker + Retry** - Resilience patterns work together
- [ ] **End-to-End Performance** - Full stack performance tested

---

### H) Database & Storage
**Check if this PR modifies database schemas or storage:**

#### SQLite Storage
- [ ] **Schema Creation** - Tables created correctly
- [ ] **Indexes** - Appropriate indexes created
- [ ] **Transactions** - Transaction-based writes work
- [ ] **Queries** - All queries return correct results
- [ ] **Connection Pooling** (if enabled) - Pool management works
- [ ] **Migration** (if schema changed) - Migration path documented

#### JSON Storage
- [ ] **File Format** - JSON files well-formatted
- [ ] **Timestamps** - Timestamps included in all records
- [ ] **Atomicity** - File writes are atomic
- [ ] **Rotation** (if applicable) - Old files rotated/archived

#### Storage Integration
- [ ] **Dual Storage** - JSON and SQLite stay in sync
- [ ] **Storage Location** - Files stored in correct location (.codex/metrics/)
- [ ] **Permissions** - File permissions correct
- [ ] **Cleanup** - Old/temporary files cleaned up

---

### I) Configuration & Environment
**Check if this PR adds configuration options:**

#### Environment Variables
- [ ] **Variables Documented** - All new env vars documented
- [ ] **Default Values** - Sensible defaults provided
- [ ] **Validation** - Invalid values rejected
- [ ] **Examples** - .env.example updated

#### Configuration Files
- [ ] **Config Format** - JSON/YAML/TOML format valid
- [ ] **Config Schema** - Schema documented
- [ ] **Config Validation** - Invalid configs rejected
- [ ] **Config Examples** - Example configs provided

#### Hydra Configuration (if applicable)
- [ ] **Hydra Configs** - Hydra config files updated
- [ ] **Config Groups** - Organized in config groups
- [ ] **Overrides** - Override mechanism works

---

### J) Error Handling & Validation
**Check if this PR includes robust error handling:**

#### Exception Handling
- [ ] **Custom Exceptions** - Domain-specific exceptions defined
- [ ] **Exception Hierarchy** - Exceptions properly organized
- [ ] **Error Messages** - Clear, actionable error messages
- [ ] **Stack Traces** - Stack traces preserved for debugging
- [ ] **Logging** - Errors logged appropriately

#### Input Validation
- [ ] **Type Validation** - Input types validated
- [ ] **Range Validation** - Numeric ranges validated
- [ ] **Format Validation** - String formats validated
- [ ] **Required Fields** - Required fields enforced
- [ ] **Validation Errors** - Validation errors clear and helpful

#### Edge Cases
- [ ] **Empty Input** - Empty input handled
- [ ] **Null/None** - Null/None values handled
- [ ] **Boundary Values** - Min/max values tested
- [ ] **Unicode** - Unicode input handled correctly
- [ ] **Large Input** - Large input handled (or rejected with clear limit)

---

### K) Metrics & Monitoring
**Check if this PR includes metrics collection:**

#### Performance Metrics
- [ ] **PerformanceMetrics Class** - Latency, throughput tracking
- [ ] **RetrievalMetrics Class** - Search latency, index size tracking
- [ ] **CacheMetrics Class** - Hit rate, eviction tracking
- [ ] **Export to Dict** - Metrics exportable to dictionary/JSON

#### Business Metrics
- [ ] **Usage Metrics** - API call counts, user actions
- [ ] **Quality Metrics** - Duplication ratio, code quality scores
- [ ] **Health Metrics** - Service health, model status

#### Monitoring Integration
- [ ] **Prometheus** (if applicable) - Prometheus metrics exposed
- [ ] **Grafana** (if applicable) - Grafana dashboards updated
- [ ] **Logging** - Structured logging for metrics

---

## 🏗️ INFRASTRUCTURE & BUILD

### Build System
- [ ] **Build Passes** - Build system completes successfully
- [ ] **Build Warnings** - No new build warnings introduced
- [ ] **Build Time** - Build time increase is acceptable (if any)
- [ ] **Artifacts Validated** - Build artifacts validated for correctness

### CI/CD Pipeline
- [ ] **Pipeline Passes** - All CI/CD pipeline stages pass
- [ ] **No Skipped Tests** - No tests skipped without justification
- [ ] **Deployment Safe** - Changes are safe to deploy
- [ ] **Rollback Plan** - Rollback plan documented for risky changes

### Environment
- [ ] **Environment Variables Documented** - New environment variables documented
- [ ] **Configuration Examples** - Configuration examples provided
- [ ] **Docker Builds** (if applicable) - Docker images build successfully
- [ ] **Compatibility Tested** - Compatibility with target environments tested

---

## 🔒 SECURITY CONSIDERATIONS

### Security Scanning
- [ ] **CodeQL Passed** - CodeQL security scan passed
- [ ] **Dependency Scan Passed** - Dependency vulnerability scan passed
- [ ] **SAST Passed** - Static Application Security Testing passed
- [ ] **Secrets Scan Passed** - No secrets detected in code

### Security Best Practices
- [ ] **Input Validation** - All user inputs validated and sanitized
- [ ] **Output Encoding** - All outputs properly encoded
- [ ] **SQL Injection Prevention** - SQL queries use parameterized statements
- [ ] **XSS Prevention** - XSS vulnerabilities prevented
- [ ] **CSRF Protection** (if web) - CSRF protection implemented
- [ ] **Authentication** (if applicable) - Proper authentication implemented
- [ ] **Authorization** (if applicable) - Proper authorization checks implemented
- [ ] **Rate Limiting** (if applicable) - Rate limiting implemented for APIs

---

## 📊 COMPLIANCE & GOVERNANCE

### Archival Policy Compliance
- [ ] **Archival Policy Followed** - Codebase archival policy followed
- [ ] **Root Folder Organized** - Root folder remains organized
- [ ] **ADR Created** (if files removed/moved) - Architecture Decision Record created
- [ ] **Tombstone Stubs** (if files removed) - Tombstone stubs added for removed files
- [ ] **Evidence Logged** (if archival) - `.codex/evidence/archive_ops.jsonl` updated
- [ ] **Pointer Bundle** (if large removal) - Pointer bundle generated for large removals

### Repository Conventions
- [ ] **Commit Messages** - Commit messages follow conventional commits format
- [ ] **Branch Naming** - Branch name follows convention
- [ ] **PR Size Reasonable** - PR is reasonably sized (ideally <500 lines changed)
- [ ] **Single Concern** - PR addresses a single concern/feature

### Code Ownership
- [ ] **Code Owners Notified** - Relevant code owners notified for review
- [ ] **Cross-Team Dependencies** - Cross-team dependencies identified
- [ ] **Stakeholders Informed** - Relevant stakeholders informed of changes

---

## 🎯 ACCEPTANCE CRITERIA

### Functional Acceptance
- [ ] **All Requirements Met** - All acceptance criteria from issue/spec met
- [ ] **User Stories Complete** - All user stories implemented and tested
- [ ] **Demo Ready** - Feature can be demoed successfully
- [ ] **QA Approved** (if applicable) - QA team approved the changes

### Technical Acceptance
- [ ] **Code Review Approved** - Code review completed and approved
- [ ] **Architecture Review** (if major change) - Architecture review completed
- [ ] **Performance Review** (if optimization) - Performance gains validated
- [ ] **Security Review** (if security-sensitive) - Security review completed

### Documentation Acceptance
- [ ] **Documentation Complete** - All required documentation complete
- [ ] **Documentation Reviewed** - Documentation reviewed for accuracy
- [ ] **Examples Validated** - Code examples tested and working

---

## 🚦 READINESS CHECKLIST

### Pre-Merge Checklist
- [ ] **All Checkboxes Reviewed** - All applicable checkboxes in this template reviewed
- [ ] **All Required Checks Pass** - All required checks (⚠️ sections) pass
- [ ] **Approvals Received** - Required number of approvals received
- [ ] **Conflicts Resolved** - No merge conflicts with target branch
- [ ] **Rebase Complete** (if required) - Branch rebased on latest target branch

### Post-Merge Checklist
- [ ] **Deployment Monitored** - Deployment monitored for issues
- [ ] **Metrics Validated** - Key metrics validated post-deployment
- [ ] **Documentation Published** - Documentation published/updated
- [ ] **Team Notified** - Team notified of changes
- [ ] **Issue Closed** - Related issues closed/updated

---

## 📝 ADDITIONAL NOTES

### Summary of Changes
**Provide a concise summary of what changed and why:**

[Your summary here]

### Testing Strategy
**Describe your testing approach:**

[Your testing strategy here]

### Performance Impact
**Describe any performance impact (positive or negative):**

[Performance impact description here]

### Breaking Changes
**List any breaking changes and migration steps:**

[Breaking changes and migration here, or "None"]

### Screenshots/Recordings
**For UI changes, provide screenshots or recordings:**

[Screenshots here, or "N/A for backend changes"]

### Deployment Notes
**Any special deployment considerations:**

[Deployment notes here, or "Standard deployment"]

### Rollback Plan
**How to rollback if issues arise:**

[Rollback plan here]

---

## ✅ FINAL VERIFICATION

### Maintainer Verification
**For maintainers only - verify before merge:**

- [ ] **All Required Boxes Checked** - All required checkboxes completed
- [ ] **Code Quality Acceptable** - Code meets quality standards
- [ ] **Tests Comprehensive** - Test coverage is adequate
- [ ] **Documentation Adequate** - Documentation is sufficient
- [ ] **Security Validated** - No security concerns
- [ ] **Performance Acceptable** - Performance impact acceptable
- [ ] **Ready to Merge** - PR is ready to merge

---

**PR Author:** @[username]  
**Date Submitted:** YYYY-MM-DD  
**Target Branch:** [e.g., main, develop]  
**Target Release:** [e.g., v1.2.0]

---

## 📚 REFERENCES

- [Contributing Guidelines](CONTRIBUTING.md)
- [Code Style Guide](./guides/code_style_guide.md)
- [Testing Guidelines](./CONTRIBUTING.md#testing)
- [Security Policy](SECURITY.md)
- [Archival Policy](./agents.md)

---

**Notes for Contributors:**
1. Check all applicable boxes with `[x]`
2. Mark non-applicable items with `[N/A]` and brief explanation
3. Required sections (⚠️) must be completed for all PRs
4. Feature-specific sections only apply to relevant PRs
5. Ask questions in PR comments if checklist items are unclear
6. Update this template if you find gaps or improvements

---

**Template Version:** 2.0.0  
**Last Updated:** 2025-11-17  
**Changelog:** Complete rewrite with comprehensive capability-specific checklists
