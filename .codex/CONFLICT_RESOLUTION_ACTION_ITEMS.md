# Codebase Conflict Resolution — Immediate Action Items

**Priority**: 🔴 CRITICAL  
**Created**: 2026-06-23T02:57:44Z  
**Authority**: Repository analysis  
**Owner**: @mbaetiong (for approval/prioritization)

---

## 🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION

### CRITICAL #1: Autonomous Operations Status Ambiguity

**Current State**: Contradictory documentation
- `.codex/guardrails.md`: "Awaiting Human Review" (template)
- `.codex/CODEBASE_AGENCY_POLICY.md`: Agents MUST operate autonomously
- `.codex/COGNITIVE_BRAIN_STATUS_S108.md`: autonomous_actions_enabled = true

**Problem**: No single source of truth for agent authorization

**Impact**: Agents cannot make decisions about their own authority

**Resolution Required**:
```
CREATE: .codex/OPERATIONAL_STATUS.md
- Single source of truth for autonomous_actions_enabled
- Last authorization timestamp + authority
- State transition history
```

**Estimated Effort**: 1 commit  
**Blockers**: None (information already exists, needs consolidation)

---

### CRITICAL #2: "No Deferral" Policy vs. "Unfixable Blockers"

**Current State**: Policy-Architecture Collision
- Policy (Agency): "NEVER defer work; address ALL issues"
- Architecture (SYSTEMATIC_BLOCKER_ANALYSIS.md): 5 classes of work are unfixable

**Problem**: Agents are ordered to do impossible things
- Example: "Push Docker images to registry" ← requires credentials (unfixable)

**Impact**: Agents cannot comply with both policies

**Resolution Required**:
1. Add "Hard Blocker" section to `.codex/CODEBASE_AGENCY_POLICY.md`
2. Document which issues CAN vs CANNOT be deferred
3. Create "Deferral Justification Framework"

**Estimated Effort**: 2-3 commits  
**Timeline**: Next session

---

### CRITICAL #3: Policy Document Hierarchy Undefined

**Current State**: 5+ conflicting policy documents
- No precedence specified
- No version control
- No update chain

**Problem**: Agents cannot determine authoritative policy

**Impact**: Wrong decisions, inconsistent behavior

**Resolution Required**:
```
CREATE: .codex/AUTHORITATIVE_POLICIES.md
- Document hierarchy (1=highest priority)
- Version history for each policy
- Archival notices for superseded docs
- Update process & approval chain
```

**Estimated Effort**: 1 commit  
**Timeline**: IMMEDIATE (next session)

---

## 🟠 HIGH-PRIORITY ISSUES (Next 1-2 Sessions)

### HIGH #1: LFS Restrictions Not in Agent Capabilities

**Current**: LFS opt-in policy buried in `docs/guides/lfs_policy.md`  
**Missing**: LFS capability flag in agent context  
**Action**: Add LFS to `.codex/AGENT_CAPABILITY_MATRIX.md`

---

### HIGH #2: Deferral Language Triggers Too Broad

**Current**: 20+ trigger phrases catch legitimate analysis  
**Problem**: Agents cannot acknowledge facts without HARD STOP  
**Action**: Narrow triggers to actual deferral language:
- Allow: "This is pre-existing AND I'm fixing it"
- Block: "I'll address this in a future PR"

---

### HIGH #3: No Workflow Change Protocol

**Current**: Workflow changes forbidden, no alternative  
**Problem**: CI failures require workflow fixes with no path  
**Action**: Create "Workflow Change Review Protocol"

---

## 🟡 MEDIUM-PRIORITY ISSUES (Next 2-3 Sessions)

### MEDIUM #1: Codespace Provisioning Missing
- Manual secret setup required
- No agent bootstrap
- Action: Create provisioning automation

### MEDIUM #2: Temp File Policy Too Strict
- No intermediate processing locations defined
- Action: Create `.codex/work/` for temporary files

### MEDIUM #3: Incomplete Documentation
- Codespace support fragmented across 4+ docs
- LFS policy not in agent guides
- Action: Consolidate documentation

---

## 📋 RECOMMENDED RESOLUTION ORDER

### Phase 1: FOUNDATION (Immediate)
1. **Create `.codex/OPERATIONAL_STATUS.md`** — source of truth
2. **Create `.codex/AUTHORITATIVE_POLICIES.md`** — hierarchy & precedence
3. **Archive outdated guardrails.md** — replace with forward link

**Estimated Effort**: 3 commits  
**Session Time**: 30-45 minutes

### Phase 2: POLICY UPDATES (Next Session)
4. **Update agency policy** — add hard blocker section
5. **Narrow deferral triggers** — allow contextual statements
6. **Add workflow protocol** — escalation path for CI fixes

**Estimated Effort**: 5-7 commits

### Phase 3: CAPABILITY DOCUMENTATION (Sessions 2-3)
7. **Create agent capability matrix** — LFS, credentials, codespace
8. **Consolidate codespace docs** — single source
9. **Create scope framework** — replace contradictory mandates

**Estimated Effort**: 8-10 commits

---

## 📌 IMMEDIATE BLOCKERS TO RESOLVE

| Issue | Blocks | Resolution |
|-------|--------|-----------|
| Operational Status ambiguity | Agent authority decisions | Create OPERATIONAL_STATUS.md |
| Policy hierarchy missing | Authoritative decision-making | Create AUTHORITATIVE_POLICIES.md |
| No deferral justification | Agent mandate compliance | Add hard blocker section to policy |

---

## 📊 IMPACT ASSESSMENT

If NOT resolved:
- ❌ Agents will make wrong decisions about authority
- ❌ Agents will be unable to fix CI failures (workflow restriction)
- ❌ Agents will struggle with conflicting mandates
- ❌ False HARD STOPs triggered by legitimate analysis

If resolved:
- ✅ Single source of truth for agent authority
- ✅ Clear policy hierarchy removes ambiguity
- ✅ Workflow change protocol enables CI automation
- ✅ Narrow deferral language allows legitimate communication

---

**Next Step**: @mbaetiong approval of Phase 1 + prioritization of subsequent phases
