# Spec: Automation Data Ingest for Status v1.2
> Generated: 2025-11-02 15:26:48 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Automation Spec Author], [Secondary: CI Integrator] ⚡ Energy: 5

Scope
- Defines required/optional fields for `automation` in the v1.2 status schema.
- Provides canonical shapes and examples for machine producers.

Sections and Shapes
| Field | Type | Required | Notes |
|---|---|---:|---|
| issues | array<object> | No | Full list of issues; match schema keys exactly |
| pull_requests | array<object> | No | Full list of PRs; match schema keys exactly |
| coverage | number (0–100) | No | Overall % from coverage tools |
| dependency_audit | object | No | Tool + vulnerabilities summary |
| security_scan | object | No | SAST and secrets scan summaries |
| performance | object | No | Training/inference/memory snapshots |
| capability_autodiscovery | object | No | New files/modules and suggested CAPs |
| mlflow_tracking | object | No | Offline MLflow counts and paths |
| nox_results | object | No | Sessions_run/Passed/Failed arrays |

Examples (YAML-like, conceptual)
- issues:
  - url: "https://github.com/Aries-Serpent/_codex_/issues/1"
    number: 1
    title: "Fix schema validation"
    state: "open"
    labels: ["schema", "validation"]
    author: "user"
    created_at: "2025-11-02T10:00:00Z"
    updated_at: "2025-11-02T11:00:00Z"

- performance:
  training:
    throughput_steps_per_sec: 12.3
    epoch_time_seconds: 45.6
    batch_size: 16
  inference:
    latency_p50_ms: 8.1
    latency_p95_ms: 10.4
    latency_p99_ms: 12.7
    device: "cpu"
  memory:
    peak_ram_gb: 2.6
    peak_vram_gb: 0.0

Producer Guidance
- Emit only fields you can determine; omit unknowns (schema allows additionalProperties).
- Use ISO8601 UTC for timestamps.
- Keep arrays ordered deterministically for diff stability in PRs.

Consumer Guidance
- Validate using `jsonschema` (Draft 2020-12).
- Do not mutate producer artifacts in-place; write transforms to new files for auditability.

CI Integration
- Produce artifacts as JSON files during workflow runs.
- Summarize into the daily status report via a bundling step (`scripts/status/validate_and_publish.py`).
