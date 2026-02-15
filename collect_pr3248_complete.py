#!/usr/bin/env python3
"""
Comprehensive data collection for PR #3248 commits.
Collects check runs, workflow runs, and artifacts for 81 specific commits.
"""

import json
import subprocess
import sys
from typing import Dict, List, Any
from datetime import datetime

OWNER = "Aries-Serpent"
REPO = "_codex_"
PR_NUMBER = 3248

COMMITS = [
    "dd7b63779e9c7a2da8806a5b902778973eaf42bf", "ec3d17b6eab2fdc170b7196429d643304ed12f4d",
    "d9731c9c5af4d31dbad2f0bf66220d20c19d04d4", "2a7e546fc698aba6a6131ed232a8b8e544211e4e",
    "0d96f686543854a0647cba99e81aacbcc17524b5", "c36c47f24c70ca3912f11ecde51bb1552b6ebed5",
    "2378dc6a96df8465dbc8a4972b4fe8b6817ba2cc", "a59dffd35d0875574db2fc806a687d84d6d8b99a",
    "483be0dea87f9b9097ef9c0d91a6efb36abc087b", "7267398869bcb253981fd10b300b0d6865825141",
    "9cc97df9e37aaef873b3271a0acee92f48af8234", "43d7f59bc2e4a26b635633e29dc6d6c0da2379e4",
    "77e29f0023896057bf406e2a59f382fbf3c80ccd", "701e1ca36718b69f4b5d990558c06e58bb389aa6",
    "1d5fccd38c5c9d7ba0c29e3435add0a754853102", "78c75ca6e435b4dfdc38ea1bd6f8237f25d6525a",
    "6593115b8e8ab13063fc0a48dded8a30fab1d755", "209ea2c216e4b1eb3b1b2c06bad541b6303071b0",
    "f5212c6f651bece0657d182147ef4992f98f5891", "27212d4a493f2504878302a5315dcea0d853005c",
    "195947d6b23b739770b05fc24e228d872b2f1ed6", "e1a9a7cfbc50280bdfbf4f820b039c6237b37652",
    "c643d565ce8a2f375d82805ed48f80900fc93c85", "0d8be400d4f7a045efa70ffd91cc3d72c1416960",
    "3a73d44792ce22f4ee2619336b00fb53707b650c", "5ca9ec6d9dfbd81e537315eb7954ca1cc943d17d",
    "a77242d5cccd607731857f1f215a6abc5d4074a5", "2937fe5861bfa5e654c5c58c149895fea98095de",
    "89a32c56aec18457ee286ab9d27c9440c94e44a6", "ff937ef0f925d563d5b09ede40f22feb0b78f747",
    "6762050e4fbf7209097e188e859930027be3a072", "7666a701f0ce4715cbe2eedd5950a53e900a7ec1",
    "a37117c697b028c2bbc13f5f0519763acc3b7167", "ce6917ac948ae6c432952a4a0df7ad0e33788d07",
    "5b44dd5d8d78b9e07858f10aabbccfdd08eb3ffe", "27daa3272aa9b13cd13c298a9fbd0392ccc39bf9",
    "a80e33fbe77a7f756d0e91bda7289b4385e7b26e", "43428572c5a75d8688a92ea61d4cdf00e6ab7d37",
    "721be8fbe6d1db02f1727a0189f1a6dd12d04c49", "0db24b5fb6fdf5e789b48f5c9cefa0632c09e48f",
    "3ab4364be487a92c9b38469bb3bcdb2efb2d8401", "c57b5da02554aad84cd445e974679aff6625564e",
    "9ad5bc92bf7afac9d87836937dafc647a4d1df07", "9b194adb18bae4c8230930151ee2ceb178e1afa3",
    "dee711cde2e767ea8815fcc11bfa53bef84a84f7", "faf0ac3ed93c5930f26e06c79921ccae6f28a934",
    "07bf832d6ce42191797282f6f7d75f0810623e43", "4985bf797565b7e44421c70984299cbc42188b4c",
    "0640f7d1bd8f690ade3b5332efa2ed6822aab451", "c18eafd9a2941f491d5c903427894273e055ada0",
    "7f0379dfac8e4ccdfc386fb898b9ed1192aca83a", "28106e64c63a38aa70b39df39d8edf1bcdeafb35",
    "38c64fa215fd81714acf881aa9d0a6f1269445ef", "07713e4bfceb88294e1c7b674c0c47f69ca4fb8e",
    "c067b49b388e4eb6f72edf5e035907c237c68338", "9a83b8c6c2ca64d95bed272ed9793e5dae4bdd4b",
    "f58b5c1d93f9abf4bf8df033a346a68a817414a5", "f2ef77258695f77985cdf2071d7b3f4b1f22ee29",
    "c3c07d1c032d02ef42250cf960d187164fe79bf2", "d088994633604a2bb8ba972d4d0ff7bf28a34fc7",
    "b3dbe1081be9c95f9e31446f4c0c20dea394500d", "f45e5cca3cd62dc799eaa12ad01adc326962e736",
    "9db17bd601cbf4b4ddd536f432f961c543f1b6a5", "0442dabdfe87d4f60739d7f9208ea6cb6a408961",
    "1aae5439725fc713196003e306e314382852dcd6", "923a49a1abffd38b34a2de7d46c30129d847e78b",
    "87919506d93c5be061a7f5ea3591ef1dc587cf79", "7abdafa3fb1e510a3175f823c2cd93e2a556c9be",
    "01f06a53595becdc99aa556b411420d5aa8a9913", "066151aed9c435463afa995ee80451bec0541428",
    "44439905ea036b825ae3fc810049acb52547d87a", "0a2f6d4c98e4ad9264560b0f61564785451a91fa",
    "eec20cdd4b09d4d8254b8d48888180ba0566da4c", "2d1cdd2994374fa512cfac2afa2036b4f6fea8fb",
    "bb5f48f3b605a75b35a4a56de8555d9815f78fa2", "5312bbc45ddd4e7a42940c0fa4fdb61782ffaef7",
    "23a340db9b72e8f104df8623cc8e89ef26383d57", "480e70d70394016586e70db7491d95ad052e665c",
    "ebed65dd3904d1f54d9f11e60a0a2474252177f0", "b3b90e185628a7831173d817396edc6e311c1574",
    "aa3210e3074eae3ea98f4aa9d9e2e127d0a82d5a"
]


