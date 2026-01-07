# Diagram and Visualization Update System

**Version**: 1.0.0  
**Created**: 2025-12-30  
**Purpose**: Systematic approach to maintaining diagrams and visualizations  
**Tool**: `scripts/maintenance/update_diagrams.py`

---

## 🎯 Overview

This system ensures all diagrams, Mermaid charts, and visual representations in the codebase remain current and accurate.

### Why Systematic Updates Matter
- **Accuracy**: Diagrams drift from reality over time
- **Onboarding**: New contributors rely on visual guides
- **Documentation**: Visual representations aid understanding
- **Maintenance**: Outdated diagrams mislead and confuse

---

## 🛠️ Automated Update Tool

### Usage

```bash
# Scan repository for all diagrams
python scripts/maintenance/update_diagrams.py --scan

# Generate update report
python scripts/maintenance/update_diagrams.py --scan --output docs/maintenance/DIAGRAM_UPDATE_REPORT.md

# Validate diagram syntax
python scripts/maintenance/update_diagrams.py --validate

# Update diagrams automatically (future)
python scripts/maintenance/update_diagrams.py --update
```

### What It Scans

1. **Mermaid Diagrams** - Flow charts, graphs, sequences
2. **PlantUML Diagrams** - UML diagrams
3. **Graphviz/DOT** - Network graphs
4. **ASCII Art** - Text-based diagrams

### What It Checks

- ✅ Phase status accuracy (Phase 6-9 completion percentages)
- ✅ Workflow diagram currency (reflects actual workflows)
- ✅ Architecture diagram accuracy (matches current structure)
- ✅ Coverage percentages (reflects current test coverage)
- ✅ Component references (all mentioned components exist)

---

## 📊 Standard Diagrams

### Phase Status Diagram

**Location**: Should be in `docs/system/CODEBASE_DASHBOARD.md` and `docs/ROADMAP.md`

**Current Version**:
```mermaid
graph LR
    P6[Phase 6: MCP<br/>100% ✅] --> P7[Phase 7: Cognitive Brain<br/>100% ✅]
    P7 --> P8[Phase 8: Documentation<br/>100% ✅]
    P8 --> P9[Phase 9: Coverage<br/>10% 🔄]
    
    P9 --> P91[9.1: Critical Paths<br/>72% → 85%]
    P9 --> P92[9.2: Public APIs<br/>85% → 92%]
    P9 --> P93[9.3: Error Paths<br/>92% → 97%]
    P9 --> P94[9.4: Edge Cases<br/>97% → 100%]
    
    style P6 fill:#90EE90
    style P7 fill:#90EE90
    style P8 fill:#90EE90
    style P9 fill:#FFD700
    style P91 fill:#FFE4B5
    style P92 fill:#FFE4B5
    style P93 fill:#FFE4B5
    style P94 fill:#FFE4B5
```

**Update Trigger**: When any phase changes status or completion percentage

### Architecture Diagram

**Location**: Should be in `docs/system/CODEBASE_COGNITIVE_MAP.md` and `README.md`

**Current Version**:
```mermaid
graph TB
    subgraph "Cognitive Brain"
        CB_MAP[Cognitive Map<br/>Architecture]
        CB_DASH[Dashboard<br/>Status]
        CB_ROAD[Roadmap<br/>Planning]
    end
    
    subgraph "Core Systems"
        CODEX[Codex Pipeline<br/>src/codex/]
        AGENTS[Agent System<br/>agents/]
        MCP[MCP Packaging<br/>scripts/mcp/]
    end
    
    subgraph "Infrastructure"
        TESTS[Test Suite<br/>1500+ tests]
        DOCS[Documentation<br/>212+ KB]
        CI[CI/CD<br/>7 workflows]
    end
    
    CB_MAP --> CODEX
    CB_MAP --> AGENTS
    CB_MAP --> MCP
    CB_DASH --> TESTS
    CB_DASH --> CI
    CB_ROAD --> DOCS
    
    AGENTS --> CODEX
    MCP --> AGENTS
    TESTS --> CODEX
    TESTS --> AGENTS
    CI --> TESTS
    
    style CB_MAP fill:#E6F3FF
    style CB_DASH fill:#E6F3FF
    style CB_ROAD fill:#E6F3FF
    style CODEX fill:#FFE6E6
    style AGENTS fill:#FFE6E6
    style MCP fill:#FFE6E6
    style TESTS fill:#E6FFE6
    style DOCS fill:#E6FFE6
    style CI fill:#E6FFE6
```

