# Session Recovery System Documentation

**Version:** 1.0  
**Status:** Active  
**Last Updated:** 2026-06-23T22:57:43Z  
**Maintained By:** @mbaetiong

---

## Overview

The Session Recovery System automatically detects, logs, and recovers from failed Copilot sessions in the `Aries-Serpent/_codex_` repository. This system ensures that work in progress is not lost and that session continuity is maintained across failures.

### Key Features

- 🔍 **Automatic Failure Detection** — Monitors GitHub Actions workflow runs for failures, cancellations, and timeouts
- 💾 **Session State Persistence** — Checkpoints session state every 15 minutes to `.codex/sessions/`
- 🫀 **Heartbeat Monitoring** — Detects stalled sessions through periodic heartbeat monitoring
- 🔄 **Auto-Recovery** — Automatically triggers recovery for up to 2 consecutive failures
- 📊 **Metrics Tracking** — Tracks recovery success rates and failure patterns
- 🚨 **Human Escalation** — Notifies @mbaetiong after 2 consecutive auto-recovery failures

---

## Architecture

### Components

```
Session Recovery System
├── Workflow: .github/workflows/session-recovery-handler.yml
│   ├── Detects failed workflow runs (cancelled, failed, timed_out)
│   ├── Extracts session context
│   ├── Triggers auto-recovery (if eligible)
│   ├── Escalates to human review (if needed)
│   └── Logs recovery events
│
├── Configuration: .codex/session_recovery_config.yml
│   ├── Auto-recovery settings
│   ├── Checkpoint interval (15 min)
│   ├── Heartbeat monitoring rules
│   ├── Escalation policy
│   └── Metrics tracking
│
├── Utility: scripts/ci/session_recovery.py
│   ├── Create session checkpoints
│   ├── Emit session heartbeats
│   ├── Detect workflow failures
│   ├── Manage recovery operations
│   └── Generate recovery metrics
│
└── Storage: .codex/sessions/
    ├── session_*.jsonl (session logs)
    ├── checkpoint_*.json (state snapshots)
    ├── session_recovery_log.jsonl (recovery events)
    └── session_heartbeats.jsonl (heartbeat log)
```

### Data Flow

```
Session Starts
    ↓
Periodic Checkpoints (15 min)
    ↓
Heartbeat Emissions (1 min)
    ↓
Session Failure Detected (timeout/error)
    ↓
session-recovery-handler.yml triggered
    ↓
Failure Context Extracted
    ↓
Check Recent Failures on Branch
    ├─ <2 failures → Auto-Recovery
    │   ├─ Log recovery event
    │   ├─ Restore checkpoint (if available)
    │   ├─ Re-trigger workflow (if safe)
    │   └─ Monitor recovery attempt
    │
    └─ ≥2 failures → Escalate
        ├─ Notify @mbaetiong
        ├─ Create escalation issue
        └─ Mark as manual recovery needed
```

---

## Usage

### For Session Agents (Copilot, custom agents)

#### Create a Checkpoint

```bash
python scripts/ci/session_recovery.py checkpoint --session-id <SESSION_ID>
```

**Example:**
```bash
python scripts/ci/session_recovery.py checkpoint --session-id 70e4f346-d908-43ef-a628-7697b5d4e099
```

**Output:**
```json
{
  "timestamp": "2026-06-23T22:57:43Z",
  "session_id": "70e4f346-d908-43ef-a628-7697b5d4e099", <!-- pragma: allowlist secret -->
  "checkpoint_type": "manual",
  "git_branch": "copilot/create-implementation-plan",
  "git_commit": "92b60067020a0a8675fa6daacd0c125bb43d3efb",
  "uncommitted_changes": false
}
```

#### Emit a Heartbeat

```bash
python scripts/ci/session_recovery.py heartbeat --session-id <SESSION_ID>
```

This should be called periodically (recommended: every 1-2 minutes) to indicate the session is still active.

### For CI/CD Workflows

#### Detect Workflow Failure

```bash
python scripts/ci/session_recovery.py detect-failure --workflow-run-id <RUN_ID>
```

**Example:**
```bash
python scripts/ci/session_recovery.py detect-failure --workflow-run-id 28059623643
```

**Output:**
```json
{
  "workflow_run_id": 28059623643,
  "detected": true,
  "failure_type": "cancelled",
  "branch": "copilot/create-implementation-plan",
  "duration_seconds": 3541
}
```

