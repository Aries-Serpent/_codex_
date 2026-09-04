# Contributing Guide

Welcome to **Codex ML**! Thank you for your interest in contributing to this project. This guide provides everything you need to get started, whether you're fixing bugs, adding features, improving documentation, or helping the community.

## 🚀 Quick Start

**New contributor?** Start here:
1. **[Development Setup Guide](docs/DEVELOPMENT.md)** - Get your environment ready in 5 minutes
2. **[Contribution Paths](CONTRIBUTING.md#contribution-paths)** - Choose how you want to contribute
3. **[Code of Conduct](CODE_OF_CONDUCT.md)** - Our community standards
4. **[Code Style Guide](docs/dev/CODE_STYLE_GUIDE.md)** - Coding standards and patterns

## 📚 Essential Resources

**Getting Help & Asking Questions**:
- **[Community Guidelines](docs/COMMUNITY_GUIDELINES.md)** - How to participate constructively
- **[Issue Reporting Guide](docs/ISSUE_REPORTING_GUIDE.md)** - How to report bugs and request features
- **[Code Review Guide](docs/CODE_REVIEW_GUIDE.md)** - Understanding code reviews

**Development & Testing**:
- **[Development Setup](docs/DEVELOPMENT.md)** - Complete environment setup
- **[Testing Guide](docs/dev/testing.md)** - Writing and running tests
- **[Code Style Guide](docs/dev/CODE_STYLE_GUIDE.md)** - Formatting and naming conventions
- **[CI Local Testing](docs/dev/CI_LOCAL_TESTING.md)** - Run CI checks locally

**Deeper Dives**:
- **[Newcomer Guide](docs/NEWCOMER_GUIDE.md)** - Detailed onboarding for new contributors
- **[Documentation Index](docs/MASTER_INDEX.md)** - Find all documentation
- **[Cognitive Map](docs/system/CODEBASE_COGNITIVE_MAP.md)** - Understand the codebase architecture
- **[Roadmap](docs/ROADMAP.md)** - Current and planned work

## Testing Requirements

All contributions must include appropriate tests and maintain code coverage standards.

### Pre-commit Hooks (Automated Quality Gates)

This repository uses pre-commit hooks to catch issues before they reach CI. Install and enable them:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Quality Gates Enforced**:
- **Meta Tensor Validator**: Prevents PyTorch meta tensor issues in ML model loading code
- **Test Pattern Guardian**: Detects mock exhaustion and serialization issues in tests
- **Test File Naming**: Prevents `test_*.py` naming for utility modules (pytest collection risk)
- **Config Validator**: Ensures all Hydra configs referenced in tests exist
- **Security Checks**: Command injection, unsafe XML, weak hashing detection
- **Code Quality**: Trailing whitespace, YAML validation, large file checks
- **Windows Compatibility**: Filename validation for cross-platform support

**Pre-commit hooks automatically run on every commit.** If they fail:
1. Fix the reported issues
2. Stage the fixes: `git add <files>`
3. Commit again: `git commit`

**Bypassing hooks** (only in emergencies): `git commit --no-verify`

## Workflow Security Checklist

If you create or modify workflows with `workflow_run` triggers, follow these security guidelines:

### Privileged Workflow Context Security

**CRITICAL:** Workflows triggered by `workflow_run` execute with elevated permissions. Follow these rules:

- **✅ DO:** Use GitHub API calls for validation (`gh api repos/.../branches/...`)
- **✅ DO:** Checkout only the main branch for trusted code
- **✅ DO:** Keep execution context minimal (avoid shell loops in privileged jobs)
- **❌ DON'T:** Use `git fetch` or `git checkout` from untrusted sources
- **❌ DON'T:** Use LGTM pragmas or comments for CodeQL suppression (they don't work for workflow-level analysis)
- **❌ DON'T:** Pass untrusted code paths to CI jobs

**CodeQL Analysis Warning:** CodeQL performs YAML-level dataflow analysis on `workflow_run` patterns. Git operations create untrusted code patterns that can be detected even without explicit code comments. Use API-only validation instead.

