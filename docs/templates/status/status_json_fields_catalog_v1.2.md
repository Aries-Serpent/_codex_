# Catalog: Status JSON Fields (v1.2)
> Generated: 2024-11-02 15:32:16 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Schema Catalog Author], [Secondary: Reviewer] ⚡ Energy: 5

Top-Level
| Field | Type | Required | Notes |
|---|---|---:|---|
| metadata | object | Yes | Title, timestamps, git_context, environment |
| snapshot | object | Yes | Repo map, capabilities, findings, tests_gates, repro, deferred |
| delta | object | No | Changes since previous report |
| patches | array | No | Atomic patch diffs |
| automation | object | No | CI/automation-produced data |
| security | object | No | Redactions, threat model version |
| questions | array | No | Q/A lifecycle |
| decisions | array | No | Decision log |
| tokenization | object | No | Tokenizer insights |
| ml_test_score | object | No | ML test coverage |
| hydra_config_snapshot | object | No | Hydra config state |

Snapshot Highlights
| Path | Description |
|---|---|
| snapshot.capabilities[].id | CAP-XXX identifier |
| snapshot.findings[].id | FIND-XXX identifier |
| snapshot.tests_gates.coverage_percent | Overall coverage (0–100) |
| snapshot.repro.registry[].id | REPRO-XXX identifier |
