# Master Implementation Plan: Comprehensive Duplicate Detection Inventory

**Branch**: `copilot/fix-strict-conflicts-detected`  
**Created**: 2024-12-08  
**Purpose**: Implement comprehensive duplicate detection across entire codebase

---

## 🎯 Objective

Create a supplemental inventory system (`SUPPLEMENTAL_DUPLICATE_INVENTORY.yaml`) that identifies duplicate files and duplicated functionality across the entire repository using multiple detection methods:

1. **Exact file-duplicate detection** (SHA256)
2. **Normalized duplicate detection** (whitespace/comment-agnostic)
3. **AST/structure-based duplicate detection** (function/class level)
4. **Semantic similarity detection** (fuzzy/embedding-based)

---

## 📋 Phased Implementation Plan

### Phase 1: Foundation & Infrastructure
**Prompt**: `01_foundation_infrastructure.md`
- Create base scanner module structure
- Implement SHA256 exact duplicate detection
- Create YAML/JSON/CSV output writers
- Design schema for SUPPLEMENTAL_DUPLICATE_INVENTORY.yaml
- Add basic CLI interface

**Deliverables**:
- `scripts/analysis/duplicate_scanner.py` (main scanner)
- `scripts/analysis/duplicate_detector.py` (detection engines)
- `scripts/analysis/inventory_writer.py` (output formatters)
- Schema documentation

**Tests**:
- `tests/analysis/test_duplicate_scanner.py`
- `tests/analysis/test_exact_duplicate_detection.py`

---

### Phase 2: Normalized Duplicate Detection
**Prompt**: `02_normalized_detection.md`
- Implement comment/whitespace stripping
- Create normalized fingerprint generation
- Add identifier normalization (optional mode)
- Integrate with main scanner

**Deliverables**:
- Normalized detection engine
- Fingerprint cache system
- Configuration for normalization rules

**Tests**:
- `tests/analysis/test_normalized_detection.py`

---

### Phase 3: AST-Based Detection
**Prompt**: `03_ast_detection.md`
- Implement Python AST parser integration
- Add JavaScript/TypeScript parser (esprima)
- Create function/class signature extraction
- Implement structural similarity scoring
- Add language-specific handlers

**Deliverables**:
- AST detection engine for Python
- AST detection engine for JS/TS
- Extensible parser registry

**Tests**:
- `tests/analysis/test_ast_detection.py`
- `tests/analysis/test_python_ast_parser.py`

---

### Phase 4: Semantic Similarity Detection
**Prompt**: `04_semantic_similarity.md`
- Implement MinHash for token-level similarity
- Add code embedding integration (optional)
- Create similarity clustering algorithm
- Implement configurable threshold system

**Deliverables**:
- Semantic similarity engine
- Clustering algorithm
- Similarity scoring matrix

**Tests**:
- `tests/analysis/test_semantic_similarity.py`
- `tests/analysis/test_clustering.py`

---

### Phase 5: Git Integration
**Prompt**: `05_git_integration.md`
- Add git blame analysis
- Implement churn metrics (90-day window)
- Extract top contributors per file/range
- Add commit history tracking

**Deliverables**:
- Git metrics collector
- Blame parser
- Churn analyzer

**Tests**:
- `tests/analysis/test_git_metrics.py`

---

### Phase 6: Inventory Schema & Output
**Prompt**: `06_inventory_output.md`
- Implement complete inventory schema
- Create YAML/JSON/CSV writers
- Add human-readable report generator
- Implement intentional duplicates detection
- Create markdown summary report

**Deliverables**:
- Complete schema validation
- Multiple output formats
- `supplemental_duplicates.md` generator
- `intentional_duplicates.yml` detector

**Tests**:
- `tests/analysis/test_inventory_output.py`
- `tests/analysis/test_report_generator.py`

---

### Phase 7: SHIM_INVENTORY Integration
**Prompt**: `07_shim_integration.md`
- Read and parse `.github/SHIM_INVENTORY.yaml`
- Cross-reference with detected duplicates
- Mark whitelisted vs non-whitelisted
- Add `not_in_shim_inventory` flag

**Deliverables**:
- SHIM inventory reader
- Cross-reference engine
- Whitelist checker

**Tests**:
- `tests/analysis/test_shim_integration.py`

---

### Phase 8: CLI & Workflow Integration
**Prompt**: `08_cli_workflow.md`
- Create comprehensive CLI with all options
- Add configuration file support
- Integrate with nightly audit workflow
- Create GitHub Actions workflow

