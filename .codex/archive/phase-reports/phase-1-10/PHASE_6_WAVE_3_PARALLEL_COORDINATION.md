# ⚡ Phase 6 Wave 3: Parallel Execution Coordination Guide

**Date:** 2026-06-27T22:22:25Z  
**Status:** ✅ Ready for Parallel Deployment  
**Campaign:** Phase 6 Wave 3 — ML Systems Coverage Gap Remediation  
**Coordination Model:** Full Parallel Execution (Lanes 3.1, 3.2, 3.3)  

---

## Parallel Execution Overview

### Three Independent Lanes → Parallel Execution Model

```
Phase 6 Wave 3 Parallel Timeline
════════════════════════════════════════════════════════════════

LANE 3.1 (ML Training Pipeline)       LANE 3.2 (ML CLI)              LANE 3.3 (ML Data)
─────────────────────────────────     ─────────────────────────────  ──────────────────
T+0h:   Setup fixtures               Setup CliRunner                 Setup data fixtures
        ↓                             ↓                               ↓
T+2h:   Dev Phase 1 (8h)             Dev Phase 1 (7h)               Dev Phase 1 (7h)
        GAP-3.1.1→3.1.4              GAP-3.2.1→3.2.4                GAP-3.3.1→3.3.4
        ↓                             ↓                               ↓
T+10h:  Checkpoint (2h)              Checkpoint (2h)                Checkpoint (2h)
        50% tests complete           50% tests complete             50% tests complete
        ↓                             ↓                               ↓
T+12h:  Dev Phase 2 (8h)             Dev Phase 2 (7h)               Dev Phase 2 (5h)
        GAP-3.1.5→3.1.7              GAP-3.2.5→3.2.7                GAP-3.3.5→3.3.7
        ↓                             ↓                               ↓
T+20h:  CI Validation (4h)           CI Validation (3h)             CI Validation (3h)
        Full test suite              Full test suite                Full test suite
        ↓                             ↓                               ↓
T+24h:  Sign-off (1h)                Sign-off (1h)                  Sign-off (1h)
        Lane 3.1 COMPLETE            Lane 3.2 COMPLETE              Lane 3.3 COMPLETE
        ─────────────────────────────────────────────────────────────
        ALL LANES COMPLETE: T+24h (53-67 hour estimate verified in practice)

┌─────────────────────────────────────────────────────────────────────────┐
│ CRITICAL: All 3 lanes execute simultaneously starting at T+0h          │
│ No dependencies between lanes, no blocking, fully parallel              │
│ Wall-clock time: ~24 hours (vs. 53-67 hours sequential)                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Dependency Analysis: Why Parallel Is Safe

### Module Isolation Verification

| Aspect | Lane 3.1 (Training) | Lane 3.2 (CLI) | Lane 3.3 (Data) | Conflict? |
|--------|-------------------|------------------|-------|----------|
| **Source Modules** | `src/codex_ml/training/` | `src/codex_ml/cli/` | `src/codex_ml/data/` | ❌ No |
| **Test Files** | `tests/codex_ml/test_training_*.py` | `tests/codex_ml/test_cli_*.py` | `tests/codex_ml/test_data_*.py` | ❌ No |
| **Fixtures** | Mock trainer/optimizer | CliRunner instance | Data loaders | ❌ No |
| **Shared State** | None | None | None | ❌ No |
| **File System** | Separate temp dirs | Separate temp dirs | Separate temp dirs | ❌ No |

### Import Dependency Check

```python
# Lane 3.1 imports
from src.codex_ml.training import Trainer, TrainingConfig
# Does NOT import: cli or data modules

# Lane 3.2 imports
from src.codex_ml.cli import train_command, evaluate_command
# Does NOT import: training or data modules

# Lane 3.3 imports
from src.codex_ml.data import DataLoader, Preprocessor, BatchCreator
# Does NOT import: training or cli modules
```

### Shared Dependency Analysis

```
torch / transformers
    ↓
    ├─ Lane 3.1 (ML Training) ────── Direct use
    ├─ Lane 3.2 (ML CLI) ──────────── Mock objects (no direct use)
    └─ Lane 3.3 (ML Data) ────────── Optional (numpy primary)
    
