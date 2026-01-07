# Security & Safeguards: Dependency Vulnerability Gate
> Generated: 2025-11-11 07:38:40 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Security Gate Owner], [Secondary: Implementer] ⚡ Energy: 5/5  
⚛️ Physics: Path🛤️ [Scan → Parse → Decide → Artifact] Fields🔄 [pip-audit, JSON] Patterns👁️ [Fail High/Critical, Allowlist Expiry] Redundancy🔀 [Artifact + Index] Balance⚖️ [Strict vs. Developer Velocity]

## Policy
- Fail build (nox session) on any HIGH or CRITICAL vulnerability not explicitly allowlisted with future expiry.
- WARN (non-failing) for LOW/MEDIUM vulnerabilities; remediation tracked separately.
- Allowlist entries must include: id, package, version, rationale, expiry_date (ISO).

## Workflow
1. Developer runs `nox -s security`.
2. `pip-audit -f json` executed; JSON parsed.
3. Allowlist filtered (non-expired only).
4. High/Critical remaining → session.error (fail).
5. JSON artifact: `artifacts/security_report.json`.
6. Update allowlist with rationale + timeboxed expiry for accepted false positives.

## Allowlist Example
```json
{
  "allowlisted_vulnerabilities": [
    {
      "id": "PYSEC-2025-99999",
      "package": "examplepkg",
      "version": "1.2.3",
      "severity": "HIGH",
      "rationale": "False positive due to vendored code not executed",
      "expiry_date": "Previous Cycle-12-31"
    }
  ]
}
```text

## Failure Message
`High/Critical vulnerabilities found (not allowlisted): <package:id:severity>`

## Remediation Checklist
| Step | Action | Owner |
|------|--------|-------|
| 1 | Pin or upgrade package | Developer |
| 2 | Re-run security session | Developer |
| 3 | If still present & false positive → allowlist with expiry | Security Gate Owner |

## References
- pip-audit docs
- Nox session spec

— End —