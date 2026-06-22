# Pre-commit Verification Hook

> **Version:** 1.0.0  
> **Status:** ✅ Active  
> **Last Updated:** 2026-02-10T09:30:00Z  
> **Cognitive Brain Plan:** Plan 1 of Short-term Planset (CB-ST-2026-02-05)

---

## 🎯 Overview

The Pre-commit Verification Hook ensures that all files logged in `action_log.ndjson` as created or modified are properly staged before commit. This prevents accidental omission of files that were worked on during a session.

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Pre-commit Verification Hook                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Action     │    │    Git       │    │   Report     │  │
│  │ Log Parser   │───▶│  Status      │───▶│  Generator   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Expected    │    │   Staged     │    │ Verification │  │
│  │   Files      │    │   Files      │    │    Result    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Usage

### As Pre-commit Hook (Automatic)

The hook is automatically run during `git commit` when configured:

```bash
# Install pre-commit hooks
pre-commit install

# Commit normally - hook runs automatically
git commit -m "Your message"
```

## Manual Verification

```bash
# Check files (no failure on missing)
python scripts/hooks/pre_commit_verify.py --check-only

# Verify with specific time range
python scripts/hooks/pre_commit_verify.py --hours 4

# Verify from specific timestamp
python scripts/hooks/pre_commit_verify.py --since "2026-02-05T09:00:00Z"

# Quiet mode (output only on issues)
python scripts/hooks/pre_commit_verify.py --quiet

# Custom action log path
python scripts/hooks/pre_commit_verify.py --action-log /path/to/action_log.ndjson
```

---

## 📋 CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--check-only` | Don't fail on missing files | `False` |
| `--quiet` | Suppress output unless issues | `False` |
| `--hours N` | Check last N hours of log | `24` |
| `--since TIMESTAMP` | Check from specific timestamp | `None` |
| `--session-id ID` | Check specific session only | `None` |
| `--action-log PATH` | Custom action log path | `.codex/action_log.ndjson` |

---

## 📄 Sample Output

### All Files Staged ✅

```
============================================================
Pre-commit Verification Report
============================================================

Expected files from action log: 5
Correctly staged: 5 ✅
Missing from staging: 0

✅ Staged Files (Correct):
   - scripts/hooks/pre_commit_verify.py
   - tests/hooks/test_pre_commit_verify.py
   - .pre-commit-config.yaml
   - docs/PRE_COMMIT_VERIFICATION.md
   - .codex/action_log.ndjson

============================================================
INFO: All expected files are staged ✅
```

### Missing Files ⚠️

```
============================================================
Pre-commit Verification Report
============================================================

Expected files from action log: 5
Correctly staged: 3 ✅
Missing from staging: 2

✅ Staged Files (Correct):
   - scripts/hooks/pre_commit_verify.py
   - tests/hooks/test_pre_commit_verify.py
   - .pre-commit-config.yaml

⚠️  Modified but not staged (need `git add`):
   - docs/PRE_COMMIT_VERIFICATION.md

⚠️  Untracked files (need `git add`):
   - .codex/new_file.md

To stage missing files:
   git add docs/PRE_COMMIT_VERIFICATION.md
   git add .codex/new_file.md

============================================================
ERROR: Some expected files are not staged!
```

---

## 🔍 How It Works

### 1. Parse Action Log

The hook reads `.codex/action_log.ndjson` and extracts file operations:

```json
{"timestamp":"2026-02-05T09:00:00Z","actor":"assistant","action":"created","path":"scripts/new.py"}
{"timestamp":"2026-02-05T09:01:00Z","actor":"assistant","action":"edited","path":"src/module.py"}
```

### 2. Filter Operations

Only these operations are considered:
- `create`, `created`
- `edit`, `edited`
- `update`, `updated`
- `modify`, `modified`

### 3. Ignore Patterns

These patterns are automatically ignored:
- `/tmp/` and `tmp/` directories
- `__pycache__` directories
- `.pyc` files
- `.git/` directory
- `node_modules/`
- `dist/`, `build/`
- `.venv/`, `venv/`
- Patterns from `.gitignore`

### 4. Compare with Git Status

The hook compares expected files with:
- Staged files (`git diff --cached --name-only`)
- Modified files (`git diff --name-only`)
- Untracked files (`git ls-files --others`)

### 5. Generate Report

A detailed report is generated showing:
- Total expected files
- Correctly staged files
- Missing modified files
- Missing untracked files
- Commands to stage missing files

---

## ⚙️ Pre-commit Configuration

The hook is configured in `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: verify-expected-files
      name: Verify expected files from action log are staged
      entry: python scripts/hooks/pre_commit_verify.py --check-only --quiet
      language: system
      pass_filenames: false
      always_run: true
      stages: [commit]
```

### Configuration Options

| Setting | Value | Description |
|---------|-------|-------------|
| `--check-only` | Recommended | Don't block commits |
| `--quiet` | Recommended | Only show issues |
| `stages: [commit]` | Required | Run on commit only |

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/hooks/test_pre_commit_verify.py -v

# Run specific test class
pytest tests/hooks/test_pre_commit_verify.py::TestShouldIgnoreFile -v

# Run with coverage
pytest tests/hooks/test_pre_commit_verify.py --cov=scripts/hooks/pre_commit_verify --cov-report=term-missing
```

---

## 🔗 Integration with Cognitive Brain

This hook is part of the cognitive brain improvement initiative:

- **Planset:** Short-term Planset (CB-ST-2026-02-05)
- **Plan:** Plan 1 - Pre-commit Verification Hook
- **Pattern:** `commit_verification` in pattern store

The hook helps maintain the 98%+ commit verification rate identified in the session analysis.

---

## 📚 Related Documents

- Short-term Planset: `.codex/plans/cognitive_brain_short_term_planset.md`
- Session Analysis Report: `reports/COPILOT_SESSION_ANALYSIS_2026_02_05.md`
- Pattern Store: `.codex/cognitive_brain/pattern_learning_store.json`
- Session Manager: `scripts/cognitive/session_manager.py`

---

## 🛡️ Safety Features

1. **Check-only Mode:** Won't block commits by default
2. **Quiet Mode:** Minimal output for clean git experience
3. **Time Filtering:** Only checks recent operations
4. **Gitignore Respect:** Honors `.gitignore` patterns
5. **Graceful Degradation:** Works even if action log is missing

---

## 📞 Support

For issues or enhancements:
- Create an issue with `[pre-commit-verify]` tag
- Contact: @mbaetiong

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-05T09:30:00Z