**Reference:** [CodeQL Workflow Security Pattern](docs/SECURITY.md#workflow_run-privileged-context-security-pattern)

For complete details on Phase 4 CodeQL resolution, see [CodeQL Alert Resolution Final Report](.codex/CODEQL_ALERT_RESOLUTION_FINAL_REPORT_2026_07_14.md)

## Terminology Standards

Consistent terminology across documentation and code reduces ambiguity and improves clarity. This repository enforces standardized terminology for key terms.

### Standard Terms

**Use these forms consistently in all documentation:**

| Term | Recommended Form | When to Capitalize | Examples |
|------|-----------------|-------------------|----------|
| **agent** | lowercase `agent` | Only in titles/sentence starts | ✅ "The agent executed..." ✅ "CI Testing agent" ❌ "The agent executed..." |
| **workflow** | lowercase `workflow` | Only in titles/sentence starts | ✅ "The workflow runs tests..." ✅ "Workflow Compliance Gate" ❌ "The workflow runs..." |
| **pull request** / **PR** | `PR` (acronym) in most contexts | N/A | ✅ "This PR must pass checks" ✅ "in the pull request..." ❌ "pull request" in text |
| **repository** | lowercase `repository` | Only in titles/sentence starts | ✅ "The repository contains..." ✅ "Repository Policy" ❌ "The repository contains..." |
| **component** | lowercase `component` | Only in titles/sentence starts | ✅ "The component manages..." ✅ "Cache component" ❌ "The component manages..." |
| **task** | lowercase `task` | Only in titles/sentence starts | ✅ "Each task has a status..." ✅ "High-Priority task" ❌ "Each task has..." |

### Usage Rules

**Capitalization:**
- ✅ Use lowercase for general mentions mid-sentence
- ✅ Capitalize only at sentence starts or in formal titles
- ❌ Avoid capitalizing mid-sentence for consistency

**Singular/Plural:**
- Use naturally: `agent` / `agents`, `workflow` / `workflows`
- Be consistent within the same section

## API Stability & Internal vs Public APIs

### 10 Stable Public APIs (v0.1.0)

All external users should use only these stable, versioned APIs. The Cognitive Brain OODA loop provides the core abstraction for all integrations:

| # | Module | Class/Function | Stability | Version | Purpose |
|---|--------|----------------|-----------|---------|---------|
| 1 | `cognitive_brain` | `ObservationData` | ✅ Stable | v0.1.0+ | OODA input: observations from environment |
| 2 | `cognitive_brain` | `OrientationResult` | ✅ Stable | v0.1.0+ | OODA phase: context & pattern matching |
| 3 | `cognitive_brain` | `Decision` | ✅ Stable | v0.1.0+ | OODA phase: action selection from patterns |
| 4 | `cognitive_brain` | `ActionResult` | ✅ Stable | v0.1.0+ | OODA output: executed actions & feedback |
| 5 | `cognitive_brain` | `Planner` | ✅ Stable | v0.1.0+ | Orchestrator: main OODA loop executor |
| 6 | `cognitive_brain` | `MemoryInterface` | ✅ Stable | v0.1.0+ | Memory abstraction: STM/LTM operations |
| 7 | `cognitive_brain` | `MemoryPattern` | ✅ Stable | v0.1.0+ | Pattern storage: learnable decision rules |
| 8 | `cognitive_brain` | `QuantumMemoryManager` | ✅ Stable | v0.1.0+ | Quantum-enhanced memory: probability-aware learning |
| 9 | `cognitive_brain` | `Pattern` | ✅ Stable | v0.1.0+ | Pattern unit: condition-action tuple |
| 10 | `cognitive_brain` | `PatternSet` | ✅ Stable | v0.1.0+ | Pattern collection: searchable pattern library |

**Public API Contract:**
- ✅ Backward compatible across minor versions (v0.1.x)
- ✅ Breaking changes only in major versions (v0.2+)
- ✅ Type hints enforced
- ✅ Docstrings required
- ✅ Unit tests validate all code paths

### Internal APIs (Private, May Change)

All modules prefixed with `_` (underscore) are **internal only**:

```python
# ❌ DO NOT use in external code
from codex_ml._internal.impl import HelperClass

# ✅ DO use public APIs
from codex_ml.safety import PromptSanitizer
```

**Internal modules may:**
- Change signature without notice
- Be refactored or replaced
- Have limited or no documentation
- Break between patch versions

### Contribution Guidelines for API Stability

**When adding new public APIs:**
1. Update the [10 Stable Public APIs](#10-stable-public-apis-v010) table
2. Include comprehensive docstrings (Google style)
3. Add type hints to all parameters and returns
4. Write unit tests with 100% code coverage
5. Mark as `@public` in docstring if non-obvious

**Example:**

```python
from codex_ml.safety import PromptSanitizer

sanitizer = PromptSanitizer(strict_mode=True)
# ✅ This is documented in the 10 stable public APIs table

try:
    result = sanitizer.sanitize(user_input)
except ValueError as e:
    print(f"Unsafe input: {e}")
```

**Hyphenation:**
- Use `pull request` or `PR`, never `pull request` in prose
- Use `pull request` only in technical identifiers (URLs, JSON keys)
- Use `agent-name` in hyphenated identifiers, `agent name` in prose

**Context-Specific Guidance:**
- **Code Comments:** Use lowercase and snake_case for identifiers
- **Docstrings:** Use lowercase, capitalize as normal for sentences
- **Markdown Headers:** Use Title Case (capitalize major words)
- **URLs/Identifiers:** Use kebab-case (e.g., `workflow-execution-gate.yml`)

### Examples

**❌ Incorrect Terminology Usage:**
```markdown
# Incorrect Examples

The agent scans the repository and creates a workflow that runs Tests.
Each workflow has many Tasks that execute in the PR.
This component manages the Cache, and it uses another component for validation.
Pull-requests require approval from the repository Manager.
```

**✅ Correct Terminology Usage:**
```markdown
# Correct Examples

The agent scans the repository and creates a workflow that runs tests.
Each workflow has many tasks that execute in the PR.
This component manages the cache, and it uses another component for validation.
Pull requests require approval from the repository manager.

# Formal Titles (Capitalized)

- Agent Accountability Report
- Repository Policy Guidelines
- Workflow Compliance Gate
- Component Architecture Overview
```

### Automated Enforcement

Terminology consistency is validated by:
- **Markdownlint Rules:** Patterns checked against `.markdownlintrc`
- **Pre-commit Hooks:** Terminology checker runs on `.md` files
- **CI/CD workflow:** `unified-governance-check` validates terminology
- **terminology-consistency-agent:** Autonomous enforcement and reporting

### Complete Terminology Guide

For comprehensive guidance on all standardized terms, usage rules, context-specific instructions, and migration information, see:

**[.codex/TERMINOLOGY_GLOSSARY.md](.codex/TERMINOLOGY_GLOSSARY.md)**

---

### Test File Naming Conventions

**Critical Rule**: pytest collects **ANY** file matching `test_*.py` pattern for test execution.

**✅ Correct Naming**:
- `tests/test_feature.py` - Actual test file
- `tests/framework/generator.py` - Utility module (no `test_` prefix)
- `tests/helpers/utils.py` - Helper module (no `test_` prefix)
- `conftest.py` - Pytest configuration (special name)

**❌ Incorrect Naming** (causes pytest collection errors):
- `tests/framework/test_generator.py` - Utility module with `test_` prefix ❌
- `tests/helpers/test_utils.py` - Helper module with `test_` prefix ❌

**Why This Matters**:
- pytest attempts to collect and run ALL `test_*.py` files
- Utility modules aren't designed to be test files
- Causes collection errors (exit code 2) and blocks CI
- Can lead to import errors and circular dependencies

**If You Need to Rename**:
```bash
# Rename the file
mv tests/framework/test_generator.py tests/framework/generator.py

# Update imports in all files that reference it
# Search for: from tests.framework.test_generator import
# Replace with: from tests.framework.generator import
```

**Optional Dependencies in Tests**:
For tests requiring optional dependencies (numpy, torch, etc.), use `pytest.importorskip()`:

```python
import pytest

# Skip entire module if dependency missing
numpy = pytest.importorskip("numpy")
torch = pytest.importorskip("torch")

def test_with_numpy():
    """This test only runs if numpy is installed."""
    arr = numpy.array([1, 2, 3])
    assert len(arr) == 3
```

Or skip individual tests:
```python
@pytest.mark.skipif(not has_numpy, reason="requires numpy")
def test_numpy_feature():
    import numpy as np
    # ...
```

### Running Tests Locally

**Quick test run:**
```bash
pytest
```

**With coverage:**
```bash
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term
```

**Run specific test categories:**
```bash
pytest -m smoke              # Smoke tests only
pytest -m "not slow"         # Skip slow tests
pytest -m integration        # Integration tests
```

See `tests/README.md` for comprehensive testing instructions.

### CI/CD Testing

All pull requests are automatically tested via GitHub Actions (`.github/workflows/ci-pytest.yml`):
- Tests run on Python 3.12+ (ubuntu-latest)
- Coverage must meet 90% threshold (configurable)
- Coverage reports are uploaded as artifacts
- Automatic PR comment with coverage summary and artifact links

### Coverage Requirements

- **Minimum threshold**: 90% (enforced in CI)
- **Local validation**: `pytest --cov=src --cov-fail-under=90`
- **Coverage reports**: Available as CI artifacts (HTML, XML, JSON formats)
- **Viewing reports**: Download `coverage-html-report` artifact from workflow run

### Before Submitting a PR

1. Run tests locally: `pytest -v`
2. Check coverage: `pytest --cov=src --cov-report=term-missing`
3. Ensure no test failures
4. Add tests for new functionality
5. Update documentation if needed
6. **🚨 CRITICAL: Verify no /tmp/ violations** - See [.github/TEMPORARY_FILES_POLICY.md](.github/TEMPORARY_FILES_POLICY.md)
   ```bash
   # Check for /tmp/ references
   git diff --cached | grep -i "/tmp/"
   # Verify no important files in /tmp/
   ls -la /tmp/ | grep -E "\.(md|txt|json|yaml|py)$"
   ```

## Safe Model Loading (PyTorch/ML)

When working with PyTorch, SentenceTransformers, or other ML models, follow these guidelines to prevent **meta tensor issues** (`NotImplementedError: Cannot copy out of meta tensor`).

### ✅ Correct Pattern

**Always use default device allocation** (no explicit `device=` parameter):

```python
import os
import torch
from sentence_transformers import SentenceTransformer

def load_model_safely(model_name: str, cache_dir: str = "./cache"):
    """Safe model loading with multi-layered prevention."""

    # Layer 1: Environment setup
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"

    # Layer 2: Initialize with default device allocation
    model = SentenceTransformer(
        model_name,
        cache_folder=cache_dir,
        trust_remote_code=False  # Security: prevent code execution
    )

    # Layer 3: Verification - Check for meta tensors
    meta_tensors = []
    for name, param in model.named_parameters():
        if param.device.type == "meta":
            meta_tensors.append(name)
    for name, buf in model.named_buffers():
        if buf.device.type == "meta":
            meta_tensors.append(name)

    if meta_tensors:
        raise RuntimeError(
            f"Model has {len(meta_tensors)} meta tensor(s). "
            f"This is a bug. Please report to: "
            f"https://github.com/Aries-Serpent/_codex_/issues"
        )

## Profile-Aware Development

Codex ML uses a 3-profile packaging strategy (core/runtime/full). When contributing, ensure your changes work across all profiles.

### Development Setup

**Install full profile for development:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[full]"
```

### Profile-Specific Testing

Test your changes against each profile:

**Core Profile (offline-first, minimal dependencies):**
```bash
pip install -e ".[core]"
pytest tests/test_core_profile.py
```

**Runtime Profile (production inference):**
```bash
pip install -e ".[runtime]"
pytest tests/test_runtime_profile.py
```

**Full Profile (development & testing):**
```bash
pip install -e ".[full]"
pytest tests/
```

### When Adding Dependencies

1. **Evaluate the profile impact:**
   - Core profile: Only stdlib + essential (hydra, pydantic, cryptography)
   - Runtime profile: Add transformers, torch, ray[serve], fastapi
   - Full profile: Add dev tools, test utilities, plugins

2. **Update `pyproject.toml`:**
   - Add to base `dependencies` if core needs it
   - Add to `[project.optional-dependencies]` for runtime or full
   - Verify via `pip install -e ".[profile]"` on each profile

3. **Document in docstring or README:**
   ```python
   """
   Requires the runtime or full profile:
   - pip install codex-ml[runtime]
   - pip install codex-ml[full]
   """
   ```

### Profile-Specific Import Checks

Use try/except for optional imports:

```python
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    
def feature_requiring_torch():
    if not HAS_TORCH:
       raise ImportError("This feature requires the runtime or full profile. Install with: pip install codex-ml[runtime]")
    # ... feature implementation
```

    model.eval()
    return model
```

### ❌ Anti-Patterns to Avoid

**1. Explicit device parameter (causes meta tensors in some PyTorch versions):**
```python
# WRONG: Can create meta tensors
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
```

**2. Attempting to fix meta tensors after creation:**
```python
# WRONG: Cannot fix meta tensors after they exist
model = SentenceTransformer('all-MiniLM-L6-v2')
if check_for_meta_tensors(model):
    model = safe_model_load(model, 'cpu')  # Doesn't work!
```

**3. Missing meta tensor verification:**
```python
# WRONG: No verification that model is safe
model = SentenceTransformer('all-MiniLM-L6-v2')
return model  # What if it has meta tensors?
```

**4. Using deprecated utilities:**
```python
# WRONG: Deprecated function
from codex.rag.utils import safe_model_load
model = safe_model_load(model, device='cpu')  # Don't use this!
```

### Best Practices

1. **Always set `trust_remote_code=False`** for security (prevents arbitrary code execution)
2. **Use default device allocation** (omit `device=` parameter in most cases)
3. **Add verification loops** to check for meta tensors after loading
4. **Handle errors gracefully** with clear upgrade instructions
5. **Pin PyTorch versions** in dependencies to avoid breaking changes

### Pre-commit Hook

The **Meta Tensor Validator** pre-commit hook automatically checks your code:

```bash
# Run manually on changed files
pre-commit run check-meta-tensors --files src/codex/rag/my_module.py

# Run on all files
pre-commit run check-meta-tensors --all-files
```

### Resources

- **agent Documentation**: [.github/agents/meta-tensor-validator.md](.github/agents/meta-tensor-validator.md)
- **Utility Registry**: [.codex/AI_AGENT_UTILITIES_REGISTRY.md](.codex/AI_AGENT_UTILITIES_REGISTRY.md) - See `safe_model_load_v2()`
- **Fix Summary**: [RAG_META_TENSOR_FIX_SUMMARY.md](.codex/RAG_META_TENSOR_FIX_SUMMARY.md) - Historical context

### Troubleshooting

**Issue**: `NotImplementedError: Cannot copy out of meta tensor`

**Solution**:
1. Remove explicit `device=` parameters from model constructors
2. Add meta tensor verification loops
3. Use utility functions from `codex.rag.utils` if available
4. Pin PyTorch version (e.g., `torch>=2.0.0,<2.2.0`) if issues persist

**Need Help?** Activate the Meta Tensor Validator agent:
```markdown
@copilot Use Meta Tensor Validator to check my model loading code
```

## Using Operational Templates

We maintain reusable templates under `docs/templates/` to streamline migrations, CLI hardening, and planning work.

| Scenario | Template | Primary Author | Reviewer |
| --- | --- | --- | --- |
| Moving Python modules while keeping imports stable | [Migration – Python File Relocation](docs/templates/Migration_PythonFileRelocation.md) | Developer | Maintainer |
| Increasing CLI robustness and coverage | [Migration – CLI Hardening](docs/templates/Migration_CLIHardening.md) | Developer | Maintainer |
| Capturing intent, risks, and validation before implementation | [Planning – Intent Validation](docs/templates/Planning_IntentValidation.md) | Developer | Maintainer |

### workflow

1. **Developer drafts** the relevant template, replacing each `[PLACEHOLDER: ...]` marker with project context.
2. **Maintainer reviews** the draft, confirms validation gates, and approves the plan.
3. **Developer executes** the agreed steps, committing code and documentation changes.
4. **Maintainer validates** results, ensuring coverage thresholds and documentation updates are met.
5. **Team archives** the completed template with the associated pull request for future reference.

### Customization Example

```markdown
Intent: Replace legacy CLI auth flow with token refresh
Assumptions: `[PLACEHOLDER:experiment_flag]` toggles rollout in staging only
Validation Gates:
- `pytest tests/cli/test_token_refresh.py -q`
- `pytest --cov=src/cli --cov-fail-under=90`
Rollback Signal: `[PLACEHOLDER:rollback_signal]` crossing threshold
```

### Additional Expectations

- Update `docs/CHANGELOG.md` when template-guided work lands.
- Run `pytest -q` for the affected paths before committing.
- Ensure coverage doesn't decrease with your changes.
- Keep placeholder markers intact until you supply concrete values.
- Reference the filled template in pull requests for reviewer context.

For questions, mention `@maintainer` in the Architecture Review forum or open a discussion thread.

## CI Pattern Prevention

This repository uses automated prevention patterns to catch and fix common CI failures before they block merges. These patterns are deployed continuously and can be run manually for validation.

### Deployed Prevention Patterns

**RP-001: API Null-Handling Validation**
- **Purpose**: Prevents NoneType crashes in API response processing
- **Reference**: `.codex/CI_PATTERN_PREVENTION_GUIDE.md` § RP-001

**RP-002: mypy Type Safety Baseline**
- **Purpose**: Enforces type annotation consistency and prevents type regressions
- **Auto-update command**: `python scripts/ci/mypy_baseline.py --update`
- **Reference**: `.codex/CI_PATTERN_PREVENTION_GUIDE.md` § RP-002

**RP-003: Documentation Link Validation**
- **Purpose**: Detects and fixes broken links in markdown documentation
- **Auto-fix command**: `python scripts/validate_docs_links.py --fix`
- **Reference**: `.codex/CI_PATTERN_PREVENTION_GUIDE.md` § RP-003

### Quick Start

**To validate patterns locally before committing:**
```bash
# Validate mypy baseline
python scripts/ci/mypy_baseline.py

# Validate and fix documentation links
python scripts/validate_docs_links.py --validate-anchors
python scripts/validate_docs_links.py --fix

# Update baseline if needed
python scripts/ci/mypy_baseline.py --update
```

### Autonomous Fixes

Prevention patterns are automatically triggered in CI when violations are detected:
- **Detection**: Patterns monitored on every PR push
- **Diagnosis**: Root cause identified by specialized agents
- **Fix**: Auto-fix applied using pattern-specific commands
- **Validation**: Results verified and reported in PR comments

### Resources

- **Comprehensive Guide**: [.codex/CI_PATTERN_PREVENTION_GUIDE.md](.codex/CI_PATTERN_PREVENTION_GUIDE.md)
- **Incident Archive**: [.codex/archive/CI_INCIDENTS/2026-06-23_RESOLUTION.md](.codex/archive/CI_INCIDENTS/2026-06-23_RESOLUTION.md)
- **Issue Tracking**: [GitHub Issue #5067](https://github.com/Aries-Serpent/_codex_/issues/5067)
- **Implementation PR**: [GitHub PR #5068](https://github.com/Aries-Serpent/_codex_/pull/5068)
- **Quarterly Review**: [Scheduled 2026-09-23](.codex/QUARTERLY_PATTERN_REVIEW_2026Q3.md)

---

## Session Wrap-up Compliance Guide

All development sessions must comply with our strict accountability and changelog standards before completion. This ensures that every autonomous or human-led action is properly documented for future reference and compliance tracking.

### REQ-4 & REQ-5 Requirements

*   **REQ-4 (Accountability Reporting):** Every session must log its accomplishments, files changed, and commands executed in `.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` (or the respective phase report). This guarantees complete traceability of AI and human modifications.
*   **REQ-5 (Changelog Updates):** You must add an entry to `CHANGELOG.md` detailing the semantic changes introduced in the session.

### Automated Compliance Checking

Before finalizing your work, you must verify compliance using the wrap-up autofix tool:

```bash
python scripts/ci/session_wrapup_autofix.py
```

This script will:
1. Verify that `.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` has been updated with the current session's changes.
2. Verify that `CHANGELOG.md` has a corresponding entry.
3. Attempt to automatically append missing entries if they are easily inferred, but **manual updates are preferred**.

**Failure to meet REQ-4 and REQ-5 will result in your pull request or session being flagged and potentially rejected during CI/CD checks.**

---

## 🎯 Contribution Paths

Whether you're fixing bugs, adding features, improving documentation, or supporting the community, there's a path for you. Choose the area that interests you:

### 🐛 Bug Fixes & Patches

**Good for**: Developers with Python experience  
**Effort**: 2-8 hours depending on complexity

**How to contribute**:
1. Find an open issue labeled `bug` or `good-first-issue`
2. Fork the repository and create a branch: `git checkout -b fix/issue-description`
3. Write a test that reproduces the issue
4. Implement the fix
5. Ensure all tests pass: `pytest`
6. Submit a pull request with the issue number in the title

**Example**:
```bash
git checkout -b fix/null-pointer-in-model-loader
pytest tests/test_model_loader.py
# ... make fixes ...
pytest tests/test_model_loader.py  # All pass ✓
git push origin fix/null-pointer-in-model-loader
```

### ✨ Feature Development

**Good for**: Experienced Python developers  
**Effort**: 8-40+ hours depending on scope

**How to contribute**:
1. **Propose first**: Open an issue with the `feature-request` label describing your idea
2. **Wait for feedback**: Maintainers will discuss scope and design
3. **Create a design document** if the feature is substantial
4. **Fork and develop**: Create a feature branch: `git checkout -b feature/new-capability`
5. **Write comprehensive tests**: Aim for >90% coverage
6. **Document thoroughly**: Update relevant docs and docstrings
7. **Submit PR**: Reference the original feature request issue

**Checklist before submitting**:
- ✅ Tests pass: `pytest`
- ✅ Coverage maintained: `pytest --cov=src --cov-fail-under=90`
- ✅ Type checking: `mypy src/`
- ✅ Code style: `black src/ && ruff check src/`
- ✅ Pre-commit hooks: `pre-commit run --all-files`
- ✅ Documentation updated
- ✅ Docstrings added/updated (Google style)

### 📖 Documentation Improvements

**Good for**: Writers, technical communicators, anyone!  
**Effort**: 1-4 hours per document

**How to contribute**:
1. **Identify gaps**: Look for unclear sections, missing examples, or outdated content
2. **Fork and create a branch**: `git checkout -b docs/improve-getting-started`
3. **Make improvements**: Add clarity, examples, screenshots, or tutorials
4. **Follow markdown standards**: See `.markdownlintrc` for style rules
5. **Test links**: Run the link validator: `python scripts/validate_docs_links.py`
6. **Submit a PR**: Include before/after examples if possible

**Documentation priorities**:
- Getting started guides
- API documentation examples
- Troubleshooting sections
- Tutorial walkthroughs
- Architecture diagrams

### 🚀 Performance Optimization

**Good for**: Developers interested in optimization  
**Effort**: 4-20+ hours

**How to contribute**:
1. **Profile the code**: Identify bottlenecks using profiling tools
2. **Create a benchmark**: Document the performance issue with benchmarks
3. **Implement optimizations**: Make targeted improvements
4. **Measure improvements**: Show before/after performance metrics
5. **Submit PR**: Include benchmark results and implementation details

**Benchmark resources**:
- Profiling tools: `cProfile`, `py-spy`, `flamegraph`
- Benchmark suite: `benches/` directory
- CI benchmarking: See `.github/workflows/benchmark.yml`

### 🧪 Test Coverage Improvements

**Good for**: QA-minded developers, students  
**Effort**: 2-8 hours

**How to contribute**:
1. **Identify gaps**: Run `pytest --cov=src` and review coverage report
2. **Write tests for uncovered code**: Create test files or extend existing ones
3. **Focus on edge cases**: Test boundary conditions, error paths, etc.
4. **Document test purpose**: Use descriptive names and docstrings
5. **Submit PR**: Include coverage metrics in the description

**Test requirements**:
- **Must pass**: All existing tests
- **Must reach**: >90% coverage for new code
- **Should include**: Unit tests, integration tests, edge cases
- **Use markers**: `@pytest.mark.slow`, `@pytest.mark.integration` as appropriate

### 💬 Community Support & Advocacy

**Good for**: Everyone! No coding required  
**Effort**: Flexible, as much or as little as you want

**How to contribute**:
1. **Answer questions**: Help on GitHub Discussions or Issues
2. **Share knowledge**: Write blog posts, tutorials, or guides
3. **Report bugs**: If you find issues, report them with clear reproduction steps
4. **Give feedback**: Participate in discussions about features and direction
5. **Promote**: Share the project with your network
6. **Help newcomers**: Welcome and mentor new contributors

**Community spaces**:
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Pull Requests**: Review and discuss code changes
- **Changelog**: Stay updated on recent changes
- **Website**: Share the project link

---

## 🔄 Pull Request Workflow

### Before You Start

1. **Check existing issues and PRs**: Avoid duplicate work
2. **Read the documentation**: Understand the codebase structure
3. **Set up development environment**: See [Development Setup](#development-setup) below

### Creating Your PR

1. **Fork the repository**: Click the "Fork" button on GitHub
2. **Clone your fork**: `git clone https://github.com/YOUR-USERNAME/_codex_.git`
3. **Create a branch**: `git checkout -b descriptive-branch-name`
4. **Make your changes**: Follow the code style guide
5. **Commit with clear messages**: See [Commit Message Guidelines](#commit-message-guidelines)
6. **Push to your fork**: `git push origin your-branch-name`
7. **Open a PR**: Include a clear description and link any related issues

### PR Description Template

Use this template when opening your PR:

```markdown
## Description
Brief description of the changes and why they're needed.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement

## Related Issues
Closes #ISSUE_NUMBER

## Testing
- [ ] Added/updated tests
- [ ] All tests pass locally
- [ ] Coverage maintained above 90%

## Checklist
- [ ] My code follows the code style guidelines
- [ ] I have updated relevant documentation
- [ ] I have added tests for new functionality
- [ ] All tests pass: `pytest`
- [ ] No new warnings are generated
```

### Code Review Process

1. **Automated checks**: Pre-commit hooks and CI/CD tests run automatically
2. **Maintainer review**: At least one maintainer will review your code
3. **Address feedback**: Make requested changes and push them to your branch
4. **Approval & merge**: Once approved, a maintainer will merge your PR

### Commit Message Guidelines

Write clear, concise commit messages following this format:

```
<type>: <subject>

<body>

<footer>
```

**Type** should be one of:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without changing functionality
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc.

**Subject** should be 50 characters or less.

**Body** (optional) should explain what and why, not how. Wrap at 72 characters.

**Footer** (optional) should reference any issues: `Closes #123`

**Examples**:
```
feat: add model validation endpoint

Implement POST /api/validate that accepts a model config and returns
validation results. This enables client-side validation before submission.

Closes #456
```

```
fix: handle None values in config parser

The config parser was crashing when encountering None values in YAML.
Updated to skip None values and use defaults instead.

Closes #789
```

---

## 🛠️ Development Setup

### Requirements

- **Python**: 3.12 or higher
- **Git**: Latest version
- **uv** or **pip**: For package management

### Quick Start (5 minutes)

#### Option 1: Using `uv` (Recommended)

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Install with development dependencies
uv sync --all-extras

# Install pre-commit hooks
pre-commit install

# Verify setup
pytest --collect-only
```

#### Option 2: Using `pip`

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install

# Verify setup
pytest --collect-only
```

### Development Environment

#### IDE Setup

**Visual Studio Code** (Recommended):
1. Install extensions:
   - Python (Microsoft)
   - Pylance (Microsoft)
   - Black Formatter (Microsoft)
   - Ruff (Astral Software)
2. Create `.vscode/settings.json`:
```json
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.mypyEnabled": true
}
```

**PyCharm**:
1. Go to Settings → Editor → Code Style → Python
2. Set line length to 100
3. Enable Black formatter (Settings → Tools → Black)
4. Enable mypy type checking (Settings → Tools → Python Integrated Tools)

#### Running Tests Locally

```bash
# Run all tests
pytest

# Run tests matching a pattern
pytest -k "test_pattern"

# Run with coverage
pytest --cov=src --cov-report=html

# Run only fast tests (skip slow tests)
pytest -m "not slow"

# Run with verbose output
pytest -v

# Run integration tests
pytest -m integration

# Stop on first failure
pytest -x
```

**View coverage report**:
```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

#### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build docs
mkdocs build

# Serve locally
mkdocs serve

# View at http://localhost:8000
```

#### Running Code Quality Checks

```bash
# Format code
black src/ tests/

# Check style
ruff check src/ tests/

# Run type checking
mypy src/

# Sort imports
isort src/ tests/

# Run all pre-commit checks
pre-commit run --all-files

# Or just install hooks and they run automatically on commit
pre-commit install
```

### Troubleshooting Setup Issues

**Python version issues**:
```bash
# Check Python version
python --version

# Use pyenv to install correct version
pyenv install 3.12.0
pyenv local 3.12.0
```

**Virtual environment problems**:
```bash
# Remove and recreate
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -e ".[dev,test]"
```

**Pre-commit installation**:
```bash
# Reinstall pre-commit
pip install pre-commit --upgrade
pre-commit install --install-hooks
```

**Tests not running**:
```bash
# Verify pytest installation
pytest --version

# Collect tests (shows what pytest will run)
pytest --collect-only

# Run with verbose output to see errors
pytest -v
```

---

## 📋 Issue Reporting & Feature Requests

### Reporting a Bug

Please use the bug report template. Include:

1. **Description**: What did you expect vs. what happened?
2. **Steps to Reproduce**: Clear steps to recreate the issue
3. **Environment**: 
   - Python version
   - Installation method (pip, poetry, etc.)
   - Operating system
4. **Error Message**: Full traceback if applicable
5. **Example Code**: Minimal reproducible example
6. **Screenshots**: If applicable

**Example**:
```
Title: Model loading fails with ValueError when config path contains spaces

Description:
When I try to load a model with a config file path that contains spaces,
the loader raises a ValueError.

Steps to Reproduce:
1. Create a config file at `/tmp/my config/model.yaml`
2. Try to load: `model = load_model('/tmp/my config/model.yaml')`
3. Observe the error

Environment:
- Python 3.12.1
- codex-ml 0.1.0
- Ubuntu 22.04

Error Message:
ValueError: Invalid path: /tmp/my config/model.yaml

Example Code:
from codex_ml import load_model
config_path = '/tmp/my config/model.yaml'
model = load_model(config_path)
```

### Requesting a Feature

Use the feature request template. Include:

1. **Title**: Clear, concise description
2. **Motivation**: Why do you need this?
3. **Proposed Solution**: How should it work?
4. **Alternatives**: Other approaches you've considered
5. **Additional Context**: Examples, use cases, etc.

**Example**:
```
Title: Add support for remote model loading from HuggingFace Hub

Motivation:
Currently, models must be local files. Many users want to load models
directly from HuggingFace Hub without downloading first.

Proposed Solution:
Add a remote_source parameter to load_model():
  model = load_model('gpt2', source='huggingface')

Alternatives:
- Manual download with huggingface-hub package first
- Environment variable for default source

Additional Context:
HuggingFace Hub has 10,000+ public models. Many projects want to use
them directly without manual download steps.
```

---

## 🤝 Code Review Guidelines

### For Contributors

When your PR gets reviewed:

1. **Read the feedback carefully**: Reviews help improve code quality
2. **Respond to comments**: Ask clarifying questions if needed
3. **Make updates**: Address all feedback
4. **Re-request review**: Push changes and request review again
5. **Be patient**: Reviewers are volunteers with limited time

### For Reviewers

When reviewing a PR:

1. **Be respectful and constructive**: Focus on the code, not the person
2. **Explain the why**: Say why a change is needed, not just "fix this"
3. **Suggest improvements**: Provide code examples when possible
4. **Acknowledge good work**: Praise what was done well
5. **Request changes only for critical issues**: Use comments for suggestions

**Review checklist**:
- [ ] Tests pass and coverage is maintained
- [ ] Code follows style guidelines
- [ ] Functionality is correct
- [ ] Documentation is clear and complete
- [ ] No obvious performance issues
- [ ] Security considerations addressed
- [ ] Breaking changes documented

---

## 🎓 Learning Resources

### Understanding the Codebase

- **[Codebase Cognitive Map](docs/system/CODEBASE_COGNITIVE_MAP.md)** - High-level architecture
- **[Module Documentation](docs/API_REFERENCE.md)** - Detailed API reference
- **[Architecture Decision Records](docs/adr/)** - Design decisions

### Coding Best Practices

- **[Code Style Guide](docs/dev/CODE_STYLE_GUIDE.md)** - Formatting and naming conventions
- **[Testing Guide](docs/dev/testing.md)** - How to write good tests
- **[Performance Guide](docs/DEVELOPMENT.md)** - Optimization techniques

### Development Tools

- **[Local Testing Guide](docs/dev/CI_LOCAL_TESTING.md)** - Run CI checks locally
- **[Pre-commit Hooks](.pre-commit-config.yaml)** - Automated quality gates
- **[Workflow Documentation](docs/workflows/)** - GitHub Actions setup

---

## 💬 Getting Help

### Finding Answers

1. **Search existing issues**: Many questions are already answered
2. **Check documentation**: Most common questions are covered in docs
3. **Read FAQs**: See [docs/FAQ.md](docs/FAQ.md)
4. **Search discussions**: GitHub Discussions is great for conversations

### Asking Questions

1. **GitHub Discussions**: For questions about usage
2. **GitHub Issues**: For bugs or feature requests (not general questions)
3. **Pull Request Comments**: For questions about code changes

### Getting Feedback

- **Code reviews**: Post a PR and request feedback
- **Design discussions**: Open an issue for substantial changes
- **Community chat**: Join our community spaces (links in README)

### Escalating Issues

If you need help from maintainers:

1. **Label appropriately**: `help-wanted`, `question`, etc.
2. **Be specific**: Provide clear details and examples
3. **Include context**: Link related issues/discussions
4. **Be patient**: Maintainers work on this in their free time

---

## 🏆 Recognition & Credits

We believe in recognizing contributors! Here's how:

### In the Repository

- **Contributors page**: [All contributors listed in CHANGELOG.md](CHANGELOG.md)
- **Commit history**: Your name on all your commits
- **Issue/PR discussions**: Your participation is visible

### In Community

- **Blog posts**: Feature articles about significant contributions
- **Releases**: Mention notable contributors in release notes
- **Discussions**: Recognition in community discussions

### Other Ways to Get Involved

- **Write a blog post**: Share your experience contributing
- **Give a talk**: Present at meetups or conferences
- **Help others**: Answer questions and mentor newcomers
- **Share feedback**: Help shape the future of the project

---

## 📞 Community Channels

### Official Channels

- **GitHub Issues**: Report bugs and feature requests
- **GitHub Discussions**: Ask questions and have conversations
- **GitHub Projects**: Track work and progress
- **Releases**: Latest updates and features

### Getting Connected

- **Follow on GitHub**: Star the repo and watch for updates
- **Read the CHANGELOG**: See what's new in each release
- **Join discussions**: Participate in community conversations
- **Contribute**: Help improve the project

---

## License & Copyright

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

---

## Questions?

- **How do I get started?** See [Development Setup](#development-setup)
- **What can I work on?** Check [Contribution Paths](#contribution-paths)
- **Where's the documentation?** Visit [docs/](docs/)
- **How do I report a bug?** See [Issue Reporting](#issue-reporting--feature-requests)
- **Got a question?** Open a discussion or check [docs/FAQ.md](docs/FAQ.md)

Thank you for contributing! 🎉
