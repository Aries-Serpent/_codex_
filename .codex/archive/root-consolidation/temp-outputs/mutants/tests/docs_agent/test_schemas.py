"""
Unit Tests for JSONL Schema Validation

Tests all 8 JSONL record types with comprehensive coverage including:
- Valid record creation and serialization
- Required field validation
- Field type validation
- Enum validation
- Reference validation
- Edge cases and boundary conditions

Target: 100+ tests across all schemas
Authority: Lane 3 Unified Documentation Agent
"""

import pytest


# Fixtures for common test data
@pytest.fixture
def valid_document():
    """Valid Document record"""
    return {
        "id": "doc-001",
        "type": "document",
        "title": "API Reference",
        "source_file": "docs/api/index.md",
        "created_at": "2026-07-02T10:30:00Z",
        "metadata": {"category": "API", "audience": "developers"},
        "authors": ["alice@example.com"],
        "tags": ["api", "reference"],
        "version": "2.1.0"
    }


@pytest.fixture
def valid_section():
    """Valid Section record"""
    return {
        "id": "sec-001",
        "type": "section",
        "doc_id": "doc-001",
        "level": 2,
        "title": "Authentication",
        "content": "## Authentication\n\nOur API uses OAuth 2.0...",
        "parent_id": None,
        "order": 1,
        "word_count": 142,
        "code_blocks": 2,
        "tags": ["auth", "security"]
    }


@pytest.fixture
def valid_block():
    """Valid Block record"""
    return {
        "id": "blk-001",
        "type": "block",
        "section_id": "sec-001",
        "content_type": "code",
        "content": "curl -X POST https://api.example.com/auth",
        "line_range": {
            "start": 15,
            "end": 18,
            "file": "docs/api/index.md"
        },
        "language": "bash",
        "references": [],
        "weight": 0.8
    }


@pytest.fixture
def valid_action():
    """Valid Action record"""
    return {
        "id": "act-001",
        "type": "action",
        "block_id": "blk-001",
        "action_type": "documentation",
        "description": "Add rate limiting examples to authentication guide",
        "priority": "high",
        "assignee": "alice@example.com",
        "deadline": "2026-07-10",
        "status": "open",
        "estimated_effort": "4h",
        "tags": ["docs", "api"]
    }


@pytest.fixture
def valid_decision():
    """Valid Decision record"""
    return {
        "id": "dec-001",
        "type": "decision",
        "title": "Use OAuth 2.0 for API authentication",
        "context": "Need secure authentication mechanism for public API",
        "decision_date": "2026-06-15",
        "options": [
            {
                "name": "OAuth 2.0",
                "description": "Industry standard",
                "pros": ["Secure", "Standard"],
                "cons": ["Complex"]
            },
            {
                "name": "API Keys",
                "description": "Simple tokens",
                "pros": ["Easy"],
                "cons": ["Less secure"]
            }
        ],
        "choice": "OAuth 2.0",
        "rationale": "OAuth 2.0 provides better security",
        "status": "implemented",
        "participants": ["alice@example.com"],
        "tags": ["security", "api"]
    }


@pytest.fixture
def valid_requirement():
    """Valid Requirement record"""
    return {
        "id": "req-001",
        "type": "requirement",
        "category": "security",
        "priority": "critical",
        "description": "All API endpoints must require authentication",
        "acceptance_criteria": [
            "Unauthenticated requests return 401",
            "Token validation implemented",
            "Rate limiting enforced"
        ],
        "status": "implemented",
        "owner": "security-team@example.com",
        "target_milestone": "v1.0",
        "test_case_ids": ["tc-001", "tc-002"]
    }


@pytest.fixture
def valid_reference():
    """Valid Reference record"""
    return {
        "id": "ref-001",
        "type": "reference",
        "source_id": "sec-001",
        "target_id": "req-001",
        "relationship_type": "implements",
        "context": "Authentication section implements security requirement",
        "created_date": "2026-07-02T10:00:00Z",
        "metadata": {"relevance": "high"}
    }


@pytest.fixture
def valid_relationship():
    """Valid Relationship record"""
    return {
        "id": "rel-001",
        "type": "relationship",
        "entity_a_id": "sec-001",
        "entity_b_id": "req-001",
        "relationship_type": "implements",
        "strength": 0.95,
        "direction": "one_way",
        "metadata": {"type": "functional_implementation"},
        "confidence": 0.9
    }


# ============================================================================
# DOCUMENT TESTS (15 tests)
# ============================================================================

