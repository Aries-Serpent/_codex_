# IMDS Error Reason Codes Reference (v1.5)
> Generated: 2025-11-14 23:07:55 UTC | Author: mbaetiong

## Purpose
Document machine-readable error codes included in `error_reasons` array of JSON summary.

## Codes
| Code | Meaning | Typical Cause | Remediation |
|------|--------|---------------|------------|
| dns_resolution_failure | Name resolution failure | Broken resolver config | Validate resolv.conf / network |
| connection_timeout | TCP timeout | Firewall / NSG / route block | Inspect ACLs, confirm route |
| http_request_failure | Generic curl failure | Transient network / proxy | Retry / inspect proxy chain |
| non_200_status | IMDS responded non-200 | Service issue / header missing | Re-check header / VM state |
| tcp_port_unreachable | Port 80 connect failed | Firewall or routing block | Allow outbound / add route |
| hosts_override | /etc/hosts mapping present | Manual override / artifact | Remove mapping |
| iptables_drop_rule | DROP rule referencing IP | Misconfigured firewall policy | Insert ACCEPT rule / adjust chain |
| walinuxagent_inactive | Agent inactive | Service crash / disabled | Restart/enable WALinuxAgent |
| metadata_ip_redirect | blocked.jsonl redirect signature | Local proxy interception | Remove redirect rule/proxy |
| missing_route | No route to metadata IP | Network config gap | Add link-local route |

## Validation Script
