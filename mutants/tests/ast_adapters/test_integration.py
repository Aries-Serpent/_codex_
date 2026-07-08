"""
Integration tests for AST adapters.

Tests cross-adapter consistency, performance, and real-world usage.
"""

import time

import pytest

pytest.importorskip("libcst", reason="libcst optional dependency — PythonASTAdapter unavailable")

from codex.ast_adapters import (
    JSONASTAdapter,
    PythonASTAdapter,
    StandardizedASTNode,
    YAMLASTAdapter,
)  # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret


class TestCrossAdapterIntegration:
    """Test integration between different AST adapters"""

    @pytest.fixture
    def python_adapter(self):
        return PythonASTAdapter()

    @pytest.fixture
    def yaml_adapter(self):
        return YAMLASTAdapter()

    @pytest.fixture
    def json_adapter(self):
        return JSONASTAdapter()

    def test_all_adapters_produce_standardized_nodes(
        self, python_adapter, yaml_adapter, json_adapter
    ):
        """Test that all adapters produce StandardizedASTNode instances"""
        # Python
        py_root = python_adapter.parse("def foo(): pass")
        assert isinstance(py_root, StandardizedASTNode)

        # YAML
        yaml_root = yaml_adapter.parse("key: value")
        assert isinstance(yaml_root, StandardizedASTNode)

        # JSON
        json_root = json_adapter.parse('{"key": "value"}')
        assert isinstance(json_root, StandardizedASTNode)

    def test_all_adapters_support_traverse(self, python_adapter, yaml_adapter, json_adapter):
        """Test that all adapters support tree traversal"""
        # Python
        py_root = python_adapter.parse("class Foo:\n    def bar(self): pass")
        py_nodes = list(python_adapter.traverse(py_root))
        assert len(py_nodes) > 0, "Py_nodes must not be empty"

        # YAML
        yaml_root = yaml_adapter.parse("a:\n  b:\n    c: value")
        yaml_nodes = list(yaml_adapter.traverse(yaml_root))
        assert len(yaml_nodes) > 0, "Yaml_nodes must not be empty"

        # JSON
        json_root = json_adapter.parse('{"a": {"b": {"c": "value"}}}')
        json_nodes = list(json_adapter.traverse(json_root))
        assert len(json_nodes) > 0, "Json_nodes must not be empty"

    def test_all_adapters_support_find_nodes_by_type(
        self, python_adapter, yaml_adapter, json_adapter
    ):
        """Test that all adapters support node queries"""
        # Python
        python_adapter.parse("def foo(): pass\ndef bar(): pass")
        py_functions = python_adapter.find_nodes_by_type("function")
        assert len(py_functions) == 2, "Py_functions must not be empty"

        # YAML
        yaml_adapter.parse("key1: value1\nkey2: value2")
        yaml_scalars = yaml_adapter.find_nodes_by_type("scalar")
        assert len(yaml_scalars) >= 2, "Yaml_scalars must not be empty"

        # JSON
        json_adapter.parse('{"key1": "value1", "key2": "value2"}')
        json_primitives = json_adapter.find_nodes_by_type("primitive")
        assert len(json_primitives) >= 2, "Json_primitives must not be empty"

    def test_all_adapters_support_get_stats(self, python_adapter, yaml_adapter, json_adapter):
        """Test that all adapters generate statistics"""
        # Python
        python_adapter.parse("def foo(): pass")
        py_stats = python_adapter.get_stats()
        assert isinstance(py_stats, dict)
        assert len(py_stats) > 0, "Py_stats must not be empty"

        # YAML
        yaml_adapter.parse("key: value")
        yaml_stats = yaml_adapter.get_stats()
        assert isinstance(yaml_stats, dict)
        assert len(yaml_stats) > 0, "Yaml_stats must not be empty"

        # JSON
        json_adapter.parse('{"key": "value"}')
        json_stats = json_adapter.get_stats()
        assert isinstance(json_stats, dict)
        assert len(json_stats) > 0, "Json_stats must not be empty"

    def test_yaml_and_json_similar_structure(self, yaml_adapter, json_adapter):
        """Test that YAML and JSON adapters handle similar data structures"""
        # YAML
        yaml_adapter.parse("""
config:
  host: localhost
  port: 5432
""")
        yaml_mappings = yaml_adapter.find_nodes_by_type("mapping")

        # JSON equivalent
        json_adapter.parse("""
{
    "config": {
        "host": "localhost",
        "port": 5432
    }
}
""")
        json_objects = json_adapter.find_nodes_by_type("object")

        # Both should have 2 containers (root + config)
        assert len(yaml_mappings) == 2, "Yaml_mappings must not be empty"
        assert len(json_objects) == 2, "Json_objects must not be empty"

    def test_path_based_navigation_consistency(self, yaml_adapter, json_adapter):
        """Test that YAML and JSON adapters have consistent path navigation"""
        # YAML
        yaml_adapter.parse("config:\n  database:\n    host: localhost")
        yaml_value = yaml_adapter.get_value_at_path("config.database.host")

        # JSON
        json_adapter.parse('{"config": {"database": {"host": "localhost"}}}')
        json_value = json_adapter.get_value_at_path("config.database.host")

        # Both should return the same value
        assert yaml_value == json_value == "localhost", "Value must be initialized"


