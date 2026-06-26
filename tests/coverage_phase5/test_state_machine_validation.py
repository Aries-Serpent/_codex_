"""Test state machine validation across components."""

from __future__ import annotations

from enum import Enum


class State(Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    PROCESSING = "processing"
    CLOSING = "closing"
    CLOSED = "closed"
    ERROR = "error"


class StateMachine:
    VALID_TRANSITIONS = {
        State.IDLE: {State.CONNECTING, State.ERROR},
        State.CONNECTING: {State.CONNECTED, State.ERROR, State.IDLE},
        State.CONNECTED: {State.PROCESSING, State.CLOSING, State.ERROR},
        State.PROCESSING: {State.CONNECTED, State.ERROR},
        State.CLOSING: {State.CLOSED, State.ERROR},
        State.CLOSED: set(),
        State.ERROR: {State.IDLE},
    }

    def __init__(self):
        self.state = State.IDLE
        self.history: list[State] = [State.IDLE]

    def transition(self, new_state: State) -> bool:
        if new_state not in self.VALID_TRANSITIONS[self.state]:
            return False
        self.state = new_state
        self.history.append(new_state)
        return True

    def can_transition_to(self, state: State) -> bool:
        return state in self.VALID_TRANSITIONS[self.state]


def test_valid_transition():
    """Test valid state transition."""
    sm = StateMachine()
    result = sm.transition(State.CONNECTING)

    assert result is True, "Result must not be empty"
    assert sm.state == State.CONNECTING, "state is not valid"


def test_invalid_transition():
    """Test invalid state transition."""
    sm = StateMachine()
    sm.transition(State.CONNECTING)

    result = sm.transition(State.PROCESSING)

    assert result is False, "Result must not be empty"
    assert sm.state == State.CONNECTING, "state is not valid"


def test_valid_path_connect_disconnect():
    """Test valid connection path."""
    sm = StateMachine()

    assert sm.transition(State.CONNECTING), "Condition must be true"
    assert sm.transition(State.CONNECTED), "Condition must be true"
    assert sm.transition(State.CLOSING), "Condition must be true"
    assert sm.transition(State.CLOSED), "Condition must be true"

    assert sm.state == State.CLOSED, "state is not valid"


def test_error_recovery():
    """Test error state and recovery."""
    sm = StateMachine()

    sm.transition(State.CONNECTING)
    sm.transition(State.ERROR)

    assert sm.state == State.ERROR, "Error should be raised or set"
    assert sm.transition(State.IDLE), "Condition must be true"


def test_transition_history():
    """Test state transition history."""
    sm = StateMachine()

    sm.transition(State.CONNECTING)
    sm.transition(State.CONNECTED)
    sm.transition(State.PROCESSING)
    sm.transition(State.CONNECTED)

    assert len(sm.history) == 5, "Collection must not be empty"
    assert sm.history[0] == State.IDLE, "Condition must be true"
    assert sm.history[-1] == State.CONNECTED, "Condition must be true"


def test_can_transition_check():
    """Test can_transition_to check."""
    sm = StateMachine()

    assert sm.can_transition_to(State.CONNECTING), "Condition must be true"
    assert not sm.can_transition_to(State.CONNECTED), "Condition must be true"

    sm.transition(State.CONNECTING)
    assert sm.can_transition_to(State.CONNECTED), "Condition must be true"
