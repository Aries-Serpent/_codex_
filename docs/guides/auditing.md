# Auditing search providers

This guide documents how to configure the optional external search provider
used by the Codex ML auditing pipeline. The internal ripgrep-based provider is
always available, while the external provider is disabled by default to honour
offline policies.

## External web search

`ExternalWebSearch` augments the audit evidence gathering step with results from
an HTTP API. The provider is safe to leave enabled in development environments
and falls back to deterministic no-op responses when configuration is missing.

### Environment variables

Set the following variables to enable the provider:

| Variable | Purpose | Default |
| --- | --- | --- |
| `CODEX_ANALYSIS_SEARCH_ENABLED` | Toggle the provider (`1` or `true` enables it). | Disabled (`0`). |
| `CODEX_ANALYSIS_SEARCH_ENDPOINT` | Base URL for the HTTP search endpoint. | Empty, treated as unavailable. |
| `CODEX_ANALYSIS_SEARCH_TIMEOUT` | Request timeout in seconds. | `5.0`. |

All values are read on instantiation. Invalid booleans fall back to the default
(`disabled`) and invalid timeouts revert to `5.0` seconds.

### Behaviour and responses

The provider always returns a structured payload:

```json
{
  "provider": "external_web",
  "query": "python",
  "status": "ok",
  "results": [
    {"title": "Python", "url": "https://example.com", "snippet": "..."}
  ]
}
```

- When disabled, the status is `"disabled"` and the result list is empty.
- If no endpoint is configured or the `requests` dependency is unavailable, the
  status becomes `"unavailable"` with a `reason` field describing the blocker.
- Network or HTTP errors are captured as `"error"` responses with a stringified
  message and optional `status_code`.

The audit pipeline records successful results as evidence and logs non-`ok`
statuses in the same evidence list for traceability. This makes CI runs
deterministic: in offline environments the provider reliably reports
`unavailable` without delaying the audit.
