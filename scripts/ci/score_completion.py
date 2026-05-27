"""
scripts/ci/score_completion.py
-------------------------------
Compute the weighted platform-completion score from a YAML scores file.

Usage:
    python scripts/ci/score_completion.py --scores .codex/completion_scores.yaml
    python scripts/ci/score_completion.py --scores .codex/completion_scores.yaml --fail-below 75

Exit codes:
    0  Score is at or above --fail-below threshold (default: 0 = never fail)
    1  Score is below --fail-below threshold
    2  Input error (missing file, bad schema)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required.  Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# Domain weights (must sum to 100)
WEIGHTS: dict[str, int] = {
    "architecture": 8,
    "ml_lifecycle": 12,
    "agent_orchestration": 12,
    "rag_quality": 10,
    "security": 14,
    "cicd_health": 12,
    "test_maturity": 10,
    "observability": 6,
    "documentation": 6,
    "performance": 5,
    "release_integrity": 5,
}

DOMAIN_LABELS: dict[str, str] = {
    "architecture": "Platform Architecture & Boundaries",
    "ml_lifecycle": "Core ML Lifecycle (train/eval/serve)",
    "agent_orchestration": "Agent Orchestration & Cognitive Brain",
    "rag_quality": "RAG Quality & Freshness",
    "security": "Security Posture",
    "cicd_health": "CI/CD Health & Workflow Governance",
    "test_maturity": "Test System Maturity",
    "observability": "Observability & Operational Telemetry",
    "documentation": "Documentation & Developer Experience",
    "performance": "Performance & Cost Efficiency",
    "release_integrity": "Release / Versioning / Supply Chain",
}

READINESS_BANDS: list[tuple[float, str]] = [
    (90.0, "Production-complete"),
    (75.0, "Operational but needs hardening"),
    (60.0, "Functional but risk-heavy"),
    (0.0, "Foundation incomplete"),
]


def _readiness_band(score: float) -> str:
    for threshold, label in READINESS_BANDS:
        if score >= threshold:
            return label
    return "Foundation incomplete"


def _validate_scores(scores: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for key in WEIGHTS:
        if key not in scores:
            errors.append(f"Missing domain key: '{key}'")
            continue
        value = scores[key]
        if not isinstance(value, (int, float)):
            errors.append(f"Domain '{key}': score must be a number, got {type(value).__name__}")
        elif not (0 <= float(value) <= 5):
            errors.append(f"Domain '{key}': score {value} is outside [0, 5]")
    unknown = set(scores) - set(WEIGHTS)
    for key in sorted(unknown):
        errors.append(f"Unknown domain key: '{key}' (ignored in computation)")
    return errors


def _get_score(scores: dict[str, object], domain: str) -> float:
    """Return the numeric score for *domain*, defaulting to 0."""
    value = scores.get(domain, 0)
    return float(value) if isinstance(value, (int, float)) else 0.0


def _compute(scores: dict[str, object]) -> tuple[float, dict[str, float]]:
    total = 0.0
    details: dict[str, float] = {}
    for domain, weight in WEIGHTS.items():
        raw = _get_score(scores, domain)
        contribution = (raw / 5.0) * weight
        details[domain] = contribution
        total += contribution
    return total, details


def _format_report(scores: dict[str, object], total: float, details: dict[str, float]) -> str:
    lines: list[str] = [
        "",
        "╔══════════════════════════════════════════════════════════════╗",
        "║          Codex Platform — Completion Score Report           ║",
        "╚══════════════════════════════════════════════════════════════╝",
        "",
        f"  {'Domain':<45} {'Wt':>4}  {'Score':>6}  {'Contrib':>7}",
        f"  {'-'*45} {'----':>4}  {'------':>6}  {'-------':>7}",
    ]
    for domain, weight in WEIGHTS.items():
        raw = _get_score(scores, domain)
        label = DOMAIN_LABELS[domain]
        contrib = details[domain]
        lines.append(f"  {label:<45} {weight:>3}%  {raw:>5.1f}/5  {contrib:>6.1f}%")

    lines += [
        f"  {'-'*45} {'----':>4}  {'------':>6}  {'-------':>7}",
        f"  {'TOTAL':.<45} {'100%':>4}  {'':>6}  {total:>6.1f}%",
        "",
        f"  Readiness band : {_readiness_band(total)}",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute the weighted Codex platform completion score.",
    )
    parser.add_argument(
        "--scores",
        default=".codex/completion_scores.yaml",
        help="Path to YAML scores file (default: .codex/completion_scores.yaml)",
    )
    parser.add_argument(
        "--fail-below",
        type=float,
        default=0.0,
        metavar="THRESHOLD",
        help="Exit with code 1 if total score is below THRESHOLD (0–100).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of a human-readable table.",
    )
    args = parser.parse_args(argv)

    scores_path = Path(args.scores)
    if not scores_path.exists():
        print(f"ERROR: Scores file not found: {scores_path}", file=sys.stderr)
        return 2

    try:
        with scores_path.open(encoding="utf-8") as fh:
            scores = yaml.safe_load(fh)
    except Exception as exc:
        print(f"ERROR: Could not parse YAML: {exc}", file=sys.stderr)
        return 2

    if not isinstance(scores, dict):
        print("ERROR: Scores file must be a YAML mapping.", file=sys.stderr)
        return 2

    errors = _validate_scores(scores)
    unknown_errors = [e for e in errors if e.startswith("Unknown")]
    fatal_errors = [e for e in errors if not e.startswith("Unknown")]

    for err in unknown_errors:
        print(f"WARNING: {err}", file=sys.stderr)
    if fatal_errors:
        for err in fatal_errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 2

    total, details = _compute(scores)

    if args.json:
        import json

        output = {
            "total": round(total, 2),
            "band": _readiness_band(total),
            "domains": {
                d: {
                    "score": _get_score(scores, d),
                    "weight": WEIGHTS[d],
                    "contribution": round(details[d], 2),
                }
                for d in WEIGHTS
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print(_format_report(scores, total, details))

    if args.fail_below > 0 and total < args.fail_below:
        print(
            f"FAIL: score {total:.1f}% is below threshold {args.fail_below:.1f}%",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
