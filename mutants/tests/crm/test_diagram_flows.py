"""
Test Diagram Flows

Test module for diagram flows.
"""

from __future__ import annotations

import pytest

from codex_crm.diagram import intake_to_mermaid


def test_intake_to_mermaid_generates_flow() -> None:
    diagram = intake_to_mermaid("Intake", ["Triage", "Vendor", "Closure"])
    assert "flowchart TD" in diagram, "Condition must be true"
    assert "Start: Intake" in diagram, "Condition must be true"
    assert diagram.strip().endswith("Z[Close]"), "Condition must be true"


@pytest.mark.parametrize("steps", [[], ["   "]])
def test_intake_to_mermaid_requires_steps(steps: list[str]) -> None:
    with pytest.raises(ValueError):
        intake_to_mermaid("Intake", steps)
