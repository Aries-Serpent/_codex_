================================================================================
COMPREHENSIVE DOCUMENTATION QUALITY AUDIT REPORT
================================================================================

## EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
Repository Root: /home/runner/work/_codex_/_codex_
Total Python Files Analyzed: 1036
Total Lines of Code: 196,013
Total Markdown Files: 1100

**OVERALL DOCUMENTATION QUALITY SCORE: 73.0/100**
Grade: C (Satisfactory)

## DOCSTRING COVERAGE BY CATEGORY
--------------------------------------------------------------------------------
Module Docstrings:      100.0%
Function Docstrings:     50.9%
Class Docstrings:        82.7%
Method Docstrings:       67.1%
Public API Coverage:     74.8%

## DETAILED STATISTICS
--------------------------------------------------------------------------------
Functions:     1608 / 3157 documented (50.9%)
Classes:       1209 / 1462 documented (82.7%)
Methods:       2832 / 4220 documented (67.1%)
Public APIs:   4492 / 6008 documented (74.8%)

## USER DOCUMENTATION
--------------------------------------------------------------------------------
Total Documentation Files: 1100
Total Documentation Lines: 228,147
API Reference Files:       20
Tutorial Files:            3
Guide Files:               84
Architecture Files:        16
Files with Links:          276
Total Internal Links:      2141

User Documentation Score: 100.0/100

## CLI DOCUMENTATION
--------------------------------------------------------------------------------
CLI Files Found:                185
CLI Commands with Help Text:    195
CLI Commands without Help Text: 10
CLI Documentation Coverage:     95.1%

## TOP 20 MODULES MISSING DOCUMENTATION
--------------------------------------------------------------------------------
Rank  Coverage   LOC      Module Path
--------------------------------------------------------------------------------
1        5.0%        9  src/codex_ml/data/dataloader.py
2        5.0%       11  src/codex_ml/reward_models/__init__.py
3        5.0%       14  src/evaluation/__init__.py
4        5.0%       16  src/agent/secrets.py
5        5.0%       17  src/codex_ml/checkpointing/utils.py
6        5.0%       19  src/codex_ml/modeling/model_factory.py
7        5.0%       26  src/codex_ml/tokenization/__init__.py
8        5.0%       28  src/codex_ml/tokenization/compat.py
9        5.0%       30  src/codex/zendesk/model/app.py
10       5.0%       31  src/codex/evidence/__init__.py
11       5.0%       31  src/codex_ml/data/sharding.py
12       5.0%       32  src/codex_ml/registry.py
13       5.0%       32  src/codex/zendesk/model/widget.py
14       5.0%       32  src/codex_ml/utils/jsonl.py
15       5.0%       34  src/monitoring/performance_monitor.py
16       5.0%       34  src/codex_ml/connectors/local.py
17       5.0%       35  src/logging_config.py
18       5.0%       35  src/codex_ml/utils/torch_det.py
19       5.0%       35  src/codex_ml/detectors/core.py
20       5.0%       36  src/mcp/server/schemas.py

## MODULES WITH ZERO DOCUMENTATION (LOC > 10)
--------------------------------------------------------------------------------
Total: 0 modules


## OVERALL QUALITY SCORE CALCULATION
--------------------------------------------------------------------------------
API Documentation (50%):    73.0%
User Documentation (30%):  100.0%
CLI Documentation (20%):    95.1%

**FINAL OVERALL DOCUMENTATION QUALITY SCORE: 85.5/100**

## PRIORITIZED REMEDIATION PLAN
--------------------------------------------------------------------------------

1. [P0] Public API Documentation
   Action: Document all public functions, classes, and methods
   Impact: High | Effort: Medium

2. [P1] Tutorials
   Action: Create getting-started tutorials and examples
   Impact: Medium | Effort: Medium

3. [P1] Function Docstrings
   Action: Add docstrings to undocumented functions
   Impact: Medium | Effort: Medium

4. [P2] CLI Help Text
   Action: Add help text to all CLI commands
   Impact: Medium | Effort: Low

## QUICK WINS (Low Effort, High Impact)
--------------------------------------------------------------------------------
1. Add help text to 10 CLI commands (~2 minutes each)

## PHASE 5 EFFORT ESTIMATION (8 phases)
--------------------------------------------------------------------------------
Undocumented Items: 3190
  - Docstring Writing:        265.8 hours
  - API Reference Creation:     0.0 hours
  - Tutorial Creation:         21.0 hours

Total Estimated Effort:       286.8 hours
Weeks at 20 hrs/phase:           14.3 phases

⚠️  Phase 5 (8 phases) may be tight. Consider 14 phases or prioritization.

================================================================================
END OF REPORT
================================================================================
