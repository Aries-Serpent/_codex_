"""
Comprehensive tests for codex.alerting.base module.

Tests cover AlertSeverity enum, AlertEvent dataclass, and AlertChannel ABC.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from codex.alerting.base import AlertChannel, AlertEvent, AlertSeverity


class TestAlertSeverity:
    """Test AlertSeverity enum and comparison operations."""

    def test_alert_severity_values(self):
        """Test AlertSeverity enum has correct values."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"

    def test_alert_severity_is_str_enum(self):
        """Test that AlertSeverity values are strings."""
        for severity in AlertSeverity:
            assert isinstance(severity.value, str)

    def test_alert_severity_ordering(self):
        """Test AlertSeverity order from least to most severe."""
        severity_list = list(AlertSeverity)
        assert severity_list[0] == AlertSeverity.INFO
        assert severity_list[1] == AlertSeverity.WARNING
        assert severity_list[2] == AlertSeverity.ERROR
        assert severity_list[3] == AlertSeverity.CRITICAL

    def test_alert_severity_less_than(self):
        """Test less than comparison operator."""
        assert AlertSeverity.INFO < AlertSeverity.WARNING
        assert AlertSeverity.WARNING < AlertSeverity.ERROR
        assert AlertSeverity.ERROR < AlertSeverity.CRITICAL

    def test_alert_severity_less_than_same(self):
        """Test less than returns False for same severity."""
        assert not (AlertSeverity.INFO < AlertSeverity.INFO)
        assert not (AlertSeverity.CRITICAL < AlertSeverity.CRITICAL)

    def test_alert_severity_less_than_greater(self):
        """Test less than returns False when first is greater."""
        assert not (AlertSeverity.CRITICAL < AlertSeverity.INFO)
        assert not (AlertSeverity.ERROR < AlertSeverity.WARNING)

    def test_alert_severity_less_equal(self):
        """Test less than or equal comparison operator."""
        assert AlertSeverity.INFO <= AlertSeverity.WARNING
        assert AlertSeverity.INFO <= AlertSeverity.INFO
        assert AlertSeverity.WARNING <= AlertSeverity.WARNING

    def test_alert_severity_less_equal_false(self):
        """Test less than or equal returns False when first is greater."""
        assert not (AlertSeverity.CRITICAL <= AlertSeverity.INFO)
        assert not (AlertSeverity.ERROR <= AlertSeverity.WARNING)

    def test_alert_severity_greater_than(self):
        """Test greater than comparison operator."""
        assert AlertSeverity.CRITICAL > AlertSeverity.ERROR
        assert AlertSeverity.ERROR > AlertSeverity.WARNING
        assert AlertSeverity.WARNING > AlertSeverity.INFO

    def test_alert_severity_greater_than_same(self):
        """Test greater than returns False for same severity."""
        assert not (AlertSeverity.INFO > AlertSeverity.INFO)
        assert not (AlertSeverity.CRITICAL > AlertSeverity.CRITICAL)

    def test_alert_severity_greater_than_less(self):
        """Test greater than returns False when first is less."""
        assert not (AlertSeverity.INFO > AlertSeverity.CRITICAL)
        assert not (AlertSeverity.WARNING > AlertSeverity.ERROR)

    def test_alert_severity_greater_equal(self):
        """Test greater than or equal comparison operator."""
        assert AlertSeverity.CRITICAL >= AlertSeverity.ERROR
        assert AlertSeverity.CRITICAL >= AlertSeverity.CRITICAL
        assert AlertSeverity.ERROR >= AlertSeverity.ERROR

    def test_alert_severity_greater_equal_false(self):
        """Test greater than or equal returns False when first is less."""
        assert not (AlertSeverity.INFO >= AlertSeverity.CRITICAL)
        assert not (AlertSeverity.WARNING >= AlertSeverity.ERROR)

    def test_alert_severity_all_comparisons_consistent(self):
        """Test that all comparison operators are consistent."""
        severities = list(AlertSeverity)
        for i, s1 in enumerate(severities):
            for j, s2 in enumerate(severities):
                if i < j:
                    assert s1 < s2
                    assert s1 <= s2
                    assert not (s1 > s2)
                    assert not (s1 >= s2)
                elif i == j:
                    assert s1 <= s2
                    assert s1 >= s2
                    assert not (s1 < s2)
                    assert not (s1 > s2)
                else:
                    assert s1 > s2
                    assert s1 >= s2
                    assert not (s1 < s2)
                    assert not (s1 <= s2)


