import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SHELL_HELPER = ROOT / "scripts" / "session_logging.sh"


@unittest.skipUnless(SHELL_HELPER.exists(), "shell helper missing")
class TestSessionHooks(unittest.TestCase):
    def test_shell_helper_records_start_and_end(self):
        with tempfile.TemporaryDirectory() as td:
            logdir = pathlib.Path(td)
            sid = "test-sess-1234"
            runner = logdir / "runner.sh"
            runner.write_text(f"""#!/usr/bin/env bash
set -euo pipefail
export CODEX_SESSION_LOG_DIR=\"{logdir.as_posix()}\"
export CODEX_SESSION_ID=\"{sid}\"
. \"{SHELL_HELPER.as_posix()}\"
codex_session_start \"unit\"
trap 'codex_session_end $?' EXIT
true
""")
            runner.chmod(0o755)
            subprocess.run([runner.as_posix()], check=True)
            ndjson = logdir / f"{sid}.ndjson"
            self.assertTrue(ndjson.exists(), "ndjson log not found")
            lines = [
                json.loads(line) for line in ndjson.read_text().strip().splitlines()
            ]
            types = [line.get("type") for line in lines]
            self.assertIn("session_start", types)
            self.assertIn("session_end", types)
            self.assertEqual(
                len([t for t in types if t in ("session_start", "session_end")]), 2
            )

    def test_shell_helper_recovers_missing_dir(self):
        with tempfile.TemporaryDirectory() as td:
            logdir = pathlib.Path(td)
            sid = "lost-dir-123"
            runner = logdir / "runner.sh"
            runner.write_text(f"""#!/usr/bin/env bash
set -euo pipefail
export CODEX_SESSION_LOG_DIR=\"{logdir.as_posix()}\"
export CODEX_SESSION_ID=\"{sid}\"
. \"{SHELL_HELPER.as_posix()}\"
codex_session_start
rm -rf \"{logdir.as_posix()}\"
codex_session_end 0
""")
            runner.chmod(0o755)
            subprocess.run([runner.as_posix()], check=True)
            ndjson = logdir / f"{sid}.ndjson"
            self.assertTrue(ndjson.exists(), "ndjson not recreated")
            lines = [
                json.loads(line) for line in ndjson.read_text().strip().splitlines()
            ]
            types = [line.get("type") for line in lines]
            self.assertIn("session_end", types)

    def test_shell_helper_handles_cwd_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            sid = "test-chdir-1234"
            runner = root / "runner.sh"
            runner.write_text(
                f"""#!/usr/bin/env bash
set -euo pipefail
export CODEX_SESSION_LOG_DIR=logs
export CODEX_SESSION_ID=\"{sid}\"
. \"{SHELL_HELPER.as_posix()}\"
codex_session_start
trap 'codex_session_end $?' EXIT
mkdir sub && cd sub
true
"""
            )
            runner.chmod(0o755)
            subprocess.run([runner.as_posix()], cwd=root, check=True)
            ndjson = root / "logs" / f"{sid}.ndjson"
            self.assertTrue(ndjson.exists(), "ndjson log not found in resolved logdir")
            self.assertFalse(
                (root / "sub" / "logs").exists(), "logdir should not depend on cwd"
            )


class TestPythonSessionHooks(unittest.TestCase):
    def test_session_logs_after_cwd_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            env = os.environ.copy()
            env.pop("CODEX_SESSION_ID", None)
            env["CODEX_SESSION_LOG_DIR"] = "logs"
            env["PYTHONPATH"] = str(ROOT)
            script = root / "runner.py"
            script.write_text(
                "import os, pathlib\n"
                "from codex.logging.session_hooks import session\n"
                "pathlib.Path('sub').mkdir()\n"
                "os.chdir('sub')\n"
                "with session():\n"
                "    pass\n"
            )
            subprocess.run([sys.executable, script.name], cwd=root, check=True, env=env)
            logdir = root / "logs"
            self.assertTrue(
                any(logdir.glob("*.ndjson")), "log not created in resolved dir"
            )
            self.assertFalse(
                (root / "sub" / "logs").exists(), "logdir should not depend on cwd"
            )


if __name__ == "__main__":
    unittest.main()
