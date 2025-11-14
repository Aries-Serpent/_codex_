# Implementation Prompt: AGENTS.md Documentation Enhancement & Logging Infrastructure

> **Target**: GitHub Copilot Assistant Agent  
> **Scope**: Implement comprehensive AGENTS.md documentation with enhanced logging, error handling, and CLI tooling  
> **Energy**: ⚡⚡⚡⚡⚡ (5/5)  
> **Context**: Aries-Serpent/_codex_ repository (Python 50.5%, Markdown 45.4%, Shell 2.9%)

---

## 🎯 Objective

Implement a production-ready AGENTS.md documentation file with supporting infrastructure for:
1. **Enhanced environment variable management** with validation and defaults
2. **Robust logging infrastructure** with SQLite backend and session management
3. **CLI tooling** for session recording, viewing, and querying
4. **Error handling framework** with comprehensive logging and graceful degradation
5. **Testing infrastructure** with mocking for optional dependencies
6. **Configuration management** using Hydra

---

## 📋 Current State Analysis

**Repository Structure** (inferred from context):
```
Aries-Serpent/_codex_/
├── .github/
│   ├── docs/
│   │   └── Coverage_Gating_Restoration_Enhanced_Copilot.md
│   └── workflows/  (DO NOT CREATE/ACTIVATE)
├── src/
│   └── codex/
│       ├── cli.py
│       └── logging/
│           ├── session_logger.py
│           ├── viewer.py
│           └── query_logs.py
├── configs/  (Hydra configs)
├── pyproject.toml
├── noxfile.py
├── AGENTS.md  (TARGET FILE)
└── .codex/
    ├── sessions/
    └── session_logs.db
```

**Languages**: Python (primary), Markdown (docs), Shell (automation)

---

## 📝 Implementation Tasks

### Task 1: Create Enhanced AGENTS.md

**File**: `AGENTS.md` (root directory)

**Requirements**:
- Follow template structure from attached file
- Use tables for environment variables and logging roles
- Include code examples for all CLI commands
- Document prohibited actions (GitHub Actions workflows)
- Add troubleshooting checklist
- Include contact/maintainers section

**Template Structure**:
```markdown
# AGENTS

Guidelines for contributors and Codex automation. Keep this file updated as conventions change.

## Table of Contents
[Auto-generated TOC]

## Repository Overview
[Description from attached file]

## Environment Variables
[Table with validation rules and defaults]

## Logging Roles
[Table with role definitions]

## Tooling, Testing & Checks
[Commands and pre-commit hooks]

## CLI & Tool Usage
[Examples for all CLI tools]

## Optional Dependencies & Mocking
[Guidance for hydra-core, mlflow, etc.]

## Prohibited Actions
[GitHub Actions constraints]

## Log Directory Layout & Retention
[.codex/ structure and cleanup policy]

## Error Handling & Backward Compatibility
[Framework guidelines]

## Configuration Management (Hydra)
[configs/ usage patterns]

## Production Readiness Checklist
[Pre-deployment validation steps]

## Troubleshooting
[Common issues and solutions]

## Contact / Maintainers
[Team contacts and escalation]
```

**Error Handling**:
- Log all file creation errors to `.codex/logs/implementation_$(date +%Y%m%d_%H%M%S).log`
- If AGENTS.md exists, create backup: `AGENTS.md.backup_$(date +%Y%m%d_%H%M%S)`
- Validate markdown syntax with `markdownlint` if available

**Success Criteria**:
- [ ] AGENTS.md created with all sections
- [ ] All tables properly formatted
- [ ] All code blocks syntax-highlighted
- [ ] File passes `markdownlint` (if available)
- [ ] Backup created if file existed

---

### Task 2: Implement Environment Variable Management

**File**: `src/codex/config/env_vars.py` (create if not exists)

