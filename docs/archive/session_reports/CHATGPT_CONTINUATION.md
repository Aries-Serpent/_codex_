# ChatGPT Continuation Protocol

This document defines the pagination and resume contract for handling long responses that exceed token budgets.

## Purpose

When generating extensive outputs (repository traversals, large documentation, multi-file diffs), responses must be chunked to fit within token limits while maintaining continuity and allowing resumption.

## Protocol Specification

### Chunk Header Format

Every chunk begins with a standardized header:

```text
—8<—[CHUNK {i}/{N} | topic: {section} | tokens≈{t}]
```text

**Parameters:**
- `{i}` - Current chunk number (1-indexed)
- `{N}` - Total number of chunks (if known, else "?")
- `{section}` - Brief topic description (e.g., "Repository Structure", "File Generation")
- `{t}` - Approximate token count for this chunk

**Example:**
```text
—8<—[CHUNK 1/3 | topic: Repository Inventory | tokens≈4500]
```text

### Chunk Footer Format

If more content remains, the chunk ends with a continuation footer:

```text
⟂ MORE:true | NEXT_CURSOR:{opaque_cursor} | NEXT_STEPS:{bulleted-next}
```text

**Parameters:**
- `MORE:true` - Indicates continuation is required
- `{opaque_cursor}` - A unique, opaque string identifying where to resume (e.g., `SEC2_FILE5`, `ARCH_DIAGRAMS`)
- `{bulleted-next}` - Brief bullet list of what comes next

**Example:**
```text
⟂ MORE:true | NEXT_CURSOR:FILES_SECURITY_MD | NEXT_STEPS:
  - Generate SECURITY.md
  - Generate .github/dependabot.yml
  - Final PR plan
```text

### Final Chunk Footer

When all content has been emitted:

```text
⟂ MORE:false | STATUS:COMPLETE
```text

### Resume Prompt Format

To resume from a continuation point, use:

```text
Resume from NEXT_CURSOR:{opaque_cursor} and continue {topic}
```text

**Example:**
```text
Resume from NEXT_CURSOR:FILES_SECURITY_MD and continue generating missing files
```text

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

- Chunk 1: Repository inventory + gap analysis + Files A-B (CODEOWNERS, SECURITY.md)
- Chunk 2: Files C-D (CHATGPT_SEARCH_RECIPES.md, CHATGPT_CONTINUATION.md)
- Chunk 3: Files E-F (ARCHITECTURE.md updates, dependabot.yml) + PR plan

### Cursor Design

Cursors should be:
- **Unique**: Each cursor identifies a distinct resume point
- **Opaque**: Internal structure not exposed to users
- **Descriptive**: Include hints for developer debugging (e.g., `SEC3_ARCH_DIAGRAMS`)
- **Stable**: Same cursor always resumes at the same point

**Recommended Pattern:**
```text
{SECTION_ID}_{ARTIFACT_ID}
```text

Examples:
- `INV_DIRECTORY_LISTING` - Resume at directory listing
- `FILES_CODEOWNERS` - Resume at CODEOWNERS generation
- `ARCH_MERMAID_DIAGRAMS` - Resume at architecture diagrams
- `PR_PLAN` - Resume at PR plan generation

## Splitting Strategies by Content Type

### Large Tables

Split tables at row boundaries, preserving headers in each chunk:
- Chunk 1: Header + rows 1-100
- Chunk 2: Header + rows 101-200
- Include cursor pointing to next row range

### Directory Trees

Split by directory depth or alphabetical ranges:
- Chunk 1: `.github/`, `docs/` (A-M)
- Chunk 2: `docs/` (N-Z), `src/`
- Chunk 3: `tests/`, `scripts/`, `config/`

### Multi-File Diffs

Split at file boundaries, never mid-file. Each chunk should contain complete file diffs.

### Generated Files

For multiple file generations, group by category:
- Chunk 1: Governance files (CODEOWNERS, SECURITY.md)
- Chunk 2: Documentation files (ARCHITECTURE.md, search recipes)
- Chunk 3: Automation files (dependabot.yml, workflows)

## Failure-Safe Rules

### Token Pressure Handling

When approaching token limits:

1. **Prefer indices over full content**: Emit file lists with summaries, not full content
2. **Defer to next chunk**: Stop mid-section if needed, resume with header context
3. **Use references**: Link to existing files instead of repeating content
4. **Summarize**: Provide abstracts instead of full details

### Token-Pressured Mode

Instead of emitting full file content, provide:
- Summary of file purpose
- Key sections overview
- Cursor to emit full content in next chunk

## Self-Resumption

For automated agents or continuous generation, the assistant can self-resume by including an `AUTO_RESUME:true` flag in the footer.

## Examples

### Example 1: Repository Traversal

**Chunk 1:**
- Emit: `—8<—[CHUNK 1/3 | topic: Repository Structure | tokens≈4200]`
- Content: Top-level structure inventory for `.github/`, `docs/`, etc.
- Footer: `⟂ MORE:true | NEXT_CURSOR:INV_SRC_DIRECTORY | NEXT_STEPS: Complete src/ listing`

**Resume Prompt:**
```text
Resume from NEXT_CURSOR:INV_SRC_DIRECTORY and continue repository inventory
```text

**Chunk 2:**
- Emit: `—8<—[CHUNK 2/3 | topic: Source Code Inventory | tokens≈4500]`
- Content: Detailed `src/` directory listing
- Footer: `⟂ MORE:true | NEXT_CURSOR:INV_SEMANTIC_MAP | NEXT_STEPS: Generate semantic map`

### Example 2: Multi-File Generation

**Chunk 1:**
- Header: `—8<—[CHUNK 1/2 | topic: Governance Files | tokens≈6000]`
- Content: Generated CODEOWNERS and SECURITY.md files
- Footer: `⟂ MORE:true | NEXT_CURSOR:FILES_PROMPTS_AND_DOCS | NEXT_STEPS: Remaining files + PR plan`

**Chunk 2:**
- Header: `—8<—[CHUNK 2/2 | topic: Documentation & Automation Files | tokens≈8000]`
- Content: Remaining files (search recipes, continuation doc, dependabot config) + PR plan
- Footer: `⟂ MORE:false | STATUS:COMPLETE`

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

When combining continuation with search operations, include search metadata in chunk headers and provide clear resume cursors for incomplete search traversals.

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
```text

---

**Version:** 1.0  
**Last Updated:** Previous Cycle-11-02  
**Maintainer:** @Aries-Serpent/docs-team
