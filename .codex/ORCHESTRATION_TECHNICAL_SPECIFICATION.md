# Multi-Lane Orchestration — Technical Specification

**Version:** 1.0  
**Date:** 2026-07-13  
**Reference Plan:** `.codex/MULTI_LANE_ORCHESTRATION_IMPLEMENTATION_PLAN.md`

---

## PART 1: DETERMINISTIC CONTRACT SYSTEM

### 1.1 Lane Manifest (`lane-manifest.json`)

**Purpose:** Immutable declaration of lane identity, execution mode, dependencies, and metadata.

**Schema:**
```json
{
  "lane_id": "string (A-K)",
  "lane_name": "string",
  "execution_mode": "enum (sequential|parallel|parallel_sharded)",
  "owner": "string (agent name or @username)",
  "run_id": "string (UUID)",
  "timestamp": "string (ISO 8601 UTC Z)",
  "dependencies": {
    "upstream_lanes": ["Lane A", "Lane B"],
    "upstream_gates": {
      "Lane A": "gate_status (pass|fail|pending)"
    }
  },
  "inputs": {
    "input_lock": "string (hash)",
    "seed": "integer",
    "policy_version": "string",
    "solver_version": "string"
  },
  "execution_order": ["task_1", "task_2"],
  "expected_outputs": ["output_contract_1.json", "output_contract_2.json"],
  "provenance": {
    "created_by": "string",
    "created_at": "string (ISO 8601 UTC Z)",
    "git_sha": "string"
  }
}
```

**Key Validation Rules:**
- Sequential lanes require all upstream gates to pass (gate_status = "pass")
- Parallel lanes require input-lock and seed to be immutable for determinism
- Sharded lanes must include shard count and deterministic merge order
- Timestamp must be UTC with Z suffix (no +00:00)

---

### 1.2 Input Lock (`input-lock.json`)

**Purpose:** Immutable snapshot of all inputs required for deterministic replay.

**Schema:**
```json
{
  "lock_version": "1",
  "lock_hash": "string (SHA256 of combined context)",
  "generated_at": "string (ISO 8601 UTC Z)",
  "context": {
    "policy_config": {
      "severity_weights": { "critical": 1.0, "high": 0.8, ... },
      "clustering_params": { "similarity_threshold": 0.85, ... },
      "policy_version": "string"
    },
    "solver_info": {
      "classical_solver": "string (name + version)",
      "hybrid_solver": "string (name + version)",
      "random_seed": "integer"
    },
    "environment": {
      "lane_id": "string",
      "attempt_number": "integer",
      "prior_attempts": [ { "attempt": 1, "lock_hash": "...", "outcome": "..." } ]
    },
    "input_checksums": {
      "security_findings": "string (SHA256)",
      "code_inventory": "string (SHA256)",
      "policy_rules": "string (SHA256)"
    }
  },
  "reproducibility": {
    "identical_lock_guarantee": "If lock_hash is identical and seed equals prior run, outcomes must match prior queue order and decision selection within statistical margin",
    "exception_log": [ "exception_1", "exception_2" ]
  },
  "provenance": {
    "created_by": "string",
    "git_sha": "string"
  }
}
```

**Generation Algorithm:**
```python
def generate_input_lock(policy_config, solver_info, input_checksums):
    combined = {
        "policy": json.dumps(policy_config, sort_keys=True),
        "solver": json.dumps(solver_info, sort_keys=True),
        "inputs": json.dumps(input_checksums, sort_keys=True),
        "version": "1"
    }
    lock_hash = hashlib.sha256(
        json.dumps(combined, sort_keys=True).encode()
    ).hexdigest()
    return InputLock(lock_hash=lock_hash, context=combined, ...)
```

---

### 1.3 Output Contract (`output-contract-{unit}.json`)

**Purpose:** Schema declaration and validation of output correctness.

**Schema:**
```json
{
  "unit_id": "string (unit identifier, e.g., 'wave_1', 'shard_2_3')",
  "output_schema": {
    "type": "object",
    "properties": {
      "findings": {
        "type": "array",
        "items": { "type": "object", "required": ["id", "severity", "family_id"] }
      },
      "status": { "type": "string", "enum": ["success", "partial", "failed"] },
      "metrics": { "type": "object", "required": ["closure_count", "regression_count"] }
    },
    "required": ["findings", "status", "metrics"]
  },
  "validators": [
    { "type": "schema_compliance", "required": true },
    { "type": "policy_threshold", "required": true, "params": { "max_critical_regression": 0 } },
    { "type": "security_gate", "required": true, "params": { "min_critical_resolved": 0.95 } }
  ],
  "validation_result": {
    "passed": "boolean",
    "timestamp": "string (ISO 8601 UTC Z)",
    "validation_log": [ { "validator": "string", "passed": "boolean", "message": "string" } ],
    "drift": { "expected_metrics": {}, "actual_metrics": {}, "delta": {} }
  }
}
```

