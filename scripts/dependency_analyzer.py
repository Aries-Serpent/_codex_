#!/usr/bin/env python3
"""
Dependency Analyzer

AST-based analysis tool to verify file dependencies and safe removal.

Features:
- Python import analysis using AST
- Configuration file dependency checking
- Build script analysis
- Safe removal verification

Usage:
    python scripts/dependency_analyzer.py --file path/to/file.py
    python scripts/dependency_analyzer.py --scan-directory scripts/
"""

import argparse
import ast
import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Dependency detection patterns (constants for better maintainability)
DEPENDENCY_INDICATORS = [".", "/", "_"]  # Indicators that a string might be a dependency
EXCLUDED_PATTERNS = [
    "error",
    "warning",
    "info",
    "debug",
    "http://",
    "https://",
]  # Common non-dependency strings
MIN_STRING_LENGTH = 3  # Minimum length for potential dependency strings
MAX_STRING_LENGTH = 100  # Maximum length for potential dependency strings


class DependencyAnalyzer(ast.NodeVisitor):
    """AST visitor to extract import dependencies."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.imports: Set[str] = set()
        self.from_imports: Dict[str, Set[str]] = defaultdict(set)
        self.string_references: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from...import statements."""
        if node.module:
            for alias in node.names:
                self.from_imports[node.module].add(alias.name)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        """
        Visit constant nodes (Python 3.8+). Filter strings by context and pattern.
        Only collect strings that are likely to be dependencies (imports, module names, etc.).
        """
        if isinstance(node.value, str):
            # Filter by context and pattern to reduce false positives
            # Only keep strings that look like module/package names or paths
            value = node.value
            # Skip very short/long strings using module constants
            if MIN_STRING_LENGTH <= len(value) <= MAX_STRING_LENGTH:
                # Check if it looks like a module name, package name, or file path
                if any(
                    indicator in value for indicator in DEPENDENCY_INDICATORS
                ) and not value.startswith((" ", "\n", "\t")):
                    # Additional filtering: exclude common non-dependency strings
                    if not any(pattern in value.lower() for pattern in EXCLUDED_PATTERNS):
                        self.string_references.add(value)
        self.generic_visit(node)


def analyze_python_file(file_path: Path) -> Dict[str, Any]:
    """
    Analyze a Python file for dependencies.

    Returns:
        Dictionary with imports, from_imports, and string_references
    """
    if not file_path.exists() or file_path.suffix != ".py":
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=str(file_path))
        analyzer = DependencyAnalyzer(file_path)
        analyzer.visit(tree)

        return {
            "file": str(file_path),
            "imports": sorted(analyzer.imports),
            "from_imports": {k: sorted(v) for k, v in analyzer.from_imports.items()},
            "string_references": sorted(analyzer.string_references),
        }

    except (SyntaxError, UnicodeDecodeError) as e:
        logger.warning(f"Could not parse {file_path}: {e}")
        return {}


def find_references_to_file(
    target_file: Path,
    search_directory: Path,
    extensions: List[str] = [".py", ".json", ".yaml", ".yml", ".toml", ".cfg"],
) -> Dict[str, List[str]]:
    """
    Find all references to a target file across the codebase.

    Returns:
        Dictionary mapping file paths to list of reference locations
    """
    references = defaultdict(list)
    target_name = target_file.name
    target_stem = target_file.stem

    # Search for references
    for ext in extensions:
        for file_path in search_directory.rglob(f"*{ext}"):
            if file_path == target_file:
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Simple text search
                if target_name in content or target_stem in content:
                    # Find line numbers
                    lines = content.split("\n")
                    for i, line in enumerate(lines, 1):
                        if target_name in line or target_stem in line:
                            references[str(file_path)].append(f"Line {i}: {line.strip()[:80]}")

            except (UnicodeDecodeError, PermissionError):
                continue

    return dict(references)


def analyze_imports_of_file(target_file: Path, search_directory: Path) -> List[Dict[str, Any]]:
    """
    Find Python files that import the target file.

    Uses AST analysis for accurate import detection.
    """
    importing_files = []
    target_module = target_file.stem

    for py_file in search_directory.rglob("*.py"):
        if py_file == target_file:
            continue

        analysis = analyze_python_file(py_file)
        if not analysis:
            continue

        # Check direct imports
        if target_module in analysis.get("imports", []):
            importing_files.append(
                {
                    "file": str(py_file),
                    "import_type": "direct",
                    "statement": f"import {target_module}",
                }
            )

        # Check from imports
        for module, names in analysis.get("from_imports", {}).items():
            if target_module in module or module == target_module:
                importing_files.append(
                    {
                        "file": str(py_file),
                        "import_type": "from",
                        "statement": f"from {module} import {', '.join(names)}",
                    }
                )

    return importing_files


