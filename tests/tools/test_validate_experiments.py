import json
from pathlib import Path
import tempfile, subprocess, sys

SCHEMA_CONTENT = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["model", "data", "training"],
    "properties": {
        "model": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}},
        "data": {"type": "object", "required": ["dataset"], "properties": {"dataset": {"type": "string"}}},
        "training": {
            "type": "object",
            "required": ["epochs", "batch_size"],
            "properties": {"epochs": {"type": "integer"}, "batch_size": {"type": "integer"}}
        }
    }
}

VALID_CFG = {
    "model": {"name": "demo"},
    "data": {"dataset": "synthetic"},
    "training": {"epochs": 1, "batch_size": 2}
}

INVALID_CFG = {
    "model": {"name": "demo"},
    "data": {},  # missing dataset
    "training": {"epochs": 1, "batch_size": 2}
}

VALID_TOML_CONTENT = """
[model]
name = "demo"

[data]
dataset = "synthetic"

[training]
epochs = 1
batch_size = 2
"""

INVALID_TOML_CONTENT = """
[model]
name = "demo"

[data]
# missing dataset

[training]
epochs = 1
batch_size = 2
"""


def test_validator_success():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        schema = td / "schema.json"
        schema.write_text(json.dumps(SCHEMA_CONTENT))
        cfg = td / "exp.json"
        cfg.write_text(json.dumps(VALID_CFG))

        result = subprocess.run(
            [sys.executable, "tools/validate_experiments.py", "--schema", str(schema), "--paths", str(td)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr

def test_validator_failure():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        schema = td / "schema.json"
        schema.write_text(json.dumps(SCHEMA_CONTENT))
        cfg = td / "exp.json"
        cfg.write_text(json.dumps(INVALID_CFG))

        result = subprocess.run(
            [sys.executable, "tools/validate_experiments.py", "--schema", str(schema), "--paths", str(td)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 3
        assert "dataset" in result.stderr

def test_validator_toml_success():
    """Test TOML config validation works (P1 fix)"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        schema = td / "schema.json"
        schema.write_text(json.dumps(SCHEMA_CONTENT))
        cfg = td / "exp.toml"
        cfg.write_text(VALID_TOML_CONTENT)

        result = subprocess.run(
            [sys.executable, "tools/validate_experiments.py", "--schema", str(schema), "--paths", str(td)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "Validated 1 config file(s) successfully" in result.stdout

def test_validator_toml_failure():
    """Test TOML config validation detects errors (P1 fix)"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        schema = td / "schema.json"
        schema.write_text(json.dumps(SCHEMA_CONTENT))
        cfg = td / "exp.toml"
        cfg.write_text(INVALID_TOML_CONTENT)

        result = subprocess.run(
            [sys.executable, "tools/validate_experiments.py", "--schema", str(schema), "--paths", str(td)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 3
        assert "dataset" in result.stderr


def test_validator_excludes_schema_files():
    """Test that discover() excludes schema files to prevent false validation failures (P1 fix)"""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        
        # Create schema directory with schema files
        schema_dir = td / "schemas"
        schema_dir.mkdir()
        schema_file = schema_dir / "experiments.schema.json"
        schema_file.write_text(json.dumps(SCHEMA_CONTENT))
        
        # Create valid config file
        config_dir = td / "configs"
        config_dir.mkdir()
        cfg = config_dir / "exp.json"
        cfg.write_text(json.dumps(VALID_CFG))
        
        # Also create a schema-like file in config dir
        schema_like = config_dir / "my.schema.json"
        schema_like.write_text(json.dumps(SCHEMA_CONTENT))
        
        # Run validator - should only validate exp.json, not schema files
        result = subprocess.run(
            [sys.executable, "tools/validate_experiments.py", "--schema", str(schema_file), "--paths", str(td)],
            capture_output=True,
            text=True,
        )
        # Should succeed because it only validates exp.json (valid), not schema files
        assert result.returncode == 0, result.stderr
        # Should report only 1 file validated (exp.json), not 2 or 3
        assert "Validated 1 config file(s) successfully" in result.stdout