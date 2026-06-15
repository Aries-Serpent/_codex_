# 🎯 Track 5B Quick Reference - Continuous Workflow Monitoring

**Status**: 🟢 **MONITORING ACTIVE** (Started 23:48 UTC)  
**Duration**: 60 minutes | **Target End**: 00:48 UTC  
**Agent**: workflow-health-monitor (PID 7737, detached)  

---

## 🔥 Quick Status Commands

```bash
# ✅ Is monitoring running?
ps aux | grep monitor_workflows_continuous.py

# 📊 Database summary - total runs tracked
sqlite3 .codex/monitoring_data.db "SELECT COUNT(*) as total_runs FROM workflow_runs;"

# 🔴 Database summary - failures by category
sqlite3 .codex/monitoring_data.db \
  "SELECT category, COUNT(*) as count FROM failures GROUP BY category ORDER BY count DESC;"

# 📋 Last 20 failures detected
sqlite3 .codex/monitoring_data.db \
  "SELECT workflow_name, category, timestamp FROM failures ORDER BY timestamp DESC LIMIT 20;"

# 📈 Success rate calculation
sqlite3 .codex/monitoring_data.db \
  "SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN conclusion = 'success' THEN 1 ELSE 0 END) as passed,
    ROUND(100.0 * SUM(CASE WHEN conclusion = 'success' THEN 1 ELSE 0 END) / COUNT(*), 1) as success_rate_pct
   FROM workflow_runs;"

# 🚨 Check for critical failures
sqlite3 .codex/monitoring_data.db \
  "SELECT workflow_name, COUNT(*) as failure_count 
   FROM failures 
   WHERE category = 'Regression'
   GROUP BY workflow_name
   ORDER BY failure_count DESC;"

# 📊 View real-time monitoring log
tail -50 .codex/WORKFLOW_MONITORING_LOG.md

# 🔍 Watch log updates in real-time
watch -n 5 'tail -20 .codex/WORKFLOW_MONITORING_LOG.md'
```

---

## 📁 Key Files

| File | Purpose | Update Interval |
|------|---------|-----------------|
| `.codex/MONITORING_SESSION_TRACKER.md` | Session overview & checklist | Manual |
| `.codex/WORKFLOW_MONITORING_LOG.md` | Real-time event log | Every 15 min |
| `.codex/WORKFLOW_HEALTH_DASHBOARD.md` | Live monitoring dashboard | Every 15 min |
| `.codex/monitoring_data.db` | SQLite database with all data | Every poll (5 min) |
| `scripts/monitor_workflows_continuous.py` | Monitoring script (running) | N/A |

---

## 🎯 Expected vs Actual Monitoring

### Monitoring Expectations (Baseline)
- **Total Workflows**: 100
- **Critical Workflows**: 34 (Testing + Security)
- **Support Workflows**: 41 (Copilot agents)
- **Expected Runs in 60 min**: ~20-30 (from recent history)
- **Expected Failures**: <5% of runs = 1-2 failures
- **Success Rate Target**: ≥95%

### Real-time Tracking
- **Current Polling**: Every 5 minutes
- **Log Updates**: Every 15 minutes
- **Database Updates**: Real-time on each poll
- **Alert Triggers**: Immediate on critical failures

---

## 🔔 What to Watch For

### From Track 1 (Environment Rebuild)
- Docker build failures
- Action environment setup issues
- Dependency/package installation problems
- Cache configuration errors

### From Track 2 (CodeQL Security Fixes)
- Security scanning validation failures
- Integration test regressions
- New security-related assertion failures
- Code quality suite failures

### From Track 4 (Test Enhancements)
- Test timeout failures (increased test count)
- Resource exhaustion issues
- Transient failures under higher load
- New test assertion failures

---

## 💡 Troubleshooting

### If monitoring stops
```bash
# Check if process is still running
pgrep -f monitor_workflows_continuous.py

# If not running, restart it
cd /home/runner/work/_codex_/_codex_
nohup python3 scripts/monitor_workflows_continuous.py > monitor.log 2>&1 &
```

### If database has errors
```bash
# Check database integrity
sqlite3 .codex/monitoring_data.db "PRAGMA integrity_check;"

# Backup database
cp .codex/monitoring_data.db .codex/monitoring_data_backup.db

# If corrupted, restore from backup
cp .codex/monitoring_data_backup.db .codex/monitoring_data.db
```

