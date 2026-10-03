# Phase 6 Test-Cycle Dependency Diagrams

## Main Remediation Flow

```mermaid
graph TD
    START["🚀 Phase 6 Sprint Start<br/>(2-3 hours parallel execution)"] 
    
    START --> ANALYSIS["📊 Error Analysis Complete<br/>142 Collection Errors Identified"]
    
    ANALYSIS -->|87 Import Errors| BATCH1["⚙️ Batch Worker 1<br/>Install Dependencies<br/>45 min"]
    ANALYSIS -->|35 Name Errors| BATCH2["🔧 Batch Worker 2<br/>Fix Import Paths<br/>40 min"]
    ANALYSIS -->|15 Syntax Errors| BATCH3["🎯 Batch Worker 3<br/>Detect Flaky Tests<br/>30 min"]
    ANALYSIS -->|5 Other Errors| BATCH1
    
    BATCH1 -->|numpy<br/>tenacity<br/>torch| INSTALL["📦 Install Missing Packages<br/>pip install numpy tenacity torch"]
    BATCH1 --> UPDATE["📝 Update requirements-test.txt<br/>Add: numpy, tenacity, torch"]
    BATCH1 --> VERIFY1["✅ Verify Installations<br/>pip list | grep -E 'numpy|tenacity'"]
    
    BATCH2 -->|P19 Shadow Import<br/>Detection| AUDIT["🔍 Audit Module Exports<br/>Check __init__.py files"]
    BATCH2 -->|Symbol Not Found<br/>BrainInterface| FIX_BRAIN["📌 Fix: Add BrainInterface<br/>to src/aries_serpent_core/cognitive/__init__.py"]
    BATCH2 -->|Symbol Not Found<br/>MultiLocaleSyncManager| FIX_CRAWLER["📌 Fix: Export from<br/>services/crawler/__init__.py"]
    BATCH2 -->|Import Path<br/>Normalization| RUFF["🎨 Run Ruff Import Check<br/>ruff check --select I001,E401,F401"]
    
    BATCH3 -->|Find Flaky Markers| GREP["🔎 grep -rn pytest.mark.flaky"]
    BATCH3 -->|Classify by Reason| CLASSIFY["📋 Classify:<br/>- Network/timing: Keep<br/>- P19-affected: Remove & fix<br/>- Other: Add reason="]
    BATCH3 -->|Update Markers| ADD_REASON["📝 Add reason= argument<br/>@pytest.mark.flaky(reruns=2, reason='...')"]
    
    VERIFY1 --> CONVERGE["🔗 CONVERGE: All Fixes Complete"]
    AUDIT --> CONVERGE
    FIX_BRAIN --> CONVERGE
    FIX_CRAWLER --> CONVERGE
    RUFF --> CONVERGE
    ADD_REASON --> CONVERGE
    
    CONVERGE --> SMOKE["🧪 Pass 1: Import Smoke Test<br/>python -c 'from codex import *'"]
    SMOKE -->|0 exceptions| PASS1["✅ Pass 1 Complete"]
    SMOKE -->|ERROR| DEBUG1["🐛 Debug: Check imports"]
    DEBUG1 --> SMOKE
    
    PASS1 --> RUFF_VAL["🎨 Pass 2: Ruff Validation<br/>ruff check --select F401,B904,I001"]
    RUFF_VAL -->|0 errors| PASS2["✅ Pass 2 Complete"]
    RUFF_VAL -->|Errors| FIX_RUFF["🔧 Fix ruff errors"]
    FIX_RUFF --> RUFF_VAL
    
    PASS2 --> COLLECT["📦 Pass 3: Test Collection<br/>pytest tests/agents/ --collect-only -q"]
    COLLECT -->|ERROR: 0| PASS3["✅ Pass 3 Complete"]
    COLLECT -->|ERROR: >0| DEBUG3["🐛 Remaining errors"]
    DEBUG3 --> COLLECT
    
    PASS3 --> REGRESS["🧪 Pass 4: Regression Check<br/>pytest tests/agents/test_exceptions.py -v"]
    REGRESS -->|Pass rate ≥95%| PASS4["✅ Pass 4 Complete"]
    REGRESS -->|Failures| DEBUG4["🐛 Debug failures"]
    DEBUG4 --> REGRESS
    
    PASS4 --> POLICY["📋 Pass 5: Policy Compliance<br/>Check: P19 imports, no deleted tests,<br/>flaky with reason=, requirements updated"]
    POLICY -->|All checks✅| PASS5["✅ Pass 5 Complete"]
    POLICY -->|Violations| FIX_POLICY["🔧 Fix policy violations"]
    FIX_POLICY --> POLICY
    
    PASS5 --> COMMIT["💾 Commit & Push<br/>chore(phase6): fix 142 test errors"]
    COMMIT --> SUCCESS["🎉 Phase 6.1 Complete<br/>✅ Collection Errors: 0/142<br/>✅ Test Pass Rate: ≥95%<br/>✅ P19 Compliance: 100%"]
```

