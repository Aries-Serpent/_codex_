# Ops: Secrets Baseline Workflow (v1.2)
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> Generated: 2026-06-22 (audited) | Author: mbaetiong  
 Roles: [Primary: Security Maintainer], [Secondary: Reviewer]  Energy: 5

Steps

| Step | Command | Output | Notes |
|---|---|---|---|
| Generate | scripts/security/generate_secrets_baseline.sh | .secrets.baseline | Initial baseline |
| Audit | detect-secrets audit .secrets.baseline --report --json > secrets_audit.json | secrets_audit.json | Review findings |
| Commit | git add .secrets.baseline; git commit -m "chore(security): baseline" | commit | Required by policy |
| CI Gate | security_gates.yml | artifacts | Ensures baseline present/audited |
