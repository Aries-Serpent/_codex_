# Path to 100% Coverage: Tokenization Module
> Generated: 2026-02-04T15:00:30Z | Owner: codex
> Scope: src/tokenization/*
> Target: 100% line coverage with deterministic tests

---

## Goal

Raise `src/tokenization/` coverage from the current baseline (25%) to **100%** by executing phased, test-driven coverage improvements aligned with the HO-001 mapping artifacts.

## Inputs & References

- Coverage baseline: `.codex/plans/pr_3145/tokenization_coverage_baseline.md`
- Test mapping: `.codex/plans/pr_3145/test_case_mapping.md`
- Gap report: `.codex/plans/pr_3145/coverage_gap_report.txt`
- Coverage tool: `scripts/analyze_tokenization_coverage.py`
- Hand-off protocol: `.codex/docs/AGENT_HANDOFF_PROTOCOL.md`
- Test patterns: `.codex/docs/TEST_DEVELOPMENT_PATTERNS.md`
- CI troubleshooting: `.github/agents/ci-testing-agent.md`

---

## Phase 1-2: Critical Coverage Lift (CLI + Loader)

**Objective**: Reach ≥70% coverage for `cli.py` and `loader.py` using mapped tests 1-10.

### Tasks
- [ ] Implement CLI fallback tests (FallbackTyper initialization, command registration, argument parsing, error handling).
- [ ] Add CLI integration checks for real Typer (when available).
- [ ] Add loader tests for special tokens, file loading, and remote/offline behavior.
- [ ] Add loader config validation error coverage.

### Acceptance Criteria
- [ ] `cli.py` ≥70% coverage
- [ ] `loader.py` ≥70% coverage
- [ ] All new tests have ≥3 assertions each

---

## Phase 3-4: Training + API Shim Coverage

**Objective**: Reach ≥65% coverage for `train_tokenizer.py` and ≥75% for `api.py` using mapped tests 11-14.

### Tasks
- [ ] Add deterministic training workflow tests with isolated temp dirs.
- [ ] Validate training configuration parsing and error handling.
- [ ] Add API import fallback and proxy attribute tests.

### Acceptance Criteria
- [ ] `train_tokenizer.py` ≥65% coverage
- [ ] `api.py` ≥75% coverage

---

## Phase 5-6: 100% Completion Pass

**Objective**: Close remaining lines (including optional sentencepiece error paths) to reach 100% coverage.

### Tasks
- [ ] Identify remaining missing lines via coverage JSON.
- [ ] Add focused tests for any remaining uncovered branches.
- [ ] Validate sentencepiece adapter error paths (if feasible).

### Acceptance Criteria
- [ ] `src/tokenization/` overall coverage = 100%
- [ ] All files in `src/tokenization/` at 100% coverage

---

## Verification Commands

```bash
# Coverage run
PYENV_VERSION=3.11.14 PYTHONPATH=src pytest \
  --cov=src/tokenization \
  --cov-report=term-missing \
  --cov-report=json:coverage_tokenization.json \
  tests/ -v --tb=short

# Gap analysis
PYENV_VERSION=3.11.14 PYTHONPATH=src python scripts/analyze_tokenization_coverage.py
```

---

## Risk & Edge Case Checklist

- [ ] CLI fallback when typer is missing
- [ ] CLI unknown command errors
- [ ] Loader offline path (`allow_remote=False`)
- [ ] Loader missing file errors
- [ ] Training config missing keys
- [ ] API import fallbacks

---

## Agent Coordination

- Use **CI Testing Agent** for dependency/test collection errors.
- Use **Tokenization Coverage Agent** for mapped coverage gaps and hand-off support.

---

## Handoff Note (Template)

```markdown
@copilot Proceed with Pre-commit 5-8

**Current Status:**
- [x] Coverage baseline + test mapping reviewed
- [ ] Implement 14 mapped tests

**Acceptance Criteria:**
- Overall coverage ≥70%
- CLI + loader ≥70%
- Training + API ≥65%

**Verification Commands:**
- PYENV_VERSION=3.11.14 PYTHONPATH=src pytest --cov=src/tokenization --cov-report=term-missing --cov-report=json:coverage_tokenization.json tests/ -v --tb=short
- PYENV_VERSION=3.11.14 PYTHONPATH=src python scripts/analyze_tokenization_coverage.py
```

---

## Status

- **Current Phase**: Phase 1-2 (Pending)
- **Next Review**: After Pre-commit 5-8 execution

