# Packaging Architecture Decision Record (ADR)

**Campaign:** Cognitive Brain-Powered Packaging Analysis & External Distribution  
**Date:** 2026-07-06T01:20:00Z  
**Status:** Accepted (Phase 1 foundation implemented)

## ADR-001 — Three-Profile Packaging Contract

**Decision:** Standardize packaging outcomes into three install profiles:
- **core**: offline-first, safety/network policy + cognitive core API
- **runtime**: core + runtime integrations
- **full**: runtime + development/extended ecosystem

**Rationale:** Enables isolated local usage by default while preserving optional capability expansion.

## ADR-002 — Fail-Closed Network Policy Enforcement

**Decision:** Introduce explicit network policy enforcement via:
- `.codex/network-policy.yaml`
- `safety.network_policy.enforce_network_policy()`
- `PolicyViolationError` on non-allowlisted hosts

**Rationale:** Whitelist-only networking is a hard requirement for external isolated deployments.

## ADR-003 — Offline Bootstrap as First-Class Artifact

**Decision:** Ship `OFFLINE_BOOTSTRAP.sh` as canonical bootstrap entry for air-gapped environments.

**Rationale:** Ensures deterministic local installs from wheelhouse without public network access.

## ADR-004 — External Consumption Documentation Set

**Decision:** Publish root-level docs for external adopters:
- `.codex/archive/misc/INSTALL.md`
- `docs/release/ISOLATED_DEPLOYMENT.md`
- `docs/api/reference/INTEGRATION.md`

**Rationale:** Reduce onboarding friction and make offline/isolated setup explicit and reproducible.

## ADR-005 — Core Safety Module Export Contract

**Decision:** Export `enforce_network_policy` and `PolicyViolationError` from `safety.__init__`.

**Rationale:** Keep policy controls discoverable and stable for external integrators.
