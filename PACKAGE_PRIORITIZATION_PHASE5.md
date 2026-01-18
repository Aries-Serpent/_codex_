# DOCUMENTATION COVERAGE BY PACKAGE - PRIORITIZATION GUIDE

## Phase 5 Package-Level Priorities

### HIGH PRIORITY (Weeks 1-4)

#### 1. codex_ml/ - **CRITICAL**
- **Undocumented Items:** 1,940
- **Files:** 439
- **Coverage:** 51.5%
- **Priority:** P0
- **Rationale:** Largest package, core ML functionality
- **Effort:** ~161 hours (48% of total)
- **Key Areas:**
  - `data/` - Data loading and preprocessing
  - `modeling/` - Model architectures
  - `training/` - Training loops
  - `checkpointing/` - Model persistence
  - `reward_models/` - RL reward models

#### 2. codex/ - **HIGH**
- **Undocumented Items:** 551
- **Files:** 257
- **Coverage:** 75.5%
- **Priority:** P0
- **Rationale:** Core application package, user-facing
- **Effort:** ~46 hours (14% of total)
- **Key Areas:**
  - `zendesk/` - CRM integrations
  - `evidence/` - Evidence tracking
  - `plans/` - Planning system
  - `rag/` - RAG pipeline

#### 3. training/ - **HIGH**
- **Undocumented Items:** 130
- **Files:** 17
- **Coverage:** 36.0%
- **Priority:** P0
- **Rationale:** Critical for ML operations, poor coverage
- **Effort:** ~11 hours (3% of total)

#### 4. mcp/ - **MEDIUM-HIGH**
- **Undocumented Items:** 123
- **Files:** 60
- **Coverage:** 62.6%
- **Priority:** P1
- **Rationale:** MCP protocol implementation
- **Effort:** ~10 hours (3% of total)

### MEDIUM PRIORITY (Weeks 5-6)

#### 5. hhg_logistics/ - **MEDIUM**
- **Undocumented Items:** 57
- **Files:** 26
- **Coverage:** 29.6%
- **Priority:** P1
- **Rationale:** Low coverage, specific domain
- **Effort:** ~5 hours

#### 6. common/ - **MEDIUM**
- **Undocumented Items:** 48
- **Files:** 9
- **Coverage:** 21.3%
- **Priority:** P1
- **Rationale:** Shared utilities, low coverage
- **Effort:** ~4 hours

#### 7. tokenization/ - **MEDIUM**
- **Undocumented Items:** 31
- **Files:** 7
- **Coverage:** 34.0%
- **Priority:** P1
- **Rationale:** Text processing core
- **Effort:** ~3 hours

#### 8. codex_audit/ - **CRITICAL (Zero Coverage)**
- **Undocumented Items:** 31
- **Files:** 6
- **Coverage:** 0.0%
- **Priority:** P0
- **Rationale:** Zero documentation is unacceptable
- **Effort:** ~3 hours

#### 9. codex_harness/ - **HIGH**
- **Undocumented Items:** 30
- **Files:** 4
- **Coverage:** 6.2%
- **Priority:** P0
- **Rationale:** Nearly zero coverage
- **Effort:** ~3 hours

#### 10. codex_cli/ - **HIGH**
- **Undocumented Items:** 24
- **Files:** 2
- **Coverage:** 7.7%
- **Priority:** P0
- **Rationale:** User-facing CLI, poor coverage
- **Effort:** ~2 hours

### LOW PRIORITY (Weeks 7-8 or Phase 6)

