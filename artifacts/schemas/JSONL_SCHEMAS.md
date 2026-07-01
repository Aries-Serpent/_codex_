# JSONL Schema Definitions — Phase 9.2 Lane 3

Machine-readable documentation schemas for semantic routing and decision logic evaluation.

## 1. Document Record Schema

Root container for documentation files.

```json
{
  "id": "doc_readme_001",
  "type": "document",
  "title": "README",
  "path": "README.md",
  "content_hash": "sha256_hash_value",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-07-02T00:00:00Z",
  "metadata": {
    "tags": ["onboarding", "getting-started"],
    "priority": "critical",
    "audience": ["contributors", "users"],
    "estimated_read_time_minutes": 15,
    "section_count": 12
  }
}
```

**Fields:**
- `id` (string, required): Unique document identifier
- `type` (string, required): "document"
- `title` (string, required): Document title
- `path` (string, required): Relative path from repo root
- `content_hash` (string, required): SHA-256 hash for change detection
- `created_at` (ISO8601): Creation timestamp
- `updated_at` (ISO8601): Last update timestamp
- `metadata` (object): Document-level metadata

**Index:** Full-text search on title + metadata tags

---

## 2. Section Record Schema

Hierarchical documentation structure (H1-H6 headers).

```json
{
  "id": "sec_readme_intro_001",
  "type": "section",
  "document_id": "doc_readme_001",
  "level": 1,
  "title": "Getting Started",
  "content": "## Getting Started\n\nThis section covers...",
  "position": 0,
  "parent_id": null,
  "children": ["sec_readme_intro_subsec_001"],
  "metadata": {
    "heading_anchor": "getting-started",
    "word_count": 342,
    "code_blocks": 3,
    "external_links": 2
  }
}
```

**Fields:**
- `id` (string, required): Unique section identifier
- `type` (string, required): "section"
- `document_id` (string, required): Parent document ID
- `level` (int, required): Heading level 1-6
- `title` (string, required): Section title
- `content` (string, required): Full section text including markdown
- `position` (int, required): Order within document
- `parent_id` (string, nullable): Parent section ID (null if root)
- `children` (array): Child section IDs
- `metadata` (object): Section-level metadata

**Index:** document_id + level for rapid hierarchical traversal

---

## 3. Block Record Schema

Content blocks within sections (text, code, lists, tables, images).

```json
{
  "id": "blk_readme_intro_code_001",
  "type": "block",
  "section_id": "sec_readme_intro_001",
  "block_type": "code",
  "content": "pip install codex-ml",
  "metadata": {
    "language": "shell",
    "executable": true,
    "tested": true,
    "line_count": 1,
    "position_in_section": 0
  }
}
```

**Fields:**
- `id` (string, required): Unique block identifier
- `type` (string, required): "block"
- `section_id` (string, required): Parent section ID
- `block_type` (enum): "text", "code", "list", "table", "image"
- `content` (string, required): Block content
- `metadata` (object): Block-specific metadata (language, executable, etc.)

**Index:** section_id + block_type for efficient filtering

---

## 4. Action Record Schema

Machine-readable actions for orchestrator execution.

```json
{
  "id": "act_trigger_tests",
  "type": "action",
  "name": "run_test_suite",
  "target": "pytest",
  "parameters": {
    "path": "tests/",
    "verbosity": "verbose",
    "timeout": 300
  },
  "precedence": 1,
  "conditions": [
    {
      "type": "gate",
      "condition": "all_tests_passing"
    }
  ],
  "metadata": {
    "description": "Execute full test suite",
    "owner": "ci-testing-agent",
    "created_at": "2026-07-02T00:00:00Z"
  }
}
```

**Fields:**
- `id` (string, required): Unique action identifier
- `type` (string, required): "action"
- `name` (string, required): Action name
- `target` (string, required): Execution target (pytest, script, etc.)
- `parameters` (object): Target-specific parameters
- `precedence` (int): Execution order
- `conditions` (array): Guard conditions for execution
- `metadata` (object): Action metadata

**Index:** type + target for orchestrator discovery

---

## 5. Decision Record Schema

Decision logic for semantic routing and branching.

```json
{
  "id": "dec_route_pr_review",
  "type": "decision",
  "name": "Route PR to Code Review",
  "criteria": {
    "pr_files_changed": ">= 5",
    "pr_complexity": "high",
    "requires_security_review": true
  },
  "branches": [
    {
      "condition": "requires_security_review && pr_complexity == 'high'",
      "action_id": "act_security_review",
      "weight": 0.8
    },
    {
      "condition": "pr_files_changed >= 10 && pr_complexity == 'high'",
      "action_id": "act_full_audit",
      "weight": 0.9
    },
    {
      "condition": "true",
      "action_id": "act_standard_review",
      "weight": 0.5
    }
  ],
  "default_action_id": "act_standard_review",
  "evaluation_logic": "weighted_deterministic",
  "metadata": {
    "priority": "P1",
    "last_updated": "2026-07-02T00:00:00Z"
  }
}
```

