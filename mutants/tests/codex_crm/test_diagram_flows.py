"""Tests for CRM flow diagram helpers."""

from __future__ import annotations

from dataclasses import dataclass

from codex_crm.diagram.flows import build_flow_edges


@dataclass
class _Step:
    label: str


def test_build_flow_edges_with_steps():
    edges, prev = build_flow_edges(["Qualification", _Step(label="Demo")])

    assert edges == [
        ("Start", "Qualification"),
        ("Qualification", "Demo"),
        ("Demo", "Close"),
    ]
    assert prev == "Close"


def test_build_flow_edges_without_steps():
    edges, prev = build_flow_edges([])

    assert edges == [("Start", "Close")]
    assert prev == "Close"


def test_build_flow_edges_from_mapping():
    edges, prev = build_flow_edges(
        [
            {"label": "Qualification"},
            {"name": "Proposal"},
        ]
    )

    assert edges == [
        ("Start", "Qualification"),
        ("Qualification", "Proposal"),
        ("Proposal", "Close"),
    ]
    assert prev == "Close"
