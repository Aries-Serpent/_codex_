# Prompt Templates - User Guide

**Purpose**: Standards and guidelines for AI agent prompt templates in the `_codex_` repository.

**Last Updated**: 2025-12-30  
**Version**: 2.0.0  
**Status**: 🟢 Active

---

## 📚 Available Prompts

### Active Prompts

| Prompt | Version | Purpose | Audience |
|--------|---------|---------|----------|
| [COVERAGE_ENHANCEMENT_PROMPT.md](COVERAGE_ENHANCEMENT_PROMPT.md) | 1.0 | Increase test coverage to 100% | GitHub Copilot |
| [COVERAGE_CONTINUATION_PROMPT.md](COVERAGE_CONTINUATION_PROMPT.md) | 1.0 | Continue coverage work | GitHub Copilot |
| [custom_gpt_self_healing_engineer.md](custom_gpt_self_healing_engineer.md) | 1.0 | Self-healing system prompt | ChatGPT |
| [QUANTUM_PLUGIN_ORCHESTRATION_DEMO.md](QUANTUM_PLUGIN_ORCHESTRATION_DEMO.md) | 1.0 | Quantum orchestration demo | GitHub Copilot |

### Specialized Prompts

| Prompt | Version | Purpose |
|--------|---------|---------|
| [codex_run_prompt_0A_base_.md](codex_run_prompt_0A_base_.md) | 1.0 | Codex run template A |
| [codex_run_prompt_0D_base_.md](codex_run_prompt_0D_base_.md) | 1.0 | Codex run template D |
| [chatgpt5_connectivity_recipes.md](chatgpt5_connectivity_recipes.md) | 1.0 | ChatGPT-5 connectivity |

---

## 📝 Prompt Template Standard (v2.0)

### Required Structure

All prompts should follow this standard format:

```markdown
# [Prompt Title]

**Version**: X.Y.Z  
**Last Updated**: YYYY-MM-DD  
**Purpose**: [One-line description]  
**Target Agent**: [GitHub Copilot | ChatGPT | Custom]  
**Status**: 🟢 Active | 🟡 Draft | 🔴 Deprecated

---

## 🧠 Context

### Cognitive Brain References
- [Cognitive Map](../system/CODEBASE_COGNITIVE_MAP.md) - System architecture
- [Dashboard](../system/CODEBASE_DASHBOARD.md) - Current status
- [Roadmap](../ROADMAP.md) - Planned work

### Prerequisites
- Requirement 1
- Requirement 2

---

## 🎯 Objective

[Clear, measurable goal statement]

---

## 📋 Instructions

### Phase 1: [Phase Name]
1. Step 1
2. Step 2

### Phase 2: [Phase Name]
1. Step 1
2. Step 2

---

## ✅ Validation

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Quality Checks
```bash
# Validation commands
```

---

## 📚 Related

- [Related Prompt`other_prompt.md` (placeholder)
- [Documentation`../path/to/doc.md` (placeholder)

---

**Maintained by**: [Team/Owner]
```

---

## 🎨 Prompt Design Guidelines

### 1. Context First

**Always include** cognitive brain references:
```markdown
## 🧠 Context

Start by loading the cognitive brain:
1. [Cognitive Map](../system/CODEBASE_COGNITIVE_MAP.md) - Understand architecture
2. [Dashboard](../system/CODEBASE_DASHBOARD.md) - Check current status
3. [Roadmap](../ROADMAP.md) - See planned work
```

### 2. Clear Objectives

**Be specific** about goals:
```markdown
## 🎯 Objective

Increase test coverage from 72% to 80% by adding tests for:
- Uncovered branches in error handling
- Edge cases in data validation
- Integration paths in API endpoints

Success metric: `pytest --cov --cov-fail-under=80` passes
```

### 3. Phased Instructions

