"""
symbolic_solver.py

Manual exact solvers for supported recurrence classes.
This file intentionally implements the core closed-form logic instead of simply
wrapping an external solver. SymPy is used for algebraic simplification only.

Supported exact classes in V2:
1. First-order linear constant-coefficient recurrence:
       a_n = c*a_(n-1) + f(n), a_0 known
   Output uses a summation form and simplifies common cases such as constant f(n).

2. kth-order homogeneous linear recurrence with constant coefficients:
       a_n = c1*a_(n-1) + ... + ck*a_(n-k)
   Output uses characteristic polynomial method and solves constants from initial values.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import sympy as sp

from .models import ClassificationResult, ParsedRecurrence, SolverResult


def _index_symbol():
    return sp.Symbol("n", integer=True, nonnegative=True)


def _to_exact(value):
    try:
        return sp.Integer(value)
    except Exception:
        return sp.sympify(value)


def _first_order_solver(parsed: ParsedRecurrence, classification: ClassificationResult) -> SolverResult:
    """
    Solve a_n = c*a_(n-1) + f(n), with a_0 known.
    Formula:
        a_n = c^n*a_0 + Sum(c^(n-j) f(j), (j, 1, n))
    This works for constant, polynomial, and many symbolic f(n) expressions.
    """
    n = _index_symbol()
    j = sp.Symbol("j", integer=True, positive=True)

    c = sp.simplify(classification.coefficients[0])
    f_n = sp.simplify(classification.nonhomogeneous_part or 0)
    a0 = _to_exact(parsed.definition.initial_terms[0])

    if f_n == 0:
        closed_form = sp.simplify((c ** n) * a0)
        return SolverResult(True, "first_order_homogeneous", closed_form, reason="Solved by direct first-order homogeneous formula.")

    # f(j) is obtained by replacing n with j in f(n).
    f_j = f_n.subs(n, j)

    if c == 1:
        closed_form = sp.simplify(a0 + sp.summation(f_j, (j, 1, n)))
        method = "first_order_nonhomogeneous_summation_c_equals_1"
    else:
        closed_form = sp.simplify((c ** n) * a0 + sp.summation((c ** (n - j)) * f_j, (j, 1, n)))
        method = "first_order_nonhomogeneous_summation"

    return SolverResult(True, method, sp.simplify(closed_form), reason="Solved using closed-form summation for first-order linear recurrence.")


def _homogeneous_characteristic_solver(parsed: ParsedRecurrence, classification: ClassificationResult) -> SolverResult:
    """
    Solve homogeneous constant-coefficient recurrence by characteristic polynomial.
    The solution basis contains n^m*r^n terms for repeated roots.
    """
    n = _index_symbol()
    r = sp.Symbol("r")
    coeffs = [sp.simplify(c) for c in classification.coefficients]
    k = len(coeffs)

    characteristic = sp.expand(r ** k - sum(coeffs[i] * r ** (k - i - 1) for i in range(k)))
    roots_dict = sp.roots(characteristic, r)

    if not roots_dict:
        return SolverResult(False, "characteristic_polynomial", None, characteristic, reason="Characteristic roots could not be computed symbolically.")

    constants = []
    basis_terms = []
    for root, multiplicity in roots_dict.items():
        for power in range(multiplicity):
            C = sp.Symbol(f"C{len(constants) + 1}")
            constants.append(C)
            basis_terms.append((n ** power) * (root ** n))

    general_solution = sum(C * term for C, term in zip(constants, basis_terms))

    equations = []
    for idx, initial_value in enumerate(parsed.definition.initial_terms[:k]):
        equations.append(sp.Eq(general_solution.subs(n, idx), _to_exact(initial_value)))

    solved_constants = sp.solve(equations, constants, dict=True)
    if not solved_constants:
        return SolverResult(False, "characteristic_polynomial", None, characteristic, list(roots_dict.keys()), "Could not solve constants from initial conditions.")

    closed_form = sp.simplify(general_solution.subs(solved_constants[0]))

    return SolverResult(
        solved=True,
        method="homogeneous_characteristic_polynomial",
        closed_form=closed_form,
        characteristic_polynomial=characteristic,
        characteristic_roots=list(roots_dict.keys()),
        reason="Solved using characteristic polynomial method.",
    )


def solve_exact(parsed: ParsedRecurrence, classification: ClassificationResult) -> SolverResult:
    """Route to the correct exact solver if the recurrence is eligible."""
    if not classification.solver_eligible:
        return SolverResult(False, "not_applicable", None, reason=classification.reason)

    if classification.is_linear and classification.is_homogeneous:
        return _homogeneous_characteristic_solver(parsed, classification)

    if classification.is_linear and classification.order == 1:
        return _first_order_solver(parsed, classification)

    return SolverResult(False, "unsupported_exact_class", None, reason="No exact solver implemented for this supported-looking class.")


def evaluate_closed_form(closed_form: Any, n_value: int):
    """Evaluate closed form at a specific integer index."""
    n = _index_symbol()
    value = sp.simplify(closed_form.subs(n, n_value))
    if value.is_Integer:
        return int(value)
    if value.is_Rational and value.q == 1:
        return int(value)
    try:
        numeric = float(value.evalf())
        if numeric.is_integer():
            return int(numeric)
        return numeric
    except Exception:
        return value
