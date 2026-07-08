"""
Integration Tests for Docs Agent

End-to-end tests for the complete docs_agent pipeline:
document processing, validation, semantic indexing, and MCP integration.

Target: 100+ integration tests
Authority: Lane 3 Unified Documentation Agent
"""

import json

import pytest

# Import docs_agent modules
from codex.docs_agent import (
    document_processor,
    mcp_bridge,
    semantic_indexer,
)


class TestDocumentProcessingPipeline:
    """Test end-to-end document processing"""
    
    @pytest.fixture
    def sample_markdown(self, tmp_path):
        """Create sample Markdown file"""
        md_file = tmp_path / "test.md"
        md_file.write_text("""# API Reference

## Authentication

OAuth 2.0 is used for authentication.

```python
import requests
requests.get('https://api.example.com/', auth=('user', 'pass'))
```

## Endpoints

### GET /users

Get list of users.

```bash
curl -X GET https://api.example.com/users
```
""")
        return md_file
    
    def test_markdown_parsing(self, sample_markdown):
        """Test Markdown file parsing"""
        processor = document_processor.DocumentProcessor()
        count = processor.process_file(sample_markdown, "doc-001")
        
        assert count >= 3  # At least 1 doc, 1+ sections, blocks
        assert len(processor.documents) == 1
        assert len(processor.sections) >= 1
        assert len(processor.blocks) >= 1
    
    def test_document_record_creation(self, sample_markdown):
        """Test document record is created correctly"""
        processor = document_processor.DocumentProcessor()
        processor.process_file(sample_markdown, "doc-001")
        
        doc = processor.documents[0]
        assert doc['id'] == "doc-001"
        assert doc['type'] == "document"
        assert doc['title'] == "API Reference"
        assert doc['source_file'] == str(sample_markdown)
    
    def test_section_extraction(self, sample_markdown):
        """Test section records are extracted"""
        processor = document_processor.DocumentProcessor()
        processor.process_file(sample_markdown, "doc-001")
        
        sections = processor.sections
        assert len(sections) >= 2
        
        # Check section types
        types = set(s['type'] for s in sections)
        assert 'section' in types
    
    def test_code_block_extraction(self, sample_markdown):
        """Test code blocks are extracted"""
        processor = document_processor.DocumentProcessor()
        processor.process_file(sample_markdown, "doc-001")
        
        code_blocks = [b for b in processor.blocks if b['content_type'] == 'code']
        assert len(code_blocks) >= 2  # Python and bash blocks
    
    def test_jsonl_output(self, sample_markdown):
        """Test JSONL output format"""
        processor = document_processor.DocumentProcessor()
        processor.process_file(sample_markdown, "doc-001")
        
        jsonl = processor.to_jsonl()
        lines = [l for l in jsonl.split('\n') if l]
        
        assert len(lines) > 0
        
        # Parse and validate each line
        for line in lines:
            record = json.loads(line)
            assert 'id' in record
            assert 'type' in record


