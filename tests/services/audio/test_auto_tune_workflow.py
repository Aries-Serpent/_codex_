"""
Test Auto Tune Workflow

Test module for auto tune workflow.
"""

#!/usr/bin/env python3
"""Test suite for auto-tune workflow."""

import pytest
from services.audio.workflow.auto_tune_workflow import (
    AutoTuneWorkflow,
    WorkflowResult,
)


class TestAutoTuneWorkflow:
    """Test cases for AutoTuneWorkflow."""
    
    def test_workflow_initialization(self):
        """Test workflow initializes correctly."""
        workflow = AutoTuneWorkflow(cognitive_mode=True)
        assert workflow.cognitive_mode is True
    
    def test_process_path_no_files(self, tmp_path):
        """Test processing empty directory."""
        workflow = AutoTuneWorkflow()
        result = workflow.process_path(str(tmp_path))
        
        assert isinstance(result, WorkflowResult)
        assert result.success is False
        assert "No audio files found" in result.error
    
    def test_process_path_with_files(self, tmp_path):
        """Test processing directory with audio files.
        
        Note: Uses text data for simplicity in unit tests. The workflow logic
        being tested (file discovery, result aggregation) doesn't require actual
        audio decoding. For integration tests that validate audio processing
        behavior, use binary fixtures or mock the audio library's load function.
        """
        # Create dummy audio files (text data for unit test simplicity)
        (tmp_path / "test1.mp3").write_text("audio data 1")
        (tmp_path / "test2.wav").write_text("audio data 2")
        
        workflow = AutoTuneWorkflow()
        result = workflow.process_path(str(tmp_path))
        
        assert isinstance(result, WorkflowResult)
        assert result.success is True
        assert result.total_files == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
