"""
Tests for YAML AST Adapter.
"""

import pytest

from codex.ast_adapters.yaml_adapter import YAMLASTAdapter


class TestYAMLASTAdapter:
    """Test suite for YAMLASTAdapter"""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance"""
        return YAMLASTAdapter()

    def test_init(self, adapter):
        """Test adapter initialization"""
        assert adapter is not None, "adapter must be initialized"
        assert adapter.root_node is None, "root_node is not valid"

    def test_parse_simple_mapping(self, adapter):
        """Test parsing simple key-value pairs"""
        yaml_source = """
key1: value1
key2: value2
"""
        root = adapter.parse(yaml_source)

        assert root.node_type == "document", "node_type is not valid"
        assert len(root.children) == 1, "Collection must not be empty"

        mapping = root.children[0]
        assert mapping.node_type == "mapping", "node_type is not valid"
        assert len(mapping.children) == 2, "Collection must not be empty"

    def test_parse_nested_mapping(self, adapter):
        """Test parsing nested mappings"""
        yaml_source = """
database:
  host: localhost
  port: 5432
  credentials:
    username: admin
    password: secret
"""
        adapter.parse(yaml_source)

        # Navigate to nested structure
        mappings = adapter.find_nodes_by_type("mapping")
        assert len(mappings) >= 3, "Mappings must not be empty"

    def test_parse_sequence(self, adapter):
        """Test parsing YAML sequences (lists)"""
        yaml_source = """
items:
  - item1
  - item2
  - item3
"""
        adapter.parse(yaml_source)

        sequences = adapter.find_nodes_by_type("sequence")
        assert len(sequences) == 1, "Sequences must not be empty"

        sequence = sequences[0]
        assert len(sequence.children) == 3, "Collection must not be empty"

    def test_parse_mixed_types(self, adapter):
        """Test parsing various scalar types"""
        yaml_source = """
string: hello
integer: 42
float: 3.14
boolean: true
null_value: null
"""
        adapter.parse(yaml_source)

        scalars = adapter.find_nodes_by_type("scalar")
        assert len(scalars) == 5, "Scalars must not be empty"

        # Check value types
        values = [node.metadata.get("value") for node in scalars]
        assert "hello" in values, "Value must be initialized"
        assert 42 in values, "Value must be initialized"
        assert 3.14 in values, "Value must be initialized"
        assert True in values, "Value must be initialized"
        assert None in values, "Value must be initialized"

    def test_traverse(self, adapter):
        """Test depth-first traversal"""
        yaml_source = """
parent:
  child1: value1
  child2: value2
"""
        root = adapter.parse(yaml_source)

        all_nodes = adapter.traverse(root)
        assert len(all_nodes) > 0, "All_nodes must not be empty"
        assert all_nodes[0] == root, "Condition must be true"

    def test_find_nodes_by_type(self, adapter):
        """Test finding nodes by type"""
        yaml_source = """
config:
  servers:
    - host: server1
      port: 8080
    - host: server2
      port: 8081
"""
        adapter.parse(yaml_source)

        mappings = adapter.find_nodes_by_type("mapping")
        sequences = adapter.find_nodes_by_type("sequence")
        scalars = adapter.find_nodes_by_type("scalar")

        assert len(mappings) >= 1, "Mappings must not be empty"
        assert len(sequences) >= 1, "Sequences must not be empty"
        assert len(scalars) >= 1, "Scalars must not be empty"

    def test_get_value_at_path(self, adapter):
        """Test retrieving value by path"""
        yaml_source = """
config:
  database:
    host: localhost
    port: 5432
"""
        adapter.parse(yaml_source)

        host = adapter.get_value_at_path("config.database.host")
        port = adapter.get_value_at_path("config.database.port")

        assert host == "localhost", "host is not valid"
        assert port == 5432, "port is not valid"

    def test_get_value_at_path_not_found(self, adapter):
        """Test path lookup for non-existent path"""
        yaml_source = """
config:
  value: test
"""
        adapter.parse(yaml_source)

        result = adapter.get_value_at_path("config.nonexistent")
        assert result is None, "Result must not be empty"

    def test_get_keys(self, adapter):
        """Test extracting keys from mapping"""
        yaml_source = """
database:
  host: localhost
  port: 5432
  user: admin
"""
        root = adapter.parse(yaml_source)

        # Get keys from root mapping
        mapping = root.children[0]
        keys = adapter.get_keys(mapping)

        assert "database" in keys, "Data must not be empty"

    def test_parse_empty_document(self, adapter):
        """Test parsing empty YAML"""
        yaml_source = ""
        root = adapter.parse(yaml_source)

        assert root.node_type == "document", "node_type is not valid"
        assert len(root.children) == 0, "Collection must not be empty"

    def test_parse_with_comments(self, adapter):
        """Test that comments are ignored (YAML safe_load behavior)"""
        yaml_source = """
