"""
Package marker for 'scripts.space_traversal'.

Exports:
- dup_similarity (optional): token-similarity scaffold used by audit runner when
  scoring.dup.heuristic == "token_similarity".

Rationale:
- Stabilizes absolute imports during 'python scripts/space_traversal/audit_runner.py'
  execution where sys.path may not include the repo root on some environments.

Version: 1.1.0
"""

__all__ = []