**Update Trigger**: When new components added or architecture changes

### Coverage Progress Diagram

**Location**: Should be in `docs/testing/COVERAGE_100_ROADMAP.md`

**Current Version**:
```mermaid
graph LR
    START[Current: 72%] --> P91[Phase 9.1<br/>85%]
    P91 --> P92[Phase 9.2<br/>92%]
    P92 --> P93[Phase 9.3<br/>97%]
    P93 --> TARGET[Target: 100% ✨]
    
    P91 -.150-200 tests.-> P91
    P92 -.100-150 tests.-> P92
    P93 -.80-120 tests.-> P93
    TARGET -.50-80 tests.-> TARGET
    
    style START fill:#FFB6C1
    style P91 fill:#FFD700
    style P92 fill:#90EE90
    style P93 fill:#90EE90
    style TARGET fill:#32CD32
```

**Update Trigger**: After each phase 9 sub-phase completion, update percentages

### Workflow Diagram

**Location**: Should be in `docs/workflows/` or `.github/workflows/README.md`

**Current Version**:
```mermaid
graph TD
    START([Start]) --> SCAN[Scan Codebase]
    SCAN --> TEST[Run Tests]
    TEST --> LINT[Lint & Format]
    LINT --> BUILD[Build Package]
    BUILD --> DEPLOY{Deploy?}
    DEPLOY -->|Yes| PROD[Production]
    DEPLOY -->|No| STAGING[Staging]
    
    TEST -.Coverage.-> COV[Coverage Report]
    LINT -.Quality.-> QUALITY[Quality Report]
    
    style START fill:#E6F3FF
    style PROD fill:#90EE90
    style STAGING fill:#FFD700
    style COV fill:#E6FFE6
    style QUALITY fill:#E6FFE6
```

**Update Trigger**: When CI/CD workflows change

---

## 📋 Update Process

### Manual Update Process

1. **Run Scanner**
   ```bash
   python scripts/maintenance/update_diagrams.py --scan
   ```

2. **Review Report**
   - Open `docs/maintenance/DIAGRAM_UPDATE_REPORT.md`
   - Identify diagrams needing updates
   - Note update reasons

3. **Update Diagrams**
   - Use standard diagrams from this guide
   - Modify percentages, names, or structure as needed
   - Maintain consistent styling

4. **Validate**
   ```bash
   python scripts/maintenance/update_diagrams.py --validate
   ```

5. **Commit Changes**
   ```bash
   git add <modified_files>
   git commit -m "docs: Update diagrams to reflect current state"
   ```

### Automated Update Process (Future)

```bash
# Automatically update all diagrams
python scripts/maintenance/update_diagrams.py --update --auto-commit
```

This will:
- Scan for outdated diagrams
- Apply standard updates
- Generate commit with changes
- Optionally create PR

---

## 🔄 Update Triggers

### Phase Status Changes
**Trigger**: Phase completion percentage changes
**Files to Update**:
- `docs/system/CODEBASE_DASHBOARD.md`
- `docs/ROADMAP.md`
- `.github/CONTINUATION_PROMPT_*.md`

**Action**: Update phase status diagram with new percentages

### Architecture Changes
**Trigger**: New components added or removed
**Files to Update**:
- `docs/system/CODEBASE_COGNITIVE_MAP.md`
- `README.md`
- Component-specific README files

**Action**: Update architecture diagram with new components

### Coverage Changes
**Trigger**: Test coverage significantly changes (>5%)
**Files to Update**:
- `docs/testing/COVERAGE_100_ROADMAP.md`
- `docs/system/CODEBASE_DASHBOARD.md`
- Test-related documentation

