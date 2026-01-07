# [ADR]: Style - Line Length and Formatting
> Generated: 2025-11-11  
> Status: Accepted  
> Decision: Adopt Black default line length (88) and align ruff configuration

## Context

The repository needs consistent style guidelines for code formatting to ensure readability and maintainability across contributors.

## Decision

- **Line Length**: 88 characters (Black default)
- **Formatter**: Black for Python code formatting
- **Linter**: Ruff with E501 (line-length) ignored since Black handles it
- **Import Sorting**: isort or ruff's built-in import sorting

## Configuration

`.ruff.toml`:
```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
ignore = ["E501"]  # Line too long - handled by Black
```text

## Rationale

- Black's 88-character default is widely adopted in the Python community
- Reduces manual formatting effort
- Ensures consistent style across codebase
- Ruff provides fast linting with Black compatibility

## Consequences

- All new code should be formatted with Black
- Existing code can be reformatted incrementally
- Pre-commit hooks should enforce Black formatting
- E402 (import order) and E741 (ambiguous names) addressed case-by-case

## Status

Accepted - 2025-11-11
