# Auditing search providers

This guide documents how to configure the optional external search provider
used by the Codex ML auditing pipeline. The internal ripgrep-based provider is
always available, while the external provider is disabled by default to honour
offline policies.

## External web search

`ExternalWebSearch` augments the audit evidence gathering step with results from
an HTTP API. The provider defaults to the DuckDuckGo Instant Answer endpoint
when enabled, but it can also consume a local JSON index for fully offline
runs. In all modes the implementation fails closed and never performs network
traffic unless explicitly configured to do so.

### Environment variables

Set the following variables to enable the provider:

| Variable | Purpose | Default |
| --- | --- | --- |
| `CODEX_ANALYSIS_SEARCH_ENABLED` | Toggle the provider (`1` or `true` enables it). | Disabled (`0`). |
| `CODEX_ANALYSIS_SEARCH_ENDPOINT` | Base URL or `file://` path for the search endpoint. | DuckDuckGo Instant Answer API. |
| `CODEX_ANALYSIS_SEARCH_TIMEOUT` | Request timeout in seconds. | `5.0`. |

All values are read on instantiation. Invalid booleans fall back to the default
(`disabled`) and invalid timeouts revert to `5.0` seconds. When pointing to a
local index, provide either an absolute `file:///path/index.json` URI or a path
relative to the current working directory. The JSON payload can be either a
list of result dictionaries or a mapping from queries to lists of results.

### CLI overrides

`python -m codex_ml.cli.audit_pipeline` accepts additional flags to control the
provider without editing code:

- `--external-search` / `--no-external-search` – force enable or disable the
  provider (default is environment driven).
- `--external-search-endpoint` – override the endpoint/JSON index for the
  current run.
- `--external-search-timeout` – override the HTTP timeout in seconds.

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
  When an offline index is missing or unreadable the provider also returns an
  `"error"` with a descriptive `reason`.

The audit pipeline records successful results as evidence and logs non-`ok`
statuses in the same evidence list for traceability. This keeps CI runs
deterministic: in offline environments the provider reliably reports
`disabled` or `unavailable` without delaying the audit.
