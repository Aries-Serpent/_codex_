# Adapter implementation notes

This short guide describes the adapter interface required by MCP and how to implement a new backend adapter.

Required Adapter API (BackendAdapter)
- connect() -> None
- upsert_batch(namespace: str, items: Iterable[VectorItem]) -> None
- query_top_k(namespace: str, query_embedding: List[float], top_k: int, filters: Optional[Dict]) -> List[BackendResponse]
- delete(namespace: str, id: str) -> bool
- health_check() -> Dict[str, Any]

Implementation checklist
- Implement the interface in `src/mcp/backends/<provider>_adapter.py`
- Use `namespace` to support multi-tenant isolation (prefix or dedicated namespace)
- Ensure `upsert_batch` accepts deterministic item dicts (id, embedding, content, metadata)
- Add unit tests in `tests/mcp/test_<provider>_adapter.py`
- Add environment variables (documented in .env.example)

Testing strategy
- Start with the in-repo mock backend (InMemoryMockBackend) for CI and local dev.
- Add mocks for external providers for unit tests (do not call live APIs in unit tests).
- Add an integration test job that is gated by presence of secrets for live runs (future step).
