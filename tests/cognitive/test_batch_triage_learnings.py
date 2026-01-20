"""Tests for batch triage learning engine"""
import json
import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.cognitive.batch_triage_learnings import (
    BatchTriageLearningEngine,
    FailurePattern,
    TriageOutcome
)


@pytest.fixture
def temp_kb_dir():
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def learning_engine(temp_kb_dir):
    return BatchTriageLearningEngine(
        kb_path=temp_kb_dir / "cognitive_brain",
        metrics_path=temp_kb_dir / "metrics"
    )


def test_initialization(learning_engine):
    """Test engine initializes correctly"""
    assert learning_engine.kb_path.exists()
    assert learning_engine.patterns_dir.exists()


def test_generate_signature_normalization(learning_engine):
    """Test signature generation normalizes variable parts"""
    desc1 = "Error on 2026-01-19: Failed with ID 12345"
    desc2 = "Error on 2026-01-20: Failed with ID 67890"
    
    sig1 = learning_engine._generate_signature(desc1)
    sig2 = learning_engine._generate_signature(desc2)
    
    # Should generate same signature after normalization
    assert sig1 == sig2


def test_classify_pattern_type(learning_engine):
    """Test pattern type classification"""
    assert learning_engine._classify_pattern_type("Test failed") == "test_failure"
    assert learning_engine._classify_pattern_type("timeout") == "timeout"
    assert learning_engine._classify_pattern_type("ImportError") == "import_error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
