# [Doc]: Ready-to-Run PoC Repo Layout — Codex ⇄ Bridge ⇄ Copilot CLI ⇄ GitHub (Self-Hosted Only)
> Generated: 2025-09-28 | Author: mbaetiong  
Roles: [Primary: Copilot Integrator], [Secondary: DevSecOps]

## Alignment note
- **Automation confined to `.codex/`**.
- **No active workflows** under `.github/workflows/` (example YAML lives under `docs/examples/`).
- **Programmatic Copilot CLI only** (via CLI `-p` mode; see CLI help for flags).
- **Auditable outputs**: bridge manifests under `.codex/copilot_bridge/var/manifests/` with SHA-256; CLI manifests remain in the trusted repo `cwd`.
- **Security posture**: deny-by-default beyond allowed set; trusted dir + per-tool approvals required by first-run UX.

## PoC directory layout
```text
.codex/
  copilot_bridge/
    bridge/server.js
    config/bridge.config.json
    manifests/bridge_manifest.schema.json
    ops/systemd/copilot-bridge.service
    scripts/{install-systemd.sh,test-bridge.sh}
    var/{logs,manifests}/
  package.json
  .env.example
  .gitignore
docs/
  examples/self_hosted_example.yml      # Example only; NOT active
  examples/python-variant/README.md     # Deprecated Python variant (note)
  validation/Bridge_Run_Validation.md
```

## Default Allow/Deny Policy
| Policy | Value |
| ---: | --- |
| allowAllTools | `false` |
| allowTools | `["shell","git","gh","write"]` |
| denyTools | `["shell(rm)","shell(sudo)","shell(dd)","shell(curl -X POST)","shell(wget)","shell(docker push)"]` |

## Governance notes
- Standardize on **`@github/copilot`** CLI; consult `copilot --help` for flags. General background: GitHub Docs for Copilot in the CLI.  
- First-run requires **/login**, trusting the directory, and **per-tool approvals**. :contentReference[oaicite:6]{index=6}

