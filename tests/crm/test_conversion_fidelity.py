from codex_crm.convert.rules import fidelity_score


def test_fidelity_bounds() -> None:
    assert 0.0 <= fidelity_score(0, 0, 0) <= 1.0
    assert 0.99 <= fidelity_score(1, 1, 1) <= 1.0
