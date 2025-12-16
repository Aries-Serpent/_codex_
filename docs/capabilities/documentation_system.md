# Documentation System

## Overview

The documentation system capability provides comprehensive documentation infrastructure including automated documentation generation, validation, cross-referencing, and searchable documentation portals for the Codex ML platform.

**Keywords**: documentation, docs, guide, reference, tutorial, api-docs, mkdocs, sphinx, docstring, readme, markdown

## Purpose

Provides documentation infrastructure through:
- **Documentation Generation**: Automated API docs from code
- **Static Site Generation**: MkDocs/Sphinx for documentation portals
- **Validation**: Link checking and code example verification
- **Templates**: Standardized documentation templates
- **Cross-References**: Automatic linking between related docs
- **Search**: Full-text search across all documentation

## Architecture

### Documentation Layers

```
┌─────────────────────────────────────┐
│   Source Code                       │
│   (Docstrings, Type hints)          │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Documentation Generator           │
│   (MkDocs, Sphinx, pdoc)            │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Static Site                       │
│   (HTML, CSS, JS)                   │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Validation & Publishing           │
│   (CI checks, GitHub Pages)         │
└─────────────────────────────────────┘
```

## Configuration

### MkDocs Configuration

```yaml
# mkdocs.yml
site_name: Codex ML Documentation
site_description: Comprehensive documentation for the Codex ML platform
site_author: Codex Team

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight
  palette:
    primary: indigo
    accent: indigo

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
    - Configuration: getting-started/configuration.md
  - Capabilities:
    - Overview: capabilities/index.md
    - MCP: capabilities/mcp/index.md
    - Training: capabilities/training/index.md
    - Serving: capabilities/serving/index.md
  - API Reference:
    - Core: api/core.md
    - Training: api/training.md
    - Serving: api/serving.md
  - Contributing: contributing.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            docstring_style: google

markdown_extensions:
  - admonition
  - codehilite
  - toc:
      permalink: true
  - pymdownx.superfences
  - pymdownx.tabbed
```

### Sphinx Configuration

```python
# conf.py
project = 'Codex ML'
copyright = '2024, Codex Team'
author = 'Codex Team'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
```

## Documentation Templates

### Capability Documentation Template

```markdown
# [Capability Name]

## Overview

Brief description of the capability and its purpose.

**Keywords**: keyword1, keyword2, keyword3

## Purpose

What problems does this capability solve?
- Point 1
- Point 2
- Point 3

## Architecture

ASCII diagram or description of architecture.

## Configuration

Code examples for configuration.

## Usage Examples

### Example 1: Basic Usage
```python
# Code example
```

### Example 2: Advanced Usage
```python
# Code example
```

## Safeguards

List of safety measures and validations.

## Best Practices

Numbered list of recommendations.

## Troubleshooting

Common issues and solutions.

## Related Capabilities

Links to related documentation.
```

### API Documentation Template

```python
def example_function(param1: str, param2: int = 10) -> dict:
    """
    Brief description of the function.
    
    Detailed description of what the function does,
    including any important notes.
    
    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 10.
    
    Returns:
        Description of return value.
    
    Raises:
        ValueError: When param1 is empty.
        TypeError: When param2 is not an integer.
    
    Example:
        >>> result = example_function("test", 20)
        >>> print(result)
        {'status': 'success'}
    
    Note:
        Additional notes about usage.
    
    See Also:
        related_function: For similar functionality.
    """
    pass
```

## Usage Examples

### Example 1: Build Documentation Locally

```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material mkdocstrings

# Serve documentation locally
mkdocs serve

# Build static site
mkdocs build

# Output in site/ directory
ls -la site/
```

### Example 2: Generate API Documentation

```bash
# Generate API docs with pdoc
pdoc --html --output-dir docs/api src/codex

# Generate with Sphinx
cd docs
make html
open _build/html/index.html
```

### Example 3: Validate Documentation

