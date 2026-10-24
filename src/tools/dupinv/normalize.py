"""Normalized duplicate detection module.

This module identifies duplicates after normalizing code by:
- Removing comments
- Removing blank lines
- Normalizing whitespace
- Optionally normalizing identifiers
"""

import hashlib
import io
import re
import tokenize
from pathlib import Path

from .exact_detector import ExactDetector
from .schema import DuplicateGroup, MemberFile


def _normalize_python_line(line: str) -> str:
    """Normalize spacing while preserving whitespace inside string literals."""

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(line).readline))
    except (IndentationError, tokenize.TokenError):
        return " ".join(line.split())

    output: list[str] = []
    previous: tokenize.TokenInfo | None = None
    for token in tokens:
        if token.type in {
            tokenize.ENCODING,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.COMMENT,
            tokenize.NL,
            tokenize.NEWLINE,
            tokenize.ENDMARKER,
        }:
            continue
        if previous is not None and _needs_space_between(previous, token):
            output.append(" ")
        output.append(token.string)
        previous = token
    return "".join(output).strip()


def _continued_string_rows(code: str) -> set[int]:
    """Return rows after the first in a multiline string literal."""

    rows: set[int] = set()
    try:
        for token in tokenize.generate_tokens(io.StringIO(code).readline):
            if token.type == tokenize.STRING and token.start[0] != token.end[0]:
                rows.update(range(token.start[0] + 1, token.end[0] + 1))
    except (IndentationError, tokenize.TokenError):
        return set()
    return rows


def _needs_space_between(left: tokenize.TokenInfo, right: tokenize.TokenInfo) -> bool:
    """Return whether a single separator should be emitted between tokens."""

    left_text = left.string
    right_text = right.string
    if left_text in {"(", "[", "{", "."} or right_text in {")", "]", "}", "."}:
        return False
    if right_text == ",":
        return False
    if left_text == ",":
        return True
    if right_text == ":":
        return False
    if left_text == ":":
        return True
    if left.type in {tokenize.NAME, tokenize.NUMBER, tokenize.STRING} and right.type in {
        tokenize.NAME,
        tokenize.NUMBER,
        tokenize.STRING,
    }:
        return True
    if left_text in {"=", "+", "-", "*", "/", "//", "%", "**", "<<", ">>", "&", "|", "^", "~", "==", "!=", "<", ">", "<=", ">=", "->", ":=", "@"} or right_text in {"=", "+", "-", "*", "/", "//", "%", "**", "<<", ">>", "&", "|", "^", "~", "==", "!=", "<", ">", "<=", ">=", "->", ":=", "@"}:
        return True
    return False