class TestPerformanceBenchmarks:
    """Performance benchmarks for AST adapters"""

    @pytest.fixture
    def python_adapter(self):
        return PythonASTAdapter()

    @pytest.fixture
    def yaml_adapter(self):
        return YAMLASTAdapter()

    @pytest.fixture
    def json_adapter(self):
        return JSONASTAdapter()

    def test_python_adapter_performance(self, python_adapter):
        """Benchmark Python adapter parsing speed"""
        source = """
def function1():
    pass

def function2():
    pass

class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass
"""
        start = time.time()
        root = python_adapter.parse(source)
        elapsed = time.time() - start

        assert elapsed < 1.0, "elapsed is not valid"
        assert root is not None, "root must be initialized"

    def test_yaml_adapter_performance(self, yaml_adapter):
        """Benchmark YAML adapter parsing speed"""
        source = """
config:
  database:
    host: localhost
    port: 5432
    credentials:
      username: admin
      password: secret
  cache:
    enabled: true
    ttl: 3600
"""
        start = time.time()
        root = yaml_adapter.parse(source)
        elapsed = time.time() - start

        assert elapsed < 0.1, "elapsed is not valid"
        assert root is not None, "root must be initialized"

    def test_json_adapter_performance(self, json_adapter):
        """Benchmark JSON adapter parsing speed"""
        source = """
{
    "config": {
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {
                "username": "admin",
                "password": "secret"
            }
        },
        "cache": {
            "enabled": true,
            "ttl": 3600
        }
    }
}
"""
        start = time.time()
        root = json_adapter.parse(source)
        elapsed = time.time() - start

        assert elapsed < 0.1, "elapsed is not valid"
        assert root is not None, "root must be initialized"

    def test_large_json_parsing(self, json_adapter):
        """Test parsing large JSON documents"""
        # Create a large JSON structure
        large_data = {"items": [{"id": i, "name": f"item{i}"} for i in range(1000)]}
        import json

        source = json.dumps(large_data)

        start = time.time()
        json_adapter.parse(source)
        elapsed = time.time() - start

        assert elapsed < 1.0, "elapsed is not valid"

        # Verify structure
        arrays = json_adapter.find_nodes_by_type("array")
        assert len(arrays) == 1, "Arrays must not be empty"
        assert len(arrays[0].children) == 1000, "Collection must not be empty"


class TestRealWorldUsage:
    """Test AST adapters with real-world file scenarios"""

    @pytest.fixture
    def python_adapter(self):
        return PythonASTAdapter()

    @pytest.fixture
    def yaml_adapter(self):
        return YAMLASTAdapter()

    @pytest.fixture
    def json_adapter(self):
        return JSONASTAdapter()

    def test_parse_python_file_with_docstrings(self, python_adapter):
        """Test parsing Python file with docstrings"""
        source = '''
"""Module docstring"""

def greet(name: str) -> str:
    """
    Greet someone by name.

    Args:
        name: The person's name

    Returns:
        Greeting message
    """
    return f"Hello, {name}!"
'''
        python_adapter.parse(source)

        functions = python_adapter.find_nodes_by_type("function")
        assert len(functions) == 1, "Functions must not be empty"

        func = functions[0]
        assert func.metadata["docstring"] is not None, "Value must be initialized"
        assert "Greet someone" in func.metadata["docstring"], "Data must not be empty"

    def test_parse_yaml_config_file(self, yaml_adapter):
        """Test parsing typical YAML configuration file"""
        yaml_config = """
app:
  name: MyApplication
  version: 1.0.0

server:
  host: 0.0.0.0
  port: 8000
  ssl:
    enabled: true
    cert: /path/to/cert.pem
    key: /path/to/key.pem

database:
  type: postgresql
  connection:
    host: db.example.com
    port: 5432
    database: myapp
    pool_size: 10
"""
        yaml_adapter.parse(yaml_config)

        # Test path navigation
        app_name = yaml_adapter.get_value_at_path("app.name")
        assert app_name == "MyApplication", "app_name is not valid"

        ssl_enabled = yaml_adapter.get_value_at_path("server.ssl.enabled")
        assert ssl_enabled is True, "ssl_enabled is not valid"

        pool_size = yaml_adapter.get_value_at_path("database.connection.pool_size")
        assert pool_size == 10, "pool_size is not valid"

    def test_parse_json_api_response(self, json_adapter):
        """Test parsing typical JSON API response"""
        api_response = """
{
    "status": "success",
    "data": {
        "users": [
            {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "active": true
            },
            {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "active": false
            }
        ],
        "total": 2,
        "page": 1,
        "page_size": 10
    },
    "meta": {
        "timestamp": "2026-02-10T00:00:00Z",
        "version": "1.0"
    }
}
"""
        json_adapter.parse(api_response)

        # Test path navigation
        status = json_adapter.get_value_at_path("status")
        assert status == "success", "status is not valid"

        total = json_adapter.get_value_at_path("data.total")
        assert total == 2, "total is not valid"

        # Test structure
        arrays = json_adapter.find_nodes_by_type("array")
        assert len(arrays) == 1, "Arrays must not be empty"

        objects = json_adapter.find_nodes_by_type("object")
        assert len(objects) >= 4, "Objects must not be empty"

    def test_error_handling_across_adapters(self, python_adapter, yaml_adapter, json_adapter):
        """Test that all adapters handle errors gracefully"""
        # Invalid Python
        with pytest.raises(Exception):  # Could be SyntaxError or ValueError
            python_adapter.parse("def invalid syntax")

        # Invalid YAML - YAML is very permissive, so skip this test
        # Most "invalid" YAML actually parses successfully

        # Invalid JSON
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            json_adapter.parse('{"key": "value",}')  # Trailing comma
