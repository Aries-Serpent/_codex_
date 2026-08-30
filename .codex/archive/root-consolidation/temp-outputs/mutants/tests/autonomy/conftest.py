"""Pytest configuration for autonomy tests.

Ensures scripts/ directory is on sys.path for importing autonomy modules.
"""

import sys
from pathlib import Path

# Add scripts directory to sys.path so imports like `from autonomy_scheduler import X` work
scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
