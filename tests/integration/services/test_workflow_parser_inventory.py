"""Workflow parser and inventory integration tests (Phase 24)."""

import pytest

from src.services.workflow.parser import WorkflowParser
from src.services.workflow.inventory import WorkflowInventory


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
    assert workflow.name == "Test Workflow"
    assert "test" in workflow.jobs


@pytest.mark.integration
def test_workflow_parser_invalid_yaml():
    """Test WorkflowParser handles invalid YAML."""
    invalid_yaml = "{ invalid yaml: [ unclosed"
    parser = WorkflowParser()
    with pytest.raises(ValueError, match="Invalid YAML"):
        parser.parse(invalid_yaml)


@pytest.mark.integration
def test_workflow_inventory_registration():
    """Test WorkflowInventory registers workflows."""
    inventory = WorkflowInventory()
    inventory.register("test.yml", {"name": "Test", "jobs": {}})
    
    assert "test.yml" in inventory.workflows
    assert inventory.workflows["test.yml"]["name"] == "Test"


@pytest.mark.integration
def test_workflow_inventory_query():
    """Test WorkflowInventory query capabilities."""
    inventory = WorkflowInventory()
    inventory.register("workflow1.yml", {"name": "Workflow 1", "jobs": {"job1": {}}})
    inventory.register("workflow2.yml", {"name": "Workflow 2", "jobs": {"job2": {}}})
    
    results = inventory.query(name="Workflow 1")
    assert len(results) == 1
    assert results[0]["name"] == "Workflow 1"


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
    assert "needs" in workflow.jobs["test"]
    assert workflow.jobs["test"]["needs"] == "build"
