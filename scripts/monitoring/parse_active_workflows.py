#!/usr/bin/env python3
"""
Active Workflow Status Parser and Monitor
Parses the workflow status from PR comment and tracks completion.
"""

import re
from datetime import datetime, timezone

# Raw data from PR #3152 comment
WORKFLOW_DATA = """
Testing Suite / Core Tests (Python 3.12) (push) Failing after 4m
Rust-Python Hybrid Swarm CI/CD / Code Coverage (push) In progress - This check has started...
Unified Security Suite / Code Security Scan (push) In progress - This check has started...
Comprehensive Tests with Caching / Python 3.12 Tests (push) In progress - This check has started...
Rust-Python Hybrid Swarm CI/CD / Rust Benchmarks (push) In progress - This check has started...
Documentation Link Checker / check-links (push) In progress - This check has started...
CodeQL - Code Quality / Analyze (go) (dynamic) Successful in 1m
CodeQL / Analyze (javascript) (push) Successful in 1m
CodeQL - Code Quality / Analyze (javascript-typescript) (dynamic) Successful in 1m
CodeQL / Analyze (python) (push) Successful in 4m
CodeQL - Code Quality / Analyze (python) (dynamic) Successful in 5m
CodeQL Chunked Analysis / Analyze agents (push) Successful in 2m
CodeQL Chunked Analysis / Analyze core (push) Successful in 2m
CodeQL Chunked Analysis / Analyze ml (push) Successful in 2m
CodeQL Chunked Analysis / Analyze scripts (push) Successful in 2m
CodeQL Chunked Analysis / Analyze training (push) Successful in 2m
Testing Suite / Auth Tests (Python ${{ matrix.python-version }}) (push) Skipped
Rust-Python Hybrid Swarm CI/CD / Build Documentation (push) Successful in 22s
Documentation Suite / Build MkDocs Documentation (push) Successful in 56s
CI — Optimized with Caching / Cache Dependencies (push) Successful in 14s
Code Quality Analysis / Code Smell Detection (Observation Mode) (push) Successful in 22s
Security Scanning Suite / CodeQL Analysis (javascript) (push) Successful in 1m
Security Scanning Suite / CodeQL Analysis (python) (push) Successful in 6m
Unified Security Suite / Dependency Security Scan (push) Successful in 2m
Security Scanning Suite / Dependency Security Scan (push) Skipped
Documentation Suite / Deploy to GitHub Pages (push) Successful in 13s
Testing Suite / Determinism Tests (push) Skipped
CodeQL Chunked Analysis / Discover Chunks (push) Successful in 7s
Documentation Suite / Documentation Link Check (push) Skipped
Documentation Suite / Documentation Suite Summary (push) Successful in 2s
Wiki Assembly & Documentation / Generate Wiki Bundle (push) Successful in 20s
Testing Suite / Integration Tests (push) Skipped
CodeQL Chunked Analysis / Merge SARIF Results (push) Successful in 22s
Rust-Python Hybrid Swarm CI/CD / Python Integration Tests (push) Successful in 7m
Testing Suite / RAG Tests (Python ${{ matrix.python-version }}) (push) Skipped
Rust-Python Hybrid Swarm CI/CD / Rust Unit Tests (push) Successful in 56s
Security Scanning Suite / SBOM Generation (push) Skipped
Scan and Report GitHub Secrets and Variables / Scan Secrets and Variables (push) Successful in 20s
Security Scanning Suite / Secret Scanning (push) Skipped
Unified Security Suite / Secret Security Scan (push) Successful in 45s
Rust-Python Hybrid Swarm CI/CD / Security Audit (push) Successful in 20s
Unified Security Suite / Security Policy Check (push) Successful in 16s
Security Scanning Suite / Security Suite Summary (push) Successful in 3s
Semgrep SAST (SARIF Upload) / Semgrep SAST (push) Successful in 4m
CodeQL Chunked Analysis / Size Report (push) Successful in 6s
Testing Suite / Test Suite Summary (push) Successful in 4s
Workflow Documentation Link Validation / Validate Workflow Documentation Links (push) Successful in 24s
pages build and deployment / build (dynamic) Successful in 47s
pages build and deployment / deploy (dynamic) Successful in 8s
CI Health Monitor / health-check (push) Successful in 10s
pages build and deployment / report-build-status (dynamic) Successful in 3s
Security Scan / security-audit (push) Successful in 5m
dynamic / submit-pypi (dynamic) Successful in 1m
Auto-update Package Configs / update-configs (push) Successful in 23s
Validate Secrets Documentation / validate-secrets-docs (push) Successful in 10s
"""


