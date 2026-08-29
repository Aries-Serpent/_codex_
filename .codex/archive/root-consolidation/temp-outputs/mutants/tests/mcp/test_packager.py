"""
Test Packager

Test module for packager.
"""

import pytest

pytest.importorskip("yaml")

from mcp.packager.generator import generate_package, load_config


def test_packager_generates_files(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
name: sample
python_package: sample_pkg
template: zendesk
output_dir: ./out
include_cli: true
include_tests: true
include_docs: true
include_serverless: true
serverless_target: aws_lambda
dependencies:
  - fastapi
""",
        encoding="utf-8",
    )

    config = load_config(str(config_path))
    out_dir = tmp_path / "generated"
    generate_package(config, output_dir=str(out_dir))

    assert (out_dir / "README.md").exists(), "Condition must be true"
    assert (out_dir / "pyproject.toml").exists(), "Condition must be true"
    assert (out_dir / "sample_pkg" / "app.py").exists(), "Condition must be true"
    assert (out_dir / "serverless" / "aws_lambda.py").exists(), "Condition must be true"
