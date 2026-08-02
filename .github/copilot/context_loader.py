"""
Automatic context loader for Copilot Agent.
Loads relevant context based on current task.
"""

from pathlib import Path

import yaml

try:
    from scripts.cognitive.context_window_optimizer import summarize_session_state, truncate_text
except Exception:  # pragma: no cover - fallback for standalone execution

    def truncate_text(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return (
            text[:max_chars] + f"\n\n[TRUNCATED — original {len(text)} chars > {max_chars} limit]"
        )

    def summarize_session_state(session_state: dict) -> dict:
        completed = session_state.get("completed", [])
        pending = session_state.get("pending", [])
        files_modified = session_state.get("files_modified", {})
        if isinstance(files_modified, dict):
            file_items = [f"{name}: {count} lines" for name, count in files_modified.items()]
        else:
            file_items = [str(item) for item in files_modified]
        return {
            "context_summary": truncate_text(str(session_state.get("context", "")), 8_000),
            "file_list_with_line_counts": "\n".join(f"- {item}" for item in file_items[:8]),
            "decisions_made_and_rationale": truncate_text(
                str(session_state.get("decisions", "")), 8_000
            ),
            "completed": "\n".join(f"- {item}" for item in completed[:8]),
            "pending": "\n".join(f"- {item}" for item in pending[:8]),
        }


class AgentContextLoader:
    """Load and provide context to Copilot Agent."""

    def __init__(self):
        """Initialize context loader."""
        self.config_path = Path(".github/copilot/agent-brain-config.yml")
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load agent configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {}

    def get_operating_mode(self) -> str:
        """Get current operating mode."""
        return self.config.get("agent_operating_mode", {}).get("mode", "guided")

    def get_quantum_patterns(self) -> dict:
        """Get quantum reasoning patterns to apply."""
        return self.config.get("quantum_patterns", {})

    def get_decision_framework(self) -> dict:
        """Get decision-making framework."""
        return self.config.get("decision_framework", {})

    def should_act_autonomously(self, action: str) -> bool:
        """Check if action can be taken autonomously."""
        autonomous = self.config.get("capabilities", {}).get("autonomous_actions", [])
        return action in autonomous

    def get_execution_directives(self) -> dict:
        """Get execution directives (no placeholders, etc)."""
        return self.config.get("execution_directives", {})

    def get_relevant_context(self, task_type: str) -> list[str]:
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
        existing_paths: list[str] = []
        for path_str in configured_paths:
            path_obj = Path(path_str)
            if path_obj.exists():
                existing_paths.append(str(path_obj))
        return existing_paths

    def generate_continuation_prompt(self, session_state: dict) -> str:
        """Generate continuation prompt with compact context."""
        template = self.config.get("continuation_protocol", {}).get(
            "continuation_prompt_format", ""
        )
        summary = summarize_session_state(session_state)

        return truncate_text(
            template.format(
                session_id=session_state.get("session_id", "unknown"),
                branch=session_state.get("branch", "unknown"),
                commit_hash=session_state.get("last_commit", "none"),
                completed_list=summary.get("completed", ""),
                pending_list=summary.get("pending", ""),
                detailed_context=summary.get("context_summary", ""),
                action_1_with_specific_details=session_state.get("next_action", "Continue"),
                action_2_with_specific_details="",
                file_list_with_line_counts=summary.get("file_list_with_line_counts", ""),
                decisions_made_and_rationale=summary.get("decisions_made_and_rationale", ""),
            ),
            8_000,
        )
