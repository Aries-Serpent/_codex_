# ALPHA DEPLOYMENT MANIFEST

**Campaign**: Multi-Phase Deployment Campaign (Alpha → Beta → GA)  
**Phase**: PHASE 1 - IMMEDIATE (Alpha Deployment + Canary Testing)  
**Status**: READY FOR EXECUTION  
**Execution Window**: Current session (~2 hours)  
**Authority**: @mbaetiong D-tier autonomous  
**Timestamp**: 2026-07-14T15:03:10Z  

---

## PHASE 1: IMMEDIATE EXECUTION GATE REQUIREMENTS

### Gate 1: Pre-Deployment Readiness

#### Security Validation
- [ ] CodeQL security scan: Zero critical vulnerabilities
  - Target: 0 high-severity issues unresolved
  - Validation: `gh workflow run codeql-analysis.yml` or check latest CodeQL run
  - Evidence: Link to CodeQL run or scan results

#### Coverage Validation
- [ ] Minimum test coverage thresholds met
  - Target: Core modules ≥75% line coverage, critical paths ≥90%
  - Validation: `nox -s tests` with coverage report
  - Evidence: Coverage percentage per module

#### CI/CD Pipeline Status
- [ ] All workflows passing on current branch
  - Target: 100% workflow pass rate
  - Validation: Check GitHub Actions status, all required checks passing
  - Evidence: Last 3 workflow runs all green

#### Compliance Documentation
- [ ] REQ-4: AGENT_ACCOUNTABILITY_REPORT.md updated in latest commit
  - Target: Session entry dated 2026-07-14 with Phase 1 initiation note
  - Validation: `git show HEAD:docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md | head -50`
  - Evidence: Commit hash includes today's session entry

- [ ] REQ-5: CHANGELOG.md updated in latest commit
  - Target: Entry dated 2026-07-14 documenting campaign start
  - Validation: `git show HEAD:CHANGELOG.md | head -30`
  - Evidence: Campaign milestone entry present

**Gate 1 Status**: ⏳ PENDING - Execute validation commands above

---

### Gate 2: Build Artifacts Validation

#### Docker Image Build
- [ ] Docker image builds successfully (single-stage production build)
  - Command: `docker build -t codex:alpha-build-TIMESTAMP .`
  - Target: Build completes in <5 minutes, 0 warnings
  - Evidence: Build log, image SHA

#### Distribution Artifacts
- [ ] Wheel distribution: `*.whl` generated
  - Command: `pip install build && python -m build --wheel`
  - Target: `dist/codex_ml-X.Y.Z-py3-none-any.whl`
  - Evidence: File exists, size >1MB

- [ ] Source distribution: `*.tar.gz` generated
  - Command: `python -m build --sdist`
  - Target: `dist/codex_ml-X.Y.Z.tar.gz`
  - Evidence: File exists, size >500KB

#### Version Consistency Check
- [ ] pyproject.toml version matches deployment version
  - Command: `grep version pyproject.toml | head -1`
  - Target: `version = "X.Y.Z"` (no "v" prefix)
  - Evidence: Version string matches

#### Artifact Checksums
- [ ] SHA-256 checksums computed for all artifacts
  - Command: `sha256sum dist/* > .codex/ALPHA_ARTIFACT_CHECKSUMS.txt`
  - Target: 3 checksums (docker image SHA, wheel, tar.gz)
  - Evidence: Checksums file created and committed

**Gate 2 Status**: ⏳ PENDING - Execute build commands above

---

### Gate 3: Environment Readiness

#### Alpha Infrastructure Provisioned
- [ ] Container registry accessible
  - Target: Registry endpoint resolvable, credentials valid
  - Validation: `docker login` succeeds
  - Evidence: Registry credentials verified

- [ ] Load balancer configured
  - Target: DNS name resolvable, health checks configured
  - Validation: `nslookup alpha-lb.internal` resolves
  - Evidence: DNS query succeeds

- [ ] Database replicas accessible
  - Target: Primary + 2 read replicas online
  - Validation: Connection test from alpha cluster succeeds
  - Evidence: Connection pool shows 3 healthy endpoints

#### Observability Stack Activated
- [ ] Metrics collection enabled (Prometheus/CloudWatch)
  - Target: Metrics scraping interval: 30s or better
  - Validation: Metrics endpoint responds
  - Evidence: First metrics ingest recorded

- [ ] Log aggregation configured (ELK/Splunk/CloudWatch)
  - Target: Logs forwarded within 5s of emission
  - Validation: Sample log appears in aggregation service
  - Evidence: Log query returns recent entries

- [ ] Distributed tracing setup (Jaeger/DataDog)
  - Target: Trace sampling configured (e.g., 10% of requests)
  - Validation: Sample trace captured and queryable
  - Evidence: Trace span visible in tracing UI

