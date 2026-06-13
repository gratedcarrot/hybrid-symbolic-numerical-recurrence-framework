from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import sympy as sp

from .cases import RecurrenceCase, n
from .simulator import generate_sequence


@dataclass
class SymbolicResult:
    case_id: str
    status: str
    closed_form: str
    simplified_closed_form: Optional[sp.Expr]
    method: str
    verification_status: str
    match_count: int
    terms_checked: int
    message: str


def _safe_int_from_sympy(value: sp.Expr) -> int:
    """Convert a symbolic value to an integer when it is mathematically integral."""

    simplified = sp.simplify(value)
    try:
        return int(simplified)
    except Exception:
        numeric = complex(sp.N(simplified, 60))
        if abs(numeric.imag) < 1e-8:
            rounded = round(numeric.real)
            if abs(numeric.real - rounded) < 1e-6:
                return int(rounded)
    raise ValueError(f"Could not safely convert symbolic value {value!r} to int")


def _first_order_closed_form(case: RecurrenceCase) -> sp.Expr:
    if not case.coefficients or case.forcing_expr is None:
        raise ValueError("First-order solver requires coefficient and forcing expression")
    r = sp.Integer(case.coefficients[0])
    f = sp.sympify(case.forcing_expr)
    a0 = sp.Integer(case.initial_conditions[0])
    i = sp.symbols("i", integer=True, positive=True)

    # a_n = r^n a_0 + sum_{i=1}^{n} r^{n-i} f(i)
    expr = r**n * a0 + sp.summation(r ** (n - i) * f.subs(n, i), (i, 1, n))
    return sp.simplify(expr)


def _homogeneous_constant_coeff_closed_form(case: RecurrenceCase) -> sp.Expr:
    if not case.coefficients:
        raise ValueError("Homogeneous solver requires coefficients")

    k = len(case.coefficients)
    x = sp.symbols("lambda")
    poly = x**k
    for idx, coeff in enumerate(case.coefficients):
        poly -= sp.Integer(coeff) * x ** (k - idx - 1)

    roots = sp.roots(sp.Poly(poly, x))
    if sum(roots.values()) != k:
        # Fall back to symbolic roots if exact multiplicities are not expanded.
        root_list = sp.Poly(poly, x).all_roots()
        roots = {}
        for root in root_list:
            roots[root] = roots.get(root, 0) + 1

    constants: List[sp.Symbol] = []
    expr = sp.Integer(0)
    c_index = 0
    for root, multiplicity in roots.items():
        for power in range(multiplicity):
            c = sp.symbols(f"C{c_index}")
            constants.append(c)
            expr += c * (n**power) * (root**n)
            c_index += 1

    equations = []
    for idx, value in sorted(case.initial_conditions.items())[:k]:
        equations.append(sp.Eq(expr.subs(n, idx), sp.Integer(value)))

    solutions = sp.solve(equations, constants, dict=True, simplify=True)
    if not solutions:
        raise ValueError("Could not solve constants for closed form")

    expr = sp.simplify(expr.subs(solutions[0]))
    return expr


def solve_symbolically(case: RecurrenceCase, verification_terms: int = 20) -> SymbolicResult:
    """Solve a supported recurrence and verify the result against generated terms."""

    if case.expected_mode != "Symbolic":
        return SymbolicResult(
            case.case_id,
            "FALLBACK",
            "N/A",
            None,
            "simulation fallback",
            "N/A",
            0,
            0,
            "Not a supported symbolic case",
        )

    try:
        if case.symbolic_strategy == "first_order_linear":
            expr = _first_order_closed_form(case)
            method = "summation formula for first-order linear recurrence"
        elif case.symbolic_strategy == "homogeneous_constant_coeff":
            expr = _homogeneous_constant_coeff_closed_form(case)
            method = "characteristic-polynomial method"
        else:
            raise ValueError(f"Unsupported symbolic strategy: {case.symbolic_strategy}")
    except Exception as exc:
        return SymbolicResult(
            case.case_id,
            "ERROR",
            "N/A",
            None,
            "none",
            "FAIL",
            0,
            verification_terms,
            str(exc),
        )

    sequence = generate_sequence(case, n_terms=verification_terms)
    match_count = 0
    checked = 0
    mismatches = []
    for idx, recurrence_value in sequence.terms:
        try:
            symbolic_value = _safe_int_from_sympy(expr.subs(n, idx))
        except Exception as exc:
            mismatches.append(f"n={idx}: evaluation error {exc}")
            checked += 1
            continue
        checked += 1
        if symbolic_value == recurrence_value:
            match_count += 1
        else:
            mismatches.append(f"n={idx}: symbolic={symbolic_value}, recurrence={recurrence_value}")

    verification = "PASS" if match_count == checked else "FAIL"
    message = "verified" if verification == "PASS" else "; ".join(mismatches[:3])

    return SymbolicResult(
        case.case_id,
        "SOLVED" if verification == "PASS" else "SOLVED_WITH_MISMATCH",
        sp.sstr(sp.simplify(expr)),
        expr,
        method,
        verification,
        match_count,
        checked,
        message,
    )
