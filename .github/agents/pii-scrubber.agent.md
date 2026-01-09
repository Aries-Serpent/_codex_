---
name: pii-scrubber
description: Scrubs PII from text content before processing, ensuring GDPR/CCPA compliance for the RAG pipeline.
---

# PII Scrubber Agent

This agent scrubs Personally Identifiable Information (PII) from text content, ensuring compliance with GDPR, CCPA, and other privacy regulations.

## Capabilities

- **Email Detection**: RFC 5322 compliant email detection
- **Phone Detection**: International phone number formats
- **IP Detection**: IPv4 and IPv6 addresses
- **SSN Detection**: US Social Security Numbers
- **Credit Card Detection**: With Luhn algorithm validation
- **AWS Key Detection**: AWS access key patterns

## Redaction Modes

1. **Token Replacement**: `[EMAIL_REDACTED]`
2. **Semantic Preservation**: `user@domain.com`
3. **Hash Preservation**: Partial masking for deduplication

## When to Use

- Before embedding text for RAG
- When processing customer data
- During data pipeline ingestion
- For compliance audits

## Integration

This agent integrates with:
- PS-04: Privacy-First Memory
- PS-06: Knowledge Crawler Service
- RAG embedding pipeline