#### Recover a Failed Session

```bash
python scripts/ci/session_recovery.py recover --session-id <SESSION_ID> --workflow-run-id <RUN_ID>
```

**Example:**
```bash
python scripts/ci/session_recovery.py recover \
  --session-id 70e4f346-d908-43ef-a628-7697b5d4e099 \
  --workflow-run-id 28059623643
```

### For Monitoring and Metrics

#### Generate Recovery Metrics

```bash
python scripts/ci/session_recovery.py metrics --output-file .codex/session_recovery_metrics.json
```

**Output Example:**
```json
{
  "generated_at": "2026-06-23T22:57:43Z",
  "total_checkpoints": 12,
  "total_heartbeats": 487,
  "total_failures": 3,
  "total_recoveries": 2,
  "successful_recoveries": 2,
  "recovery_success_rate": 1.0
}
```

---

## Workflow: Session Recovery Handler

**File:** `.github/workflows/session-recovery-handler.yml`

### Trigger Conditions

The workflow is triggered when a `Running Copilot cloud agent` workflow completes with:
- Status: `cancelled`
- Conclusion: `cancelled`, `failure`, or `timed_out`

### Workflow Steps

1. **Extract Failed Workflow Context**
   - Extracts workflow run ID, branch, commit, status, conclusion, duration
   - Outputs context to job outputs for use in subsequent steps

2. **Create Session Recovery Log**
   - Creates a recovery log file: `.codex/session_recovery_<TIMESTAMP>.md`
   - Documents the failure and recovery attempt

3. **Log Recovery Event**
   - Appends event to `.codex/session_recovery_log.jsonl` for structured tracking

4. **Check Recovery Eligibility**
   - Queries recent failures on the branch (last 24 hours)
   - Determines if auto-recovery should be triggered
   - Counts consecutive failures to prevent infinite loops

5. **Auto-Recover (If Eligible)**
   - Automatic re-trigger if <2 consecutive failures
   - Logs recovery attempt
   - Stores recovery metadata

6. **Escalate (If Needed)**
   - Escalates to human review after 2+ consecutive failures
   - Creates escalation notification
   - Documents escalation reason

7. **Commit Recovery Artifacts**
   - Commits recovery logs and metrics to the branch
   - Uses `[skip ci]` to prevent recursive workflow triggers

### Configuration

Recovery behavior can be customized via `.codex/session_recovery_config.yml`:

```yaml
# Auto-recovery settings
auto_recovery_enabled: true
max_auto_recovery_attempts: 2
escalation_contact: "@mbaetiong"

# Session checkpointing
checkpoint_enabled: true
checkpoint_interval: 900  # 15 minutes

# Heartbeat monitoring
heartbeat_enabled: true
heartbeat_interval: 60  # 1 minute
heartbeat_timeout: 300  # 5 minutes
```

---

## Session State Persistence

### Checkpoint Storage

Checkpoints are stored in `.codex/sessions/` in JSON format:

```json
{
  "timestamp": "2026-06-23T22:57:43Z",
  "session_id": "70e4f346-d908-43ef-a628-7697b5d4e099",
  "checkpoint_type": "manual",
  "git_branch": "copilot/create-implementation-plan",
  "git_commit": "92b60067020a0a8675fa6daacd0c125bb43d3efb",
  "git_status": {
    "changed_files": ["src/example.py"]
  },
  "uncommitted_changes": false
}
```

### Recovery Log Format (JSONL)

`.codex/session_recovery_log.jsonl` contains one JSON object per line:

```jsonl
{"type":"session_failure_detected","timestamp":"2026-06-23T22:52:29Z","workflow_run_id":28059623643,"branch":"copilot/create-implementation-plan","status":"cancelled","recovery_triggered":true}
{"type":"recovery_initiated","timestamp":"2026-06-23T22:57:43Z","session_id":"70e4f346-d908-43ef-a628-7697b5d4e099","recovery_status":"initiated"}
{"type":"recovery_completed","timestamp":"2026-06-23T22:57:50Z","session_id":"70e4f346-d908-43ef-a628-7697b5d4e099","recovery_status":"completed"}
```

---

## Monitoring and Metrics

### Metrics Tracked

