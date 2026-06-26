# PHASE 11.2 Quick Routing Rules

## Executive Summary
Session-scoped incremental routing system for agent orchestration. Enables semantic task classification, confidence-based approval gates, and fallback chains.

---

## Routing Architecture

### 1. Task Classification (Domain-Based Keywords)
```
Domains:
- "test" / "coverage" / "pytest" → test-coverage-agent
- "security" / "scan" / "vulnerability" → security-alert-verification-agent
- "ci" / "workflow" / "github-actions" → workflow-ci-fixer
- "documentation" / "docs" / "link" → doc-freshness-checker
- "performance" / "benchmark" / "regression" → performance-regression-detector
- "import" / "module" / "importerror" → ci-importerror-agent
- "code" / "review" / "analysis" → code-analysis-agent
- "release" / "version" / "deploy" → pypi-publishing-operations-agent
- "health" / "monitor" / "alert" → workflow-health-monitor
- "dependency" / "package" / "conflict" → dependency-conflict-agent
```

### 2. FAISS Semantic Search Integration
- **Index source:** Phase 11.1 agent capability corpus (FAISS embeddings)
- **Query encoding:** Natural language task description → embedding
- **Top-k retrieval:** Return top 3 matching agents
- **Reranking:** Combine keyword + semantic scores

### 3. Confidence Scoring Formula
```
confidence = 0.4 × keyword_match_score + 0.6 × semantic_similarity_score

keyword_match_score: 0-100 (exact match = 100, partial = 50-99, none = 0)
semantic_similarity_score: 0-100 (cosine similarity to FAISS embeddings, scaled)

Final score: max(top_3_agents) rounded to nearest int
```

### 4. Approval Gates
```
Score ≥ 90%  → Auto-approve (agent routed immediately)
Score 75-89% → Human review recommended (post PR comment, wait approval)
Score <75%   → Escalate to 3-agent fallback chain
```

### 5. Fallback Strategy (3-Agent Chain)
When confidence <75%:
1. Route to `orchestrator-agent` (semantic re-analysis)
2. If still uncertain, route to `recon-scout-agent` (codebase context)
3. If still unresolved, escalate to @mbaetiong (human decision)

---

## Performance Baseline

| Metric | Target | Definition |
|--------|--------|-----------|
| p50 latency | <200ms | Time from query to routing decision |
| p95 latency | <400ms | 95th percentile |
| p99 latency | <800ms | 99th percentile (acceptable for offline) |
| Top-1 accuracy | ≥95% | Correct agent chosen as top result |
| Throughput | 1000 req/sec | Concurrent requests handled |

---

## Safety Gates

### Privilege Checks
- No agent can access production secrets without explicit RBAC approval
- Destructive operations (delete, force-push) require human approval
- CodeQL fixes auto-approved only if score ≥95%

### Confidence Thresholds
- <50%: Always human review
- 50-74%: Recommend review + allow auto-route if explicitly approved
- ≥75%: Auto-route (with monitoring)

### Rollback Triggers
- If agent output contains xfail(strict=False) without root-cause doc → reject
- If new test failures introduced → rollback + escalate
- If latency spike >2x median → circuit breaker (stop routing, escalate)

---

## Implementation Checklist

- [ ] FAISS index loaded from Phase 11.1 (s3://codex-embeddings/agent-corpus.index)
- [ ] Keyword domain map deployed
- [ ] Confidence scoring formula implemented
- [ ] Approval gate middleware active
- [ ] Fallback chain configured (orchestrator → recon → human)
- [ ] Monitoring metrics exported (p50, p95, accuracy, throughput)
- [ ] Canary rollout: 10% of traffic (1 day monitoring)
- [ ] Full rollout: 100% traffic (metrics reviewed, alerts set)

---

## Deployment

### Canary (Day 1)
- Route 10% of tasks through new system
- Monitor accuracy, latency, false positives
- Alert if accuracy <90% or latency >400ms p95

### Full Rollout (Day 2+)
- 100% traffic to routing system
- Keep fallback chain active for <75% confidence cases
- Weekly accuracy report to @mbaetiong

---

## Monitoring Queries

```sql
-- Accuracy by domain (daily)
SELECT domain, COUNT(*) as routed, SUM(CASE WHEN correct THEN 1 ELSE 0 END) as correct,
       ROUND(100.0 * SUM(CASE WHEN correct THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy_pct
FROM routing_events
WHERE DATE(timestamp) = CURRENT_DATE
GROUP BY domain
ORDER BY accuracy_pct DESC;

-- Latency percentiles (hourly)
SELECT 
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY latency_ms) as p50,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99
FROM routing_events
WHERE timestamp > NOW() - INTERVAL '1 hour';

-- Confidence distribution
SELECT confidence_bucket, COUNT(*) as count
FROM (
  SELECT FLOOR(confidence / 10) * 10 as confidence_bucket FROM routing_events
)
GROUP BY confidence_bucket ORDER BY confidence_bucket DESC;
```

---

## Success Criteria (This Session)

✅ Routing rules documented (clear, implementable)
✅ FAISS integration specified (with index location)
✅ Confidence scoring formula finalized
✅ Approval gates defined (90/75 thresholds)
✅ Fallback strategy documented
✅ Safety gates enforced
✅ Performance targets set (p50 <200ms, accuracy ≥95%)
