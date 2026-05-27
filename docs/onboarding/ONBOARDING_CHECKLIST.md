# Contributor Onboarding Checklist

**Version**: 1.0  
**Created**: 2026-05-27  
**Owner**: `unified-doc-agent`  
**Full guide**: [`../CONTRIBUTOR_ONBOARDING.md`](../CONTRIBUTOR_ONBOARDING.md)  
**Quick start**: [`QUICK_START.md`](QUICK_START.md)

---

## Purpose

Use this checklist to verify that a new contributor has completed all onboarding steps.
The checklist covers environment setup, codebase orientation, tooling, and first
contribution. Target completion time: **≤ 60 minutes** for a developer with Python
experience.

---

## Step 1 — Prerequisites (5 min)

- [ ] Python ≥ 3.12 installed (`python --version`)
- [ ] Git configured with name and email
- [ ] GitHub account with repository access granted
- [ ] Read [`CODE_OF_CONDUCT.md`](../../CODE_OF_CONDUCT.md)
- [ ] Read [`CONTRIBUTING.md`](../../CONTRIBUTING.md)

---

## Step 2 — Clone and Set Up (10 min)

```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev,test]"
```

- [ ] Repository cloned successfully
- [ ] Virtual environment created and activated
- [ ] `pip install -e ".[dev,test]"` completed without errors
- [ ] `python -c "import codex_ml; print(codex_ml.__version__)"` runs without error

---

## Step 3 — Verify Tests Pass (10 min)

```bash
python -m pytest tests/ -q --timeout=60 -x
```

- [ ] Test collection succeeds (no import errors)
- [ ] At least the smoke tests pass (`pytest -m smoke`)
- [ ] Coverage report generated (optional: `--cov=src`)

---

## Step 4 — Codebase Orientation (15 min)

Read the following (skim is fine):

- [ ] [`README.md`](../../README.md) — repo overview
- [ ] [`AGENTS.md`](../../AGENTS.md) — agent system overview
- [ ] [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) — system architecture
- [ ] [`docs/CI.md`](../CI.md) — CI/CD pipeline
- [ ] [`.codex/DOMAIN_OWNERSHIP.md`](../../.codex/DOMAIN_OWNERSHIP.md) — who owns what

Key directories:

| Path | Purpose |
|------|---------|
| `src/` | Main Python packages |
| `agents/` | Copilot custom agents |
| `tests/` | Test suite |
| `.github/workflows/` | CI/CD (286 workflows) |
| `.codex/` | Governance, plans, config |
| `docs/` | Documentation |

- [ ] Can locate `src/codex_ml/` in file explorer
- [ ] Can locate `agents/` and read one agent spec
- [ ] Can locate the `tests/` directory

---

## Step 5 — Tooling Check (10 min)

```bash
# Linting
python -m ruff check src/ tests/

# Type checking
python -m mypy src/ --ignore-missing-imports

# Import architecture
lint-imports --config .importlinter 2>/dev/null || echo "import-linter not installed"
```

- [ ] Ruff runs without errors on `src/`
- [ ] Mypy runs (errors are expected; just verify it runs)
- [ ] Understand how to read CI workflow logs in GitHub Actions

---

## Step 6 — Make a Small Change (10 min)

1. Create a branch: `git checkout -b onboarding/your-name-hello-world`
2. Add a one-line comment to any test file
3. Run `python -m ruff check` and `python -m pytest -m smoke -q`
4. Open a draft PR

- [ ] Branch created following naming convention
- [ ] Ruff passes on changed files
- [ ] At least smoke tests pass
- [ ] Draft PR opened (you can close it immediately)

---

## Sign-Off

Once all boxes are checked, record your onboarding completion:

```
Onboarding completed by: ___________________
Date: ______________________
Time taken: ________________ minutes
Reviewer: __________________
```

Feedback on this checklist → open an issue with label `docs:onboarding`.
