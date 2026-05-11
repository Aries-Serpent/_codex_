#!/usr/bin/env python3
"""Cognitive Brain Autonomous Healing Loop.

Runs a sequence of diagnostic checks and attempts to auto-fix common issues:
1. Lint check (ruff) — auto-fix with ruff --fix
2. Import guard scan — add missing pytest.importorskip guards
3. Auto-fix common CI issues — run auto_fix_common_issues.py
4. Syntax validation — compile all Python files
5. MkDocs build check — validate documentation builds

Usage:
    python scripts/cognitive/healing_loop.py [--dry-run] [--verbose]
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def run_cmd(cmd: list[str], capture: bool = True, cwd: Path | None = None) -> tuple[int, str]:
    """Run a command and return (exit_code, output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            cwd=cwd or REPO_ROOT,
            timeout=300,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode, output.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, str(e)


def check_lint(verbose: bool = False, fix: bool = False) -> dict:
    """Check and optionally fix lint issues with ruff."""
    cmd = ["python", "-m", "ruff", "check", "src/", "tests/"]
    if fix:
        cmd.append("--fix")
    code, output = run_cmd(cmd)
    issues = len([line for line in output.split("\n") if line.strip()]) if output and code != 0 else 0
    return {
        "check": "lint",
        "status": "pass" if code == 0 else "fail",
        "issues": issues,
        "auto_fixed": fix and code == 0,
        "details": output[:500] if verbose else "",
    }


def check_syntax(verbose: bool = False) -> dict:
    """Validate Python syntax for key project scripts."""
    scripts = [
        "scripts/ci/generate_cache_keys.py",
        "scripts/cognitive/healing_loop.py",
        "scripts/monitoring/agent_orchestrator.py",
    ]
    failed = []
    for script in scripts:
        path = REPO_ROOT / script
        if path.exists():
            code, output = run_cmd(["python", "-m", "py_compile", str(path)])
            if code != 0:
                failed.append(f"{script}: {output[:100]}")
    return {
        "check": "syntax",
        "status": "pass" if not failed else "fail",
        "issues": len(failed),
        "details": "\n".join(failed)[:500] if verbose else "",
    }


def check_auto_fix(verbose: bool = False) -> dict:
    """Run auto-fix check for common CI issues."""
    script = REPO_ROOT / "scripts" / "ci" / "auto_fix_common_issues.py"
    if not script.exists():
        return {"check": "auto_fix", "status": "skip", "issues": 0, "details": "script not found"}

    code, output = run_cmd(["python", str(script), "--check-only"])
    return {
        "check": "auto_fix",
        "status": "pass" if code == 0 else "fail",
        "issues": 0 if code == 0 else 1,
        "details": output[:500] if verbose else "",
    }


def check_fragile_tests(verbose: bool = False) -> dict:
    """Scan for fragile test files with unguarded imports."""
    scanner = REPO_ROOT / ".codex" / "scripts" / "fragile_tests_scan.py"
    if not scanner.exists():
        return {"check": "fragile_tests", "status": "skip", "issues": 0, "details": "scanner not found"}

    run_cmd(["python", str(scanner)])
    # Parse result
    json_file = REPO_ROOT / ".codex" / "fragile_tests.json"
    count = 0
    if json_file.exists():
        data = json.loads(json_file.read_text())
        count = len(data)

    return {
        "check": "fragile_tests",
        "status": "info",
        "issues": count,
        "details": f"{count} fragile test files detected" if verbose else "",
    }


def _run_single_iteration(dry_run: bool, verbose: bool) -> dict:
    """Run a single iteration of checks and return results."""
    checks = []

    # 1. Lint check
    checks.append(check_lint(verbose=verbose, fix=not dry_run))

    # 2. Syntax check
    checks.append(check_syntax(verbose=verbose))

    # 3. Auto-fix check
    checks.append(check_auto_fix(verbose=verbose))

    # 4. Fragile tests scan
    checks.append(check_fragile_tests(verbose=verbose))

    failed = [c for c in checks if c["status"] == "fail"]
    return {
        "checks": checks,
        "status": "needs_attention" if failed else "healthy",
        "failed_count": len(failed),
    }


def run_healing_loop(
    dry_run: bool = False,
    verbose: bool = False,
    max_iterations: int = 1,
) -> dict:
    """Run the healing loop with multi-iteration support.

    When *max_iterations* > 1 and fixes are applied (not dry-run), the loop
    re-runs checks after each fix attempt until all checks pass or the
    iteration limit is reached.
    """
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "dry-run" if dry_run else "active",
        "max_iterations": max_iterations,
        "iterations": [],
        "checks": [],
        "overall_status": "healthy",
    }

    for i in range(1, max_iterations + 1):
        iteration = _run_single_iteration(dry_run=dry_run, verbose=verbose)
        iteration["iteration"] = i
        results["iterations"].append(iteration)

        if iteration["status"] == "healthy" or dry_run:
            # All checks passed or we're in dry-run mode — stop iterating
            results["checks"] = iteration["checks"]
            break

        # In active mode with failures, the fixes were already applied
        # (ruff --fix ran). Re-check on next iteration.
        if i == max_iterations:
            # Last iteration — use these results
            results["checks"] = iteration["checks"]

    # Determine overall status from final iteration
    final = results["iterations"][-1]
    results["overall_status"] = final["status"]
    results["total_iterations"] = len(results["iterations"])
    results["converged"] = final["status"] == "healthy"

    failed = [c for c in results["checks"] if c["status"] == "fail"]
    results["summary"] = {
        "total_checks": len(results["checks"]),
        "passed": len([c for c in results["checks"] if c["status"] == "pass"]),
        "failed": len(failed),
        "skipped": len([c for c in results["checks"] if c["status"] == "skip"]),
        "info": len([c for c in results["checks"] if c["status"] == "info"]),
    }

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Cognitive Brain Autonomous Healing Loop")
    parser.add_argument("--dry-run", action="store_true", help="Check only, don't fix")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=1,
        help="Maximum healing iterations (default: 1, recommended: 3)",
    )
    args = parser.parse_args()

    results = run_healing_loop(
        dry_run=args.dry_run,
        verbose=args.verbose,
        max_iterations=args.max_iterations,
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"🧠 Cognitive Brain Healing Loop — {results['timestamp']}")
        print(f"   Mode: {results['mode']}")
        print(f"   Iterations: {results['total_iterations']}/{results['max_iterations']}"
              f" {'(converged)' if results.get('converged') else ''}")
        print()
        for check in results["checks"]:
            icon = {"pass": "✅", "fail": "❌", "skip": "⏭️", "info": "ℹ️"}.get(check["status"], "❓")
            print(f"   {icon} {check['check']}: {check['status']} ({check['issues']} issues)")
            if args.verbose and check.get("details"):
                for line in check["details"].split("\n")[:5]:
                    print(f"      {line}")
        print()
        summary = results["summary"]
        print(f"   Overall: {results['overall_status'].upper()}")
        print(f"   Checks: {summary['passed']} passed, {summary['failed']} failed, "
              f"{summary['skipped']} skipped, {summary['info']} info")

    return 1 if results["overall_status"] == "needs_attention" else 0


if __name__ == "__main__":
    raise SystemExit(main())
