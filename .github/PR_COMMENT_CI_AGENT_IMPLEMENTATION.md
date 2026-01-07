# GitHub Copilot Agent Prompt: Implement CI Testing Agent Infrastructure

**TO BE POSTED AS PR COMMENT**

---

@copilot Implement the complete CI Testing Agent infrastructure per specification

## Context

The ci-testing-agent is currently documented (`.github/agents/ci-testing-agent.md`) but lacks the full modular implementation structure. This task implements the complete infrastructure to make it a standalone, testable, containerized agent.

## Specification

Full implementation plan available in `.github/CI_TESTING_AGENT_IMPLEMENTATION_PLAN.md`

## Required Directory Structure

```
.github/agents/ci-testing-agent/
├── Dockerfile                  # Pinned Python 3.12-slim base
├── cli.py                      # Entry point (manifest + task payload)
├── requirements.txt            # pytest, coverage, GitPython, PyYAML
├── manifest.yaml               # Agent configuration
├── agent/
│   ├── __init__.py
│   ├── generator.py            # Test scaffolding logic
│   ├── executor.py             # Sandbox command runner  
│   ├── validator.py            # Coverage delta evaluator
│   └── reporter.py             # Artifact uploader, PR/commit helpers
├── tests/
│   ├── unit/                   # Mocked OpenAI/network
│   │   ├── __init__.py
│   │   ├── test_generator.py
│   │   ├── test_executor.py
│   │   ├── test_validator.py
│   │   └── test_reporter.py
│   ├── contract/               # Sample request/response pairs
│   │   ├── __init__.py
│   │   └── test_cli_interface.py
│   └── integration/            # Sandbox repo run
│       ├── __init__.py
│       └── test_sandbox_run.py
└── docs/
    └── runbook.md              # Operations guide
```

## Implementation Tasks

### Phase 1: Directory Structure & Manifest (10 min)

Create all directories and the manifest file:

```bash
cd /home/runner/work/_codex_/_codex_
mkdir -p .github/agents/ci-testing-agent/{agent,tests/{unit,contract,integration},docs}
```

**manifest.yaml** content:
```yaml
name: CI Testing Agent
version: 1.0.0
description: Specialized agent for debugging and fixing CI/CD pipeline issues, test failures, and build problems
created: Previous Cycle-12-29
updated: Previous Cycle-12-31

capabilities:
  - ci_pipeline_debugging
  - test_failure_analysis
  - import_path_resolution
  - dependency_management
  - lint_format_fixes

runtime:
  python_version: "3.12"
  base_image: "python:3.12-slim"
  dependencies:
    - pytest>=8.0.0
    - pytest-cov>=4.1.0
    - hypothesis>=6.100
    - GitPython>=3.1.0
    - PyYAML>=6.0

entry_point: cli.py
tools:
  - bash
  - git
  - pytest
  - coverage
```

### Phase 2: Core Modules (60 min)

**Key Requirements for Each Module**:

1. **cli.py**: 
   - Accept `--manifest`, `--task`, `--workspace` arguments
   - Load YAML manifest and JSON task
   - Route to appropriate component (generator/executor/validator)
   - Handle errors gracefully

2. **agent/generator.py**:
   - `TestGenerator` class with `generate(task)` method
   - Extract functions from Python modules using AST
   - Generate test scaffolds using AAA pattern
   - Return list of generated test files

3. **agent/executor.py**:
   - `SandboxExecutor` class with `execute(task)` method
   - Run subprocess commands with timeout
   - Capture stdout/stderr
   - Support parallel execution

4. **agent/validator.py**:
   - `CoverageValidator` class with `validate(task)` method
   - Parse coverage reports (baseline vs current)
   - Compute coverage delta
   - Identify gaps below threshold

5. **agent/reporter.py**:
   - `ArtifactReporter` class with `report(result)` method
   - Generate JSON and Markdown reports
   - Save to `.reports/` directory
   - Support GitHub Actions artifact upload

**Implementation Guidelines**:
- Use type hints throughout
- Include comprehensive docstrings
- Follow existing codebase patterns
- Add error handling for edge cases
- Use pathlib for file operations
- Mock external dependencies in tests

### Phase 3: Dockerfile & Requirements (10 min)