def check_config_file_references(target_file: Path, root_directory: Path) -> List[str]:
    """
    Check if file is referenced in configuration files.

    Checks: pyproject.toml, setup.py, setup.cfg, requirements.txt, etc.
    """
    config_files = [
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "requirements-dev.txt",
        "MANIFEST.in",
        "tox.ini",
        "noxfile.py",
    ]

    references = []
    target_name = target_file.name

    for config_name in config_files:
        config_path = root_directory / config_name
        if not config_path.exists():
            continue

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()

            if target_name in content or str(target_file) in content:
                references.append(str(config_path))

        except (UnicodeDecodeError, PermissionError):
            continue

    return references


def assess_safe_removal(target_file: Path, root_directory: Path) -> Tuple[str, str, Dict[str, Any]]:
    """
    Assess whether a file can be safely removed.

    Returns:
        (safety_level, reason, details)
        safety_level: 'safe', 'risky', 'unsafe'
    """
    details = {
        "python_imports": [],
        "text_references": {},
        "config_references": [],
        "assessment_date": datetime.now().isoformat(),
    }

    # Check Python imports
    if target_file.suffix == ".py":
        details["python_imports"] = analyze_imports_of_file(target_file, root_directory)

    # Check text references
    details["text_references"] = find_references_to_file(target_file, root_directory)

    # Check config files
    details["config_references"] = check_config_file_references(target_file, root_directory)

    # Assess safety
    if details["config_references"]:
        return "unsafe", "Referenced in configuration files", details

    if details["python_imports"]:
        return "unsafe", f"Imported by {len(details['python_imports'])} Python file(s)", details

    if details["text_references"]:
        ref_count = len(details["text_references"])
        if ref_count > 5:
            return "risky", f"Referenced in {ref_count} files", details
        elif ref_count > 0:
            return "risky", f"Referenced in {ref_count} file(s)", details

    return "safe", "No critical dependencies found", details


def generate_removal_report(
    file_path: Path, safety_level: str, reason: str, details: Dict[str, Any], output_path: Path
) -> None:
    """Generate detailed removal safety report."""
    lines = [
        f"# Safe Removal Report: {file_path.name}",
        "",
        f"**File**: `{file_path}`",
        f"**Safety Level**: {safety_level.upper()}",
        f"**Reason**: {reason}",
        "",
        "## Analysis Details",
        "",
    ]

    # Python imports
    if details.get("python_imports"):
        lines.append("### Python Import Dependencies")
        lines.append(f"Found {len(details['python_imports'])} importing file(s):")
        lines.append("")
        for imp in details["python_imports"]:
            lines.append(f"- `{imp['file']}`")
            lines.append(f"  - Type: {imp['import_type']}")
            lines.append(f"  - Statement: `{imp['statement']}`")
        lines.append("")

    # Text references
    if details.get("text_references"):
        lines.append("### Text References")
        lines.append(f"Found in {len(details['text_references'])} file(s):")
        lines.append("")
        for ref_file, locations in details["text_references"].items():
            lines.append(f"- `{ref_file}`")
            for loc in locations[:3]:  # Show first 3
                lines.append(f"  - {loc}")
            if len(locations) > 3:
                lines.append(f"  - ... and {len(locations) - 3} more")
        lines.append("")

    # Config references
    if details.get("config_references"):
        lines.append("### Configuration File References")
        lines.append("Referenced in:")
        lines.append("")
        for config in details["config_references"]:
            lines.append(f"- `{config}`")
        lines.append("")

    # Recommendation
    lines.append("## Recommendation")
    lines.append("")
    if safety_level == "safe":
        lines.append("✅ **SAFE TO REMOVE**: No critical dependencies detected.")
    elif safety_level == "risky":
        lines.append("⚠️ **RISKY**: Review references before removal.")
    else:
        lines.append("❌ **UNSAFE**: File has active dependencies. Do not remove.")

    # Write report
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    logger.info(f"Generated report: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze file dependencies for safe removal")
    parser.add_argument("--file", type=Path, help="File to analyze")
    parser.add_argument(
        "--scan-directory", type=Path, default=Path("."), help="Directory to scan for dependencies"
    )
    parser.add_argument("--output", type=Path, help="Output file for report")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if not args.file:
        parser.print_help()
        return 1

    if not args.file.exists():
        logger.error(f"File not found: {args.file}")
        return 1

    logger.info(f"Analyzing: {args.file}")

    # Perform analysis
    safety_level, reason, details = assess_safe_removal(args.file, args.scan_directory)

    # Output results
    if args.json:
        result = {
            "file": str(args.file),
            "safety_level": safety_level,
            "reason": reason,
            "details": details,
        }

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            logger.info(f"Saved JSON report: {args.output}")
        else:
            print(json.dumps(result, indent=2))
    else:
        # Generate markdown report
        output_path = args.output or Path(f"{args.file.stem}_removal_report.md")
        generate_removal_report(args.file, safety_level, reason, details, output_path)

    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info(f"Safety Level: {safety_level.upper()}")
    logger.info(f"Reason: {reason}")
    logger.info(f"{'='*60}")

    return 0 if safety_level == "safe" else 1


if __name__ == "__main__":
    exit(main())
