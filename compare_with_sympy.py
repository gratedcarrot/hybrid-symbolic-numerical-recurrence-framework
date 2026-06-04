"""
compare_with_sympy.py

Optional comparison against SymPy's rsolve for supported exact cases.
This is not used as the main solver; it is a comparison/validation experiment
for the paper's V2 evaluation section.

Run:
    python compare_with_sympy.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

import sympy as sp

from src.cases import get_v2_cases
from src.classifier import classify
from src.parser import parse_recurrence
from src.symbolic_solver import solve_exact


def sympy_rsolve_for_case(parsed, classification):
    if not classification.is_linear or classification.coefficient_type != "constant":
        return None, "Not a linear constant-coefficient case."
    if not classification.is_homogeneous and classification.order != 1:
        return None, "Only comparing supported non-homogeneous first-order cases."

    n = sp.Symbol("n", integer=True, nonnegative=True)
    a = sp.Function("a")

    rhs = 0
    for i, c in enumerate(classification.coefficients, start=1):
        rhs += c * a(n - i)
    if classification.nonhomogeneous_part is not None:
        rhs += classification.nonhomogeneous_part

    recurrence_expr = a(n) - rhs
    init = {}
    for i, value in enumerate(parsed.definition.initial_terms[:classification.order]):
        init[a(i)] = sp.Integer(value)

    try:
        result = sp.rsolve(recurrence_expr, a(n), init)
        return sp.simplify(result), "OK"
    except Exception as exc:
        return None, f"SymPy rsolve failed: {exc}"


def main() -> None:
    rows: List[Dict[str, Any]] = []
    for case in get_v2_cases(total_terms=20):
        parsed = parse_recurrence(case)
        classification = classify(parsed)
        our = solve_exact(parsed, classification)
        sympy_result, status = sympy_rsolve_for_case(parsed, classification)

        comparable = our.solved and sympy_result is not None
        equivalent = False
        if comparable:
            n = sp.Symbol("n", integer=True, nonnegative=True)
            try:
                equivalent = sp.simplify(our.closed_form - sympy_result) == 0
            except Exception:
                equivalent = False

        rows.append({
            "case_name": case.name,
            "recurrence": case.expression,
            "our_solver_solved": our.solved,
            "our_method": our.method,
            "our_closed_form": str(our.closed_form) if our.closed_form is not None else "",
            "sympy_status": status,
            "sympy_closed_form": str(sympy_result) if sympy_result is not None else "",
            "symbolically_equivalent": "PASS" if equivalent else ("NOT_COMPARABLE" if not comparable else "CHECK"),
        })

    out = Path("results") / "v2_sympy_comparison.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {out}")
    for row in rows:
        print(f"{row['case_name']}: {row['symbolically_equivalent']}")


if __name__ == "__main__":
    main()
