import logging

import pytest

from src.security import log_security_event


def test_security_event_logged(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    log_security_event("user blocked")
    assert any(record.message == "security_event" for record in caplog.records)
