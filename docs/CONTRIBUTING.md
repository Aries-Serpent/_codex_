# Contributing to _codex_

**Last Updated:** 2026-07-08  
**Audience:** Contributors, Maintainers  
**Related:** [Code Style Guide](guides/code_style_guide.md), [Testing Guide](TESTING.md), [Documentation Style Guide](../.codex/DOCUMENTATION_STYLE_GUIDE.md)

---

## Overview

Welcome! This guide helps you contribute to _codex_ successfully.

!!! note
    This repository is designed for and managed by AI Assistants and Agents. All processes are automated and autonomous. Guidelines below support this workflow.

---

## Quick Start for Contributors

### 1. Set Up Your Environment

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Install dependencies
pip install -r requirements-dev.txt
pre-commit install --install-hooks
```

### 2. Configure Git Hooks

```bash
# Install pre-commit hooks
pre-commit migrate-config
pre-commit autoupdate
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

### 3. Make Your Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test locally: `pytest tests/`
4. Commit: `git commit -m "feat: description"`

### 4. Push and Create PR

```bash
# Normalize line endings
git add --renormalize .
git commit -m "chore: normalize line endings via .gitattributes"

# Push your branch
git push origin feature/your-feature-name
```

---

## Making Changes

### Code Standards

Follow the [Code Style Guide](guides/code_style_guide.md) for:
- Code formatting and naming conventions
- Comment guidelines
- Import organization
- Test requirements

### Documentation Standards

All documentation must follow the [Documentation Style Guide](../.codex/DOCUMENTATION_STYLE_GUIDE.md):
- Single H1 title per file
- Clear, active voice
- Working code examples
- Proper heading hierarchy
- Relative internal links

### Commit Message Format

Use [conventional commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

**Examples:**
```
feat(api): add authentication endpoint
fix(cli): resolve import error on Windows
docs(readme): update installation instructions
```

---

## Managing Line Endings

After `.gitattributes` updates, normalize once:

```bash
git add --renormalize .
git commit -m "chore: normalize line endings via .gitattributes"
```

---

## Fast Path vs. Full Checks

### Commit-Time Hooks (Fast)

Run locally before pushing:
```bash
pre-commit run
```

### Full Checks (Before Merge)

Run when committing:
```bash
SKIP=semgrep git commit -m "feat: description"
```

!!! note
    Semgrep runs automatically on pre-push and in CI. Use `pre-commit run --all-files` for manual full scans.

---

## Using Operational Templates

Operational templates in [`docs/templates/`](./templates/README.md) follow a role-gated execution model.

| Task | Template | Purpose |
|------|----------|---------|
| Move Python files | [Python File Relocation](./templates/Migration_PythonFileRelocation.md) | Preserve backward compatibility |
| CLI changes | [CLI Hardening](./templates/Migration_CLIHardening.md) | Target ≥85% coverage |
| Plan work | [Intent Validation](./templates/Planning_IntentValidation.md) | Document assumptions & risks |

### Using a Template

1. Copy the template file
2. Replace all `[PLACEHOLDER: ...]` entries
3. Attach supporting assets (tests, notebooks)
4. Document execution in "Execution Notes"
5. Validate placeholders are resolved
6. Ensure references are accessible

**Example:**
```
[PLACEHOLDER: MIGRATION_INTENT_SUMMARY] 
→ "Relocate tokenizer helpers to `codex.text`"

[PLACEHOLDER: COMMAND_LIST]
→ "`codex-cli sync`, `codex-cli diff`"

[PLACEHOLDER: APPROVAL_DEADLINE]
→ "2025-11-07"
```

---

## Troubleshooting

### Missing Pre-Commit Hooks

Reinstall hooks:
```bash
pre-commit install --install-hooks \
  --hook-type pre-commit \
  --hook-type pre-push \
  --hook-type commit-msg
```

### Hook Configuration

Check `.pre-commit-config.yaml` for available stages. Values match hook names (`pre-commit`, `pre-push`, etc).

### Common Issues

| Issue | Solution |
|-------|----------|
| Hooks won't install | Run: `pre-commit autoupdate` |
| Hook too slow | Use `SKIP=toolname git commit` |
| Line ending issues | Run: `git add --renormalize .` |
| Semgrep blocking | Run on pre-push only, not pre-commit |

---

## Code Review Expectations

### What Reviewers Check

- ✅ Code follows style guide
- ✅ Tests cover new code
- ✅ Documentation is updated
- ✅ Examples are working
- ✅ No breaking changes (unless major version)
- ✅ Commit messages are clear
- ✅ Related issues are linked

### How to Prepare

1. Test locally: `pytest`
2. Run linting: `pre-commit run --all-files`
3. Update docs if needed
4. Reference related issues/PRs
5. Keep commits logical (not squashed)

---

## Asking for Help

- **How-to questions:** [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions)
- **Bug reports:** [Issue Tracker](https://github.com/Aries-Serpent/_codex_/issues)
- **Design feedback:** Open a draft PR for early feedback

---

## Code of Conduct

Please review our [Code of Conduct](../CODE_OF_CONDUCT.md) before contributing. We're committed to fostering an inclusive and respectful environment.

---

*Thank you for contributing to _codex_! 🚀*
