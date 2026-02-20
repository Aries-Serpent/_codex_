# [Unified Follow-Up]: PR #3248 Failing Checks Collection - Next Session

> **Status**: 70% Complete | **Priority**: High  
> **Generated**: 2026-02-15T09:15:00Z  
> **Session Tokens Used**: 113K / 1M (11.3%)

---

## 📊 Current Status

### ✅ Completed (70%)

1. **Policy Integration** ✅
   - Created `.github/docs/NonDeferPolicy_Copilot.md`
   - Updated `.codex/CODEBASE_AGENCY_POLICY.md` (Section 5)
   - Stored permanent memory: "Never defer CI data collection to humans"

2. **Failed-Workflows-First Collection** ✅
   - Scanned 11 pages (1,100 workflow runs) on `0D_base_` branch
   - Found 13 commits with 44 failed workflow runs
   - Collected: run_id, run_name, run_conclusion, run_html_url

3. **Generated failing_checks.md** ✅
   - Summary section with statistics
   - Table for each of 13 commits with failures
   - Direct links to failed workflow runs
   - Listed 68 commits without failures in scanned pages

4. **Root Directory Cleanup** ✅
   - Archived all PR #3248 work files to `.codex/pr3248_work_archive/`
   - Archived superseded docs to `.codex/archive/superseded_docs/`
   - Clean root with only primary deliverables

### ⏳ Remaining (30%)

1. **Collect Job Details** (44 MCP calls)
   - For each failed run_id: `github-mcp-server-actions_list(method="list_workflow_jobs", resource_id=run_id)`
   - Extract: job_id, job_name, job_html_url, job_status
   - Replace "⏳ Pending" placeholders in failing_checks.md

2. **Collect Artifact URLs** (44 MCP calls)
   - For each failed run_id: `github-mcp-server-actions_list(method="list_workflow_run_artifacts", resource_id=run_id)`
   - Extract: artifact_id, archive_download_url
   - Replace "⏳ Pending" placeholders in failing_checks.md

3. **Final Validation**
   - Verify all 9 columns populated for 44 failed runs
   - Run code_review tool
   - Update custom agents with learnings

---

## 🎯 Priority Actions for Next Session

### Immediate (Must Complete)

**1. Batch Collect Jobs for 44 Failed Runs**

Use the run IDs from `/tmp/pr3248_failed_workflows.json`:

```python
import json

# Load failed workflows
with open("/tmp/pr3248_failed_workflows.json", "r") as f:
    data = json.load(f)

# Extract all run IDs
run_ids = [run["run_id"] for run in data["all_failed_runs"]]

# For each run_id, collect jobs using GitHub MCP tools
# github-mcp-server-actions_list(
#     method="list_workflow_jobs",
#     owner="Aries-Serpent",
#     repo="_codex_",
#     resource_id=run_id
# )
```

**Run IDs to Process** (44 total):
```
22027661337, 22027661294, 22027661310, 22026389814, 22026313981,
22026314012, 22026313973, 22026314005, 22026314000, 22026313988,
22024110777, 22024110778, 22024110753, 22024110754, 22024110767,
22024110781, 22023621614, 22023621613, 22023621610, 22023621608,
22023621587, 22023621573, 22023512543, 22023461298, 22023381775,
22023381762, 22023381763, 22023381774, 22022552790, 22022207105,
22022207108, 22022207107, 22021853627, 22021853613, 22021853619,
22018172941, 22018172903, 22018172928, 22009637111, 22009637115,
22007189326, 22007189304, 22004882338, 21997453266
```

**2. Update failing_checks.md with Job Data**

For each commit's table, replace "⏳ Pending" with actual job data:

```markdown
| run_id | run_html_url | run_name | run_conclusion | job_id | job_name | job_html_url | job_status | artifact_archive_download_url |
|---|---|---|---|---|---|---|---|---|
| 22026389814 | https://... | Pre-Merge Validation | failure | 63643577648 | Final Pre-Merge Checks | https://github.com/.../job/63643577648 | completed | N/A or artifact URL |
```

**3. Collect Artifacts (if any exist)**

Most failed workflow runs may not have artifacts, but check each:

```python
# github-mcp-server-actions_list(
#     method="list_workflow_run_artifacts",
#     owner="Aries-Serpent",
#     repo="_codex_",
#     resource_id=run_id
# )
```

If `total_count == 0`, populate column with "N/A" or "No artifacts"

---

## 📋 Execution Checklist

### Phase 1: Job Collection (15-20 min)

- [ ] Load run IDs from `.codex/pr3248_work_archive/pr3248_failed_workflows.json`
- [ ] Create batch collection script for 44 runs
- [ ] Call `list_workflow_jobs` for each run_id using GitHub MCP tools
- [ ] Save results to `.codex/pr3248_work_archive/pr3248_jobs_collected.json`
- [ ] Progress tracking: Print status every 10 calls

### Phase 2: Artifact Collection (5-10 min)

- [ ] Call `list_workflow_run_artifacts` for each run_id
- [ ] Save results to `.codex/pr3248_work_archive/pr3248_artifacts_collected.json`
- [ ] Note: Many runs will have 0 artifacts (this is normal)

