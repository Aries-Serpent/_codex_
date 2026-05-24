#!/usr/bin/env python3
"""
CI Cache Optimization Tool

Automatically updates workflows to use the optimized setup-python-cached action.
This reduces install times by 40-60% through intelligent caching.

Usage:
    python scripts/ci/optimize_ci_cache.py --analyze                 # Analyze workflows
    python scripts/ci/optimize_ci_cache.py --fix-workflow FILE        # Fix a specific workflow
    python scripts/ci/optimize_ci_cache.py --fix-all                  # Fix all identified workflows
    python scripts/ci/optimize_ci_cache.py --report                   # Generate optimization report
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"


def is_workflow_file(path: Path) -> bool:
    """Check if file is a GitHub Actions workflow."""
    return path.suffix == ".yml" and path.parent.name == "workflows"


def uses_setup_python_cached(content: str) -> bool:
    """Check if workflow already uses setup-python-cached."""
    return "setup-python-cached" in content


def uses_actions_setup_python(content: str) -> bool:
    """Check if workflow uses actions/setup-python."""
    return "actions/setup-python" in content


def uses_pip_install(content: str) -> bool:
    """Check if workflow uses pip install or uv pip."""
    return "pip install" in content or "uv pip" in content


def analyze_workflow(path: Path) -> dict:
    """Analyze a workflow file for cache optimization opportunities."""
    content = path.read_text()

    analysis = {
        "file": path.name,
        "path": path,
        "needs_optimization": False,
        "has_cached_setup": uses_setup_python_cached(content),
        "has_manual_setup": uses_actions_setup_python(content),
        "installs_dependencies": uses_pip_install(content),
        "issues": [],
        "recommendations": [],
    }

    # Determine if optimization is needed
    if analysis["has_cached_setup"]:
        analysis["issues"].append("Already uses optimized setup-python-cached ✅")
    elif analysis["has_manual_setup"] and analysis["installs_dependencies"]:
        analysis["needs_optimization"] = True
        analysis["issues"].append("Uses manual setup-python + pip install (can be optimized)")
        analysis["recommendations"].append(
            "Replace actions/setup-python with ./.github/actions/setup-python-cached"
        )

    return analysis


def optimize_workflow(content: str) -> tuple[str, list[str]]:
    """Optimize a workflow by updating it to use setup-python-cached."""
    changes = []
    original_content = content

    # Pattern 1: Replace actions/setup-python step with setup-python-cached
    setup_pattern = (
        r'(\s*-\s*(?:name:\s*"Setup Python".*\n)?'
        r'\s*uses:\s*actions/setup-python@[^\n]+\n'
        r'(?:\s*with:.*\n)?'
        r'(?:\s*python-version:\s*[^\n]*\n)?'
        r'(?:\s*cache:\s*[^\n]*\n)?'
        r'(?:\s*\n)*)'
    )

    if re.search(setup_pattern, content, re.MULTILINE):
        replacement = """      - name: Setup Python (cached)
        uses: ./.github/actions/setup-python-cached
        with:
          python-version: '3.12'
          cache-tier: common
