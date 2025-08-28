from codex_digest.pipeline import run_pipeline


def test_pipeline_converges():
    ctx = "Objective: organize and prioritize tasks for audit, hooks, and tests."
    raw = "Generate audit; pre-commit run is slow; pytest coverage flags missing."
    out = run_pipeline(ctx, raw, dry_run=True)
    assert out.convergence > 0.5
    assert "Prioritized Tasks" in out.tasks_md
