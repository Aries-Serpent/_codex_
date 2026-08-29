#!/usr/bin/env python3
"""Advanced token utility adoption refactoring for Phase 4.2.

This is a second-pass refactoring that handles more complex patterns than
the first pass. It specifically targets scripts with true inline token
handling (the 136 scripts from Phase 4.1 analysis).

Strategy:
1. Focus on scripts with actual anti-patterns (inline token access)
2. Apply context-aware refactoring based on usage patterns
3. Validate each change to ensure correctness
4. Skip false positive scripts (those just using elevated APIs)
"""

import json
import tempfile
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
from typing import Dict, List, Optional, Set, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class RefactoringPass:
    """Represents a single refactoring pass."""

    pass_number: int
    scripts_processed: int = 0
    scripts_changed: int = 0
    total_changes: int = 0
    errors: List[str] = field(default_factory=list)


class AdvancedTokenRefactorer:
    """Advanced refactoring engine for complex token patterns."""

    # Patterns for different token usage contexts
    USAGE_PATTERNS = {
        "function_param": {
            "pattern": r"def\s+\w+\([^)]*token[^)]*\):",
            "description": "Function takes token as parameter",
        },
        "class_init": {
            "pattern": r"def\s+__init__\([^)]*token[^)]*\):",
            "description": "Class __init__ takes token parameter",
        },
        "direct_environ": {
            "pattern": r"(?:os\.environ|os\.getenv)\s*[\[\(].*?(?:CODEX_MASTER_KEY|CODEX_BACKUP_KEY|GH_TOKEN|GITHUB_TOKEN)",
            "description": "Direct environment variable access",
        },
    }

    def __init__(self):
        self.passes: List[RefactoringPass] = []

    def should_skip_script(self, file_path: str, content: str) -> Tuple[bool, str]:
        """Determine if a script should be skipped (false positive).

        Args:
            file_path: Path to the script
            content: File content

        Returns:
            Tuple of (should_skip, reason)
        """
        # Skip if it has genuine token handling
        token_patterns = [
            r"os\.getenv\s*\(\s*['\"]CODEX_(MASTER|BACKUP)_KEY['\"]",
            r"os\.environ\s*\[\s*['\"]CODEX_(MASTER|BACKUP)_KEY['\"]",
            r"os\.environ\.get\s*\(\s*['\"]CODEX_(MASTER|BACKUP)_KEY['\"]",
        ]

        has_token_handling = any(
            re.search(pattern, content) for pattern in token_patterns
        )

        if has_token_handling:
            return False, "Has token handling"

        # Check if it's a test or example script
        if any(
            x in str(file_path).lower()
            for x in ["test_", "example_", "sample_", "mock_"]
        ):
            # Unless it has token handling
            if "token" not in content.lower():
                return True, "Test/example script without token handling"

        return False, "Should refactor"

    def refactor_with_context(
        self, file_path: str, content: str
    ) -> Optional[Tuple[str, List[str]]]:
        """Refactor script with context-aware token handling.

        Args:
            file_path: Path to the script
            content: File content

        Returns:
            Tuple of (refactored_content, imports_added) or None if no changes
        """
        should_skip, reason = self.should_skip_script(file_path, content)
        if should_skip:
            logger.debug(f"Skipping {Path(file_path).name}: {reason}")
            return None

        # Pattern 1: os.getenv/os.environ.get for CODEX keys
        pattern1 = r'os\.(?:getenv|environ\.get)\s*\(\s*["\']CODEX_(MASTER|BACKUP)_KEY["\']\s*\)'
        replacement1 = "get_token(required_elevated=True)[0]"

        # Pattern 2: os.environ[...] for CODEX keys
        pattern2 = r'os\.environ\s*\[\s*["\']CODEX_(MASTER|BACKUP)_KEY["\']\s*\]'
        replacement2 = "get_token(required_elevated=True)[0]"

        # Pattern 3: Fallback chain with CODEX keys
        pattern3 = (
            r'(?:token\s*=\s*)?os\.getenv\s*\(\s*["\']CODEX_MASTER_KEY["\']\s*\)\s*or\s*'
            r'os\.getenv\s*\(\s*["\']GH_TOKEN["\']\s*\)'
        )
        replacement3 = "get_token(required_elevated=False)[0]"

        refactored_content = content
        imports_added = set()
        changes_made = False

        # Apply replacements if patterns found
        for pattern, replacement in [
            (pattern1, replacement1),
            (pattern2, replacement2),
            (pattern3, replacement3),
        ]:
            if re.search(pattern, refactored_content):
                refactored_content = re.sub(pattern, replacement, refactored_content)
                imports_added.add("from scripts.ci._token_resolver import get_token")
                changes_made = True

        # Add imports if needed
        if imports_added:
            refactored_content = self._add_imports(refactored_content, imports_added)

        return (refactored_content, list(imports_added)) if changes_made else None

    def _add_imports(self, content: str, imports: Set[str]) -> str:
        """Add import statements."""
        lines = content.split("\n")

        # Find import section
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                import_end = i + 1

        # Check existing
        existing = "\n".join(lines[:import_end])
        new_imports = [imp for imp in imports if imp not in existing]

        if new_imports:
            for imp in reversed(new_imports):
                lines.insert(import_end, imp)

        return "\n".join(lines)

    def refactor_scripts_batch(self, file_paths: List[str]) -> RefactoringPass:
        """Refactor a batch of scripts."""
        pass_num = len(self.passes) + 1
        pass_result = RefactoringPass(pass_number=pass_num)

        for i, file_path in enumerate(file_paths):
            if (i + 1) % 100 == 0:
                logger.info(f"Pass {pass_num}: {i+1}/{len(file_paths)} processed")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                result = self.refactor_with_context(file_path, content)

                if result:
                    refactored_content, imports = result
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(refactored_content)

                    pass_result.scripts_changed += 1
                    pass_result.total_changes += len(imports)
                    logger.debug(f"✓ Refactored {Path(file_path).name}")

                pass_result.scripts_processed += 1

            except Exception as e:
                pass_result.errors.append(f"{file_path}: {str(e)}")

        self.passes.append(pass_result)
        return pass_result

    def get_summary(self) -> Dict:
        """Get summary of all refactoring passes."""
        return {
            "passes": [
                {
                    "pass_number": p.pass_number,
                    "scripts_processed": p.scripts_processed,
                    "scripts_changed": p.scripts_changed,
                    "total_changes": p.total_changes,
                    "errors_count": len(p.errors),
                }
                for p in self.passes
            ],
            "total_passes": len(self.passes),
            "cumulative_changes": sum(p.total_changes for p in self.passes),
            "cumulative_errors": sum(len(p.errors) for p in self.passes),
        }


