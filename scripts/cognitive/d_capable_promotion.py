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
import sys
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_DEFAULT = Path(".github/agents/AGENT_REGISTRY.yaml")

ELIGIBLE_MATURITIES = {"production", "stable"}
ELIGIBLE_HANDOFFS = {"structured", "soft"}
MIN_TAGS = 3


def load_registry(path: Path) -> dict:
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        print("::error::pyyaml not installed — run: pip install pyyaml", file=sys.stderr)
        sys.exit(1)
    try:
        return yaml.safe_load(path.read_text())
    except Exception as exc:  # noqa: BLE001
        print(f"::error::Failed to load {path}: {exc}", file=sys.stderr)
        sys.exit(1)


def save_registry(data: dict, path: Path) -> None:
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        print("::error::pyyaml not installed", file=sys.stderr)
        sys.exit(1)
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False))


def evaluate_agent(agent: dict) -> tuple[bool, list[str]]:
    """Return (eligible, reasons_blocked)."""
    blocked: list[str] = []

    if agent.get("autonomy_model") != "E":
        blocked.append(f"already at {agent.get('autonomy_model', '?')}")
    if agent.get("maturity") not in ELIGIBLE_MATURITIES:
        blocked.append(f"maturity={agent.get('maturity', 'unknown')} (need production/stable)")
    if (agent.get("violations_30d") or 0) > 0:
        blocked.append(f"violations_30d={agent['violations_30d']}")
    if agent.get("handoff_protocol") not in ELIGIBLE_HANDOFFS:
        blocked.append(
            f"handoff_protocol={agent.get('handoff_protocol', 'none')} (need structured/soft)"
        )
    tags = agent.get("capability_tags") or []
    if len(tags) < MIN_TAGS:
        blocked.append(f"only {len(tags)} capability_tags (need ≥{MIN_TAGS})")
    if not (agent.get("description") or "").strip():
        blocked.append("description is empty")

    return len(blocked) == 0, blocked


def run(registry_path: Path, apply: bool) -> int:
    data = load_registry(registry_path)
    agents: list[dict] = data.get("agents", [])

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
        for agent in agents:
            if any(e["id"] == agent["id"] for e in eligible):
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
