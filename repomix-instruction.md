# _codex_ Repository Architecture & Global Coding Guidelines

## Project Overview

**_codex_** is an advanced AI-powered development automation platform featuring:
- Autonomous code remediation with ML-based fix generation
- Real-time CI/CD monitoring and diagnostic capabilities
- ML-based threat detection and security scanning
- Self-healing workflows with cognitive decision-making
- Comprehensive test automation with deterministic execution

## Architecture Philosophy

### Core Principles

1. **Cognitive Brain Architecture**: Self-healing, self-learning system that evolves
2. **Security First**: Multi-layer defense, no secrets in code, proactive scanning
3. **Deterministic Execution**: Reproducible builds, tests, and workflows
4. **Modular Design**: Clear boundaries, dependency injection, testability
5. **Continuous Improvement**: Metrics-driven evolution, automated optimization

### System Components

```
_codex_/
├── tools/auto_remediation/     # Intelligent fix generation & PR automation
├── monitoring/                 # Real-time CI/CD & security metrics
├── services/msp_gateway/       # API gateway with CORS security
├── .github/agents/             # Custom GitHub Copilot agents
│   ├── ci-diagnostic-agent/    # CI failure analysis
│   └── ml-threat-detector/     # ML-based vulnerability detection
├── src/codex/                  # Core Python codebase
├── tests/                      # Comprehensive test suite
└── rust_swarm/                 # Rust performance-critical components
```

## Global Coding Guidelines

### Python Code Standards

**Formatting & Style**:
- Black formatter (line length: 100)
- Ruff linter with strict settings
- isort for import organization
- Type hints required for all public APIs
- Docstrings in Google style

**Example**:
```python
def analyze_vulnerability(
    code: str,
    patterns: list[str],
    confidence_threshold: float = 0.8
) -> tuple[bool, float]:
    """Analyze code for vulnerability patterns.
    
    Args:
        code: Source code to analyze
        patterns: List of vulnerability patterns
        confidence_threshold: Minimum confidence for detection
    
    Returns:
        Tuple of (is_vulnerable, confidence_score)
    
    Raises:
        ValueError: If code is empty or patterns invalid
    """
    # Implementation
```

**Security Best Practices**:
- Never hardcode credentials or secrets
- Use environment variables for sensitive data
- Validate all inputs before processing
- Use parameterized queries (no string interpolation for SQL)
- Sanitize user inputs to prevent XSS/injection

**Error Handling**:
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # Graceful degradation or raise
    raise
```

### Rust Code Standards

**Formatting & Linting**:
- cargo fmt for formatting
- cargo clippy with `deny(warnings)`
- Explicit error handling (avoid `.unwrap()` in production)
- Documentation comments (`///`) for public items

**Example**:
```rust
/// Analyzes code performance metrics
///
/// # Arguments
/// * `code` - Source code to analyze
/// * `threshold` - Performance threshold in ms
///
/// # Returns
/// Performance score (0.0-1.0)
///
/// # Errors
/// Returns `AnalysisError` if code parsing fails
pub fn analyze_performance(
    code: &str,
    threshold: f64
) -> Result<f64, AnalysisError> {
    // Implementation
}
```

### YAML (Workflows & Configuration)

**GitHub Actions**:
- 2-space indentation
- Descriptive job and step names
- Comments for complex logic
- Secrets via GitHub Secrets only (never hardcoded)
- Use checkout@v4, setup-python@v5, etc. (latest stable)

**Example**:
```yaml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:

permissions:
  contents: read
  security-events: write

jobs:
  scan:
    name: Run Security Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run CodeQL
        uses: github/codeql-action/analyze@v2
        with:
          languages: python, javascript
```

## Key Design Patterns

### 1. Auto-Remediation Pattern
```
Detection → Analysis → Fix Generation → Verification → PR Creation
```
- Use AST parsing for precise code modification
- Validate fixes before and after application
- Generate comprehensive test coverage for fixes
- Include rollback procedures

