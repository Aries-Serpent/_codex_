# Gap 12 — Training Failure Alerting

**Priority:** P1 High  
**Status:** ✅ Implemented  
**Implementation date:** 2025-07-14

---

## Summary

Implemented a lightweight, zero-external-dependency alerting system for the
Codex training pipeline.  The package lives at `src/codex/alerting/` and
provides Slack-webhook and SMTP-email notification channels wired into the
main `run_training()` function.

---

## Files Created / Modified

### New files

| File | Purpose |
|------|---------|
| `src/codex/alerting/__init__.py` | Package public API — exports `TrainingAlertManager`, `AlertChannel`, `AlertSeverity`, `AlertEvent` |
| `src/codex/alerting/base.py` | Abstract base: `AlertSeverity` (StrEnum), `AlertEvent` dataclass, `AlertChannel` ABC |
| `src/codex/alerting/slack.py` | `SlackChannel` — posts to Slack incoming webhooks via `urllib.request` (no new deps) |
| `src/codex/alerting/email.py` | `EmailChannel` — sends via `smtplib` + `email.mime`; STARTTLS for port 587 |
| `src/codex/alerting/manager.py` | `TrainingAlertManager` — fan-out dispatcher with `from_env()` factory |
| `tests/unit/test_alerting.py` | 44-test suite covering all public surface areas |
| `workbench/evidence/gap12_training_alerts.md` | This file |

### Modified files

| File | Change |
|------|--------|
| `src/codex_ml/train_loop.py` | Added lazy import of `TrainingAlertManager`; wrapped epoch `for` loop in `try/except` to emit failure alerts; added completion alert before final `return` |

---

## Design Decisions

### Zero new dependencies
All I/O uses stdlib modules only (`urllib.request`, `smtplib`, `email.mime`).
No `requests`, `httpx`, or other third-party packages were introduced.

### Graceful degradation
Every alert call is wrapped in `try/except Exception` with `logger.debug`.
Alerting failures **never** crash or interrupt training.

### Severity filtering
`TrainingAlertManager(min_severity=...)` silently drops events below the
threshold, making it easy to suppress `INFO`-level completion messages in
production without changing code.

### StrEnum for AlertSeverity
Python 3.12 `StrEnum` ensures `str(AlertSeverity.INFO) == "info"`, enabling
safe use in f-strings, JSON payloads, and comparisons.

### UTC timestamp convention
`AlertEvent.fill_timestamp()` uses
`datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")` per repository convention
(never `.isoformat()` which appends `+00:00`).

---

## Environment Variables

### Slack
| Variable | Description |
|----------|-------------|
| `CODEX_SLACK_WEBHOOK_URL` | Slack incoming webhook URL |

### Email (SMTP)
| Variable | Description |
|----------|-------------|
| `CODEX_ALERT_SMTP_HOST` | SMTP hostname |
| `CODEX_ALERT_SMTP_PORT` | SMTP port (default 587 → STARTTLS) |
| `CODEX_ALERT_FROM` | Sender address |
| `CODEX_ALERT_TO` | Comma-separated recipient addresses |
| `CODEX_ALERT_SMTP_USER` | Optional SMTP login username |
| `CODEX_ALERT_SMTP_PASS` | Optional SMTP login credential |

### General
| Variable | Description |
|----------|-------------|
| `CODEX_ALERT_MIN_SEVERITY` | Minimum severity to dispatch (`info`/`warning`/`error`/`critical`; default `error`) |

---

## Usage

### Auto-configure from environment (recommended)

```python
from codex.alerting import TrainingAlertManager

manager = TrainingAlertManager.from_env()
try:
    result = run_training(epochs=10, ...)
    manager.alert_training_complete(
        run_id="run-abc", epochs=10, final_loss=result["final_loss"]
    )
except Exception as exc:
    manager.alert_training_failure(exc, run_id="run-abc", epoch=5)
    raise
```

### Manual channel configuration

```python
from codex.alerting import TrainingAlertManager, AlertSeverity
from codex.alerting.slack import SlackChannel
from codex.alerting.email import EmailChannel

manager = TrainingAlertManager(
    channels=[
        SlackChannel(webhook_url="https://hooks.slack.com/..."),
        EmailChannel(
            smtp_host="smtp.example.com",
            smtp_port=587,
            from_addr="noreply@example.com",
            to_addrs=["ops@example.com"],
        ),
    ],
    min_severity=AlertSeverity.ERROR,
)
```

---

## Test Results

```
collected 44 items

tests/unit/test_alerting.py ....................................................
44 passed in 2.93s
```

### Test coverage breakdown

| Test class | Cases |
|-----------|-------|
| `TestAlertSeverity` | Enum values, ordering, str representation |
| `TestAlertEvent` | Defaults, auto-timestamp, timestamp preservation |
| `TestTrainingAlertManager` | Fan-out, severity filtering, auto-timestamp, failure/complete helpers, channel errors |
| `TestFromEnv` | No-op with no env vars, Slack/email activation, min-severity override, invalid severity fallback |
| `TestSlackChannel` | JSON payload structure, HTTP 200/non-200, URLError, no-URL guard, colour mapping, env-var reading |
| `TestEmailChannel` | STARTTLS flow, message field verification, SMTP/OS errors, no-host/no-to guards, `from_env()`, invalid port |
| `TestGracefulDegradation` | Raising channel doesn't propagate, failure alert safe, Slack URLError safe, email SMTPError safe |

---

## Gap 13 Readiness

This implementation provides the alerting infrastructure that Gap 13 (performance
degradation alerts) depends on.  Gap 13 can extend `TrainingAlertManager` with
additional `alert_performance_degradation()` helpers using the same channel
infrastructure.