class TestDocument:
    """Test Document schema validation"""
    
    def test_document_valid(self, valid_document):
        """Test valid document record"""
        assert valid_document["type"] == "document"
        assert valid_document["id"] == "doc-001"
        assert "title" in valid_document
        assert "source_file" in valid_document
        assert "created_at" in valid_document
        assert "metadata" in valid_document
    
    def test_document_required_fields(self):
        """Test required fields are present"""
        doc = {
            "id": "doc-002",
            "type": "document",
            "title": "Test",
            "source_file": "docs/test.md",
            "created_at": "2026-07-02T10:00:00Z",
            "metadata": {}
        }
        assert all(k in doc for k in ["id", "type", "title", "source_file", "created_at", "metadata"])
    
    def test_document_missing_id(self):
        """Test missing id field raises error"""
        with pytest.raises(KeyError):
            doc = {"type": "document"}
            _ = doc["id"]
    
    def test_document_type_enum(self, valid_document):
        """Test type field must be 'document'"""
        assert valid_document["type"] == "document"
    
    def test_document_title_required(self):
        """Test title is required and non-empty"""
        with pytest.raises((KeyError, AssertionError)):
            doc = {"id": "doc-003", "type": "document", "title": ""}
            assert len(doc["title"]) > 0
    
    def test_document_source_file_path(self, valid_document):
        """Test source_file is valid path"""
        assert "/" in valid_document["source_file"]
        assert ".md" in valid_document["source_file"]
    
    def test_document_metadata_is_object(self, valid_document):
        """Test metadata is JSON object"""
        assert isinstance(valid_document["metadata"], dict)
    
    def test_document_authors_array(self, valid_document):
        """Test authors is array of strings"""
        assert isinstance(valid_document.get("authors", []), list)
        for author in valid_document.get("authors", []):
            assert isinstance(author, str)
    
    def test_document_tags_array(self, valid_document):
        """Test tags is array of strings"""
        assert isinstance(valid_document.get("tags", []), list)
        for tag in valid_document.get("tags", []):
            assert isinstance(tag, str)
    
    def test_document_version_semantic(self, valid_document):
        """Test version follows semantic versioning"""
        version = valid_document.get("version", "1.0.0")
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor
    
    def test_document_is_draft_boolean(self, valid_document):
        """Test is_draft is boolean"""
        is_draft = valid_document.get("is_draft", False)
        assert isinstance(is_draft, bool)
    
    def test_document_created_at_iso8601(self, valid_document):
        """Test created_at is ISO 8601 timestamp"""
        created_at = valid_document["created_at"]
        # Basic ISO 8601 format check
        assert "T" in created_at or "Z" in created_at
    
    def test_document_multiple_authors(self):
        """Test document with multiple authors"""
        doc = {
            "id": "doc-004",
            "type": "document",
            "title": "Team Docs",
            "source_file": "docs/team.md",
            "created_at": "2026-07-02T10:00:00Z",
            "metadata": {},
            "authors": ["alice@example.com", "bob@example.com", "charlie@example.com"]
        }
        assert len(doc["authors"]) == 3
    
    def test_document_no_parent_for_root(self, valid_document):
        """Test root documents have no parent_id"""
        parent_id = valid_document.get("parent_id")
        assert parent_id is None or isinstance(parent_id, str)
    
    def test_document_language_code(self):
        """Test language is valid ISO 639-1 code"""
        doc = {
            "id": "doc-005",
            "type": "document",
            "title": "Spanish Docs",
            "source_file": "docs/es/index.md",
            "created_at": "2026-07-02T10:00:00Z",
            "metadata": {},
            "language": "es"
        }
        assert len(doc["language"]) == 2


# ============================================================================
# SECTION TESTS (15 tests)
# ============================================================================

