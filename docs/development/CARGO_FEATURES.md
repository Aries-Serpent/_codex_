# Cargo Features Documentation

**Last Updated:** 2026-06-22

## Overview

This document explains the feature system in `Cargo.toml` for the Rust-Python hybrid swarm engine. Understanding these features is critical to prevent CI failures like the January 19, 2026 incident where 10 workflows failed due to missing feature declarations.

## Feature Declarations

### Location
All features are declared in `Cargo.toml` under the `[features]` section (line 79+).

```toml
[features]
default = []
python = ["extension-module"]
extension-module = ["pyo3/extension-module"]
```

## Feature Definitions

### 1. `default` Feature
- **Purpose**: Features enabled by default when building without explicit flags
- **Current State**: Empty (`[]`)
- **Rationale**: Allows both Rust-only builds and Python extension builds

### 2. `python` Feature
- **Purpose**: Convenience alias for Python bindings
- **Dependencies**: Enables `extension-module` feature
- **Usage**: Automatically enabled by `maturin` during Python extension builds
- **Source Code**: Used in `src/lib.rs` lines 47, 51

```rust
#[cfg(feature = "python")]
use pyo3::prelude::*;

#[cfg(feature = "python")]
#[pymodule]
fn codex_swarm(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Python module definition
}
```

### 3. `extension-module` Feature
- **Purpose**: Controls PyO3 extension module linking
- **Dependencies**: Enables `pyo3/extension-module`
- **Critical**: Required for Python extensions that don't link libpython
- **Build Tool**: Added automatically by `maturin` (NOT by `cargo build`)

## Build Scenarios

### Scenario 1: Rust-Only Testing
```bash
cargo test --lib
# Features: default only
# Result: Compiles without Python bindings
```

### Scenario 2: Full Feature Testing (CI)
```bash
cargo clippy --all-features
# Features: default, python, extension-module
# Result: Validates all code paths including Python bindings
```

### Scenario 3: Python Extension Build
```bash
maturin build --release
# Features: default, extension-module (auto-added)
# Result: Creates Python .so/.pyd file
```

### Scenario 4: Development Python Extension
```bash
maturin develop
# Features: default, extension-module (auto-added)
# Result: Installs extension in current Python environment
```

## Common Pitfalls

### ❌ Pitfall 1: Using `cargo build` for Python Extensions
**Problem**: `cargo build` does NOT add `extension-module` feature automatically.

```bash
# WRONG - Does not create proper Python extension
cargo build --features python

# CORRECT - Use maturin
maturin build --features python
```

### ❌ Pitfall 2: Missing Feature Declaration
**Problem**: Code uses `#[cfg(feature = "xyz")]` but `xyz` not in Cargo.toml.

**Symptoms**:
```
error: unexpected `cfg` condition value: `xyz`
```

**Solution**: Always declare features in `[features]` section before using them.

### ❌ Pitfall 3: Dependabot Regression
**Problem**: Dependabot PRs can accidentally remove or modify feature declarations.

**Prevention**:
1. CI validation script (`scripts/ci/validate_cargo_features.py`)
2. Protected feature declarations in `.github/dependabot.yml`
3. Manual review of all Dependabot merges

### ❌ Pitfall 4: Rust Version Upgrades
**Problem**: Newer Rust versions (1.92.0+) have stricter `cfg` validation.

**Solution**: Always test with `--all-features` in CI:
```bash
cargo clippy --all-features --locked -- -D warnings
```

## Validation

### Automated Validation
The repository includes `scripts/ci/validate_cargo_features.py` that checks:

1. ✅ `[features]` section exists
2. ✅ Required features (`python`, `extension-module`) declared
3. ✅ Features match usage in `src/lib.rs`
4. ✅ Proper dependency chain (`python` → `extension-module` → `pyo3/extension-module`)

Run manually:
```bash
python scripts/ci/validate_cargo_features.py
```

Run in CI:
- Integrated into `.github/workflows/rust_swarm_ci.yml`
- Runs before clippy and tests
- Blocks CI if features misconfigured

### Manual Validation
```bash
# Check features are recognized
cargo build --all-features --verbose

# Verify no unexpected cfg warnings
cargo clippy --all-features -- -D warnings

# Test Python extension builds
maturin build --release
```

## Historical Context

### January 19, 2026 Incident
- **Root Cause**: `python` feature missing from Cargo.toml
- **Impact**: 10 CI workflow failures
- **Trigger**: Dependabot merge PR #2890 regressed previous fix
- **Resolution**: Manual intervention + feature declaration restored
- **Prevention**: This documentation + validation script

See: `.codex/incident_reports/ci_failure_batch_2026_01_19.md`

## Best Practices

### For Developers
1. ✅ Always run `cargo clippy --all-features` before committing Cargo.toml changes
2. ✅ Test both Rust-only and Python extension builds locally
3. ✅ Review Dependabot PRs carefully for Cargo.toml modifications
4. ✅ Run validation script after any feature changes

### For CI/CD
1. ✅ Validate features before building (done via validation script)
2. ✅ Test with `--all-features` flag
3. ✅ Use `--locked` to ensure Cargo.lock consistency
4. ✅ Fail fast on feature validation errors

### For Dependabot
1. ✅ Review generated Cargo.toml carefully
2. ✅ Ensure [features] section unchanged
3. ✅ Run validation script on Dependabot branch before merge
4. ✅ Consider `.github/dependabot.yml` ignore patterns for feature-related files

## Troubleshooting

### Error: "unexpected `cfg` condition value"
```
error: unexpected `cfg` condition value: `python`
  --> src/lib.rs:47:7
```

**Solution**:
1. Check `Cargo.toml` has `[features]` section
2. Verify feature declared: `python = ["extension-module"]`
3. Run validation: `python scripts/ci/validate_cargo_features.py`
4. Rebuild: `cargo clean && cargo build --all-features`

### Error: Python extension won't import
```
ImportError: dynamic module does not define module export function
```

**Solution**:
1. Ensure built with `maturin`, not `cargo build`
2. Verify `extension-module` feature enabled
3. Check PyO3 version compatibility (currently 0.24.x)

### Dependabot Removed Features
**Solution**:
1. Revert the merge: `git revert <commit>`
2. Manually restore feature declarations from this document
3. Re-run validation script
4. Create new PR with fixed Cargo.toml

## References

- [PyO3 Features Documentation](https://pyo3.rs/v0.24.0/building-and-distribution)
- [Cargo Features Guide](https://doc.rust-lang.org/cargo/reference/features.html)
- [Rust Conditional Compilation](https://doc.rust-lang.org/reference/conditional-compilation.html)
- Incident Report: `.codex/incident_reports/ci_failure_batch_2026_01_19.md`
- Validation Script: `scripts/ci/validate_cargo_features.py`

## Maintenance

This document should be updated when:
- New features added to Cargo.toml
- PyO3 version upgraded
- Rust version upgraded (major version)
- New build scenarios introduced

Last updated: 2026-02-10