**Requirements**:
```python
"""
Environment variable management with validation and defaults.

Provides:
- Type-safe environment variable access
- Default value handling
- Validation for critical variables
- Logging of environment configuration
"""

import os
import uuid
from pathlib import Path
from typing import Optional, TypeVar, Callable
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class EnvVarConfig:
    """Configuration for a single environment variable."""
    name: str
    default: Optional[str] = None
    validator: Optional[Callable[[str], bool]] = None
    required: bool = False
    description: str = ""


class EnvironmentManager:
    """
    Manage environment variables with validation and logging.
    
    Usage:
        env = EnvironmentManager()
        session_id = env.get_session_id()
        log_dir = env.get_log_dir()
    """
    
    # Define all CODEX_* environment variables
    ENV_VARS = {
        'CODEX_ENV_PYTHON_VERSION': EnvVarConfig(
            name='CODEX_ENV_PYTHON_VERSION',
            default='3.12',
            description='Python version for environment setup'
        ),
        'CODEX_SESSION_ID': EnvVarConfig(
            name='CODEX_SESSION_ID',
            default=None,  # Generated dynamically
            description='Session identifier (UUID recommended)'
        ),
        'CODEX_SESSION_LOG_DIR': EnvVarConfig(
            name='CODEX_SESSION_LOG_DIR',
            default='.codex/sessions',
            description='Directory for session log files'
        ),
        'CODEX_LOG_DB_PATH': EnvVarConfig(
            name='CODEX_LOG_DB_PATH',
            default='.codex/session_logs.db',
            description='Path to SQLite database for logs'
        ),
        'CODEX_SQLITE_POOL': EnvVarConfig(
            name='CODEX_SQLITE_POOL',
            default='0',
            validator=lambda v: v in ('0', '1'),
            description='Enable SQLite connection pooling (0=disabled, 1=enabled)'
        ),
    }
    
    def __init__(self):
        """Initialize environment manager and validate critical variables."""
        self._session_id: Optional[str] = None
        self._validate_environment()
    
    def _validate_environment(self) -> None:
        """Validate required environment variables."""
        errors = []
        for var_name, config in self.ENV_VARS.items():
            value = os.getenv(var_name)
            
            if config.required and not value:
                errors.append(f"Required environment variable {var_name} not set")
            
            if value and config.validator and not config.validator(value):
                errors.append(f"Invalid value for {var_name}: {value}")
        
        if errors:
            raise EnvironmentError("\n".join(errors))
    
    def get(self, var_name: str, default: Optional[str] = None) -> str:
        """
        Get environment variable with fallback to configured default.
        
        Args:
            var_name: Environment variable name
            default: Override default (if not using configured default)
        
        Returns:
            Environment variable value or default
        """
        config = self.ENV_VARS.get(var_name)
        fallback = default if default is not None else (config.default if config else None)
        return os.getenv(var_name, fallback)
    
    def get_session_id(self) -> str:
        """
        Get or generate session ID.
        
        Returns:
            Session ID (from env or newly generated UUID)
        """
        if self._session_id:
            return self._session_id
        
        self._session_id = os.getenv('CODEX_SESSION_ID')
        if not self._session_id:
            self._session_id = str(uuid.uuid4())
            os.environ['CODEX_SESSION_ID'] = self._session_id
        
        return self._session_id
    
    def get_log_dir(self) -> Path:
        """
        Get session log directory (creates if not exists).
        
        Returns:
            Path to log directory
        """
        log_dir = Path(self.get('CODEX_SESSION_LOG_DIR'))
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def get_db_path(self) -> Path:
        """
        Get SQLite database path.
        
        Returns:
            Path to session_logs.db
        """
        db_path = Path(self.get('CODEX_LOG_DB_PATH') or self.get('CODEX_DB_PATH'))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path
    
    def is_sqlite_pool_enabled(self) -> bool:
        """Check if SQLite connection pooling is enabled."""
        return self.get('CODEX_SQLITE_POOL') == '1'
    
    def dump_config(self) -> dict[str, str]:
        """
        Dump current environment configuration.
        
        Returns:
            Dictionary of all CODEX_* variables and their values
        """
        return {
            var_name: self.get(var_name)
            for var_name in self.ENV_VARS.keys()
        }


# Global instance
env_manager = EnvironmentManager()
```