class TestAlertEvent:
    """Test AlertEvent dataclass creation and methods."""

    def test_alert_event_creation_minimal(self):
        """Test creating AlertEvent with required fields only."""
        event = AlertEvent(
            title="Test Alert",
            message="This is a test alert",
            severity=AlertSeverity.INFO,
        )
        assert event.title == "Test Alert"
        assert event.message == "This is a test alert"
        assert event.severity == AlertSeverity.INFO
        assert event.run_id == ""
        assert event.epoch == 0
        assert event.metadata == {}
        assert event.timestamp == ""

    def test_alert_event_creation_full(self):
        """Test creating AlertEvent with all fields."""
        metadata = {"key1": "value1", "key2": "value2"}
        event = AlertEvent(
            title="Critical Issue",
            message="System error occurred",
            severity=AlertSeverity.CRITICAL,
            run_id="run-12345",
            epoch=10,
            metadata=metadata,
            timestamp="2024-01-01T12:00:00Z",
        )
        assert event.title == "Critical Issue"
        assert event.message == "System error occurred"
        assert event.severity == AlertSeverity.CRITICAL
        assert event.run_id == "run-12345"
        assert event.epoch == 10
        assert event.metadata == metadata
        assert event.timestamp == "2024-01-01T12:00:00Z"

    def test_alert_event_different_severities(self):
        """Test AlertEvent with different severity levels."""
        for severity in AlertSeverity:
            event = AlertEvent(
                title="Test",
                message="Test",
                severity=severity,
            )
            assert event.severity == severity

    def test_alert_event_metadata_isolated(self):
        """Test that metadata dict is isolated between instances."""
        metadata1 = {"key": "value1"}
        event1 = AlertEvent(
            title="Event1",
            message="Test1",
            severity=AlertSeverity.INFO,
            metadata=metadata1,
        )

        event2 = AlertEvent(
            title="Event2",
            message="Test2",
            severity=AlertSeverity.WARNING,
        )

        # Modify event1's metadata
        event1.metadata["key"] = "modified"

        # event2's metadata should be empty
        assert event2.metadata == {}

    def test_alert_event_fill_timestamp_empty(self):
        """Test fill_timestamp sets timestamp when empty."""
        from datetime import timedelta
        before = datetime.now(UTC).replace(microsecond=0)
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
        )
        assert event.timestamp == ""

        event.fill_timestamp()
        after = (datetime.now(UTC).replace(microsecond=0) + timedelta(seconds=1))

        assert event.timestamp != ""
        # Parse the timestamp and verify it's within expected range
        parsed_ts = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
        assert before <= parsed_ts <= after

    def test_alert_event_fill_timestamp_format(self):
        """Test fill_timestamp creates ISO-8601 UTC format."""
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
        )
        event.fill_timestamp()

        # Should match ISO-8601 format: YYYY-MM-DDTHH:MM:SSZ
        assert event.timestamp.endswith("Z")
        assert "T" in event.timestamp
        parts = event.timestamp[:-1].split("T")
        assert len(parts) == 2
        assert len(parts[0].split("-")) == 3  # YYYY-MM-DD
        assert len(parts[1].split(":")) == 3  # HH:MM:SS

    def test_alert_event_fill_timestamp_preserves_existing(self):
        """Test fill_timestamp doesn't overwrite existing timestamp."""
        existing_ts = "2024-01-01T12:00:00Z"
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
            timestamp=existing_ts,
        )

        event.fill_timestamp()

        assert event.timestamp == existing_ts

    def test_alert_event_fill_timestamp_multiple_calls(self):
        """Test fill_timestamp is idempotent."""
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
        )

        event.fill_timestamp()
        first_ts = event.timestamp

        event.fill_timestamp()
        second_ts = event.timestamp

        assert first_ts == second_ts

    def test_alert_event_empty_title_allowed(self):
        """Test AlertEvent allows empty title."""
        event = AlertEvent(
            title="",
            message="Test message",
            severity=AlertSeverity.INFO,
        )
        assert event.title == ""

    def test_alert_event_empty_message_allowed(self):
        """Test AlertEvent allows empty message."""
        event = AlertEvent(
            title="Test title",
            message="",
            severity=AlertSeverity.INFO,
        )
        assert event.message == ""

    def test_alert_event_zero_epoch_allowed(self):
        """Test AlertEvent allows zero epoch."""
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
            epoch=0,
        )
        assert event.epoch == 0

    def test_alert_event_large_epoch(self):
        """Test AlertEvent with large epoch number."""
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
            epoch=999999,
        )
        assert event.epoch == 999999

    def test_alert_event_negative_epoch_allowed(self):
        """Test AlertEvent allows negative epoch."""
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
            epoch=-1,
        )
        assert event.epoch == -1

    def test_alert_event_empty_run_id(self):
        """Test AlertEvent allows empty run_id."""
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
            run_id="",
        )
        assert event.run_id == ""

    def test_alert_event_complex_metadata(self):
        """Test AlertEvent with complex nested metadata."""
        metadata = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "string": "test",
            "number": 42,
        }
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
            metadata=metadata,
        )
        assert event.metadata == metadata


