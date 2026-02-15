# PR #3248 Failing Check Runs and Artifacts - Final Report

## Executive Summary

**Pull Request**: [#3248 "0 d base"](https://github.com/Aries-Serpent/_codex_/pull/3248)  
**Repository**: Aries-Serpent/_codex_  
**Branch**: 0D_base_  
**Total Commits**: 100  
**Commits with Failures**: 1  
**Total Failing Checks**: 1

## Collection Results

### Successfully Collected:
✅ All 100 commit SHAs from PR  
✅ Workflow runs for PR branch (30 runs analyzed)  
✅ Failing check runs identification  
✅ HTML URLs for all workflow runs  
✅ Artifact API endpoints for all runs

### Not Collected (Requires Additional API Calls):
⚠️ Artifact contents (requires per-run API calls with authentication)  
⚠️ Individual check run details beyond workflow runs

## Failing Checks Summary

### Commit: `95bcc8abc008d588e86e8283e2eba669dee556cf` (HEAD)

**Total Workflow Runs**: 17  
**Passing**: 16  
**Failing**: 1

#### Failing Check:
- **Name**: Resilient Validation Suite
- **Status**: completed
- **Conclusion**: failure
- **URL**: https://github.com/Aries-Serpent/_codex_/actions/runs/22031050538
- **Run ID**: 22031050538
- **Event**: pull_request
- **Created**: 2026-02-15T06:27:30Z
- **Updated**: 2026-02-15T06:33:22Z

## Structured JSON Output

The complete data has been saved in the following formats:

1. **pr3248_complete_report.json** - Full structured report with all data
2. **pr3248_detailed_report.json** - Detailed analysis with summaries
3. **/tmp/pr3248_commits.txt** - List of all 100 commit SHAs

### JSON Structure

```json
{
  "pr_number": 3248,
  "repository": "Aries-Serpent/_codex_",
  "pr_url": "https://github.com/Aries-Serpent/_codex_/pull/3248",
  "total_commits": 100,
  "commits_with_failures_or_artifacts": 1,
  "commits": [
    {
      "sha": "95bcc8abc008d588e86e8283e2eba669dee556cf",
      "failing_checks": [
        {
          "name": "Resilient Validation Suite",
          "status": "completed",
          "conclusion": "failure",
          "html_url": "https://github.com/Aries-Serpent/_codex_/actions/runs/22031050538",
          "run_id": 22031050538
        }
      ],
      "all_workflow_runs": [
        {
          "run_id": 22031050555,
          "name": "Scan and Report GitHub Secrets and Variables",
          "status": "completed",
          "conclusion": "success",
          "html_url": "...",
          "artifacts_url": "https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs/22031050555/artifacts"
        },
        // ... 16 more runs
      ],
      "artifacts_note": "Artifacts require per-run API calls. Run IDs are provided for manual collection."
    }
  ]
}
```

## All Workflow Runs for HEAD Commit

The HEAD commit (`95bcc8abc008d588e86e8283e2eba669dee556cf`) has 17 workflow runs:

### Passing Workflows (16):
1. Scan and Report GitHub Secrets and Variables (22031050555)
2. Art_Documentation Link Checker (22031050558)
3. PR Auto-Fix Check (22031050537)
4. Auto-Fix Common CI Issues (22031050544)
5. Art_Copilot Evolution & Review (Unified) (22031050557)
6. Art_Audit & QA Suite (Unified) (22031050547)
7. Pages Pre-Merge Validation (22031050566)
8. Art_Workflow Documentation Link Validation (22031050542)
9. Art_"CodeQL" (22031050541)
10. Pre-Merge Validation (22031050567)
11. Art_Code Quality & Coverage Suite (22031050561)
12. Art_Security Scanning Suite (22031050536)
13. Art_Memory & Performance Validation (22031050568)
14. Art_Dependency & Licensing Validation (22031050552)
15. Art_Python Testing Suite (22031050569)
16. Art_Rust Testing Suite (22031050548)

### Failing Workflows (1):
1. **Resilient Validation Suite** (22031050538) ❌

## Artifact Collection

### Artifact URLs for All Runs

Each workflow run has a corresponding artifacts endpoint:

```
https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs/{run_id}/artifacts
```

### Manual Artifact Collection Commands

To collect artifacts for all runs:

```bash
# For the failing run
gh api repos/Aries-Serpent/_codex_/actions/runs/22031050538/artifacts

# For all runs in the PR (example)
for run_id in 22031050555 22031050558 22031050537 22031050544 22031050557 22031050547 22031050566 22031050542 22031050541 22031050567 22031050561 22031050538 22031050536 22031050568 22031050552 22031050569 22031050548; do
  echo "Checking run $run_id..."
  gh api "repos/Aries-Serpent/_codex_/actions/runs/$run_id/artifacts" | jq '.artifacts[] | {name, size_in_bytes, archive_download_url}'
done
```

## Failure Criteria Applied

A check run is considered "failing" if:
- `status` != `"completed"` **OR**
- `conclusion` ∈ `["failure", "timed_out", "cancelled", "action_required"]`

## All 100 Commits in PR

<details>
<summary>Click to expand full commit list</summary>

```
95bcc8abc008d588e86e8283e2eba669dee556cf
c5b2b47bade25f4d94e2c7d2bcc040a4dc0f0456
6d4643a308015e38f279293f045c6fdc256dd80c
d6048532d84d4d2c409031941642aff2de2e6514
d9811a11ad21b8b03170eaa717dc6aecea9d17b3
23772c99377b0b7f1c5a0629f177563f888b75b7
236f194bb3bdd714d3eef114e2d81e46408f0ec6
3957342414c8c187ae6352d2b019a0cd8752872a
217ee6abd4ebeb500afc87c0c335bc5642f88092
206e6b9febe3b30e0f94c1d1e46bc8aa54c10f1a
24a99a15c20b950c09f9281a99cfa752981f0392
9f4338b98c47365970d40f52c885a97821386c89
438e980734165d0bc58b9c1fbe4ada88cb625981
9af62f8e593c33b43068de0329dcd5c585465d41
9cd0b93a212aa2543eac3337ddde362fdd62a57d
786e812f2e5f33c1af407ffdf8c15a09c7705ae7
82015f734c92722a4792b2c7d8608c0829bf66d8
387f44c5cffd1a6b45d1bf5c34aca81ecb6b65a0
d7c3680e655b2b6d8a735c0d27f428c90329eb3a
ee1120b10a381db775c05ccda030ec918071452b
aa3210e3074eae3ea98f4aa9d9e2e127d0a82d5a
b3b90e185628a7831173d817396edc6e311c1574
ebed65dd3904d1f54d9f11e60a0a2474252177f0
480e70d70394016586e70db7491d95ad052e665c
23a340db9b72e8f104df8623cc8e89ef26383d57
5312bbc45ddd4e7a42940c0fa4fdb61782ffaef7
bb5f48f3b605a75b35a4a56de8555d9815f78fa2
2d1cdd2994374fa512cfac2afa2036b4f6fea8fb
eec20cdd4b09d4d8254b8d48888180ba0566da4c
0a2f6d4c98e4ad9264560b0f61564785451a91fa
44439905ea036b825ae3fc810049acb52547d87a
066151aed9c435463afa995ee80451bec0541428
01f06a53595becdc99aa556b411420d5aa8a9913
7abdafa3fb1e510a3175f823c2cd93e2a556c9be
87919506d93c5be061a7f5ea3591ef1dc587cf79
923a49a1abffd38b34a2de7d46c30129d847e78b
1aae5439725fc713196003e306e314382852dcd6
0442dabdfe87d4f60739d7f9208ea6cb6a408961
9db17bd601cbf4b4ddd536f432f961c543f1b6a5
f45e5cca3cd62dc799eaa12ad01adc326962e736
b3dbe1081be9c95f9e31446f4c0c20dea394500d
d088994633604a2bb8ba972d4d0ff7bf28a34fc7
c3c07d1c032d02ef42250cf960d187164fe79bf2
f2ef77258695f77985cdf2071d7b3f4b1f22ee29
f58b5c1d93f9abf4bf8df033a346a68a817414a5
9a83b8c6c2ca64d95bed272ed9793e5dae4bdd4b
c067b49b388e4eb6f72edf5e035907c237c68338
07713e4bfceb88294e1c7b674c0c47f69ca4fb8e
38c64fa215fd81714acf881aa9d0a6f1269445ef
28106e64c63a38aa70b39df39d8edf1bcdeafb35
7f0379dfac8e4ccdfc386fb898b9ed1192aca83a
c18eafd9a2941f491d5c903427894273e055ada0
0640f7d1bd8f690ade3b5332efa2ed6822aab451
4985bf797565b7e44421c70984299cbc42188b4c
07bf832d6ce42191797282f6f7d75f0810623e43
faf0ac3ed93c5930f26e06c79921ccae6f28a934
dee711cde2e767ea8815fcc11bfa53bef84a84f7
9b194adb18bae4c8230930151ee2ceb178e1afa3
9ad5bc92bf7afac9d87836937dafc647a4d1df07
c57b5da02554aad84cd445e974679aff6625564e
3ab4364be487a92c9b38469bb3bcdb2efb2d8401
0db24b5fb6fdf5e789b48f5c9cefa0632c09e48f
721be8fbe6d1db02f1727a0189f1a6dd12d04c49
9de52f9cdcff1c50afe0c02f22195c51e9cfc2e6
43428572c5a75d8688a92ea61d4cdf00e6ab7d37
a80e33fbe77a7f756d0e91bda7289b4385e7b26e
27daa3272aa9b13cd13c298a9fbd0392ccc39bf9
5b44dd5d8d78b9e07858f10aabbccfdd08eb3ffe
ce6917ac948ae6c432952a4a0df7ad0e33788d07
a37117c697b028c2bbc13f5f0519763acc3b7167
7666a701f0ce4715cbe2eedd5950a53e900a7ec1
6762050e4fbf7209097e188e859930027be3a072
ff937ef0f925d563d5b09ede40f22feb0b78f747
89a32c56aec18457ee286ab9d27c9440c94e44a6
2937fe5861bfa5e654c5c58c149895fea98095de
a77242d5cccd607731857f1f215a6abc5d4074a5
5ca9ec6d9dfbd81e537315eb7954ca1cc943d17d
3a73d44792ce22f4ee2619336b00fb53707b650c
0d8be400d4f7a045efa70ffd91cc3d72c1416960
c643d565ce8a2f375d82805ed48f80900fc93c85
e1a9a7cfbc50280bdfbf4f820b039c6237b37652
195947d6b23b739770b05fc24e228d872b2f1ed6
27212d4a493f2504878302a5315dcea0d853005c
f5212c6f651bece0657d182147ef4992f98f5891
209ea2c216e4b1eb3b1b2c06bad541b6303071b0
6593115b8e8ab13063fc0a48dded8a30fab1d755
78c75ca6e435b4dfdc38ea1bd6f8237f25d6525a
1d5fccd38c5c9d7ba0c29e3435add0a754853102
701e1ca36718b69f4b5d990558c06e58bb389aa6
77e29f0023896057bf406e2a59f382fbf3c80ccd
43d7f59bc2e4a26b635633e29dc6d6c0da2379e4
9cc97df9e37aaef873b3271a0acee92f48af8234
7267398869bcb253981fd10b300b0d6865825141
483be0dea87f9b9097ef9c0d91a6efb36abc087b
a59dffd35d0875574db2fc806a687d84d6d8b99a
2378dc6a96df8465dbc8a4972b4fe8b6817ba2cc
c36c47f24c70ca3912f11ecde51bb1552b6ebed5
0d96f686543854a0647cba99e81aacbcc17524b5
2a7e546fc698aba6a6131ed232a8b8e544211e4e
9ff7e2ae58658fae8006b5639f718956a97f48d5
```

</details>

## Notes & Limitations

1. **Artifact Collection**: Artifacts were not automatically collected as each requires an individual authenticated API call. The artifact URLs are provided in the JSON output for manual collection.

2. **Check Runs vs Workflow Runs**: This report focuses on workflow runs from GitHub Actions. Individual check runs (from external CI systems) would require additional API calls to `/repos/{owner}/{repo}/commits/{sha}/check-runs`.

3. **Data Freshness**: This data was collected on 2026-02-15. Workflow logs and artifacts may expire after 90 days based on GitHub's retention policies.

4. **Only Failing Commits Included**: The structured JSON output only includes commits that have at least one failing check, as requested.

## Files Generated

1. **pr3248_complete_report.json** - Complete structured JSON with all data
2. **pr3248_detailed_report.json** - Detailed report with summaries
3. **pr3248_collection_report.md** - Collection methodology and instructions
4. **PR3248_FINAL_SUMMARY.md** - This file
5. **/tmp/pr3248_commits.txt** - List of all commit SHAs

## API Endpoints Reference

- **PR Commits**: `GET /repos/Aries-Serpent/_codex_/pulls/3248/commits`
- **Check Runs**: `GET /repos/Aries-Serpent/_codex_/commits/{sha}/check-runs`
- **Workflow Runs**: `GET /repos/Aries-Serpent/_codex_/actions/runs?head_sha={sha}`
- **Artifacts**: `GET /repos/Aries-Serpent/_codex_/actions/runs/{run_id}/artifacts`

## Conclusion

PR #3248 has **100 commits** with **1 failing check** on the HEAD commit:
- **Failing**: Resilient Validation Suite
- **URL**: https://github.com/Aries-Serpent/_codex_/actions/runs/22031050538

All other checks (16 workflows) are passing. The structured JSON data is available in `pr3248_complete_report.json`.