**Action**: Update coverage diagrams and percentages

### Workflow Changes
**Trigger**: New workflows added or modified
**Files to Update**:
- `.github/workflows/README.md`
- `docs/workflows/`
- CI/CD documentation

**Action**: Update workflow diagrams

---

## 📊 Diagram Standards

### Naming Conventions
- Use descriptive, kebab-case filenames for diagram files
- Prefix with diagram type: `mermaid-`, `plantuml-`, etc.
- Include date in version history: `architecture-Previous Cycle-12-30`

### Styling Guidelines
- **Completed**: Green (#90EE90)
- **In Progress**: Yellow/Gold (#FFD700)
- **Pending**: Light colors (#FFE4B5)
- **Infrastructure**: Light green (#E6FFE6)
- **Core Systems**: Light red (#FFE6E6)
- **Cognitive Brain**: Light blue (#E6F3FF)

### Mermaid Best Practices
1. Use subgraphs for logical groupings
2. Add descriptions with `<br/>` for multi-line labels
3. Use appropriate graph types (TB, LR, etc.)
4. Apply consistent styling
5. Add legends when needed

---

## 🔧 Integration with CI/CD

### Pre-Commit Hook (Future)
```bash
# .git/hooks/pre-commit
python scripts/maintenance/update_diagrams.py --validate
if [ $? -ne 0 ]; then
    echo "❌ Diagram validation failed"
    exit 1
fi
```

### GitHub Actions Workflow (Future)
```yaml
name: Diagram Validation
on: [pull_request]
jobs:
  validate-diagrams:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate diagrams
        run: python scripts/maintenance/update_diagrams.py --validate
```

---

## 📈 Maintenance Schedule

| Task | Frequency | Trigger | Owner |
|------|-----------|---------|-------|
| **Phase Diagrams** | After each phase completion | Phase status change | AI Agent |
| **Architecture** | Quarterly or on major changes | New component | DevOps |
| **Coverage** | After Phase 9 sub-phases | Coverage +5% | AI Agent |
| **Workflows** | On workflow changes | Workflow modified | DevOps |
| **Full Scan** | Monthly | First Monday | AI Agent |

---

## ✅ Acceptance Criteria

Diagram system is well-maintained when:
- [ ] All diagrams reflect current state (0 outdated)
- [ ] Automated scanner runs successfully
- [ ] Update reports generated monthly
- [ ] Standard diagrams used consistently
- [ ] Validation passes for all diagrams
- [ ] Update process documented
- [ ] Integration with CI/CD (future)

---

## 📚 References

### Documentation
- [Cognitive Map](../system/CODEBASE_COGNITIVE_MAP.md) - Architecture
- [Dashboard](../system/CODEBASE_DASHBOARD.md) - Current status
- [Roadmap](../ROADMAP.md) - Phase planning
- [Coverage Roadmap](../testing/COVERAGE_100_ROADMAP.md) - Testing plan

### Tools
- [Mermaid Documentation](https://mermaid.js.org/)
- [PlantUML Guide](https://plantuml.com/)
- [Graphviz Documentation](https://graphviz.org/)

### Scripts
- `scripts/maintenance/update_diagrams.py` - Diagram updater
- `scripts/maintenance/check_doc_links.py` - Link validator
- `scripts/mcp/mcp-package` - MCP packager

---

## 🎯 Future Enhancements

### Phase 1 (Phase 1 (Current Cycle))
- [ ] Automatic diagram updates
- [ ] CI/CD integration
- [ ] Pre-commit validation

### Phase 2 (Phase 2 (Current Cycle))
- [ ] Diagram versioning system
- [ ] Diff visualization
- [ ] Historical diagram viewer

### Phase 3 (Phase 3 (Current Cycle))
- [ ] AI-powered diagram generation
- [ ] Real-time diagram updates
- [ ] Interactive diagram editor

---

**Status**: System operational  
**Last Updated**: 2025-12-30  
**Next Review**: 2026-01-30  
**Maintainer**: AI Agent + DevOps Team
