#!/usr/bin/env python3
"""
build_doc_search_index.py — Build a JSON search index from the documentation catalog.

Reads the DOC_CATALOG entries defined in
  cognitive_app/src/components/documentation/documentation-data.ts

and produces a JSON file at:
  cognitive_app/public/doc-search-index.json

The index format mirrors the in-browser inverted index so that tests and
CI validators can work against the same schema.

Usage:
    python scripts/docs/build_doc_search_index.py [--output PATH]
    python scripts/docs/build_doc_search_index.py --dry-run

Exit codes:
    0  — success
    1  — I/O or parse error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOC_DATA_TS = REPO_ROOT / "cognitive_app" / "src" / "components" / "documentation" / "documentation-data.ts"
DEFAULT_OUTPUT = REPO_ROOT / "cognitive_app" / "public" / "doc-search-index.json"

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _extract_doc_catalog(ts_source: str) -> list[dict]:
    """
    Extract the DOC_CATALOG array from TypeScript source using a simple
    regex-based parser.  Sufficient for the fixed, machine-generated format.

    Note: The comment-stripping step uses a heuristic that avoids clobbering
    URL-like `//` sequences inside string literals by only removing `//` that
    are preceded by whitespace or appear at the start of a line.
    """
    # Strip single-line comments only when // is not inside a string literal
    # (heuristic: match // preceded by optional whitespace after `,`, `{`, or
    # a newline — not `/http` or `://` URL patterns).
    ts_source = re.sub(r"(?<![:/])(?:^|(?<=\s))//[^\n]*", "", ts_source)

    # Find the array literal
    m = re.search(r"export const DOC_CATALOG[^=]*=\s*(\[[\s\S]*?\]);", ts_source)
    if not m:
        raise ValueError("Could not locate DOC_CATALOG in documentation-data.ts")

    array_str = m.group(1)

    # Extract object literals
    entries = []
    obj_re = re.compile(r"\{([^{}]*)\}", re.DOTALL)
    for obj_m in obj_re.finditer(array_str):
        body = obj_m.group(1)
        entry: dict = {}
        for field in ("id", "title", "path", "category", "description"):
            field_m = re.search(rf'\b{field}\s*:\s*[\'"]([^\'"]*)[\'"]', body)
            if field_m:
                entry[field] = field_m.group(1)
        # tags array
        tags_m = re.search(r"\btags\s*:\s*\[([^\]]*)\]", body)
        if tags_m:
            entry["tags"] = re.findall(r'[\'"]([^\'"]*)[\'"]', tags_m.group(1))
        else:
            entry["tags"] = []
        if entry.get("id"):
            entries.append(entry)
    return entries


def _tokenize(text: str) -> list[str]:
    return [
        t for t in re.split(r"[^a-z0-9]+", text.lower())
        if len(t) > 1
    ]


def _build_index(catalog: list[dict]) -> dict:
    """
    Return a dict with:
      - catalog: raw entry list
      - inverted_index: { term → [entry_id, ...] }
    """
    FIELD_WEIGHTS = {
        "title": 10,
        "tags": 6,
        "category": 4,
        "description": 2,
        "path": 1,
    }
    inverted: dict[str, list[str]] = {}

    for entry in catalog:
        fields = {
            "title": entry.get("title", ""),
            "category": entry.get("category", ""),
            "tags": " ".join(entry.get("tags", [])),
            "description": entry.get("description", ""),
            "path": entry.get("path", ""),
        }
        seen_terms: dict[str, int] = {}
        for field, text in fields.items():
            weight = FIELD_WEIGHTS.get(field, 1)
            for term in _tokenize(text):
                seen_terms[term] = seen_terms.get(term, 0) + weight

        for term in seen_terms:
            inverted.setdefault(term, [])
            if entry["id"] not in inverted[term]:
                inverted[term].append(entry["id"])

    return {
        "version": 1,
        "catalog": catalog,
        "inverted_index": inverted,
        "entry_count": len(catalog),
        "term_count": len(inverted),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                   help="Output JSON path (default: %(default)s)")
    p.add_argument("--dry-run", action="store_true",
                   help="Parse and build index but do not write to disk")
    p.add_argument("--source", type=Path, default=DOC_DATA_TS,
                   help="documentation-data.ts source path")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if not args.source.exists():
        print(f"ERROR: source file not found: {args.source}", file=sys.stderr)
        return 1

    try:
        ts_source = args.source.read_text(encoding="utf-8")
        catalog = _extract_doc_catalog(ts_source)
    except Exception as exc:
        print(f"ERROR parsing documentation-data.ts: {exc}", file=sys.stderr)
        return 1

    if not catalog:
        print("WARNING: DOC_CATALOG is empty — index not written.", file=sys.stderr)
        return 0

    index = _build_index(catalog)

    if args.dry_run:
        print(f"DRY-RUN: would write {len(catalog)} entries, {index['term_count']} terms → {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Wrote {len(catalog)} entries, {index['term_count']} terms → {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