# This is a comment
key: value  # inline comment
"""
        adapter.parse(yaml_source)

        # Comments should not create nodes
        scalars = adapter.find_nodes_by_type("scalar")
        assert len(scalars) == 1, "Scalars must not be empty"
        assert scalars[0].metadata.get("value") == "value", "Data must not be empty"

    def test_invalid_yaml(self, adapter):
        """Test handling of invalid YAML"""
        yaml_source = """
invalid: [unmatched bracket
"""
        with pytest.raises(ValueError, match="Failed to parse YAML"):
            adapter.parse(yaml_source)

    def test_metadata_extraction(self, adapter):
        """Test metadata is properly extracted"""
        yaml_source = """
items:
  - item1
  - item2
"""
        adapter.parse(yaml_source)

        sequence = adapter.find_nodes_by_type("sequence")[0]

        assert "length" in sequence.metadata, "Data must not be empty"
        assert sequence.metadata["length"] == 2, "Data must not be empty"
        assert "item_types" in sequence.metadata, "Data must not be empty"

    def test_parent_child_relationships(self, adapter):
        """Test that parent-child relationships are maintained"""
        yaml_source = """
parent:
  child: value
"""
        root = adapter.parse(yaml_source)

        mapping = root.children[0]
        assert mapping.parent == root, "parent is not valid"

        if mapping.children:
            child = mapping.children[0]
            assert child.parent == mapping, "parent is not valid"

    def test_complex_nested_structure(self, adapter):
        """Test parsing complex nested structure"""
        yaml_source = """
application:
  name: MyApp
  version: 1.0.0
  environments:
    production:
      servers:
        - host: prod1.example.com
          port: 443
        - host: prod2.example.com
          port: 443
    staging:
      servers:
        - host: staging.example.com
          port: 8080
"""
        root = adapter.parse(yaml_source)

        # Verify structure
        all_nodes = adapter.traverse(root)
        assert len(all_nodes) > 10, "All_nodes must not be empty"

        # Verify we can navigate to deep values
        adapter.get_value_at_path("application.environments.production.servers")
        # Note: path won't work for sequences, but structure is valid

    def test_traverse_empty_adapter(self, adapter):
        """Test traverse when root is None"""
        result = adapter.traverse(None)
        assert result == [], "Result must not be empty"

    def test_find_nodes_empty_adapter(self, adapter):
        """Test find_nodes_by_type when root is None"""
        result = adapter.find_nodes_by_type("mapping")
        assert result == [], "Result must not be empty"

    def test_get_keys_empty(self, adapter):
        """Test get_keys with None node"""
        result = adapter.get_keys(None)
        assert result == [], "Result must not be empty"

    def test_get_keys_wrong_type(self, adapter):
        """Test get_keys with non-mapping node"""
        yaml_source = "- item1\n- item2"
        root = adapter.parse(yaml_source)
        sequence = root.children[0]

        result = adapter.get_keys(sequence)
        assert result == [], "Result must not be empty"

    def test_extract_metadata_mapping(self, adapter):
        """Test metadata extraction for mapping nodes"""
        yaml_source = """
config:
  host: localhost
  port: 5432
"""
        root = adapter.parse(yaml_source)
        mapping = root.children[0]

        metadata = adapter.extract_metadata(mapping)
        assert metadata["node_type"] == "mapping", "Data must not be empty"
        assert "keys" in metadata, "Data must not be empty"
        assert "size" in metadata, "Data must not be empty"

    def test_extract_metadata_sequence(self, adapter):
        """Test metadata extraction for sequence nodes"""
        yaml_source = """
items:
  - value1
  - value2
  - value3
"""
        root = adapter.parse(yaml_source)
        mapping = root.children[0]
        sequence = mapping.children[0]

        metadata = adapter.extract_metadata(sequence)
        assert metadata["node_type"] == "sequence", "Data must not be empty"
        assert "length" in metadata, "Data must not be empty"
        assert "item_types" in metadata, "Data must not be empty"

    def test_extract_metadata_scalar(self, adapter):
        """Test metadata extraction for scalar nodes"""
        yaml_source = """
text: hello
number: 42
flag: true
"""
        root = adapter.parse(yaml_source)
        mapping = root.children[0]
        scalar = mapping.children[0]  # First scalar

        metadata = adapter.extract_metadata(scalar)
        assert metadata["node_type"] == "scalar", "Data must not be empty"
        assert "value" in metadata, "Data must not be empty"
        assert "value_type" in metadata, "Data must not be empty"
        assert "is_null" in metadata, "Data must not be empty"

    def test_yaml_with_comments(self, adapter):
        """Test parsing YAML with comments"""
        yaml_source = """
# Configuration file
database:
  # Production database
  host: localhost  # Hostname
  port: 5432       # Default PostgreSQL port
"""
        adapter.parse(yaml_source)

        # Comments should be ignored, structure should be valid
        host = adapter.get_value_at_path("database.host")
        assert host == "localhost", "host is not valid"
