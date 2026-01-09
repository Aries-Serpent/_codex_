"""Conftest for services/crawler tests to handle import path issues."""

# This conftest ensures the src directory is in the path before test collection
import sys
from pathlib import Path

# Add src to path if not already there
src_dir = Path(__file__).resolve().parent.parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
