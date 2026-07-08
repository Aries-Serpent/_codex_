"""Unit tests for the codex.alerting package (Gap 12 — Training Failure Alerting).

Covers:
- AlertEvent dataclass auto-timestamp behaviour
- AlertSeverity ordering
- TrainingAlertManager fan-out and min_severity filtering
- TrainingAlertManager.from_env() env-var reading
- SlackChannel.send() with mocked urllib.request.urlopen
- EmailChannel.send() with mocked smtplib.SMTP
- Graceful degradation — alerting failures never propagate
"""

# pragma: allowlist secret
from __future__ import annotations

import os
import smtplib
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from codex.alerting import AlertChannel, AlertEvent, AlertSeverity, TrainingAlertManager
from codex.alerting.email import EmailChannel
from codex.alerting.slack import SlackChannel

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeChannel(AlertChannel):
    """In-memory channel for testing."""

    def __init__(self, channel_name: str = "fake", succeed: bool = True) -> None:
        self._name = channel_name
        self._succeed = succeed
        self.received: list[AlertEvent] = []

    def name(self) -> str:
        return self._name

    def send(self, event: AlertEvent) -> bool:
        self.received.append(event)
        return self._succeed


class _RaisingChannel(AlertChannel):
    """Channel that raises unconditionally — tests graceful degradation."""

    def name(self) -> str:
        return "raising"

    def send(self, event: AlertEvent) -> bool:
        raise RuntimeError("channel is broken")


# ---------------------------------------------------------------------------
# AlertSeverity
# ---------------------------------------------------------------------------


class TestAlertSeverity:
    def test_values(self) -> None:
        assert AlertSeverity.INFO.value == "info", "Value must be initialized"
        assert AlertSeverity.WARNING.value == "warning", "Value must be initialized"
        assert AlertSeverity.ERROR.value == "error", "Value must be initialized"
        assert AlertSeverity.CRITICAL.value == "critical", "Value must be initialized"

    def test_ordering_lt(self) -> None:
        assert AlertSeverity.INFO < AlertSeverity.WARNING, "INFO is not valid"
        assert AlertSeverity.WARNING < AlertSeverity.ERROR, "Error should be raised or set"
        assert AlertSeverity.ERROR < AlertSeverity.CRITICAL, "Error should be raised or set"

    def test_ordering_ge(self) -> None:
        assert AlertSeverity.CRITICAL >= AlertSeverity.ERROR, "CRITICAL must be greater than zero"
        assert AlertSeverity.ERROR >= AlertSeverity.WARNING, "ERROR must be greater than zero"

    def test_ordering_gt(self) -> None:
        assert AlertSeverity.CRITICAL > AlertSeverity.WARNING, "CRITICAL must be greater than zero"

    def test_str_value(self) -> None:
        # AlertSeverity extends str
        assert str(AlertSeverity.INFO) == "info", "Condition must be true"


# ---------------------------------------------------------------------------
# AlertEvent
# ---------------------------------------------------------------------------


class TestAlertEvent:
    def test_defaults(self) -> None:
        event = AlertEvent(title="t", message="m", severity=AlertSeverity.INFO)
        assert event.run_id == "", "run_id is not valid"
        assert event.epoch == 0, "epoch is not valid"
        assert event.metadata == {}, "Data must not be empty"
        assert event.timestamp == "", "timestamp is not valid"

    def test_fill_timestamp_fills_when_empty(self) -> None:
        event = AlertEvent(title="t", message="m", severity=AlertSeverity.INFO)
        event.fill_timestamp()
        assert event.timestamp != "", "timestamp is not valid"
        # Must match YYYY-MM-DDTHH:MM:SSZ — not isoformat() with +00:00
        assert event.timestamp.endswith("Z"), "Condition must be true"
        assert "T" in event.timestamp, "Condition must be true"
        assert "+" not in event.timestamp, "Condition must be true"

    def test_fill_timestamp_does_not_overwrite(self) -> None:
        ts = "2024-01-01T00:00:00Z"
        event = AlertEvent(title="t", message="m", severity=AlertSeverity.INFO, timestamp=ts)
        event.fill_timestamp()
        assert event.timestamp == ts, "timestamp is not valid"

    def test_metadata_isolation(self) -> None:
        meta: dict[str, Any] = {"k": "v"}
        event = AlertEvent(title="t", message="m", severity=AlertSeverity.INFO, metadata=meta)
        meta["extra"] = "x"
        # The stored dict is the same reference — mutation is the caller's responsibility
        assert "extra" in event.metadata, "Data must not be empty"


