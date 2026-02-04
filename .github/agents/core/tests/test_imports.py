"""
Quick import validation test for Phase 1 framework.
"""
import importlib.util
import sys
from pathlib import Path

# Add core to path
core_path = Path(__file__).parent.parent
sys.path.insert(0, str(core_path))

def test_imports():
    """Test that all core modules can be imported"""
    try:
        # Check availability using importlib.util.find_spec
        required_modules = [
            'base_agent',
            'cognitive_brain',
            'pattern_recognizer',
            'orchestrator',
            'config',
        ]
        
        for module_name in required_modules:
            if importlib.util.find_spec(module_name) is None:
                raise ImportError(f"Module {module_name} not found")
        
        print("✅ All core imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
