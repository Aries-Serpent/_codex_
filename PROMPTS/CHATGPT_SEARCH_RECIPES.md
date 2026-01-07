# ChatGPT Search Recipes for Aries-Serpent/_codex_

This guide teaches ChatGPT and humans how to effectively traverse and search the `_codex_` repository.

## Table of Contents
- [Web Code Search Recipes](#web-code-search-recipes)
- [GitHub CLI Search](#github-cli-search)
- [GraphQL Search with Pagination](#graphql-search-with-pagination)
- [Finding Specific Artifact Types](#finding-specific-artifact-types)
- [Triage Matrix](#triage-matrix)

---

## Web Code Search Recipes

Use these queries in GitHub's web search or via the GitHub API:

### Basic Repository Navigation
```text
repo:Aries-Serpent/_codex_ path:/ in:path
```text
Lists all top-level directories and files.

### Find All Markdown Documentation
```text
repo:Aries-Serpent/_codex_ language:Markdown in:file
```text
Returns all Markdown files across the repository.

### Locate README Files
```text
repo:Aries-Serpent/_codex_ filename:README.md
```text
Finds all README files in any directory.

### Search GitHub Workflows & Actions
```text
repo:Aries-Serpent/_codex_ path:.github/ in:path
```text
Lists all `.github/` directory contents including workflows, templates, and configs.

```text
repo:Aries-Serpent/_codex_ path:.github/workflows/ extension:yml
```text
Specifically finds workflow YAML files.

### Find Architecture & Design Documents
```text
repo:Aries-Serpent/_codex_ (ADR OR "architecture" OR "design") in:file
```text
Searches for Architecture Decision Records and design documentation.

```text
repo:Aries-Serpent/_codex_ path:docs/arch/ OR path:docs/architecture/
```text
Targets architecture-specific directories.

### Find Prompts & Search Guidance
```text
repo:Aries-Serpent/_codex_ ("prompt" OR "recipes" OR "search") in:file
```text
Locates prompt templates and search documentation.

```text
repo:Aries-Serpent/_codex_ path:docs/prompts/ OR path:PROMPTS/
```text
Searches prompt-specific directories.

### Security & Policy Files
```text
repo:Aries-Serpent/_codex_ (SECURITY OR CODEOWNERS OR "security policy") in:file
```text
Finds security documentation and ownership files.

```text
repo:Aries-Serpent/_codex_ path:docs/security/ OR path:docs/policies/
```text
Targets security and policy directories.

### Python Source Code
```text
repo:Aries-Serpent/_codex_ language:Python path:src/
```text
Searches Python source in the main `src/` directory.

```text
repo:Aries-Serpent/_codex_ language:Python path:src/codex_ml/
```text
Specifically targets the ML core module.

### Configuration Files
```text
repo:Aries-Serpent/_codex_ filename:pyproject.toml OR filename:noxfile.py
```text
Finds project configuration and build files.

```text
repo:Aries-Serpent/_codex_ path:config/ OR path:configs/
```text
Searches configuration directories.

### Test Files
```text
repo:Aries-Serpent/_codex_ path:tests/ language:Python
```text
Locates test files.

```text
repo:Aries-Serpent/_codex_ "def test_" language:Python
```text
Finds test functions across the codebase.

### Scripts & Automation
```text
repo:Aries-Serpent/_codex_ path:scripts/ (language:Python OR language:Shell)
```text
Searches automation scripts.

---

## GitHub CLI Search

### Search Issues
```bash
gh search issues --repo Aries-Serpent/_codex_ --state open
```text
Lists all open issues.

```bash
gh search issues --repo Aries-Serpent/_codex_ --label "bug" --state open
```text
Filters by label.

```bash
gh search issues --repo Aries-Serpent/_codex_ "security" --state all
```text
Searches issues by keyword.

### Search Pull Requests
```bash
gh search prs --repo Aries-Serpent/_codex_ --state open --sort updated --order desc
```text
Lists open PRs sorted by most recently updated.

```bash
gh search prs --repo Aries-Serpent/_codex_ --author "username"
```text
Filters PRs by author.

```bash
gh search prs --repo Aries-Serpent/_codex_ --review required
```text
Finds PRs awaiting review.

### Search Code via CLI
```bash
gh search code --repo Aries-Serpent/_codex_ "FenceState"
```text
Searches for specific symbols or classes.

```bash
gh search code --repo Aries-Serpent/_codex_ --language Python "validate_file"
```text
Searches Python code for a function.

```bash
gh search code --repo Aries-Serpent/_codex_ --path "docs/" "mermaid"
```text
Searches within a specific path.

---

## GraphQL Search with Pagination

Use GitHub's GraphQL API for advanced queries with cursor-based pagination:

```graphql
query SearchRepositoryCode($query: String!, $after: String) {
  search(query: $query, type: CODE, first: 100, after: $after) {
    codeCount
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        ... on Code {
          path
          repository {
            nameWithOwner
          }
          textMatches {
            fragment
          }
        }
      }
    }
  }
}
```text

**Variables:**
```json
{
  "query": "repo:Aries-Serpent/_codex_ language:Python",
  "after": null
}
```text

For subsequent pages, set `after` to the `endCursor` from the previous response.

### Example: Paginated Issue Search
```graphql
query SearchIssues($query: String!, $after: String) {
  search(query: $query, type: ISSUE, first: 100, after: $after) {
    issueCount
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        ... on Issue {
          number
          title
          state
          createdAt
          labels(first: 10) {
            nodes {
              name
            }
          }
        }
      }
    }
  }
}
```text

---

## Finding Specific Artifact Types

### Architecture Decision Records (ADRs)
```text
repo:Aries-Serpent/_codex_ path:docs/decision_records/ filename:*.md
```text

### API Documentation
```text
repo:Aries-Serpent/_codex_ path:docs/api/ OR filename:*api*.md
```text

### Quickstart Guides
```text
repo:Aries-Serpent/_codex_ (quickstart OR "getting started") in:file
```text

### Release Documentation
```text
repo:Aries-Serpent/_codex_ (CHANGELOG OR RELEASE OR "release checklist") filename:*.md
```text

### Docker & Deployment
```text
repo:Aries-Serpent/_codex_ filename:Dockerfile OR filename:docker-compose.yml
```text

```text
repo:Aries-Serpent/_codex_ path:deploy/ OR path:docker/
```text

### CI/CD Workflows
```text
repo:Aries-Serpent/_codex_ path:.github/workflows/ filename:*.yml
```text

### Logging & Monitoring
```text
repo:Aries-Serpent/_codex_ path:src/codex/logging/ OR path:docs/logging/
```text

### ML & Training Modules
```text
repo:Aries-Serpent/_codex_ path:src/codex_ml/ language:Python
```text

```text
repo:Aries-Serpent/_codex_ ("train" OR "model" OR "checkpoint") path:src/
```text

---

## Triage Matrix

**Which query should you run first?** Use this decision tree:

| Your Goal | Recommended Query |
|-----------|------------------|
| **Understand project structure** | `repo:Aries-Serpent/_codex_ path:/ in:path` |
| **Find documentation** | `repo:Aries-Serpent/_codex_ language:Markdown in:file` |
| **Learn architecture** | `repo:Aries-Serpent/_codex_ path:docs/ARCHITECTURE.md` or `path:docs/arch/` |
| **Find code owners** | `repo:Aries-Serpent/_codex_ path:.github/CODEOWNERS` |
| **Report security issue** | `repo:Aries-Serpent/_codex_ filename:SECURITY.md` |
| **Understand how to contribute** | `repo:Aries-Serpent/_codex_ filename:CONTRIBUTING.md` |
| **Find recent issues** | `gh search issues --repo Aries-Serpent/_codex_ --state open --sort updated` |
| **Find recent PRs** | `gh search prs --repo Aries-Serpent/_codex_ --state open --sort updated` |
| **Search for a symbol/function** | `gh search code --repo Aries-Serpent/_codex_ "YourSymbol"` |
| **Find test coverage** | `repo:Aries-Serpent/_codex_ path:tests/` |
| **Understand configuration** | `repo:Aries-Serpent/_codex_ filename:pyproject.toml` or `path:config/` |
| **Find workflows/CI** | `repo:Aries-Serpent/_codex_ path:.github/workflows/` |
| **Learn about releases** | `repo:Aries-Serpent/_codex_ filename:CHANGELOG.md` |
| **Find prompts for automation** | `repo:Aries-Serpent/_codex_ path:PROMPTS/ OR path:docs/prompts/` |

### Search Strategy Flow

1. **Start Broad**: Use repository-level queries to understand structure
2. **Narrow by Path**: Use `path:` filters to focus on specific directories
3. **Filter by Type**: Use `language:` or `extension:` for specific file types
4. **Search Content**: Use `in:file` with keywords for deep content search
5. **Paginate Large Results**: Use GraphQL with cursor pagination for >100 results

### Tips for Effective Searching

- **Combine filters**: `repo:X path:Y language:Z keyword`
- **Use quotes**: For exact phrase matching: `"exact phrase"`
- **Use OR**: `(term1 OR term2 OR term3)` for multiple alternatives
- **Use negation**: `-term` to exclude results
- **Use wildcards**: `filename:test_*.py` for pattern matching
- **Check file extensions**: `extension:md` or `extension:py`

---

## Advanced Patterns

### Find All Configuration Entry Points
```text
repo:Aries-Serpent/_codex_ (pyproject.toml OR setup.py OR setup.cfg OR noxfile.py OR Makefile)
```text

### Find Deprecation Notices
```text
repo:Aries-Serpent/_codex_ ("deprecated" OR "DEPRECATED" OR "TODO: remove") in:file
```text

### Find Security-Sensitive Code
```text
repo:Aries-Serpent/_codex_ ("password" OR "secret" OR "api_key" OR "token") language:Python
```text

### Find Error Handling Patterns
```text
repo:Aries-Serpent/_codex_ "try:" language:Python path:src/
```text

### Find Logging Patterns
```text
repo:Aries-Serpent/_codex_ ("logging.info" OR "logger.error" OR "print(") language:Python
```text

---

## Quick Reference Card

```text
# Structure                  # Documentation              # Code Search
path:/ in:path              language:Markdown           language:Python path:src/
path:.github/               filename:README.md          "def class_name"
path:docs/                  path:docs/arch/             path:tests/

# Issues & PRs               # Security                   # Configuration
is:issue state:open         filename:SECURITY.md        filename:pyproject.toml
is:pr sort:updated-desc     path:docs/security/         path:config/
label:bug                   CODEOWNERS                  filename:*.yml
```text

---

**Last Updated**: 2024-11-02  
**Maintainer**: @Aries-Serpent/docs-team
