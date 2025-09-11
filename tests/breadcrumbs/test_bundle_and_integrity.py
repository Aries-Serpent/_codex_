import os
import subprocess
from pathlib import Path

from tools import bundle_run


def test_bundle_smoke(tmp_path: Path) -> None:
    f = tmp_path / 'a.txt'
    f.write_text('hi')
    out = bundle_run.bundle_run([str(f)], run_id='r1')
    assert out.exists()


def test_integrity_auditor(tmp_path: Path) -> None:
    pre = tmp_path / 'pre.json'
    post = tmp_path / 'post.json'
    data = tmp_path / 'x.txt'
    data.write_text('1')
    repo_root = Path(__file__).resolve().parents[2]
    env = dict(os.environ, PYTHONPATH=str(repo_root))
    subprocess.run(['python', '-m', 'tools.file_integrity_audit', 'snapshot', str(pre)], cwd=tmp_path, env=env, check=True)
    data.write_text('2')
    subprocess.run(['python', '-m', 'tools.file_integrity_audit', 'snapshot', str(post)], cwd=tmp_path, env=env, check=True)
    res = subprocess.run(['python', '-m', 'tools.file_integrity_audit', 'compare', str(pre), str(post)], cwd=tmp_path, env=env)
    assert res.returncode == 1
