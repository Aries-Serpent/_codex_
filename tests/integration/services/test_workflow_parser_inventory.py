"""Workflow parser and inventory integration tests (Phase 24)."""

import pytest

from src.services.workflow.inventory import WorkflowInventory
from src.services.workflow.parser import WorkflowParser


@pytest.mark.integration
def test_workflow_parser_yaml_parsing():
    """Test WorkflowParser parses YAML correctly."""
    yaml_content = """
name: Test Workflow
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: echo "test"
"""
    parser = WorkflowParser()
    workflow = parser.parse(yaml_content)
    assert workflow.name == "Test Workflow", "name is not valid"
    assert "test" in workflow.jobs, "Condition must be true"


@pytest.mark.integration
def test_workflow_parser_invalid_yaml():
    """Test WorkflowParser handles invalid YAML."""
    invalid_yaml = "{ invalid yaml: [ unclosed"
    parser = WorkflowParser()
    with pytest.raises(ValueError, match="Invalid YAML"):
        parser.parse(invalid_yaml)


@pytest.mark.integration
def test_workflow_inventory_registration(tmp_path):
    """Test WorkflowInventory scans and registers workflows."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    # Create a test workflow file
    test_workflow = workflows_dir / "test.yml"
    test_workflow.write_text("""
name: Test Workflow
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
""")

    inventory = WorkflowInventory(workflows_dir)
    count = inventory.scan()

    assert count == 1, "Count must be greater than zero"
    assert "test.yml" in inventory.workflows, "Condition must be true"
    assert inventory.workflows["test.yml"].name == "Test Workflow", "name is not valid"


@pytest.mark.integration
def test_workflow_inventory_query(tmp_path):
    """Test WorkflowInventory query capabilities."""
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)

    # Create test workflow files
    (workflows_dir / "workflow1.yml").write_text("""
name: Workflow 1
on: [push]
jobs:
  job1:
    runs-on: ubuntu-latest
    steps: []
""")
    (workflows_dir / "workflow2.yml").write_text("""
name: Workflow 2
on: [push]
jobs:
  job2:
    runs-on: ubuntu-latest
    steps: []
""")

    inventory = WorkflowInventory(workflows_dir)
    inventory.scan()

    # Test get_workflow method
    workflow1 = inventory.get_workflow("workflow1.yml")
    assert workflow1 is not None, "workflow1 must be initialized"
    assert workflow1.name == "Workflow 1", "name is not valid"

    # Test list_workflows method
    all_workflows = inventory.list_workflows()
    assert len(all_workflows) == 2, "All_workflows must not be empty"
    assert "workflow1.yml" in all_workflows, "Condition must be true"
    assert "workflow2.yml" in all_workflows, "Condition must be true"


@pytest.mark.integration
def test_workflow_parser_job_dependencies():
    """Test WorkflowParser extracts job dependencies."""
    yaml_content = """
name: Test
jobs:
  build:
    runs-on: ubuntu-latest
    steps: []
  test:
    needs: build
    runs-on: ubuntu-latest
    steps: []
"""
    parser = WorkflowParser()
    workflow = parser.parse(yaml_content)
    # WorkflowJob uses Pydantic model with `needs` field
    assert workflow.jobs["test"].needs == ["build"], "needs is not valid"
