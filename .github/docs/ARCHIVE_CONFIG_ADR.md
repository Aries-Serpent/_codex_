# ADR: Archive Configuration System

## Status

Accepted – 2024-05-07

## Context

Operational workflows for the Codex archive previously relied on ad-hoc
environment variables. The lack of an explicit configuration contract made it
difficult to reason about deployment changes, replicate production settings, or
introduce new features (retry policies, structured logging, batch operations).

## Decision

Introduce a typed configuration layer (`codex.archive.config`) that combines:

* **Default values** suitable for local development.
* **Environment variable overrides** (prefixed with `CODEX_ARCHIVE_`).
* **Optional TOML configuration** (`.codex/archive.toml`).

The composed object exposes five sections:

| Section      | Dataclass              | Purpose                                    |
|--------------|------------------------|--------------------------------------------|
| `backend`    | `BackendConfig`        | Connection URL & backend flavour           |
| `logging`    | `LoggingConfig`        | Level, format, optional evidence override  |
| `retry`      | `RetrySettings`        | Exponential backoff parameters             |
| `batch`      | `BatchConfig`          | Batch execution tuning                     |
| `performance`| `PerformanceConfig`    | Toggle metrics emission                    |

The CLI loads the configuration on demand and converts the backend section into
the legacy `ArchiveConfig` so existing services continue to work.

## Consequences

* Configuration can be committed as TOML and overridden during deployment.
* Tests can synthesise configurations without mutating global state.
* New subsystems (logging, retry, performance) obtain strongly-typed settings.

## Alternatives Considered

* **Hydra/OmegaConf** – powerful but unnecessary for the current surface area.
* **Keep environment-only configuration** – rejected to avoid repetition and
  improve validation.

## Follow-up

* Document additional backends (e.g. cloud object stores) as they are
  implemented.
* Consider surfacing configuration via `codex archive config-show` in the CLI
  (implemented alongside this ADR).
