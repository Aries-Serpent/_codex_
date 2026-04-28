#!/usr/bin/env python3
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast
import gzip
import hashlib
import json
import re
import sys
import tarfile
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class ProcessedFile:
    """Represents a processed file in the dataset."""
    path: str
    relative_path: str
    category: str  # documentation, source_code, notebook, config, etc.
    size_original: int
    size_compressed: int
    checksum: str
    last_modified: str
    quality_score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    extracted_content: Optional[str] = None
    compression_ratio: float = 0.0


@dataclass
class DatasetManifest:
    """Manifest for a versioned dataset."""
    version: str
    created_at: str
    total_files: int
    total_size_original: int
    total_size_compressed: int
    compression_ratio: float
    file_categories: dict[str, int]
    files: list[ProcessedFile]
    quality_metrics: dict[str, float]


class FileProcessor:
    """Enhanced file processing with category-specific handling."""

    # File category mappings
    CATEGORIES = {
        'documentation': {'.md', '.rst', '.adoc', '.txt'},
        'source_code': {'.py', '.js', '.ts', '.go', '.java', '.cpp', '.c', '.rs'},
        'notebook': {'.ipynb'},
        'config': {'.yaml', '.yml', '.json', '.toml', '.ini', '.cfg'},
        'binary_doc': {'.pdf', '.docx', '.pptx'},
        'media': {'.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mp3'},
        'database': {'.sql', '.db', '.sqlite'},
        'archive': {'.zip', '.tar', '.gz', '.bz2', '.xz'},
    }

    # Files to skip
    SKIP_PATTERNS = {
        '.git', '.venv', 'venv', '__pycache__', 'node_modules',
        '.tox', '.pytest_cache', '.mypy_cache', '.ruff_cache',
        'dist', 'build', '*.egg-info'
    }

    @classmethod
    def categorize_file(cls, filepath: Path) -> Optional[str]:
        """Determine file category based on extension."""
        ext = filepath.suffix.lower()
        for category, extensions in cls.CATEGORIES.items():
            if ext in extensions:
                return category
        return None

    @classmethod
    def should_skip(cls, filepath: Path) -> bool:
        """Check if file should be skipped."""
        for pattern in cls.SKIP_PATTERNS:
            if pattern in filepath.parts:
                return True
            if pattern.startswith('*') and filepath.name.endswith(pattern[1:]):
                return True
        return False

    @classmethod
    def calculate_checksum(cls, filepath: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            return ""

    @classmethod
    def process_documentation(cls, filepath: Path) -> tuple[Optional[str], float]:
        """Process documentation files with structure extraction."""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')

            # Extract headers and structure
            headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
            code_blocks = re.findall(r'```[\s\S]*?```', content)

            # Quality score based on structure
            quality = min(1.0, (len(headers) * 0.1 + len(code_blocks) * 0.05))

            # Extract metadata
            metadata = {
                'headers_count': len(headers),
                'code_blocks_count': len(code_blocks),
                'has_structure': len(headers) > 0
            }

            return json.dumps(metadata), quality

        except Exception as e:
            logger.debug(f"Exception: {e}")
            print(f"Warning: Could not process documentation {filepath}: {e}", file=sys.stderr)
            return None, 0.5

    @classmethod
    def process_source_code(cls, filepath: Path) -> tuple[Optional[str], float]:
        """Process source code with AST analysis."""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')

            # For Python files, use AST
            if filepath.suffix == '.py':
                try:
                    tree = ast.parse(content)

                    # Extract entities
                    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

                    # Count imports
                    imports = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])

                    # Calculate complexity (simple metric)
                    complexity = len(classes) + len(functions) + imports

                    metadata = {
                        'classes': len(classes),
                        'functions': len(functions),
                        'imports': imports,
                        'complexity': complexity
                    }

                    # Quality score based on code structure
                    quality = min(1.0, 0.5 + (complexity * 0.01))

                    return json.dumps(metadata), quality

                except SyntaxError as e:
                    logger.debug(f"SyntaxError: {e}")
                    logger.warning(f"SyntaxError: {e}", exc_info=True)
                    return None, 0.3

            # For other languages, basic metrics
            lines = content.split('\n')
            non_empty = [line_item for line_item in lines if line_item.strip()]
            comments = [line_item for line_item in lines if line_item.strip().startswith(('#', '//', '/*'))]

            quality = min(1.0, len(non_empty) / max(len(lines), 1))

            metadata = {
                'lines': len(lines),
                'non_empty_lines': len(non_empty),
                'comment_lines': len(comments)
            }

            return json.dumps(metadata), quality

        except Exception as e:
            logger.debug(f"Exception: {e}")
            print(f"Warning: Could not process source code {filepath}: {e}", file=sys.stderr)
            return None, 0.5

    @classmethod
    def process_config(cls, filepath: Path) -> tuple[Optional[str], float]:
        """Process configuration files with schema extraction."""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')

            # Try to parse as JSON/YAML
            metadata = {}
            quality = 0.7

            if filepath.suffix == '.json':
                try:
                    data = json.loads(content)
                    metadata['keys_count'] = len(data) if isinstance(data, dict) else 0
                    metadata['is_valid'] = True
                    quality = 0.9
                except json.JSONDecodeError:
                    metadata['is_valid'] = False
                    quality = 0.3

            return json.dumps(metadata), quality

        except Exception as e:
            logger.debug(f"Exception: {e}")
            print(f"Warning: Could not process config {filepath}: {e}", file=sys.stderr)
            return None, 0.5

    @classmethod
    def process_file(cls, filepath: Path, root: Path) -> Optional[ProcessedFile]:
        """Process a single file based on its category."""
        if cls.should_skip(filepath):
            return None

        category = cls.categorize_file(filepath)
        if not category:
            return None

        # Get file stats
        stat = filepath.stat()
        relative_path = str(filepath.relative_to(root))
        checksum = cls.calculate_checksum(filepath)

        # Process based on category
        extracted_content, quality = None, 0.5

        if category == 'documentation':
            extracted_content, quality = cls.process_documentation(filepath)
        elif category == 'source_code':
            extracted_content, quality = cls.process_source_code(filepath)
        elif category == 'config':
            extracted_content, quality = cls.process_config(filepath)

        # Calculate compressed size (estimate)
        try:
            with open(filepath, 'rb') as f:
                compressed = gzip.compress(f.read())
                size_compressed = len(compressed)
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            size_compressed = stat.st_size

        compression_ratio = size_compressed / max(stat.st_size, 1)

        return ProcessedFile(
            path=str(filepath),
            relative_path=relative_path,
            category=category,
            size_original=stat.st_size,
            size_compressed=size_compressed,
            checksum=checksum,
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            quality_score=quality,
            metadata={'extracted_metadata': extracted_content} if extracted_content else {},
            compression_ratio=compression_ratio
        )


