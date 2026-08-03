# Cognitive Brain Runtime — Operator Runbook

## Overview
The Cognitive Brain Runtime is the process-level control plane for model negotiation, tool-surface selection, shell safety, and telemetry in `src.codex.cognitive_brain`. It boots a singleton kernel, enforces model/tool safety before execution, and emits decision records that let operators trace why a model or toolchain was chosen.

## Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `COGNITIVE_BRAIN_POLICY_SEED` | `42` | Seed used by `DeterministicPolicy` when ranking toolchains. |
| `COGNITIVE_BRAIN_REGISTRY_TTL` | `3600` | TTL in seconds for cached `ModelCapabilityProfile` entries. |
| `COGNITIVE_BRAIN_ALLOW_SHELL` | `false` | Enables shell participation in orchestration and makes the default `ShellPolicy` shell-enabled. |
| `COGNITIVE_BRAIN_TELEMETRY_PATH` | unset | When set, appends telemetry events to an NDJSON file in addition to in-memory storage. |
| `CODEX_SESSION_ID` | unset | Injected into emitted telemetry events as `session_id`. |
| `COGNITIVE_BRAIN_FAILSAFE_OFF` | `false` | Disables auto-load; `assert_loaded()` raises instead of auto-booting. |
| `COGNITIVE_BRAIN_AUTO_LOAD` | `true` | Controls whether `auto_load()` boots the kernel automatically. |
| `COPILOT_AGENT_CCA_VERSION_LOCK` | `stable` | Required CCA pin; deviations generate startup warnings. |
| `COPILOT_AGENT_DEDUPLICATION_ENABLED` | `true` | Required CCA payload deduplication flag; `false` generates startup warnings. |
| `COPILOT_AGENT_TURN_ISOLATION_ENABLED` | `true` | Required CCA turn-isolation flag; `false` generates startup warnings. |

## Startup and Auto-Load
`auto_load()` returns `get_kernel()` only when `COGNITIVE_BRAIN_AUTO_LOAD=true` and `COGNITIVE_BRAIN_FAILSAFE_OFF!=true`; otherwise it returns `None`. It never raises; boot failures are logged as warnings.

`assert_loaded()` is the hard entrypoint guard for reasoning-critical code. If the kernel is already loaded it is a no-op; if not, it auto-boots unless `COGNITIVE_BRAIN_FAILSAFE_OFF=true`, in which case it raises `RuntimeError`.

`COGNITIVE_BRAIN_FAILSAFE_OFF=true` therefore switches the runtime from fail-open auto-boot to fail-fast manual boot.

```python
from src.codex.cognitive_brain.kernel import auto_load, get_kernel

kernel = auto_load() or get_kernel()
kernel.assert_loaded()
```

## Model Negotiation
The negotiator strips config keys gated by `supports_reasoning_effort`: `reasoning_effort` and `thinking`. This prevents model-specific `session.create` failures on models whose capability profile does not advertise reasoning-effort support.

Use `kernel.negotiate_model()` when you want negotiation telemetry; `safe_session_config()` only returns the cleaned config.

```python
from src.codex.cognitive_brain.kernel import get_kernel

kernel = get_kernel()
result = kernel.negotiate_model(
    "claude-haiku-4.5",
    {"reasoning_effort": "high", "max_tokens": 4096},
    required_capabilities=["reasoning_effort"],
)
print(result.resolved_model_id)
print(result.stripped_params)
print(kernel.telemetry.query(event_type="negotiation", limit=1)[0].payload)
```

Default fallback model chain, in order:
1. `claude-sonnet-5`
2. `claude-sonnet-4.6`
3. `claude-opus-4.8`
4. `claude-opus-4.7`
5. `claude-opus-5`
6. `gpt-5.5`
7. `gpt-5.4`
8. `gemini-3.1-pro-preview`
9. `grok-4.5`

## Session Guard
Use `safe_create_session()` or `SessionGuard.create_session()` for every `session.create` call. The guard runs model negotiation, injects the resolved model under `safe_config["model"]`, generates a `decision_id`, and optionally emits a `session_guard` telemetry event.

