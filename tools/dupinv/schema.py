"""Schema definitions for supplemental duplicate inventory."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemberFile:
    """Represents a file that is part of a duplicate group."""

    path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    file_hash: str = ""
    normalized_hash: Optional[str] = None
    similarity_score: float = 1.0
    git_blame_top_author: Optional[str] = None
    git_author_email: Optional[str] = None
    churn_last_90_days: Optional[int] = None
    test_coverage: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                result[key] = value
        return result


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate or similar files/code."""

    id: str
    type: str  # exact-file, normalized-file, function-ast, semantic-cluster
    language: Optional[str]
    representative_path: str
    member_files: List[MemberFile]
    reason: str
    suggested_action: str  # refactor, consolidate, vendorize, ignore, whitelist
    confidence: str  # low, medium, high
    tags: List[str]
    meta: Dict[str, Any]
    summary: str
    # SHIM integration fields (added in Phase 7)
    in_shim_inventory: bool = False
    shim_status: Optional[str] = None
    is_whitelisted: bool = False
    shim_recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "language": self.language,
            "representative_path": self.representative_path,
            "member_files": [mf.to_dict() for mf in self.member_files],
            "reason": self.reason,
            "suggested_action": self.suggested_action,
            "confidence": self.confidence,
            "tags": self.tags,
            "meta": self.meta,
            "summary": self.summary,
            "in_shim_inventory": self.in_shim_inventory,
            "shim_status": self.shim_status,
            "is_whitelisted": self.is_whitelisted,
            "shim_recommendations": self.shim_recommendations,
        }

    def validate(self) -> List[str]:
        """Validate the duplicate group, return list of errors."""
        errors = []

        if not self.id:
            errors.append("ID is required")

        if self.type not in [
            "exact-file",
            "normalized-file",
            "function-ast",
            "semantic-cluster",
        ]:
            errors.append(f"Invalid type: {self.type}")

        if self.suggested_action not in [
            "refactor",
            "consolidate",
            "vendorize",
            "ignore",
            "whitelist",
        ]:
            errors.append(f"Invalid suggested_action: {self.suggested_action}")

        if self.confidence not in ["low", "medium", "high"]:
            errors.append(f"Invalid confidence: {self.confidence}")

        if not self.member_files:
            errors.append("At least one member_file is required")

        if len(self.member_files) < 2:
            errors.append("At least two member_files required for a duplicate group")

        return errors


@dataclass
class InventoryMetadata:
    """Metadata for the supplemental inventory."""

    generated_at: str  # ISO8601
    scanner_version: str
    repository_root: str
    detection_modes: List[str]
    total_files_scanned: int
    total_groups: int
    total_violations: int
    scan_duration_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.__dict__.copy()


@dataclass
class SupplementalInventory:
    """Complete supplemental duplicate inventory."""

    metadata: InventoryMetadata
    duplicate_groups: List[DuplicateGroup]
    intentional_duplicates: List[DuplicateGroup] = field(default_factory=list)

    def validate(self) -> List[str]:
        """Validate the entire inventory, return list of errors."""
        errors = []

        # Validate each duplicate group
        for i, group in enumerate(self.duplicate_groups):
            group_errors = group.validate()
            for error in group_errors:
                errors.append(f"Group {i} ({group.id}): {error}")

        # Validate intentional duplicates
        for i, group in enumerate(self.intentional_duplicates):
            group_errors = group.validate()
            for error in group_errors:
                errors.append(f"Intentional group {i} ({group.id}): {error}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metadata": self.metadata.to_dict(),
            "duplicate_groups": [group.to_dict() for group in self.duplicate_groups],
            "intentional_duplicates": [
                group.to_dict() for group in self.intentional_duplicates
            ],
        }
