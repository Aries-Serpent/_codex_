# Session Tracking & Event Correlation

Codex ML records every training, inference, and CLI invocation with a unique session identifier. Session-aware
logging enables reproducible experiments and simplifies incident reconstruction.

## Session identifiers

Specify a session explicitly or allow Codex to generate one automatically:

```bash
export CODEX_SESSION_ID=$(uuidgen)
python -m codex_ml.cli.train --config-name default
```

When unset, `codex_ml.codex_structured_logging` creates a UUIDv4 and stores it in `.codex/logs/session_<ID>.jsonl`.
The `SessionLogger` applies secret redaction before persisting events so API keys and tokens never reach disk.

## Event schema

Each line in `.codex/logs/session_<SESSION_ID>.jsonl` contains a JSON record with the following structure:

```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "system|user|assistant|tool",
  "event_type": "training_start|training_end|inference_request|error",
  "data": {
    "key": "value"
  }
}
```

The training loop logs `training_start` and `training_end` events automatically, including epoch counts,
optimizer steps, and wall-clock durations. Calls to `codex_structured_logging.log_event` propagate to the
session log transparently, so CLI utilities inherit the same correlation identifiers.

## Querying sessions

Use standard CLI tools to inspect and filter session histories:

```bash
# Show all events for a session
jq '.session_id == "550e8400-e29b-41d4-a716-446655440000"' .codex/logs/session_*.jsonl

# Sort the session timeline by timestamp
jq -s 'sort_by(.timestamp)' .codex/logs/session_550e8400-e29b-41d4-a716-446655440000.jsonl
```

## SQLite metrics mirroring

When the NDJSON `SessionLogger` records events that include a `metrics` payload
and an `epoch` counter, the values are mirrored into `.codex/session_logs.db`
(`metric_records` table). Each row captures the session id, event type, epoch,
metric name, and scalar value, making it trivial to aggregate training runs with
SQL queries:

```sql
SELECT epoch, metric, AVG(value) AS avg_value
FROM metric_records
WHERE metric IN ('loss', 'acc')
GROUP BY epoch, metric
ORDER BY epoch;
```

The database schema is managed by `codex.logging.db_manager.DBManager` and is
initialized automatically when `codex_ml.logging.session_logger.SessionLogger`
is constructed (mirroring is best effort and never blocks training).

## Integrating with other systems

* Forward the NDJSON files to log aggregation pipelines (e.g. Loki, Elastic) for centralised dashboards.
* Annotate CI jobs with a session ID to correlate build logs with Codex telemetry.
* When running notebooks, set `CODEX_SESSION_LOG_DIR` to isolate the outputs per experiment.
