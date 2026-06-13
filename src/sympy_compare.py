from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import sympy as sp

from .cases import RecurrenceCase, n
from .simulator import generate_sequence
from .symbolic_solver import _safe_int_from_sympy


@dataclass
class SympyComparisonResult:
    case_id: str
    status: str
    sympy_closed_form: str
    match_status: str
    terms_checked: int
    message: str


def compare_with_sympy(case: RecurrenceCase, terms_checked: int = 20) -> SympyComparisonResult:
    """Use SymPy rsolve as an external reference for comparable symbolic cases."""

    if case.expected_mode != "Symbolic" or not case.coefficients:
        return SympyComparisonResult(case.case_id, "N/C", "N/A", "N/A", 0, "Fallback/non-comparable case")

    a = sp.Function("a")
    lhs = a(n)
    rhs = sp.Integer(0)
    for idx, coeff in enumerate(case.coefficients, start=1):
        rhs += sp.Integer(coeff) * a(n - idx)
    if case.forcing_expr is not None:
        rhs += sp.sympify(case.forcing_expr)
    equation = sp.Eq(lhs, rhs)

    init = {a(k): sp.Integer(v) for k, v in case.initial_conditions.items()}
    try:
        solution = sp.rsolve(equation, a(n), init)
    except Exception as exc:
        return SympyComparisonResult(case.case_id, "ERROR", "N/A", "FAIL", 0, str(exc))

    if solution is None:
        return SympyComparisonResult(case.case_id, "N/C", "N/A", "N/A", 0, "SymPy returned no solution")

    sequence = generate_sequence(case, n_terms=terms_checked)
    matches = 0
    checked = 0
    for idx, recurrence_value in sequence.terms:
        try:
            sympy_value = _safe_int_from_sympy(solution.subs(n, idx))
        except Exception as exc:
            return SympyComparisonResult(
                case.case_id, "ERROR", sp.sstr(solution), "FAIL", checked, f"evaluation error: {exc}"
            )
        checked += 1
        if sympy_value == recurrence_value:
            matches += 1

    status = "PASS" if matches == checked else "FAIL"
    return SympyComparisonResult(case.case_id, "COMPARABLE", sp.sstr(sp.simplify(solution)), status, checked, "checked")