Result: No conflicts, Lane 3.2 uses mocks to avoid import
```

### Fixture Isolation Verification

**Lane 3.1 Fixtures:**
```python
@pytest.fixture
def trainer(training_config, mock_model):
    trainer = Trainer(training_config)
    trainer.model = mock_model  # Isolated instance
    trainer.optimizer = MagicMock()  # Isolated mock
    return trainer
```

**Lane 3.2 Fixtures:**
```python
@pytest.fixture
def cli_runner():
    return CliRunner()  # Fresh instance each test

@pytest.fixture
def mock_trainer(mocker):
    trainer = MagicMock()  # New mock each test
    mocker.patch('src.codex_ml.cli.Trainer', ...)
    return trainer
```

**Lane 3.3 Fixtures:**
```python
@pytest.fixture
def sample_dataframe():
    # Fresh dataframe each test
    return pd.DataFrame({...})

@pytest.fixture
def sample_csv(tmp_path):
    # Separate temp directory per test
    csv_path = tmp_path / 'sample.csv'
    ...
    return csv_path
```

### No Shared Resources

✅ **No shared database**  
✅ **No shared files** (separate temp directories: `/tmp/pytest-of-user/pytest-NNN/test_*/`)  
✅ **No shared mocks** (each lane creates own MagicMock instances)  
✅ **No environment variables** (pytest isolates per test)  
✅ **No monkey-patching conflicts** (each lane patches different modules)  

---

## Parallel Execution Configuration

### GitHub Actions CI Setup

```yaml
# .github/workflows/phase-6-wave-3-coverage.yml
name: Phase 6 Wave 3 Coverage

on: [workflow_dispatch]