`SessionCreateResult` contains:
- `safe_config`
- `negotiation`
- `decision_id`
- `turn_id`
- `task_id`
- `duration_ms`
- `notes`

Pass `turn_id` and `task_id` from the caller so the resulting telemetry can be joined to turn logs, PR/task logs, and incident timelines.

```python
from src.codex.cognitive_brain.session_guard import safe_create_session

result = safe_create_session(
    "claude-haiku-4.5",
    {"reasoning_effort": "high", "max_tokens": 4096},
    required_capabilities=["reasoning_effort"],
    turn_id="turn-2026-08-03-001",
    task_id="pr-5430",
)
api_payload = result.safe_config
```

## Shell Execution Safety
`ShellPolicy.gate(command, cwd)` evaluates commands in this order:
1. working-directory allowlist check
2. deny-pattern match
3. allow-pattern match
4. default decision when no pattern matched

Deny patterns have precedence over allow patterns. `sudo *`, `curl * | sh`, `wget * | bash`, `rm -rf /*`, `dd *`, `mkfs *`, and similar patterns are always denied.

Working-directory constraints are prefix-based. If `working_dir_allowlist` is configured, `cwd` must start with at least one allowed prefix or the command is denied with `risk_flags=["cwd_violation"]`.

Token redaction is applied before logging commands and after capturing output. Built-in redaction covers GitHub PATs, `GITHUB_TOKEN=...`, `CODEX_MASTER_KEY=...`, bearer tokens, `--password ...`, and `--token ...`.

Set `COGNITIVE_BRAIN_ALLOW_SHELL=true` to opt in to shell execution. In the default policy this sets `default_shell_enabled=True`; unmatched commands become `ALLOW` or `AUDIT` instead of hard `DENY`, but deny rules still win.

```python
from src.codex.cognitive_brain.shell_policy import get_default_policy, PolicyVerdict

policy = get_default_policy()
decision = policy.gate("git status", cwd="/repo")
if decision.verdict == PolicyVerdict.DENY:
    raise PermissionError(decision.reason)
print(decision.safe_command)
```

## Capability Registry and Tool Surface Parity

| Surface | Count | Read-only | Requires auth | Network | Policy-gated | Canonical entry |
| --- | ---: | --- | --- | --- | --- | --- |
| GitHub MCP | 35 | yes | yes | yes | no | `ToolSurfaceCategory.GITHUB_MCP` |
| Playwright | 21 | no | no | yes | no | `ToolSurfaceCategory.PLAYWRIGHT` |
| web_search | 1 | yes | no | yes | no | `ToolSurfaceCategory.WEB_SEARCH` |
| shell | 1 | no | no | yes | yes | `ToolSurfaceCategory.SHELL` |

The tool-surface registry is versioned by `CAPABILITY_SCHEMA_VERSION`, currently `2.0.0`. Check compatibility with `check_capability_schema_version(required_version)` or per-profile `is_compatible_with(required_version)`; compatibility is major-version based.

Register custom model capability profiles by injecting a `ModelCapabilityProfile` into `CapabilityRegistry.register()`.

```python
from src.codex.cognitive_brain.capability_registry import (
    CapabilityRegistry,
    ModelCapabilityProfile,
    check_capability_schema_version,
)

assert check_capability_schema_version("2.0.0")
registry = CapabilityRegistry()
registry.register(
    ModelCapabilityProfile(
        model_id="my-custom-model",
        supports_reasoning_effort=True,
        supports_streaming=True,
        supports_tools=True,
    )
)
```

## Telemetry and Decision Forensics
Emitted event types are `startup`, `negotiation`, `policy_score`, `orchestration`, `fallback`, `forensics`, and `session_guard`.

