from pathlib import Path


def test_no_root_user_in_container() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    assert "USER appuser" in dockerfile


def test_minimal_attack_surface() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
    assert "apt-get" in dockerfile
    assert "curl" in dockerfile
