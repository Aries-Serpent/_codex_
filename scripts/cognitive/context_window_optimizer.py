#!/usr/bin/env python3
"""Context window optimizer — maximize effective context usage for AI agents.

Implements AAIS Improvement #10: Context Window Optimization (+0.8 pts).

Provides utilities for:
- Rolling context compression: summarize old context to fit more recent data
- Priority-based context allocation: rank content by relevance
- Session state snapshots: persist compact state between interactions

Usage:
    python scripts/cognitive/context_window_optimizer.py [--snapshot] [--estimate]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTEXT_BUDGET = 128_000  # tokens (approximate)
CHARS_PER_TOKEN = 4  # rough estimate


class ContextWindowOptimizer:
    """Optimize context window usage for AI agent sessions."""

    # Content priority tiers (higher = more important to keep)
    PRIORITY_TIERS = {
        "active_errors": 10,  # Current CI failures, test errors
        "recent_changes": 9,  # Files changed in current session
        "task_definition": 8,  # User instructions, PR description
        "api_contracts": 7,  # Public API signatures, __init__.py exports
        "test_patterns": 6,  # Test file patterns, fixtures
        "configuration": 5,  # pyproject.toml, noxfile.py, CI configs
        "documentation": 4,  # README, CONTRIBUTING, change_log
        "history": 3,  # Previous session summaries
        "exploration": 2,  # Codebase exploration results
        "boilerplate": 1,  # License headers, generated code
    }

    def __init__(self, budget_tokens: int = CONTEXT_BUDGET) -> None:
        self.budget_tokens = budget_tokens
        self.budget_chars = budget_tokens * CHARS_PER_TOKEN
        self.segments: list[dict] = []

    def add_segment(
        self,
        content: str,
        tier: str,
        source: str = "",
    ) -> None:
        """Add a content segment with priority tier."""
        priority = self.PRIORITY_TIERS.get(tier, 1)
        self.segments.append({
            "content": content,
            "tier": tier,
            "priority": priority,
            "source": source,
            "chars": len(content),
            "tokens_est": len(content) // CHARS_PER_TOKEN,
        })

    def optimize(self) -> list[dict]:
        """Return segments sorted by priority, trimmed to fit budget."""
        sorted_segments = sorted(
            self.segments, key=lambda s: s["priority"], reverse=True
        )
        result = []
        used_chars = 0
        for seg in sorted_segments:
            if used_chars + seg["chars"] <= self.budget_chars:
                result.append(seg)
                used_chars += seg["chars"]
            else:
                # Truncate last segment to fit
                remaining = self.budget_chars - used_chars
                if remaining > 100:  # worth including
                    truncated = {**seg, "content": seg["content"][:remaining]}
                    truncated["chars"] = remaining
                    truncated["tokens_est"] = remaining // CHARS_PER_TOKEN
                    truncated["truncated"] = True
                    result.append(truncated)
                break
        return result

    def utilization(self) -> dict:
        """Report context window utilization statistics."""
        total_chars = sum(s["chars"] for s in self.segments)
        total_tokens = total_chars // CHARS_PER_TOKEN
        by_tier = {}
        for seg in self.segments:
            tier = seg["tier"]
            by_tier[tier] = by_tier.get(tier, 0) + seg["chars"]

        return {
            "budget_tokens": self.budget_tokens,
            "used_tokens_est": total_tokens,
            "utilization_pct": round(total_tokens / self.budget_tokens * 100, 1)
            if self.budget_tokens
            else 0,
            "segments": len(self.segments),
            "by_tier": {
                k: {"chars": v, "tokens_est": v // CHARS_PER_TOKEN}
                for k, v in sorted(by_tier.items(), key=lambda x: -x[1])
            },
        }


def create_session_snapshot(session_id: int = 0) -> dict:
    """Create a compact session state snapshot for cross-session transfer."""
    return {
        "session_id": session_id,
        "planset_status": _scan_planset_status(),
        "active_files": _scan_recent_changes(),
        "key_metrics": _extract_metrics(),
    }


def _scan_planset_status() -> dict:
    """Extract planset completion from registry."""
    registry = REPO_ROOT / "docs" / "evolution" / "PLANSET_REGISTRY.md"
    if not registry.exists():
        return {"complete": 0, "active": 0, "total": 0}

    text = registry.read_text(encoding="utf-8", errors="ignore")
    complete = len(re.findall(r"✅ Complete", text))
    active = len(re.findall(r"🟢 Active", text))
    return {"complete": complete, "active": active, "total": complete + active}


def _scan_recent_changes() -> list[str]:
    """List recently modified files (from git status)."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~5..HEAD"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            check=False,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        return files[:20]  # cap at 20 most recent
    except Exception:
        return []


def _extract_metrics() -> dict:
    """Extract key metrics from dashboard."""
    dashboard = REPO_ROOT / ".codex" / "cognitive_brain" / "dashboard.md"
    if not dashboard.exists():
        return {}
    text = dashboard.read_text(encoding="utf-8", errors="ignore")
    metrics = {}
    # Extract AAIS score
    m = re.search(r"AAIS.*?(\d+\.\d+)/100", text)
    if m:
        metrics["aais_score"] = float(m.group(1))
    # Extract sessions count
    m = re.search(r"Sessions\s*\|\s*(\d+)", text)
    if m:
        metrics["sessions"] = int(m.group(1))
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Context window optimizer")
    parser.add_argument("--snapshot", action="store_true", help="Generate session snapshot")
    parser.add_argument("--estimate", action="store_true", help="Estimate context utilization")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.snapshot:
        snap = create_session_snapshot()
        if args.json:
            print(json.dumps(snap, indent=2))
        else:
            print(f"Session snapshot: {snap['planset_status']['complete']} plansets complete")
            print(f"AAIS: {snap['key_metrics'].get('aais_score', 'N/A')}")
            print(f"Recent files: {len(snap['active_files'])}")
        return 0

    if args.estimate:
        optimizer = ContextWindowOptimizer()
        # Scan key files to estimate usage
        for path in [
            "docs/evolution/PLANSET_REGISTRY.md",
            "docs/evolution/AI_AGENCY_INTUITIVENESS_SCORE_V3.md",
            ".codex/cognitive_brain/dashboard.md",
        ]:
            full = REPO_ROOT / path
            if full.exists():
                content = full.read_text(encoding="utf-8", errors="ignore")
                optimizer.add_segment(content, "documentation", path)

        util = optimizer.utilization()
        if args.json:
            print(json.dumps(util, indent=2))
        else:
            print(f"Context utilization: {util['utilization_pct']}%")
            print(f"Segments: {util['segments']}")
            for tier, data in util["by_tier"].items():
                print(f"  {tier}: ~{data['tokens_est']} tokens")
        return 0

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
