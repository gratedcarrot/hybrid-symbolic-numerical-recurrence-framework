"""
classifier.py

Mathematical classifier for recurrence expressions.
The classifier determines whether an expression is eligible for exact solving
or should be routed to simulation fallback.
"""

from __future__ import annotations

from typing import Any, List
import re

import sympy as sp

from .models import ClassificationResult, ParsedRecurrence


def _special_operators(expression: str) -> List[str]:
    operators = []
    for name in ["gcd", "lcm", "floor", "ceil", "sqrt", "sin", "cos", "tan", "log", "exp", "mod"]:
        if re.search(rf"\b{name}\s*\(", expression) or (name == "mod" and "%" in expression):
            operators.append(name)
    return operators


def _depends_on_n(expr: Any) -> bool:
    n = sp.Symbol("n", integer=True, nonnegative=True)
    try:
        return n in expr.free_symbols
    except Exception:
        return False


def _contains_prev_symbols_in_special_function(expr: Any, previous_symbols: List[sp.Symbol]) -> bool:
    """Detect functions like sqrt(x1), sin(x1), floor(x1), etc."""
    if expr is None:
        return False
    for atom in expr.atoms(sp.Function):
        if any(sym in atom.free_symbols for sym in previous_symbols):
            return True
    return False


def classify(parsed: ParsedRecurrence) -> ClassificationResult:
    expr = parsed.sympy_expression
    order = parsed.order
    original = parsed.definition.expression
    normalized = parsed.normalized_expression
    special = _special_operators(original) + _special_operators(normalized)
    special = sorted(set(special))

    if expr is None:
        reason = "Expression contains unsupported symbolic operators or could not be parsed symbolically."
        if any(op in special for op in ["gcd", "lcm", "mod"]):
            reason = "Number-theoretic/special operator detected; exact closed-form solver is not applied."
        return ClassificationResult(
            order=order,
            is_linear=False,
            is_homogeneous=None,
            coefficient_type="undetermined",
            nonhomogeneous_type="undetermined",
            special_operators=special,
            solver_eligible=False,
            recommended_mode="simulation_fallback",
            reason=reason,
        )

    n = sp.Symbol("n", integer=True, nonnegative=True)
    x_symbols = [sp.Symbol(f"x{i}") for i in range(1, order + 1)]

    try:
        poly = sp.Poly(expr, *x_symbols)
        degree = poly.total_degree()
        contains_function_of_prev = _contains_prev_symbols_in_special_function(expr, x_symbols)
        is_linear = degree <= 1 and not contains_function_of_prev
    except Exception:
        is_linear = False

    coefficients: List[Any] = []
    coefficient_type = "undetermined"
    nonhomogeneous_part = None
    is_homogeneous = None
    nonhomogeneous_type = "undetermined"
    solver_eligible = False
    recommended_mode = "simulation_fallback"
    reason = "Nonlinear or unsupported recurrence; simulation fallback recommended."

    if is_linear:
        coefficients = [sp.simplify(expr.coeff(x)) for x in x_symbols]
        nonhomogeneous_part = sp.simplify(expr.subs({x: 0 for x in x_symbols}))

        coeffs_depend_on_n = any(_depends_on_n(c) for c in coefficients)
        coefficient_type = "constant" if not coeffs_depend_on_n else "variable/index-dependent"
        is_homogeneous = sp.simplify(nonhomogeneous_part) == 0

        if is_homogeneous:
            nonhomogeneous_type = "none"
        else:
            if not _depends_on_n(nonhomogeneous_part):
                nonhomogeneous_type = "constant"
            elif sp.Poly(nonhomogeneous_part, n, domain="EX") is not None:
                try:
                    degree = sp.Poly(nonhomogeneous_part, n).degree()
                    nonhomogeneous_type = f"polynomial_in_n_degree_{degree}"
                except Exception:
                    nonhomogeneous_type = "index-dependent"
            else:
                nonhomogeneous_type = "index-dependent"

        if coefficient_type == "constant" and not special:
            if is_homogeneous:
                solver_eligible = True
                recommended_mode = "exact_symbolic_solver"
                reason = "Linear homogeneous recurrence with constant coefficients is supported by the exact solver."
            elif order == 1:
                solver_eligible = True
                recommended_mode = "exact_symbolic_solver"
                reason = "First-order linear non-homogeneous recurrence with constant coefficient is supported by summation-form exact solver."
            else:
                solver_eligible = False
                recommended_mode = "simulation_fallback"
                reason = "Linear non-homogeneous recurrence of order greater than one is not yet in the manual exact-solver class."
        elif coefficient_type != "constant":
            reason = "Coefficient depends on n; exact solver not applied in current version."
        elif special:
            reason = "Special operator detected; exact solver not applied."

    return ClassificationResult(
        order=order,
        is_linear=is_linear,
        is_homogeneous=is_homogeneous,
        coefficient_type=coefficient_type,
        nonhomogeneous_type=nonhomogeneous_type,
        special_operators=special,
        solver_eligible=solver_eligible,
        recommended_mode=recommended_mode,
        reason=reason,
        coefficients=coefficients,
        nonhomogeneous_part=nonhomogeneous_part,
    )
