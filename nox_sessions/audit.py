from __future__ import annotations

import nox


@nox.session
def audit(session: nox.Session) -> None:
    """
    Local, offline gate:
      1) install dev deps
      2) run quick unit tests
      3) run fast audit path
    """
    session.install("-r", "requirements/base.txt")
    session.install("-r", "requirements/dev.txt")
    session.run(
        "pytest",
        "-q",
        "tests/atomic_diffs",
        env={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "CODEX_ALLOW_REMOTE": "0"},
    )
    session.run("pytest", "-q")
    session.run("make", "-f", "space.mk", "space-audit-fast")
