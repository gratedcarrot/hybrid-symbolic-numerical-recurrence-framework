"""
analyzer.py

Numerical analysis utilities used by both exact-solver and simulation-fallback modes.
"""

from __future__ import annotations

from typing import List
import math

Number = int | float


def first_differences(seq: List[Number]) -> List[Number]:
    return [seq[i] - seq[i - 1] for i in range(1, len(seq))]


def second_differences(seq: List[Number]) -> List[Number]:
    first = first_differences(seq)
    return [first[i] - first[i - 1] for i in range(1, len(first))]


def ratio_an_over_prev(seq: List[Number]) -> List[float]:
    ratios: List[float] = []
    for i in range(1, len(seq)):
        if seq[i - 1] == 0:
            ratios.append(float("inf"))
        else:
            ratios.append(float(seq[i] / seq[i - 1]))
    return ratios


def ratio_an_over_n(seq: List[Number], index_start: int = 0) -> List[float]:
    out: List[float] = []
    for i, value in enumerate(seq):
        n = index_start + i
        out.append(float("inf") if n == 0 else float(value / n))
    return out


def is_monotonic_non_decreasing(seq: List[Number]) -> bool:
    return all(seq[i] >= seq[i - 1] for i in range(1, len(seq)))


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def classify_numbers(values: List[int]) -> List[str]:
    labels: List[str] = []
    for x in values:
        if x == 1:
            labels.append("1")
        elif is_prime(int(x)):
            labels.append("prime")
        else:
            labels.append("composite")
    return labels


def digit_count(value: Number) -> int:
    value = int(abs(value))
    if value == 0:
        return 1
    return len(str(value))


def safe_log10(value: Number) -> float:
    try:
        return math.log10(abs(float(value)) + 1.0)
    except Exception:
        return 0.0


def growth_observation(seq: List[Number]) -> str:
    if len(seq) < 4:
        return "Insufficient terms for growth observation"

    abs_values = [abs(x) for x in seq]
    if all(x == 0 for x in abs_values):
        return "Zero sequence"

    increasing = all(abs_values[i] <= abs_values[i + 1] for i in range(len(abs_values) - 1))
    last_digits = digit_count(seq[-1])
    mid_digits = digit_count(seq[len(seq) // 2])

    ratios = ratio_an_over_prev(seq)
    finite_ratios = [r for r in ratios[-5:] if math.isfinite(r)]
    if finite_ratios:
        spread = max(finite_ratios) - min(finite_ratios)
        if spread < 1e-6 and abs(finite_ratios[-1]) > 1:
            return f"Approximately exponential growth; recent ratio stabilizes near {finite_ratios[-1]:.6g}"

    if last_digits > mid_digits + 20:
        return "Very rapid growth observed"
    if increasing and last_digits > mid_digits:
        return "Increasing growth observed"
    if increasing:
        return "Monotonic non-decreasing pattern observed"
    return "Non-monotonic or mixed growth pattern observed"
