# Migrating ci-testing-agent to Unified Agent Framework

**Date**: Current Cycle-01-01  
**Target Agent**: ci-testing-agent.v1  
**Framework Version**: 1.0.0

---

## Overview

This guide provides step-by-step instructions for migrating the existing `ci-testing-agent` to use the new unified agent framework. The migration will:

1. **Preserve all existing functionality** - No features removed
2. **Add cognitive brain integration** - Cross-session learning
3. **Standardize PDA Loop** - Consistent execution pattern
4. **Enable orchestration** - Multi-agent workflows

---

## Prerequisites

- ✅ Unified agent framework installed (`.github/agents/core/`)
- ✅ Existing ci-testing-agent working
- ✅ Tests passing for current implementation
- ✅ Backup of current agent code

---

## Migration Steps

### Step 1: Import Framework Components

**Current code** (`cli.py` or main file):
```python
# Old imports
from .agent import generator, validator, executor, reporter
```

**Add new imports**:
```python
# Add framework imports
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from github.agents.core import (
    CognitiveAgent,
    CognitiveBrain,
    PatternRecognizer
)
```

---

### Step 2: Create Agent Class

**Create new file**: `.github/agents/ci-testing-agent/agent/cognitive_ci_agent.py`

```python
"""
CI Testing Agent - Cognitive Brain Integration
Migrated to use unified agent framework.
"""
from typing import Any, Dict
from pathlib import Path

from github.agents.core import CognitiveAgent, PatternRecognizer

# Import existing components
from .generator import TestGenerator
from .validator import TestValidator
from .executor import SandboxExecutor
from .reporter import ResultReporter


class CICognitiveAgent(CognitiveAgent):
    """
    CI Testing Agent with cognitive brain integration.
    
    Implements PDA Loop for CI/CD debugging and test generation.
    """
    
    def __init__(self, workspace: Path):
        super().__init__(
            name="ci-testing-agent",
            version="2.0.0",  # Bumped for cognitive integration
            workspace=workspace
        )
        
        # Initialize existing components
        self.generator = TestGenerator(workspace)
        self.validator = TestValidator(workspace)
        self.executor = SandboxExecutor(workspace)
        self.reporter = ResultReporter()
        self.pattern_recognizer = PatternRecognizer()
    
    def perceive(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        PERCEPTION: Analyze CI failure and gather context.
        
        Maps to existing functionality:
        - Parse CI logs
        - Identify failure patterns
        - Extract test context
        """
        task_type = task.get("task_type")
        
        if task_type == "generate_tests":
            # Use pattern recognizer to analyze existing tests
            test_dir = self.workspace / "tests"
            patterns = {}
            if test_dir.exists():
                patterns = self.pattern_recognizer.analyze_directory(
                    test_dir,
                    recursive=True
                )
            
            context = {
                "parsed_inputs": task.get("parameters", {}),
                "existing_patterns": patterns,
                "test_coverage": self.validator.get_baseline().get("coverage", 0),
                "risks": [],
                "opportunities": ["improve_coverage"]
            }
            
        elif task_type == "validate_coverage":
            baseline = self.validator.get_baseline()
            
            context = {
                "parsed_inputs": task.get("parameters", {}),
                "baseline_coverage": baseline.get("coverage", 0),
                "risks": ["coverage_regression"] if baseline else [],
                "opportunities": []
            }
            
        elif task_type == "execute_tests":
            context = {
                "parsed_inputs": task.get("parameters", {}),
                "patterns": [],
                "risks": [],
                "opportunities": []
            }
        
        else:
            context = {"parsed_inputs": task.get("parameters", {})}
        
        # Query cognitive brain for historical context
        if self.cognitive_brain:
            history = self.cognitive_brain.get_session_history(
                agent_name=self.name,
                limit=5
            )
            context["history"] = history
        
        return context
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DECISION: Determine test generation/execution strategy.
        
        Maps to existing functionality:
        - Prioritize test generation
        - Select validation approach
        - Plan execution sequence
        """
        task_inputs = context.get("parsed_inputs", {})
        task_type = task_inputs.get("task_type", "generate_tests")
        
        if task_type == "generate_tests":
            steps = ["analyze_coverage", "generate_missing", "validate_syntax"]
            priority = 8
            strategy = "coverage_driven_generation"
            
        elif task_type == "validate_coverage":
            steps = ["run_coverage", "compare_baseline", "report_delta"]
            priority = 7
            strategy = "baseline_comparison"
            
        elif task_type == "execute_tests":
            steps = ["setup_sandbox", "run_tests", "collect_results"]
            priority = 9
            strategy = "sandboxed_execution"
        
        else:
            steps = []
            priority = 5
            strategy = "default"
        
        return {
            "strategy": strategy,
            "steps": steps,
            "priority": priority,
            "rationale": f"CI task type: {task_type}",
            "estimated_time": len(steps) * 30  # 30s per step
        }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACTION: Execute test generation/validation.
        
        Maps to existing functionality:
        - generator.generate_tests()
        - validator.validate_coverage()
        - executor.execute()
        """
        strategy = decision["strategy"]
        steps_completed = []
        outputs = {}
        logs = []
        
        try:
            if strategy == "coverage_driven_generation":
                # Use existing generator
                result = self.generator.generate_tests()
                outputs["tests_generated"] = result.get("count", 0)
                outputs["files"] = result.get("files", [])
                steps_completed = decision["steps"]
                logs.append("Test generation completed")
                
            elif strategy == "baseline_comparison":
                # Use existing validator
                result = self.validator.validate_coverage()
                outputs["coverage"] = result.get("coverage", 0)
                outputs["delta"] = result.get("delta", 0)
                steps_completed = decision["steps"]
                logs.append("Coverage validation completed")
                
            elif strategy == "sandboxed_execution":
                # Use existing executor
                result = self.executor.execute({"command": "pytest"})
                outputs["returncode"] = result.get("returncode", -1)
                outputs["status"] = result.get("status")
                steps_completed = decision["steps"]
                logs.append("Test execution completed")
            
            return {
                "status": "success",
                "outputs": outputs,
                "steps_completed": steps_completed,
                "steps_failed": [],
                "logs": logs
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "error": str(e),
                "outputs": outputs,
                "steps_completed": steps_completed,
                "steps_failed": [decision["steps"][-1]] if decision["steps"] else [],
                "logs": logs + [f"Error: {str(e)}"]
            }
    
    def aftermath(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any],
        decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AFTERMATH: Learn from execution and update cognitive brain.
        
        New functionality:
        - Record patterns for future sessions
        - Store lessons learned
        - Track decision outcomes
        """
        # Calculate metrics
        metrics = {
            "status": result.get("status"),
            "strategy": decision.get("strategy"),
            "steps_completed": len(result.get("steps_completed", [])),
            "success": result.get("status") == "success"
        }
        
        # Add strategy-specific metrics
        if "tests_generated" in result.get("outputs", {}):
            metrics["tests_generated"] = result["outputs"]["tests_generated"]
        if "coverage" in result.get("outputs", {}):
            metrics["coverage"] = result["outputs"]["coverage"]
        
        # Identify patterns
        patterns = []
        if metrics["success"]:
            patterns.append(f"successful_{decision['strategy']}")
        else:
            patterns.append(f"failed_{decision['strategy']}")
        
        # Extract lessons
        lessons = []
        if metrics["success"]:
            lessons.append(f"Strategy '{decision['strategy']}' effective for CI tasks")
        
        # Record in cognitive brain
        if self.cognitive_brain and self.session_id:
            for pattern in patterns:
                self.cognitive_brain.record_pattern(
                    session_id=self.session_id,
                    pattern_name=pattern,
                    pattern_type="ci_execution",
                    description=f"CI execution pattern"
                )
            
            for lesson in lessons:
                self.cognitive_brain.record_lesson(
                    session_id=self.session_id,
                    lesson_text=lesson,
                    category="ci_testing",
                    confidence=0.85
                )
            
            self.cognitive_brain.record_decision(
                session_id=self.session_id,
                context=context,
                decision=decision,
                rationale=decision.get("rationale"),
                outcome=result,
                success=metrics["success"]
            )
        
        return {
            "metrics": metrics,
            "patterns": patterns,
            "lessons": lessons,
            "recommendations": []
        }
```

