#!/usr/bin/env python3
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class SearchResult:
    """Represents a search result."""
    path: str
    relevance_score: float
    match_type: str  # semantic, structural, entity, keyword
    context: dict[str, Any]
    snippet: Optional[str] = None


class AIRepositorySearch:
    """AI-optimized repository search engine."""

    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.content_index: dict[str, Any] = {}
        self.semantic_index: dict[str, list[str]] = {}
        self.structural_index: dict[str, Any] = {}
        self.entity_index: dict[str, Any] = {}
        self.metadata_index: dict[str, Any] = {}

        self.load_indices()

    def load_indices(self):
        """Load all indices from disk."""
        try:
            with open(self.index_dir / "content_index.json", 'r') as f:
                self.content_index = json.load(f)
        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            print("⚠ Warning: content_index.json not found", file=sys.stderr)

        try:
            with open(self.index_dir / "semantic_index.json", 'r') as f:
                self.semantic_index = json.load(f)
        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            print("⚠ Warning: semantic_index.json not found", file=sys.stderr)

        try:
            with open(self.index_dir / "structural_index.json", 'r') as f:
                self.structural_index = json.load(f)
        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            print("⚠ Warning: structural_index.json not found", file=sys.stderr)

        try:
            with open(self.index_dir / "entity_index.json", 'r') as f:
                self.entity_index = json.load(f)
        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            print("⚠ Warning: entity_index.json not found", file=sys.stderr)

        try:
            with open(self.index_dir / "metadata_index.json", 'r') as f:
                self.metadata_index = json.load(f)
        except FileNotFoundError as e:
            logger.debug(f"FileNotFoundError: {e}")
            logger.warning(f"FileNotFoundError: {e}", exc_info=True)
            print("⚠ Warning: metadata_index.json not found", file=sys.stderr)

    def search_by_keyword(self, keyword: str, max_results: int = 10) -> list[SearchResult]:
        """Search for files by keyword."""
        results = []
        keyword_lower = keyword.lower()

        # Exact match
        if keyword in self.semantic_index:
            for path in self.semantic_index[keyword][:max_results]:
                results.append(SearchResult(
                    path=path,
                    relevance_score=1.0,
                    match_type="keyword_exact",
                    context={"keyword": keyword}
                ))

        # Partial match
        if len(results) < max_results:
            for key, paths in self.semantic_index.items():
                if keyword_lower in key.lower() and key != keyword:
                    for path in paths[:max(1, max_results - len(results))]:
                        if path not in [r.path for r in results]:
                            results.append(SearchResult(
                                path=path,
                                relevance_score=0.7,
                                match_type="keyword_partial",
                                context={"keyword": key, "query": keyword}
                            ))

                if len(results) >= max_results:
                    break

        return results[:max_results]

    def search_by_entity(self, entity_name: str, entity_type: Optional[str] = None) -> list[SearchResult]:
        """Search for entities (classes, functions, etc.)."""
        results = []

        for hash, entity in self.entity_index.items():
            if entity['name'] == entity_name:
                if entity_type and entity['type'] != entity_type:
                    continue

                results.append(SearchResult(
                    path=entity['path'],
                    relevance_score=1.0,
                    match_type="entity_exact",
                    context={
                        "entity": entity,
                        "line_start": entity['line_start'],
                        "line_end": entity['line_end']
                    }
                ))

        # Partial match on name
        if not results:
            entity_name_lower = entity_name.lower()
            for hash, entity in self.entity_index.items():
                if entity_name_lower in entity['name'].lower():
                    if entity_type and entity['type'] != entity_type:
                        continue

                    results.append(SearchResult(
                        path=entity['path'],
                        relevance_score=0.6,
                        match_type="entity_partial",
                        context={
                            "entity": entity,
                            "line_start": entity['line_start'],
                            "line_end": entity['line_end']
                        }
                    ))

        return results

    def search_by_path_pattern(self, pattern: str) -> list[SearchResult]:
        """Search for files matching a path pattern."""
        results = []
        pattern_lower = pattern.lower()

        for file_path, file_data in self.content_index.items():
            relative_path = file_data['relative_path']
            if pattern_lower in relative_path.lower():
                score = 1.0 if pattern in relative_path else 0.8
                results.append(SearchResult(
                    path=relative_path,
                    relevance_score=score,
                    match_type="path_pattern",
                    context={
                        "language": file_data['language'],
                        "size": file_data['size'],
                        "entities_count": len(file_data['entities'])
                    }
                ))

        return sorted(results, key=lambda r: r.relevance_score, reverse=True)

    def search_by_tag(self, tag: str) -> list[SearchResult]:
        """Search for files by semantic tag."""
        results = []

        for file_path, file_data in self.content_index.items():
            if tag in file_data.get('semantic_tags', []):
                results.append(SearchResult(
                    path=file_data['relative_path'],
                    relevance_score=1.0,
                    match_type="semantic_tag",
                    context={
                        "tags": file_data['semantic_tags'],
                        "language": file_data['language']
                    }
                ))

        return results

    def find_similar_files(self, reference_path: str, max_results: int = 5) -> list[SearchResult]:
        """Find files similar to the reference file."""
        results = []

        # Find reference file data
        reference_data = None
        for file_path, file_data in self.content_index.items():
            if file_data['relative_path'] == reference_path:
                reference_data = file_data
                break

        if not reference_data:
            return results

        # Calculate similarity based on keywords and tags
        reference_keywords = set(reference_data.get('keywords', []))
        reference_tags = set(reference_data.get('semantic_tags', []))

        similarities = []
        for file_path, file_data in self.content_index.items():
            if file_data['relative_path'] == reference_path:
                continue

            file_keywords = set(file_data.get('keywords', []))
            file_tags = set(file_data.get('semantic_tags', []))

            # Calculate Jaccard similarity
            keyword_overlap = len(reference_keywords & file_keywords)
            tag_overlap = len(reference_tags & file_tags)

            if keyword_overlap > 0 or tag_overlap > 0:
                score = (keyword_overlap * 0.7 + tag_overlap * 0.3) / max(
                    len(reference_keywords | file_keywords),
                    1
                )
                similarities.append((file_data['relative_path'], score, file_data))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        for path, score, file_data in similarities[:max_results]:
            results.append(SearchResult(
                path=path,
                relevance_score=score,
                match_type="similarity",
                context={
                    "reference": reference_path,
                    "language": file_data['language'],
                    "shared_keywords": len(reference_keywords & set(file_data.get('keywords', [])))
                }
            ))

        return results

    def get_file_details(self, relative_path: str) -> Optional[dict[str, Any]]:
        """Get detailed information about a specific file."""
        for file_path, file_data in self.content_index.items():
            if file_data['relative_path'] == relative_path:
                return file_data
        return None

    def get_repository_summary(self) -> dict[str, Any]:
        """Get repository summary statistics."""
        return self.metadata_index

    def multi_search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Perform multi-strategy search combining different search types."""
        all_results = []

        # Keyword search
        all_results.extend(self.search_by_keyword(query, max_results))

        # Entity search
        all_results.extend(self.search_by_entity(query))

        # Path pattern search
        all_results.extend(self.search_by_path_pattern(query))

        # Deduplicate and sort by relevance
        seen_paths = set()
        unique_results = []
        for result in all_results:
            if result.path not in seen_paths:
                seen_paths.add(result.path)
                unique_results.append(result)

        unique_results.sort(key=lambda r: r.relevance_score, reverse=True)
        return unique_results[:max_results]


def main():
    """Demo search interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Search AI-indexed repository")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--type", choices=["keyword", "entity", "path", "multi"],
                        default="multi", help="Search type")
    parser.add_argument("--max-results", type=int, default=10,
                        help="Maximum number of results")
    parser.add_argument("--index-dir", type=Path,
                        default=Path(__file__).parent.parent / ".codex" / "ai_index",
                        help="Index directory")

    args = parser.parse_args()

    if not args.index_dir.exists():
        print(f"❌ Index directory not found: {args.index_dir}")
        print("Run: python scripts/generate_ai_index.py")
        return 1

    search = AIRepositorySearch(args.index_dir)

    # Perform search
    if args.type == "keyword":
        results = search.search_by_keyword(args.query, args.max_results)
    elif args.type == "entity":
        results = search.search_by_entity(args.query)
    elif args.type == "path":
        results = search.search_by_path_pattern(args.query)
    else:  # multi
        results = search.multi_search(args.query, args.max_results)

    # Display results
    print(f"\n🔍 Search results for: {args.query}")
    print(f"Found {len(results)} result(s)\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result.path}")
        print(f"   Score: {result.relevance_score:.2f} | Type: {result.match_type}")
        if result.context:
            print(f"   Context: {json.dumps(result.context, indent=6)}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
