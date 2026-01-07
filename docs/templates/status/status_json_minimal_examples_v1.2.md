# Reference: Minimal JSON Examples for Status v1.2
> Generated: 2024-11-02 15:29:01 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Schema Example Curator], [Secondary: Reviewer] ⚡ Energy: 5

Purpose
- Provide minimal but valid JSON snippets for common authoring scenarios.

Minimal Skeleton (valid against v1.2)
```json
{
  "metadata": {
    "title": "📍 `_codex_` : Status Update Previous Cycle-11-02-15:29:UTC",
    "timestamp_utc": "2024-11-02T15:29:01Z",
    "report_version": "v1.0",
    "template_version": "v1.2",
    "authors": ["mbaetiong"],
    "reviewers": [],
    "previous_report_path": "",
    "git_context": {
      "branch": "0D_base_",
      "commit_sha": "0000000000000000000000000000000000000000",
      "commit_sha_short": "00000000",
      "is_dirty": false,
      "tags": []
    },
    "environment": {
      "python_version": "3.10.0",
      "pytorch_version": "",
      "cuda_version": "",
      "os": "linux-5.15",
      "hostname": "local"
    }
  },
  "snapshot": {
    "repo_map": "",
    "capabilities": [],
    "capability_discovery_log": [],
    "findings": [],
    "tests_gates": {
      "tests_summary": {"total":0,"passed":0,"failed":0,"skipped":0,"duration_seconds":0},
      "coverage_percent": 0,
      "coverage_threshold": 0,
      "coverage_by_module": {},
      "quality_gates": {"lint":"skip","typecheck":"skip","security_sast":"skip","security_secrets":"skip","security_deps":"skip","format":"skip","docs":"skip"},
      "nox_sessions": {"lint":"skip","tests":"skip","gates":"skip","typecheck":"skip","precommit":"skip"},
      "reproducibility": "",
      "missing_tests": []
    },
    "repro": {
      "core_controls": [],
      "registry": [],
      "determinism_tests": {"seed_control":"skip","data_splits":"skip","training_loop":"skip","checkpointing":"skip"}
    },
    "deferred": []
  },
  "delta": {},
  "patches": [],
  "automation": {},
  "security": {"masking_applied": true, "redactions_count": 0, "threat_model_version": "", "notes": ""},
  "questions": [],
  "decisions": [],
  "tokenization": {},
  "ml_test_score": {},
  "hydra_config_snapshot": {}
}
```text

Minimal Finding (add to snapshot.findings)
```json
{
  "id": "FIND-001",
  "title": "Schema mismatch in training profile",
  "evidence": "epochs=0 violates minimum 1",
  "impact": "Blocks CI",
  "proposed_action": "Set trainer.epochs>=1",
  "severity": 4,
  "confidence": 4,
  "category": "maintainability",
  "status": "acknowledged",
  "links": { "capability_ids": ["CAP-002"], "patch_ids": ["PATCH-010"], "issues": [], "prs": [] }
}
```text

Minimal Capability (add to snapshot.capabilities)
```json
{
  "id": "CAP-002",
  "name": "Training Engine",
  "category": "Training",
  "status": "Stubbed",
  "artifacts": "src/codex_ml/training/",
  "gaps": "No trainer loop",
  "risks": "No e2e validation",
  "severity": 4,
  "confidence": 3,
  "tags": ["gpu"],
  "patch_plan": "Introduce toy trainer",
  "rollback": "Revert new files",
  "owner": "mbaetiong"
}
```text
