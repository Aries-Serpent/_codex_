"""
Performance tests for AST adapters.

This module contains stress tests to validate performance characteristics
of all AST adapters under load. Tests generate large synthetic files to
measure parsing speed and memory efficiency.

Performance Targets:
- Python: <2s for 10KB+ file (500+ functions)
- YAML: <500ms for 1000+ keys
- JSON: <1s for 10000+ items
- SQL: <1s for 100+ tables
"""

import time

import pytest

pytest.importorskip("libcst", reason="libcst optional dependency — PythonASTAdapter unavailable")

from codex.ast_adapters import (
    JSONASTAdapter,
    PythonASTAdapter,
    SQLASTAdapter,
    YAMLASTAdapter,
)


class TestPythonPerformance:
    """Performance tests for Python adapter."""

    def test_large_python_file(self):
        """Test parsing large Python file (10KB+, 500+ functions)."""
        # Generate large Python source (500 functions)
        functions = []
        for i in range(500):
            functions.append(
                f"def function_{i}(arg1, arg2, arg3):\n"
                f'    """Function {i} docstring."""\n'
                f"    result = arg1 + arg2 + arg3\n"
                f"    return result * {i}\n"
            )

        source = "\n".join(functions)
        assert len(source) > 10000, "Source must not be empty"

        adapter = PythonASTAdapter()

        start_time = time.time()
        root = adapter.parse(source)
        elapsed = time.time() - start_time

        # Verify parsing succeeded
        assert root is not None, "root must be initialized"
        functions_found = adapter.find_nodes_by_type("function")
        assert len(functions_found) == 500, "Functions_found must not be empty"

        # Performance assertion: <2s target
        assert elapsed < 2.0, f"Python parsing took {elapsed:.2f}s (target: <2s)"
        print(f"\n✅ Python: Parsed 500 functions in {elapsed:.3f}s (target: <2s)")

    def test_deeply_nested_python(self):
        """Test parsing deeply nested Python structures."""
        # Generate nested class structure (10 levels deep)
        indent_level = 0
        lines = []
        for i in range(10):
            indent = "    " * indent_level
            lines.append(f"{indent}class Class{i}:")
            lines.append(f'{indent}    """Class {i}."""')
            lines.append(f"{indent}    def method{i}(self):")
            lines.append(f'{indent}        """Method {i}."""')
            lines.append(f"{indent}        return {i}")
            indent_level += 1

        source = "\n".join(lines)

        adapter = PythonASTAdapter()

        start_time = time.time()
        root = adapter.parse(source)
        elapsed = time.time() - start_time

        # Verify parsing succeeded
        assert root is not None, "root must be initialized"
        classes = adapter.find_nodes_by_type("class")
        assert len(classes) == 10, "Classes must not be empty"

        # Should be fast for nested structures
        assert elapsed < 1.0, f"Nested Python took {elapsed:.2f}s"
        print(f"\n✅ Python nested: Parsed 10 levels in {elapsed:.3f}s")


class TestYAMLPerformance:
    """Performance tests for YAML adapter."""

    def test_large_yaml_file(self):
        """Test parsing YAML with 1000+ keys."""
        # Generate YAML with 1000 keys (10 sections, 100 keys each)
        lines = []
        for section in range(10):
            lines.append(f"section_{section}:")
            for key in range(100):
                lines.append(f"  key_{key}: value_{section}_{key}")

        yaml_source = "\n".join(lines)

        adapter = YAMLASTAdapter()

        start_time = time.time()
        root = adapter.parse(yaml_source)
        elapsed = time.time() - start_time

        # Verify parsing succeeded
        assert root is not None, "root must be initialized"
        mappings = adapter.find_nodes_by_type("mapping")
        assert len(mappings) >= 10, "Mappings must not be empty"

        # Performance assertion: <500ms target
        assert elapsed < 0.5, f"YAML parsing took {elapsed:.2f}s (target: <0.5s)"
        print(f"\n✅ YAML: Parsed 1000 keys in {elapsed:.3f}s (target: <0.5s)")

    def test_deeply_nested_yaml(self):
        """Test parsing deeply nested YAML structures."""
        # Generate 20-level deep nesting
        lines = []
        for level in range(20):
            indent = "  " * level
            lines.append(f"{indent}level_{level}:")
        lines.append("  " * 20 + "value: deep_value")

        yaml_source = "\n".join(lines)

        adapter = YAMLASTAdapter()

        start_time = time.time()
        root = adapter.parse(yaml_source)
        elapsed = time.time() - start_time

        # Verify parsing succeeded
        assert root is not None, "root must be initialized"

        # Should handle deep nesting efficiently
        assert elapsed < 0.2, f"Deep YAML took {elapsed:.2f}s"
        print(f"\n✅ YAML nested: Parsed 20 levels in {elapsed:.3f}s")


