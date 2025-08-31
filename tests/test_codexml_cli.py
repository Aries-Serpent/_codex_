import pytest

from codex_ml.cli.main import cli


def test_codexml_cli_help():
    with pytest.raises(SystemExit):
        cli(["--help"])
