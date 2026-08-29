from cognitive_brain.experiments.exp2_validation import generate_test_audits, run_exp2


def test_generate_test_audits():
    audits = generate_test_audits(5, seed=42)
    assert len(audits) == 5, "Audits must not be empty"
    assert audits[0].audit_id == "EXP2-AUD-0000", "audit_id is not valid"
    for audit in audits:
        assert 0.0 <= audit.score <= 1.0, "0 is not valid"
        assert audit.risk_level in ["low", "medium", "high", "critical"]
        assert len(audit.violations) > 0, "Collection must not be empty"


def test_run_exp2():
    # Mocking out the heavier components or allowing them to run if they are lightweight enough
    # run_exp2 simulates with 500 samples by default, let's test with a smaller sample
    results = run_exp2(sample_size=10, seed=42)
    assert results["experiment_id"] == "EXP-2", "Result must not be empty"
    assert results["sample_size"] == 10, "Result must not be empty"
    assert "redundancy_reduction" in results, "Result must not be empty"
    assert "avg_entangled_correlation" in results, "Result must not be empty"
    assert "avg_control_correlation" in results, "Result must not be empty"
    assert "latency_overhead_ms" in results, "Result must not be empty"
    assert "success" in results, "Result must not be empty"
