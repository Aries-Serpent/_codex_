"""Unit tests for [Agent Name]"""

import pytest
from pathlib import Path
from ..src.agent import AgentClass


@pytest.fixture
def agent():
    """Create agent instance for testing"""
    return AgentClass()


def test_agent_initialization(agent):
    """Test agent initializes correctly"""
    assert agent is not None
    assert agent.config is not None
    assert agent.config['version'] == '1.0.0'


def test_agent_execute_success(agent):
    """Test agent execution with valid task"""
    task = {'description': 'test task'}
    result = agent.execute(task)
    
    assert result is not None
    assert result['status'] == 'success'
    assert 'output' in result
    assert 'test task' in result['output']


def test_agent_execute_missing_description(agent):
    """Test agent handles missing description"""
    invalid_task = {}
    
    with pytest.raises(ValueError, match="Task must include 'description'"):
        agent.execute(invalid_task)


def test_agent_execute_none_task(agent):
    """Test agent handles None task"""
    with pytest.raises(ValueError):
        agent.execute(None)


def test_agent_config_loading(tmp_path):
    """Test agent loads custom config"""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("""
version: 2.0.0
enabled: false
custom_setting: test_value
""")
    
    agent = AgentClass(config_file)
    assert agent.config['version'] == '2.0.0'
    assert agent.config['enabled'] is False
    assert agent.config['custom_setting'] == 'test_value'


def test_agent_default_config(agent):
    """Test agent uses default config"""
    assert agent.config['timeout_seconds'] == 300
    assert agent.config['max_retries'] == 3
    assert agent.config['log_level'] == 'INFO'
