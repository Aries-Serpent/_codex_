from pathlib import Path


def test_compose_does_not_embed_secrets() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    assert "API_KEY" not in compose or "${API_KEY}" in compose