#### Alert Policies Configured
- [ ] Critical alert: Error rate >1%
  - Target: Alert fires within 2 minutes of threshold breach
  - Validation: Dry-run alert trigger test
  - Evidence: Test alert received

- [ ] Critical alert: Latency p95 >1000ms
  - Target: Alert fires within 2 minutes of threshold breach
  - Evidence: Test alert received

- [ ] Critical alert: CPU >90% sustained (5 min)
  - Target: Alert fires when sustained for 5+ minutes
  - Evidence: Test alert received

- [ ] Critical alert: Memory >85% sustained (5 min)
  - Target: Alert fires when sustained for 5+ minutes
  - Evidence: Test alert received

- [ ] Critical alert: Service unhealthy (health check failing)
  - Target: Alert fires within 1 minute of health check failure
  - Evidence: Test alert received

**Gate 3 Status**: ⏳ PENDING - Validate infrastructure above

---

## PHASE 1 EXECUTION STEPS

### Step 1.1: Deploy to Alpha Cluster

**Command Sequence**:
```bash
# 1. Tag and push docker image
docker tag codex:alpha-build-TIMESTAMP codex.registry.io/codex:alpha-latest
docker tag codex:alpha-build-TIMESTAMP codex.registry.io/codex:alpha-2026-07-14
docker push codex.registry.io/codex:alpha-latest
docker push codex.registry.io/codex:alpha-2026-07-14

# 2. Deploy to alpha cluster with resource limits
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-alpha
  namespace: alpha
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 50% max surge for 2 replicas = 1 extra
      maxUnavailable: 0  # 0% unavailable = graceful rollout
  selector:
    matchLabels:
      app: codex-alpha
  template:
    metadata:
      labels:
        app: codex-alpha
    spec:
      containers:
      - name: codex
        image: codex.registry.io/codex:alpha-latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        resources:
          requests:
            cpu: 1000m      # 1 CPU minimum
            memory: 2Gi     # 2GB minimum
          limits:
            cpu: 2000m      # 2 CPU max
            memory: 4Gi     # 4GB max
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
EOF

# 3. Verify deployment
kubectl rollout status deployment/codex-alpha -n alpha --timeout=5m
kubectl get pods -n alpha -l app=codex-alpha
```

**Success Criteria**:
- ✅ 2 pods in `Running` state
- ✅ Both pods pass readiness probe
- ✅ Rollout completes in <5 minutes
- ✅ No errors in pod logs

**Status**: ⏳ PENDING

---

### Step 1.2: Post-Deployment Validation

**Command Sequence**:
```bash
# 1. Verify health checks pass
curl -v http://alpha-lb.internal/health
# Expected: HTTP 200 OK

# 2. Test readiness endpoint
curl -v http://alpha-lb.internal/ready
# Expected: HTTP 200 OK

# 3. Verify service dependencies
curl -v http://alpha-db.internal:5432/status
curl -v http://alpha-cache.internal:6379/ping
curl -v http://alpha-api.internal/status

# 4. Record baseline metrics
kubectl exec -it deployment/codex-alpha -n alpha -- \
  curl http://localhost:8000/metrics > /tmp/alpha_baseline_metrics.txt

# 5. Capture baseline latency
curl -w "\nDNS: %{time_namelookup}\nConnect: %{time_connect}\nTotal: %{time_total}\n" \
  http://alpha-lb.internal/api/ping
```

**Baseline Metrics to Record**:
- Latency: p50, p95, p99 (ms)
- Error rate: 4xx, 5xx per 1000 requests (%)
- Throughput: Requests/sec
- Resource utilization: CPU (%), Memory (%), Disk I/O (%)

**Status**: ⏳ PENDING

---

## PHASE 1.3: CANARY TESTING (Parallel Execution)

### Canary Workload Configuration

**Load Generation Pattern**:
```
Time 0-5m:  Ramp-up from 5 req/s to 50 req/s (10 req/s per minute)
Time 5-20m: Hold at 50 req/s (sustained traffic)
Time 20-25m: Ramp to 100 req/s (10 req/s per minute)
Time 25-30m: Peak at 100 req/s (5 min hold)
Time 30-35m: Ramp down to baseline (10 req/s per minute decrease)
Time 35-40m: Cool-down at 5 req/s
```

### Canary Test Coverage

**API Operations** (Execute via synthetic client):
- [ ] CRUD Operations
  - POST /api/items (create)
  - GET /api/items/{id} (read)
  - PUT /api/items/{id} (update)
  - DELETE /api/items/{id} (delete)

- [ ] Authentication
  - POST /auth/login
  - POST /auth/refresh
  - POST /auth/logout

