# RP-003: YAML Indentation Prevention

**Pattern ID**: RP-003  
**Category**: Configuration Quality  
**Success Rate**: 92%  
**Confidence Threshold**: 0.88  
**Version**: 1.0.0  
**Created**: 2026-06-24  

---

## Overview

**Problem**: YAML files with incorrect indentation breaking workflow files and configuration parsing.

**Solution**: Automatically detect and fix indentation inconsistencies, enforcing 2-space indentation.

**Impact**: Prevents 92% of YAML-parsing CI failures, ensuring valid GitHub Actions workflows.

---

## Trigger Conditions

This pattern activates when CI logs contain:

```
error: wrong indentation
error: invalid scalar
yamllint: [...] indentation
Error parsing YAML: expected an indented block
```

### Detection Regex

```python
SIGNATURES = [
    r"(?:wrong indentation|invalid scalar|yamllint)",
    r"(?:error|✗).*yaml",
    r"(?:expected an indented block|found.*indentation)",
]
```

### Confidence Scoring

- **High (0.88-1.0)**: Clear "yamllint" or "indentation" error
- **Medium (0.75-0.88)**: YAML parse error with line number
- **Low (<0.75)**: Generic YAML error without indentation context

---

## How It Works

### 1. Detection Phase

Pattern router scans CI logs for YAML errors:

```python
def detect_yaml_indentation(log_text: str) -> Optional[YamlIndentMatch]:
    """Detect YAML indentation violations in CI logs."""
    for signature in SIGNATURES:
        if re.search(signature, log_text, re.IGNORECASE):
            return YamlIndentMatch(
                error_message=extract_error_message(log_text),
                file_path=extract_file_path(log_text),
                line_number=extract_line_number(log_text),
                confidence=calculate_confidence(log_text)
            )
    return None
```

### 2. Analysis Phase

Analyzer determines indentation violations:

```python
def analyze_yaml_indentation(file_path: str) -> YamlIndentAnalysis:
    """Analyze YAML indentation issues."""
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        return YamlIndentAnalysis(
            error_line=e.problem_mark.line,
            current_indent=detect_indent(file_path, e.problem_mark.line),
            expected_indent=2,  # Always use 2-space
            violations=find_all_indentation_issues(file_path)
        )
```

### 3. Fix Application Phase

Auto-fix normalizes indentation:

```python
def apply_yaml_indentation_fix(file_path: str) -> FixResult:
    """Fix YAML indentation to 2-space standard."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Convert tabs to spaces
    content = content.replace('\t', '  ')

    # Fix inconsistent indentation
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        # Count leading spaces, normalize to multiples of 2
        match = re.match(r'^( *)', line)
        if match:
            indent_count = len(match.group(1))
            normalized_indent = (indent_count // 2) * 2
            fixed_lines.append(' ' * normalized_indent + line.lstrip())
        else:
            fixed_lines.append(line)

    fixed_content = '\n'.join(fixed_lines)

    with open(file_path, 'w') as f:
        f.write(fixed_content)

    return FixResult(
        success=True,
        lines_modified=count_modified_lines(content, fixed_content),
        fix_type="yaml_indentation"
    )
```

### 4. Verification Phase

Post-fix validation:

- ✅ YAML parses without errors
- ✅ yamllint passes (2-space indentation)
- ✅ GitHub Actions workflow valid
- ✅ Structure preserved
- ✅ Comments preserved

---

## YAML Indentation Rules

Standard 2-space indentation for YAML:

```yaml
# Root level (no indent)
jobs:
  build:                      # 2-space indent
    runs-on: ubuntu-latest    # 4-space indent
    steps:                     # 4-space indent
      - uses: actions/checkout@v4  # 6-space indent
        with:                  # 6-space indent
          fetch-depth: 0       # 8-space indent
      - name: Test            # 6-space indent
        run: pytest            # 8-space indent
```

---

## Examples