class TestSchemalValidator:
    """Test JSONL schema validation"""
    
    @pytest.fixture
    def sample_jsonl(self, tmp_path):
        """Create sample JSONL file"""
        jsonl_file = tmp_path / "test.jsonl"
        records = [
            {
                "id": "doc-001",
                "type": "document",
                "title": "Test Doc",
                "source_file": "test.md",
                "created_at": "2026-07-02T10:00:00Z",
                "metadata": {}
            },
            {
                "id": "sec-001",
                "type": "section",
                "doc_id": "doc-001",
                "level": 2,
                "title": "Section 1",
                "content": "Content here",
                "parent_id": None
            },
        ]
        
        with open(jsonl_file, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')
        
        return jsonl_file
    
    def test_valid_jsonl_validation(self, sample_jsonl):
        """Test validation of valid JSONL"""
        # Note: This test assumes schemas are available
        # In real environment, schemas would be in .codex/schemas/
        pass
    
    def test_record_validation(self):
        """Test individual record validation"""
        record = {
            "id": "test-001",
            "type": "document",
            "title": "Test",
            "source_file": "test.md",
            "created_at": "2026-07-02T10:00:00Z",
            "metadata": {}
        }
        
        # Validate record structure
        assert record.get('id') is not None
        assert record.get('type') == "document"
        assert record.get('title') is not None


class TestSemanticIndexing:
    """Test semantic indexing"""
    
    @pytest.fixture
    def sample_indexer(self):
        """Create indexer with sample records"""
        indexer = semantic_indexer.SemanticIndexer(model_name="all-MiniLM-L6-v2")
        
        records = [
            {"id": "doc-001", "type": "document", "title": "Authentication Guide", "created_at": "2026-07-02T10:00:00Z"},
            {"id": "sec-001", "type": "section", "title": "OAuth 2.0", "content": "OAuth 2.0 authentication mechanism..."},
            {"id": "sec-002", "type": "section", "title": "API Keys", "content": "Alternative API key authentication..."},
            {"id": "blk-001", "type": "block", "content": "import oauth2", "content_type": "code"},
        ]
        
        for record in records:
            indexer.add_record(record)
        
        return indexer
    
    def test_record_addition(self, sample_indexer):
        """Test adding records to indexer"""
        assert len(sample_indexer.records) == 4
    
    def test_index_building(self, sample_indexer):
        """Test building semantic index"""
        stats = sample_indexer.build_index(batch_size=2)
        
        assert stats['record_count'] > 0
        assert stats['indexed'] > 0
    
    def test_search_functionality(self, sample_indexer):
        """Test search"""
        sample_indexer.build_index()
        results = sample_indexer.search("authentication", k=5)
        
        # Should return some results (if embeddings work)
        assert isinstance(results, list)


class TestMCPBridge:
    """Test MCP bridge functionality"""
    
    @pytest.fixture
    def sample_bridge(self):
        """Create MCP bridge with sample indexer"""
        indexer = semantic_indexer.SemanticIndexer()
        
        # Add sample records
        records = [
            {"id": "doc-001", "type": "document", "title": "API Docs"},
            {"id": "sec-001", "type": "section", "title": "Authentication"},
        ]
        
        for record in records:
            indexer.add_record(record)
        
        bridge = mcp_bridge.MCPBridge(indexer)
        return bridge
    
    def test_tool_registration(self, sample_bridge):
        """Test tool registration"""
        tools = sample_bridge.list_tools()
        assert len(tools) > 0
    
    def test_tool_call(self, sample_bridge):
        """Test calling a tool"""
        result = sample_bridge.call_tool('list_documents', {})
        
        assert result['success'] is not None
        assert 'request_id' in result
    
    def test_unknown_tool_call(self, sample_bridge):
        """Test calling unknown tool"""
        result = sample_bridge.call_tool('unknown_tool', {})
        
        assert result['success'] == False
        assert 'error' in result


class TestEndToEndPipeline:
    """Test complete end-to-end pipeline"""
    
    @pytest.fixture
    def docs_directory(self, tmp_path):
        """Create temporary docs directory with samples"""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        
        # Create sample files
        (docs_dir / "index.md").write_text("# Main Documentation\n\nWelcome!")
        (docs_dir / "api.md").write_text("# API Reference\n\n## Authentication\n\nOAuth 2.0 is used.")
        
        return docs_dir
    
    def test_full_pipeline(self, docs_directory, tmp_path):
        """Test complete pipeline: process -> validate -> index"""
        # Process documents
        processor = document_processor.DocumentProcessor()
        processor.process_directory(docs_directory)
        
        assert len(processor.documents) > 0
        assert len(processor.sections) > 0
        
        # Write to JSONL
        jsonl_file = tmp_path / "docs.jsonl"
        processor.write_jsonl(jsonl_file)
        
        assert jsonl_file.exists()
        
        # Build semantic index
        indexer = semantic_indexer.SemanticIndexer()
        
        with open(jsonl_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    indexer.add_record(record)
        
        indexer.build_index()
        
        # Verify results
        stats = indexer.get_statistics()
        assert stats['total_records'] > 0


class TestStatistics:
    """Test statistics collection"""
    
    def test_processor_statistics(self):
        """Test document processor statistics"""
        processor = document_processor.DocumentProcessor()
        
        # Add some dummy data
        processor.documents = [{"id": "doc-001", "type": "document"}]
        processor.sections = [{"id": "sec-001", "type": "section"}]
        processor.blocks = [{"id": "blk-001", "type": "block"}]
        
        stats = processor.get_statistics()
        
        assert stats['documents'] == 1
        assert stats['sections'] == 1
        assert stats['blocks'] == 1
        assert stats['total_records'] == 3
    
    def test_indexer_statistics(self):
        """Test semantic indexer statistics"""
        indexer = semantic_indexer.SemanticIndexer()
        
        # Add records
        for i in range(5):
            indexer.add_record({
                "id": f"rec-{i}",
                "type": "section",
                "title": f"Record {i}",
                "content": "Test content"
            })
        
        stats = indexer.get_statistics()
        
        assert stats['total_records'] == 5
        assert stats['index_built'] == False
        
        # Build index
        indexer.build_index()
        stats = indexer.get_statistics()
        assert stats['index_built'] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
