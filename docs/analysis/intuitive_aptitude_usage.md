# Intuitive Aptitude Code Analysis

**Last Updated:** 2026-06-22

> **Module**: `analysis/intuitive_aptitude.py`  
> **Status**: ✅ Production Ready  
> **Tests**: 76 tests, all passing  
> **Type Safety**: mypy compliant

## Overview

The `intuitive_aptitude` module provides rich code analysis helpers for Python source code. It offers comprehensive AST parsing, pattern recognition, style analysis, and code generation capabilities in a self-contained module that doesn't require optional third-party packages.

## Features

### Core Capabilities

1. **AST Parsing & Structure Extraction**
   - Functions with full metadata (args, decorators, returns, complexity)
   - Classes with inheritance and methods
   - Import statements (regular and relative)
   - Global variables and constants

2. **Pattern Recognition**
   - Error handling patterns (try/except/finally)
   - Iteration patterns (for/while loops)
   - Conditional patterns (if/elif/else)
   - Function call patterns

3. **Style Analysis**
   - Naming conventions (snake_case, camelCase, PascalCase)
   - Indentation style (spaces vs tabs)
   - Docstring styles (Google, NumPy, Sphinx)
   - Programming paradigm (functional vs OOP)

4. **Code Metrics**
   - Lines of code (LOC)
   - Comment ratio
   - Cyclomatic complexity
   - Function call analysis

5. **Code Generation & Transformation**
   - Clone code with identifier renaming
   - Generate skeleton code from structure
   - Generate common patterns

## Quick Start

### Basic Usage

```python
from analysis.intuitive_aptitude import intuitive_aptitude

# Create analyzer
analyzer = intuitive_aptitude()

# Analyze Python code
code = """
def calculate_sum(numbers):
    '''Calculate sum of numbers.

    Args:
        numbers: List of numbers

    Returns:
        int: Sum of all numbers
    '''
    total = 0
    for num in numbers:
        total += num
    return total
"""

# Ingest and analyze
if analyzer.ingest(code):
    # Get high-level summary
    summary = analyzer.get_summary()
    print(f"Functions: {summary['functions_count']}")
    print(f"Complexity: {summary['metrics']['complexity']}")

    # Get detailed structure
    structure = analyzer.get_detailed_structure()
    print(f"Function args: {structure['functions']['calculate_sum']['args']}")

    # Extract patterns
    patterns = analyzer.extract_patterns()
    print(f"Iterations found: {len(patterns['iteration'])}")

    # Analyze code style
    style = analyzer.analyze_code_style()
    print(f"Naming: {style['naming']}")
```

## Using analyze_and_suggest Helper

```python
from analysis.intuitive_aptitude import analyze_and_suggest

code = """
def PoorlyFormattedFunction(x,y):
    if x>0:
        if y>0:
            return x+y
    return 0
"""

result = analyze_and_suggest(code)

if result['success']:
    print("Metrics:", result['summary']['metrics'])
    print("Patterns:", result['patterns'])
    print("Style:", result['style'])
    print("Suggestions:", result['suggestions'])
else:
    print("Error:", result['error'])
```

## API Reference

### Classes

#### `intuitive_aptitude`

Main analyzer class for code ingestion and analysis.

**Methods:**

- `ingest(code: str) -> bool`: Parse and analyze Python code
- `get_summary() -> Dict[str, Any]`: Get high-level summary of analysis
- `get_detailed_structure() -> Dict[str, Any]`: Get complete structural information
- `clone_structure(mappings: Dict[str, str]) -> str`: Generate new code with renamed identifiers
- `extract_patterns() -> Dict[str, List[Dict]]`: Extract code patterns
- `analyze_code_style() -> Dict[str, Any]`: Analyze coding style
- `reset() -> None`: Clear all analysis state

**Attributes:**

- `functions`: Dictionary of discovered functions
- `classes`: Dictionary of discovered classes
- `imports`: List of import statements
- `variables`: Dictionary of global variables
- `patterns`: Dictionary of discovered patterns
- `metrics`: Dictionary of computed metrics
- `ast_tree`: Parsed AST tree
- `last_error`: Last error message (if any)

#### Dataclasses

**`ImportInfo`**
- `module`: Module name (for from imports)
- `name`: Import name
- `alias`: Import alias
- `level`: Relative import level

**`FunctionInfo`**
- `name`: Function name
- `args`: List of argument names
- `defaults`: Number of default arguments
- `kwonlyargs`: Keyword-only arguments
- `decorators`: List of decorators
- `returns`: Return type annotation
- `docstring`: Function docstring
- `lineno`: Starting line number
- `end_lineno`: Ending line number
- `complexity`: Cyclomatic complexity
- `calls`: List of function calls made

**`ClassInfo`**
- `name`: Class name
- `bases`: Base classes
- `decorators`: Class decorators
- `docstring`: Class docstring
- `methods`: Dictionary of methods
- `lineno`: Starting line number
- `end_lineno`: Ending line number

### Functions

#### `analyze_and_suggest(user_code: str) -> Dict[str, Any]`

High-level helper that analyzes code and provides suggestions.

**Returns:**
```python
{
    'success': bool,
    'error': Optional[str],
    'summary': Dict,
    'patterns': Dict,
    'style': Dict,
    'structure': Dict,
    'suggestions': Dict
}
```

## Advanced Usage

### Extracting Specific Patterns

```python
analyzer = intuitive_aptitude()
analyzer.ingest(code)

# Get error handling patterns
error_patterns = analyzer.patterns['error_handling']
for pattern in error_patterns:
    print(f"Line {pattern['lineno']}: {pattern['handlers']}")
    print(f"  Has finally: {pattern['has_finally']}")

# Get iteration patterns
for pattern in analyzer.patterns['iteration']:
    print(f"Loop at line {pattern['lineno']}: {pattern['kind']}")
```