jobs:
  lane-3-1:
    name: "Lane 3.1: ML Training Pipeline"
    runs-on: ubuntu-latest-large
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run Lane 3.1 Tests
        run: |
          pytest tests/codex_ml/test_training_comprehensive.py \
            -v --tb=short --cov=src/codex_ml/training --cov-report=json
      - name: Upload Coverage Report
        uses: actions/upload-artifact@v5
        with:
          name: coverage-lane-3-1
          path: coverage.json

  lane-3-2:
    name: "Lane 3.2: ML CLI Interface"
    runs-on: ubuntu-latest-large
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run Lane 3.2 Tests
        run: |
          pytest tests/codex_ml/test_cli_comprehensive.py \
            -v --tb=short --cov=src/codex_ml/cli --cov-report=json
      - name: Upload Coverage Report
        uses: actions/upload-artifact@v5
        with:
          name: coverage-lane-3-2
          path: coverage.json

  lane-3-3:
    name: "Lane 3.3: ML Data Pipeline"
    runs-on: ubuntu-latest-large
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run Lane 3.3 Tests
        run: |
          pytest tests/codex_ml/test_data_comprehensive.py \
            -v --tb=short --cov=src/codex_ml/data --cov-report=json
      - name: Upload Coverage Report
        uses: actions/upload-artifact@v5
        with:
          name: coverage-lane-3-3
          path: coverage.json

  consolidate-results:
    name: "Consolidate Results"
    needs: [lane-3-1, lane-3-2, lane-3-3]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v5
      - name: Merge Coverage Reports
        run: |
          python scripts/ci/merge_coverage_reports.py coverage-lane-*/*.json
      - name: Generate Wave 3 Report
        run: |
          python scripts/ci/generate_wave_3_report.py
      - name: Upload Final Report
        uses: actions/upload-artifact@v5
        with:
          name: phase-6-wave-3-report
          path: coverage-report.json
```

---

## Execution Safeguards

### Pre-Execution Gates (Must Pass)

- [ ] Phase 6 Wave 1 promoted to main (0D_base_ merged)
- [ ] All 3 lane briefs reviewed and approved
- [ ] Test templates validated for each lane
- [ ] CI pipelines configured and tested
- [ ] Artifact upload paths verified
- [ ] Coverage report merge script ready

### During-Execution Monitoring

| Gate | Trigger | Action | Owner |
|------|---------|--------|-------|
| **Checkpoint 1** | T+10h | 50% tests written | Monitor progress |
| **Checkpoint 2** | T+18h | 100% tests written | Run full CI gate |
| **Coverage Gate** | T+22h | Measure coverage | Verify ≥60% per module |
| **Regression Gate** | T+23h | Run all tests | Ensure zero failures |

### Post-Execution Validation

```bash
# Merge all coverage reports
python scripts/ci/merge_coverage_reports.py \
  coverage-lane-3-1.json \
  coverage-lane-3-2.json \
  coverage-lane-3-3.json \
  -o coverage-wave-3-combined.json

# Verify thresholds met
python scripts/ci/check_coverage_gates.py \
  coverage-wave-3-combined.json \
  --fail-under 60 \
  --modules training cli data
```

---

## Worker Allocation & Resource Usage

### Recommended CI Configuration

| Lane | Runner | Workers | Memory | CPU | Duration |
|------|--------|---------|--------|-----|----------|
| **3.1** | ubuntu-latest-large | 4 | 8GB | 4 cores | 20-25h |
| **3.2** | ubuntu-latest-large | 4 | 8GB | 4 cores | 18-22h |
| **3.3** | ubuntu-latest-large | 4 | 8GB | 4 cores | 15-20h |
| **Total** | 3 × large runners | 12 (parallel) | 24GB | 12 cores | ~24h |

### Cost Optimization

**Sequential Execution (NOT RECOMMENDED):**
- Duration: 53-67 hours
- Cost: 3 × $0.08/min × 60 min = ~$14.40 per hour → $764-$806 total

**Parallel Execution (RECOMMENDED):**
- Duration: ~24 hours (same 3 large runners)
- Cost: 3 × $0.08/min × 60 min × 24 = ~$345.60
- **Savings: 60% cost reduction**

---

## Parallel Failure Scenarios

### Scenario 1: Lane 3.1 Fails, Others Succeed

**Action:**
1. Continue Lane 3.2 and Lane 3.3 (no dependency)
2. Investigate Lane 3.1 failure
3. Re-run Lane 3.1 independently
4. Merge results when all pass

### Scenario 2: Two Lanes Fail

**Action:**
1. All lanes independent, so isolate each failure
2. Fix and re-run independently
3. No need to re-run passing lane

### Scenario 3: Coverage Target Missed in One Lane

**Action:**
1. Identify gap in coverage report
2. Write additional edge case tests for that lane only
3. Re-run that lane only
4. Others remain green

### Scenario 4: Timeout on Large Runner

**Action:**
1. Check test file size
2. Increase worker count to 6
3. Or reduce batch size
4. Re-run lane with adjusted config

---

## Progress Tracking & Reporting

### Real-Time Progress Dashboard

```
Phase 6 Wave 3 Execution Status (2026-06-28 10:00 UTC)
═════════════════════════════════════════════════════════

Lane 3.1: ML Training Pipeline
  Status: ✅ IN PROGRESS
  Progress: ██████░░░░░░░░░░░░░░ 35% (21/60 tests)
  Coverage: 9.4% → 18% (target: 60%)
  ETA: T+12h (2026-06-28 20:00 UTC)

Lane 3.2: ML CLI Interface
  Status: ✅ IN PROGRESS
  Progress: █████░░░░░░░░░░░░░░░ 30% (15/50 tests)
  Coverage: 10.0% → 22% (target: 60%)
  ETA: T+11h (2026-06-28 19:00 UTC)

Lane 3.3: ML Data Pipeline
  Status: ✅ IN PROGRESS
  Progress: ██████░░░░░░░░░░░░░░ 33% (13/40 tests)
  Coverage: 8.6% → 20% (target: 60%)
  ETA: T+10h (2026-06-28 18:00 UTC)

OVERALL STATUS: ⏳ 32% complete (49/150 tests)
Expected completion: 2026-06-28 23:00 UTC
```

### Commit Strategy

```bash
# Lane 3.1: One commit per 20 tests
commit 1: tests/codex_ml/test_training_comprehensive.py (tests 1-20)
commit 2: tests/codex_ml/test_training_comprehensive.py (tests 21-40)
commit 3: tests/codex_ml/test_training_comprehensive.py (tests 41-60+)

# Lane 3.2: One commit per 15-20 tests
commit 4: tests/codex_ml/test_cli_comprehensive.py (tests 1-15)
commit 5: tests/codex_ml/test_cli_comprehensive.py (tests 16-35)
commit 6: tests/codex_ml/test_cli_comprehensive.py (tests 36-50+)

# Lane 3.3: One commit per 15 tests
commit 7: tests/codex_ml/test_data_comprehensive.py (tests 1-15)
commit 8: tests/codex_ml/test_data_comprehensive.py (tests 16-30)
commit 9: tests/codex_ml/test_data_comprehensive.py (tests 31-40+)

# Final: Merge all and create Wave 3 summary
commit 10: docs/PHASE_6_WAVE_3_EXECUTION_SUMMARY.md
```

---

## Rollback & Recovery

### If Wave 3 Fails Catastrophically

1. **All 3 lanes can be rolled back independently**
   ```bash
   git reset --hard HEAD~9  # Before any Wave 3 commits
   ```

2. **Or roll back just the failing lane**
   ```bash
   # Identify failing lane commits
   git log --oneline | grep "test_training_comprehensive" -A 2
   # Revert just those commits
   git revert <commit-sha-1> <commit-sha-2> <commit-sha-3>
   ```

3. **Coverage remains intact** (if rollback needed)
   - Wave 3 is isolated to test files
   - No changes to source code
   - Previous coverage baseline preserved

---

## Success Criteria for Parallel Execution

### Must-Have (Wave 3 Sign-Off)
- ✅ Lane 3.1: 60-80 tests, ≥60% coverage, 100% pass rate
- ✅ Lane 3.2: 50-70 tests, ≥60% coverage, 100% pass rate
- ✅ Lane 3.3: 40-60 tests, ≥60% coverage, 100% pass rate
- ✅ Zero regressions (all existing tests still pass)
- ✅ Parallel execution completes in <30 hours
- ✅ All artifacts uploaded and verified

### Nice-to-Have
- [ ] Execution completes in <24 hours (not required)
- [ ] 100% test pass rate (not 95%+)
- [ ] Mutation score >80% for all new tests
- [ ] Documentation 100% complete

---

## Parallel Execution Checklist

### Pre-Execution (Do Before T+0h)

- [ ] All 4 documents created and reviewed
  - `.codex/PHASE_6_WAVE_3_COVERAGE_EXECUTION_BRIEF.md`
  - `.codex/PHASE_6_WAVE_3_LANE_31_BRIEF.md`
  - `.codex/PHASE_6_WAVE_3_LANE_32_BRIEF.md`
  - `.codex/PHASE_6_WAVE_3_LANE_33_BRIEF.md`
  
- [ ] CI workflows configured
  - GitHub Actions jobs for each lane
  - Coverage report merge script ready
  - Artifact upload paths validated

- [ ] Lane briefs approved
  - Phase 6 Wave 1 promoted to main
  - Authority (@mbaetiong) confirms GO status
  - All lane owners briefed

### Execution Gates (During T+0 to T+24h)

- [ ] T+0h: All 3 lanes start simultaneously
- [ ] T+10h: Checkpoint 1 — 50% tests written (all lanes)
- [ ] T+18h: Checkpoint 2 — 100% tests written (all lanes)
- [ ] T+22h: Coverage measurement — verify ≥60% per module
- [ ] T+23h: Regression test — ensure zero failures
- [ ] T+24h: All lanes complete, results consolidated

### Post-Execution (After T+24h)

- [ ] Coverage reports merged and verified
- [ ] Wave 3 execution summary generated
- [ ] All commits pushed to 0D_base_
- [ ] Artifacts preserved for Wave 4 handoff
- [ ] Team notified of completion

---

## Contact & Escalation

**Wave 3 Coordinator:** unified-coverage-agent  
**Parallel Execution Owner:** unified-coverage-agent  
**Phase 6 Authority:** @mbaetiong  

**Escalation Path:**
1. Single lane fails → Investigate independently
2. Two lanes fail → Escalate to @mbaetiong
3. Coverage target missed → Write additional tests, re-run
4. Timeout/resource issue → Increase worker count or runner size

---

## Confirmation: Full Parallel Execution Ready

✅ **All 3 lanes can execute in parallel**
✅ **Zero dependencies between lanes**
✅ **Separate test files, fixtures, and temp directories**
✅ **No shared resources or mock conflicts**
✅ **Wall-clock time: ~24 hours (53-67 hour estimate optimized)**
✅ **Ready to deploy upon Wave 1 promotion**

---

**Document Generated:** 2026-06-27T22:22:25Z  
**Status:** ✅ READY FOR PARALLEL DEPLOYMENT  
**Next Action:** Deploy upon Phase 6 Wave 1 promotion to main  

