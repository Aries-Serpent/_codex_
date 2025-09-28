# [Doc]: Ready-to-Run PoC Repo Layout — Codex ⇄ Bridge ⇄ Copilot CLI ⇄ GitHub (Self-Hosted Only)
> Generated: 2025-09-28 | Author: mbaetiong  
Roles: [Primary: Copilot Integrator], [Secondary: DevSecOps] — Energy: [5]

## Alignment note
- **Automation confined to `.codex/`**.  
- **No active workflows** under `.github/workflows/` (example YAML lives under `docs/examples/`).  
- **Programmatic Copilot CLI only** (`copilot -p` + `--allow-tool/--deny-tool`).  
- **Auditable outputs**: bridge manifests under `.codex/copilot_bridge/var/manifests/` with SHA-256; CLI manifests remain in the trusted repo `cwd`.  
- **Security posture**: deny-by-default beyond allowed set; trusted dir + per-tool approvals required by first-run UX.

## Repository context

| Item | Value |
| ---: | --- |
| Repository | Aries-Serpent/_codex_ |
| Branch | `codex/implement-offline-first-ml-dev-loop_2025-09-27` |
| Commit (target) | `26e0ee5b2e55a6ff2a5631b0e1e30ec39ea29563` |

## PoC directory layout

```text
.codex/
  copilot_bridge/
    bridge/server.js           # Canonical Node/Express bridge
    config/bridge.config.json  # Defaults: cwd, timeouts, allow/deny
    manifests/bridge_manifest.schema.json
    ops/systemd/copilot-bridge.service
    scripts/{install-systemd.sh,test-bridge.sh}
    var/{logs,manifests}/     # Runtime artifacts
    package.json
    .env.example
    .gitignore
docs/
  examples/self_hosted_example.yml        # Example only; NOT active
  examples/python-variant/README.md       # Deprecated Python variant (note)
  validation/Bridge_Run_Validation.md
```

## Bridge API contract

| Method | Path | Body (JSON) | Description |
| ---: | --- | --- | --- |
| POST | `/copilot/run` | `{ prompt, cwd?, timeoutMs?, allowAllTools?, allowTools?, denyTools? }` | Runs Copilot CLI in programmatic mode (`-p`) with explicit tool gating |
| GET | `/health` | — | Liveness/info |

### Request fields

| Field | Type | Required | Default | Notes |
| ---: | --- | :---: | --- | --- |
| prompt | string | ✓ | — | Passed to `copilot -p` |
| cwd | string |  | `config.defaultCwd` | Must be a trusted repo dir |
| timeoutMs | number |  | `config.defaultTimeoutMs` | Hard kill after grace |
| allowAllTools | boolean |  | `config.allowAllTools` | Sets `--allow-all-tools` |
| allowTools | string[] |  | `config.allowTools` | Repeated `--allow-tool` |
| denyTools | string[] |  | `config.denyTools` | Repeated `--deny-tool` |

### Response fields

| Field | Type | Description |
| ---: | --- | --- |
| ok | boolean | `true` when exit code is 0 |
| rc | number | Copilot CLI exit code |
| stdout, stderr | string | Raw streams |
| bytes_stdout, bytes_stderr | number | Sizes (bytes) |
| started_at, ended_at | string | ISO-8601 timestamps |
| duration_ms | number | Duration |
| manifest_path, manifest_sha256 | string | **CLI** manifest path/hash (`.copilot.manifest.*.json` in `cwd`) |
| bridge_manifest_path, bridge_manifest_sha256 | string | **Bridge** manifest path/hash (`.codex/copilot_bridge/var/manifests/…`) |

## Runner label mapping (swap without code changes)

| Environment | Labels example |
| ---: | --- |
| Default (this PoC) | `[self-hosted, linux, copilot-bridge]` |
| Alt: GPU node | `[self-hosted, linux, gpu, copilot-bridge]` |
| Alt: ARM | `[self-hosted, linux, arm64, copilot-bridge]` |

> Change labels only in **example** workflows or external orchestration; the bridge itself is label-agnostic.

## Default Allow/Deny Policy

| Policy | Value |
| ---: | --- |
| allowAllTools | `false` |
| allowTools | `["shell","git","gh","write"]` |
| denyTools | `["shell(rm)","shell(sudo)","shell(dd)","shell(curl -X POST)","shell(wget)","shell(docker push)"]` |

## Governance notes
- **Do not use `gh-copilot`** (deprecated). Standardize on **`@github/copilot`** CLI.  
- First-run requires **/login**, trusting the directory, and **per-tool approvals**.  
- Self-hosted runners only; keep any CI examples **outside** `.github/workflows/`.
