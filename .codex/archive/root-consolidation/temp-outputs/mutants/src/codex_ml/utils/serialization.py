"""Serialization utilities for converting objects to dictionaries."""

from typing import Any


class DictSerializable:
    """Mixin class providing dict serialization capability.

    Automatically converts object attributes to dictionary,
    excluding None values and private attributes.

    Usage:
        @dataclass
        class MyModel(DictSerializable):
            name: str
            value: int = None

        model = MyModel(name="test", value=42)
        data = model.to_dict()  # {"name": "test", "value": 42}
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert object to dictionary representation.

        Returns:
            Dictionary with non-None public attributes
        """
        result = {}
        for key, value in self.__dict__.items():
            # Skip private attributes
            if key.startswith("_"):
                continue
            # Skip None values
            if value is not None:
                # Handle nested DictSerializable objects
                if isinstance(value, DictSerializable):
                    result[key] = value.to_dict()
                # Handle lists of DictSerializable objects
                elif isinstance(value, list) and value and isinstance(value[0], DictSerializable):
                    result[key] = [v.to_dict() for v in value]  # type: ignore[assignment]
                else:
                    result[key] = value
        return result
