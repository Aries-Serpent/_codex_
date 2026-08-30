#!/usr/bin/env python3
"""Automated token utility adoption refactoring for Phase 4.2.

This script automatically refactors non-compliant Python scripts to use the
centralized _token_resolver utility instead of inline token handling.

Strategy:
1. Read pre-refactor analysis from validator
2. For each non-compliant script:
   - Parse and identify token patterns
   - Apply appropriate refactoring based on pattern type
   - Add necessary imports
   - Replace inline logic with utility calls
3. Track changes and generate detailed report

Exit codes:
    0 = Success (scripts refactored)
    1 = Error during refactoring
"""

import json
import tempfile
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
from typing import Dict, List, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class RefactoringChange:
    """Represents a single refactoring change applied to a script."""

    file_path: str
    pattern_type: str  # "inline_get", "environ_bracket", "implicit_token", etc.
    line_number: int
    original_code: str
    refactored_code: str
    success: bool = True
    error_msg: str = ""


@dataclass
class ScriptRefactoring:
    """Represents all refactoring changes for a single script."""

    file_path: str
    script_name: str
    changes: List[RefactoringChange] = field(default_factory=list)
    added_imports: Set[str] = field(default_factory=set)
    success: bool = False
    error_msg: str = ""

    def total_changes(self) -> int:
        return len([c for c in self.changes if c.success])

    def failed_changes(self) -> int:
        return len([c for c in self.changes if not c.success])


