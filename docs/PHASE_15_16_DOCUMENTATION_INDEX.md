# Phase 15-16 Documentation Index

> Complete index of all Phase 15-16 documentation, architecture, API, and pattern library resources.

**Last Updated**: 2026-07-11 | **Documentation Health**: 🟢 Verified

---

## Quick Navigation

### For Developers

- **Getting Started**: [Quick Start Guide](./onboarding/QUICK_START.md)
- **API Reference**: [All 11 Endpoints](./API_REFERENCE_PHASE_15_16.md)
- **Code Examples**: [Python & JavaScript](./API_REFERENCE_PHASE_15_16.md#code-examples)
- **Integration**: [SDK & CLI Guide](./cognitive_brain/COGNITIVE_APP_CONNECTION_GUIDE.md)

### For Architects

- **Architecture Overview**: [Phase 15-16 System Design](./ARCHITECTURE_PHASE_15_16.md)
- **Data Flow Diagrams**: [Request/Response Flows](./ARCHITECTURE_PHASE_15_16.md#data-flow)
- **Deployment Guide**: [Container & K8s Setup](./ARCHITECTURE_PHASE_15_16.md#deployment-architecture)

### For DevOps/SRE

- **Pattern Library**: [40+ Patterns for CI/CD](./PATTERN_LIBRARY_GUIDE.md)
- **Performance Patterns**: [Optimization Guide](./PATTERN_LIBRARY_GUIDE.md#3-performance-optimization-patterns-6-patterns)
- **Deployment Patterns**: [Release Procedures](./PATTERN_LIBRARY_GUIDE.md#6-deployment-patterns-4-patterns)

### For Security Team

- **Security Patterns**: [6 Security Patterns](./PATTERN_LIBRARY_GUIDE.md#4-security-patterns-6-patterns)
- **Vulnerability Detection**: [CodeQL Integration](./PATTERN_LIBRARY_GUIDE.md#2-security-pattern-example)
- **Compliance**: [Security Best Practices](./ARCHITECTURE_PHASE_15_16.md#security-considerations)

---

## Documentation Structure

```
docs/
├── ARCHITECTURE_PHASE_15_16.md          📐 System architecture & design
├── API_REFERENCE_PHASE_15_16.md         🔌 11 API endpoints with examples
├── PATTERN_LIBRARY_GUIDE.md             🎯 40+ patterns + CI/CD integration
├── PATTERN_LIBRARY_INDEX.md             📑 Searchable pattern index
│
├── architecture/                        
│   └── ARCHITECTURE_CONSOLIDATED.md     
│
├── api/
│   ├── API_MASTER_REFERENCE.md
│   ├── python-api-reference.md
│   ├── brain-api-reference.md
│   ├── session-api-reference.md
│   └── CURL_EXAMPLES.md
│
├── cognitive_brain/
│   ├── COGNITIVE_APP_CONNECTION_GUIDE.md
│   ├── CUSTOM_AGENT_COORDINATION_WORKFLOWS.md
│   └── OPERATIONAL_GUIDELINES.md
│
├── agent/
│   ├── CUSTOM_AGENT_INTERACTION_PROTOCOL.md
│   ├── CUSTOM_AGENT_SELECTION_FRAMEWORK.md
│   └── OPERATIONAL_GUIDELINES.md
│
├── guides/
│   ├── GETTING_STARTED_API_CONSUMER.md
│   ├── INTEGRATION_EXAMPLES.md
│   └── ERROR_HANDLING.md
│
└── accountability/
    └── AGENT_ACCOUNTABILITY_REPORT.md
```

---

## Core Documentation

### 1. Architecture Documentation

**File**: [ARCHITECTURE_PHASE_15_16.md](./ARCHITECTURE_PHASE_15_16.md)

**Contains**:
- ✅ System architecture overview (with Mermaid diagrams)
- ✅ Core components (Decision API, Memory API, Workflow API)
- ✅ Data flow diagrams (sequence & interaction)
- ✅ Deployment architecture (K8s + containerized)
- ✅ Integration points (GitHub Actions, CLI, Cognitive App)
- ✅ Performance characteristics
- ✅ Security considerations

**Key Diagrams**:
- System architecture (client → API → storage)
- Decision recording flow (client → API → SQLite)
- Memory retrieval flow (API → cache → LTM)
- Workflow gate check flow (parallel checkers)

**Target Audience**: Architects, Tech Leads, DevOps

### 2. API Reference

**File**: [API_REFERENCE_PHASE_15_16.md](./API_REFERENCE_PHASE_15_16.md)

**Contains**:
- ✅ All 11 endpoints documented with schemas
- ✅ Request/response examples for each endpoint
- ✅ Error codes and handling
- ✅ cURL examples (executable)
- ✅ Python SDK code
- ✅ JavaScript/Node.js examples
- ✅ Authentication & rate limiting
- ✅ Query parameter reference

**11 Endpoints**:
1. `POST /api/decisions/submit` - Record decision
2. `GET /api/decisions/{id}` - Get decision
3. `GET /api/decisions/recent` - List recent
4. `GET /api/decisions/history` - Paginated history
5. `POST /api/memory/store` - Store pattern
6. `GET /api/memory/retrieve` - Search patterns
7. `POST /api/memory/stm-push` - Cache data
8. `GET /api/memory/stats` - Memory stats
9. `GET /api/workflows/status` - Workflow status
10. `POST /api/workflows/gate-check` - Check gates
11. `GET /api/workflows/rate-limit` - Rate limit status

**Target Audience**: API Consumers, Integration Engineers, Frontend Developers

### 3. Pattern Library Guide

**File**: [PATTERN_LIBRARY_GUIDE.md](./PATTERN_LIBRARY_GUIDE.md)

**Contains**:
- ✅ Pattern overview (40+ patterns, 7 categories)
- ✅ Pattern categories with confidence scores
- ✅ Discovery methods (API, Python SDK, YAML)
- ✅ Application examples (with code)
- ✅ Pattern combinations
- ✅ CI/CD integration
- ✅ Best practices
- ✅ Troubleshooting

**7 Pattern Categories**:
1. **CI Failure Patterns** (8) - Fix pipeline failures
2. **Test Flakiness** (7) - Stabilize unreliable tests
3. **Performance** (6) - Optimize build/runtime
4. **Security** (6) - Detect vulnerabilities
5. **Documentation** (5) - Maintain doc quality
6. **Deployment** (4) - Reliable releases
7. **Observability** (4) - Comprehensive monitoring

**Target Audience**: DevOps, SRE, CI/CD Engineers, Security

---

## Supporting Documentation

### Cognitive Brain Integration

- [Cognitive App Connection Guide](./cognitive_brain/COGNITIVE_APP_CONNECTION_GUIDE.md)
- [Custom Agent Coordination](./cognitive_brain/CUSTOM_AGENT_COORDINATION_WORKFLOWS.md)
- [Operational Guidelines](./cognitive_brain/OPERATIONAL_GUIDELINES.md)

### API Examples & Integration

- [Python API Reference](./api/python-api-reference.md)
- [Brain API Reference](./api/brain-api-reference.md)
- [Session API Reference](./api/session-api-reference.md)
- [cURL Examples](./api/CURL_EXAMPLES.md)
- [Integration Examples](./guides/INTEGRATION_EXAMPLES.md)

### Custom Agents

- [Agent Interaction Protocol](./agent/CUSTOM_AGENT_INTERACTION_PROTOCOL.md)
- [Agent Selection Framework](./agent/CUSTOM_AGENT_SELECTION_FRAMEWORK.md)
- [Merge Readiness](./agent/AGENT_MERGE_READINESS_INTEGRATION.md)

---

## Patterns Reference

### By Confidence Level

**High Confidence (≥0.90)** - 8 patterns
- Use without hesitation
- Proven track record
- High success rate (90%+)

**Medium-High Confidence (0.75-0.89)** - 12 patterns
- Generally reliable
- Some edge cases may need adjustment
- Success rate 75-90%

**Medium Confidence (0.60-0.74)** - 15 patterns
- Helpful as starting point
- Requires validation
- Success rate 60-75%

**Acceptable (0.50-0.59)** - 5 patterns
- Limited applicability
- Requires thorough testing
- Success rate 50-60%

### By Lane

| Lane | Patterns | Primary Focus |
|------|----------|---------------|
| **Security** | 6 | Vulnerability detection & remediation |
| **CI** | 8 | Pipeline failure fixes |
| **Testing** | 7 | Test reliability & flakiness |
| **Performance** | 6 | Build & runtime optimization |
| **Documentation** | 5 | Quality & freshness |
| **Deployment** | 4 | Release procedures |
| **Observability** | 4 | Monitoring & logging |

---

## API Endpoints by Category

### Decision Management
- `POST /api/decisions/submit` - Create decision record
- `GET /api/decisions/{id}` - Retrieve decision
- `GET /api/decisions/recent` - List recent decisions
- `GET /api/decisions/history` - Full decision history

### Memory Management
- `POST /api/memory/store` - Store pattern/learning
- `GET /api/memory/retrieve` - Search patterns
- `POST /api/memory/stm-push` - Cache session data
- `GET /api/memory/stats` - Memory metrics

### Workflow Management
- `GET /api/workflows/status` - Check workflow status
- `POST /api/workflows/gate-check` - Verify gates pass
- `GET /api/workflows/rate-limit` - Rate limit status

---

## Common Use Cases

### 1. Fix a CI Pipeline Failure

```
1. Search patterns: /api/memory/retrieve?lane_name=ci&pattern_type=timeout
2. Review pattern details (confidence, fixes)
3. Apply recommended fix
4. Monitor workflow for success
5. Store result as new pattern if applicable
```

**Docs**: [CI Failure Patterns](./PATTERN_LIBRARY_GUIDE.md#1-ci-failure-patterns-8-patterns)

### 2. Detect Security Vulnerability

```
1. CodeQL alerts pattern: SQL injection detected
2. Search: /api/memory/retrieve?pattern_type=sql_injection
3. Get pattern: "SQL Injection Vulnerability" (0.93 confidence)
4. Apply fix: Use parameterized queries
5. Record decision: POST /api/decisions/submit
```

**Docs**: [Security Patterns](./PATTERN_LIBRARY_GUIDE.md#4-security-patterns-6-patterns)

### 3. Optimize Slow Build

```
1. Analyze dependencies between jobs
2. Search patterns: /api/memory/retrieve?pattern_type=parallel&min_confidence=0.85
3. Apply: "Parallelization of Sequential Jobs"
4. Expected improvement: 25 min → 8 min (68%)
5. Verify: Get /api/workflows/status
```

**Docs**: [Performance Patterns](./PATTERN_LIBRARY_GUIDE.md#3-performance-optimization-patterns-6-patterns)

### 4. Stabilize Flaky Test

```
1. Detect flaky test: 15% failure rate
2. Search: /api/memory/retrieve?pattern_type=flaky_test&tag=concurrency
3. Review pattern: "Race Condition in Concurrent Test" (0.88 confidence)
4. Apply fix: Add mutex/synchronization
5. Validate: Run test suite 10x
```

**Docs**: [Test Flakiness Patterns](./PATTERN_LIBRARY_GUIDE.md#2-test-flakiness-patterns-7-patterns)

---

## Search Recipes

### Find Solutions for Your Problem

```bash
# 1. Generic search by lane
curl ".../api/memory/retrieve?lane_name=security"

# 2. Type-specific search
curl ".../api/memory/retrieve?pattern_type=sql_injection"

# 3. High-confidence only
curl ".../api/memory/retrieve?min_confidence=0.85"

# 4. Complex query
curl ".../api/memory/retrieve?lane_name=ci&min_confidence=0.80&limit=10"

# 5. By tag
curl ".../api/memory/retrieve?tag=concurrency&tag=mutex"
```

### Retrieve Statistics

```bash
# Memory system stats
curl ".../api/memory/stats"

# Workflow status
curl ".../api/workflows/status?phase=15-16"

# Rate limit check
curl ".../api/workflows/rate-limit"
```

### Record Decisions

```bash
# Submit new decision
curl -X POST ".../api/decisions/submit" \
  -d '{"lane_name":"security","decision_type":"fix",...}'

# Get decision history
curl ".../api/decisions/history?lane_name=security&page_size=50"
```

---

## Quality Metrics

| Metric | Target | Status |
|--------|--------|--------|
| **API Endpoints** | 11 | ✅ 11/11 Documented |
| **Code Examples** | All endpoints | ✅ cURL + Python + JS |
| **Architecture Diagrams** | 4+ | ✅ 6 diagrams |
| **Patterns** | 40+ | ✅ 40+ with schemas |
| **Internal Link Health** | 100% | 🟡 In Progress |
| **API Latency (p99)** | <100ms | ✅ <80ms |
| **Cache Hit Rate** | >80% | ✅ 85% |

---

## Getting Help

### Documentation Issues

- **Broken Link**: Report in [Issues](https://github.com/Aries-Serpent/_codex_/issues)
- **Unclear Example**: Comment on [Discussion](https://github.com/Aries-Serpent/_codex_/discussions)
- **Missing Endpoint**: Check [API Reference](./API_REFERENCE_PHASE_15_16.md) or file issue

### Pattern Questions

- **Pattern Selection**: See [Discovery Guide](./PATTERN_LIBRARY_GUIDE.md#discovery--search)
- **Applying Patterns**: See [Examples](./PATTERN_LIBRARY_GUIDE.md#applying-patterns)
- **Combinations**: See [Pattern Combinations](./PATTERN_LIBRARY_GUIDE.md#pattern-combinations)

### API Support

- **Authentication**: See [Auth Guide](./API_REFERENCE_PHASE_15_16.md#authentication--rate-limiting)
- **Rate Limits**: See [Rate Limiting](./API_REFERENCE_PHASE_15_16.md#rate-limiting)
- **Errors**: See [Error Handling](./API_REFERENCE_PHASE_15_16.md#error-handling)

---

## Links to Key Resources

**Core Documentation**:
- [ARCHITECTURE_PHASE_15_16.md](./ARCHITECTURE_PHASE_15_16.md) - System design
- [API_REFERENCE_PHASE_15_16.md](./API_REFERENCE_PHASE_15_16.md) - 11 endpoints
- [PATTERN_LIBRARY_GUIDE.md](./PATTERN_LIBRARY_GUIDE.md) - 40+ patterns

**Integration**:
- [Cognitive App Guide](./cognitive_brain/COGNITIVE_APP_CONNECTION_GUIDE.md)
- [Custom Agents](./agent/CUSTOM_AGENT_INTERACTION_PROTOCOL.md)
- [CLI Usage](./cli/ADVANCED_USAGE.md)

**Related**:
- [README.md](../README.md) - Main project page
- [ROADMAP.md](./ROADMAP.md) - Future plans
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contributing guide
- [Security](../SECURITY.md) - Security policy

---

**Generated**: 2026-07-11 | **Phase**: 15-16 | **Lane**: 5 - Documentation Refresh