---

## Import Error Resolution Flow

```mermaid
graph LR
    A["142 Collection Errors"] -->|87 Import<br/>Errors| B["ModuleNotFoundError<br/>or ImportError"]
    
    B -->|34 files| C["numpy<br/>not installed"]
    B -->|3 files| D["tenacity<br/>not installed"]
    B -->|2 files| E["torch<br/>not installed"]
    B -->|7 files| F["Symbol not<br/>found in module"]
    B -->|41 files| G["Other import<br/>issues"]
    
    C -->|pip install| H1["✅ numpy installed"]
    D -->|pip install| H2["✅ tenacity installed"]
    E -->|pip install| H3["✅ torch installed"]
    F -->|audit __init__.py| I["Check exports"]
    G -->|P19 audit| J["Verify src/ path"]
    
    I -->|Add symbol| K["Export in __init__.py"]
    I -->|Update import| L["Use correct path"]
    K -->|Verify| M["Import works ✅"]
    L -->|Verify| M
    J -->|src/ path OK| N["✅ P19 Compliant"]
    J -->|Wrong path| O["Reinstall package"]
    O -->|pip install --force| N
    
    H1 --> TEST["Test Collection<br/>pytest --collect-only"]
    H2 --> TEST
    H3 --> TEST
    M --> TEST
    N --> TEST
    
    TEST -->|0 errors| SUCCESS["✅ 87 Import<br/>Errors Resolved"]
    TEST -->|Errors remain| DEBUG["🐛 Debug & Retry"]
    DEBUG --> TEST
```

---

## P19 Shadow Import Detection & Resolution

```mermaid
graph TD
    DETECT["🔍 P19 Shadow Import Detection<br/>(Stale .egg-link or sys.path ordering)"]
    
    DETECT --> CHECK1["Check import resolution<br/>python -c import codex<br/>print codex.__file__"]
    
    CHECK1 -->|Contains src/| OK["✅ Correct: src/ path<br/>No shadow import"]
    CHECK1 -->|site-packages/| SHADOW["❌ ERROR: site-packages<br/>Old .egg-link shadowing src/"]
    
    SHADOW --> FIX1["Fix Option 1:<br/>Reinstall with --force"]
    SHADOW --> FIX2["Fix Option 2:<br/>Clear sys.path and reinstall"]
    
    FIX1 --> CMD1["pip install<br/>--force-reinstall --no-deps<br/>-e ."]
    FIX2 --> CMD2["pip uninstall codex -y &&<br/>pip install -e ."]
    
    CMD1 --> VERIFY["Verify fix<br/>python -c import codex"]
    CMD2 --> VERIFY
    
    VERIFY -->|src/ path| SUCCESS["✅ P19 Shadow Import Fixed"]
    VERIFY -->|still wrong| ESCALATE["🚨 Escalate to agent-iq-scoring-gate"]
    
    OK --> TEST["Run tests that were failing<br/>due to import mismatches"]
    SUCCESS --> TEST
    
    TEST -->|Pass| DONE["✅ P19 Resolution Complete"]
    TEST -->|Fail| DEBUG["Debug: Check other causes"]
```

