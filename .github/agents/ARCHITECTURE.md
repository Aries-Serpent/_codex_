# Architecture Documentation

Complete architectural documentation for the GitHub Agent PR Reviewer System.

---

## 📐 System Architecture

### High-Level Overview

```
┌─────────────┐
│   GitHub    │
│  (Webhook)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  API Gateway    │
│  (AWS)          │
└────────┬────────┘
         │
         ▼
┌────────────────────┐
│  Lambda Function   │
│  (Agent Core)      │
├────────────────────┤
│ - Event Handler    │
│ - Pattern Analyzer │
│ - Security Scanner │
│ - Orchestrator     │
│ - GitHub Client    │
└───┬────────┬───────┘
    │        │
    ▼        ▼
┌────────┐ ┌────────────┐
│   S3   │ │  Secrets   │
│(Metrics)│ │  Manager   │
└────────┘ └────────────┘
    │
    ▼
┌─────────────┐
│ CloudWatch  │
│ (Monitoring)│
└─────────────┘
```

---

## 🏗️ Component Architecture

### 1. Core Components

#### CodexQuantumReviewer (Main Orchestrator)
```python
class CodexQuantumReviewer:
    - pattern_analyzer: QuantumPatternAnalyzer
    - security_scanner: SecurityValidator
    - orchestrator: WorkflowOrchestrator
    - knowledge_engine: KnowledgeGapDetector
    - learning_system: SelfEvolutionSystem
    - github_client: GitHubAPIClient
```

**Responsibilities:**
- Event routing and handling
- Coordinating analysis components
- Aggregating results
- Posting reviews to GitHub

#### Security Validator
```python
class SecurityValidator:
    - _sql_patterns: List[Pattern]
    - _xss_patterns: List[Pattern]
    - _cmd_patterns: List[Pattern]
    - _path_patterns: List[Pattern]
```

**Detection Capabilities:**
- SQL injection
- XSS vulnerabilities
- Command injection
- Path traversal
- Hardcoded secrets (14+ types)

#### GitHub API Client
```python
class GitHubAPIClient:
    - base_url: str
    - token: str
    - retry_count: int
    - timeout: int
```

**API Methods:**
- `post_review()` - Post PR reviews
- `add_comment()` - Add issue comments
- `get_pr_details()` - Fetch PR metadata
- `get_pr_files()` - Get changed files
- `get_pr_diff()` - Get unified diff

---

## 🔄 Data Flow

### PR Review Flow

```
1. GitHub Webhook → API Gateway
   ├─ Event: pull_request.opened
   ├─ Event: pull_request.synchronize
   └─ Event: pull_request_review.submitted

2. API Gateway → Lambda
   ├─ Verify signature
   ├─ Parse payload
   └─ Route to handler

3. Lambda → Analysis Pipeline
   ├─ Extract ReviewContext
   ├─ Parallel Analysis:
   │   ├─ Code Quality
   │   ├─ Security Scan
   │   ├─ Performance Check
   │   ├─ Documentation Review
   │   ├─ Quantum Patterns
   │   └─ Knowledge Gaps
   └─ Aggregate Results

4. Results → Orchestration
   ├─ Calculate confidence
   ├─ Generate plan
   ├─ Prioritize suggestions
   └─ Create next steps

5. Orchestration → GitHub
   ├─ Format review body
   ├─ Determine action (APPROVE/REQUEST_CHANGES/COMMENT)
   ├─ Post review
   └─ Add inline comments

6. Side Effects
   ├─ Store metrics in S3
   ├─ Log to CloudWatch
   └─ Update learning system
```

---

## 🗄️ Data Models

### ReviewContext
```python
@dataclass
class ReviewContext:
    pr_number: int
    repo: str
    files_changed: List[str]
    diff: str
    base_branch: str
    head_branch: str
    author: str
    description: str
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())
```

### ReviewResult
```python
@dataclass
class ReviewResult:
    status: str  # approved, changes_requested, commented
    confidence: float  # 0.0 - 1.0
    suggestions: List[Dict]
    orchestration_plan: Dict
    next_steps: List[str]
    knowledge_gaps: List[str]
```

### ReviewMetrics
```python
@dataclass
class ReviewMetrics:
    pr_number: int
    repo: str
    timestamp: datetime
    review_time_seconds: float
    confidence: float
    status: str
    suggestions_count: int
    knowledge_gaps_count: int
    files_changed: int
```

---

## 🔐 Security Architecture

### Authentication Flow

```
1. GitHub Webhook Request
   ├─ Contains X-Hub-Signature-256 header
   └─ Computed from payload + webhook secret

2. API Gateway
   ├─ Receives request
   └─ Forwards to Lambda

3. Lambda Verification
   ├─ Retrieve webhook secret from env
   ├─ Compute expected signature
   ├─ Compare with received signature
   └─ Reject if mismatch

4. GitHub API Calls
   ├─ Retrieve private key from Secrets Manager
   ├─ Generate JWT token
   ├─ Get installation token
   └─ Make authenticated API calls
```

### Secret Storage

```
┌─────────────────┐
│ AWS Secrets     │
│ Manager         │
├─────────────────┤
│ - Private Key   │
│   (PEM format)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Lambda          │
│ Environment     │
├─────────────────┤
│ - App ID        │
│ - Webhook Secret│
│ - Secret ARN    │
└─────────────────┘
```

---

## 📊 Monitoring Architecture

### Metrics Collection