#### Well-Documented Packages (>90% coverage):
- **cognitive_brain/** - 97.7% ✅
- **context_management/** - 99.6% ✅
- **zendesk/** - 93.6% ✅
- **ingestion/** - 88.2% ✅
- **agent/** - 89.3% ✅
- **security/** - 84.0% ✅

These packages serve as **examples of good documentation** and can be used as templates.

---

## FOCUSED STRATEGY: 80/20 RULE

### Top 5 Packages Account for 80% of Work

| Package | Undocumented | % of Total | Cumulative |
|---------|--------------|------------|------------|
| codex_ml | 1,940 | 58.7% | 58.7% |
| codex | 551 | 16.7% | 75.4% |
| training | 130 | 3.9% | 79.3% |
| mcp | 123 | 3.7% | 83.0% |
| hhg_logistics | 57 | 1.7% | 84.7% |

**Recommendation:** Focus 80% of Phase 5 effort on these 5 packages.

---

## WEEKLY BREAKDOWN

### Week 1-2: Foundation & Quick Wins
- **codex_audit/** (3 hrs) - Zero to 90%
- **codex_harness/** (3 hrs) - 6% to 90%
- **codex_cli/** (2 hrs) - 8% to 95%
- **Training package core** (11 hrs) - 36% to 80%
- **Start codex_ml/data/** (20 hrs)

**Total: 39 hours**  
**Impact: 3 packages to >90%, training to 80%**

### Week 3-4: codex_ml Deep Dive
- **codex_ml/modeling/** (40 hrs)
- **codex_ml/training/** (30 hrs)
- **codex_ml/data/** (continued, 30 hrs)

**Total: 100 hours**  
**Impact: Core ML components documented**

### Week 5-6: codex Package & MCP
- **codex/rag/** (15 hrs)
- **codex/zendesk/** (10 hrs)
- **codex/plans/** (10 hrs)
- **mcp/** (10 hrs)
- **Tutorial creation** (21 hrs)

**Total: 66 hours**  
**Impact: Main packages to 90%+, tutorials complete**

### Week 7-8: Polish & Remaining
- **codex_ml/remaining** (30 hrs)
- **tokenization/** (3 hrs)
- **common/** (4 hrs)
- **hhg_logistics/** (5 hrs)
- **Link fixes & API reference** (25 hrs)

**Total: 67 hours**  
**Impact: All P0/P1 complete, docs polished**

---

## PACKAGE-SPECIFIC DOCUMENTATION TEMPLATES

### For ML Packages (codex_ml, training)

```python
"""Machine learning model training utilities.

This module provides training loops, optimization strategies,
and checkpoint management for neural network models.

Key Components:
    - Trainer: Main training orchestration
    - Optimizer: Learning rate scheduling
    - Checkpointer: Model persistence

Example:
    >>> from codex_ml.training import Trainer
    >>> trainer = Trainer(model, config)
    >>> trainer.train(dataset)

See Also:
    - codex_ml.modeling: Model architectures
    - codex_ml.data: Data loading
"""
```

### For API/Service Packages (mcp, codex)

```python
"""MCP protocol server implementation.

Implements the Model Context Protocol for AI model serving,
including request handling, authentication, and rate limiting.

Architecture:
    FastAPI server with async request handling, Redis caching,
    and PostgreSQL for persistence.

Example:
    >>> from mcp.server import create_app
    >>> app = create_app(config)
    >>> app.run(host="0.0.0.0", port=8000)

See Also:
    - docs/MCP_SETUP_GUIDE.md
    - docs/api/mcp_reference.md
"""
```

---

## MEASUREMENT & TRACKING

### Weekly Progress Metrics

```yaml
week_1:
  target_coverage: 88.0
  packages_completed:
    - codex_audit
    - codex_harness
    - codex_cli
  hours_spent: 39

week_2:
  target_coverage: 89.0
  packages_in_progress:
    - codex_ml
    - training
  hours_spent: 40

# ... continue tracking
```

### Package Coverage Goals

| Package | Current | Week 4 | Week 8 | Final Goal |
|---------|---------|--------|--------|------------|
| codex_ml | 51.5% | 65% | 80% | 85% |
| codex | 75.5% | 85% | 92% | 95% |
| training | 36.0% | 80% | 90% | 90% |
| mcp | 62.6% | 75% | 90% | 90% |
| codex_audit | 0.0% | 90% | 95% | 95% |

---

## AUTOMATION SCRIPTS

### Generate Package Report

```bash
#!/bin/bash
# check_package_coverage.sh

PACKAGE=$1

interrogate --fail-under=80 \
            --ignore-init-method \
            --ignore-module \
            --verbose \
            src/${PACKAGE}/

echo "Package: ${PACKAGE}"
echo "Coverage threshold: 80%"
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml addition
- repo: local
  hooks:
    - id: docstring-coverage
      name: Check docstring coverage
      entry: interrogate
      args: ['--fail-under=75', 'src/']
      language: python
      pass_filenames: false
```

---

## SUCCESS CRITERIA BY PACKAGE

### Tier 1 (Must Achieve - P0)
- codex_ml: 80%+ coverage
- codex: 90%+ coverage
- training: 85%+ coverage
- codex_audit: 90%+ coverage (from 0%)
- codex_harness: 90%+ coverage (from 6%)

### Tier 2 (Should Achieve - P1)
- mcp: 85%+ coverage
- hhg_logistics: 70%+ coverage
- common: 75%+ coverage
- tokenization: 75%+ coverage

### Tier 3 (Nice to Have - P2)
- All other packages: 70%+ coverage

---

## RISK MITIGATION

### Package-Specific Risks

**codex_ml (1,940 items):**
- Risk: Too large, may not complete
- Mitigation: Focus on public APIs first (data/, modeling/, training/)
- Fallback: Document top-level only, defer internals

**training (36% coverage):**
- Risk: Complex ML concepts hard to document
- Mitigation: Pair with ML engineer for technical review
- Fallback: Link to external references (PyTorch docs)

**codex_audit (0% coverage):**
- Risk: May be deprecated/unused code
- Mitigation: Verify with maintainers before documenting
- Fallback: Mark for removal if obsolete

---

## CONCLUSION

Phase 5 should follow a **package-centric approach** with clear weekly targets:

1. **Weeks 1-2:** Quick wins (3 packages from <10% to >90%)
2. **Weeks 3-4:** codex_ml core (51% → 65%)
3. **Weeks 5-6:** codex & MCP (75% → 92%, 63% → 85%)
4. **Weeks 7-8:** Remaining packages + polish

**Expected Final Coverage:**
- Overall: 92/100 (from 85.5)
- codex_ml: 80%+ (from 51.5%)
- codex: 92%+ (from 75.5%)
- All P0 packages: 85%+

This focused approach delivers maximum impact within the 8-week timeline.
