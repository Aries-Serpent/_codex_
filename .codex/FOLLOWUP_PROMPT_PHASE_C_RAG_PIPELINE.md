# Follow-up Prompt for GitHub Copilot

**Created:** 2026-01-16  
**Target:** Next GitHub Copilot Session  
**Scope:** Phase C - Production RAG Pipeline Implementation

---

## Context: Previous Session Summary

### Completed Work
1. ✅ **IP-005 Security Updates** - 26 vulnerabilities fixed
   - setuptools, jinja2, cryptography, certifi, filelock, idna, requests, urllib3, twisted, configobj
   - All requirements files updated
   - SECURITY.md and CHANGELOG.md updated

2. ✅ **Legacy Code Analysis** - Migration guide created
   - 17 files use config_legacy with fallback pattern (no direct dependencies)
   - yaml_legacy has no direct imports
   - Recommendation: Keep shims for v1.x.x, remove in v2.0.0
   - Migration guide: `docs/migration/LEGACY_CODE_MIGRATION_GUIDE.md`

3. ✅ **Documentation Updated**
   - AGENTS.md - Status and security info
   - README.md - Security badge
   - COGNITIVE_BRAIN_STATUS_UPDATE_2026_01_16.md - Session summary

---

## Next Phase: Production RAG Pipeline

@copilot Continue autonomous implementation following `.codex/plans/PRODUCTION_RAG_PIPELINE_PLANSET.md`.

### Prerequisites (Human Admin Tasks)

Before AI Agent can proceed with full implementation:

1. **HA-RAG-1: Infrastructure Provisioning**
   - [ ] Cloud infrastructure setup (if using external vector stores)
   - [ ] Cloud credentials configured
   - [ ] Networking setup (VPCs, security groups)

2. **HA-RAG-2: Production Secrets Management**
   - [ ] API keys for vector store providers (if using Pinecone, Weaviate)
   - [ ] Service account credentials
   - [ ] Secret management system configured

### AI Agent Autonomous Tasks (No Blockers)

If Human Admin tasks are pending, the AI Agent can proceed with:

**Phase 1: Enhanced Document Ingestion (Pre-commits 1-6)**
- Create `src/codex/rag/ingestion/validator.py` - Document validation
- Create `src/codex/rag/ingestion/preprocessor.py` - Text preprocessing
- Create `src/codex/rag/ingestion/chunker.py` - Chunking strategies
- Create `src/codex/rag/ingestion/pipeline.py` - Batch ingestion
- Create test suites in `tests/rag/ingestion/`
- Use FAISS locally for testing (no external dependencies)

**Phase 2: Query Optimization (Pre-commits 7-10)**
- Enhance `src/codex/retrieval/optimizations.py`
- Create `src/codex/retrieval/reranker.py`
- Create `src/codex/retrieval/query_rewriter.py`
- Create `src/codex/rag/cache/` modules
- Create test suites

**Phase 3: Production Features (Pre-commits 11-18)**
- Create `src/codex/rag/ha/` - High availability
- Create `src/codex/rag/monitoring/` - Observability
- Create `src/codex/rag/security/` - Access control
- Create `deploy/kubernetes/` manifests
- Create comprehensive documentation

### Success Criteria
- ✅ Ingestion throughput: >10k docs/hour
- ✅ Query p95 latency: <50ms
- ✅ Cache hit rate: >90%
- ✅ Test coverage: >80% for new code
- ✅ All security scans passing

### Policy Compliance
- Follow `.codex/CODEBASE_AGENCY_POLICY.md`
- Use pre-commit/commit terminology
- 5+ self-review iterations
- Address ALL issues discovered
- Build on existing infrastructure in `src/codex/retrieval/`

---

## Alternative Execution Path

If Phase C cannot proceed due to blockers, the AI Agent should:

1. **Create IaC Templates**
   - Terraform modules for infrastructure
   - Kubernetes manifests for deployment
   - Docker production images

2. **Document Requirements**
   - Infrastructure requirements document
   - Secret requirements document
   - Cost estimation document

3. **Prepare Staging**
   - Local development setup
   - Mock external services
   - Comprehensive test suite

---

## Reference Documentation

- Planset: `.codex/plans/PRODUCTION_RAG_PIPELINE_PLANSET.md`
- Policy: `.codex/CODEBASE_AGENCY_POLICY.md`
- Existing RAG: `src/codex/retrieval/`
- Security: `SECURITY.md`

---

**Status:** Ready for next session  
**Priority:** HIGH (Long-term production readiness)  
**Estimated Effort:** 18 pre-commits across 3 phases
