from codex import __version__
from codex_ml.cli.main import cli


def test_cli_reports_package_version(capsys):
    cli(["--version"])
    out = capsys.readouterr().out.strip()
    assert out == f"codex-ml-cli {__version__}"


def test_cli_reports_package_version_short_flag(capsys):
    cli(["-V"])
    out = capsys.readouterr().out.strip()
    assert out == f"codex-ml-cli {__version__}"
