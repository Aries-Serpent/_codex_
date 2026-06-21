# 📊 REAL-TIME MONITORING GUIDE
## Campaign Execution Dashboard

**Campaign Status:** 🟢 LIVE (4/5 agents active)  
**Campaign Start:** 2026-06-21T18:08:30Z  
**Next Checkpoint:** 2026-06-21 ~21:00Z  

---

## ACTIVE AGENTS - LIVE STATUS

### How to Check Agent Status

```bash
# Check individual agent (blocks until complete or timeout)
read_agent agent_id=lane-1-coverage-expansion wait=false timeout=30

# Check all agents
list_agents include_completed=false

# Wait for specific agent with detailed output
read_agent agent_id=lane-1-coverage-expansion wait=true timeout=300
```

---

## AGENT MONITORING SCHEDULE

### Recommended Check Intervals

| Time | Action | Command |
|------|--------|---------|
| Now (18:09) | Log initial status | `list_agents` |
| 18:45 | Mid-phase check | `read_agent agent_id=lane-1-coverage-expansion` |
| 19:30 | Pre-checkpoint review | `read_agent` for all 4 agents |
| **21:00** | **Phase 1A Checkpoint** | Create `.codex/PHASE_1A_CHECKPOINT.md` |
| 22:00 | Phase 1 completion check | All agents should be done/reporting |
| 00:08 | Phase 1 complete | Scale LANE 5 when others finish |

---

## METRICS TO TRACK

### Real-Time Dashboard Metrics

Update `.codex/CAMPAIGN_PROGRESS_DASHBOARD.md` with these metrics as agents report:

| Metric | LANE | Current | Target | Source |
|--------|------|---------|--------|--------|
| **Coverage %** | 1 | 35% | 22%+ | LANE 1 checkpoint |
| **Tests Added** | 1 | 0 | 285+ | LANE 1 checkpoint |
| **Security Issues** | 2 | 0 | 0 | LANE 2 checkpoint |
| **CI Failure Rate %** | 3 | 1.5% | <1% | LANE 3 checkpoint |
| **Doc Accuracy %** | 4 | 93% | 100% | LANE 4 checkpoint |
| **Governance Gates** | 5 | 32/32 | 32/32 | LANE 5 checkpoint |

---

## CHECKPOINT CREATION WORKFLOW

### When to Create Checkpoints

1. **Phase 1A Checkpoint (~21:00Z)** — When LANE 1 reaches ~50% completion
   - LANE 1: 140+ tests added
   - LANE 2: Security scan ~50% done
   - LANE 3: Workflow validation starting
   - LANE 4: Documentation audit ~25% done

2. **Phase 1 Complete Checkpoint (~00:08Z)** — When all 4 agents finish Phase 1
   - LANE 1: 285+ tests, coverage gain confirmed
   - LANE 2: Audit results published
   - LANE 3: Stability targets set
   - LANE 4: Documentation audit complete

### How to Create a Checkpoint

```bash
# Step 1: Read agent outputs
read_agent agent_id=lane-1-coverage-expansion wait=false
read_agent agent_id=lane-2-security-audit wait=false
read_agent agent_id=lane-3-ci-stabilization wait=false
read_agent agent_id=lane-4-documentation wait=false

# Step 2: Extract metrics from outputs
# (Coverage %, tests, issues, failure rate, docs %)

# Step 3: Copy template and fill in
# Source: .codex/CHECKPOINT_MONITORING_TEMPLATE.md
# Destination: .codex/PHASE_N_CHECKPOINT_REPORT.md

# Step 4: Commit checkpoint
git add .codex/PHASE_N_CHECKPOINT_REPORT.md
git commit -m "Checkpoint: Phase N metrics and progress"
git push

# Step 5: Update main dashboard
# Edit: .codex/CAMPAIGN_PROGRESS_DASHBOARD.md
# Update: Real-time metrics section
```

---

## ISSUE DETECTION & ESCALATION

### Warning Signs to Watch For

| Warning | Severity | Action |
|---------|----------|--------|
| Agent timeout (>30 min no output) | 🔴 CRITICAL | Escalate to @mbaetiong |
| Coverage plateau at <20% | 🟡 HIGH | Check agent logs, may need manual intervention |
| Security vulnerabilities found | 🔴 CRITICAL | Escalate immediately |
| CI failure rate >5% | 🟡 HIGH | Switch to ci-emergency-response-agent |
| Documentation accuracy <50% | 🟡 MEDIUM | Increase focus on link validation |

### Escalation Process

```bash
# 1. Document issue with full context
# 2. Create GitHub issue tagged [ESCALATION]
# 3. Tag @mbaetiong
# 4. Include agent ID and error output
# 5. Suggest mitigation steps
```

---

## LANE-BY-LANE MONITORING

### LANE 1: Coverage Expansion
**Agent:** `lane-1-coverage-expansion`  
**Key Metrics:** Coverage %, tests added, mutation kill rate  
**Success:** 285+ tests passing, +2.22pp coverage gain

