"""Tests for workflow inventory system."""

import pytest

from src.services.workflow.inventory import WorkflowInventory
from src.services.workflow.parser import WorkflowParser
from src.services.workflow.types import (
    TriggerType,
)


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
    assert inventory.workflows_dir == temp_workflows_dir
    assert isinstance(inventory.parser, WorkflowParser)
    assert len(inventory.workflows) == 0


def test_scan_empty_directory(temp_workflows_dir):
    """Test scanning an empty directory."""
    inventory = WorkflowInventory(temp_workflows_dir)
    count = inventory.scan()
    assert count == 0
    assert len(inventory.workflows) == 0


def test_scan_with_workflows(temp_workflows_dir, sample_workflow_content):
    """Test scanning directory with workflows."""
    # Create a workflow file
    workflow_file = temp_workflows_dir / "test.yml"
    workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    count = inventory.scan()

    assert count == 1
    assert "test.yml" in inventory.workflows

    workflow = inventory.get_workflow("test.yml")
    assert workflow is not None
    assert workflow.name == "Test Workflow"
    assert workflow.is_triggerable is True


def test_scan_skips_disabled_workflows(temp_workflows_dir, sample_workflow_content):
    """Test that disabled workflows are skipped."""
    # Create enabled and disabled workflows
    enabled_file = temp_workflows_dir / "enabled.yml"
    enabled_file.write_text(sample_workflow_content)

    disabled_file = temp_workflows_dir / "disabled.yml.disabled"
    disabled_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    count = inventory.scan()

    assert count == 1
    assert "enabled.yml" in inventory.workflows
    assert "disabled.yml.disabled" not in inventory.workflows


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
    assert len(triggerable) == 1
    assert triggerable[0].filename == "triggerable.yml"


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
    assert len(reusable) == 1
    assert reusable[0].filename == "reusable.yml"


def test_get_by_trigger_type(temp_workflows_dir):
    """Test filtering by trigger type."""
    push_workflow = temp_workflows_dir / "push.yml"
    push_workflow.write_text(
        """
name: Push Workflow
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""
    )

    pr_workflow = temp_workflows_dir / "pr.yml"
    pr_workflow.write_text(
        """
name: PR Workflow
on: pull_request
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
"""
    )

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    push_workflows = inventory.get_by_trigger_type(TriggerType.PUSH)
    assert len(push_workflows) == 1
    assert push_workflows[0].filename == "push.yml"

    pr_workflows = inventory.get_by_trigger_type(TriggerType.PULL_REQUEST)
    assert len(pr_workflows) == 1
    assert pr_workflows[0].filename == "pr.yml"


def test_get_stats(temp_workflows_dir, sample_workflow_content):
    """Test getting inventory statistics."""
    # Create multiple workflows
    for i in range(3):
        workflow_file = temp_workflows_dir / f"test{i}.yml"
        workflow_file.write_text(sample_workflow_content)

    inventory = WorkflowInventory(temp_workflows_dir)
    inventory.scan()

    stats = inventory.get_stats()
    assert stats.total_workflows == 3
    assert stats.triggerable_workflows == 3
    assert stats.total_jobs == 3
    assert stats.total_triggers >= 3


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
    assert workflow.name == "Test Workflow"

    # Update the workflow file
    updated_content = sample_workflow_content.replace("Test Workflow", "Updated Workflow")
    workflow_file.write_text(updated_content)

    # Refresh and verify
    success = inventory.refresh_workflow("test.yml")
    assert success is True

    workflow = inventory.get_workflow("test.yml")
    assert workflow.name == "Updated Workflow"


def test_scan_nonexistent_directory():
    """Test scanning a directory that doesn't exist."""
    inventory = WorkflowInventory("/nonexistent/path")
    count = inventory.scan()
    assert count == 0


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
    assert "reusable.yml" in deps

    dependents = inventory.get_workflow_dependents("reusable.yml")
    assert "caller.yml" in dependents


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

    assert count1 == count2 == 1


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
        assert filename in inventory.workflows
    else:
        assert filename not in inventory.workflows


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
    assert len(inventory.workflows) == count
    
    # Verify stats make sense
    stats = inventory.get_stats()
    assert stats.total_workflows == count
    assert stats.total_jobs >= 0
    assert stats.total_triggers >= 0
    
    # Verify triggerable workflows are identified
    triggerable = inventory.get_triggerable()
    assert len(triggerable) >= 0
    
    # Verify at least one workflow has proper metadata
    if count > 0:
        first_workflow = list(inventory.workflows.values())[0]
        assert first_workflow.name is not None
        assert first_workflow.file_path.exists()
        assert isinstance(first_workflow.jobs, dict)


def test_workflow_inventory_import_from_services():
    """Test that WorkflowInventory can be imported from services module."""
    from src.services import WorkflowInventory as WI
    from src.services.workflow import WorkflowInventory
    
    # Verify both import paths work
    assert WI is WorkflowInventory