# ---------------------------------------------------------------------------
# TrainingAlertManager
# ---------------------------------------------------------------------------


class TestTrainingAlertManager:
    def test_dispatches_to_all_channels(self) -> None:
        ch1 = _FakeChannel("ch1")
        ch2 = _FakeChannel("ch2")
        mgr = TrainingAlertManager(channels=[ch1, ch2], min_severity=AlertSeverity.INFO)
        event = AlertEvent(title="t", message="m", severity=AlertSeverity.INFO)
        results = mgr.alert(event)
        assert results == {"ch1": True, "ch2": True}
        assert len(ch1.received) == 1, "Collection must not be empty"
        assert len(ch2.received) == 1, "Collection must not be empty"

    def test_min_severity_filtering(self) -> None:
        ch = _FakeChannel()
        mgr = TrainingAlertManager(channels=[ch], min_severity=AlertSeverity.ERROR)
        # INFO and WARNING should be dropped
        mgr.alert(AlertEvent(title="t", message="m", severity=AlertSeverity.INFO))
        mgr.alert(AlertEvent(title="t", message="m", severity=AlertSeverity.WARNING))
        assert len(ch.received) == 0, "Collection must not be empty"
        # ERROR and CRITICAL should pass
        mgr.alert(AlertEvent(title="t", message="m", severity=AlertSeverity.ERROR))
        mgr.alert(AlertEvent(title="t", message="m", severity=AlertSeverity.CRITICAL))
        assert len(ch.received) == 2, "Collection must not be empty"

    def test_auto_fills_timestamp(self) -> None:
        ch = _FakeChannel()
        mgr = TrainingAlertManager(channels=[ch], min_severity=AlertSeverity.INFO)
        event = AlertEvent(title="t", message="m", severity=AlertSeverity.INFO)
        mgr.alert(event)
        assert ch.received[0].timestamp != "", "timestamp is not valid"

    def test_alert_training_failure(self) -> None:
        ch = _FakeChannel()
        mgr = TrainingAlertManager(channels=[ch], min_severity=AlertSeverity.CRITICAL)
        exc = ValueError("NaN loss")
        results = mgr.alert_training_failure(exc, run_id="run-1", epoch=3, lr=0.001)
        assert results == {"fake": True}, "Result must not be empty"
        sent = ch.received[0]
        assert sent.severity == AlertSeverity.CRITICAL, "severity is not valid"
        assert "ValueError" in sent.message, "Value must be initialized"
        assert "NaN loss" in sent.message, "Condition must be true"
        assert sent.run_id == "run-1", "run_id is not valid"
        assert sent.epoch == 3, "epoch is not valid"
        assert sent.metadata["lr"] == 0.001, "Data must not be empty"

    def test_alert_training_complete(self) -> None:
        ch = _FakeChannel()
        # INFO events only reach channels when min_severity is INFO
        mgr = TrainingAlertManager(channels=[ch], min_severity=AlertSeverity.INFO)
        results = mgr.alert_training_complete(run_id="run-2", epochs=10, final_loss=0.123)
        assert results == {"fake": True}, "Result must not be empty"
        sent = ch.received[0]
        assert sent.severity == AlertSeverity.INFO, "severity is not valid"
        assert "10" in sent.message, "Condition must be true"
        assert "0.123000" in sent.message, "Condition must be true"
        assert sent.run_id == "run-2", "run_id is not valid"

    def test_channel_failure_recorded_not_raised(self) -> None:
        failing = _FakeChannel("failing", succeed=False)
        mgr = TrainingAlertManager(channels=[failing], min_severity=AlertSeverity.INFO)
        results = mgr.alert(AlertEvent(title="t", message="m", severity=AlertSeverity.INFO))
        assert results == {"failing": False}, "Result must not be empty"

    def test_channel_exception_does_not_propagate(self) -> None:
        raising = _RaisingChannel()
        mgr = TrainingAlertManager(channels=[raising], min_severity=AlertSeverity.INFO)
        # Must NOT raise
        results = mgr.alert(AlertEvent(title="t", message="m", severity=AlertSeverity.INFO))
        assert results == {"raising": False}, "Result must not be empty"

    def test_empty_channels_returns_empty_dict(self) -> None:
        mgr = TrainingAlertManager(channels=[], min_severity=AlertSeverity.INFO)
        results = mgr.alert(AlertEvent(title="t", message="m", severity=AlertSeverity.INFO))
        assert results == {}, "Result must not be empty"


