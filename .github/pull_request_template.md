## Pull Request Summary

### Description
<!-- Provide a clear and concise description of the changes -->



### Type of Change
<!-- Check all that apply -->
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] 🔧 Configuration change
- [ ] 🎨 Code style/refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🔒 Security fix
- [ ] 🚀 Deployment/promotion (see checklist below)

### Related Issues
<!-- Link related issues using keywords: Fixes #123, Closes #456, Relates to #789 -->



### Testing
<!-- Describe the tests you ran and how to reproduce them -->
- [ ] Tests pass locally (`pytest`)
- [ ] Linting passes (`ruff check`, `black --check`)
- [ ] Type checking passes (`mypy`)
- [ ] Pre-commit hooks pass

### Documentation
- [ ] Documentation has been updated (if needed)
- [ ] CHANGELOG.md has been updated (if applicable)
- [ ] Architecture docs updated (if applicable)

### Checklist
- [ ] My code follows the repository's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

### Screenshots (if applicable)
<!-- Add screenshots to help explain your changes -->



---

## Promotion / Readiness Checklist

**Note:** Fill this section out only for PRs that:
- Promote work from a rollout ring (for example `0D_base_`) toward `main`, OR
- Introduce / update reasoning-serving infra (deployment presets, pod YAMLs, etc.).

If this PR is only docs, bug fixes, or features, the section below does not apply.

---

### 1. Rollout ring and branch context
- Target rollout_ring from training artifacts (run_metadata.json):  
  `rollout_ring = ____________________`

- Source branch / ring being promoted (e.g. `0D_base_`):  
  `branch = ____________________`

- Target branch (e.g. `main`):  
  `target = ____________________`

### 2. Survey snapshot
- Path to the committed survey snapshot under docs/status_updates/:  
  `docs/status_updates/____________________.md`

Confirm this file:
- Describes orchestrators (TrainLoop / UnifiedTraining), reasoning harness trace capture, curricula config, evaluation preset, deployment preset.
- Captures any known code/docs mismatches.

### 3. Status report
Attach the output of:

```bash
python -m codex_ml.cli.codex_cli status-report \
  --run-metadata-dir runs/train_loop
```

Paste JSON here (trim secrets if any):

```text
<status-report JSON here>
```

This MUST include:
- `rollout_ring`
- `knobs.trace_mode`
- `knobs.curriculum_preset`
- `knobs.evaluation_preset`
- `knobs.deployment_preset`

### 4. Dry-run deploy proof
Provide the output (or summary) of:

```bash
python -m codex_ml.cli.codex_cli deploy \
  --config configs/deploy/reasoning_pod.yaml \
  --dry-run \
  --run-metadata-dir runs/train_loop
```

`codex_ml.cli.codex_cli deploy` MUST report success with `--dry-run`. If it printed `DEPLOYMENT BLOCKED`, stop and explain why.

Paste result / summary here:

```text
<deploy dry-run result>
```

### 5. Evaluation preset sign-off
Check ONE:

- [ ] Offline evaluation preset passed and is reflected in `evaluation.json`.
- [ ] This PR does not modify model behavior; safe to merge without new evaluation.
      Rationale:
      ____________________________________________

### 6. Ack: This PR follows docs/ops/promotion_checklist.md
- [ ] I confirm I walked through `docs/ops/promotion_checklist.md` and this PR satisfies the required gates.

---

Reviewer notes / escalation contact:
- Owner / escalation contact from run_metadata.json: ____________________
- Additional context:
  ______________________________________________________

---

## Status v1.2 Compliance (if applicable)

**Note:** Fill this section if your PR includes status reports, schemas, or validation tooling changes.

### Validation Checklist
- [ ] Status example JSON validates against v1.2 schema (run `pytest -q tests/status/test_example_report_schema.py`)
- [ ] Hydra configs validated or explicitly N/A (run `python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml`)
- [ ] Security gates executed; artifacts uploaded
- [ ] CAP-/FIND-/PATCH-/REPRO- IDs consistent and cross-linked
- [ ] No secrets or sensitive data in diffs/logs

### Validation Commands Run
```bash
# Schema validation
pytest -q tests/status/test_example_report_schema.py

# Config validation  
python tools/validate_configs.py --root configs/training --schema configs/schemas/training.schema.yaml

# Audit chain
python scripts/audit/build_integrity_chain.py
```
