"""
Conftest for GitHub Guru Agent tests.

Adds the agent directory to sys.path FIRST so agent modules (e.g.
cognitive_adapter.py) shadow any same-named modules elsewhere in the repo.
"""
import sys
from pathlib import Path

# Agent package root (.github/agents/github-guru-agent/)
_AGENT_ROOT = Path(__file__).resolve().parent.parent

# Insert at position 0 unconditionally so agent modules take precedence
# over same-named modules in agents/ at repo root.
if str(_AGENT_ROOT) in sys.path:
    sys.path.remove(str(_AGENT_ROOT))
sys.path.insert(0, str(_AGENT_ROOT))
