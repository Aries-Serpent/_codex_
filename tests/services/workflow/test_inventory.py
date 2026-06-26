"""Tests for workflow inventory system."""

import pytest

from src.services.workflow.inventory import WorkflowInventory
from src.services.workflow.parser import WorkflowParser
from src.services.workflow.types import (
    TriggerType,
)
from tests.services.workflow._helpers import raise_exception


@pytest.fixture
def temp_workflows_dir(tmp_path):
    """Create a temporary workflows directory."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    return workflows_dir


@pytest.fixture
def sample_workflow_content():
    """Sample workflow YAML content."""
    return """
name: Test Workflow
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        type: choice
        options:
          - dev
          - staging
          - production

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest
"""


@pytest.fixture
def sample_reusable_workflow():
    """Sample reusable workflow content."""
    return """
name: Reusable Workflow
on:
  workflow_call:
    inputs:
      config:
        required: true
        type: string

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building with ${{ inputs.config }}"
"""


def test_workflow_inventory_initialization(temp_workflows_dir):
    """Test that inventory can be initialized."""
    inventory = WorkflowInventory(temp_workflows_dir)
    assert inventory.workflows_dir == temp_workflows_dir, "workflows_dir is not valid"
    assert isinstance(inventory.parser, WorkflowParser)
    assert len(inventory.workflows) == 0, "Collection must not be empty"


def test_scan_empty_directory(temp_workflows_dir):
    """Test scanning an empty directory."""
    inventory = WorkflowInventory(temp_workflows_dir)
    count = inventory.scan()
    assert count == 0, "Count must be greater than zero"
    assert len(inventory.workflows) == 0, "Collection must not be empty"


def test_scan_with_workflows(temp_workflows_dir, sample_workflow_content):
    """Test scanning directory with workflows."""
    # Create a workflow file
    workflow_file = temp_workflows_dir / "test.yml"
    workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    count = inventory.scan()

    assert count == 1, "Count must be greater than zero"
    assert "test.yml" in inventory.workflows, "Condition must be true"

    workflow = inventory.get_workflow("test.yml")
    assert workflow is not None, "workflow must be initialized"
    assert workflow.name == "Test Workflow", "name is not valid"
    assert workflow.is_triggerable is True, "is_triggerable is not valid"


def test_scan_skips_disabled_workflows(temp_workflows_dir, sample_workflow_content):
    """Test that disabled workflows are skipped."""
    # Create enabled and disabled workflows
    enabled_file = temp_workflows_dir / "enabled.yml"
    enabled_file.write_text(sample_workflow_content)

    disabled_file = temp_workflows_dir / "disabled.yml.disabled"
    disabled_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    count = inventory.scan()

    assert count == 1, "Count must be greater than zero"
    assert "enabled.yml" in inventory.workflows, "Condition must be true"
    assert "disabled.yml.disabled" not in inventory.workflows, "Condition must be true"


def test_get_triggerable_workflows(
    temp_workflows_dir, sample_workflow_content, sample_reusable_workflow
):
    """Test filtering triggerable workflows."""
    # Create triggerable and non-triggerable workflows
    triggerable_file = temp_workflows_dir / "triggerable.yml"
    triggerable_file.write_text(sample_workflow_content)

    reusable_file = temp_workflows_dir / "reusable.yml"
    reusable_file.write_text(sample_reusable_workflow)

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    triggerable = inventory.get_triggerable()
    assert len(triggerable) == 1, "Triggerable must not be empty"
    assert triggerable[0].filename == "triggerable.yml", "filename is not valid"


def test_get_reusable_workflows(
    temp_workflows_dir, sample_workflow_content, sample_reusable_workflow
):
    """Test filtering reusable workflows."""
    regular_file = temp_workflows_dir / "regular.yml"
    regular_file.write_text(sample_workflow_content)

    reusable_file = temp_workflows_dir / "reusable.yml"
    reusable_file.write_text(sample_reusable_workflow)

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    reusable = inventory.get_reusable()
    assert len(reusable) == 1, "Reusable must not be empty"
    assert reusable[0].filename == "reusable.yml", "filename is not valid"


def test_get_by_trigger_type(temp_workflows_dir):
    """Test filtering by trigger type."""
    push_workflow = temp_workflows_dir / "push.yml"
    push_workflow.write_text("""
