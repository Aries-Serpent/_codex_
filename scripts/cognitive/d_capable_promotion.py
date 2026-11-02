"""
D_CAPABLE Per-Agent Promotion Pipeline (Priority 1 — AAIS 85→90+).

Evaluates every E-model agent in AGENT_REGISTRY.yaml against the D_CAPABLE
promotion criteria and emits a machine-readable promotion report.

Promotion criteria (all must pass):
  1. autonomy_model == "E"           — not already promoted
  2. maturity in {production, stable} — proven track record
  3. violations_30d == 0              — no recent policy violations
  4. handoff_protocol in {structured, soft} — can participate in handoffs
  5. len(capability_tags) >= 3        — adequately tagged for routing
  6. description populated            — human-readable identity

Usage:
    python scripts/cognitive/d_capable_promotion.py [--promote] [--registry PATH]

    --promote   Apply promotions to AGENT_REGISTRY.yaml (default: dry-run).
    --registry  Override path to AGENT_REGISTRY.yaml.

Exit codes:
    0  Report emitted (or promotions applied) successfully.
    1  Error reading registry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_DEFAULT = Path(".github/agents/AGENT_REGISTRY.yaml")

ELIGIBLE_MATURITIES = {"production", "stable"}
ELIGIBLE_HANDOFFS = {"structured", "soft"}
MIN_TAGS = 3


def load_registry(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("::error::pyyaml not installed — run: pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    try:
        return yaml.safe_load(path.read_text())
    except Exception as exc:  # noqa: BLE001
        print(f"::error::Failed to load {path}: {exc}", file=sys.stderr)
        sys.exit(1)


def save_registry(data: dict, path: Path) -> None:
    validate_registry(data)
    try:
        import yaml
    except ImportError:
        print("::error::pyyaml not installed", file=sys.stderr)
        sys.exit(1)
    original = path.read_text(encoding="utf-8")
    validate_registry(yaml.safe_load(original))
    root = yaml.compose(original)
    if not isinstance(root, yaml.MappingNode):
        raise ValueError("registry must be a mapping")
    replacements = []
    for key, node in root.value:
        if key.value == "agents":
            if not isinstance(node, yaml.SequenceNode):
                raise ValueError("agents must be a sequence")
            if len(node.value) != len(data.get("agents", [])):
                raise ValueError("minimal-diff writer cannot add or remove agents")
            for old_agent, new_agent in zip(node.value, data["agents"], strict=True):
                if not isinstance(old_agent, yaml.MappingNode):
                    raise ValueError("agent must be a mapping")
                for field, value in old_agent.value:
                    if field.value == "autonomy_model":
                        replacements.append((value, new_agent["autonomy_model"]))
        elif key.value == "last_updated":
            replacements.append((node, data["last_updated"]))
    updated = original
    for node, value in sorted(
        replacements, key=lambda pair: pair[0].start_mark.index, reverse=True
    ):
        if not isinstance(node, yaml.ScalarNode) or not isinstance(value, str):
            raise ValueError("minimal-diff writer requires string scalars")
        if not value or any(
            char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_:.-"
            for char in value
        ):
            raise ValueError("unsupported registry scalar")
        quote = node.style if node.style in ("'", '"') else ""
        if not quote and not isinstance(yaml.safe_load(value), str):
            quote = "'"
        updated = (
            updated[: node.start_mark.index]
            + quote
            + value
            + quote
            + updated[node.end_mark.index :]
        )
    if "last_updated" in data and not any(key.value == "last_updated" for key, _ in root.value):
        insertion = root.start_mark.index
        timestamp = {"last_updated": data["last_updated"]}
        if root.flow_style:
            insertion = next(
                token.end_mark.index
                for token in yaml.scan(original)
                if isinstance(token, yaml.FlowMappingStartToken)
                and token.start_mark.index >= insertion
            )
            text = yaml.safe_dump(timestamp, default_flow_style=True).strip()[1:-1] + ", "
        else:
            text = yaml.safe_dump(timestamp, sort_keys=False).replace(
                "\n", "\n" + " " * root.start_mark.column
            )
        updated = updated[:insertion] + text + updated[insertion:]
    if yaml.safe_load(updated) != data:
        raise ValueError("minimal-diff writer refuses unrelated registry changes")
    path.write_text(updated, encoding="utf-8")


def validate_registry(data: dict) -> None:
    """Require a structurally valid registry with unambiguous agent identities."""
    if not isinstance(data, dict):
        raise ValueError("registry must be a mapping")
    agents = data.get("agents")
    if not isinstance(agents, list):
        raise ValueError("registry agents must be a list of mappings")
    seen: set[str] = set()
    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError("registry agents must be a list of mappings")
        identity = agent.get("id")
        if (
            not isinstance(identity, str)
            or not 3 <= len(identity) <= 64
            or re.fullmatch(r"[a-z][a-z0-9-]*[a-z0-9]", identity) is None
        ):
            raise ValueError("agent ID must satisfy the canonical kebab-case identity schema")
        if identity in seen:
            raise ValueError("agent IDs must be unique")
        seen.add(identity)


def evaluate_agent(agent: dict) -> tuple[bool, list[str]]:
    """Return (eligible, reasons_blocked)."""
    blocked: list[str] = []

    if agent.get("autonomy_model") != "E":
        blocked.append(f"already at {agent.get('autonomy_model', '?')}")
    if agent.get("maturity") not in ELIGIBLE_MATURITIES:
        blocked.append(f"maturity={agent.get('maturity', 'unknown')} (need production/stable)")
    if type(agent.get("violations_30d")) is not int or agent["violations_30d"] != 0:
        blocked.append("violations_30d must be an explicitly measured zero")
    if agent.get("handoff_protocol") not in ELIGIBLE_HANDOFFS:
        blocked.append(
            f"handoff_protocol={agent.get('handoff_protocol', 'none')} (need structured/soft)"
        )
    tags = agent.get("capability_tags")
    if (
        not isinstance(tags, list)
        or not all(isinstance(tag, str) and tag.strip() for tag in tags)
        or len(set(tags)) < MIN_TAGS
    ):
        blocked.append(f"need ≥{MIN_TAGS} distinct populated capability_tags")
    description = agent.get("description")
    if not isinstance(description, str) or not description.strip():
        blocked.append("description is empty")

    return len(blocked) == 0, blocked


def run(registry_path: Path, apply: bool) -> int:
    data = load_registry(registry_path)
    try:
        validate_registry(data)
    except ValueError as exc:
        print(f"::error::Invalid registry: {exc}", file=sys.stderr)
        return 1
    agents: list[dict] = data["agents"]

    eligible: list[dict] = []
    ineligible: list[tuple[dict, list[str]]] = []

    for agent in agents:
        ok, reasons = evaluate_agent(agent)
        if ok:
            eligible.append(agent)
        else:
            ineligible.append((agent, reasons))

    already_d = [a for a in agents if a.get("autonomy_model") == "D_CAPABLE"]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registry_path": str(registry_path),
        "total_agents": len(agents),
        "already_d_capable": len(already_d),
        "newly_eligible": len(eligible),
        "ineligible": len(ineligible),
        "apply_promotions": apply,
        "eligible_agents": [
            {"id": a["id"], "name": a.get("name", a["id"]), "maturity": a.get("maturity")}
            for a in eligible
        ],
        "ineligible_agents": [
            {
                "id": a["id"],
                "name": a.get("name", a["id"]),
                "blocked_reasons": reasons,
            }
            for a, reasons in ineligible[:20]  # cap to avoid huge output
        ],
    }

    # Print human-readable summary
    print("=" * 60)
    print("D_CAPABLE Promotion Pipeline Report")
    print("=" * 60)
    print(f"Registry   : {registry_path}")
    print(f"Total agents: {len(agents)}")
    print(f"Already D_CAPABLE: {len(already_d)}")
    print(f"Newly eligible   : {len(eligible)}")
    print()

    if eligible:
        print("✅ Agents eligible for D_CAPABLE promotion:")
        for a in eligible:
            print(f"  • {a['id']} ({a.get('maturity', '?')})")
    else:
        print("ℹ️  No agents are currently eligible for promotion.")
        print("   Most common blockers: handoff_protocol=none, insufficient tags.")

    # Apply promotions if requested
    if apply and eligible:
        for agent in eligible:
            agent["autonomy_model"] = "D_CAPABLE"
        data["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        save_registry(data, registry_path)
        print(f"\n✅ Applied {len(eligible)} promotion(s) to {registry_path}")
        report["promotions_applied"] = [a["id"] for a in eligible]
    elif apply:
        print("\nℹ️  No promotions to apply.")
    else:
        print("\n(Dry-run mode — pass --promote to apply changes)")

    # Write JSON report
    report_path = Path(".codex/promotion_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\nReport written to {report_path}")

    # GitHub Actions output
    import os

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"eligible_count={len(eligible)}\n")
            f.write(f"already_d_count={len(already_d)}\n")
            f.write(f"applied={'true' if (apply and eligible) else 'false'}\n")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="D_CAPABLE per-agent promotion pipeline")
    parser.add_argument("--promote", action="store_true", help="Apply promotions to registry")
    parser.add_argument(
        "--registry",
        type=Path,
        default=REGISTRY_DEFAULT,
        help="Path to AGENT_REGISTRY.yaml",
    )
    args = parser.parse_args()
    sys.exit(run(args.registry, args.promote))


if __name__ == "__main__":
    main()
