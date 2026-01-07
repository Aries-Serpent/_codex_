# CI Testing Agent Implementation Plan

**Date**: Previous Cycle-12-31 20:30 UTC  
**Purpose**: Complete implementation of ci-testing-agent infrastructure  
**Context**: Required structure verification and gap analysis

---

## Current State Analysis

### ✅ What Exists
1. **Documentation**: `.github/agents/ci-testing-agent.md` (comprehensive agent guide)
2. **Integration**: Agent callable via custom tool `ci-testing-agent`
3. **Functionality**: Currently working for test generation and CI debugging

### ❌ What's Missing

The required full implementation structure is not present:
- No dedicated `ci-testing-agent/` directory
- Missing modular Python implementation
- No standalone CLI or manifest
- Missing unit/contract/integration tests
- No Docker containerization

---

## Required Structure (Per Specification)

```
ci-testing-agent/
├── Dockerfile                  # Pinned base image for containerization
├── cli.py                      # Entry point: accepts manifest + task payload
├── agent/
│   ├── __init__.py
│   ├── generator.py            # Test scaffolding logic
│   ├── executor.py             # Sandbox command runner
│   ├── validator.py            # Coverage delta evaluator
│   └── reporter.py             # Artifact uploader, PR/commit helpers
├── tests/
│   ├── unit/                   # Mocked OpenAI/network tests
│   ├── contract/               # Sample request/response pairs
│   └── integration/            # Sandbox repo run tests
├── docs/
│   └── runbook.md              # Operations guide
└── manifest.yaml               # Agent configuration
```

---

## Implementation Plan

### Phase 1: Directory Structure & Core Files (30-40 min)

**Task 1.1: Create Directory Structure**
```bash
mkdir -p .github/agents/ci-testing-agent/{agent,tests/{unit,contract,integration},docs}
touch .github/agents/ci-testing-agent/{Dockerfile,cli.py,manifest.yaml}
touch .github/agents/ci-testing-agent/agent/{__init__.py,generator.py,executor.py,validator.py,reporter.py}
touch .github/agents/ci-testing-agent/docs/runbook.md
```

**Task 1.2: Create manifest.yaml**
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

entry_point: cli.py
tools:
  - bash
  - git
  - pytest
  - coverage
```

### Phase 2: Core Agent Modules (60-90 min)

**Task 2.1: Implement cli.py**
```python
"""
CI Testing Agent CLI
Entry point for agent invocation with manifest and task payload.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from agent.generator import TestGenerator
from agent.executor import SandboxExecutor
from agent.validator import CoverageValidator
from agent.reporter import ArtifactReporter


def load_manifest(path: Path) -> Dict[str, Any]:
    """Load task manifest."""
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="CI Testing Agent")
    parser.add_argument("--manifest", required=True, help="Task manifest file")
    parser.add_argument("--task", required=True, help="Task payload JSON")
    parser.add_argument("--workspace", default=".", help="Repository workspace")
    args = parser.parse_args()
    
    # Load manifest and task
    manifest = load_manifest(Path(args.manifest))
    task = json.loads(args.task)
    
    # Initialize components
    generator = TestGenerator(workspace=Path(args.workspace))
    executor = SandboxExecutor(workspace=Path(args.workspace))
    validator = CoverageValidator(workspace=Path(args.workspace))
    reporter = ArtifactReporter(workspace=Path(args.workspace))
    
    # Execute task
    print(f"🤖 CI Testing Agent v{manifest['version']}")
    print(f"📋 Task: {task.get('type', 'unknown')}")
    
    try:
        if task['type'] == 'generate_tests':
            result = generator.generate(task)
        elif task['type'] == 'validate_coverage':
            result = validator.validate(task)
        elif task['type'] == 'execute_tests':
            result = executor.execute(task)
        else:
            raise ValueError(f"Unknown task type: {task['type']}")
        
        # Report results
        reporter.report(result)
        
        print("✅ Task completed successfully")
        return 0
    except Exception as e:
        print(f"❌ Task failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Task 2.2: Implement agent/generator.py**
```python
"""
Test Scaffolding Logic
Generates test files based on coverage gaps and templates.
"""
from pathlib import Path
from typing import Dict, List, Any
import ast


class TestGenerator:
    """Generates test scaffolding for uncovered code paths."""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.templates_dir = Path(__file__).parent / "templates"
    
    def generate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test files based on task specification."""
        target_module = task.get('module')
        coverage_threshold = task.get('threshold', 85)
        
        # Analyze module structure
        module_path = self.workspace / "src" / target_module.replace('.', '/')
        functions = self._extract_functions(module_path)
        
        # Generate test scaffolds
        test_files = []
        for func in functions:
            if not self._has_test_coverage(func):
                test_code = self._scaffold_test(func)
                test_files.append({
                    'path': f"tests/{target_module}/test_{func['name']}_phase9_1.py",
                    'content': test_code
                })
        
        return {
            'status': 'success',
            'files_generated': len(test_files),
            'test_files': test_files
        }
    
    def _extract_functions(self, module_path: Path) -> List[Dict[str, Any]]:
        """Extract function definitions from module."""
        functions = []
        for py_file in module_path.rglob("*.py"):
            with open(py_file) as f:
                tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append({
                            'name': node.name,
                            'file': str(py_file),
                            'lineno': node.lineno
                        })
        return functions
    
    def _has_test_coverage(self, func: Dict[str, Any]) -> bool:
        """Check if function has existing test coverage."""
        # Simplified - would use coverage.py data
        return False
    
    def _scaffold_test(self, func: Dict[str, Any]) -> str:
        """Generate test scaffold for function."""
        return f'''"""
Tests for {func['name']} function.
Generated by CI Testing Agent.
"""
import pytest
from {func['file'].replace('src/', '').replace('.py', '').replace('/', '.')} import {func['name']}


class Test{func['name'].title().replace('_', '')}:
    """Test {func['name']} functionality."""
    
    def test_{func['name']}_basic(self):
        """Test basic functionality of {func['name']}."""
        # Arrange
        # TODO: Setup test data
        
        # Act
        # result = {func['name']}(...)
        
        # Assert
        # assert result == expected
        pytest.skip("Generated test - needs implementation")
'''
```

**Task 2.3: Implement agent/executor.py**
```python
"""
Sandbox Command Runner
Executes tests in isolated environment with timeout and resource limits.
"""
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import shlex