| event_type | Key fields | Purpose |
| --- | --- | --- |
| `startup` | `payload.version`, `payload.config` | Confirms kernel boot and startup config. |
| `negotiation` | `model_id`, `payload.stripped_params`, `payload.resolved_model` | Records model-parameter stripping and fallback selection. |
| `policy_score` | `task_intent`, `payload.plan_id`, `payload.scores` | Captures plan scoring from the deterministic policy. |
| `orchestration` | `task_intent`, `payload.primary_tool`, `payload.notes` | Records the chosen toolchain. |
| `fallback` | `payload.label`, `payload.attempts`, `payload.final_strategy` | Records fallback execution outcome. |
| `forensics` | `decision_id`, `turn_id`, `task_id`, `payload.selected_toolchain`, `payload.rejected_alternatives` | Enables per-decision traceability across turns/tasks. |
| `session_guard` | `decision_id`, `turn_id`, `task_id`, `payload.original_model`, `payload.resolved_model` | Traces guarded `session.create` calls. |

Query events with `CognitiveTelemetry.query(event_type=..., model_id=..., task_intent=..., limit=...)`. In the kernel wiring, `query()` reads from the first backend, which is the in-memory backend; NDJSON is the persistence sink, not the default query source.

`decision_id`, `turn_id`, and `task_id` are the cross-system tracing fields. `decision_id` identifies one negotiation/planning decision, `turn_id` links the decision to an agent turn, and `task_id` links it to a PR, issue, or external task. Use all three on long-running or incident-sensitive flows.

When `COGNITIVE_BRAIN_TELEMETRY_PATH` is set, telemetry is also appended to NDJSON. The NDJSON reader tolerates older records by discarding unknown keys during reload.

```python
from src.codex.cognitive_brain.kernel import get_kernel

kernel = get_kernel()
events = kernel.telemetry.query(event_type="startup", limit=5)
for event in events:
    print(event.timestamp, event.event_type, event.payload)
```

## Enable/Disable Guide

| Subsystem | Enable | Disable | Effect |
| --- | --- | --- | --- |
| Kernel auto-load | `COGNITIVE_BRAIN_AUTO_LOAD=true` | `COGNITIVE_BRAIN_AUTO_LOAD=false` | Controls whether `auto_load()` boots automatically. |
| Fail-fast boot guard | `COGNITIVE_BRAIN_FAILSAFE_OFF=true` | `COGNITIVE_BRAIN_FAILSAFE_OFF=false` | Raises on unloaded entrypoints instead of auto-booting. |
| Shell planning + default shell policy | `COGNITIVE_BRAIN_ALLOW_SHELL=true` | `COGNITIVE_BRAIN_ALLOW_SHELL=false` | Adds shell to orchestration candidates and enables default shell execution. |
| NDJSON telemetry persistence | Set `COGNITIVE_BRAIN_TELEMETRY_PATH` | Unset `COGNITIVE_BRAIN_TELEMETRY_PATH` | Persists events to file in addition to memory. |
| Session/task forensics | Pass `turn_id` and `task_id` to `safe_create_session()` / `plan_tools()` | Omit identifiers | Keeps or removes caller-level trace joins. |
| CCA stability guardrails | `stable` / `true` / `true` | Any other values | Keeps startup warnings silent or emits CCA risk warnings. |

## Fallback Order
Model fallback order is the negotiator chain listed above. If the requested model lacks a required capability, the first compatible fallback is selected; if no fallback satisfies the requirement, the runtime proceeds on the original model with unsupported params stripped and records the failure in notes/logging.

Tool fallback order is planner-driven:
- primary candidate comes from policy ranking over `github_mcp`, `playwright`, `web_search`, and optionally `shell`
- second-ranked candidate becomes `fallback_plan`
- per-step fallback mapping is `github_mcp -> web_search`, `playwright -> web_search`, `web_search -> github_mcp`, `shell -> github_mcp`

## Incident Response
### `reasoning_effort` error
1. Wrap the call with `safe_create_session()`.
2. Require `required_capabilities=["reasoning_effort"]` if the caller truly needs it.
3. Inspect `result.params_stripped`, `result.resolved_model`, and the latest `negotiation` or `session_guard` event.
4. If the model should support the feature, update the registry with `register(ModelCapabilityProfile(...))` and retry.

### Kernel not loaded at entrypoint
1. Call `auto_load()` at process start.
2. Add `kernel.assert_loaded()` at the reasoning-critical entrypoint.
3. If `COGNITIVE_BRAIN_FAILSAFE_OFF=true`, switch it off or explicitly call `boot()` before the entrypoint.
4. Confirm a `startup` event exists.

