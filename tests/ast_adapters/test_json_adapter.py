"""
Tests for JSON AST Adapter.
"""

import pytest
from pathlib import Path

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
        json_source = '''
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
        '''
        root = adapter.parse(json_source)
        
        # Navigate to nested structure
        objects = adapter.find_nodes_by_type("object")
        assert len(objects) >= 3  # Root, database, credentials
    
    def test_parse_array(self, adapter):
        """Test parsing JSON arrays"""
        json_source = '{"items": ["item1", "item2", "item3"]}'
        root = adapter.parse(json_source)
        
        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 1
        
        array = arrays[0]
        assert len(array.children) == 3
    
    def test_parse_mixed_types(self, adapter):
        """Test parsing various primitive types"""
        json_source = '''
        {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": true,
            "null_value": null
        }
        '''
        root = adapter.parse(json_source)
        
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
        json_source = '{}'
        root = adapter.parse(json_source)
        
        assert root.node_type == "document"
        obj = root.children[0]
        assert obj.node_type == "object"
        assert len(obj.children) == 0
    
    def test_parse_empty_array(self, adapter):
        """Test parsing empty JSON array"""
        json_source = '{"items": []}'
        root = adapter.parse(json_source)
        
        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 1
        assert len(arrays[0].children) == 0
    
    def test_parse_nested_arrays(self, adapter):
        """Test parsing nested arrays"""
        json_source = '{"matrix": [[1, 2], [3, 4], [5, 6]]}'
        root = adapter.parse(json_source)
        
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
        json_source = '''
        {
            "app": {
                "database": {
                    "connection": {
                        "host": "db.example.com"
                    }
                }
            }
        }
        '''
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
        json_source = '''
        {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "settings": {"theme": "dark"}
        }
        '''
        root = adapter.parse(json_source)
        
        objects = adapter.find_nodes_by_type("object")
        assert len(objects) == 4  # Root + settings + 2 user objects
        
        arrays = adapter.find_nodes_by_type("array")
        assert len(arrays) == 1
        
        primitives = adapter.find_nodes_by_type("primitive")
        assert len(primitives) == 5  # 2 names + 2 ages + 1 theme
    
    def test_get_stats(self, adapter):
        """Test AST statistics generation"""
        json_source = '''
        {
            "data": {
                "items": [1, 2, 3]
            }
        }
        '''
        root = adapter.parse(json_source)
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
    
    def test_complex_mixed_structure(self, adapter):
        """Test parsing complex mixed data structures"""
        json_source = '''
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
        '''
        root = adapter.parse(json_source)
        
        # Verify structure
        assert root.node_type == "document"
        
        # Check node counts
        stats = adapter.get_stats()
        assert stats["object"] >= 4
        assert stats["array"] >= 3
        assert stats["primitive"] >= 10
