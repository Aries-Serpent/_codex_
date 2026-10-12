import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.ci import session_wrapup_autofix as swa


def test_accountability_report_targets_active_report():
    assert swa.ACCOUNTABILITY_REPORT == (
        _REPO_ROOT / "docs" / "accountability" / "AGENT_ACCOUNTABILITY_REPORT.md"
    )


def test_accountability_report_is_current_when_recent_entry_is_at_top(tmp_path, monkeypatch):
    report = tmp_path / "AGENT_ACCOUNTABILITY_REPORT.md"
    today = swa.datetime.now(tz=swa.timezone.utc).strftime("%Y-%m-%d")
    report.write_text(f"## Session: {today} — current session\n" + "older\n" * 200)
    monkeypatch.setattr(swa, "ACCOUNTABILITY_REPORT", report)

    assert swa._accountability_report_is_current()


def test_accountability_report_requires_recent_date_on_session_heading(
    tmp_path, monkeypatch
):
    report = tmp_path / "AGENT_ACCOUNTABILITY_REPORT.md"
    today = swa.datetime.now(tz=swa.timezone.utc).strftime("%Y-%m-%d")
    report.write_text(f"## Session: 2020-01-01 — old session\nToday is {today}.\n")
    monkeypatch.setattr(swa, "ACCOUNTABILITY_REPORT", report)

    assert not swa._accountability_report_is_current()
