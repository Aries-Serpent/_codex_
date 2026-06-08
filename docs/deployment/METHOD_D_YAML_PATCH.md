# Method D — YAML Patch Reference

## Overview

Method D is the proven stable YAML pattern for the session preload step in
`.github/workflows/copilot-setup-steps.yml`. It is a drop-in copy of the
Session Access Probe pattern, which has never regressed.

## What is Method D?

| Feature | Detail |
|---------|--------|
| Block scalar wrapper | `run: |` — YAML parses correctly; no inline brace issues |
| Flow scalar fallback | `\|\| { }` inside the block — non-blocking error handling |
| Log grouping | `::group::` / `::endgroup::` — structured logs, prevents agent simplification |
| Env var on failure | `SESSION_PRELOAD_STATUS=failed` — downstream steps can react |
| Step ID | `id: session_preload` — allows downstream `steps.session_preload.outcome` references |
| Non-blocking | `continue-on-error: true` — agent starts even if preload fails |

## Exact YAML to Apply

Apply this to `.github/workflows/copilot-setup-steps.yml`, replacing the
current `"🧠 Session Context Pre-load"` step (search for `Session Context Pre-load`
to locate it — the exact line numbers may shift as the file evolves):

```yaml
      # ⚠️ DO NOT REFACTOR THIS STEP — See docs/agent/COPILOT_SETUP_STEPS_GUARD.md
      # Canonical form: block scalar run: | with flow scalar fallback (Method D)
      # This pattern is proven stable in Session Access Probe step; never regressed.
      # RULE: if you are fixing a CI failure, fix the failing file — NOT this step.
      - name: "🧠 Session Context Pre-load (memory + policy + accountability + PDA)"
        id: session_preload
        continue-on-error: true   # non-blocking: agent must start even if preload fails
        run: |
          echo "::group::Session Context Pre-load"
          python3 .github/scripts/session_preload.py || {
            echo "⚠️ session_preload.py failed (non-blocking) — agent will operate without preloaded context"
            echo "SESSION_PRELOAD_STATUS=failed" >> "$GITHUB_ENV"
          }
          echo "::endgroup::"
```

## Why Method D Works

The `|| { }` (flow scalar) shell construct is **valid bash** but causes
YAML parsing failures when written directly as a `run:` flow scalar value:

```yaml
# ❌ BROKEN — YAML parser sees the { as part of YAML flow mapping
run: python3 script.py || {
  echo "failed"
}
```

Method D wraps the construct in a block scalar (`run: |`), making the entire
shell snippet an opaque string to the YAML parser:

```yaml
# ✅ CORRECT — YAML parser sees only the | sigil; bash handles the rest
run: |
  python3 script.py || {
    echo "failed"
  }
```

## Regression History

| Method | Form | Status |
|--------|------|--------|
| Flow scalar direct | `run: python3 script.py \|\| { ... }` | ❌ YAML parse failure |
| Method B — if/fi | `run: \|` + `if ! python3; then ... fi` | ⚠️ Agents revert 8+ times |
| **Method D** | `run: \|` + `\|\| { }` inside block | ✅ **Never regressed** |

Method D is proven because it is already active in the Session Access Probe
step (lines ~166–184) in the same workflow file.

## Validation Commands

After applying the patch, run:

```bash
# 1. YAML syntax
yamllint .github/workflows/copilot-setup-steps.yml

# 2. Architecture test
pytest tests/architecture/test_layer_boundaries.py::test_copilot_setup_steps_session_preload_block_intact -v

# 3. Full canonical baseline check
bash scripts/ci/validate_setup_steps_yaml.sh .github/workflows/copilot-setup-steps.yml
```

All three must pass before pushing.

## References

- Validation checklist: `docs/deployment/METHOD_D_VALIDATION_CHECKLIST.md`
- Live session monitoring: `docs/deployment/METHOD_D_SESSION_MONITORING_GUIDE.md`
- Guard doc: `docs/agent/COPILOT_SETUP_STEPS_GUARD.md`
