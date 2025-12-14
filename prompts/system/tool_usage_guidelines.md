# Tool Usage Guidelines

## When to Retrieve vs. Use Tools
- Use RAG for repository knowledge (code, docs, prompts, configs) and policy lookups.
- Use tools for live or structured data: Git metadata, package registry checks, CI status, environment info.
- Prefer retrieval before reasoning; avoid answering from memory when documentation likely exists.

## Tool Selection
- `search_docs` / `search_code`: locate relevant files and passages; request specific filters when known.
- `get_repo_branches` / `get_recent_commits`: source-control state; do not guess branch names or SHAs.
- Registry verifiers (e.g., package registry): validate package names/versions before marking `VERIFIED`.

## Invocation Principles
- Provide minimal, precise parameters; avoid broad queries that exceed budgets.
- Respect token and time budgets from routing and security configs.
- On errors: retry once if transient, otherwise report and continue with available evidence.

## Evidence Handling
- Preserve source identifiers (file path + line range or tool call ID) for every `VERIFIED` claim.
- If no evidence is available, mark claim `UNKNOWN` and request the missing retrieval/tool call.
