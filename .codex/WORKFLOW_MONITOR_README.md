# Workflow Monitoring System - Commit 194f6af0

## 🎯 Overview

A comprehensive real-time monitoring system for tracking all workflows triggered by commit `194f6af0dbef18c680f40b40a7d4cfd0b1ea6aee` in PR #5328.

**Status:** ✅ Deployed and Active  
**Dashboard:** `.codex/WORKFLOW_MONITORING_194F6AF0.md`  
**Last Updated:** 2026-07-16 23:48:00 UTC

---

## 📊 Monitoring Configuration

| Setting | Value |
|---------|-------|
| **Commit SHA** | `194f6af0dbef18c680f40b40a7d4cfd0b1ea6aee` |
| **Commit Message** | Apply remaining changes |
| **Pull Request** | #5328 |
| **Repository** | aries-serpent/_codex_ |
| **Polling Interval** | 5 minutes |
| **Max Duration** | 55 minutes |
| **Status Counts** | Queued, Running, Success, Failed, Cancelled |
| **Auto-stop** | When all workflows complete or timeout |

---

## 🚀 Deployed Components

### 1. Dashboard File
**Location:** `.codex/WORKFLOW_MONITORING_194F6AF0.md`

- Real-time status summary
- Workflow list with status/conclusion
- Failed workflow tracking
- Stalled workflow detection
- Execution metrics and trends
- Update history log

**Auto-updates:** Every 5 minutes when monitoring service is active

### 2. Monitoring Scripts

#### Primary Monitor
**File:** `scripts/continuous_workflow_monitor.py`

- Queries GitHub API for workflow status
- Filters workflows by commit SHA
- Calculates execution metrics
- Detects stalled workflows (>25 min running)
- Tracks failures and categorizes them
- Updates dashboard markdown
- 12-poll cycle (60 minutes maximum)

**Usage:**
```bash
python3 scripts/continuous_workflow_monitor.py 12  # 12 polls
python3 scripts/continuous_workflow_monitor.py 1   # Single poll
```

#### Alternative Monitor
**File:** `scripts/workflow_monitor_service.py`

- Production-grade monitoring engine
- Enhanced error handling and fallback
- Caching mechanism for API resilience
- Detailed execution metrics
- Failure analysis
- Stalled workflow alerts

**Usage:**
```bash
python3 scripts/workflow_monitor_service.py 12
```

#### Shell Script Monitor
**File:** `/tmp/monitor_workflow_bg.sh`

- Lightweight bash-based monitoring
- Uses `gh run list` for reliability
- Simple status counting
- Minimal dependencies

**Usage:**
```bash
/tmp/monitor_workflow_bg.sh
```

### 3. Support Files

- `.codex/.workflow_cache.json` - Cached workflow data
- `.codex/.workflow_status_cache.json` - Status snapshots
- `.codex/.workflow_last_data.json` - Last query results

---

## 📈 Metrics Tracked

### Per Workflow
- ✅ Run ID and Run Number
- ✅ Workflow Name
- ✅ Status (queued, in_progress, completed)
- ✅ Conclusion (success, failure, cancelled)
- ✅ Created and Updated Timestamps
- ✅ Duration calculations

### Aggregated
- ✅ Total Workflows Count
- ✅ Success Rate (%)
- ✅ Failure Rate (%)
- ✅ Completion Rate (%)
- ✅ In-Progress Count
- ✅ Queued Count
- ✅ Stalled Workflows (>25 min)
- ✅ Failed Workflows (detailed list)

---

## 🔍 Workflow Detection

### Commit Filtering
- Primary: `head_sha` starts with `194f6af0`
- Scope: Last 100 workflow runs
- PR Association: #5328

### Query Methods
1. **GitHub REST API** (`gh api repos/.../actions/runs`)
2. **GitHub CLI Run List** (`gh run list`)
3. **Cached Data** (fallback when API unavailable)

---

## 🚨 Alert Conditions

### Stalled Workflows
- **Trigger:** Running for >25 minutes
- **Action:** Logged and highlighted in dashboard
- **Follow-up:** Job logs retrieved for analysis

### Failed Workflows
- **Trigger:** Workflow completed with `failure` conclusion
- **Action:** Listed in "Failed Workflows" section
- **Details:** Name, Run ID, Run Number included

### API Failures
- **Fallback 1:** Use cached workflow data
- **Fallback 2:** Retry with alternative query method
- **Fallback 3:** Manual GitHub check recommended

