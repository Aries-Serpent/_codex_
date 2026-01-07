# Infrastructure Basics

> For AI Agents - Last Updated: 2024-12-24

This document provides essential infrastructure knowledge for AI agents.

## Repository Structure

```
_codex_/
├── src/                 # Source code
│   ├── agent/           # Agent core logic
│   ├── config/          # Configuration modules
│   ├── mcp/             # MCP integration
│   ├── rag/             # RAG pipelines
│   └── verification/    # CoVe implementation
├── configs/             # YAML/JSON configuration
├── prompts/             # System and domain prompts
├── tests/               # Test suites
├── docs/                # Documentation
└── scripts/             # Utility scripts
```

## Key Configuration Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies |
| `configs/models.yaml` | Model selection config |
| `configs/rag_config.yaml` | RAG pipeline settings |
| `.semgrep/semgrep.yml` | Security scanning rules |

## Build & Test Commands

```bash
# Install dependencies
pip install -e .

# Run all tests
pytest tests/

# Run specific test file
pytest tests/config/test_openai_client.py

# Run with coverage
pytest --cov=src tests/

# Lint code
ruff check .

# Format code
ruff format .
```

## Common Paths

| Path | Contents |
|------|----------|
| `src/config/openai_client.py` | OpenAI client implementation |
| `src/agents/autonomous_runner.py` | Autonomous agent runner |
| `configs/` | All configuration files |
| `tests/` | All test files |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI API access |
| `GITHUB_CODEX` | Alternative API key |
| `PINECONE_API_KEY` | Vector store access |
| `LOG_LEVEL` | Logging verbosity |

## CI/CD Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `pr-checks.yml` | Pull request | Run tests and linting |
| `build-container-cache.yml` | Push to main | Build Docker images |
| `wiki-assemble.yml` | Push to main | Generate documentation |

## Dependencies

Key dependencies used in this repository:

| Package | Purpose |
|---------|---------|
| `openai` | OpenAI API client |
| `pytest` | Testing framework |
| `ruff` | Linting and formatting |
| `pydantic` | Data validation |

## Common Issues

1. **Import errors**: Ensure package is installed with `pip install -e .`
2. **API key missing**: Set `OPENAI_API_KEY` environment variable
3. **Test failures**: Check if dependencies are installed

## See Also

- [Tools Reference](tools_reference.md)
- [Coding Standards](coding_standards.md)
