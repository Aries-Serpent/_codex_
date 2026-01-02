"""
Quick import validation test for Phase 1 framework.
"""
import sys
from pathlib import Path

# Add core to path
core_path = Path(__file__).parent.parent
sys.path.insert(0, str(core_path))

def test_imports():
    """Test that all core modules can be imported"""
    try:
        from base_agent import CognitiveAgent
        from cognitive_brain import CognitiveBrain
        from pattern_recognizer import PatternRecognizer
        from orchestrator import AgentOrchestrator
        from config import FrameworkConfig
        print("✅ All core imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
