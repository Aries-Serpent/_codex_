# Planset 04: Privacy-First Memory (PII Scrubbing)

**Planset ID:** PS-04  
**Priority:** P0 - Critical (Compliance)  
**Phase:** Pre-commit Cycle 1-2  
**Status:** 📋 Planned  
**Dependencies:** PS-06 (Knowledge Crawler)  
**Cognitive Brain Objective:** Ensure zero PII in RAG embeddings, maintain privacy compliance

---

## Context

**Problem:** RAG system stores raw customer data in embeddings
- Email addresses embedded
- IP addresses embedded
- Potential GDPR/CCPA violations

**Compliance Risk:** CRITICAL - Privacy violations, potential fines

**Solution:** Implement PII scrubbing before embedding generation

---

## Implementation Plan

### Pre-commit Cycle 1: PII Detection Implementation

**Goal:** Create robust PII detection and redaction system

**Tasks:**
- [ ] Implement `src/codex/knowledge/pii.py` with regex patterns
- [ ] Email detection (RFC 5322 compliant)
- [ ] IP address detection (IPv4, IPv6)
- [ ] Phone number detection (international formats)
- [ ] SSN/Tax ID detection
- [ ] Credit card number detection (Luhn algorithm)
- [ ] Comprehensive unit tests (95%+ coverage)

**Files to Create:**
- `src/codex/knowledge/pii.py` (~300 lines)
- `tests/test_pii_scrubber.py` (~400 lines)

**Patterns to Detect:**
```python
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
IPV4_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
IPV6_PATTERN = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
PHONE_PATTERN = r'\b(?:\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'
```

**Success Criteria:**
- [ ] All PII types detected
- [ ] False positive rate <1%
- [ ] Performance <10ms per document
- [ ] Tests covering edge cases

### Pre-commit Cycle 2: Integration & Validation

**Goal:** Integrate PII scrubber into RAG pipeline

**Tasks:**
- [ ] Update `src/codex/knowledge/vector_store.py`
- [ ] Add scrubbing before embedding generation
- [ ] Implement audit logging for scrubbed PII
- [ ] Create privacy compliance report
- [ ] Validate no PII in existing embeddings
- [ ] Backfill scrubbing for historical data

**Files to Modify:**
- `src/codex/knowledge/vector_store.py` (+50 lines)
- `src/codex/rag/indexer.py` (add scrubbing call)

**Integration Point:**
```python
# Before embedding
text = scrub_pii(document_text)
embedding = generate_embedding(text)
```

**Success Criteria:**
- [ ] Zero PII in new embeddings
- [ ] Audit trail complete
- [ ] Compliance validation passing
- [ ] Performance maintained

---

## PII Scrubbing Strategy

### Redaction Modes

**Mode 1: Token Replacement**
```
"Contact john.doe@example.com" → "Contact [EMAIL_REDACTED]"
"IP: 192.168.1.1" → "IP: [IP_REDACTED]"
```

**Mode 2: Semantic Preservation**
```
"Email john.doe@example.com" → "Email user@domain.com"
"IP 192.168.1.1" → "IP 10.0.0.1"
```

**Mode 3: Hash Preservation (for deduplication)**
```
"john.doe@example.com" → "email_abc123"
```

### Audit Trail

```python
{
    "timestamp": "2026-01-08T...",
    "document_id": "doc_123",
    "pii_found": ["email", "ip"],
    "redactions": 2,
    "mode": "token_replacement"
}
```

---

## Success Metrics

- **PII Detection Rate:** 99.9%+
- **False Positives:** <1%
- **Performance:** <10ms per document
- **Compliance Score:** 100%
- **Audit Coverage:** 100% of operations

---

## Cognitive Brain Integration

**Patterns Learned:**
1. PII detection regex patterns
2. Privacy-first design principles
3. Audit trail implementation
4. Compliance validation strategies

**Reusable Utilities:**
1. `pii.py` - Generic PII scrubber
2. Privacy compliance checker
3. Audit logging decorators

---

**Created:** 2026-01-08  
**Agent:** GitHub Copilot (PR #2750)
