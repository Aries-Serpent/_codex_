# HAR File Integration & Web Function Caching Plan

**Version**: 1.0.0  
**Date**: Previous Cycle-12-10  
**Status**: Planning Phase  
**Related**: Audit Dashboard Enhancement, Web-Based Function Storage

---

## Executive Summary

This plan outlines the integration of HTTP Archive (HAR) file format for storing and caching web-based functions, API responses, and audit data. HAR files provide a standardized JSON format for capturing HTTP transactions, making them ideal for:

1. **Caching audit dashboard data** for offline viewing
2. **Storing API responses** for reproducible testing
3. **Recording web function executions** for debugging and analysis
4. **Creating portable audit snapshots** that include all web assets

---

## Table of Contents

1. [Background & Use Cases](#background--use-cases)
2. [Technical Architecture](#technical-architecture)
3. [Implementation Plan](#implementation-plan)
4. [HAR File Structure](#har-file-structure)
5. [Integration Points](#integration-points)
6. [Security Considerations](#security-considerations)
7. [Performance & Storage](#performance--storage)
8. [Testing Strategy](#testing-strategy)
9. [Operational Considerations](#operational-considerations)
10. [Future Enhancements](#future-enhancements)

---

## Background & Use Cases

### What are HAR Files?

HTTP Archive (HAR) files are JSON-formatted archive files that contain a complete record of web browser interactions with web pages. They capture:
- HTTP requests and responses
- Headers, cookies, and query parameters
- Response content (HTML, JSON, images, etc.)
- Timing information
- Cache information

### Primary Use Cases for Codex

#### 1. **Audit Dashboard Caching**
Store complete audit dashboard state including:
- All API calls to load artifacts
- Generated HTML and assets
- Interactive planning tool selections
- Allows offline viewing and analysis

#### 2. **API Response Caching**
Cache GitHub API responses for:
- Deterministic testing
- Offline development
- Rate limit mitigation
- Reproducible audit runs

#### 3. **Web Function Recording**
Record executions of web-based functions:
- Browser automation traces
- Playwright interactions
- API integration tests
- Performance profiling

#### 4. **Audit Artifact Bundling**
Include HAR files in `determinism-audit-*.zip`:
- Complete snapshot of audit execution
- All network requests during audit
- Reproducible environment capture

---

## Technical Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Codex ML System                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Audit      │      │  Dashboard   │      │  GitHub   │ │
│  │   Runner     │─────▶│  Generator   │─────▶│    API    │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                     │       │
│         │                      ▼                     │       │
│         │            ┌──────────────────┐           │       │
│         │            │   HAR Recorder   │           │       │
│         │            └──────────────────┘           │       │
│         │                      │                     │       │
│         ▼                      ▼                     ▼       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              HAR Cache Storage Layer                   │ │
│  │  - Request/Response Cache                              │ │
│  │  - Session Recording                                   │ │
│  │  - Playback Engine                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                      │                                       │
│                      ▼                                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          audit_artifacts/                              │ │
│  │          ├── audit_session.har                         │ │
│  │          ├── dashboard_assets.har                      │ │
│  │          └── github_api_cache.har                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **HAR Recorder**
   - Captures HTTP/HTTPS traffic
   - Integrates with existing tools (requests, httpx)
   - Optional: Browser-based capture via Playwright

2. **HAR Cache Storage**
   - Indexed HAR files for fast lookup
   - Cache invalidation strategies
   - Compression for large responses

3. **HAR Playback Engine**
   - Serves cached responses
   - Mock server for testing
   - Offline mode support

4. **HAR Integration Layer**
   - Hooks into audit pipeline
   - Dashboard generation
   - API client wrappers

---

## Implementation Plan

### Phase 1: Foundation (Pre-commit 1-4)

#### 1.1 Create HAR Utility Module

**File**: `scripts/space_traversal/har_utils.py`

```python
"""
HAR (HTTP Archive) utilities for caching and recording web functions.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import gzip

class HARRecorder:
    """Record HTTP requests/responses in HAR format."""
    
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.entries = []
        self.pages = []
        
    def record_request(self, request, response, timing):
        """
        Record a single HTTP transaction.
        
        TODO: Implementation needed
        - Parse request object (method, URL, headers, body)
        - Parse response object (status, headers, body, size)
        - Record timing information (send, wait, receive)
        - Format as HAR entry and append to self.entries
        - Link to appropriate page in self.pages
        """
        pass
    
    def save(self):
        """
        Save HAR file to disk.
        
        TODO: Implementation needed
        - Construct HAR JSON structure with version, creator, pages, entries
        - Write to self.output_path with proper formatting
        - Consider compression for large HAR files
        - Validate HAR format before saving
        """
        pass

class HARCache:
    """Cache HTTP responses using HAR format."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.index = {}
        
    def get(self, url: str, method: str = "GET") -> Optional[dict]:
        """
        Retrieve cached response.
        
        TODO: Implementation needed
        - Generate cache key from URL and method
        - Check self.index for entry existence
        - Verify cache entry hasn't expired
        - Load and return cached response data
        """
        pass
        
    def set(self, url: str, method: str, response: dict, ttl: int = 3600):
        """
        Store response in cache.
        
        TODO: Implementation needed
        - Generate cache key from URL and method
        - Store response data with expiration timestamp
        - Update self.index with cache entry metadata
        - Consider size limits and eviction policies
        """
        pass
        
    def clear(self, pattern: str = "*"):
        """
        Clear cache entries matching pattern.
        
        TODO: Implementation needed
        - Support glob patterns for URL matching
        - Remove matching entries from cache directory
        - Update self.index to reflect deletions
        - Log cleared entries for debugging
        """
        pass

class HARPlayer:
    """Replay HTTP requests from HAR file."""
    
    def __init__(self, har_file: Path):
        self.har_file = har_file
        self.har_data = {}
        
    def find_response(self, url: str, method: str = "GET") -> Optional[dict]:
        """Find matching response in HAR."""
        pass
        
    def serve_mock(self, host: str = "localhost", port: int = 8000):
        """Start mock HTTP server from HAR."""
        pass
```

#### 1.2 Create Tests

**File**: `tests/space_traversal/test_har_utils.py`

- Test HAR recording
- Test cache hit/miss
- Test playback
- Test compression
- Test expiration

#### 1.3 Add Documentation

**File**: `docs/capabilities/har_integration.md`

- HAR format overview
- Usage examples
- Configuration options
- Best practices

### Phase 2: Integration (Pre-commit 5-8)

#### 2.1 Integrate with Audit Runner

Modify `scripts/space_traversal/audit_runner.py`:

```python
from har_utils import HARRecorder

def run_full(cfg):
    # Initialize HAR recorder
    har_recorder = HARRecorder(
        output_path=Path("audit_artifacts/audit_session.har")
    )
    
    # Wrap HTTP calls
    with har_recorder.recording():
        # ... existing audit code ...
        pass
    
    har_recorder.save()
```

#### 2.2 Add HAR to Dashboard Generator

Modify `scripts/generate_audit_dashboard.py`:

```python
from har_utils import HARCache, HARRecorder

def generate_with_har_caching(artifacts, reports, manifest, output_path):
    """Generate dashboard with HAR-cached assets."""
    
    har_cache = HARCache(Path("audit_artifacts/.har_cache"))
    
    # Cache external resources (CDNs, fonts, etc.)
    # Generate self-contained HTML with embedded assets
    
    # Record generation process
    har_recorder = HARRecorder(
        Path("audit_artifacts/dashboard_generation.har")
    )
```

#### 2.3 GitHub API Caching

**File**: `scripts/space_traversal/github_har_cache.py`

```python
"""
GitHub API caching using HAR format.
Reduces rate limit pressure and enables offline development.
"""

from har_utils import HARCache
import httpx

class GitHubHARClient:
    """GitHub API client with HAR caching."""
    
    def __init__(self, token: str, cache_ttl: int = 3600):
        self.client = httpx.Client()
        self.har_cache = HARCache(Path(".cache/github_api"))
        self.token = token
        self.cache_ttl = cache_ttl
        
    def get(self, url: str, use_cache: bool = True):
        """GET request with HAR caching."""
        if use_cache:
            cached = self.har_cache.get(url, "GET")
            if cached:
                return cached
        
        response = self.client.get(url, headers={"Authorization": f"token {self.token}"})
        
        if use_cache and response.status_code == 200:
            self.har_cache.set(url, "GET", response.json(), self.cache_ttl)
        
        return response.json()
```

### Phase 3: Dashboard Enhancement (Pre-commit 9-12)

#### 3.1 Add HAR Viewer to Dashboard

Enhance `scripts/planning_components.py` to include:

- HAR file browser
- Request/response inspector
- Timing waterfall chart
- Cache statistics

#### 3.2 HAR Export Feature

Add button to export current dashboard session as HAR:

```javascript
function exportSessionAsHAR() {
    const har = {
        log: {
            version: "1.2",
            creator: {
                name: "Audit Dashboard",
                version: "1.0.0"
            },
            pages: [],
            entries: [
                // All dashboard API calls
                // All resource loads
                // All interactive selections
            ]
        }
    };
    
    // Download HAR file
    downloadFile('dashboard_session.har', JSON.stringify(har, null, 2));
}
```

### Phase 4: Testing & Optimization (Pre-commit 13-16)

#### 4.1 Performance Testing

- Measure cache hit rates
- Compare HAR vs direct API calls
- Test with large audit artifacts
- Benchmark compression ratios

#### 4.2 Integration Testing

- Test offline mode
- Test with expired cache
- Test concurrent access
- Test cache invalidation

#### 4.3 Documentation

- Update README.md
- Add HAR usage guide
- Create troubleshooting guide
- Add examples

---

## HAR File Structure

### Standard HAR Format

```json
{
  "log": {
    "version": "1.2",
    "creator": {
      "name": "Codex Audit System",
      "version": "1.5.0"
    },
    "pages": [{
      "startedDateTime": "Previous Cycle-12-10T22:00:00.000Z",
      "id": "page_1",
      "title": "Audit Run",
      "pageTimings": {
        "onContentLoad": 1200,
        "onLoad": 2500
      }
    }],
    "entries": [{
      "startedDateTime": "Previous Cycle-12-10T22:00:01.000Z",
      "time": 150,
      "request": {
        "method": "GET",
        "url": "https://api.github.com/repos/Aries-Serpent/_codex_/commits",
        "httpVersion": "HTTP/1.1",
        "headers": [],
        "queryString": [],
        "cookies": [],
        "headersSize": -1,
        "bodySize": 0
      },
      "response": {
        "status": 200,
        "statusText": "OK",
        "httpVersion": "HTTP/1.1",
        "headers": [],
        "cookies": [],
        "content": {
          "size": 12345,
          "mimeType": "application/json",
          "text": "{...}",
          "encoding": "utf-8"
        },
        "redirectURL": "",
        "headersSize": -1,
        "bodySize": 12345
      },
      "cache": {},
      "timings": {
        "blocked": 0,
        "dns": 5,
        "connect": 20,
        "send": 1,
        "wait": 100,
        "receive": 24,
        "ssl": 15
      }
    }]
  }
}
```

### Custom Extensions for Codex

```json
{
  "log": {
    "_codex": {
      "auditRunId": "run_20251210_220000",
      "auditVersion": "1.5.0",
      "capabilities": [],
      "metrics": {
        "totalRequests": 45,
        "cacheHits": 12,
        "cacheMisses": 33,
        "totalTime": 5400
      }
    }
  }
}
```

---

## Integration Points

### 1. Audit Runner

```python
# scripts/space_traversal/audit_runner.py

def cmd_run(args, cfg):
    """Run audit with HAR recording."""
    har_recorder = HARRecorder(Path("audit_artifacts/audit_session.har"))
    
    try:
        with har_recorder.recording():
            # Existing audit logic
            pass
    finally:
        har_recorder.save()
```

### 2. Dashboard Generator

```python
# scripts/generate_audit_dashboard.py

def main():
    """Generate dashboard with HAR caching."""
    har_cache = HARCache(Path(".cache/dashboard"))
    
    # Load artifacts with caching
    # Generate HTML with cached assets
    
    # Export session HAR
    har_recorder.export("audit_artifacts/dashboard_session.har")
```

### 3. GitHub API Client

```python
# New file: scripts/space_traversal/github_client.py

class GitHubClient:
    def __init__(self, har_cache_enabled=True):
        self.har_cache = HARCache(Path(".cache/github")) if har_cache_enabled else None
```

### 4. Determinism Workflow

```yaml
# .github/workflows/determinism.yml

- name: Generate audit dashboard with HAR
  run: |
    python scripts/generate_audit_dashboard.py --enable-har
    
- name: Upload artifacts including HAR files
  uses: actions/upload-artifact@v4
  with:
    name: determinism-audit-${{ github.run_number }}
    path: |
      index.html
      audit_artifacts/**
      audit_artifacts/*.har
```

---

## Security Considerations

### 1. Sensitive Data Filtering

**Problem**: HAR files Phase 5 contain sensitive data (tokens, passwords, API keys)

**Solution**:
```python
class SecureHARRecorder(HARRecorder):
    """HAR recorder with sensitive data filtering."""
    
    SENSITIVE_HEADERS = ['authorization', 'cookie', 'x-api-key']
    SENSITIVE_PATTERNS = [r'token=\w+', r'key=\w+', r'password=\w+']
    
    def sanitize_request(self, request):
        """Remove sensitive data from request."""
        for header in self.SENSITIVE_HEADERS:
            if header in request['headers']:
                request['headers'][header] = '[REDACTED]'
        return request
```

### 2. Access Control

- Store HAR files in secure locations
- Add to `.gitignore`
- Encrypt sensitive HAR files
- Set proper file permissions

### 3. Data Retention

- Auto-delete old HAR files
- Configurable retention period
- Compressed storage for archives

---

## Performance & Storage

### Storage Estimates

| Item | Uncompressed | Compressed (gzip) | Retention |
|------|--------------|-------------------|-----------|
| Audit Session HAR | 5-10 MB | 500KB - 1MB | 30 days |
| Dashboard Generation HAR | 1-2 MB | 100-200 KB | 7 days |
| GitHub API Cache | 20-50 MB | 2-5 MB | 24 hours |
| Per-run total | 25-60 MB | 2.5-6 MB | Varies |

### Optimization Strategies

1. **Selective Recording**
   - Only record relevant requests
   - Skip large binary responses
   - Filter by content type

2. **Compression**
   - gzip compression for storage
   - Brotli for transmission
   - Automatic compression >1MB

3. **Indexing**
   - SQLite index for fast lookup
   - URL-based hashing
   - LRU cache eviction

4. **Chunking**
   - Split large HAR files
   - Per-page HAR files
   - Lazy loading

---

## Testing Strategy

### Unit Tests

```python
# tests/space_traversal/test_har_utils.py

def test_har_recorder_basic():
    """Test basic HAR recording."""
    recorder = HARRecorder(Path("/tmp/test.har"))
    recorder.record_request(mock_request, mock_response, mock_timing)
    recorder.save()
    assert Path("/tmp/test.har").exists()

def test_har_cache_hit():
    """Test cache hit scenario."""
    cache = HARCache(Path("/tmp/cache"))
    cache.set("http://example.com", "GET", {"data": "test"})
    result = cache.get("http://example.com", "GET")
    assert result == {"data": "test"}

def test_har_sanitization():
    """Test sensitive data removal."""
    recorder = SecureHARRecorder(Path("/tmp/secure.har"))
    request = {"headers": {"authorization": "Bearer secret"}}
    sanitized = recorder.sanitize_request(request)
    assert sanitized["headers"]["authorization"] == "[REDACTED]"
```

### Integration Tests

```python
def test_audit_with_har_recording():
    """Test full audit run with HAR recording."""
    # Run audit
    # Verify HAR file created
    # Verify HAR contains expected entries
    # Verify sensitive data redacted

def test_dashboard_with_har_cache():
    """Test dashboard generation with HAR caching."""
    # Generate dashboard
    # Verify cache used
    # Verify offline mode works
```

---

## Operational Considerations

### Known Issues & Limitations

#### 1. CodeQL Repository Size Limit

**Issue**: Repository exceeds 10MB limit (11.2MB), causing CodeQL scans to skip.

**Impact**: Security scanning not performed on Python code.

**Mitigation Options**:
- Use alternative security scanning tools (Bandit, Semgrep)
- Split large files into smaller modules
- Use CodeQL locally with higher limits
- Document security review process

**Action Items**:
```yaml
# Add to .github/workflows/security.yml
- name: Run Bandit Security Scan
  run: |
    pip install bandit
    bandit -r scripts/ src/ -f json -o bandit-report.json
```

#### 2. Git Command Failures in CI

**Issue**: CI tries to access files across different commits.

**Error Example**:
```
fatal: path 'scripts/planning_components.py' exists on disk, 
but not in 'db45016d98daf73e5cab5b73d88b39602343d6e5'
```

**Root Cause**: New files added in later commits aren't in base commit.

**Mitigation**:
- Ensure CI checkouts correct commit range
- Use `git diff --name-only` with proper commit refs
- Add error handling for missing files

**Action Items**:
```yaml
# Update workflow to handle missing files
- name: Check changed files
  run: |
    git fetch origin ${{ github.base_ref }}
    git diff --name-only origin/${{ github.base_ref }}...HEAD || true
```

### Monitoring & Logging

```python
# Add to har_utils.py

import logging

logger = logging.getLogger(__name__)

class HARRecorder:
    def __init__(self, output_path, enable_logging=True):
        self.logger = logger if enable_logging else None
        
    def record_request(self, request, response, timing):
        if self.logger:
            self.logger.info(f"Recording: {request.method} {request.url}")
            self.logger.debug(f"Response size: {len(response.content)} bytes")
```

### Configuration

```yaml
# Add to config files
har:
  enabled: true
  cache_dir: ".cache/har"
  retention_days: 30
  compress: true
  sanitize_sensitive: true
  max_entry_size_mb: 10
  excluded_patterns:
    - "*.jpg"
    - "*.png"
    - "*.woff2"
```

---

## Future Enhancements

### Phase 5+: Advanced Features

1. **HAR Diff Tool**
   - Compare HAR files across audit runs
   - Detect API changes
   - Performance regression detection

2. **HAR Merge**
   - Combine multiple HAR files
   - De-duplicate entries
   - Create master archive

3. **HAR Analytics**
   - Request distribution analysis
   - Response time trends
   - Cache efficiency metrics
   - Dashboard visualizations

4. **HAR Replay Testing**
   - Automated replay of HAR sessions
   - Regression testing
   - Load testing from HAR

5. **Browser Integration**
   - Chrome DevTools export
   - Firefox HAR export
   - Playwright HAR capture

6. **HAR to Mock Server**
   - Generate mock API from HAR
   - Dynamic response generation
   - Scenario-based testing

---

## Success Criteria

### Functional Requirements

- ✅ HAR recording works for HTTP/HTTPS requests
- ✅ HAR caching reduces API calls by 50%+
- ✅ Offline mode works with cached HAR
- ✅ Sensitive data properly redacted
- ✅ HAR files included in audit artifacts

### Non-Functional Requirements

- ✅ HAR file size <10MB per audit run
- ✅ Cache hit rate >60%
- ✅ Performance overhead <10%
- ✅ Storage <100MB per month
- ✅ Compatible with existing workflows

### Documentation Requirements

- ✅ Usage guide published
- ✅ API documentation complete
- ✅ Examples provided
- ✅ Troubleshooting guide available

---

## Implementation Checklist

### Foundation
- [ ] Create `har_utils.py` module
- [ ] Implement `HARRecorder` class
- [ ] Implement `HARCache` class
- [ ] Implement `HARPlayer` class
- [ ] Add unit tests (15+ test cases)
- [ ] Add documentation

### Integration
- [ ] Integrate with audit runner
- [ ] Add to dashboard generator
- [ ] Create GitHub API HAR client
- [ ] Update determinism workflow
- [ ] Add integration tests

### Enhancement
- [ ] Add HAR viewer to dashboard
- [ ] Implement export feature
- [ ] Add cache statistics
- [ ] Create HAR diff tool
- [ ] Performance optimization

### Operations
- [ ] Document known limitations
- [ ] Add monitoring/logging
- [ ] Configure retention policies
- [ ] Setup CI/CD integration
- [ ] Create runbook

---

## References

- [HAR 1.2 Spec](http://www.softwareishard.com/blog/har-12-spec/)
- [HAR Viewer](http://www.softwareishard.com/har/viewer/)
- [Python HAR Parser](https://github.com/JustusW/haralyzer)
- [Chrome DevTools HAR](https://developer.chrome.com/docs/devtools/network/reference/)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Previous Cycle-12-10 | Copilot | Initial plan created |

---

**Next Steps**: Review this plan with stakeholders, prioritize features, and begin Phase 1 implementation.
