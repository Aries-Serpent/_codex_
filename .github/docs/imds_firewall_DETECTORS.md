# IMDS Firewall Detectors
> Generated: 2025-11-14 23:14:07 UTC | Author: mbaetiong

## Purpose
Explain detection-only checks for UFW and firewalld introduced in `imds_diagnostic.sh` v1.6.

## Scope
- Detection highlights potential rules impacting IMDS egress.
- No automatic modification is performed for these systems.
- Recommendations are produced for manual review.

## UFW Detector
| Command | Behavior |
|---------|----------|
| `ufw status numbered` | Scans for `169.254.169.254`, `DENY OUT`, `REJECT OUT` |

- Error code: `ufw_block_rule`
- Recommendation: "Review UFW outbound rules; ensure 169.254.169.254 is permitted."

## firewalld Detector
| Command | Behavior |
|---------|----------|
| `firewall-cmd --get-zones` + `--list-all` per zone | Searches zone config output for `169.254.169.254` references |

- Error code: `firewalld_rule_imds`
- Recommendation: "Review firewalld zone rules for IMDS egress allowance."

## Notes
- iptables/nftables checks remain in place and may overlap with these detectors.
- Detectors are heuristics; absence of findings is not a guarantee that egress is allowed.

Relates to: #2226
