#!/usr/bin/env python3
"""Read-only promotion assessment; missing infrastructure evidence denies readiness."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.cognitive.d_capable_promotion import evaluate_agent, load_registry


def assess(registry: Path) -> dict:
    before = registry.read_bytes()
    data = load_registry(registry)
    agents = data.get("agents")
    if not isinstance(agents, list) or not all(isinstance(agent, dict) for agent in agents):
        raise ValueError("registry agents must be a list of mappings")
    results = []
    for agent in agents:
        eligible, blocked = evaluate_agent(agent)
        results.append({"id": agent.get("id"), "eligible": eligible, "blocked_reasons": blocked})
    if registry.read_bytes() != before:
        raise RuntimeError("registry changed during read-only assessment")
    # ADR C1/C2/C4 need schema, hosted activation and manifest provenance evidence.
    # A checkout or this per-agent evaluator alone cannot establish those facts.
    soft = sum(agent.get("enforcement_tier") == "SOFT" for agent in agents)
    grounded = sum(agent.get("enforcement_tier") == "GROUNDED" for agent in agents)
    return {
        "schema_version": 1,
        "registry_sha256": hashlib.sha256(before).hexdigest(),
        "registry_written": False,
        "promotion_authorized": False,
        "status": "unknown",
        "conditions": {
            "C1": {
                "status": "unknown",
                "reason": "registry JSON Schema validation not established",
            },
            "C2": {
                "status": "unknown",
                "reason": "two active Tier-1 hosted CI gates not established",
            },
            "C3": {"status": "pass" if soft <= 2 else "fail", "soft_agents": soft},
            "C4": {"status": "unknown", "reason": "manifest provenance/integrity not established"},
            "C5": {"status": "pass" if grounded >= 8 else "fail", "grounded_agents": grounded},
        },
        "agents": results,
        "approvals_required": [
            "Independent human promotion approval; assessment confers no authority"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.registry.resolve() or (
        args.output.exists() and args.output.samefile(args.registry)
    ):
        parser.error("output must not overwrite the registry")
    report = assess(args.registry)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 1 if report["status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
