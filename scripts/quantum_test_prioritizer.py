#!/usr/bin/env python3
"""
Quantum-Inspired Test Prioritization Tool.

This script applies quantum physics principles from the _codex_ codebase
to prioritize test development based on coverage data.

Physics Principles Applied:
- Superposition: Untested code exists in multiple states
- Born Rule: Probability = |amplitude|²
- Free Energy: G = E - TS (lower = higher priority)
- Entropy: Measures uncertainty in code correctness

Usage:
    python scripts/quantum_test_prioritizer.py
    python scripts/quantum_test_prioritizer.py --target 0.70
    python scripts/quantum_test_prioritizer.py --json coverage.json

Author: Copilot Coding Agent
Generated: 2026-02-04
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ModuleQuantumState:
    """Quantum state representation of a source module."""

    path: str
    total_files: int
    tested_files: int
    lines_of_code: int = 0

    @property
    def coverage_ratio(self) -> float:
        """Coverage as ratio 0.0 to 1.0."""
        if self.total_files <= 0:
            return 0.0
        return min(1.0, self.tested_files / self.total_files)

    @property
    def entropy(self) -> float:
        """
        Shannon entropy of coverage distribution.

        Maximum entropy (1.0) at 50% coverage.
        Minimum entropy (0.0) at 0% or 100% coverage.
        """
        p = self.coverage_ratio
        if p <= 0 or p >= 1:
            return 0.0
        return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

    @property
    def amplitude(self) -> float:
        """
        Probability amplitude based on untested code.

        ψ = √(1 - coverage)
        """
        return math.sqrt(max(0, 1 - self.coverage_ratio))

    @property
    def born_probability(self) -> float:
        """
        Born rule: P = |ψ|²

        Probability of finding bugs in untested code.
        """
        return self.amplitude ** 2

    @property
    def energy(self) -> float:
        """
        Energy cost of testing this module.

        Proportional to complexity (file count, lines).
        """
        file_energy = math.log(self.total_files + 1)
        loc_energy = math.log(self.lines_of_code + 1) * 0.1 if self.lines_of_code > 0 else 0
        return file_energy + loc_energy

    @property
    def free_energy(self) -> float:
        """
        Gibbs free energy: G = E - TS

        Lower free energy = higher priority.
        """
        temperature = 1.0  # Urgency factor
        return self.energy - temperature * self.entropy

    def tests_needed(self, target: float = 0.70) -> int:
        """Calculate tests needed to reach target coverage."""
        target_tested = int(self.total_files * target)
        files_to_cover = max(0, target_tested - self.tested_files)
        avg_tests_per_file = 5
        return files_to_cover * avg_tests_per_file

    def priority_score(self) -> float:
        """
        Calculate priority score using quantum principles.

        Priority = Born_Probability / max(Free_Energy, 0.01)
        """
        return self.born_probability / max(0.01, self.free_energy)


def load_coverage_data(json_path: Path) -> list[ModuleQuantumState]:
    """Load coverage data from JSON file."""
    with open(json_path) as f:
        data = json.load(f)

    modules = []
    source_modules = data.get("source_modules", {})

    for path, info in source_modules.items():
        total = info.get("total_files", 0)
        tested = info.get("tested_files", 0)
        modules.append(
            ModuleQuantumState(
                path=path,
                total_files=total,
                tested_files=tested,
            )
        )

    return modules


def get_default_modules() -> list[ModuleQuantumState]:
    """Default module data from Phase 52 coverage analysis."""
    return [
        ModuleQuantumState("src/codex_plans", 2, 0),
        ModuleQuantumState("src/agent", 7, 4),
        ModuleQuantumState("src/mcp", 60, 10),
        ModuleQuantumState("src/services", 27, 3),
        ModuleQuantumState("src/codex_ml", 446, 47),
        ModuleQuantumState("src/codex", 259, 52),
        ModuleQuantumState("src/rag", 6, 2),
        ModuleQuantumState("src/cognitive_brain", 35, 12),
        ModuleQuantumState("src/security", 16, 6),
        ModuleQuantumState("src/training", 17, 8),
        ModuleQuantumState("src/tokenization", 7, 2),
        ModuleQuantumState("src/common", 9, 2),
        ModuleQuantumState("src/utils", 10, 3),
    ]


def quantum_prioritize(
    modules: list[ModuleQuantumState], target_coverage: float = 0.70
) -> list[dict[str, Any]]:
    """
    Prioritize modules using quantum principles.

    Returns sorted list with priority scores and test counts.
    """
    results = []

    for module in modules:
        results.append(
            {
                "path": module.path,
                "coverage": f"{module.coverage_ratio * 100:.1f}%",
                "entropy": module.entropy,
                "amplitude": module.amplitude,
                "born_prob": module.born_probability,
                "energy": module.energy,
                "free_energy": module.free_energy,
                "priority": module.priority_score(),
                "tests_needed": module.tests_needed(target_coverage),
            }
        )

    # Sort by priority (highest first)
    return sorted(results, key=lambda x: x["priority"], reverse=True)


def print_quantum_analysis(
    priorities: list[dict[str, Any]], target_coverage: float
) -> None:
    """Print quantum analysis results."""
    print("\n" + "=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("🔬 QUANTUM-INSPIRED TEST DEVELOPMENT PRIORITY ANALYSIS")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print(f"\nTarget Coverage: {target_coverage * 100:.0f}%")  # codeql[py/clear-text-logging-sensitive-data]
    print("\nPhysics Principles:")  # codeql[py/clear-text-logging-sensitive-data]
    print("  • Superposition: Untested code exists in multiple correctness states")  # codeql[py/clear-text-logging-sensitive-data]
    print("  • Born Rule: P = |ψ|² (probability of finding bugs)")  # codeql[py/clear-text-logging-sensitive-data]
    print("  • Free Energy: G = E - TS (lower = higher priority)")  # codeql[py/clear-text-logging-sensitive-data]
    print("  • Entropy: Maximum uncertainty at 50% coverage")  # codeql[py/clear-text-logging-sensitive-data]

    print("\n" + "-" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print(f"{'Module':<25} {'Cover':>7} {'Entropy':>8} {'Born P':>8} {'Priority':>10} {'Tests':>8}")  # codeql[py/clear-text-logging-sensitive-data]
    print("-" * 80)  # codeql[py/clear-text-logging-sensitive-data]

    total_tests = 0
    for item in priorities:
        print(
            f"{item['path']:<25} "
            f"{item['coverage']:>7} "
            f"{item['entropy']:>8.3f} "
            f"{item['born_prob']:>8.3f} "
            f"{item['priority']:>10.4f} "
            f"{item['tests_needed']:>8}"
        )
        total_tests += item["tests_needed"]

    print("-" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print(f"{'TOTAL':<25} {'':<7} {'':<8} {'':<8} {'':<10} {total_tests:>8}")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    # Priority tier breakdown
    print("📊 PRIORITY TIERS:")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]

    critical = [p for p in priorities if p["priority"] > 0.5]
    high = [p for p in priorities if 0.2 < p["priority"] <= 0.5]
    medium = [p for p in priorities if 0.1 < p["priority"] <= 0.2]
    low = [p for p in priorities if p["priority"] <= 0.1]

    if critical:
        print("🔴 CRITICAL (Priority > 0.5):")  # codeql[py/clear-text-logging-sensitive-data]
        for p in critical:
            print(f"   • {p['path']} - {p['tests_needed']} tests needed")  # codeql[py/clear-text-logging-sensitive-data]

    if high:
        print("🟡 HIGH (Priority 0.2-0.5):")  # codeql[py/clear-text-logging-sensitive-data]
        for p in high:
            print(f"   • {p['path']} - {p['tests_needed']} tests needed")  # codeql[py/clear-text-logging-sensitive-data]

    if medium:
        print("🟠 MEDIUM (Priority 0.1-0.2):")  # codeql[py/clear-text-logging-sensitive-data]
        for p in medium:
            print(f"   • {p['path']} - {p['tests_needed']} tests needed")  # codeql[py/clear-text-logging-sensitive-data]

    if low:
        print("🟢 LOW (Priority < 0.1):")  # codeql[py/clear-text-logging-sensitive-data]
        for p in low:
            print(f"   • {p['path']} - {p['tests_needed']} tests needed")  # codeql[py/clear-text-logging-sensitive-data]

    print()  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    print("📋 RECOMMENDED NEXT STEPS:")  # codeql[py/clear-text-logging-sensitive-data]
    print("=" * 80)  # codeql[py/clear-text-logging-sensitive-data]
    if critical:
        top = critical[0]
        print(f"\n1. Focus on {top['path']} (highest priority: {top['priority']:.4f})")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"   • Current coverage: {top['coverage']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"   • Tests needed: {top['tests_needed']}")  # codeql[py/clear-text-logging-sensitive-data]
        print(f"   • Shannon entropy: {top['entropy']:.3f}")  # codeql[py/clear-text-logging-sensitive-data]
    elif high:
        top = high[0]
        print(f"\n1. Focus on {top['path']} (highest priority: {top['priority']:.4f})")  # codeql[py/clear-text-logging-sensitive-data]
    else:
        print("\n1. All modules at acceptable priority levels")  # codeql[py/clear-text-logging-sensitive-data]

    print("\n2. Use patterns from .codex/docs/TEST_DEVELOPMENT_PATTERNS.md")  # codeql[py/clear-text-logging-sensitive-data]
    print("3. Apply thermodynamic scheduling for test execution order")  # codeql[py/clear-text-logging-sensitive-data]
    print()  # codeql[py/clear-text-logging-sensitive-data]


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Quantum-inspired test prioritization tool"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Path to coverage_analysis.json file",
    )
    parser.add_argument(
        "--target",
        type=float,
        default=0.70,
        help="Target coverage ratio (default: 0.70)",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Load modules
    if args.json and args.json.exists():
        modules = load_coverage_data(args.json)
    else:
        modules = get_default_modules()

    # Run quantum analysis
    priorities = quantum_prioritize(modules, args.target)

    # Output results
    if args.output == "json":
        print(json.dumps(priorities, indent=2))  # codeql[py/clear-text-logging-sensitive-data]
    else:
        print_quantum_analysis(priorities, args.target)

    return 0


if __name__ == "__main__":
    sys.exit(main())
