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
        return JSONASTAdapter()

    def test_init(self, adapter):
        """Test adapter initialization"""
        assert adapter is not None
        assert adapter.root_node is None

    def test_parse_simple_object(self, adapter):
        """Test parsing simple key-value pairs"""
        json_source = '{"key1": "value1", "key2": "value2"}'
        root = adapter.parse(json_source)

        assert root.node_type == "document"
        assert len(root.children) == 1

        obj = root.children[0]
        assert obj.node_type == "object"
        assert len(obj.children) == 2

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
        assert len(objects) >= 3  # Root, database, credentials

    def test_parse_array(self, adapter):
        """Test parsing JSON arrays"""
        json_source = '{"items": ["item1", "item2", "item3"]}'
        adapter.parse(json_source)

        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 1

        array = arrays[0]
        assert len(array.children) == 3

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
        assert len(primitives) == 5

        # Check metadata for different types
        values = [p.metadata["value"] for p in primitives]
        assert "hello" in values
        assert 42 in values
        assert 3.14 in values
        assert True in values
        assert None in values

    def test_parse_empty_object(self, adapter):
        """Test parsing empty JSON object"""
        json_source = "{}"
        root = adapter.parse(json_source)

        assert root.node_type == "document"
        obj = root.children[0]
        assert obj.node_type == "object"
        assert len(obj.children) == 0

    def test_parse_empty_array(self, adapter):
        """Test parsing empty JSON array"""
        json_source = '{"items": []}'
        adapter.parse(json_source)

        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 1
        assert len(arrays[0].children) == 0

    def test_parse_nested_arrays(self, adapter):
        """Test parsing nested arrays"""
        json_source = '{"matrix": [[1, 2], [3, 4], [5, 6]]}'
        adapter.parse(json_source)

        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 4  # 1 outer + 3 inner

    def test_get_value_at_path_simple(self, adapter):
        """Test path-based value retrieval for simple paths"""
        json_source = '{"config": {"host": "localhost", "port": 5432}}'
        adapter.parse(json_source)

        host = adapter.get_value_at_path("config.host")
        assert host == "localhost"

        port = adapter.get_value_at_path("config.port")
        assert port == 5432

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
        assert host == "db.example.com"

    def test_get_value_at_path_not_found(self, adapter):
        """Test path-based retrieval with non-existent path"""
        json_source = '{"key": "value"}'
        adapter.parse(json_source)

        result = adapter.get_value_at_path("nonexistent.path")
        assert result is None

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
        assert len(objects) == 4  # Root + settings + 2 user objects

        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 1

        primitives = adapter.find_nodes_by_type("primitive")
        assert len(primitives) == 5  # 2 names + 2 ages + 1 theme

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

        assert stats["document"] == 1
        assert stats["object"] == 2
        assert stats["array"] == 1
        assert stats["primitive"] == 3

    def test_extract_metadata(self, adapter):
        """Test metadata extraction"""
        json_source = '{"key": "value", "number": 42}'
        root = adapter.parse(json_source)

        obj = root.children[0]
        metadata = adapter.extract_metadata(obj)

        assert metadata["node_type"] == "JSON object"
        assert metadata["key_count"] == 2
        assert "keys" in metadata

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
        assert len(nodes) > 0

        # Should contain document, objects, and primitive
        node_types = [n.node_type for n in nodes]
        assert "document" in node_types
        assert "object" in node_types
        assert "primitive" in node_types

    def test_parse_with_file_path(self, adapter):
        """Test parsing with file path specified"""
        json_source = '{"key": "value"}'
        file_path = Path("/test/data.json")

        root = adapter.parse(json_source, file_path=file_path)
        assert root.file_path == file_path

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
        assert name == "Alice"

        age = adapter.get_value_at_path("users[1].age")
        assert age == 25

        # Test out of bounds index
        result = adapter.get_value_at_path("users[10].name")
        assert result is None

        # Test invalid index
        result = adapter.get_value_at_path("users[invalid].name")
        assert result is None

    def test_path_on_empty_adapter(self, adapter):
        """Test get_value_at_path when root is None"""
        result = adapter.get_value_at_path("some.path")
        assert result is None

    def test_extract_metadata_array(self, adapter):
        """Test metadata extraction for arrays"""
        json_source = '["item1", "item2", "item3"]'
        root = adapter.parse(json_source)

        array = root.children[0]
        metadata = adapter.extract_metadata(array)

        assert metadata["node_type"] == "JSON array"
        assert metadata["element_count"] == 3

    def test_extract_metadata_primitive(self, adapter):
        """Test metadata extraction for primitives"""
        json_source = '{"text": "hello", "number": 42, "flag": true}'
        root = adapter.parse(json_source)

        obj = root.children[0]
        # Get first primitive (text)
        text_node = obj.children[0]
        metadata = adapter.extract_metadata(text_node)

        assert metadata["node_type"] == "JSON primitive"
        assert "json_type" in metadata

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
        assert value == "deep_value"

        # Count depth
        nodes = list(adapter.traverse(root))
        object_nodes = [n for n in nodes if n.node_type == "object"]
        assert len(object_nodes) >= 10

    def test_large_array(self, adapter):
        """Test parsing large arrays"""
        # Create a large array with 1000 items
        items = [{"id": i, "value": f"item_{i}"} for i in range(1000)]
        import json

        json_source = json.dumps({"items": items})

        root = adapter.parse(json_source)

        # Verify structure
        obj = root.children[0]
        assert obj.node_type == "object"

        items_array = obj.children[0]
        assert items_array.node_type == "array"
        assert items_array.metadata["length"] == 1000

        # Verify we can access random items
        value = adapter.get_value_at_path("items[0].id")
        assert value == 0

        value = adapter.get_value_at_path("items[999].id")
        assert value == 999

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
        assert adapter.get_value_at_path("null_value") is None
        assert adapter.get_value_at_path("empty_string") == ""
        assert adapter.get_value_at_path("zero") == 0
        assert adapter.get_value_at_path("negative") == -42
        assert adapter.get_value_at_path("true_val") is True
        assert adapter.get_value_at_path("false_val") is False

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
        assert "世界" in unicode_val
        assert "🌍" in unicode_val

        escaped_val = adapter.get_value_at_path("escaped")
        assert "\\n" in escaped_val or "\n" in escaped_val

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
        assert root.node_type == "document"

        # Check node counts
        stats = adapter.get_stats()
        assert stats["object"] >= 4
        assert stats["array"] >= 3
        assert stats["primitive"] >= 10
