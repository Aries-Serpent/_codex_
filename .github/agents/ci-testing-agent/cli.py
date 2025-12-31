"""
CI Testing Agent CLI
Entry point for agent invocation with manifest and task payload.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from agent.executor import SandboxExecutor
from agent.generator import TestGenerator
from agent.reporter import ArtifactReporter
from agent.validator import CoverageValidator


def load_manifest(path: Path) -> Dict[str, Any]:
    """
    Load task manifest from YAML file.
    
    Args:
        path: Path to manifest YAML file
        
    Returns:
        Dictionary containing manifest data
        
    Raises:
        FileNotFoundError: If manifest file doesn't exist
        yaml.YAMLError: If manifest is invalid YAML
    """
    import yaml

    with open(path) as f:
        return yaml.safe_load(f)


def main() -> int:
    """
    Main entry point for CI Testing Agent.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="CI Testing Agent - Specialized agent for CI/CD debugging and test failures"
    )
    parser.add_argument(
        "--manifest", required=True, type=Path, help="Task manifest YAML file"
    )
    parser.add_argument(
        "--task", required=True, help="Task payload as JSON string"
    )
    parser.add_argument(
        "--workspace",
        default=".",
        type=Path,
        help="Repository workspace directory (default: current directory)",
    )
    args = parser.parse_args()

    try:
        # Load manifest and task
        manifest = load_manifest(args.manifest)
        task = json.loads(args.task)

        # Add timestamp to task
        task["timestamp"] = datetime.utcnow().isoformat()

        # Initialize components
        workspace = args.workspace.resolve()
        generator = TestGenerator(workspace=workspace)
        executor = SandboxExecutor(workspace=workspace)
        validator = CoverageValidator(workspace=workspace)
        reporter = ArtifactReporter(workspace=workspace)

        # Print header
        print(f"🤖 CI Testing Agent v{manifest['version']}")
        print(f"📋 Task Type: {task.get('type', 'unknown')}")
        print(f"📂 Workspace: {workspace}")
        print("-" * 60)

        # Execute task based on type
        task_type = task.get("type")
        result = None

        if task_type == "generate_tests":
            print("🔨 Generating test scaffolds...")
            result = generator.generate(task)
        elif task_type == "validate_coverage":
            print("📊 Validating coverage...")
            result = validator.validate(task)
        elif task_type == "execute_tests":
            print("🧪 Executing tests...")
            result = executor.execute(task)
        elif task_type == "debug_ci_failure":
            print("🔍 Debugging CI failure...")
            # Combine execution and validation
            exec_result = executor.execute(task)
            result = {**exec_result, "task_type": "debug_ci_failure"}
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        # Report results
        print("-" * 60)
        reporter.report(result)

        # Determine exit code
        if result.get("status") == "success":
            print("✅ Task completed successfully")
            return 0
        else:
            print(f"⚠️ Task completed with status: {result.get('status')}")
            return 1

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in task payload: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Task failed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
