#!/usr/bin/env python3
"""
Cognitive Brain Session Manager

This module provides session state management for GitHub Copilot Coding Agent
sessions, enabling:
1. Automatic session state tracking
2. Pattern learning and application
3. Objective alignment verification
4. Continuation prompt generation

Usage:
    python scripts/cognitive/session_manager.py --start
    python scripts/cognitive/session_manager.py --checkpoint
    python scripts/cognitive/session_manager.py --end
    python scripts/cognitive/session_manager.py --generate-continuation
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Represents the current session state."""
    session_id: str
    pr_number: Optional[int]
    phase: str
    started: str
    status: str
    objectives: list[str] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)
    pending_tasks: list[str] = field(default_factory=list)
    patterns_applied: list[str] = field(default_factory=list)
    patterns_learned: list[str] = field(default_factory=list)
    checkpoints: list[dict[str, Any]] = field(default_factory=list)
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)


@dataclass
class Pattern:
    """Represents a learned pattern."""
    id: str
    category: str
    symptoms: list[str]
    solutions: list[str]
    success_rate: float
    times_applied: int
    last_used: str


class CognitiveBrainSessionManager:
    """Manages session state and pattern learning for cognitive brain."""

    def __init__(self, repo_root: Optional[str] = None):
        """Initialize the session manager."""
        self.repo_root = Path(repo_root or os.getcwd())
        self.cognitive_brain_dir = self.repo_root / ".codex" / "cognitive_brain"
        self.session_tracker_path = self.cognitive_brain_dir / "session_tracker.md"
        self.pattern_store_path = self.cognitive_brain_dir / "pattern_learning_store.json"
        self.objectives_path = self.cognitive_brain_dir / "objectives_tracker.md"

        # Ensure directories exist
        self.cognitive_brain_dir.mkdir(parents=True, exist_ok=True)

        self.current_session: Optional[SessionState] = None
        self.patterns: dict[str, Pattern] = {}

        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load patterns from the pattern store."""
        if self.pattern_store_path.exists():
            try:
                with open(self.pattern_store_path) as f:
                    data = json.load(f)
                    for name, pattern_data in data.get("patterns", {}).items():
                        self.patterns[name] = Pattern(
                            id=pattern_data.get("id", name),
                            category=pattern_data.get("category", "general"),
                            symptoms=pattern_data.get("symptoms", []),
                            solutions=pattern_data.get("solutions", []),
                            success_rate=pattern_data.get("success_rate", 0.0),
                            times_applied=pattern_data.get("times_applied", 0),
                            last_used=pattern_data.get("last_used", "")
                        )
                logger.info(f"Loaded {len(self.patterns)} patterns")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error loading patterns: {e}")

    def _save_patterns(self) -> None:
        """Save patterns to the pattern store."""
        if not self.pattern_store_path.exists():
            return

        with open(self.pattern_store_path) as f:
            data = json.load(f)

        for name, pattern in self.patterns.items():
            if name in data.get("patterns", {}):
                data["patterns"][name]["times_applied"] = pattern.times_applied
                data["patterns"][name]["last_used"] = pattern.last_used
                data["patterns"][name]["success_rate"] = pattern.success_rate

        with open(self.pattern_store_path, 'w') as f:
            json.dump(data, f, indent=2)

    def start_session(
        self,
        session_id: str,
        pr_number: Optional[int] = None,
        objectives: Optional[list[str]] = None
    ) -> SessionState:
        """Start a new session."""
        timestamp = datetime.now(timezone.utc).isoformat()

        self.current_session = SessionState(
            session_id=session_id,
            pr_number=pr_number,
            phase="initialization",
            started=timestamp,
            status="in_progress",
            objectives=objectives or []
        )

        logger.info(f"Started session: {session_id}")
        return self.current_session

    def checkpoint(
        self,
        phase: str,
        completed: Optional[list[str]] = None,
        pending: Optional[list[str]] = None,
        notes: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a session checkpoint."""
        if not self.current_session:
            raise ValueError("No active session")

        now = datetime.now(timezone.utc).isoformat()

        checkpoint = {
            "timestamp": now,
            "phase": phase,
            "completed": completed or [],
            "pending": pending or [],
            "notes": notes
        }

        self.current_session.phase = phase
        self.current_session.checkpoints.append(checkpoint)

        if completed:
            self.current_session.completed_tasks.extend(completed)
        if pending:
            self.current_session.pending_tasks = pending

        logger.info(f"Checkpoint created: {phase}")
        return checkpoint

    def apply_pattern(self, pattern_name: str, success: bool = True) -> Optional[Pattern]:
        """Record application of a pattern."""
        if pattern_name not in self.patterns:
            logger.warning(f"Pattern not found: {pattern_name}")
            return None

        pattern = self.patterns[pattern_name]
        pattern.times_applied += 1
        pattern.last_used = datetime.now(timezone.utc).isoformat()

        # Update success rate with exponential moving average (EMA).
        # Alpha=0.1 weights: 10% current result, 90% historical average.
        # This creates stability while still adapting to recent outcomes.
        alpha = 0.1
        pattern.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * pattern.success_rate

        if self.current_session:
            self.current_session.patterns_applied.append(pattern_name)

        self._save_patterns()
        logger.info(f"Applied pattern: {pattern_name} (success={success})")
        return pattern

    def learn_pattern(
        self,
        name: str,
        category: str,
        symptoms: list[str],
        solutions: list[str]
    ) -> Pattern:
        """Learn a new pattern."""
        pattern_id = f"{category.upper()[:2]}-{len(self.patterns) + 1:03d}"
        now = datetime.now(timezone.utc).isoformat()

        pattern = Pattern(
            id=pattern_id,
            category=category,
            symptoms=symptoms,
            solutions=solutions,
            success_rate=0.5,  # Initial neutral rate
            times_applied=0,
            last_used=now
        )

        self.patterns[name] = pattern

        if self.current_session:
            self.current_session.patterns_learned.append(name)

        logger.info(f"Learned new pattern: {name}")
        return pattern

    def find_applicable_patterns(self, symptoms: list[str]) -> list[Pattern]:
        """Find patterns that match given symptoms."""
        applicable = []

        for pattern in self.patterns.values():
            # Check if any symptom matches
            for symptom in symptoms:
                symptom_lower = symptom.lower()
                for pattern_symptom in pattern.symptoms:
                    if symptom_lower in pattern_symptom.lower() or pattern_symptom.lower() in symptom_lower:
                        applicable.append(pattern)
                        break
                else:
                    continue
                break

        # Sort by success rate
        applicable.sort(key=lambda p: p.success_rate, reverse=True)
        return applicable

    def end_session(self, outcome: str = "success") -> dict[str, Any]:
        """End the current session."""
        if not self.current_session:
            raise ValueError("No active session")

        now = datetime.now(timezone.utc).isoformat()

        self.current_session.status = outcome

        summary = {
            "session_id": self.current_session.session_id,
            "pr_number": self.current_session.pr_number,
            "started": self.current_session.started,
            "ended": now,
            "outcome": outcome,
            "completed_tasks": self.current_session.completed_tasks,
            "pending_tasks": self.current_session.pending_tasks,
            "patterns_applied": self.current_session.patterns_applied,
            "patterns_learned": self.current_session.patterns_learned,
            "checkpoints": len(self.current_session.checkpoints),
            "files_created": self.current_session.files_created,
            "files_modified": self.current_session.files_modified
        }

        logger.info(f"Session ended: {self.current_session.session_id} ({outcome})")
        return summary

    def generate_continuation_prompt(self) -> str:
        """Generate a continuation prompt for the next session."""
        if not self.current_session:
            return "No active session to generate continuation from."

        timestamp = datetime.now(timezone.utc).isoformat()

        prompt = f"""## Session Continuation - PR #{self.current_session.pr_number or 'N/A'}

**Last Session:** {self.current_session.started}
**Generated:** {timestamp}
**Status:** {self.current_session.status}

### Completed Tasks
"""
        for task in self.current_session.completed_tasks:
            prompt += f"- [x] {task}\n"

        prompt += "\n### Pending Tasks\n"
        for task in self.current_session.pending_tasks:
            prompt += f"- [ ] {task}\n"

        prompt += "\n### Patterns Applied\n"
        for pattern in self.current_session.patterns_applied:
            if pattern in self.patterns:
                p = self.patterns[pattern]
                prompt += f"- **{pattern}** (success rate: {p.success_rate:.0%})\n"

        prompt += "\n### Key Context\n"
        if self.current_session.checkpoints:
            last_checkpoint = self.current_session.checkpoints[-1]
            prompt += f"- Last phase: {last_checkpoint.get('phase', 'unknown')}\n"
            if last_checkpoint.get('notes'):
                prompt += f"- Notes: {last_checkpoint['notes']}\n"

        prompt += "\n### Recommended Next Actions\n"
        if self.current_session.pending_tasks:
            prompt += f"1. Continue with: {self.current_session.pending_tasks[0]}\n"
        prompt += "2. Review cognitive brain objectives for alignment\n"
        prompt += "3. Apply relevant patterns from pattern store\n"

        return prompt

    def track_file_operation(self, path: str, operation: str) -> None:
        """Track a file operation."""
        if not self.current_session:
            return

        if operation in ("create", "created"):
            self.current_session.files_created.append(path)
        elif operation in ("edit", "modified", "updated"):
            self.current_session.files_modified.append(path)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Cognitive Brain Session Manager")
    parser.add_argument("--start", action="store_true", help="Start a new session")
    parser.add_argument("--checkpoint", action="store_true", help="Create a checkpoint")
    parser.add_argument("--end", action="store_true", help="End the current session")
    parser.add_argument("--generate-continuation", action="store_true",
                        help="Generate continuation prompt")
    parser.add_argument("--session-id", type=str, help="Session ID")
    parser.add_argument("--pr", type=int, help="PR number")
    parser.add_argument("--phase", type=str, help="Current phase")
    parser.add_argument("--find-patterns", type=str, nargs="+",
                        help="Find patterns matching symptoms")
    parser.add_argument("--apply-pattern", type=str, help="Apply a pattern")
    parser.add_argument("--outcome", type=str, default="success",
                        help="Session outcome (success/failure)")

    args = parser.parse_args()

    manager = CognitiveBrainSessionManager()

    if args.start:
        if not args.session_id:
            print("Error: --session-id required for --start")
            sys.exit(1)
        session = manager.start_session(args.session_id, args.pr)
        print(f"Session started: {session.session_id}")

    elif args.checkpoint:
        if not args.phase:
            print("Error: --phase required for --checkpoint")
            sys.exit(1)
        checkpoint = manager.checkpoint(args.phase)
        print(f"Checkpoint created: {checkpoint}")

    elif args.end:
        summary = manager.end_session(args.outcome)
        print(f"Session ended: {json.dumps(summary, indent=2)}")

    elif args.generate_continuation:
        prompt = manager.generate_continuation_prompt()
        print(prompt)

    elif args.find_patterns:
        patterns = manager.find_applicable_patterns(args.find_patterns)
        for p in patterns:
            print(f"- {p.id}: {p.category} (success: {p.success_rate:.0%})")
            print(f"  Solutions: {', '.join(p.solutions[:2])}")

    elif args.apply_pattern:
        pattern = manager.apply_pattern(args.apply_pattern)
        if pattern:
            print(f"Applied: {pattern.id} ({pattern.success_rate:.0%} success rate)")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
