import subprocess
from pathlib import Path


def test_cli_smoke(tmp_path: Path) -> None:
    zendesk_out = tmp_path / "zd"
    d365_out = tmp_path / "d365"

    subprocess.check_call(["python", "-m", "codex_crm.cli", "apply-zd", "--out", str(zendesk_out)])
    subprocess.check_call(["python", "-m", "codex_crm.cli", "apply-d365", "--out", str(d365_out)])

    assert (zendesk_out / "forms.json").exists()
    assert (d365_out / "tables.csv").exists()
