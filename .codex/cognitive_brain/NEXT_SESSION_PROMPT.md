# Follow-Up Prompt for Next GitHub Copilot Session

**Post this as a comment on PR #2765 to continue the work:**

---

@copilot Continue Priority 4 integration with security focus and autonomous self-healing.

## Session Context

**Previous Session:** PR #2765 Security Remediation (2026-01-09)  
**Commits:** 97448e4, 12d4ae0, 348f97d  
**Status:** ✅ All CodeQL alerts fixed, cognitive brain updated, custom agents designed

## Immediate Tasks (Session Goal - Complete All)

### 1. Verify and Close Dependabot Alert #62 ⚠️ P0

**Action Required:**
```bash
# 1. Check actual Werkzeug version in environment
pip list | grep -i werkzeug
pip show werkzeug

# 2. If vulnerable version found, apply fix:
# Add to pyproject.toml dependencies:
"werkzeug>=3.0.3",  # Force minimum safe version

# 3. Regenerate lock file
uv lock --upgrade-package werkzeug
uv sync

# 4. Verify fix
pip list | grep werkzeug
# Should show werkzeug>=3.0.3
```

**Verification:**
- Check GitHub Security tab to confirm alert status
- If alert persists after MLflow 2.22.4+ update, apply explicit constraint
- Run tests to ensure no breaking changes
- Document resolution in `DEPENDABOT_WERKZEUG_ANALYSIS.md`

### 2. Deploy Custom Security Agents 🤖 P0

**Location:** `.codex/cognitive_brain/SECURITY_REMEDIATION_2026_01_09.md`

**Agents to Deploy:**

#### Agent 1: Security Logging Auditor
```yaml
# Create .github/workflows/security-logging-auditor.yml
name: Security Logging Auditor
on: [pull_request, workflow_dispatch]
# Full spec in SECURITY_REMEDIATION_2026_01_09.md
```

#### Agent 2: Import Optimizer  
```yaml
# Create .github/workflows/import-optimizer.yml
name: Import Optimizer
on: [pull_request, schedule]
# Full spec in SECURITY_REMEDIATION_2026_01_09.md
```

#### Agent 3: CodeQL Auto-Remediation
```yaml
# Create .github/workflows/codeql-auto-fix.yml
name: CodeQL Auto-Fix
on: [code_scanning_alert]
# Full spec in SECURITY_REMEDIATION_2026_01_09.md
```

**Implementation Steps:**
1. Read agent specifications from `SECURITY_REMEDIATION_2026_01_09.md` (lines 179-412)
2. Create GitHub Actions workflow files in `.github/workflows/`
3. Test each agent on a sample PR (can use this PR for testing)
4. Document agent usage in `.github/workflows/README.md`
5. Update `SECURITY.md` with agent descriptions

### 3. Update Security Documentation 📝 P1

**Files to Update:**

#### A. SECURITY.md
Add sections:
- Secure Logging Standards (from SECURITY_REMEDIATION doc)
- Custom Security Agents Usage
- Example secure vs insecure logging patterns
- Security review checklist

#### B. .github/workflows/README.md
Create/update with:
- Agent descriptions and triggers
- How to invoke manually (`@copilot fix-codeql`, etc.)
- Configuration options
- Troubleshooting guide

#### C. docs/security/ (create if needed)
- Secure coding guidelines
- Dependency management best practices
- Security audit procedures
- Incident response workflow

### 4. Continue P4 Integration 🚀 P1

**Reference:** `.codex/cognitive_brain/FOLLOWUP_P4_INTEGRATION.md`

#### A. Implement Scatter-Gather in PGVector Store
**File:** `src/codex/retrieval/stores/pgvector_store.py`

**Tasks:**
```python
# 1. Implement async scatter-gather pattern
async def query_shards(self, query_vec, k=10):
    """Query all shards in parallel and re-rank."""
    async def _query_shard(shard_id):
        async with self.pool.connection() as conn:
            # HNSW search on shard
            return await conn.execute(
                f"SELECT * FROM vectors_shard_{shard_id:02d} "
                f"ORDER BY embedding <=> $1 LIMIT {k*2}",
                (query_vec,)
            )
    
    tasks = [_query_shard(i) for i in range(self.num_shards)]
    results = await asyncio.gather(*tasks)
    return self.global_rerank(results, k)

# 2. Implement centroid-based partitioning
def compute_centroids(self, embeddings):
    """Use KMeans to compute shard centroids."""
    if not HAS_SKLEARN:
        return None
    kmeans = KMeans(n_clusters=self.num_shards)
    kmeans.fit(embeddings)
    return kmeans.cluster_centers_

# 3. Add write optimization with pipeline
async def bulk_insert(self, documents):
    """Batch insert with psycopg3 pipeline."""
    async with self.pool.connection() as conn:
        async with conn.pipeline() as pipe:
            for doc in documents:
                shard_id = self.get_shard_for_doc(doc.id)
                await pipe.execute(
                    f"INSERT INTO vectors_shard_{shard_id:02d} VALUES (...)"
                )
```