class PythonNormalizer:
    """Normalizes Python code."""

    def normalize(self, code: str) -> str:
        """
        Normalize Python code.

        Args:
            code: Raw Python code

        Returns:
            Normalized code
        """
        # Remove single-line comments
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)

        # Remove docstrings (simple approach - handles most cases)
        code = re.sub(r'""".*?"""', "", code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", "", code, flags=re.DOTALL)

        # Remove blank lines
        lines = [line for line in code.split("\n") if line.strip()]

        # Continuation indentation is not suite indentation. In particular, a
        # closing delimiter at column zero must not dedent its enclosing blocks.
        logical_depths: dict[int, int] = {}
        depth = 0
        try:
            for token in tokenize.generate_tokens(io.StringIO("\n".join(lines)).readline):
                if token.type == tokenize.INDENT:
                    depth += 1
                elif token.type == tokenize.DEDENT:
                    depth -= 1
                elif token.type != tokenize.ENDMARKER:
                    logical_depths.setdefault(token.start[0], depth)
        except (IndentationError, tokenize.TokenError):
            # Retain best-effort normalization for incomplete or invalid input.
            logical_depths.clear()

        # Normalize whitespace (consistent indentation), while preserving the
        # literal content of spanning STRING tokens that may contain backslash
        # continuations and leading spaces on the next physical line.
        normalized_lines = []
        indent_widths = [0]
        depth = 0
        string_rows = _continued_string_rows("\n".join(lines))
        for row, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            if stripped:
                if logical_depths:
                    depth = logical_depths.get(row, depth)
                else:
                    prefix = line[: len(line) - len(stripped)]
                    indent_width = len(prefix.expandtabs(8))
                    while indent_width < indent_widths[-1]:
                        indent_widths.pop()
                    if indent_width > indent_widths[-1]:
                        indent_widths.append(indent_width)
                    depth = len(indent_widths) - 1
                normalized_indent = depth * "    "
                if row in string_rows:
                    normalized_lines.append(normalized_indent + line.strip())
                else:
                    normalized_lines.append(normalized_indent + _normalize_python_line(stripped))

        return "\n".join(normalized_lines)


class JavaScriptNormalizer:
    """Normalizes JavaScript/TypeScript code."""

    def normalize(self, code: str) -> str:
        """
        Normalize JavaScript code.

        Args:
            code: Raw JavaScript code

        Returns:
            Normalized code
        """
        # Remove single-line comments
        code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)

        # Remove multi-line comments
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)

        # Remove blank lines
        lines = [line for line in code.split("\n") if line.strip()]

        # Normalize whitespace
        normalized_lines = []
        for line in lines:
            stripped = line.lstrip()
            if stripped:
                indent_level = len(line) - len(stripped)
                # Normalize to 2-space indents (JS convention)
                normalized_indent = (indent_level // 2) * "  "
                normalized_lines.append(normalized_indent + " ".join(stripped.split()))

        return "\n".join(normalized_lines)


class GenericNormalizer:
    """Generic normalizer for unknown languages."""

    def normalize(self, code: str) -> str:
        """
        Normalize code generically.

        Args:
            code: Raw code

        Returns:
            Normalized code
        """
        # Remove blank lines
        lines = [line for line in code.split("\n") if line.strip()]

        # Normalize whitespace
        normalized_lines = []
        for line in lines:
            # Just normalize internal whitespace
            normalized_lines.append(" ".join(line.split()))

        return "\n".join(normalized_lines)


class NormalizedDetector:
    """Detects duplicates after normalizing code."""

    def __init__(
        self,
        root_path: Path,
        exclude_patterns: list[str] | None = None,
        respect_gitignore: bool = True,
        normalize_identifiers: bool = False,
    ):
        """
        Initialize normalized detector.

        Args:
            root_path: Repository root path
            exclude_patterns: Patterns to exclude
            respect_gitignore: Whether to respect .gitignore
            normalize_identifiers: Whether to normalize variable names (future)
        """
        self.root_path = Path(root_path)
        self.exclude_patterns = exclude_patterns or []
        self.respect_gitignore = respect_gitignore
        self.normalize_identifiers = normalize_identifiers

        # Use ExactDetector for file walking
        self.exact_detector = ExactDetector(root_path, exclude_patterns, respect_gitignore)

        # Language-specific normalizers
        self.normalizers: dict[str, PythonNormalizer | JavaScriptNormalizer | GenericNormalizer] = {
            "python": PythonNormalizer(),
            "javascript": JavaScriptNormalizer(),
            "typescript": JavaScriptNormalizer(),  # Same as JS
        }
        self.generic_normalizer = GenericNormalizer()

    def normalize_content(self, content: str, language: str) -> str:
        """
        Normalize code content for comparison.

        Args:
            content: Raw code content
            language: Programming language

        Returns:
            Normalized content
        """
        normalizer = self.normalizers.get(language, self.generic_normalizer)
        return normalizer.normalize(content)

    def compute_normalized_hash(self, normalized_content: str) -> str:
        """
        Compute hash of normalized content.

        Args:
            normalized_content: Normalized code

        Returns:
            SHA256 hash
        """
        return hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()

    def scan(self) -> list[DuplicateGroup]:
        """
        Scan repository and return normalized duplicate groups.

        Returns:
            List of duplicate groups
        """
        # Build normalized_hash -> (file_path, original_hash, language) mapping
        hash_to_files: dict[str, list[tuple]] = {}

        # Scan all files
        for file_path in self.root_path.rglob("*"):
            if not file_path.is_file():
                continue

            if self.exact_detector._should_exclude(file_path):
                continue

            # Detect language
            language = self.exact_detector._detect_language(file_path)

            # Read and normalize content
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                normalized_content = self.normalize_content(content, language)
                normalized_hash = self.compute_normalized_hash(normalized_content)

                # Also compute original hash for reference
                original_hash = self.exact_detector.compute_hash(file_path)

                if normalized_hash not in hash_to_files:
                    hash_to_files[normalized_hash] = []

                hash_to_files[normalized_hash].append((file_path, original_hash, language))

            except Exception:
                # Skip files that can't be read as text
                continue

        # Create duplicate groups
        duplicate_groups = []
        group_id = 1

        for norm_hash, files in hash_to_files.items():
            # Need at least 2 files for a duplicate
            if len(files) < 2:
                continue

            # Check if files are already identical (exact duplicates)
            # If all original hashes are the same, this is an exact duplicate
            original_hashes = set(f[1] for f in files)
            if len(original_hashes) == 1:
                # This is an exact duplicate, not just normalized
                # Skip it to avoid duplicating exact detector results
                continue

            # Create member files
            member_files = []
            for file_path, original_hash, language in files:
                rel_path = str(file_path.relative_to(self.root_path))
                member_files.append(
                    MemberFile(
                        path=rel_path,
                        file_hash=original_hash,
                        normalized_hash=norm_hash,
                        similarity_score=1.0,  # Normalized duplicates are identical after normalization
                    )
                )

            # Select representative (shortest path)
            representative = min(files, key=lambda f: len(str(f[0])))
            rep_path = str(representative[0].relative_to(self.root_path))

            # Get language from representative
            language = representative[2]

            # Create snippet from first file
            summary = self.exact_detector._get_file_summary(files[0][0])

            # Create duplicate group
            group = DuplicateGroup(
                id=f"dup-norm-{group_id:03d}",
                type="normalized-file",
                language=language,
                representative_path=rep_path,
                member_files=member_files,
                reason="Identical after removing comments and normalizing whitespace",
                suggested_action="consolidate",
                confidence="high",
                tags=["normalized-duplicate", "formatting-difference"],
                meta={
                    "detection_method": ["normalized"],
                    "normalization_mode": "standard",
                },
                summary=summary,
            )

            duplicate_groups.append(group)
            group_id += 1

        return duplicate_groups
