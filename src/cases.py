from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Callable, Dict, List, Optional

import sympy as sp

n = sp.symbols("n", integer=True, nonnegative=True)


@dataclass(frozen=True)
class RecurrenceCase:
    """Structured recurrence case used by the experiments.

    The recurrence function receives the current index n and a dictionary
    containing previously generated values {index: value}.
    """

    case_id: str
    relation: str
    initial_conditions: Dict[int, int]
    order: int
    coefficients: Optional[List[int]]
    forcing_expr: Optional[sp.Expr]
    recurrence_func: Callable[[int, Dict[int, int]], int]
    expected_mode: str
    recurrence_type: str
    purpose: str
    symbolic_strategy: str = "none"
    special_operator: str = "none"


def get_cases() -> List[RecurrenceCase]:
    """Return the expanded C1-C14 benchmark suite."""

    return [
        RecurrenceCase(
            "C1",
            "a_n = 2a_{n-1}, a_0 = 1",
            {0: 1},
            1,
            [2],
            sp.Integer(0),
            lambda i, a: 2 * a[i - 1],
            "Symbolic",
            "first-order homogeneous linear",
            "baseline geometric recurrence",
            "first_order_linear",
        ),
        RecurrenceCase(
            "C2",
            "a_n = 2a_{n-1} + 3, a_0 = 1",
            {0: 1},
            1,
            [2],
            sp.Integer(3),
            lambda i, a: 2 * a[i - 1] + 3,
            "Symbolic",
            "first-order non-homogeneous linear",
            "constant non-homogeneous term",
            "first_order_linear",
        ),
        RecurrenceCase(
            "C3",
            "a_n = a_{n-1} + 5, a_0 = 2",
            {0: 2},
            1,
            [1],
            sp.Integer(5),
            lambda i, a: a[i - 1] + 5,
            "Symbolic",
            "arithmetic progression",
            "linear additive growth",
            "first_order_linear",
        ),
        RecurrenceCase(
            "C4",
            "a_n = 2a_{n-1} + n, a_0 = 1",
            {0: 1},
            1,
            [2],
            n,
            lambda i, a: 2 * a[i - 1] + i,
            "Symbolic",
            "first-order index-dependent linear",
            "index-term non-homogeneous recurrence",
            "first_order_linear",
        ),
        RecurrenceCase(
            "C5",
            "a_n = a_{n-1} + a_{n-2}, a_0 = 0, a_1 = 1",
            {0: 0, 1: 1},
            2,
            [1, 1],
            sp.Integer(0),
            lambda i, a: a[i - 1] + a[i - 2],
            "Symbolic",
            "second-order homogeneous linear",
            "Fibonacci-type recurrence",
            "homogeneous_constant_coeff",
        ),
        RecurrenceCase(
            "C6",
            "a_n = 3a_{n-1} - 2a_{n-2}, a_0 = 1, a_1 = 2",
            {0: 1, 1: 2},
            2,
            [3, -2],
            sp.Integer(0),
            lambda i, a: 3 * a[i - 1] - 2 * a[i - 2],
            "Symbolic",
            "second-order homogeneous linear",
            "distinct characteristic-root recurrence",
            "homogeneous_constant_coeff",
        ),
        RecurrenceCase(
            "C7",
            "a_n = 6a_{n-1} - 11a_{n-2} + 6a_{n-3}, a_0 = 3, a_1 = 6, a_2 = 14",
            {0: 3, 1: 6, 2: 14},
            3,
            [6, -11, 6],
            sp.Integer(0),
            lambda i, a: 6 * a[i - 1] - 11 * a[i - 2] + 6 * a[i - 3],
            "Symbolic",
            "third-order homogeneous linear",
            "higher-order symbolic recurrence with distinct characteristic roots",
            "homogeneous_constant_coeff",
        ),
        RecurrenceCase(
            "C8",
            "a_n = 2a_{n-1} - a_{n-2}, a_0 = 1, a_1 = 3",
            {0: 1, 1: 3},
            2,
            [2, -1],
            sp.Integer(0),
            lambda i, a: 2 * a[i - 1] - a[i - 2],
            "Symbolic",
            "second-order repeated-root linear",
            "repeated characteristic root",
            "homogeneous_constant_coeff",
        ),
        RecurrenceCase(
            "C9",
            "a_n = a_{n-1} + n^2, a_0 = 0",
            {0: 0},
            1,
            [1],
            n**2,
            lambda i, a: a[i - 1] + i**2,
            "Symbolic",
            "first-order polynomial non-homogeneous linear",
            "polynomial forcing term",
            "first_order_linear",
        ),
        RecurrenceCase(
            "C10",
            "a_n = 3a_{n-1} - 3a_{n-2} + a_{n-3}, a_0 = 1, a_1 = 2, a_2 = 4",
            {0: 1, 1: 2, 2: 4},
            3,
            [3, -3, 1],
            sp.Integer(0),
            lambda i, a: 3 * a[i - 1] - 3 * a[i - 2] + a[i - 3],
            "Symbolic",
            "third-order repeated-root linear",
            "higher-order repeated-root symbolic case",
            "homogeneous_constant_coeff",
        ),
        RecurrenceCase(
            "C11",
            "a_n = n a_{n-1}, a_0 = 1",
            {0: 1},
            1,
            None,
            None,
            lambda i, a: i * a[i - 1],
            "Fallback",
            "variable-coefficient recurrence",
            "factorial-like growth pattern",
            "none",
            "variable_coefficient",
        ),
        RecurrenceCase(
            "C12",
            "a_n = a_{n-1} + gcd(n, a_{n-1}), a_1 = 7",
            {1: 7},
            1,
            None,
            None,
            lambda i, a: a[i - 1] + gcd(i, a[i - 1]),
            "Fallback",
            "Rowland gcd number-theoretic recurrence",
            "increment and prime-jump diagnostics",
            "none",
            "gcd",
        ),
        RecurrenceCase(
            "C13",
            "a_n = (a_{n-1})^2 + 1, a_0 = 1",
            {0: 1},
            1,
            None,
            None,
            lambda i, a: a[i - 1] ** 2 + 1,
            "Fallback",
            "nonlinear square recurrence",
            "explosive nonlinear growth and divergence guard",
            "none",
            "power",
        ),
        RecurrenceCase(
            "C14",
            "a_n = (a_{n-1} + 2) mod 5, a_0 = 0",
            {0: 0},
            1,
            None,
            None,
            lambda i, a: (a[i - 1] + 2) % 5,
            "Fallback",
            "modular periodic recurrence",
            "periodicity and tail-cycle detection",
            "none",
            "mod",
        ),
    ]