# ---------------------------------------------------------------------------
# TrainingAlertManager.from_env()
# ---------------------------------------------------------------------------


class TestFromEnv:
    def test_no_env_vars_yields_empty_channels(self) -> None:
        clean_env = {
            k: v
            for k, v in os.environ.items()
            if k
            not in {
                "CODEX_SLACK_WEBHOOK_URL",
                "CODEX_ALERT_SMTP_HOST",
                "CODEX_ALERT_TO",
                "CODEX_ALERT_MIN_SEVERITY",
            }
        }
        with patch.dict(os.environ, clean_env, clear=True):
            mgr = TrainingAlertManager.from_env()
        assert mgr._channels == [], "_channels is not valid"

    def test_slack_env_var_adds_slack_channel(self) -> None:
        env = {"CODEX_SLACK_WEBHOOK_URL": "https://hooks.slack.com/test"}
        with patch.dict(os.environ, env, clear=True):
            mgr = TrainingAlertManager.from_env()
        assert any(c.name() == "slack" for c in mgr._channels), "Condition must be true"

    def test_email_env_vars_add_email_channel(self) -> None:
        env = {
            "CODEX_ALERT_SMTP_HOST": "smtp.example.com",
            "CODEX_ALERT_TO": "ops@example.com",
            "CODEX_ALERT_FROM": "noreply@example.com",
        }
        with patch.dict(os.environ, env, clear=True):
            mgr = TrainingAlertManager.from_env()
        assert any(c.name() == "email" for c in mgr._channels), "Condition must be true"

    def test_min_severity_env_var(self) -> None:
        env = {"CODEX_ALERT_MIN_SEVERITY": "warning"}
        with patch.dict(os.environ, env, clear=True):
            mgr = TrainingAlertManager.from_env()
        assert mgr._min_severity == AlertSeverity.WARNING, "_min_severity is not valid"

    def test_invalid_min_severity_defaults_to_error(self) -> None:
        env = {"CODEX_ALERT_MIN_SEVERITY": "bogus"}
        with patch.dict(os.environ, env, clear=True):
            mgr = TrainingAlertManager.from_env()
        assert mgr._min_severity == AlertSeverity.ERROR, "Error should be raised or set"


# ---------------------------------------------------------------------------
# SlackChannel
# ---------------------------------------------------------------------------


class TestSlackChannel:
    def _make_event(self, severity: AlertSeverity = AlertSeverity.CRITICAL) -> AlertEvent:
        return AlertEvent(
            title="Training failed",
            message="NaN loss at step 100",
            severity=severity,
            run_id="run-42",
            epoch=5,
            timestamp="2024-06-01T12:00:00Z",
            metadata={"lr": "0.001"},
        )

    def test_send_posts_json_payload(self) -> None:
        fake_resp = MagicMock()
        fake_resp.getcode.return_value = 200
        fake_resp.__enter__ = lambda s: s
        fake_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=fake_resp) as mock_open:
            ch = SlackChannel(webhook_url="https://hooks.slack.com/services/test")
            result = ch.send(self._make_event())

        assert result is True, "Result must not be empty"
        mock_open.assert_called_once()
        req = mock_open.call_args[0][0]
        import json as _json

        payload = _json.loads(req.data.decode())
        assert "Training failed" in payload["text"], "Condition must be true"
        field_titles = [f["title"] for f in payload["attachments"][0]["fields"]]
        assert "Severity" in field_titles, "Condition must be true"
        assert "Run ID" in field_titles, "Condition must be true"
        assert "Epoch" in field_titles, "Condition must be true"
        assert "lr" in field_titles, "Condition must be true"

    def test_send_returns_false_on_url_error(self) -> None:
        import urllib.error

        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            ch = SlackChannel(webhook_url="https://hooks.slack.com/services/test")
            assert ch.send(self._make_event()) is False, "Condition must be true"

    def test_send_returns_false_when_no_url(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            ch = SlackChannel()
            assert ch.send(self._make_event()) is False, "Condition must be true"

    def test_send_returns_false_on_non_200(self) -> None:
        fake_resp = MagicMock()
        fake_resp.getcode.return_value = 400
        fake_resp.__enter__ = lambda s: s
        fake_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=fake_resp):
            ch = SlackChannel(webhook_url="https://hooks.slack.com/services/test")
            assert ch.send(self._make_event()) is False, "Condition must be true"

    def test_send_returns_false_on_disallowed_webhook_host(self) -> None:
        ch = SlackChannel(webhook_url="https://example.com/not-slack")
        assert ch.send(self._make_event()) is False, "Condition must be true"

    def test_send_returns_false_on_disallowed_webhook_path(self) -> None:
        ch = SlackChannel(webhook_url="https://hooks.slack.com/not-a-webhook")
        assert ch.send(self._make_event()) is False, "Condition must be true"

    @pytest.mark.parametrize(
        "severity,expected_color",
        [
            (AlertSeverity.INFO, "#36a64f"),
            (AlertSeverity.WARNING, "#ffcc00"),
            (AlertSeverity.ERROR, "#e01e5a"),
            (AlertSeverity.CRITICAL, "#c0392b"),
        ],
    )
    def test_colour_mapping(self, severity: AlertSeverity, expected_color: str) -> None:
        ch = SlackChannel(webhook_url="https://hooks.slack.com/services/test")
        payload = ch._build_payload(self._make_event(severity))
        assert payload["attachments"][0]["color"] == expected_color, "Condition must be true"

    def test_reads_webhook_from_env(self) -> None:
        with patch.dict(
            os.environ, {"CODEX_SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/env"}
        ):
            ch = SlackChannel()
        assert ch._webhook_url == "https://hooks.slack.com/services/env", "_webhook_url is not valid"