## Code Clone with Renaming

```python
analyzer = intuitive_aptitude()
code = """
def old_function(old_arg):
    return old_arg * 2
"""

analyzer.ingest(code)

# Clone with new names
new_code = analyzer.clone_structure({
    'old_function': 'new_function',
    'old_arg': 'new_arg'
})

print(new_code)
# Output: def new_function(new_arg):
# return new_arg * 2
```

## Analyzing Complexity

```python
analyzer = intuitive_aptitude()
analyzer.ingest(complex_code)

for func_name, func_info in analyzer.functions.items():
    if func_info.complexity > 10:
        print(f"High complexity: {func_name} ({func_info.complexity})")
        print(f"  Calls: {', '.join(func_info.calls)}")
```

### Style Analysis

```python
analyzer = intuitive_aptitude()
analyzer.ingest(code)

style = analyzer.analyze_code_style()

# Check naming conventions
naming = style['naming']
if naming['snake_case'] > naming['camelCase']:
    print("Predominantly snake_case style")

# Check docstring style
docstrings = style['docstrings']
dominant = max(docstrings.items(), key=lambda x: x[1])
print(f"Dominant docstring style: {dominant[0]}")

# Check paradigm
paradigm = style['paradigm']
if paradigm['functional_signals'] > paradigm['oop_signals']:
    print("Functional programming style detected")
```

## Use Cases

### 1. Code Quality Analysis

```python
def analyze_quality(source_file):
    with open(source_file) as f:
        code = f.read()

    result = analyze_and_suggest(code)

    if result['success']:
        # Check complexity
        if result['summary']['metrics']['complexity'] > 10:
            print("⚠️ High complexity detected")

        # Check for suggestions
        if result['suggestions']:
            print("📝 Suggestions:")
            for key, suggestion in result['suggestions'].items():
                print(f"  - {key}: {suggestion}")

        # Check patterns
        error_count = len(result['patterns']['error_handling'])
        print(f"✅ {error_count} error handling patterns found")
```

### 2. Code Template Generation

```python
def generate_test_skeleton(source_code):
    analyzer = intuitive_aptitude()
    analyzer.ingest(source_code)

    test_code = []
    for func_name, func_info in analyzer.functions.items():
        test_name = f"test_{func_name}"
        args = ", ".join(func_info.args)

        test_code.append(f"""
def {test_name}():
    '''Test {func_name} function.'''
    # TODO: Add test implementation
    result = {func_name}({args})
    assert result is not None
""")

    return "\n".join(test_code)
```

### 3. Refactoring Assistant

```python
def suggest_refactoring(code):
    analyzer = intuitive_aptitude()
    analyzer.ingest(code)

    suggestions = []

    # Find complex functions
    for func_name, func_info in analyzer.functions.items():
        if func_info.complexity > 10:
            suggestions.append({
                'type': 'complexity',
                'function': func_name,
                'complexity': func_info.complexity,
                'suggestion': 'Consider splitting into smaller functions'
            })

    # Find missing docstrings
    for func_name, func_info in analyzer.functions.items():
        if not func_info.docstring:
            suggestions.append({
                'type': 'documentation',
                'function': func_name,
                'suggestion': 'Add docstring'
            })

    return suggestions
```

### 4. Style Consistency Checker

```python
def check_style_consistency(project_files):
    styles = []

    for file in project_files:
        with open(file) as f:
            code = f.read()

        analyzer = intuitive_aptitude()
        analyzer.ingest(code)
        style = analyzer.analyze_code_style()
        styles.append((file, style))

    # Aggregate naming conventions
    snake_total = sum(s['naming']['snake_case'] for _, s in styles)
    camel_total = sum(s['naming']['camelCase'] for _, s in styles)

    if snake_total > camel_total * 2:
        print("✅ Project follows snake_case convention")
    elif camel_total > snake_total * 2:
        print("✅ Project follows camelCase convention")
    else:
        print("⚠️ Mixed naming conventions detected")
```

## Testing

The module has comprehensive test coverage with 76 tests:

```bash
# Run all tests
pytest tests/analysis/test_intuitive_aptitude.py -v

# Run specific test class
pytest tests/analysis/test_intuitive_aptitude.py::TestIntuitiveAptitudeIngest -v

# Run with coverage
pytest tests/analysis/test_intuitive_aptitude.py --cov=analysis.intuitive_aptitude
```

## Limitations

1. **Python Syntax Only**: Only analyzes valid Python code
2. **Static Analysis**: Cannot determine runtime behavior
3. **AST-Based**: Limited to information available in the AST
4. **No Cross-File Analysis**: Analyzes single files independently

## Backward Compatibility

The module supports Python 3.9+ using the built-in `ast.unparse()` function. For older Python versions, it falls back to the `astor` package if available.

## Performance

- **Small files** (<1000 LOC): < 50ms
- **Medium files** (1000-5000 LOC): 50-200ms
- **Large files** (>5000 LOC): 200ms-1s

## Contributing

When modifying this module:

1. Run tests: `pytest tests/analysis/test_intuitive_aptitude.py`
2. Run type checking: `mypy analysis/intuitive_aptitude.py`
3. Run linting: `ruff check analysis/intuitive_aptitude.py`
4. Ensure all tests pass before committing

## See Also

- [AST Documentation](https://docs.python.org/3/library/ast.html)
- [Cyclomatic Complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity)
- [Python Style Guide (PEP 8)](https://peps.python.org/pep-0008/)

## License

MIT License - See repository LICENSE file for details.