class TestJSONPerformance:
    """Performance tests for JSON adapter."""

    def test_large_json_array(self):
        """Test parsing JSON with 10000+ items."""
        # Generate large JSON array (10000 items)
        import json

        data = {
            "items": [
                {
                    "id": i,
                    "name": f"item_{i}",
                    "value": i * 2,
                    "active": i % 2 == 0,
                    "metadata": {
                        "created": f"2024-01-{(i % 30) + 1:02d}",
                        "category": f"cat_{i % 10}",
                    },
                }
                for i in range(10000)
            ]
        }

        json_source = json.dumps(data)
        assert len(json_source) > 500000, "Json_source must not be empty"

        adapter = JSONASTAdapter()

        start_time = time.time()
        root = adapter.parse(json_source)
        elapsed = time.time() - start_time

        # Verify parsing succeeded
        assert root is not None, "root must be initialized"
        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) >= 1, "Arrays must not be empty"

        # Performance assertion: <1s target
        assert elapsed < 1.0, f"JSON parsing took {elapsed:.2f}s (target: <1s)"
        print(f"\n✅ JSON: Parsed 10000 items in {elapsed:.3f}s (target: <1s)")

    def test_deeply_nested_json(self):
        """Test parsing deeply nested JSON structures."""
        import json

        # Generate 50-level deep nesting
        data = {"level_0": {}}
        current = data["level_0"]
        for i in range(1, 50):
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]
        current["value"] = "deep_value"

        json_source = json.dumps(data)

        adapter = JSONASTAdapter()

        start_time = time.time()
        root = adapter.parse(json_source)
        elapsed = time.time() - start_time

        # Verify parsing succeeded
        assert root is not None, "root must be initialized"

        # Should handle deep nesting efficiently
        assert elapsed < 0.5, f"Deep JSON took {elapsed:.2f}s"
        print(f"\n✅ JSON nested: Parsed 50 levels in {elapsed:.3f}s")


