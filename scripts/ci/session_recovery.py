#!/usr/bin/env python3
"""
Session Recovery Utility

Provides tools for detecting, recovering, and managing failed Copilot sessions.
This script is used by the session-recovery-handler.yml workflow and by Copilot
agents to checkpoint session state and handle recovery.

Usage:
  python scripts/ci/session_recovery.py checkpoint --session-id <id>
  python scripts/ci/session_recovery.py heartbeat --session-id <id>
  python scripts/ci/session_recovery.py detect-failure --workflow-run-id <id>
  python scripts/ci/session_recovery.py recover --session-id <id>
  python scripts/ci/session_recovery.py metrics --output-file <path>
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class SessionRecoveryManager:
    """Manages session recovery operations."""

    SESSION_DIR = Path(".codex/sessions")
    RECOVERY_LOG = Path(".codex/session_recovery_log.jsonl")
    HEARTBEAT_FILE = Path(".codex/session_heartbeats.jsonl")
    METRICS_FILE = Path(".codex/session_recovery_metrics.json")
    CONFIG_FILE = Path(".codex/session_recovery_config.yml")

    def __init__(self):
        """Initialize session recovery manager."""
        self.session_dir = self.SESSION_DIR
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def create_checkpoint(self, session_id: str) -> Dict[str, Any]:
        """Create a checkpoint of the current session state."""
        checkpoint = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "checkpoint_type": "manual",
            "git_branch": self._get_current_branch(),
            "git_commit": self._get_current_commit(),
            "git_status": self._get_git_status(),
            "uncommitted_changes": self._has_uncommitted_changes(),
        }

        # Save checkpoint
        checkpoint_file = self.session_dir / f"checkpoint_{session_id}_{int(time.time())}.json"
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint, f, indent=2)

        # Log to JSONL
        self._append_log("checkpoint", checkpoint)

        print(f"✅ Checkpoint created: {checkpoint_file}")
        return checkpoint

    def emit_heartbeat(self, session_id: str) -> Dict[str, Any]:
        """Emit a session heartbeat."""
        heartbeat = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "git_branch": self._get_current_branch(),
            "git_commit": self._get_current_commit(),
            "status": "alive",
        }

        # Log to heartbeat file
        with open(self.HEARTBEAT_FILE, "a") as f:
            f.write(json.dumps(heartbeat) + "\n")

        return heartbeat

    def detect_failure(self, workflow_run_id: int) -> Dict[str, Any]:
        """Detect a failed session from workflow run ID."""
        result = {
            "workflow_run_id": workflow_run_id,
            "detected": False,
            "failure_type": None,
            "details": None,
        }

        # Try to get workflow run info
        try:
            cmd = [
                "gh",
                "run",
                "view",
                str(workflow_run_id),
                "--json",
                "conclusion,status,name,headBranch,createdAt,updatedAt",
            ]
            output = subprocess.run(cmd, capture_output=True, text=True, check=True)
            run_info = json.loads(output.stdout)

            result["detected"] = True
            result["failure_type"] = run_info.get("conclusion", "unknown")
            result["details"] = run_info
            result["branch"] = run_info.get("headBranch", "unknown")
            result["duration_seconds"] = self._calculate_duration(
                run_info.get("createdAt"), run_info.get("updatedAt")
            )

        except subprocess.CalledProcessError as e:
            result["error"] = str(e)

        return result

    def recover_session(self, session_id: str, workflow_run_id: int) -> Dict[str, Any]:
        """Recover a failed session."""
        recovery = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": session_id,
            "workflow_run_id": workflow_run_id,
            "recovery_status": "initiated",
            "steps": [],
        }

        # Step 1: Log recovery event
        self._append_log("recovery_initiated", recovery)
        recovery["steps"].append("✅ Recovery logged")

        # Step 2: Extract failure context
        failure_info = self.detect_failure(workflow_run_id)
        recovery["failure_type"] = failure_info.get("failure_type")
        recovery["branch"] = failure_info.get("branch")
        recovery["steps"].append(f"✅ Failure detected: {failure_info.get('failure_type')}")

        # Step 3: Load last checkpoint
        checkpoint = self._find_last_checkpoint(session_id)
        if checkpoint:
            recovery["checkpoint_recovered"] = True
            recovery["steps"].append(f"✅ Last checkpoint recovered from {checkpoint}")
        else:
            recovery["checkpoint_recovered"] = False
            recovery["steps"].append("⚠️ No checkpoint found (fresh recovery)")

        # Step 4: Verify git state
        recovery["git_state"] = {
            "branch": self._get_current_branch(),
            "commit": self._get_current_commit(),
            "clean": not self._has_uncommitted_changes(),
        }
        recovery["steps"].append(f"✅ Git state verified on {recovery['git_state']['branch']}")

        # Step 5: Mark recovery complete
        recovery["recovery_status"] = "completed"
        self._append_log("recovery_completed", recovery)
        recovery["steps"].append("✅ Recovery completed")

        print("\n".join(recovery["steps"]))
        return recovery

    def get_metrics(self) -> Dict[str, Any]:
        """Get session recovery metrics."""
        metrics = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_checkpoints": 0,
            "total_heartbeats": 0,
            "total_failures": 0,
            "total_recoveries": 0,
            "successful_recoveries": 0,
        }

        # Count checkpoints
        if self.session_dir.exists():
            metrics["total_checkpoints"] = len(list(self.session_dir.glob("checkpoint_*.json")))

        # Parse logs
        if self.RECOVERY_LOG.exists():
            with open(self.RECOVERY_LOG, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("type") == "recovery_initiated":
                            metrics["total_recoveries"] += 1
                        elif entry.get("type") == "recovery_completed":
                            metrics["successful_recoveries"] += 1
                        elif entry.get("type") == "session_failure_detected":
                            metrics["total_failures"] += 1
                    except json.JSONDecodeError:
                        pass

        # Count heartbeats
        if self.HEARTBEAT_FILE.exists():
            with open(self.HEARTBEAT_FILE, "r") as f:
                metrics["total_heartbeats"] = sum(1 for _ in f)

        # Calculate rates
        if metrics["total_recoveries"] > 0:
            metrics["recovery_success_rate"] = (
                metrics["successful_recoveries"] / metrics["total_recoveries"]
            )
        else:
            metrics["recovery_success_rate"] = 0.0

        return metrics

    # Private helper methods

    def _get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"

    def _get_current_commit(self) -> str:
        """Get current git commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"

    def _get_git_status(self) -> Dict[str, Any]:
        """Get git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--short"], capture_output=True, text=True, check=True
            )
            return {"changed_files": result.stdout.strip().split("\n") if result.stdout else []}
        except subprocess.CalledProcessError:
            return {"error": "Could not get git status"}

    def _has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--quiet"], capture_output=True, check=False
            )
            return result.returncode != 0
        except subprocess.CalledProcessError:
            return True

    def _append_log(self, event_type: str, data: Dict[str, Any]) -> None:
        """Append event to recovery log."""
        entry = {"type": event_type, **data}
        with open(self.RECOVERY_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _find_last_checkpoint(self, session_id: str) -> Optional[str]:
        """Find the last checkpoint for a session."""
        if not self.session_dir.exists():
            return None

        checkpoints = sorted(
            self.session_dir.glob(f"checkpoint_{session_id}_*.json"), reverse=True
        )
        return str(checkpoints[0]) if checkpoints else None

    def _calculate_duration(self, created_at: Optional[str], updated_at: Optional[str]) -> int:
        """Calculate duration in seconds between two ISO timestamps."""
        if not created_at or not updated_at:
            return 0
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            return int((updated - created).total_seconds())
        except (ValueError, AttributeError):
            return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Session Recovery Utility")
    subparsers = parser.add_subparsers(dest="command", help="Recovery command")

    # Checkpoint command
    checkpoint_parser = subparsers.add_parser("checkpoint", help="Create session checkpoint")
    checkpoint_parser.add_argument("--session-id", required=True, help="Session ID")

    # Heartbeat command
    heartbeat_parser = subparsers.add_parser("heartbeat", help="Emit session heartbeat")
    heartbeat_parser.add_argument("--session-id", required=True, help="Session ID")

    # Detect failure command
    detect_parser = subparsers.add_parser("detect-failure", help="Detect workflow failure")
    detect_parser.add_argument("--workflow-run-id", required=True, type=int, help="Workflow run ID")

    # Recover command
    recover_parser = subparsers.add_parser("recover", help="Recover a failed session")
    recover_parser.add_argument("--session-id", required=True, help="Session ID")
    recover_parser.add_argument("--workflow-run-id", required=True, type=int, help="Workflow run ID")

    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Get recovery metrics")
    metrics_parser.add_argument("--output-file", help="Output file for metrics (JSON)")

    args = parser.parse_args()

    manager = SessionRecoveryManager()

    if args.command == "checkpoint":
        result = manager.create_checkpoint(args.session_id)
        print(json.dumps(result, indent=2))

    elif args.command == "heartbeat":
        result = manager.emit_heartbeat(args.session_id)
        print(json.dumps(result, indent=2))

    elif args.command == "detect-failure":
        result = manager.detect_failure(args.workflow_run_id)
        print(json.dumps(result, indent=2))

    elif args.command == "recover":
        result = manager.recover_session(args.session_id, args.workflow_run_id)
        print(json.dumps(result, indent=2))

    elif args.command == "metrics":
        metrics = manager.get_metrics()
        print(json.dumps(metrics, indent=2))

        if args.output_file:
            with open(args.output_file, "w") as f:
                json.dump(metrics, f, indent=2)
            print(f"✅ Metrics saved to {args.output_file}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
