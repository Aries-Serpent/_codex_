# ISOLATED_DEPLOYMENT
**Last Updated:** 2026-07-11
**Version:** v0.2.1

## Goal

Run the system in a local isolated repository with allowlist-only networking and offline dependency provisioning.

## Deployment Model

1. Prepare artifact bundle (dist + wheelhouse + checksums/SBOM).
2. Install with `--no-index --find-links ./wheelhouse`.
3. Enforce deny-by-default network policy.
4. Allow only explicitly approved hosts where required.

> Pre-release note: treat this as v0.2.1 pre-release deployment guidance pending P0 campaign closure (lock/profile alignment, hash-verified manifests, strict no-network bootstrap path).

## Recommended Allowlist Seed (Example)

```yaml
allowed_hosts:
  # Keep empty for strict offline-isolated deployment.
mode: fail_closed
```

For controlled external bootstrap (not strict offline mode), add temporary hosts with explicit approval and expiry.

## Validation Checklist

- [ ] Core profile installs fully offline.
- [ ] Runtime/full profiles install offline when selected.
- [ ] No outbound network during offline validation jobs.
- [ ] Policy guard blocks non-allowlisted hosts.
- [ ] Checksums/SBOM verified against bundle.

## Go/No-Go Criteria

**GO** when lock/profile alignment, hash-verified manifests, and strict offline bootstrap are complete.

**NO-GO** if resolver/network access is required during offline path or unresolved HIGH vulnerability exceptions remain ungoverned.