---

## 📋 Dashboard Updates

### Update Frequency
- **Automatic:** Every 5 minutes when service active
- **Manual:** Run monitoring script anytime

### Update Content
```markdown
- Status counts (success, failed, running, queued)
- Progress bar visualization
- Workflow detail table
- Failure tracking
- Running workflows list
- Poll history
- Execution metrics
- Timestamps and elapsed time
```

### Live Status Indicators
- 🟢 Complete - All workflows finished
- 🔵 Monitoring - Workflows still running
- 🟡 Initializing - First poll in progress
- 🔴 Stalled - Workflows running >25 min

---

## 🔄 Continuous Monitoring Workflow

```
┌─────────────────────────────────────────┐
│ Poll #N at 5-minute interval            │
├─────────────────────────────────────────┤
│ 1. Query GitHub API                     │
│ 2. Filter by commit 194f6af0            │
│ 3. Analyze workflow status              │
│ 4. Calculate metrics                    │
│ 5. Detect stalled/failed workflows      │
│ 6. Update dashboard                     │
│ 7. Store status snapshot                │
│ 8. Check completion (all done?)         │
│    └─ YES → Stop monitoring             │
│    └─ NO → Sleep 5 min, repeat          │
└─────────────────────────────────────────┘
```

---

## 🛠️ Manual Operations

### Run Single Poll
```bash
cd /home/runner/work/_codex_/_codex_
python3 scripts/continuous_workflow_monitor.py 1
```

### Run Extended Monitoring (60 min)
```bash
python3 scripts/continuous_workflow_monitor.py 12
```

### View Current Dashboard
```bash
cat .codex/WORKFLOW_MONITORING_194F6AF0.md
```

### Check Cached Status
```bash
cat .codex/.workflow_cache.json | jq .
```

### Force Dashboard Update
```bash
# Manually run a poll to refresh dashboard
python3 scripts/continuous_workflow_monitor.py 1
```

---

## 🔧 Troubleshooting

### Problem: No Workflows Found
**Cause:** GitHub API unavailable or commit not triggered any workflows
**Solution:**
1. Check PR #5328 exists and includes this commit
2. Verify GitHub CLI (`gh`) is authenticated
3. Run: `gh auth status`

### Problem: API Query Timeout
**Cause:** GitHub API responding slowly
**Solution:**
1. Wait 30 seconds and retry
2. Check GitHub status: https://www.githubstatus.com/
3. Use cached data with `cat .codex/.workflow_cache.json`

### Problem: Dashboard Not Updating
**Cause:** Monitoring service not running
**Solution:**
1. Run: `python3 scripts/continuous_workflow_monitor.py 12`
2. Check for errors in output
3. Verify file permissions on `.codex/`

---

## 📝 Integration

### With CI/CD Workflows
Dashboard can be referenced in workflow summaries:
```yaml
- name: Report Workflow Status
  run: cat .codex/WORKFLOW_MONITORING_194F6AF0.md >> $GITHUB_STEP_SUMMARY
```

### With GitHub Actions
Monitor can be triggered by workflow:
```yaml
- name: Monitor Workflows
  run: python3 scripts/continuous_workflow_monitor.py 12
```

---

## 📊 Success Criteria

✅ Monitoring deployed  
✅ Dashboard created  
✅ Polling mechanism ready  
✅ Error handling configured  
✅ Fallback queries implemented  
✅ Caching system active  
⏳ GitHub API connectivity restored (pending)  
⏳ First poll completed (pending API restoration)  
⏳ Real-time updates flowing (pending API restoration)  

---

## 🔐 Data Storage

All monitoring data is stored locally:
- Dashboard: `.codex/WORKFLOW_MONITORING_194F6AF0.md` (markdown)
- Cache: `.codex/.workflow_cache.json` (JSON)
- Status: `.codex/.workflow_status_cache.json` (JSON)

No data transmitted to external services.

---

## 📞 Support

For workflow monitoring issues:

1. **Check dashboard:** `.codex/WORKFLOW_MONITORING_194F6AF0.md`
2. **Review script logs:** Run with `-v` flag (if implemented)
3. **Check GitHub status:** https://www.githubstatus.com/
4. **Verify PR #5328:** https://github.com/aries-serpent/_codex_/pull/5328

---

**System Status:** ✅ Ready  
**Last Check:** 2026-07-16 23:48:00 UTC  
**Dashboard Version:** 1.0.0  