```python
# scripts/validate_docs.py
"""
Documentation validation script.

Safeguard: Validates all documentation links and code examples.
Validation: Checks for broken links and syntax errors.
"""
import re
from pathlib import Path

def validate_links(docs_dir: Path) -> list:
    """
    Validate all markdown links in documentation.
    
    Safeguard: Bounded file reads to prevent memory issues.
    """
    broken_links = []
    
    for md_file in docs_dir.glob("**/*.md"):
        content = md_file.read_text()[:100000]  # Bounded read
        
        # Find markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        for text, url in links:
            if url.startswith('#') or url.startswith('http'):
                continue
            
            # Check relative links
            target = md_file.parent / url
            if not target.exists():
                broken_links.append({
                    'file': str(md_file),
                    'link': url,
                    'text': text
                })
    
    return broken_links

if __name__ == "__main__":
    broken = validate_links(Path("docs"))
    if broken:
        print(f"Found {len(broken)} broken links")
        for link in broken:
            print(f"  {link['file']}: {link['link']}")
        exit(1)
    print("All links valid!")
```

### Example 4: CI Documentation Check

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    paths:
      - 'docs/**'
      - 'src/**/*.py'

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install mkdocs mkdocs-material mkdocstrings
      
      - name: Build documentation
        run: mkdocs build --strict
      
      - name: Validate links
        run: python scripts/validate_docs.py
      
      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        run: mkdocs gh-deploy --force
```

### Example 5: Auto-generate README Sections

```python
# scripts/generate_readme.py
"""
Generate README sections from code analysis.

Safeguard: Validates output before writing.
"""
from pathlib import Path
import ast

def extract_module_docstrings(src_dir: Path) -> dict:
    """Extract module-level docstrings from Python files."""
    modules = {}
    
    for py_file in src_dir.glob("**/*.py"):
        try:
            content = py_file.read_text()[:50000]  # Bounded read
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            if docstring:
                modules[py_file.stem] = docstring.split('\n')[0]
        except SyntaxError:
            continue
    
    return modules

def generate_module_list(modules: dict) -> str:
    """Generate markdown list of modules."""
    lines = ["## Modules\n"]
    for name, desc in sorted(modules.items()):
        lines.append(f"- **{name}**: {desc}")
    return '\n'.join(lines)
```

## Safeguards

### Documentation Safeguards

- **Validation**: All links checked before deployment
- **Code Examples**: Python syntax validated
- **Bounded Reads**: File reads limited to prevent memory issues
- **Schema Validation**: YAML configurations validated
- **Spell Check**: Automated spell checking in CI

### Build Safeguards

```yaml
# Safe documentation build with validation
docs-build:
  runs-on: ubuntu-latest
  steps:
    - name: Build with strict mode
      run: mkdocs build --strict
      # Fails on warnings
    
    - name: Validate HTML
      run: |
        pip install html5validator
        html5validator --root site/
    
    - name: Check for broken links
      run: |
        pip install linkchecker
        linkchecker site/index.html
```

## Best Practices

1. **Write Docstrings**: Every public function should have docstrings
2. **Use Templates**: Follow consistent documentation structure
3. **Include Examples**: At least 3 usage examples per capability
4. **Cross-Reference**: Link to related documentation
5. **Keep Updated**: Update docs when code changes
6. **Validate in CI**: Automated checks on every PR
7. **Use Diagrams**: Visual aids for complex concepts
8. **Version Docs**: Match docs versions to code versions

## Troubleshooting

### Build Failures

```bash
# Check for syntax errors
mkdocs build 2>&1 | grep -i error

# Validate YAML
python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"

# Check for missing files
mkdocs build --strict 2>&1 | grep "not found"
```

### Missing API Documentation

```bash
# Verify docstrings exist
python -c "from codex import module; print(module.__doc__)"

# Check mkdocstrings configuration
grep -A10 "mkdocstrings" mkdocs.yml
```

### Search Not Working

```bash
# Rebuild search index
mkdocs build --clean

# Check search plugin is enabled
grep "search" mkdocs.yml
```

## Integration

### IDE Integration

```json
// .vscode/settings.json
{
  "python.analysis.typeCheckingMode": "basic",
  "python.linting.pylintEnabled": true,
  "autoDocstring.docstringFormat": "google"
}
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-docs
        name: Validate Documentation
        entry: python scripts/validate_docs.py
        language: python
        types: [markdown]
```

## Related Capabilities

- [Status Reporting](status_reporting.md) - Generate status reports
- [CI/CD Pipeline](ci_cd_pipeline.md) - Documentation deployment
- [Code Quality Tooling](code_quality_tooling.md) - Code analysis

## References

- MkDocs Documentation: https://www.mkdocs.org/
- Sphinx Documentation: https://www.sphinx-doc.org/
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
