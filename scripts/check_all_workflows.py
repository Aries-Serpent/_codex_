#!/usr/bin/env python3
"""Check status of all workflows mentioned in the problem statement."""

import json
import sys
from datetime import datetime, timezone

# Workflow IDs from problem statement
WORKFLOW_IDS = [
    21731916569,  # CodeQL - Code Quality / Analyze (go) (dynamic)
    21731917150,  # CodeQL / Analyze (javascript) (push)
    21731917179,  # CodeQL Chunked Analysis
    21731917130,  # Deploy Pages (MkDocs)
    21731917110,  # Unified Security Suite
    21731917163,  # Code Quality Analysis
    21731917139,  # Security Scanning Suite
    21731917109,  # Testing Suite
    21731917123,  # Comprehensive Tests with Caching
    21731917104,  # Rust-Python Hybrid Swarm CI/CD
    21731917115,  # Semgrep SAST
    21731916612,  # pages build and deployment
    21731917144,  # Documentation Link Checker
    21731917146,  # Security Scan
    21731918302,  # dynamic / submit-pypi
    21731917117,  # Auto-update Package Configs
    21731917157,  # Scan and Report GitHub Secrets and Variables
    21731917143,  # Wiki Assembly & Documentation
]

def main():
    """Check status of all workflows using gh CLI."""

    results = []
    in_progress = []
    queued = []
    failed = []
    success = []

    for wf_id in sorted(WORKFLOW_IDS):
        try:
            # Use gh api to get workflow run status
            cmd = f"gh api repos/Aries-Serpent/_codex_/actions/runs/{wf_id}"
            import subprocess
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                status = data.get('status')
                conclusion = data.get('conclusion')
                name = data.get('name')

                info = {
                    'id': wf_id,
                    'name': name,
                    'status': status,
                    'conclusion': conclusion,
                    'html_url': data.get('html_url'),
                }
                results.append(info)

                if status == 'in_progress':
                    in_progress.append(info)
                elif status == 'queued':
                    queued.append(info)
                elif status == 'completed':
                    if conclusion == 'success':
                        success.append(info)
                    elif conclusion in ['failure', 'cancelled']:
                        failed.append(info)
            else:
                print(f"Error fetching workflow {wf_id}: {result.stderr}", file=sys.stderr)

        except Exception as e:
            print(f"Exception fetching workflow {wf_id}: {e}", file=sys.stderr)

    # Print summary
    print("=" * 80)
    print(f"WORKFLOW STATUS REPORT - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 80)
    print(f"\nTotal workflows checked: {len(WORKFLOW_IDS)}")
    print(f"Successfully queried: {len(results)}")
    print(f"\n✅ Success: {len(success)}")
    print(f"🔄 In Progress: {len(in_progress)}")
    print(f"⏳ Queued: {len(queued)}")
    print(f"❌ Failed: {len(failed)}")

    if in_progress:
        print("\n" + "!" * 80)
        print("⚠️  WORKFLOWS STILL IN PROGRESS:")
        print("!" * 80)
        for wf in in_progress:
            print(f"\n  {wf['name']} (ID: {wf['id']})")
            print(f"    URL: {wf['html_url']}")

    if queued:
        print("\n" + "!" * 80)
        print("⚠️  WORKFLOWS QUEUED:")
        print("!" * 80)
        for wf in queued:
            print(f"\n  {wf['name']} (ID: {wf['id']})")
            print(f"    URL: {wf['html_url']}")

    if failed:
        print("\n" + "!" * 80)
        print("❌ WORKFLOWS FAILED:")
        print("!" * 80)
        for wf in failed:
            print(f"\n  {wf['name']} (ID: {wf['id']})")
            print(f"    Conclusion: {wf['conclusion']}")
            print(f"    URL: {wf['html_url']}")

    if not in_progress and not queued:
        print("\n" + "=" * 80)
        print("✅ ALL WORKFLOWS COMPLETE!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print(f"⏳ WAITING: {len(in_progress) + len(queued)} workflows still running")
        print("=" * 80)
        sys.exit(2)

if __name__ == "__main__":
    main()
