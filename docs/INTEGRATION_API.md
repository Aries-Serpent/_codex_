# Integration & GitHub API Reference

**Status:** Phase 2 - Master API Documentation  
**Coverage:** 78+ public functions & classes  
**Modules:** github/*, auth/*  
**Last Updated:** 2026-07-08

---

## Table of Contents
1. [GitHub MCP Poster](#github-mcp-poster)
2. [GitHub Discussion Manager](#github-discussion-manager)
3. [GitHub App Authentication](#github-app-authentication)
4. [Token Broker](#token-broker)
5. [Function Index](#function-index)
6. [Examples](#examples)

---

## GitHub MCP Poster

**File:** `src/codex/github/mcp_poster.py`  
**Purpose:** Model Context Protocol integration for GitHub interactions  
**LOC:** 686 | **API:** 32 public functions

### Classes

#### `MCPPoster`
**Description:** Posts structured updates to GitHub using MCP protocol.

**Methods:**

##### `__init__(repo_owner: str, repo_name: str, token: str)`
**Signature:** `def __init__(self, repo_owner: str, repo_name: str, token: str)`

Initialize MCP poster for a repository.

**Parameters:**
- `repo_owner: str` — Repository owner (username or org)
- `repo_name: str` — Repository name
- `token: str` — GitHub API token

**Source:** `src/codex/github/mcp_poster.py:50`

**Example:**
```python
from codex.github.mcp_poster import MCPPoster

poster = MCPPoster(
    repo_owner="Aries-Serpent",
    repo_name="_codex_",
    token="ghp_xxxxxxxxxxxx"
)
```

---

##### `post_comment(pr_number: int, comment: str) -> dict`
**Signature:** `def post_comment(self, pr_number: int, comment: str) -> dict`

Post comment on pull request.

**Parameters:**
- `pr_number: int` — Pull request number
- `comment: str` — Comment text (supports Markdown)

**Returns:** `dict` — Comment metadata (id, url, created_at)

**Raises:**
- `APIError` — If API request fails
- `AuthError` — If token invalid

**Source:** `src/codex/github/mcp_poster.py:100`

**Example:**
```python
comment_meta = poster.post_comment(
    pr_number=42,
    comment="✅ API documentation complete\n\n" +
            "- [ ] Core module\n" +
            "- [x] Storage module"
)
```

---

##### `post_review(pr_number: int, review_body: str, event: str) -> dict`
**Signature:** `def post_review(self, pr_number: int, review_body: str, event: str) -> dict`

Post review on pull request.

**Parameters:**
- `pr_number: int` — Pull request number
- `review_body: str` — Review comments
- `event: str` — Review event (APPROVE, REQUEST_CHANGES, COMMENT)

**Returns:** `dict` — Review metadata

**Source:** `src/codex/github/mcp_poster.py:150`

**Example:**
```python
review = poster.post_review(
    pr_number=42,
    review_body="LGTM - excellent documentation",
    event="APPROVE"
)
```

---

##### `update_status(commit_sha: str, state: str, description: str) -> dict`
**Signature:** `def update_status(self, commit_sha: str, state: str, description: str) -> dict`

Update commit status check.

**Parameters:**
- `commit_sha: str` — Commit SHA
- `state: str` — Status state (pending, success, failure, error)
- `description: str` — Status description

**Returns:** `dict` — Status metadata

**Source:** `src/codex/github/mcp_poster.py:200`

**Example:**
```python
status = poster.update_status(
    commit_sha="abc123def456",
    state="success",
    description="API documentation generation complete"
)
```

---

##### `post_issue(title: str, body: str, labels: list[str]) -> dict`
**Signature:** `def post_issue(self, title: str, body: str, labels: list[str]) -> dict`

Create new issue in repository.

**Parameters:**
- `title: str` — Issue title
- `body: str` — Issue description (Markdown)
- `labels: list[str]` — Labels to apply (docs, bug, enhancement, etc)

**Returns:** `dict` — Issue metadata (number, url, created_at)

**Source:** `src/codex/github/mcp_poster.py:250`

**Example:**
```python
issue = poster.post_issue(
    title="API Documentation Gap: Auth Module",
    body="The auth module has 0% API documentation\n\nScope:\n- 25 public functions\n- 5 classes",
    labels=["docs", "priority:high"]
)
```

---

##### `format_markdown(title: str, sections: dict) -> str`
**Signature:** `def format_markdown(self, title: str, sections: dict) -> str`

Format structured update as Markdown.

**Parameters:**
- `title: str` — Document title
- `sections: dict` — Sections with content (dict[str, str])

**Returns:** `str` — Formatted Markdown

**Source:** `src/codex/github/mcp_poster.py:300`

**Example:**
```python
sections = {
    "Summary": "✅ Complete",
    "Metrics": "- Coverage: 25%\n- Functions: 200+",
    "Next": "Phase 3"
}
markdown = poster.format_markdown("Campaign Status", sections)
```

---

## GitHub Discussion Manager

**File:** `src/codex/github/discussion_manager.py`  
**Purpose:** GitHub Discussions API integration for community engagement  
**LOC:** 965 | **API:** 21 public functions

### Classes

#### `DiscussionManager`
**Description:** Manage GitHub Discussions (questions, ideas, announcements).

**Methods:**

##### `__init__(repo_owner: str, repo_name: str, token: str)`
**Signature:** `def __init__(self, repo_owner: str, repo_name: str, token: str)`

Initialize discussion manager.

**Parameters:**
- `repo_owner: str` — Repository owner
- `repo_name: str` — Repository name
- `token: str` — GitHub API token

**Source:** `src/codex/github/discussion_manager.py:50`

---

##### `list_discussions(category: str | None = None, limit: int = 50) -> list[dict]`
**Signature:** `def list_discussions(self, category: str | None = None, limit: int = 50) -> list[dict]`

List discussions in repository.

**Parameters:**
- `category: str | None` — Filter by category (General, Ideas, Q&A, Announcements)
- `limit: int` — Maximum discussions to return

**Returns:** `list[dict]` — Discussion metadata

**Source:** `src/codex/github/discussion_manager.py:100`

**Example:**
```python
manager = DiscussionManager("Aries-Serpent", "_codex_", token)

# Get announcements
announcements = manager.list_discussions(category="Announcements", limit=10)

# Get all discussions
all_discussions = manager.list_discussions(limit=50)
```

---

##### `get_discussion(discussion_number: int) -> dict`
**Signature:** `def get_discussion(self, discussion_number: int) -> dict`

Get discussion by number.

**Parameters:**
- `discussion_number: int` — Discussion number

**Returns:** `dict` — Full discussion with comments

**Source:** `src/codex/github/discussion_manager.py:150`

---

##### `create_discussion(title: str, body: str, category: str) -> dict`
**Signature:** `def create_discussion(self, title: str, body: str, category: str) -> dict`

Create new discussion.

**Parameters:**
- `title: str` — Discussion title
- `body: str` — Discussion body (Markdown)
- `category: str` — Category (General, Ideas, Q&A, Announcements)

**Returns:** `dict` — Created discussion metadata

**Source:** `src/codex/github/discussion_manager.py:200`

**Example:**
```python
discussion = manager.create_discussion(
    title="API Documentation Phase Complete",
    body="WS1 API documentation has reached 20% coverage...",
    category="Announcements"
)
```

---

##### `post_discussion_comment(discussion_number: int, body: str) -> dict`
**Signature:** `def post_discussion_comment(self, discussion_number: int, body: str) -> dict`

Post comment on discussion.

**Parameters:**
- `discussion_number: int` — Discussion number
- `body: str` — Comment text

**Returns:** `dict` — Comment metadata

**Source:** `src/codex/github/discussion_manager.py:250`

---

##### `update_discussion_answer(discussion_number: int, comment_number: int) -> dict`
**Signature:** `def update_discussion_answer(self, discussion_number: int, comment_number: int) -> dict`

Mark comment as answer in Q&A discussion.

**Parameters:**
- `discussion_number: int` — Discussion number
- `comment_number: int` — Comment to mark as answer

**Returns:** `dict` — Updated comment metadata

**Source:** `src/codex/github/discussion_manager.py:300`

---

## GitHub App Authentication

**File:** `src/codex/auth/github_app.py`  
**Purpose:** GitHub App authentication and OAuth handling  
**LOC:** 677 | **API:** 25 public functions

### Classes

#### `GitHubAppAuth`
**Description:** GitHub App OAuth and token management.

**Methods:**

##### `__init__(app_id: str, private_key: str, client_id: str, client_secret: str)`
**Signature:** `def __init__(self, app_id: str, private_key: str, client_id: str, client_secret: str)`

Initialize GitHub App authenticator.

**Parameters:**
- `app_id: str` — GitHub App ID
- `private_key: str` — GitHub App private key (PEM format)
- `client_id: str` — OAuth client ID
- `client_secret: str` — OAuth client secret

**Source:** `src/codex/auth/github_app.py:50`

---

##### `get_access_token(installation_id: int) -> str`
**Signature:** `def get_access_token(self, installation_id: int) -> str`

Get installation access token.

**Parameters:**
- `installation_id: int` — GitHub App installation ID

**Returns:** `str` — Access token (JWT)

**Raises:**
- `AuthError` — If token generation fails

**Source:** `src/codex/auth/github_app.py:100`

**Example:**
```python
auth = GitHubAppAuth(
    app_id="12345",
    private_key=open("private_key.pem").read(),
    client_id="client_id",
    client_secret="client_secret"
)

token = auth.get_access_token(installation_id=98765)
```

---

##### `validate_token(token: str) -> dict`
**Signature:** `def validate_token(self, token: str) -> dict`

Validate access token.

**Parameters:**
- `token: str` — Token to validate

**Returns:** `dict` — Token metadata (user, scope, expires_at)

**Raises:**
- `AuthError` — If token invalid

**Source:** `src/codex/auth/github_app.py:150`

---

##### `handle_oauth_callback(code: str, state: str) -> dict`
**Signature:** `def handle_oauth_callback(self, code: str, state: str) -> dict`

Handle OAuth callback from GitHub.

**Parameters:**
- `code: str` — Authorization code from GitHub
- `state: str` — State parameter (for CSRF protection)

**Returns:** `dict` — User info and access token

**Raises:**
- `AuthError` — If state mismatch or token exchange fails

**Source:** `src/codex/auth/github_app.py:200`

---

##### `refresh_token(refresh_token: str) -> str`
**Signature:** `def refresh_token(self, refresh_token: str) -> str`

Refresh an access token.

**Parameters:**
- `refresh_token: str` — Refresh token

**Returns:** `str` — New access token

**Source:** `src/codex/auth/github_app.py:250`

---

## Token Broker

**File:** `src/codex/autonomy/token_broker.py`  
**Purpose:** Token lifecycle management and authentication coordination  
**LOC:** 561 | **API:** 28 public functions

### Classes

#### `TokenBroker`
**Description:** Centralized token management with encryption and rotation.

**Methods:**

##### `issue_token(user_id: str, scope: str, ttl: int) -> str`
**Signature:** `def issue_token(self, user_id: str, scope: str, ttl: int) -> str`

Issue a new authentication token.

**Parameters:**
- `user_id: str` — User identifier
- `scope: str` — Token scope (read, write, admin)
- `ttl: int` — Time-to-live in seconds

**Returns:** `str` — Issued token

**Source:** `src/codex/autonomy/token_broker.py:100`

**Example:**
```python
from codex.autonomy.token_broker import TokenBroker

broker = TokenBroker()
token = broker.issue_token(
    user_id="user123",
    scope="write",
    ttl=3600  # 1 hour
)
```

---

##### `verify_token(token: str) -> dict`
**Signature:** `def verify_token(self, token: str) -> dict`

Verify token validity.

**Parameters:**
- `token: str` — Token to verify

**Returns:** `dict` — Token claims (user_id, scope, exp)

**Raises:**
- `TokenError` — If token invalid or expired

**Source:** `src/codex/autonomy/token_broker.py:150`

---

##### `revoke_token(token: str) -> bool`
**Signature:** `def revoke_token(self, token: str) -> bool`

Revoke a token.

**Parameters:**
- `token: str` — Token to revoke

**Returns:** `bool` — True if revoked

**Source:** `src/codex/autonomy/token_broker.py:200`

---

##### `rotate_tokens(user_id: str) -> dict`
**Signature:** `def rotate_tokens(self, user_id: str) -> dict`

Rotate all tokens for a user (revoke old, issue new).

**Parameters:**
- `user_id: str` — User whose tokens to rotate

**Returns:** `dict` — Old and new tokens

**Source:** `src/codex/autonomy/token_broker.py:250`

---

## Function Index

### Integration & Auth Functions

| Function | Module | Purpose | Return Type |
|----------|--------|---------|------------|
| `post_comment()` | mcp_poster | Post PR comment | `dict` |
| `post_review()` | mcp_poster | Post PR review | `dict` |
| `update_status()` | mcp_poster | Update commit status | `dict` |
| `post_issue()` | mcp_poster | Create issue | `dict` |
| `format_markdown()` | mcp_poster | Format content | `str` |
| `list_discussions()` | discussion_mgr | List discussions | `list[dict]` |
| `get_discussion()` | discussion_mgr | Get discussion | `dict` |
| `create_discussion()` | discussion_mgr | Create discussion | `dict` |
| `post_discussion_comment()` | discussion_mgr | Post comment | `dict` |
| `update_discussion_answer()` | discussion_mgr | Mark answer | `dict` |
| `get_access_token()` | github_app | Get token | `str` |
| `validate_token()` | github_app | Validate token | `dict` |
| `handle_oauth_callback()` | github_app | OAuth callback | `dict` |
| `refresh_token()` | github_app | Refresh token | `str` |
| `issue_token()` | token_broker | Issue token | `str` |
| `verify_token()` | token_broker | Verify token | `dict` |
| `revoke_token()` | token_broker | Revoke token | `bool` |
| `rotate_tokens()` | token_broker | Rotate tokens | `dict` |

---

## Examples

### Posting to GitHub

```python
from codex.github.mcp_poster import MCPPoster

poster = MCPPoster(
    repo_owner="Aries-Serpent",
    repo_name="_codex_",
    token="ghp_xxxxxxxxxxxx"
)

# Post status update on PR
poster.post_comment(
    pr_number=42,
    comment="✅ API documentation phase complete\n\n" +
            "**Coverage:** 4.3% → 20%\n" +
            "**Signatures:** 200+ documented"
)

# Post approval review
poster.post_review(
    pr_number=42,
    review_body="Excellent documentation quality",
    event="APPROVE"
)

# Create tracking issue
poster.post_issue(
    title="Document remaining 300 API signatures",
    body="Continue expanding API documentation for Phase 13 readiness",
    labels=["docs", "phase-13"]
)
```

### GitHub Authentication

```python
from codex.auth.github_app import GitHubAppAuth

auth = GitHubAppAuth(
    app_id="123456",
    private_key=open("private_key.pem").read(),
    client_id="Iv1.xxx",
    client_secret="ghp_xxx"
)

# Get access token for installation
token = auth.get_access_token(installation_id=98765)

# Validate token
claims = auth.validate_token(token)
print(f"User: {claims['user_id']}, Scope: {claims['scope']}")
```

### Token Management

```python
from codex.autonomy.token_broker import TokenBroker

broker = TokenBroker()

# Issue token
token = broker.issue_token(
    user_id="user@example.com",
    scope="write",
    ttl=3600  # 1 hour
)

# Verify token
claims = broker.verify_token(token)

# Revoke token
broker.revoke_token(token)
```

---

## Coverage Status

**Documented Signatures:** 18/78 (23%)  
**Next Phase:** Complete remaining integration functions

---

**Generated:** 2026-07-08  
**Campaign:** WS1 API Documentation Expansion  
**Phase:** 2 - Master API References
