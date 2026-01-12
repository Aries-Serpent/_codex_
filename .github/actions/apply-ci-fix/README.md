# Apply CI Fix Action

Automated fix application action for the CI self-healing system.

## Overview

This action applies automated fixes based on CI failure analysis results. It supports multiple fix types and integrates with the cognitive brain learning system.

## Supported Fix Types

### 1. `rust_format`
Applies Rust formatting using `cargo fmt --all`.

**Requirements**: Rust toolchain must be installed
**Confidence**: 95%
**Safe**: Yes - only formatting changes

### 2. `python_lint`
Applies Python linting fixes using `ruff check --fix`.

**Requirements**: ruff (auto-installed if missing)
**Confidence**: 85%
**Safe**: Yes - only linting fixes

### 3. `increase_timeout`
Increases test timeout values in pytest configuration.

**Requirements**: pytest.ini or pyproject.toml
**Confidence**: 70%
**Safe**: Yes - only configuration changes

**Parameters**:
```json
{
  "current_timeout": 60,
  "suggested_timeout": 120
}
```

### 4. `add_dependency`
Adds missing Python dependencies to requirements.txt.

**Requirements**: requirements.txt file
**Confidence**: 80%
**Safe**: Moderate - adds dependencies

**Parameters**:
```json
{
  "missing_module": "module_name"
}
```

### 5. `clear_cache`
Clears GitHub Actions caches.

**Requirements**: gh CLI and appropriate permissions
**Confidence**: 90%
**Safe**: Yes - only clears caches

## Usage

### In a Workflow

```yaml
- name: Apply Fix
  uses: ./.github/actions/apply-ci-fix
  with:
    fix_type: rust_format
    fix_params: '{}'
    repo_token: ${{ secrets.GITHUB_TOKEN }}
```

### With Parameters

```yaml
- name: Increase Timeout
  uses: ./.github/actions/apply-ci-fix
  with:
    fix_type: increase_timeout
    fix_params: '{"current_timeout": 60, "suggested_timeout": 120}'
```

## Outputs

- `fix_applied`: Boolean indicating if fix was successful
- `fix_details`: Human-readable description of what was done
- `commit_sha`: Git commit SHA if changes were committed

## Safety Mechanisms

1. **[skip ci]**: All commits include `[skip ci]` to prevent infinite loops
2. **Validation**: Each fix validates prerequisites before applying
3. **Error Handling**: Failures are logged but don't crash the workflow
4. **Git Config**: Commits are attributed to `github-actions[bot]`

## Integration with Self-Healing System

This action is designed to work with:
- `.github/agents/ci-testing-agent/src/analyzer.py` - Failure detection
- `.github/workflows/self-healing.yml` - Orchestration workflow
- Cognitive brain learning system - Pattern tracking

## Examples

### Example 1: Format Rust Code
```yaml
- uses: ./.github/actions/apply-ci-fix
  with:
    fix_type: rust_format
# Output: Commits formatted Rust code
```

### Example 2: Add Missing Dependency
```yaml
- uses: ./.github/actions/apply-ci-fix
  with:
    fix_type: add_dependency
    fix_params: '{"missing_module": "requests"}'
# Output: Adds requests to requirements.txt
```

## Development

To add a new fix type:

1. Add pattern to `analyzer.py`
2. Add new step in `action.yml`
3. Update this README
4. Add tests
5. Update cognitive brain patterns

## Testing

Test locally with act:
```bash
act -j test-apply-fix -s GITHUB_TOKEN=xxx
```

## Maintenance

- Review fix success rates monthly
- Update confidence scores based on outcomes
- Add new fix types as patterns emerge
- Remove/deprecate ineffective fixes
