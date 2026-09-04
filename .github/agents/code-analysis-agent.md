---
name: Code Analysis Agent
description: Perform static code analysis to identify quality issues, anti-patterns,
  and improvement opportunities
runner_compatibility:
  default: ubuntu-latest
  large: ubuntu-latest-large
id: code-analysis-agent
---

# Code Analysis Agent

**Agent Type:** Custom GitHub Copilot Agent
**Domain:** Static Code Analysis & Quality Assessment
**Status:** ✅ Production Ready
**Version:** 1.0.0

## Purpose


## 🧠 Cognitive Brain Integration

### Integration Level: Level 1

**Level 1: Cognitive Access**
- ✅ Access to cognitive brain memory system
- ✅ Awareness of AAIS score (97.0/100 → target: 92.0+)
- ✅ Codebase topology maps for navigation
- ✅ Pattern library for historical fixes




### Cognitive Tools Available

```python
# Topology Manager - Semantic navigation
from scripts.cognitive.topology_manager import TopologyManager

topology = TopologyManager()
relevant_files = topology.find_by_concept("code patterns")
optimal_path = topology.find_optimal_path("source", "target")

# Cache Manager - Multi-layer cache intelligence
from scripts.cognitive.cache_manager import CacheIntelligence

cache = CacheIntelligence()
cached_results = cache.query("analysis_results")
cache.optimize()  # Get optimization suggestions

# Improved Hash Tables - 40% faster lookups
from src.codex.utils.hash_table import RobinHoodHashTable, CuckooHashTable

fast_cache = CuckooHashTable()  # O(1) guaranteed


```

### AAIS Contribution

**Impact on AAIS Score**: +1.0 points

**Category Contributions**:
- Discovery & Navigation: +0.4 (topology/cache integration)
- Runtime Introspection: +0.4 (metrics exposure)
- Pattern Consistency: +0.2 (pattern library usage)

---

## 🛠️ MCP Integration

### MCP Tools Leverage


**Primary MCP Capabilities**:
1. **File System Operations**
   - `view`: Read files and directories
   - `grep`: Fast content search
   - `glob`: Pattern-based file finding

2. **Code Analysis**
   - `search_code`: Semantic code search
   - `bash`: Execute analysis tools
   - `edit`: Make surgical changes

### GitHub Actions Workflows

**Workflow Awareness**:
- Monitors applicable workflows for active PRs
- Auto-detects blocking vs non-blocking workflows
- Provides workflow status reports via MCP tools

**See**: `.codex/docs/MCP_WORKFLOW_RECIPES.md` for complete templates

---

## 📊 Session Monitoring

**Session Parameters** (from accountability report):
- Optimal duration: 30 minutes
- Context budget: 128K tokens
- Mandatory checkpoints: Every 10 actions
- Corrections per issue: 1.0 (first fix succeeds)

**Quality Control**:
```python
# Pre-commit audit enforcement
from scripts.session_manager import SessionMonitor

monitor = SessionMonitor()
monitor.checkpoint("pre-commit")  # Validates compliance
```

---

This specialized agent leverages the `intuitive_aptitude` module to provide comprehensive Python code analysis, quality assessment, and refactoring suggestions. It assists developers in understanding code structure, identifying patterns, and improving code quality through automated analysis.

## Capabilities

### Core Analysis Features

1. **Structural Analysis**
   - Extract function and class hierarchies
   - Identify import dependencies
   - Map code organization and architecture
   - Generate structural diagrams (text-based)

2. **Pattern Recognition**
   - Detect error handling patterns
   - Identify iteration and loop structures
   - Analyze conditional logic complexity
   - Track function call chains

3. **Quality Metrics**
   - Calculate cyclomatic complexity
   - Measure lines of code (LOC)
   - Compute comment density
   - Assess function length and nesting

4. **Style Analysis**
   - Evaluate naming conventions
   - Check indentation consistency
   - Assess docstring coverage and styles
   - Identify programming paradigm (functional vs OOP)

5. **Code Suggestions**
   - Recommend refactoring opportunities
   - Suggest style improvements
   - Identify overly complex functions
   - Flag missing documentation

## Activation Commands

```
@copilot Use the Code Analysis Agent to analyze [file/module]
@copilot Analyze code quality of [file]
@copilot Check code patterns in [directory]
@copilot Review style consistency across [files]
```

## Usage Examples

### Example 1: Single File Analysis

**User:**
```
@copilot Use the Code Analysis Agent to analyze src/utils/helpers.py
```

