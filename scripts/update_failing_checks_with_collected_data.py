#!/usr/bin/env python3
"""
Update failing_checks.md with collected job and artifact data from PR3248_SESSION_CONTINUATION_SUMMARY.md

This script:
1. Parses the continuation summary for collected job data
2. Updates failing_checks.md replacing "⏳ Pending" with actual data
3. Adds summary statistics
"""

import re
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent
CONTINUATION_SUMMARY = REPO_ROOT / "PR3248_SESSION_CONTINUATION_SUMMARY.md"
FAILING_CHECKS = REPO_ROOT / "failing_checks.md"
ACCOUNTABILITY = REPO_ROOT / "ACCOUNTABILITY_REPORT_DRAFT.md"

def parse_job_data(summary_file: Path) -> dict[str, dict]:
    """
    Parse job data from continuation summary.

    Returns:
        Dict mapping run_id to job info
    """
    with open(summary_file) as f:
        content = f.read()

    job_data = {}

    # Pattern to extract run entries
    # Looking for: "1. **22026389814** - Pre-Merge Validation"
    pattern = r'\d+\.\s+\*\*(\d+)\*\*\s+-\s+(.+?)(?:\n\s+-\s+(.+?))?(?=\n\n|\d+\.\s+\*\*|\Z)'

    matches = re.findall(pattern, content, re.DOTALL)

    for run_id, workflow_name, job_info in matches:
        run_id = run_id.strip()
        workflow_name = workflow_name.strip()
        job_info = job_info.strip() if job_info else ""

        # Parse job information
        jobs = []
        if job_info:
            # Look for job patterns like "Job: 63643577648 (Final Pre-Merge Checks) - failure"
            job_pattern = r'Job:\s+(\d+)\s+\(([^)]+)\)\s+-\s+(\w+)'
            job_matches = re.findall(job_pattern, job_info)

            for job_id, job_name, job_status in job_matches:
                jobs.append({
                    'job_id': job_id,
                    'job_name': job_name,
                    'job_status': job_status,
                    'job_html_url': f'https://github.com/Aries-Serpent/_codex_/actions/runs/{run_id}/job/{job_id}'
                })

            # Also look for multi-job patterns like "4 jobs:"
            if 'jobs:' in job_info.lower():
                # Extract job details
                parts = job_info.split('\n')
                for part in parts:
                    if '(' in part and ')' in part:
                        # Try to extract job name and status
                        status_match = re.search(r'\(([^)]+)\)', part)
                        if status_match:
                            job_desc = status_match.group(1)
                            if 'cancelled' in part.lower():
                                status = 'cancelled'
                            elif 'failure' in part.lower() or 'failed' in part.lower():
                                status = 'failure'
                            elif 'success' in part.lower():
                                status = 'success'
                            elif 'skipped' in part.lower():
                                status = 'skipped'
                            else:
                                status = 'completed'

                            # Create placeholder job entry
                            jobs.append({
                                'job_id': f'{run_id}_{len(jobs)+1}',
                                'job_name': job_desc,
                                'job_status': status,
                                'job_html_url': f'https://github.com/Aries-Serpent/_codex_/actions/runs/{run_id}'
                            })

        job_data[run_id] = {
            'workflow_name': workflow_name,
            'jobs': jobs if jobs else [{'job_id': 'N/A', 'job_name': 'Data pending', 'job_status': 'pending', 'job_html_url': f'https://github.com/Aries-Serpent/_codex_/actions/runs/{run_id}'}]
        }

    return job_data

def parse_artifact_data(accountability_file: Path) -> dict[str, list[str]]:
    """
    Parse artifact data from accountability report.

    Returns:
        Dict mapping run_id to list of artifacts
    """
    try:
        with open(accountability_file) as f:
            content = f.read()

        # Look for artifact summary section
        artifact_section = re.search(r'## Artifact Summary.*?(?=##|\Z)', content, re.DOTALL)
        if artifact_section:
            # Extract artifact mentions
            # Pattern: diagnostic-report, code-quality-reports, etc.
            artifacts = re.findall(r'`([^`]+)`', artifact_section.group(0))
            return {'artifacts_found': artifacts}
    except Exception as e:
        print(f"Warning: Could not parse artifacts: {e}")

    return {}

def update_failing_checks(failing_checks_file: Path, job_data: dict, artifact_data: dict):
    """
    Update failing_checks.md with collected data.
    """
    with open(failing_checks_file) as f:
        content = f.read()

    # Track updates
    updates_made = 0

    # For each run_id in job_data, update the corresponding rows
    for run_id, run_info in job_data.items():
        # Find all occurrences of this run_id in the file
        pattern = rf'\|\s*{run_id}\s*\|([^|]*\|){{7}}[^|]*\|'
        matches = list(re.finditer(pattern, content))

        if matches:
            print(f"Found {len(matches)} rows for run {run_id}")

            for match in matches:
                old_row = match.group(0)

                # Get the first job for this run (or create a summary row)
                job = run_info['jobs'][0] if run_info['jobs'] else {}

                # Build new row
                new_row = (
                    f"| {run_id} | "
                    f"https://github.com/Aries-Serpent/_codex_/actions/runs/{run_id} | "
                    f"{run_info['workflow_name']} | "
                    f"failure | "  # Conclusion from original template
                    f"{job.get('job_id', 'N/A')} | "
                    f"{job.get('job_name', 'Multiple jobs - see run')} | "
                    f"{job.get('job_html_url', 'N/A')} | "
                    f"{job.get('job_status', 'completed')} | "
                    f"{'See artifacts section' if artifact_data else 'N/A'} |"
                )

                # Replace in content
                content = content.replace(old_row, new_row)
                updates_made += 1
                print(f"  Updated row for run {run_id}")

    # Write back
    with open(failing_checks_file, 'w') as f:
        f.write(content)

    print(f"\n✅ Updated {updates_made} rows in {failing_checks_file}")
    return updates_made

def main():
    print("🚀 Updating failing_checks.md with collected data...\n")

    # Step 1: Parse job data
    print("📊 Step 1: Parsing job data from continuation summary...")
    job_data = parse_job_data(CONTINUATION_SUMMARY)
    print(f"   Found data for {len(job_data)} workflow runs")

    # Step 2: Parse artifact data
    print("\n📦 Step 2: Parsing artifact data from accountability report...")
    artifact_data = parse_artifact_data(ACCOUNTABILITY)
    if artifact_data:
        print(f"   Found {len(artifact_data.get('artifacts_found', []))} artifact types")

    # Step 3: Update failing_checks.md
    print("\n✏️  Step 3: Updating failing_checks.md...")
    updates = update_failing_checks(FAILING_CHECKS, job_data, artifact_data)

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE: Updated {updates} rows")
    print(f"📁 Output: {FAILING_CHECKS}")
    print(f"{'='*60}")

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
