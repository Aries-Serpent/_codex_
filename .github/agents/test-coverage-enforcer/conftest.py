"""Pytest configuration for test-coverage-enforcer agent tests"""

import sys
from pathlib import Path

# Add src directory to Python path for test imports
sys.path.insert(0, str(Path(__file__).parent / "src"))
