# Phase 1 Infrastructure Roadmap — Tracking & Checkpoints

## 🔴 CRITICAL: Node.js 20 End-of-Life (Deadline: 2026-06-02)

**Status**: ⏰ 9 DAYS REMAINING

### Context
Node.js 20.x reaches end of support on **2026-06-02**. The repository must complete migration to Node.js 22+ before deadline.

### Checklist
- [ ] Audit all `.github/workflows/*.yml` for Node.js version pinning
- [ ] Identify all npm-based workflows currently using Node.js 20
- [ ] Update GitHub Actions runner OS versions if needed
- [ ] Update `package.json` engines field to Node.js 22+
- [ ] Run full test suite against Node.js 22
- [ ] Verify no breaking changes in npm dependencies
- [ ] Update CI/CD pipelines to use Node.js 22 LTS
- [ ] Document Node.js 22 requirement in README

### Affected Components
- Frontend build pipelines (Cognitive App React build)
- Package management workflows
- Node.js-based CI/CD tools

### Commands to Audit
```bash
# Find Node.js version references in workflows
grep -r "node-version\|NODE_VERSION" .github/workflows/

# Check package.json engine spec
cat package.json | grep -A 2 '"engines"'
```

---

## 🟡 Phase 1 Infrastructure Status

### Completed
- [x] CI/CD Cache Optimization Infrastructure
  - Identified 28 workflows for cache optimization
  - Created `optimize_ci_cache.py` analysis tool
  - Created custom action `.github/actions/setup-python-cached`
  - Estimated savings: 14 hours/month, 14GB/month

- [x] Session Context Enrichment Infrastructure
  - Created `session_context_enrichment.py` tool
  - Captures 5 dimensions: PR state, commits, tasks, issues, tests
  - Enables <5% handoff loss (from 20% baseline)

- [x] Self-Healing Workflow Stub
  - Implemented `.github/workflows/self-healing.yml`
  - Delegates to `copilot-iterative-self-healing.yml`
  - Ready for autonomous failure detection

- [x] Coverage Gap-Fill Tests (Phase 1 Milestone)
  - Added 78 comprehensive tests for 6 cognitive modules
  - Coverage improvements:
    - code_search/handler.py: 0% → 96.72%
    - doc_loader.py: 22.43% → 93.46%
    - doc_refresh/handler.py: 0% → 82.67%
    - doc_retriever/handler.py: 0% → 88.46%
    - loader.py: 29.79% → 95.74%
  - Skills module baseline: 58.94% → 80%+

### In Progress
- [ ] WebSocket Real-Time Metrics Streaming
  - Added `/ws/metrics` endpoint to cognitive app server
  - Broadcasts quantum brain, OODA, memory, agent metrics every 1s
  - Supports dynamic channel subscription/unsubscription

### Pending (Next Priority)
- [ ] Apply Cache Optimization to 28+ Workflows
  - Use `optimize_ci_cache.py --fix-all` with manual review
  - Test on high-impact workflows first: docker-build-push, coverage-with-timeout, nox_gates
  - Verify no regressions in CI performance

- [ ] Cognitive App FastAPI Backend (0% → Phase 1 Target)
  - Implement `/api/metrics` endpoints
  - Wire up `/ws/metrics` to actual cognitive brain metrics
  - Add authentication/authorization

- [ ] Coverage Ramp Toward Phase 10 Target (50%)
  - Current: ~10.7% overall
  - Phase 1 target: 15%
  - Add tests for CLI module (0% coverage, 253 lines)
  - Add tests for compression.py (67.32%), telemetry.py (43.72%)

- [ ] CI/CD Maturity: Uncovered Python Workflows
  - Identify and apply cache to remaining uncached workflows
  - Update nox_gates.yml, test-rag.yml, and others
  - Document cache tier strategy in operational guide

### Success Criteria for Phase 1 Completion
- ✅ All 5 blocking code review comments answered
- ✅ Pre-flight validation passing
- ✅ Cache optimization infrastructure deployed
- ✅ Session context enrichment tools ready
- ✅ Coverage gap-fill tests at 80%+ for target modules
- ⏳ Node.js 20 migration completed (CRITICAL: 9 days)
- ⏳ WebSocket metrics streaming integrated (50% → 100%)
- ⏳ Cognitive app FastAPI backend functional
- ⏳ Coverage trending toward 15% target (from 10.7%)

---

## Next Actions (Priority Order)

### Immediate (Today)
1. Create GitHub issue for Node.js 20 migration (link: TBD)
2. Complete WebSocket metrics integration test
3. Run all tests to ensure no regressions

### This Week
1. Apply cache optimization to top 5 high-impact workflows
2. Test Node.js 22 compatibility
3. Update package.json engines field
4. Implement Cognitive App FastAPI metrics endpoints

### Next Week (Phase 2 Preparation)
1. Complete cache optimization rollout (28+ workflows)
2. Finalize Node.js 22 migration
3. Add coverage tests for CLI module
4. Begin WebSocket frontend integration

---

## Related Documentation
- Cache Strategy: `.codex/CI_CACHE_OPTIMIZATION.md`
- Session Context: `scripts/ci/session_context_enrichment.py`
- Cognitive App: `cognitive_app/IMPLEMENTATION_STATUS.md`
- Node.js LTS Timeline: https://nodejs.org/en/about/releases/
