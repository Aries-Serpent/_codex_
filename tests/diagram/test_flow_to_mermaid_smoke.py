from __future__ import annotations

from codex.diagram.flows import flow_to_mermaid


def test_mermaid_smoke():
    edges = [
        ("Intake", "create", "Triage"),
        ("Triage", "route", "Assignment"),
        ("Assignment", "SLA", "Work"),
    ]
    mmd = flow_to_mermaid("CRM Flow", edges)
    assert "graph TD" in mmd
    assert "Intake" in mmd and "Triage" in mmd and "Assignment" in mmd and "Work" in mmd