# ---------------------------------------------------------------------------
# EmailChannel
# ---------------------------------------------------------------------------


class TestEmailChannel:
    def _make_channel(self) -> EmailChannel:
        return EmailChannel(
            smtp_host="smtp.example.com",
            smtp_port=587,
            from_addr="noreply@example.com",
            to_addrs=["ops@example.com"],
        )

    def _make_event(self) -> AlertEvent:
        return AlertEvent(
            title="Training complete",
            message="Finished 10 epochs",
            severity=AlertSeverity.INFO,
            run_id="run-99",
            epoch=10,
            timestamp="2024-06-01T12:00:00Z",
        )

    def test_send_uses_starttls_for_port_587(self) -> None:
        mock_smtp = MagicMock()
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_smtp_instance)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
        # smtplib.SMTP is used as a context manager in the implementation
        with patch("smtplib.SMTP", return_value=mock_smtp.return_value) as mock_cls:
            ch = self._make_channel()
            result = ch.send(self._make_event())

        assert result is True, "Result must not be empty"
        mock_cls.assert_called_once_with("smtp.example.com", 587, timeout=10)
        # STARTTLS path calls ehlo twice + starttls
        mock_smtp.return_value.ehlo.assert_called()
        mock_smtp.return_value.starttls.assert_called_once()

    def test_send_verifies_message_fields(self) -> None:
        captured_messages: list[Any] = []

        def _fake_sendmail(from_: str, to_: list[str], msg_str: str) -> None:
            captured_messages.append((from_, to_, msg_str))

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = lambda s: s
        mock_smtp.__exit__ = MagicMock(return_value=False)
        mock_smtp.sendmail = _fake_sendmail

        with patch("smtplib.SMTP", return_value=mock_smtp):
            ch = self._make_channel()
            ch.send(self._make_event())

        assert len(captured_messages) == 1, "Captured_messages must not be empty"
        from_addr, to_addrs, raw_msg = captured_messages[0]
        assert from_addr == "noreply@example.com", "from_addr is not valid"
        assert "ops@example.com" in to_addrs, "Condition must be true"
        # The subject is always plaintext in the headers
        assert "[INFO]" in raw_msg, "Condition must be true"
        assert "Training complete" in raw_msg, "Condition must be true"
        # Body may be base64-encoded — decode and inspect
        import base64 as _b64
        import email as _email_lib

        parsed = _email_lib.message_from_string(raw_msg)
        payload = parsed.get_payload()
        if parsed.get("Content-Transfer-Encoding") == "base64":
            body = _b64.b64decode(payload.replace("\n", "")).decode("utf-8")
        else:
            body = payload
        assert "run-99" in body, "Condition must be true"

    def test_send_returns_false_on_smtp_exception(self) -> None:
        with patch("smtplib.SMTP", side_effect=smtplib.SMTPException("connect failed")):
            ch = self._make_channel()
            assert ch.send(self._make_event()) is False, "Condition must be true"

    def test_send_returns_false_on_os_error(self) -> None:
        with patch("smtplib.SMTP", side_effect=OSError("network unreachable")):
            ch = self._make_channel()
            assert ch.send(self._make_event()) is False, "Condition must be true"

    def test_send_returns_false_when_no_host(self) -> None:
        ch = EmailChannel(
            smtp_host="",
            smtp_port=587,
            from_addr="noreply@example.com",
            to_addrs=["ops@example.com"],
        )
        assert ch.send(self._make_event()) is False, "Condition must be true"

    def test_send_returns_false_when_no_to_addrs(self) -> None:
        ch = EmailChannel(
            smtp_host="smtp.example.com",
            smtp_port=587,
            from_addr="noreply@example.com",
            to_addrs=[],
        )
        assert ch.send(self._make_event()) is False, "Condition must be true"

    def test_from_env_reads_env_vars(self) -> None:
        env = {
            "CODEX_ALERT_SMTP_HOST": "smtp.test.com",
            "CODEX_ALERT_SMTP_PORT": "465",
            "CODEX_ALERT_FROM": "from@test.com",
            "CODEX_ALERT_TO": "a@test.com, b@test.com",
            "CODEX_ALERT_SMTP_USER": "user",
            "CODEX_ALERT_SMTP_PASS": "s3cr3t",
        }
        with patch.dict(os.environ, env, clear=True):
            ch = EmailChannel.from_env()
        assert ch._smtp_host == "smtp.test.com", "_smtp_host is not valid"
        assert ch._smtp_port == 465  # pragma: allowlist secret
        assert ch._from_addr == "from@test.com", "_from_addr is not valid"
        assert ch._to_addrs == ["a@test.com", "b@test.com"]
        assert ch._username == "user", "_username is not valid"
        assert ch._password == "s3cr3t"  # pragma: allowlist secret

    def test_from_env_defaults_port_to_587(self) -> None:
        env = {
            "CODEX_ALERT_SMTP_HOST": "smtp.test.com",
            "CODEX_ALERT_TO": "ops@test.com",
            "CODEX_ALERT_FROM": "noreply@test.com",
        }
        with patch.dict(os.environ, env, clear=True):
            ch = EmailChannel.from_env()
        assert ch._smtp_port == 587, "_smtp_port is not valid"

    def test_from_env_invalid_port_defaults_to_587(self) -> None:
        env = {
            "CODEX_ALERT_SMTP_HOST": "smtp.test.com",
            "CODEX_ALERT_SMTP_PORT": "not-a-number",
            "CODEX_ALERT_TO": "ops@test.com",
            "CODEX_ALERT_FROM": "noreply@test.com",
        }
        with patch.dict(os.environ, env, clear=True):
            ch = EmailChannel.from_env()
        assert ch._smtp_port == 587, "_smtp_port is not valid"