```
Lambda Execution
    │
    ├─→ CloudWatch Logs
    │   ├─ INFO: Review started
    │   ├─ DEBUG: Analysis results
    │   └─ ERROR: Failures
    │
    ├─→ CloudWatch Metrics
    │   ├─ Invocations
    │   ├─ Errors
    │   ├─ Duration
    │   └─ Concurrent Executions
    │
    └─→ S3 Metrics
        ├─ Review details
        ├─ Pattern matches
        ├─ Confidence scores
        └─ Performance data
```

### Dashboard Components

1. **Lambda Performance**
   - Invocation count
   - Error rate
   - Duration (avg, p95, p99)
   - Memory usage

2. **API Gateway**
   - Request count
   - 4XX/5XX errors
   - Latency

3. **Custom Metrics**
   - Review time
   - Confidence scores
   - Pattern accuracy
   - Suggestion acceptance

---

## 🚀 Deployment Architecture

### Multi-Environment Strategy

```
Development
    ├─ Lambda: codex-reviewer-agent-dev
    ├─ API Gateway: dev stage
    ├─ S3: metrics-dev
    └─ CloudWatch: dev logs

Staging
    ├─ Lambda: codex-reviewer-agent-staging
    ├─ API Gateway: staging stage
    ├─ S3: metrics-staging
    └─ CloudWatch: staging logs

Production
    ├─ Lambda: codex-reviewer-agent-prod
    ├─ API Gateway: prod stage
    ├─ S3: metrics-prod
    ├─ CloudWatch: prod logs
    └─ X-Ray: Tracing enabled
```

### Scaling Characteristics

**Lambda Auto-Scaling:**
- Concurrent executions: Up to 1000 (default)
- Memory: 512MB per instance
- Timeout: 300 seconds
- Cold start: ~2-3 seconds

**API Gateway:**
- Rate limit: 10,000 requests/second
- Burst: 5,000 requests
- Regional deployment

---

## 🎯 Design Patterns

### 1. Event-Driven Architecture
- GitHub webhooks trigger Lambda
- Asynchronous processing
- Event-sourcing for metrics

### 2. Strategy Pattern
- Pluggable analyzers
- Configurable patterns
- Multiple security scanners

### 3. Observer Pattern
- Metrics collection
- Learning system feedback
- Audit logging

### 4. Factory Pattern
- ReviewContext creation
- ReviewResult aggregation
- Metrics object instantiation

### 5. Adapter Pattern
- GitHub API client
- Multiple authentication methods
- Backward compatibility

---

## 🔌 Integration Points

### External Services

1. **GitHub API**
   - Authentication: GitHub App (JWT + Installation Token)
   - Rate Limits: 5,000 requests/hour per installation
   - Retry Strategy: Exponential backoff (3 attempts)

2. **AWS Services**
   - Lambda: Compute execution
   - API Gateway: HTTP endpoint
   - S3: Metrics storage
   - Secrets Manager: Credential storage
   - CloudWatch: Logging and monitoring

3. **Development Tools**
   - Terraform: Infrastructure as Code
   - pytest: Testing framework
   - GitHub Actions: CI/CD (optional)

---

## 📏 Design Decisions

### ADR-001: Lambda over EC2
**Decision:** Use AWS Lambda for compute  
**Rationale:**
- Pay-per-use pricing
- Auto-scaling
- No server management
- Event-driven model fits use case

**Trade-offs:**
- Cold start latency (2-3s)
- 15-minute execution limit
- Limited runtime customization

### ADR-002: Pre-compiled Patterns
**Decision:** Compile regex patterns at initialization  
**Rationale:**
- 40x performance improvement
- Patterns don't change at runtime
- Memory overhead acceptable

### ADR-003: Buffered Metrics
**Decision:** Buffer metrics before S3 write  
**Rationale:**
- Reduce S3 API calls (10x)
- Lower costs
- Better performance

**Trade-offs:**
- Potential data loss on crash
- Slightly delayed metrics visibility

### ADR-004: Async/Await Throughout
**Decision:** Use asyncio for all I/O operations  
**Rationale:**
- Parallel analysis tasks
- Better Lambda utilization
- Improved response time

---

## 🔄 Evolution Strategy

### Phase 1: Core Functionality (Current)
- Basic PR review
- Security pattern detection
- GitHub integration

### Phase 2: Enhancement (Pre-commit 3-8)
- Machine learning for pattern accuracy
- Advanced quantum pattern analysis
- Multi-language support

### Phase 3: Scale (Month 2)
- Distributed processing
- Advanced caching
- Real-time dashboards

### Phase 4: Intelligence (Month 3+)
- Deep learning models
- Predictive analysis
- Automated code fixes

---

## 📝 Technical Specifications

**Languages:** Python 3.11+  
**Frameworks:** asyncio, aiohttp  
**Cloud:** AWS (Lambda, API Gateway, S3, Secrets Manager, CloudWatch)  
**Infrastructure:** Terraform  
**Testing:** pytest, pytest-asyncio, pytest-cov  
**CI/CD:** GitHub Actions (optional)  

**Performance Requirements:**
- Review Time: < 30s (95th percentile)
- API Success Rate: > 99%
- Pattern Accuracy: > 95%
- Uptime: > 99.9%

**Security Requirements:**
- All secrets in Secrets Manager
- Encryption at rest (S3)
- HTTPS only
- Webhook signature verification
- Least privilege IAM roles

---

**Version:** 1.0.0  
**Last Updated:** 2024-12-21  
**Status:** Production-Ready