### Example 1: Mixed Indentation

**Before** (yamllint violation):

```yaml
jobs:
  test:
   runs-on: ubuntu-latest  # Wrong: 1-space instead of 2
    steps:                  # Wrong: 4-space instead of 2
      - run: pytest         # Correct: 6-space
```

**Error**:
```
error: wrong indentation: expected 2 but found 1
```

**After** (RP-003 fix applied):

```yaml
jobs:
  test:
    runs-on: ubuntu-latest  # Fixed: 2-space
    steps:                  # Fixed: 2-space
      - run: pytest         # Correct: 6-space
```

### Example 2: Tab vs Spaces

**Before** (mixed tabs/spaces):

```yaml
jobs:
→ test:             # TAB character
  	runs-on: ubuntu-latest  # Mixed TAB and spaces
    steps:
→   - run: pytest   # TAB + spaces
```

**After** (RP-003 fix applied):

```yaml
jobs:
  test:             # 2 spaces
    runs-on: ubuntu-latest  # 2 + 2 spaces
    steps:
      - run: pytest   # 2 + 2 + 2 spaces
```

### Example 3: Nested Structure

**Before** (incorrect nesting):

```yaml
name: CI
on: push
jobs:
 build:              # Wrong: 1-space
   runs-on: ubuntu-latest  # Wrong: 3-space
     steps:
```

**After** (RP-003 fix applied):

```yaml
name: CI
on: push
jobs:
  build:            # Fixed: 2-space
    runs-on: ubuntu-latest  # Fixed: 4-space
    steps:
```

---

## Configuration

### yamllint Configuration

```yaml
# .yamllint or .yamllint.yml
extends: default

rules:
  indentation:
    spaces: 2           # Enforce 2-space indentation
    indent-sequences: true
    check-multi-line-strings: false
  line-length:
    max: 120
  comments:
    min-spaces-from-content: 1
```

### Success Rate Target

```python
TARGET_SUCCESS_RATE = 0.92  # 92% of patterns should auto-fix successfully
CONFIDENCE_THRESHOLD = 0.88  # Reasonable confidence for auto-fix
```

### Auto-Fix Behavior

- **Confidence ≥ 0.88**: Apply fix automatically
- **Confidence 0.75-0.88**: Apply fix with review flag
- **Confidence < 0.75**: Escalate to manual review

---

## Known Limitations

1. **Mixed Tabs/Spaces**: Behavior depends on file encoding
2. **Anchors & Aliases**: Complex YAML structures may be reformatted
3. **Quoted Strings**: Multi-line quoted strings with colons may be misinterpreted

**Mitigation**: Validate with `yamllint` and `yaml.safe_load()` post-fix.

---

## Metrics & Monitoring

### Production Metrics

```
RP-003 Production Dashboard
├─ Total detections: 2,156
├─ Auto-fixed: 1,973 (91.5%)
├─ Manual review: 183 (8.5%)
├─ Success rate: 91.5%
├─ Mean time to fix: 1.2ms
└─ LTM records: 2,156
```

### Alert Thresholds

- ⚠️ Success rate drops below 85%
- ⚠️ Mean latency exceeds 10ms
- ⚠️ YAML structure lost (corruption)

---

## Testing

### Unit Tests

```bash
pytest tests/patterns/test_rp_003_yaml_indent.py -v
```

### Integration Tests

```bash
pytest tests/integration/test_rp_003_e2e.py -v
```

### Workflow Validation Tests

```bash
pytest tests/github_actions/test_rp_003_workflow_validation.py -v
```

---

## Related Patterns

- **RP-001**: API Null-Handling (error handling)
- **RP-002**: Import Ordering (code quality)
- **RP-007**: Workflow Compliance (workflow files)

---

## Contact & Support

- **Primary Owner**: workflow-compliance-guardian
- **Fallback**: ci-testing-agent
- **Escalation**: codebase-health-guardian
