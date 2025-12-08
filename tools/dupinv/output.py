"""Output writers for supplemental inventory."""

import csv
import json
from pathlib import Path
from typing import List

import yaml

from .schema import SupplementalInventory


class InventoryWriter:
    """Writes duplicate inventory to multiple formats."""

    def write_yaml(self, inventory: SupplementalInventory, path: Path):
        """
        Write inventory to YAML file.

        Args:
            inventory: Supplemental inventory
            path: Output file path
        """
        with open(path, "w") as f:
            yaml.dump(
                inventory.to_dict(),
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

    def write_json(self, inventory: SupplementalInventory, path: Path):
        """
        Write inventory to JSON file.

        Args:
            inventory: Supplemental inventory
            path: Output file path
        """
        with open(path, "w") as f:
            json.dump(inventory.to_dict(), f, indent=2, ensure_ascii=False)

    def write_csv(self, inventory: SupplementalInventory, path: Path):
        """
        Write flat summary to CSV file.

        Args:
            inventory: Supplemental inventory
            path: Output file path
        """
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(
                [
                    "group_id",
                    "type",
                    "language",
                    "confidence",
                    "suggested_action",
                    "num_files",
                    "representative_path",
                    "member_paths",
                    "reason",
                ]
            )

            # Data rows
            for group in inventory.duplicate_groups:
                member_paths = "; ".join([m.path for m in group.member_files])
                writer.writerow(
                    [
                        group.id,
                        group.type,
                        group.language or "",
                        group.confidence,
                        group.suggested_action,
                        len(group.member_files),
                        group.representative_path,
                        member_paths,
                        group.reason,
                    ]
                )

    def write_markdown(self, inventory: SupplementalInventory, path: Path):
        """
        Write human-readable markdown report.

        Args:
            inventory: Supplemental inventory
            path: Output file path
        """
        lines = []

        # Header
        lines.append("# Supplemental Duplicate Detection Report")
        lines.append("")
        lines.append(f"**Generated:** {inventory.metadata.generated_at}")
        lines.append(f"**Repository:** {inventory.metadata.repository_root}")
        lines.append(f"**Scanner Version:** {inventory.metadata.scanner_version}")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Total files scanned:** {inventory.metadata.total_files_scanned}")
        lines.append(f"- **Duplicate groups found:** {inventory.metadata.total_groups}")
        lines.append(f"- **Detection modes:** {', '.join(inventory.metadata.detection_modes)}")
        lines.append(f"- **Scan duration:** {inventory.metadata.scan_duration_seconds:.2f}s")
        lines.append("")

        # Summary by type
        type_counts = {}
        for group in inventory.duplicate_groups:
            type_counts[group.type] = type_counts.get(group.type, 0) + 1

        if type_counts:
            lines.append("## Summary by Detection Type")
            lines.append("")
            lines.append("| Type | Groups | Files |")
            lines.append("|------|--------|-------|")

            for dtype, count in sorted(type_counts.items()):
                files = sum(
                    len(g.member_files)
                    for g in inventory.duplicate_groups
                    if g.type == dtype
                )
                lines.append(f"| {dtype} | {count} | {files} |")

            lines.append("")

        # Duplicate groups
        if inventory.duplicate_groups:
            lines.append("## Duplicate Groups")
            lines.append("")

            for i, group in enumerate(inventory.duplicate_groups[:20], 1):  # Top 20
                lines.append(f"### {i}. {group.id} ({group.confidence.upper()})")
                lines.append("")
                lines.append(f"- **Type:** {group.type}")
                lines.append(f"- **Language:** {group.language or 'unknown'}")
                lines.append(f"- **Confidence:** {group.confidence}")
                lines.append(f"- **Suggested Action:** {group.suggested_action}")
                lines.append(f"- **Reason:** {group.reason}")
                lines.append(f"- **Files:** {len(group.member_files)}")
                lines.append("")

                lines.append("**Member Files:**")
                for member in group.member_files:
                    lines.append(f"- `{member.path}` (similarity: {member.similarity_score:.2f})")

                lines.append("")

                # Code snippet
                if group.summary:
                    lines.append("**Code Snippet:**")
                    lines.append("```")
                    lines.append(group.summary[:200])  # Limit snippet length
                    lines.append("```")
                    lines.append("")

            if len(inventory.duplicate_groups) > 20:
                lines.append(f"*...and {len(inventory.duplicate_groups) - 20} more groups*")
                lines.append("")

        # Write file
        with open(path, "w") as f:
            f.write("\n".join(lines))