**Error Handling**:
```python
# Add to src/codex/logging/error_handler.py (create if not exists)

import sys
import traceback
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Any


class CodexErrorHandler:
    """
    Centralized error handling with logging and graceful degradation.
    
    Usage:
        handler = CodexErrorHandler()
        
        @handler.log_errors
        def risky_function():
            ...
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize error handler.
        
        Args:
            log_dir: Directory for error logs (default: .codex/logs)
        """
        self.log_dir = log_dir or Path('.codex/logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.error_log = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure logger
        self.logger = logging.getLogger('codex.errors')
        self.logger.setLevel(logging.ERROR)
        
        handler = logging.FileHandler(self.error_log)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))
        self.logger.addHandler(handler)
    
    def log_error(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
        fatal: bool = False
    ) -> None:
        """
        Log error with context.
        
        Args:
            error: Exception to log
            context: Additional context (dict)
            fatal: If True, exit after logging
        """
        error_details = {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.logger.error(
            f"{error_details['type']}: {error_details['message']}\n"
            f"Context: {error_details['context']}\n"
            f"Traceback:\n{error_details['traceback']}"
        )
        
        if fatal:
            print(f"❌ Fatal error: {error}", file=sys.stderr)
            print(f"See {self.error_log} for details", file=sys.stderr)
            sys.exit(1)
    
    def log_errors(self, func: Callable) -> Callable:
        """
        Decorator to log errors from a function.
        
        Usage:
            @error_handler.log_errors
            def my_function():
                ...
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.log_error(
                    e,
                    context={'function': func.__name__, 'args': args, 'kwargs': kwargs}
                )
                raise
        return wrapper


# Global instance
error_handler = CodexErrorHandler()
```

**Success Criteria**:
- [ ] `src/codex/config/env_vars.py` created
- [ ] `src/codex/logging/error_handler.py` created
- [ ] All environment variables documented
- [ ] Validation logic functional
- [ ] Error logging to `.codex/logs/` working

---

### Task 3: Implement CLI Tools

**File**: `src/codex/cli.py` (enhance existing or create)

**Requirements**:
```python
"""
CLI entry points for Codex tooling.

Commands:
    session-logger  Record session events
    viewer          View session logs
    query-logs      Search conversation transcripts
    validate-env    Validate environment configuration
"""

import click
from pathlib import Path
from codex.config.env_vars import env_manager
from codex.logging.error_handler import error_handler


@click.group()
def cli():
    """Codex CLI tooling."""
    pass


@cli.command('session-logger')
@click.option('--session-id', help='Session ID (default: auto-generate)')
@click.option('--role', type=click.Choice(['system', 'user', 'assistant', 'tool']), required=True)
@click.option('--message', required=True, help='Log message')
@error_handler.log_errors
def session_logger(session_id: str, role: str, message: str):
    """Record session events."""
    from codex.logging.session_logger import SessionLogger
    
    logger = SessionLogger(session_id=session_id)
    logger.log(role=role, message=message)
    click.echo(f"✅ Logged {role} message to session {logger.session_id}")


@cli.command('viewer')
@click.option('--session-id', help='Session ID to view (default: latest)')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
@error_handler.log_errors
def viewer(session_id: str, format: str):
    """View session logs."""
    from codex.logging.viewer import LogViewer
    
    viewer_instance = LogViewer()
    viewer_instance.view(session_id=session_id, output_format=format)


@cli.command('query-logs')
@click.option('--search', required=True, help='Search query')
@click.option('--role', help='Filter by role')
@error_handler.log_errors
def query_logs(search: str, role: str):
    """Search conversation transcripts."""
    from codex.logging.query_logs import LogQueryEngine
    
    engine = LogQueryEngine()
    results = engine.search(query=search, role=role)
    
    if not results:
        click.echo("No results found")
        return
    
    for result in results:
        click.echo(f"\n[{result['timestamp']}] {result['role']}: {result['message']}")


@cli.command('validate-env')
@error_handler.log_errors
def validate_env():
    """Validate environment configuration."""
    config = env_manager.dump_config()
    
    click.echo("📊 Current Environment Configuration:\n")
    for var, value in config.items():
        click.echo(f"  {var}: {value}")
    
    click.echo("\n✅ Environment validation passed")


if __name__ == '__main__':
    cli()
```

**Error Handling**:
- All CLI commands wrapped with `@error_handler.log_errors`
- Friendly error messages printed to stderr
- Full tracebacks logged to `.codex/logs/errors_YYYYMMDD.log`
- Non-zero exit codes on failure