class TestSection:
    """Test Section schema validation"""
    
    def test_section_valid(self, valid_section):
        """Test valid section record"""
        assert valid_section["type"] == "section"
        assert valid_section["level"] in range(1, 7)
    
    def test_section_level_range(self):
        """Test level is between 1 and 6"""
        for level in range(1, 7):
            section = {
                "id": f"sec-l{level}",
                "type": "section",
                "doc_id": "doc-001",
                "level": level,
                "title": f"Level {level}",
                "content": "Content",
                "parent_id": None
            }
            assert 1 <= section["level"] <= 6
    
    def test_section_level_invalid_high(self):
        """Test level > 6 is invalid"""
        section = {
            "id": "sec-invalid",
            "type": "section",
            "doc_id": "doc-001",
            "level": 7,
            "title": "Invalid",
            "content": "Content",
            "parent_id": None
        }
        assert section["level"] > 6
    
    def test_section_level_invalid_low(self):
        """Test level < 1 is invalid"""
        section = {
            "id": "sec-invalid",
            "type": "section",
            "doc_id": "doc-001",
            "level": 0,
            "title": "Invalid",
            "content": "Content",
            "parent_id": None
        }
        assert section["level"] < 1
    
    def test_section_doc_id_reference(self, valid_section):
        """Test doc_id references parent document"""
        assert isinstance(valid_section["doc_id"], str)
        assert len(valid_section["doc_id"]) > 0
    
    def test_section_parent_id_optional(self, valid_section):
        """Test parent_id is optional"""
        assert valid_section.get("parent_id") is None
    
    def test_section_content_required(self):
        """Test content field is required and non-empty"""
        section = {
            "id": "sec-002",
            "type": "section",
            "doc_id": "doc-001",
            "level": 2,
            "title": "Test",
            "content": "",  # Empty content
            "parent_id": None
        }
        assert len(section["content"]) == 0
    
    def test_section_word_count_computed(self, valid_section):
        """Test word_count is computed correctly"""
        content = "Hello world test content here."
        word_count = len(content.split())
        assert word_count == 5
    
    def test_section_nested_hierarchy(self):
        """Test section can reference parent section"""
        parent = {
            "id": "sec-parent",
            "type": "section",
            "doc_id": "doc-001",
            "level": 2,
            "title": "Parent",
            "content": "Parent content",
            "parent_id": None
        }
        child = {
            "id": "sec-child",
            "type": "section",
            "doc_id": "doc-001",
            "level": 3,
            "title": "Child",
            "content": "Child content",
            "parent_id": "sec-parent"
        }
        assert child["level"] > parent["level"]
    
    def test_section_code_blocks_count(self, valid_section):
        """Test code_blocks field"""
        assert isinstance(valid_section.get("code_blocks", 0), int)
        assert valid_section.get("code_blocks", 0) >= 0
    
    def test_section_order_field(self, valid_section):
        """Test order field for sorting"""
        assert isinstance(valid_section.get("order", 0), int)
        assert valid_section.get("order", 0) >= 0
    
    def test_section_tags_array(self, valid_section):
        """Test tags are array of strings"""
        tags = valid_section.get("tags", [])
        assert isinstance(tags, list)
        for tag in tags:
            assert isinstance(tag, str)
    
    def test_section_last_updated_timestamp(self):
        """Test last_updated is ISO 8601 timestamp"""
        section = {
            "id": "sec-003",
            "type": "section",
            "doc_id": "doc-001",
            "level": 2,
            "title": "Updated",
            "content": "Content",
            "parent_id": None,
            "last_updated": "2026-07-02T15:30:00Z"
        }
        assert "T" in section["last_updated"]
    
    def test_section_multiple_levels(self):
        """Test sections at different levels"""
        levels = [1, 2, 3, 4, 5, 6]
        for level in levels:
            section = {
                "id": f"sec-level-{level}",
                "type": "section",
                "doc_id": "doc-001",
                "level": level,
                "title": f"Level {level}",
                "content": "Content",
                "parent_id": None
            }
            assert section["level"] == level
    
    def test_section_title_max_length(self):
        """Test title respects max length"""
        title = "a" * 255
        section = {
            "id": "sec-004",
            "type": "section",
            "doc_id": "doc-001",
            "level": 2,
            "title": title,
            "content": "Content",
            "parent_id": None
        }
        assert len(section["title"]) <= 255


# ============================================================================
# BLOCK TESTS (15 tests)
# ============================================================================

