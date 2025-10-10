from pathlib import Path


def test_compose_defines_required_volumes() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "./data:/data" in compose
    assert "./artifacts:/artifacts" in compose
