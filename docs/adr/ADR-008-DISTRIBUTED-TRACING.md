# ADR-008: Distributed Tracing for Observability

**Version**: v0.2.1
**Last Updated:** 2026-07-11

**Status:** Accepted  
**Date:** 2026-07-10  
**Author:** @mbaetiong  
**Session:** S250-doc-arch  

---

## Context

As the platform scales across multiple layers and eventually multiple services, it becomes difficult to:
- Track request flow across components
- Identify performance bottlenecks
- Diagnose failures
- Understand latency distribution

Centralized logging alone is insufficient because we lose context about:
- Which component caused delays
- How requests flow through the system
- Dependencies between components

---

## Decision

Implement **distributed tracing** using **OpenTelemetry** with **Jaeger** as the tracing backend:

**Benefits:**
1. **End-to-end visibility** — Trace requests from entry to exit
2. **Performance analysis** — Identify bottleneck components
3. **Error tracking** — Link errors to request traces
4. **Dependency mapping** — Automatic service discovery
5. **Sampling** — Configurable tracing overhead
6. **Open standard** — Not vendor-locked

---

## Trace Structure

```
Request: /api/v1/inference POST

Trace:
├─ trace_id: abc123def456
├─ root_span: api.inference.POST (0-500ms)
│  ├─ api.auth (5-10ms)
│  ├─ span: rag.embed_query (50-100ms)
│  │  └─ vectorstore.search (45-95ms)
│  ├─ span: model.forward (200-380ms)
│  │  ├─ model.encode (100-150ms)
│  │  └─ model.decode (100-200ms)
│  └─ span: api.serialize (5-10ms)
└─ span_metrics:
   ├─ total_duration: 500ms
   ├─ bottleneck: model.forward (380ms, 76%)
   └─ errors: 0
```

---

## Implementation

**Installation:**

```bash
pip install opentelemetry-api opentelemetry-sdk \
            opentelemetry-exporter-jaeger \
            opentelemetry-instrumentation-fastapi \
            opentelemetry-instrumentation-requests
```

**Initialization:**

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

# Set up tracing
trace_provider = TracerProvider()
trace_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(trace_provider)

# Auto-instrument libraries
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

# Get tracer for custom spans
tracer = trace.get_tracer(__name__)
```

**Custom span creation:**

```python
def process_data(data):
    with tracer.start_as_current_span("process_data") as span:
        span.set_attribute("data.size", len(data))
        
        with tracer.start_as_current_span("validate") as validate_span:
            validate_data(data)
            validate_span.set_attribute("valid", True)
        
        with tracer.start_as_current_span("transform") as transform_span:
            result = transform_data(data)
            transform_span.set_attribute("output.size", len(result))
        
        return result
```

---

## Jaeger Deployment

**Docker Compose (local development):**

```yaml
version: "3"
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "6831:6831/udp"  # Collector
      - "16686:16686"     # UI (http://localhost:16686)
    environment:
      COLLECTOR_OTLP_ENABLED: "true"
```

**Kubernetes (production):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: jaeger-all-in-one
spec:
  containers:
  - name: jaeger
    image: jaegertracing/all-in-one:latest
    ports:
    - containerPort: 6831
      protocol: UDP
    - containerPort: 16686
      protocol: TCP
    resources:
      requests:
        memory: "2Gi"
        cpu: "1"
      limits:
        memory: "4Gi"
        cpu: "2"
```

---

## Consequences

### Positive
 Complete visibility into request flow  
 Performance bottlenecks identified automatically  
 Easier debugging of distributed issues  
 Automatic service dependency mapping  
 Integrates with Prometheus metrics  
 Sampling reduces overhead  

### Negative
️ Additional infrastructure (Jaeger)  
️ Storage overhead (traces can be large)  
️ Sampling might miss rare errors  

### Mitigations
- Jaeger provided via Docker for easy setup
- Configurable sampling rate
- Error traces always sampled (100%)
- Automatic cleanup of old traces

---

## Performance Impact

**Typical overhead:**
- Span creation: <1µs
- Serialization: <10µs per span
- Network: <5ms per batch (batched)
- Total impact: <1% latency overhead with 1% sampling

**With 100% sampling:**
- Overhead: ~5-10% latency
- Storage: ~1-2% of total data
- Not recommended for production, use error sampling instead

---

## Sampling Strategy

**Recommended:**
```python
sampler = TraceIdRatioBased(rate=0.1)  # 10% of requests

# For errors, always sample:
if is_error:
    sampler = TraceIdRatioBased(rate=1.0)
```

---

## Related ADRs
- ADR-006: Event-Driven Architecture
- ADR-009: Monitoring & Alerting Strategy
