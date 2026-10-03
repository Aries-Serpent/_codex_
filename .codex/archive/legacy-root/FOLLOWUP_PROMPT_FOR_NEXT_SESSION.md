@copilot Continue Phase 2 implementation: Integrate AI/ML interpretability features and activate pytest workflow.

## Context

All code review feedback from PR#2624 has been successfully addressed with comprehensive fixes and validation. Pytest workflow template created and ready for activation.

## Completed Work

### Phase 1: Code Review Fixes (✅ Complete)
- Commit 036caff: All 7 review comments addressed
- Removed workflow file violation
- Fixed validation logic (boolean comparison, UUID check, security)
- Removed duplicate lessons (4 unique remain)
- Added security warnings to documentation

### Phase 2: Pytest Template (✅ Complete)
- Commit 65b7162: Created complete pytest workflow template
- Location: `.codex/templates/tests-workflow-TEMPLATE.yml`
- Guide: `.codex/templates/PYTEST_WORKFLOW_GUIDE.md`
- Features: Linux only, Python 3.11/3.12, coverage, PR integration
- Compliance: Template requires human approval per guidelines

## Immediate Tasks

### 1. Activate Pytest Workflow (Human Admin Action Required)

**You must coordinate with human admin** to activate the workflow:

```bash
# Human admin must execute:
cp .codex/templates/tests-workflow-TEMPLATE.yml .github/workflows/tests.yml
git add .github/workflows/tests.yml
git commit -m "feat: activate pytest workflow for CI/CD"
git push
```

**Rationale**: Per `.github/copilot-instructions.md`, AI agents cannot create or activate workflow files. Template is ready for human review and activation.

### 2. Create AI/ML Interpretability Utilities

**Requirements** (from user comment #3693692760):
- Interpretability utilities for model analysis
- Attention scoring mechanisms
- MLP (Multi-Layer Perceptron) scoring

**Implementation Plan**:

#### A. Create Module Structure
```
agents/
├── interpretability/
│   ├── __init__.py
│   ├── attention_scorer.py
│   ├── mlp_scorer.py
│   └── utils.py
```

#### B. Attention Scoring Implementation
- Multi-head attention weight extraction
- Attention visualization generation
- Score normalization and aggregation
- Support for transformer-based models

**Example API**:
```python
from agents.interpretability import AttentionScorer

scorer = AttentionScorer(model, layer_idx=6)
attention_weights = scorer.extract_attention(input_ids)
attention_scores = scorer.score(attention_weights)
visualization = scorer.visualize(attention_scores, tokens)
```

#### C. MLP Scoring Implementation
- Layer-wise activation analysis
- Feature importance calculation
- Gradient-based attribution
- Neuron activation patterns

**Example API**:
```python
from agents.interpretability import MLPScorer

scorer = MLPScorer(model)
layer_scores = scorer.score_layers(input_data)
feature_importance = scorer.get_feature_importance()
activations = scorer.analyze_neurons(layer_idx=3)
```

#### D. Integration Tests
Create tests in `tests/interpretability/`:
- `test_attention_scoring.py`
- `test_mlp_scoring.py`
- `test_interpretability_utils.py`

### 3. Update Dependencies

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
interpretability = [
    "captum>=0.6.0",  # PyTorch interpretability
    "shap>=0.42.0",   # SHAP values
    "transformers>=4.35.0",  # For attention mechanisms
]
```

### 4. Documentation

Create `.codex/docs/INTERPRETABILITY_GUIDE.md`:
- Architecture overview
- Usage examples
- API reference
- Integration with existing codebase

### 5. Testing Strategy

After implementation:
1. Run local tests: `pytest tests/interpretability/ -v`
2. Validate attention scoring with sample models
3. Verify MLP scoring accuracy
4. Check integration with existing agents

## Success Criteria

✅ Pytest workflow activated (human admin action)
✅ Interpretability module created with full API
✅ Attention scoring functional and tested
✅ MLP scoring functional and tested
✅ Integration tests passing
✅ Documentation complete
✅ Dependencies updated

## Constraints & Guidelines

**Must Follow**:
- Repository guidelines from `.github/copilot-instructions.md`
- Do NOT create or activate workflow files (template only)
- Keep artifacts in `.codex/` directory
- Document all decisions
- Test all implementations

**Dependencies**:
- Python 3.11+ support
- Compatible with existing agents/
- No breaking changes to existing APIs

## Next Steps After Completion

If unable to complete within this session:
1. Commit all work in progress
2. Document completion status
3. Create follow-up prompt with remaining tasks
4. Use `@copilot` format for next session trigger

## Reference Documents

- Original request: PR#2624 comment #3693692760
- Pytest template: `.codex/templates/tests-workflow-TEMPLATE.yml`
- Guidelines: `.github/copilot-instructions.md`
- Genesis validation: `scripts/validate_genesis_readiness.py`

## Priority Order

1. **HIGH**: Coordinate workflow activation with human admin
2. **HIGH**: Create interpretability module structure
3. **MEDIUM**: Implement attention scoring
4. **MEDIUM**: Implement MLP scoring
5. **MEDIUM**: Create integration tests
6. **LOW**: Documentation and examples

Begin with workflow activation coordination, then proceed with interpretability implementation.
