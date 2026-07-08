import pytest

from mcp.adapters.base_adapter import AdapterConfig, BaseAdapter, QueryResult


def test_adapter_config_defaults():
    config = AdapterConfig()
    assert config.timeout_seconds == 30, "timeout_seconds is not valid"
    assert config.max_retries == 3, "max_retries is not valid"
    assert config.retry_delay_seconds == 1.0, "retry_delay_seconds is not valid"


def test_query_result():
    res = QueryResult(success=True, data={"items": []})
    assert res.success is True, "success is not valid"
    assert res.data == {"items": []}, "Data must not be empty"
    assert res.error is None, "Error should be raised or set"
    assert res.metadata == {}, "Data must not be empty"

    res2 = QueryResult(success=False, error="failed", metadata={"meta": True})
    assert res2.success is False, "success is not valid"
    assert res2.error == "failed", "Error should be raised or set"
    assert res2.metadata == {"meta": True}, "Data must not be empty"


class MockAdapter(BaseAdapter):
    @property
    def adapter_name(self) -> str:
        return "mock"

    @property
    def is_connected(self) -> bool:
        return True

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> None:
        pass

    async def health_check(self) -> bool:
        return True

    async def query(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        filters: dict | None = None,
    ) -> QueryResult:
        return QueryResult(success=True)

    async def upsert(self, vectors: list[dict]) -> QueryResult:
        return QueryResult(success=True)


def test_base_adapter_init():
    adapter = MockAdapter()
    assert adapter.config.timeout_seconds == 30, "timeout_seconds is not valid"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_base_adapter_context_manager():
    adapter = MockAdapter()
    async with adapter as a:
        assert a.is_connected is True, "is_connected is not valid"
