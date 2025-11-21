# PR: chore(audit): consolidate audit pipeline — canonical runner, package layout, remove duplicates

## Summary
This PR reorganizes and consolidates the deterministic audit pipeline to a single authoritative package location, removes duplicate/conflicting files, and adds safety/packaging scaffolding so CI and local runs are deterministic and importable.

Key changes:
- Move capability_scoring.py → scripts/space_traversal/capability_scoring.py (canonical import path).
- Ensure canonical orchestrator: scripts/space_traversal/audit_runner.py (remove root-level audit_runner.py).
- Consolidate workflow config to .copilot-space/workflow.yaml (remove root workflow.yaml).
- Add package markers:
  - scripts/space_traversal/__init__.py
  - scripts/space_traversal/detectors/__init__.py
- Add detectors README: scripts/space_traversal/detectors/README.md
- Ensure schema & tests are present: scripts/space_traversal/schemas/capability_matrix.schema.json, tests/audit/*
- Update Makefile target alignment and cleanup target.

## Testing / Verification
1. pip install -r requirements-dev.txt
2. pytest -q tests/audit
3. python scripts/space_traversal/audit_runner.py run
4. Validate JSON companion with schema (optional)

## Notes
- Review detectors for import-time side effects.
- Run script .github/prune-and-consolidate.sh in dry-run mode first.

*End of PR*
