"""SHIM Inventory Integration.

Cross-references detected duplicates with .github/SHIM_INVENTORY.yaml
to identify whitelisted duplicates and flag unknowns.
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Tuple, Optional, Dict


@dataclass
class ShimEntry:
    """Entry from SHIM_INVENTORY.yaml."""

    module: str
    legacy_path: str
    canonical_path: str
    owner: str
    status: str
    rationale: str
    deprecation_date: Optional[str]
    whitelist_duplicates: List[str]
    notes: str


@dataclass
class CrossReferenceResult:
    """Result of cross-referencing with SHIM inventory."""

    in_shim_inventory: bool
    is_whitelisted: bool
    shim_status: Optional[str]
    recommendations: List[str] = field(default_factory=list)


class ShimInventoryReader:
    """Reads and parses SHIM_INVENTORY.yaml."""

    def __init__(self, repo_root: Path):
        """Initialize with repository root.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self.shim_path = repo_root / ".github" / "SHIM_INVENTORY.yaml"
        self._entries: Optional[List[ShimEntry]] = None

    def load(self) -> List[ShimEntry]:
        """Load and parse SHIM inventory.

        Returns:
            List of ShimEntry objects

        Raises:
            FileNotFoundError: If SHIM_INVENTORY.yaml not found
            yaml.YAMLError: If YAML is malformed
        """
        if not self.shim_path.exists():
            raise FileNotFoundError(f"SHIM inventory not found: {self.shim_path}")

        with open(self.shim_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        entries = []
        for item in data.get("inventory", []):
            entry = ShimEntry(
                module=item.get("module", ""),
                legacy_path=item.get("legacy_path", ""),
                canonical_path=item.get("canonical_path", ""),
                owner=item.get("owner", ""),
                status=item.get("status", ""),
                rationale=item.get("rationale", ""),
                deprecation_date=item.get("deprecation_date"),
                whitelist_duplicates=item.get("whitelist_duplicates", []),
                notes=item.get("notes", ""),
            )
            entries.append(entry)

        self._entries = entries
        return entries

    def get_whitelisted_paths(self) -> Set[Tuple[str, str]]:
        """Get set of whitelisted (module, path) pairs.

        Returns:
            Set of (module, path) tuples
        """
        if self._entries is None:
            self.load()

        whitelisted = set()
        for entry in self._entries:
            for path in entry.whitelist_duplicates:
                whitelisted.add((entry.module, path))
            # Also add legacy and canonical paths
            if entry.legacy_path:
                whitelisted.add((entry.module, entry.legacy_path))
            if entry.canonical_path:
                whitelisted.add((entry.module, entry.canonical_path))

        return whitelisted

    def get_entries_dict(self) -> Dict[str, ShimEntry]:
        """Get entries indexed by module name.

        Returns:
            Dict mapping module name to ShimEntry
        """
        if self._entries is None:
            self.load()

        return {entry.module: entry for entry in self._entries}


class CrossReference:
    """Cross-references duplicates with SHIM inventory."""

    def __init__(self, shim_entries: List[ShimEntry]):
        """Initialize with SHIM inventory.

        Args:
            shim_entries: List of SHIM inventory entries
        """
        self.shim_entries = shim_entries
        self.entries_dict = {entry.module: entry for entry in shim_entries}
        self.whitelisted_paths = self._build_whitelist()

    def _build_whitelist(self) -> Set[Tuple[str, str]]:
        """Build set of whitelisted (module, path) pairs."""
        whitelisted = set()
        for entry in self.shim_entries:
            for path in entry.whitelist_duplicates:
                whitelisted.add((entry.module, path))
            # Also add legacy and canonical paths
            if entry.legacy_path:
                whitelisted.add((entry.module, entry.legacy_path))
            if entry.canonical_path:
                whitelisted.add((entry.module, entry.canonical_path))
        return whitelisted

    def is_whitelisted(self, module: str, path: str) -> bool:
        """Check if module/path combination is whitelisted.

        Args:
            module: Module name (e.g., "training.engine_hf_trainer")
            path: File path (e.g., "training/engine_hf_trainer.py")

        Returns:
            True if whitelisted, False otherwise
        """
        return (module, path) in self.whitelisted_paths

    def check_paths(
        self, paths: List[str], derive_module: bool = True
    ) -> CrossReferenceResult:
        """Check if paths are in SHIM inventory.

        Args:
            paths: List of file paths
            derive_module: If True, derive module name from path

        Returns:
            CrossReferenceResult with findings
        """
        # Try to find matching SHIM entry
        in_inventory = False
        is_whitelisted = False
        shim_status = None
        recommendations = []

        for path in paths:
            if derive_module:
                # Derive module name from path
                # e.g., "training/engine_hf_trainer.py" -> "training.engine_hf_trainer"
                module = path.replace("/", ".").replace(".py", "")
                if module.startswith("src."):
                    module = module[4:]  # Remove "src." prefix
            else:
                module = None

            # Check if in SHIM inventory
            if module and module in self.entries_dict:
                in_inventory = True
                entry = self.entries_dict[module]
                shim_status = entry.status

                # Check if this specific path is whitelisted
                if self.is_whitelisted(module, path):
                    is_whitelisted = True

        # Generate recommendations
        if not in_inventory:
            recommendations.append(
                "Add to .github/SHIM_INVENTORY.yaml with appropriate status"
            )
            recommendations.append(
                "Or consolidate immediately if not actively used"
            )
        elif not is_whitelisted:
            recommendations.append(
                "Path not whitelisted - add to whitelist_duplicates or consolidate"
            )
        else:
            recommendations.append("Already tracked in SHIM_INVENTORY.yaml")
            if shim_status == "shim":
                recommendations.append(
                    "Consider consolidating after legacy usage declines"
                )

        return CrossReferenceResult(
            in_shim_inventory=in_inventory,
            is_whitelisted=is_whitelisted,
            shim_status=shim_status,
            recommendations=recommendations,
        )

    def get_recommendations(self, paths: List[str]) -> List[str]:
        """Get recommendations for duplicate paths.

        Args:
            paths: List of file paths

        Returns:
            List of recommendation strings
        """
        result = self.check_paths(paths)
        return result.recommendations
