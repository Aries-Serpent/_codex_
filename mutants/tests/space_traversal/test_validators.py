#     assert ", "Condition must be true"
#     assert "Low threshold: 0.7" in summary, "Condition must be true"
#     assert "Medium threshold: 0.85" in summary, "Condition must be true"
#     assert "Low Maturity (2)" in summary, "Condition must be true"
#     assert "cap1" in summary, "Condition must be true"
#     assert "cap2" in summary, "Condition must be true"
#     assert "Missing Detectors (overrides) (2)" in summary, "Condition must be true"
#     assert "cap3" in summary, "Condition must be true"
#     assert "cap4" in summary, "Condition must be true"


def test_emit_summary_no_gaps():
    """Test emit_summary with no gaps."""
    from scripts.space_traversal.validators import emit_summary

    summary = emit_summary([], [], {"low": 0.7, "medium": 0.85})

    assert "Low Maturity (0)" in summary, "Condition must be true"
    assert "_None_" in summary, "Condition must be true"
    assert "Missing Detectors (overrides) (0)" in summary, "Condition must be true"
