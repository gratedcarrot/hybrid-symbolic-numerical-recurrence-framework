"""
core_engine.py

Iterative recurrence sequence generation.
This engine is intentionally separate from symbolic solving so that
closed-form results can be verified against direct recurrence generation.
"""

from __future__ import annotations

from typing import Callable, List

Number = int | float


def normalize_number(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def generate_sequence(
    initial_terms: List[Number],
    next_term_fn: Callable[[int, List[Number]], Number],
    total_terms: int,
    index_start: int = 0,
) -> List[Number]:
    """
    Generate sequence terms using an iterative recurrence rule.

    If initial_terms represent a_0, a_1, ..., then index_start=0.
    If initial_terms represent a_1, a_2, ..., then index_start=1.

    The next_term_fn receives:
        n   -> mathematical index of the term currently being generated
        seq -> sequence terms already generated
    """

    if total_terms <= 0:
        raise ValueError("total_terms must be positive")
    if not initial_terms:
        raise ValueError("At least one initial term is required")
    if total_terms <= len(initial_terms):
        return list(initial_terms[:total_terms])

    seq = list(initial_terms)
    while len(seq) < total_terms:
        n = index_start + len(seq)
        seq.append(normalize_number(next_term_fn(n, seq)))
    return seq