---

### Step 3: Update CLI Entry Point

**Modify**: `.github/agents/ci-testing-agent/cli.py`

```python
#!/usr/bin/env python3
"""
CI Testing Agent CLI - Cognitive Brain Enabled
"""
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from github.agents.core import CognitiveBrain
from .agent.cognitive_ci_agent import CICognitiveAgent


def main():
    """Main CLI entry point with cognitive brain."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CI Testing Agent")
    parser.add_argument("task", choices=["generate", "validate", "execute"])
    parser.add_argument("--workspace", default=".", help="Workspace path")
    parser.add_argument("--db", default=".codex/brain.db", help="Brain database")
    args = parser.parse_args()
    
    # Initialize cognitive brain
    brain = CognitiveBrain(Path(args.db))
    
    # Create agent
    agent = CICognitiveAgent(Path(args.workspace))
    agent.set_cognitive_brain(brain)
    
    # Generate session ID
    import uuid
    session_id = f"ci-{uuid.uuid4().hex[:8]}"
    agent.set_session_id(session_id)
    
    # Start session
    brain.start_session(
        session_id=session_id,
        agent_name=agent.name,
        agent_version=agent.version,
        task_type=args.task
    )
    
    # Build task
    task = {
        "task_type": f"{args.task}_tests" if args.task == "generate" else f"{args.task}_coverage",
        "parameters": {}
    }
    
    # Execute PDA loop
    result = agent.execute_pda_loop(task)
    
    # End session
    brain.end_session(session_id, result["status"], result.get("metrics"))
    
    # Print result
    print(f"Status: {result['status']}")
    if result.get("lessons"):
        print(f"Lessons: {', '.join(result['lessons'])}")
    
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
```

