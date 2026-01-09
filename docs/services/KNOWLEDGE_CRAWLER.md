# Knowledge Crawler Service - Operational Guide

**Service:** Zendesk Knowledge Synchronization  
**Version:** 2.0  
**Status:** Production Ready  
**Created:** 2026-01-09 (PS-06)  

---

## Overview

The Zendesk Knowledge Crawler Service implements "Check and Pull" synchronization to keep the Agent's knowledge base synchronized with Zendesk Help Center.

### Key Features

✅ **Incremental Sync** - Only fetch changed articles (80% bandwidth reduction)  
✅ **Drift Detection** - ETag and Last-Modified tracking  
✅ **PII Scrubbing** - Mandatory before disk writes  
✅ **State Management** - Persistent cache  
✅ **Error Handling** - Retry logic with exponential backoff  
✅ **JSON Dataset Export** - Structured data for ML pipelines

---

## Quick Start

```bash
# Incremental sync (default)
python -m src.services.crawler.zendesk_sync

# Full sync
python -m src.services.crawler.zendesk_sync --mode full

# Dry run
python -m src.services.crawler.zendesk_sync --dry-run

# With pipeline
python -m src.services.crawler.zendesk_sync --pipeline
```

---

## Architecture

```
Zendesk API → Check (Metadata) → Compare Cache → Pull (if changed)
    → PII Scrubbing → Disk Write → Cache Update → JSON Export
```

---

## Configuration

Edit `configs/services/zendesk_crawler.yaml`:

```yaml
sync_mode: incremental
retries: 3
monitoring:
  log_level: INFO
  alerts:
    max_failures: 5
```

---

## State Management

**Cache:** `data/zendesk_api_index.json`

Tracks article ETags, Last-Modified timestamps, and sync history for incremental updates.

---

## Output Structure

```
docs/vendors/zendesk/
└── YYYY-MM-DD/
    ├── <section>/<bucket>/*.html
    └── zendesk_knowledge_dataset.json
```

---

## Monitoring

**Success Metrics:**
- Sync Drift: <1 hour
- Success Rate: >95%
- Performance: <5 minutes per sync

---

## PII Scrubbing

PII scrubbing is **mandatory**. All content automatically scrubbed before disk writes.

Detection: Email, phone, credit cards, SSN, API keys  
Action: Automatic redaction with `[REDACTED]` markers  
Audit: All detections logged

---

## Testing

```bash
pytest tests/services/test_zendesk_sync.py -v
```

30+ comprehensive tests covering unit and integration scenarios.

---

## References

- [Service Implementation](../src/services/crawler/zendesk_sync.py)
- [Test Suite](../tests/services/test_zendesk_sync.py)
- [Configuration](../configs/services/zendesk_crawler.yaml)
- [PS-06 Planset](.github/plans/PLANSET_06_KNOWLEDGE_CRAWLER.md)

---

**Last Updated:** 2026-01-09  
**Status:** Production Ready