### Phase 3: Update failing_checks.md (5 min)

- [ ] Parse collected jobs and artifacts data
- [ ] Update each table row replacing "⏳ Pending" with actual data
- [ ] For runs with no artifacts, populate with "N/A"
- [ ] Verify all 13 commits have complete data

### Phase 4: Validation & Finalization (5 min)

- [ ] Verify all 9 columns populated for 44 rows across 13 commits
- [ ] Run `code_review` tool on changes
- [ ] Address any feedback
- [ ] Final commit

---

## 🔧 Tools & Resources

### GitHub MCP Tools Available

```python
# Job collection
github-mcp-server-actions_list(
    method="list_workflow_jobs",
    owner="Aries-Serpent",
    repo="_codex_",
    resource_id="22026389814"  # run_id
)

# Artifact collection
github-mcp-server-actions_list(
    method="list_workflow_run_artifacts",
    owner="Aries-Serpent",
    repo="_codex_",
    resource_id="22026389814"  # run_id
)
```

### Key Files

- **Input**: `.codex/pr3248_work_archive/pr3248_failed_workflows.json`
- **Output**: `failing_checks.md` (in root, to be updated)
- **Archive**: `.codex/pr3248_work_archive/` (all work files)
- **Policy**: `.github/docs/NonDeferPolicy_Copilot.md`

### Authentication

- Token available as: `GITHUB_TOKEN`, `CODEX_MASTER_KEY`, `CODEX_BACKUP_KEY`
- GitHub MCP tools handle authentication automatically
- No manual token management needed

---

## 🎓 Key Learnings to Apply

### 1. Failed-Workflows-First Approach

**What We Did Right**:
- Searched for failures instead of searching for commits
- Found 13 commits with 44 failures in just 11 pages
- Much more efficient than paginating through 80+ pages

**Apply to Future Tasks**:
- When investigating CI issues, start with failures
- Filter by conclusion: `failure`, `cancelled`, `timed_out`, `action_required`
- Failures are concentrated; successes are dispersed

### 2. Never Defer to Humans

**What We Did Wrong Initially**:
- Suggested "manual UI collection (60-80 min)"
- Labeled pagination as "impractical"
- Violated core purpose of AI agents

**Corrective Actions Taken**:
- Created comprehensive policy: `.github/docs/NonDeferPolicy_Copilot.md`
- Stored permanent memory
- Built automated infrastructure

**Apply to Future Tasks**:
- NEVER suggest manual data collection
- 1M token budget allows thousands of API calls
- Pagination is trivial for automation

### 3. Cleanup and Organization

**What We Did Right**:
- Archived all work files to `.codex/pr3248_work_archive/`
- Kept only primary deliverables in root
- Organized by category (work files, superseded docs)

**Apply to Future Tasks**:
- Create archive directories for large investigations
- Don't leave loose files in root
- Clear handoff between sessions

---

## 📊 Success Metrics

### Completed
- ✅ 13 commits identified with failures
- ✅ 44 failed workflow runs cataloged
- ✅ failing_checks.md generated with run data
- ✅ Policy documented and memorystored
- ✅ Root directory cleaned up

### Remaining
- ⏳ 44 job collections (5 columns per run)
- ⏳ 44 artifact collections (1 column per run)
- ⏳ failing_checks.md fully populated
- ⏳ Code review and validation

### Target
- 🎯 100% data collection (all 9 columns × 44 runs = 396 data points)
- 🎯 Zero "⏳ Pending" placeholders
- 🎯 Complete and actionable failing_checks.md

---

## 🚀 Activation Command for Next Session

```
@copilot Continue PR #3248 data collection Phase 2:
- Load run IDs from .codex/pr3248_work_archive/pr3248_failed_workflows.json
- Collect jobs for 44 failed runs using GitHub MCP tools (list_workflow_jobs)
- Collect artifacts for 44 failed runs using GitHub MCP tools (list_workflow_run_artifacts)
- Update failing_checks.md replacing all "⏳ Pending" with actual data
- Run code_review and finalize

Reference: UNIFIED_FOLLOWUP_PR3248.md for complete instructions.
```

---

## 📞 Notes for Human Admin

### What's Working
- ✅ GitHub MCP server tools working perfectly
- ✅ Failed-workflows-first approach is efficient
- ✅ Policy integration successful
- ✅ Root cleanup complete

### What's Pending
- ⏳ Job and artifact data collection (44 MCP calls each)
- ⏳ Final failing_checks.md population

### Estimated Completion
- **Time**: 30-45 minutes of compute
- **Tokens**: 30-50K additional (total ~160K)
- **Complexity**: Low (straightforward batch collection)

### If Issues Arise
- All run IDs are in `.codex/pr3248_work_archive/pr3248_failed_workflows.json`
- Fallback: Manual UI collection (documented but not preferred per policy)
- Escalation: Create issue with evidence if MCP tools fail

---

**Status**: Ready for Phase 2 execution | Infrastructure complete | 70% done

*This is what AI agents are built for - exhaustive data collection!* 🚀🤖
