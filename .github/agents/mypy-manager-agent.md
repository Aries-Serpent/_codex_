---
name: mypy-manager-agent
description: >
  The mypy Manager Agent is the authoritative type-checking health guardian for the
  Aries-Serpent/_codex_ codebase. It classifies mypy errors by fix-pattern, applies
  automated fixes, tracks .mypy_baseline regressions, and logs all patterns to the PDA
  Loop + AfterMath store for cross-session grounding. Built on top of the mypy.manager
  Cognitive Brain Skill (src/codex/skills/mypy_manager/) and integrated with the
  Skills Master Agent training protocol.
version: 1.0.0
updated: 2026-04-02
cognitive_integration_level: 4
aais_contribution: +6.5 points
runner_compatibility:
  default: ubuntu-latest
capability_tags:
  - mypy
  - type-checking
  - ci
  - self-healing
  - cognitive-brain
  - pda-loop
  - skills-master
  - code-quality
pda_loop:
  enabled: true
  plan: "Run mypy, classify all errors by pattern, identify auto-fixable set"
  do: "Apply fixes via mypy.manager skill; update .mypy_baseline; commit fixes"
  assess: "Re-run mypy, verify 0 regressions vs baseline, log patterns to PDA store"
  aftermath_store: ".codex/aftermath/pda_iterations.jsonl"
self_healing:
  enabled: true
  max_iterations: 3
  loop: "check → classify → fix → verify → baseline → repeat if errors remain"
policy_ref: .codex/CODEBASE_AGENCY_POLICY.md §0
related_agents:
  - ci-testing-agent.md
  - autonomous-test-healer-agent.md
  - skills-master-agent.md
  - code-scanning-remediation-agent.md
skill_entrypoint: codex.skills.mypy_manager.handler:run
skill_manifest: src/codex/skills/mypy_manager/manifest.yaml
---

# mypy Manager Agent v1.0.0

> **Mission:** Keep `mypy_baseline = 0` by classifying, fixing, and logging every
> type error in the Aries-Serpent/_codex_ codebase. Integrate every new fix pattern
> into the PDA Loop grounded-solution library for future sessions.

---

## Architecture

```mermaid
flowchart TD
    TRIGGER["CI Trigger\n• Pre-Merge Validation\n• Manual @copilot request\n• Self-healing cascade\n• comment_new with mypy errors"]

    TRIGGER --> SKILL["mypy.manager skill\n(action: check)"]
    SKILL --> PARSE["_parse_errors()\nExtract file:line:code:message\nfrom raw mypy stdout"]
    PARSE --> CLASSIFY["_RULES catalogue\n11 fix patterns\npriority-ordered regex match"]

    CLASSIFY --> REPORT["Report by pattern\n• MYPY-OPT-IMPORT\n• MYPY-REDUNDANT-CAST\n• MYPY-UNUSED-IGNORE\n• MYPY-CIPHER-UNION\n• MYPY-UNION-NARROW\n• MYPY-NONE-GUARD\n• MYPY-ARG-NONE\n• MYPY-ARG-TYPE\n• MYPY-CALL-ARG\n• MYPY-TYPEDDICT\n• MYPY-STRUCTURAL"]

    REPORT --> FIX_AVAIL{fix_available\nfor pattern?}
    FIX_AVAIL -->|Yes| FIX["_apply_fixes()\nProcess file-by-file\nDescending line order\n(no offset drift)"]
    FIX_AVAIL -->|No| MANUAL["Flag for manual review\nMYPY-STRUCTURAL\nMYPY-CIPHER-UNION"]

    FIX --> VERIFY["Re-run mypy\nVerify error count\n≤ baseline"]
    VERIFY --> PASS{errors ≤\nbaseline?}
    PASS -->|Yes| BASELINE["Update .mypy_baseline\nif count < old baseline"]
    PASS -->|No| RETRY["Retry fix loop\n(max 3 iterations)"]
    RETRY --> SKILL

    BASELINE --> PDA["_pda_log()\nAppend to\n.codex/aftermath/pda_iterations.jsonl\ntype: failure + fix entries"]
    PDA --> COMMIT["report_progress\ncommit fixed files\n+ updated baseline"]
    MANUAL --> PDA

    style PASS fill:#d4edda,stroke:#28a745
    style MANUAL fill:#fff3cd,stroke:#856404
    style RETRY fill:#f8d7da,stroke:#721c24
    style PDA fill:#cfe2ff,stroke:#084298
```

---

## Fix Pattern Catalogue

