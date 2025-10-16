from __future__ import annotations

import zipfile
from pathlib import Path

from tools.scan_secrets import scan_archive, scan_file


def test_scanner_finds_obvious_tokens(tmp_path: Path) -> None:
    aws = "AKIA1234567890" + "ABCD" + "EF"
    slack = "xoxb-" + "abcdefghij" + "klmno"
    target = tmp_path / "sample.txt"
    target.write_text(f"AWS: {aws}\nSlack: {slack}\n", encoding="utf-8")

    hits = scan_file(target)
    kinds = {name for (name, _line, _text) in hits}
    assert "aws_access_key" in kinds
    assert "slack_token" in kinds


def test_scanner_reads_archive(tmp_path: Path) -> None:
    archive = tmp_path / "bundle.zip"
    aws = "AKIA1234567890" + "ABCD" + "EF"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("inner.txt", f"aws={aws}\n")

    hits = scan_file(archive)
    kinds = {name for (name, _line, _text) in hits}
    assert "aws_access_key" in kinds