class DatasetManager:
    """Manages dataset creation, compression, and versioning."""

    def __init__(self, repo_path: Path, output_dir: Optional[Path] = None):
        self.repo_path = repo_path.resolve()
        self.output_dir = output_dir or (repo_path / ".codex" / "datasets")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.processed_files: list[ProcessedFile] = []
        self.dedup_checksums: set[str] = set()

    def scan_repository(self, include_patterns: Optional[list[str]] = None) -> int:
        """Scan repository and process files."""
        print(f"Scanning repository: {self.repo_path}")

        count = 0
        for filepath in self.repo_path.rglob("*"):
            if not filepath.is_file():
                continue

            # Skip if in skip directory
            if any(FileProcessor.should_skip(parent) for parent in filepath.parents):
                continue

            processed = FileProcessor.process_file(filepath, self.repo_path)
            if processed:
                # Deduplication by checksum
                if processed.checksum and processed.checksum not in self.dedup_checksums:
                    self.processed_files.append(processed)
                    self.dedup_checksums.add(processed.checksum)
                    count += 1

                    if count % 100 == 0:
                        print(f"  Processed {count} files...", end='\r')

        print(f"✓ Processed {count} unique files                    ")
        return count

    def create_compressed_archive(self, version: str, format: str = "tar.gz") -> Path:
        """Create compressed archive of processed dataset."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"dataset_{version}_{timestamp}.{format}"
        archive_path = self.output_dir / archive_name

        print(f"Creating compressed archive: {archive_name}")

        if format in {"tar", "tar.gz"} or format.endswith(".tar.gz"):
            with tarfile.open(archive_path, "w:gz") as tar:
                for pf in self.processed_files:
                    try:
                        tar.add(pf.path, arcname=pf.relative_path)
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        print(f"Warning: Could not add {pf.path}: {e}", file=sys.stderr)

        elif format == "zip":
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for pf in self.processed_files:
                    try:
                        zf.write(pf.path, arcname=pf.relative_path)
                    except Exception as e:
                        logger.debug(f"Exception: {e}")
                        print(f"Warning: Could not add {pf.path}: {e}", file=sys.stderr)

        print(f"✓ Created archive: {archive_path}")
        return archive_path

    def generate_manifest(self, version: str) -> DatasetManifest:
        """Generate dataset manifest with metadata."""
        total_size_orig = sum(pf.size_original for pf in self.processed_files)
        total_size_comp = sum(pf.size_compressed for pf in self.processed_files)

        # Category counts
        category_counts = {}
        for pf in self.processed_files:
            category_counts[pf.category] = category_counts.get(pf.category, 0) + 1

        # Quality metrics
        avg_quality = sum(pf.quality_score for pf in self.processed_files) / max(len(self.processed_files), 1)
        avg_compression = sum(pf.compression_ratio for pf in self.processed_files) / max(len(self.processed_files), 1)

        quality_metrics = {
            'average_quality_score': avg_quality,
            'average_compression_ratio': avg_compression,
            'files_with_high_quality': sum(1 for pf in self.processed_files if pf.quality_score > 0.7),
            'files_with_low_quality': sum(1 for pf in self.processed_files if pf.quality_score < 0.3)
        }

        return DatasetManifest(
            version=version,
            created_at=datetime.now().isoformat(),
            total_files=len(self.processed_files),
            total_size_original=total_size_orig,
            total_size_compressed=total_size_comp,
            compression_ratio=total_size_comp / max(total_size_orig, 1),
            file_categories=category_counts,
            files=self.processed_files,
            quality_metrics=quality_metrics
        )

    def save_manifest(self, manifest: DatasetManifest, version: str) -> Path:
        """Save manifest to disk."""
        manifest_path = self.output_dir / f"manifest_{version}.json"

        # Convert to dict
        manifest_dict = asdict(manifest)

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_dict, f, indent=2)

        print(f"✓ Saved manifest: {manifest_path}")
        return manifest_path

    def print_summary(self, manifest: DatasetManifest):
        """Print dataset summary statistics."""
        print("\n" + "="*60)
        print(f"Dataset Summary - Version {manifest.version}")
        print("="*60)
        print(f"Total Files: {manifest.total_files}")
        print(f"Original Size: {manifest.total_size_original / 1024 / 1024:.2f} MB")
        print(f"Compressed Size: {manifest.total_size_compressed / 1024 / 1024:.2f} MB")
        print(f"Compression Ratio: {manifest.compression_ratio:.2%}")
        print(f"Space Saved: {(1 - manifest.compression_ratio) * 100:.1f}%")
        print("\nFile Categories:")
        for category, count in sorted(manifest.file_categories.items()):
            print(f"  {category}: {count}")
        print("\nQuality Metrics:")
        for metric, value in manifest.quality_metrics.items():
            print(f"  {metric}: {value:.3f}")
        print("="*60)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced dataset pipeline")
    parser.add_argument("--repo", type=Path, default=Path.cwd(),
                        help="Repository path")
    parser.add_argument("--output", type=Path,
                        help="Output directory for datasets")
    parser.add_argument("--version", default="v1.0",
                        help="Dataset version")
    parser.add_argument("--format", default="tar.gz",
                        choices=["tar.gz", "zip"],
                        help="Archive format")
    parser.add_argument("--no-archive", action="store_true",
                        help="Skip archive creation (manifest only)")

    args = parser.parse_args()

    manager = DatasetManager(args.repo, args.output)

    # Scan and process files
    count = manager.scan_repository()

    if count == 0:
        print("No files to process")
        return 1

    # Generate manifest
    manifest = manager.generate_manifest(args.version)

    # Save manifest
    manager.save_manifest(manifest, args.version)

    # Create archive if requested
    if not args.no_archive:
        manager.create_compressed_archive(args.version, args.format)

    # Print summary
    manager.print_summary(manifest)

    return 0


if __name__ == "__main__":
    sys.exit(main())