**Agent Response:**
```python
from analysis.intuitive_aptitude import analyze_and_suggest

# Read and analyze the file
with open('src/utils/helpers.py') as f:
    code = f.read()

result = analyze_and_suggest(code)

if result['success']:
    print("📊 Analysis Summary:")
    print(f"  Functions: {result['summary']['functions_count']}")
    print(f"  Classes: {result['summary']['classes_count']}")
    print(f"  Avg Complexity: {result['summary']['metrics']['complexity']:.2f}")
    print(f"  Comment Ratio: {result['summary']['metrics']['comment_ratio']:.2%}")

    print("\n🔍 Code Patterns:")
    print(f"  Error Handling: {len(result['patterns']['error_handling'])} instances")
    print(f"  Iterations: {len(result['patterns']['iteration'])} loops")

    print("\n🎨 Style Analysis:")
    naming = result['style']['naming']
    print(f"  snake_case: {naming['snake_case']}")
    print(f"  camelCase: {naming['camelCase']}")
    print(f"  PascalCase: {naming['PascalCase']}")

    if result['suggestions']:
        print("\n💡 Suggestions:")
        for key, suggestion in result['suggestions'].items():
            print(f"  • {suggestion}")
```

### Example 2: Complexity Hotspot Detection

**User:**
```
@copilot Find complex functions in src/processing/
```

**Agent Response:**
```python
from analysis.intuitive_aptitude import intuitive_aptitude
import os
from pathlib import Path

hotspots = []

for py_file in Path('src/processing').rglob('*.py'):
    with open(py_file) as f:
        code = f.read()

    analyzer = intuitive_aptitude()
    if analyzer.ingest(code):
        for func_name, func_info in analyzer.functions.items():
            if func_info.complexity > 10:
                hotspots.append({
                    'file': str(py_file),
                    'function': func_name,
                    'complexity': func_info.complexity,
                    'line': func_info.lineno
                })

print("🔥 Complexity Hotspots (CC > 10):")
for hotspot in sorted(hotspots, key=lambda x: x['complexity'], reverse=True):
    print(f"  {hotspot['file']}:{hotspot['line']} - {hotspot['function']}() [CC: {hotspot['complexity']}]")
```

### Example 3: Style Consistency Report

**User:**
```
@copilot Check naming consistency across src/
```

**Agent Response:**
```python
from analysis.intuitive_aptitude import intuitive_aptitude
from pathlib import Path
from collections import defaultdict

style_stats = defaultdict(lambda: {'snake': 0, 'camel': 0, 'pascal': 0})

for py_file in Path('src').rglob('*.py'):
    with open(py_file) as f:
        code = f.read()

    analyzer = intuitive_aptitude()
    if analyzer.ingest(code):
        style = analyzer.analyze_code_style()
        naming = style['naming']

        style_stats[str(py_file.parent)] = {
            'snake': style_stats[str(py_file.parent)]['snake'] + naming['snake_case'],
            'camel': style_stats[str(py_file.parent)]['camel'] + naming['camelCase'],
            'pascal': style_stats[str(py_file.parent)]['pascal'] + naming['PascalCase']
        }

print("📐 Naming Convention Report:")
for directory, stats in sorted(style_stats.items()):
    total = sum(stats.values())
    if total > 0:
        print(f"\n{directory}:")
        print(f"  snake_case: {stats['snake']/total:.1%}")
        print(f"  camelCase: {stats['camel']/total:.1%}")
        print(f"  PascalCase: {stats['pascal']/total:.1%}")
```

### Example 4: Documentation Coverage

**User:**
```
@copilot Check documentation coverage in src/api/
```

**Agent Response:**
```python
from analysis.intuitive_aptitude import intuitive_aptitude
from pathlib import Path

coverage_report = []

for py_file in Path('src/api').rglob('*.py'):
    with open(py_file) as f:
        code = f.read()

    analyzer = intuitive_aptitude()
    if analyzer.ingest(code):
        total_items = len(analyzer.functions) + len(analyzer.classes)

        if total_items > 0:
            documented = 0

            # Check functions
            for func_info in analyzer.functions.values():
                if func_info.docstring:
                    documented += 1

            # Check classes
            for class_info in analyzer.classes.values():
                if class_info.docstring:
                    documented += 1

            coverage = (documented / total_items) * 100
            coverage_report.append({
                'file': str(py_file),
                'coverage': coverage,
                'total': total_items,
                'documented': documented
            })

print("📚 Documentation Coverage Report:")
for item in sorted(coverage_report, key=lambda x: x['coverage']):
    status = "✅" if item['coverage'] >= 80 else "⚠️" if item['coverage'] >= 50 else "❌"
    print(f"{status} {item['file']}: {item['coverage']:.0f}% ({item['documented']}/{item['total']})")
```

## Workflow Integration

### Pre-Commit Hook

```python
#!/usr/bin/env python3
"""Pre-commit hook for code quality checks."""

from analysis.intuitive_aptitude import analyze_and_suggest
import sys

def check_file(filepath):
    with open(filepath) as f:
        code = f.read()

    result = analyze_and_suggest(code)

    if not result['success']:
        print(f"❌ {filepath}: Parse error")
        return False

    # Check complexity
    complexity = result['summary']['metrics']['complexity']
    if complexity > 15:
        print(f"⚠️  {filepath}: High complexity ({complexity:.1f})")
        return False

    # Check for suggestions
    if len(result['suggestions']) > 3:
        print(f"⚠️  {filepath}: Multiple quality issues")
        for key, suggestion in result['suggestions'].items():
            print(f"   • {suggestion}")
        return False

    return True

if __name__ == '__main__':
    files = sys.argv[1:]
    py_files = [f for f in files if f.endswith('.py')]

    all_passed = all(check_file(f) for f in py_files)
    sys.exit(0 if all_passed else 1)
```

