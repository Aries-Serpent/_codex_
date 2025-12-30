#!/usr/bin/env python3
"""
Component Selection Tool for ChatGPT Project Packaging
Filters repository files by topic or custom glob patterns
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Set
import fnmatch


def load_topics(topics_file: Path) -> dict:
    """Load topic-to-path mappings from JSON file"""
    with open(topics_file, 'r') as f:
        return json.load(f)


def expand_globs(patterns: List[str], base_dir: Path) -> Set[Path]:
    """Expand glob patterns to actual file paths"""
    matched_files = set()
    
    for pattern in patterns:
        # Handle ** recursive patterns
        if '**' in pattern:
            # Split into parts and handle recursively
            parts = pattern.split('/')
            if parts[0] == '.':
                parts = parts[1:]
            
            # Find the first ** position (guaranteed to exist due to if condition)
            star_idx = parts.index('**')
            # Path before **
            prefix = '/'.join(parts[:star_idx]) if star_idx > 0 else '.'
            # Pattern after **
            suffix_pattern = '/'.join(parts[star_idx+1:]) if star_idx < len(parts) - 1 else '*'
            
            prefix_path = base_dir / prefix
            if prefix_path.exists():
                for path in prefix_path.rglob(suffix_pattern):
                    if path.is_file():
                        matched_files.add(path.relative_to(base_dir))
        else:
            # Simple glob without **
            for path in base_dir.glob(pattern):
                if path.is_file():
                    matched_files.add(path.relative_to(base_dir))
    
    return matched_files


def filter_by_topic(topic: str, topics_map: dict, base_dir: Path) -> Set[Path]:
    """Filter files by topic using the topics map"""
    if topic not in topics_map:
        raise ValueError(f"Unknown topic: {topic}. Available topics: {', '.join(topics_map.keys())}")
    
    patterns = topics_map[topic]
    return expand_globs(patterns, base_dir)


def filter_by_globs(glob_patterns: str, base_dir: Path) -> Set[Path]:
    """Filter files by custom glob patterns (comma-separated)"""
    patterns = [p.strip() for p in glob_patterns.split(',') if p.strip()]
    return expand_globs(patterns, base_dir)


def main():
    parser = argparse.ArgumentParser(
        description='Select repository components by topic or glob patterns',
        epilog='Example: python select_components.py --topic zendesk --output filelist.txt'
    )
    parser.add_argument(
        '--topic',
        help='Topic to select (zendesk, agents, quantum, docs, mcp, workflows)'
    )
    parser.add_argument(
        '--overrides',
        help='Comma-separated glob patterns to override topic (e.g., "src/**/*.py,docs/*.md")'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output file path for the file list'
    )
    parser.add_argument(
        '--topics-file',
        type=Path,
        default=Path(__file__).parent / 'topics.json',
        help='Path to topics.json file (default: same directory as script)'
    )
    parser.add_argument(
        '--base-dir',
        type=Path,
        default=Path.cwd(),
        help='Base directory for file selection (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.topic and not args.overrides:
        parser.error('Either --topic or --overrides must be specified')
    
    if not args.topics_file.exists():
        print(f"Error: Topics file not found: {args.topics_file}", file=sys.stderr)
        return 1
    
    # Load topics
    topics_map = load_topics(args.topics_file)
    
    # Select files
    try:
        if args.overrides:
            print(f"Selecting files using custom globs: {args.overrides}")
            selected_files = filter_by_globs(args.overrides, args.base_dir)
        else:
            print(f"Selecting files for topic: {args.topic}")
            selected_files = filter_by_topic(args.topic, topics_map, args.base_dir)
        
        # Sort for consistent output
        selected_files = sorted(selected_files)
        
        print(f"Selected {len(selected_files)} files")
        
        # Write output
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            for file_path in selected_files:
                f.write(str(file_path) + '\n')
        
        print(f"File list written to: {args.output}")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
