# PHASE 5.4: DOCUMENTATION SCHEMA & STANDARDIZATION TEMPLATES

**Campaign:** Phase 3-5 Multi-Agent Deployment  
**Phase:** Phase 5 - Repository Organization (Agent 4)  
**Document:** Schema & Template Reference  
**Version:** 1.0.0  
**Created:** 2026-02-17  

---

## 📋 Table of Contents

1. [YAML Frontmatter Schema](#yaml-frontmatter-schema)
2. [Document Type Templates](#document-type-templates)
3. [Naming Conventions](#naming-conventions)
4. [Directory Structure Standards](#directory-structure-standards)
5. [Schema Compliance Checklist](#schema-compliance-checklist)
6. [Examples](#examples)

---

## YAML Frontmatter Schema

### Complete Schema with All Fields

```yaml
---
# REQUIRED FIELDS (must be present on every document)

title: "Document Title"
# Type: String (required)
# Description: Human-readable title matching the main H1 heading
# Examples:
#   - "Architecture Overview"
#   - "Installation Guide"
#   - "API Reference"
# Max length: 100 characters

type: "guide"
# Type: Enum (required)
# Valid values: "guide", "reference", "tutorial", "architecture", "runbook", 
#              "explanation", "example", "template", "checklist", "status"
# Description: What kind of document this is
# Used for: categorization, filtering, navigation generation

category: "agents"
# Type: Enum (required)
# Valid values: "agents", "architecture", "configuration", "operations", "security",
#              "development", "testing", "deployment", "api", "guides", "planning",
#              "governance", "compliance", "performance", "monitoring"
# Description: Primary topic category
# Used for: navigation structure, cross-linking

version: "1.0.0"
# Type: String (required, semantic versioning)
# Format: MAJOR.MINOR.PATCH (e.g., "1.2.3")
# Description: Document version for tracking changes
# Examples:
#   - "1.0.0" (initial release)
#   - "1.1.0" (feature addition)
#   - "1.0.1" (bug fix)

status: "active"
# Type: Enum (required)
# Valid values: "active", "draft", "review", "archived", "deprecated"
# Descriptions:
#   - active: Document is current and maintained
#   - draft: Document is work-in-progress
#   - review: Document pending review/approval
#   - archived: Document no longer maintained (historical reference)
#   - deprecated: Document should not be used (replaced by another)

audience: "developers"
# Type: Enum or list (required)
# Valid values: "developers", "operators", "users", "contributors", "maintainers", "all"
# Description: Primary audience for this document
# Examples:
#   - "developers" (for technical implementation guides)
#   - ["users", "developers"] (for features affecting both)
#   - "all" (for general information)

last_updated: "2026-02-17T14:30:00Z"
# Type: ISO 8601 timestamp (required)
# Format: YYYY-MM-DDTHH:MM:SSZ
# Description: Last date this document was reviewed/updated
# Used for: staleness detection, sort by recency

# OPTIONAL FIELDS (recommended for better organization)

authors:
  - name: "Author Name"
    role: "role/Agent Name"
    # Examples: "Senior Developer", "Phase 5.4 Agent", "Documentation Team"
  - name: "Co-Author Name"
    role: "Contributor"

tags:
  - "agent-system"
  - "documentation"
  - "consolidation"
# Type: Array of strings
# Description: Keywords for discovery and search
# Best practices:
#   - Use hyphen-separated lowercase
#   - 5-10 tags per document
#   - Enables cross-cutting searches

related_docs:
  - title: "Related Document Name"
    path: "relative/path/to/doc.md"
  - title: "Another Related Doc"
    path: "relative/path/to/another.md"
# Type: Array of objects
# Description: Links to related documents
# Format: relative paths from docs/ root

depth: 2
# Type: Integer 0-3 (required)
# Description: Directory nesting level
# Values:
#   - 0: docs/FILE.md (root level)
#   - 1: docs/category/FILE.md
#   - 2: docs/category/subcategory/FILE.md
#   - 3: docs/category/sub/sub/FILE.md (max allowed)
# Used for: navigation structure, breadcrumbs

# CONDITIONAL FIELDS (for specific document types)

parent: "relative/path/to/parent.md"
# When to use: If this doc is part of a larger guide/reference
# Examples: guides/setup/GUIDE.md has parent: "guides/OVERVIEW.md"

next_doc: "relative/path/to/next.md"
prev_doc: "relative/path/to/prev.md"
# When to use: For sequential documents (tutorials, guides with chapters)
# Creates navigation flow between documents

supersedes: "old/path/to/old_doc.md"
# When to use: If this document replaces another
# Used for: redirect planning, deprecation

migrated_from: "docs/old_location/FILE.md"
# When to use: If document was moved from another location
# Used for: redirect content, historical tracking

search_keywords:
  - "setup"
  - "installation"
# When to use: Additional search terms beyond tags
# Format: simple words or phrases (3-5 terms)

---
```

### Field Validation Rules

| Field | Type | Required | Min Len | Max Len | Format |
|-------|------|----------|---------|---------|--------|
| title | String | ✓ | 3 | 100 | Plain text |
| type | Enum | ✓ | - | - | lowercase |
| category | Enum | ✓ | - | - | lowercase |
| version | String | ✓ | 5 | 10 | MAJOR.MINOR.PATCH |
| status | Enum | ✓ | - | - | lowercase |
| audience | Enum/Array | ✓ | - | - | lowercase |
| last_updated | Timestamp | ✓ | 20 | 24 | ISO 8601Z |
| authors | Array | ✗ | 1 | 5 | name + role |
| tags | Array | ✗ | 3 | 10 | hyphen-separated |
| related_docs | Array | ✗ | 0 | 15 | title + path |
| depth | Integer | ✓ | 0 | 3 | 0-3 only |

---

## Document Type Templates

### Template 1: Guide Template

Use for: Step-by-step guides, how-to docs, quickstart guides

```markdown
---
title: "[Topic] Guide"
type: "guide"
category: "guides"  # or appropriate category
version: "1.0.0"
status: "active"
audience: "developers"  # or appropriate audience
last_updated: "2026-02-17T00:00:00Z"
authors:
  - name: "Author Name"
    role: "Contributor"
tags:
  - "guide"
  - "how-to"
  - "topic-keyword"
depth: 1
---

# [Topic] Guide

**Purpose**: Brief one-sentence description of what this guide teaches.

**Estimated Time**: 15-30 minutes

## Prerequisites

What the reader needs before starting:
- Prerequisite 1
- Prerequisite 2
- Skill or knowledge required

## Overview

High-level description of what you'll learn and accomplish:
- What this guide teaches
- What you'll be able to do after completing it
- Key concepts covered

## Step 1: [First Action]

Detailed instructions for first step.

```
code example here
```

**Key point**: Important note about this step.

## Step 2: [Second Action]

Detailed instructions for second step.

### Sub-step 2.1

If there are sub-steps, detail them here.

## Verification

How to verify this step worked correctly.

```
verification command or screenshot
```

## Common Issues

### Issue: [Common Problem]

**Symptom**: How it manifests.

**Solution**: How to fix it.

### Issue: [Another Common Problem]

**Symptom**: Symptoms.

**Solution**: Fix.

## Next Steps

What to do after completing this guide:
- Next topic to learn
- Advanced variations
- Related topics

## See Also

- [Related Guide](../related.md)
- [Reference Documentation](../reference.md)
- External links if applicable

## Troubleshooting

General troubleshooting tips not in the issues section.

---

**Document History**
| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-17 | Initial guide |
```

### Template 2: Reference Template

Use for: API docs, configuration reference, command reference

```markdown
---
title: "[Topic] Reference"
type: "reference"
category: "reference"  # or appropriate category
version: "1.0.0"
status: "active"
audience: "developers"
last_updated: "2026-02-17T00:00:00Z"
depth: 2
tags:
  - "reference"
  - "api"
  - "spec"
---

# [Topic] Reference

**Scope**: What this reference covers.

**Last Updated**: Date and version.

## Quick Reference

| Term | Definition | Example |
|------|-----------|---------|
| Term 1 | Brief definition | example_1 |
| Term 2 | Brief definition | example_2 |

## Detailed Reference

### [Section 1]

Detailed information about this section.

#### [Subsection 1.1]

- Point 1
- Point 2

### [Section 2]

Additional reference information.

## Examples

### Example 1: [Use Case]

```
code example
```

Explanation of the example.

### Example 2: [Another Use Case]

```
code example
```

Explanation.

## Best Practices

Recommended ways to use this reference.

## Related References

- [Related Reference 1](../ref1.md)
- [Related Reference 2](../ref2.md)

## See Also

- [Guide that uses this](../guide.md)
- [Tutorial](../tutorial.md)
```

### Template 3: Architecture Template

Use for: System architecture, design docs, technical specifications

```markdown
---
title: "[System] Architecture"
type: "architecture"
category: "architecture"
version: "1.0.0"
status: "active"
audience: "developers"
last_updated: "2026-02-17T00:00:00Z"
depth: 2
tags:
  - "architecture"
  - "design"
  - "system"
---

# [System] Architecture

**Author**: [Name/Team]  
**Last Reviewed**: [Date]  
**Next Review**: [Date + 6 months]

## Overview

High-level description of this system and its purpose.

### Goals

- Goal 1
- Goal 2

### Constraints

- Constraint 1
- Constraint 2

## System Diagram

```
[ASCII diagram or reference to image]
```

## Components

### Component 1: [Name]

**Purpose**: What this component does.

**Responsibilities**:
- Responsibility 1
- Responsibility 2

**Inputs**: What data comes in.

**Outputs**: What data goes out.

### Component 2: [Name]

[Same structure as Component 1]

## Data Flow

Describe how data moves through the system:

1. User initiates action
2. Component A processes request
3. Component B handles business logic
4. Component C returns response

### Flow Diagram

```
[ASCII or reference to diagram showing data flow]
```

## Integration Points

How this system connects to other systems:

| System | Connection Type | Protocol | Data Format |
|--------|-----------------|----------|-------------|
| System A | REST API | HTTP/HTTPS | JSON |
| System B | Message Queue | AMQP | Protobuf |

## Design Decisions

### Decision 1: [What was decided]

**Context**: Why this decision was needed.

**Options Considered**:
- Option A (rejected because...)
- Option B (selected because...)
- Option C (rejected because...)

**Consequences**: What this decision enables/constrains.

### Decision 2: [Another decision]

[Same structure]

## Deployment

How this system is deployed:

- Containerization: Docker / Kubernetes
- Scaling: Horizontal / Vertical
- Failover: Active-Active / Active-Passive
- Data Persistence: [Approach]

## Monitoring & Observability

Key metrics to monitor:

| Metric | Purpose | Threshold |
|--------|---------|-----------|
| Requests/sec | Load monitoring | >1000 = alert |
| Latency (p99) | Performance | >100ms = alert |
| Error rate | Health | >1% = alert |

Key logs to collect:

- Request/response logs
- Error logs
- Performance logs

## Security Considerations

- Authentication: [How users are authenticated]
- Authorization: [How access is controlled]
- Data Protection: [Encryption, PII handling]
- Network Security: [Firewalls, VPCs]

## Testing Strategy

How this system is tested:

- Unit tests: [Coverage %]
- Integration tests: [Scope]
- Load tests: [Capacity expectations]

## Known Limitations

- Limitation 1
- Limitation 2

## Future Improvements

Planned enhancements:

- Enhancement 1 (Phase X)
- Enhancement 2 (Phase X)

## Related Documentation

- [Implementation Guide](../implementation.md)
- [Operations Guide](../operations.md)
- [API Reference](../api.md)

---

**Architecture Review History**
| Version | Date | Reviewer | Changes |
|---------|------|----------|---------|
| 1.0.0 | 2026-02-17 | Reviewer Name | Initial design |
```

### Template 4: Tutorial Template

Use for: Step-by-step learning paths, hands-on exercises

```markdown
---
title: "[Topic] Tutorial"
type: "tutorial"
category: "guides"
version: "1.0.0"
status: "active"
audience: ["developers", "users"]
last_updated: "2026-02-17T00:00:00Z"
depth: 2
tags:
  - "tutorial"
  - "learning"
  - "hands-on"
next_doc: "advanced_tutorial.md"
---

# [Topic] Tutorial

**Level**: Beginner / Intermediate / Advanced

**Estimated Duration**: 1-2 hours

**What You'll Learn**: 
- Learning outcome 1
- Learning outcome 2

## Prerequisites

- Prerequisite 1 (link to prerequisite doc)
- Prerequisite 2

## Environment Setup

### Installing Required Tools

```bash
command to install
```

### Verifying Installation

```bash
verification command
```

## Lesson 1: [First Concept]

### Understanding [Concept]

Explanation of the concept.

### Try It Out

**Task**: Do something practical.

```
code to try
```

**Expected Output**:
```
what you should see
```

### Common Mistakes

- Mistake 1: What goes wrong and how to fix it
- Mistake 2: What goes wrong and how to fix it

## Lesson 2: [Second Concept]

[Same structure as Lesson 1]

## Building Your Project

Now put concepts together to build something real.

### Project Overview

Description of what you'll build.

### Step 1: [Project Step]

Detailed steps.

### Step 2: [Project Step]

More steps.

## Verification

Test that your project works:

```
test commands
```

## Troubleshooting

### Problem: [Common Issue]

**Symptoms**: How it appears.

**Solution**: Steps to fix.

## Next Steps

- [Intermediate Tutorial](../intermediate.md)
- [Advanced Topic](../advanced.md)
- [Real-World Project](../project.md)

## Additional Resources

- [Reference Documentation](../reference.md)
- [Related Tutorial](../related.md)
- External resources
```

---

## Naming Conventions

### Directory Naming Rules

```
✅ CORRECT:
- docs/cognitive-brain/  (lowercase, hyphens)
- docs/api-reference/    (hyphenated)
- docs/setup/            (singular form for collections)
- docs/guides/           (plural for collections)

❌ INCORRECT:
- docs/CognitiveBrain/   (PascalCase)
- docs/Cognitive_Brain/  (snake_case)
- docs/cognitive_brain/  (underscore - use hyphens)
- docs/guide/            (singular for collections)
```

### File Naming Rules

```
✅ CORRECT:
- docs/architecture/ARCHITECTURE.md     (SNAKE_CASE for primary)
- docs/guides/SETUP_GUIDE.md            (SNAKE_CASE for primary)
- docs/agent/QUICK_REFERENCE.md
- docs/config/HYDRA_MIGRATION.md
- docs/agents/INDEX.md                  (INDEX.md for indices)
- docs/agents/README.md                 (README.md for overviews)
- docs/agents/introduction.md           (lowercase for supporting docs)
- docs/agents/quick-tips.md             (lowercase with hyphens for supporting)

❌ INCORRECT:
- docs/architecture/architecture.md     (should be ARCHITECTURE.md)
- docs/guides/setup-guide.md            (should be SETUP_GUIDE.md)
- docs/agents/INDEX.txt                 (should be .md)
- docs/agents/Quick_Reference.md        (should be QUICK_REFERENCE.md)
- docs/agents/quickReference.md         (should be lowercase with hyphens: quick-reference.md)
```

### File Organization Pattern

```
docs/
├── [PRIMARY_DOCS].md                  # Root-level primary docs (few files)
├── category/                          # Categorical organization
│   ├── README.md                      # Category overview
│   ├── INDEX.md                       # Category index/navigation
│   ├── PRIMARY_TOPIC.md               # Primary topic documents (SNAKE_CASE)
│   ├── supporting-doc.md              # Supporting docs (lowercase-hyphens)
│   ├── examples/                      # Examples subdirectory
│   │   ├── example-1.md
│   │   └── example-2.md
│   └── archive/                       # Deprecated/old docs
│       ├── OLD_DOCUMENT.md
│       └── OLD_DOCUMENT.v1.md
└── archive/                           # Repository-wide archive
    ├── old-category/
    └── deprecated-docs/
```

---

## Directory Structure Standards

### Canonical Directory Hierarchy

After consolidation, this is the standard structure:

```
docs/
├── INDEX.md                           # Master documentation index
├── README.md                          # Root documentation overview
│
├── agents/                            # Agent system documentation
│   ├── INDEX.md
│   ├── README.md
│   ├── custom-agents/
│   │   ├── ARCHITECTURE.md
│   │   ├── DEVELOPMENT_GUIDE.md
│   │   ├── CATALOG.md
│   │   └── TEMPLATES.md
│   ├── quick-reference/
│   │   ├── TOKEN_QUICK_REFERENCE.md
│   │   ├── MCP_QUICK_START.md
│   │   └── SELECTION_FRAMEWORK.md
│   ├── workflows/
│   │   ├── INTERACTION_PROTOCOL.md
│   │   ├── COORDINATION_WORKFLOWS.md
│   │   └── REPEATABLE_PROCESSES.md
│   ├── setup/
│   │   ├── COPILOT_SETUP_COMPLETE_GUIDE.md
│   │   ├── COPILOT_VALIDATION.md
│   │   ├── TOKEN_GUIDE.md
│   │   └── COGNITIVE_APP_CONNECTION.md
│   └── archive/
│
├── architecture/                      # Architecture documentation
│   ├── INDEX.md
│   ├── ARCHITECTURE.md                # Primary architecture
│   ├── BLUEPRINT.md                   # Architecture blueprints
│   ├── ast/                           # Specialized architectures
│   │   └── ARCHITECTURE.md
│   ├── cognitive-brain/
│   │   ├── ARCHITECTURE.md
│   │   └── STATUS.md
│   └── archive/
│
├── configuration/                     # Configuration documentation
│   ├── INDEX.md
│   ├── README.md
│   ├── guides/
│   │   ├── HYDRA_QUICK_START.md
│   │   ├── HYDRA_ADVANCED.md
│   │   ├── OMEGACONF_SCHEMA.md
│   │   └── MIGRATION_GUIDE.md
│   ├── reference/
│   │   ├── ENVIRONMENT_VARIABLES.md
│   │   ├── HYDRA_REFERENCE.md
│   │   ├── SCHEMA_REFERENCE.md
│   │   └── TROUBLESHOOTING.md
│   ├── patterns/
│   │   ├── CONVENTIONS.md
│   │   └── BEST_PRACTICES.md
│   └── archive/
│
├── phases/                            # Phase and planning documentation
│   ├── PHASE_HISTORY_TIMELINE.md      # Master phase index
│   ├── CONTINUATION_PROMPTS.md        # Consolidated continuation prompts
│   ├── active/
│   │   ├── PHASE_1.md
│   │   ├── PHASE_2.md
│   │   └── ...
│   └── archive/
│       └── [completed phases]
│
├── plans/                             # Active planning documents
│   ├── INDEX.md
│   ├── ACTIVE_PLANS_INDEX.md
│   ├── [categorized plans]
│   └── archive/
│       ├── completed/
│       └── obsolete/
│
├── guides/                            # General guides
├── tutorials/                         # Tutorial documentation
├── reference/                         # General references
├── api/                               # API documentation
├── operations/                        # Operations and runbooks
├── security/                          # Security documentation
├── development/                       # Development guides
├── testing/                           # Testing documentation
├── deployment/                        # Deployment guides
├── governance/                        # Governance and compliance
│
└── archive/                           # Complete archive
    ├── pre_consolidation_backups/
    ├── status_updates/
    ├── phases/
    ├── plans/
    ├── audits/
    └── [other consolidated content]
```

---

## Schema Compliance Checklist

Use this checklist to verify documents meet the consolidation schema:

### YAML Frontmatter Check
- [ ] `title` field present and matches H1 heading
- [ ] `type` field present and is valid enum value
- [ ] `category` field present and is valid enum value
- [ ] `version` field present and follows semver
- [ ] `status` field present and is valid enum value
- [ ] `audience` field present and is valid enum value(s)
- [ ] `last_updated` field present in ISO 8601 format
- [ ] `depth` field present and is valid integer 0-3
- [ ] `authors` field populated with at least one author
- [ ] All required fields validated without errors

### Content Structure Check
- [ ] Document has H1 heading (starts with `#`)
- [ ] H1 heading matches `title` in frontmatter
- [ ] Document follows appropriate template structure
- [ ] Sections use consistent heading hierarchy (H2, H3, etc.)
- [ ] Code examples have syntax highlighting (```language)
- [ ] Links are relative and use correct paths
- [ ] Related docs listed in frontmatter or at end

### Naming & Organization Check
- [ ] File name follows convention (SNAKE_CASE for primary, lowercase-hyphens for supporting)
- [ ] Directory follows hierarchical structure
- [ ] File is in appropriate category directory
- [ ] Archived files in `archive/` subdirectories
- [ ] All cross-references updated to new locations

### Link Validation Check
- [ ] All internal links valid and working
- [ ] Links use relative paths from docs/ root
- [ ] Related docs cross-references valid
- [ ] No circular references
- [ ] Redirect files in place for moved documents

### Quality Checks
- [ ] No TODO or FIXME comments in final version
- [ ] All code examples syntactically correct
- [ ] Examples tested and verified
- [ ] Spelling and grammar reviewed
- [ ] Markdown formatting valid
- [ ] Tables format correctly

### Metadata Check
- [ ] Tags field contains 3-10 relevant tags
- [ ] Authors field populated correctly
- [ ] Version field accurate
- [ ] Status field accurate
- [ ] Audience field appropriate
- [ ] Last_updated is current

---

## Examples

### Example 1: Properly Formatted Document

```markdown
---
title: "Custom Agent Development Guide"
type: "guide"
category: "agents"
version: "1.2.0"
status: "active"
audience: ["developers", "contributors"]
last_updated: "2026-02-17T14:30:00Z"
authors:
  - name: "Phase 5.4 Agent"
    role: "Documentation Consolidation"
tags:
  - "agents"
  - "development"
  - "custom-agents"
  - "guide"
related_docs:
  - title: "Agent Architecture"
    path: "agents/custom-agents/ARCHITECTURE.md"
  - title: "Agent Selection Framework"
    path: "agents/quick-reference/SELECTION_FRAMEWORK.md"
depth: 2
---

# Custom Agent Development Guide

**Purpose**: Learn how to develop and deploy custom GitHub Copilot agents.

**Estimated Time**: 2-3 hours

## Prerequisites

- Understanding of GitHub Copilot basics
- Python 3.9+ installed
- Git knowledge

## Overview

This guide teaches you to build custom agents that ...

[rest of document follows template structure]
```

### Example 2: Consolidated Agent Documentation Index

```markdown
---
title: "Agent System Documentation"
type: "reference"
category: "agents"
version: "1.0.0"
status: "active"
audience: "developers"
last_updated: "2026-02-17T00:00:00Z"
depth: 1
tags:
  - "agents"
  - "index"
  - "navigation"
---

# Agent System Documentation

**Overview**: Complete documentation for the _codex_ agent system.

## Quick Links

- [Getting Started](agents/setup/COPILOT_SETUP_COMPLETE_GUIDE.md)
- [Agent Development](agents/custom-agents/DEVELOPMENT_GUIDE.md)
- [API Reference](agents/reference/API.md)

## Documentation Categories

### Setup & Configuration
- [Copilot Setup Guide](agents/setup/COPILOT_SETUP_COMPLETE_GUIDE.md)
- [Token Management](agents/quick-reference/TOKEN_QUICK_REFERENCE.md)
- [MCP Integration](agents/quick-reference/MCP_QUICK_START.md)

### Development
- [Agent Architecture](agents/custom-agents/ARCHITECTURE.md)
- [Development Guide](agents/custom-agents/DEVELOPMENT_GUIDE.md)
- [Code Templates](agents/custom-agents/TEMPLATES.md)

### Workflows
- [Agent Interaction Protocol](agents/workflows/INTERACTION_PROTOCOL.md)
- [Coordination Patterns](agents/workflows/COORDINATION_WORKFLOWS.md)

### Reference
- [Agent Catalog](agents/custom-agents/CATALOG.md)
- [Selection Framework](agents/quick-reference/SELECTION_FRAMEWORK.md)

---

**Last Updated**: 2026-02-17  
**Maintained by**: Phase 5.4 Agent
```

---

## Schema Enforcement

### Automated Compliance Checking

During Week 6 (Finalization), run this automated check:

```bash
# Check all docs for schema compliance
python3 scripts/validate_doc_schema.py docs/

# Output will show:
# ✓ docs/agents/ARCHITECTURE.md - COMPLIANT
# ✗ docs/guides/SETUP.md - MISSING: title, type, category
# ⚠ docs/reference/API.md - DEPRECATED: author field (use authors)
```

### Manual Review Checklist

For high-risk consolidations, manually verify:

1. **Content Completeness**: No information lost in merge
2. **Link Integrity**: All references updated
3. **Schema Compliance**: All required fields present
4. **Navigation**: Indices and cross-references correct
5. **Archive**: Old files properly archived with redirects

---

## Migration Path for Existing Docs

For documents not yet compliant:

**Phase 1: Add YAML Frontmatter**
```markdown
---
title: "Document Title"
type: "guide"
category: "general"
version: "1.0.0"
status: "draft"
audience: "all"
last_updated: "2026-02-17T00:00:00Z"
depth: 1
---
```

**Phase 2: Update Content Structure**
- Reorganize to match template
- Add missing sections
- Improve code examples

**Phase 3: Verify Schema Compliance**
- Run automated checks
- Manual review
- Update links

**Phase 4: Move to Canonical Location**
- Rename file if needed
- Move to appropriate directory
- Create redirects

---

## Ongoing Maintenance

### Monthly Review

- Check for deprecated documents
- Verify last_updated dates
- Update status field as needed
- Review for accuracy

### Quarterly Reorganization

- Assess directory structure
- Move files if needed
- Update indices
- Review consistency

### Annual Audit

- Full schema compliance audit
- Content accuracy review
- Link validation
- Archive cleanup

---

## Questions & Support

For questions about the schema:
- Consult this document first
- Examples section for common cases
- Run automated compliance check
- Escalate complex questions to Phase 5.4 Agent

---

**Document History**
| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-17 | Initial schema and templates |

**End of Schema & Standardization Templates**
