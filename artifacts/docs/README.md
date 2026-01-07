# Codex Documentation Artifacts

> Generated documentation and reference materials (local-only)

## Contents

### API Reference (`api/`)

Auto-generated API documentation from source code docstrings.

- **Build command**: `nox -s docs` or `python tools/build_api_docs.py`
- **View**: Open `api/index.html` in your browser
- **Source**: Generated from `src/` Python modules

The API documentation provides comprehensive reference for:
- `codex.cli` - Command-line interface and entry points
- `codex.logging` - Session logging and telemetry system

### Viewing Documentation

**Option 1: Direct file access**
```bash
# On macOS
open artifacts/docs/api/index.html

# On Linux
xdg-open artifacts/docs/api/index.html

# On Windows
start artifacts/docs/api/index.html
```text

**Option 2: Local HTTP server**
```bash
# Start server
python -m http.server -d artifacts/docs/api 8000

# Navigate to http://localhost:8000
```text

## Building Documentation

### Prerequisites

- Python 3.10+
- pdoc3 (automatically installed by build script)

### Build Commands

```bash
# Full API documentation
nox -s docs

# Or directly with the script
python tools/build_api_docs.py

# With options
python tools/build_api_docs.py --verbose
python tools/build_api_docs.py --skip-optional  # Skip heavy dependencies
python tools/build_api_docs.py --output-dir /custom/path
```text

### Environment Variables

- `CODEX_SKIP_OPTIONAL_IMPORTS=1` - Skip modules requiring optional dependencies

## Directory Structure

```text
artifacts/docs/
├── README.md          # This file
└── api/               # Auto-generated API reference (git-ignored)
    ├── index.html     # Main index page
    └── codex/         # Module documentation
        ├── cli.html
        └── logging/
            ├── index.html
            ├── session_logger.html
            ├── query_logs.html
            └── ...
```text

## Maintenance

### Updating Documentation

Documentation is generated from source code. To update:

1. Update docstrings in source code
2. Rebuild documentation: `nox -s docs`
3. Review changes in browser

### Adding New Modules

To document additional modules, edit `tools/build_api_docs.py`:

```python
MODULES_TO_DOCUMENT = [
    "codex.cli",
    "codex.logging",
    "your_new_module",  # Add here
]
```text

For modules requiring optional dependencies:

```python
OPTIONAL_MODULES = [
    "codex_ml",  # may require torch and other heavy dependencies
    "your_optional_module",  # Add here
]
```text

## Troubleshooting

### "No module named 'pdoc'"

The build script will automatically install pdoc3. If this fails:

```bash
pip install pdoc3
```text

### Import Errors During Build

Use `--skip-optional` to exclude modules with heavy dependencies:

```bash
python tools/build_api_docs.py --skip-optional
```text

### Empty or Missing Documentation

1. Check that modules have docstrings
2. Verify module is in `MODULES_TO_DOCUMENT`
3. Ensure module can be imported:
   ```bash
   PYTHONPATH=src python -c "import your_module"
   ```

## Related Documentation

- [API Build Guide](../../docs/api/README.md) - Detailed build instructions
- [Plugin API](../../docs/plugins/Plugin_API_Broader.md) - Plugin development guide
- [Contributing](../../docs/CONTRIBUTING.md) - Contribution guidelines

## CI/CD Integration

The API documentation build is designed for local use. For CI/CD:

1. Use `nox -s docs` in build pipeline
2. Publish artifacts to documentation hosting service
3. Configure appropriate caching for dependencies

## Support

For issues or questions:

1. Review [docs/api/README.md](../../docs/api/README.md)
2. Check build script: `tools/build_api_docs.py`
3. Open issue on GitHub with `[docs]` tag
