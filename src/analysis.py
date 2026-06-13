from __future__ import annotations

from dataclasses import dataclass
from math import log, sqrt
from statistics import mean, median, pstdev
from typing import Dict, List, Optional, Tuple

import sympy as sp

from .cases import RecurrenceCase
from .simulator import SequenceResult


@dataclass
class BehaviourIndicators:
    case_id: str
    first_terms: str
    first_differences: str
    second_differences: str
    ratio_summary: str
    log_growth_slope: Optional[float]
    digit_length_start: int
    digit_length_end: int
    monotonicity: str
    periodicity: str
    spike_count: int
    growth_class: str
    overflowed: bool
    stop_reason: str


def _values(sequence: SequenceResult) -> List[int]:
    return [value for _, value in sequence.terms]


def _differences(values: List[int]) -> List[int]:
    return [values[i] - values[i - 1] for i in range(1, len(values))]


def _ratios(values: List[int]) -> List[Optional[float]]:
    ratios: List[Optional[float]] = []
    for i in range(1, len(values)):
        prev = values[i - 1]
        curr = values[i]
        if prev == 0:
            ratios.append(None)
            continue
        # Avoid float overflow for very large integers.
        if abs(prev).bit_length() > 900 or abs(curr).bit_length() > 900:
            ratios.append(None)
        else:
            ratios.append(float(curr / prev))
    return ratios


def _ratio_summary(ratios: List[Optional[float]]) -> str:
    valid = [r for r in ratios if r is not None]
    if not valid:
        return "undefined"
    tail = valid[-5:] if len(valid) >= 5 else valid
    return f"tail_mean={mean(tail):.6g}, tail_std={(pstdev(tail) if len(tail) > 1 else 0):.6g}"


def _log_growth_slope(values: List[int]) -> Optional[float]:
    if len(values) < 3:
        return None
    xs = list(range(len(values)))
    ys = [log(abs(v) + 1) for v in values]
    x_bar = mean(xs)
    y_bar = mean(ys)
    denom = sum((x - x_bar) ** 2 for x in xs)
    if denom == 0:
        return None
    return sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denom


def _monotonicity(values: List[int]) -> str:
    if all(values[i] > values[i - 1] for i in range(1, len(values))):
        return "strictly increasing"
    if all(values[i] >= values[i - 1] for i in range(1, len(values))):
        return "non-decreasing"
    if all(values[i] < values[i - 1] for i in range(1, len(values))):
        return "strictly decreasing"
    if all(values[i] <= values[i - 1] for i in range(1, len(values))):
        return "non-increasing"
    return "mixed/oscillatory"


def _periodicity(values: List[int], max_period: int = 20) -> str:
    if len(values) < 6:
        return "not enough terms"
    for period in range(1, min(max_period, len(values) // 2) + 1):
        if values[-period:] == values[-2 * period : -period]:
            return f"tail-cycle period {period}"
    return "not detected"


def _spike_count(diffs: List[int]) -> int:
    if len(diffs) < 4:
        return 0
    abs_diffs = [abs(d) for d in diffs]
    med = median(abs_diffs)
    deviations = [abs(x - med) for x in abs_diffs]
    mad = median(deviations)
    if mad == 0:
        threshold = med * 3 if med != 0 else 1
    else:
        threshold = med + 3 * mad
    return sum(1 for x in abs_diffs if x > threshold)


def _is_constant(seq: List[int]) -> bool:
    return bool(seq) and all(x == seq[0] for x in seq)


def classify_growth(case: RecurrenceCase, values: List[int], overflowed: bool) -> str:
    if not values:
        return "unknown"
    diffs = _differences(values)
    second = _differences(diffs)
    ratios = [r for r in _ratios(values) if r is not None]
    periodicity = _periodicity(values)

    if case.special_operator == "gcd":
        return "irregular number-theoretic"
    if "tail-cycle" in periodicity or case.special_operator == "mod":
        return "periodic/cyclic"
    if overflowed or case.special_operator == "power":
        return "explosive nonlinear"
    if _is_constant(diffs):
        return "linear"
    if _is_constant(second):
        return "quadratic/polynomial"

    # Detect higher-degree polynomial behaviour through finite differences.
    current_diff = second
    for degree in range(3, 6):
        current_diff = _differences(current_diff)
        if _is_constant(current_diff):
            return f"degree-{degree} polynomial-like"

    if ratios:
        tail = ratios[-5:] if len(ratios) >= 5 else ratios
        if len(tail) >= 3 and abs(mean(tail) - 1.61803398875) < 0.05:
            return "Fibonacci-like exponential"
        if len(tail) >= 3 and pstdev(tail) < 0.02 * max(1, abs(mean(tail))):
            return "geometric/exponential"
        if len(ratios) >= 5 and all(ratios[i] <= ratios[i + 1] for i in range(len(ratios) - 1)):
            return "super-exponential/factorial-like"
    if case.special_operator == "variable_coefficient":
        return "factorial-like variable-coefficient"
    return "irregular/mixed"


def analyse_sequence(case: RecurrenceCase, sequence: SequenceResult) -> BehaviourIndicators:
    values = _values(sequence)
    diffs = _differences(values)
    second = _differences(diffs)
    ratios = _ratios(values)
    first_terms = ", ".join(str(v) for v in values[:8])
    digit_lengths = [len(str(abs(v))) for v in values] if values else [0]

    growth_class = classify_growth(case, values, sequence.overflowed)
    smooth_classes = {
        "linear",
        "quadratic/polynomial",
        "degree-3 polynomial-like",
        "degree-4 polynomial-like",
        "degree-5 polynomial-like",
        "geometric/exponential",
        "Fibonacci-like exponential",
        "super-exponential/factorial-like",
        "factorial-like variable-coefficient",
    }
    spike_count = 0 if growth_class in smooth_classes else _spike_count(diffs)

    return BehaviourIndicators(
        case_id=case.case_id,
        first_terms=first_terms,
        first_differences=", ".join(str(v) for v in diffs[:8]),
        second_differences=", ".join(str(v) for v in second[:8]),
        ratio_summary=_ratio_summary(ratios),
        log_growth_slope=round(_log_growth_slope(values), 6) if _log_growth_slope(values) is not None else None,
        digit_length_start=digit_lengths[0],
        digit_length_end=digit_lengths[-1],
        monotonicity=_monotonicity(values),
        periodicity=_periodicity(values),
        spike_count=spike_count,
        growth_class=growth_class,
        overflowed=sequence.overflowed,
        stop_reason=sequence.stop_reason,
    )


def is_prime_int(x: int) -> bool:
    if x < 2:
        return False
    return bool(sp.isprime(x))


def rowland_jump_rows(case: RecurrenceCase, sequence: SequenceResult) -> List[Dict[str, object]]:
    values = sequence.terms
    rows: List[Dict[str, object]] = []
    for i in range(1, len(values)):
        n_value, current = values[i]
        _, previous = values[i - 1]
        increment = current - previous
        if increment == 1:
            label = "trivial_one"
        elif is_prime_int(increment):
            label = "nontrivial_prime_jump"
        else:
            label = "nontrivial_composite_jump"
        rows.append(
            {
                "case_id": case.case_id,
                "n": n_value,
                "a_previous": previous,
                "a_current": current,
                "increment": increment,
                "increment_class": label,
                "is_prime_increment": is_prime_int(increment),
            }
        )
    return rows