---

### 1.4 Decision Trace (`decision-trace.jsonl`)

**Purpose:** Immutable audit log of all step-level decisions for replay and compliance.

**Format:** One JSON object per line (JSONL).

**Schema (per line):**
```json
{
  "step_id": "string (e.g., 'clustering_step_5', 'wave_4_shard_2_repair_3')",
  "timestamp": "string (ISO 8601 UTC Z)",
  "decision_point": "string (what choice was made)",
  "choice_made": "string (which option selected)",
  "alternatives": [ "alt_1", "alt_2", "alt_3" ],
  "rationale": "string (why this choice)",
  "supporting_data": { "key1": "value1", ... },
  "outcome": "object (result of this decision)",
  "deterministic": "boolean (whether outcome reproducible with same seed)",
  "actor": "string (which agent/function made decision)"
}
```

**Replay Usage:**
```python
def replay_trace(trace_file: str, lock: InputLock, seed: int):
    """Replay all decisions from trace file with identical seed."""
    replayed_outcomes = []
    for line in open(trace_file):
        decision = json.loads(line)
        current_outcome = execute_decision_point(
            decision['decision_point'],
            decision['alternatives'],
            seed=seed
        )
        assert current_outcome matches decision['outcome'], f"Determinism violated at {decision['step_id']}"
        replayed_outcomes.append(current_outcome)
    return replayed_outcomes
```

---

### 1.5 Artifact Provenance (`artifact-provenance.json`)

**Purpose:** Track lineage and version history of all artifacts.

**Schema:**
```json
{
  "artifact_id": "string (UUID)",
  "artifact_name": "string (e.g., 'wave_1_findings.json')",
  "artifact_type": "string (findings_family|remediation_plan|healing_report|etc)",
  "created_at": "string (ISO 8601 UTC Z)",
  "created_by": "string (agent or user)",
  "source_artifacts": [
    { "artifact_id": "uuid", "artifact_name": "string", "relationship": "parent|dependency" }
  ],
  "lineage_chain": [
    {
      "artifact_id": "uuid",
      "version": "1",
      "checksum": "string (SHA256)",
      "created_at": "string"
    }
  ],
  "git_context": {
    "branch": "string",
    "commit": "string (SHA)",
    "tag": "string"
  },
  "reproducibility": {
    "input_lock": "string (hash)",
    "seed": "integer",
    "deterministic": "boolean"
  }
}
```

---

### 1.6 Rollback Instruction (`rollback-instruction.json`)

**Purpose:** Deterministic, one-command recovery from any failed state.

**Schema:**
```json
{
  "rollback_id": "string (UUID)",
  "triggered_by_incident": "string (incident_id)",
  "rollback_type": "enum (force_classical|pause_wave|proposal_only|disable_hybrid|revert_bundle|revert_release)",
  "instructions": [
    {
      "step": 1,
      "action": "string (CLI command or internal function call)",
      "description": "string",
      "expected_effect": "string",
      "verification_command": "string (command to verify success)",
      "timeout_seconds": 60,
      "critical": true
    }
  ],
  "rollback_sequence": [
    { "step": 1, "status": "pending|executing|success|failed" }
  ],
  "evidence": {
    "state_before": { "classical_mode": true, "wave_paused": false, ... },
    "state_after": { "classical_mode": false, "wave_paused": true, ... },
    "validation_passed": "boolean",
    "timestamp": "string (ISO 8601 UTC Z)"
  }
}
```

**Example Rollback (Force Classical Mode):**
```json
{
  "rollback_type": "force_classical",
  "instructions": [
    {
      "step": 1,
      "action": "python scripts/orchestration/force_classical_mode.py",
      "description": "Disable hybrid decision solver, enable classical-only mode",
      "expected_effect": "All new decisions use classical solver",
      "verification_command": "grep ORCHESTRATION_MODE=CLASSICAL .codex/agent_context.json",
      "timeout_seconds": 30,
      "critical": true
    },
    {
      "step": 2,
      "action": "python scripts/orchestration/report_rollback_status.py force_classical",
      "description": "Emit evidence and notify governance",
      "expected_effect": "Rollback recorded in decision-trace.jsonl",
      "verification_command": "tail -1 decision-trace.jsonl | grep rollback",
      "timeout_seconds": 10,
      "critical": false
    }
  ]
}
```

