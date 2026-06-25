# 🔧 AGENT DOCUMENTATION MAINTENANCE GUIDE

**Version:** 2.0.0  
**Generated:** 2026-06-20T06:52:59.400173  
**Purpose:** How to maintain agent documentation over time

---

## Overview

This guide defines the ongoing maintenance procedures for the 159-agent ecosystem documentation.

---

## PART 1: REGISTRY UPDATES

### When to Update AGENT_REGISTRY.yaml

**Update when:**
- New agent is created
- Agent is deprecated or archived
- Agent capabilities change
- Agent moves to different category
- Agent model preference changes
- Performance characteristics change significantly

### How to Update

**Step 1: Edit AGENT_REGISTRY.yaml**
```yaml
- id: new-agent-id
  name: New Agent Name
  version: 1.0.0
  directory: .github/agents/new-agent-id
  file: new-agent-id.md
  status: active  # or: archived
  maturity: production
  category: ci_cd  # or appropriate category
  description: Clear description of what agent does
  capability_tags:
    - capability1
    - capability2
```

**Step 2: Update Catalog Documents**
```bash
# Run: python3 .github/agents/registry-generator.py
# This regenerates all catalog markdown files
```

**Step 3: Commit & Push**
```bash
git add .github/agents/AGENT_REGISTRY.yaml
git add .codex/AGENT_ECOSYSTEM_CATALOG.md
git commit -m "docs: Register new agent [agent-id]"
git push
```

---

## PART 2: VERSION CONTROL FOR AGENT CAPABILITIES

### Capability Versioning

Each agent should track its capabilities version:

```yaml
capability_version: 2.1.0
capabilities:
  v2.0.0: [initial capabilities]
  v2.1.0: [added new capability X]
```

### When Capabilities Change

**Major (v X.0.0):** Fundamental capability changes
- Agent consolidation (e.g., test-coverage-agent → unified-coverage-agent)
- New primary responsibility
- Breaking API changes

**Minor (v X.Y.0):** New capabilities added
- New feature flags
- Extended analysis options
- Additional integrations

**Patch (v X.Y.Z):** Bug fixes
- Accuracy improvements
- Performance optimizations
- Documentation clarifications

---

## PART 3: DEPRECATION PROCESS

### Deprecation Tiers

**Tier 1: Announcement (Week 1)**
- Mark agent as deprecated in AGENT_REGISTRY.yaml
- Add deprecation notice to agent documentation
- Identify replacement agent
- Notify users via changelog

**Tier 2: Soft Removal (Week 4)**
- Agent still callable but returns deprecation warning
- Users must manually migrate scripts
- Old agent IDs still recognized
- Documentation points to replacements

**Tier 3: Hard Removal (Week 8)**
- Agent completely removed from registry
- API returns 410 Gone error
- Historical data archived
- No way to call archived agent

### Example Deprecation Timeline

```
June 20, 2026: coverage-gapfill-agent marked as deprecated
  Status: active → deprecated
  Replacement: unified-coverage-agent
  Users notified via CHANGELOG.md

July 1, 2026: Soft removal
  Agent still works but returns warning
  Error message: "Use unified-coverage-agent instead"
  CLI shows deprecation warning

August 1, 2026: Hard removal
  Agent completely removed
  API calls return 410 Gone
  Historical data in archive/
```

---

## PART 4: NEW AGENT ONBOARDING CHECKLIST

When adding a new agent, follow this checklist:

### Pre-Registration

- [ ] Agent code complete and tested
- [ ] Agent documentation written
- [ ] Agent has passable CI/CD tests
- [ ] Agent owner identified
- [ ] Agent category assigned
- [ ] Capability tags defined
- [ ] Model preference selected

### Registration

- [ ] Agent added to AGENT_REGISTRY.yaml
- [ ] Unique ID assigned (kebab-case)
- [ ] Maturity level set (production/beta/experimental)
- [ ] Integration points documented
- [ ] Capability tags populated
- [ ] Use case examples provided