**Fields:**
- `id` (string, required): Unique decision identifier
- `type` (string, required): "decision"
- `name` (string, required): Decision name
- `criteria` (object): Decision criteria (rule definitions)
- `branches` (array): Condition → action mappings with weights
- `default_action_id` (string): Fallback action ID
- `evaluation_logic` (enum): "weighted_deterministic", "probabilistic", "first_match"
- `metadata` (object): Decision metadata

**Index:** criteria tags for decision discovery

---

## 6. Requirement Record Schema

Trackable requirements (REQ-1 through REQ-10+).

```json
{
  "id": "req_003",
  "type": "requirement",
  "category": "FUNCTIONAL",
  "description": "All public APIs must be documented with examples",
  "acceptance_criteria": [
    "100% API surface documented",
    "All examples executable",
    "Type hints present on all public functions"
  ],
  "priority": "P1",
  "status": "in_progress",
  "metadata": {
    "owner": "skills-master-agent",
    "created_at": "2026-06-01T00:00:00Z",
    "target_completion": "2026-07-15T00:00:00Z",
    "blocked_by": ["req_001"]
  }
}
```

**Fields:**
- `id` (string, required): Requirement ID (REQ-N format)
- `type` (string, required): "requirement"
- `category` (enum): "FUNCTIONAL", "PERFORMANCE", "SECURITY", "COMPLIANCE"
- `description` (string, required): Requirement description
- `acceptance_criteria` (array): Verifiable criteria
- `priority` (enum): P0, P1, P2, P3
- `status` (enum): "open", "in_progress", "blocked", "completed"
- `metadata` (object): Requirement metadata

**Index:** category + status for compliance auditing

---

## 7. Reference Record Schema

Cross-repository references (commits, PRs, issues, files, sections).

```json
{
  "id": "ref_commit_abc123",
  "type": "reference",
  "reference_type": "commit",
  "value": "abc123def456", <!-- pragma: allowlist secret -->
  "source_id": "doc_readme_001",
  "metadata": {
    "message": "feat: implement machine-readable docs",
    "author": "agent-orchestrator",
    "timestamp": "2026-07-02T00:00:00Z",
    "verified_at": "2026-07-02T01:00:00Z",
    "resolution_status": "resolved",
    "context_summary": "Implementation of JSONL schema infrastructure"
  }
}
```

**Fields:**
- `id` (string, required): Unique reference identifier
- `type` (string, required): "reference"
- `reference_type` (enum): "commit", "pr", "issue", "file", "section"
- `value` (string, required): Reference value (SHA, PR#, issue#, path, section ID)
- `source_id` (string): Document/record that contains reference
- `metadata` (object): Reference metadata

**Index:** type + value for linkage validation

---

## 8. Relationship Record Schema

Record-to-record connections (dependencies, cross-references, hierarchies).

```json
{
  "id": "rel_doc_security_to_config",
  "type": "relationship",
  "source_id": "doc_security_001",
  "target_id": "doc_config_001",
  "relationship_type": "references",
  "strength": 0.8,
  "metadata": {
    "direction": "unidirectional",
    "reason": "Security guide references configuration patterns",
    "created_at": "2026-07-02T00:00:00Z",
    "bidirectional": false,
    "traversal_weight": 0.8
  }
}
```

**Fields:**
- `id` (string, required): Unique relationship identifier
- `type` (string, required): "relationship"
- `source_id` (string, required): Source record ID
- `target_id` (string, required): Target record ID
- `relationship_type` (enum): "references", "depends_on", "extends", "contradicts", "complements"
- `strength` (float 0-1): Relationship strength
- `metadata` (object): Relationship metadata

**Index:** source_id + type for graph traversal

---

## Schema Validation Rules

All JSONL records must:

1. ✅ **Type Consistency**: `type` field matches record schema
2. ✅ **Required Fields**: All required fields present and non-null
3. ✅ **ID Uniqueness**: Record IDs are globally unique within type
4. ✅ **Reference Integrity**: All ID references resolve to existing records
5. ✅ **Timestamp Format**: ISO 8601 timestamps (YYYY-MM-DDTHH:MM:SSZ)
6. ✅ **Enum Validation**: Enum fields contain only defined values
7. ✅ **Metadata Structure**: Metadata objects follow type-specific schemas

---

## Index Strategy

| Schema | Index Name | Keys | Purpose |
|--------|-----------|------|---------|
| Document | doc_full_text | title, tags, content_summary | Full-text search |
| Section | sec_hierarchy | document_id, level, position | Hierarchical traversal |
| Block | blk_filter | section_id, block_type, language | Content filtering |
| Action | act_discovery | type, target, precedence | Action orchestration |
| Decision | dec_criteria | criteria, branches | Decision routing |
| Requirement | req_compliance | category, status, priority | Compliance tracking |
| Reference | ref_linkage | reference_type, value | Link validation |
| Relationship | rel_graph | source_id, relationship_type | Graph traversal |

---

## JSONL File Format

Each record on a single line, newline-delimited:

```jsonl
{"id":"doc_001","type":"document",...}
{"id":"sec_001","type":"section",...}
{"id":"blk_001","type":"block",...}
```

No trailing newline after last record. UTF-8 encoding required.

---

**Schema Version:** 1.0  
**Last Updated:** 2026-07-02  
**Author:** unified-doc-agent  
**Status:** Phase 9.2 Lane 3 Active
