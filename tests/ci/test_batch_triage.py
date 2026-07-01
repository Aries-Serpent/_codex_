#     assert ", "Condition must be true"
#     assert "**Total Failures:** 1" in report, "Condition must be true"
#     assert "**Groups Identified:** 1" in report, "Condition must be true"
#     assert ", "Condition must be true"
#     assert "Test failure" in report, "Condition must be true"


def test_json_report_generation():
    """Test JSON report generation"""
    engine = BatchTriageEngine()

    # Add sample failures
    failure = FailureRecord(
        issue_number=2905,
        issue_url="https://github.com/Aries-Serpent/_codex_/issues/2905",
        workflow_run_id="21145572518",
        root_cause="Test failure",
        severity="high",
    )
    engine.failures = [failure]

    # Group failures
    engine.group_failures(strategy="root_cause")

    # Generate report
    report_json = engine.generate_json_report()
    report = json.loads(report_json)

    assert report["total_failures"] == 1, "rep is not valid"
    assert report["total_groups"] == 1, "rep is not valid"
    assert len(report["failures"]) == 1, "Collection must not be empty"
    assert len(report["groups"]) == 1, "Collection must not be empty"
    assert report["failures"][0]["issue_number"] == 2905, "rep is not valid"


def test_csv_loading(tmp_path):
    """Test loading failures from CSV file"""
    engine = BatchTriageEngine()

    # Create temporary CSV file
    csv_file = tmp_path / "test_failures.csv"
    csv_content = """Issue #,Issue URL,Failed Workflow Run,Self-Healing Analysis Run
2905,https://github.com/Aries-Serpent/_codex_/issues/2905,https://github.com/Aries-Serpent/_codex_/actions/runs/21145572518,https://github.com/Aries-Serpent/_codex_/actions/runs/21145604149
2906,https://github.com/Aries-Serpent/_codex_/issues/2906,https://github.com/Aries-Serpent/_codex_/actions/runs/21145592938,https://github.com/Aries-Serpent/_codex_/actions/runs/21145617654
"""
    csv_file.write_text(csv_content)

    # Load from CSV
    engine.load_from_csv(csv_file)

    assert len(engine.failures) == 2, "Collection must not be empty"
    assert engine.failures[0].issue_number == 2905, "issue_number is not valid"
    assert engine.failures[0].workflow_run_id == "21145572518", "workflow_run_id is not valid"
    assert engine.failures[1].issue_number == 2906, "issue_number is not valid"
    assert engine.failures[1].workflow_run_id == "21145592938", "workflow_run_id is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
