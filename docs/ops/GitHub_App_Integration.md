# GitHub App Integration Helpers

## GitHub API wrapper (App token or PAT)
The wrapper emits a sanitized curl for review or performs the request:

```bash
# Redacted curl (no network)
GH_TOKEN=xxxxx python tools/github/gh_api.py \
  --method GET \
  --path /repos/Aries-Serpent/_codex_/branches \
  --param per_page=100 \
  --paginate \
  --print-curl

# Actual call (prints JSON to stdout)
GH_TOKEN=$INSTALLATION_TOKEN python tools/github/gh_api.py \
  --method GET \
  --path /repos/Aries-Serpent/_codex_/branches \
  --param per_page=100 \
  --paginate \
  --cache-dir .gh_cache
```

## Caching
- Enable cache with `--cache-dir .gh_cache` (or set `GH_API_CACHE_DIR`).
- Serve from cache only with `--use-cache-only` (no network attempt).
- Force a re-fetch with `--refresh-cache`.

## Pagination
- Use `--paginate` to follow `Link: ... rel="next"` until exhausted.
- Control page size with `--per-page 100` and bound traversal with `--max-pages`.
