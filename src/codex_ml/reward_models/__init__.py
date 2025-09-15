"""Built-in reward model implementations."""

__all__ = ["LengthRewardModel"]


def __getattr__(name: str):  # pragma: no cover - thin shim
    if name == "LengthRewardModel":
        from .simple import LengthRewardModel as _LengthRewardModel

        return _LengthRewardModel
    raise AttributeError(name)
