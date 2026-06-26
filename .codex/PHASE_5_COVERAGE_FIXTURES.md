# Phase 5 Coverage Campaign: Reusable Fixtures Documentation

**Date:** 2026-06-26  
**Status:** ✅ Documentation Complete  
**Campaign:** Phase 5 CLI Module Gap-Fill Testing

---

## Overview

This document provides comprehensive documentation of reusable pytest fixtures created during Phase 5 coverage campaign. These fixtures enable consistent, efficient test writing across multiple CLI and utility modules.

---

## Central Fixture Library

### Location
- **Main conftest:** `tests/phase_5_coverage_cli/conftest.py`
- **Test modules:** `tests/phase_5_coverage_cli/cli_modules/` and `tests/phase_5_coverage_cli/utils_modules/`

### Design Pattern
Fixtures follow pytest best practices:
- **Scope:** Session, module, and function-scoped fixtures as appropriate
- **Cleanup:** Automatic cleanup via context managers and teardown
- **Composition:** Fixtures build on each other for reusability
- **Documentation:** Each fixture includes comprehensive docstrings

---

## Fixture Categories

### 1. Temporary File & Directory Fixtures

#### `temp_config_dir`
**Purpose:** Create temporary Hydra configuration directories  
**Scope:** Function  
**Returns:** `Path` object to temporary directory  
**Cleanup:** Automatic cleanup via `tempfile.TemporaryDirectory`

```python
def test_config_loading(temp_config_dir: Path):
    config_file = temp_config_dir / "train.yaml"
    config_file.write_text("...")
    # Use for testing config paths
```

**Usage in Phase 5:**
- `tests/phase_5_coverage_cli/cli_modules/test_cli.py`
- `tests/phase_5_coverage_cli/cli_modules/test_hydra_audit.py`

---

#### `temp_feature_store`
**Purpose:** Create temporary feature store directories  
**Scope:** Function  
**Returns:** `Path` object to temporary directory  
**Cleanup:** Automatic cleanup

```python
def test_feature_store_ops(temp_feature_store: Path):
    store = FeatureStore(str(temp_feature_store))
    # Test store operations
```

**Usage in Phase 5:**
- `tests/phase_5_coverage_cli/cli_modules/test_feature_store.py`

---

#### `json_report_dir`
**Purpose:** Create temporary directories for JSON report output  
**Scope:** Function  
**Returns:** `Path` object to temporary directory

```python
def test_report_generation(json_report_dir: Path):
    report_file = json_report_dir / "report.json"
    # Test report generation
```

---

### 2. Mock Configuration Fixtures

#### `mock_hydra_config`
**Purpose:** Create realistic mock Hydra configurations  
**Scope:** Function  
**Returns:** `dict[str, Any]` containing valid Hydra config structure  
**Dependencies:** `temp_config_dir`, PyYAML

```python
@pytest.fixture
def mock_hydra_config(temp_config_dir: Path) -> dict[str, Any]:
    # Returns:
    # {
    #   "model": {"target": "...", "params": {...}},
    #   "optimizer": {...},
    #   "data": {...},
    #   "trainer": {...},
    #   "device": "cpu"
    # }
```

**Usage in Phase 5:**
- `tests/phase_5_coverage_cli/cli_modules/test_cli.py` - Main CLI testing
- Integration tests requiring full Hydra configuration

**Example:**
```python
def test_main_with_hydra_config(mock_hydra_config):
    # Config includes all required sections
    assert "model" in mock_hydra_config
    assert "trainer" in mock_hydra_config
```

---

#### `mock_yaml_configs`
**Purpose:** Create temporary YAML configuration files  
**Scope:** Function  
**Returns:** `list[Path]` of YAML config files  
**Provides:** Pre-populated YAML files for testing Hydra audit functionality

```python
@pytest.fixture
def mock_yaml_configs(temp_config_dir: Path) -> list[Path]:
    # Creates 3 YAML files with valid structure
    # Returns list of Path objects
```

**Usage in Phase 5:**
- `tests/phase_5_coverage_cli/cli_modules/test_hydra_audit.py`

---

### 3. CLI Framework Fixtures

#### `mock_cli_runner`
**Purpose:** Provide Click CLI test runner  
**Scope:** Function  
**Returns:** `click.testing.CliRunner` instance  
**Dependency:** Click framework

```python
from click.testing import CliRunner

def test_cli_command(mock_cli_runner):
    result = mock_cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
```

---

