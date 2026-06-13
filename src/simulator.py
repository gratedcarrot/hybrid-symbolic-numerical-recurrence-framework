from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .cases import RecurrenceCase


@dataclass
class SequenceResult:
    case_id: str
    terms: List[Tuple[int, int]]
    overflowed: bool
    stop_reason: str


def generate_sequence(
    case: RecurrenceCase,
    n_terms: int = 30,
    max_abs: int = 10**120,
    max_digits: int = 2000,
) -> SequenceResult:
    """Generate recurrence terms safely using the recurrence definition.

    The generator starts from the smallest supplied initial index. It stops early
    if values exceed the configured magnitude/digit guard.
    """

    if not case.initial_conditions:
        raise ValueError(f"{case.case_id}: missing initial conditions")

    values: Dict[int, int] = dict(case.initial_conditions)
    start = min(values)
    terms: List[Tuple[int, int]] = []
    overflowed = False
    stop_reason = "completed"

    for idx in range(start, start + n_terms):
        if idx not in values:
            try:
                values[idx] = int(case.recurrence_func(idx, values))
            except KeyError as exc:
                raise ValueError(
                    f"{case.case_id}: insufficient initial conditions for index {idx}; missing {exc}"
                ) from exc

        value = values[idx]
        terms.append((idx, value))

        if abs(value) > max_abs:
            overflowed = True
            stop_reason = f"stopped: |a_n| exceeded {max_abs}"
            break
        if len(str(abs(value))) > max_digits:
            overflowed = True
            stop_reason = f"stopped: digit length exceeded {max_digits}"
            break

    return SequenceResult(case.case_id, terms, overflowed, stop_reason)
