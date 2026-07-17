# Integration Master Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> **Consolidated Master Document** for Codex Integrations
> **Created**: 2026-07-08
> **Consolidation Campaign**: Phase 12 WS3
> **Status**: Active Master Document

**Consolidated from** 10 source files:
- docs/COGNITIVE_BRAIN_GITHUB_LOGS_UPDATE.md
- docs/BUNDLE_BUILDER_INTEGRATION_PLAN.md
- docs/agent/AGENT_MERGE_READINESS_docs/api/reference/INTEGRATION.md
- docs/agent/AI_AGENT_WORKFLOW_docs/api/reference/INTEGRATION.md
- docs/api/JAVASCRIPT_docs/api/reference/INTEGRATION.md
- docs/api/PYTHON_docs/api/reference/INTEGRATION.md
- docs/changelogs/CHANGELOG_GITHUB_LOGS.md
- docs/crm/CRM_INTEGRATION_FOR_REPO_MANAGEMENT.md
- docs/GITHUB_LOGS_IMPLEMENTATION_SUMMARY.md
- docs/ci/FAST_FORWARD_INTEGRATION_GUIDE.md

---

## Table of Contents

1. [Integration Overview](#integration-overview)
2. [GitHub Integration](#github-integration)
3. [Python Client Integration](#python-client-integration)
4. [JavaScript/Node Integration](#javascriptnodejs-integration)
5. [Cognitive Brain Integration](#cognitive-brain-integration)
6. [CI/CD Workflow Integration](#cicd-workflow-integration)
7. [Third-Party Integrations](#third-party-integrations)
8. [Bundle Builder Integration](#bundle-builder-integration)

---

## Integration Overview

### Available Integrations

```

 Integration Hub 

 • GitHub APIs 
 • Python Client Library 
 • JavaScript/Node SDK 
 • Cognitive Brain (Memory/Skills) 
 • CI/CD Workflows 
 • CRM Integration 
 • Bundle Builder 
 • Fast-Forward Merging 
 • GitHub Logs Integration 

```

### Integration Layers

| Layer | Technology | Purpose | Status |
|-------|-----------|---------|--------|
| **API Layer** | REST/GraphQL | System communication | Active |
| **Client Layer** | Python/JS SDKs | User interaction | Active |
| **Agent Layer** | Agent system | Automation | Active |
| **Cognitive Layer** | Memory/Skills | Intelligence | Active |
| **Workflow Layer** | GitHub Actions | CI/CD automation | Active |

---

## GitHub Integration

### GitHub REST API

**Authentication**:
```python
import requests

headers = {
 "Authorization": f"token {GITHUB_TOKEN}",
 "Accept": "application/vnd.github.v3+json"
}

# List repositories
response = requests.get(
 "https://api.github.com/user/repos",
 headers=headers
)
repos = response.json()
```

### GitHub GraphQL API

**Query Example**:
```graphql
query {
 repository(owner: "Aries-Serpent", name: "_codex_") {
 nameWithOwner
 description
 isPrivate
 issues(first: 5) {
 edges {
 node {
 number
 title
 state
 }
 }
 }
 pullRequests(first: 5) {
 edges {
 node {
 number
 title
 state
 author {
 login
 }
 }
 }
 }
 }
}
```

### GitHub App Integration

```python
from github import Github
from github import GithubIntegration

# Using GitHub App
integration = GithubIntegration(
 integration_id=APP_ID,
 private_key=PRIVATE_KEY
)

# Get installation
for installation in integration.get_installations():
 if installation.account.login == "Aries-Serpent":
 access_token = integration.get_access_token(
 installation.id
 )
 
 # Use access token
 g = Github(access_token.token)
 repo = g.get_repo("Aries-Serpent/_codex_")
```

### GitHub Logs Integration

**GitHub Logs Features**:
- Audit logs for compliance
- Action logs for CI/CD tracking
- Security logs for threat detection
- Performance logs for monitoring

```python
# Retrieve GitHub logs
import requests

response = requests.get(
 "https://api.github.com/repos/Aries-Serpent/_codex_/logs",
 headers=headers,
 params={
 "per_page": 100,
 "page": 1,
 "sort": "desc"
 }
)

logs = response.json()
for log in logs:
 print(f"{log['timestamp']}: {log['action']} by {log['actor']}")
```

---

## Python Client Integration

### Installation

```bash
pip install codex-client
# or
pip install -e git+https://github.com/Aries-Serpent/_codex_.git#egg=codex
```

### Basic Usage

```python
from codex import Codex

# Initialize client
client = Codex(
 api_key="your-api-key",
 base_url="https://api.example.com"
)

# Create session
session = client.sessions.create(
 session_type="cli",
 metadata={"user": "alice"}
)

# Log event
event = client.events.log(
 session_id=session.id,
 type="user.message",
 content="Analyze this code"
)

# Get response
response = client.execute(
 session_id=session.id,
 action="analyze_code",
 params={"code": code_snippet}
)
```

### Advanced Features

```python
# Semantic search
results = client.search(
 query="ML training pipeline",
 type="code",
 limit=10
)

# Store memory
client.memory.store(
 fact="Use Ray for distributed training",
 scope="ltm", # Long-term memory
 tags=["ml", "training"]
)

# Retrieve memory
facts = client.memory.retrieve(
 query="distributed training",
 scope="both"
)
```

---

## JavaScript/Node.js Integration

### Installation

```bash
npm install @codex/client
# or
yarn add @codex/client
```

### Basic Usage

```javascript
import { Codex } from '@codex/client';

// Initialize client
const client = new Codex({
 apiKey: process.env.CODEX_API_KEY,
 baseUrl: 'https://api.example.com'
});

// Create session
const session = await client.sessions.create({
 sessionType: 'cli',
 metadata: { user: 'bob' }
});

// Log event
const event = await client.events.log({
 sessionId: session.id,
 type: 'user.message',
 content: 'Analyze this code'
});

// Execute action
const response = await client.execute({
 sessionId: session.id,
 action: 'analyze_code',
 params: { code: codeSnippet }
});

console.log(response.result);
```

### Advanced Features

```javascript
// Semantic search
const results = await client.search({
 query: 'API authentication patterns',
 type: 'code',
 limit: 10
});

// Store memory
await client.memory.store({
 fact: 'Use OAuth 2.0 for user authentication',
 scope: 'ltm',
 tags: ['auth', 'security']
});

// Stream responses
const stream = client.createStream({
 sessionId: session.id,
 action: 'analyze_large_codebase'
});

stream.on('data', chunk => {
 console.log('Received:', chunk);
});

stream.on('end', () => {
 console.log('Analysis complete');
});
```

---

## Cognitive Brain Integration

### Memory System Integration

**Short-Term Memory (STM)**:
```python
# Store temporary facts
client.memory.store_stm({
 "fact": "Current task is refactoring auth module",
 "ttl": 3600 # 1 hour
})

# Retrieve STM
recent_context = client.memory.retrieve_stm(
 query="current task"
)
```

**Long-Term Memory (LTM)**:
```python
# Store persistent facts
client.memory.store_ltm({
 "fact": "Always use bcrypt for password hashing",
 "category": "security_best_practices",
 "confidence": 0.95
})

# Query LTM
best_practices = client.memory.retrieve_ltm(
 query="password hashing",
 limit=5
)
```

### Skill Execution

```python
# List available skills
skills = client.skills.list()
# Output: [
# {'name': 'code_analyzer', 'version': '1.0.0'},
# {'name': 'test_generator', 'version': '2.1.0'},
# ...
# ]

# Execute skill
result = client.skills.execute(
 name='code_analyzer',
 input={
 'code': code_snippet,
 'language': 'python'
 }
)

# Result includes:
# - analysis: code analysis results
# - metrics: quality metrics
# - recommendations: improvement suggestions
```

### Cognitive Context Integration

```python
# Get cognitive context
context = client.get_cognitive_context({
 "session_id": session_id,
 "include": ["memory", "skills", "patterns"]
})

# Use context for enhanced responses
response = client.execute(
 action="explain_architecture",
 params={"module": "data_pipeline"},
 context=context # Include cognitive context
)
```

---

## CI/CD Workflow Integration

### GitHub Actions Integration

**Trigger Agent Execution**:
```yaml
# .github/workflows/code-review.yml
name: AI Code Review
on: [pull_request]

jobs:
 ai-review:
 runs-on: ubuntu-latest
 steps:
 - uses: actions/checkout@v3
 
 - name: Run AI Code Review
 uses: ./.github/actions/agent-runner
 with:
 agent: code-review-agent
 pr_number: ${{ github.event.pull_request.number }}
 
 - name: Comment on PR
 uses: actions/github-script@v6
 with:
 script: |
 github.rest.issues.createComment({
 issue_number: context.issue.number,
 owner: context.repo.owner,
 repo: context.repo.repo,
 body: 'AI code review completed'
 })
```

### Fast-Forward Integration

**Auto-merge for Simple PRs**:
```yaml
# .github/workflows/auto-merge.yml
name: Auto-Merge Simple PRs
on: [pull_request_review]

jobs:
 auto-merge:
 runs-on: ubuntu-latest
 if: github.event.review.state == 'APPROVED'
 steps:
 - name: Check PR complexity
 id: complexity
 run: |
 # Analyze PR diff
 # If < 100 lines + no dependency changes + all tests pass
 echo "is_simple=true" >> $GITHUB_OUTPUT
 
 - name: Auto-merge if simple
 if: steps.complexity.outputs.is_simple == 'true'
 uses: ./.github/actions/fast-forward-merge
 with:
 pr_number: ${{ github.event.pull_request.number }}
```

### Agent Merge Readiness

```yaml
# .github/workflows/agent-merge-check.yml
name: Agent Merge Readiness
on: [pull_request]

jobs:
 check:
 runs-on: ubuntu-latest
 steps:
 - uses: actions/checkout@v3
 
 - name: Agent Consolidation Check
 run: |
 python scripts/check_agent_consolidation.py
 # Verifies:
 # - No duplicate agents
 # - All agents in registry
 # - No deprecated agents active
```

---

## Third-Party Integrations

### CRM Integration

**Connect Codex to CRM for Customer Management**:

```python
# Sync customer data with Codex
from crm_integration import CRMClient

crm = CRMClient(api_key=CRM_API_KEY)

# Get customer projects
projects = crm.get_customer_projects(customer_id)

# Create Codex session per project
for project in projects:
 session = client.sessions.create(
 session_type="customer_project",
 metadata={
 "customer_id": customer_id,
 "project_id": project.id,
 "crm_sync": True
 }
 )
 
 # Track Codex work in CRM
 crm.update_project(
 project_id=project.id,
 codex_session_id=session.id
 )
```

### Bundle Builder Integration

```python
# Create deployment bundle
from bundle_builder import BundleBuilder

builder = BundleBuilder(
 version="1.2.3",
 target_platform="docker"
)

# Include dependencies
builder.add_dependency("python==3.11")
builder.add_dependency("torch==2.0.0")

# Include Codex
builder.add_package(
 name="codex",
 path="./src/codex",
 include_tests=False
)

# Build bundle
bundle_path = builder.build()
# Output: ./dist/codex-1.2.3-bundle.tar.gz
```

---

## Integration Patterns

### Event-Driven Integration

```python
# Set up webhooks
client.webhooks.create({
 "event_type": "pr_opened",
 "url": "https://example.com/webhooks/pr",
 "active": True
})

# Handle webhook
@app.post("/webhooks/pr")
async def handle_pr_webhook(payload: dict):
 if payload['action'] == 'opened':
 # Trigger analysis
 client.execute(
 action="analyze_pr",
 params={"pr_number": payload['pull_request']['number']}
 )
```

### Polling Integration

```python
# Poll for updates
import time

while True:
 # Check for new issues
 issues = client.issues.list(
 state="open",
 since=last_check_time
 )
 
 for issue in issues:
 # Process issue
 client.execute(
 action="triage_issue",
 params={"issue_id": issue.id}
 )
 
 last_check_time = datetime.now()
 time.sleep(300) # Check every 5 minutes
```

---

## Integration Testing

### Unit Tests

```python
# test_integrations.py
import pytest
from unittest.mock import MagicMock

def test_github_integration():
 client = Codex(api_key="test-key")
 
 # Mock GitHub API
 with patch('requests.get') as mock_get:
 mock_get.return_value.json.return_value = [
 {'id': 1, 'name': 'repo1'}
 ]
 
 repos = client.github.get_repositories()
 assert len(repos) == 1
 assert repos[0]['name'] == 'repo1'
```

### Integration Tests

```python
# test_integration_end_to_end.py
@pytest.mark.integration
def test_end_to_end_workflow():
 # Create session
 session = client.sessions.create()
 
 # Log events
 client.events.log(
 session_id=session.id,
 type="user.message",
 content="Analyze code"
 )
 
 # Execute action
 result = client.execute(
 session_id=session.id,
 action="analyze_code",
 params={"code": "x = 1"}
 )
 
 # Verify result
 assert result.status == "success"
 assert len(result.analysis) > 0
```

---

**This document is the authoritative integration guide for Codex.**

*Last Updated: 2026-07-08
*Consolidation Status: Complete (10 files merged)*