The system tracks:
- **Total Failures:** Count of detected session failures
- **Total Recoveries:** Count of recovery attempts initiated
- **Successful Recoveries:** Count of successful recovery completions
- **Recovery Success Rate:** `successful_recoveries / total_recoveries`
- **Average Recovery Time:** Average time to complete recovery
- **Escalation Count:** Number of escalations to human review

### Viewing Metrics

```bash
python scripts/ci/session_recovery.py metrics
```

Metrics are also saved to `.codex/session_recovery_metrics.json` for CI/CD integration and dashboards.

---

## Troubleshooting

### Session Keeps Failing

**Symptom:** A session repeatedly fails and triggers multiple recovery attempts.

**Solution:**
1. Check `.codex/session_recovery_log.jsonl` for failure patterns
2. Review the failed workflow run logs
3. Check git status and uncommitted changes
4. After 2 consecutive failures, escalation will automatically notify @mbaetiong

### Recovery Workflow Not Triggering

**Symptom:** Session fails but no recovery workflow is created.

**Solution:**
1. Verify `.github/workflows/session-recovery-handler.yml` is present and enabled
2. Check that the workflow trigger condition matches the failure type
3. Verify repository has permission to run workflows
4. Check GitHub Actions is enabled in repository settings

### Lost Session State

**Symptom:** Session state is not recovered after a failure.

**Solution:**
1. Check `.codex/sessions/` for checkpoint files
2. If no checkpoint exists, recovery starts from current git state
3. Ensure session is periodically calling `session_recovery.py checkpoint`
4. Review `.codex/session_recovery_config.yml` checkpoint settings

### Metrics Not Generated

**Symptom:** `.codex/session_recovery_metrics.json` is not being created.

**Solution:**
1. Run: `python scripts/ci/session_recovery.py metrics --output-file .codex/session_recovery_metrics.json`
2. Verify output file location is writable
3. Check `.codex/session_recovery_log.jsonl` exists and contains entries

---

## Integration with Copilot Sessions

### Automatic Checkpointing

To enable automatic checkpointing in a Copilot workflow:

```yaml
- name: Checkpoint session state
  run: |
    python scripts/ci/session_recovery.py checkpoint --session-id "${{ env.COPILOT_SESSION_ID }}"
```

### Heartbeat Emission

To emit periodic heartbeats:

```yaml
- name: Emit session heartbeat
  run: |
    while true; do
      python scripts/ci/session_recovery.py heartbeat --session-id "${{ env.COPILOT_SESSION_ID }}"
      sleep 60
    done &
  shell: bash
```

---

## Best Practices

1. **Regular Checkpointing:** Call `checkpoint` command at least every 15 minutes
2. **Heartbeat Monitoring:** Emit heartbeats at least every 1-2 minutes if session is active
3. **Log Retention:** Keep `.codex/session_recovery_log.jsonl` for audit trail (30-day retention)
4. **Metrics Review:** Regularly review recovery metrics to identify patterns and improve session stability
5. **Escalation Response:** Always respond to escalation notifications promptly
6. **Documentation:** Update this guide if recovery procedures change

---

## Emergency Recovery (Manual)

If automatic recovery fails or is not sufficient:

1. **Check Failed Workflow Run:**
   ```bash
   gh run view <RUN_ID>
   ```

2. **Review Session Logs:**
   ```bash
   cat .codex/session_recovery_log.jsonl
   ```

3. **Inspect Last Checkpoint:**
   ```bash
   ls -la .codex/sessions/ | tail -5
   ```

4. **Check Git State:**
   ```bash
   git status
   git log -5 --oneline
   ```

5. **Manual Recovery:**
   - Restore branch to last known good state (if needed)
   - Create new session with fresh checkout
   - Contact @mbaetiong if manual recovery is unclear

---

## Related Documentation

- **Session Recovery Workflow:** `.github/workflows/session-recovery-handler.yml`
- **Recovery Configuration:** `.codex/session_recovery_config.yml`
- **Recovery Utility:** `scripts/ci/session_recovery.py`
- **Session Recovery Log:** `.codex/SESSION_RECOVERY_LOG.md`
- **Accountability Report:** `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`

---

**Last Updated:** 2026-06-23T22:57:43Z  
**Next Review:** 2026-06-30 (weekly check-in)  
**Status:** ✅ ACTIVE