### Documentation

- [ ] Updated AGENT_ECOSYSTEM_CATALOG.md
- [ ] Updated UNIFIED_ENTRY_POINTS_GUIDE.md (if applicable)
- [ ] Updated AGENT_SELECTION_DECISION_TREE.md (if new domain)
- [ ] Updated AGENT_PERFORMANCE_GUIDE.md
- [ ] Added CHANGELOG entry
- [ ] Added to appropriate domain cluster

### Testing

- [ ] Agent works with test data
- [ ] Agent integrates with orchestrator
- [ ] Agent documented in decision tree
- [ ] Agent performance characterized
- [ ] Agent patterns identified

### Launch

- [ ] PR created for new agent
- [ ] Code review completed
- [ ] Documentation reviewed
- [ ] Merged to main branch
- [ ] CHANGELOG updated
- [ ] Announced to team

---

## PART 5: ANNUAL REVIEW PROCESS

### Schedule

**Q2 Review (April-June):**
- Review agent catalog accuracy
- Update performance metrics
- Assess deprecation candidates
- Plan Q3-Q4 improvements

**Q3 Review (July-September):**
- Review security posture
- Consolidation opportunities
- Pattern updates
- Cost analysis

**Q4 Review (October-December):**
- Plan next year's roadmap
- Archive obsolete agents
- Refresh documentation
- Budget planning

### Annual Review Checklist

- [ ] Review all 159 agent definitions
- [ ] Update performance characteristics
- [ ] Identify low-usage agents (<5% usage)
- [ ] Identify consolidation opportunities
- [ ] Review deprecation timeline
- [ ] Update capability matrix
- [ ] Refresh domain clusters
- [ ] Plan new agents for next year
- [ ] Update cost projections
- [ ] Validate decision tree accuracy

### Example Annual Review Output

```
2026 Annual Review - Agent Ecosystem Health

Total Agents: 159 (145 active, 14 archived)
Active Usage: 78% of agents (112/145)
Low Usage (<5%): 22 agents (candidates for deprecation)
Consolidation Opportunities: 3 agent families
Proposed New Agents: 5 (CI health, ML ops, security, docs, testing)

Performance: Average 8 min/agent, 50% improvement from 2025
Cost: $3200/month agent operations (down 40% YoY)

Recommendations:
1. Archive 3 low-usage agents (coverage-gapfill, doc-quality-v1, etc)
2. Consolidate into 2 new unified agents
3. Add 5 new specialized agents for 2027
4. Refactor orchestrator for parallel execution
```

---

## PART 6: ARCHIVE MIGRATION GUIDE

### When Archiving Agents

**Archived agents move to:**
```
.codex/archived/
  ├── coverage-gapfill-agent/
  ├── test-coverage-agent/
  └── ... (other archived agents)
```

**Archive Checklist:**

- [ ] Agent marked as `status: archived` in AGENT_REGISTRY.yaml
- [ ] Agent documentation moved to `.codex/archived/`
- [ ] Migration guide created (→ replacement agent)
- [ ] Historical data preserved
- [ ] Deprecation notice added to main documentation
- [ ] CHANGELOG entry created
- [ ] Dependent workflows updated
- [ ] User notification sent

### Archive Metadata

Each archived agent should include:

```yaml
archived_agent:
  id: coverage-gapfill-agent
  archived_date: 2026-06-20
  reason: Consolidated into unified-coverage-agent
  replacement: unified-coverage-agent
  migration_guide: ARCHIVED_AGENTS_REFERENCE.md
  deprecation_timeline:
    soft_removal: 2026-07-01
    hard_removal: 2026-08-01
  historical_data: .codex/archived/coverage-gapfill-agent/
  contact: @mbaetiong
```

---

## PART 7: DOCUMENTATION ROLLOUT

### Documentation Updates

