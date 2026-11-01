#!/usr/bin/env python3
"""Read-only promotion assessment; missing infrastructure evidence denies readiness."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import jsonschema

from scripts.ci.generate_manifest import verify_integrity
from scripts.cognitive.d_capable_promotion import evaluate_agent, load_registry

_ENTRY_SCHEMA = Path(__file__).resolve().parents[2] / "configs/schemas/agent_spec.schema.json"


def assess(registry: Path, *, manifest: Path | None = None) -> dict:
    before = registry.read_bytes()
    data = load_registry(registry)
    if not isinstance(data, dict):
        raise ValueError("registry must be a mapping")
    agents = data.get("agents")
    if not isinstance(agents, list) or not all(isinstance(agent, dict) for agent in agents):
        raise ValueError("registry agents must be a list of mappings")
    schema_bytes = _ENTRY_SCHEMA.read_bytes()
    validator = jsonschema.Draft7Validator(json.loads(schema_bytes))
    errors = []
    if not agents:
        errors.append("registry agents must not be empty")
    ids = []
    results = []
    for index, agent in enumerate(agents):
        entry_errors = list(validator.iter_errors(agent))
        errors.extend(f"agents[{index}]: {error.message}" for error in entry_errors)
        if isinstance(agent.get("id"), str):
            ids.append(agent["id"])
        if entry_errors:
            eligible, blocked = False, ["agent entry failed canonical schema validation"]
        else:
            try:
                eligible, blocked = evaluate_agent(agent)
            except (TypeError, ValueError):
                eligible, blocked = False, ["malformed promotion evidence"]
        results.append({"id": agent.get("id"), "eligible": eligible, "blocked_reasons": blocked})
    if len(ids) != len(set(ids)):
        errors.append("agent IDs must be unique")
    manifest_result = {"status": "unknown", "reason": "manifest input not supplied"}
    if manifest is not None:
        try:
            manifest_bytes = manifest.read_bytes()
            if not isinstance(json.loads(manifest_bytes), dict):
                raise ValueError("manifest must be a mapping")
            matched = verify_integrity(manifest)
            if manifest.read_bytes() != manifest_bytes:
                raise RuntimeError("manifest changed during read-only assessment")
            manifest_result = {
                "status": "pass" if matched else "fail",
                "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "reason": "local canonical integrity hash matches" if matched else "hash mismatch",
                "provenance": "unverified; a local hash is not hosted provenance",
            }
        except (OSError, ValueError, AttributeError) as exc:
            manifest_result = {
                "status": "fail",
                "reason": f"invalid manifest: {type(exc).__name__}",
            }
    if registry.read_bytes() != before:
        raise RuntimeError("registry changed during read-only assessment")
    # Local schema/hash checks cannot establish hosted activation or approval.
    soft = sum(agent.get("enforcement_tier") == "SOFT" for agent in agents)
    grounded = sum(agent.get("enforcement_tier") == "GROUNDED" for agent in agents)
    unknown_tiers = sum(
        agent.get("enforcement_tier") not in ("SOFT", "PARTIAL", "GROUNDED") for agent in agents
    )
    conditions: dict[str, dict] = {
        "C1": {
            "status": "fail" if errors else "pass",
            "schema_sha256": hashlib.sha256(schema_bytes).hexdigest(),
            "errors": errors,
        },
        "C2": {
            "status": "unknown",
            "reason": "two active Tier-1 hosted CI gates not established",
        },
        "C3": {
            "status": "fail" if soft > 2 else "unknown" if unknown_tiers else "pass",
            "soft_agents": soft,
            "unknown_tiers": unknown_tiers,
        },
        "C4": manifest_result,
        "C5": {
            "status": "pass" if grounded >= 8 else "unknown" if unknown_tiers else "fail",
            "grounded_agents": grounded,
            "unknown_tiers": unknown_tiers,
        },
    }
    return {
        "schema_version": 1,
        "registry_sha256": hashlib.sha256(before).hexdigest(),
        "registry_written": False,
        "promotion_authorized": False,
        "status": "fail" if any(c["status"] == "fail" for c in conditions.values()) else "unknown",
        "conditions": conditions,
        "agents": results,
        "approvals_required": [
            "Independent human promotion approval; assessment confers no authority"
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, help="Optional local manifest integrity evidence")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for source in (args.registry, args.manifest, _ENTRY_SCHEMA):
        if source is not None and (
            args.output.resolve() == source.resolve()
            or (args.output.exists() and source.exists() and args.output.samefile(source))
        ):
            parser.error("output must not overwrite an evidence input")
    report = assess(args.registry, manifest=args.manifest)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 1 if report["status"] != "pass" else 0


if __name__ == "__main__":
    raise SystemExit(main())
