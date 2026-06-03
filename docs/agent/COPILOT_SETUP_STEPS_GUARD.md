# COPILOT_SETUP_STEPS_GUARD — Do Not Refactor

**Status:** HARD RULE — enforced by CI (`scripts/ci/validate_setup_steps_yaml.sh`)
**Relevant file:** `.github/workflows/copilot-setup-steps.yml`
**Canonical baseline:** commit `12f7a861` / blob `8c84a8c1` (~1,075 lines)

---

## Why This File Has a Guard

`.github/workflows/copilot-setup-steps.yml` has regressed 4+ times across
consecutive Copilot agent sessions. Each regression broke the entire
`copilot-setup-steps` job — the mandatory pre-session environment setup
for every Copilot coding agent session.

---

## Canonical Baseline

Commit [`12f7a861`](https://github.com/Aries-Serpent/_codex_/blob/12f7a861a067ed5d9f1e1939119325f896624588/.github/workflows/copilot-setup-steps.yml)
(blob `8c84a8c1`, ~1,075 lines) **plus** the session preload block scalar fix
is the authoritative version. It is the only version that simultaneously has:

| Feature | Required Value |
|---------|---------------|
| `cancel-in-progress` | `true` |
| `runs-on` | `${{ vars.COPILOT_RUNNER_PROFILE \|\| 'ubuntu-latest' }}` |
| `NODE_VERSION` | `"22"` |
| Workflow-level `permissions` | `contents: read` |
| Action SHAs | All pinned (not floating `@v5`/`@v6` tags) |
| Session Preload step `run:` form | Block scalar (`run: \|`) |
| Session Access Probe | Present |
| RAG Context Build | Present |
| Cascade-control injection | Present |
| `rescue-comment` job | Present |

---

## Known Defect Blobs — NEVER restore to these

| Blob | Defects |
|------|---------|
| `45bf1b4c` | Missing `cancel-in-progress`, hardcoded runner, no `rescue-comment` job |
| `415da93573` | Missing Session Preload, Access Probe, RAG Context Build, cascade steps; floating SHAs |
| `5d47ccd3` | Orphaned `run:` key — YAML parse failure |

---

## Canonical Session Preload Step — DO NOT CHANGE

```yaml
      # ⚠️ DO NOT REFACTOR THIS STEP — See docs/agent/COPILOT_SETUP_STEPS_GUARD.md
      # Canonical form: block scalar run: | with if ! ...; then syntax.
      # This step has been broken 4+ times by agents converting it to flow scalar
      # (|| { } syntax) or orphaning the run: key. yamllint 1.38.0 crashes on
      # flow scalar brace syntax. Canonical baseline: commit 12f7a861 / blob 8c84a8c1.
      # RULE: if you are fixing a CI failure, fix the failing file — NOT this step.
      - name: "🧠 Session Context Pre-load (memory + policy + accountability + PDA)"
        continue-on-error: true   # non-blocking: agent must start even if preload fails
        run: |
          if ! python3 .github/scripts/session_preload.py; then
            echo "⚠️ session_preload.py failed (non-blocking) — agent will operate without preloaded context"
          fi
```

---

## Restore Procedure

If you must restore this file from the canonical commit:

```bash
git show 12f7a861a067ed5d9f1e1939119325f896624588:.github/workflows/copilot-setup-steps.yml \
  > .github/workflows/copilot-setup-steps.yml
python3 scripts/ci/patch_session_preload.py
```

---

## Agent Instruction

> ⚠️ **If you are a Copilot coding agent reading this:**
> Do NOT refactor, simplify, or touch the session preload step in `copilot-setup-steps.yml`.
> If a CI failure led you here, identify and fix the **other** file that is failing.
> If `copilot-setup-steps.yml` itself is failing, run the restore procedure above.
> Do not rewrite the step inline.
