# 🚀 Quick Start - Workflow Monitoring

## One-Minute Setup

### Start Monitoring Now
```bash
# Run full 60-minute monitoring (12 polls x 5 min)
python3 scripts/continuous_workflow_monitor.py 12

# Or quick check (1 poll)
python3 scripts/continuous_workflow_monitor.py 1
```

### View Dashboard
```bash
# Check live status
cat .codex/WORKFLOW_MONITORING_194F6AF0.md
```

---

## What Gets Monitored

✅ **Commit:** `194f6af0dbef18c680f40b40a7d4cfd0b1ea6aee`  
✅ **PR:** #5328  
✅ **Repository:** aries-serpent/_codex_

---

## Dashboard Updates

- **Frequency:** Every 5 minutes
- **Location:** `.codex/WORKFLOW_MONITORING_194F6AF0.md`
- **Contains:** Status, metrics, failures, running jobs

---

## Status Icons

| Icon | Meaning |
|------|---------|
| 🟢 | Complete / Success |
| 🔵 | In Progress / Running |
| 🟡 | Initializing / Stalled |
| ❌ | Failed / Error |
| ⏳ | Queued / Waiting |

---

## Quick Commands

```bash
# View current status
cat .codex/WORKFLOW_MONITORING_194F6AF0.md

# Run single poll
python3 scripts/continuous_workflow_monitor.py 1

# Run 12 polls (60 min)
python3 scripts/continuous_workflow_monitor.py 12

# Check cached data
cat .codex/.workflow_cache.json

# View monitoring guide
cat .codex/WORKFLOW_MONITOR_README.md
```

---

## Expected Output

```
🚀 Starting Workflow Monitor
   Commit: 194f6af0
   PR: #5328
   Max Polls: 12 (≈60 minutes)

[HH:MM:SS] Poll #1
  ✅ Retrieved NNN workflows
  📊 OK:XXX FAIL:XXX RUN:XXX Q:XXX
  
[Dashboard updated to .codex/WORKFLOW_MONITORING_194F6AF0.md]
```

---

## Troubleshooting

**No workflows found?**
- Check PR #5328 includes this commit
- Verify: `gh auth status`

**API timeout?**
- Wait and retry
- Check: https://www.githubstatus.com/

**Dashboard not updating?**
- Run: `python3 scripts/continuous_workflow_monitor.py 1`
- Check file permissions on `.codex/`

---

**Need help?** See `.codex/WORKFLOW_MONITOR_README.md`

