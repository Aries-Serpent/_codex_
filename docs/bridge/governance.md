# Bridge Governance & Guardrails

Codex and Copilot share responsibility for safe execution. The bridge centralises policy so that
clients can remain thin and predictable. Use this guide when configuring production or Ubuntu-based
development environments.

## Access control

- **API keys** are short-lived. Generate them with `python services/ita/scripts/issue_api_key.py`.
  Hashes are stored in `services/ita/runtime/api_keys.json`, which is ignored by git.
- **Environment overrides**: set `ITA_API_KEYS_PATH` to relocate the key store or
  `ITA_ADDITIONAL_API_KEYS` when you must honour pre-provisioned credentials (comma separated).
- **GitHub App credentials** live outside the repository. Export `GITHUB_APP_ID`,
  `GITHUB_INSTALLATION_ID`, and `GITHUB_PRIVATE_KEY_PEM` in the shell that runs Codex or Copilot.

## Operational semantics

All write-like endpoints share the same safety semantics:

| Concept | Behaviour |
| --- | --- |
| `dry_run=true` | Simulates side effects. Default for `/git/create-pr`. Responses include a `simulated` flag. |
| `confirm=true` | Required when `dry_run=false`. Prevents accidental writes. Requests without it return **412 Precondition Failed**. |
| `X-Request-Id` | Mandatory header propagated to responses for correlation. Useful for Ubuntu systemd or journald logs. |
| Idempotency | Clients should reuse the same `X-Request-Id` when retrying to ease log inspection. |

## Logging & observability

- The ITA issues structured logs that include the hashed API key, request identifier, and endpoint
  metadata. Forward them to your preferred aggregator on Ubuntu (e.g. `journalctl`, `fluent-bit`).
- Clients should log the `X-Request-Id` they generated so cross-system tracing is trivial.
- Enable `morgan` logging inside the Copilot Express shim (already configured) to audit inbound
  extension calls.

## Threat model touchpoints

The STRIDE snapshot under `ops/threat_model/STRIDE.md` captures the baseline controls. A quick
translation for operators:

- **Spoofing** → Pair short-lived API keys with GitHub App JWTs exchanged for installation tokens.
- **Tampering** → Idempotent write flows plus `confirm` gating keep destructive actions deliberate.
- **Repudiation** → Persist correlation IDs and hashed API keys in audit logs.
- **Information Disclosure** → Keep scopes minimal and redact tokens in logs or telemetry.
- **Denial of Service** → Clients implement exponential backoff; the ITA is ready for rate limiting.
- **Elevation of Privilege** → Hard-code repository/org allowlists before enabling write operations.

For deeper architectural context, read the [bridge overview](overview.md) and keep the knowledge base
entries up to date so Codex can surface the latest operational expectations.

