#!/usr/bin/env python3
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class CodeEntity:
    """Represents a searchable code entity."""
    type: str  # function, class, module, constant, method
    name: str
    path: str
    line_start: int
    line_end: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    complexity: int = 1
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            content = f"{self.type}:{self.name}:{self.path}:{self.line_start}"
            self.hash = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[:16]


@dataclass
class FileIndex:
    """Index entry for a single file."""
    path: str
    relative_path: str
    language: str
    size: int
    last_modified: str
    entities: list[CodeEntity] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    summary: str = ""
    keywords: list[str] = field(default_factory=list)
    semantic_tags: list[str] = field(default_factory=list)


class RepositoryIndexer:
    """Generate AI-optimized repository indices."""

    # File patterns to index
    PYTHON_EXTENSIONS = {'.py'}
    CONFIG_EXTENSIONS = {'.yaml', '.yml', '.toml', '.ini', '.json', '.cfg'}
    DOC_EXTENSIONS = {'.md', '.rst', '.txt'}

    # Directories to skip
    SKIP_DIRS = {
        '.git', '.venv', 'venv', '__pycache__', '.tox', '.pytest_cache',
        'node_modules', 'dist', 'build', '.eggs', '*.egg-info',
        '.hypothesis', '.mypy_cache', '.ruff_cache'
    }

    def __init__(self, repo_path: Path, output_dir: Optional[Path] = None):
        self.repo_path = repo_path.resolve()
        self.output_dir = output_dir or (repo_path / ".codex" / "ai_index")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Indices
        self.semantic_index: dict[str, list[str]] = {}  # keyword -> file paths
        self.structural_index: dict[str, Any] = {}  # module hierarchy
        self.content_index: dict[str, FileIndex] = {}  # file path -> FileIndex
        self.metadata_index: dict[str, Any] = {}  # aggregated metadata
        self.entity_index: dict[str, CodeEntity] = {}  # entity hash -> CodeEntity

    def should_skip_dir(self, dir_path: Path) -> bool:
        """Check if directory should be skipped."""
        dir_name = dir_path.name
        return any(
            dir_name == skip or dir_name.startswith(skip.rstrip('*'))
            for skip in self.SKIP_DIRS
        )

    def extract_python_entities(self, filepath: Path) -> list[CodeEntity]:
        """Extract code entities from Python file using AST."""
        entities = []

        try:
            content = filepath.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(filepath))
        except (SyntaxError, UnicodeDecodeError, ValueError) as e:
            logger.debug(f"Exception: {e}")
            print(f"⚠ Warning: Could not parse {filepath}: {e}", file=sys.stderr)
            return entities

        relative_path = str(filepath.relative_to(self.repo_path))

        for node in ast.walk(tree):
            entity = None

            if isinstance(node, ast.ClassDef):
                entity = CodeEntity(
                    type="class",
                    name=node.name,
                    path=relative_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    docstring=ast.get_docstring(node),
                    tags=self._extract_tags(node)
                )

            elif isinstance(node, ast.FunctionDef):
                # Determine if it's a method or function
                is_method = any(
                    isinstance(parent, ast.ClassDef)
                    for parent in ast.walk(tree)
                    if any(n is node for n in ast.walk(parent))
                )

                entity = CodeEntity(
                    type="method" if is_method else "function",
                    name=node.name,
                    path=relative_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    signature=self._extract_signature(node),
                    docstring=ast.get_docstring(node),
                    tags=self._extract_tags(node)
                )

            elif isinstance(node, ast.AsyncFunctionDef):
                entity = CodeEntity(
                    type="async_function",
                    name=node.name,
                    path=relative_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    signature=self._extract_signature(node),
                    docstring=ast.get_docstring(node),
                    tags=["async"] + self._extract_tags(node)
                )

            if entity and not entity.name.startswith('_'):
                entities.append(entity)
                self.entity_index[entity.hash] = entity

        return entities

    def _extract_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract function signature."""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        return f"{node.name}({', '.join(args)})"

    def _extract_tags(self, node: ast.AST) -> list[str]:
        """Extract semantic tags from AST node."""
        tags = []

        # Check decorators
        if hasattr(node, 'decorator_list'):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    tags.append(f"@{decorator.id}")
                elif isinstance(decorator, ast.Attribute):
                    tags.append(f"@{decorator.attr}")

        return tags

    def extract_imports(self, filepath: Path) -> list[str]:
        """Extract import statements from Python file."""
        imports = []

        try:
            content = filepath.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(filepath))
        except (SyntaxError, UnicodeDecodeError, ValueError):
            logger.debug("Exception caught, returning", exc_info=True)
            return imports

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)

        return imports

    def extract_keywords(self, content: str, docstring: Optional[str] = None) -> list[str]:
        """Extract semantic keywords from content."""
        keywords = set()

        # Extract from docstring if available
        if docstring:
            # Simple keyword extraction: words longer than 3 chars
            words = re.findall(r'\b[a-z]{4,}\b', docstring.lower())
            keywords.update(words[:20])  # Limit keywords

        # Extract class/function names from content
        class_pattern = r'class\s+([A-Z][a-zA-Z0-9_]*)'
        func_pattern = r'def\s+([a-z_][a-zA-Z0-9_]*)'

        keywords.update(re.findall(class_pattern, content))
        keywords.update(re.findall(func_pattern, content))

        return sorted(keywords)[:30]  # Limit to 30 keywords

    def index_file(self, filepath: Path) -> Optional[FileIndex]:
        """Create index entry for a single file."""
        if not filepath.is_file():
            return None

        relative_path = str(filepath.relative_to(self.repo_path))
        extension = filepath.suffix.lower()

        # Determine language
        if extension in self.PYTHON_EXTENSIONS:
            language = "python"
        elif extension in self.CONFIG_EXTENSIONS:
            language = "config"
        elif extension in self.DOC_EXTENSIONS:
            language = "documentation"
        else:
            return None  # Skip unsupported files

        # Basic file info
        stat = filepath.stat()
        file_index = FileIndex(
            path=str(filepath),
            relative_path=relative_path,
            language=language,
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )

        # Extract Python-specific information
        if language == "python":
            file_index.entities = self.extract_python_entities(filepath)
            file_index.imports = self.extract_imports(filepath)

            # Extract exports from __all__ if present
            try:
                content = filepath.read_text(encoding='utf-8')
                all_pattern = r'__all__\s*=\s*\[(.*?)\]'
                match = re.search(all_pattern, content, re.DOTALL)
                if match:
                    exports = re.findall(r'["\']([^"\']+)["\']', match.group(1))
                    file_index.exports = exports

                # Extract keywords
                file_index.keywords = self.extract_keywords(content)

            except (UnicodeDecodeError, ValueError):
                # If the file cannot be decoded or parsed for __all__/keywords,
                # skip these optional enrichments but still index the file itself.
                pass

        # Add semantic tags based on path
        path_parts = Path(relative_path).parts
        file_index.semantic_tags = [
            part for part in path_parts[:-1]
            if part not in {'src', 'tests', 'scripts', 'docs'}
        ]

        return file_index

    def build_structural_index(self):
        """Build hierarchical structure of the repository."""
        structure = {}

        for file_path, file_index in self.content_index.items():
            parts = Path(file_index.relative_path).parts
            current = structure

            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Add file entry
            filename = parts[-1]
            current[filename] = {
                "language": file_index.language,
                "entities": len(file_index.entities),
                "size": file_index.size
            }

        self.structural_index = structure

    def build_semantic_index(self):
        """Build keyword-based semantic index."""
        for file_path, file_index in self.content_index.items():
            # Index by keywords
            for keyword in file_index.keywords:
                if keyword not in self.semantic_index:
                    self.semantic_index[keyword] = []
                self.semantic_index[keyword].append(file_index.relative_path)

            # Index by entity names
            for entity in file_index.entities:
                if entity.name not in self.semantic_index:
                    self.semantic_index[entity.name] = []
                self.semantic_index[entity.name].append(file_index.relative_path)

            # Index by semantic tags
            for tag in file_index.semantic_tags:
                if tag not in self.semantic_index:
                    self.semantic_index[tag] = []
                self.semantic_index[tag].append(file_index.relative_path)

    def build_metadata_index(self):
        """Build aggregated metadata index."""
        self.metadata_index = {
            "generated_at": datetime.now().isoformat(),
            "repository_path": str(self.repo_path),
            "total_files": len(self.content_index),
            "total_entities": len(self.entity_index),
            "languages": {},
            "top_keywords": [],
            "directory_summary": {}
        }

        # Count by language
        for file_index in self.content_index.values():
            lang = file_index.language
            self.metadata_index["languages"][lang] = \
                self.metadata_index["languages"].get(lang, 0) + 1

        # Top keywords
        keyword_counts = {}
        for keyword, files in self.semantic_index.items():
            keyword_counts[keyword] = len(files)

        top_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:50]
        self.metadata_index["top_keywords"] = [
            {"keyword": k, "count": c} for k, c in top_keywords
        ]

    def scan_repository(self):
        """Scan the entire repository and build indices."""
        print(f"Scanning repository: {self.repo_path}")

        file_count = 0
        for filepath in self.repo_path.rglob("*"):
            # Skip directories
            if filepath.is_dir():
                if self.should_skip_dir(filepath):
                    continue
                continue

            # Skip if in skip directory
            if any(self.should_skip_dir(parent) for parent in filepath.parents):
                continue

            # Index file
            file_index = self.index_file(filepath)
            if file_index:
                self.content_index[str(filepath)] = file_index
                file_count += 1

                if file_count % 100 == 0:
                    print(f"  Indexed {file_count} files...", end='\r')

        print(f"✓ Indexed {file_count} files                    ")

        # Build other indices
        print("Building structural index...")
        self.build_structural_index()

        print("Building semantic index...")
        self.build_semantic_index()

        print("Building metadata index...")
        self.build_metadata_index()

    def save_indices(self):
        """Save all indices to disk."""
        print(f"Saving indices to {self.output_dir}")

        # Save content index (file-level details)
        content_index_path = self.output_dir / "content_index.json"
        with open(content_index_path, 'w', encoding='utf-8') as f:
            # Convert to serializable format
            content_data = {
                path: {
                    **asdict(file_index),
                    'entities': [asdict(e) for e in file_index.entities]
                }
                for path, file_index in self.content_index.items()
            }
            json.dump(content_data, f, indent=2)
        print(f"  ✓ {content_index_path}")

        # Save semantic index (keyword -> files)
        semantic_index_path = self.output_dir / "semantic_index.json"
        with open(semantic_index_path, 'w', encoding='utf-8') as f:
            json.dump(self.semantic_index, f, indent=2)
        print(f"  ✓ {semantic_index_path}")

        # Save structural index (directory tree)
        structural_index_path = self.output_dir / "structural_index.json"
        with open(structural_index_path, 'w', encoding='utf-8') as f:
            json.dump(self.structural_index, f, indent=2)
        print(f"  ✓ {structural_index_path}")

        # Save metadata index (summary stats)
        metadata_index_path = self.output_dir / "metadata_index.json"
        with open(metadata_index_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata_index, f, indent=2)
        print(f"  ✓ {metadata_index_path}")

        # Save entity index (all code entities)
        entity_index_path = self.output_dir / "entity_index.json"
        with open(entity_index_path, 'w', encoding='utf-8') as f:
            entity_data = {
                hash: asdict(entity)
                for hash, entity in self.entity_index.items()
            }
            json.dump(entity_data, f, indent=2)
        print(f"  ✓ {entity_index_path}")

        print(f"\n✅ Generated {len(self.content_index)} file indices")
        print(f"✅ Indexed {len(self.entity_index)} code entities")
        print(f"✅ Created {len(self.semantic_index)} semantic mappings")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent

    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])

    indexer = RepositoryIndexer(repo_root)
    indexer.scan_repository()
    indexer.save_indices()

    return 0


if __name__ == "__main__":
    sys.exit(main())
