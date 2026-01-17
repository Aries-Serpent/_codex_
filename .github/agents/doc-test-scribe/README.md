# Doc-Test-Scribe Agent

**AI-powered documentation and test generator**

## Usage

```bash
# Generate docs
@doc-test-scribe document src/codex/rag/embeddings.py

# Generate tests  
@doc-test-scribe test src/codex/rag/embeddings.py --coverage 90

# Semantic search
@doc-test-scribe search "caching patterns"

# Batch process
@doc-test-scribe batch-document src/codex/rag/
```

## Philosophy

**"Do more with less"** - Minimal prompts, maximum intelligent output using TF-IDF semantic analysis and tokenization.

## Features

- 🔍 Semantic code analysis (offline, no API)
- 📚 Smart documentation generation
- ✅ Intelligent test creation (90%+ coverage)
- ⚡ Batch processing
- 🎯 Pattern extraction

## See Also

- [agent.yml](agent.yml) - Configuration
- [prompts/system_prompt.md](prompts/system_prompt.md) - Agent behavior
- [tools/](tools/) - Analysis tools