---

## PART 2: LANE EXECUTION MODEL

### 2.1 Sequential Lane Execution

**Requirements:**
- Must complete upstream dependencies (gate_status = "pass") before starting
- Produces deterministic output given identical lock + seed
- Emits lane-manifest.json, output-contract-*.json, decision-trace.jsonl

**Pseudocode:**
```python
def execute_sequential_lane(lane_manifest: LaneManifest):
    # Validate upstream gates
    for upstream_lane in lane_manifest.dependencies.upstream_lanes:
        assert upstream_gates[upstream_lane] == "pass", \
            f"Upstream {upstream_lane} not passed"
    
    # Generate deterministic seed
    seed = derive_seed(
        lock=lane_manifest.inputs.input_lock,
        lane_id=lane_manifest.lane_id,
        attempt=0
    )
    seed_all_random_sources(seed)
    
    # Execute lane tasks in order
    for task in lane_manifest.execution_order:
        result = execute_task(task, seed)
        emit_decision_trace(task_id=task, outcome=result)
    
    # Validate output contract
    output = collect_outputs(lane_manifest.expected_outputs)
    for contract in lane_manifest.expected_outputs:
        validate_output_contract(output, contract)
    
    # Emit lane completion artifacts
    emit_lane_manifest(lane_manifest)
    emit_provenance(lane_manifest, sources=[upstream_lanes])
    
    return LaneResult(status="success", outputs=output)
```

---

### 2.2 Parallel Lane Execution

**Requirements:**
- Input-lock must be immutable across all parallel lanes
- Each lane executes independently with deterministic seed
- Concurrent execution with <30min timeout per lane
- DAG dependency validation pre-execution

**Pseudocode:**
```python
def execute_parallel_lanes(lanes: list[LaneManifest]):
    # Validate DAG (no cycles, all dependencies satisfied)
    validate_dag(lanes)
    
    # Execute lanes concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(execute_lane, lane): lane
            for lane in lanes
        }
        
        results = {}
        for future in as_completed(futures, timeout=1800):  # 30min
            lane = futures[future]
            results[lane.lane_id] = future.result()
    
    # Validate all lanes completed
    for lane in lanes:
        assert results[lane.lane_id].status == "success"
    
    return ParallelLaneResult(lane_results=results)
```

---

### 2.3 Sharded Lane Execution

**Requirements:**
- Deterministic fan-out into shards (e.g., by ownership boundary)
- Each shard is a parallel lane
- Deterministic fan-in merge (sorted by shard_id, then by output_order)
- Output order reproducible with identical lock + seed

**Pseudocode:**
```python
def execute_sharded_lane(lane_manifest: LaneManifest):
    # Deterministic shard generation
    shards = deterministic_fan_out(
        lane_manifest.inputs.seed,
        shard_count=lane_manifest.shard_count,
        boundaries=lane_manifest.shard_boundaries
    )
    
    # Execute each shard in parallel
    shard_results = execute_parallel_lanes([
        create_shard_manifest(lane_manifest, shard)
        for shard in shards
    ])
    
    # Deterministic fan-in merge
    merged_output = deterministic_merge(
        shard_results=shard_results,
        merge_order=lane_manifest.deterministic_merge_order,
        seed=lane_manifest.inputs.seed
    )
    
    # Validate merged output matches contract
    validate_output_contract(merged_output, lane_manifest.output_contract)
    
    return ShardedLaneResult(
        shard_results=shard_results,
        merged_output=merged_output
    )
```

---

## PART 3: POLICY TIER SYSTEM (T0-T3)

### 3.1 Tier Definitions

| Tier | Classification | Automation | Approval | Validation Re-run | Audit Flag |
|------|---|---|---|---|---|
| **T0** | Metadata/contract regeneration | Auto-apply | None | Optional | Required |
| **T1** | Low-risk non-critical fix | Auto-apply | None | Required | Required |
| **T2** | Code-level remediation | Proposal-only | Explicit approval required | Required | Required |
| **T3** | Governance/gate change | Governance-only | Governance approval | Required | Required |

### 3.2 Incident Classification Algorithm

