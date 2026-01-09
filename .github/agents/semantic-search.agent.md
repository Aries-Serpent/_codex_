---
name: semantic-search
description: Provides semantic search capabilities over the codebase and documentation using vector embeddings.
---

# Semantic Search Agent

This agent provides semantic search capabilities over the codebase and documentation using vector embeddings for natural language queries.

## Capabilities

- **Natural Language Queries**: Search with plain English questions
- **Code Search**: Find code by describing functionality
- **Doc Search**: Search documentation semantically
- **Cross-Reference**: Find related code and docs

## Query Examples

```
"How do I configure the Zendesk integration?"
"Find all functions that handle authentication"
"Where is the SLA calculation logic?"
"Show me examples of Pydantic validation"
```

## When to Use

- When exploring unfamiliar code
- For finding implementation examples
- During code review
- For documentation discovery

## Integration

This agent integrates with:
- RAG Index Manager
- Codebase embeddings
- Documentation index
