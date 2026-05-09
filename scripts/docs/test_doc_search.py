#!/usr/bin/env python3
"""
test_doc_search.py — Integration/smoke tests for the documentation search index.

Verifies that:
  1. build_doc_search_index.py can parse documentation-data.ts and build a valid index
  2. The inverted index contains expected terms
  3. Lookup for known catalog entries works correctly

Intended to be run in CI as part of the pre-flight validation gate.

Usage:
    python scripts/docs/test_doc_search.py
    python scripts/docs/test_doc_search.py --verbose

Exit codes:
    0 — all tests pass
    1 — one or more tests fail
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

PASS = "✅ PASS"
FAIL = "❌ FAIL"


class SimpleTestCase:
    """Minimal test case runner (no third-party deps)."""

    def __init__(self, name: str):
        self.name = name
        self._failures: list[str] = []
        self.verbose = False

    def assertEqual(self, a, b, msg: str = "") -> None:
        if a != b:
            self._failures.append(msg or f"expected {b!r}, got {a!r}")

    def assertTrue(self, cond, msg: str = "") -> None:
        if not cond:
            self._failures.append(msg or "expected True, got False")

    def assertIn(self, item, container, msg: str = "") -> None:
        if item not in container:
            self._failures.append(msg or f"{item!r} not in {container!r}")

    def assertGreater(self, a, b, msg: str = "") -> None:
        if not (a > b):
            self._failures.append(msg or f"expected {a!r} > {b!r}")

    def run(self) -> bool:
        return len(self._failures) == 0

    def report(self) -> str:
        if self._failures:
            detail = "; ".join(self._failures[:3])
            return f"{FAIL}  {self.name}: {detail}"
        return f"{PASS}  {self.name}"


# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------

SCRIPTS_DOCS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DOCS_DIR))
try:
    from build_doc_search_index import (
        DOC_DATA_TS,
        _build_index,
        _extract_doc_catalog,
        _tokenize,
    )
except ImportError as exc:
    print(f"FATAL: cannot import build_doc_search_index: {exc}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Test definitions
# ---------------------------------------------------------------------------

def test_tokenize() -> SimpleTestCase:
    t = SimpleTestCase("tokenize basic")
    tokens = _tokenize("Hello, World! 123 foo-bar")
    t.assertIn("hello", tokens)
    t.assertIn("world", tokens)
    t.assertIn("123", tokens)
    t.assertIn("foo", tokens)
    t.assertIn("bar", tokens)
    return t


def test_source_file_exists() -> SimpleTestCase:
    t = SimpleTestCase("documentation-data.ts exists")
    t.assertTrue(DOC_DATA_TS.exists(), f"{DOC_DATA_TS} not found")
    return t


def test_catalog_parse() -> SimpleTestCase:
    t = SimpleTestCase("DOC_CATALOG parse")
    try:
        source = DOC_DATA_TS.read_text(encoding="utf-8")
        catalog = _extract_doc_catalog(source)
        t.assertGreater(len(catalog), 0, "catalog should be non-empty")
        for entry in catalog:
            t.assertIn("id", entry, f"entry missing 'id': {entry}")
            t.assertIn("title", entry, f"entry missing 'title': {entry}")
            t.assertIn("path", entry, f"entry missing 'path': {entry}")
            t.assertIn("category", entry, f"entry missing 'category': {entry}")
    except Exception:
        t._failures.append(traceback.format_exc())
    return t


def test_unique_ids() -> SimpleTestCase:
    t = SimpleTestCase("DOC_CATALOG unique IDs")
    try:
        source = DOC_DATA_TS.read_text(encoding="utf-8")
        catalog = _extract_doc_catalog(source)
        ids = [e["id"] for e in catalog]
        t.assertEqual(len(set(ids)), len(ids), "IDs are not unique")
    except Exception:
        t._failures.append(traceback.format_exc())
    return t


def test_index_build() -> SimpleTestCase:
    t = SimpleTestCase("inverted index build")
    try:
        source = DOC_DATA_TS.read_text(encoding="utf-8")
        catalog = _extract_doc_catalog(source)
        index = _build_index(catalog)

        t.assertIn("version", index)
        t.assertIn("catalog", index)
        t.assertIn("inverted_index", index)
        t.assertIn("entry_count", index)
        t.assertIn("term_count", index)
        t.assertEqual(index["entry_count"], len(catalog))
        t.assertGreater(index["term_count"], 0, "inverted index should have terms")
    except Exception:
        t._failures.append(traceback.format_exc())
    return t


def test_known_term_lookup() -> SimpleTestCase:
    t = SimpleTestCase("known term 'agents' in index")
    try:
        source = DOC_DATA_TS.read_text(encoding="utf-8")
        catalog = _extract_doc_catalog(source)
        index = _build_index(catalog)
        inv = index["inverted_index"]
        t.assertIn("agents", inv, "'agents' should appear in the index")
        t.assertGreater(len(inv["agents"]), 0)
    except Exception:
        t._failures.append(traceback.format_exc())
    return t


def test_readme_entry_indexed() -> SimpleTestCase:
    t = SimpleTestCase("'readme' entry indexed")
    try:
        source = DOC_DATA_TS.read_text(encoding="utf-8")
        catalog = _extract_doc_catalog(source)
        index = _build_index(catalog)
        inv = index["inverted_index"]
        # 'readme' or 'read' should appear
        found = any("readme" in k or "read" in k for k in inv)
        t.assertTrue(found, "no readme-related term in inverted index")
    except Exception:
        t._failures.append(traceback.format_exc())
    return t


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    test_fns = [
        test_tokenize,
        test_source_file_exists,
        test_catalog_parse,
        test_unique_ids,
        test_index_build,
        test_known_term_lookup,
        test_readme_entry_indexed,
    ]

    results = []
    for fn in test_fns:
        case = fn()
        case.verbose = args.verbose
        case.run()
        results.append(case)

    passed = sum(1 for r in results if not r._failures)
    failed = len(results) - passed

    for r in results:
        print(r.report())

    print(f"\n{'=' * 48}")
    print(f"Tests: {len(results)}  Passed: {passed}  Failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
