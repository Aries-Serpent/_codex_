"""Integration tests for Test Assertion Updater Agent"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import TestAssertionUpdater, AssertionMismatch


@pytest.fixture
def agent():
    """Create agent instance for integration testing"""
    return TestAssertionUpdater()


@pytest.fixture
def temp_test_file():
    """Create a temporary test file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def test_example():
    result = "new_value"
    assert result == "old_value"
""")
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


def test_end_to_end_string_format_fix(agent, temp_test_file):
    """Test complete workflow from detection to fix for string format"""
    mismatch = AssertionMismatch(
        test_name="test_example",
        file_path=temp_test_file,
        line_number=3,
        mismatch_type='string_format',
        expected_value='"old_value"',
        actual_value='"new_value"',
        confidence=0.9
    )
    
    # Generate fix
    fix = agent.generate_fix(mismatch)
    assert fix is not None
    
    # Validate fix
    is_valid = agent.validate_fix(fix, temp_test_file)
    assert is_valid is True
    
    # Generate commit message
    message = agent.generate_commit_message(fix, mismatch)
    assert 'fix(tests)' in message
    assert 'test_example' in message


def test_end_to_end_data_structure_fix(agent):
    """Test complete workflow for data structure change"""
    mismatch = AssertionMismatch(
        test_name="test_data_structure",
        file_path=Path("test.py"),
        line_number=10,
        mismatch_type='data_structure',
        expected_value='["item1", "item2"]',
        actual_value='[{"name": "item1"}, {"name": "item2"}]',
        confidence=0.95
    )
    
    # Generate fix
    fix = agent.generate_fix(mismatch)
    assert fix is not None
    assert 'isinstance(item, dict)' in fix.fixed_code
    
    # Validate fix
    is_valid = agent.validate_fix(fix, Path("test.py"))
    assert is_valid is True


def test_end_to_end_type_change_fix(agent):
    """Test complete workflow for type change"""
    mismatch = AssertionMismatch(
        test_name="test_type_change",
        file_path=Path("test.py"),
        line_number=15,
        mismatch_type='type_change',
        expected_value='123',
        actual_value='{"count": 123}',
        confidence=0.90
    )
    
    # Generate fix
    fix = agent.generate_fix(mismatch)
    assert fix is not None
    assert '["value"]' in fix.fixed_code
    
    # Validate fix
    is_valid = agent.validate_fix(fix, Path("test.py"))
    assert is_valid is True


def test_multiple_mismatches_workflow(agent):
    """Test handling multiple mismatches in sequence"""
    mismatches = [
        AssertionMismatch(
            test_name="test1",
            file_path=Path("test1.py"),
            line_number=10,
            mismatch_type='string_format',
            expected_value='"old1"',
            actual_value='"new1"',
            confidence=0.9
        ),
        AssertionMismatch(
            test_name="test2",
            file_path=Path("test2.py"),
            line_number=20,
            mismatch_type='data_structure',
            expected_value='["a"]',
            actual_value='[{"name": "a"}]',
            confidence=0.95
        )
    ]
    
    for mismatch in mismatches:
        fix = agent.generate_fix(mismatch)
        assert fix is not None
        is_valid = agent.validate_fix(fix, mismatch.file_path)
        assert is_valid is True


def test_agent_resilience_to_invalid_mismatch(agent):
    """Test agent handles invalid mismatch types gracefully"""
    mismatch = AssertionMismatch(
        test_name="test_invalid",
        file_path=Path("test.py"),
        line_number=5,
        mismatch_type='unknown_type',
        expected_value='something',
        actual_value='something_else',
        confidence=0.5
    )
    
    with pytest.raises(ValueError, match="Unknown mismatch type"):
        agent.generate_fix(mismatch)


def test_config_loading_from_file(temp_test_file):
    """Test agent loads configuration from file if provided"""
    # Create a temporary config file
    config_content = """
version: 1.0.0
agent_name: test-assertion-updater
capabilities:
  - parse_failures
  - analyze_code
settings:
  timeout_seconds: 600
  max_retries: 5
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)
    
    try:
        agent = TestAssertionUpdater(config_path=config_path)
        assert agent.config['settings']['timeout_seconds'] == 600
        assert agent.config['settings']['max_retries'] == 5
    finally:
        if config_path.exists():
            config_path.unlink()