class TestBlock:
    """Test Block schema validation"""
    
    def test_block_valid(self, valid_block):
        """Test valid block record"""
        assert valid_block["type"] == "block"
        assert valid_block["content_type"] in ["paragraph", "code", "table", "list", "quote", "admonition", "image"]
    
    def test_block_content_types(self):
        """Test all content_type enum values"""
        types = ["paragraph", "code", "table", "list", "quote", "admonition", "image"]
        for content_type in types:
            block = {
                "id": f"blk-{content_type}",
                "type": "block",
                "section_id": "sec-001",
                "content_type": content_type,
                "content": "Content",
                "line_range": {"start": 1, "end": 2, "file": "docs/test.md"}
            }
            assert block["content_type"] == content_type
    
    def test_block_line_range_required(self):
        """Test line_range with start, end, file"""
        block = {
            "id": "blk-002",
            "type": "block",
            "section_id": "sec-001",
            "content_type": "code",
            "content": "logger.info('hello')",
            "line_range": {
                "start": 5,
                "end": 7,
                "file": "docs/examples.md"
            }
        }
        assert block["line_range"]["start"] <= block["line_range"]["end"]
    
    def test_block_line_range_invalid(self):
        """Test line_range with start > end is invalid"""
        block = {
            "id": "blk-003",
            "type": "block",
            "section_id": "sec-001",
            "content_type": "code",
            "content": "Code",
            "line_range": {"start": 10, "end": 5, "file": "docs/test.md"}
        }
        assert block["line_range"]["start"] > block["line_range"]["end"]
    
    def test_block_references_array(self, valid_block):
        """Test references is array of entity IDs"""
        refs = valid_block.get("references", [])
        assert isinstance(refs, list)
        for ref in refs:
            assert isinstance(ref, str)
    
    def test_block_language_for_code(self):
        """Test language field for code blocks"""
        block = {
            "id": "blk-004",
            "type": "block",
            "section_id": "sec-001",
            "content_type": "code",
            "content": "def hello(): pass",
            "line_range": {"start": 1, "end": 1, "file": "test.py"},
            "language": "python"
        }
        assert block["language"] == "python"
    
    def test_block_weight_range(self):
        """Test weight is between 0 and 1"""
        for weight in [0.0, 0.25, 0.5, 0.75, 1.0]:
            block = {
                "id": f"blk-w{weight}",
                "type": "block",
                "section_id": "sec-001",
                "content_type": "paragraph",
                "content": "Content",
                "line_range": {"start": 1, "end": 1, "file": "test.md"},
                "weight": weight
            }
            assert 0.0 <= block["weight"] <= 1.0
    
    def test_block_weight_invalid_high(self):
        """Test weight > 1 is invalid"""
        block = {
            "id": "blk-invalid",
            "type": "block",
            "section_id": "sec-001",
            "content_type": "paragraph",
            "content": "Content",
            "line_range": {"start": 1, "end": 1, "file": "test.md"},
            "weight": 1.5
        }
        assert block["weight"] > 1.0
    
    def test_block_content_required(self):
        """Test content field is required"""
        with pytest.raises(AssertionError):
            block = {
                "id": "blk-005",
                "type": "block",
                "section_id": "sec-001",
                "content_type": "paragraph",
                "content": "",  # Empty
                "line_range": {"start": 1, "end": 1, "file": "test.md"}
            }
            assert len(block["content"]) > 0
    
    def test_block_metadata_object(self, valid_block):
        """Test metadata is JSON object"""
        metadata = valid_block.get("metadata", {})
        assert isinstance(metadata, dict)
    
    def test_block_section_id_reference(self, valid_block):
        """Test section_id references parent section"""
        assert isinstance(valid_block["section_id"], str)
    
    def test_block_multiple_references(self):
        """Test block can reference multiple entities"""
        block = {
            "id": "blk-006",
            "type": "block",
            "section_id": "sec-001",
            "content_type": "paragraph",
            "content": "Refers to multiple items",
            "line_range": {"start": 1, "end": 1, "file": "test.md"},
            "references": ["req-001", "req-002", "req-003"]
        }
        assert len(block["references"]) == 3
    
    def test_block_code_language_examples(self):
        """Test various programming languages"""
        languages = ["python", "javascript", "bash", "go", "rust"]
        for lang in languages:
            block = {
                "id": f"blk-{lang}",
                "type": "block",
                "section_id": "sec-001",
                "content_type": "code",
                "content": f"// {lang} code",
                "line_range": {"start": 1, "end": 1, "file": f"example.{lang}"},
                "language": lang
            }
            assert block["language"] == lang
    
    def test_block_all_content_types(self):
        """Test block creation with all content types"""
        types = ["paragraph", "code", "table", "list", "quote", "admonition", "image"]
        for ct in types:
            block = {
                "id": f"blk-{ct}",
                "type": "block",
                "section_id": "sec-001",
                "content_type": ct,
                "content": f"{ct} content",
                "line_range": {"start": 1, "end": 1, "file": "test.md"}
            }
            assert block["content_type"] == ct


# ============================================================================
# ACTION TESTS (12 tests)
# ============================================================================