**Break work** into logical phases:
```markdown
## 📋 Instructions

### Phase 1: Analysis (10K tokens)
1. Run coverage report
2. Identify gaps
3. Prioritize modules

### Phase 2: Implementation (30K tokens)
1. Add tests for priority 1 modules
2. Validate coverage improvement
3. Commit changes

### Phase 3: Validation (5K tokens)
1. Run full test suite
2. Check coverage metrics
3. Update documentation
```

### 4. Validation Criteria

**Define success** measurably:
```markdown
## ✅ Validation

### Acceptance Criteria
- [ ] Coverage ≥ 80%
- [ ] All tests passing
- [ ] No new warnings
- [ ] Documentation updated

### Quality Checks
```bash
pytest --cov=src --cov-fail-under=80
ruff check src/
mypy src/
```
```

### 5. Duration Awareness

**Include token budgets** for each phase:
```markdown
### Token Budget

| Phase | Estimated Tokens | Duration |
|-------|------------------|----------|
| Analysis | 5K-10K | 5-10 min |
| Implementation | 20K-40K | 20-40 min |
| Validation | 5K-10K | 5-10 min |
| **Total** | **30K-60K** | **30-60 min** |
```

---

## 🔄 Version Control

### Semantic Versioning

- **Major (X.0.0)**: Breaking changes, complete restructure
- **Minor (X.Y.0)**: New features, significant additions
- **Patch (X.Y.Z)**: Bug fixes, clarifications

### Update Process

1. **Update the prompt** file
2. **Increment version** number
3. **Update "Last Updated"** date
4. **Document changes** in prompt (optional changelog section)
5. **Test the prompt** with target agent
6. **Commit with** descriptive message

---

## 🧪 Testing Prompts

### Before Committing

1. **Test with target agent**:
   ```
   Copy prompt → Paste in agent interface → Execute
   ```

2. **Verify cognitive brain links**:
   ```bash
   # Check all markdown links
   python scripts/maintenance/check_doc_links.py --report /tmp/prompt_links.md
   ```

3. **Validate examples**:
   ```bash
   # Run any code examples in prompt
   python -c "$(grep -A 5 '```python' prompt.md | grep -v '```')"
   ```

### After Deployment

1. **Collect feedback** from agent sessions
2. **Iterate on** unclear instructions
3. **Update** based on common issues
4. **Maintain** version history

---

## 📊 Prompt Effectiveness Metrics

### Track These Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Completion Rate** | >90% | Agent completes all phases |
| **Time Accuracy** | ±20% | Actual vs estimated tokens |
| **Quality** | >95% | Outputs meet acceptance criteria |
| **Reusability** | >3 uses | Prompt used 3+ times successfully |

### Continuous Improvement

1. **Monthly review** of all prompts
2. **Update** based on agent feedback
3. **Archive** unused prompts to `archive/`
4. **Create new** prompts for emerging patterns

---

## 🎯 Creating New Prompts

### Checklist

- [ ] Choose clear, descriptive title
- [ ] Follow template standard v2.0
- [ ] Include cognitive brain references
- [ ] Define specific objective
- [ ] Break into phases with token budgets
- [ ] Add validation criteria
- [ ] Test with target agent
- [ ] Add to this README
- [ ] Commit with version 1.0.0

### Template

```bash
# Copy template
cp docs/prompts/TEMPLATE_PROMPT.md docs/prompts/NEW_PROMPT.md

# Edit new prompt
vim docs/prompts/NEW_PROMPT.md

# Test
# ... test with agent ...

# Commit
git add docs/prompts/NEW_PROMPT.md
git commit -m "docs: Add new prompt for [purpose]"
```

---

## 📚 Related Documentation

- [Agent Continuation Protocol](../workflows/AGENT_CONTINUATION_PROTOCOL.md) - Session handoff
- [Cognitive Brain](../system/) - Context system
- [Master Index](../MASTER_INDEX.md) - Documentation hub

---

## 🤝 Contributing

See [Contributing Guide](../CONTRIBUTING.md) for:
- How to propose new prompts
- Prompt review process
- Quality standards

---

**Maintained by**: AI Agent Team  
**Questions?**: Open an issue with tag `prompts`