# ---------------------------------------------------------------------------
# Graceful degradation — alerting failure must not crash training
# ---------------------------------------------------------------------------


class TestGracefulDegradation:
    def test_manager_with_raising_channel_does_not_raise(self) -> None:
        raising = _RaisingChannel()
        mgr = TrainingAlertManager(channels=[raising], min_severity=AlertSeverity.INFO)
        # Should not raise
        results = mgr.alert(AlertEvent(title="t", message="m", severity=AlertSeverity.INFO))
        assert results["raising"] is False, "Result must not be empty"

    def test_alert_training_failure_does_not_raise_on_bad_channel(self) -> None:
        raising = _RaisingChannel()
        mgr = TrainingAlertManager(channels=[raising], min_severity=AlertSeverity.CRITICAL)
        exc = RuntimeError("GPU OOM")
        # Must NOT re-raise
        results = mgr.alert_training_failure(exc, run_id="test", epoch=1)
        assert results["raising"] is False, "Result must not be empty"

    def test_slack_channel_does_not_raise_on_url_error(self) -> None:
        import urllib.error

        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("timeout"),
        ):
            ch = SlackChannel(webhook_url="https://hooks.slack.com/services/test")
            result = ch.send(AlertEvent(title="t", message="m", severity=AlertSeverity.ERROR))
        assert result is False, "Result must not be empty"

    def test_email_channel_does_not_raise_on_smtp_error(self) -> None:
        with patch(
            "smtplib.SMTP", side_effect=smtplib.SMTPConnectError(421, "Service unavailable")
        ):
            ch = EmailChannel(
                smtp_host="smtp.bad.com",
                smtp_port=587,
                from_addr="noreply@example.com",
                to_addrs=["ops@example.com"],
            )
            result = ch.send(AlertEvent(title="t", message="m", severity=AlertSeverity.ERROR))
        assert result is False, "Result must not be empty"
