#!/usr/bin/env python3
"""
Analyze PR #2449 commits to extract objectives and build trace matrix.
"""
import subprocess
import json
import csv
import sys
import shlex
from pathlib import Path


def run_git(cmd):
    """Run git command safely without shell=True to prevent command injection."""
    # Split command string into list for safe execution
    cmd_list = shlex.split(cmd)
    result = subprocess.run(
        cmd_list, capture_output=True, text=True, shell=False, cwd="/home/runner/work/_codex_/_codex_"
    )
    return result.stdout.strip()


# Get a sample of recent commits (last 100 to keep it manageable)
print("Fetching commit details...", file=sys.stderr)
commits_output = run_git("git log --format='%H|||%s|||%b|||%an|||%ad' main..0D_base_ -100")

commits_list = []
for entry in commits_output.split("\n"):
    if "|||" in entry:
        parts = entry.split("|||", 4)
        if len(parts) >= 4:
            sha, subject, body, author, date = (
                parts[0],
                parts[1],
                parts[2] if len(parts) > 2 else "",
                parts[3] if len(parts) > 3 else "",
                parts[4] if len(parts) > 4 else "",
            )
            commits_list.append(
                {"sha": sha[:8], "message": subject, "body": body, "author": author, "date": date}
            )

print(f"Analyzed {len(commits_list)} commits", file=sys.stderr)

# Build objectives trace matrix
objectives_matrix = []

for commit in commits_list:
    msg = commit["message"].lower()
    body = commit["body"].lower()
    full_text = f"{msg} {body}"

    # Parse for objectives
    objectives = []
    evidence_found = "no"
    evidence_notes = ""

    # Look for docs objectives
    if any(kw in full_text for kw in ["docs", "documentation", "capability", "readme"]):
        objectives.append("docs")
        evidence_notes += "docs keyword found; "

    # Look for test objectives
    if any(kw in full_text for kw in ["test", "pytest", "coverage", "unittest"]):
        objectives.append("test")
        evidence_notes += "test keyword found; "

    # Look for feature/code objectives
    if any(kw in full_text for kw in ["add", "implement", "feature", "enhance", "upgrade"]):
        objectives.append("feature")
        evidence_notes += "feature keyword found; "

    # Look for bug fix objectives
    if any(kw in full_text for kw in ["fix", "bug", "issue", "error", "correct"]):
        objectives.append("bugfix")
        evidence_notes += "bugfix keyword found; "

    # Look for audit/scoring objectives
    if any(
        kw in full_text for kw in ["audit", "scoring", "coverage_map", "token_similarity", "v1.4"]
    ):
        objectives.append("audit")
        evidence_notes += "audit keyword found; "

    # Get files changed in this commit
    files_changed = run_git(f"git diff-tree --no-commit-id --name-only -r {commit['sha']}")
    files_list = files_changed.split("\n") if files_changed else []

    # Determine if evidence exists
    has_docs = any("docs/" in f or ".md" in f for f in files_list)
    has_tests = any("test" in f.lower() for f in files_list)
    has_code = any(f.endswith(".py") and "test" not in f.lower() for f in files_list)

    if objectives:
        if "docs" in objectives and has_docs:
            evidence_found = "yes"
        elif "test" in objectives and has_tests:
            evidence_found = "yes"
        elif (
            "feature" in objectives or "bugfix" in objectives or "audit" in objectives
        ) and has_code:
            evidence_found = "yes"
        elif has_docs or has_tests or has_code:
            evidence_found = "partial"

    objectives_matrix.append(
        {
            "commit_sha": commit["sha"],
            "objective_summary": ", ".join(objectives) if objectives else "maintenance",
            "files_changed": len(files_list),
            "evidence_found": evidence_found,
            "evidence_notes": evidence_notes.strip(),
            "message": commit["message"][:80],
        }
    )

# Save as CSV
output_dir = Path("/home/runner/work/_codex_/_codex_/.github/audit_artifacts_output")
output_dir.mkdir(exist_ok=True, parents=True)

csv_path = output_dir / "objectives_trace_matrix.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "commit_sha",
            "objective_summary",
            "files_changed",
            "evidence_found",
            "evidence_notes",
            "message",
        ],
    )
    writer.writeheader()
    writer.writerows(objectives_matrix)

print(f"Wrote {len(objectives_matrix)} rows to {csv_path}", file=sys.stderr)

# Also save as JSON for programmatic access
json_path = output_dir / "pr_commits_with_files.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(
        {
            "pr_number": 2449,
            "total_commits_analyzed": len(commits_list),
            "commits": commits_list[:50],  # Limit for size
            "objectives_summary": objectives_matrix,
        },
        f,
        indent=2,
    )

print(f"Wrote commit analysis to {json_path}", file=sys.stderr)

# Generate summary stats
stats = {
    "total_commits": len(commits_list),
    "with_evidence": sum(1 for o in objectives_matrix if o["evidence_found"] == "yes"),
    "partial_evidence": sum(1 for o in objectives_matrix if o["evidence_found"] == "partial"),
    "no_evidence": sum(1 for o in objectives_matrix if o["evidence_found"] == "no"),
    "objective_types": {},
}

for obj in objectives_matrix:
    for obj_type in obj["objective_summary"].split(", "):
        stats["objective_types"][obj_type] = stats["objective_types"].get(obj_type, 0) + 1

print(json.dumps(stats, indent=2))
