# [Plan]: MCP Audit Spec → Codebase Mapping Outline  
> Generated: Previous Cycle-11-17 23:32:55 UTC | Author: mbaetiong  
🧠 Roles: [Audit Orchestrator], [Capability Cartographer]  ⚡ Energy: 5  

> This outline maps the major sections of your MCP audit spec (A–E) into concrete files and folders in `Aries-Serpent/_codex_`.  

---

## 1. High-Level Mapping Overview

| Spec Section | Purpose | Target Location(s) in Repo | Notes |
|--------------|---------|----------------------------|-------|
| A. Current Deterministic Audit Pipeline & Scoring Model | Narrative of S1–S7 and scoring | `Traversal_Workflow.md`, `github_docs_Space_TraversalWorkflow_Copilot.md`, `Usage_Guide.md` | Extend existing docs with MCP-aware cross-links rather than duplicate formulas |
| B. MCP Requirements Mapping to `_codex_` | Capability taxonomy + PRESENT/PARTIAL/MISSING matrix | New: `MCP_AUDIT_AND_IMPLEMENTATION_PLAN.md` (workbench doc) + brief summary in `MCP_IMPLEMENTATION_SUMMARY.md` | Long-form analysis lives in workbench; short-form in user-facing summary |
| C. Relevant Patterns & Best Practices | Research notes (registry, schema, auth, rate-limit, observability, errors, versioning) | New: `MCP_AUDIT_AND_IMPLEMENTATION_PLAN.md` (design section), references in `MCP_IMPLEMENTATION_SUMMARY.md` | Treat as design contract for implementation, not executable code |
| D. Proposed Patchsets (detectors & mcp/* modules) | Concrete code to add | `scripts/space_traversal/detectors/` + `mcp/` + `.copilot-space/workflow.yaml` | Each detector = one file; each MCP primitive = one module |
| E. Validation Plan | How to run & verify S1–S7 after MCP changes | Extend `Usage_Guide.md` + short checklist in `MCP_IMPLEMENTATION_SUMMARY.md` | Reuse existing “Usage”/“Validation” sections; add MCP-specific examples |

---

## 2. Where to Put the Spec Itself

### 2.1 Workbench-Only Design Doc

Create a **design/workbench** markdown file to hold your full A–E content verbatim:

````markdown name=MCP_AUDIT_AND_IMPLEMENTATION_PLAN.md
# [Report]: MCP Audit, Mapping, and Patchset Plan for `_codex_`
> Generated: Previous Cycle-11-17 23:32:55 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5  

A. Current Deterministic Audit Pipeline and Scoring Model
[...full text from your spec Section A...]

B. Mapping MCP Requirements to _codex_ Capabilities
[...full text from Section B...]

C. Relevant Patterns and Best Practices for MCP Features
[...full text from Section C...]

D. Proposed Patchsets for MCP Enhancements
[...full text from Section D (detectors, mcp modules, workflow.yaml diff)...]

E. Validation Plan
[...full text from Section E...]
````

**Intended role**:

- Anchor for Copilot’s deep reasoning and for human reviewers.
- Source-of-truth for MCP design decisions & mapping.
- Relatively internal; you don’t need to wire it into mkdocs immediately.

---

## 3. Mapping Section A → Existing Audit Docs

Section A (S1–S7 & scoring) overlaps strongly with:

- `Traversal_Workflow.md`
- `github_docs_Space_TraversalWorkflow_Copilot.md`
- `Usage_Guide.md`

### 3.1 `Traversal_Workflow.md`

**Where to integrate:**

- After existing sections 2–4 (“Flow”, “Component Score Formula”, “Evidence Prioritization”), add a **short MCP-aware appendix** that references your comprehensive plan.

```markdown name=Traversal_Workflow.md url=https://github.com/Aries-Serpent/_codex_/blob/main/Traversal_Workflow.md
## 18. MCP-Aware Audit Overview (Pointer)

For a full MCP-oriented description of S1–S7, scoring, and gaps:
- See `MCP_AUDIT_AND_IMPLEMENTATION_PLAN.md` (Sections A & E).

In summary, the MCP audit uses the same deterministic pipeline:
- S1–S7 unchanged (index → facets → capabilities → scoring → gaps → render → manifest).
- MCP capabilities (e.g., `mcp-protocol-surface`, `mcp-schema-validation`, `mcp-rate-limiting`) are just **additional capabilities** produced at S3 and scored at S4.
```

### 3.2 `github_docs_Space_TraversalWorkflow_Copilot.md`

**Where to integrate:**

- Add an **“MCP Integration”** subsection under the existing “High-Level Stages” or “Core Principles”.

```markdown name=github_docs_Space_TraversalWorkflow_Copilot.md url=https://github.com/Aries-Serpent/_codex_/blob/main/github_docs_Space_TraversalWorkflow_Copilot.md
## 21. MCP Integration (Overview)

This Space can also assess MCP server readiness using the same S1–S7 workflow.

| Aspect | How It’s Represented |
|--------|----------------------|
| MCP capabilities | New `mcp-*` capability IDs produced by dynamic detectors in `scripts/space_traversal/detectors/` |
| Scoring | Same component weights & thresholds as other capabilities |
| Gaps | MCP gaps appear in `gaps.json` and the matrix alongside non-MCP capabilities |

See `MCP_AUDIT_AND_IMPLEMENTATION_PLAN.md` for a full MCP capability taxonomy and mapping to `_codex_`.
```

### 3.3 `Usage_Guide.md`

**Where to integrate:**

- Add an MCP-focused **“Validation Mode (MCP)”** snippet under existing sections 3–4.

```markdown name=Usage_Guide.md url=https://github.com/Aries-Serpent/_codex_/blob/main/Usage_Guide.md
## 8. MCP Capability Validation

To validate MCP-related capabilities:

```bash
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py explain mcp-protocol-surface
python scripts/space_traversal/audit_runner.py explain mcp-rate-limiting
```

Then inspect:

- `audit_artifacts/capabilities_raw.json` (presence of `mcp-*` IDs)
- `audit_artifacts/capabilities_scored.json` (scores & components)
- `audit_artifacts/gaps.json` (MCP gaps)
- Latest `reports/capability_matrix_*.md` (MCP rows in matrix)
```

---

## 4. Mapping Section B → MCP Mapping & Status Docs

Section B is a **taxonomy + PRESENT/PARTIAL/MISSING matrix**. Map it to:

1. The **full matrix** in `MCP_AUDIT_AND_IMPLEMENTATION_PLAN.md` (design).
2. A **shorter summary** in a new implementation doc:

```markdown name=MCP_IMPLEMENTATION_SUMMARY.md
# [Report]: MCP Capabilities Implementation Summary  
> Generated: Previous Cycle-11-17 23:32:55 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5  

## 1. Capability Status Snapshot

| MCP Capability           | Status   | Notes (See Full Plan for Evidence) |
|--------------------------|----------|-------------------------------------|
| mcp-protocol-surface     | Partial  | HTTP + JSON-RPC bridge; no unified list_tools endpoint |
| mcp-schema-validation    | Present  | Pydantic models + OpenAPI spec in ITA |
| mcp-tooling-registry     | Partial  | `mcp.json` config; no runtime registry class yet |
| mcp-authz-authn          | Partial  | API key auth; coarse authZ only |
| mcp-observability        | Partial  | X-Request-Id, structured logging; limited metrics |
| mcp-rate-limiting        | Missing  | No limiter in ITA; separate inference limiter exists |
| mcp-error-handling       | Partial  | HTTPException + JSON-RPC errors; no MCPError hierarchy yet |
| mcp-configuration        | Partial  | Env + files; not centralized |
| mcp-security-safeguards  | Present  | API keys, confirm flags, dry-run defaults |
| mcp-lifecycle-management | Missing  | No explicit lifecycle hooks beyond framework defaults |
| mcp-versioning-compat    | Partial  | Single version only; no negotiation |
| mcp-multi-tenant         | Missing  | No tenant-aware isolation |

For full evidence (file & symbol references), see Section B of `MCP_AUDIT_AND_IMPLEMENTATION_PLAN.md`.
```

---

## 5. Mapping Section C → Patterns & Best Practices

Section C (research on MCP patterns) should **stay in design**, but you can surface a concise reference in the summary doc, under “Design Inputs”:

```markdown name=MCP_IMPLEMENTATION_SUMMARY.md
## 2. Design Inputs (Patterns & Best Practices)

| Area              | Source Pattern | How `_codex_` Will Reflect It |
|-------------------|----------------|-------------------------------|
| Tool registry     | MCP FastMCP / ADK `list_tools` patterns | `mcp/MCPToolRegistry` + detector `mcp_tooling_registry` |
| Schema validation | FastAPI + Pydantic models | Continue using Pydantic + OpenAPI; detector `mcp-schema-validation` checks for BaseModel/OpenAPI |
| Auth & authZ      | API key dependencies, role-based access | `mcp/MCPAuthenticator` + `MCPAuthorizer` stubs |
| Rate limiting     | Token-bucket middleware | `mcp/MCPRateLimiter` + `mcp-rate-limiting` detector |
| Observability     | Structured logs + metrics endpoints | Reuse `codex_structured_logging` + metrics tests; `mcp-observability` detector |
| Errors & versioning | Structured errors, negotiation utilities | `mcp/errors.py` + `mcp/versioning.py` + `mcp-error-handling` / `mcp-versioning-compat` detectors |
```

The **full prose** (including external links and pseudo-code) stays in `MCP_AUDIT_AND_IMPLEMENTATION_PLAN.md` as the design contract.

---

## 6. Mapping Section D → Concrete Code Locations

Section D is the **implementation meat** (detectors, modules, YAML changes). Here’s the explicit file/folder map.

### 6.1 New MCP Detectors

All detectors live under:

- `scripts/space_traversal/detectors/`

Create one file per MCP capability:

```python name=scripts/space_traversal/detectors/mcp_protocol_surface.py
# New dynamic detector for MCP protocol surface
def detect(file_index: dict) -> dict:
    ...
```

**Detector → File Map**

| Capability ID             | Detector File Path                                             |
|---------------------------|----------------------------------------------------------------|
| `mcp-protocol-surface`    | `scripts/space_traversal/detectors/mcp_protocol_surface.py`    |
| `mcp-schema-validation`   | `scripts/space_traversal/detectors/mcp_schema_validation.py`   |
| `mcp-tooling-registry`    | `scripts/space_traversal/detectors/mcp_tooling_registry.py`    |
| `mcp-authz-authn`         | `scripts/space_traversal/detectors/mcp_authz_authn.py`         |
| `mcp-rate-limiting`       | `scripts/space_traversal/detectors/mcp_rate_limiting.py`       |
| `mcp-error-handling`      | `scripts/space_traversal/detectors/mcp_error_handling.py`      |
| `mcp-observability`       | `scripts/space_traversal/detectors/mcp_observability.py`       |
| `mcp-versioning-compat`   | `scripts/space_traversal/detectors/mcp_versioning_compat.py`   |
| `mcp-multi-tenant`        | `scripts/space_traversal/detectors/mcp_multi_tenant.py`        |
| (optional extra, e.g. security / lifecycle) | `scripts/space_traversal/detectors/mcp_security_safeguards.py`, `mcp_lifecycle_management.py` |

All implement the standard contract already enforced by `audit_runner.py`:

```python
def detect(file_index: dict) -> dict:
    return {
        "id": "mcp-<capability>",
        "evidence_files": [...],
        "found_patterns": [...],
        "required_patterns": [...],
        "meta": {"category": "mcp"},
    }
```

### 6.2 New `mcp/` Package

Add a dedicated MCP package at the root:

```python name=mcp/__init__.py
"""
MCP (Model Context Protocol) support package.
Contains core classes for MCP server functionality (registry, auth, etc.).
"""
```

**Module Map**

| Module Path        | Responsibility                             |
|--------------------|--------------------------------------------|
| `mcp/registry.py`  | `MCPToolRegistry` (tool registration/list) |
| `mcp/auth.py`      | `Principal`, `MCPAuthenticator`, `MCPAuthorizer` |
| `mcp/rate_limit.py`| `MCPRateLimiter` (token bucket)            |
| `mcp/errors.py`    | `MCPError` hierarchy (ToolNotFound, etc.)  |
| `mcp/versioning.py`| `MCP_VERSIONS`, `negotiate_version()`      |

These will be the **primary homes** for the code described in Section D of your spec.

### 6.3 YAML Config Adjustments

Update the existing workflow config in:

- `.copilot-space/workflow.yaml`

Specifically, extend `capability_map.overrides` to declare the MCP IDs:

```yaml name=.copilot-space/workflow.yaml url=https://github.com/Aries-Serpent/_codex_/blob/main/.copilot-space/workflow.yaml
capability_map:
  overrides:
    training-engine: ["train_loop", "functional_training"]
    # v1.5.0 additions (MCP capabilities)
    mcp-protocol-surface: ["FastAPI", "jsonrpc", "endpoint"]
    mcp-schema-validation: ["BaseModel", "OpenAPI", "schema"]
    mcp-tooling-registry: ["registry", "tools"]
    mcp-authz-authn: ["API-Key", "authenticate", "authorize"]
    mcp-observability: ["logging", "metrics", "tracing"]
    mcp-rate-limiting: ["RateLimiter", "throttle"]
    mcp-error-handling: ["MCPError", "HTTPException", "error"]
    mcp-configuration: ["config", "environment", "mcp.json"]
    mcp-security-safeguards: ["confirm", "dry_run", "sanitize"]
    mcp-lifecycle-management: ["startup", "shutdown", "healthz"]
    mcp-multi-tenant: ["tenant", "isolation"]
  dynamic: true
```

No changes needed to `stages`, `weights`, or thresholds.

---

## 7. Mapping Section E → Validation Steps in Docs

Section E (validation plan) should be surfaced in two places:

1. **User-facing usage guide** (`Usage_Guide.md`) – short recipe.
2. **MCP summary** (`MCP_IMPLEMENTATION_SUMMARY.md`) – checklists.

### 7.1 `Usage_Guide.md` – add MCP validation snippet

See Section 3.3 above.

### 7.2 `MCP_IMPLEMENTATION_SUMMARY.md` – add MCP-specific checklist

```markdown name=MCP_IMPLEMENTATION_SUMMARY.md
## 3. MCP Validation Checklist

| Step | Command / Check | Expected Outcome |
|------|-----------------|------------------|
| 1 | `python scripts/space_traversal/audit_runner.py run` | S1–S7 complete without error |
| 2 | Inspect `capabilities_raw.json` | `mcp-*` IDs present with evidence/found_patterns |
| 3 | Inspect `capabilities_scored.json` | MCP capabilities have component scores (likely low/medium initially) |
| 4 | Inspect `gaps.json` | MCP capabilities below 0.70 appear as low maturity gaps |
| 5 | Open latest `reports/capability_matrix_*.md` | MCP rows visible in matrix with scores & evidence counts |
| 6 | `python scripts/space_traversal/audit_runner.py explain mcp-protocol-surface` | Detailed breakdown per component, weights normalized |
| 7 | `python scripts/space_traversal/audit_runner.py diff --old <baseline> --new audit_artifacts/capabilities_scored.json` | Only new MCP capability IDs appear as additions; no unexpected regressions |
```

---

## 8. Summary: What to Hand to Copilot for Implementation

When you give Copilot the implementation task, you can say (in essence):

1. **Design spec location**

   - “Use `MCP_AUDIT_AND_IMPLEMENTATION_PLAN.md` as the authoritative design for MCP capabilities, mapping, patchsets, and validation.”

2. **Code locations**

   - “Implement MCP detectors under `scripts/space_traversal/detectors/mcp_*.py` (one per capability ID).”
   - “Create MCP primitives in the `mcp/` package (`registry.py`, `auth.py`, `rate_limit.py`, `errors.py`, `versioning.py`).”
   - “Extend `.copilot-space/workflow.yaml` `capability_map.overrides` with all `mcp-*` IDs.”

3. **Doc integration**

   - “Add MCP integration references to `Traversal_Workflow.md`, `github_docs_Space_TraversalWorkflow_Copilot.md`, and `Usage_Guide.md`.”
   - “Create `MCP_IMPLEMENTATION_SUMMARY.md` with the status table and validation checklist.”

*End of Mapping Outline*