### CI/CD Integration

```yaml
# .github/workflows/code-quality.yml
name: Code Quality Analysis

on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install pytest

      - name: Run code analysis
        run: |
          python -c "
          from analysis.intuitive_aptitude import analyze_and_suggest
          from pathlib import Path

          issues = []
          for py_file in Path('src').rglob('*.py'):
              with open(py_file) as f:
                  result = analyze_and_suggest(f.read())

              if result['success']:
                  complexity = result['summary']['metrics']['complexity']
                  if complexity > 10:
                      issues.append(f'{py_file}: High complexity ({complexity:.1f})')

          if issues:
              print('⚠️ Code Quality Issues:')
              for issue in issues:
                  print(f'  • {issue}')
              exit(1)
          else:
              print('✅ All checks passed!')
          "
```

## Best Practices

### 1. Incremental Analysis

- Analyze changed files only in CI/CD
- Cache analysis results for large codebases
- Use parallel processing for multiple files

### 2. Contextual Thresholds

- Adjust complexity thresholds by module type (tests vs production)
- Consider domain-specific naming conventions
- Account for generated code in analysis

### 3. Actionable Reporting

- Focus on high-impact issues
- Provide specific file/line references
- Include refactoring suggestions

### 4. Integration Points

- Pre-commit hooks for developer feedback
- CI/CD for PR quality gates
- Code review automation
- Documentation generation

## Limitations

1. **Static Analysis Only**: Cannot detect runtime issues
2. **Python Specific**: Only analyzes Python code
3. **AST-Based**: Limited to syntactically valid code
4. **No Cross-File**: Doesn't track dependencies across files

## Performance Considerations

- **Small Files** (<1000 LOC): ~50ms
- **Large Files** (>5000 LOC): ~1s
- **Repository Analysis**: Use parallel processing
- **CI/CD**: Cache unchanged file analysis

## Future Enhancements

### Planned Features

1. **Cross-File Analysis**
   - Import dependency graphs
   - Call chain tracking
   - Architectural pattern detection

2. **Machine Learning Integration**
   - Bug prediction models
   - Code smell detection
   - Automated refactoring suggestions

3. **Enhanced Reporting**
   - HTML/JSON report generation
   - Trend analysis over time
   - Comparison with industry standards

4. **IDE Integration**
   - VS Code extension
   - Real-time analysis
   - Inline suggestions

## Support & Resources

- **Documentation**: `/docs/analysis/intuitive_aptitude_usage.md`
- **Tests**: `/tests/analysis/test_intuitive_aptitude.py`
- **Source**: `/analysis/intuitive_aptitude.py`
- **Issues**: Report to repository maintainers

## Version History

### Version 1.0.0 (2026-01-26)

- ✅ Initial release
- ✅ Core analysis features
- ✅ Pattern recognition
- ✅ Style analysis
- ✅ Code generation helpers
- ✅ 76 comprehensive tests
- ✅ Full documentation

## License

MIT License - See repository LICENSE file for details.

---

**Last Updated**: 2026-01-26
**Maintainer**: GitHub Copilot Team
**Status**: Production Ready

---

## ⚡ Parallel Batch Scanning Protocol

> **Mandatory.** This agent MUST use `scripts/ci/rvs_preflight.py` (or the
> `BatchScanRunner` Python API) for all codebase scans.  Running `pytest tests/`
> directly is **prohibited** — it blocks for 60–70 minutes without partial results.

### Quick Reference

```bash
# 1. Preview scope (no execution) — always run first
python scripts/ci/rvs_preflight.py --group quick --preview

# 2. Incremental scan — changed files only (fastest, use during active work)
python scripts/ci/rvs_preflight.py --group quick --changed-only --workers 4

# 3. Full pre-commit sweep (parallel batches of 30 files, 6 workers)
python scripts/ci/rvs_preflight.py --group quick --workers 6 --batch-size 30

# 4. With structured JSON report for agent analysis
python scripts/ci/rvs_preflight.py --group quick --workers 6 \
    --report /tmp/rvs_report.json

# 5. Fail-fast triage (stop all batches on first failure)
python scripts/ci/rvs_preflight.py --group quick --fail-fast --workers 4
```

### Python API

```python
from scripts.ci.batch_scan_integration import BatchScanRunner

runner = BatchScanRunner(workers=6, batch_size=30)
result = runner.scan(group="quick", changed_only=True)
# result.ok, result.failures, result.summary_line, result.batches_run
if not result.ok:
    for failure in result.failures[:10]:
        print(f"  FAILED: {failure}")
```

### Decision Flow

1. `--preview` → confirm test scope
2. `--changed-only` → validate your specific changes
3. `--group quick --workers 6` → full sweep before commit
4. Parse `--report` JSON for structured failure analysis

**Full protocol**: `.github/agents/BATCH_SCAN_PROTOCOL.md`