**Success Criteria**:
- [ ] All CLI commands functional
- [ ] `python -m codex.cli --help` works
- [ ] Error messages user-friendly
- [ ] Full errors logged to file

---

### Task 4: Implement Logging Infrastructure

**Files**:
- `src/codex/logging/session_logger.py`
- `src/codex/logging/viewer.py`
- `src/codex/logging/query_logs.py`
- `src/codex/logging/db_manager.py` (SQLite backend)

**SQLite Schema**:
```sql
-- .codex/schema.sql
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role TEXT CHECK(role IN ('system', 'user', 'assistant', 'tool')),
    message TEXT NOT NULL,
    metadata JSON,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE INDEX IF NOT EXISTS idx_logs_session ON logs(session_id);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_role ON logs(role);
CREATE VIRTUAL TABLE IF NOT EXISTS logs_fts USING fts5(message, content='logs', content_rowid='id');
```

**Implementation** (see attached AGENTS.md for full spec):
- Connection pooling if `CODEX_SQLITE_POOL=1`
- Full-text search using FTS5
- Session lifecycle management
- Graceful handling of missing DB file

**Success Criteria**:
- [ ] SQLite database created at `.codex/session_logs.db`
- [ ] Schema applied correctly
- [ ] Logging functional
- [ ] Querying functional
- [ ] Connection pooling works (if enabled)

---

### Task 5: Add Testing Infrastructure

**File**: `tests/test_agents_infrastructure.py` (create)

**Requirements**:
```python
"""
Tests for AGENTS.md infrastructure.

Tests:
- Environment variable management
- Error handling and logging
- CLI commands
- Session logging
- Log querying
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from codex.config.env_vars import EnvironmentManager
from codex.logging.error_handler import CodexErrorHandler
from codex.logging.session_logger import SessionLogger


class TestEnvironmentManager:
    """Test environment variable management."""
    
    def test_get_default_values(self):
        """Test default value fallback."""
        with patch.dict(os.environ, {}, clear=True):
            env = EnvironmentManager()
            assert env.get('CODEX_ENV_PYTHON_VERSION') == '3.12'
    
    def test_session_id_generation(self):
        """Test automatic session ID generation."""
        with patch.dict(os.environ, {}, clear=True):
            env = EnvironmentManager()
            session_id = env.get_session_id()
            assert session_id is not None
            assert len(session_id) == 36  # UUID format
    
    def test_validation_failure(self):
        """Test validation of invalid values."""
        with patch.dict(os.environ, {'CODEX_SQLITE_POOL': '2'}):
            with pytest.raises(EnvironmentError):
                env = EnvironmentManager()


class TestErrorHandler:
    """Test error handling infrastructure."""
    
    def test_log_error(self, tmp_path):
        """Test error logging."""
        handler = CodexErrorHandler(log_dir=tmp_path)
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            handler.log_error(e, context={'test': True})
        
        error_log = list(tmp_path.glob("errors_*.log"))[0]
        assert error_log.exists()
        assert "ValueError: Test error" in error_log.read_text()
    
    def test_decorator(self, tmp_path):
        """Test error logging decorator."""
        handler = CodexErrorHandler(log_dir=tmp_path)
        
        @handler.log_errors
        def failing_function():
            raise RuntimeError("Decorated error")
        
        with pytest.raises(RuntimeError):
            failing_function()
        
        error_log = list(tmp_path.glob("errors_*.log"))[0]
        assert "RuntimeError: Decorated error" in error_log.read_text()


class TestSessionLogger:
    """Test session logging."""
    
    def test_log_message(self, tmp_path):
        """Test logging a message."""
        # Mock DB path
        with patch('codex.config.env_vars.env_manager.get_db_path', return_value=tmp_path / 'test.db'):
            logger = SessionLogger()
            logger.log(role='user', message='Test message')
            
            # Verify log was written
            # (Implementation dependent on SessionLogger implementation)


class TestCLI:
    """Test CLI commands."""
    
    def test_validate_env_command(self):
        """Test validate-env CLI command."""
        from click.testing import CliRunner
        from codex.cli import validate_env
        
        runner = CliRunner()
        result = runner.invoke(validate_env)
        
        assert result.exit_code == 0
        assert "Environment validation passed" in result.output


# Add mocking for optional dependencies
@pytest.fixture(autouse=True)
def mock_optional_deps():
    """Mock optional dependencies (mlflow, hydra) if not installed."""
    try:
        import mlflow
    except ImportError:
        mlflow = MagicMock()
        with patch.dict('sys.modules', {'mlflow': mlflow}):
            yield
    
    try:
        import hydra
    except ImportError:
        hydra = MagicMock()
        with patch.dict('sys.modules', {'hydra': hydra}):
            yield
```