---

## Flaky Test Classification & Escalation

```mermaid
graph TD
    FLAKY["🎯 Flaky Test Detected<br/>@pytest.mark.flaky(reruns=N)"]
    
    FLAKY --> CHECK["Analyze failure reason"]
    
    CHECK -->|Network timeout<br/>External API call| NETWORK["✅ Network Flaky<br/>Acceptable cause"]
    CHECK -->|Timing/race condition<br/>Async test| TIMING["⚠️ Timing Flaky<br/>Investigate"]
    CHECK -->|Import error<br/>Module path issue| SHADOW["🔴 P19 Shadow Import<br/>Not a real flaky!"]
    CHECK -->|Random test data<br/>Non-deterministic| RANDOM["⚠️ Data Flaky<br/>Fix test"]
    
    NETWORK -->|reruns ≤ 2| KEEP1["✅ Keep flaky marker<br/>Add reason="]
    NETWORK -->|reruns ≥ 3| ESCALATE1["🚨 High reruns<br/>Escalate if >50% fail rate"]
    
    TIMING -->|Investigate root cause| FIX_TIMING["Add @pytest.mark.xfail<br/>with strict=False"]
    
    SHADOW -->|Remove flaky| REMOVE["Remove @pytest.mark.flaky"]
    SHADOW -->|Apply P19 fix| P19FIX["Fix import paths<br/>Resolve shadow import"]
    
    RANDOM -->|Fix test| FIX_RANDOM["Make test deterministic<br/>Add seed or mock randomness"]
    
    KEEP1 --> RESULT1["✅ Flaky Test Properly Marked"]
    ESCALATE1 -->|Check last 10 runs| EVAL["Evaluate fail rate"]
    EVAL -->|>50% failures| ESCALATE2["🚨 Escalate to<br/>self-healing-orchestrator<br/>RP-002"]
    EVAL -->|<50% failures| RESULT1
    FIX_TIMING --> RESULT2["✅ Timing Issue Tracked"]
    REMOVE --> RESULT2
    P19FIX --> RESULT2
    FIX_RANDOM --> RESULT3["✅ Test Fixed<br/>Remove flaky marker"]
    
    RESULT1 --> DONE["✅ Flaky Management Complete"]
    RESULT2 --> DONE
    RESULT3 --> DONE
```

---

## Quality Gate Sequential Checks

```mermaid
graph TB
    START["Phase 6 Quality Gates<br/>(Sequential validation)"] -->|Gate 1| IMPORT["Import Resolution Check<br/>✓ All 87 import errors resolved<br/>✓ No ModuleNotFoundError"]
    
    IMPORT -->|PASS| SYNTAX["Syntax Correction Gate<br/>✓ All 15 syntax errors fixed<br/>✓ ruff check: 0 errors"]
    IMPORT -->|FAIL| IMPORT_DEBUG["🐛 Debug imports<br/>pip list, python -c import"]
    IMPORT_DEBUG --> IMPORT
    
    SYNTAX -->|PASS| P19["P19 Compliance Gate<br/>✓ All imports from src/<br/>✓ No site-packages shadowing<br/>✓ Check: python -c 'import codex'"]
    SYNTAX -->|FAIL| SYNTAX_DEBUG["🐛 Fix syntax errors<br/>ruff check --select F,I,E"]
    SYNTAX_DEBUG --> SYNTAX
    
    P19 -->|PASS| REGRESS["Regression Prevention Gate<br/>✓ Test pass rate ≥ 95%<br/>✓ No new test failures<br/>✓ Coverage maintained"]
    P19 -->|FAIL| P19_DEBUG["🐛 Reinstall package<br/>pip install --force-reinstall -e ."]
    P19_DEBUG --> P19
    
    REGRESS -->|PASS| FLAKY["Flaky Test Management Gate<br/>✓ 12 flaky tests marked<br/>✓ All have reason=<br/>✓ High-rerun tests escalated"]
    REGRESS -->|FAIL| REGRESS_DEBUG["🐛 Run failing tests<br/>Identify root cause"]
    REGRESS_DEBUG --> REGRESS
    
    FLAKY -->|PASS| SUCCESS["✅ ALL GATES PASSED<br/>Phase 6.1 Complete"]
    FLAKY -->|FAIL| FLAKY_DEBUG["🐛 Add reason= to markers<br/>Escalate high-rerun tests"]
    FLAKY_DEBUG --> FLAKY
    
    SUCCESS --> COMMIT["💾 Commit Changes<br/>Push to Phase 6 branch"]
```

