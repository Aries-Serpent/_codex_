from __future__ import annotations

from codex_ml_telemetry import server


def test_render_prometheus_without_optional_dependency(monkeypatch) -> None:
    monkeypatch.setattr(server, "generate_latest", None)

    assert server.render_prometheus() == "# prometheus_client not installed\n"


def test_render_prometheus_uses_explicit_registry(monkeypatch) -> None:
    registry = object()
    monkeypatch.setattr(server, "generate_latest", lambda target: b"metric 1\n")

    assert server.render_prometheus(registry) == "metric 1\n"


def test_start_metrics_server_without_optional_dependency(monkeypatch) -> None:
    monkeypatch.setattr(server, "start_http_server", None)

    assert server.start_metrics_server() is False


def test_start_metrics_server_delegates_to_prometheus(monkeypatch) -> None:
    calls: list[tuple[int, str]] = []
    monkeypatch.setattr(
        server,
        "start_http_server",
        lambda port, addr: calls.append((port, addr)),
    )

    assert server.start_metrics_server(9123, "0.0.0.0") is True
    assert calls == [(9123, "0.0.0.0")]


def test_start_metrics_server_handles_bind_error(monkeypatch) -> None:
    def fail_to_start(port: int, addr: str) -> None:
        raise OSError("address already in use")

    monkeypatch.setattr(server, "start_http_server", fail_to_start)

    assert server.start_metrics_server() is False