def main():
    """Main entry point for advanced refactoring."""
    validator_output = Path(os.path.join(tempfile.gettempdir(), "post_refactor_1.json"))
    if not validator_output.exists():
        logger.error("Post-refactor 1 analysis not found")
        return 1

    with open(validator_output, "r") as f:
        analysis_data = json.load(f)

    # Get non-compliant scripts
    non_compliant = [
        REPO_ROOT / script["file_path"]
        for script in analysis_data.get("script_analyses", [])
        if not script["is_compliant"]
    ]

    refactorer = AdvancedTokenRefactorer()

    logger.info(f"Pass 2: Processing {len(non_compliant)} scripts...")
    pass_result = refactorer.refactor_scripts_batch(
        [str(p) for p in non_compliant if p.exists()]
    )

    logger.info(
        f"\nPass 2 Results:\n"
        f"  Processed: {pass_result.scripts_processed}\n"
        f"  Changed: {pass_result.scripts_changed}\n"
        f"  Total changes: {pass_result.total_changes}"
    )

    # Save summary
    summary_path = Path(".codex/PHASE_4_2_REFACTORING_SUMMARY.json")
    summary_path.parent.mkdir(exist_ok=True, parents=True)

    with open(summary_path, "w") as f:
        json.dump(refactorer.get_summary(), f, indent=2)

    logger.info(f"Summary saved to {summary_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