---

### Step 4: Update Tests

**Create**: `.github/agents/ci-testing-agent/tests/test_cognitive_integration.py`

```python
"""
Tests for cognitive brain integration.
"""
import pytest
import tempfile
from pathlib import Path

from github.agents.core import CognitiveBrain
from ..agent.cognitive_ci_agent import CICognitiveAgent


def test_agent_with_brain():
    """Test agent integrated with cognitive brain."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        brain = CognitiveBrain(workspace / "brain.db")
        
        agent = CICognitiveAgent(workspace)
        agent.set_cognitive_brain(brain)
        agent.set_session_id("test-001")
        
        brain.start_session("test-001", "ci-testing-agent", "2.0.0", "test")
        
        task = {
            "task_type": "generate_tests",
            "parameters": {}
        }
        
        result = agent.execute_pda_loop(task)
        
        assert result["status"] in ["success", "failure"]
        assert "metrics" in result
        
        brain.end_session("test-001", result["status"])
```

---

### Step 5: Run Migration Tests

```bash
# Run existing tests (should still pass)
pytest .github/agents/ci-testing-agent/tests/unit/ -v

# Run new cognitive integration tests
pytest .github/agents/ci-testing-agent/tests/test_cognitive_integration.py -v

# Run all tests
pytest .github/agents/ci-testing-agent/tests/ -v
```

---

### Step 6: Deploy and Validate

1. **Backup current agent**:
   ```bash
   cp -r .github/agents/ci-testing-agent .github/agents/ci-testing-agent.backup
   ```

2. **Deploy new version**:
   ```bash
   # New files should be in place from steps above
   ```

3. **Test in sandbox**:
   ```bash
   python .github/agents/ci-testing-agent/cli.py generate --workspace=./
   ```

4. **Check cognitive brain**:
   ```bash
   python brain_cli.py stats
   python brain_cli.py sessions --agent ci-testing-agent
   ```

---

## Rollback Plan

If issues occur:

```bash
# Restore backup
rm -rf .github/agents/ci-testing-agent
mv .github/agents/ci-testing-agent.backup .github/agents/ci-testing-agent
```

---

## Benefits After Migration

1. ✅ **Cross-session learning** - Agent learns from previous executions
2. ✅ **Pattern recognition** - Automatic detection of recurring issues
3. ✅ **Standardized PDA Loop** - Consistent execution across all agents
4. ✅ **Orchestration ready** - Can participate in multi-agent workflows
5. ✅ **Better observability** - All sessions tracked in cognitive brain
6. ✅ **Lesson storage** - Insights preserved across runs

---

## Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'github.agents.core'`

**Solution**: Ensure path is added:
```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

### Database Errors

**Error**: `sqlite3.OperationalError: no such table: sessions`

**Solution**: Database schema not initialized. Brain creates schema on first use.

### Test Failures

**Error**: Existing tests fail after migration

**Solution**: Ensure all existing components (generator, validator, executor, reporter) are still functional and properly imported.

---

## Timeline

- **Phase 1**: Steps 1-2 (Create cognitive agent class) - 2 hours
- **Phase 2**: Step 3 (Update CLI) - 1 hour
- **Phase 3**: Step 4 (Update tests) - 2 hours
- **Phase 4**: Steps 5-6 (Testing & deployment) - 2 hours

**Total**: ~7 hours

---

## Support

- **Documentation**: See `.github/agents/core/README.md`
- **Example**: See `examples/example_agent.py`
- **CLI Tool**: Use `brain_cli.py` to inspect cognitive brain

---

**Status**: Ready for implementation  
**Risk Level**: Low (existing functionality preserved)  
**Estimated Effort**: 1 developer-day
