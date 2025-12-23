"""
Automatic context loader for Copilot Agent.
Loads relevant context based on current task.
"""

from pathlib import Path
from typing import Dict, List

import yaml


class AgentContextLoader:
    """Load and provide context to Copilot Agent."""

    def __init__(self):
        """Initialize context loader."""
        self.config_path = Path(".github/copilot/agent-brain-config.yml")
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load agent configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {}

    def get_operating_mode(self) -> str:
        """Get current operating mode."""
        return self.config.get("agent_operating_mode", {}).get("mode", "guided")

    def get_quantum_patterns(self) -> Dict:
        """Get quantum reasoning patterns to apply."""
        return self.config.get("quantum_patterns", {})

    def get_decision_framework(self) -> Dict:
        """Get decision-making framework."""
        return self.config.get("decision_framework", {})

    def should_act_autonomously(self, action: str) -> bool:
        """Check if action can be taken autonomously."""
        autonomous = self.config.get("capabilities", {}).get("autonomous_actions", [])
        return action in autonomous

    def get_execution_directives(self) -> Dict:
        """Get execution directives (no placeholders, etc)."""
        return self.config.get("execution_directives", {})

    def get_relevant_context(self, task_type: str) -> List[str]:
        """Get relevant context files/directories for task type that exist on disk."""
        context_map = {
            "ast_implementation": [
                "docs/admin/AST_IMPLEMENTATION_STATUS.md",
                "src/codex/ast/parser.py",
                "agents/advanced_physics_calculators.py",
            ],
            "security_fix": ["scripts/security/", ".github/workflows/security-scan.yml"],
            "feature_implementation": [
                "docs/maturity/MATURITY_REMAINING_WORK.md",
                "agents/agent_memory.py",
            ],
        }
        configured_paths = context_map.get(task_type, [])
        existing_paths: List[str] = []
        for path_str in configured_paths:
            path_obj = Path(path_str)
            if path_obj.exists():
                existing_paths.append(str(path_obj))
        return existing_paths

    def generate_continuation_prompt(self, session_state: Dict) -> str:
        """Generate continuation prompt with full context."""
        template = self.config.get("continuation_protocol", {}).get(
            "continuation_prompt_format", ""
        )

        return template.format(
            session_id=session_state.get("session_id", "unknown"),
            branch=session_state.get("branch", "unknown"),
            commit_hash=session_state.get("last_commit", "none"),
            completed_list="\n".join(f"- {t}" for t in session_state.get("completed", [])),
            pending_list="\n".join(f"- {t}" for t in session_state.get("pending", [])),
            detailed_context=session_state.get("context", ""),
            action_1_with_specific_details=session_state.get("next_action", "Continue"),
            action_2_with_specific_details="",
            file_list_with_line_counts="\n".join(
                f"- {f}: {c} lines" for f, c in session_state.get("files_modified", {}).items()
            ),
            decisions_made_and_rationale=session_state.get("decisions", ""),
        )
