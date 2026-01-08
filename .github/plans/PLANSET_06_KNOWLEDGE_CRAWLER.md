# Planset 06: Knowledge Crawler Service Operationalization

**Planset ID:** PS-06  
**Priority:** P0 - Critical  
**Phase:** Pre-commit Cycle 1-4  
**Status:** 📋 Planned  
**Dependencies:** PS-01 (Configuration)  
**Cognitive Brain Objective:** Transform ad-hoc script into resilient service with state awareness

---

## Context

**Problem:** `scripts/zendesk_docs_fetch.py` is standalone script without state tracking
- No drift detection
- Full re-fetch every run
- No incremental updates
- Inefficient and slow

**Solution:** Refactor into service with "Check and Pull" sync logic

---

## Implementation Plan

### Pre-commit Cycle 1-2: Service Core

**Goal:** Create ZendeskKnowledgeSync service

**Tasks:**
- [ ] Create `src/services/crawler/zendesk_sync.py`
- [ ] Implement state management (`data/zendesk_api_index.json`)
- [ ] Add drift detection logic
- [ ] Implement incremental fetch
- [ ] Add error handling and retry logic
- [ ] Create service configuration in Hydra

**Files to Create:**
- `src/services/crawler/zendesk_sync.py` (~400 lines)
- `src/services/crawler/__init__.py`
- `conf/services/crawler.yaml` (~50 lines)
- `tests/services/test_zendesk_sync.py` (~500 lines)

**Check and Pull Logic:**
```python
def check_and_pull(self):
    local_index = load_index()
    remote_articles = fetch_article_metadata()
    
    for article in remote_articles:
        if needs_update(article, local_index):
            content = fetch_article_content(article['id'])
            save_to_raw(content)
            update_index(article['id'], article['updated_at'])
```

### Pre-commit Cycle 3: Integration

**Goal:** Connect to RAG pipeline

**Tasks:**
- [ ] Update `src/codex/ingest/adapter.py`
- [ ] Add crawler → RAG integration
- [ ] Implement content preprocessing
- [ ] Add PII scrubbing integration (PS-04)
- [ ] Configure automatic triggers

### Pre-commit Cycle 4: Deployment

**Goal:** Deploy as scheduled service

**Tasks:**
- [ ] Create GitHub Actions workflow
- [ ] Configure 6-hour sync schedule
- [ ] Add monitoring and alerting
- [ ] Implement health checks
- [ ] Document operational procedures

**Files to Create:**
- `.github/workflows/knowledge-sync.yml`
- `docs/services/KNOWLEDGE_CRAWLER.md`

---

## Success Metrics

- **Sync Drift:** <1 hour
- **Bandwidth Reduction:** 80% (incremental only)
- **Reliability:** 99.9% uptime
- **Performance:** <5min per sync cycle

---

**Created:** 2026-01-08  
**Agent:** GitHub Copilot (PR #2750)
