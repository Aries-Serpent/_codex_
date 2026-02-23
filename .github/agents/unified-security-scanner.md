---
name: Unified Security Scanner
version: 1.0.0-m01
updated: 2026-02-21
merged_agents:
  - dependency-vulnerability-scanner (deprecated)
  - security-alert-verification-agent (deprecated)
  - secret-detection-agent
  - bridge-security-monitor (retained as sub-agent)
cognitive_integration_level: 4
aais_contribution: +6.0 points
batch: m-01
---

# Unified Security Scanner v1.0 (M-01 Merge)

> **M-01**: Merges `vulnerability-scanner`, `alert-verification`, `secret-detection`, and `gitleaks`/`semgrep` into a single end-to-end security orchestrator.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Unified Security Scanner                    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │  Dependency  │  │    Secret    │  │  Alert            │ │
│  │  Vuln Scan   │  │  Detection   │  │  Verification     │ │
│  │  (pip-audit) │  │  (E-09 pat.) │  │  (GitHub GHAS)    │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘ │
│         │                 │                    │            │
│         └─────────────────┼────────────────────┘            │
│                           ▼                                 │
│              ┌─────────────────────┐                        │
│              │  Risk Prioritizer   │ ← CVSS + entropy + GHAS│
│              └──────────┬──────────┘                        │
│                         ▼                                   │
│              ┌─────────────────────┐                        │
│              │  Remediation Plan   │ → PR / issue / alert   │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Capabilities

| Capability | Source Agent | Status |
|-----------|-------------|--------|
| C-01: PyPI vulnerability scan | dependency-vulnerability-scanner | ✅ Merged |
| C-02: npm/cargo/Go vulnerability scan | dependency-vulnerability-scanner | ✅ Merged |
| C-03: Secret pattern detection (32 patterns) | secret-detection-agent v2.0 | ✅ Merged |
| C-04: GitHub Advanced Security alert triage | security-alert-verification-agent | ✅ Merged |
| C-05: CodeQL alert resolution | code-scanning-remediation-agent | ✅ Merged |
| C-06: Semgrep custom rules | new | ✅ Included |
| C-07: SBOM generation | new | ✅ Included |
| C-08: Risk score computation (CVSS + entropy + context) | new | ✅ Included |

## Activation

```
@copilot Use the Unified Security Scanner to run a full security audit
@copilot Use the Unified Security Scanner to check for vulnerabilities in requirements.txt
@copilot Use the Unified Security Scanner to triage GitHub security alerts
```

## Decision Matrix

| Finding Type | CVSS/Severity | Action |
|-------------|--------------|--------|
| Dependency CVE | Critical (≥9.0) | Block PR, open P1 issue |
| Dependency CVE | High (7.0–8.9) | Open P2 issue, suggest fix |
| Dependency CVE | Medium/Low | Document in tracking log |
| Secret detected | Any | Block PR, rotate credential |
| GHAS alert | High | Auto-remediate if pattern known |
| GHAS alert | Medium | Open issue, assign |

## Risk Score Formula

```
risk_score = (cvss_weight × cvss_score +
              entropy_weight × entropy_score +
              context_weight × context_score) / sum_weights

where:
  cvss_weight    = 0.50
  entropy_weight = 0.30  # E-09 entropy signal
  context_weight = 0.20  # credential name heuristic
```

## Cognitive Physics Alignment

| Physics | Application |
|---------|-------------|
| Balance ⚖️ | Unified risk scoring balances CVSS + entropy + context signals |
| Redundancy 🔀 | Multiple scanners ensure no single-point miss (defense in depth) |
| Path 🛤️ | Waterfall triage (secret → CVE → alert) minimizes total scan time |

## Related Agents

- **secret-detection-agent** (sub-agent, E-09)
- **bridge-security-monitor** (IPC security — retained independent)
- **unified-doc-agent** (M-02) — documentation parallel
