# Docs: OmegaConf Schema Guard — Offline Validation

> Generated: 2025-11-05 | Author: mbaetiong

## Overview

The config schema guard provides best-effort validation of Hydra/OmegaConf configurations to catch common shape and type errors early without requiring network access.

## Features

- **Offline-first**: No network calls required
- **Non-blocking**: Always exits 0 to avoid breaking workflows
- **Extensible**: Easy to add more validation checks
- **Format-agnostic**: Supports YAML and JSON configs

## Usage

### Basic Validation

```bash
python tools/configs/schema_guard.py --path configs/train/example.yaml
```text

### Via Nox

```bash
nox -s config_schema
```text

## Output Format

The tool outputs a JSON report:

```json
{
  "path": "configs/train/example.yaml",
  "valid": true,
  "issues": []
}
```text

Or with issues:

```json
{
  "path": "configs/train/example.yaml",
  "valid": false,
  "issues": [
    {
      "path": "training.seed",
      "issue": "Expected int or null, got str"
    }
  ]
}
```text

## Validation Checks

### Root Structure

- Verifies config is a mapping (dict)

### Training Configuration

- `training.seed`: Must be `int` or `null`

### Evaluation Configuration

- `evaluation.metrics`: Must be a list

## Extending Validation

Add more checks by extending the `_validate()` function in `tools/configs/schema_guard.py`:

```python
def _validate(config: dict[str, Any]) -> list[dict[str, str]]:
    issues = []
    
    # Add your custom checks here
    if "model" in config:
        model = config["model"]
        if isinstance(model, dict) and "name" in model:
            if not isinstance(model["name"], str):
                issues.append({
                    "path": "model.name",
                    "issue": f"Expected str, got {type(model['name']).__name__}"
                })
    
    return issues
```text

## Integration

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: config-schema
      name: Validate config schemas
      entry: python tools/configs/schema_guard.py
      language: system
      files: '^configs/.*\.(yaml|yml|json)$'
      pass_filenames: true
```text

### CI/CD

```yaml
- name: Validate configs
  run: |
    for cfg in configs/**/*.yaml; do
      python tools/configs/schema_guard.py --path "$cfg"
    done
```text

## Troubleshooting

### OmegaConf Not Available

**Issue**: Tool falls back to YAML/JSON parsing

**Solution**: Install OmegaConf for better validation:
```bash
pip install omegaconf>=2.3
```text

### YAML Parse Errors

**Issue**: Invalid YAML syntax

**Solution**: Use a YAML linter first:
```bash
yamllint configs/train/example.yaml
```text

### False Positives

**Issue**: Valid config reported as invalid

**Solution**: The guard is best-effort. Review the specific check and adjust if needed.

## Best Practices

1. **Run Early**: Validate configs before training/evaluation
2. **Extend Gradually**: Add checks as conventions evolve
3. **Keep Non-Blocking**: Always exit 0 to avoid breaking workflows
4. **Document Conventions**: Update this guide when adding new checks

## See Also

- [Hydra Documentation](https://hydra.cc/)
- [OmegaConf Documentation](https://omegaconf.readthedocs.io/)
- [Config Groups Discovery](https://github.com/Aries-Serpent/_codex_/blob/main/configs/list_groups.py)