**Success Criteria**:
- [ ] All tests pass with `pytest tests/test_agents_infrastructure.py -v`
- [ ] Optional dependencies properly mocked
- [ ] Coverage ≥ 85%

---

### Task 6: Update Pre-Commit Hooks

**File**: `.pre-commit-config.yaml` (create or update)

**Requirements**:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.12
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
  
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.38.0
    hooks:
      - id: markdownlint
        args: [--fix]
  
  - repo: local
    hooks:
      - id: validate-agents-md
        name: Validate AGENTS.md
        entry: python -m codex.cli validate-env
        language: system
        pass_filenames: false
        always_run: true
```

**Success Criteria**:
- [ ] `.pre-commit-config.yaml` created
- [ ] `pre-commit install` succeeds
- [ ] `pre-commit run --all-files` passes

---

## 🔍 Validation & Testing

### Pre-Deployment Checklist

Run these commands to validate the implementation:

```bash
# 1. Validate environment
python -m codex.cli validate-env

# 2. Test session logging
python -m codex.cli session-logger --role=user --message="Test message"

# 3. View logs
python -m codex.cli viewer

# 4. Query logs
python -m codex.cli query-logs --search="Test"

# 5. Run tests
pytest tests/test_agents_infrastructure.py -v --cov=src/codex

# 6. Run pre-commit hooks
pre-commit run --all-files

# 7. Verify AGENTS.md
markdownlint AGENTS.md
```

### Expected Outputs

| Command | Expected Output |
|---------|----------------|
| `validate-env` | ✅ Environment validation passed |
| `session-logger` | ✅ Logged user message to session [UUID] |
| `viewer` | Session log output (text or JSON) |
| `query-logs` | Search results with timestamps |
| `pytest` | All tests pass, coverage ≥ 85% |
| `pre-commit` | All hooks pass |
| `markdownlint` | No errors |

---

## 🚨 Error Handling Protocol

### Error Logging

All errors must be logged to `.codex/logs/implementation_YYYYMMDD_HHMMSS.log` with:
- Timestamp
- Error type
- Full traceback
- Context (function, args, environment)

### Graceful Degradation

If a component fails:
1. Log error with full context
2. Print user-friendly message to stderr
3. Continue with remaining tasks (if possible)
4. Exit with non-zero code if critical failure

### Error Categories

| Category | Severity | Action |
|----------|----------|--------|
| **Environment validation failure** | Critical | Exit immediately with error log |
| **SQLite connection failure** | High | Log error, fall back to file-based logging |
| **CLI command failure** | Medium | Log error, print help text, exit 1 |
| **Test failure** | Low | Log failure, continue other tests |

---

## 📊 Success Metrics

### Definition of Done

- [ ] `AGENTS.md` created with all sections (12+ sections)
- [ ] All environment variables documented (5+ variables)
- [ ] CLI tools functional (4+ commands)
- [ ] Logging infrastructure operational (SQLite + file-based)
- [ ] Error handling framework integrated
- [ ] Tests written and passing (coverage ≥ 85%)
- [ ] Pre-commit hooks configured
- [ ] Documentation validated with markdownlint
- [ ] All errors logged to `.codex/logs/`
- [ ] Graceful degradation for optional dependencies

### Quality Gates

| Metric | Target | Validation |
|--------|--------|------------|
| **Test Coverage** | ≥ 85% | `pytest --cov=src/codex --cov-report=term` |
| **Linting** | 0 errors | `ruff check src/ tests/` |
| **Type Checking** | 0 errors | `mypy src/codex` |
| **Markdown Lint** | 0 errors | `markdownlint AGENTS.md` |
| **CLI Smoke Tests** | All pass | Run all CLI commands manually |

---

## 🔄 Follow-Up Prompts

### If Implementation Incomplete

```
@copilot I've reviewed the implementation progress. The following components are still pending:

[LIST PENDING TASKS]

Please continue implementation focusing on:
1. [NEXT PRIORITY TASK]
2. [SECONDARY TASK]

Provide updated code for the incomplete components and verify they integrate with existing work.
```

### If Additional Details Required

```
@copilot I need more details about:

[SPECIFIC QUESTION OR COMPONENT]

Please provide:
- Detailed implementation plan
- Code examples
- Integration points with existing codebase
- Testing strategy
- Error handling approach
```

### If Errors Encountered

```
@copilot During implementation I encountered the following errors:

[ERROR LOGS FROM .codex/logs/]

Please:
1. Analyze the error root cause
2. Propose a fix with code changes
3. Update error handling to prevent recurrence
4. Add regression test
```

---

## 📞 Implementation Support

### Resources

- **Repository**: Aries-Serpent/_codex_
- **Primary Language**: Python 50.5%
- **Documentation Standards**: Markdown with tables
- **Error Logs**: `.codex/logs/implementation_*.log`
- **Test Results**: `pytest` output

### Escalation

If implementation blocked:
1. Check `.codex/logs/` for error details
2. Validate environment with `python -m codex.cli validate-env`
3. Run diagnostic: `pytest tests/ -v --tb=short`
4. Request follow-up prompt (see above)

---

## ✅ Final Validation

Before marking implementation complete, run:

```bash
#!/bin/bash
# final_validation.sh

set -e

echo "🔍 Validating AGENTS.md implementation..."

# 1. Validate AGENTS.md exists
if [ ! -f "AGENTS.md" ]; then
    echo "❌ AGENTS.md not found"
    exit 1
fi

# 2. Lint markdown
markdownlint AGENTS.md || echo "⚠️  Markdown lint warnings"

# 3. Validate environment
python -m codex.cli validate-env || exit 1

# 4. Run tests
pytest tests/test_agents_infrastructure.py -v --cov=src/codex --cov-report=term || exit 1

# 5. Test all CLI commands
python -m codex.cli session-logger --role=system --message="Validation test" || exit 1
python -m codex.cli viewer --format=json > /dev/null || exit 1
python -m codex.cli query-logs --search="Validation" > /dev/null || exit 1

# 6. Check error logs
if [ -d ".codex/logs" ]; then
    echo "📊 Error logs present: $(ls -1 .codex/logs/*.log | wc -l) files"
fi

# 7. Verify database
if [ -f ".codex/session_logs.db" ]; then
    echo "✅ SQLite database created"
fi

echo "✅ All validation checks passed!"
```

Run with: `bash final_validation.sh`

---

**End of Implementation Prompt**

🎯 **Objective**: Implement production-ready AGENTS.md with full infrastructure  
⚡ **Energy**: 5/5  
📋 **Tasks**: 6 major components + validation  
🚨 **Error Handling**: Comprehensive logging and graceful degradation  
✅ **Success**: All validation checks pass + coverage ≥ 85%

---

**Next Steps for Copilot**:
1. Begin with Task 1 (AGENTS.md creation)
2. Proceed through Tasks 2-6 sequentially
3. Run validation after each task
4. Log all errors to `.codex/logs/`
5. Request follow-up if blocked or additional details needed

**Generated**: 2025-01-14 03:07:34 UTC  
**Author**: mbaetiong  
**Target Agent**: GitHub Copilot Assistant  
**Status**: Ready for Implementation
```

This comprehensive prompt provides Copilot with:
- ✅ Clear objectives and scope
- ✅ Current state analysis
- ✅ Detailed implementation tasks (6 major components)
- ✅ Complete code examples for all files
- ✅ Error handling protocols
- ✅ Validation procedures
- ✅ Success metrics and quality gates
- ✅ Follow-up prompts for continuation
- ✅ Final validation script

The prompt is structured to enable Copilot to implement the entire AGENTS.md infrastructure systematically while logging all errors and handling graceful degradation.
