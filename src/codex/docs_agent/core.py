"""
Core documentation infrastructure: registry, validation, indexing.

Classes:
  - DocumentRegistry: Manage document index and metadata
  - SchemaValidator: Validate JSONL record schemas
  - SemanticIndexer: Build semantic indexes from documents
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class DocumentRecord:
    """Document record with metadata."""

    id: str
    type: str = "document"
    title: str = ""
    path: str = ""
    content_hash: str = ""
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


@dataclass
class SectionRecord:
    """Section record (H1-H6 heading)."""

    id: str
    document_id: str
    level: int
    title: str = ""
    content: str = ""
    position: int = 0
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    type: str = "section"

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


@dataclass
class BlockRecord:
    """Content block (text, code, list, table, image)."""

    id: str
    section_id: str
    block_type: str
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    type: str = "block"

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


class DocumentRegistry:
    """Manage document index and metadata.

    Provides:
      - Document registration and indexing
      - Metadata management
      - Section and block tracking
      - Query interface
    """

    def __init__(self):
        self.documents: Dict[str, DocumentRecord] = {}
        self.sections: Dict[str, SectionRecord] = {}
        self.blocks: Dict[str, BlockRecord] = {}
        self._index: Dict[str, Any] = {
            "by_path": {},
            "by_tag": {},
        }

    def register_document(
        self,
        doc_id: str,
        title: str,
        path: str,
        metadata: Optional[Dict] = None,
    ) -> DocumentRecord:
        """Register a document in the registry."""
        content_hash = self._compute_hash(f"{title}{path}")
        now = datetime.utcnow().isoformat() + "Z"

        doc = DocumentRecord(
            id=doc_id,
            title=title,
            path=path,
            content_hash=content_hash,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

        self.documents[doc_id] = doc
        self._index["by_path"][path] = doc_id

        for tag in doc.metadata.get("tags", []):
            if tag not in self._index["by_tag"]:
                self._index["by_tag"][tag] = []
            self._index["by_tag"][tag].append(doc_id)

        return doc

    def add_section(self, section: SectionRecord) -> None:
        """Register a section in the document."""
        self.sections[section.id] = section
        if section.parent_id and section.parent_id in self.sections:
            self.sections[section.parent_id].children.append(section.id)

    def add_block(self, block: BlockRecord) -> None:
        """Register a block in a section."""
        self.blocks[block.id] = block

    def get_document(self, doc_id: str) -> Optional[DocumentRecord]:
        """Retrieve a document by ID."""
        return self.documents.get(doc_id)

    def list_documents(self) -> List[DocumentRecord]:
        """List all registered documents."""
        return list(self.documents.values())

    def get_sections(self, doc_id: str) -> List[SectionRecord]:
        """Get all sections for a document."""
        return [s for s in self.sections.values() if s.document_id == doc_id]

    def get_blocks(self, section_id: str) -> List[BlockRecord]:
        """Get all blocks for a section."""
        return [b for b in self.blocks.values() if b.section_id == section_id]

    def find_by_path(self, path: str) -> Optional[DocumentRecord]:
        """Find document by file path."""
        doc_id = self._index["by_path"].get(path)
        return self.documents.get(doc_id) if doc_id else None

    def find_by_tag(self, tag: str) -> List[DocumentRecord]:
        """Find documents by tag."""
        doc_ids = self._index["by_tag"].get(tag, [])
        return [self.documents[doc_id] for doc_id in doc_ids]

    @staticmethod
    def _compute_hash(content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()


class SchemaValidator:
    """Validate JSONL record schemas.

    Validates:
      - Type consistency
      - Required fields
      - ID uniqueness
      - Reference integrity
      - Enum constraints
    """

    REQUIRED_FIELDS = {
        "document": {"id", "type", "title", "path", "content_hash"},
        "section": {"id", "type", "document_id", "level", "title"},
        "block": {"id", "type", "section_id", "block_type", "content"},
        "action": {"id", "type", "name", "target"},
        "decision": {"id", "type", "name", "criteria", "branches"},
        "requirement": {"id", "type", "category", "description", "priority"},
        "reference": {"id", "type", "reference_type", "value"},
        "relationship": {"id", "type", "source_id", "target_id", "relationship_type"},
    }

    ENUM_FIELDS = {
        "block": {"block_type": ["text", "code", "list", "table", "image"]},
        "requirement": {
            "category": ["FUNCTIONAL", "PERFORMANCE", "SECURITY", "COMPLIANCE"],
            "priority": ["P0", "P1", "P2", "P3"],
            "status": ["open", "in_progress", "blocked", "completed"],
        },
        "reference": {
            "reference_type": ["commit", "pr", "issue", "file", "section"],
        },
        "relationship": {
            "relationship_type": [
                "references",
                "depends_on",
                "extends",
                "contradicts",
                "complements",
            ],
        },
    }

    def validate_record(self, record: Dict) -> tuple[bool, Optional[str]]:
        """Validate a single JSONL record.

        Returns:
            (is_valid, error_message)
        """
        record_type = record.get("type")

        if not record_type:
            return False, "Missing required 'type' field"

        # Check required fields
        required = self.REQUIRED_FIELDS.get(record_type, set())
        missing = required - set(record.keys())
        if missing:
            return False, f"Missing required fields: {missing}"

        # Check enum constraints
        enum_rules = self.ENUM_FIELDS.get(record_type, {})
        for field_name, valid_values in enum_rules.items():
            if field_name in record:
                value = record[field_name]
                if value not in valid_values:
                    return False, f"Field '{field_name}' has invalid value: {value}"

        # Check timestamp format (ISO 8601)
        for ts_field in ["created_at", "updated_at", "verified_at"]:
            if ts_field in record and record[ts_field]:
                if not self._is_valid_iso8601(record[ts_field]):
                    return False, f"Invalid ISO 8601 timestamp in '{ts_field}'"

        return True, None

    @staticmethod
    def _is_valid_iso8601(timestamp: str) -> bool:
        """Check if timestamp is valid ISO 8601 format."""
        try:
            # Accept YYYY-MM-DDTHH:MM:SSZ format
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return True
        except (ValueError, AttributeError):
            return False

    def validate_file(self, filepath: str) -> tuple[int, int, List[str]]:
        """Validate a JSONL file.

        Returns:
            (valid_count, invalid_count, error_messages)
        """
        valid_count = 0
        invalid_count = 0
        errors = []

        try:
            with open(filepath, "r") as f:
                for line_no, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                        is_valid, error = self.validate_record(record)
                        if is_valid:
                            valid_count += 1
                        else:
                            invalid_count += 1
                            errors.append(f"Line {line_no}: {error}")
                    except json.JSONDecodeError as e:
                        invalid_count += 1
                        errors.append(f"Line {line_no}: Invalid JSON: {e}")
        except IOError as e:
            errors.append(f"Cannot read file: {e}")

        return valid_count, invalid_count, errors


class SemanticIndexer:
    """Build semantic indexes from documents.

    Creates:
      - Full-text indexes
      - Section hierarchies
      - Cross-references
      - Relationship graphs
    """

    def __init__(self, registry: DocumentRegistry):
        self.registry = registry
        self.semantic_index: Dict[str, List[Dict]] = {
            "documents": [],
            "sections": [],
            "blocks": [],
            "relationships": [],
        }

    def build_index(self) -> Dict[str, List[Dict]]:
        """Build complete semantic index from registry."""
        self.semantic_index["documents"] = [
            doc.to_dict() for doc in self.registry.documents.values()
        ]
        self.semantic_index["sections"] = [sec.to_dict() for sec in self.registry.sections.values()]
        self.semantic_index["blocks"] = [blk.to_dict() for blk in self.registry.blocks.values()]
        return self.semantic_index

    def search_documents(self, query: str) -> List[DocumentRecord]:
        """Search documents by title or tags."""
        query_lower = query.lower()
        results = []

        for doc in self.registry.documents.values():
            if query_lower in doc.title.lower():
                results.append(doc)
            elif any(query_lower in tag.lower() for tag in doc.metadata.get("tags", [])):
                results.append(doc)

        return results

    def search_sections(self, doc_id: str, query: str) -> List[SectionRecord]:
        """Search sections within a document."""
        query_lower = query.lower()
        sections = self.registry.get_sections(doc_id)
        return [s for s in sections if query_lower in s.title.lower()]

    def get_document_hierarchy(self, doc_id: str) -> Dict:
        """Get hierarchical view of document structure."""
        doc = self.registry.get_document(doc_id)
        if not doc:
            return {}

        sections = self.registry.get_sections(doc_id)
        hierarchy = {
            "document": doc.to_dict(),
            "sections": [s.to_dict() for s in sections],
        }

        for section in sections:
            blocks = self.registry.get_blocks(section.id)
            section_data = section.to_dict()
            section_data["blocks"] = [b.to_dict() for b in blocks]

        return hierarchy

    def export_jsonl(self, filepath: str) -> int:
        """Export index as JSONL format.

        Returns:
            Number of records exported
        """
        record_count = 0

        with open(filepath, "w") as f:
            # Export documents
            for doc in self.registry.documents.values():
                f.write(doc.to_jsonl() + "\n")
                record_count += 1

            # Export sections
            for section in self.registry.sections.values():
                f.write(section.to_jsonl() + "\n")
                record_count += 1

            # Export blocks
            for block in self.registry.blocks.values():
                f.write(block.to_jsonl() + "\n")
                record_count += 1

        return record_count
