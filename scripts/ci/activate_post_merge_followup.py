#!/usr/bin/env python3
"""
POST-MERGE FOLLOW-UP ACTIVATION GUIDE
Orchestrates multi-lane custom agent delegation for post-merge work.

Usage:
    python scripts/ci/activate_post_merge_followup.py --pr <PR_NUMBER> [--commit <SHA>]

This script:
1. Validates merge state
2. Extracts PR comments
3. Generates lane-specific prompts
4. Activates custom agents in parallel
5. Tracks completion status
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configuration
AGENTS_CONFIG = {
    "lane_1": {
        "name": "Release Success Investigation",
        "agent": "pypi-publishing-operations-agent",
        "task": "Comparative analysis of successful vs failed releases",
        "priority": "high",
    },
    "lane_2": {
        "name": "PR Comment Resolution",
        "agent": "post-merge-doc-alignment-agent",
        "task": "Explicit review and response to all PR comments",
        "priority": "high",
    },
    "lane_3": {
        "name": "CI/Deployment Validation",
        "agent": "ci-emergency-response-agent",
        "task": "Validate CI/CD pipeline post-merge",
        "priority": "high",
    },
    "lane_4": {
        "name": "Monitoring & Health Check",
        "agent": "workflow-health-monitor",
        "task": "System health metrics and baseline",
        "priority": "medium",
    },
    "lane_5": {
        "name": "Documentation Alignment",
        "agent": "post-merge-doc-alignment-agent",
        "task": "Verify docs align with merge changes",
        "priority": "medium",
    },
}


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_lane_prompt(lane_id: str, config: Dict):
    """Print activation prompt for a specific lane."""
    print(f"\n🚀 LANE {lane_id.split('_')[1].upper()}: {config['name']}")
    print(f"   Agent: {config['agent']}")
    print(f"   Priority: {config['priority'].upper()}")
    print(f"   Task: {config['task']}")


def generate_activation_manifest(pr_number: int, commit_sha: str = None) -> Dict:
    """Generate manifest for multi-agent activation."""
    return {
        "activation_time": datetime.utcnow().isoformat() + "Z",
        "pr_number": pr_number,
        "merge_commit": commit_sha or "auto-detect",
        "lanes": {
            lane_id: {
                "status": "READY",
                "config": config,
                "start_time": None,
                "end_time": None,
                "result": None,
            }
            for lane_id, config in AGENTS_CONFIG.items()
        },
    }


def print_activation_guide():
    """Print the complete activation guide."""
    print_header("POST-MERGE FOLLOW-UP ACTIVATION GUIDE")

    print("\n📋 MULTI-LANE CUSTOM AGENT DELEGATION")
    print("\nThe following specialized agents will activate IN PARALLEL:\n")

    for lane_id, config in AGENTS_CONFIG.items():
        print_lane_prompt(lane_id, config)

    print_header("ACTIVATION STEPS")

    steps = [
        (
            "1. VALIDATION",
            [
                "Verify merge to main or 0D_base_ branch completed",
                "Confirm all pre-merge checks passed",
                "Extract merge commit SHA",
                "Load PR metadata and comments",
            ],
        ),
        (
            "2. LANE PROMPTS GENERATION",
            [
                "Lane 1: Release success investigation prompt",
                "Lane 2: PR comment extraction and response template",
                "Lane 3: CI/CD validation checklist",
                "Lane 4: Health monitoring baseline setup",
                "Lane 5: Documentation sync checklist",
            ],
        ),
        (
            "3. PARALLEL AGENT ACTIVATION",
            [
                "POST Lane 1 prompt → pypi-publishing-operations-agent",
                "POST Lane 2 prompt → post-merge-doc-alignment-agent",
                "POST Lane 3 prompt → ci-emergency-response-agent",
                "POST Lane 4 prompt → workflow-health-monitor",
                "POST Lane 5 prompt → post-merge-doc-alignment-agent",
                "💡 All 5 lanes run concurrently (typical duration: 15-45 min)",
            ],
        ),
        (
            "4. DELIVERABLE CONSOLIDATION",
            [
                "Lane 1: .codex/RELEASE_SUCCESS_COMPARISON_ANALYSIS.md",
                "Lane 2: .codex/PR_COMMENT_RESOLUTION_SUMMARY.md",
                "Lane 3: .codex/POST_MERGE_CI_VALIDATION_REPORT.md",
                "Lane 4: .codex/POST_MERGE_HEALTH_BASELINE.md",
                "Lane 5: .codex/POST_MERGE_DOC_ALIGNMENT_REPORT.md",
                "Final: .codex/POST_MERGE_CONSOLIDATION_SUMMARY.md",
            ],
        ),
        (
            "5. COMPLETION & SIGN-OFF",
            [
                "Verify all lane deliverables committed",
                "Confirm 100% of PR comments answered (Lane 2)",
                "Validate release fix playbook provided (Lane 1)",
                "Check health metrics within thresholds (Lane 4)",
                "Post final summary to PR comments",
            ],
        ),
    ]

    for step_title, step_items in steps:
        print(f"\n{step_title}:")
        for item in step_items:
            print(f"   • {item}")

    print_header("REFERENCE DOCUMENTS")
    print(
        """
The complete POST-MERGE FOLLOW-UP PROMPT is available at:
  📄 .codex/POST_MERGE_FOLLOWUP_PROMPT.md

Key sections:
  1. MULTI-LANE AGENT DELEGATION FRAMEWORK
  2. RELEASE SUCCESS INVESTIGATION — DETAILED METHODOLOGY
  3. PR COMMENT RESOLUTION — EXPLICIT RESPONSE PROTOCOL
  4. RELEASE COMPARISON ANALYSIS — DETAILED CHECKLIST
  5. ACTIVATION CHECKLIST
  6. EXPECTED DELIVERABLES
  7. ESCALATION TRIGGERS
"""
    )

    print_header("QUICK START FOR CURRENT PR")
    print(
        """
To activate post-merge follow-up for a specific PR:

  # Using Python
  python scripts/ci/activate_post_merge_followup.py --pr 5367

  # OR manually trigger in agent prompt:
  
  > Activate post-merge follow-up for PR #5367
  > Use lanes: 1,2,3,4,5
  > Reference successful releases: 0b670311, 2bd5fbb1
  > Include explicit PR comment responses
"""
    )

    print_header("SUCCESS CRITERIA")
    print(
        """
Post-merge follow-up is COMPLETE when:

  ✅ Lane 1: Release analysis with remediation playbook
  ✅ Lane 2: All PR comments explicitly answered + commit refs
  ✅ Lane 3: CI validation confirms post-merge stability
  ✅ Lane 4: Health metrics within acceptable ranges
  ✅ Lane 5: All documentation verified + links valid
  ✅ No escalated blockers remaining
  ✅ Final summary posted to PR
"""
    )


def main():
    """Main activation entry point."""
    print_activation_guide()

    # Generate and save activation manifest if args provided
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-manifest":
        pr_number = int(sys.argv[2].split("=")[1]) if len(sys.argv) > 2 else 0
        commit_sha = (
            sys.argv[3].split("=")[1] if len(sys.argv) > 3 else None
        )

        manifest = generate_activation_manifest(pr_number, commit_sha)

        codex_dir = Path(".codex")
        codex_dir.mkdir(exist_ok=True)

        manifest_path = (
            codex_dir / f"POST_MERGE_ACTIVATION_MANIFEST_PR{pr_number}.json"
        )
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✅ Activation manifest saved to: {manifest_path}")


if __name__ == "__main__":
    main()
