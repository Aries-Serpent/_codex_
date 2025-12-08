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
        
        # Initialize available detectors
        self._init_detectors()

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
        
        # Other detectors will be added in later phases
        # self.detectors["normalized"] = NormalizedDetector(...)
        # self.detectors["ast"] = ASTDetector(...)
        # self.detectors["semantic"] = SemanticDetector(...)

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
        inventory = SupplementalInventory(
            metadata=metadata,
            duplicate_groups=all_groups,
            intentional_duplicates=[],  # Will be populated in Phase 6
        )
        
        return inventory

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