def parse_workflows() -> tuple[list[dict], dict[str, int]]:
    """Parse workflow data and return structured information."""
    workflows = []
    status_counts = {
        'failing': 0,
        'in_progress': 0,
        'successful': 0,
        'skipped': 0,
    }

    for line in WORKFLOW_DATA.strip().split('\n'):
        if not line.strip():
            continue

        # Parse workflow name and status
        match_failing = re.search(r'(.+) Failing after (.+)', line)
        match_progress = re.search(r'(.+) In progress', line)
        match_success = re.search(r'(.+) Successful in (.+)', line)
        match_skipped = re.search(r'(.+) Skipped', line)

        if match_failing:
            workflow = {
                'name': match_failing.group(1).strip(),
                'status': 'FAILING',
                'duration': match_failing.group(2).strip(),
                'priority': 'CRITICAL',
            }
            status_counts['failing'] += 1
        elif match_progress:
            workflow = {
                'name': match_progress.group(1).strip(),
                'status': 'IN_PROGRESS',
                'duration': 'Running...',
                'priority': 'HIGH',
            }
            status_counts['in_progress'] += 1
        elif match_success:
            workflow = {
                'name': match_success.group(1).strip(),
                'status': 'SUCCESS',
                'duration': match_success.group(2).strip(),
                'priority': 'LOW',
            }
            status_counts['successful'] += 1
        elif match_skipped:
            workflow = {
                'name': match_skipped.group(1).strip(),
                'status': 'SKIPPED',
                'duration': 'N/A',
                'priority': 'LOW',
            }
            status_counts['skipped'] += 1
        else:
            continue

        workflows.append(workflow)

    return workflows, status_counts


def generate_monitoring_report():
    """Generate comprehensive monitoring report."""
    workflows, counts = parse_workflows()

    print("="*80)
    print("ACTIVE WORKFLOW MONITORING REPORT")
    print("="*80)
    print(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    print("Source: PR #3152 Comment #3848790670")
    print("="*80)

    print("\n📊 EXECUTIVE SUMMARY")
    print("-"*80)
    print(f"Total Workflows: {len(workflows)}")
    print(f"  ❌ FAILING:      {counts['failing']:2d} (CRITICAL - Requires immediate attention)")
    print(f"  ▶  IN PROGRESS:  {counts['in_progress']:2d} (Monitoring - Awaiting completion)")
    print(f"  ✅ SUCCESSFUL:   {counts['successful']:2d} (Complete - No action needed)")
    print(f"  ⊘  SKIPPED:      {counts['skipped']:2d} (Expected - Conditional execution)")

    print("\n🔴 CRITICAL - FAILING WORKFLOWS (Priority 1)")
    print("-"*80)
    failing = [w for w in workflows if w['status'] == 'FAILING']
    if failing:
        for w in failing:
            print(f"❌ {w['name']}")
            print(f"   Duration: {w['duration']}")
            print("   Action: INVESTIGATE AND FIX IMMEDIATELY")
    else:
        print("✓ No failing workflows")

    print("\n🟡 IN PROGRESS - AWAITING COMPLETION (Priority 2)")
    print("-"*80)
    in_progress = [w for w in workflows if w['status'] == 'IN_PROGRESS']
    if in_progress:
        for w in in_progress:
            print(f"▶  {w['name']}")
            print("   Status: Currently running...")
            print("   Action: Monitor until completion")
    else:
        print("✓ No workflows in progress")

    print("\n✅ SUCCESSFUL WORKFLOWS")
    print("-"*80)
    print(f"Count: {counts['successful']} workflows completed successfully")

    print("\n⊘ SKIPPED WORKFLOWS")
    print("-"*80)
    print(f"Count: {counts['skipped']} workflows skipped (conditional execution)")

    print("\n📋 REQUIRED ACTIONS")
    print("="*80)
    print(f"1. FIX {counts['failing']} FAILING WORKFLOW(S) - CRITICAL PRIORITY")
    print(f"2. MONITOR {counts['in_progress']} IN-PROGRESS WORKFLOW(S) - Wait for completion")
    print("3. VALIDATE all workflows complete successfully before applying fixes")
    print("="*80)

    return workflows, counts


def save_structured_report(workflows: list[dict], counts: dict[str, int]):
    """Save structured monitoring data."""
    import json
    from pathlib import Path

    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'source': 'PR #3152 Comment #3848790670',
        'summary': counts,
        'workflows': workflows,
        'critical_count': counts['failing'],
        'monitoring_count': counts['in_progress'],
        'requires_action': counts['failing'] > 0 or counts['in_progress'] > 0,
    }

    output_path = Path('.codex/active_workflow_status.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Structured data saved to: {output_path}")


if __name__ == '__main__':
    workflows, counts = generate_monitoring_report()
    save_structured_report(workflows, counts)
