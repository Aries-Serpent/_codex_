# ChatGPT Continuation Protocol

This document defines the pagination and resume contract for handling long responses that exceed token budgets.

## Purpose

When generating extensive outputs (repository traversals, large documentation, multi-file diffs), responses must be chunked to fit within token limits while maintaining continuity and allowing resumption.

## Protocol Specification

### Chunk Header Format

Every chunk begins with a standardized header:

```
—8<—[CHUNK {i}/{N} | topic: {section} | tokens≈{t}]
```

**Parameters:**
- `{i}` - Current chunk number (1-indexed)
- `{N}` - Total number of chunks (if known, else "?")
- `{section}` - Brief topic description (e.g., "Repository Structure", "File Generation")
- `{t}` - Approximate token count for this chunk

**Example:**
```
—8<—[CHUNK 1/3 | topic: Repository Inventory | tokens≈4500]
```

### Chunk Footer Format

If more content remains, the chunk ends with a continuation footer:

```
⟂ MORE:true | NEXT_CURSOR:{opaque_cursor} | NEXT_STEPS:{bulleted-next}
```

**Parameters:**
- `MORE:true` - Indicates continuation is required
- `{opaque_cursor}` - A unique, opaque string identifying where to resume (e.g., `SEC2_FILE5`, `ARCH_DIAGRAMS`)
- `{bulleted-next}` - Brief bullet list of what comes next

**Example:**
```
⟂ MORE:true | NEXT_CURSOR:FILES_SECURITY_MD | NEXT_STEPS:
  - Generate SECURITY.md
  - Generate .github/dependabot.yml
  - Final PR plan
```

### Final Chunk Footer

When all content has been emitted:

```
⟂ MORE:false | STATUS:COMPLETE
```

### Resume Prompt Format

To resume from a continuation point, use:

```
Resume from NEXT_CURSOR:{opaque_cursor} and continue {topic}
```

**Example:**
```
Resume from NEXT_CURSOR:FILES_SECURITY_MD and continue generating missing files
```

## Implementation Guidelines

### When to Chunk

Chunk responses when:
- Total output exceeds ~8,000 tokens (conservative threshold)
- Generating multiple large files (>2,000 tokens each)
- Traversing large directory trees (>100 files)
- Producing extensive tables or multi-file diffs

### How to Split Content

**Preferred Split Points:**
1. **Between major sections** - Split at logical boundaries (e.g., between different files being generated)
2. **Within large tables** - Use row boundaries, include table headers in each chunk
3. **Within file lists** - Group by directory or alphabetically
4. **Within diffs** - Split at file boundaries, not mid-file

**Example Split Strategy for File Generation:**

Chunk 1:
- Repository inventory
- Gap analysis
- Files A-B (CODEOWNERS, SECURITY.md)

Chunk 2:
- Files C-D (CHATGPT_SEARCH_RECIPES.md, CHATGPT_CONTINUATION.md)

Chunk 3:
- Files E-F (ARCHITECTURE.md updates, dependabot.yml)
- PR plan and checklist

### Cursor Design

Cursors should be:
- **Unique**: Each cursor identifies a distinct resume point
- **Opaque**: Internal structure not exposed to users
- **Descriptive**: Include hints for developer debugging (e.g., `SEC3_ARCH_DIAGRAMS`)
- **Stable**: Same cursor always resumes at the same point

**Recommended Pattern:**
```
{SECTION_ID}_{ARTIFACT_ID}
```

Examples:
- `INV_DIRECTORY_LISTING` - Resume at directory listing
- `FILES_CODEOWNERS` - Resume at CODEOWNERS generation
- `ARCH_MERMAID_DIAGRAMS` - Resume at architecture diagrams
- `PR_PLAN` - Resume at PR plan generation

## Splitting Strategies by Content Type

### Large Tables

**Before:**
```markdown
| Path | Purpose | Risk |
|------|---------|------|
| ... 200 rows ...
```

**Chunked:**

Chunk 1:
```markdown
—8<—[CHUNK 1/2 | topic: Repository Map | tokens≈4000]

| Path | Purpose | Risk |
|------|---------|------|
| ... rows 1-100 ...

⟂ MORE:true | NEXT_CURSOR:TABLE_REPO_MAP_PART2 | NEXT_STEPS:
  - Continue repository map (rows 101-200)
```

Chunk 2:
```markdown
—8<—[CHUNK 2/2 | topic: Repository Map (continued) | tokens≈4000]

| Path | Purpose | Risk |
|------|---------|------|
| ... rows 101-200 ...

⟂ MORE:false | STATUS:COMPLETE
```

### Directory Trees

Split by directory depth or alphabetical ranges:

Chunk 1: `.github/`, `docs/` (A-M)
Chunk 2: `docs/` (N-Z), `src/`
Chunk 3: `tests/`, `scripts/`, `config/`

### Multi-File Diffs

Split at file boundaries, never mid-file:

Chunk 1:
```
File: .github/CODEOWNERS
[full diff]

File: SECURITY.md
[full diff]
```

Chunk 2:
```
File: PROMPTS/CHATGPT_SEARCH_RECIPES.md
[full diff]
```

### Generated Files

For multiple file generations, group by category:

Chunk 1: Governance files (CODEOWNERS, SECURITY.md)
Chunk 2: Documentation files (ARCHITECTURE.md, search recipes)
Chunk 3: Automation files (dependabot.yml, workflows)

## Failure-Safe Rules

### Token Pressure Handling

When approaching token limits:

1. **Prefer indices over full content**: Emit file lists with summaries, not full content
2. **Defer to next chunk**: Stop mid-section if needed, resume with header context
3. **Use references**: Link to existing files instead of repeating content
4. **Summarize**: Provide abstracts instead of full details