class SandboxExecutor:
    """Executes test commands in sandboxed environment."""
    
    def __init__(self, workspace: Path, timeout: int = 300):
        self.workspace = workspace
        self.timeout = timeout
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test command in sandbox."""
        command = task.get('command', 'pytest')
        args = task.get('args', [])
        env = task.get('env', {})
        
        full_command = [command] + args
        
        try:
            result = subprocess.run(
                full_command,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**subprocess.os.environ, **env}
            )
            
            return {
                'status': 'success' if result.returncode == 0 else 'failure',
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(full_command)
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'returncode': -1,
                'error': f'Command timed out after {self.timeout}s'
            }
        except Exception as e:
            return {
                'status': 'error',
                'returncode': -1,
                'error': str(e)
            }
    
    def execute_parallel(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple test commands in parallel."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.execute, task): task for task in tasks}
            for future in as_completed(futures):
                results.append(future.result())
        
        return results
```

**Task 2.4: Implement agent/validator.py**
```python
"""
Coverage Delta Evaluator
Validates coverage improvements and identifies gaps.
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json


class CoverageValidator:
    """Validates test coverage and computes deltas."""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
    
    def validate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate coverage meets target threshold."""
        baseline_file = task.get('baseline', 'baseline_coverage.txt')
        target_threshold = task.get('threshold', 85)
        
        # Parse coverage data
        baseline = self._parse_coverage(self.workspace / baseline_file)
        current = self._run_coverage()
        
        # Compute delta
        delta = self._compute_delta(baseline, current)
        
        # Validate threshold
        meets_threshold = current['total'] >= target_threshold
        
        return {
            'status': 'success' if meets_threshold else 'below_threshold',
            'baseline_coverage': baseline['total'],
            'current_coverage': current['total'],
            'delta': delta,
            'threshold': target_threshold,
            'meets_threshold': meets_threshold,
            'gaps': self._identify_gaps(current, target_threshold)
        }
    
    def _parse_coverage(self, coverage_file: Path) -> Dict[str, Any]:
        """Parse coverage report file."""
        # Simplified - would parse actual coverage.py output
        with open(coverage_file) as f:
            lines = f.readlines()
            for line in lines:
                if 'TOTAL' in line:
                    # Extract coverage percentage
                    parts = line.split()
                    coverage_pct = float(parts[-1].rstrip('%'))
                    return {'total': coverage_pct}
        return {'total': 0.0}
    
    def _run_coverage(self) -> Dict[str, Any]:
        """Run coverage analysis on current codebase."""
        import subprocess
        result = subprocess.run(
            ['pytest', '--cov=src', '--cov=agents', '--cov=scripts', '--cov-report=json'],
            cwd=self.workspace,
            capture_output=True
        )
        
        if result.returncode == 0:
            coverage_json = self.workspace / 'coverage.json'
            if coverage_json.exists():
                with open(coverage_json) as f:
                    data = json.load(f)
                    return {'total': data['totals']['percent_covered']}
        
        return {'total': 0.0}
    
    def _compute_delta(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> float:
        """Compute coverage delta."""
        return current['total'] - baseline['total']
    
    def _identify_gaps(self, current: Dict[str, Any], threshold: float) -> List[str]:
        """Identify modules below coverage threshold."""
        gaps = []
        # Would analyze per-module coverage
        if current['total'] < threshold:
            gaps.append(f"Overall coverage {current['total']}% below {threshold}%")
        return gaps
```

**Task 2.5: Implement agent/reporter.py**
```python
"""
Artifact Uploader and PR/Commit Helpers
Reports results and manages GitHub integration.
"""
from pathlib import Path
from typing import Dict, Any, List
import json


class ArtifactReporter:
    """Reports test results and uploads artifacts."""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.reports_dir = workspace / ".reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def report(self, result: Dict[str, Any]) -> None:
        """Generate and save test report."""
        report_file = self.reports_dir / f"report_{result.get('timestamp', 'latest')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"📄 Report saved: {report_file}")
        
        # Generate markdown summary
        summary = self._generate_summary(result)
        summary_file = self.reports_dir / "summary.md"
        
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"📝 Summary saved: {summary_file}")
    
    def _generate_summary(self, result: Dict[str, Any]) -> str:
        """Generate markdown summary of results."""
        status = result.get('status', 'unknown')
        emoji = '✅' if status == 'success' else '❌'
        
        summary = f"""# CI Testing Agent Report

