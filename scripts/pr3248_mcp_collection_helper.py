#!/usr/bin/env python3
"""
Complete PR #3248 Failing Checks Collection using GitHub MCP Server Tools.

This script works as a GitHub Copilot Agent helper to collect comprehensive
CI/CD data for PR #3248 using the available MCP server tool outputs.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Target commits (all 81 commits from user requirement)
COMMIT_SHAS = [
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
    "aa3210e3074eae3ea98f4aa9d9e2e127d0a82d5a",
]

OWNER = "Aries-Serpent"
REPO = "_codex_"
PR_NUMBER = 3248

# HEAD SHA from PR (as identified by GitHub MCP tool)
HEAD_SHA = "95bcc8abc008d588e86e8283e2eba669dee556cf"


def main() -> None:
    print(f"📋 PR #{PR_NUMBER} Failing Checks Collection Tool")
    print(f"📊 Target: {len(COMMIT_SHAS)} commits")
    print(f"🎯 HEAD SHA: {HEAD_SHA[:7]}")
    print("⚠️  Note: API access limitations detected - generating template structure")
    print()

    # Since API calls are blocked, create template with proper structure
    results = []

    for sha in COMMIT_SHAS:
        results.append({
            "sha": sha,
            "short_sha": sha[:7],
            "commit_url": f"https://github.com/{OWNER}/{REPO}/commit/{sha}",
            "check_runs_total": 0,
            "failing_checks": [],
            "workflow_runs_total": 0,
            "artifacts": [],
            "note": "Data collection blocked by API access restrictions (403 Forbidden)",
            "collection_method": "template_generation",
            "requires_manual_collection": True
        })

    # Generate comprehensive JSON
    json_output = {
        "pr_number": PR_NUMBER,
        "repository": f"{OWNER}/{REPO}",
        "head_sha": HEAD_SHA,
        "total_commits": len(results),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "collection_status": "partial_template",
        "api_access_issue": "403 Forbidden - DNS monitoring proxy or token scope limitation",
        "required_token_scopes": ["repo", "actions:read", "checks:read"],
        "commits": results,
        "next_steps": [
            "Verify GITHUB_TOKEN has required scopes: repo, actions:read, checks:read",
            "Check if DNS monitoring proxy is blocking api.github.com",
            "Consider using GitHub CLI (gh) with authenticated session",
            "Alternative: Use Playwright browser automation to scrape workflow pages"
        ]
    }

    json_path = Path("pr3248_final_collection_template.json")
    with open(json_path, "w") as f:
        json.dump(json_output, f, indent=2)

    print(f"✅ JSON template created: {json_path}")

    # Generate markdown table
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    md_lines = [
        "# [Investigation Request]: Failing Checks per Commit",
        f"> Generated: {timestamp}",
        f"> Pull Request: #{PR_NUMBER}",
        f"> Repository: {OWNER}/{REPO}",
        f"> HEAD SHA: {HEAD_SHA}",
        "",
        "## ⚠️ Collection Status",
        "",
        "**API Access Issue Detected:** All API calls returned `403 Forbidden`.",
        "",
        "**Possible Causes:**",
        "- DNS monitoring proxy blocking `api.github.com`",
        "- GITHUB_TOKEN missing required scopes (`repo`, `actions:read`, `checks:read`)",
        "- Rate limiting or authentication issues",
        "",
        "**Required Actions:**",
        "1. Verify token has `repo` + `actions:read` + `checks:read` scopes",
        "2. Check network/proxy configuration",
        "3. Consider alternative data collection methods (see below)",
        "",
        "## Summary",
        "",
        f"This report is a **template** for {len(results)} commits in PR #{PR_NUMBER}.",
        "Actual check run and artifact data requires API access resolution.",
        "",
        "## Template Table Structure",
        "",
        "| Commit SHA | Failing Check Workflows (explicit links to failing runs) | Artifacts (download links) |",
        "|---|---|---|"
    ]

    for result in results:
        sha = result["sha"]
        short_sha = result["short_sha"]
        commit_url = result["commit_url"]

        md_lines.append(
            f"| [{short_sha}]({commit_url}) | "
            f"⚠️ Pending API access | "
            f"⚠️ Pending API access |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## Alternative Collection Methods",
        "",
        "### Method 1: GitHub CLI with Authenticated Session",
        "```bash",
        "# For each commit SHA",
        f"gh api /repos/{OWNER}/{REPO}/commits/{{SHA}}/check-runs",
        f"gh api /repos/{OWNER}/{REPO}/actions/runs?head_sha={{SHA}}",
        "```",
        "",
        "### Method 2: Playwright Browser Automation",
        "Navigate to workflow run pages and scrape artifact links:",
        f"- https://github.com/{OWNER}/{REPO}/actions/runs/{{RUN_ID}}",
        "",
        "### Method 3: Manual UI Collection",
        f"Visit PR directly: https://github.com/{OWNER}/{REPO}/pull/{PR_NUMBER}",
        "- Check 'Checks' tab for failing workflows",
        "- Click each workflow run to view artifacts",
        "",
        "---",
        "",
        "**Generated by:** `scripts/pr3248_mcp_collection_helper.py`",
        f"**Last Updated:** {timestamp}",
        "**Status:** Template generated - requires API access for actual data"
    ])

    md_content = "\n".join(md_lines)
    md_path = Path("failing_checks.md")
    md_path.write_text(md_content, encoding="utf-8")

    print(f"✅ Markdown template created: {md_path}")
    print()
    print("📝 Next Steps:")
    print("1. Review API access configuration")
    print("2. Verify GITHUB_TOKEN scopes")
    print("3. Consider using ci-log-retrieval-agent for authenticated collection")
    print("4. Alternative: Manual data entry from GitHub UI")

    sys.exit(0)



if __name__ == "__main__":
    main()