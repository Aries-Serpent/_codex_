#!/usr/bin/env python3
"""
Expanded Context Audit

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/expanded_context_audit.py [options]

    Examples:
    $ python scripts/expanded_context_audit.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import argparse
import json
import re
from pathlib import Path
from typing import Any


class ExpandedContextAuditor:
    """Audit repository for expanded context features"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.features = {
            "vectorstore": {"files": [], "score": 0, "priority": "P0"},
            "embeddings": {"files": [], "score": 0, "priority": "P0"},
            "rag": {"files": [], "score": 0, "priority": "P0"},
            "session_logging": {"files": [], "score": 0, "priority": "P1"},
            "copilot_bridge": {"files": [], "score": 0, "priority": "P1"},
            "retriever": {"files": [], "score": 0, "priority": "P0"},
            "indexer": {"files": [], "score": 0, "priority": "P0"},
            "summarization": {"files": [], "score": 0, "priority": "P1"},
            "provenance": {"files": [], "score": 0, "priority": "P1"},
            "subagent_orchestrator": {"files": [], "score": 0, "priority": "P2"},
            "cache": {"files": [], "score": 0, "priority": "P0"},
        }
        self.patterns = {
            "vectorstore": [
                r"faiss",
                r"vector.*store",
                r"index.*persist",
                r"ChromaDB",
                r"Pinecone",
            ],
            "embeddings": [
                r"embed.*model",
                r"sentence.*transform",
                r"EmbeddingModel",
                r"embed_chunks",
            ],
            "rag": [r"retriev.*augment", r"RAG", r"rag/", r"retrieval/"],
            "session_logging": [
                r"session.*log",
                r"SessionLogger",
                r"CODEX_SESSION",
            ],
            "copilot_bridge": [r"copilot.*bridge", r"CopilotBridge"],
            "retriever": [r"Retriever", r"retriev.*query", r"top_k"],
            "indexer": [r"Indexer", r"chunk_text", r"build.*index"],
            "summarization": [r"summariz", r"summary", r"abstract"],
            "provenance": [r"provenance", r"lineage", r"source.*track"],
            "subagent_orchestrator": [
                r"subagent",
                r"orchestrat",
                r"agent.*coord",
            ],
            "cache": [r"embeddings.*cache", r"cache.*embed", r"\.codex/.*cache"],
        }

    def scan_file(self, filepath: Path) -> dict[str, list[str]]:
        """Scan a single file for features"""
        matches: dict[str, list[str]] = {key: [] for key in self.features}

        if not filepath.is_file():
            return matches

        # Skip binary files, large files, and certain directories
        if filepath.suffix in [
            ".pyc",
            ".so",
            ".dylib",
            ".dll",
            ".jpg",
            ".png",
            ".pdf",
        ]:
            return matches

        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Check each feature pattern
            for feature, patterns in self.patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        matches[feature].append(str(filepath.relative_to(self.root_dir)))
                        break  # Only count once per file per feature

        except (UnicodeDecodeError, PermissionError):
            # Intentionally skip files that cannot be read due to encoding or permissions.
            # These files cannot be scanned for text-based patterns, so we return no matches.
            # Intentionally skip files that cannot be read due to encoding or permissions.
            # These files cannot be scanned for text-based patterns, so we return no matches.
            return matches

        return matches

    def scan_repository(self) -> dict[str, Any]:
        """Scan the entire repository"""
        print(f"Scanning repository: {self.root_dir}")

        # Define directories to scan
        scan_dirs = ["src", "scripts", "agents", "tests", ".codex"]

        python_files: list[Path] = []
        for scan_dir in scan_dirs:
            dir_path = self.root_dir / scan_dir
            if dir_path.exists():
                python_files.extend(dir_path.rglob("*.py"))

        total_files = len(python_files)
        print(f"Found {total_files} Python files to scan")

        # Scan all files
        for i, filepath in enumerate(python_files, 1):
            if i % 100 == 0:
                print(f"Progress: {i}/{total_files}")

            matches = self.scan_file(filepath)
            for feature, file_list in matches.items():
                if file_list:
                    self.features[feature]["files"].extend(file_list)

        # Calculate scores (0-100) based on file count and completeness indicators
        for feature, data in self.features.items():
            file_count = len(set(data["files"]))  # Unique files
            # Score based on presence and quantity
            if file_count == 0:
                data["score"] = 0
            elif file_count < 3:
                data["score"] = 25
            elif file_count < 10:
                data["score"] = 50
            else:
                data["score"] = 75

            # Specific completeness checks
            if feature == "retriever" and file_count > 0:
                # Check if retriever.py exists
                if any("retriever.py" in f for f in data["files"]):
                    data["score"] = min(100, data["score"] + 25)

            if feature == "indexer" and file_count > 0:
                # Check if indexer.py exists
                if any("indexer.py" in f for f in data["files"]):
                    data["score"] = min(100, data["score"] + 25)

            if feature == "embeddings" and file_count > 0:
                # Check if embeddings.py or embed.py exists
                if any("embed" in f for f in data["files"]):
                    data["score"] = min(100, data["score"] + 25)

            data["files"] = sorted(set(data["files"]))  # Unique and sorted

        return {
            "summary": {
                "total_files_scanned": total_files,
                "features_detected": sum(
                    1 for f in self.features.values() if f["score"] > 0
                ),
                "features_complete": sum(
                    1 for f in self.features.values() if f["score"] >= 75
                ),
            },
            "features": self.features,
            "missing_areas": self._identify_missing_areas(),
        }

    def _identify_missing_areas(self) -> dict[str, list[str]]:
        """Identify missing or incomplete areas by priority"""
        missing = {"P0": [], "P1": [], "P2": []}

        for feature, data in self.features.items():
            if data["score"] < 50:  # Less than 50% complete
                priority = data["priority"]
                missing[priority].append(
                    {
                        "feature": feature,
                        "score": data["score"],
                        "file_count": len(data["files"]),
                    }
                )

        return missing

    def generate_summary(self, report: dict[str, Any]) -> str:
        """Generate a markdown summary of the audit"""
        summary = "# Expanded Context Audit Summary\n\n"

        # Overview
        summary += "## Overview\n\n"
        summary += f"- Total files scanned: {report['summary']['total_files_scanned']}\n"
        summary += f"- Features detected: {report['summary']['features_detected']}\n"
        summary += (
            f"- Features complete (≥75%): {report['summary']['features_complete']}\n\n"
        )

        # Detected Features
        summary += "## Detected Features\n\n"
        for feature, data in report["features"].items():
            status = "✅" if data["score"] >= 75 else "⚠️" if data["score"] >= 50 else "❌"
            summary += f"- {status} **{feature}** (Score: {data['score']}/100, Files: {len(data['files'])})\n"
            if data["files"][:3]:  # Show first 3 files
                for f in data["files"][:3]:
                    summary += f"  - `{f}`\n"
                if len(data["files"]) > 3:
                    summary += f"  - ... and {len(data['files']) - 3} more\n"

        summary += "\n"

        # Missing/Partial Areas
        summary += "## Missing/Partial Areas (Prioritized)\n\n"
        for priority in ["P0", "P1", "P2"]:
            items = report["missing_areas"][priority]
            if items:
                summary += f"### {priority} Priority\n\n"
                for item in items:
                    summary += f"- **{item['feature']}** (Score: {item['score']}/100, Files: {item['file_count']})\n"
                summary += "\n"

        # Recommendations
        summary += "## Recommendations\n\n"
        p0_items = report["missing_areas"]["P0"]
        if p0_items:
            summary += "### Immediate Actions (P0)\n\n"
            for item in p0_items:
                feature = item["feature"]
                if feature == "retriever":
                    summary += "- Implement `src/codex/rag/retriever.py` with query() method\n"
                elif feature == "indexer":
                    summary += "- Implement `src/codex/rag/indexer.py` with chunk_text(), embed_chunks(), persist_index()\n"
                elif feature == "embeddings":
                    summary += "- Enhance embeddings with caching layer and provider abstraction\n"
                elif feature == "vectorstore":
                    summary += "- Add FAISS-based vectorstore with persistence to `.codex/tenants/`\n"
                elif feature == "cache":
                    summary += "- Implement embeddings cache in `.codex/embeddings_cache/`\n"
            summary += "\n"

        return summary


def main():
    parser = argparse.ArgumentParser(description="Audit expanded context features")
    parser.add_argument(
        "--root", default=".", help="Root directory to scan (default: .)"
    )
    parser.add_argument(
        "--out",
        default=".codex/reports/expanded_context_report.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--summary",
        default=".codex/reports/expanded_context_summary.md",
        help="Output summary markdown file path",
    )

    args = parser.parse_args()

    # Create reports directory if needed
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    # Run audit
    auditor = ExpandedContextAuditor(args.root)
    report = auditor.scan_repository()

    # Save JSON report
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n✅ Report saved to: {out_path}")

    # Generate and save summary
    summary = auditor.generate_summary(report)
    with open(summary_path, "w") as f:
        f.write(summary)
    print(f"✅ Summary saved to: {summary_path}")

    # Print summary to console
    print("\n" + "=" * 80)
    print(summary)


if __name__ == "__main__":
    main()