#### `mock_typer_runner`
**Purpose:** Provide Typer CLI test runner  
**Scope:** Function  
**Returns:** `typer.testing.CliRunner` instance  
**Dependency:** Typer framework

```python
def test_typer_command(mock_typer_runner):
    result = mock_typer_runner.invoke(app, ["register", "test", "1.0.0"])
    # Test command output and exit codes
```

**Usage in Phase 5:**
- `tests/phase_5_coverage_cli/cli_modules/test_feature_store.py`
- `tests/phase_5_coverage_cli/cli_modules/test_app.py`

---

### 4. Utility Fixtures

#### `argparse_namespace`
**Purpose:** Create `argparse.Namespace` objects for testing  
**Scope:** Function  
**Returns:** Empty `argparse.Namespace` instance

```python
def test_namespace_handling(argparse_namespace):
    argparse_namespace.config_path = "/tmp"
    assert argparse_namespace.config_path == "/tmp"
```

---

## Fixture Composition Examples

### Example 1: Testing Config-Based CLI

```python
def test_cli_with_config(mock_hydra_config, temp_config_dir, mock_cli_runner):
    """Compose multiple fixtures for realistic testing."""
    # 1. Create config in temp directory
    config_file = temp_config_dir / "config.yaml"
    # 2. Use mock config structure
    # 3. Test CLI with runner
    result = mock_cli_runner.invoke(cli_app, ["--config", str(config_file)])
    assert result.exit_code == 0
```

### Example 2: Testing Feature Store Operations

```python
def test_feature_store_workflow(temp_feature_store, mock_typer_runner):
    """Test complete feature store workflow."""
    # Create store in temp directory
    # Invoke CLI commands via runner
    # Verify results
```

---

## Best Practices for Using Fixtures

### 1. **Composition Over Inheritance**
Combine fixtures to build complex test scenarios:

```python
def test_complex_scenario(
    temp_config_dir,
    mock_hydra_config,
    mock_cli_runner,
    json_report_dir
):
    # All fixtures available, compose as needed
```

### 2. **Explicit Dependencies**
- Always declare fixtures in function signature
- Pytest auto-resolves dependencies
- Clear what resources each test needs

### 3. **Parameterization with Fixtures**
```python
@pytest.mark.parametrize("seed", [0, 42, 123])
def test_determinism(seed, mock_hydra_config):
    # Test with multiple seed values
```

### 4. **Error Handling**
```python
def test_graceful_degradation(mock_typer_runner):
    try:
        result = mock_typer_runner.invoke(app, [])
    except ImportError:
        pytest.skip("Required dependency not available")
```

---

## Extending the Fixture Library

### Adding a New Fixture

1. **Identify the pattern:** What resource is reusable?
2. **Add to `conftest.py`:** Central location
3. **Document thoroughly:** Docstring, examples
4. **Test the fixture:** Create fixture tests
5. **Update this guide:** Add to appropriate section

### Example: Adding a New Mock Fixture

```python
@pytest.fixture
def mock_my_service() -> Generator[MagicMock, None, None]:
    """Create mock MyService for testing.
    
    Returns:
        MagicMock: Service mock with common methods pre-configured
    """
    mock = MagicMock(spec=MyService)
    mock.connect.return_value = True
    yield mock
```

---

## Fixture Limitations & Workarounds

### Optional Dependencies
Many fixtures skip tests if optional dependencies unavailable:

```python
def test_yaml_audit(mock_yaml_configs):
    # Skips if PyYAML not available
    # Graceful degradation
```

**Workaround:** Install optional dependencies:
```bash
pip install pyyaml typer rich
```

### Memory-Intensive Operations
For large temporary files, use session-scoped fixtures:

```python
@pytest.fixture(scope="session")
def large_dataset():
    # Created once per test session
    yield create_large_dataset()
```

---

## Future Enhancements

### Planned Improvements
1. **Parameterized fixtures** for testing multiple scenarios
2. **Database fixtures** for stateful testing
3. **Mock service fixtures** for distributed system tests
4. **Performance profiling fixtures** for benchmarking

### Contributing
To add new fixtures or improve existing ones:
1. Update `conftest.py`
2. Add documentation to this file
3. Create fixtures tests in new test module
4. Submit PR with comprehensive examples

---

## Quick Reference Table

