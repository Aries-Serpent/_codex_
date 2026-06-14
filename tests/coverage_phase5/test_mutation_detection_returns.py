"""Tests for mutation detection - return value changes."""
from __future__ import annotations


def get_status_code(success: bool) -> int:
    if success:
        return 200
    return 400


def get_message(code: int) -> str:
    codes = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        500: "Internal Server Error"
    }
    return codes.get(code, "Unknown")


def transform_value(x: int) -> int:
    return x * 2 + 1


class TestReturnValueMutations:
    """Test return values for mutation detection."""

    def test_status_success(self):
        assert get_status_code(True) == 200

    def test_status_failure(self):
        assert get_status_code(False) == 400

    def test_status_not_201(self):
        # Ensure not substituted with 201
        assert get_status_code(True) != 201

    def test_status_not_401(self):
        # Ensure not substituted with 401
        assert get_status_code(False) != 401

    def test_message_ok(self):
        assert get_message(200) == "OK"

    def test_message_bad_request(self):
        assert get_message(400) == "Bad Request"

    def test_message_not_found(self):
        assert get_message(404) == "Not Found"

    def test_message_server_error(self):
        assert get_message(500) == "Internal Server Error"

    def test_message_unknown(self):
        assert get_message(999) == "Unknown"

    def test_transform_value_positive(self):
        assert transform_value(1) == 3
        assert transform_value(2) == 5
        assert transform_value(5) == 11

    def test_transform_value_zero(self):
        assert transform_value(0) == 1

    def test_transform_value_negative(self):
        assert transform_value(-1) == -1
