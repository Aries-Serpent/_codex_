# PR #3248 Failing Check Runs and Artifacts Collection Report

## Repository Information
- **Repository**: Aries-Serpent/_codex_
- **PR Number**: 3248
- **PR Title**: "0 d base"
- **Total Commits**: 100
- **HEAD SHA**: 95bcc8abc008d588e86e8283e2eba669dee556cf

## Collection Status

**Status**: ⚠️ Partial - Authentication/Rate Limit Issues

During automated collection, we encountered GitHub API authentication issues (HTTP 403) that prevented automated retrieval of check runs and artifacts for all commits.

## Commits in PR #3248

The following 100 commits were identified in this PR (from newest to oldest):

```
95bcc8abc008d588e86e8283e2eba669dee556cf
c5b2b47bade25f4d94e2c7d2bcc040a4dc0f0456
6d4643a308015e38f279293f045c6fdc256dd80c
d6048532d84d4d2c409031941642aff2de2e6514
d9811a11ad21b8b03170eaa717dc6aecea9d17b3
23772c99377b0b7f1c5a0629f177563f888b75b7
236f194bb3bdd714d3eef114e2d81e46408f0ec6
... (97 more commits)
```

Full list saved to: `/tmp/pr3248_commits.txt`

## Data Collection Structure

The requested JSON format structure is as follows:

```json
{
  "pr_number": 3248,
  "repository": "Aries-Serpent/_codex_",
  "total_commits": 100,
  "commits_with_failures_or_artifacts": 0,
  "commits": [
    {
      "sha": "COMMIT_SHA",
      "failing_checks": [
        {
          "name": "Check Name",
          "status": "completed|in_progress|queued",
          "conclusion": "failure|timed_out|cancelled|action_required|null",
          "html_url": "https://github.com/..."
        }
      ],
      "artifacts": [
        {
          "name": "Artifact Name",
          "size_in_bytes": 12345,
          "archive_download_url": "https://api.github.com/repos/.../actions/artifacts/.../zip",
          "workflow_run_id": 123456,
          "workflow_name": "Workflow Name"
        }
      ]
    }
  ]
}
```

## Manual Collection Instructions

Due to API authentication limitations in this environment, please use one of the following methods to collect the data:

### Method 1: Using authenticated `gh` CLI

```bash
# For each commit SHA in the PR:
for sha in $(cat /tmp/pr3248_commits.txt); do
  echo "Processing $sha..."
  
  # Get check runs
  gh api "repos/Aries-Serpent/_codex_/commits/$sha/check-runs" > "checks_$sha.json"
  
  # Get workflow runs
  gh api "repos/Aries-Serpent/_codex_/actions/runs?head_sha=$sha" > "runs_$sha.json"
  
  # For each run, get artifacts
  for run_id in $(jq -r '.workflow_runs[].id' "runs_$sha.json"); do
    gh api "repos/Aries-Serpent/_codex_/actions/runs/$run_id/artifacts" > "artifacts_${run_id}.json"
  done
done
```

### Method 2: Using GitHub UI

1. Navigate to: https://github.com/Aries-Serpent/_codex_/pull/3248
2. Click on the "Checks" tab
3. Review failing checks for each commit
4. Click on "Details" for each failing check to get the `html_url`
5. Navigate to "Actions" tab to view workflow runs and artifacts

### Method 3: Using GitHub REST API directly

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_token_here"

# Example API calls for a commit
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/Aries-Serpent/_codex_/commits/95bcc8abc008d588e86e8283e2eba669dee556cf/check-runs"

curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs?head_sha=95bcc8abc008d588e86e8283e2eba669dee556cf"
```

## Check Run Failure Criteria

A check run is considered "failing" if:
- **status** is not `"completed"`, OR
- **conclusion** is one of:
  - `"failure"`
  - `"timed_out"`
  - `"cancelled"`
  - `"action_required"`

## Artifacts Information

Artifacts are collected from workflow runs associated with each commit. Each artifact includes:
- `name`: The artifact name
- `size_in_bytes`: Size of the artifact
- `archive_download_url`: URL to download the artifact (requires authentication)
- `workflow_run_id`: ID of the workflow run that created this artifact
- `workflow_name`: Name of the workflow

## Next Steps

To complete data collection with proper authentication:

1. **Ensure valid GITHUB_TOKEN**: Set up a GitHub Personal Access Token with appropriate permissions (`repo`, `actions:read`)
2. **Run collection script**: Use the provided Python script with proper authentication
3. **Save results**: Output will be in JSON format matching the structure above
4. **Filter results**: Only commits with at least one failing check or artifact will be included

## Scripts Provided

The following collection scripts have been created:

1. `collect_pr_failures.py` - Initial version
2. `collect_pr_failures_v2.py` - With rate limiting handling
3. Complete commit list in `/tmp/pr3248_commits.txt`

## API Endpoints Reference

- **Get PR commits**: `GET /repos/{owner}/{repo}/pulls/{pr_number}/commits`
- **Get check runs**: `GET /repos/{owner}/{repo}/commits/{ref}/check-runs`
- **Get workflow runs**: `GET /repos/{owner}/{repo}/actions/runs?head_sha={sha}`
- **Get artifacts**: `GET /repos/{owner}/{repo}/actions/runs/{run_id}/artifacts`

## Notes

- Workflow logs are transient and expire after 90 days
- Artifacts expire based on repository retention settings (default: 90 days)
- Check run URLs (`html_url`) provide direct links to CI/CD job details
- Authentication is required to download artifacts via `archive_download_url`
