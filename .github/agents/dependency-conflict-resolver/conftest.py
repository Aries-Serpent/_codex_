#!/usr/bin/env python3
"""pytest configuration"""
import sys
from pathlib import Path

# Add agent root and src directories to path
agent_root = Path(__file__).parent
src_root = agent_root / "src"
sys.path.insert(0, str(src_root))
sys.path.insert(0, str(agent_root))
