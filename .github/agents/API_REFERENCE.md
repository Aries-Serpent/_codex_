# API Reference

Complete API reference for the GitHub Agent PR Reviewer System.

---

## 📦 Core Modules

### codex_reviewer.main

#### CodexQuantumReviewer

Main orchestrator for PR reviews.

**Methods:**

```python
async def handle_event(event: Dict[str, Any]) -> Dict[str, Any]
```
Main event handler for all triggers.

**Parameters:**
- `event`: Event payload from GitHub webhook
  - `action`: Event type (initial_review, incremental_review, etc.)
  - `context`: ReviewContext object

**Returns:** Dictionary with status and review results

**Example:**
```python
reviewer = CodexQuantumReviewer()
event = {"action": "initial_review", "context": context}
result = await reviewer.handle_event(event)
```

---

```python
async def perform_initial_review(event: Dict) -> Dict
```
Perform comprehensive initial PR review.

**Returns:** Complete review results with suggestions and orchestration plan

---

```python
def _format_review_body(result: ReviewResult) -> str
```
Format review results as markdown.

**Parameters:**
- `result`: ReviewResult object

**Returns:** Markdown-formatted review body

---

### codex_reviewer.security

#### SecurityValidator

Security vulnerability scanner.

**Methods:**

```python
async def scan(context: ReviewContext) -> List[Dict]
```
Scan code for security vulnerabilities.

**Parameters:**
- `context`: ReviewContext with PR details

**Returns:** List of security issues found

**Example:**
```python
validator = SecurityValidator()
issues = await validator.scan(context)
```

---

### codex_reviewer.secret_patterns

#### SecretPatterns

Secret detection pattern configuration.

**Class Attributes:**

```python
PATTERNS: Dict[str, str]
```
Dictionary of regex patterns for secret detection.

**Keys:** api_key, password, token, secret, aws_access_key, aws_secret_key, github_token, private_key, slack_token, stripe_key, jwt, bearer_token

---

```python
PLACEHOLDER_PATTERNS: List[str]
```
Patterns for placeholder detection (to avoid false positives).

---

```python
HIGH_RISK_FILES: List[str]
```
List of high-risk file patterns (.env, credentials, etc.).

---

**Functions:**

```python
def calculate_entropy(string: str) -> float
```
Calculate Shannon entropy of a string.

**Parameters:**
- `string`: String to analyze

**Returns:** Entropy value (0.0 = no entropy, ~8.0 = maximum)

**Example:**
```python
entropy = calculate_entropy("Xy9kL2mN8pQ4rT6vW3zB1cF5gH7jK0oP")
print(f"Entropy: {entropy}")  # High entropy indicates randomness
```

---

```python
def has_high_entropy(string: str, threshold: float = 4.5, min_length: int = 20) -> bool
```
Check if string has high entropy (likely a secret).

**Parameters:**
- `string`: String to check
- `threshold`: Entropy threshold (default: 4.5)
- `min_length`: Minimum string length (default: 20)

**Returns:** True if high entropy

---

### codex_reviewer.github_client

#### GitHubAPIClient

GitHub API client for PR operations.

**Constructor:**

```python
def __init__(token: str, base_url: str = "https://api.github.com")
```

**Parameters:**
- `token`: GitHub API token
- `base_url`: GitHub API base URL

---

**Methods:**

```python
async def post_review(
    repo: str,
    pr_number: int,
    body: str,
    event: str,
    comments: List[Dict]
) -> Dict
```
Post review to PR.

**Parameters:**
- `repo`: Repository (format: "owner/repo")
- `pr_number`: PR number
- `body`: Review body text
- `event`: Review event (APPROVE, REQUEST_CHANGES, COMMENT)
- `comments`: List of inline comments

**Returns:** GitHub API response

**Example:**
```python
client = GitHubAPIClient(token="ghp_...")
await client.post_review(
    repo="owner/repo",
    pr_number=123,
    body="Review body",
    event="COMMENT",
    comments=[]
)
```

---

```python
async def get_pr_details(repo: str, pr_number: int) -> Dict
```
Get PR details from GitHub.

**Returns:** PR metadata including title, description, author, etc.

---

```python
async def get_pr_files(repo: str, pr_number: int) -> List[Dict]
```
Get list of files changed in PR.

**Returns:** List of file objects with filename, status, additions, deletions

---

```python
async def get_pr_diff(repo: str, pr_number: int) -> str
```
Get unified diff for PR.

**Returns:** Unified diff string

---

### codex_reviewer.metrics

#### MetricsCollector

Metrics collection and storage.

**Constructor:**

```python
def __init__(storage_path: Path, buffer_size: int = 10)
```

**Parameters:**
- `storage_path`: Path for metrics storage
- `buffer_size`: Number of metrics to buffer before flush

---

**Methods:**

```python
def record_review(metric: ReviewMetrics, flush_immediately: bool = False)
```
Record review metrics.

**Parameters:**
- `metric`: ReviewMetrics object
- `flush_immediately`: If True, flush buffer immediately

---

