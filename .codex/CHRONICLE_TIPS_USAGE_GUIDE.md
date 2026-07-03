# 📊 `/chronicle tips` — Session History Analysis & Personalized Recommendations

## Overview

The `/chronicle tips` command analyzes your session history and generates personalized recommendations to improve your productivity and effectiveness. It examines patterns across multiple dimensions and provides actionable insights.

## Usage

### Basic Usage

Get personalized tips based on your session history:

```bash
python -m codex.cli chronicle tips
```

### Output Formats

#### Text Format (Default)
Displays a formatted markdown summary with session statistics and personalized tips:

```bash
python -m codex.cli chronicle tips --format text
```

Output includes:
- Session History Summary
  - Total sessions
  - Date range
  - Average sessions per day
  - Success rate metrics
- Personalized Tips (1-7 recommendations)
- Usage Patterns
  - Peak hours
  - Most active days
  - Top tools and agents

#### JSON Format
Export analysis data as machine-readable JSON:

```bash
python -m codex.cli chronicle tips --format json
```

Output structure:
```json
{
  "timestamp": "2026-07-02T21:26:38Z",
  "patterns": {
    "frequency": { ... },
    "tools": { ... },
    "agents": { ... },
    "time_patterns": { ... },
    "performance": { ... },
    "trends": { ... },
    "status_distribution": { ... }
  },
  "tips": [
    {
      "category": "...",
      "title": "...",
      "description": "..."
    }
  ]
}
```

### File Output

Save tips to a file instead of stdout:

```bash
# Save as text
python -m codex.cli chronicle tips --format text --output tips.md

# Save as JSON
python -m codex.cli chronicle tips --format json --output tips.json
```

## Analysis Patterns

The `/chronicle tips` analyzes the following dimensions:

### 1. Session Frequency
**What it measures:**
- Total number of sessions
- Date range of sessions
- Average sessions per day
- Sessions in the last 7 days

**Tips generated:**
- 🎯 If > 5 sessions/day: Consider batching related work
- 📈 If < 1 session/day: Encourage consistent engagement
- ⚡ If trending up: Recognize increasing momentum
- 📉 If trending down: Suggest establishing routine

### 2. Tool Usage Patterns
**What it measures:**
- Top 10 most frequently used tools
- Success rate for each tool
- Tool reliability metrics

**Tips generated:**
- 🔧 If top tool has < 70% success: Review error patterns
- 📊 Suggest alternative approaches for low-success tools

### 3. Agent Delegation
**What it measures:**
- Number of different agents used
- Agent usage frequency
- Agent specialization opportunities

**Tips generated:**
- 🤖 If using 2+ agents: Suggest specialized agents (unified-coverage-agent, ci-auto-healer-agent, etc.)
- 📋 If no agents used: Recommend agent-based approaches

### 4. Time Patterns
**What it measures:**
- Peak hours (when most active)
- Most active days of week
- Time-of-day activity distribution

**Tips generated:**
- 📅 Suggest scheduling complex tasks during peak hours
- ⏰ Identify optimal working hours

### 5. Performance Metrics
**What it measures:**
- Success rate (% of successful sessions)
- Breakdown by status (completed, failed, error, etc.)
- Success/failure counts

**Tips generated:**
- ✅ If > 90% success: Recognize excellent performance
- ⚠️  If < 50% success: Suggest smaller tasks and better planning

### 6. Usage Trends
**What it measures:**
- Sessions per day trend (first half vs. second half)
- Direction of trend (increasing, stable, decreasing)
- Momentum indicators

**Tips generated:**
- 📈 If increasing: Maintain momentum
- 📉 If decreasing: Establish regular routine
- ➡️ If stable: Continue consistent engagement

## Tip Categories

Tips are organized by category to help you focus on specific areas:

| Category | Purpose | Example |
|----------|---------|---------|
| **productivity** | Optimize session frequency and batching | "Consider longer sessions to reduce context switching" |
| **efficiency** | Improve tool and process effectiveness | "Review error patterns for your most-used tool" |
| **coordination** | Better use of agents and delegation | "Leverage specialized agents more effectively" |
| **scheduling** | Optimize timing and patterns | "Schedule complex tasks during peak hours" |
| **recognition** | Acknowledge excellent performance | "Excellent success rate - keep it up!" |
| **improvement** | Address performance gaps | "Break down complex tasks into smaller sessions" |
| **momentum** | Maintain positive trends | "You're building momentum - maintain consistency" |
| **engagement** | Encourage consistent participation | "Establish a regular routine for better results" |
| **strategy** | High-level approach recommendations | "Use specialized agents for focused work" |

## Tip Examples

### Example 1: High Frequency Tip
```
Title: High Session Activity Detected
Category: productivity

Your sessions are averaging 6.5 sessions per day. 
Consider using longer sessions to batch related work together 
and reduce context switching overhead.
```

### Example 2: Tool Success Rate Tip
```
Title: Low Success Rate for bash
Category: efficiency

Your most-used tool 'bash' has a 65% success rate. 
Review error patterns and consider alternative approaches.
```

### Example 3: Agent Delegation Tip
```
Title: Multi-Agent Delegation
Category: coordination

You're using 5 different agents. Consider leveraging 
specialized agents more (like unified-coverage-agent, 
ci-auto-healer-agent) for focused work.
```

## Practical Use Cases

### 1. Performance Review
Review your overall success rate and identify patterns:

```bash
python -m codex.cli chronicle tips --format text | grep -A 5 "Success Rate"
```

### 2. Optimization Analysis
Export detailed analysis for your own review:

```bash
python -m codex.cli chronicle tips --format json --output my_analysis.json
# Then analyze with your preferred tools
```

### 3. Trend Tracking
Monitor how your patterns change over time:

```bash
# Save weekly tips
python -m codex.cli chronicle tips --format text --output tips_$(date +%Y%m%d).md
# Compare multiple weeks to identify trends
```

### 4. Agent Strategy Planning
Understand which agents to focus on:

```bash
python -m codex.cli chronicle tips --format json | jq '.patterns.agents'
```

## Integration with Other Tools

### With your workflow
- Review tips after major milestones
- Use trends to adjust session strategy
- Share patterns with team for optimization opportunities

### With session logging
Tips automatically use the same session database that stores all your session history:
- `.codex/codex.sqlite` - Contains all session data

## Implementation Details

### Analysis Engine
Located in: `src/codex/logging/chronicle_analytics.py`

Key components:
- `ChronicleAnalytics` - Main analysis class
- `analyze_patterns()` - Analyze all dimensions
- `generate_tips()` - Generate personalized tips
- `generate_summary()` - Create formatted summary
- `export_json()` - Export data as JSON

### Data Sources
- Session database (sessions table)
- Tool calls table (for tool usage analysis)
- Status information from completed sessions

### Algorithms
- Frequency analysis: Count and date-based calculations
- Trend analysis: First half vs. second half comparison
- Time patterns: Hour and day of week aggregation
- Success rate: Percentage calculations by tool and category

## Troubleshooting

### No sessions found
If the analysis shows 0 sessions, ensure:
1. You have run sessions that were recorded
2. The session database exists at `.codex/codex.sqlite`
3. Sessions have been properly saved

### Tips seem generic
If tips are generic (low session frequency warnings), it means:
1. Not enough session data yet (recommend running more sessions)
2. Tips will become more specific with more data
3. Continue using the feature - it improves over time

### Command not found
If `/chronicle tips` command is not available:
1. Ensure package is installed: `pip install -e .`
2. Try running from repository root
3. Check CLI is properly configured

## Future Enhancements

Potential improvements for future versions:
- 📈 Historical trending graphs
- 🔔 Threshold-based alerts
- 🎯 Custom recommendation rules
- 📊 Team aggregated insights
- 🤖 ML-based anomaly detection
- 💡 Context-aware suggestions

## Related Documents

- **CHRONICLE_TIPS.md** - Best practices and design patterns
- **CHRONICLE_IMPROVE.md** - Implementation improvement roadmap
- **CHRONICLE_SEARCH.md** - Session search and filtering
- **CHRONICLE_STANDUP.md** - Daily standup insights

---

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** 2026-07-02T21:26:38Z