### View script output
```bash
# If running in nohup, check output
tail -100 monitor.log

# Check for recent errors
grep -i "error\|exception\|failed" monitor.log | tail -20
```

---

## 📊 Sample Queries by Use Case

### "What's the success rate right now?"
```bash
sqlite3 .codex/monitoring_data.db \
  "SELECT 
    COUNT(*) as total_runs,
    SUM(CASE WHEN conclusion = 'success' THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN conclusion = 'success' THEN 1 ELSE 0 END) / COUNT(*), 1) as success_pct
   FROM workflow_runs WHERE datetime(updated_at) >= datetime('now', '-1 hour');"
```

### "Which workflows are failing most?"
```bash
sqlite3 .codex/monitoring_data.db \
  "SELECT workflow_name, COUNT(*) as failure_count 
   FROM failures 
   GROUP BY workflow_name 
   ORDER BY failure_count DESC LIMIT 10;"
```

### "Are there any regression failures?"
```bash
sqlite3 .codex/monitoring_data.db \
  "SELECT workflow_name, COUNT(*) as regressions 
   FROM failures 
   WHERE category = 'Regression'
   GROUP BY workflow_name 
   ORDER BY regressions DESC;"
```

### "What's the breakdown by failure category?"
```bash
sqlite3 .codex/monitoring_data.db \
  "SELECT 
    category,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM failures), 1) as pct
   FROM failures 
   GROUP BY category 
   ORDER BY count DESC;"
```

### "How many workflows are still in progress?"
```bash
sqlite3 .codex/monitoring_data.db \
  "SELECT COUNT(*) as in_progress 
   FROM workflow_runs 
   WHERE status = 'in_progress';"
```

### "Which critical workflows have failed?"
```bash
sqlite3 .codex/monitoring_data.db \
  "SELECT DISTINCT f.workflow_name, COUNT(*) as failures
   FROM failures f
   WHERE f.workflow_name IN (
     'Validation Pipeline', 'CI — Optimized with Caching', 'CodeQL', 'Semgrep SAST',
     'Pre-Merge Validation', 'Code Quality & Coverage Suite', 'Security Scanning Suite'
   )
   GROUP BY f.workflow_name
   ORDER BY failures DESC;"
```

---

## 📈 Campaign Timeline

| Time | Event | Status |
|------|-------|--------|
| 23:48 UTC | Campaign started, baseline established | ✅ |
| ~23:53 UTC | First polling iteration | ⏳ Expected |
| 00:03 UTC | First log update (15 min) | ⏳ Expected |
| 00:18 UTC | Second log update (30 min) | ⏳ Expected |
| 00:33 UTC | Third log update (45 min) | ⏳ Expected |
| 00:48 UTC | Campaign end, final report | ⏳ Expected |

---

## ✅ Campaign Checklist

**Pre-campaign** (COMPLETE ✅)
- [x] Baseline established (100 workflows)
- [x] Critical workflows identified (34)
- [x] Database initialized
- [x] Monitoring script started (async/detached)
- [x] Real-time log created

**During campaign** (IN PROGRESS ⏳)
- [ ] Poll every 5 minutes (running)
- [ ] Log failures to database (running)
- [ ] Update log every 15 minutes (pending first update)
- [ ] Alert on critical failures (ready)
- [ ] Categorize failures (running)

**Post-campaign** (PENDING ⏳)
- [ ] Final data collection (at 00:48 UTC)
- [ ] Statistics calculation
- [ ] Report generation
- [ ] Analysis & recommendations
- [ ] Session archive

---

## 🎯 Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| All 100 workflows monitored | Yes | ✅ |
| Real-time polling active | Every 5 min | ✅ |
| Log updates every 15 min | On schedule | ⏳ |
| Failure rate <5% | <5 failures | TBD |
| All failures categorized | 100% | TBD |
| Final report generated | Yes | TBD |

---

## 📞 Contact & Support

If monitoring needs intervention:
- Check script status: `pgrep -f monitor_workflows_continuous.py`
- Review real-time log: `tail -f .codex/WORKFLOW_MONITORING_LOG.md`
- Check database: `sqlite3 .codex/monitoring_data.db ".tables"`
- View recent errors: `grep -i error monitor.log`

---

**Campaign Status**: 🟢 MONITORING ACTIVE  
**Last Updated**: 2026-02-05T23:49:00Z  
**Next Update**: ~2026-02-06T00:03:00Z (log update)  
**Session**: TRACK_5B_CONTINUOUS_2026-02-05_2348
