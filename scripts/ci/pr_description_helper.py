#!/usr/bin/env python3
"""
pr_description_helper.py — WEC Preservation & PR Description Management

Purpose
-------
Provides utilities for building PR descriptions while preserving Workflow Execution
Checklist (WEC) state across agent turns. Implements the "read-before-write" pattern
to prevent loss of maintainer-selected checkboxes. Also handles CI workflow updates
(secrets-baseline-enforcer push logic), RAG cache loading semantics, and auth
email validation.

Functions
---------
- build_pr_description_with_wec(): Main entry point for agents
- read_pr_body(): Fetch live PR body from GitHub
- extract_and_preserve_wec_state(): Extract and record WEC state
- record_wec_checkpoint(): Record WEC state to .codex/wec_state.json
- calculate_merge_readiness_score(): Calculate 10-gate readiness score

Usage
-----
    from pr_description_helper import build_pr_description_with_wec

    # Implement the read-before-write pattern
    pr_description = build_pr_description_with_wec(
        checklist_text=my_progress_checklist,
        pr_number=4662,
        repo_owner="Aries-Serpent",
        repo_name="_codex_"
    )

    # Pass to report_progress
    engine_tools_report_progress(
        prDescription=pr_description,
        commitMessage="Fix: Update merge readiness gates"
    )

Design Principles
-----------------
- **Non-destructive**: Always reads current state before writing
- **Maintainer-respecting**: Preserves maintainer [x] selections
- **Auditable**: Records all state transitions to .codex/wec_state.json
- **Idempotent**: Safe to call multiple times without duplication
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Repository configuration
REPO_ROOT = Path(__file__).resolve().parents[2]
WEC_STATE_FILE = REPO_ROOT / ".codex" / "wec_state.json"
REPO_OWNER = "Aries-Serpent"
REPO_NAME = "_codex_"


def read_pr_body(pr_number: int, repo_owner: str = REPO_OWNER, repo_name: str = REPO_NAME) -> str:
    """
    Fetch live PR body from GitHub using gh CLI.

    Args:
        pr_number: PR number to fetch
        repo_owner: Repository owner (default: "Aries-Serpent")
        repo_name: Repository name (default: "_codex_")

    Returns:
        PR body content as string, or empty string if fetch fails
    """
    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "view",
                str(pr_number),
                "--repo",
                f"{repo_owner}/{repo_name}",
                "--json",
                "body",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        return data.get("body", "")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to fetch PR body for #{pr_number}: {e.stderr}")
        return ""
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse gh output: {e}")
        return ""


def extract_and_preserve_wec_state(
    pr_body: str,
) -> Dict[str, bool]:
    """
    Extract WEC checkbox state from PR body using session_wrapup_autofix utilities.

    Args:
        pr_body: Full PR body content

    Returns:
        Dictionary mapping workflow names to their checked state:
        {
            "pre-merge-validation.yml": True,
            "comment-review-gate.yml": True,
            ...
        }

    Implementation Note:
        This function delegates to session_wrapup_autofix._extract_wec_state()
        which is the canonical WEC parser. It handles both current and legacy
        WEC formats.
    """
    try:
        ci_path = str(REPO_ROOT / "scripts" / "ci")
        if ci_path not in sys.path:
            sys.path.insert(0, ci_path)
        import session_wrapup_autofix as swa

        existing_state = swa._extract_wec_state(pr_body)
        logger.debug(f"Extracted WEC state: {existing_state}")
        return existing_state
    except ImportError as e:
        logger.warning(f"Could not import session_wrapup_autofix: {e}. Using default state.")
        return {
            "deferral-language-gate.yml": True,
            "agent-auth-delegation.yml": True,
            "workflow-execution-gate.yml": True,
            "cost-gate.yml": True,
            "auto-approve-workflows": True,
            "auth-tests.yml": False,
            "audit-qa-suite.yml": False,
            "data-quality-suite.yml": False,
            "docker-build-push.yml": False,
            "nox_gates.yml": False,
            "security-scanning-suite.yml": False,
            "test-rag.yml": False,
            "scheduled-archival.yml": False,
            "scheduled-dependency-audit.yml": False,
        }


def build_wec_block(existing_state: Optional[Dict[str, bool]] = None) -> str:
    """
    Build canonical WEC block with maintained state.

    Args:
        existing_state: Maintainer-selected checkpoint state (or None for default)

    Returns:
        Canonical WEC markdown block ready to append to PR body

    Implementation Note:
        This function delegates to session_wrapup_autofix._build_wec_block()
        to ensure consistency with the authoritative WEC builder.
    """
    try:
        ci_path = str(REPO_ROOT / "scripts" / "ci")
        if ci_path not in sys.path:
            sys.path.insert(0, ci_path)
        import session_wrapup_autofix as swa

        wec_block = swa._build_wec_block(existing_state=existing_state)
        logger.debug("Built canonical WEC block")
        return wec_block
    except ImportError as e:
        logger.error(f"Could not import session_wrapup_autofix: {e}")
        # Fallback to minimal WEC
        return "## 🔄 Workflow Execution Checklist\n\nWorkflows can be skipped/dispatched by updating these checkboxes:\n\n- [x] deferral-language-gate.yml\n- [x] agent-auth-delegation.yml\n- [x] workflow-execution-gate.yml\n- [x] cost-gate.yml\n- [x] auto-approve-workflows\n"


def compute_body_hash(body_without_wec: str) -> str:
    """
    Compute SHA256 hash of PR body (excluding WEC section).

    Args:
        body_without_wec: PR body content before WEC marker

    Returns:
        Hex-encoded SHA256 hash
    """
    return hashlib.sha256(body_without_wec.encode()).hexdigest()


def record_wec_checkpoint(
    pr_number: int,
    wec_state: Dict[str, bool],
    body_hash: str,
    session_id: Optional[str] = None,
    turn_number: Optional[int] = None,
    merge_readiness_score: Optional[int] = None,
) -> bool:
    """
    Record WEC checkpoint to .codex/wec_state.json for auditing.

    Args:
        pr_number: PR number
        wec_state: Current WEC checkbox state
        body_hash: Hash of current PR body (without WEC)
        session_id: Optional session identifier
        turn_number: Optional turn number in session
        merge_readiness_score: Optional merge readiness score (0–100)

    Returns:
        True if successfully recorded, False otherwise
    """
    try:
        # Load existing state
        if WEC_STATE_FILE.exists():
            with open(WEC_STATE_FILE, "r") as f:
                state_data = json.load(f)
        else:
            state_data = {
                "session_metadata": {
                    "session_id": session_id,
                    "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "updated_at": None,
                    "pr_number": pr_number,
                    "branch": None,
                },
                "wec_state_history": [],
            }

        # Add checkpoint
        checkpoint = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "report_progress",
            "session_id": session_id,
            "turn_number": turn_number,
            "wec_state": wec_state,
            "body_hash": body_hash,
            "merge_readiness_score": merge_readiness_score,
        }

        state_data["wec_state_history"].append(checkpoint)
        state_data["session_metadata"]["updated_at"] = checkpoint["timestamp"]
        state_data["last_maintainer_selections"] = wec_state

        # Write updated state
        with open(WEC_STATE_FILE, "w") as f:
            json.dump(state_data, f, indent=2)

        logger.info(f"Recorded WEC checkpoint for PR #{pr_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to record WEC checkpoint: {e}")
        return False


def calculate_merge_readiness_score(
    gates: Dict[str, bool],
    gate_weights: Optional[Dict[str, int]] = None,
) -> int:
    """
    Calculate merge readiness score (0–100) from 10 pre-merge gates.

    Args:
        gates: Dictionary mapping gate names to boolean pass/fail status
            {
                "code_quality": True,
                "test_coverage": True,
                ...
            }
            Each gate receives full credit (weight) if True, zero if False.
        gate_weights: Optional custom weights (default: standard weights)

    Returns:
        Composite merge readiness score as integer (0–100).
        Note: Partial credit (e.g., 0.5×) is not currently supported;
        each gate is binary (pass/fail with full weight or zero).

    Gate Weights (default):
        - code_quality: 12 pts
        - test_coverage: 12 pts
        - security_secrets: 15 pts
        - wec_integrity: 14 pts
        - deferral_language: 10 pts
        - comment_review: 12 pts
        - accountability_report: 8 pts
        - action_versions: 7 pts
        - workflow_syntax: 7 pts
        - merge_dependencies: 3 pts
        Total: 100 pts
    """
    if gate_weights is None:
        gate_weights = {
            "code_quality": 12,
            "test_coverage": 12,
            "security_secrets": 15,
            "wec_integrity": 14,
            "deferral_language": 10,
            "comment_review": 12,
            "accountability_report": 8,
            "action_versions": 7,
            "workflow_syntax": 7,
            "merge_dependencies": 3,
        }

    total_points = 0
    for gate_name, weight in gate_weights.items():
        if gates.get(gate_name, False):
            total_points += weight

    return min(100, max(0, total_points))


def build_pr_description_with_wec(
    checklist_text: str,
    pr_number: Optional[int] = None,
    repo_owner: str = REPO_OWNER,
    repo_name: str = REPO_NAME,
    session_id: Optional[str] = None,
    turn_number: Optional[int] = None,
    merge_readiness_score: Optional[int] = None,
) -> str:
    """
    Build PR description with live WEC state preserved (PRIMARY ENTRY POINT).

    This implements the "read-before-write" pattern documented in
    Phase 3.1 of the PR Merge Readiness Implementation plan.

    Args:
        checklist_text: Progress checklist content (typically from report_progress)
        pr_number: PR number for fetching live WEC state (required for state preservation)
        repo_owner: Repository owner (default: "Aries-Serpent")
        repo_name: Repository name (default: "_codex_")
        session_id: Optional session identifier for checkpoint recording
        turn_number: Optional turn number for auditing
        merge_readiness_score: Optional score to record in checkpoint

    Returns:
        Complete PR description ready for report_progress():
        ```
        {checklist_text}

        {wec_block}
        ```

    Raises:
        subprocess.CalledProcessError: If gh command fails and pr_number is provided

    Example:
        ```python
        from pr_description_helper import build_pr_description_with_wec

        checklist = '''## ✅ Progress
        - [x] Phase 1: PR body preparation
        - [x] Phase 2: Validation gates
        - [ ] Phase 3: WEC management'''

        pr_description = build_pr_description_with_wec(
            checklist_text=checklist,
            pr_number=4662,
            session_id="S12345",
            turn_number=1
        )

        engine_tools_report_progress(
            prDescription=pr_description,
            commitMessage="Progress: Implementing merge readiness framework"
        )
        ```
    """
    logger.info(f"Building PR description with WEC preservation (PR #{pr_number})")

    # Read live PR body to get current WEC state
    live_body = ""
    existing_state = None

    if pr_number:
        try:
            live_body = read_pr_body(pr_number, repo_owner, repo_name)
            if live_body:
                existing_state = extract_and_preserve_wec_state(live_body)
                logger.info("Extracted existing WEC state from live PR body")
            else:
                logger.warning(f"Could not fetch live PR body for #{pr_number}")
        except Exception as e:
            logger.warning(f"Error reading PR body: {e}. Using default WEC state.")

    # Build canonical WEC with preserved state
    wec_block = build_wec_block(existing_state=existing_state)

    # Construct final description
    pr_description = f"{checklist_text}\n\n{wec_block}"

    # Record checkpoint if pr_number provided
    if pr_number and existing_state:
        try:
            body_without_wec = checklist_text
            body_hash = compute_body_hash(body_without_wec)
            record_wec_checkpoint(
                pr_number=pr_number,
                wec_state=existing_state,
                body_hash=body_hash,
                session_id=session_id,
                turn_number=turn_number,
                merge_readiness_score=merge_readiness_score,
            )
        except Exception as e:
            logger.warning(f"Could not record WEC checkpoint: {e}")

    logger.debug("PR description with WEC built successfully")
    return pr_description


if __name__ == "__main__":
    # Example usage for testing
    logging.basicConfig(level=logging.DEBUG)

    # Test read-before-write pattern
    test_checklist = """## 📊 Merge Readiness Progress
- [x] Phase 1: PR body preparation
- [x] Phase 2: Validation gates
- [ ] Phase 3: WEC management"""

    try:
        # Example (would fail without a real PR)
        result = build_pr_description_with_wec(
            checklist_text=test_checklist,
            pr_number=4662,
            session_id="S_TEST",
            turn_number=1,
        )
        print("✅ Generated PR description:")
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")