class TokenRefactorer:
    """Main refactoring engine for token utility adoption."""

    # Patterns to detect and refactor
    PATTERNS = {
        "inline_get": {
            "regex": r"os\.getenv\(['\"]CODEX_(MASTER|BACKUP)_KEY['\"]\)",
            "replacement": "get_token(required_elevated=True)[0]",
            "import": "from scripts.ci._token_resolver import get_token",
        },
        "environ_get": {
            "regex": r"os\.environ\.get\(['\"]CODEX_(MASTER|BACKUP)_KEY['\"]\)",
            "replacement": "get_token(required_elevated=True)[0]",
            "import": "from scripts.ci._token_resolver import get_token",
        },
        "environ_bracket": {
            "regex": r"os\.environ\[['\"]CODEX_(MASTER|BACKUP)_KEY['\"]\]",
            "replacement": "get_token(required_elevated=True)[0]",
            "import": "from scripts.ci._token_resolver import get_token",
        },
        "gh_token": {
            "regex": r"os\.getenv\(['\"]GH_TOKEN['\"]\)|os\.environ\.get\(['\"]GH_TOKEN['\"]\)",
            "replacement": "get_token(required_elevated=False)[0]",
            "import": "from scripts.ci._token_resolver import get_token",
        },
    }

    def __init__(self):
        self.refactorings: List[ScriptRefactoring] = []
        self.total_files_processed = 0
        self.total_files_changed = 0

    def refactor_file(self, file_path: str) -> ScriptRefactoring:
        """Refactor a single Python script file."""
        self.total_files_processed += 1
        result = ScriptRefactoring(
            file_path=file_path,
            script_name=Path(file_path).name,
        )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            refactored_content = original_content
            imports_to_add = set()
            changes = []

            # Apply each pattern
            for pattern_name, pattern_info in self.PATTERNS.items():
                pattern = pattern_info["regex"]
                replacement = pattern_info["replacement"]
                import_stmt = pattern_info["import"]

                # Find all matches
                matches = list(re.finditer(pattern, refactored_content))
                for match in matches:
                    # Calculate line number
                    line_num = refactored_content[: match.start()].count("\n") + 1

                    change = RefactoringChange(
                        file_path=file_path,
                        pattern_type=pattern_name,
                        line_number=line_num,
                        original_code=match.group(0),
                        refactored_code=replacement,
                    )
                    changes.append(change)
                    imports_to_add.add(import_stmt)

                # Apply replacements
                refactored_content = re.sub(pattern, replacement, refactored_content)

            # Add imports if needed
            if imports_to_add:
                refactored_content = self._add_imports(
                    refactored_content, imports_to_add
                )
                result.added_imports = imports_to_add

            # Only write if changes were made
            if changes:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(refactored_content)

                result.changes = changes
                result.success = True
                self.total_files_changed += 1
                logger.info(
                    f"✓ Refactored {result.script_name}: "
                    f"{result.total_changes()} changes"
                )
            else:
                result.success = True
                result.error_msg = "No patterns found (already compliant)"

        except Exception as e:
            result.success = False
            result.error_msg = str(e)
            logger.error(f"✗ Failed to refactor {result.script_name}: {e}")

        self.refactorings.append(result)
        return result

    def _add_imports(self, content: str, imports: Set[str]) -> str:
        """Add import statements to the beginning of the file."""
        # Extract existing imports
        lines = content.split("\n")
        import_section_end = 0

        # Find where imports end
        in_import_block = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("from ") or stripped.startswith("import "):
                import_section_end = i + 1
                in_import_block = True
            elif in_import_block and (
                not stripped or stripped.startswith("#")
            ):
                # Empty line or comment after imports
                continue
            elif in_import_block and not (
                stripped.startswith("from ") or stripped.startswith("import ")
            ):
                # End of import block
                break

        # Check if imports already exist
        existing_imports = "\n".join(lines[:import_section_end])
        new_imports = []

        for imp in imports:
            if imp not in existing_imports:
                new_imports.append(imp)

        if not new_imports:
            return content

        # Insert new imports
        if import_section_end > 0:
            lines.insert(import_section_end, "")

        for imp in new_imports:
            lines.insert(import_section_end, imp)

        return "\n".join(lines)

    def refactor_scripts(self, file_paths: List[str]) -> bool:
        """Refactor multiple scripts."""
        logger.info(f"Starting refactoring of {len(file_paths)} scripts...")

        for i, file_path in enumerate(file_paths):
            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i+1}/{len(file_paths)} scripts processed")
            self.refactor_file(file_path)

        logger.info(
            f"\n✅ Refactoring complete:\n"
            f"   Total processed: {self.total_files_processed}\n"
            f"   Total changed: {self.total_files_changed}"
        )
        return True

    def get_report(self) -> Dict:
        """Generate a detailed report of all refactorings."""
        successful = sum(1 for r in self.refactorings if r.success and r.changes)
        failed = sum(1 for r in self.refactorings if not r.success)

        return {
            "total_files_processed": self.total_files_processed,
            "total_files_changed": self.total_files_changed,
            "successful_refactorings": successful,
            "failed_refactorings": failed,
            "refactorings": [
                {
                    "file_path": r.file_path,
                    "script_name": r.script_name,
                    "changes_count": r.total_changes(),
                    "failed_changes": r.failed_changes(),
                    "added_imports": list(r.added_imports),
                    "success": r.success,
                    "error": r.error_msg,
                    "changes": [
                        {
                            "pattern_type": c.pattern_type,
                            "line_number": c.line_number,
                            "original": c.original_code,
                            "refactored": c.refactored_code,
                        }
                        for c in r.changes
                    ],
                }
                for r in self.refactorings
            ],
        }


def main():
    """Main entry point."""
    # Load pre-refactor analysis
    validator_output = Path(os.path.join(tempfile.gettempdir(), "pre_refactor.json"))
    if not validator_output.exists():
        logger.error("Pre-refactor analysis not found. Run validator first.")
        return 1

    with open(validator_output, "r") as f:
        analysis_data = json.load(f)

    # Get list of non-compliant scripts
    non_compliant_scripts = [
        REPO_ROOT / script["file_path"]
        for script in analysis_data.get("script_analyses", [])
        if not script["is_compliant"]
    ]

    logger.info(f"Found {len(non_compliant_scripts)} non-compliant scripts to refactor")

    # Run refactoring
    refactorer = TokenRefactorer()
    refactorer.refactor_scripts(
        [str(p) for p in non_compliant_scripts if p.exists()]
    )

    # Save report
    report = refactorer.get_report()
    report_path = Path(".codex/PHASE_4_2_REFACTORING_CHANGES.json")
    report_path.parent.mkdir(exist_ok=True, parents=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Report saved to {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