### Example - Token Pressure Adaptation

**Normal Mode:**
```markdown
## Generated File: SECURITY.md

```md
[Full 2000-line SECURITY.md content]
```
```

**Token-Pressured Mode:**
```markdown
## Generated File: SECURITY.md

Summary: Complete security policy with vulnerability reporting, SLAs, triage process, disclosure policy, and dependency management.

Key sections: Supported Versions, Reporting (private), Response SLAs, Triage, Disclosure, PGP (optional), Dependencies (Dependabot link)

⟂ MORE:true | NEXT_CURSOR:FILE_SECURITY_MD_FULL | NEXT_STEPS:
  - Emit full SECURITY.md content
```

Then in next chunk:
```markdown
—8<—[CHUNK 2/3 | topic: SECURITY.md Full Content | tokens≈2000]

```md
[Full SECURITY.md content]
```
```

## Self-Resumption

For automated agents or continuous generation, the assistant can self-resume:

```markdown
⟂ MORE:true | NEXT_CURSOR:FILES_ARCH_MD | AUTO_RESUME:true

[Agent automatically continues with next chunk header]

—8<—[CHUNK 2/3 | topic: Architecture Documentation | tokens≈5000]
```

## Examples

### Example 1: Repository Traversal

**Chunk 1:**
```markdown
—8<—[CHUNK 1/3 | topic: Repository Structure | tokens≈4200]

# Repository Inventory

## Top-Level Structure (depth=2)
.github/
  CODEOWNERS
  workflows/
  ... 

docs/
  ARCHITECTURE.md
  api/
  ...

⟂ MORE:true | NEXT_CURSOR:INV_SRC_DIRECTORY | NEXT_STEPS:
  - Complete src/ directory listing
  - List tests/, scripts/, config/
  - Generate semantic map
```

**Resume:**
```
Resume from NEXT_CURSOR:INV_SRC_DIRECTORY and continue repository inventory
```

**Chunk 2:**
```markdown
—8<—[CHUNK 2/3 | topic: Source Code Inventory | tokens≈4500]

## src/ Directory

src/codex_ml/
  training/
    ...
  evaluation/
    ...

⟂ MORE:true | NEXT_CURSOR:INV_SEMANTIC_MAP | NEXT_STEPS:
  - Generate semantic map table
  - Identify gaps
```

### Example 2: Multi-File Generation

**Chunk 1:**
```markdown
—8<—[CHUNK 1/2 | topic: Governance Files | tokens≈6000]

# Generated Files

## A. .github/CODEOWNERS

```
# Default owners
* @Aries-Serpent/owners
...
```

## B. SECURITY.md

```md
# Security Policy
...
```

⟂ MORE:true | NEXT_CURSOR:FILES_PROMPTS_AND_DOCS | NEXT_STEPS:
  - Generate PROMPTS/CHATGPT_SEARCH_RECIPES.md
  - Generate CHATGPT_CONTINUATION.md
  - Generate docs/ARCHITECTURE.md updates
  - Generate .github/dependabot.yml
  - Emit PR plan
```

**Chunk 2:**
```markdown
—8<—[CHUNK 2/2 | topic: Documentation & Automation Files | tokens≈8000]

## C. PROMPTS/CHATGPT_SEARCH_RECIPES.md

```md
# ChatGPT Search Recipes
...
```

## D-F. [Additional files...]

# PR Plan
...

⟂ MORE:false | STATUS:COMPLETE
```

## Best Practices

1. **Always include chunk headers** - Even if you're unsure of total chunks, use `CHUNK 1/?`
2. **Make cursors meaningful** - Future you (or another agent) should understand where to resume
3. **Provide context in NEXT_STEPS** - Don't just say "continue", specify what's next
4. **Test resumption** - Ensure cursors actually identify correct resume points
5. **Document chunk strategy** - In first chunk, outline how content will be split
6. **Maintain state** - Each chunk should be self-contained enough to understand context
7. **Use consistent formatting** - Makes parsing and automation easier

## Validation Checklist

Before emitting a continuation footer:

- [ ] Cursor is unique and descriptive
- [ ] NEXT_STEPS clearly describes remaining work
- [ ] Current chunk ends at a logical boundary
- [ ] Next chunk can start cleanly from cursor
- [ ] Total chunks estimate is reasonable

## Integration with Search Recipes

When combining continuation with search operations:

```markdown
—8<—[CHUNK 1/? | topic: Search Trace | tokens≈3000]

# Search Trace

## Query 1: Repository Structure
**Query:** `repo:Aries-Serpent/_codex_ path:/ in:path`
**Why:** Understand top-level organization
**Top Hits:**
  - .github/
  - docs/
  - src/
  ...

⟂ MORE:true | NEXT_CURSOR:SEARCH_DOCUMENTATION | NEXT_STEPS:
  - Search for documentation files
  - Search for architecture files
  - Search for security files
  - Generate gap list
```

## Tooling Support

For automated parsing and resumption:

```python
import re

def parse_footer(text):
    """Extract continuation metadata from chunk footer."""
    pattern = r'⟂ MORE:(\w+) \| NEXT_CURSOR:(\S+)(?: \| NEXT_STEPS:(.+))?'
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return {
            'more': match.group(1) == 'true',
            'cursor': match.group(2),
            'next_steps': match.group(3).strip() if match.group(3) else None
        }
    return None

def format_resume_prompt(cursor, topic):
    """Generate standardized resume prompt."""
    return f"Resume from NEXT_CURSOR:{cursor} and continue {topic}"
```

---

**Version:** 1.0  
**Last Updated:** 2025-11-02  
**Maintainer:** @Aries-Serpent/docs-team
