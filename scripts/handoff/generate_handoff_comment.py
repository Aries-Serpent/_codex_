#!/usr/bin/env python3
"""
Hand-off Comment Generator

Generates hand-off comments from templates with variable substitution.
Supports both Copilot→Codex and Codex→Copilot templates.

Usage:
    python generate_handoff_comment.py --template copilot_to_codex --phase "Pre-commit 3-4" --output comment.md
    python generate_handoff_comment.py --template codex_to_copilot --phase "Pre-commit 3-4" --decision approve --output response.md
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Template paths
TEMPLATE_DIR = Path(".codex/templates/handoff")
COPILOT_TO_CODEX_TEMPLATE = TEMPLATE_DIR / "copilot_to_codex_template.md"
CODEX_TO_COPILOT_TEMPLATE = TEMPLATE_DIR / "codex_to_copilot_template.md"


def generate_timestamp() -> str:
    """Generate ISO 8601 timestamp."""
    return datetime.utcnow().isoformat() + "Z"


def load_template(template_name: str) -> str:
    """Load template content from file."""
    template_map = {
        "copilot_to_codex": COPILOT_TO_CODEX_TEMPLATE,
        "codex_to_copilot": CODEX_TO_COPILOT_TEMPLATE
    }

    template_path = template_map.get(template_name)
    if not template_path or not template_path.exists():
        print(f"❌ Template not found: {template_name}")
        print(f"   Expected at: {template_path}")
        sys.exit(1)

    with open(template_path) as f:
        return f.read()


def substitute_variables(template: str, variables: Dict[str, str]) -> str:
    """Substitute variables in template."""
    result = template

    for key, value in variables.items():
        placeholder = f"{{{key}}}"
        result = result.replace(placeholder, value)

    return result


def generate_copilot_to_codex_comment(
    phase: str,
    plan_file: str,
    status: str = "Complete",
    deliverables: List[str] = None,
    metrics: Dict[str, str] = None,
    review_focus: str = "",
    validation_items: List[str] = None,
    next_action: str = "",
    handoff_id: str = ""
) -> str:
    """Generate Copilot → Codex hand-off comment."""

    # Load template
    template = load_template("copilot_to_codex")

    # Build deliverables list
    deliverables_str = ""
    if deliverables:
        for d in deliverables:
            deliverables_str += f"- {d}\n"
    else:
        deliverables_str = "- (No deliverables specified)"

    # Build metrics table
    metrics_str = ""
    if metrics:
        metrics_str = "| Metric | Value | Target | Status |\n"
        metrics_str += "|--------|-------|--------|--------|\n"
        for key, value in metrics.items():
            parts = value.split("|")
            if len(parts) == 3:
                metrics_str += f"| {key} | {parts[0]} | {parts[1]} | {parts[2]} |\n"
    else:
        metrics_str = "(No metrics provided)"

    # Build validation checklist
    validation_str = ""
    if validation_items:
        for item in validation_items:
            validation_str += f"- [ ] {item}\n"
    else:
        validation_str = "- [ ] Review deliverables"

    # Build variables dict
    variables = {
        "phase_name": phase,
        "plan_file": plan_file,
        "status": status,
        "completion_timestamp": generate_timestamp(),
        "deliverables_list": deliverables_str,
        "metrics_table": metrics_str,
        "primary_review_focus": review_focus or "Review deliverables and validate approach",
        "validation_item_1": validation_items[0] if validation_items and len(validation_items) > 0 else "Verify deliverables complete",
        "validation_item_2": validation_items[1] if validation_items and len(validation_items) > 1 else "Validate approach",
        "validation_item_3": validation_items[2] if validation_items and len(validation_items) > 2 else "Check quality",
        "next_action_description": next_action or "Review and provide feedback",
        "handoff_id": handoff_id or "HO-XXX",
        "timestamp": generate_timestamp()
    }

    # Substitute and return
    return substitute_variables(template, variables)


def generate_codex_to_copilot_comment(
    phase: str,
    decision: str,
    decision_explanation: str = "",
    next_phase: str = "",
    next_plan: str = "",
    strengths: List[str] = None,
    improvements: List[str] = None,
    issues: List[str] = None,
    handoff_id: str = ""
) -> str:
    """Generate Codex → Copilot hand-off response."""

    # Load template
    template = load_template("codex_to_copilot")

    # Map decision to status
    decision_map = {
        "approve": "✅ APPROVE",
        "approve_with_conditions": "⚠️ APPROVE with Conditions",
        "request_changes": "❌ REQUEST CHANGES"
    }
    decision_status = decision_map.get(decision, decision)

    # Build lists
    strengths_str = ""
    if strengths:
        for s in strengths:
            strengths_str += f"- {s}\n"
    else:
        strengths_str = "- Deliverables complete\n"

    improvements_str = ""
    if improvements:
        for i in improvements:
            improvements_str += f"- {i}\n"
    else:
        improvements_str = "- None identified"

    issues_str = ""
    if issues:
        for issue in issues:
            issues_str += f"- {issue}\n"
    else:
        issues_str = "- None identified ✅"

    # Build variables dict
    variables = {
        "phase_name": phase,
        "review_type": f"{phase} Validation",
        "review_timestamp": generate_timestamp(),
        "overall_status": decision_status,
        "validation_summary": "Review complete. See findings below.",
        "strengths_list": strengths_str,
        "improvements_list": improvements_str,
        "issues_list": issues_str,
        "decision_status": decision_status,
        "decision_explanation": decision_explanation or "Deliverables meet requirements.",
        "next_phase_name": next_phase or "Next Phase",
        "next_plan_file": next_plan or "Next plan file",
        "instructions_for_copilot": f"Proceed with {next_phase}" if next_phase else "Proceed to next phase",
        "handoff_id": handoff_id or "HO-XXX",
        "response_time": "30 minutes",
        "timestamp": generate_timestamp()
    }

    # Substitute and return
    return substitute_variables(template, variables)


def main():
    parser = argparse.ArgumentParser(description="Generate hand-off comments from templates")
    parser.add_argument("--template", required=True, choices=["copilot_to_codex", "codex_to_copilot"],
                       help="Template to use")
    parser.add_argument("--phase", required=True, help="Phase name (e.g., 'Pre-commit 3-4')")
    parser.add_argument("--plan", help="Plan file path")
    parser.add_argument("--status", default="Complete", help="Status (default: Complete)")
    parser.add_argument("--deliverables", nargs="+", help="List of deliverables")
    parser.add_argument("--metrics", nargs="+", help="Metrics in format key=value|target|status")
    parser.add_argument("--review-focus", help="Primary review focus")
    parser.add_argument("--validation-items", nargs="+", help="Validation checklist items")
    parser.add_argument("--next-action", help="Next action description")
    parser.add_argument("--decision", choices=["approve", "approve_with_conditions", "request_changes"],
                       help="Decision (for codex_to_copilot)")
    parser.add_argument("--decision-explanation", help="Explanation for decision")
    parser.add_argument("--next-phase", help="Next phase name")
    parser.add_argument("--next-plan", help="Next plan file")
    parser.add_argument("--strengths", nargs="+", help="List of strengths")
    parser.add_argument("--improvements", nargs="+", help="List of improvements")
    parser.add_argument("--issues", nargs="+", help="List of issues")
    parser.add_argument("--handoff-id", help="Hand-off ID (e.g., HO-002)")
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    # Generate comment based on template
    comment = ""

    if args.template == "copilot_to_codex":
        # Parse metrics if provided
        metrics_dict = {}
        if args.metrics:
            for m in args.metrics:
                if "=" in m:
                    key, value = m.split("=", 1)
                    metrics_dict[key] = value

        comment = generate_copilot_to_codex_comment(
            phase=args.phase,
            plan_file=args.plan or "",
            status=args.status,
            deliverables=args.deliverables,
            metrics=metrics_dict,
            review_focus=args.review_focus,
            validation_items=args.validation_items,
            next_action=args.next_action,
            handoff_id=args.handoff_id or ""
        )

    elif args.template == "codex_to_copilot":
        if not args.decision:
            print("❌ --decision required for codex_to_copilot template")
            sys.exit(1)

        comment = generate_codex_to_copilot_comment(
            phase=args.phase,
            decision=args.decision,
            decision_explanation=args.decision_explanation,
            next_phase=args.next_phase,
            next_plan=args.next_plan,
            strengths=args.strengths,
            improvements=args.improvements,
            issues=args.issues,
            handoff_id=args.handoff_id or ""
        )

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(comment)
        print(f"✅ Generated comment: {output_path}")
    else:
        print(comment)


if __name__ == "__main__":
    main()
