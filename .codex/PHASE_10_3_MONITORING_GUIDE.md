# PHASE 10.3 OODA ORCHESTRATION — MONITORING GUIDE

**Metrics Dashboard - Real-Time Monitoring**

```
OODA Loop Orchestration Status
─────────────────────────────────────
Cycles: 1,247 (✓1,187 ✗60)
Uptime: 95.2%

Phase Latencies (p95):
  OBSERVE: 89ms
  ORIENT: 44ms
  DECIDE: 41ms
  ACT: 186ms
  Total: 360ms

Decision Quality:
  Confidence (avg): 87.3%
  Auto-approval: 73%
  Success Rate: 92.1%

Resources:
  Active Agents: 12/145
  Queue Depth: 8
  Side Effects: 3
```

**Key Metrics to Monitor:**
- Cycle latency p95 <1000ms ✅
- Decision confidence >90% ✅
- Execution success >85% ✅
- Agent utilization >10% ✅
- Side effects <5/cycle ✅

**Query Recent Cycles:**
```python
orchestrator = OODAOrchestrator()
recent = orchestrator.get_recent_cycles(limit=100)
metrics = orchestrator.get_metrics()
orchestrator.print_metrics_dashboard()
```

**Alert Thresholds:**
- ⚠️ Cycle latency >2000ms
- ⚠️ Confidence <0.70
- ⚠️ Success rate <0.75
- 🔴 Side effects >10/cycle
