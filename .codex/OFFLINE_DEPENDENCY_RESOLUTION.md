# OFFLINE_DEPENDENCY_RESOLUTION

Date: 2026-07-07
Source: consolidated from lane2-packaging + lane2-depsec

## Objective

Resolve dependency/profile drift and produce deterministic offline installs for `core`, `runtime`, and `full`.

## Current Conflicts / Gaps

1. Profile drift between `pyproject.toml` extras and lock/export surfaces.
2. Lock exports generated with `--no-hashes` reduce reproducibility guarantees.
3. Runtime/full profiles include heavy transitive dependencies that conflict with lightweight expectations.
4. Vulnerable/ignored dependencies require explicit risk governance.

## Resolution Plan

### Step 1: Lock Alignment
- Regenerate lock artifacts from canonical `pyproject.toml` profile definitions.
- Add CI check that fails on extras-lock drift.

### Step 2: Offline Install Integrity
- Generate hash-verified release manifests.
- Build wheelhouse from lock-aligned manifests with checksums and SBOM.

### Step 3: Profile Clarity
- Preserve strict boundaries:
  - core: offline-safe minimal surface
  - runtime: inference stack
  - full: dev/test ecosystem
- Optionally split runtime into cpu/gpu tracks if footprint requires.

### Step 4: Security Governance
- Add owner+expiry on dependency suppressions.
- Gate external release when unresolved HIGH issues exist without approved exception.

## Validation

- Offline install command must succeed with `--no-index --find-links ./wheelhouse`.
- No resolver/network access in isolated install test jobs.
- Profile-specific smoke imports pass for core/runtime/full.
