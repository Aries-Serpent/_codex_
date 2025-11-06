# API Documentation

> Comprehensive API reference for the Codex ML framework

## Overview

This directory contains tooling and documentation for generating comprehensive API reference documentation from source code docstrings.

## Building API Documentation

### Quick Start

Build API documentation locally:

```bash
# Using the build script directly
python tools/build_api_docs.py

# Using nox
nox -s docs
```

The generated documentation will be written to `artifacts/docs/api/` (local only, git-ignored).

### Build Options

```bash
# Specify custom output directory
python tools/build_api_docs.py --output-dir /path/to/output

# Skip modules requiring optional dependencies
python tools/build_api_docs.py --skip-optional

# Enable verbose logging
python tools/build_api_docs.py --verbose
```

### Environment Variables

- `CODEX_SKIP_OPTIONAL_IMPORTS=1` - Skip modules requiring optional dependencies (useful for minimal environments)

## Viewing Documentation

After building, open the documentation in your browser:

```bash
# On macOS
open artifacts/docs/api/index.html

# On Linux
xdg-open artifacts/docs/api/index.html

# Or use Python's HTTP server
python -m http.server -d artifacts/docs/api 8000
# Then navigate to http://localhost:8000
```

## API Documentation Structure

The API documentation covers the following main modules:

- **codex_ml** - Core ML utilities: training, evaluation, metrics, models
  - `codex_ml.training` - Training engine and loops
  - `codex_ml.eval` - Evaluation runner and metrics
  - `codex_ml.models` - Model factories and wrappers
  - `codex_ml.data` - Data loaders and preprocessing
  - `codex_ml.metrics` - Metrics registry and implementations
  - `codex_ml.plugins` - Plugin system and registries
  - `codex_ml.tracking` - MLflow and experiment tracking
  - `codex_ml.peft` - LoRA/QLoRA adapters (optional)
  - `codex_ml.distributed` - Distributed training utilities (optional)

- **codex.cli** - Command-line interface and entry points
  
- **codex.logging** - Session logging and telemetry

## Prerequisites

### Required Dependencies

API documentation generation requires:

- Python 3.10+
- pdoc3 (automatically installed by the build script)

### Optional Dependencies

Some modules require optional dependencies to import successfully:

- **LoRA/PEFT modules**: `peft`, `accelerate`
- **Distributed training**: `torch.distributed`, `accelerate`
- **Metrics**: `nltk`, `rouge-score`, `sacrebleu`

When building in minimal environments, use `--skip-optional` to exclude these modules.

## Documentation Standards

### Docstring Format

All public modules, classes, and functions should have docstrings following these conventions:

```python
def example_function(param1: str, param2: int = 0) -> dict:
    """
    Brief one-line summary of the function.
    
    More detailed description if needed. Explain the purpose,
    behavior, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        
    Returns:
        Dictionary containing result data
        
    Raises:
        ValueError: When param1 is empty
        
    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    ...
```

### Module-Level Docstrings

Each module should have a top-level docstring:

```python
"""
Module name and brief description.

This module provides utilities for X. It includes:
- Feature A
- Feature B
- Feature C

Example usage:
    from codex_ml import module
    result = module.do_something()
"""
```

## Troubleshooting

### Import Errors During Build

If the build fails due to import errors:

1. **Check optional dependencies**: Use `--skip-optional` to exclude modules requiring optional packages
2. **Install missing packages**: Install the package with extras: `pip install -e .[all]`
3. **Set environment variable**: `CODEX_SKIP_OPTIONAL_IMPORTS=1 python tools/build_api_docs.py`

### pdoc3 Installation Issues

If pdoc3 fails to install:

```bash
# Install manually
pip install pdoc3

# Or use a specific version
pip install pdoc3==0.10.0
```

### Empty or Missing Documentation

If modules appear without documentation:

1. Ensure the module has a top-level docstring
2. Check that functions/classes have docstrings
3. Verify the module is in `MODULES_TO_DOCUMENT` in `tools/build_api_docs.py`

## Maintenance

### Adding New Modules

To document new modules, edit `tools/build_api_docs.py`:

```python
MODULES_TO_DOCUMENT = [
    "codex_ml",
    "codex.cli",
    "codex.logging",
    "your_new_module",  # Add here
]
```

If the module requires optional dependencies:

```python
OPTIONAL_MODULES = [
    "codex_ml.peft",
    "codex_ml.distributed",
    "your_optional_module",  # Add here
]
```

### Updating Documentation

API documentation is generated from source code. To update:

1. Update docstrings in source code
2. Rebuild documentation: `python tools/build_api_docs.py`
3. Review changes in `artifacts/docs/api/`

### CI/CD Integration

The build script is designed for local-only use. To integrate with CI:

1. Add a nox session (already included)
2. Run as part of documentation deployment pipeline
3. Publish artifacts to a documentation hosting service

## Related Documentation

- **User Guides**: See `docs/guides/` for tutorials and how-tos
- **Architecture**: See `docs/architecture/` for system design docs
- **Examples**: See `examples/` for code examples
- **Testing**: See `tests/` for usage examples in tests

## Support

For questions or issues:

1. Check troubleshooting section above
2. Review existing documentation in `docs/`
3. Open an issue on GitHub with `[docs]` tag
