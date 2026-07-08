"""Seed utilities for deterministic operations.

This module now forwards seeding to centralized helpers in
codex_ml.utils.seeding to avoid duplication and drift.
"""

from __future__ import annotations

import random
from collections.abc import MutableSequence, Sequence
from typing import TypeVar

from codex_ml.utils.seeding import set_deterministic as _set_deterministic
from codex_ml.utils.seeding import set_reproducible as _set_reproducible

T = TypeVar("T")


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_deterministic_shuffle__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_deterministic_shuffle__mutmut)
def deterministic_shuffle(seq: Sequence[T], seed: int) -> list[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = list(seq)
    rng = random.Random(seed)  # nosec B311 - deterministic utility shuffle
    rng.shuffle(items)
    return list(items)


def x_deterministic_shuffle__mutmut_orig(seq: Sequence[T], seed: int) -> list[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = list(seq)
    rng = random.Random(seed)  # nosec B311 - deterministic utility shuffle
    rng.shuffle(items)
    return list(items)


def x_deterministic_shuffle__mutmut_1(seq: Sequence[T], seed: int) -> list[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = None
    rng = random.Random(seed)  # nosec B311 - deterministic utility shuffle
    rng.shuffle(items)
    return list(items)


def x_deterministic_shuffle__mutmut_2(seq: Sequence[T], seed: int) -> list[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = list(None)
    rng = random.Random(seed)  # nosec B311 - deterministic utility shuffle
    rng.shuffle(items)
    return list(items)


def x_deterministic_shuffle__mutmut_3(seq: Sequence[T], seed: int) -> list[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = list(seq)
    rng = None  # nosec B311 - deterministic utility shuffle
    rng.shuffle(items)
    return list(items)


def x_deterministic_shuffle__mutmut_4(seq: Sequence[T], seed: int) -> list[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = list(seq)
    rng = random.Random(None)  # nosec B311 - deterministic utility shuffle
    rng.shuffle(items)
    return list(items)


def x_deterministic_shuffle__mutmut_5(seq: Sequence[T], seed: int) -> list[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = list(seq)
    rng = random.Random(seed)  # nosec B311 - deterministic utility shuffle
    rng.shuffle(None)
    return list(items)


def x_deterministic_shuffle__mutmut_6(seq: Sequence[T], seed: int) -> list[T]:
    """Return a shuffled copy of *seq* using ``seed`` for randomness.

    The original sequence is left unmodified. A :class:`random.Random` instance
    seeded with ``seed`` performs the shuffling to ensure deterministic
    behaviour across runs.
    """

    items: MutableSequence[T] = list(seq)
    rng = random.Random(seed)  # nosec B311 - deterministic utility shuffle
    rng.shuffle(items)
    return list(None)

mutants_x_deterministic_shuffle__mutmut['_mutmut_orig'] = x_deterministic_shuffle__mutmut_orig # type: ignore # mutmut generated
mutants_x_deterministic_shuffle__mutmut['x_deterministic_shuffle__mutmut_1'] = x_deterministic_shuffle__mutmut_1 # type: ignore # mutmut generated
mutants_x_deterministic_shuffle__mutmut['x_deterministic_shuffle__mutmut_2'] = x_deterministic_shuffle__mutmut_2 # type: ignore # mutmut generated
mutants_x_deterministic_shuffle__mutmut['x_deterministic_shuffle__mutmut_3'] = x_deterministic_shuffle__mutmut_3 # type: ignore # mutmut generated
mutants_x_deterministic_shuffle__mutmut['x_deterministic_shuffle__mutmut_4'] = x_deterministic_shuffle__mutmut_4 # type: ignore # mutmut generated
mutants_x_deterministic_shuffle__mutmut['x_deterministic_shuffle__mutmut_5'] = x_deterministic_shuffle__mutmut_5 # type: ignore # mutmut generated
mutants_x_deterministic_shuffle__mutmut['x_deterministic_shuffle__mutmut_6'] = x_deterministic_shuffle__mutmut_6 # type: ignore # mutmut generated
mutants_x_set_seed__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_set_seed__mutmut)
def set_seed(seed: int, *, deterministic: bool = True) -> None:
    """Forward seeding to centralized helpers for deterministic behaviour."""

    _set_reproducible(seed, deterministic=deterministic)
    _set_deterministic(deterministic)


def x_set_seed__mutmut_orig(seed: int, *, deterministic: bool = True) -> None:
    """Forward seeding to centralized helpers for deterministic behaviour."""

    _set_reproducible(seed, deterministic=deterministic)
    _set_deterministic(deterministic)


def x_set_seed__mutmut_1(seed: int, *, deterministic: bool = False) -> None:
    """Forward seeding to centralized helpers for deterministic behaviour."""

    _set_reproducible(seed, deterministic=deterministic)
    _set_deterministic(deterministic)


def x_set_seed__mutmut_2(seed: int, *, deterministic: bool = True) -> None:
    """Forward seeding to centralized helpers for deterministic behaviour."""

    _set_reproducible(None, deterministic=deterministic)
    _set_deterministic(deterministic)


def x_set_seed__mutmut_3(seed: int, *, deterministic: bool = True) -> None:
    """Forward seeding to centralized helpers for deterministic behaviour."""

    _set_reproducible(seed, deterministic=None)
    _set_deterministic(deterministic)


def x_set_seed__mutmut_4(seed: int, *, deterministic: bool = True) -> None:
    """Forward seeding to centralized helpers for deterministic behaviour."""

    _set_reproducible(deterministic=deterministic)
    _set_deterministic(deterministic)


def x_set_seed__mutmut_5(seed: int, *, deterministic: bool = True) -> None:
    """Forward seeding to centralized helpers for deterministic behaviour."""

    _set_reproducible(seed, )
    _set_deterministic(deterministic)


def x_set_seed__mutmut_6(seed: int, *, deterministic: bool = True) -> None:
    """Forward seeding to centralized helpers for deterministic behaviour."""

    _set_reproducible(seed, deterministic=deterministic)
    _set_deterministic(None)

mutants_x_set_seed__mutmut['_mutmut_orig'] = x_set_seed__mutmut_orig # type: ignore # mutmut generated
mutants_x_set_seed__mutmut['x_set_seed__mutmut_1'] = x_set_seed__mutmut_1 # type: ignore # mutmut generated
mutants_x_set_seed__mutmut['x_set_seed__mutmut_2'] = x_set_seed__mutmut_2 # type: ignore # mutmut generated
mutants_x_set_seed__mutmut['x_set_seed__mutmut_3'] = x_set_seed__mutmut_3 # type: ignore # mutmut generated
mutants_x_set_seed__mutmut['x_set_seed__mutmut_4'] = x_set_seed__mutmut_4 # type: ignore # mutmut generated
mutants_x_set_seed__mutmut['x_set_seed__mutmut_5'] = x_set_seed__mutmut_5 # type: ignore # mutmut generated
mutants_x_set_seed__mutmut['x_set_seed__mutmut_6'] = x_set_seed__mutmut_6 # type: ignore # mutmut generated


__all__ = ["deterministic_shuffle", "set_seed"]
