# StructuralPolicyManager — RBAC Policy Manager (Phase 5 Planset)

> **PLANSET ONLY — DO NOT EXECUTE until separate approval obtained.**
>
> Source: comment-3977050660 (Cognitive Brain Integration, Phase 5)
> Session: S108 (2026-02-28)

## Overview

Detailed planset for implementing a full RBAC-style permission manager
(`StructuralPolicyManager`) for the `AgentBrainAPI`.  Includes permission
lattice, mermaid diagrams, and implementation sub-tasks.

## RBAC Permission Lattice

```
SYSTEM_OWNER (mbaetiong)
│   ┌──────────────────────────────────────────────────────────┐
│   │ Permissions: ALL — read/write brain, promote patterns,   │
│   │ elevate autonomous_actions, manage policy, delegate admin│
│   └──────────────────────────────────────────────────────────┘
│
├── ORG_OWNER (Aries-Serpent org owners)
│   ┌──────────────────────────────────────────────────────────┐
│   │ Permissions: read brain, write store_memory, report CI,  │
│   │ promote pattern candidates (SYSTEM_OWNER review req.)    │
│   └──────────────────────────────────────────────────────────┘
│
├── DELEGATE_ADMIN (via GitHub token + explicit grant)
│   ┌──────────────────────────────────────────────────────────┐
│   │ Permissions: read brain, write store_memory, report CI,  │
│   │ NO pattern promotion, NO policy changes                  │
│   └──────────────────────────────────────────────────────────┘
│
└── READ_ONLY_AGENT (future: CI bots, external contributors)
    ┌──────────────────────────────────────────────────────────┐
    │ Permissions: read store_memory facts + pattern IDs ONLY  │
    │ NO write, NO promotion, NO delegation                    │
    └──────────────────────────────────────────────────────────┘
```

## Mermaid: RBAC Architecture

```mermaid
flowchart TD
    subgraph PERMISSION_LATTICE["⊕ RBAC Permission Lattice"]
        SO["🔐 SYSTEM_OWNER\n(mbaetiong)\nFull authority"]
        OO["🏛️ ORG_OWNER\n(Aries-Serpent)\nRead+Write+Report"]
        DA["🔑 DELEGATE_ADMIN\n(token-granted)\nRead+Write+Report"]
        RO["👁️ READ_ONLY_AGENT\n(CI bots)\nRead only"]
    end

    SO -->|"delegates via\nGitHub token"| DA
    SO -->|"grants org\nrole"| OO
    OO -->|"read-only\ndowngrade"| RO
    DA -->|"read-only\ndowngrade"| RO

    subgraph POLICY_MANAGER["⚙️ StructuralPolicyManager"]
        PM_EVAL["evaluate_permission(\n  actor, action, resource\n)"]
        PM_AUDIT["audit_log(\n  actor, action, outcome\n)"]
        PM_CACHE["permission_cache\n(TTL: 5 min)"]
    end

    PERMISSION_LATTICE --> PM_EVAL
    PM_EVAL --> PM_AUDIT
    PM_EVAL --> PM_CACHE

    subgraph BRAIN_RESOURCES["🧠 Cognitive Brain Resources"]
        BR_READ["get_session_context()"]
        BR_WRITE["store_memory()"]
        BR_REPORT["report_completion()"]
        BR_PROMOTE["promote_pattern()"]
        BR_POLICY["modify_policy()"]
    end

    PM_EVAL -->|"ALLOW"| BR_READ
    PM_EVAL -->|"ALLOW (OO+)"| BR_WRITE
    PM_EVAL -->|"ALLOW (OO+)"| BR_REPORT
    PM_EVAL -->|"ALLOW (SO only)"| BR_PROMOTE
    PM_EVAL -->|"ALLOW (SO only)"| BR_POLICY
```

## Mermaid: Permission Evaluation Flow

```mermaid
sequenceDiagram
    participant Agent as 🤖 Copilot Agent
    participant MCP as ⚡ MCP Server
    participant SPM as ⚙️ StructuralPolicyManager
    participant Cache as 💾 Permission Cache
    participant Brain as 🧠 AgentBrainAPI

    Agent->>MCP: session_start(actor, pr_metadata)
    MCP->>SPM: evaluate_permission(actor, "read_context")
    SPM->>Cache: lookup(actor)
    alt Cache hit
        Cache-->>SPM: cached_role
    else Cache miss
        SPM->>SPM: resolve_role_from_github_token(actor)
        SPM-->>Cache: store(actor, role, TTL=5min)
    end
    SPM-->>MCP: ALLOW / DENY
    alt ALLOW
        MCP->>Brain: get_session_context()
        Brain-->>MCP: raw_context
        MCP->>MCP: apply_allowlist + recency_rank
        MCP-->>Agent: enriched_system_prompt
    else DENY
        MCP-->>Agent: default_system_prompt (unmodified)
    end
    MCP->>SPM: audit_log(actor, "read_context", outcome)
```

## Implementation Sub-Tasks (Planset-Defined)

1. Define `PermissionTier` enum + role resolution logic
2. Implement `evaluate_permission(actor, action, resource) → ALLOW/DENY`
3. Implement `permission_cache` with TTL eviction
4. Implement `audit_log → .codex/rbac_audit.jsonl`
5. Wire into `mcp_session_bridge.py` (replace `validate_actor()`)
6. Create RBAC config section in `agent-brain-config.yml`
7. Write 25+ tests covering all permission tiers and edge cases
8. Integration test: unauthorised agent attempts + audit trail verification

## Acceptance Criteria (Planset)

- [ ] Permission lattice strictly hierarchical
- [ ] Audit log captures all `evaluate_permission` calls
- [ ] Cache TTL eviction tested
- [ ] Zero escalation possible
- [ ] Policy file modifiable only by `SYSTEM_OWNER`

## Integration Points

- `mcp_session_bridge.py`: `validate_actor()` → `evaluate_permission()`
- `cognitive_brain_ci_feedback.yml`: actor check → permission gate
- `SessionContextInjector`: pass through only if ALLOW

## Execution Guard

**Zero execution until explicit approval separate from this plan.**
