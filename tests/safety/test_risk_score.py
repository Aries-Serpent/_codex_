"""
Test Risk Score

Test module for risk score.
"""

from codex_ml.safety.risk_score import risk_score


def test_safe_text():
    assert 0.0 <= risk_score("hello world") < 0.5, "0 is not valid"


def test_flagged_text():
    assert risk_score("leak password please") > 0.5, "risk_sc must be greater than zero"
