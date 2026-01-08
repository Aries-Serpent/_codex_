# Tools Reference

> For AI Agents - Last Updated: 2025-12-24

This document provides reference information for tools available to AI agents.

## Available Tools

### File Operations

| Tool | Description | Parameters |
|------|-------------|------------|
| `read_file` | Read file contents | `path: str` |
| `write_file` | Write to file | `path: str, content: str` |
| `list_directory` | List directory contents | `path: str` |
| `search_files` | Search for patterns | `pattern: str, path: str` |

### Code Operations

| Tool | Description | Parameters |
|------|-------------|------------|
| `run_tests` | Execute test suite | `path: str, filter: str?` |
| `lint_code` | Run linters | `path: str` |
| `format_code` | Format code | `path: str` |
| `analyze_code` | Static analysis | `path: str` |

### Git Operations

| Tool | Description | Parameters |
|------|-------------|------------|
| `git_status` | Show repo status | none |
| `git_diff` | Show changes | `ref: str?` |
| `git_log` | Show commit history | `count: int?` |
| `git_blame` | Show line authors | `path: str` |

### External APIs

| Tool | Description | Parameters |
|------|-------------|------------|
| `web_search` | Search the web | `query: str` |
| `fetch_url` | Fetch URL content | `url: str` |

## Tool Usage Guidelines

### Best Practices

1. **Prefer reading over guessing** - Use `read_file` to verify file contents
2. **Validate before writing** - Check file exists with `list_directory` first
3. **Minimal changes** - Make the smallest change that solves the problem
4. **Test after changes** - Run relevant tests to verify correctness

### Common Patterns

#### Reading a file
```
Tool: read_file
Parameters: {"path": "src/main.py"}
```

#### Searching for patterns
```
Tool: search_files
Parameters: {"pattern": "def calculate", "path": "src/"}
```

#### Running tests
```
Tool: run_tests
Parameters: {"path": "tests/", "filter": "test_calculator"}
```

## Error Handling

Tools may return errors. Common error types:

| Error | Meaning | Action |
|-------|---------|--------|
| `FileNotFound` | Path doesn't exist | Verify path with `list_directory` |
| `PermissionDenied` | No access | Check file permissions |
| `Timeout` | Operation too slow | Retry with smaller scope |
| `RateLimited` | Too many requests | Wait and retry |

## Rate Limits

- File operations: 100/minute
- External APIs: 10/minute
- Git operations: 50/minute

## Security Restrictions

- Cannot access paths outside repository
- Cannot execute arbitrary shell commands
- Cannot modify `.git` directory
- Cannot access secrets directly

## See Also

- [Coding Standards](coding_standards.md)
- [Business Rules](business_rules.md)