```bash
# Monitor coverage progress
read_agent agent_id=lane-1-coverage-expansion wait=false

# Expected output includes:
# - Tests generated: [count]
# - Coverage: [%]
# - Pass rate: [%]
# - Mutations: [kill rate]
```

### LANE 2: Security Audit
**Agent:** `lane-2-security-audit`  
**Key Metrics:** Critical/high issues, CVEs, secrets  
**Success:** 0 critical/high issues maintained

```bash
# Monitor security audit
read_agent agent_id=lane-2-security-audit wait=false

# Expected output includes:
# - CodeQL issues: [count]
# - CVEs found: [count]
# - Secrets detected: [count]
# - SBOM generated: [yes/no]
```

### LANE 3: CI/CD Stabilization
**Agent:** `lane-3-ci-stabilization`  
**Key Metrics:** Failure rate, workflow errors, cascade prevention  
**Success:** <1% failure rate, zero cascades

```bash
# Monitor CI stabilization
read_agent agent_id=lane-3-ci-stabilization wait=false

# Expected output includes:
# - Workflows fixed: [count]
# - Actions updated: [count]
# - Failure rate: [%]
# - Cascades prevented: [count]
```

### LANE 4: Documentation
**Agent:** `lane-4-documentation`  
**Key Metrics:** Accuracy %, broken links, pages updated  
**Success:** 100% accuracy, zero broken links

```bash
# Monitor documentation
read_agent agent_id=lane-4-documentation wait=false

# Expected output includes:
# - Accuracy: [%]
# - Links validated: [count]
# - Pages updated: [count]
# - GitHub Pages: [deployed/failed]
```

### LANE 5: Production Readiness (Queued)
**Agent:** `lane-5-production-readiness`  
**Key Metrics:** Readiness score, checklist items, sign-off  
**Success:** 100% readiness, deployment approved

```bash
# Will launch when 4 agents free up
# Expected output includes:
# - Readiness: [%]
# - Checklist: [#/100+]
# - QA items: [#/100+]
# - Sign-off: [approved/pending]
```

---

## QUICK REFERENCE COMMANDS

```bash
# Check all agents at once
list_agents include_completed=false

# Get detailed status for single agent
read_agent agent_id=lane-1-coverage-expansion wait=false timeout=30

# Wait for agent completion (blocks up to 5 min)
read_agent agent_id=lane-1-coverage-expansion wait=true timeout=300

# Update campaign dashboard
# Manually edit: .codex/CAMPAIGN_PROGRESS_DASHBOARD.md

# Create new checkpoint
cp .codex/CHECKPOINT_MONITORING_TEMPLATE.md .codex/PHASE_N_CHECKPOINT_REPORT.md
# Edit and commit

# Update progress in PR
engine-tools-report_progress \
  commitMessage="Phase N checkpoint: metrics update" \
  prDescription="[x] LANE 1 active\n[ ] LANE 2..."
```

---

## EXPECTED OUTPUT STRUCTURE

Each agent checkpoint report should include:

```markdown
# LANE N Checkpoint Report
- Agent: [name]
- Status: ✅ COMPLETE | ⏳ IN PROGRESS | 🔴 BLOCKED
- Duration: [time elapsed]
- Key Metrics:
  - Metric 1: [value] (target: [target])
  - Metric 2: [value] (target: [target])
- Deliverables:
  - [Item 1]: [status]
  - [Item 2]: [status]
- Next Steps: [description]
- Issues: [count] (if any)
```

---

## DASHBOARD UPDATE SCHEDULE

| Time | Update | Section |
|------|--------|---------|
| 18:30 | Initial baseline | Real-time metrics |
| 19:00 | Phase 1A progress | Lane status |
| 19:30 | Pre-checkpoint review | Metrics table |
| **21:00** | **Phase 1A checkpoint** | Full checkpoint section |
| 22:00 | Phase 1 completion | Lane summaries |
| 00:08 | Scale LANE 5 | Activate LANE 5 row |
| Next day | Phase consolidation | Consolidation report |

---

## TROUBLESHOOTING

### Agent Not Responding

```bash
# Check if agent is running
list_agents include_completed=false

# If missing, may have completed or failed
# Check recent commits for results

# If truly stuck, escalate to @mbaetiong
```

### Dashboard Not Updating

```bash
# Manually edit: .codex/CAMPAIGN_PROGRESS_DASHBOARD.md
# Update real-time metrics section with latest values
# Commit changes
```

### Checkpoint Not Creating

```bash
# Use template: .codex/CHECKPOINT_MONITORING_TEMPLATE.md
# Fill in metrics from agent outputs
# Save as: .codex/PHASE_N_CHECKPOINT_REPORT.md
# Commit and push
```

---

**Last Updated:** 2026-06-21T18:09:30Z  
**Next Check:** 2026-06-21T18:45:00Z  
**Checkpoint Due:** 2026-06-21T21:00:00Z
