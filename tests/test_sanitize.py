#     assert "&, "Condition must be true"


def test_sanitize_escapes_ampersand():
    """Test that ampersand is properly escaped."""
    prompt = "foo & bar"
    escaped = sanitize_prompt(prompt)
    assert "&amp;" in escaped, "Condition must be true"


def test_sanitize_preserves_safe_text():
    """Test that safe text without HTML chars passes through."""
    prompt = "This is a safe prompt without HTML"
    escaped = sanitize_prompt(prompt)
    # Should still be readable
    assert escaped == "This is a safe prompt without HTML", "escaped is not valid"
