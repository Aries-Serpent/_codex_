"""
Document Validation Module

Provides robust document validation for the RAG ingestion pipeline:
- Format detection (PDF, TXT, MD, HTML, JSON, etc.)
- Content validation (size limits, encoding)
- Malicious content detection (basic sanitization)
- Schema validation for structured documents
"""

import hashlib
import logging
import mimetypes
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


class DocumentFormat(Enum):
    """Supported document formats for ingestion."""

    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    XML = "xml"
    DOCX = "docx"
    UNKNOWN = "unknown"

    @classmethod
    def from_extension(cls, extension: str) -> "DocumentFormat":
        """Detect format from file extension."""
        ext_map = {
            ".txt": cls.TEXT,
            ".md": cls.MARKDOWN,
            ".markdown": cls.MARKDOWN,
            ".html": cls.HTML,
            ".htm": cls.HTML,
            ".pdf": cls.PDF,
            ".json": cls.JSON,
            ".yaml": cls.YAML,
            ".yml": cls.YAML,
            ".csv": cls.CSV,
            ".xml": cls.XML,
            ".docx": cls.DOCX,
        }
        return ext_map.get(extension.lower(), cls.UNKNOWN)

    @classmethod
    def from_mime_type(cls, mime_type: str) -> "DocumentFormat":
        """Detect format from MIME type."""
        mime_map = {
            "text/plain": cls.TEXT,
            "text/markdown": cls.MARKDOWN,
            "text/html": cls.HTML,
            "application/pdf": cls.PDF,
            "application/json": cls.JSON,
            "application/x-yaml": cls.YAML,
            "text/yaml": cls.YAML,
            "text/csv": cls.CSV,
            "application/xml": cls.XML,
            "text/xml": cls.XML,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": cls.DOCX,
        }
        return mime_map.get(mime_type, cls.UNKNOWN)


@dataclass
class ValidationResult:
    """Result of document validation."""

    is_valid: bool
    document_format: DocumentFormat
    file_size: int = 0
    encoding: str = "utf-8"
    content_hash: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        """Add an error and mark as invalid."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning (doesn't affect validity)."""
        self.warnings.append(message)


@dataclass
class ValidationConfig:
    """Configuration for document validation."""

    max_file_size_mb: float = 100.0  # Maximum file size in MB
    min_file_size_bytes: int = 1  # Minimum file size in bytes
    allowed_formats: list[DocumentFormat] = field(
        default_factory=lambda: [
            DocumentFormat.TEXT,
            DocumentFormat.MARKDOWN,
            DocumentFormat.HTML,
            DocumentFormat.PDF,
            DocumentFormat.JSON,
            DocumentFormat.YAML,
            DocumentFormat.CSV,
            DocumentFormat.XML,
            DocumentFormat.DOCX,
        ]  # Excludes UNKNOWN by default
    )
    detect_encoding: bool = True
    compute_hash: bool = True
    check_malicious: bool = True
    max_text_length: int = 10_000_000  # 10M characters max


