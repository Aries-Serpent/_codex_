"""Exact duplicate detection using SHA256 hashing."""

import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple

from .schema import DuplicateGroup, MemberFile


class ExactDetector:
    """Detects exact file duplicates using SHA256 hashing."""

    DEFAULT_EXCLUDE_DIRS = {
        ".git",
        "node_modules",
        "vendor",
        "third_party",
        "build",
        "dist",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        "venv",
        ".venv",
    }

    DEFAULT_EXCLUDE_PATTERNS = {
        "*.pyc",
        "*.pyo",
        "*.so",
        "*.dylib",
        "*.dll",
        ".DS_Store",
    }

    def __init__(
        self,
        root_path: Path,
        exclude_patterns: List[str] = None,
        respect_gitignore: bool = True,
    ):
        """
        Initialize detector with repository root and exclusion patterns.

        Args:
            root_path: Root directory to scan
            exclude_patterns: Additional patterns to exclude
            respect_gitignore: Whether to respect .gitignore
        """
        self.root_path = Path(root_path)
        self.exclude_patterns = set(exclude_patterns or [])
        self.exclude_patterns.update(self.DEFAULT_EXCLUDE_PATTERNS)
        self.respect_gitignore = respect_gitignore
        self.gitignore_patterns = self._load_gitignore() if respect_gitignore else set()

    def _load_gitignore(self) -> Set[str]:
        """Load patterns from .gitignore."""
        gitignore_path = self.root_path / ".gitignore"
        patterns = set()
        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.add(line)
            except Exception:
                pass
        return patterns

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        # Check if any parent directory is in exclude list
        for parent in path.parents:
            if parent.name in self.DEFAULT_EXCLUDE_DIRS:
                return True

        # Check if filename matches exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.startswith("*"):
                if path.name.endswith(pattern[1:]):
                    return True
            elif path.name == pattern:
                return True

        return False

    def compute_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of file contents.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string
        """
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return ""

    def scan(self) -> List[DuplicateGroup]:
        """
        Scan repository and return list of duplicate groups.

        Returns:
            List of duplicate groups
        """
        # Build hash -> files mapping
        hash_to_files: Dict[str, List[Path]] = {}

        # Scan all files
        for file_path in self.root_path.rglob("*"):
            if not file_path.is_file():
                continue

            if self._should_exclude(file_path):
                continue

            file_hash = self.compute_hash(file_path)
            if file_hash:
                if file_hash not in hash_to_files:
                    hash_to_files[file_hash] = []
                hash_to_files[file_hash].append(file_path)

        # Create duplicate groups for files with same hash
        duplicate_groups = []
        group_id = 1

        for file_hash, files in hash_to_files.items():
            if len(files) < 2:
                continue

            # Determine language from first file extension
            language = self._detect_language(files[0])

            # Create member files
            member_files = []
            for file_path in files:
                rel_path = str(file_path.relative_to(self.root_path))
                member_files.append(
                    MemberFile(
                        path=rel_path,
                        file_hash=file_hash,
                        similarity_score=1.0,
                    )
                )

            # Select representative (shortest path)
            representative = min(files, key=lambda p: len(str(p)))
            rep_path = str(representative.relative_to(self.root_path))

            # Create snippet from first few lines
            summary = self._get_file_summary(files[0])

            # Create duplicate group
            group = DuplicateGroup(
                id=f"dup-exact-{group_id:03d}",
                type="exact-file",
                language=language,
                representative_path=rep_path,
                member_files=member_files,
                reason="Exact file duplicate (SHA256 match)",
                suggested_action="consolidate",
                confidence="high",
                tags=["exact-duplicate"],
                meta={
                    "detection_method": ["sha256"],
                    "file_size": files[0].stat().st_size if files[0].exists() else 0,
                },
                summary=summary,
            )

            duplicate_groups.append(group)
            group_id += 1

        return duplicate_groups

    def _detect_language(self, file_path: Path) -> str:
        """Detect language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "shell",
            ".bash": "shell",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".md": "markdown",
        }
        return ext_map.get(file_path.suffix.lower(), "unknown")

    def _get_file_summary(self, file_path: Path, max_lines: int = 3) -> str:
        """Get summary snippet from file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip())
                return "\n".join(lines) + "..."
        except Exception:
            return "(binary or unreadable file)"
