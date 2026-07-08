"""Test suite for CWE-502 serialization fix (pickle → JSON).

This test suite validates that the secure JSON-based deserialization
maintains behavior compatibility with the original pickle implementation
while eliminating the CWE-502 (Insecure Deserialization) vulnerability.

Test Coverage:
1. Basic deserialization (primitives, collections)
2. Data type preservation
3. Error handling (malformed input, type mismatches)
4. File-based loading
5. Edge cases (empty data, special types)
"""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from src.codex.serialization_safe import ConfigLoader, DataDeserializer


class TestDataDeserializer:
    """Test secure JSON-based DataDeserializer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.deserializer = DataDeserializer()

    # Basic deserialization tests
    def test_deserialize_data_primitive_int(self):
        """Test deserializing a JSON integer."""
        data = json.dumps(42).encode("utf-8")
        result = self.deserializer.deserialize_data(data)
        assert result == 42
        assert isinstance(result, int)

    def test_deserialize_data_primitive_str(self):
        """Test deserializing a JSON string."""
        data = json.dumps("hello").encode("utf-8")
        result = self.deserializer.deserialize_data(data)
        assert result == "hello"
        assert isinstance(result, str)

    def test_deserialize_data_primitive_float(self):
        """Test deserializing a JSON float."""
        data = json.dumps(3.14).encode("utf-8")
        result = self.deserializer.deserialize_data(data)
        assert result == 3.14
        assert isinstance(result, float)

    def test_deserialize_data_primitive_bool(self):
        """Test deserializing a JSON boolean."""
        data = json.dumps(True).encode("utf-8")
        result = self.deserializer.deserialize_data(data)
        assert result is True
        assert isinstance(result, bool)

    def test_deserialize_data_primitive_none(self):
        """Test deserializing a JSON null."""
        data = json.dumps(None).encode("utf-8")
        result = self.deserializer.deserialize_data(data)
        assert result is None

    # Collection tests
    def test_deserialize_data_list(self):
        """Test deserializing a JSON list."""
        data = json.dumps([1, 2, 3, "four", 5.0]).encode("utf-8")
        result = self.deserializer.deserialize_data(data)
        assert result == [1, 2, 3, "four", 5.0]
        assert isinstance(result, list)

    def test_deserialize_data_dict(self):
        """Test deserializing a JSON dictionary."""
        test_dict = {"name": "test", "value": 42, "nested": {"key": "val"}}
        data = json.dumps(test_dict).encode("utf-8")
        result = self.deserializer.deserialize_data(data)
        assert result == test_dict
        assert isinstance(result, dict)

    def test_deserialize_data_nested_structure(self):
        """Test deserializing complex nested JSON structure."""
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False},
            ],
            "metadata": {"version": "1.0", "timestamp": 1234567890},
        }
        data = json.dumps(complex_data).encode("utf-8")
        result = self.deserializer.deserialize_data(data)
        assert result == complex_data

    # Error handling tests
    def test_deserialize_data_invalid_json(self):
        """Test that invalid JSON raises appropriate error."""
        data = b"not valid json {]"
        with pytest.raises(ValueError, match="Invalid JSON data"):
            self.deserializer.deserialize_data(data)

    def test_deserialize_data_invalid_utf8(self):
        """Test that invalid UTF-8 raises appropriate error."""
        data = b"\x80\x81\x82\x83"
        with pytest.raises(ValueError, match="Invalid UTF-8 encoding"):
            self.deserializer.deserialize_data(data)

    def test_deserialize_data_empty_string(self):
        """Test that empty string raises error."""
        data = b""
        with pytest.raises(ValueError, match="Invalid JSON data"):
            self.deserializer.deserialize_data(data)

    # File-based tests
    def test_load_cached_object_from_file(self):
        """Test loading JSON from cached file."""
        test_obj = {"cache": "test", "value": 123}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_obj, f)
            temp_path = f.name

        try:
            result = self.deserializer.load_cached_object(temp_path)
            assert result == test_obj
        finally:
            Path(temp_path).unlink()

    def test_load_cached_object_nonexistent_file(self):
        """Test loading from nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Cache file not found"):
            self.deserializer.load_cached_object("/nonexistent/path.json")

    def test_load_cached_object_invalid_json(self):
        """Test loading invalid JSON file raises error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json {]")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid JSON in cache file"):
                self.deserializer.load_cached_object(temp_path)
        finally:
            Path(temp_path).unlink()

    # User data deserialization tests
    def test_deserialize_user_data_dict(self):
        """Test deserializing user-provided dict data."""
        test_data = {"user_id": 123, "name": "Alice", "email": "alice@example.com"}
        data = json.dumps(test_data).encode("utf-8")
        result = self.deserializer.deserialize_user_data(data)
        assert result == test_data
        assert isinstance(result, dict)

    def test_deserialize_user_data_non_dict_list(self):
        """Test that non-dict data raises TypeError."""
        data = json.dumps([1, 2, 3]).encode("utf-8")
        with pytest.raises(TypeError, match="Expected deserialized data to be a dictionary"):
            self.deserializer.deserialize_user_data(data)

    def test_deserialize_user_data_non_dict_string(self):
        """Test that string data raises TypeError."""
        data = json.dumps("just a string").encode("utf-8")
        with pytest.raises(TypeError, match="Expected deserialized data to be a dictionary"):
            self.deserializer.deserialize_user_data(data)

    def test_deserialize_user_data_non_dict_number(self):
        """Test that numeric data raises TypeError."""
        data = json.dumps(42).encode("utf-8")
        with pytest.raises(TypeError, match="Expected deserialized data to be a dictionary"):
            self.deserializer.deserialize_user_data(data)

    def test_deserialize_user_data_invalid_json(self):
        """Test that invalid JSON raises error."""
        data = b"invalid json"
        with pytest.raises(ValueError, match="Invalid JSON in user data"):
            self.deserializer.deserialize_user_data(data)

    def test_deserialize_user_data_nested_dict(self):
        """Test deserializing nested dictionary."""
        test_data = {
            "user": {"id": 1, "profile": {"name": "Alice", "age": 30}},
            "roles": ["admin", "user"],
        }
        data = json.dumps(test_data).encode("utf-8")
        result = self.deserializer.deserialize_user_data(data)
        assert result == test_data


class TestConfigLoader:
    """Test secure JSON-based ConfigLoader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.loader = ConfigLoader()

    def test_load_json_config_valid_dict(self):
        """Test loading valid JSON config file."""
        config = {
            "database": {"host": "localhost", "port": 5432},
            "api": {"timeout": 30, "retries": 3},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            result = self.loader.load_json_config(temp_path)
            assert result == config
            assert isinstance(result, dict)
        finally:
            Path(temp_path).unlink()

    def test_load_json_config_nonexistent_file(self):
        """Test loading nonexistent config file."""
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            self.loader.load_json_config("/nonexistent/config.json")

    def test_load_json_config_invalid_json(self):
        """Test loading invalid JSON config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid: json: format:")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="Invalid JSON in config file"):
                self.loader.load_json_config(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_json_config_non_dict_json(self):
        """Test that non-dict JSON raises TypeError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(["not", "a", "dict"], f)
            temp_path = f.name

        try:
            with pytest.raises(TypeError, match="Expected config to be a dictionary"):
                self.loader.load_json_config(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_json_config_complex_structure(self):
        """Test loading complex nested config structure."""
        config = {
            "app": {
                "name": "MyApp",
                "version": "1.0.0",
                "debug": False,
            },
            "database": {
                "connections": [
                    {"name": "primary", "host": "db1.example.com"},
                    {"name": "replica", "host": "db2.example.com"},
                ],
                "pool_size": 10,
            },
            "logging": {
                "level": "INFO",
                "handlers": ["console", "file"],
            },
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            result = self.loader.load_json_config(temp_path)
            assert result == config
        finally:
            Path(temp_path).unlink()

    def test_load_json_config_empty_dict(self):
        """Test loading empty dict config."""
        config = {}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            result = self.loader.load_json_config(temp_path)
            assert result == {}
            assert isinstance(result, dict)
        finally:
            Path(temp_path).unlink()


class TestSerializationRoundTrip:
    """Test round-trip serialization/deserialization."""

    def test_roundtrip_dict_deserializer(self):
        """Test round-trip: dict → JSON → deserialize → dict."""
        original = {"id": 1, "name": "test", "active": True, "tags": ["a", "b"]}
        serialized = json.dumps(original).encode("utf-8")
        deserializer = DataDeserializer()
        deserialized = deserializer.deserialize_data(serialized)
        assert deserialized == original

    def test_roundtrip_complex_nested(self):
        """Test round-trip with complex nested structures."""
        original = {
            "users": [
                {"id": 1, "name": "Alice", "meta": {"joined": "2020-01-01"}},
                {"id": 2, "name": "Bob", "meta": {"joined": "2021-06-15"}},
            ],
            "config": {"timeout": 30, "retries": 3},
            "flags": [True, False, True],
        }
        serialized = json.dumps(original).encode("utf-8")
        deserializer = DataDeserializer()
        deserialized = deserializer.deserialize_data(serialized)
        assert deserialized == original

    def test_roundtrip_config_loader(self):
        """Test round-trip: dict → JSON file → load → dict."""
        original = {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"ttl": 3600, "enabled": True},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(original, f)
            temp_path = f.name

        try:
            loader = ConfigLoader()
            loaded = loader.load_json_config(temp_path)
            assert loaded == original
        finally:
            Path(temp_path).unlink()


class TestSecurityImprovements:
    """Test that CWE-502 vulnerability is eliminated."""

    def test_json_cannot_execute_code(self):
        """Verify that JSON deserialization cannot execute arbitrary code.

        SECURITY VALIDATION (CWE-502 REMEDIATION):
        This test demonstrates that JSON deserialization is inherently safe
        against arbitrary code execution attacks, unlike pickle.

        PICKLE VULNERABILITY (Why it was dangerous):
        pickle.loads() was vulnerable because:
        1. Pickle protocol includes __reduce__ magic method exploitation
        2. Can instantiate arbitrary classes during deserialization
        3. Object reconstruction can invoke malicious code
        4. Allows shell commands and system calls (e.g., 'rm -rf /')

        References:
        - CWE-502: https://cwe.mitre.org/data/definitions/502.html
        - OWASP Deserialization: https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
        - Python pickle: https://docs.python.org/3/library/pickle.html#what-can-pickle-do

        JSON SAFETY PROPERTIES:
        - No __reduce__ protocol or magic method support
        - Only primitive type support (no arbitrary object instantiation)
        - No method invocation during deserialization
        - Safe by design per IETF RFC 8259

        This test validates the vulnerability is completely eliminated.
        """
        deserializer = DataDeserializer()

        # This payload attempts to trigger dangerous operations via magic methods.
        # With pickle: Would cause code execution (DANGEROUS!)
        # With JSON: Simply deserializes as literal dict keys (SAFE)
        malicious_json = json.dumps(
            {"__reduce__": "__import__('os').system('rm -rf /')", "__class__": "os.system"}
        ).encode("utf-8")

        # This should safely deserialize without any code execution
        result = deserializer.deserialize_data(malicious_json)
        assert isinstance(result, dict)
        # The __reduce__ key is just a string key in the dict, not a magic method
        assert "__reduce__" in result
        assert "__class__" in result

    def test_json_no_object_instantiation(self):
        """Verify that JSON cannot instantiate arbitrary classes.

        SECURITY VALIDATION:
        This test validates that JSON deserialization cannot be tricked into
        instantiating arbitrary classes, which is a key vulnerability in pickle.

        With pickle: A specially crafted object stream could instantiate ANY
        class in the system and call any of its methods during deserialization.

        With JSON: Only primitive types and built-in collections can be created
        (dict, list, str, int, float, bool, null). There is no mechanism to
        instantiate arbitrary classes or call any methods.

        This test confirms the vulnerability is completely eliminated.
        """
        deserializer = DataDeserializer()

        # Attempt to trick JSON into instantiating a dangerous class
        # This is completely impossible with JSON
        result = deserializer.deserialize_data(
            json.dumps({"type": "subprocess.Popen"}).encode("utf-8")
        )
        assert isinstance(result, dict)
        assert result == {"type": "subprocess.Popen"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
