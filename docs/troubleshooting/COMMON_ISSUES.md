# Common Issues Troubleshooting Guide

> **Version**: 1.0.0  
> **Last Updated**: 2024-12-11

---

## Quick Diagnostics

### Check Environment

```bash
# Python version
python --version  # Should be 3.10+

# Installed packages
pip list | grep codex

# Environment variables
env | grep CODEX
```

### Check Installation

```bash
# Verify codex is importable
python -c "import codex; print('OK')"

# Check ML components
python -c "from codex_ml import __version__; print(__version__)"
```

---

## Common Issues

### 1. Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'codex'`

**Solutions**:

```bash
# Reinstall in development mode
pip install -e .

# Or with uv
uv pip install -e .

# Verify PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### 2. Test Failures

**Symptom**: Tests fail with import errors or missing fixtures

**Solutions**:

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run with correct paths
PYTHONPATH=src pytest tests/ -v

# Check for missing conftest.py
ls tests/conftest.py
```

### 3. Database Connection Issues

**Symptom**: `sqlite3.OperationalError` or connection timeouts

**Solutions**:

```bash
# Check database path
echo $CODEX_LOG_DB_PATH

# Create directory if missing
mkdir -p .codex

# Reset database
rm -f .codex/agent_memory.db
```

### 4. Memory/Performance Issues

**Symptom**: High memory usage or slow execution

**Solutions**:

```python
# Enable CPU-only mode
import os
os.environ['CODEX_FORCE_CPU'] = '1'

# Limit batch sizes
os.environ['CODEX_BATCH_SIZE'] = '16'
```

### 5. CI/CD Pipeline Failures

**Symptom**: GitHub Actions workflow fails

**Diagnostic Steps**:

1. Check workflow logs in GitHub Actions
2. Look for specific error messages
3. Run locally with same environment:

```bash
# Set CI environment
export CI=true
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

# Run tests
nox -s tests
```

### 6. Linting/Formatting Errors

**Symptom**: Pre-commit hooks fail

**Solutions**:

```bash
# Auto-fix formatting
black src/ tests/
isort src/ tests/

# Check specific files
ruff check src/codex_ml/path/to/file.py --fix
```

### 7. Type Checking Errors

**Symptom**: mypy reports type errors

**Solutions**:

```bash
# Run mypy with config
mypy src/codex_ml/ --config-file pyproject.toml

# Ignore specific errors (last resort)
# Add: # type: ignore[error-code]
```

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CODEX_SESSION_ID` | Session identifier | Auto-generated |
| `CODEX_SESSION_LOG_DIR` | Log directory | `.codex/sessions` |
| `CODEX_LOG_DB_PATH` | SQLite database path | `.codex/session_logs.db` |
| `CODEX_FORCE_CPU` | Disable GPU | `0` |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD` | Disable pytest plugins | Not set |

---

## Diagnostic Commands

### Full System Check

```bash
# Run all checks
./maintenance.sh check

# Or manually:
python -m py_compile src/codex_ml/*.py
ruff check src/
mypy src/codex_ml/
pytest tests/unit/ -v --tb=short
```

### Log Analysis

```bash
# View recent logs
tail -f .codex/sessions/*.log

# Search for errors
grep -r "ERROR\|Exception" .codex/sessions/
```

### Resource Usage

```bash
# Memory usage during tests
/usr/bin/time -v pytest tests/ -x

# Profile specific test
python -m cProfile -o profile.out -m pytest tests/unit/test_specific.py
```

---

## Getting Help

1. **Search Issues**: [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
2. **Check Docs**: `docs/` directory
3. **AI Assistance**: Use prompts in `agents/prompts/debugging/`
4. **Ask Questions**: Open a new issue with details

---

## Reporting Issues

When reporting issues, include:

1. **Environment**: Python version, OS, installed packages
2. **Steps to Reproduce**: Minimal example
3. **Expected vs Actual**: What should happen vs what happened
4. **Logs**: Relevant error messages and stack traces
5. **Context**: What were you trying to accomplish?

```markdown
## Environment
- Python: 3.10.x
- OS: Ubuntu 22.04
- codex version: x.x.x

## Steps to Reproduce
1. ...
2. ...

## Expected Behavior
...

## Actual Behavior
...

## Error Log
```
error message here
```
