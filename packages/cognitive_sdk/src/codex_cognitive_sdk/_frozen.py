"""Shared internal helpers for the SDK's frozen contract dataclasses."""

from __future__ import annotations

from typing import Iterator, Mapping


class FrozenMapping(Mapping[str, object]):
    """A minimal immutable ``Mapping`` over a copied dict.

    Used in place of ``types.MappingProxyType`` so the SDK contract modules
    stay within the package's dependency-light import budget while still
    guaranteeing that frozen dataclass fields cannot be mutated.
    """

    __slots__ = ("_data",)

    def __init__(self, source: Mapping[str, object] | None = None) -> None:
        self._data = dict(source) if source else {}

    def __getitem__(self, key: str) -> object:
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"FrozenMapping({self._data!r})"


def freeze_mapping(value: Mapping[str, object] | None) -> Mapping[str, object]:
    """Return an immutable mapping snapshot for a frozen dataclass field."""

    if value is None:
        return FrozenMapping()
    if isinstance(value, FrozenMapping):
        return value
    return FrozenMapping(value)