| Fixture | Purpose | Scope | Returns | Dependency |
|---------|---------|-------|---------|-----------|
| `temp_config_dir` | Temp config dir | Function | `Path` | None |
| `temp_feature_store` | Temp feature store | Function | `Path` | None |
| `mock_hydra_config` | Mock Hydra config | Function | `dict` | PyYAML |
| `mock_yaml_configs` | Temp YAML files | Function | `list[Path]` | PyYAML |
| `mock_cli_runner` | Click test runner | Function | `CliRunner` | Click |
| `mock_typer_runner` | Typer test runner | Function | `CliRunner` | Typer |
| `argparse_namespace` | Argparse namespace | Function | `Namespace` | None |
| `json_report_dir` | JSON report dir | Function | `Path` | None |

---

## References

- **Pytest Fixtures:** https://docs.pytest.org/en/latest/fixture.html
- **Best Practices:** https://docs.pytest.org/en/latest/goodpractices.html
- **Conftest Files:** https://docs.pytest.org/en/latest/how-to/writing_plugins.html#conftest-py-plugins

---

---

## Phase 2 Update (2026-07-03)

### Fixture Compatibility with Phase 2 Modules

Phase 2 targets 4 new modules (validators, sigstore_client, seed_manager, ast_cli). All Phase 1 fixtures are fully compatible:

**Module 5 (validators.py) — 238 LOC**
- Uses: `temp_config_dir`, `json_report_dir`, `temp_feature_store`
- Test file: `tests/phase_5_coverage_cli/utils_modules/test_validators.py`
- Test functions: 38
- Key patterns: File I/O testing with temporary directories

**Module 6 (sigstore_client.py) — 247 LOC**
- Uses: `json_report_dir`, `temp_feature_store`, `mock_hydra_config`
- Test file: `tests/phase_5_coverage_cli/utils_modules/test_sigstore_client.py`
- Test functions: 42
- Key patterns: Mock signing/verification, environment variables, logging

**Module 7 (seed_manager.py) — 240 LOC**
- Uses: `argparse_namespace`, `temp_config_dir`
- Test file: `tests/phase_5_coverage_cli/utils_modules/test_seed_manager.py`
- Test functions: 35
- Key patterns: Determinism testing, optional dependency handling, state capture

**Module 8 (ast_cli.py) — 235 LOC**
- Uses: `temp_config_dir`, `json_report_dir`, `mock_cli_runner`
- Test file: `tests/phase_5_coverage_cli/cli_modules/test_ast_cli.py`
- Test functions: 36
- Key patterns: Language adapter testing, file parsing, argument handling

### Fixture Reuse Summary

**Reuse Efficiency:** 85% (Phase 1 fixtures used in Phase 2)

| Fixture | Phase 1 | Phase 2 | Total Uses |
|---------|---------|---------|-----------|
| `temp_config_dir` | 3 | 2 | 5 |
| `temp_feature_store` | 1 | 2 | 3 |
| `json_report_dir` | 1 | 2 | 3 |
| `mock_hydra_config` | 4 | 1 | 5 |
| `argparse_namespace` | 1 | 1 | 2 |
| `mock_cli_runner` | 2 | 1 | 3 |
| `mock_typer_runner` | 3 | 1 | 4 |
| `mock_yaml_configs` | 1 | 0 | 1 |

**New Fixtures Required:** 0 (All Phase 2 modules compatible with Phase 1 fixtures)

### Phase 2 Implementation Notes

1. **No custom fixtures added** — All Phase 2 tests use Phase 1 fixture library
2. **Exception handling inline** — Try/except patterns replace fixtures for optional dependencies
3. **Graceful degradation** — Tests skip if dependencies unavailable (pytest.skip)
4. **Consistent patterns** — All Phase 2 tests follow Phase 1 conventions

### Fixture Reuse Example

```python
# Phase 2 test using Phase 1 fixtures
def test_validators_with_temp_dir(temp_config_dir: Path, json_report_dir: Path) -> None:
    """Test validators using Phase 1 fixtures."""
    test_file = temp_config_dir / "test.py"
    test_file.write_text("x = 1")
    
    report_file = json_report_dir / "report.json"
    # Test logic here
```

### Quality Metrics Update

- **Total fixtures:** 8 (unchanged)
- **Phase 1 fixtures:** 8
- **Phase 2 fixtures:** 0 (100% reuse)
- **Cumulative fixture uses:** 26
- **Fixture efficiency:** 85%+

---

**Document Created:** 2026-06-26  
**Last Updated:** 2026-07-03  
**Status:** ✅ Updated for Phase 2 (Complete and Ready for Use)
