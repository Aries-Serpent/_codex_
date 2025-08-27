# [Test]: Offline Auditor Sanity
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong

from tools.offline_repo_auditor import IntuitiveAptitude

SAMPLE_PY = '''
import os
import torch
# TODO: implement training loop

class Model:
    """doc"""
    pass

def train():
    raise NotImplementedError("later")
'''


def test_collect_and_render_markdown(tmp_path):
    # Create a minimal repo structure
    (tmp_path / "module").mkdir()
    (tmp_path / "module" / "core.py").write_text(SAMPLE_PY, encoding="utf-8")
    (tmp_path / "README.md").write_text("# readme", encoding="utf-8")
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "base.yaml").write_text("seed: 1", encoding="utf-8")

    auditor = IntuitiveAptitude(debug=True)
    summary = auditor.collect(str(tmp_path))
    assert "module/core.py" in summary.py_structs
    assert any("TODO" in f.line for f in summary.stubs)

    out_path = tmp_path / "AUDIT.md"
    auditor.render_markdown(str(out_path), repo="test/repo")
    text = out_path.read_text(encoding="utf-8")
    assert "Repo Map" in text
    assert "Capability Audit Table" in text
