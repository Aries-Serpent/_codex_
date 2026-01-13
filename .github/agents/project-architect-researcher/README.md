# Project Architect Researcher Agent

**Version**: 1.0.0  
**Status**: Production  
**Maturity**: Tier 1  
**Test Coverage**: 100% (10/10 tests passing)

## Purpose

Generates research artifacts and structured documentation for AI knowledge platforms, enabling efficient research and architecture analysis.

## Features

- **Documentation Discovery**: Automatically finds Markdown, JSON, YAML, and text files
- **Source Parsing**: Extracts content, metadata, and citations
- **Artifact Creation**: Organizes sources into structured research artifacts
- **Multiple Export Formats**: JSON, Markdown, and YAML
- **Citation Extraction**: Automatically extracts links and references
- **Report Generation**: Provides statistics and summaries

## Quick Start

```bash
# Scan directory and create artifact
python -m project_architect_researcher \
  --source-dir ./docs \
  --output ./artifacts \
  --title "Project Documentation" \
  --tags "docs,research" \
  --report

# Output different format
python -m project_architect_researcher \
  --source-dir ./docs \
  --output ./artifacts \
  --format markdown
```

## Installation

```bash
pip install -r requirements.txt
```

Requirements:
- Python 3.11+
- click
- pyyaml

## Testing

```bash
pytest tests/ -v
```

**Test Coverage**: 100% (10/10 tests passing)

## Configuration

See `config/agent_config.yaml` for customization options.

## License

Part of the _codex_ repository.

## Maintainers

- GitHub Copilot Agent
- @mbaetiong
