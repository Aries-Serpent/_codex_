# Duplicate Detection Inventory - Implementation Prompts

This directory contains the complete phased implementation plan for building a comprehensive duplicate detection system for the _codex_ repository.

## 📋 Overview

The duplicate detection system identifies duplicate files and functionality across the entire codebase using multiple detection methods:

1. **Exact File Duplicate Detection** - SHA256 hash matching
2. **Normalized Duplicate Detection** - Comment/whitespace-agnostic matching  
3. **AST-Based Detection** - Function/class structure matching
4. **Semantic Similarity Detection** - Fuzzy/embedding-based matching

## 🗂️ Prompt Files

| File | Phase | Status | Description |
|------|-------|--------|-------------|
| `00_MASTER_PLAN.md` | Master | ✅ Complete | Overall implementation plan and coordination |
| `01_foundation_infrastructure.md` | Phase 1 | 📝 Ready | Base scanner, exact detection, schema, CLI |
| `02_normalized_detection.md` | Phase 2 | ⏳ Pending | Normalized detection, comment stripping |
| `03_ast_detection.md` | Phase 3 | ⏳ Pending | AST parsing, function-level detection |
| `04_semantic_similarity.md` | Phase 4 | ⏳ Pending | MinHash, clustering, semantic matching |
| `05_git_integration.md` | Phase 5 | ⏳ Pending | Git blame, churn metrics |
| `06_inventory_output.md` | Phase 6 | ⏳ Pending | Complete schema, output formats, reports |
| `07_shim_integration.md` | Phase 7 | ⏳ Pending | SHIM_INVENTORY cross-reference |
| `08_cli_workflow.md` | Phase 8 | ⏳ Pending | CLI, config files, GitHub Actions |
| `09_documentation.md` | Phase 9 | ⏳ Pending | README, guides, examples |
| `10_testing_validation.md` | Phase 10 | ⏳ Pending | Testing, validation, benchmarks |

## 🎯 Execution Strategy

### Iterative Self-Healing Process

Each phase follows this workflow:

1. **Implement** - Code the features from the prompt
2. **Test** - Run all test cases
3. **Review** - Use code_review tool
4. **Scan** - Run codeql_checker for security
5. **Refine** - Address any issues found
6. **Validate** - Verify acceptance criteria met
7. **Document** - Update documentation
8. **Commit** - Use report_progress to commit

**Do not proceed to next phase until current phase fully complete and validated.**

### Phase Dependencies

```
Phase 1 (Foundation)
    ↓
Phase 2 (Normalized)
    ↓
Phase 3 (AST)
    ↓
Phase 4 (Semantic)
    ↓
Phase 5 (Git Integration)
    ↓
Phase 6 (Inventory Output)
    ↓
Phase 7 (SHIM Integration)
    ↓
Phase 8 (CLI & Workflow)
    ↓
Phase 9 (Documentation)
    ↓
Phase 10 (Testing & Validation)
```

## 🚀 Getting Started

### For Automated Agents

To execute this plan:

```bash
# Start with Phase 1
cat .github/prompts/duplicate_detection_inventory/01_foundation_infrastructure.md

# Follow the tasks in order
# Run tests after each task
# Commit progress incrementally
# Move to Phase 2 only after Phase 1 complete
```

### For Human Developers

1. Review `00_MASTER_PLAN.md` for overall strategy
2. Read the specific phase prompt you're working on
3. Follow the tasks sequentially
4. Run the self-healing checklist after implementation
5. Validate acceptance criteria before moving on

## 📊 Progress Tracking

Track progress in `00_MASTER_PLAN.md` under "Current Status" section.

## 🎓 Design Principles

1. **Modularity** - Each detector is independent
2. **Extensibility** - Easy to add new detection methods
3. **Performance** - Cache results, optimize for large repos
4. **Reliability** - Comprehensive testing, graceful error handling
5. **Usability** - Clear CLI, good documentation, actionable reports

## 📦 Expected Outputs

After completion:

```
scripts/analysis/
├── duplicate_scanner.py
├── exact_detector.py
├── normalized_detector.py
├── ast_detector.py
├── semantic_detector.py
├── git_metrics.py
├── inventory_writer.py
├── shim_integration.py
└── cli.py

tests/analysis/
├── test_duplicate_scanner.py
├── test_exact_detection.py
└── ... (comprehensive test suite)

Output files:
├── SUPPLEMENTAL_DUPLICATE_INVENTORY.yaml
├── supplemental_duplicates.json
├── supplemental_duplicates.csv
├── supplemental_duplicates.md
└── intentional_duplicates.yml
```

## 🔗 Integration Points

- **SHIM_INVENTORY.yaml** - Cross-reference with existing inventory
- **Nightly Audit Workflow** - Add duplicate detection step
- **GitHub Actions** - Automated weekly scans
- **verify_conflicts.py** - Complementary to existing tool

## 📝 Notes

- This feature is being added to the `copilot/fix-strict-conflicts-detected` branch
- Original PR fix (whitelist parsing) remains intact and functional
- New feature adds complementary capabilities
- Maintains clean separation of concerns

## ⚠️ Important

**DO NOT SKIP PHASES** - Each phase builds on the previous one. Complete validation before proceeding.

## 🎯 Success Criteria

- [ ] All 10 phases completed
- [ ] All tests passing (>80% coverage)
- [ ] Documentation complete
- [ ] Security scan clean (0 alerts)
- [ ] Performance acceptable (<5 min medium repo)
- [ ] Integration with SHIM_INVENTORY working
- [ ] GitHub Actions workflow functional
- [ ] Production-ready

## 📧 Support

For questions or issues during implementation:
- Review the specific phase prompt
- Check the master plan
- Consult existing codebase patterns
- Follow repository conventions

---

**Last Updated**: 2024-12-08
**Version**: 1.0.0
**Status**: Planning Complete, Ready for Phase 1 Implementation
