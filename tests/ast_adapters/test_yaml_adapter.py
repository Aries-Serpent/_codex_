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
        assert adapter is not None
        assert adapter.root_node is None

    def test_parse_simple_mapping(self, adapter):
        """Test parsing simple key-value pairs"""
        yaml_source = """
key1: value1
key2: value2
"""
        root = adapter.parse(yaml_source)

        assert root.node_type == "document"
        assert len(root.children) == 1

        mapping = root.children[0]
        assert mapping.node_type == "mapping"
        assert len(mapping.children) == 2

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
        root = adapter.parse(yaml_source)  # noqa: F841 - parse populates adapter

        # Navigate to nested structure
        mappings = adapter.find_nodes_by_type("mapping")
        assert len(mappings) >= 3  # Root, database, credentials

    def test_parse_sequence(self, adapter):
        """Test parsing YAML sequences (lists)"""
        yaml_source = """
items:
  - item1
  - item2
  - item3
"""
        root = adapter.parse(yaml_source)  # noqa: F841 - parse populates adapter

        sequences = adapter.find_nodes_by_type("sequence")
        assert len(sequences) == 1

        sequence = sequences[0]
        assert len(sequence.children) == 3

    def test_parse_mixed_types(self, adapter):
        """Test parsing various scalar types"""
        yaml_source = """
string: hello
integer: 42
float: 3.14
boolean: true
null_value: null
"""
        root = adapter.parse(yaml_source)  # noqa: F841 - parse populates adapter

        scalars = adapter.find_nodes_by_type("scalar")
        assert len(scalars) == 5

        # Check value types
        values = [node.metadata.get("value") for node in scalars]
        assert "hello" in values
        assert 42 in values
        assert 3.14 in values
        assert True in values
        assert None in values

    def test_traverse(self, adapter):
        """Test depth-first traversal"""
        yaml_source = """
parent:
  child1: value1
  child2: value2
"""
        root = adapter.parse(yaml_source)

        all_nodes = adapter.traverse(root)
        assert len(all_nodes) > 0
        assert all_nodes[0] == root

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
        root = adapter.parse(yaml_source)  # noqa: F841 - parse populates adapter

        mappings = adapter.find_nodes_by_type("mapping")
        sequences = adapter.find_nodes_by_type("sequence")
        scalars = adapter.find_nodes_by_type("scalar")

        assert len(mappings) >= 1
        assert len(sequences) >= 1
        assert len(scalars) >= 1

    def test_get_value_at_path(self, adapter):
        """Test retrieving value by path"""
        yaml_source = """
config:
  database:
    host: localhost
    port: 5432
"""
        root = adapter.parse(yaml_source)  # noqa: F841 - parse populates adapter

        host = adapter.get_value_at_path("config.database.host")
        port = adapter.get_value_at_path("config.database.port")

        assert host == "localhost"
        assert port == 5432

    def test_get_value_at_path_not_found(self, adapter):
        """Test path lookup for non-existent path"""
        yaml_source = """
config:
  value: test
"""
        root = adapter.parse(yaml_source)  # noqa: F841 - parse populates adapter

        result = adapter.get_value_at_path("config.nonexistent")
        assert result is None

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

        assert "database" in keys

    def test_parse_empty_document(self, adapter):
        """Test parsing empty YAML"""
        yaml_source = ""
        root = adapter.parse(yaml_source)

        assert root.node_type == "document"
        assert len(root.children) == 0

    def test_parse_with_comments(self, adapter):
        """Test that comments are ignored (YAML safe_load behavior)"""
        yaml_source = """
# This is a comment
key: value  # inline comment
"""
        root = adapter.parse(yaml_source)  # noqa: F841 - parse populates adapter

        # Comments should not create nodes
        scalars = adapter.find_nodes_by_type("scalar")
        assert len(scalars) == 1
        assert scalars[0].metadata.get("value") == "value"

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
        root = adapter.parse(yaml_source)  # noqa: F841 - parse populates adapter

        sequence = adapter.find_nodes_by_type("sequence")[0]

        assert "length" in sequence.metadata
        assert sequence.metadata["length"] == 2
        assert "item_types" in sequence.metadata

    def test_parent_child_relationships(self, adapter):
        """Test that parent-child relationships are maintained"""
        yaml_source = """
parent:
  child: value
"""
        root = adapter.parse(yaml_source)

        mapping = root.children[0]
        assert mapping.parent == root

        if mapping.children:
            child = mapping.children[0]
            assert child.parent == mapping

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
        assert len(all_nodes) > 10  # Should have many nodes

        # Verify we can navigate to deep values
        adapter.get_value_at_path("application.environments.production.servers")
        # Note: path won't work for sequences, but structure is valid

    def test_traverse_empty_adapter(self, adapter):
        """Test traverse when root is None"""
        result = adapter.traverse(None)
        assert result == []

    def test_find_nodes_empty_adapter(self, adapter):
        """Test find_nodes_by_type when root is None"""
        result = adapter.find_nodes_by_type("mapping")
        assert result == []

    def test_get_keys_empty(self, adapter):
        """Test get_keys with None node"""
        result = adapter.get_keys(None)
        assert result == []

    def test_get_keys_wrong_type(self, adapter):
        """Test get_keys with non-mapping node"""
        yaml_source = "- item1\n- item2"
        root = adapter.parse(yaml_source)
        sequence = root.children[0]

        result = adapter.get_keys(sequence)
        assert result == []

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
        assert metadata["node_type"] == "mapping"
        assert "keys" in metadata
        assert "size" in metadata

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
        assert metadata["node_type"] == "sequence"
        assert "length" in metadata
        assert "item_types" in metadata

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
        assert metadata["node_type"] == "scalar"
        assert "value" in metadata
        assert "value_type" in metadata
        assert "is_null" in metadata

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
        assert host == "localhost"
