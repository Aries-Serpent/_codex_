#!/usr/bin/env python3
"""
Cost Estimator for GitHub Actions workflows.

Calculates estimated Actions-minute consumption and GHCR data-transfer cost
for a job, then classifies it into a cost tier that drives the cost gate.

Usage:
    python scripts/ci/cost_estimator.py \
        --runner ubuntu-latest \
        --timeout 30 \
        --matrix-count 2 \
        --pushes-to-ghcr \
        --workflow "Build & Push Preview Image"

Exit codes:
    0  — GREEN  (auto-approved)
    1  — YELLOW (warn, auto-proceed after 5 min window)
    2  — RED    (blocked until stakeholder approves in PR)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Optional


# ── GitHub Team + Copilot Pro Plus budget constants ──────────────────────────
MONTHLY_MINUTES_BUDGET = 3_000          # Linux equivalent minutes/month
MINUTES_REMAINING_WARN_THRESHOLD = 500  # warn when <500 min left

# Minute multipliers per runner type (relative to ubuntu-latest 2-core = 1×)
# Source: https://docs.github.com/en/billing/concepts/product-billing/github-actions
RUNNER_MULTIPLIERS: dict[str, float] = {
    "ubuntu-latest":       1.0,
    "ubuntu-latest-m":     2.0,   # 4-core medium runner
    "ubuntu-latest-l":     4.0,   # 8-core large runner
    "ubuntu-latest-xl":    8.0,   # 16-core XL runner
    "windows-latest":      2.0,
    "macos-latest":        10.0,
    "macos-latest-xl":     10.0,
    "self-hosted":         0.0,   # no billed minutes
    "self-hosted-linux":   0.0,
}

# Approximate GHCR data-transfer cost (USD per GB pushed beyond free tier)
GHCR_TRANSFER_COST_PER_GB_USD = 0.0   # free for public repos on Team plan
# Note: within 10 GB/month free transfer; beyond that billed at GitHub rates.
# For a private repo on Team plan, first 10 GB/month outbound transfer is free.

# Cost tier thresholds (effective linux-equivalent minutes per trigger)
TIER_GREEN_MAX  = 30   # <30 effective min → auto-approve
TIER_YELLOW_MAX = 90   # 30–90 → warn + 5-min window
# >90 effective min → RED: blocked until stakeholder checkbox ticked


@dataclass
class CostEstimate:
    workflow_name:    str
    runner:           str
    timeout_minutes:  int
    matrix_count:     int
    pushes_to_ghcr:   bool
    multiplier:       float = field(init=False)
    effective_minutes: float = field(init=False)
    tier:             str = field(init=False)   # GREEN | YELLOW | RED
    tier_emoji:       str = field(init=False)
    reason:           str = field(init=False)
    proposal_lines:   list[str] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.multiplier = RUNNER_MULTIPLIERS.get(
            self.runner.lower().replace(" ", "-"), 1.0
        )
        self.effective_minutes = (
            self.timeout_minutes * self.multiplier * self.matrix_count
        )
        self._classify()
        self._build_proposal()

    def _classify(self) -> None:
        reasons: list[str] = []
        if self.pushes_to_ghcr:
            reasons.append("GHCR image push (data-transfer cost)")
        if self.multiplier > 1.0:
            reasons.append(
                f"Non-standard runner `{self.runner}` "
                f"({self.multiplier:.0f}× minute rate)"
            )
        if self.matrix_count > 1:
            reasons.append(f"Matrix: {self.matrix_count} parallel jobs")
        if self.effective_minutes > TIER_YELLOW_MAX:
            reasons.append(
                f"Effective minutes: {self.effective_minutes:.0f} "
                f"(>{TIER_YELLOW_MAX} = high consumption)"
            )

        if self.effective_minutes < TIER_GREEN_MAX and not self.pushes_to_ghcr:
            self.tier = "GREEN"
            self.tier_emoji = "✅"
        elif self.effective_minutes <= TIER_YELLOW_MAX and not self.pushes_to_ghcr:
            self.tier = "YELLOW"
            self.tier_emoji = "⚠️"
        else:
            self.tier = "RED"
            self.tier_emoji = "🔴"

        self.reason = "; ".join(reasons) if reasons else "Low-cost job"

    def _build_proposal(self) -> None:
        self.proposal_lines = [
            f"## {self.tier_emoji} Cost Proposal — `{self.workflow_name}`",
            "",
            "| Parameter | Value |",
            "|-----------|-------|",
            f"| Runner | `{self.runner}` ({self.multiplier:.0f}× Linux rate) |",
            f"| Timeout | {self.timeout_minutes} min |",
            f"| Matrix jobs | {self.matrix_count} |",
            f"| Effective minutes | **{self.effective_minutes:.0f}** |",
            f"| GHCR push | {'Yes ⚠️' if self.pushes_to_ghcr else 'No'} |",
            f"| **Cost tier** | **{self.tier}** |",
            f"| Reason | {self.reason} |",
            "",
            "**GitHub Team budget:** 3,000 Linux-equivalent minutes/month",
            "",
        ]

        if self.tier == "GREEN":
            self.proposal_lines += [
                "✅ **Auto-approved** — within low-cost threshold.",
                "No stakeholder action required.",
            ]
        elif self.tier == "YELLOW":
            self.proposal_lines += [
                "⚠️ **Warning** — moderate cost.",
                "Job will proceed automatically in 5 minutes.",
                "To block, close the PR or cancel the run before then.",
            ]
        else:  # RED
            self.proposal_lines += [
                "🔴 **BLOCKED** — high cost job requires stakeholder approval.",
                "",
                "**To approve, tick the checkbox in the PR description:**",
                "> `- [ ] 💰 Cost Proposal Approved — stakeholder sign-off`",
                "  → Change to: `- [x] 💰 Cost Proposal Approved`",
                "",
                "Alternatively, trigger manually via `workflow_dispatch` to bypass the PR gate.",
                "",
                "_Budget context: GitHub Team (3,000 min/mo) + Copilot Pro Plus_",
            ]

    def to_dict(self) -> dict:
        return {
            "workflow_name":     self.workflow_name,
            "runner":            self.runner,
            "timeout_minutes":   self.timeout_minutes,
            "matrix_count":      self.matrix_count,
            "pushes_to_ghcr":    self.pushes_to_ghcr,
            "multiplier":        self.multiplier,
            "effective_minutes": round(self.effective_minutes, 1),
            "tier":              self.tier,
            "reason":            self.reason,
        }

    @property
    def proposal_markdown(self) -> str:
        return "\n".join(self.proposal_lines)

    @property
    def exit_code(self) -> int:
        return {"GREEN": 0, "YELLOW": 1, "RED": 2}[self.tier]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Estimate Actions cost for a workflow job")
    p.add_argument("--runner",        default="ubuntu-latest",
                   help="Runner type (e.g. ubuntu-latest, ubuntu-latest-m, macos-latest)")
    p.add_argument("--timeout",       type=int, default=30,
                   help="Job timeout-minutes")
    p.add_argument("--matrix-count",  type=int, default=1,
                   help="Number of parallel matrix jobs")
    p.add_argument("--pushes-to-ghcr", action="store_true",
                   help="Job pushes an image to GHCR")
    p.add_argument("--workflow",      default="Unknown workflow",
                   help="Human-readable workflow name")
    p.add_argument("--json",          action="store_true",
                   help="Output JSON instead of markdown")
    p.add_argument("--github-output", action="store_true",
                   help="Write tier to GITHUB_OUTPUT env file")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    estimate = CostEstimate(
        workflow_name=args.workflow,
        runner=args.runner,
        timeout_minutes=args.timeout,
        matrix_count=args.matrix_count,
        pushes_to_ghcr=args.pushes_to_ghcr,
    )

    if args.json:
        print(json.dumps(estimate.to_dict(), indent=2))
    else:
        print(estimate.proposal_markdown)

    # Write tier to GITHUB_OUTPUT if requested (for use in Actions workflows)
    if args.github_output:
        github_output = os.environ.get("GITHUB_OUTPUT", "")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"tier={estimate.tier}\n")
                f.write(f"effective_minutes={estimate.effective_minutes:.0f}\n")
                f.write(f"reason={estimate.reason}\n")
        else:
            print(f"::set-output name=tier::{estimate.tier}", file=sys.stderr)

    sys.exit(estimate.exit_code)


if __name__ == "__main__":
    main()
