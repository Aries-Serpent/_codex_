# Secrets Rotation Runbook — `CODEX_MASTER_KEY` / `CODEX_BACKUP_KEY`

> **Document**: `docs/ops/secrets_rotation_runbook.md`  
> **Version**: 1.0 (P10-06 — S96 2026-06-22)  
> **Owner**: @mbaetiong  
> **Status**: Production Readiness — Phase 10  
> **Classification**: Internal — do not commit key material to source control

---

## Overview

This runbook covers the full lifecycle of the two primary repository secrets:

| Secret | Purpose | Scope |
|--------|---------|-------|
| `CODEX_MASTER_KEY` | Primary encryption/signing key for codex operations | Repo secret (org-level optional) |
| `CODEX_BACKUP_KEY` | Fallback key used during rotation window | Repo secret |

Both keys are GitHub Actions secrets injected at CI runtime. They are **never**
committed to source control and **never** logged.

---

## Key Properties

```
Algorithm: AES-256-GCM (encryption) or HMAC-SHA256 (signing)
Length: 32 bytes (256 bits), base64-encoded = 44 chars
Rotation frequency: Every 90 days (or immediately on suspected compromise)
Grace window: 48 hours (BACKUP_KEY accepts old material during rotation)
```

---

## Pre-Rotation Checklist

Before rotating either key, verify:

- [ ] No CI jobs are currently running (`gh run list --repo Aries-Serpent/_codex_ --status in_progress`)
- [ ] Last successful backup of encrypted artifacts (`audit_artifacts/` snapshot)
- [ ] Replacement key is generated **offline** using a CSPRNG (see Generation step)
- [ ] New key is securely stored in password manager / KMS **before** GitHub update
- [ ] Pair rotation: BACKUP_KEY → old MASTER_KEY, MASTER_KEY → new key

---

## Step 1 — Generate New Key (Offline)

```bash
# Python — generate cryptographically secure 256-bit key
python3 -c "
import secrets, base64
key = base64.b64encode(secrets.token_bytes(32)).decode()
print(f'New key ({len(key)} chars): {key}')
"
# Example output: New key (44 chars): <base64-string>
# ⚠️ Store this value in your password manager BEFORE proceeding
```

**Never generate keys inside CI/CD.** Keys generated on ephemeral runners are
transient and may be exposed via logs if `set -x` is active.

---

## Step 2 — Stage BACKUP_KEY (Grace Window Opens)

1. Copy the **current `CODEX_MASTER_KEY`** value from GitHub Secrets.
2. Set `CODEX_BACKUP_KEY` = (current MASTER_KEY value).

```bash
# Using GitHub CLI (requires `admin:repo` scope)
gh secret set CODEX_BACKUP_KEY \
  --repo Aries-Serpent/_codex_ \
  --body "<CURRENT_MASTER_KEY_VALUE>"
```

This opens a 48-hour grace window during which both keys are accepted.

---

## Step 3 — Rotate CODEX_MASTER_KEY

```bash
gh secret set CODEX_MASTER_KEY \
  --repo Aries-Serpent/_codex_ \
  --body "<NEW_KEY_VALUE>"
```

---

## Step 4 — Validate

```bash
# Trigger a manual CI run to confirm the new key works
gh workflow run resilient_validation.yml \
  --repo Aries-Serpent/_codex_ \
  --ref main

# Monitor for success (wait ~10 min)
gh run watch --repo Aries-Serpent/_codex_
```

Verify:
- [ ] `resilient_validation.yml` completes green with new MASTER_KEY
- [ ] No `KeyError` or `DecryptionError` in logs
- [ ] Audit chain integrity check passes (if `CODEX_AUDIT_HMAC_KEY` is coupled)

---

## Step 5 — Close Grace Window (Clear BACKUP_KEY)

Once validation is confirmed:

```bash
# Set BACKUP_KEY to empty string (disables fallback)
gh secret set CODEX_BACKUP_KEY \
  --repo Aries-Serpent/_codex_ \
  --body ""
```

> **Note**: GitHub does not support deleting secrets via CLI in all plan tiers.
> Setting to empty string is equivalent — the consuming code must handle empty
> BACKUP_KEY as "no fallback".

---

## Emergency Rotation (Suspected Compromise)

If a key is suspected compromised:

1. **Immediately** rotate MASTER_KEY (skip BACKUP_KEY grace window — set both
   simultaneously with the new key).
2. Invalidate all artifacts signed/encrypted with the old key.
3. File an incident in GitHub Issues with label `[SECURITY-INCIDENT]`.
4. Notify @mbaetiong within 1 hour.
5. Review CI logs for potential key exposure (grep for key prefix in log archives).

```bash
# Immediate double-rotation (no grace window)
NEW_KEY=$(python3 -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())")
gh secret set CODEX_MASTER_KEY --repo Aries-Serpent/_codex_ --body "$NEW_KEY"
gh secret set CODEX_BACKUP_KEY --repo Aries-Serpent/_codex_ --body "$NEW_KEY"
```

---

## Code-Side Key Consumption Pattern

All code consuming `CODEX_MASTER_KEY` / `CODEX_BACKUP_KEY` must follow this pattern:

```python
import os

def _get_active_key() -> bytes:
    """Return master key, falling back to backup key during rotation window."""
    master = os.environ.get("CODEX_MASTER_KEY", "").strip()
    backup = os.environ.get("CODEX_BACKUP_KEY", "").strip()
    if master:
        return master.encode()
    if backup:
        import warnings
        warnings.warn(
            "CODEX_MASTER_KEY unset — using CODEX_BACKUP_KEY (rotation window)",
            RuntimeWarning,
            stacklevel=2,
        )
        return backup.encode()
    raise EnvironmentError(
        "Neither CODEX_MASTER_KEY nor CODEX_BACKUP_KEY is set. "
        "Cannot proceed with encrypted operations."
    )
```

---

## Rotation Schedule

| Rotation | Due Date | Status |
|----------|----------|--------|
| Initial provisioning | 2026-02-28 | ✅ Keys set |
| Rotation 1 | 2026-05-28 | ⏳ Scheduled |
| Rotation 2 | 2026-08-26 | ⏳ Scheduled |

---

## Related Documents

- `docs/ops/HMAC_rotation.md` — CODEX_AUDIT_HMAC_KEY rotation (separate key, separate lifecycle)
- `docs/ops/secrets_baseline_workflow.md` — detect-secrets baseline management
- `docs/ops/hardware_compatibility_matrix.md` — primary test machine constraints

---

*Created: S96 (P10-06) 2026-02-28 — @copilot*
