# AST Analysis Agent

**Status:** Active  
**Created:** 2026-01-03  
**Version:** 1.0.0

## Overview

The AST Analysis Agent provides intelligent code analysis using the AST standardization 
module (`src/codex_ml/ast/`). It integrates with the Cognitive Brain for pattern learning
and memory-enhanced analysis.

## Features

- **Code Analysis**: Parse and analyze Python code using StandardizedASTNode
- **Pattern Detection**: Identify code patterns using PatternRecognizer
- **Finding Reports**: Generate structured finding reports with severity levels
- **Learning Integration**: Learn from analysis results via Cognitive Brain

## Architecture

```
ast-analysis-agent/
├── agent/
│   ├── __init__.py           # Package exports
│   ├── analyzer.py           # Core analysis engine
│   ├── pattern_detector.py   # Pattern detection logic
│   └── report_generator.py   # Finding report generation
├── tests/
│   ├── __init__.py
│   └── test_ast_agent.py     # Agent tests
└── README.md                 # This file
```

## Usage

```python
from ast_analysis_agent.agent import ASTAnalysisAgent

# Create agent
agent = ASTAnalysisAgent()

# Analyze code
findings = agent.analyze_file("path/to/code.py")

# Generate report
report = agent.generate_report(findings)
```

## Integration with Cognitive Brain

The agent uses the Cognitive Brain for:
1. Pattern storage and retrieval
2. Learning from analysis outcomes
3. Decision quality optimization via Q-learning

## Dependencies

- `src/codex_ml/ast/` - AST standardization module
- `.github/agents/core/` - Unified agent framework
- `.github/agents/cognitive-brain-agent/` - Cognitive Brain integration