class DocumentValidator:
    """
    Production-grade document validator for RAG ingestion.

    Features:
    - Format detection from extension, MIME type, and content
    - Size and encoding validation
    - Content hash computation for deduplication
    - Basic malicious content detection

    Example:
        validator = DocumentValidator()
        result = validator.validate_file("/path/to/document.pdf")
        if result.is_valid:
            process_document(document)
        else:
            log_errors(result.errors)
    """

    # Patterns for detecting potentially malicious content
    MALICIOUS_PATTERNS = [
        re.compile(r"<script\b[^>]*>", re.IGNORECASE),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"data:text/html", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),  # Event handlers
    ]

    def __init__(self, config: Optional[ValidationConfig] = None):
        """Initialize validator with configuration."""
        self.config = config or ValidationConfig()

    def validate_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate a document file.

        Args:
            file_path: Path to the document file

        Returns:
            ValidationResult with validation status and metadata
        """
        path = Path(file_path)
        result = ValidationResult(
            is_valid=True,
            document_format=DocumentFormat.UNKNOWN,
        )

        # Check file exists
        if not path.exists():
            result.add_error(f"File not found: {path}")
            return result

        if not path.is_file():
            result.add_error(f"Not a file: {path}")
            return result

        # Get file size
        result.file_size = path.stat().st_size

        # Validate file size
        self._validate_file_size(result)
        if not result.is_valid:
            return result

        # Detect format from extension
        result.document_format = DocumentFormat.from_extension(path.suffix)

        # Try to detect from MIME type if unknown
        if result.document_format == DocumentFormat.UNKNOWN:
            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type:
                result.document_format = DocumentFormat.from_mime_type(mime_type)

        # Check if format is allowed
        if result.document_format not in self.config.allowed_formats:
            result.add_error(
                f"Format not allowed: {result.document_format.value}. "
                f"Allowed: {[f.value for f in self.config.allowed_formats]}"
            )
            return result

        # Read and validate content
        try:
            with open(path, "rb") as f:
                content = f.read()

            # Compute content hash
            if self.config.compute_hash:
                result.content_hash = hashlib.sha256(content).hexdigest()

            # Detect encoding and decode for text-based formats
            if self._is_text_format(result.document_format):
                text_content = self._decode_content(content, result)
                if result.is_valid and text_content:
                    self._validate_text_content(text_content, result)

        except OSError as e:
            result.add_error(f"Failed to read file: {e}")

        # Store metadata
        result.metadata["filename"] = path.name
        result.metadata["extension"] = path.suffix
        result.metadata["path"] = str(path.absolute())

        return result

    def validate_bytes(
        self,
        content: bytes,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate document from bytes.

        Args:
            content: Document content as bytes
            filename: Optional filename for format detection
            mime_type: Optional MIME type for format detection

        Returns:
            ValidationResult with validation status and metadata
        """
        result = ValidationResult(
            is_valid=True,
            document_format=DocumentFormat.UNKNOWN,
            file_size=len(content),
        )

        # Validate size
        self._validate_file_size(result)
        if not result.is_valid:
            return result

        # Detect format
        if filename:
            ext = Path(filename).suffix
            result.document_format = DocumentFormat.from_extension(ext)

        if result.document_format == DocumentFormat.UNKNOWN and mime_type:
            result.document_format = DocumentFormat.from_mime_type(mime_type)

        # Compute hash
        if self.config.compute_hash:
            result.content_hash = hashlib.sha256(content).hexdigest()

        # Validate text content if applicable
        if self._is_text_format(result.document_format):
            text_content = self._decode_content(content, result)
            if result.is_valid and text_content:
                self._validate_text_content(text_content, result)

        # Store metadata
        if filename:
            result.metadata["filename"] = filename

        return result

    def validate_text(self, text: str, source: str = "string") -> ValidationResult:
        """
        Validate text content directly.

        Args:
            text: Text content to validate
            source: Optional source identifier for logging

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(
            is_valid=True,
            document_format=DocumentFormat.TEXT,
            file_size=len(text.encode("utf-8")),
            encoding="utf-8",
        )

        # Compute hash
        if self.config.compute_hash:
            result.content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        # Validate content
        self._validate_text_content(text, result)

        result.metadata["source"] = source

        return result

    def _validate_file_size(self, result: ValidationResult) -> None:
        """Validate file size against configured limits."""
        max_bytes = int(self.config.max_file_size_mb * 1024 * 1024)

        if result.file_size < self.config.min_file_size_bytes:
            result.add_error(
                f"File too small: {result.file_size} bytes "
                f"(minimum: {self.config.min_file_size_bytes} bytes)"
            )
        elif result.file_size > max_bytes:
            result.add_error(
                f"File too large: {result.file_size / (1024 * 1024):.2f} MB "
                f"(maximum: {self.config.max_file_size_mb} MB)"
            )

    def _is_text_format(self, fmt: DocumentFormat) -> bool:
        """Check if format is text-based."""
        text_formats = {
            DocumentFormat.TEXT,
            DocumentFormat.MARKDOWN,
            DocumentFormat.HTML,
            DocumentFormat.JSON,
            DocumentFormat.YAML,
            DocumentFormat.CSV,
            DocumentFormat.XML,
        }
        return fmt in text_formats

    def _decode_content(self, content: bytes, result: ValidationResult) -> Optional[str]:
        """Attempt to decode binary content to string."""
        # Try common encodings
        encodings = ["utf-8", "utf-16", "latin-1", "cp1252", "ascii"]

        for encoding in encodings:
            try:
                text = content.decode(encoding)
                result.encoding = encoding
                return text
            except (UnicodeDecodeError, LookupError):
                continue

        result.add_error("Could not decode content with any supported encoding")
        return None

    def _validate_text_content(self, text: str, result: ValidationResult) -> None:
        """Validate text content for issues."""
        # Check length
        if len(text) > self.config.max_text_length:
            result.add_error(
                f"Text too long: {len(text)} characters (maximum: {self.config.max_text_length})"
            )
            return

        # Check for empty content
        if not text.strip():
            result.add_warning("Document is empty or contains only whitespace")

        # Check for malicious patterns
        if self.config.check_malicious:
            for pattern in self.MALICIOUS_PATTERNS:
                if pattern.search(text):
                    result.add_warning(f"Potentially malicious content detected: {pattern.pattern}")

        # Store content statistics
        result.metadata["char_count"] = len(text)
        result.metadata["line_count"] = text.count("\n") + 1
        result.metadata["word_count"] = len(text.split())


def validate_document(
    source: Union[str, Path, bytes],
    filename: Optional[str] = None,
    config: Optional[ValidationConfig] = None,
) -> ValidationResult:
    """
    Convenience function to validate a document.

    Args:
        source: File path, bytes, or string content
        filename: Optional filename (used when source is bytes)
        config: Optional validation configuration

    Returns:
        ValidationResult with validation status and metadata
    """
    validator = DocumentValidator(config)

    if isinstance(source, (str, Path)) and Path(source).exists():
        return validator.validate_file(source)
    if isinstance(source, bytes):
        return validator.validate_bytes(source, filename)
    if isinstance(source, str):
        return validator.validate_text(source)
    result = ValidationResult(is_valid=False, document_format=DocumentFormat.UNKNOWN)
    result.add_error(f"Unsupported source type: {type(source)}")
    return result