name: Push Workflow
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    pr_workflow = temp_workflows_dir / "pr.yml"
    pr_workflow.write_text("""
name: PR Workflow
on: pull_request
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    push_workflows = inventory.get_by_trigger_type(TriggerType.PUSH)
    assert len(push_workflows) == 1, "Push_workflows must not be empty"
    assert push_workflows[0].filename == "push.yml", "filename is not valid"

    pr_workflows = inventory.get_by_trigger_type(TriggerType.PULL_REQUEST)
    assert len(pr_workflows) == 1, "Pr_workflows must not be empty"
    assert pr_workflows[0].filename == "pr.yml", "filename is not valid"


def test_get_stats(temp_workflows_dir, sample_workflow_content):
    """Test getting inventory statistics."""
    # Create multiple workflows
    for i in range(3):
        workflow_file = temp_workflows_dir / f"test{i}.yml"
        workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    stats = inventory.get_stats()
    assert stats.total_workflows == 3, "total_workflows is not valid"
    assert stats.triggerable_workflows == 3, "triggerable_workflows is not valid"
    assert stats.total_jobs == 3, "total_jobs is not valid"
    assert stats.total_triggers >= 3, "total_triggers must be greater than zero"


def test_list_workflows(temp_workflows_dir, sample_workflow_content):
    """Test listing all workflows."""
    # Create workflows in random order
    for name in ["zebra.yml", "apple.yml", "mango.yml"]:
        workflow_file = temp_workflows_dir / name
        workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    workflows = inventory.list_workflows()
    assert workflows == ["apple.yml", "mango.yml", "zebra.yml"]


def test_refresh_workflow(temp_workflows_dir, sample_workflow_content):
    """Test refreshing a single workflow."""
    workflow_file = temp_workflows_dir / "test.yml"
    workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    # Verify initial state
    workflow = inventory.get_workflow("test.yml")
    assert workflow.name == "Test Workflow", "name is not valid"

    # Update the workflow file
    updated_content = sample_workflow_content.replace("Test Workflow", "Updated Workflow")
    workflow_file.write_text(updated_content)

    # Refresh and verify
    success = inventory.refresh_workflow("test.yml")
    assert success is True, "success is not valid"

    workflow = inventory.get_workflow("test.yml")
    assert workflow.name == "Updated Workflow", "name is not valid"


def test_scan_nonexistent_directory():
    """Test scanning a directory that doesn't exist."""
    inventory = WorkflowInventory("/nonexistent/path")
    count = inventory.scan()
    assert count == 0, "Count must be greater than zero"


def test_workflow_dependencies(temp_workflows_dir):
    """Test building workflow dependency graph."""
    # Create caller workflow that uses a reusable workflow
    caller_content = """
name: Caller Workflow
on: push
jobs:
  call-reusable:
    uses: ./.github/workflows/reusable.yml
    with:
      config: "test"
"""

    reusable_content = """
name: Reusable Workflow
on:
  workflow_call:
    inputs:
      config:
        required: true
        type: string
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""

    caller_file = temp_workflows_dir / "caller.yml"
    caller_file.write_text(caller_content)

    reusable_file = temp_workflows_dir / "reusable.yml"
    reusable_file.write_text(reusable_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    # Check dependencies
    deps = inventory.get_workflow_dependencies("caller.yml")
    assert "reusable.yml" in deps, "Condition must be true"

    dependents = inventory.get_workflow_dependents("reusable.yml")
    assert "caller.yml" in dependents, "Condition must be true"


def test_force_refresh(temp_workflows_dir, sample_workflow_content):
    """Test force refresh clears cache."""
    workflow_file = temp_workflows_dir / "test.yml"
    workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    # Scan again without force_refresh (should use cache)
    count1 = inventory.scan()

    # Scan with force_refresh
    count2 = inventory.scan(force_refresh=True)

    assert count1 == count2 == 1, "Count must be greater than zero"


@pytest.mark.parametrize(
    "filename,expected_found",
    [
        ("test.yml", True),
        ("test.yaml", True),
        ("test.txt", False),
        ("test", False),
    ],
)
def test_scan_file_extensions(
    temp_workflows_dir, sample_workflow_content, filename, expected_found
):
    """Test that only .yml and .yaml files are scanned."""
    workflow_file = temp_workflows_dir / filename
    workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    if expected_found:
        assert filename in inventory.workflows, "Condition must be true"
    else:
        assert filename not in inventory.workflows, "Condition must be true"


def test_real_workflow_integration():
    """Integration test with actual repository workflows."""
    from pathlib import Path

    # Use actual workflows directory
    workflows_dir = Path(__file__).parent.parent.parent.parent / ".github" / "workflows"

    if not workflows_dir.exists():
        pytest.skip("Workflows directory not found")

    inventory = WorkflowInventory(workflows_dir)
    count = inventory.scan()

    # Verify we found workflows
    assert count > 0, "Should find at least one workflow"
    assert len(inventory.workflows) == count, "Collection must not be empty"

    # Verify stats make sense
    stats = inventory.get_stats()
    assert stats.total_workflows == count, "Count must be greater than zero"
    assert stats.total_jobs >= 0, "total_jobs must be greater than zero"
    assert stats.total_triggers >= 0, "total_triggers must be greater than zero"

    # Verify triggerable workflows are identified
    triggerable = inventory.get_triggerable()
    assert all(item.filename in inventory.workflows for item in triggerable), "Item must not be empty"

    # Verify at least one workflow has proper metadata
    first_workflow = list(inventory.workflows.values())[0]
    assert first_workflow.name is not None, "name must be initialized"
    assert first_workflow.file_path.exists(), "first_w is not valid"
    assert isinstance(first_workflow.jobs, dict)


def test_workflow_inventory_import_from_services():
    """Test that WorkflowInventory can be imported from services module."""
    from src.services import WorkflowInventory as WI
    from src.services.workflow import WorkflowInventory

    # Verify both import paths work
    assert WI is WorkflowInventory, "WI is not valid"


def test_parser_handles_invalid_yaml(temp_workflows_dir):
    """Test that parser handles invalid YAML gracefully."""
    from src.services.workflow.parser import WorkflowParser

    # Create file with invalid YAML
    invalid_file = temp_workflows_dir / "invalid.yml"
    invalid_file.write_text("name: test\non:\n  push: [\n  # Missing closing bracket")

    parser = WorkflowParser()
    result = parser.parse_file(invalid_file)

    # Should return None for invalid YAML
    assert result is None, "Result must not be empty"


def test_parser_handles_invalid_utf8(temp_workflows_dir):
    """Test that parser handles invalid UTF-8 gracefully."""
    from src.services.workflow.parser import WorkflowParser

    # Create file with invalid UTF-8
    invalid_file = temp_workflows_dir / "invalid_utf8.yml"
    invalid_file.write_bytes(b"name: test\xc3\x28")  # Invalid UTF-8

    parser = WorkflowParser()
    result = parser.parse_file(invalid_file)

    # Should return None for invalid encoding
    assert result is None, "Result must not be empty"


def test_inventory_skips_corrupted_files(temp_workflows_dir, sample_workflow_content):
    """Test that inventory continues scanning after encountering corrupted files."""
    # Create one valid and one invalid workflow
    valid_file = temp_workflows_dir / "valid.yml"
    valid_file.write_text(sample_workflow_content)

    invalid_file = temp_workflows_dir / "invalid.yml"
    invalid_file.write_text("invalid: yaml: content: [[[")

    inventory = WorkflowInventory(temp_workflows_dir)
    count = inventory.scan()

    # Should successfully parse the valid one
    assert count == 1, "Count must be greater than zero"
    assert "valid.yml" in inventory.workflows, "Condition must be true"
    assert "invalid.yml" not in inventory.workflows, "Condition must be true"


def test_parser_handles_missing_required_fields():
    """Test parser handles workflows missing required fields."""
    from pathlib import Path

    from src.services.workflow.parser import WorkflowParser

    # Workflow with no jobs
    content = """
name: Test
on: push
"""

    parser = WorkflowParser()
    result = parser.parse_content(content, Path("test.yml"))

    # Should still parse (jobs can be empty)
    assert result is not None, "result must be initialized"
    assert result.name == "Test", "Result must not be empty"
    assert len(result.jobs) == 0, "Collection must not be empty"


def test_workflow_dependencies_caller_uses_workflow(temp_workflows_dir):
    """Test workflow_call dependency detection with uses: syntax."""
    caller = temp_workflows_dir / "caller.yml"
    caller.write_text("""
name: Caller
on: push
jobs:
  use-reusable:
    uses: ./.github/workflows/reusable.yml@main
    with:
      param: value
""")

    reusable = temp_workflows_dir / "reusable.yml"
    reusable.write_text("""
name: Reusable
on:
  workflow_call:
    inputs:
      param:
        required: true
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    # Check dependencies are detected
    deps = inventory.get_workflow_dependencies("caller.yml")
    assert "reusable.yml" in deps, "Condition must be true"


def test_schedule_trigger_parsing(temp_workflows_dir):
    """Test parsing of schedule triggers with cron."""
    workflow = temp_workflows_dir / "scheduled.yml"
    workflow.write_text("""
name: Scheduled
on:
  schedule:
    - cron: '0 0 * * *'
    - cron: '0 12 * * *'
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("scheduled.yml")
    assert wf is not None, "wf must be initialized"
    assert len(wf.triggers) > 0, "Collection must not be empty"

    # Find schedule trigger
    schedule_triggers = [t for t in wf.triggers if t.type.value == "schedule"]
    assert len(schedule_triggers) > 0, "Schedule_triggers must not be empty"


def test_workflow_with_if_condition(temp_workflows_dir):
    """Test parsing workflow jobs with if conditions."""
    workflow = temp_workflows_dir / "conditional.yml"
    workflow.write_text("""
name: Conditional
on: push
jobs:
  conditional-job:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("conditional.yml")
    assert wf is not None, "wf must be initialized"
    assert "conditional-job" in wf.jobs, "Condition must be true"
    # if_condition should be captured (uses 'if' alias)


def test_inventory_nonexistent_directory():
    """Test inventory with nonexistent directory."""
    inventory = WorkflowInventory("/nonexistent/path/to/workflows")
    count = inventory.scan()
    assert count == 0, "Count must be greater than zero"


def test_refresh_nonexistent_workflow(temp_workflows_dir):
    """Test refreshing a workflow that doesn't exist."""
    inventory = WorkflowInventory(temp_workflows_dir)
    success = inventory.refresh_workflow("nonexistent.yml")
    assert success is False, "success is not valid"


def test_scan_continues_when_parser_raises(
    temp_workflows_dir, sample_workflow_content, monkeypatch
):
    """Test scan continues gracefully when parser.parse_file raises unexpectedly."""
    workflow_file = temp_workflows_dir / "test.yml"
    workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    monkeypatch.setattr(inventory.parser, "parse_file", raise_exception(RuntimeError("boom")))

    assert inventory.scan() == 0, "invent is not valid"
    assert inventory.workflows == {}, "workflows is not valid"


def test_refresh_workflow_handles_parser_exception(
    temp_workflows_dir, sample_workflow_content, monkeypatch
):
    """Test refresh_workflow returns False when parse_file raises unexpectedly."""
    workflow_file = temp_workflows_dir / "test.yml"
    workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    monkeypatch.setattr(inventory.parser, "parse_file", raise_exception(RuntimeError("boom")))

    assert inventory.refresh_workflow("test.yml") is False, "invent is not valid"


def test_parser_with_list_trigger_format(temp_workflows_dir):
    """Test parsing workflows with list format triggers."""
    from src.services.workflow.parser import WorkflowParser

    content = """
name: Multi Trigger
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""

    parser = WorkflowParser()
    workflow = parser.parse_content(content, temp_workflows_dir / "test.yml")

    assert workflow is not None, "workflow must be initialized"
    assert len(workflow.triggers) == 2, "Collection must not be empty"


def test_parser_with_string_trigger_format(temp_workflows_dir):
    """Test parsing workflows with string format triggers."""
    from src.services.workflow.parser import WorkflowParser

    content = """
name: Simple
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""

    parser = WorkflowParser()
    workflow = parser.parse_content(content, temp_workflows_dir / "test.yml")

    assert workflow is not None, "workflow must be initialized"
    assert len(workflow.triggers) == 1, "Collection must not be empty"
    assert workflow.triggers[0].type.value == "push", "Value must be initialized"


def test_job_with_needs_string(temp_workflows_dir):
    """Test parsing job with needs as string (single dependency)."""
    workflow = temp_workflows_dir / "needs.yml"
    workflow.write_text("""
name: Needs Test
on: push
jobs:
  first:
    runs-on: ubuntu-latest
    steps:
      - run: echo "first"
  second:
    runs-on: ubuntu-latest
    needs: first
    steps:
      - run: echo "second"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("needs.yml")
    assert wf is not None, "wf must be initialized"
    assert "second" in wf.jobs, "Condition must be true"
    assert wf.jobs["second"].needs == ["first"], "needs is not valid"


def test_job_with_timeout(temp_workflows_dir):
    """Test parsing job with timeout-minutes."""
    workflow = temp_workflows_dir / "timeout.yml"
    workflow.write_text("""
name: Timeout Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("timeout.yml")
    assert wf is not None, "wf must be initialized"
    assert wf.jobs["test"].timeout_minutes == 60, "timeout_minutes is not valid"


def test_clear_parser_cache():
    """Test clearing parser cache."""
    from pathlib import Path

    from src.services.workflow.parser import WorkflowParser

    parser = WorkflowParser()

    # Parse something to populate cache
    content = "name: Test\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo test"
    parser.parse_content(content, Path("test.yml"))

    # Clear cache
    parser.clear_cache()

    # Cache should be empty
    assert len(parser._cache) == 0, "Collection must not be empty"


def test_workflow_run_trigger_with_workflows(temp_workflows_dir):
    """Test workflow_run trigger type with workflow dependencies."""
    workflow = temp_workflows_dir / "depends.yml"
    workflow.write_text("""
name: Dependent
on:
  workflow_run:
    workflows: ["CI Tests"]
    types: [completed]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploy"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("depends.yml")
    assert wf is not None, "wf must be initialized"


def test_job_with_invalid_needs_type(temp_workflows_dir):
    """Test job with needs that's not a string or list."""
    workflow = temp_workflows_dir / "bad_needs.yml"
    workflow.write_text("""
name: Bad Needs
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    needs: 123
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("bad_needs.yml")
    assert wf is not None, "wf must be initialized"
    # needs should be None for invalid type
    assert wf.jobs["test"].needs is None, "needs is not valid"


def test_workflow_with_string_permissions(temp_workflows_dir):
    """Test workflow with permissions as string."""
    workflow = temp_workflows_dir / "perms.yml"
    workflow.write_text("""
name: Permissions Test
on: push
permissions: read-all
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("perms.yml")
    assert wf is not None, "wf must be initialized"
    assert "default" in wf.permissions, "Condition must be true"


def test_workflow_with_non_dict_env(temp_workflows_dir):
    """Test workflow with invalid env type."""
    workflow = temp_workflows_dir / "bad_env.yml"
    workflow.write_text("""
name: Bad Env
on: push
env: "not a dict"
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("bad_env.yml")
    assert wf is not None, "wf must be initialized"
    # env should be empty dict for invalid type
    assert wf.env == {}, "env is not valid"


def test_input_with_default_value(temp_workflows_dir):
    """Test workflow_dispatch input with default value."""
    workflow = temp_workflows_dir / "inputs.yml"
    workflow.write_text("""
name: Inputs
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment'
        required: false
        default: 'staging'
        type: string
      debug:
        description: 'Debug mode'
        type: boolean
        default: false
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("inputs.yml")
    assert wf is not None, "wf must be initialized"
    assert "environment" in wf.inputs, "Condition must be true"
    assert wf.inputs["environment"].default == "staging", "default is not valid"
    assert "debug" in wf.inputs, "Condition must be true"
    assert wf.inputs["debug"].default is False, "default is not valid"


def test_input_with_invalid_type(temp_workflows_dir):
    """Test input with invalid type falls back to string."""
    from src.services.workflow.parser import WorkflowParser

    content = """
name: Invalid Input
on:
  workflow_dispatch:
    inputs:
      test:
        type: invalid_type
        description: 'Test'
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
"""

    parser = WorkflowParser()
    wf = parser.parse_content(content, temp_workflows_dir / "test.yml")

    assert wf is not None, "wf must be initialized"
    assert "test" in wf.inputs, "Condition must be true"
    # Should fall back to STRING for invalid type
    from src.services.workflow.types import InputType

    assert wf.inputs["test"].type == InputType.STRING, "type is not valid"


def test_job_steps_count(temp_workflows_dir):
    """Test that job step count is correct."""
    workflow = temp_workflows_dir / "steps.yml"
    workflow.write_text("""
name: Steps
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "step 1"
      - run: echo "step 2"
      - name: Step 3
        run: echo "step 3"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("steps.yml")
    assert wf is not None, "wf must be initialized"
    assert wf.jobs["test"].steps == 4, "steps is not valid"


def test_job_with_non_list_steps(temp_workflows_dir):
    """Test job with steps that's not a list."""
    workflow = temp_workflows_dir / "bad_steps.yml"
    workflow.write_text("""
name: Bad Steps
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps: "not a list"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("bad_steps.yml")
    assert wf is not None, "wf must be initialized"
    # steps should be 0 for invalid type
    assert wf.jobs["test"].steps == 0, "steps is not valid"


def test_trigger_with_branches_filter(temp_workflows_dir):
    """Test trigger with branches filter."""
    workflow = temp_workflows_dir / "branches.yml"
    workflow.write_text("""
name: Branches
on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("branches.yml")
    assert wf is not None, "wf must be initialized"

    # Check branches are parsed
    push_trigger = [t for t in wf.triggers if t.type.value == "push"][0]
    assert push_trigger.branches is not None, "branches must be initialized"
    assert "main" in push_trigger.branches, "Condition must be true"


def test_trigger_with_paths_filter(temp_workflows_dir):
    """Test trigger with paths filter."""
    workflow = temp_workflows_dir / "paths.yml"
    workflow.write_text("""
name: Paths
on:
  push:
    paths:
      - 'src/**'
      - '**.py'
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("paths.yml")
    assert wf is not None, "wf must be initialized"

    push_trigger = [t for t in wf.triggers if t.type.value == "push"][0]
    assert push_trigger.paths is not None, "paths must be initialized"
    assert "src/**" in push_trigger.paths, "Condition must be true"


def test_trigger_with_types_filter(temp_workflows_dir):
    """Test trigger with types filter."""
    workflow = temp_workflows_dir / "types.yml"
    workflow.write_text("""
name: Types
on:
  pull_request:
    types: [opened, synchronize, reopened]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("types.yml")
    assert wf is not None, "wf must be initialized"

    pr_trigger = [t for t in wf.triggers if t.type.value == "pull_request"][0]
    assert pr_trigger.types is not None, "types must be initialized"
    assert "opened" in pr_trigger.types, "Condition must be true"


def test_trigger_with_string_branches(temp_workflows_dir):
    """Test trigger with branches as string (single branch)."""
    from src.services.workflow.parser import WorkflowParser

    content = """
name: Single Branch
on:
  push:
    branches: main
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo test
"""

    parser = WorkflowParser()
    wf = parser.parse_content(content, temp_workflows_dir / "test.yml")

    assert wf is not None, "wf must be initialized"
    push_trigger = [t for t in wf.triggers if t.type.value == "push"][0]
    assert push_trigger.branches == ["main"], "branches is not valid"


def test_input_with_options(temp_workflows_dir):
    """Test input with options (choice type)."""
    workflow = temp_workflows_dir / "choice.yml"
    workflow.write_text("""
name: Choice
on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options:
          - dev
          - staging
          - production
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("choice.yml")
    assert wf is not None, "wf must be initialized"
    assert "environment" in wf.inputs, "Condition must be true"
    assert wf.inputs["environment"].options is not None, "options must be initialized"
    assert "dev" in wf.inputs["environment"].options, "Condition must be true"


def test_workflow_metadata_properties(temp_workflows_dir):
    """Test WorkflowMetadata computed properties."""
    workflow = temp_workflows_dir / "props.yml"
    workflow.write_text("""
name: Properties Test
on:
  push:
  workflow_dispatch:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "build"
""")

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    wf = inventory.get_workflow("props.yml")
    assert wf is not None, "wf must be initialized"

    # Test properties
    assert wf.filename == "props.yml", "filename is not valid"
    assert wf.has_workflow_dispatch is True, "has_workflow_dispatch is not valid"
    assert len(wf.trigger_types) == 2, "Collection must not be empty"
    assert len(wf.job_ids) == 2, "Collection must not be empty"
    assert "test" in wf.job_ids, "Condition must be true"
    assert "build" in wf.job_ids, "Condition must be true"
