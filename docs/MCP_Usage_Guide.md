# [Guide]: MCP Usage & Validation

> Generated: 2025-11-18 05:32:13 | Author: mbaetiong  
> Roles: [Audit Orchestrator], [Capability Cartographer] · Energy: 5

## 1. Running the MCP-Aware Audit

```bash
python scripts/space_traversal/audit_runner.py run
```

This command produces the MCP evidence artifacts that power the capability matrix:

- `audit_artifacts/capabilities_raw.json`
- `audit_artifacts/capabilities_scored.json`
- `audit_artifacts/gaps.json`
- `reports/capability_matrix_<timestamp>.md`

## 2. MCP Capabilities in the Matrix

The following MCP capabilities appear as dedicated rows (IDs) in the capability matrix:

- `mcp-protocol-surface`
- `mcp-schema-validation`
- `mcp-tooling-registry`
- `mcp-authz-authn`
- `mcp-observability`
- `mcp-rate-limiting`
- `mcp-error-handling`
- `mcp-versioning-compat`
- `mcp-multi-tenant`
- `mcp-tools-integration`

Example snippet from the generated matrix:

```text
| mcp-observability | 0.70 | Medium | 2.00 | 0.87 | 0.29 | 1.00 | 0.37 | 706 |
```

### Component Interpretation (MCP Context)

- **Functionality** – Presence of MCP primitives (e.g., `MCPToolRegistry`, `MCPAuthenticator`, `MCPRateLimiter`).
- **Consistency** – Shared helpers vs. duplicated logic across modules.
- **Tests** – Coverage coming from `tests/mcp/*.py` suites.
- **Safeguards** – Evidence of keywords such as `sha256`, `checksum`, `rng`, `seed`, `offline`, `WANDB_MODE`, `RateLimitExceeded`, `Unauthorized` in MCP modules.
- **Documentation** – Count of documentation hits referencing the capability ID and `mcp`.

## 3. Per-Capability Explanation Commands

Use the `explain` verb to inspect any MCP capability score:

```bash
python scripts/space_traversal/audit_runner.py explain mcp-protocol-surface
python scripts/space_traversal/audit_runner.py explain mcp-tooling-registry
python scripts/space_traversal/audit_runner.py explain mcp-authz-authn
python scripts/space_traversal/audit_runner.py explain mcp-rate-limiting
python scripts/space_traversal/audit_runner.py explain mcp-schema-validation
python scripts/space_traversal/audit_runner.py explain mcp-error-handling
python scripts/space_traversal/audit_runner.py explain mcp-versioning-compat
python scripts/space_traversal/audit_runner.py explain mcp-multi-tenant
python scripts/space_traversal/audit_runner.py explain mcp-observability
python scripts/space_traversal/audit_runner.py explain mcp-tools-integration
```

Each invocation prints component contributions so you can see whether tests, safeguards, or docs are the limiting factor.

## 4. How to Interpret Scores (and Boost Them)

| Component  | When High                                      | When Low (Action)                                                                 |
|------------|-----------------------------------------------|-----------------------------------------------------------------------------------|
| Functionality | Hooks exist end-to-end (registry, auth, limiter, protocol). | Implement missing MCP primitives or wire FastAPI/MCP bridges.                    |
| Consistency | Shared helpers (`mcp.errors`, `mcp.registry`) are reused.      | Consolidate duplicate helpers into shared modules.                               |
| Tests        | `tests/mcp/` suites cover happy-path + error cases.            | Add regression tests for the missing scenarios (e.g., rate limiting, auth).      |
| Safeguards   | Offline, checksum, RNG, RateLimitExceeded keywords observed.   | Enrich modules with safeguard keywords/logs where features already exist.        |
| Documentation| Docs cite capability IDs and guidance.                         | Update docs (this guide, MCP references) with explicit mention of the capability.|

### Missing or Low Scores

- **Missing row entirely** – Ensure `.copilot-space/workflow.yaml` has `capability_map.dynamic: true` and inspect detector logs under `scripts/space_traversal/detectors/mcp_*.py`.
- **Score < 0.70** – Target the lowest component in `capabilities_scored.json`. Most fixes involve either new tests or documentation references.

## 5. What to Do When MCP Capabilities Are Missing or Low

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| `mcp-protocol-surface` missing | Detector not seeing JSON-RPC or FastAPI bridges. | Review ITA endpoints (`services/ita/app/main.py`) and MCP server wiring. |
| `mcp-tooling-registry` score low | Registry exists but lacks tests/docs. | Add registry tests in `tests/mcp/test_utilities.py` and mention registry usage in docs. |
| `mcp-authz-authn` safeguards = 0 | Auth modules lack safeguard keywords. | Ensure files such as `mcp/auth.py` and `mcp/safeguards.py` mention `Unauthorized`, `checksum`, `offline`. |
| `mcp-rate-limiting` tests low | No tests exercising limiters. | Add coverage for `MCPRateLimiter` in `tests/mcp/test_rate_limiting.py` or integration suites. |
| `mcp-multi-tenant` < 0.50 | Feature intentionally partial. | Document the limitation and backlog items in `MCP_IMPLEMENTATION_SUMMARY.md`. |

## 6. Related MCP Documentation

For deeper design and evidence references:

- `MCP_IMPLEMENTATION_SUMMARY.md` – High-level status and evidence for each capability.
- `MCP_CAPABILITIES_REFERENCE.md` – Detailed descriptions, code snippets, and usage patterns.
- `MCP_SECURITY_GUIDE.md` – AuthN/AuthZ, rate limiting, and safeguard patterns.
- `MCP_DEVELOPER_GUIDE.md` – Steps to add new MCP tools, extend protocol surface, and integrate with ITA.

## 7. Troubleshooting MCP Issues

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| JSON-RPC responses missing `X-Request-Id`. | Middleware not attaching headers. | Verify `_get_request_id` helper in `services/ita/app/main.py`. |
| Offline audit hangs on prompts. | Multi-tenant confirm path calling `input()` in offline mode. | Use `confirm_tenant_operation(..., offline=True)` to skip prompts. |
| Rate limit capability low. | `MCPRateLimiter` unused or untested. | Wire limiter in FastAPI middleware and add regression tests. |
| Documentation deficit. | Capability not mentioned in docs. | Update this guide or related references with explicit capability coverage. |

## 8. Per-Capability Deep Dives

Use the evidence explorer scripts when you need root-cause detail:

```bash
python scripts/space_traversal/audit_runner.py explain mcp-error-handling --show-evidence
python scripts/space_traversal/audit_runner.py explain mcp-observability --show-tests
```

These flags surface which files or detectors influence the score so remediation can be targeted.

## 9. Related References

- `MCP_IMPLEMENTATION_SUMMARY.md`
- `MCP_CAPABILITIES_REFERENCE.md`
- `MCP_SECURITY_GUIDE.md`
- `MCP_DEVELOPER_GUIDE.md`

*End of MCP Guide*