### Shell command denied
1. Check `GateDecision.reason` and `risk_flags`.
2. Verify `cwd` is inside the configured allowlist.
3. If the command is legitimate, prefer rewriting it to match an existing allow pattern.
4. Only extend allow patterns by constructing an explicit `ShellPolicy(...)`; deny rules should not be weakened casually.

### Model capability outage
1. Query recent `negotiation` and `session_guard` events for the failing model.
2. Force required capabilities so the negotiator selects a fallback deterministically.
3. If all fallbacks fail, proceed with stripped config only if the feature is optional; otherwise block the caller and register a corrected capability profile.
4. Record `decision_id`, `turn_id`, and `task_id` in the incident timeline.

## Verification Steps
```bash
cd /home/runner/work/_codex_/_codex_
python - <<'PY'
from src.codex.cognitive_brain.kernel import reset_kernel, auto_load, get_kernel
reset_kernel()
kernel = auto_load() or get_kernel()
print(kernel.is_loaded)
print(kernel.telemetry.query(event_type="startup", limit=1)[0].event_type)
PY
```

```bash
cd /home/runner/work/_codex_/_codex_
python - <<'PY'
from src.codex.cognitive_brain.kernel import reset_kernel, get_kernel
reset_kernel()
kernel = get_kernel()
result = kernel.negotiate_model(
    "claude-haiku-4.5",
    {"reasoning_effort": "high", "max_tokens": 128},
    required_capabilities=["reasoning_effort"],
)
print(result.resolved_model_id)
print(result.stripped_params)
print(kernel.telemetry.query(event_type="negotiation", limit=1)[0].payload)
PY
```

```bash
cd /home/runner/work/_codex_/_codex_
python - <<'PY'
from src.codex.cognitive_brain.session_guard import SessionGuard
from src.codex.cognitive_brain.telemetry import CognitiveTelemetry
telemetry = CognitiveTelemetry()
guard = SessionGuard(telemetry=telemetry)
result = guard.create_session(
    "claude-haiku-4.5",
    {"reasoning_effort": "high"},
    required_capabilities=["reasoning_effort"],
    turn_id="verify-turn",
    task_id="verify-task",
)
event = telemetry.query(event_type="session_guard", limit=1)[0]
print(result.safe_config["model"])
print(event.decision_id == result.decision_id, event.turn_id, event.task_id)
PY
```

```bash
cd /home/runner/work/_codex_/_codex_
COGNITIVE_BRAIN_ALLOW_SHELL=true python - <<'PY'
from src.codex.cognitive_brain.shell_policy import reset_default_policy, get_default_policy
reset_default_policy()
policy = get_default_policy()
decision = policy.gate("git status", cwd=".")
print(decision.verdict.value, decision.allowed)
print(policy.redact("GITHUB_TOKEN=secret123 git status"))
PY
```

```bash
cd /home/runner/work/_codex_/_codex_
COGNITIVE_BRAIN_TELEMETRY_PATH=docs/cognitive_brain/telemetry-smoke.ndjson python - <<'PY'
from pathlib import Path
from src.codex.cognitive_brain.kernel import reset_kernel, get_kernel
reset_kernel()
kernel = get_kernel()
kernel.negotiate_model("claude-haiku-4.5", {"reasoning_effort": "high"}, ["reasoning_effort"])
print(Path("docs/cognitive_brain/telemetry-smoke.ndjson").exists())
PY
rm -f docs/cognitive_brain/telemetry-smoke.ndjson
```

## CCA Stability Requirements
Required settings:
- `COPILOT_AGENT_CCA_VERSION_LOCK=stable`
- `COPILOT_AGENT_DEDUPLICATION_ENABLED=true`
- `COPILOT_AGENT_TURN_ISOLATION_ENABLED=true`

If they are wrong, kernel boot still completes, but `_assert_cca_stability()` emits warnings for version drift, disabled payload deduplication, or disabled turn-state isolation. Operationally, that means elevated risk of duplicate function-call IDs, payload reuse across turns, and turn-state leakage in multi-turn CCA flows.