**Deliverables**:
- Complete CLI interface
- Configuration file schema
- GitHub Actions workflow file
- Documentation

**Tests**:
- `tests/analysis/test_cli.py`
- Integration test suite

---

### Phase 9: Documentation & Examples
**Prompt**: `09_documentation.md`
- Create comprehensive README
- Add usage examples
- Document all configuration options
- Create troubleshooting guide
- Add architecture diagrams

**Deliverables**:
- `scripts/analysis/README.md`
- `docs/duplicate_detection.md`
- Example configurations
- Architecture diagrams

---

### Phase 10: Testing & Validation
**Prompt**: `10_testing_validation.md`
- Run full test suite
- Perform integration testing
- Validate output schema
- Test on real codebase
- Performance benchmarking

**Deliverables**:
- Complete test coverage report
- Performance benchmarks
- Validation results
- Sample inventory outputs

---

## 🔄 Iterative Self-Healing Process

After each phase:
1. **Run automated tests** - Validate implementation
2. **Code review** - Use code_review tool
3. **Security scan** - Run codeql_checker
4. **Documentation check** - Verify docs updated
5. **Self-assessment** - Identify gaps or issues
6. **Refinement** - Address any concerns
7. **Progress report** - Commit and document

Loop until no concerns remain for the phase.

---

## 📊 Success Criteria

- [ ] All 4 detection modes working
- [ ] Complete test coverage (>80%)
- [ ] Schema validation passing
- [ ] Multiple output formats working
- [ ] Git integration functional
- [ ] SHIM inventory integration complete
- [ ] CLI fully documented
- [ ] Performance acceptable (<5 min for full repo scan)
- [ ] Security scan clean (0 alerts)
- [ ] Documentation complete

---

## 🚀 Execution Order

1. Create all phase prompt files (01-10)
2. Execute Phase 1 with iterative refinement
3. Validate Phase 1 completion
4. Execute Phase 2 with iterative refinement
5. Continue through Phase 10
6. Final integration testing
7. Documentation review
8. Production readiness check

---

## 📁 File Structure

```
scripts/analysis/
├── __init__.py
├── duplicate_scanner.py          # Main entry point
├── duplicate_detector.py          # Detection engines
├── exact_detector.py              # SHA256 detection
├── normalized_detector.py         # Normalized detection
├── ast_detector.py                # AST-based detection
├── semantic_detector.py           # Semantic similarity
├── git_metrics.py                 # Git blame/churn
├── inventory_writer.py            # Output formatters
├── shim_integration.py            # SHIM inventory reader
├── cli.py                         # CLI interface
└── README.md                      # Documentation

tests/analysis/
├── __init__.py
├── test_duplicate_scanner.py
├── test_exact_detection.py
├── test_normalized_detection.py
├── test_ast_detection.py
├── test_semantic_similarity.py
├── test_git_metrics.py
├── test_inventory_output.py
├── test_shim_integration.py
└── test_cli.py

.github/workflows/
└── duplicate-detection.yml        # Automated workflow

Output files (generated):
├── SUPPLEMENTAL_DUPLICATE_INVENTORY.yaml
├── supplemental_duplicates.json
├── supplemental_duplicates.csv
├── supplemental_duplicates.md
└── intentional_duplicates.yml
```

---

## 🎯 Current Status

- [x] Master plan created
- [ ] Phase 1 prompt created
- [ ] Phase 1 implemented
- [ ] Phase 2 prompt created
- [ ] Phase 2 implemented
- [ ] Phase 3 prompt created
- [ ] Phase 3 implemented
- [ ] Phase 4 prompt created
- [ ] Phase 4 implemented
- [ ] Phase 5 prompt created
- [ ] Phase 5 implemented
- [ ] Phase 6 prompt created
- [ ] Phase 6 implemented
- [ ] Phase 7 prompt created
- [ ] Phase 7 implemented
- [ ] Phase 8 prompt created
- [ ] Phase 8 implemented
- [ ] Phase 9 prompt created
- [ ] Phase 9 implemented
- [ ] Phase 10 prompt created
- [ ] Phase 10 implemented

---

## 📝 Notes

- This feature is being added to the `copilot/fix-strict-conflicts-detected` branch
- Original PR fix (whitelist parsing) remains intact
- New feature adds complementary duplicate detection capabilities
- Maintains separation of concerns with modular design
- All phases include iterative self-healing and validation