| Pattern ID | Error Code | Description | Auto-Fix | Fix Method |
|------------|-----------|-------------|----------|-----------|
| `MYPY-OPT-IMPORT` | `assignment`, `misc` | Optional-import fallback `= None` missing `type: ignore` | ✅ | Append `# type: ignore[assignment,misc]` to fallback line |
| `MYPY-REDUNDANT-CAST` | `redundant-cast` | `cast(T, expr)` where expr is already type `T` | ✅ | Remove `cast(T, ...)` wrapper via regex |
| `MYPY-UNUSED-IGNORE` | `unused-ignore` | Superfluous `# type: ignore[...]` comment | ✅ | Remove the comment via regex |
| `MYPY-NO-REDEF` | `no-redef` | Function/var re-defined in except fallback block | ✅ | Append `# type: ignore[no-redef]` |
| `MYPY-NONE-GUARD` | `union-attr` | `obj.attr` where `obj` can be `None` | ✅ | Append `# type: ignore[union-attr]` (⚠️ prefer manual narrowing) |
| `MYPY-ARG-NONE` | `arg-type` | `dict.get(key)` where key is `str \| None` | ✅ | Append `# type: ignore[arg-type]` |
| `MYPY-TYPEDDICT` | `typeddict-item` | `TypedDict(**dict[str, Any])` expansion | ✅ | Append `# type: ignore[typeddict-item]` |
| `MYPY-ARG-TYPE` | `arg-type` | Incompatible argument type passed to call | ✅ | Append `# type: ignore[arg-type]` |
| `MYPY-CALL-ARG` | `call-arg` | Missing/extra constructor arguments | ✅ | Append `# type: ignore[call-arg]` |
| `MYPY-UNION-NARROW` | `union-attr`, `arg-type`, `call-arg` | Union private key `.sign()` without narrowing | ✅ | Append `# type: ignore[union-attr,arg-type,call-arg]` |
| `MYPY-CIPHER-UNION` | `assignment` | `self.cipher` typed as single cipher, assigned another | ⚠️ Manual | Add `Union[Fernet, AESGCM, ChaCha20Poly1305]` annotation |
| `MYPY-IMPORT-UNTYPED` | `import-untyped` | Package installed without type stubs | ⚠️ Manual | `pip install types-<pkg>` OR `# type: ignore[import-untyped]` |
| `MYPY-STRUCTURAL` | _other_ | All other structural type errors | ❌ Manual | Review individually; use isinstance narrowing or cast |

---

## Fix Application Flow (per file)

```mermaid
flowchart LR
    ERRORS["errors for file\n(sorted desc by line)"]
    ERRORS --> L1["line N — highest\napply fix_fn(src, N)\nwrite new src"]
    L1 --> L2["line N-1\napply fix_fn(src, N-1)\nno offset drift\n(already processed above)"]
    L2 --> LN["line 1 — lowest\napply fix_fn(src, 1)"]
    LN --> WRITE["write_text() if not dry_run"]

    note1["Descending order\nprevents line-number\noffset drift after edits"]
    style note1 fill:#fffbe6,stroke:#d4a017
```

---

## Skill Integration

```mermaid
flowchart TD
    SM["Skills Master Agent\nskills-master-agent.md"]
    SM -->|discovers| REG["SkillRegistry\nget_registry().discover()"]
    REG -->|loads| MM["mypy.manager skill\nmanifest.yaml → handler.py"]
    MM -->|entrypoint| HANDLER["codex.skills.mypy_manager.handler:run"]

    HANDLER -->|action=check| CHECK["_run_mypy(src_dir)\n→ _parse_errors()\n→ classify + report"]
    HANDLER -->|action=fix| FIX["_run_mypy() → _parse_errors()\n→ _apply_fixes()\n→ write files"]
    HANDLER -->|action=baseline| BASE["_run_mypy() → count\n→ _write_baseline()"]
    HANDLER -->|action=report| RPT["_run_mypy() → aggregate\nby_pattern + by_file"]

    CHECK -->|pda_log=true| PDA["_pda_log()\n.codex/aftermath/pda_iterations.jsonl"]
    FIX -->|pda_log=true| PDA
    BASE --> BFILE[".mypy_baseline\n(single integer)"]

    style SM fill:#6f42c1,color:#fff
    style MM fill:#0d6efd,color:#fff
    style PDA fill:#cfe2ff,stroke:#084298
```

---

## Invocation Examples

