# Documentation Sync Validator - Real-World Examples

## Example 1: Weekly Documentation Audit

### Scenario
Run a comprehensive weekly audit of all project documentation to identify stale content and broken links.

### Command
```bash
python -m documentation_sync_validator.src.agent validate . \
  --output-format json \
  --save-report audit_$(date +%Y%m%d).json
```

### Expected Output
```json
[
  {
    "file": "docs/deprecated_api.md",
    "type": "freshness",
    "severity": "medium",
    "description": "Documentation is stale (150 days old)",
    "confidence": 1.0
  },
  {
    "file": "README.md",
    "type": "broken_link",
    "severity": "medium",
    "description": "Broken link: docs/removed_guide.md - File not found"
  }
]
```

### Actions Taken
1. Update deprecated_api.md with current information
2. Remove broken link from README.md
3. Schedule review of all docs >90 days old

---

## Example 2: Pre-Release Documentation Validation

### Scenario
Before a major release, ensure all documentation is fresh and accurately reflects the codebase.

### Command
```bash
python -m documentation_sync_validator.src.agent validate docs/ \
  --freshness-threshold 30 \
  --semantic-drift-threshold 0.8 \
  --fail-on-stale
```

### Expected Output
```
Documentation Validation Report
==================================================
Total Issues: 3

[MEDIUM] docs/api_reference.md
  Type: semantic_drift
  Semantic drift detected with src/api.py (similarity: 0.62)
  Mismatched concepts: ['new_endpoint', 'authentication_v2']

[LOW] docs/installation.md
  Type: freshness
  Documentation is aging (45 days old)

[MEDIUM] docs/examples.md
  Type: broken_link
  Broken link: examples/advanced.py - File not found
```

### Actions Taken
1. Update API reference with new endpoints and authentication changes
2. Refresh installation guide
3. Fix broken link to examples file

---

## Example 3: Semantic Drift Detection After Refactor

### Scenario
After a major codebase refactor, check which documentation has become outdated.

### Command
```bash
python -m documentation_sync_validator.src.agent semantic-check docs/ src/ \
  --output-format markdown
```

### Expected Output
```markdown
# Semantic Drift Report

## CRITICAL (1)
- **docs/architecture.md** vs **src/core/engine.py**: 0.08 similarity
  - Mismatched: async_processing, event_loop, worker_pool

## HIGH (2)
- **docs/database.md** vs **src/db/connection.py**: 0.15 similarity
  - Mismatched: connection_pooling, transaction_manager

## MEDIUM (3)
- **docs/api.md** vs **src/api/routes.py**: 0.45 similarity
  - Mismatched: rate_limiting, cache_headers
```

### Actions Taken
1. Completely rewrite architecture.md to match new async architecture
2. Update database.md with new connection pooling details
3. Add API documentation for rate limiting and caching

---

## Example 4: Continuous Monitoring with Alerts

### Scenario
Set up continuous monitoring that alerts when documentation quality degrades.

### Command
```bash
python -m documentation_sync_validator.src.agent monitor \
  --watch docs/ \
  --alert-on-drift \
  --webhook $SLACK_WEBHOOK \
  --check-interval 3600
```

### Expected Behavior
- Runs validation every hour
- Sends Slack alert when:
  - New broken links detected
  - Semantic drift increases significantly
  - Docs become stale
- Maintains historical metrics in cognitive brain

---

## Example 5: CI/CD Integration

### Scenario
Integrate documentation validation into GitHub Actions CI/CD pipeline.

### GitHub Workflow
```yaml
name: Documentation Validation
on:
  pull_request:
    paths:
      - 'docs/**'
      - 'src/**'
      - '*.md'

jobs:
  validate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pyyaml
      
      - name: Validate documentation
        run: |
          python -m documentation_sync_validator.src.agent validate . \
            --output-format json \
            --save-report validation_report.json
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: documentation-validation-report
          path: validation_report.json
      
      - name: Comment on PR
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('validation_report.json', 'utf8'));
            const issues = report.length;
            const comment = `## 📚 Documentation Validation Results\n\n` +
              `Found ${issues} issue(s). Please review and fix before merging.\n\n` +
              `See artifacts for detailed report.`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

---

## Example 6: Schema Validation for Standardized Docs

### Scenario
Enforce that all API documentation follows a standard schema.

### Schema Definition (schema.yaml)
```yaml
required:
  - title
  - version
  - author
  - last_updated
  - status
properties:
  status:
    enum: [draft, review, published, deprecated]
  version:
    pattern: '^\d+\.\d+\.\d+$'
```

### Command
```bash
python -m documentation_sync_validator.src.agent validate-schema docs/api/*.md \
  --schema schema.yaml \
  --output-format markdown
```

### Expected Output
```markdown
# Schema Validation Report

## Violations (3)

### docs/api/auth.md
- ❌ Missing required field: `last_updated`
- ❌ Missing required field: `status`

### docs/api/database.md
- ❌ Invalid version format: `v1.2` (expected: X.Y.Z)

### docs/api/endpoints.md
- ✅ All required fields present
- ✅ Schema valid
```

---

## Example 7: Link Validation for External Dependencies

### Scenario
Check that all external documentation links (e.g., to dependency docs) are still valid.

### Command
```bash
python -m documentation_sync_validator.src.agent validate-links docs/ \
  --check-external \
  --timeout 10 \
  --output-format json
```

### Expected Output
```json
[
  {
    "file": "docs/dependencies.md",
    "type": "broken_link",
    "severity": "medium",
    "description": "External link timeout: https://old-deprecated-lib.com/docs",
    "confidence": 0.9
  },
  {
    "file": "docs/references.md",
    "type": "broken_link",
    "severity": "high",
    "description": "External link 404: https://example.com/nonexistent",
    "confidence": 1.0
  }
]
```

### Actions Taken
1. Update dependency docs link to new official site
2. Remove reference to nonexistent page
3. Add checks for external link health to monitoring

---

## Example 8: Freshness Report for Management

### Scenario
Generate an executive summary of documentation health for management review.

### Command
```bash
python -m documentation_sync_validator.src.agent validate . \
  --output-format markdown \
  --include-metrics \
  > docs_health_report.md
```

### Expected Output
```markdown
# Documentation Health Report
**Date**: 2026-01-12

## Summary
- **Total Files**: 47
- **Fresh**: 32 (68%)
- **Aging**: 10 (21%)
- **Stale**: 5 (11%)
- **Broken Links**: 3
- **High Drift**: 2

## Recommendations
1. Update 5 stale documents (>90 days)
2. Fix 3 broken links
3. Address 2 high-drift cases immediately

## Trend Analysis
- Documentation freshness improving (+5% vs last month)
- Broken links stable (0 new)
- Semantic drift increased after Q4 refactor
```

---

**These examples demonstrate real-world usage patterns for the Documentation Sync Validator agent across different scenarios and workflows.**
