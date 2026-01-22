# Workflow Analytics Quick Start Guide

**Version**: 1.0.0  
**Last Updated**: 2026-01-22

---

## 🚀 Get Started in 5 Minutes

### Option 1: GitHub UI (Easiest)

1. Go to **Actions** tab
2. Click **Manual Workflow Analytics**
3. Click **Run workflow**
4. Leave defaults (50 runs, all workflows, create report)
5. Click **Run workflow** button
6. Wait 1-2 minutes
7. Download artifacts from run

**That's it!** Your report is in the artifacts.

---

### Option 2: Command Line

```bash
# One command to analyze last 50 runs
gh workflow run workflow-analytics-manual.yml

# Wait for completion
gh run watch

# Download report
gh run download --name workflow-analytics-report-*
```

---

## 📊 View Results

### Find Your Report

```bash
# Latest report
ls -t .codex/reports/workflow_analytics_*.md | head -1

# View it
cat .codex/reports/workflow_analytics_*.md | less
```

### What You'll See

```markdown
# Workflow Analytics Report

Health Status: HEALTHY ✅
Success Rate: 100%
Failed Runs: 0

## Key Metrics
- Total Runs: 50
- Success: 48
- Skipped: 2
- Failures: 0

## Error Patterns
✅ No patterns detected - CI is healthy!
```

---

## 🔍 Common Use Cases

### 1. "Why are tests failing?"

```bash
gh workflow run workflow-analytics-manual.yml \
  -f analysis_period=100 \
  -f status_filter=failure \
  -f create_issue=true
```

**Result**: Creates GitHub issue with detailed failure analysis

---

### 2. "Is CI healthy before release?"

```bash
gh workflow run workflow-analytics-manual.yml \
  -f analysis_period=50 \
  -f create_report=true
```

**Result**: Report shows CI health status

---

### 3. "What's wrong with this specific workflow?"

```bash
gh workflow run workflow-analytics-manual.yml \
  -f workflow_filter="test-comprehensive.yml" \
  -f analysis_period=20
```

**Result**: Focused analysis of one workflow

---

## 📚 Learn More

- **Complete Guide**: `.github/workflows/WORKFLOW_ANALYTICS_USAGE.md`
- **Integration Guide**: `.github/agents/WORKFLOW_ANALYTICS_SCRIBE_INTEGRATION.md`
- **Error Patterns**: `.codex/reports/ERROR_PATTERN_DATABASE.md`

---

## 🆘 Need Help?

**Issue**: Workflow doesn't start
- Check you're logged in to GitHub
- Verify permissions: `gh auth status`

**Issue**: No workflows found
- Check repository has workflow runs: `gh run list`

**Issue**: Reports not generated
- Check workflow logs: `gh run view <run-id>`

---

## 🎯 Pro Tips

1. **Weekly checks**: Scheduled workflow runs automatically every Monday
2. **After changes**: Run manual analysis to verify improvements
3. **Before releases**: Always check CI health
4. **Create issues**: Use `-f create_issue=true` to track problems

---

**Quick Reference**:
```bash
# Basic
gh workflow run workflow-analytics-manual.yml

# Investigate failures
gh workflow run workflow-analytics-manual.yml -f status_filter=failure

# Specific workflow
gh workflow run workflow-analytics-manual.yml -f workflow_filter="<name>"

# Create issue
gh workflow run workflow-analytics-manual.yml -f create_issue=true
```

---

**Need more details?** See `.github/workflows/WORKFLOW_ANALYTICS_USAGE.md`