**Major Update (quarterly):**
- [ ] Regenerate full catalog
- [ ] Update all 8 framework documents
- [ ] Update decision tree
- [ ] Refresh performance metrics
- [ ] Create new CHANGELOG entry

**Minor Update (monthly):**
- [ ] Add new agents to catalog
- [ ] Update performance data
- [ ] Fix documentation errors
- [ ] Update examples

**Patch Update (as needed):**
- [ ] Fix typos
- [ ] Clarify examples
- [ ] Update links
- [ ] Add small use cases

### Rollout Checklist

- [ ] All documents regenerated
- [ ] Consistency checks pass
- [ ] Links validated
- [ ] Metadata accurate
- [ ] Version numbers updated
- [ ] Authority attribution present
- [ ] Committed to git
- [ ] CHANGELOG entry added
- [ ] Announcement sent

---

## PART 8: MAINTENANCE CADENCE

### Daily
- Monitor agent usage metrics
- Alert on failures
- Update performance data

### Weekly
- Review agent activity
- Update low-level documentation
- Fix emergent issues

### Monthly
- Update AGENT_REGISTRY.yaml
- Regenerate catalog (if changes)
- Update performance guide
- Review deprecation candidates

### Quarterly (Q1, Q2, Q3, Q4)
- Full framework review
- Update all 8 documents
- Deprecation wave (if needed)
- Performance analysis
- Budget review

### Annually (end of year)
- Comprehensive audit
- Archive review
- Roadmap planning
- Cost forecasting
- New agent planning

---

## PART 9: AUTOMATED MAINTENANCE TOOLS

### Validation Scripts

**Check registry validity:**
```bash
python3 .github/agents/validate-registry.py
# Checks: valid YAML, required fields, unique IDs, etc
```

**Generate documentation:**
```bash
python3 .github/agents/generate-docs.py
# Regenerates all 8 framework documents
```

**Check documentation freshness:**
```bash
python3 .github/agents/check-freshness.py
# Verifies links, updates timestamps, checks consistency
```

**Archive migration:**
```bash
python3 .github/agents/migrate-to-archive.py --agent coverage-gapfill-agent
# Moves agent to archive, updates all references
```

---

## PART 10: METRICS TO TRACK

### Agent Health Metrics

- **Usage Rate:** % of agents used per month
- **Performance:** Average runtime per agent
- **Cost:** Token usage per agent
- **Errors:** Failure rate per agent
- **Dependencies:** Cross-agent dependencies
- **Consolidation Candidates:** Agents with <5% usage

### Framework Metrics

- **Documentation Freshness:** Days since last update
- **Link Validity:** % broken links
- **Consistency:** Terminology consistency score
- **Completeness:** % of required documentation
- **Search Quality:** Search index relevance

### Reporting

**Dashboard:** Real-time metrics at `.codex/AGENT_METRICS_DASHBOARD.md`

**Reports:**
- Weekly: usage trends, failures, performance
- Monthly: consolidation candidates, cost analysis
- Quarterly: comprehensive audit, roadmap planning
- Annually: year-end review, next-year planning

---

## FAQ

**Q: How often should I update the catalog?**  
A: Monthly for performance data, quarterly for full reviews.

**Q: Can I deprecate an agent without replacement?**  
A: No. Always have a replacement agent ready before deprecating.

**Q: What if an agent isn't used much?**  
A: After 6 months of <5% usage, consider consolidation or archival.

**Q: How long is the deprecation timeline?**  
A: Standard: 6 weeks (Week 1: announce, Week 4: soft removal, Week 8: hard removal)

**Q: Who approves new agents?**  
A: Agent author + @mbaetiong (authority review)

**Q: Can users override deprecation warnings?**  
A: Not recommended, but possible via ENV override (not for production)

---

## METADATA

- **Generated:** 2026-06-20T06:52:59.400188
- **Authority:** @mbaetiong
- **Maintainers:** Agent ecosystem team
- **Review Frequency:** Quarterly
- **Next Review:** 2026-07-20
- **Next Annual Review:** 2026-12-31