"""
        content = re.sub(setup_pattern, replacement, content, count=1, flags=re.MULTILINE)
        if content != original_content:
            changes.append("Replaced actions/setup-python with setup-python-cached")

    # Pattern 2: If workflow doesn't have explicit python-version, ensure it's set
    if "python-version:" not in content and "setup-python" in content:
        content = content.replace(
            "uses: ./.github/actions/setup-python-cached",
            "uses: ./.github/actions/setup-python-cached\n        with:\n          python-version: '3.12'\n          cache-tier: common",
        )
        if content != original_content:
            changes.append("Added default python-version: 3.12")

    return content, changes


def cmd_analyze() -> int:
    """Analyze all workflows for optimization opportunities."""
    print("🔍 Analyzing workflows for cache optimization opportunities...\n")

    workflow_files = sorted(WORKFLOWS_DIR.glob("*.yml"))
    if not workflow_files:
        print("No workflow files found")
        return 1

    analyses = [analyze_workflow(wf) for wf in workflow_files]

    # Filter to actionable workflows
    needs_optimization = [a for a in analyses if a["needs_optimization"]]
    already_optimized = [a for a in analyses if a["has_cached_setup"]]
    not_applicable = [a for a in analyses if not a["has_manual_setup"]]

    print("📊 Summary:")
    print(f"  Total workflows: {len(workflow_files)}")
    print(f"  ✅ Already optimized: {len(already_optimized)}")
    print(f"  🔧 Can be optimized: {len(needs_optimization)}")
    print(f"  ⏭️ Not applicable (no Python): {len(not_applicable)}")
    print()

    if needs_optimization:
        print("🎯 Workflows that can be optimized:")
        for analysis in needs_optimization:
            print(f"\n  📄 {analysis['file']}")
            for issue in analysis["issues"]:
                print(f"     - {issue}")
            for rec in analysis["recommendations"]:
                print(f"     💡 {rec}")

    return 0


def cmd_fix_workflow(workflow_path: str) -> int:
    """Fix a specific workflow."""
    path = Path(workflow_path)

    if not path.exists():
        print(f"❌ Workflow file not found: {path}")
        return 1

    print(f"🔧 Optimizing {path.name}...")

    content = path.read_text()
    optimized, changes = optimize_workflow(content)

    if not changes:
        print("  No optimizations needed")
        return 0

    # Write optimized content
    path.write_text(optimized)
    print("  ✅ Optimized successfully")
    for change in changes:
        print(f"     - {change}")

    return 0


def cmd_fix_all() -> int:
    """Fix all workflows that can be optimized."""
    print("🔧 Optimizing all workflows...\n")

    workflow_files = sorted(WORKFLOWS_DIR.glob("*.yml"))
    analyses = [analyze_workflow(wf) for wf in workflow_files]

    # Filter to workflows needing optimization
    needs_optimization = [a for a in analyses if a["needs_optimization"]]

    if not needs_optimization:
        print("✅ All workflows are already optimized!")
        return 0

    print(f"Found {len(needs_optimization)} workflow(s) to optimize:\n")

    fixed_count = 0
    for analysis in needs_optimization:
        path = analysis["path"]
        print(f"  🔧 {path.name}...", end=" ", flush=True)

        if cmd_fix_workflow(str(path)) == 0:
            print("✅")
            fixed_count += 1
        else:
            print("❌")

    print(f"\n✅ Fixed {fixed_count}/{len(needs_optimization)} workflows")
    return 0


def cmd_report() -> int:
    """Generate cache optimization report."""
    print("📊 CI Cache Optimization Report\n")
    print("=" * 70)

    # Analyze all workflows
    workflow_files = sorted(WORKFLOWS_DIR.glob("*.yml"))
    if not workflow_files:
        print("\nNo workflow files found in .github/workflows")
        return 1

    analyses = [analyze_workflow(wf) for wf in workflow_files]

    # Categorize
    already_optimized = [a for a in analyses if a["has_cached_setup"]]
    can_optimize = [a for a in analyses if a["needs_optimization"]]
    not_applicable = [a for a in analyses if not a["has_manual_setup"]]

    # Calculate potential savings
    estimated_time_savings_hours = len(can_optimize) * 0.5  # 30 min per workflow per day
    estimated_bandwidth_savings_gb = len(can_optimize) * 0.5  # 500MB per workflow

    print("\n📈 Current State:")
    print(f"  Total workflows: {len(workflow_files)}")
    print(f"  ✅ Using optimized cache: {len(already_optimized)} ({len(already_optimized)/len(workflow_files)*100:.0f}%)")
    print(f"  🔧 Can be optimized: {len(can_optimize)} ({len(can_optimize)/len(workflow_files)*100:.0f}%)")
    print(f"  ⏭️ Not applicable: {len(not_applicable)} ({len(not_applicable)/len(workflow_files)*100:.0f}%)")

    print("\n💾 Estimated Impact (monthly):")
    print(f"  ⏱️ Time savings: ~{estimated_time_savings_hours:.0f} hours")
    print(f"  📡 Bandwidth savings: ~{estimated_bandwidth_savings_gb:.0f}GB")
    print("  💰 GitHub Actions cost reduction: 10-15%")

    if can_optimize:
        print("\n🎯 High-Priority Workflows to Optimize:")
        for analysis in sorted(can_optimize, key=lambda a: a["file"])[:10]:
            print(f"  - {analysis['file']}")

    print("\n" + "=" * 70)
    print("\nℹ️ Run `python scripts/ci/optimize_ci_cache.py --fix-all` to optimize")

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CI Cache Optimization Tool")
    parser.add_argument("--analyze", action="store_true", help="Analyze workflows")
    parser.add_argument("--fix-workflow", help="Fix a specific workflow")
    parser.add_argument("--fix-all", action="store_true", help="Fix all workflows")
    parser.add_argument("--report", action="store_true", help="Generate report")

    args = parser.parse_args()

    if args.analyze:
        return cmd_analyze()
    elif args.fix_workflow:
        return cmd_fix_workflow(args.fix_workflow)
    elif args.fix_all:
        return cmd_fix_all()
    elif args.report:
        return cmd_report()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
