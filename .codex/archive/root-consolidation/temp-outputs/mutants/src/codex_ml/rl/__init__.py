"""Reinforcement learning agents for Codex."""

from .scripted_agent import ScriptedAgent
from .simple_agent import RandomAgent

__all__ = ["RandomAgent", "ScriptedAgent"]