```python
def classify_incident(incident: dict) -> Tier:
    """Classify incident to T0-T3 based on type, severity, and impact."""
    
    incident_type = incident['type']  # e.g., 'contract_mismatch', 'code_change', 'policy_violation'
    severity = incident['severity']    # e.g., 'critical', 'high', 'medium', 'low'
    blast_radius = incident.get('blast_radius', 1)  # count of affected files/systems
    
    if incident_type == 'contract_mismatch':
        if severity == 'critical' or blast_radius > 10:
            return Tier.T2  # Code-level debugging needed
        else:
            return Tier.T0  # Metadata regeneration
    
    elif incident_type == 'code_fix':
        if severity == 'critical' or blast_radius > 5:
            return Tier.T2  # Code-level, requires approval
        elif blast_radius <= 2 and severity <= 'medium':
            return Tier.T1  # Low-risk fix, auto-apply
        else:
            return Tier.T2
    
    elif incident_type == 'policy_violation':
        if 'governance' in incident['tags']:
            return Tier.T3  # Governance-only
        else:
            return Tier.T2  # Code-level remediation approval
    
    else:
        return Tier.T1  # Default: low-risk
```

### 3.3 Action Routing Algorithm

```python
def route_repair(tier: Tier, repair: dict) -> ActionRoute:
    """Route repair action based on tier."""
    
    if tier == Tier.T0:
        return ActionRoute(
            action_type='auto_apply',
            requires_approval=False,
            audit_flag=True,
            validation_required=False
        )
    
    elif tier == Tier.T1:
        return ActionRoute(
            action_type='auto_apply',
            requires_approval=False,
            audit_flag=True,
            validation_required=True  # Re-run tests
        )
    
    elif tier == Tier.T2:
        return ActionRoute(
            action_type='proposal',
            requires_approval=True,
            approval_chain=[
                {'actor': 'code_reviewer', 'timeout_hours': 4},
                {'actor': '@mbaetiong', 'timeout_hours': 24}
            ],
            audit_flag=True,
            validation_required=True
        )
    
    elif tier == Tier.T3:
        return ActionRoute(
            action_type='governance_only',
            requires_approval=True,
            approval_chain=[
                {'actor': 'governance_owner', 'timeout_hours': 1}
            ],
            audit_flag=True,
            validation_required=True,
            escalation_required=True
        )
```

---

## PART 4: SECURITY FACTORY PIPELINE (S1-S7)

### 4.1 Canonical Finding Schema (Post-Normalization)

```json
{
  "finding_id": "string (UUID)",
  "source": "string (CodeQL|Semgrep|Bandit|etc)",
  "source_id": "string (original ID from scanner)",
  "severity": "enum (critical|high|medium|low)",
  "category": "string (SQL_injection|XSS|etc)",
  "location": {
    "file": "string (path)",
    "line": "integer",
    "column": "integer",
    "snippet": "string (context)"
  },
  "cwe_ids": ["CWE-123"],
  "reachability": "enum (reachable|potentially_reachable|unreachable)",
  "language": "string (python|javascript|etc)",
  "root_cause": "string (description)",
  "context": {
    "source": "string (data source)",
    "sink": "string (where taint flows to)",
    "dataflow_path": ["location_1", "location_2"]
  },
  "lifecycle": "enum (open|triaged|remediated|suppressed)",
  "suppression": {
    "expiration_date": "string (ISO 8601)",
    "owner": "string (@username)",
    "rationale": "string",
    "evidence": "string (URL or file reference)"
  }
}
```

### 4.2 S1: Ingest & Normalize

**Input:** Scanner outputs (CodeQL JSON, Semgrep JSON, Bandit SARIF, etc.)

**Output:** List of NormalizedFinding + InventoryManifest

**Algorithm:**
1. Parse each scanner output file
2. Extract fields: severity, category, location, CWE, reachability
3. Map severity levels to canonical (critical|high|medium|low)
4. Generate fingerprints (file+line+category hash) for deduplication pre-clustering
5. Emit InventoryManifest with total count, source breakdown, language breakdown

---

### 4.3 S2: Cluster & Deduplicate

**Input:** List of NormalizedFinding

**Output:** List of FindingFamily (root-cause clusters)

