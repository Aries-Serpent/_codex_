"""Content-addressed artifact references."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping
from urllib.parse import urlsplit

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*$")
_INVALID_PERCENT_ESCAPE = re.compile(r"%(?![0-9A-Fa-f]{2})")
_MEDIA_TYPE = re.compile(r"^[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+$")
_MAX_URI_LENGTH = 4096
_MAX_METADATA_ITEMS = 128
_MAX_METADATA_KEY_LENGTH = 256
_MAX_METADATA_VALUE_LENGTH = 4096


def _contains_unsafe_text(value: str) -> bool:
    return any(
        character.isspace() or ord(character) < 32 or ord(character) == 127
        for character in value
    )


def _validate_uri(uri: object) -> str:
    if not isinstance(uri, str) or not uri:
        raise ValueError("uri must be a non-empty string")
    if not uri.isascii():
        raise ValueError("uri must contain only ASCII characters")
    if len(uri) > _MAX_URI_LENGTH or _contains_unsafe_text(uri) or "\\" in uri:
        raise ValueError("uri must be bounded text without whitespace, controls, or backslashes")
    if _INVALID_PERCENT_ESCAPE.search(uri):
        raise ValueError("uri contains an invalid percent escape")
    try:
        parsed = urlsplit(uri)
        # Accessing these properties also validates malformed ports and bracketed hosts.
        _ = parsed.hostname
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("uri is malformed") from exc
    if not _URI_SCHEME.fullmatch(parsed.scheme):
        raise ValueError("uri must be absolute and include a valid scheme")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("uri must not contain user information")
    if parsed.fragment:
        raise ValueError("uri must not contain a fragment")
    if parsed.scheme.lower() == "file":
        if parsed.query or not parsed.path.startswith("/"):
            raise ValueError("file uri must contain an absolute path without a query")
    elif not parsed.netloc:
        raise ValueError("non-file uri must include an authority")
    return uri


@dataclass(frozen=True, slots=True)
class ArtifactReference:
    """Reference large artifacts without embedding their bytes in events."""

    uri: str
    sha256: str
    size_bytes: int
    media_type: str = "application/octet-stream"
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_uri(self.uri)
        if not isinstance(self.sha256, str) or not _SHA256.fullmatch(self.sha256):
            raise ValueError("sha256 must be 64 lowercase hexadecimal characters")
        if (
            not isinstance(self.size_bytes, int)
            or isinstance(self.size_bytes, bool)
            or self.size_bytes < 0
        ):
            raise ValueError("size_bytes must be a non-negative integer")
        if (
            not isinstance(self.media_type, str)
            or len(self.media_type) > 255
            or not _MEDIA_TYPE.fullmatch(self.media_type)
        ):
            raise ValueError("media_type must be a bounded type/subtype")
        if not isinstance(self.metadata, Mapping):
            raise ValueError("metadata must be a mapping")
        if len(self.metadata) > _MAX_METADATA_ITEMS:
            raise ValueError("metadata contains too many items")
        metadata = dict(self.metadata)
        if any(
            not isinstance(key, str)
            or not isinstance(value, str)
            or not key
            or len(key) > _MAX_METADATA_KEY_LENGTH
            or len(value) > _MAX_METADATA_VALUE_LENGTH
            or _contains_unsafe_text(key)
            or any(ord(character) < 32 or ord(character) == 127 for character in value)
            for key, value in metadata.items()
        ):
            raise ValueError("metadata keys and values must be safe bounded strings")
        object.__setattr__(self, "metadata", MappingProxyType(metadata))

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""

        return {
            "uri": self.uri,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "media_type": self.media_type,
            "metadata": dict(self.metadata),
        }
