"""
Tests for WorkflowNavigator module.

Tests tokenized workflow navigation and execution.
"""

import pytest
from pathlib import Path
from agents.workflow_navigator import (
    WorkflowNavigator,
    Workflow,
    WorkflowStep,
    WorkflowFrequency,
    StepStatus
)


class TestWorkflowNavigator:
    """Test workflow navigator functionality."""
    
    def test_initialization(self):
        """Test WorkflowNavigator initializes correctly."""
        navigator = WorkflowNavigator()
        
        assert navigator.workspace_dir is not None
        assert isinstance(navigator.workflows, dict)
        assert len(navigator.workflows) > 0  # Should have default workflows
    
    def test_initialization_with_workspace(self, tmp_path):
        """Test initialization with custom workspace."""
        navigator = WorkflowNavigator(workspace_dir=tmp_path)
        
        assert navigator.workspace_dir == tmp_path
        assert navigator.workflow_state_dir.exists()
    
    def test_register_workflow(self):
        """Test workflow registration."""
        navigator = WorkflowNavigator()
        
        workflow = Workflow(
            workflow_id='TEST_WF',
            name='Test Workflow',
            description='A test workflow',
            frequency=WorkflowFrequency.LOW,
            steps=[]
        )
        
        navigator.register_workflow(workflow)
        
        assert 'TEST_WF' in navigator.workflows
        assert navigator.workflows['TEST_WF'] == workflow
    
    def test_get_workflow(self):
        """Test retrieving a workflow."""
        navigator = WorkflowNavigator()
        
        # Should have AUDIT_EXEC from defaults
        workflow = navigator.get_workflow('AUDIT_EXEC')
        
        assert workflow is not None
        assert workflow.workflow_id == 'AUDIT_EXEC'
    
    def test_get_nonexistent_workflow(self):
        """Test retrieving a non-existent workflow."""
        navigator = WorkflowNavigator()
        
        workflow = navigator.get_workflow('DOES_NOT_EXIST')
        
        assert workflow is None
    
    def test_list_workflows(self):
        """Test listing all workflows."""
        navigator = WorkflowNavigator()
        
        workflows = navigator.list_workflows()
        
        assert isinstance(workflows, list)
        assert len(workflows) > 0
        assert all(isinstance(w, Workflow) for w in workflows)
    
    def test_list_workflows_by_category(self):
        """Test listing workflows filtered by category."""
        navigator = WorkflowNavigator()
        
        # Register a test workflow with specific category
        workflow = Workflow(
            workflow_id='TEST_CAT',
            name='Test Category',
            description='Test',
            frequency=WorkflowFrequency.LOW,
            category='testing',
            steps=[]
        )
        navigator.register_workflow(workflow)
        
        workflows = navigator.list_workflows(category='testing')
        
        assert isinstance(workflows, list)
        assert any(w.workflow_id == 'TEST_CAT' for w in workflows)
    
    def test_search_workflows(self):
        """Test workflow search functionality."""
        navigator = WorkflowNavigator()
        
        results = navigator.search_workflows('audit')
        
        assert isinstance(results, list)
        # Should find audit-related workflows
        assert any('audit' in w.name.lower() or 'audit' in w.description.lower() 
                  for w in results)
    
    def test_suggest_workflow_recent_commits(self):
        """Test workflow suggestion for recent commits."""
        navigator = WorkflowNavigator()
        
        state = {'recent_commits': True}
        suggestions = navigator.suggest_workflow(state)
        
        assert isinstance(suggestions, list)
        # Should suggest audit workflow for recent commits
        assert any(w.workflow_id == 'AUDIT_EXEC' for w in suggestions)
    
    def test_suggest_workflow_low_coverage(self):
        """Test workflow suggestion for low test coverage."""
        navigator = WorkflowNavigator()
        
        state = {'test_coverage': 50}
        suggestions = navigator.suggest_workflow(state)
        
        assert isinstance(suggestions, list)
        # Should suggest test coverage workflow
        assert any('test' in w.name.lower() or 'coverage' in w.name.lower() 
                  for w in suggestions)
    
    def test_suggest_workflow_many_issues(self):
        """Test workflow suggestion for many open issues."""
        navigator = WorkflowNavigator()
        
        state = {'open_issues': 15}
        suggestions = navigator.suggest_workflow(state)
        
        assert isinstance(suggestions, list)
        # Should suggest self-healing workflow
        assert any('heal' in w.name.lower() or 'issue' in w.name.lower() 
                  for w in suggestions)
    
    def test_create_dynamic_workflow_test_coverage(self):
        """Test dynamic workflow creation for test coverage."""
        navigator = WorkflowNavigator()
        
        workflow = navigator._create_dynamic_workflow('test_coverage')
        
        assert workflow is not None
        assert workflow.workflow_id == 'TEST_COVERAGE_DYNAMIC'
        assert len(workflow.steps) > 0
    
    def test_create_dynamic_workflow_self_heal(self):
        """Test dynamic workflow creation for self-healing."""
        navigator = WorkflowNavigator()
        
        workflow = navigator._create_dynamic_workflow('self_heal')
        
        assert workflow is not None
        assert workflow.workflow_id == 'SELF_HEAL_DYNAMIC'
        assert len(workflow.steps) > 0
    
    def test_create_dynamic_workflow_invalid_type(self):
        """Test dynamic workflow creation with invalid type."""
        navigator = WorkflowNavigator()
        
        with pytest.raises(ValueError, match="Unknown workflow type"):
            navigator._create_dynamic_workflow('invalid_type')


class TestWorkflow:
    """Test Workflow dataclass."""
    
    def test_to_dict(self):
        """Test workflow serialization to dict."""
        workflow = Workflow(
            workflow_id='TEST',
            name='Test',
            description='Test workflow',
            frequency=WorkflowFrequency.HIGH,
            steps=[
                WorkflowStep(
                    id='step1',
                    action='Do something',
                    command='echo test'
                )
            ]
        )
        
        data = workflow.to_dict()
        
        assert data['workflow_id'] == 'TEST'
        assert data['name'] == 'Test'
        assert data['frequency'] == 'high'
        assert len(data['steps']) == 1
        assert data['steps'][0]['id'] == 'step1'


class TestWorkflowStep:
    """Test WorkflowStep functionality."""
    
    def test_step_initialization(self):
        """Test WorkflowStep initializes correctly."""
        step = WorkflowStep(
            id='test_step',
            action='Test action',
            command='echo test'
        )
        
        assert step.id == 'test_step'
        assert step.action == 'Test action'
        assert step.command == 'echo test'
        assert step.status == StepStatus.PENDING
    
    def test_step_optional_flag(self):
        """Test optional step flag."""
        step = WorkflowStep(
            id='optional_step',
            action='Optional action',
            optional=True
        )
        
        assert step.optional is True
