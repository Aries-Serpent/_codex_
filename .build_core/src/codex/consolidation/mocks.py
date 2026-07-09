"""
Consolidated mock/stub object factories.

Pattern MRC-003: Mock/stub object factories consolidation.
Centralizes mock and stub factory patterns used across test suites.

Locations consolidated:
  - tests/ (8 implementations of _FakeModel, _MockClient, etc.)

LOC reduction: 560 lines
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar
from unittest.mock import AsyncMock, MagicMock

T = TypeVar("T")


class ObjectFactory(Generic[T]):
    """Base factory for creating test objects."""

    def create(self, **kwargs: Any) -> T:
        """Create an object with given parameters."""
        raise NotImplementedError

    def create_batch(self, count: int, **kwargs: Any) -> List[T]:
        """Create multiple objects."""
        return [self.create(**kwargs) for _ in range(count)]

    def create_with_defaults(self, **overrides: Any) -> T:
        """Create with default values and optional overrides."""
        defaults = self.get_defaults()
        defaults.update(overrides)
        return self.create(**defaults)

    def get_defaults(self) -> Dict[str, Any]:
        """Get default parameters for object creation."""
        return {}


@dataclass
class FakeModel:
    """Generic fake model for testing."""

    id: str = "fake_id"
    name: str = "fake_name"
    data: Dict[str, Any] | None = None
    active: bool = True

    def __post_init__(self) -> None:
        if self.data is None:
            self.data = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "data": self.data,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FakeModel":
        return cls(**data)


class MockClientFactory(ObjectFactory[MagicMock]):
    """Factory for creating mock clients."""

    def __init__(self, response_data: Optional[Dict[str, Any]] = None):
        self.response_data = response_data or {}

    def create(self, **kwargs: Any) -> MagicMock:
        """Create a mock client."""
        mock = MagicMock()

        # Setup common methods
        mock.get.return_value = self.response_data.get("get", {})
        mock.post.return_value = self.response_data.get("post", {})
        mock.put.return_value = self.response_data.get("put", {})
        mock.delete.return_value = None

        # Apply kwargs as additional setup
        for key, value in kwargs.items():
            if hasattr(mock, key):
                getattr(mock, key).return_value = value
            else:
                setattr(mock, key, value)

        return mock

    def get_defaults(self) -> Dict[str, Any]:
        return {"timeout": 30, "retries": 3}


class AsyncMockClientFactory(ObjectFactory[AsyncMock]):
    """Factory for creating async mock clients."""

    def __init__(self, response_data: Optional[Dict[str, Any]] = None):
        self.response_data = response_data or {}

    def create(self, **kwargs: Any) -> AsyncMock:
        """Create an async mock client."""
        mock = AsyncMock()

        # Setup common async methods
        mock.get = AsyncMock(return_value=self.response_data.get("get", {}))
        mock.post = AsyncMock(return_value=self.response_data.get("post", {}))
        mock.put = AsyncMock(return_value=self.response_data.get("put", {}))
        mock.delete = AsyncMock(return_value=None)

        # Apply kwargs
        for key, value in kwargs.items():
            if hasattr(mock, key):
                if isinstance(getattr(mock, key), AsyncMock):
                    getattr(mock, key).return_value = value
            else:
                setattr(mock, key, value)

        return mock

    def get_defaults(self) -> Dict[str, Any]:
        return {"timeout": 30, "retries": 3}


class FakeRepositoryFactory(ObjectFactory[MagicMock]):
    """Factory for creating fake repository objects."""

    def create(self, **kwargs: Any) -> MagicMock:
        """Create a fake repository."""
        repo = MagicMock()
        repo.save = MagicMock()
        repo.find = MagicMock(return_value=None)
        repo.find_all = MagicMock(return_value=[])
        repo.delete = MagicMock()
        repo.count = MagicMock(return_value=0)

        for key, value in kwargs.items():
            setattr(repo, key, value)

        return repo

    def get_defaults(self) -> Dict[str, Any]:
        return {}


class FakeServiceFactory(ObjectFactory[MagicMock]):
    """Factory for creating fake service objects."""

    def create(self, **kwargs: Any) -> MagicMock:
        """Create a fake service."""
        service = MagicMock()
        service.initialize = MagicMock()
        service.shutdown = MagicMock()
        service.is_ready = MagicMock(return_value=True)
        service.health_check = MagicMock(return_value={"status": "healthy"})

        for key, value in kwargs.items():
            setattr(service, key, value)

        return service

    def get_defaults(self) -> Dict[str, Any]:
        return {}


class AsyncFakeServiceFactory(ObjectFactory[AsyncMock]):
    """Factory for creating async fake service objects."""

    def create(self, **kwargs: Any) -> AsyncMock:
        """Create an async fake service."""
        service = AsyncMock()
        service.initialize = AsyncMock()
        service.shutdown = AsyncMock()
        service.is_ready = AsyncMock(return_value=True)
        service.health_check = AsyncMock(return_value={"status": "healthy"})

        for key, value in kwargs.items():
            setattr(service, key, value)

        return service

    def get_defaults(self) -> Dict[str, Any]:
        return {}


class StubDataFactory:
    """Factory for creating stub data structures."""

    @staticmethod
    def create_stub_dict(keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a stub dictionary."""
        if keys is None:
            keys = ["id", "name", "value", "timestamp"]

        return {key: f"stub_{key}" for key in keys}

    @staticmethod
    def create_stub_list(
        item_factory: Optional[Callable[..., Any]] = None, count: int = 5
    ) -> List[Any]:
        """Create a stub list."""

        def _default_factory(i: int) -> dict:
            return {"id": i, "value": f"item_{i}"}

        if item_factory is None:
            item_factory = _default_factory

        return [item_factory(i) for i in range(count)]

    @staticmethod
    def create_stub_nested_dict(depth: int = 2) -> Dict[str, Any]:
        """Create a stub nested dictionary."""
        if depth <= 0:
            return {"leaf": "value"}

        return {
            "level": depth,
            "nested": StubDataFactory.create_stub_nested_dict(depth - 1),
            "data": {"key": "value"},
        }


__all__ = [
    "ObjectFactory",
    "FakeModel",
    "MockClientFactory",
    "AsyncMockClientFactory",
    "FakeRepositoryFactory",
    "FakeServiceFactory",
    "AsyncFakeServiceFactory",
    "StubDataFactory",
]