## Status: {emoji} {status.upper()}

### Results
"""
        
        if 'files_generated' in result:
            summary += f"- **Files Generated**: {result['files_generated']}\n"
        
        if 'current_coverage' in result:
            summary += f"- **Current Coverage**: {result['current_coverage']}%\n"
            summary += f"- **Baseline Coverage**: {result.get('baseline_coverage', 'N/A')}%\n"
            summary += f"- **Delta**: {result.get('delta', 'N/A')}%\n"
        
        if 'gaps' in result and result['gaps']:
            summary += f"\n### Coverage Gaps\n"
            for gap in result['gaps']:
                summary += f"- {gap}\n"
        
        return summary
    
    def upload_artifact(self, file_path: Path, artifact_name: str) -> bool:
        """Upload artifact to GitHub Actions."""
        # Would integrate with GitHub Actions artifact API
        print(f"📦 Artifact ready for upload: {artifact_name}")
        return True
    
    def create_pr_comment(self, pr_number: int, comment: str) -> bool:
        """Create comment on pull request."""
        # Would integrate with GitHub API
        print(f"💬 PR comment ready for #{pr_number}")
        return True
```

### Phase 3: Dockerfile & Containerization (20-30 min)

**Task 3.1: Create Dockerfile**
```dockerfile
# Pinned base image for reproducibility
FROM python:3.12.3-slim

# Set working directory
WORKDIR /agent

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent/ ./agent/
COPY cli.py .
COPY manifest.yaml .

# Set entry point
ENTRYPOINT ["python", "cli.py"]
```

**Task 3.2: Create requirements.txt**
```
pytest==8.0.0
pytest-cov==4.1.0
pytest-randomly==4.0.1
coverage[toml]==7.13.0
hypothesis>=6.100
GitPython>=3.1.0
PyYAML>=6.0
```

### Phase 4: Tests (60-90 min)

**Task 4.1: Unit Tests (tests/unit/)**
```python
# tests/unit/test_generator.py
"""Unit tests for TestGenerator with mocked dependencies."""
import pytest
from unittest.mock import Mock, patch
from agent.generator import TestGenerator


class TestTestGenerator:
    def test_generate_creates_test_files(self, tmp_path):
        """Test that generator creates test file scaffolds."""
        generator = TestGenerator(workspace=tmp_path)
        task = {
            'module': 'codex.ingest',
            'threshold': 85
        }
        
        with patch.object(generator, '_extract_functions') as mock_extract:
            mock_extract.return_value = [{'name': 'test_func', 'file': 'src/module.py', 'lineno': 10}]
            result = generator.generate(task)
        
        assert result['status'] == 'success'
        assert result['files_generated'] > 0
```

**Task 4.2: Contract Tests (tests/contract/)**
```python
# tests/contract/test_cli_interface.py
"""Contract tests with sample request/response pairs."""
import json
from pathlib import Path


class TestCLIContract:
    def test_generate_tests_request_response(self):
        """Test CLI contract for generate_tests task."""
        request = {
            "type": "generate_tests",
            "module": "codex.ingest",
            "threshold": 85
        }
        
        expected_response = {
            "status": "success",
            "files_generated": 5,
            "test_files": [...]
        }
        
        # Validate request schema
        assert "type" in request
        assert "module" in request
        
        # Validate response schema
        assert "status" in expected_response
        assert "files_generated" in expected_response
```

**Task 4.3: Integration Tests (tests/integration/)**
```python
# tests/integration/test_sandbox_run.py
"""Integration tests running agent in sandbox repo."""
import subprocess
import tempfile
from pathlib import Path


class TestSandboxIntegration:
    def test_full_agent_execution(self, tmp_path):
        """Test complete agent execution in sandbox."""
        # Create test repository
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        
        # Create manifest
        manifest = repo_dir / "manifest.yaml"
        manifest.write_text("name: test\nversion: 1.0.0\n")
        
        # Create task
        task = '{"type": "generate_tests", "module": "test"}'
        
        # Execute agent
        result = subprocess.run(
            ["python", "cli.py", "--manifest", str(manifest), "--task", task],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True
        )
        
        assert result.returncode == 0
```

### Phase 5: Documentation (30-40 min)

**Task 5.1: Create docs/runbook.md**
```markdown
# CI Testing Agent Runbook

## Overview
Operational guide for the CI Testing Agent.

## Architecture
[Component diagram and data flow]

## Usage

### Direct Invocation
```bash
python cli.py --manifest manifest.yaml --task '{"type": "generate_tests", "module": "codex.ingest"}'
```

### Docker Invocation
```bash
docker run ci-testing-agent --manifest /workspace/manifest.yaml --task '...'
```

### GitHub Copilot Integration
```
@copilot use ci-testing-agent to add tests for module X
```

## Task Types

### generate_tests
Generates test scaffolds for uncovered code.

**Input**:
```json
{
  "type": "generate_tests",
  "module": "codex.ingest",
  "threshold": 85
}
```

**Output**:
```json
{
  "status": "success",
  "files_generated": 5,
  "test_files": [...]
}
```

### validate_coverage
Validates coverage meets threshold.

### execute_tests
Runs tests in sandboxed environment.

## Troubleshooting

### Import Errors
[Solutions]

### Timeout Issues
[Solutions]

### Coverage Calculation
[Solutions]

## Monitoring
[Metrics and logging]

## Maintenance
[Update procedures]
```

---

## Implementation Timeline

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 1: Structure | 30-40 min | High |
| Phase 2: Core Modules | 60-90 min | High |
| Phase 3: Docker | 20-30 min | Medium |
| Phase 4: Tests | 60-90 min | Medium |
| Phase 5: Documentation | 30-40 min | Low |
| **Total** | **3-4 hours** | - |

---

## Validation Checklist

After implementation, verify:
- [ ] All directory structure exists
- [ ] All Python modules importable
- [ ] CLI accepts manifest and task
- [ ] Docker image builds successfully
- [ ] Unit tests pass
- [ ] Contract tests validate schemas
- [ ] Integration tests run in sandbox
- [ ] Documentation complete
- [ ] Runbook has operational procedures

---

## Next Steps

1. **Immediate**: Create directory structure and manifest
2. **Short-term**: Implement core modules (generator, executor, validator, reporter)
3. **Medium-term**: Add Docker support and testing
4. **Long-term**: Enhance with ML-based test generation

---

**Status**: 📋 PLAN READY  
**Implementation Required**: YES  
**Estimated Effort**: 3-4 hours  
**Complexity**: Medium  
**Dependencies**: None (standalone implementation)
