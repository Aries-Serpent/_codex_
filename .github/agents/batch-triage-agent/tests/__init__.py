"""Tests for __init__.py - package initialization."""

import sys
from pathlib import Path

# Add parent directories to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent / "src"))


def test_package_imports():
    """Test that all modules can be imported."""
    import analyzer
    import pattern_learner
    import remediation_engine
    import notifier
    
    assert analyzer.BatchTriageAnalyzer is not None
    assert pattern_learner.PatternLearner is not None
    assert remediation_engine.RemediationEngine is not None
    assert notifier.Notifier is not None


def test_package_version():
    """Test package version is set."""
    # Import __init__ directly
    src_init = SCRIPT_DIR.parent / "src" / "__init__.py"
    
    # Read version from file
    with open(src_init, 'r') as f:
        content = f.read()
        assert '__version__ = "1.0.0"' in content
