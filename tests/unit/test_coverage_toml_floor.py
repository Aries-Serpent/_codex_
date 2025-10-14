from __future__ import annotations


def test_toml_fail_under_from_str_parses_valid_value() -> None:
    import noxfile  # type: ignore

    text = """
    [tool.coverage.report]
    fail_under = 73
    """
    got = noxfile._toml_fail_under_from_str(text)  # type: ignore[attr-defined]
    assert got == "73"


def test_toml_fail_under_from_str_absent_returns_none() -> None:
    import noxfile  # type: ignore

    text = """
    [tool.coverage.report]
    show_missing = true
    """
    got = noxfile._toml_fail_under_from_str(text)  # type: ignore[attr-defined]
    assert got is None


def test_toml_fail_under_from_str_non_int_returns_none() -> None:
    import noxfile  # type: ignore

    text = """
    [tool.coverage.report]
    fail_under = "eighty"
    """
    got = noxfile._toml_fail_under_from_str(text)  # type: ignore[attr-defined]
    assert got is None