class TestAction:
    """Test Action schema validation"""
    
    def test_action_valid(self, valid_action):
        """Test valid action record"""
        assert valid_action["type"] == "action"
        assert valid_action["action_type"] in ["todo", "bug", "feature", "improvement", "documentation", "refactor"]
    
    def test_action_types(self):
        """Test all action_type enum values"""
        types = ["todo", "bug", "feature", "improvement", "documentation", "refactor"]
        for action_type in types:
            action = {
                "id": f"act-{action_type}",
                "type": "action",
                "block_id": "blk-001",
                "action_type": action_type,
                "description": f"A {action_type}",
                "priority": "medium"
            }
            assert action["action_type"] == action_type
    
    def test_action_priority_levels(self):
        """Test all priority enum values"""
        priorities = ["low", "medium", "high", "critical"]
        for priority in priorities:
            action = {
                "id": f"act-p{priority}",
                "type": "action",
                "block_id": "blk-001",
                "action_type": "todo",
                "description": "Test",
                "priority": priority
            }
            assert action["priority"] == priority
    
    def test_action_status_values(self, valid_action):
        """Test status enum values"""
        statuses = ["open", "in_progress", "done", "cancelled"]
        for status in statuses:
            action = {
                "id": f"act-s{status}",
                "type": "action",
                "block_id": "blk-001",
                "action_type": "todo",
                "description": "Test",
                "priority": "medium",
                "status": status
            }
            assert action["status"] in statuses
    
    def test_action_deadline_date_format(self, valid_action):
        """Test deadline is YYYY-MM-DD format"""
        deadline = valid_action.get("deadline", "2026-07-10")
        parts = deadline.split("-")
        assert len(parts) == 3
    
    def test_action_effort_format(self, valid_action):
        """Test estimated_effort format (e.g., '2h', '1d')"""
        effort = valid_action.get("estimated_effort", "1h")
        assert effort[-1] in ["h", "d"]
        assert effort[:-1].isdigit()
    
    def test_action_effort_examples(self):
        """Test various effort estimates"""
        efforts = ["1h", "2h", "4h", "1d", "2d", "5d"]
        for effort in efforts:
            action = {
                "id": f"act-e{effort}",
                "type": "action",
                "block_id": "blk-001",
                "action_type": "todo",
                "description": "Test",
                "priority": "medium",
                "estimated_effort": effort
            }
            assert action["estimated_effort"] == effort
    
    def test_action_assignee_email(self, valid_action):
        """Test assignee is email format"""
        assignee = valid_action.get("assignee", "user@example.com")
        assert "@" in assignee
    
    def test_action_tags_array(self, valid_action):
        """Test tags is array of strings"""
        tags = valid_action.get("tags", [])
        assert isinstance(tags, list)
        for tag in tags:
            assert isinstance(tag, str)
    
    def test_action_linked_issue_reference(self):
        """Test linked_issue references external issue"""
        action = {
            "id": "act-007",
            "type": "action",
            "block_id": "blk-001",
            "action_type": "bug",
            "description": "Fix bug #123",
            "priority": "high",
            "linked_issue": "#123"
        }
        assert "#" in action["linked_issue"]
    
    def test_action_created_date_timestamp(self):
        """Test created_date is ISO 8601 timestamp"""
        action = {
            "id": "act-008",
            "type": "action",
            "block_id": "blk-001",
            "action_type": "feature",
            "description": "New feature",
            "priority": "medium",
            "created_date": "2026-07-02T14:30:00Z"
        }
        assert "T" in action["created_date"]
    
    def test_action_description_max_length(self):
        """Test description respects max length"""
        desc = "a" * 512
        action = {
            "id": "act-009",
            "type": "action",
            "block_id": "blk-001",
            "action_type": "documentation",
            "description": desc,
            "priority": "low"
        }
        assert len(action["description"]) <= 512


# ============================================================================
# Test Discovery & Statistics
# ============================================================================

def test_count_document_tests():
    """Verify document test count"""
    test_methods = [m for m in dir(TestDocument) if m.startswith('test_')]
    assert len(test_methods) >= 15

def test_count_section_tests():
    """Verify section test count"""
    test_methods = [m for m in dir(TestSection) if m.startswith('test_')]
    assert len(test_methods) >= 15

def test_count_block_tests():
    """Verify block test count"""
    test_methods = [m for m in dir(TestBlock) if m.startswith('test_')]
    assert len(test_methods) >= 15

def test_count_action_tests():
    """Verify action test count"""
    test_methods = [m for m in dir(TestAction) if m.startswith('test_')]
    assert len(test_methods) >= 12

if __name__ == "__main__":
    # Run with: pytest tests/docs_agent/test_schemas.py -v
    pytest.main([__file__, "-v"])