def run_gh_command(args: List[str]) -> Dict[str, Any]:
    """Run a gh api command and return JSON response."""
    try:
        cmd = ["gh", "api"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command {' '.join(args)}: {e.stderr}", file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {' '.join(args)}: {e}", file=sys.stderr)
        return {}


def get_check_runs_for_commit(sha: str) -> List[Dict[str, Any]]:
    """Get all check runs for a commit."""
    check_runs = []
    page = 1
    per_page = 100
    
    while True:
        data = run_gh_command([
            f"/repos/{OWNER}/{REPO}/commits/{sha}/check-runs",
            "-f", f"per_page={per_page}",
            "-f", f"page={page}"
        ])
        
        if not data or "check_runs" not in data:
            break
            
        runs = data["check_runs"]
        if not runs:
            break
            
        check_runs.extend(runs)
        
        # Check if there are more pages
        if len(runs) < per_page:
            break
        page += 1
    
    return check_runs


def get_workflow_runs_for_commit(sha: str) -> List[Dict[str, Any]]:
    """Get all workflow runs for a commit."""
    workflow_runs = []
    page = 1
    per_page = 100
    
    while True:
        data = run_gh_command([
            f"/repos/{OWNER}/{REPO}/actions/runs",
            "-f", f"per_page={per_page}",
            "-f", f"page={page}",
            "-f", f"head_sha={sha}"
        ])
        
        if not data or "workflow_runs" not in data:
            break
            
        runs = data["workflow_runs"]
        if not runs:
            break
            
        workflow_runs.extend(runs)
        
        # Check if there are more pages
        if len(runs) < per_page:
            break
        page += 1
    
    return workflow_runs


def get_artifacts_for_run(run_id: int) -> List[Dict[str, Any]]:
    """Get all artifacts for a workflow run."""
    artifacts = []
    page = 1
    per_page = 100
    
    while True:
        data = run_gh_command([
            f"/repos/{OWNER}/{REPO}/actions/runs/{run_id}/artifacts",
            "-f", f"per_page={per_page}",
            "-f", f"page={page}"
        ])
        
        if not data or "artifacts" not in data:
            break
            
        arts = data["artifacts"]
        if not arts:
            break
            
        artifacts.extend(arts)
        
        # Check if there are more pages
        if len(arts) < per_page:
            break
        page += 1
    
    return artifacts


def is_failing_check(check_run: Dict[str, Any]) -> bool:
    """Determine if a check run is failing."""
    status = check_run.get("status", "")
    conclusion = check_run.get("conclusion")
    
    # Check is failing if:
    # 1. Conclusion is in the failing list
    # 2. Status is not completed
    failing_conclusions = ["failure", "timed_out", "cancelled", "action_required"]
    
    if conclusion in failing_conclusions:
        return True
    if status != "completed":
        return True
    
    return False


