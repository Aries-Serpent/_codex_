# Codex Quantum Reviewer - Usage Guide

## 🚀 Quick Start

### 1. Enable the Agent

The agent is automatically available after the manifest is merged to the default branch.

### 2. Request as Reviewer

#### Via GitHub UI:
1. Open a Pull Request
2. Click "Reviewers" in the right sidebar
3. Search for "codex-quantum-reviewer"
4. Select to add as reviewer

#### Via GitHub CLI:
```bash
gh pr edit PR_NUMBER --add-reviewer codex-quantum-reviewer
```

#### Via REST API:
```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/Aries-Serpent/_codex_/pulls/PR_NUMBER/requested_reviewers \
  -d '{"reviewers": ["codex-quantum-reviewer[bot]"]}'
```

### 3. Interact with the Agent

**Trigger re-review:**
```
@codex-reviewer review
```

**Ask for specific analysis:**
```
@codex-reviewer analyze security
@codex-reviewer check performance
@codex-reviewer suggest improvements
```

**Teach the agent:**
```
@codex-reviewer learn: [knowledge or pattern]
```

## 📊 Review Capabilities

### Automatic Analysis
- Code quality assessment
- Security vulnerability detection
- Performance impact evaluation
- Documentation completeness
- Quantum pattern opportunities
- Knowledge gap identification

### Orchestration Features
- Prioritized fix suggestions
- Workflow automation plans
- Dependency resolution
- Next steps generation

### Learning & Evolution
- Learns from review feedback
- Adapts to repository patterns
- Improves suggestions over time
- Identifies knowledge gaps

## 🔧 Configuration

Edit `.github/agents/codex-reviewer.agent.yml` to customize:

```yaml
configuration:
  review_depth: "comprehensive"  # minimal, standard, comprehensive
  auto_approve_threshold: 0.95  # 0.0-1.0
  suggestion_mode: "proactive"  # reactive, proactive, aggressive
```

## 🎯 Review Workflow

1. **PR Opened/Updated** → Agent triggered automatically
2. **Initial Analysis** → Comprehensive multi-aspect review
3. **Results Posted** → Suggestions, orchestration plan, next steps
4. **Human Interaction** → Address suggestions or teach agent
5. **Re-review** → Agent validates fixes
6. **Approval/Changes** → Based on confidence and findings

## 🧠 Knowledge Feeding

Help the agent learn by providing knowledge:

```markdown
@codex-reviewer learn: In our codebase, we prefer async/await over callbacks for consistency
```

The agent will integrate this knowledge and apply it in future reviews.

## 📈 Metrics & Monitoring

View agent performance:
- Review accuracy rate
- Suggestion acceptance rate
- Average review time
- Knowledge gaps identified
- Evolution progress

Access metrics at: `/_codex_/insights/agent-metrics`