### 2. CI Diagnostic Pattern
```
Log Collection → Pattern Matching → Root Cause Analysis → Remediation Suggestion
```
- Analyze workflow logs for known failure patterns
- Calculate confidence scores for diagnoses
- Suggest auto-fixes for common issues
- Learn from historical failures

### 3. Monitoring Pattern
```
Metrics Collection → Aggregation → Visualization → Alerting
```
- Collect from GitHub APIs (workflows, security, releases)
- Store time-series data for trending
- Real-time dashboard updates
- Threshold-based alerting

### 4. Security Scanning Pattern
```
Pre-commit → Static Analysis → Dynamic Analysis → Vulnerability DB Check
```
- Multi-layer scanning (Semgrep, CodeQL, Bandit)
- Custom rules for _codex_-specific patterns
- Automated PR comments for findings
- Block merges on critical vulnerabilities

## Testing Standards

### Test Organization
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Multi-component tests
├── e2e/            # End-to-end workflow tests
└── fixtures/       # Test data and mocks
```

### Test Quality Requirements
- Minimum 85% code coverage
- All tests must be deterministic (use fixed seeds)
- Integration tests for critical paths
- Mocking for external dependencies
- Clear test names describing behavior

**Example**:
```python
def test_fix_generator_handles_sql_injection_with_parameterized_queries():
    """Fix generator should convert string interpolation to parameterized queries."""
    vulnerable_code = 'cursor.execute(f"SELECT * FROM users WHERE id={user_id}")'
    
    fix = generator.generate_fix(vulnerable_code, VulnType.SQL_INJECTION)
    
    assert "execute(" in fix.fixed_code
    assert "?" in fix.fixed_code or "%s" in fix.fixed_code
    assert "f\"" not in fix.fixed_code
    assert fix.confidence > 0.9
```

## Documentation Standards

### Code Documentation
- Docstrings for all public APIs (modules, classes, functions)
- Type hints for function signatures
- Inline comments for complex logic only
- Architecture diagrams in Mermaid format

### File-Level Documentation
- README.md in each major directory
- ARCHITECTURE.md for complex components
- TROUBLESHOOTING.md for operational issues
- SECURITY.md for security-sensitive code

## Git Commit Conventions

**Format**: `<type>(<scope>): <subject>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `docs`: Documentation changes
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `security`: Security improvements

**Examples**:
```
feat(auto-remediation): add AST-based code replacement
fix(ci-diagnostic): handle timeout errors gracefully
security(api): implement rate limiting
docs(architecture): update Phase 10 integration diagram
```

## Performance Considerations

1. **Avoid N+1 Queries**: Batch database/API operations
2. **Cache Aggressively**: Use Redis/in-memory for frequent reads
3. **Lazy Loading**: Load data only when needed
4. **Async Where Possible**: Use asyncio for I/O-bound operations
5. **Profile Before Optimizing**: Use profilers to identify bottlenecks

## Security Checklist

Before committing code, verify:
- [ ] No hardcoded secrets or credentials
- [ ] All inputs validated and sanitized
- [ ] SQL queries use parameterization
- [ ] File operations check paths (no traversal)
- [ ] Authentication/authorization on sensitive endpoints
- [ ] HTTPS/TLS for external communications
- [ ] Secrets detection tools pass (secretlint, detect-secrets)
- [ ] Dependencies scanned for vulnerabilities

## CI/CD Integration

All code must pass:
1. **Linting**: Black, Ruff, cargo fmt, cargo clippy
2. **Type Checking**: mypy for Python
3. **Security Scanning**: Semgrep, CodeQL, Bandit
4. **Tests**: Unit, integration, and E2E
5. **Coverage**: Minimum 85% coverage
6. **Determinism**: Tests produce consistent results

## Critical Paths for AI Analysis

When analyzing this codebase, focus on:

### 1. Security-Critical Components
- `tools/auto_remediation/fix_generator.py` - Fix generation logic
- `services/msp_gateway/app.py` - CORS and authentication
- `.github/workflows/security-*.yml` - Security scanning workflows
- `semgrep_rules/` - Custom security rules

### 2. Performance-Critical Components
- `rust_swarm/` - High-performance Rust code
- `src/codex/ingestion/` - Data processing pipeline
- `monitoring/metrics_collector.py` - Metrics aggregation

### 3. Reliability-Critical Components
- `.github/workflows/determinism.yml` - Deterministic test execution
- `.github/agents/ci-diagnostic-agent/` - CI failure analysis
- `tools/auto_remediation/verifier.py` - Fix verification

### 4. Integration Points
- `monitoring/dashboard_api.py` - Dashboard API
- `services/msp_gateway/` - External API gateway
- `.github/workflows/notebooklm-sync.yml` - Knowledge sync

## AI Architect Analysis Guidelines

### Health Check Protocol

**Step 1: Context Loading**
- Parse XML consolidation
- Establish module hierarchy
- Map inter-module dependencies
- Identify critical data flows

**Step 2: Multi-Pass Analysis**
For each category (Architecture, Security, Performance, Quality, Dependencies):
1. Initial scan for obvious issues
2. Deep dive into flagged components
3. Cross-reference with best practices
4. Generate specific recommendations

**Step 3: Recursive Refinement**
Ask yourself: **"Is that ALL you need to know?"**
- If NO: Perform additional research loops
- If YES: Compile comprehensive report

**Step 4: Report Generation**
Structure findings:
1. Executive Summary (critical issues only)
2. Detailed Findings (by category)
3. Actionable Recommendations (prioritized)
4. Prevention Strategies (long-term)

### Validation Criteria

**Architecture Consistency**:
- No circular dependencies
- No God classes (>500 LOC, >10 dependencies)
- Clear modular boundaries
- Proper dependency injection

**Security Posture**:
- No unvalidated inputs
- No injection vulnerabilities
- Proper authentication/authorization
- Secrets managed securely

**Performance & Scalability**:
- No N+1 query patterns
- Efficient algorithms (O(n log n) or better)
- Proper caching strategies
- No memory leaks

**Code Quality**:
- Cyclomatic complexity < 15
- Code duplication < 5%
- Proper error handling
- Comprehensive logging

**Test Coverage**:
- Coverage > 85%
- Tests are deterministic
- Critical paths covered
- Integration tests present

## Continuous Improvement

This codebase follows a cognitive brain model:
- Self-healing capabilities
- Continuous learning from failures
- Metrics-driven optimization
- Automated improvement suggestions

**Current Health Score**: 99/100
- Knowledge Synthesis: 99/100
- Self-Healing: 99/100
- Code Quality: 98/100
- CI Reliability: 98/100

## Questions for AI Analysis

When analyzing this codebase, consider:

1. **Is the modular structure optimal?** Can we reduce coupling further?
2. **Are there hidden security vulnerabilities?** Check for subtle injection risks
3. **Can performance be improved?** Identify algorithmic bottlenecks
4. **Is the code maintainable?** Check complexity and duplication
5. **Are dependencies healthy?** Check for outdated or vulnerable packages
6. **Is the architecture sustainable?** Can it scale to 10x current load?
7. **Are tests comprehensive?** Do they cover edge cases and error paths?

## Conclusion

This repository represents a mature, production-ready AI-powered development platform with advanced self-healing capabilities. Maintain high standards for code quality, security, and performance. Always validate changes against the cognitive brain health metrics.

**Remember**: "Is that ALL you need to know?" - Keep asking until you've uncovered all logic bottlenecks and architectural concerns.

---

*For detailed implementation guidance, see:*
- `PHASE_10_MASTER_INTEGRATION_PLANSET.md`
- `COGNITIVE_BRAIN_STATUS_V3.md`
- `AGENTS.md`
