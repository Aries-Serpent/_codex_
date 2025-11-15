# IMDS Diagnostic Runbook (Canonical v1.5 Expansion)
> Generated: 2025-11-14 23:07:55 UTC | Author: mbaetiong

## 1. Purpose
This runbook documents the fully expanded IMDS diagnostic and minimal remediation tool (`.github/scripts/imds_diagnostic.sh`) now at version 1.5, integrating environment classification, performance timing (runtime_ms), memory snapshot, HTML reporting, and extended JSON fields.

## 2. Supported Modes
| Mode | Command | Output | System Changes |
|------|---------|--------|----------------|
| Diagnostics | `bash .github/scripts/imds_diagnostic.sh` | `diagnostic_results.txt` | None |
| Dry-run | `bash .github/scripts/imds_diagnostic.sh --dry-run` | Recommendations preview | None |
| Apply (approved) | `sudo IMDS_APPROVAL_TOKEN=<tok> bash .github/scripts/imds_diagnostic.sh --apply` | Remediation + audit JSONL | Yes |
| JSON Summary | `bash .github/scripts/imds_diagnostic.sh --json` | `diagnostic_results.json` | None |
| Metrics Export | `bash .github/scripts/imds_diagnostic.sh --metrics` | `imds_metrics.prom` | None |
| HTML Report | `bash .github/scripts/imds_diagnostic.sh --html --json` | `imds_report.html` | None |
| Self-Test | `bash .github/scripts/imds_diagnostic.sh --self-test` | Validation routine | None |
| Full Evidence | `sudo IMDS_APPROVAL_TOKEN=<tok> bash .github/scripts/imds_diagnostic.sh --apply --json --metrics --html` | All artifacts | Yes |

## 3. New v1.5 Additions
| Feature | Description | Benefit |
|---------|-------------|---------|
| Environment classifier | Heuristics: azure_vm, gha_runner, container, onprem_vm | Contextual interpretation |
| Performance timing | `runtime_ms` captured | SLA & latency tracking |
| Memory snapshot | MemTotal / MemFree / MemAvailable (kB) | Capacity context |
| HTML report | Human-friendly consolidated view | Rapid triage |
| Extended JSON fields | `env_class`, memory, runtime metrics | Automation-ready |
| Hardened dependency checks | Graceful degrade for missing tools | Reliability |

## 4. Diagnostic Coverage
| # | Category | Detail | Evidence |
|---|----------|--------|---------|
| 1 | Env snapshot | Hostname, kernel, distro, interfaces, IP, memory | results.txt |
| 2 | Classification | azure_vm / gha_runner / container / onprem_vm | results.txt |
| 3 | HTTP reachability | Curl with metadata header | status line / error reason |
| 4 | TCP reachability | Raw bash socket connect | success/failure |
| 5 | Ping heuristic | Single ICMP attempt | gauge only |
| 6 | /etc/hosts overrides | Metadata IP lines | numbered lines |
| 7 | iptables screening | OUTPUT chain + DROP rules | rule subset |
| 8 | nftables screening | Ruleset search | matching lines |
| 9 | WALinuxAgent health | Active state + journal tail | last 100 lines |
|10 | Redirection signatures | blocked.jsonl IP redirect to 127.0.0.1 | presence/absence |
|11 | Routing presence | `ip route get` + policy rules | route or missing |
|12 | DNS heuristic | Hostname mapped to metadata IP | hostnames list |
|13 | Recommendations | Aggregated fix suggestions | summary section |
|14 | JSON summary | Structured extended fields | `diagnostic_results.json` |
|15 | Metrics | Prometheus gauges | `imds_metrics.prom` |
|16 | HTML report | Consolidated visual summary | `imds_report.html` |
|17 | Audit trail | JSONL append on remediation | `.codex/audit/imds_remediations.jsonl` |

## 5. Remediation (Guarded)
| Action | Trigger | Backup | Notes |
|--------|---------|--------|-------|
| Remove /etc/hosts lines | Override present | `/etc/hosts.bak.d/hosts.bak.<ts>` | Reversible |
| Insert iptables ACCEPT | Missing allow rule | N/A (removable rule) | Minimal change |
| Restart WALinuxAgent | Service installed | Service restart only | Safe |

## 6. Exit Codes
| Code | Meaning | Operator Action |
|------|---------|-----------------|
| 0 | Diagnostics OK | Attach outputs to issue #2226 |
| 1 | Error occurred | Inspect error reasons / retry |
| 2 | Remediation recommended | Seek @mbaetiong approval |
| 3 | Remediation applied | Re-run diagnostics & attach before/after |

## 7. Extended JSON Fields
| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Tool version (1.5) |
| `env_class` | string | Environment classifier |
| `runtime_ms` | integer | Execution duration |
| `mem_total_kb` | integer | Total memory |
| `mem_free_kb` | integer | Free memory |
| `mem_available_kb` | integer | Available memory |
| `recommendation_count` | integer | Recommendations length |
| `actions_count` | integer | Actions applied length |
| `error_reasons` | array[string] | Machine error codes |
| `metrics_generated` | boolean | Metrics file produced |

## 8. Metrics Catalog
| Metric | 0 | 1 | Description |
|--------|---|---|-------------|
| `imds_http_reachable` | Fail | Success | HTTP GET to IMDS with header |
| `imds_tcp_reachable` | Fail | Success | Raw TCP connect |
| `imds_ping_success` | Fail | Success | ICMP heuristic |
| `hosts_override_present` | No | Yes | /etc/hosts override exists |
| `iptables_drop_detected` | No | Yes | DROP rule referencing IP |
| `walinuxagent_active` | Inactive | Active | Agent health |
| `redirect_signature_present` | Absent | Present | blocked.jsonl redirect |
| `route_to_imds_present` | Missing | Present | Link-local route |
| `hostname_mapped_to_imds` | None | Present | Hostname mapping |

## 9. HTML Report Contents
| Section | Description |
|---------|-------------|
| Header | Status, timestamp, env_class |
| Summary | Raw JSON formatted (if JSON mode) |
| Recommendations | Color-coded list |
| Metrics | Raw metrics file (if exported) |
| Raw Output | Full textual diagnostic log |

## 10. Approval Policy Summary
| Requirement | Mechanism |
|------------|-----------|
| Token (strict) | `IMDS_APPROVAL_TOKEN` or `--approval-token` |
| Bypass (sandbox) | `--no-approval` flag |
| Root required | UID check for `--apply` |
| Audit trail | JSONL append with token hash |
| Backup creation | `/etc/hosts.bak.d/hosts.bak.<ts>` |

## 11. Self-Test Routine
Command: `bash .github/scripts/imds_diagnostic.sh --self-test`  
Performs syntax, dry-run, JSON, and HTML generation tests. Does not modify system or require token.

## 12. Suggested CI Gating
