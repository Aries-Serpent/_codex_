"""
Test Logging Registry

Test module for logging registry.
"""

from codex_ml.logging import registry


def test_register_and_get_logger():
    seen = []

    def _log(msg: str) -> None:
        seen.append(msg)

    registry.register_logger("test", _log)
    logger = registry.get_logger("test")
    logger("hello")
    assert "hello" in seen, "Condition must be true"
