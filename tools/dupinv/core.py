"""
Core scanner module for duplicate detection.

This module coordinates all detection engines and manages the scanning process.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .exact_detector import ExactDetector
from .schema import DuplicateGroup, InventoryMetadata, SupplementalInventory
from .shim_integration import CrossReference, ShimInventoryReader


class DuplicateScanner:
    """
    Main coordinator for duplicate detection.

    Manages multiple detection engines and produces comprehensive
    supplemental inventory.
    """

    def __init__(self, root_path: Path, config: Optional[Dict] = None):
        """
        Initialize scanner with repository root and configuration.

        Args:
            root_path: Path to repository root
            config: Optional configuration dictionary
        """
        self.root_path = Path(root_path).resolve()
        self.config = config or {}
        self.detectors = {}
        self.cross_reference = None
        self.git_metadata = None

        # Initialize git metadata collector (Phase 5)
        from .git_metadata import GitMetadataCollector

        try:
            self.git_metadata = GitMetadataCollector(self.root_path)
        except Exception:
            self.git_metadata = None

        # Initialize SHIM inventory integration
        self._init_shim_integration()

        # Initialize available detectors
        self._init_detectors()

    def _init_shim_integration(self):
        """Initialize SHIM inventory integration."""
        import logging

        logger = logging.getLogger(__name__)

        try:
            reader = ShimInventoryReader(self.root_path)
            shim_entries = reader.load()
            self.cross_reference = CrossReference(shim_entries)
        except FileNotFoundError:
            # SHIM inventory not found - continue without it
            self.cross_reference = None
            logger.debug("SHIM inventory not found, continuing without cross-reference")
        except Exception as e:
            # Log error but continue
            logger.warning(f"Failed to load SHIM inventory: {e}")
            self.cross_reference = None

    def _init_detectors(self):
        """Initialize detection engines based on configuration."""
        # Always include exact detector
        exclude_patterns = self.config.get("exclude_patterns", [])
        respect_gitignore = self.config.get("respect_gitignore", True)

        self.detectors["exact"] = ExactDetector(
            self.root_path,
            exclude_patterns=exclude_patterns,
            respect_gitignore=respect_gitignore,
        )

        # Add normalized detector (Phase 2)
        from .normalize import NormalizedDetector

        normalize_identifiers = self.config.get("normalize_identifiers", False)
        self.detectors["normalized"] = NormalizedDetector(
            self.root_path,
            exclude_patterns=exclude_patterns,
            respect_gitignore=respect_gitignore,
            normalize_identifiers=normalize_identifiers,
        )

        # Add AST detector (Phase 3)
        from .ast_detector import ASTDetector

        similarity_threshold = self.config.get("ast_similarity_threshold", 0.85)
        self.detectors["ast"] = ASTDetector(
            self.root_path,
            similarity_threshold=similarity_threshold,
            exclude_patterns=exclude_patterns,
            respect_gitignore=respect_gitignore,
        )

        # Add semantic detector (Phase 4)
        from .semantic_detector import MinHashDetector

        semantic_threshold = self.config.get("semantic_threshold", 0.75)
        self.detectors["semantic"] = MinHashDetector(
            self.root_path,
            threshold=semantic_threshold,
            exclude_patterns=exclude_patterns,
            respect_gitignore=respect_gitignore,
        )

        # Other detectors will be added in later phases

    def _apply_shim_cross_reference(self, groups: List[DuplicateGroup]) -> List[DuplicateGroup]:
        """
        Apply SHIM inventory cross-reference to duplicate groups.

        Args:
            groups: List of duplicate groups

        Returns:
            Updated list of duplicate groups with SHIM data populated
        """
        for group in groups:
            # Extract file paths from member files
            paths = [member.path for member in group.member_files]

            # Cross-reference with SHIM inventory
            result = self.cross_reference.check_paths(paths, derive_module=True)

            # Update group with SHIM data
            group.in_shim_inventory = result.in_shim_inventory
            group.is_whitelisted = result.is_whitelisted
            group.shim_status = result.shim_status
            group.shim_recommendations = result.recommendations

        return groups

    def _apply_git_metadata(self, groups: List[DuplicateGroup]) -> List[DuplicateGroup]:
        """
        Enrich duplicate groups with git metadata.

        Args:
            groups: List of duplicate groups

        Returns:
            Updated list with git metadata
        """
        for group in groups:
            for member in group.member_files:
                # Construct full path
                file_path = self.root_path / member.path

                if file_path.exists():
                    # Enrich with git metadata
                    self.git_metadata.enrich_member_file(member, file_path)

        return groups

    def scan(self, modes: List[str] = None) -> SupplementalInventory:
        """
        Scan repository for duplicates using specified detection modes.

        Args:
            modes: List of detection modes to use.
                   Options: ["exact", "normalized", "ast", "semantic"]
                   If None, uses all available modes.

        Returns:
            Complete supplemental inventory
        """
        start_time = time.time()

        # Determine which modes to run
        if modes is None:
            modes = list(self.detectors.keys())

        # Validate modes
        invalid_modes = set(modes) - set(self.detectors.keys())
        if invalid_modes:
            raise ValueError(f"Invalid detection modes: {invalid_modes}")

        # Run each detector
        all_groups = []
        files_scanned = set()

        for mode in modes:
            detector = self.detectors[mode]
            groups = detector.scan()
            all_groups.extend(groups)

            # Track scanned files
            for group in groups:
                for member in group.member_files:
                    files_scanned.add(member.path)

        # Apply SHIM cross-reference to all groups
        if self.cross_reference:
            all_groups = self._apply_shim_cross_reference(all_groups)

        # Apply git metadata enrichment (Phase 5)
        if self.git_metadata:
            all_groups = self._apply_git_metadata(all_groups)

        # Calculate duration
        duration = time.time() - start_time

        # Create metadata
        from . import __version__

        metadata = InventoryMetadata(
            generated_at=datetime.utcnow().isoformat() + "Z",
            scanner_version=__version__,
            repository_root=str(self.root_path),
            detection_modes=modes,
            total_files_scanned=len(files_scanned),
            total_groups=len(all_groups),
            total_violations=len(all_groups),  # Will be refined after SHIM integration
            scan_duration_seconds=round(duration, 2),
        )

        # Create inventory
        return SupplementalInventory(
            metadata=metadata,
            duplicate_groups=all_groups,
            intentional_duplicates=[],  # Will be populated in Phase 6
        )


    def write_outputs(
        self, inventory: SupplementalInventory, output_dir: Path, formats: List[str] = None
    ):
        """
        Write inventory to output files.

        Args:
            inventory: Supplemental inventory to write
            output_dir: Directory to write outputs to
            formats: List of formats to write (yaml, json, csv, markdown)
                     If None, writes all formats.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if formats is None:
            formats = ["yaml", "json", "csv", "markdown"]

        # Import writer (will be created in next step)
        try:
            from .output import InventoryWriter

            writer = InventoryWriter()

            if "yaml" in formats:
                writer.write_yaml(inventory, output_dir / "SUPPLEMENTAL_DUPLICATE_INVENTORY.yaml")
            if "json" in formats:
                writer.write_json(inventory, output_dir / "supplemental_duplicates.json")
            if "csv" in formats:
                writer.write_csv(inventory, output_dir / "supplemental_duplicates.csv")
            if "markdown" in formats:
                writer.write_markdown(inventory, output_dir / "supplemental_duplicates.md")

        except ImportError:
            # Fallback: write simple YAML manually
            import yaml

            with open(output_dir / "SUPPLEMENTAL_DUPLICATE_INVENTORY.yaml", "w") as f:
                yaml.dump(inventory.to_dict(), f, default_flow_style=False, sort_keys=False)