---

## Dependencies Between Fix Tasks

```mermaid
graph LR
    W1["Worker 1:<br/>Install Deps"]
    W2["Worker 2:<br/>Import Paths"]
    W3["Worker 3:<br/>Flaky Tests"]
    
    W1 -->|pip install| DEP["Dependencies<br/>Available"]
    W2 -->|audit| EXP["Module exports<br/>verified"]
    W3 -->|grep| MARKERS["Flaky markers<br/>identified"]
    
    DEP --> CONV["Convergence<br/>Point"]
    EXP --> CONV
    MARKERS --> CONV
    
    CONV --> SMOKE["🧪 Pass 1: Smoke Test<br/>All imports work"]
    CONV --> RUFF["🎨 Pass 2: Ruff Check<br/>0 import errors"]
    CONV --> COLLECT["📦 Pass 3: Collection<br/>0 collection errors"]
    
    SMOKE --> S1["✅ Pass 1"]
    RUFF --> S1
    COLLECT --> S1
    
    S1 --> S4["🧪 Pass 4: Regressions<br/>≥95% pass rate"]
    S4 --> S5["📋 Pass 5: Policy<br/>P19 compliant"]
    
    S5 --> FINAL["🎉 Phase 6.1 Complete"]
    
    style W1 fill:#ff9999
    style W2 fill:#99ccff
    style W3 fill:#99ff99
    style CONV fill:#ffff99
    style FINAL fill:#99ff99
```

---

## Error Category Breakdown

```mermaid
pie title Distribution of 142 Collection Errors
    "Import/Module (87, 61%)" : 87
    "Name Errors (35, 25%)" : 35
    "Syntax Errors (15, 11%)" : 15
    "Other Errors (5, 3%)" : 5
```

---

## Remediation Progress Tracking

```mermaid
gantt
    title Phase 6 Sprint Execution (2-3 hours total)
    
    section Worker 1
    Install numpy (10 min) :w1_1, 0, 10m
    Install tenacity (5 min) :w1_2, 10m, 5m
    Install torch (10 min) :w1_3, 15m, 10m
    Update requirements (10 min) :w1_4, 25m, 10m
    Verify installations (10 min) :w1_5, 35m, 10m
    
    section Worker 2
    Audit P19 (10 min) :w2_1, 0, 10m
    Fix BrainInterface export (10 min) :w2_2, 10m, 10m
    Fix crawler exports (10 min) :w2_3, 20m, 10m
    Run ruff (5 min) :w2_4, 30m, 5m
    Apply fixes (10 min) :w2_5, 35m, 10m
    
    section Worker 3
    Find flaky markers (5 min) :w3_1, 0, 5m
    Classify tests (15 min) :w3_2, 5m, 15m
    Add reason= (5 min) :w3_3, 20m, 5m
    Generate report (5 min) :w3_4, 25m, 5m
    
    section Validation
    Convergence (5 min) :crit, conv, 45m, 5m
    Pass 1-2 (5 min) :crit, p12, after conv, 5m
    Pass 3-5 (10 min) :crit, p35, after p12, 10m
    Commit (5 min) :crit, commit, after p35, 5m
    
    section Overall
    Total Duration :overall, 0, 70m
```

---

## Notes

- All diagrams show parallel execution paths
- Workers 1-3 can run simultaneously
- Convergence point ensures all fixes complete before validation
- 5-pass review gates ensure no regressions
- Success criteria: 0 collection errors, ≥95% pass rate, 100% P19 compliance