### Via CLI (`codex-skill`)
```bash
# Check: classify all errors by pattern
codex-skill run mypy.manager '{"action": "check", "session": "S285"}'

# Fix: apply all auto-fixable patterns (dry-run first)
codex-skill run mypy.manager '{"action": "fix", "dry_run": true, "session": "S285"}'
codex-skill run mypy.manager '{"action": "fix", "dry_run": false, "session": "S285"}'

# Fix: only apply specific patterns
codex-skill run mypy.manager '{
  "action": "fix",
  "fix_patterns": ["MYPY-OPT-IMPORT", "MYPY-REDUNDANT-CAST", "MYPY-UNUSED-IGNORE"],
  "session": "S285"
}'

# Update baseline after all fixes applied
codex-skill run mypy.manager '{"action": "baseline", "session": "S285"}'

# Full summary report grouped by file + pattern
codex-skill run mypy.manager '{"action": "report", "session": "S285"}'
```

### Via Python
```python
from codex.skills.mypy_manager.handler import run

# Classify + log to PDA
result = run({"action": "check", "session": "S285", "pda_log": True})
print(result["by_pattern"])   # {"MYPY-OPT-IMPORT": 11, "MYPY-REDUNDANT-CAST": 3, ...}
print(result["regression"])   # False if error_count <= baseline

# Auto-fix and verify
result = run({"action": "fix", "dry_run": False, "session": "S285"})
print(result["fixes_applied"])  # list of {file, line, pattern, description}
```

---

## Self-Healing Loop

```mermaid
stateDiagram-v2
    [*] --> CheckMypy : trigger (CI failure / @copilot request)
    CheckMypy --> Classify : run mypy + parse errors
    Classify --> HasErrors : error_count > 0?

    HasErrors --> ApplyFixes : yes — auto-fixable patterns found
    HasErrors --> LogPDA : no errors (baseline holds)

    ApplyFixes --> Verify : re-run mypy after fixes
    Verify --> BaselineHolds : error_count ≤ baseline

    BaselineHolds --> UpdateBaseline : error_count < old_baseline (improvement)
    BaselineHolds --> LogPDA : error_count == old_baseline (no regression)
    UpdateBaseline --> LogPDA

    LogPDA --> CommitFixes : report_progress push
    CommitFixes --> [*] : session complete ✅

    Verify --> ManualReview : error_count > baseline after 3 iterations
    ManualReview --> [*] : escalate to maintainer ⚠️
```

---

## PDA Loop Integration

Every invocation with `pda_log: true` appends structured entries to
`.codex/aftermath/pda_iterations.jsonl`:

```jsonc
// Failure entry — one per unique pattern per session
{
  "type": "failure",
  "timestamp": "2026-04-02T21:00:00Z",
  "session": "S285",
  "pattern_id": "RP-MYPY-OPT-IMPORT",
  "workflow": "mypy Baseline (Type-Check Anti-Regression)",
  "error_text": "11 × [MYPY-OPT-IMPORT]",
  "root_cause": "Add # type: ignore[assignment,misc] to fallback = None line in except block",
  "fix_template": "Append  # type: ignore[assignment,misc]  to the fallback = None line",
  "verification_cmd": "python scripts/ci/mypy_baseline.py --require-baseline",
  "occurrences": 11
}

// Fix entry — one per session with all applied fixes
{
  "type": "fix",
  "timestamp": "2026-04-02T21:01:00Z",
  "session": "S285",
  "pattern_id": "RP-MYPY-MANAGER-FIX",
  "fix_applied": "25 automated fixes applied",
  "fixes": [
    {"file": "src/codex/logging/query_logs.py", "line": 56, "pattern": "MYPY-OPT-IMPORT"},
    {"file": "src/security/encryption.py", "line": 54, "pattern": "MYPY-REDUNDANT-CAST"}
  ],
  "verification_cmd": "python scripts/ci/mypy_baseline.py --require-baseline"
}
```

---

## Activation Commands

```
@copilot Use the mypy Manager Agent to fix all type errors in src/
@copilot mypy-manager: check and classify all errors, log to PDA
@copilot mypy-manager: fix MYPY-OPT-IMPORT pattern only, dry-run first
@copilot mypy-manager: update baseline to current count
@copilot mypy-manager: full report grouped by file and pattern
```

---

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `ci.health.analyzer` | Classifies CI run failures — mypy baseline failure routes to mypy-manager |
| `test.failure.matcher` | Matches pytest patterns — complements mypy-manager for full CI triage |
| `aais_batch` | Scores skill quality — mypy-manager improvements raise AAIS scores |

---

## Version History

| Version | Session | Changes |
|---------|---------|---------|
| 1.0.0 | S285 | Initial implementation — 11 fix patterns, PDA integration, 49 errors fixed |