class TestAlertChannel:
    """Test AlertChannel abstract base class."""

    def test_alert_channel_is_abstract(self):
        """Test that AlertChannel cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AlertChannel()

    def test_alert_channel_requires_send_method(self):
        """Test that subclass must implement send method."""

        class IncompleteChannel(AlertChannel):
            def name(self) -> str:
                return "incomplete"

        with pytest.raises(TypeError):
            IncompleteChannel()

    def test_alert_channel_requires_name_method(self):
        """Test that subclass must implement name method."""

        class IncompleteChannel(AlertChannel):
            def send(self, event: AlertEvent) -> bool:
                return True

        with pytest.raises(TypeError):
            IncompleteChannel()

    def test_alert_channel_concrete_implementation(self):
        """Test that concrete implementation can be created."""

        class ConcreteChannel(AlertChannel):
            def send(self, event: AlertEvent) -> bool:
                return True

            def name(self) -> str:
                return "concrete"

        channel = ConcreteChannel()
        assert isinstance(channel, AlertChannel)

    def test_alert_channel_send_receives_event(self):
        """Test that send method receives AlertEvent."""

        class TestChannel(AlertChannel):
            def __init__(self):
                self.received_event = None

            def send(self, event: AlertEvent) -> bool:
                self.received_event = event
                return True

            def name(self) -> str:
                return "test"

        channel = TestChannel()
        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.WARNING,
        )
        result = channel.send(event)

        assert result is True
        assert channel.received_event == event

    def test_alert_channel_send_return_types(self):
        """Test that send method returns boolean."""

        class TrueChannel(AlertChannel):
            def send(self, event: AlertEvent) -> bool:
                return True

            def name(self) -> str:
                return "true"

        class FalseChannel(AlertChannel):
            def send(self, event: AlertEvent) -> bool:
                return False

            def name(self) -> str:
                return "false"

        true_channel = TrueChannel()
        false_channel = FalseChannel()

        event = AlertEvent(
            title="Test",
            message="Test",
            severity=AlertSeverity.INFO,
        )

        assert true_channel.send(event) is True
        assert false_channel.send(event) is False

    def test_alert_channel_name_method(self):
        """Test that name method returns string."""

        class NamedChannel(AlertChannel):
            def send(self, event: AlertEvent) -> bool:
                return True

            def name(self) -> str:
                return "my-channel"

        channel = NamedChannel()
        assert channel.name() == "my-channel"
        assert isinstance(channel.name(), str)

    def test_alert_channel_multiple_implementations(self):
        """Test multiple different implementations."""

        class SlackLike(AlertChannel):
            def send(self, event: AlertEvent) -> bool:
                return True

            def name(self) -> str:
                return "slack"

        class EmailLike(AlertChannel):
            def send(self, event: AlertEvent) -> bool:
                return False

            def name(self) -> str:
                return "email"

        slack = SlackLike()
        email = EmailLike()

        assert slack.name() == "slack"
        assert email.name() == "email"
        assert slack.send(AlertEvent("t", "m", AlertSeverity.INFO)) is True
        assert email.send(AlertEvent("t", "m", AlertSeverity.INFO)) is False


class TestAlertEventAndSeverityIntegration:
    """Integration tests for AlertEvent and AlertSeverity."""

    def test_alert_event_with_severity_comparisons(self):
        """Test AlertEvent with severity comparisons."""
        events = [
            AlertEvent("E1", "M1", AlertSeverity.INFO),
            AlertEvent("E2", "M2", AlertSeverity.WARNING),
            AlertEvent("E3", "M3", AlertSeverity.ERROR),
            AlertEvent("E4", "M4", AlertSeverity.CRITICAL),
        ]

        # Verify severity ordering
        for i in range(len(events) - 1):
            assert events[i].severity < events[i + 1].severity

    def test_alert_event_timestamp_with_different_severities(self):
        """Test fill_timestamp works with all severity levels."""
        for severity in AlertSeverity:
            event = AlertEvent(
                title="Test",
                message="Test",
                severity=severity,
            )
            event.fill_timestamp()
            assert event.timestamp != ""
            assert event.timestamp.endswith("Z")

    def test_alert_event_filter_by_severity(self):
        """Test filtering events by minimum severity."""
        events = [
            AlertEvent("E1", "M1", AlertSeverity.INFO),
            AlertEvent("E2", "M2", AlertSeverity.WARNING),
            AlertEvent("E3", "M3", AlertSeverity.ERROR),
            AlertEvent("E4", "M4", AlertSeverity.CRITICAL),
        ]

        min_severity = AlertSeverity.ERROR
        critical_events = [e for e in events if e.severity >= min_severity]

        assert len(critical_events) == 2
        assert critical_events[0].severity == AlertSeverity.ERROR
        assert critical_events[1].severity == AlertSeverity.CRITICAL
