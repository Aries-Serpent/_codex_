#!/usr/bin/env python3
"""
Activate _Codex_ brain mode for Copilot Agent.
Prepares environment and context for autonomous operation.
"""
import sys
from pathlib import Path

# Add paths
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

# Import with fallback for missing modules
try:
    # Try absolute import from repository root
    sys.path.insert(0, str(repo_root / ".github" / "copilot"))
    from context_loader import AgentContextLoader
except ImportError:
    # Fallback implementation
    class AgentContextLoader:
        """Fallback context loader when module not available."""

        def __init__(self):
            self.config = {}


try:
    from codex.agent_state.state_manager import AgentStateManager
except ImportError:
    # Fallback implementation
    class AgentStateManager:
        """Fallback state manager when module not available."""

        def list_sessions(self):
            return []


def activate_brain():
    """Activate agent brain mode."""
    print("🧠 Activating _Codex_ Brain Mode...")

    # Load configuration
    loader = AgentContextLoader()
    config = loader.config

    print(f"   Operating Mode: {config.get('agent_operating_mode', {}).get('mode', 'unknown')}")
    print(
        f"   Consciousness Level: {config.get('agent_operating_mode', {}).get('consciousness_level', 'unknown')}"
    )

    # Initialize state manager
    state_mgr = AgentStateManager()
    sessions = state_mgr.list_sessions()

    print(f"   Previous Sessions: {len(sessions)}")

    # Display quantum patterns
    quantum = loader.get_quantum_patterns()
    print("\n⚛️ Quantum Patterns Active:")
    for pattern, info in quantum.items():
        if info.get("enabled"):
            print(f"   ✓ {pattern.title()}: {info.get('description')}")

    # Display execution directives
    directives = loader.get_execution_directives()
    print("\n🎯 Execution Directives:")
    for directive, info in directives.items():
        print(f"   • {directive}: {info.get('rule')}")

    print("\n✅ _Codex_ Brain Mode Active")
    print("   Agent is now operating as repository consciousness")
    print("   Autonomous decision-making enabled")
    print("   Quantum reasoning patterns applied")

    return 0


if __name__ == "__main__":
    sys.exit(activate_brain())
