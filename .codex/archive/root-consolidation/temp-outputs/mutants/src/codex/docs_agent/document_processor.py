"""
Document Processor Module for Docs Agent

Converts Markdown documentation files to JSONL format with automatic
extraction of sections, blocks, and metadata.

Authority: Lane 3 Unified Documentation Agent
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class DocumentRecord:
    """Document record (top-level)"""

    id: str
    type: str = "document"
    title: str = ""
    source_file: str = ""
    created_at: str = ""
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat() + "Z"


@dataclass
class SectionRecord:
    """Section record (hierarchical)"""

    id: str
    type: str = "section"
    doc_id: str = ""
    level: int = 1
    title: str = ""
    content: str = ""
    parent_id: Optional[str] = None
    order: int = 0
    word_count: int = 0
    code_blocks: int = 0


@dataclass
class BlockRecord:
    """Block record (atomic content)"""

    id: str
    type: str = "block"
    section_id: str = ""
    content_type: str = "paragraph"
    content: str = ""
    line_range: Optional[Dict[str, Any]] = None
    language: Optional[str] = None
    references: Optional[List[str]] = None


class MarkdownParser:
    """Parses Markdown files and extracts structured records"""

    def __init__(self, source_file: Path):
        """Initialize with source Markdown file

        Args:
            source_file: Path to Markdown file
        """
        self.source_file = source_file
        self.content = source_file.read_text(encoding="utf-8")
        self.lines = self.content.split("\n")
        self.title = self._extract_title()

    def _extract_title(self) -> str:
        """Extract title from first H1 heading or filename"""
        for line in self.lines:
            if line.startswith("# "):
                return line[2:].strip()
        return self.source_file.stem.replace("_", " ").title()

    def parse(self, doc_id: str) -> Tuple[DocumentRecord, List[SectionRecord], List[BlockRecord]]:
        """Parse Markdown file into records

        Args:
            doc_id: Document ID

        Returns:
            Tuple of (document, sections, blocks)
        """
        doc_rec = self._create_document_record(doc_id)
        section_recs = []
        block_recs = []

        current_section: Optional[Dict[str, Any]] = None
        current_content: List[str] = []
        line_start: Optional[int] = None
        section_order = 0

        for line_no, line in enumerate(self.lines, 1):
            # Check for heading
            if line.startswith("#"):
                # Save previous section if any
                if current_section and current_content:
                    assert line_start is not None
                    section_recs.append(current_section)
                    blocks = self._extract_blocks_from_content(
                        current_section["id"], current_content, line_start
                    )
                    block_recs.extend(blocks)

                # Create new section
                level = len(line) - len(line.lstrip("#"))
                title = line.lstrip("#").strip()
                section_id = f"sec-{doc_id}-{section_order}"

                current_section = {
                    "id": section_id,
                    "type": "section",
                    "doc_id": doc_id,
                    "level": level,
                    "title": title,
                    "content": "",
                    "parent_id": None,
                    "order": section_order,
                }
                current_content = []
                line_start = line_no
                section_order += 1

            elif current_section:
                current_content.append(line)

        # Save final section
        if current_section and current_content:
            assert line_start is not None
            section_recs.append(current_section)
            blocks = self._extract_blocks_from_content(
                current_section["id"], current_content, line_start
            )
            block_recs.extend(blocks)

        # Update section content and compute stats
        for section in section_recs:
            section["content"] = "\n".join(current_content)
            section["word_count"] = len(section["content"].split())
            section["code_blocks"] = len(re.findall(r"```", section["content"]))

        return doc_rec, section_recs, block_recs

    def _create_document_record(self, doc_id: str) -> Dict[str, Any]:
        """Create document record"""
        return {
            "id": doc_id,
            "type": "document",
            "title": self.title,
            "source_file": str(self.source_file),
            "created_at": datetime.now().isoformat() + "Z",
            "metadata": {
                "file_size": len(self.content),
                "line_count": len(self.lines),
            },
        }

    def _extract_blocks_from_content(
        self, section_id: str, content_lines: List[str], start_line: int
    ) -> List[Dict[str, Any]]:
        """Extract content blocks from section content

        Args:
            section_id: Parent section ID
            content_lines: Lines of content
            start_line: Starting line number

        Returns:
            List of block records
        """
        blocks = []
        current_block = None
        block_start = 0
        block_order = 0

        for line_idx, line in enumerate(content_lines):
            # Detect code blocks
            if line.strip().startswith("```"):
                if current_block is None:
                    # Start code block
                    current_block = {
                        "type": "code",
                        "language": line.strip()[3:].strip() or "plaintext",
                        "lines": [],
                        "start": start_line + line_idx,
                    }
                    block_start = line_idx
                else:
                    # End code block
                    content_text = "\n".join(current_block["lines"])
                    block_id = f"blk-{section_id}-{block_order}"

                    blocks.append(
                        {
                            "id": block_id,
                            "type": "block",
                            "section_id": section_id,
                            "content_type": "code",
                            "content": content_text,
                            "line_range": {
                                "start": current_block["start"] + 1,
                                "end": start_line + line_idx,
                                "file": str(self.source_file),
                            },
                            "language": current_block["language"],
                        }
                    )
                    current_block = None
                    block_order += 1

            elif current_block:
                current_block["lines"].append(line)

        return blocks


class DocumentProcessor:
    """Processes Markdown documentation files to JSONL"""

    def __init__(self):
        """Initialize processor"""
        self.documents = []
        self.sections = []
        self.blocks = []

    def process_file(self, source_file: Path, doc_id: str) -> int:
        """Process a single Markdown file

        Args:
            source_file: Path to Markdown file
            doc_id: Document ID to assign

        Returns:
            Number of records created
        """
        logger.info(f"Processing: {source_file}")

        parser = MarkdownParser(source_file)
        doc, sections, blocks = parser.parse(doc_id)

        self.documents.append(doc)
        self.sections.extend(sections)
        self.blocks.extend(blocks)

        count = 1 + len(sections) + len(blocks)
        logger.info(
            f"  Created {count} records (1 doc, {len(sections)} sections, {len(blocks)} blocks)"
        )

        return count

    def process_directory(self, docs_dir: Path, prefix: str = "doc") -> int:
        """Process all Markdown files in directory

        Args:
            docs_dir: Path to directory
            prefix: ID prefix (default: "doc")

        Returns:
            Total number of records created
        """
        total = 0
        doc_count = 0

        for md_file in docs_dir.rglob("*.md"):
            doc_id = f"{prefix}-{doc_count}"
            total += self.process_file(md_file, doc_id)
            doc_count += 1

        logger.info(f"Processed {doc_count} files, created {total} total records")
        return total

    def to_jsonl(self) -> str:
        """Export all records as JSONL string

        Returns:
            JSONL formatted string
        """
        lines = []

        for doc in self.documents:
            lines.append(json.dumps(doc))

        for section in self.sections:
            lines.append(json.dumps(section))

        for block in self.blocks:
            lines.append(json.dumps(block))

        return "\n".join(lines)

    def write_jsonl(self, output_file: Path):
        """Write records to JSONL file

        Args:
            output_file: Path to output file
        """
        output_file.write_text(self.to_jsonl(), encoding="utf-8")
        logger.info(
            f"Wrote {len(self.documents) + len(self.sections) + len(self.blocks)} records to {output_file}"
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics

        Returns:
            Dictionary with statistics
        """
        return {
            "documents": len(self.documents),
            "sections": len(self.sections),
            "blocks": len(self.blocks),
            "total_records": len(self.documents) + len(self.sections) + len(self.blocks),
        }