**Dockerfile**:
```dockerfile
FROM python:3.12.3-slim
WORKDIR /agent
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent/ ./agent/
COPY cli.py .
COPY manifest.yaml .
ENTRYPOINT ["python", "cli.py"]
```

**requirements.txt**:
```
pytest==8.0.0
pytest-cov==4.1.0
pytest-randomly==4.0.1
coverage[toml]==7.13.0
hypothesis>=6.100
GitPython>=3.1.0
PyYAML>=6.0
```

### Phase 4: Tests (60 min)

**Unit Tests** (`tests/unit/`):
- Mock all external dependencies
- Test each module independently
- Cover happy path and error cases
- Use pytest fixtures

**Contract Tests** (`tests/contract/`):
- Validate CLI request/response schemas
- Test task type routing
- Ensure backward compatibility

**Integration Tests** (`tests/integration/`):
- Create temporary sandbox repository
- Execute full agent workflow
- Verify artifact generation
- Test end-to-end scenarios

### Phase 5: Documentation (20 min)

**docs/runbook.md** must include:
- Overview and architecture
- Usage examples (direct, Docker, GitHub Copilot)
- Task type specifications with JSON schemas
- Troubleshooting guide
- Monitoring and maintenance procedures

## Success Criteria

✅ All directories and files exist
✅ CLI accepts manifest and task, routes correctly
✅ All 4 core modules (generator, executor, validator, reporter) implemented
✅ Dockerfile builds successfully
✅ All unit tests pass (100% pass rate)
✅ Contract tests validate schemas
✅ Integration test runs complete workflow
✅ Runbook documentation complete
✅ Code follows project conventions (type hints, docstrings, error handling)

## Validation Commands

```bash
# Structure verification
ls -la .github/agents/ci-testing-agent/
tree .github/agents/ci-testing-agent/

# Import verification
cd .github/agents/ci-testing-agent
python -c "from agent.generator import TestGenerator; print('✓ Generator imports')"
python -c "from agent.executor import SandboxExecutor; print('✓ Executor imports')"
python -c "from agent.validator import CoverageValidator; print('✓ Validator imports')"
python -c "from agent.reporter import ArtifactReporter; print('✓ Reporter imports')"

# CLI test
python cli.py --help

# Unit tests
pytest tests/unit/ -v

# Docker build
docker build -t ci-testing-agent .

# Integration test
pytest tests/integration/ -v
```

## Implementation Tips

1. **Start with structure**: Create all directories and empty files first
2. **Implement incrementally**: One module at a time, test as you go
3. **Use existing patterns**: Reference existing test files for patterns
4. **Mock liberally**: Unit tests should not hit real filesystems/networks
5. **Document as you code**: Add docstrings immediately
6. **Validate continuously**: Run tests after each module

## Quality Standards

- **Type Safety**: Use type hints for all function signatures
- **Documentation**: Comprehensive docstrings with Args, Returns, Raises
- **Error Handling**: Try/except blocks with informative messages
- **Testing**: Aim for 90%+ coverage of new code
- **Code Style**: Follow PEP 8, use Black/Ruff formatting
- **Security**: Validate all file paths, sanitize subprocess inputs

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1 | 10 min | Directory structure + manifest |
| Phase 2 | 60 min | Core modules (4 files) |
| Phase 3 | 10 min | Dockerfile + requirements |
| Phase 4 | 60 min | Tests (unit/contract/integration) |
| Phase 5 | 20 min | Documentation (runbook) |
| **Total** | **~2.5 hours** | **Complete implementation** |

## After Completion

1. Commit all files with descriptive message
2. Update `.github/agents/ci-testing-agent.md` to reference new structure
3. Add entry to main AGENTS.md documentation
4. Create example task payloads in `docs/examples/`
5. Update CI workflows to potentially use containerized agent

## References

- **Implementation Plan**: `.github/CI_TESTING_AGENT_IMPLEMENTATION_PLAN.md` (detailed specs)
- **Agent Documentation**: `.github/agents/ci-testing-agent.md` (current guide)
- **Existing Tests**: `tests/` directory (for patterns and conventions)
- **Docker Examples**: `Dockerfile.*` files in repository root

---

**Focus**: Implement complete, tested, documented ci-testing-agent infrastructure
**Quality**: Production-ready code with comprehensive tests
**Timeline**: Complete in single session (~2.5 hours)

Good luck! 🚀
