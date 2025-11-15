# IMDS Metrics Exporter Guide (v1.5 Update)
> Generated: 2025-11-14 23:07:55 UTC | Author: mbaetiong

## Additions
| Update | Description |
|--------|-------------|
| Version annotation | Metrics file now includes tool version |
| Runtime tracking | `runtime_ms` captured in JSON (not gauge yet) |
| HTML integration | Metrics embedded in HTML report if generated |

## Metrics File
`imds_metrics.prom`  
Prometheus textfile format; scraped via node_exporter textfile collector.

## Metric Catalog
| Metric | Type | Values | Description |
|--------|------|--------|-------------|
| `imds_http_reachable` | Gauge | 0/1 | HTTP metadata endpoint reachable |
| `imds_tcp_reachable` | Gauge | 0/1 | Raw TCP connect to 169.254.169.254:80 |
| `imds_ping_success` | Gauge | 0/1 | ICMP heuristic |
| `hosts_override_present` | Gauge | 0/1 | /etc/hosts override exists |
| `iptables_drop_detected` | Gauge | 0/1 | DROP rule blocking metadata |
| `walinuxagent_active` | Gauge | 0/1 | WALinuxAgent active |
| `redirect_signature_present` | Gauge | 0/1 | blocked.jsonl redirect signature |
| `route_to_imds_present` | Gauge | 0/1 | IP route exists |
| `hostname_mapped_to_imds` | Gauge | 0/1 | Hostname mapped to IP |

## Sample