```python
def flush_all() -> None
```
Flush all buffered metrics to storage.

---

```python
def get_recent_metrics(days: int = 7) -> List[ReviewMetrics]
```
Get recent metrics.

**Parameters:**
- `days`: Number of days to retrieve

**Returns:** List of ReviewMetrics

---

```python
def get_aggregate_stats(days: int = 7) -> Dict
```
Get aggregate statistics.

**Returns:** Dictionary with avg_confidence, avg_review_time, total_reviews, etc.

---

### codex_reviewer.orchestration

#### WorkflowOrchestrator

Workflow orchestration and planning.

**Methods:**

```python
async def create_plan(
    context: ReviewContext,
    result: ReviewResult
) -> Dict
```
Create orchestration plan based on review results.

**Parameters:**
- `context`: ReviewContext
- `result`: ReviewResult

**Returns:** Dictionary with priority, steps, estimated_time, dependencies

**Example:**
```python
orchestrator = WorkflowOrchestrator()
plan = await orchestrator.create_plan(context, result)
print(f"Priority: {plan['priority']}")
print(f"Steps: {len(plan['steps'])}")
```

---

## 📊 Data Classes

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

**Example:**
```python
context = ReviewContext(
    pr_number=123,
    repo="owner/repo",
    files_changed=["file.py"],
    diff="+ new line",
    base_branch="main",
    head_branch="feature",
    author="user",
    description="PR description"
)
```

---

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

---

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

## 🔧 Configuration

### Environment Variables

```python
GITHUB_APP_ID: str  # GitHub App ID
GITHUB_WEBHOOK_SECRET: str  # Webhook secret
GITHUB_PRIVATE_KEY_SECRET: str  # Secrets Manager secret name
METRICS_BUCKET: str  # S3 bucket for metrics
LOG_LEVEL: str  # DEBUG, INFO, WARNING, ERROR
ENVIRONMENT: str  # dev, staging, prod
```

---

### Constants

```python
# From secret_patterns.py
ENTROPY_THRESHOLD = 4.5
MIN_SECRET_LENGTH = 16
MAX_SECRET_LENGTH = 512

# From metrics.py
DEFAULT_BUFFER_SIZE = 10
DEFAULT_STORAGE_PATH = Path(".codex/metrics")

# From github_client.py
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
```

---

## 🎯 Usage Examples

### Complete Review Flow

```python
import asyncio
from codex_reviewer.main import CodexQuantumReviewer, ReviewContext

async def review_pr():
    # Create reviewer
    reviewer = CodexQuantumReviewer()
    
    # Create context
    context = ReviewContext(
        pr_number=123,
        repo="owner/repo",
        files_changed=["app.py"],
        diff="+ print('hello')",
        base_branch="main",
        head_branch="feature/test",
        author="developer",
        description="Add hello world"
    )
    
    # Perform review
    event = {"action": "initial_review", "context": context}
    result = await reviewer.handle_event(event)
    
    print(f"Review complete: {result['status']}")
    print(f"Confidence: {result['confidence']}")

asyncio.run(review_pr())
```

### Pattern Detection

```python
from codex_reviewer.secret_patterns import SecretPatterns, has_high_entropy

# Check for secrets
patterns = SecretPatterns.get_compiled_patterns()
code = 'API_KEY = "sk_test_1234567890abcdef"'

for name, pattern in patterns.items():
    if pattern.search(code):
        print(f"Found {name} in code!")

# Check entropy
if has_high_entropy("Xy9kL2mN8pQ4rT6vW3zB"):
    print("High entropy detected - likely a secret")
```

### Custom Security Scan

```python
from codex_reviewer.security import SecurityValidator
from codex_reviewer.main import ReviewContext

async def scan_for_vulnerabilities():
    validator = SecurityValidator()
    
    context = ReviewContext(
        pr_number=1,
        repo="test/repo",
        files_changed=["app.py"],
        diff="query = f'SELECT * FROM users WHERE id={user_id}'",
        base_branch="main",
        head_branch="feature",
        author="dev",
        description="Database query"
    )
    
    issues = await validator.scan(context)
    
    for issue in issues:
        print(f"Security Issue: {issue['message']}")

asyncio.run(scan_for_vulnerabilities())
```

---

## 🔍 Error Codes

### Common Errors

| Code | Message | Cause | Solution |
|------|---------|-------|----------|
| 401 | Unauthorized | Invalid GitHub token | Check token validity |
| 403 | Forbidden | Insufficient permissions | Update app permissions |
| 404 | Not Found | Invalid repo or PR | Verify repo/PR exists |
| 422 | Unprocessable Entity | Invalid request format | Check API payload |
| 500 | Internal Server Error | Agent error | Check CloudWatch logs |

---

## 📚 Type Hints

All functions include comprehensive type hints for better IDE support:

```python
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

async def process_review(
    context: ReviewContext,
    options: Optional[Dict[str, Any]] = None
) -> ReviewResult:
    ...
```

---

**Version:** 1.0.0  
**Python:** 3.11+  
**Last Updated:** 2025-12-21
