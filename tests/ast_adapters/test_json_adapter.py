"""
Tests for JSON AST Adapter.
"""

from pathlib import Path

import pytest

from codex.ast_adapters.json_adapter import JSONASTAdapter


class TestJSONASTAdapter:
    """Test suite for JSONASTAdapter"""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance"""
        return JSONASTAdapter() # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

    def test_init(self, adapter):
        """Test adapter initialization"""
        assert adapter is not None, "adapter must be initialized"
        assert adapter.root_node is None, "root_node is not valid"

    def test_parse_simple_object(self, adapter):
        """Test parsing simple key-value pairs"""
        json_source = '{"key1": "value1", "key2": "value2"}'
        root = adapter.parse(json_source)

        assert root.node_type == "document", "node_type is not valid"
        assert len(root.children) == 1, "Collection must not be empty"

        obj = root.children[0]
        assert obj.node_type == "object", "Object must be initialized"
        assert len(obj.children) == 2, "Collection must not be empty"

    def test_parse_nested_object(self, adapter):
        """Test parsing nested objects"""
        json_source = """
        {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "secret"
                }
            }
        }
        """
        adapter.parse(json_source)

        # Navigate to nested structure
        objects = adapter.find_nodes_by_type("object")
        assert len(objects) >= 3, "Objects must not be empty"

    def test_parse_array(self, adapter):
        """Test parsing JSON arrays"""
        json_source = '{"items": ["item1", "item2", "item3"]}'
        adapter.parse(json_source)

        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 1, "Arrays must not be empty"

        array = arrays[0]
        assert len(array.children) == 3, "Collection must not be empty"

    def test_parse_mixed_types(self, adapter):
        """Test parsing various primitive types"""
        json_source = """
        {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": true,
            "null_value": null
        }
        """
        adapter.parse(json_source)

        primitives = adapter.find_nodes_by_type("primitive")
        assert len(primitives) == 5, "Primitives must not be empty"

        # Check metadata for different types
        values = [p.metadata["value"] for p in primitives]
        assert "hello" in values, "Value must be initialized"
        assert 42 in values, "Value must be initialized"
        assert 3.14 in values, "Value must be initialized"
        assert True in values, "Value must be initialized"
        assert None in values, "Value must be initialized"

    def test_parse_empty_object(self, adapter):
        """Test parsing empty JSON object"""
        json_source = "{}"
        root = adapter.parse(json_source)

        assert root.node_type == "document", "node_type is not valid"
        obj = root.children[0]
        assert obj.node_type == "object", "Object must be initialized"
        assert len(obj.children) == 0, "Collection must not be empty"

    def test_parse_empty_array(self, adapter):
        """Test parsing empty JSON array"""
        json_source = '{"items": []}'
        adapter.parse(json_source)

        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 1, "Arrays must not be empty"
        assert len(arrays[0].children) == 0, "Collection must not be empty"

    def test_parse_nested_arrays(self, adapter):
        """Test parsing nested arrays"""
        json_source = '{"matrix": [[1, 2], [3, 4], [5, 6]]}'
        adapter.parse(json_source)

        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 4, "Arrays must not be empty"

    def test_get_value_at_path_simple(self, adapter):
        """Test path-based value retrieval for simple paths"""
        json_source = '{"config": {"host": "localhost", "port": 5432}}'
        adapter.parse(json_source)

        host = adapter.get_value_at_path("config.host")
        assert host == "localhost", "host is not valid"

        port = adapter.get_value_at_path("config.port")
        assert port == 5432, "port is not valid"

    def test_get_value_at_path_nested(self, adapter):
        """Test path-based value retrieval for deeply nested paths"""
        json_source = """
        {
            "app": {
                "database": {
                    "connection": {
                        "host": "db.example.com"
                    }
                }
            }
        }
        """
        adapter.parse(json_source)

        host = adapter.get_value_at_path("app.database.connection.host")
        assert host == "db.example.com", "host is not valid"

    def test_get_value_at_path_not_found(self, adapter):
        """Test path-based retrieval with non-existent path"""
        json_source = '{"key": "value"}'
        adapter.parse(json_source)

        result = adapter.get_value_at_path("nonexistent.path")
        assert result is None, "Result must not be empty"

    def test_find_nodes_by_type(self, adapter):
        """Test finding nodes by type"""
        json_source = """
        {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "settings": {"theme": "dark"}
        }
        """
        adapter.parse(json_source)

        objects = adapter.find_nodes_by_type("object")
        assert len(objects) == 4, "Objects must not be empty"

        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 1, "Arrays must not be empty"

        primitives = adapter.find_nodes_by_type("primitive")
        assert len(primitives) == 5, "Primitives must not be empty"

    def test_get_stats(self, adapter):
        """Test AST statistics generation"""
        json_source = """
        {
            "data": {
                "items": [1, 2, 3]
            }
        }
        """
        adapter.parse(json_source)
        stats = adapter.get_stats()

        assert stats["document"] == 1, "Condition must be true"
        assert stats["object"] == 2, "Object must be initialized"
        assert stats["array"] == 1, "Condition must be true"
        assert stats["primitive"] == 3, "Condition must be true"

    def test_extract_metadata(self, adapter):
        """Test metadata extraction"""
        json_source = '{"key": "value", "number": 42}'
        root = adapter.parse(json_source)

        obj = root.children[0]
        metadata = adapter.extract_metadata(obj)

        assert metadata["node_type"] == "JSON object", "Data must not be empty"
        assert metadata["key_count"] == 2, "Data must not be empty"
        assert "keys" in metadata, "Data must not be empty"

    def test_parse_invalid_json(self, adapter):
        """Test error handling for invalid JSON"""
        invalid_json = '{"key": "value",}'  # Trailing comma

        with pytest.raises(ValueError, match="Failed to parse JSON"):
            adapter.parse(invalid_json)

    def test_traverse(self, adapter):
        """Test tree traversal"""
        json_source = '{"a": {"b": {"c": "value"}}}'
        root = adapter.parse(json_source)

        nodes = list(adapter.traverse(root))
        assert len(nodes) > 0, "Nodes must not be empty"

        # Should contain document, objects, and primitive
        node_types = [n.node_type for n in nodes]
        assert "document" in node_types, "Condition must be true"
        assert "object" in node_types, "Object must be initialized"
        assert "primitive" in node_types, "Condition must be true"

    def test_parse_with_file_path(self, adapter):
        """Test parsing with file path specified"""
        json_source = '{"key": "value"}'
        file_path = Path("/test/data.json")

        root = adapter.parse(json_source, file_path=file_path)
        assert root.file_path == file_path, "file_path is not valid"

    def test_array_indexing_in_path(self, adapter):
        """Test path navigation with array indices"""
        json_source = """
        {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]
        }
        """
        adapter.parse(json_source)

        # Test array index access
        name = adapter.get_value_at_path("users[0].name")
        assert name == "Alice", "name is not valid"

        age = adapter.get_value_at_path("users[1].age")
        assert age == 25, "age is not valid"

        # Test out of bounds index
        result = adapter.get_value_at_path("users[10].name")
        assert result is None, "Result must not be empty"

        # Test invalid index
        result = adapter.get_value_at_path("users[invalid].name")
        assert result is None, "Result must not be empty"

    def test_path_on_empty_adapter(self, adapter):
        """Test get_value_at_path when root is None"""
        result = adapter.get_value_at_path("some.path")
        assert result is None, "Result must not be empty"

    def test_extract_metadata_array(self, adapter):
        """Test metadata extraction for arrays"""
        json_source = '["item1", "item2", "item3"]'
        root = adapter.parse(json_source)

        array = root.children[0]
        metadata = adapter.extract_metadata(array)

        assert metadata["node_type"] == "JSON array", "Data must not be empty"
        assert metadata["element_count"] == 3, "Data must not be empty"

    def test_extract_metadata_primitive(self, adapter):
        """Test metadata extraction for primitives"""
        json_source = '{"text": "hello", "number": 42, "flag": true}'
        root = adapter.parse(json_source)

        obj = root.children[0]
        # Get first primitive (text)
        text_node = obj.children[0]
        metadata = adapter.extract_metadata(text_node)

        assert metadata["node_type"] == "JSON primitive", "Data must not be empty"
        assert "json_type" in metadata, "Data must not be empty"

    def test_deeply_nested_json(self, adapter):
        """Test parsing very deeply nested JSON (10+ levels)"""
        json_source = """
        {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "level6": {
                                    "level7": {
                                        "level8": {
                                            "level9": {
                                                "level10": "deep_value"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        root = adapter.parse(json_source)

        # Verify we can navigate deep
        value = adapter.get_value_at_path(
            "level1.level2.level3.level4.level5.level6.level7.level8.level9.level10"
        )
        assert value == "deep_value", "Value must be initialized"

        # Count depth
        nodes = list(adapter.traverse(root))
        object_nodes = [n for n in nodes if n.node_type == "object"]
        assert len(object_nodes) >= 10, "Object_nodes must not be empty"

    def test_large_array(self, adapter):
        """Test parsing large arrays"""
        # Create a large array with 1000 items
        items = [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        import json

        json_source = json.dumps({"items": items})

        root = adapter.parse(json_source)

        # Verify structure
        obj = root.children[0]
        assert obj.node_type == "object", "Object must be initialized"

        items_array = obj.children[0]
        assert items_array.node_type == "array", "Item must not be empty"
        assert items_array.metadata["length"] == 1000, "Data must not be empty"

        # Verify we can access random items
        value = adapter.get_value_at_path("items[0].id")
        assert value == 0, "Value must be initialized"

        value = adapter.get_value_at_path("items[999].id")
        assert value == 999, "Value must be initialized"

    def test_special_json_values(self, adapter):
        """Test parsing special JSON values"""
        json_source = """
        {
            "null_value": null,
            "empty_string": "",
            "zero": 0,
            "negative": -42,
            "float": 3.14159,
            "scientific": 1.23e-10,
            "true_val": true,
            "false_val": false
        }
        """
        adapter.parse(json_source)

        # Test retrieval of special values
        assert adapter.get_value_at_path("null_value") is None, "Value must be initialized"
        assert adapter.get_value_at_path("empty_string") == "", "Value must be initialized"
        assert adapter.get_value_at_path("zero") == 0, "Value must be initialized"
        assert adapter.get_value_at_path("negative") == -42, "Value must be initialized"
        assert adapter.get_value_at_path("true_val") is True, "Value must be initialized"
        assert adapter.get_value_at_path("false_val") is False, "Value must be initialized"

    def test_unicode_and_escapes(self, adapter):
        """Test parsing JSON with Unicode and escape sequences"""
        json_source = """
        {
            "unicode": "Hello 世界 🌍",
            "escaped": "Line1\\nLine2\\tTabbed",
            "quote": "She said \\"hello\\""
        }
        """
        adapter.parse(json_source)

        unicode_val = adapter.get_value_at_path("unicode")
        assert "世界" in unicode_val, "Condition must be true"
        assert "🌍" in unicode_val, "Condition must be true"

        escaped_val = adapter.get_value_at_path("escaped")
        assert "\\n" in escaped_val or "\n" in escaped_val, "Condition must be true"

    def test_complex_mixed_structure(self, adapter):
        """Test parsing complex mixed data structures"""
        json_source = """
        {
            "config": {
                "name": "MyApp",
                "version": "1.0.0",
                "features": ["auth", "api", "db"],
                "settings": {
                    "debug": true,
                    "timeout": 30,
                    "endpoints": [
                        {"path": "/api/v1", "methods": ["GET", "POST"]},
                        {"path": "/api/v2", "methods": ["GET", "POST", "PUT"]}
                    ]
                }
            }
        }
        """
        root = adapter.parse(json_source)

        # Verify structure
        assert root.node_type == "document", "node_type is not valid"

        # Check node counts
        stats = adapter.get_stats()
        assert stats["object"] >= 4, "Value must be greater than zero"
        assert stats["array"] >= 3, "Value must be greater than zero"
        assert stats["primitive"] >= 10, "Value must be greater than zero"