def process_commit(sha: str, index: int, total: int) -> Dict[str, Any]:
    """Process a single commit and collect all required data."""
    print(f"Processing commit {index}/{total}: {sha[:8]}...", file=sys.stderr)
    
    # Get check runs
    check_runs = get_check_runs_for_commit(sha)
    
    # Filter failing check runs
    failing_checks = [
        {
            "id": cr.get("id"),
            "name": cr.get("name"),
            "status": cr.get("status"),
            "conclusion": cr.get("conclusion"),
            "html_url": cr.get("html_url"),
            "started_at": cr.get("started_at"),
            "completed_at": cr.get("completed_at"),
            "details_url": cr.get("details_url")
        }
        for cr in check_runs
        if is_failing_check(cr)
    ]
    
    # Get workflow runs
    workflow_runs = get_workflow_runs_for_commit(sha)
    
    # Collect all artifacts
    all_artifacts = []
    for run in workflow_runs:
        run_id = run.get("id")
        if run_id:
            artifacts = get_artifacts_for_run(run_id)
            for artifact in artifacts:
                all_artifacts.append({
                    "id": artifact.get("id"),
                    "name": artifact.get("name"),
                    "archive_download_url": artifact.get("archive_download_url"),
                    "size_in_bytes": artifact.get("size_in_bytes"),
                    "expired": artifact.get("expired"),
                    "workflow_run_id": run_id,
                    "created_at": artifact.get("created_at"),
                    "expires_at": artifact.get("expires_at")
                })
    
    return {
        "sha": sha,
        "check_runs_total": len(check_runs),
        "check_runs_failing": failing_checks,
        "workflow_runs": [
            {
                "id": wr.get("id"),
                "name": wr.get("name"),
                "status": wr.get("status"),
                "conclusion": wr.get("conclusion"),
                "html_url": wr.get("html_url"),
                "created_at": wr.get("created_at"),
                "updated_at": wr.get("updated_at")
            }
            for wr in workflow_runs
        ],
        "artifacts": all_artifacts
    }


def create_failing_checks_markdown(commits_data: List[Dict[str, Any]]) -> str:
    """Create markdown table of failing checks."""
    lines = [
        "# Failing Checks for PR #3248",
        "",
        f"Generated: {datetime.utcnow().isoformat()}Z",
        "",
        "| Commit SHA | Check Name | Status | Conclusion | URL |",
        "|------------|------------|--------|------------|-----|"
    ]
    
    total_failing = 0
    for commit in commits_data:
        sha = commit["sha"]
        sha_short = sha[:8]
        failing = commit["check_runs_failing"]
        
        if failing:
            for check in failing:
                name = check.get("name", "N/A")
                status = check.get("status", "N/A")
                conclusion = check.get("conclusion", "N/A")
                url = check.get("html_url", "N/A")
                
                lines.append(f"| {sha_short} | {name} | {status} | {conclusion} | {url} |")
                total_failing += 1
    
    lines.insert(3, f"Total failing checks: {total_failing}")
    lines.insert(4, "")
    
    return "\n".join(lines)


def main():
    """Main execution function."""
    print(f"Starting data collection for {len(COMMITS)} commits...", file=sys.stderr)
    print(f"Repository: {OWNER}/{REPO}", file=sys.stderr)
    print(f"PR: #{PR_NUMBER}", file=sys.stderr)
    print("", file=sys.stderr)
    
    commits_data = []
    
    for idx, commit_sha in enumerate(COMMITS, 1):
        commit_data = process_commit(commit_sha, idx, len(COMMITS))
        commits_data.append(commit_data)
        
        # Print progress
        failing_count = len(commit_data["check_runs_failing"])
        artifact_count = len(commit_data["artifacts"])
        print(f"  - Found {failing_count} failing checks, {artifact_count} artifacts", file=sys.stderr)
    
    # Create output JSON
    output_data = {
        "metadata": {
            "repository": f"{OWNER}/{REPO}",
            "pr_number": PR_NUMBER,
            "total_commits": len(COMMITS),
            "generated_at": datetime.utcnow().isoformat() + "Z"
        },
        "commits": commits_data
    }
    
    # Write JSON file
    json_file = "pr3248_all_commits_complete.json"
    with open(json_file, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\n✓ Wrote {json_file}", file=sys.stderr)
    
    # Write markdown file
    md_content = create_failing_checks_markdown(commits_data)
    md_file = "failing_checks.md"
    with open(md_file, "w") as f:
        f.write(md_content)
    print(f"✓ Wrote {md_file}", file=sys.stderr)
    
    # Print summary
    total_checks = sum(c["check_runs_total"] for c in commits_data)
    total_failing = sum(len(c["check_runs_failing"]) for c in commits_data)
    total_workflows = sum(len(c["workflow_runs"]) for c in commits_data)
    total_artifacts = sum(len(c["artifacts"]) for c in commits_data)
    
    print("\n" + "="*60, file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(f"Commits processed: {len(commits_data)}", file=sys.stderr)
    print(f"Total check runs: {total_checks}", file=sys.stderr)
    print(f"Failing check runs: {total_failing}", file=sys.stderr)
    print(f"Total workflow runs: {total_workflows}", file=sys.stderr)
    print(f"Total artifacts: {total_artifacts}", file=sys.stderr)
    print("="*60, file=sys.stderr)


if __name__ == "__main__":
    main()
