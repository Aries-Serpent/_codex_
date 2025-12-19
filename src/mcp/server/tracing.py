from __future__ import annotations
import importlib
import importlib.util
import os
import uuid
from starlette.requests import Request


def init_tracing(service_name: str = "mcp"):
    """
    Lazy OpenTelemetry bootstrap. If OTEL_EXPORTER_OTLP_ENDPOINT is set and OTel
    packages are available, initialize provider. Silently no-ops otherwise.
    """
    otlp = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not otlp:
        return
    if importlib.util.find_spec("opentelemetry") is None:
        return
    if importlib.util.find_spec("opentelemetry.sdk") is None:
        return
    if importlib.util.find_spec("opentelemetry.exporter.otlp.proto.grpc.trace_exporter") is None:
        return

    trace = importlib.import_module("opentelemetry.trace")
    resource_mod = importlib.import_module("opentelemetry.sdk.resources")
    tracer_mod = importlib.import_module("opentelemetry.sdk.trace")
    export_mod = importlib.import_module("opentelemetry.sdk.trace.export")
    otlp_mod = importlib.import_module("opentelemetry.exporter.otlp.proto.grpc.trace_exporter")

    resource = resource_mod.Resource.create({"service.name": service_name})
    provider = tracer_mod.TracerProvider(resource=resource)
    provider.add_span_processor(export_mod.BatchSpanProcessor(otlp_mod.OTLPSpanExporter(endpoint=otlp)))
    trace.set_tracer_provider(provider)


def ensure_request_id(request: Request) -> str:
    """
    Ensure request has X-Request-Id (generate if missing) and attach to request.state for downstream use.
    """
    rid = request.headers.get("x-request-id")
    if not rid:
        rid = str(uuid.uuid4())
        # Note: we don't mutate headers immutable mapping; handler may read request.state.request_id
    request.state.request_id = rid
    return rid
