#!/usr/bin/env python3
"""
Simple script to list all folder paths in the repository.
Outputs multiple formats: plain text, markdown with links, categorized, tree, JSON, and compressed.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path
from typing import Any

# Try importing optional compression libraries
try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False

IGNORE_PATTERNS = {
    '.git', '.venv', 'node_modules', '__pycache__', 
    '.pytest_cache', '.hypothesis', 'dist', 'build',
    '.mypy_cache', '.tox', 'htmlcov', '.eggs', 'venv',
    '.codex_cache', '.nox', 'target', 'bin', 'obj',
}


def should_ignore(path: Path) -> bool:
    """Check if path should be ignored."""
    parts = path.parts
    return any(pattern in parts for pattern in IGNORE_PATTERNS)


def list_all_folders(root: Path) -> list[str]:
    """Get list of all folders in repository."""
    folders = []
    
    # Add root
    folders.append('.')
    
    # Find all subdirectories
    for item in sorted(root.rglob('*')):
        if item.is_dir() and not should_ignore(item):
            rel_path = item.relative_to(root)
            folders.append(str(rel_path))
    
    return sorted(folders)


def list_all_files(root: Path) -> dict[str, list[str]]:
    """Get mapping of folders to files within them."""
    files_by_folder: dict[str, list[str]] = {}
    
    # Process root directory
    root_files = [f.name for f in root.iterdir() if f.is_file() and not f.name.startswith('.')]
    if root_files:
        files_by_folder['.'] = sorted(root_files)
    
    # Find all files
    for item in sorted(root.rglob('*')):
        if item.is_file() and not should_ignore(item):
            folder = item.parent.relative_to(root)
            folder_str = str(folder) if str(folder) != '.' else '.'
            if folder_str not in files_by_folder:
                files_by_folder[folder_str] = []
            files_by_folder[folder_str].append(item.name)
    
    # Sort files within each folder
    for folder in files_by_folder:
        files_by_folder[folder] = sorted(files_by_folder[folder])
    
    return files_by_folder


def generate_plain_list(folders: list[str]) -> str:
    """Generate plain text list."""
    return '\n'.join(folders)


def generate_markdown_links(folders: list[str], root: Path) -> str:
    """Generate markdown with clickable folder links."""
    lines = []
    lines.append("# Repository Folder Links")
    lines.append(f"\nTotal Folders: {len(folders)}\n")
    lines.append("---\n")
    lines.append("## All Folders (Alphabetical)\n")
    
    for folder in folders:
        # Create relative link
        if folder == '.':
            lines.append(f"- [`.` (root)](.)")
        else:
            lines.append(f"- [`{folder}`]({folder})")
    
    return '\n'.join(lines)


def generate_categorized_links(folders: list[str]) -> str:
    """Generate categorized folder links."""
    lines = []
    lines.append("# Repository Folder Links (Categorized)")
    lines.append(f"\nTotal Folders: {len(folders)}\n")
    lines.append("---\n")
    
    # Categorize by top-level directory
    categories: dict[str, list[str]] = {}
    for folder in folders:
        if folder == '.':
            categories.setdefault('root', []).append(folder)
        else:
            parts = folder.split('/')
            top_level = parts[0]
            categories.setdefault(top_level, []).append(folder)
    
    for category in sorted(categories.keys()):
        lines.append(f"\n## {category.upper()}\n")
        for folder in sorted(categories[category]):
            if folder == '.':
                lines.append(f"- [`.` (root)](.)")
            else:
                lines.append(f"- [`{folder}`]({folder})")
    
    return '\n'.join(lines)


def generate_tree_with_links(folders: list[str], max_depth: int = 10) -> str:
    """Generate tree structure with links."""
    lines = []
    lines.append("# Repository Folder Tree (with Links)")
    lines.append(f"\nTotal Folders: {len(folders)}\n")
    lines.append("---\n")
    
    # Build tree structure
    tree: dict[str, Any] = {}
    for folder in folders:
        if folder == '.':
            continue
        parts = folder.split('/')
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
    
    def render_tree(node: dict[str, Any], prefix: str = "", path: str = ".", depth: int = 0) -> None:
        if depth > max_depth:
            return
        
        items = sorted(node.items())
        for i, (name, children) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            current_path = f"{path}/{name}" if path != "." else name
            
            # Add link
            lines.append(f"{prefix}{connector}[`{name}`]({current_path})")
            
            if children:
                child_prefix = prefix + ("    " if is_last else "│   ")
                render_tree(children, child_prefix, current_path, depth + 1)
    
    lines.append("[`.` (root)](.)\n")
    render_tree(tree)
    
    return '\n'.join(lines)


def generate_files_markdown(files_by_folder: dict[str, list[str]]) -> str:
    """Generate markdown with files in each folder."""
    lines = []
    lines.append("# Repository Files by Folder")
    lines.append(f"\nTotal Folders: {len(files_by_folder)}\n")
    lines.append("---\n")
    
    for folder in sorted(files_by_folder.keys()):
        files = files_by_folder[folder]
        lines.append(f"\n## `{folder}`\n")
        lines.append(f"**Files**: {len(files)}\n")
        for file in files:
            file_path = f"{folder}/{file}" if folder != '.' else file
            lines.append(f"- [`{file}`]({file_path})")
    
    return '\n'.join(lines)


def generate_json_output(
    folders: list[str],
    files_by_folder: dict[str, list[str]] | None = None,
    include_summaries: bool = False
) -> dict[str, Any]:
    """Generate JSON output."""
    output: dict[str, Any] = {
        "total_folders": len(folders),
        "folders": folders
    }
    
    if files_by_folder:
        output["files_by_folder"] = files_by_folder
        output["total_files"] = sum(len(files) for files in files_by_folder.values())
    
    if include_summaries:
        # Basic summaries for folders
        output["summaries"] = {}
        for folder in folders:
            if files_by_folder and folder in files_by_folder:
                file_count = len(files_by_folder[folder])
                output["summaries"][folder] = f"Contains {file_count} file(s)"
            else:
                output["summaries"][folder] = "No files"
    
    return output


def save_compressed(data: str, output_path: Path, format: str) -> None:
    """Save compressed data."""
    if format == 'gzip':
        with gzip.open(output_path.with_suffix('.gz'), 'wt', encoding='utf-8') as f:
            f.write(data)
    elif format == 'brotli':
        if not HAS_BROTLI:
            print(f"⚠️  Brotli not available. Install with: pip install brotli")
            return
        compressed = brotli.compress(data.encode('utf-8'))
        output_path.with_suffix('.br').write_bytes(compressed)
    elif format == 'zstd':
        if not HAS_ZSTD:
            print(f"⚠️  Zstandard not available. Install with: pip install zstandard")
            return
        cctx = zstd.ZstdCompressor()
        compressed = cctx.compress(data.encode('utf-8'))
        output_path.with_suffix('.zst').write_bytes(compressed)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='List all folders in repository with multiple output formats'
    )
    parser.add_argument(
        '--root',
        type=Path,
        default=Path('.'),
        help='Repository root path (default: current directory)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('.codex/repository_structure'),
        help='Output directory (default: .codex/repository_structure)'
    )
    parser.add_argument(
        '--format',
        choices=['plain', 'markdown', 'categorized', 'tree', 'files', 'json', 'jsonl', 'all'],
        default='all',
        help='Output format (default: all)'
    )
    parser.add_argument(
        '--include-files',
        action='store_true',
        help='Also list files within folders'
    )
    parser.add_argument(
        '--compress',
        choices=['gzip', 'brotli', 'zstd', 'all'],
        help='Compress JSON output'
    )
    parser.add_argument(
        '--include-summaries',
        action='store_true',
        help='Include summary comments in JSON output'
    )
    
    args = parser.parse_args()
    
    root = args.root.resolve()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 Scanning folders in: {root}")
    folders = list_all_folders(root)
    print(f"✅ Found {len(folders)} folders")
    
    files_by_folder = None
    if args.include_files:
        print(f"🔍 Scanning files...")
        files_by_folder = list_all_files(root)
        total_files = sum(len(files) for files in files_by_folder.values())
        print(f"✅ Found {total_files} files")
    
    # Generate outputs based on format
    if args.format in ['plain', 'all']:
        # Plain text list
        plain_file = output_dir / 'ALL_FOLDERS.txt'
        plain_file.write_text(generate_plain_list(folders), encoding='utf-8')
        print(f"📝 Saved plain list: {plain_file}")
    
    if args.format in ['markdown', 'all']:
        # Markdown with links
        md_file = output_dir / 'ALL_FOLDERS_LINKS.md'
        md_content = generate_markdown_links(folders, root)
        md_file.write_text(md_content, encoding='utf-8')
        print(f"📝 Saved markdown links: {md_file}")
    
    if args.format in ['categorized', 'all']:
        # Categorized markdown
        cat_file = output_dir / 'ALL_FOLDERS_CATEGORIZED.md'
        cat_content = generate_categorized_links(folders)
        cat_file.write_text(cat_content, encoding='utf-8')
        print(f"📝 Saved categorized links: {cat_file}")
    
    if args.format in ['tree', 'all']:
        # Tree with links
        tree_file = output_dir / 'ALL_FOLDERS_TREE.md'
        tree_content = generate_tree_with_links(folders)
        tree_file.write_text(tree_content, encoding='utf-8')
        print(f"📝 Saved tree with links: {tree_file}")
    
    if args.format in ['files', 'all'] and files_by_folder:
        # Files by folder
        files_file = output_dir / 'ALL_FILES_BY_FOLDER.md'
        files_content = generate_files_markdown(files_by_folder)
        files_file.write_text(files_content, encoding='utf-8')
        print(f"📝 Saved files by folder: {files_file}")
    
    if args.format in ['json', 'jsonl', 'all']:
        # JSON output
        json_data = generate_json_output(folders, files_by_folder, args.include_summaries)
        
        # Regular JSON
        json_file = output_dir / 'repository_structure.json'
        json_file.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
        print(f"📝 Saved JSON: {json_file}")
        
        # JSONL (one folder per line)
        if args.format in ['jsonl', 'all']:
            jsonl_file = output_dir / 'repository_structure.jsonl'
            with jsonl_file.open('w', encoding='utf-8') as f:
                for folder in folders:
                    entry = {"folder": folder}
                    if files_by_folder and folder in files_by_folder:
                        entry["files"] = files_by_folder[folder]
                    f.write(json.dumps(entry) + '\n')
            print(f"📝 Saved JSONL: {jsonl_file}")
        
        # Compressed formats
        if args.compress:
            json_str = json.dumps(json_data)
            compress_formats = ['gzip', 'brotli', 'zstd'] if args.compress == 'all' else [args.compress]
            
            for fmt in compress_formats:
                save_compressed(json_str, json_file, fmt)
                suffix = {'gzip': '.gz', 'brotli': '.br', 'zstd': '.zst'}[fmt]
                print(f"📦 Saved {fmt.upper()} compressed: {json_file.with_suffix(suffix)}")
    
    print(f"\n✅ Complete! All outputs saved to: {output_dir}/")
    print(f"\nGenerated files:")
    if args.format in ['plain', 'all']:
        print(f"  - ALL_FOLDERS.txt (plain text list)")
    if args.format in ['markdown', 'all']:
        print(f"  - ALL_FOLDERS_LINKS.md (alphabetical with links)")
    if args.format in ['categorized', 'all']:
        print(f"  - ALL_FOLDERS_CATEGORIZED.md (grouped by top-level)")
    if args.format in ['tree', 'all']:
        print(f"  - ALL_FOLDERS_TREE.md (tree structure with links)")
    if args.format in ['files', 'all'] and files_by_folder:
        print(f"  - ALL_FILES_BY_FOLDER.md (files in each folder)")
    if args.format in ['json', 'jsonl', 'all']:
        print(f"  - repository_structure.json (JSON format)")
        if args.format in ['jsonl', 'all']:
            print(f"  - repository_structure.jsonl (JSON Lines format)")
        if args.compress:
            compress_formats = ['gzip', 'brotli', 'zstd'] if args.compress == 'all' else [args.compress]
            for fmt in compress_formats:
                suffix = {'gzip': '.gz', 'brotli': '.br', 'zstd': '.zst'}[fmt]
                print(f"  - repository_structure{suffix} ({fmt.upper()} compressed)")


if __name__ == '__main__':
    main()