- [ ] Search/Query
  - GET /api/search?query=test (complex query)
  - GET /api/items?filter=active&sort=created (filtered list)

- [ ] Compute-Heavy Operations
  - POST /api/compute (batch processing)
  - GET /api/results/{job_id} (fetch results)

**Success Criteria** (All must pass):
- ✅ Error rate <0.1% (≤5 errors per 5000 requests)
- ✅ Latency p95 <500ms (95th percentile response time)
- ✅ Latency p99 <800ms (99th percentile response time)
- ✅ Zero panic/crash logs in application logs
- ✅ Memory utilization stable (<80%)
- ✅ CPU utilization smooth (no spikes >90%)
- ✅ Zero connection pool exhaustion
- ✅ Zero database timeout errors

### Real-User Traffic Validation (Optional)

- [ ] Shadow traffic from staging routed to alpha (read-only)
  - 5% of staging production-like traffic
  - Validate response consistency
  - Capture workload patterns

**Status**: ⏳ PENDING

---

## PHASE 1.4: CANARY RESULTS & GATE DECISION

### Success Gate Validation

```
All canary metrics pass?
├─ YES → Proceed to Phase 2 (short-term monitoring)
│        Create ALPHA_CANARY_RESULTS_SESSION_DATE.md ✅
│        Sign-off on gate decision
└─ NO  → Trigger auto-rollback
         Execute rollback procedure
         Root-cause analysis
         Re-prepare and restart Phase 1
```

### Telemetry Capture Format

When canary testing completes, create `.codex/ALPHA_CANARY_RESULTS_2026_07_14.md` with:

```markdown
# Alpha Canary Test Results - 2026-07-14

## Test Execution Summary
- Start Time: [TIMESTAMP]
- End Time: [TIMESTAMP]
- Duration: [MINUTES]
- Peak QPS: [VALUE]
- Total Requests: [COUNT]

## Success Metrics
- Error Rate: [PERCENTAGE] ✅/❌
- Latency p95: [MS] ✅/❌
- Latency p99: [MS] ✅/❌
- Memory Peak: [MB] ✅/❌
- CPU Peak: [%] ✅/❌

## Error Analysis
- 5xx Errors: [COUNT]
- 4xx Errors: [COUNT]
- Timeout Errors: [COUNT]
- Sample Error: [SAMPLE LOG]

## Resource Utilization
- CPU Avg: [%]
- CPU Max: [%]
- Memory Avg: [MB]
- Memory Max: [MB]
- Disk I/O: [MB/s]

## Decision: PASS ✅ / FAIL ❌
- Executor: @copilot
- Approval: @mbaetiong
- Timestamp: [TIMESTAMP]
- Next Phase: Phase 2 Short-term Monitoring
```

**Status**: ⏳ PENDING

---

## COMPLIANCE CHECKLIST

### Documentation Requirements
- [ ] Session date: 2026-07-14
- [ ] Execution start time: [TO BE RECORDED]
- [ ] Execution end time: [TO BE RECORDED]
- [ ] Executor identity: @copilot
- [ ] Pre-gate checklist: All 3 gates documented
- [ ] Metrics snapshots: Baseline and peak values recorded
- [ ] Issue list: Any issues encountered (with resolutions)
- [ ] Go/No-Go decision: Recorded with explicit approval

### Repository Artifacts Verification
- [ ] ALPHA_DEPLOYMENT_MANIFEST.md (this file)
- [ ] ALPHA_ARTIFACT_CHECKSUMS.txt (checksums for build artifacts)
- [ ] ALPHA_CANARY_RESULTS_2026_07_14.md (test results)
- [ ] AGENT_ACCOUNTABILITY_REPORT.md updated with Phase 1 entry
- [ ] CHANGELOG.md updated with Phase 1 milestone

### WEC (Workflow Execution Checklist) Status
- [ ] Workflow Execution Checklist present in PR body
- [ ] All required workflows green (100% pass rate)
- [ ] No pending approvals blocking Phase 1 execution

---

## NEXT PHASE: PHASE 2 SHORT-TERM MONITORING & BETA PREP

**Trigger**: Upon Phase 1 gate pass  
**Duration**: ~2-4 hours (same session)  
**Checkpoint Document**: `BETA_READINESS_CHECKPOINT_SESSION_DATE.md`  
**Success Criteria**: Alpha stability (4-6h monitoring window) + Beta infrastructure ready  

---

## APPROVALS & SIGN-OFF

**Campaign Authority**: @mbaetiong D-tier autonomous  
**Execution Authority**: @copilot  
**Timestamp**: 2026-07-14T15:03:10Z  

---

**Status**: ⏳ READY FOR GATE VALIDATION