**Algorithm:**
1. Group by (category, language, source+sink structure) → fuzzy families
2. Within each family, select exemplar (most severe, most reachable, most impactful)
3. Compute family confidence (0-1 based on consistency of severity, reachability)
4. Document exceptions (findings that don't fit family pattern) with justification
5. Emit FamilyIndex with exemplar IDs and confidence scores

---

### 4.4 S3: Risk-Weighted Prioritization & Wave Planning

**Scoring Formula:**
```
RiskScore = (
    w_severity * severity_score(finding.severity) +
    w_exploitability * exploitability_score(finding.reachability) +
    w_blast_radius * blast_radius_score(affected_files_count) +
    w_closure_fanout * closure_fanout_score(remediation_effort) +
    w_regression_risk * regression_risk_score(test_coverage) +
    w_effort * effort_score(estimated_loc_changes)
)
```

**Wave Planning:**
- Wave 0 (10%): Top 10% highest-risk findings
- Wave 1 (50%): Next 40% (cumulative 50%)
- Wave 2 (100%): Remaining 50%

**Rationale:** Conservative Wave 0 allows early validation; escalate scope with evidence of success.

---

### 4.5 S4: Parallel Wave Execution (Sharded by Ownership)

**Input:** Wave (list of FindingFamily), CodemodTemplates

**Output:** WaveResult with changes, validations, exceptions

**Algorithm:**
1. Shard by owner (code_owner metadata or CODEOWNERS)
2. Execute each shard in parallel:
   - For each finding_family in shard:
     - Select matching codemod template
     - Apply template (or skip if no template exists)
     - Run localized test suite on changed files
3. Collect results: changed files, validation report, unresolved findings

---

### 4.6 S5: Validation & Merge Gates

**Mandatory Checks:**
1. **Security Scans:** Re-run scanner on changed code, must pass with no new critical/high
2. **Regression Tests:** Baseline tests must pass
3. **Contract Integrity:** Output must match output-contract schema
4. **Policy Conformance:** No policy violations introduced

**Block Condition:** If any check fails → pause wave, escalate to governance

---

### 4.7 S6: Recurrence Prevention

**For each remediated family:**
1. Derive preventive pattern (e.g., "always sanitize user input before SQL query")
2. Add to linting rules or code analysis patterns
3. Emit SuppressionPolicy (for false positives) with owner, expiration, evidence
4. Schedule periodic revalidation (e.g., quarterly)

---

### 4.8 S7: Burndown Intelligence

**Metrics Tracked:**
- Findings closed this week, month
- Average time-to-closure per severity level
- Reopened findings (indicates insufficient fix)
- Recurrence rate (pattern-level regression)

**Coefficient Adaptation:**
If closure rate declining → increase severity weight, decrease effort weight

---

## PART 5: QUANTUM-HYBRID ORCHESTRATION

### 5.1 Decision Domains

**Applicable domains:**
1. Task-to-lane assignment
2. Time-slot scheduling under contention
3. Security wave packing
4. Recovery strategy selection
5. Tunneling path optimization

### 5.2 Classical Baseline Solver

**Interface:**
```python
class ClassicalSolver(ABC):
    @abstractmethod
    def solve(self, problem: dict, constraints: dict) -> Solution:
        """Solve problem deterministically using classical algorithms."""
        pass
```

**Example (Task-to-Lane Assignment):**
```python
class TaskLaneAssignmentClassicalSolver(ClassicalSolver):
    def solve(self, problem: dict, constraints: dict) -> Solution:
        # Greedy algorithm: assign tasks to lanes minimizing makespan
        tasks = problem['tasks']  # list of Task with estimated_time, dependencies
        lanes = problem['lanes']   # list of Lane with current_utilization, capacity
        
        solution = Solution()
        for task in sorted(tasks, key=lambda t: t.estimated_time, reverse=True):
            best_lane = min(
                lanes,
                key=lambda l: l.current_utilization + task.estimated_time
            )
            solution.assign(task, best_lane)
            best_lane.current_utilization += task.estimated_time
        
        return solution
```

### 5.3 Hybrid Candidate Solver

```python
class HybridCandidateSolver(ABC):
    @abstractmethod
    def solve_hybrid(self, problem: dict, constraints: dict) -> Solution:
        """Solve using hybrid (classical + quantum) approach."""
        pass
```

**Example (Variational Quantum-Inspired):**
```python
class QuantumInspiredTaskAssignmentSolver(HybridCandidateSolver):
    def solve_hybrid(self, problem: dict, constraints: dict) -> Solution:
        # Use quantum-inspired ansatz to explore assignment space
        tasks = problem['tasks']
        lanes = problem['lanes']
        
        # Encode problem as QUBO (Quadratic Unconstrained Binary Optimization)
        qubo = self._encode_as_qubo(tasks, lanes)
        
        # Solve using quantum processor or simulator (with classical fallback)
        bitstring = solve_qubo(qubo, classical_fallback=True)
        
        # Decode bitstring to assignment
        solution = self._decode_bitstring(bitstring, tasks, lanes)
        return solution
```

### 5.4 Shadow Mode Execution

```python
def run_shadow(domain: str, problem: dict, constraints: dict) -> ShadowResult:
    """Run both classical and hybrid in advisory-only mode."""
    
    classical_solution = ClassicalSolver.solve(problem, constraints)
    hybrid_solution = HybridCandidateSolver.solve_hybrid(problem, constraints)
    
    classical_objective = evaluate_objective(classical_solution, problem)
    hybrid_objective = evaluate_objective(hybrid_solution, problem)
    
    comparison = {
        'domain': domain,
        'classical_objective': classical_objective,
        'hybrid_objective': hybrid_objective,
        'improvement_pct': (hybrid_objective - classical_objective) / classical_objective * 100,
        'determinism_delta': compute_determinism_delta(classical_solution, hybrid_solution),
        'timestamp': now_utc_z(),
        'advisory_only': True  # No actual decisions made
    }
    
    return ShadowResult(**comparison)
```

### 5.5 Promotion Gates (Shadow→Canary→Production)

**Gate 1: KPI Pass (Shadow Mode)**
- Objective improvement >5% (or domain-specific threshold)
- Determinism delta <0.1%
- SLA metrics within bounds

**Gate 2: Canary Pass (7+ days)**
- Error rate <0.1% in canary cohort
- Latency p99 within budget
- No policy violations

**Gate 3: Production Activation**
- Expand to all jobs with continued monitoring
- Classical fallback always available

---

## PART 6: TRANSFER FABRIC ARCHITECTURE

### 6.1 Five-Plane Model

```
┌─────────────────────────────────────────────────────────┐
│ POLICY PLANE                                            │
│ • Trust boundaries, classification                      │
│ • Legal route determination                            │
│ • Authorization checks                                 │
└────────────┬────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────┐
│ CONTROL PLANE                                           │
│ • Route scoring (latency, reliability, cost)           │
│ • Slot assignment, scheduling                          │
│ • Congestion-aware planning                            │
└────────────┬────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────┐
│ TUNNEL PLANE                                            │
│ • Ephemeral tunnel lifecycle (establish, auth, close)  │
│ • Mutual authentication                                │
│ • Failover policy enforcement                          │
└────────────┬────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────┐
│ DATA PLANE                                              │
│ • Encrypted chunk transfer                             │
│ • Chunk-level checksums                                │
│ • Integrity commit protocol                            │
└────────────┬────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────┐
│ OBSERVABILITY PLANE                                     │
│ • Transfer telemetry (latency, loss, retry)            │
│ • Integrity anomaly detection                          │
│ • Evidence emission for audit                          │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Data Plane: Integrity Commit Protocol

**Chunk Transfer Algorithm:**
```python
def transfer_chunks(tunnel: Tunnel, data: bytes, chunk_size: int = 1MB):
    """Transfer data in chunks with per-chunk integrity."""
    
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    chunk_checksums = {}
    
    for idx, chunk in enumerate(chunks):
        # Encrypt chunk
        encrypted_chunk = encrypt(chunk, tunnel.session_key)
        
        # Compute checksum
        chunk_checksum = hashlib.sha256(chunk).hexdigest()
        chunk_checksums[idx] = chunk_checksum
        
        # Send chunk
        tunnel.send(encrypted_chunk)
        
        # Receive ACK from destination
        ack = tunnel.receive_ack(timeout=30)
        assert ack.chunk_id == idx and ack.checksum == chunk_checksum
    
    # Final integrity commit
    final_checksum = hashlib.sha256(
        json.dumps(chunk_checksums, sort_keys=True).encode()
    ).hexdigest()
    
    tunnel.send_commit(final_checksum)
    commit_ack = tunnel.receive_commit_ack(timeout=10)
    
    assert commit_ack.status == 'committed', "Integrity commit failed"
    
    return TransferResult(
        status='success',
        total_bytes=len(data),
        chunk_count=len(chunks),
        final_checksum=final_checksum,
        timestamp=now_utc_z()
    )
```

---

## NEXT STEPS

1. **Review Schemas:** Validate JSON schemas align with use cases
2. **Prototype Phase 1:** Implement input-lock generator, seed system, replay verification
3. **Integrate with Existing Agents:** Update orchestrator-agent with lane manifest support
4. **Deploy Phases 0-2:** Foundational infrastructure before security factory

---

**Document Status:** Ready for technical review and prototype implementation

