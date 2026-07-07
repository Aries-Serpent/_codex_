# ISOLATED_DEPLOYMENT

## Goal

Run the system in a local isolated repository with whitelist-only networking and offline dependency provisioning.

## Deployment Model

1. Prepare artifact bundle (dist + wheelhouse + checksums/SBOM).
2. Install with `--no-index --find-links ./wheelhouse`.
3. Enforce deny-by-default network policy.
4. Allow only explicitly approved hosts where required.

## Recommended Allowlist Seed (Example)

```yaml
allowed_hosts:
  - github.com
  - api.github.com
  - huggingface.co
  - pypi.org
  - files.pythonhosted.org
mode: fail_closed
```

## Validation Checklist

- [ ] Core profile installs fully offline.
- [ ] Runtime/full profiles install offline when selected.
- [ ] No outbound network during offline validation jobs.
- [ ] Policy guard blocks non-allowlisted hosts.
- [ ] Checksums/SBOM verified against bundle.

## Go/No-Go Criteria

**GO** when lock/profile alignment, hash-verified manifests, and strict offline bootstrap are complete.

**NO-GO** if resolver/network access is required during offline path or unresolved HIGH vulnerability exceptions remain ungoverned.
