# ⚡ `/chronicle tips` Quick Reference

## Get Started Immediately

### Command Cheat Sheet

```bash
# Get tips (text format)
python -m codex.cli chronicle tips

# Get tips (JSON format)
python -m codex.cli chronicle tips --format json

# Save tips to file
python -m codex.cli chronicle tips --format text --output tips.md

# Analyze specific patterns
python -m codex.cli chronicle analyze --pattern frequency
python -m codex.cli chronicle analyze --pattern tools
python -m codex.cli chronicle analyze --pattern agents

# Get help
python -m codex.cli chronicle --help
python -m codex.cli chronicle tips --help
```

## What You'll Learn

The `/chronicle tips` command analyzes:

| Metric | What It Shows | Example Insight |
|--------|---------------|-----------------|
| **Frequency** | How often you run sessions | "Consider batching work if > 5/day" |
| **Tools** | Which tools you use most | "Your top tool has only 65% success rate" |
| **Agents** | How you delegate work | "You use 5 agents - specialize more" |
| **Time** | When you're most active | "You're most active at 14:00" |
| **Performance** | Your success rate | "91% success rate - excellent work!" |
| **Trends** | If you're accelerating/slowing | "Your activity is trending up" |

## Tip Categories

**9 Types of Tips Generated:**
- 🎯 **Productivity** - Session frequency optimization
- 🔧 **Efficiency** - Tool and process improvements
- 🤖 **Coordination** - Agent delegation strategies
- 📅 **Scheduling** - Time-based optimizations
- ✅ **Recognition** - Performance acknowledgments
- ⚠️ **Improvement** - Performance gap addressing
- 📈 **Momentum** - Trend maintenance
- 📊 **Engagement** - Consistency encouragement
- 🎲 **Strategy** - High-level approach recommendations

## Example Output

### Tips Section
```
### 1. High Session Activity Detected
Category: productivity
You're averaging 6.5 sessions per day. Consider using longer 
sessions to batch related work together and reduce context 
switching overhead.

### 2. Multi-Agent Delegation
Category: coordination
You're using 5 different agents. Consider leveraging specialized 
agents more (like unified-coverage-agent, ci-auto-healer-agent) 
for focused work.
```

### Statistics Section
```
Total Sessions: 127
Date Range: 2026-06-15 to 2026-07-02
Average Sessions/Day: 5.2

Success Rate: 87.4%
Successful: 111
Failed: 16
```

## Common Use Cases

### 📋 Weekly Review
```bash
# Generate this week's tips
python -m codex.cli chronicle tips --output weekly_tips.md
# Review improvements from last week
```

### 📊 Quarterly Analysis
```bash
# Export detailed metrics
python -m codex.cli chronicle tips --format json --output q3_analysis.json
# Share with team or review trends
```

### 🔍 Troubleshoot Low Success Rates
```bash
# Analyze which tools need improvement
python -m codex.cli chronicle analyze --pattern tools
# Focus on tools with < 80% success rate
```

### 🎯 Optimize Session Strategy
```bash
# Check if sessions are too frequent or infrequent
python -m codex.cli chronicle analyze --pattern frequency
# Check your peak hours
python -m codex.cli chronicle analyze --pattern time
```

## Output Formats

### Text (Default) - Markdown Summary
```
# 📊 Chronicle Tips Analysis

## Session History Summary
- **Total Sessions**: 127
- **Date Range**: 2026-06-15 to 2026-07-02
- **Success Rate**: 87.4%

## 💡 Personalized Tips
1. [tip content]
2. [tip content]
...
```

### JSON - Machine Readable
```json
{
  "timestamp": "2026-07-02T21:26:38Z",
  "patterns": {
    "frequency": {...},
    "tools": {...},
    "agents": {...},
    "performance": {...}
  },
  "tips": [...]
}
```

## Tips Interpretation Guide

| Tip | What It Means | Action |
|-----|---------------|--------|
| "High Session Activity (>5/day)" | Too many frequent switches | Batch related work together |
| "Low Session Frequency (<1/day)" | Inconsistent engagement | Establish a regular routine |
| "Tool Success Rate < 70%" | Tool is unreliable for you | Review errors or use alternatives |
| "Using 5+ Agents" | Scattered delegation | Focus on 2-3 specialized agents |
| "Trending Up" | Increasing momentum | Maintain current pace |
| "Trending Down" | Decreasing participation | Establish regular schedule |
| "Success Rate > 90%" | Excellent execution | Continue current approach |
| "Success Rate < 50%" | Too ambitious/scattered | Break into smaller tasks |

## Pro Tips

1. **Track Over Time** - Run regularly and compare outputs
2. **Focus on Trends** - Small changes compound over time
3. **Validate Insights** - Verify tips against your experience
4. **Share Patterns** - Use JSON export for data analysis
5. **Improve Iteratively** - Implement one suggestion per week

## Troubleshooting

### No tips generated?
- ✅ This is normal if you have few sessions
- ✅ Tips improve with more data
- ✅ Some default tips always appear

### Unexpected insights?
- ✅ Check if session data is being saved correctly
- ✅ Verify database file exists: `.codex/codex.sqlite`
- ✅ Run more sessions for better analysis

### Want to understand more?
- 📖 Read: `.codex/CHRONICLE_TIPS_USAGE_GUIDE.md`
- 💻 Examples: `examples/chronicle_tips_example.py`
- 🔍 Source: `src/codex/logging/chronicle_analytics.py`

## Related Commands

```bash
# View all available CLI commands
python -m codex.cli --help

# Session logging (the source of chronicle data)
python -m codex.cli logs --help

# Test your setup
python -m codex.cli chronicle tips
```

---

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2026-07-02

For detailed documentation, see `.codex/CHRONICLE_TIPS_USAGE_GUIDE.md`
