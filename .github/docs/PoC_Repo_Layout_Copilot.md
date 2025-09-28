# [Doc]: Ready-to-Run PoC Repo Layout — Codex ⇄ Bridge ⇄ Copilot CLI ⇄ GitHub (Self-Hosted Only)
> Updated: 2025-09-28

## Alignment note
- **Automation confined to `.codex/`**.
- **No active workflows** under `.github/workflows/` (example YAML lives under `docs/examples/`).
- **Programmatic Copilot CLI only** (`copilot -p` + `--allow-tool/--deny-tool`). :contentReference[oaicite:4]{index=4}
- **Auditable outputs**: bridge manifests under `.codex/copilot_bridge/var/manifests/` with SHA-256; CLI manifests remain in the trusted repo `cwd`.
- **Security posture**: deny-by-default beyond allowed set; trusted dir + per-tool approvals required by first-run UX. :contentReference[oaicite:5]{index=5}
- **Node runtime**: Default to **Node 22** (unified). Copilot CLI **requires Node 22+**. :contentReference[oaicite:6]{index=6}

## Node Strategy (Unified vs Scoped)
To satisfy Copilot CLI’s Node 22 requirement while minimizing host disruption, choose one:

- **Unified (default):** upgrade the host’s Node to **22.x**. The bridge `package.json` enforces `engines.node: ">=22.0.0"`. Service uses `/usr/bin/env node` and the host PATH should resolve to Node 22. :contentReference[oaicite:7]{index=7}
- **Scoped (fallback):** keep the host default Node for other tooling, but set **PATH in `/etc/copilot-bridge/env`** so *only* the bridge service runs with Node 22 (e.g., `/opt/node-v22/bin` first). The install script prints the detected strategy.

> Decision helper: `.codex/copilot_bridge/scripts/detect-node-strategy.sh` prints `strategy=unified|scoped` and the currently detected Node.

## Bridge API contract (unchanged)
- **POST** `/copilot/run` — body: `{ prompt, cwd?, timeoutMs?, allowAllTools?, allowTools?, denyTools? }`
- **GET** `/health` — liveness/info

**CLI flags** (programmatic mode): `-p/--prompt`, `--allow-tool`, `--deny-tool`, `--allow-all-tools`. :contentReference[oaicite:8]{index=8}