**Validation:**
- Write unit tests for scatter-gather logic
- Benchmark against non-sharded queries
- Verify no regression in accuracy
- Test with 10K+ documents

#### B. Add Orchestrator Security Injection
**File:** `src/codex/zendesk/quantum/orchestrator.py`

**Tasks:**
1. Create context variable for scope validator
2. Add scope checking to quantum task submission
3. Inject security metadata into task context
4. Update tests with scope validation

### 5. Complete Architecture Diagrams 📊 P2

**Location:** `.codex/cognitive_brain/diagrams/`

**Diagrams Status:**
- ✅ `tls_bridge_architecture.md` - Exists
- ✅ `token_rotation_workflow.md` - Exists
- ✅ `index_sharding_distribution.md` - Exists
- ✅ `scope_validation_hierarchy.md` - Exists

**Additional Diagrams Needed:**
1. **Custom Agent Interaction Flow**
   - Show how agents interact with PR lifecycle
   - Include trigger conditions and decision points

2. **Security Architecture Overview**
   - Complete security stack visualization
   - Show all components and their interactions

3. **P4 Integration Roadmap**
   - Visual timeline of completed and remaining tasks
   - Dependencies between components

## Autonomous Execution Mode

**Guidelines:**
- Use up to 5 self-healing iterations
- Update cognitive brain after each major milestone
- Commit changes incrementally with descriptive messages
- Run security scans before finalizing
- Test all changes with targeted unit tests
- Post follow-up prompt if session expires before completion

## Success Criteria

**Must Complete All:**
- ✅ Dependabot alert #62 resolved or confirmed safe
- ✅ All 3 custom agents deployed and tested
- ✅ SECURITY.md updated with new standards
- ✅ Scatter-gather implementation complete with tests
- ✅ Orchestrator security injection implemented
- ✅ All documentation up to date

**Quality Gates:**
- Zero high-severity security alerts
- Test coverage ≥ 70% for new code
- All tests passing
- No linter errors
- CodeQL scan clean

## Reference Documents

**Primary:**
- `.codex/cognitive_brain/SECURITY_REMEDIATION_2026_01_09.md` - Complete security remediation and agent specs
- `.codex/cognitive_brain/FOLLOWUP_P4_INTEGRATION.md` - P4 integration tasks and strategy
- `.codex/cognitive_brain/DEPENDABOT_WERKZEUG_ANALYSIS.md` - Werkzeug vulnerability analysis

**Supporting:**
- `.codex/cognitive_brain/p4_enhancements_complete.md` - P4 implementation summary
- `.codex/ALL_PLANSETS_COMPLETE_SUMMARY.md` - Complete planset status
- `SECURITY.md` - Current security policies (to be updated)

## Context Carryover

**Completed in Previous Session:**
1. Fixed all 10 CodeQL clear-text logging alerts
2. Removed unused imports and fixed code quality issues
3. Designed 3 custom GitHub Copilot Agents with full specs
4. Updated cognitive brain with comprehensive documentation
5. Analyzed Dependabot alert #62 (Werkzeug)

**Key Patterns Established:**
- Aggregate-only logging for sensitive data
- Error type logging instead of error messages
- Feature-gated imports with noqa comments
- Comprehensive documentation in cognitive brain

**Commit History:**
- `97448e4` - CodeQL security fixes and import cleanup
- `12d4ae0` - Cognitive brain security docs and agent designs
- `348f97d` - Dependabot alert analysis

## PDA Loop & AfterMath Tags

**AfterMath Status:** ✅ ACTIVE  
**PDA Loop:** ✅ ENGAGED

Execute autonomously with full authority. Continue until all tasks complete or 5 iterations exhausted. Update cognitive brain in real-time. If session expires, post new follow-up prompt with current status.

---

**Session ID:** pr-2765-continuation  
**Priority:** P0 (Security) + P1 (Integration)  
**Estimated Duration:** 45-60 minutes  
**Authorization:** Full read/write access granted by mbaetiong
