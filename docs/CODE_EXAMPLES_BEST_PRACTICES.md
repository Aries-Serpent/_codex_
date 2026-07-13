# Code Examples: Best Practices & Templates
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Phase 12 WS5 - Code Example Validation**  
**Status**: 174/348 examples validated (50% of Phase 12 target)  
**Updated**: 2026-07-08

---

## Executive Summary

This guide provides standardized templates and best practices for code examples across the _codex_ documentation. 

**Current Metrics:**
- **Total Examples**: 12,776
- **Validated (Phase 12)**: 174 (50% target achieved)
- **Success Rate**: 91/174 (52.3%)
- **Top Languages**: Bash (54), Python (38), TypeScript (20), Text (27)

---

## Example Standards

### 1. Python Examples

**Template:**
```python
# Example: <Clear descriptive title>
# Context: <What problem this solves>
# Prerequisites: <Required imports/setup>

import sys
from pathlib import Path

def example_function():
    """
    Brief description of what the function does.
    
    Returns:
        <Type>: <Description>
    
    Example:
        >>> result = example_function()
        >>> print(result)
        <expected output>
    """
    # Implementation
    return result

# Expected output:
# <Show what the example produces>
```

**Validation Checklist:**
-  All imports are included
-  Function/class is properly documented
-  Example runs without errors
-  Shows expected output
-  No external dependencies (or documented)

**Enhancements:**
1. Add docstring with usage examples
2. Include error handling if relevant
3. Show expected output as comment
4. Link to related examples

### 2. Shell/Bash Examples

**Template:**
```bash
#!/bin/bash
# Example: <Clear descriptive title>
# Context: <What this command does>
# Prerequisites: <Required tools/environment>

# Basic command example
command_name argument1 argument2

# Output:
# <Show what the command produces>

# Advanced usage with error handling
if command_name --flag; then
    echo "Success"
else
    echo "Failed"
fi
```

**Validation Checklist:**
-  Syntax is valid (parentheses balanced, etc.)
-  Common tools are widely available
-  Uses portable command syntax
-  Includes error handling
-  Shows output comments

**Enhancements:**
1. Add comments explaining each step
2. Include error handling patterns
3. Show actual command output
4. Document all flags used

### 3. YAML/Configuration Examples

**Template:**
```yaml
# Example: <Clear descriptive title>
# Context: <What this configuration does>
# File location: <Where to place this>

# Main configuration block
config:
  # Required settings
  setting1: value1
  setting2: value2
  
  # Optional settings (explained below)
  optional_setting: value3

# Configuration explanation:
# - setting1: What this does (default: <default>)
# - setting2: What this does (required)
# - optional_setting: When to use this
```

**Validation Checklist:**
-  Valid YAML syntax
-  Indentation is correct (2 or 4 spaces)
-  Comments explain each section
-  Shows all required fields
-  Marks optional fields **Enhancements:**
1. Add schema comments
2. Document required vs optional
3. Show common variations
4. Link to validation tools

### 4. TypeScript/JavaScript Examples

**Template:**
```typescript
/**
 * Example: <Clear descriptive title>
 * Context: <What problem this solves>
 * Prerequisites: <Required packages>
 */

// Import necessary types and functions
import type { SomeType } from './types';
import { someFunction } from './module';

// Example function
async function exampleFunction(): Promise<SomeType> {
  // Implementation
  const result = await someFunction();
  
  // Output:
  // { key: 'value' }
  
  return result;
}

// Usage:
// const result = await exampleFunction();
// console.log(result);
```

**Validation Checklist:**
-  Syntax is valid (no compilation errors)
-  Types are properly defined
-  Async/await is correctly used
-  Imports are valid
-  Shows expected output

**Enhancements:**
1. Include TypeScript types
2. Add JSDoc comments
3. Show error handling
4. Include actual output examples

### 5. JSON Examples

**Template:**
```json
{
  "example": "JSON with explanations as comments",
  "context": "What this JSON structure represents",
  "required_fields": [
    "field1",
    "field2"
  ],
  "optional_fields": [
    "field3"
  ],
  "nested": {
    "structure": "Can contain any valid JSON",
    "array": [1, 2, 3]
  }
}

// Schema explanation:
// - example (string, required): What this field contains
// - context (string, required): Description of purpose
// - required_fields (array): Fields that must be present
// - nested.structure (string): Nested field explanation
```

**Validation Checklist:**
-  Valid JSON syntax
-  Includes schema comments
-  Shows all field types
-  Marks required vs optional
-  Uses realistic values

**Enhancements:**
1. Add field type annotations
2. Show schema in comments
3. Provide validation rules
4. Include common variations

---

## Example Enhancement Workflow

### Step 1: Document Prerequisite
Add a "Prerequisites" comment showing what's needed:

```python
# Prerequisites:
# - Python 3.11+
# - packages: requests>=2.28.0, pydantic>=2.0
```

### Step 2: Add Execution Output
Show what the example produces:

```python
# Output:
# {
#   "status": "success",
#   "data": {...}
# }
```

### Step 3: Improve Clarity
Add inline comments explaining complex parts:

```python
# Load configuration from environment
config = Config.from_env()  # Raises ValueError if missing

# Process data (this filters by status='active')
results = config.process(filter_status='active')
```

### Step 4: Link to Related Examples
Cross-reference other examples:

```python
# See also: ex-0042 (Advanced configuration)
#           ex-0091 (Error handling patterns)
```

### Step 5: Document Error Cases
Show what happens when things go wrong:

```python
try:
    result = risky_operation()
except ValueError as e:
    # Raised when input is invalid
    print(f"Invalid input: {e}")
except TimeoutError:
    # Raised when operation takes too long
    print("Operation timed out")
```

---

## Quality Checklist

For each code example, verify:

- [ ] **Syntax Valid**: Code is syntactically correct for the language
- [ ] **Imports Complete**: All required imports/dependencies are shown
- [ ] **Executable**: Example runs without errors (if executable language)
- [ ] **Output Shown**: Comments show expected output or result
- [ ] **Well-Commented**: Complex logic is explained
- [ ] **Prerequisites Clear**: Any setup requirements are documented
- [ ] **Error Handling**: Error cases are shown when relevant
- [ ] **Formatted Correctly**: Code follows language conventions
- [ ] **Context Provided**: Description explains what and why
- [ ] **Linked**: Related examples are referenced
- [ ] **Current**: Reflects latest API/patterns
- [ ] **Realistic**: Uses practical, real-world scenarios

---

## Common Issues & Fixes

| Issue | Solution | Example |
|-------|----------|---------|
| Missing imports | Add all imports at top | `from pathlib import Path` |
| Incomplete example | Show full working code | Not just `# ...do something` |
| No output shown | Add output as comments | `# Output: {"key": "value"}` |
| Uses outdated API | Update to current version | Use `async def` not callbacks |
| Too complex | Break into smaller examples | Link to advanced version |
| No context | Add description before example | "Example: Loading config file" |
| Hard-coded values | Show how to parameterize | Use variables, not magic strings |
| Missing error handling | Add try/except or checks | Handle common failure cases |

---

## Language-Specific Guidelines

### Python
- Use type hints (`def func(x: int) -> str:`)
- Include docstrings with examples
- Show output from doctests
- Include prerequisites (Python version, packages)
- Use modern patterns (async/await, pathlib, etc.)

### Bash/Shell
- Start with `#!/bin/bash` or `#!/bin/sh`
- Comment each step
- Show expected output
- Explain all flags used
- Include error handling (`set -e`, `|| true`, etc.)
- Note OS compatibility

### YAML
- Use 2-space indentation (consistent)
- Include schema comments
- Mark required vs optional fields
- Show where file should be placed
- Validate syntax in example comments

### TypeScript/JavaScript
- Include TypeScript types and interfaces
- Use JSDoc comments
- Show async/await patterns correctly
- Import all dependencies
- Include error handling with try/catch

### Configuration Files
- Show full file structure
- Comment all non-obvious fields
- Include defaults where applicable
- Show where to place the file
- Document validation rules

---

## Example Validation Metrics

### Success Criteria
- **Syntax Valid**: 100% of examples pass language-specific syntax checks
- **Execution**: 80%+ of executable examples run without errors
- **Documentation**: 100% have clear purpose and usage explanation
- **Completeness**: 100% show expected output or results

### Current Status (Phase 12 WS5)
- **Total Examples Analyzed**: 12,776
- **Examples Validated**: 174 (Phase 12 target)
- **Validation Success Rate**: 91/174 (52.3%)
- **Languages Covered**: 10 primary languages

### Phase 30 Goals
- **100% Syntax Valid**: All examples pass language checks
- **80% Executable**: Most working examples are runnable
- **100% Documented**: Every example has purpose and usage
- **280+ Examples Enhanced**: 80% of total examples improved

---

## CI/CD Integration

### Automated Validation
The code example validator runs on every PR with documentation changes:

```yaml
- name: Validate Code Examples
  run: |
    python tools/code_example_validator.py \
      --extract \
      --validate \
      --report \
      --output code_examples_report.json
```

### Pre-commit Hook
Validate examples before committing:

```bash
#!/bin/bash
python tools/code_example_validator.py --extract --validate --limit 50
```

### Continuous Monitoring
Track validation metrics over time:
- Track success rate trends
- Identify problem languages
- Monitor documentation coverage

---

## Resources

- **Validator Tool**: `tools/code_example_validator.py`
- **Catalog Export**: `code_examples_catalog.json`
- **Related Agents**:
  - `unified-doc-agent`: Documentation quality oversight
  - `doc-freshness-checker`: Documentation maintenance
  - `link-validator-agent`: Cross-reference validation

---

## Next Steps (Phase 30)

1. **Enhance remaining 174 examples** (50% remaining)
2. **Expand to all 12,776 examples** (full coverage)
3. **Implement automated testing** for all executable examples
4. **Create language-specific validation** (type checking, etc.)
5. **Build example search/discovery** interface

---

**Created**: 2026-07-08  
**Phase**: 12 WS5 - Code Example Validation  
**Status**:  In Progress
