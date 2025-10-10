@codex implement plan
title: "Run 0D_base_ audit and commit artifacts"
on_conflict: "prefer-upstream"
steps:
  - sh: |
      # Offline-first environment
      export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
      # Optional (non-fatal) tools for spec tests
      pip -q install pyyaml jinja2 jsonschema z3-solver || true
  - sh: |
      # Full audit pipeline (S1–S7)
      python scripts/space_traversal/audit_runner.py run
  - sh: |
      # Quick validation subset (offline)
      pytest -q tests/specs/test_cli_normalization.py || true
      pytest -q tests/specs/test_regex_props.py || true
  - sh: |
      # Stage outputs snapshot
      ls -l audit_artifacts || true
      test -f audit_run_manifest.json && jq '.repo_root_sha, .template_hash' audit_run_manifest.json || true
  - commit: |
      chore(audit): add audit artifacts & manifest (0D_base_)
    add: |
      audit_artifacts/context_index.json
      audit_artifacts/facets.json
      audit_artifacts/capabilities_raw.json
      audit_artifacts/capabilities_scored.json
      audit_artifacts/gaps.json
      audit_run_manifest.json
    message: |
      chore(audit): add audit artifacts & manifest (0D_base_)
      - Deterministic outputs (S1–S7)
      - Include manifest chain (repo_root_sha, per-artifact SHA, template_hash)
