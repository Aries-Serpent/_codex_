import os, subprocess, tempfile, pathlib, json, unittest

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
            lines = [json.loads(l) for l in ndjson.read_text().strip().splitlines()]
            types = [l.get("type") for l in lines]
            self.assertIn("session_start", types)
            self.assertIn("session_end", types)
            self.assertEqual(len([t for t in types if t in ("session_start","session_end")]), 2)

if __name__ == "__main__":
    unittest.main()
