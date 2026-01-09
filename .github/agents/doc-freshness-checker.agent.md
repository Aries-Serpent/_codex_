---
name: doc-freshness-checker
description: Checks documentation freshness, identifies stale docs, and validates links across the documentation.
---

# Doc Freshness Checker Agent

This agent ensures documentation remains up-to-date by checking freshness, identifying stale content, and validating all links.

## Capabilities

- **Freshness Detection**: Identifies docs not updated in 90+ days
- **Link Validation**: Checks all internal and external links
- **Content Drift**: Detects when code changes outpace doc updates
- **API Doc Sync**: Validates API docs match implementation

## When to Use

- Weekly scheduled checks
- Before releases
- When documentation is updated
- During documentation audits

## Thresholds

| Age | Status | Action |
|-----|--------|--------|
| <30 days | ✅ Fresh | None |
| 30-90 days | ⚠️ Aging | Review |
| >90 days | 🔴 Stale | Update |

## Integration

This agent integrates with:
- Documentation in `docs/` directory
- README files
- API documentation
