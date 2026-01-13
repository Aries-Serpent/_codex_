# CI Failure Resolution Guide - PR #2835

## Overview
This document provides implementation steps for resolving all 4 failing CI checks identified in comment #3744362033.

## Failing Checks Summary

| Check | Issue | Priority | Fix ETA |
|-------|-------|----------|---------|
| Determinism & Audit Validation | Disk full (99MB free) | P0 | Immediate |
| Code Coverage | Artifacts not found | P1 | 30 min |
| Performance Regression Detection | No benchmark results | P1 | 30 min |
| Python Integration Tests | maturin env missing | P1 | 45 min |

---

## Fix 1: Determinism Check - Disk Space

### Root Cause
GitHub runners have limited disk space (~14GB). Build artifacts, caches, and dependencies fill disk during `pip install`.

### Solution
Add disk cleanup step before installation:

```yaml
- name: Free disk space
  run: |
    echo "=== Disk usage before cleanup ==="
    df -h
    
    # Remove unnecessary packages
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /opt/ghc
    sudo rm -rf "/usr/local/share/boost"
    sudo rm -rf "$AGENT_TOOLSDIRECTORY"
    
    # Clean apt caches
    sudo apt-get clean
    
    # Remove old Docker images
    docker rmi $(docker images -q) 2>/dev/null || true
    
    echo "=== Disk usage after cleanup ==="
    df -h
```

### Verification
```bash
df -h | grep /dev/root
# Should show > 2GB free after cleanup
```

---

## Fix 2: Code Coverage - Missing Artifacts

### Root Cause
Coverage commands not generating coverage files, or paths mismatch in upload step.

### Solution
Ensure coverage is generated and uploaded:

```yaml
- name: Generate Rust coverage
  run: |
    cargo install cargo-tarpaulin || true
    cargo tarpaulin --out Xml --output-dir ./coverage
    
- name: Generate Python coverage  
  run: |
    pytest --cov=src --cov-report=xml:coverage/python-coverage.xml
    
- name: Upload coverage artifacts
  uses: actions/upload-artifact@v4
  with:
    name: coverage-reports
    path: coverage/
    if-no-files-found: warn
```

### Verification
```bash
ls -lh coverage/
# Should show cobertura.xml, python-coverage.xml
```

---

## Fix 3: Performance Regression - No Benchmark Results

### Root Cause
`cargo bench` not run, or Criterion results not persisted.

### Solution
Run benchmarks and save results:

```yaml
- name: Run benchmarks
  run: |
    # Create target directory if needed
    mkdir -p target/criterion
    
    # Run benchmarks with Criterion
    cargo bench --bench swarm_benchmarks
    
    # Save Criterion results
    cp -r target/criterion ./criterion-results
    
- name: Upload benchmark results
  uses: actions/upload-artifact@v4
  with:
    name: benchmark-results
    path: criterion-results/
```

### Verification
```bash
ls -lh criterion-results/
# Should show benchmark JSON files
```

---

## Fix 4: Python Integration Tests - maturin Environment

### Root Cause
maturin not installed, or venv not initialized for PyO3 builds.

### Solution
Install and configure maturin properly:

```yaml
- name: Setup maturin environment
  run: |
    python -m pip install --upgrade pip
    pip install maturin setuptools wheel
    
    # Create and activate venv
    python -m venv .venv
    source .venv/bin/activate
    
    # Build Python extension with maturin
    maturin develop --release
    
- name: Run Python integration tests
  run: |
    source .venv/bin/activate
    pytest tests/integration/ -v --tb=short
```

### Verification
```bash
source .venv/bin/activate
python -c "import codex_swarm; print('✅ Extension loaded')"
```

---

## Implementation Workflow

### Step 1: Update determinism.yml

```yaml
# Add after checkout, before pip install
- name: Free disk space for CI
  run: |
    sudo rm -rf /usr/share/dotnet /opt/ghc /usr/local/share/boost "$AGENT_TOOLSDIRECTORY"
    sudo apt-get clean
    df -h
```

### Step 2: Update rust_swarm_ci.yml

```yaml
# Add coverage job
rust_coverage:
  name: Code Coverage
  runs-on: ubuntu-latest
  needs: rust_tests
  steps:
    - uses: actions/checkout@v4
    - name: Install cargo-tarpaulin
      run: cargo install cargo-tarpaulin
    - name: Generate coverage
      run: cargo tarpaulin --out Xml --output-dir ./coverage
    - name: Upload coverage
      uses: actions/upload-artifact@v4
      with:
        name: rust-coverage
        path: coverage/cobertura.xml

# Update performance job
rust_performance:
  name: Performance Regression Detection
  runs-on: ubuntu-latest
  needs: rust_tests
  steps:
    - uses: actions/checkout@v4
    - name: Run benchmarks
      run: |
        cargo bench --bench swarm_benchmarks
        mkdir -p benchmark-results
        cp -r target/criterion/* benchmark-results/
    - name: Upload results
      uses: actions/upload-artifact@v4
      with:
        name: performance-benchmarks
        path: benchmark-results/

# Add integration test job
python_integration:
  name: Python Integration Tests
  runs-on: ubuntu-latest
  needs: rust_tests
  steps:
    - uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install maturin
      run: |
        pip install maturin pytest
        maturin develop --release
    - name: Run integration tests
      run: pytest tests/integration/ -v
```

### Step 3: Validate Changes

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/rust_swarm_ci.yml'))"
python -c "import yaml; yaml.safe_load(open('.github/workflows/determinism.yml'))"

# Check workflow names
grep "name:" .github/workflows/rust_swarm_ci.yml
grep "name:" .github/workflows/determinism.yml
```

---

## Testing Strategy

### Local Testing

```bash
# Test disk cleanup
bash .github/scripts/free_disk_space.sh

# Test coverage generation
cargo tarpaulin --out Xml --output-dir ./coverage

# Test benchmarks
cargo bench --bench swarm_benchmarks

# Test maturin build
maturin develop --release
pytest tests/integration/
```

### CI Testing

1. Push changes to branch
2. Monitor workflow runs
3. Check artifact uploads
4. Verify no disk space errors

---

## Success Criteria

- [ ] Determinism check passes with > 2GB disk free
- [ ] Coverage artifacts uploaded successfully
- [ ] Benchmark results available for comparison
- [ ] Python integration tests pass with maturin
- [ ] All 4 workflows green

---

## Rollback Plan

If fixes cause issues:

1. Revert workflow changes: `git checkout HEAD~1 .github/workflows/`
2. Keep security fixes (commit 80f5816)
3. Investigate failures individually
4. Apply fixes incrementally

---

## Monitoring

After deployment, monitor:

- Disk usage trends: `df -h` in workflow logs
- Artifact sizes: GitHub Actions UI
- Benchmark performance: Criterion output
- Test coverage: Coverage reports

---

## References

- GitHub Actions disk space: https://github.com/actions/runner-images/issues/2840
- cargo-tarpaulin docs: https://github.com/xd009642/tarpaulin
- Criterion benchmarking: https://bheisler.github.io/criterion.rs/
- maturin guide: https://www.maturin.rs/

---

**Created**: 2026-01-13  
**Author**: @copilot  
**Status**: Ready for implementation  
**Priority**: P0 (Blocking CI)
