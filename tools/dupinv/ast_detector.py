"""AST-based duplicate detector for function and class level duplication."""

from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from .schema import DuplicateGroup, MemberFile
from .ast_parsers.python_parser import FunctionSignature, PythonASTParser


class ASTDetector:
    """Detects duplicates at function/class level using AST analysis."""

    def __init__(
        self,
        root_path: Path,
        similarity_threshold: float = 0.85,
        exclude_patterns: List[str] = None,
        respect_gitignore: bool = True,
    ):
        """
        Initialize AST detector.

        Args:
            root_path: Repository root path
            similarity_threshold: Minimum similarity for near-duplicates (0.0-1.0)
            exclude_patterns: Patterns to exclude from scanning
            respect_gitignore: Whether to respect .gitignore
        """
        self.root_path = Path(root_path)
        self.similarity_threshold = similarity_threshold
        self.exclude_patterns = exclude_patterns or []
        self.respect_gitignore = respect_gitignore

        self.python_parser = PythonASTParser()

    def scan(self) -> List[DuplicateGroup]:
        """
        Scan repository for AST-level duplicates.

        Returns:
            List of duplicate groups
        """
        # Find all Python files
        python_files = self._find_python_files()

        # Extract all function signatures
        all_signatures = []
        for file_path in python_files:
            sigs = self.python_parser.parse_file(file_path)
            all_signatures.extend(sigs)

        # Find identical and similar functions
        duplicate_groups = []
        duplicate_groups.extend(self.find_identical_functions(all_signatures))
        duplicate_groups.extend(self.find_similar_functions(all_signatures))

        return duplicate_groups

    def find_identical_functions(self, signatures: List[FunctionSignature]) -> List[DuplicateGroup]:
        """
        Find functions with identical AST.

        Args:
            signatures: List of function signatures

        Returns:
            List of duplicate groups for identical functions
        """
        # Group by AST hash
        hash_groups: Dict[str, List[FunctionSignature]] = defaultdict(list)
        for sig in signatures:
            hash_groups[sig.ast_hash].append(sig)

        # Create duplicate groups for hashes with multiple functions
        duplicate_groups = []
        group_id = 0

        for ast_hash, sigs in hash_groups.items():
            if len(sigs) < 2:
                continue

            # Skip if all from same file (nested functions)
            files = set(sig.file_path for sig in sigs)
            if len(files) < 2:
                continue

            group_id += 1

            # Create member files
            member_files = []
            for sig in sigs:
                # Make path relative to repo root
                rel_path = self._make_relative(sig.file_path)

                member = MemberFile(
                    path=str(rel_path),
                    start_line=sig.start_line,
                    end_line=sig.end_line,
                    file_hash=sig.body_hash,
                    similarity_score=1.0,
                )
                member_files.append(member)

            # Create summary
            representative = sigs[0]
            if representative.is_method and representative.class_name:
                summary = f"class {representative.class_name}:\n    def {representative.name}({', '.join(representative.parameters)})"
            else:
                summary = f"def {representative.name}({', '.join(representative.parameters)})"

            if representative.return_type:
                summary += f" -> {representative.return_type}"

            # Create duplicate group
            group = DuplicateGroup(
                id=f"dup-ast-{group_id:03d}",
                type="function-ast",
                language="python",
                representative_path=str(self._make_relative(representative.file_path)),
                member_files=member_files,
                reason=f"Identical function: {representative.name}",
                suggested_action="refactor",
                confidence="high",
                tags=["function-duplicate", "ast-identical"],
                meta={
                    "detection_method": ["ast"],
                    "function_name": representative.name,
                    "parameter_count": len(representative.parameters),
                    "is_method": representative.is_method,
                },
                summary=summary,
            )

            duplicate_groups.append(group)

        return duplicate_groups

    def find_similar_functions(self, signatures: List[FunctionSignature]) -> List[DuplicateGroup]:
        """
        Find functions with similar AST (above threshold).

        Args:
            signatures: List of function signatures

        Returns:
            List of duplicate groups for similar functions
        """
        # This is computationally expensive for large codebases
        # For now, we'll use a simpler approach: group by function name
        # and then check similarity within same-named functions

        name_groups: Dict[str, List[FunctionSignature]] = defaultdict(list)
        for sig in signatures:
            name_groups[sig.name].append(sig)

        duplicate_groups = []
        group_id = 1000  # Start from 1000 to distinguish from identical

        for func_name, sigs in name_groups.items():
            if len(sigs) < 2:
                continue

            # Skip if all from same file
            files = set(sig.file_path for sig in sigs)
            if len(files) < 2:
                continue

            # For now, consider same-named functions with same parameter count
            # as potentially similar (simplified approach)
            param_groups: Dict[int, List[FunctionSignature]] = defaultdict(list)
            for sig in sigs:
                param_groups[len(sig.parameters)].append(sig)

            for param_count, param_sigs in param_groups.items():
                if len(param_sigs) < 2:
                    continue

                # Skip if all from same file
                files = set(sig.file_path for sig in param_sigs)
                if len(files) < 2:
                    continue

                # Create duplicate group
                group_id += 1

                member_files = []
                for sig in param_sigs:
                    rel_path = self._make_relative(sig.file_path)
                    member = MemberFile(
                        path=str(rel_path),
                        start_line=sig.start_line,
                        end_line=sig.end_line,
                        file_hash=sig.body_hash,
                        similarity_score=0.9,  # Approximate
                    )
                    member_files.append(member)

                representative = param_sigs[0]
                summary = f"def {representative.name}({', '.join(representative.parameters)})"

                group = DuplicateGroup(
                    id=f"dup-ast-{group_id:03d}",
                    type="function-ast",
                    language="python",
                    representative_path=str(self._make_relative(representative.file_path)),
                    member_files=member_files,
                    reason=f"Similar function: {representative.name} (same name and parameter count)",
                    suggested_action="refactor",
                    confidence="medium",
                    tags=["function-similar", "ast-candidate"],
                    meta={
                        "detection_method": ["ast"],
                        "function_name": representative.name,
                        "parameter_count": param_count,
                    },
                    summary=summary,
                )

                duplicate_groups.append(group)

        return duplicate_groups

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in repository."""
        python_files = []

        # Exclusion patterns
        exclude_dirs = {
            ".git",
            "node_modules",
            "vendor",
            "third_party",
            "__pycache__",
            "build",
            "dist",
            ".venv",
            "venv",
        }

        for path in self.root_path.rglob("*.py"):
            # Check if any parent directory is excluded
            if any(part in exclude_dirs for part in path.parts):
                continue

            python_files.append(path)

        return python_files

    def _make_relative(self, file_path: str) -> Path:
        """Make file path relative to repository root."""
        try:
            return Path(file_path).relative_to(self.root_path)
        except ValueError:
            return Path(file_path)