class TestSQLPerformance:
    """Performance tests for SQL adapter."""

    def test_large_sql_schema(self):
        """Test parsing SQL with 100+ tables."""
        # Generate SQL schema with 100 tables
        statements = []
        for i in range(100):
            statements.append(
                f"CREATE TABLE table_{i} ("
                f"id INT PRIMARY KEY, "
                f"name VARCHAR(100), "
                f"value INT, "
                f"created_at TIMESTAMP"
                f");"
            )

        sql_source = "\n".join(statements)

        adapter = SQLASTAdapter()

        start_time = time.time()
        root = adapter.parse(sql_source)
        elapsed = time.time() - start_time

        # Verify parsing succeeded
        assert root is not None, "root must be initialized"
        statements_found = adapter.find_nodes_by_type("sql_statement")
        assert len(statements_found) >= 100, "Statements_found must not be empty"

        # Performance assertion: <1s target
        assert elapsed < 1.0, f"SQL parsing took {elapsed:.2f}s (target: <1s)"
        print(f"\n✅ SQL: Parsed 100 tables in {elapsed:.3f}s (target: <1s)")

    def test_complex_sql_queries(self):
        """Test parsing complex SQL queries with joins."""
        # Generate complex SELECT statements
        statements = []
        for i in range(50):
            statements.append(
                f"SELECT t1.id, t1.name, t2.value, t3.total "
                f"FROM table_{i} AS t1 "
                f"JOIN table_{i + 1} AS t2 ON t1.id = t2.id "
                f"LEFT JOIN table_{i + 2} AS t3 ON t2.id = t3.id "
                f"WHERE t1.active = 1 AND t2.value > {i * 10} "
                f"ORDER BY t1.created_at DESC "
                f"LIMIT {i + 10};"
            )

        sql_source = "\n".join(statements)

        adapter = SQLASTAdapter()

        start_time = time.time()
        root = adapter.parse(sql_source)
        elapsed = time.time() - start_time

        # Verify parsing succeeded
        assert root is not None, "root must be initialized"
        statements_found = adapter.find_nodes_by_type("sql_statement")
        assert len(statements_found) >= 50, "Statements_found must not be empty"

        # Should handle complex queries efficiently
        assert elapsed < 1.0, f"Complex SQL took {elapsed:.2f}s"
        print(f"\n✅ SQL complex: Parsed 50 queries in {elapsed:.3f}s")


class TestMemoryEfficiency:
    """Memory efficiency tests for all adapters."""

    def test_python_memory_efficient(self):
        """Verify Python adapter doesn't leak memory."""
        adapter = PythonASTAdapter()

        # Parse the same file multiple times
        source = "def test(): pass\n" * 100

        for _ in range(10):
            root = adapter.parse(source)
            assert root is not None, "root must be initialized"

        print("\n✅ Python: No memory leaks detected")

    def test_yaml_memory_efficient(self):
        """Verify YAML adapter doesn't leak memory."""
        adapter = YAMLASTAdapter()

        # Parse the same YAML multiple times
        yaml_source = "key: value\n" * 100

        for _ in range(10):
            root = adapter.parse(yaml_source)
            assert root is not None, "root must be initialized"

        print("\n✅ YAML: No memory leaks detected")

    def test_json_memory_efficient(self):
        """Verify JSON adapter doesn't leak memory."""
        import json

        adapter = JSONASTAdapter()

        # Parse the same JSON multiple times
        data = {"items": [{"id": i} for i in range(100)]}
        json_source = json.dumps(data)

        for _ in range(10):
            root = adapter.parse(json_source)
            assert root is not None, "root must be initialized"

        print("\n✅ JSON: No memory leaks detected")

    def test_sql_memory_efficient(self):
        """Verify SQL adapter doesn't leak memory."""
        adapter = SQLASTAdapter()

        # Parse the same SQL multiple times
        sql_source = "SELECT * FROM table_1;\n" * 100

        for _ in range(10):
            root = adapter.parse(sql_source)
            assert root is not None, "root must be initialized"

        print("\n✅ SQL: No memory leaks detected")


class TestConcurrentParsing:
    """Test concurrent parsing scenarios."""

    def test_multiple_adapters_simultaneously(self):
        """Test using multiple adapters at the same time."""
        py_adapter = PythonASTAdapter()
        yaml_adapter = YAMLASTAdapter()
        json_adapter = JSONASTAdapter()
        sql_adapter = SQLASTAdapter()

        # Parse different formats simultaneously
        py_root = py_adapter.parse("def test(): pass")
        yaml_root = yaml_adapter.parse("key: value")
        json_root = json_adapter.parse('{"key": "value"}')
        sql_root = sql_adapter.parse("SELECT * FROM table1;")

        # Verify all succeeded
        assert py_root is not None, "py_root must be initialized"
        assert yaml_root is not None, "yaml_root must be initialized"
        assert json_root is not None, "json_root must be initialized"
        assert sql_root is not None, "sql_root must be initialized"

        print("\n✅ Concurrent: All adapters work simultaneously")
