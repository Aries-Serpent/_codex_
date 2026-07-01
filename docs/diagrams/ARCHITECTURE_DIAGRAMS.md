# 📊 Architecture Diagrams Index

> **Last updated:** 2026-05-29 (P2.3 Phase 2)
> **Coverage:** 20 diagrams (Phase 1-2: 30% of target)

All `.mmd` files in this directory are authoritative Mermaid source diagrams.
Render with the Mermaid CLI (`mmdc`), GitHub's native Mermaid rendering, or the
[Mermaid Live Editor](https://mermaid.live).

---

## Phase 1: High-Impact System Architecture (4 diagrams)

| File | Purpose | Evidence |
|------|---------|----------|
| [`architecture.mmd`](architecture.mmd) | Full system architecture: ML core, tokenization, RAG, cognitive brain, logging, CI self-healing | S1292 |
| [`ci_self_healing_flow.mmd`](ci_self_healing_flow.mmd) | CI auto-fix pipeline: push → agent-auth → validation → merge gate | S1292 |
| [`runtime_logic_map.mmd`](runtime_logic_map.mmd) | Runtime flow: CLI entry, training, tokenization, quantum orchestrator | S178 |
| [`audit_pipeline_v1.4.0.mmd`](audit_pipeline_v1.4.0.mmd) | 7-stage audit pipeline: context → facets → capabilities → scoring → gaps → report → manifest | v1.4.0 |

---

## Phase 2: Module Interaction Diagrams (10 diagrams)

### System Integration Flows

| File | Purpose | Evidence |
|------|---------|----------|
| [`phase2_01_agent_ecosystem_routing.mmd`](phase2_01_agent_ecosystem_routing.mmd) | Agent discovery, routing, and selection via semantic search + tag filtering | orchestrator-agent, AGENT_REGISTRY |
| [`phase2_04_cognitive_brain_ooda.mmd`](phase2_04_cognitive_brain_ooda.mmd) | OODA loop: Observe → Orient → Decide → Act with memory promotion (STM → LTM) | cognitive_brain_core.py |
| [`phase2_05_security_auth_flow.mmd`](phase2_05_security_auth_flow.mmd) | Auth pipeline: token validation → RBAC → authorization → secrets scanning | src/security/ |

### Data & ML Pipelines

| File | Purpose | Evidence |
|------|---------|----------|
| [`phase2_02_ml_training_pipeline.mmd`](phase2_02_ml_training_pipeline.mmd) | Training flow: data → tokenization → training loop → evaluation → checkpoint → export | src/codex_ml/ |
| [`phase2_03_rag_indexing_flow.mmd`](phase2_03_rag_indexing_flow.mmd) | RAG end-to-end: documents → embedding → FAISS index → query → ranking → context assembly | src/codex/rag/ |
| [`phase2_10_tokenization_pipeline.mmd`](phase2_10_tokenization_pipeline.mmd) | Multi-backend tokenization: HF, SentencePiece, BPE with caching and special tokens | src/tokenization/ |

### Configuration & Operations

| File | Purpose | Evidence |
|------|---------|----------|
| [`phase2_06_config_management.mmd`](phase2_06_config_management.mmd) | Hydra config composition: defaults → overrides → validation → instantiation → runtime | configs/, OmegaConf |
| [`phase2_07_logging_telemetry.mmd`](phase2_07_logging_telemetry.mmd) | Observability: event collection → storage (NDJSON, SQLite) → metrics → alerting → analysis | src/codex/logging/ |

### Development & Execution

| File | Purpose | Evidence |
|------|---------|----------|
| [`phase2_08_skills_deployment.mmd`](phase2_08_skills_deployment.mmd) | Skill lifecycle: develop → register → version → install → discover → invoke → monitor | skills-master-agent |
| [`phase2_09_testing_infrastructure.mmd`](phase2_09_testing_infrastructure.mmd) | Test pipeline: discovery → configuration → parallel execution → coverage → CI integration → analysis | pytest, conftest.py |

---

## Architecture Coverage Summary

### By Module (Phase 1-2)

- ✅ **Agent Ecosystem:** discovery, routing, orchestration (2 diagrams)
- ✅ **ML Core:** training, evaluation, model registry (1 diagram)
- ✅ **Data Layer:** RAG, tokenization, caching (2 diagrams)
- ✅ **Configuration:** Hydra, overrides, validation (1 diagram)
- ✅ **Cognitive Brain:** OODA loop, memory, learning (1 diagram)
- ✅ **Security:** auth, RBAC, secrets, scanning (1 diagram)
- ✅ **Observability:** logging, metrics, alerting (1 diagram)
- ✅ **Skills:** lifecycle, discovery, execution (1 diagram)
- ✅ **Testing:** framework, CI, coverage (1 diagram)
- ⏳ **CI/CD:** (comprehensive Phase 1 diagram covers this)
- ⏳ **Component Dependencies:** (Phase 3)
- ⏳ **Integration Scenarios:** (Phase 4)

### By Type

| Type | Count | Phase |
|------|-------|-------|
| System Architecture | 3 | 1 |
| Module Interaction | 10 | 2 |
| Component Relationships | 15 | 3 (planned) |
| Integration Scenarios | 15 | 4 (planned) |
| **Total** | **43** | **1-4** |

---

## Key Concepts by Diagram

### Architecture Map (`architecture.mmd`)
System-wide components and interactions:
- ML Core (training, models, data registries)
- Tokenization API (HF/Legacy adapters)
- RAG (embedding, indexing, retrieval)
- Cognitive Brain (OODA, memory, orchestration)
- Logging (session logger, telemetry)
- CI Self-Healing (patterns, validation gates)
- GitHub Actions workflows (AAD, PMV, WEG, CodeQL)

### CI Self-Healing Flow (`ci_self_healing_flow.mmd`)
Automated fix pipeline on every push:
- Parallel triggers: agent-auth-delegation, pre-merge-validation, workflow-execution-gate
- Session wrapup auto-fix: REQ-4, REQ-5, REQ-6, REQ-PDA, PR-DESC
- Pattern pipeline: 32 patterns with 10-dimension scorecard
- Merge readiness gate: ≥98% score + <25 CodeQL alerts

### Agent Ecosystem Routing (`phase2_01_agent_ecosystem_routing.mmd`)
Agent discovery and selection:
- AGENT_REGISTRY.yaml (manifest + FAISS index + capability tags)
- Semantic search → tag filtering → relevance scoring
- Orchestrator routes to specialists (explore, task, general-purpose, code-review, research, etc.)
- Execution backends: bash, Python, MCP, GitHub API
- Feedback loop updates routing index

### ML Training Pipeline (`phase2_02_ml_training_pipeline.mmd`)
End-to-end training flow:
1. Data acquisition (registry, loader, cache)
2. Tokenization & preprocessing (encoder validation)
3. Configuration (Hydra, overrides)
4. Model initialization (registry, weights, device placement)
5. Training loop (forward/backward, optimizer, checkpoints)
6. Validation (metrics, early stopping)
7. Logging (telemetry, dashboards)
8. Post-training (evaluation, export, metadata)

### RAG System (`phase2_03_rag_indexing_flow.mmd`)
Retrieval-augmented generation:
1. Document ingestion (chunking, metadata)
2. Embedding generation (backend selection, normalization)
3. Index building (FAISS, IVF clustering)
4. Query processing (parsing, expansion, embedding)
5. Result ranking (BM25 re-rank, deduplication, diversity boost)
6. Context assembly (fetch source, formatting, token trimming)
7. Feedback loop (query logging, usage stats, retraining)

### OODA Loop (`phase2_04_cognitive_brain_ooda.mmd`)
Cognitive Brain decision cycle:
- **Observe:** Listen → Parse → Capture state → Retrieve context
- **Orient:** Load patterns → Semantic match → Query KB → Build model
- **Decide:** Generate options → Evaluate → Pick strategy → Plan execution
- **Act:** Load skill → Execute → Monitor → Handle failure
- **Memory:** STM → LTM promotion at 80% capacity, prune stale entries
- **Feedback:** Measure outcome → Compare expected → Extract lesson → Update patterns
- **Iteration:** Success → return; Partial → refine; Failed → escalate

### Security & Auth (`phase2_05_security_auth_flow.mmd`)
Full auth/authz pipeline:
1. **Authentication:** Token validation, signature check, expiry, claims extraction
2. **Secrets:** Vault → Loader → Encryption → Audit
3. **Authorization:** RBAC rules → permission check → allow/deny
4. **Scanning:** File scan → pattern detection → false positive filter → redaction
5. **Enforcement:** Access control decisions with audit logging
6. **OAuth:** Provider flow with consent, code exchange, token storage

### Configuration System (`phase2_06_config_management.mmd`)
Hydra-based configuration:
- **Sources:** YAML defaults → domain configs → env vars → CLI args
- **Discovery:** Walk configs/, validate schema, compose hierarchy
- **Overrides:** Parse CLI (++key=val), apply env precedence, merge cascade
- **Validation:** Type check, range check, dependency check, custom validators
- **Instantiation:** Structured config → object creation → constructor injection
- **Runtime:** Access via OmegaConf, watch for changes

### Logging & Telemetry (`phase2_07_logging_telemetry.mmd`)
Observable systems:
1. **Event Sources:** Training, inference, system, app, CI
2. **Collection:** Unified collector → SessionLogger → contextualization
3. **Storage:** NDJSON files + SQLite DB
4. **Metrics:** Extract → Aggregate (windows) → Compute stats
5. **Observability:** Log viewer, search, export
6. **Alerting:** Anomaly detection → severity classification → routing → deduplication
7. **Analysis:** Correlation → pattern finding → recommendations

### Skills Lifecycle (`phase2_08_skills_deployment.mmd`)
Skill management:
1. **Development:** Write code → define interface → write tests → docstring
2. **Registration:** Scan directory → parse manifest → extract schema → add to registry
3. **Versioning:** Semantic versioning → changelog → git tag → production promotion
4. **Installation:** Resolve deps → validate env → install → setup → register
5. **Discovery:** List → filter tags → search keyword → rank relevance
6. **Invocation:** Select → validate inputs → prepare env → execute → capture output
7. **Error Handling:** Classify error → retry with backoff → fallback skill
8. **Monitoring:** Track latency, errors, usage → compute reliability score

### Testing Infrastructure (`phase2_09_testing_infrastructure.mmd`)
Test framework & CI:
1. **Discovery:** Scan files → parse markers → collect functions → group by category
2. **Configuration:** Load pytest.ini → setup fixtures → setup DB → mock external
3. **Execution:** Parallel run (pytest-xdist) → capture output → measure time → detect flakiness
4. **Coverage:** Instrument code → track lines/branches → calculate coverage %
5. **Assertion:** Run assertions → compare values → generate diff → mark result
6. **Collection:** Collect results → extract metrics → store in DB → generate report
7. **CI Integration:** CI trigger → run matrix (Python 3.10-3.12) → upload coverage → post badge
8. **Analysis:** Find flaky tests → identify slow tests → find coverage gaps → suggest fixes

### Tokenization (`phase2_10_tokenization_pipeline.mmd`)
Multi-backend tokenization:
1. **Selection:** Lookup registry → check if installed → select backend
2. **Backends:** HuggingFace (pretrained download) vs SentencePiece (trained) vs BPE (vocab)
3. **Tokenization:** Preprocess → split words → encode → add special tokens → validate length
4. **Padding/Truncation:** Truncate if too long, pad if too short
5. **Output:** Token tensor (input_ids, attention_mask)
6. **Decoding:** Reverse mapping (token IDs → text)
7. **Caching:** LRU cache for common inputs (~100MB)

---

## Rendering

### Install Mermaid CLI
```bash
npm install -g @mermaid-js/mermaid-cli
```

### Render All Diagrams
```bash
for f in docs/diagrams/*.mmd; do
  mmdc -i "$f" -o "${f%.mmd}.svg" --width 1600 --height 1200
done
```

### Render Single Diagram
```bash
mmdc -i docs/diagrams/phase2_04_cognitive_brain_ooda.mmd -o docs/diagrams/phase2_04.svg
```

### View in Browser
- Open [Mermaid Live Editor](https://mermaid.live)
- Copy-paste `.mmd` content and render

---

## Phase 3 & 4 Roadmap

### Phase 3: Component Relationship Diagrams (15 diagrams)
**Focus:** Inter-module dependencies and data flows

- **Core Layer Diagrams (5):**
  - Execution layer (CLI, entry points, orchestration)
  - Data layer (registries, caching, persistence)
  - Processing layer (ML, tokenization, features)
  - Orchestration layer (agents, scheduling)
  - Observability layer (logging, metrics, debugging)

- **Inter-Module Dependencies (5):**
  - Cognitive Brain → RAG, logging, memory
  - RAG → indexing, caching, embeddings
  - ML → tokenization, data, evaluation
  - Security → auth, policies, validation
  - CI → patterns, validation, gates

- **Integration Paths (5):**
  - Data flow through ML pipeline
  - Agent-to-skill mapping and invocation
  - Error recovery and fallbacks
  - 4-layer cache hierarchy integration
  - Session metadata propagation

### Phase 4: Integration Scenario Diagrams (15 diagrams)
**Focus:** End-to-end workflows and collaboration patterns

- **User Workflows (5):**
  - Query → Agent → Skill → Response
  - Training job submission → monitoring → checkpoint
  - PR push → checks → validation → merge
  - Model evaluation scenario
  - Deployment workflow

- **Agent Collaboration (5):**
  - Orchestrator multi-agent dispatch
  - Skill chaining (sequential execution)
  - Feedback-based learning and coaching
  - Concurrent agent coordination
  - Hierarchical agent delegation

- **Resilience & Performance (5):**
  - Bottleneck identification
  - Graceful degradation paths
  - Circuit breaker patterns
  - Capacity scaling triggers
  - Observability troubleshooting

---

## Cross-Diagram Navigation

- **System-wide view:** Start with `architecture.mmd` and `ci_self_healing_flow.mmd`
- **Agent workflows:** `phase2_01_agent_ecosystem_routing.mmd` → `phase2_04_cognitive_brain_ooda.mmd`
- **ML workflows:** `phase2_02_ml_training_pipeline.mmd` → `phase2_10_tokenization_pipeline.mmd`
- **Data retrieval:** `phase2_03_rag_indexing_flow.mmd` → `phase2_07_logging_telemetry.mmd`
- **Operations:** `phase2_06_config_management.mmd` → `phase2_09_testing_infrastructure.mmd`
- **Security:** `phase2_05_security_auth_flow.mmd` across all workflows

---

## Validation & Quality

✅ **Diagrams created:** 20 (Phase 1: 4 + Phase 2: 10 + Phase 1 legacy: 6)
✅ **Format:** All in Mermaid `.mmd` format
✅ **Documentation:** Context and evidence for each diagram
✅ **Rendering:** Tested in GitHub-native Mermaid renderer
✅ **Cross-references:** Navigation between related diagrams

📊 **Coverage progress:** 30% toward 85% target (40+ diagrams)

---

**Last commit:** P2.3 Phase 2: 10 Module Interaction Diagrams (20 total diagrams, 30% coverage)
