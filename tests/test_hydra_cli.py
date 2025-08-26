import subprocess, sys

def test_hydra_cli_smoke():
    cmd = [sys.executable, '-m', 'src.codex_ml.cli.main', 'dry_run=true', 'pipeline.steps=[]']
    subprocess.run(cmd, check=True)
