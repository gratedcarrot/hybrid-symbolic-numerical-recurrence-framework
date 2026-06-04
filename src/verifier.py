"""
verifier.py

Computational verification of exact closed forms.
The closed form is evaluated for the first N indices and compared with the
sequence produced by direct recurrence iteration.
"""

from __future__ import annotations

from typing import List

from .core_engine import generate_sequence
from .models import ParsedRecurrence, SolverResult, VerificationResult
from .symbolic_solver import evaluate_closed_form


def verify_closed_form(parsed: ParsedRecurrence, solver: SolverResult, terms_to_check: int = 20) -> VerificationResult:
    if not solver.solved or solver.closed_form is None:
        raise ValueError("Cannot verify because no closed form was produced.")

    generated = generate_sequence(
        parsed.definition.initial_terms,
        parsed.rule,
        total_terms=terms_to_check,
        index_start=parsed.definition.index_start,
    )

    closed_terms = []
    mismatches = []

    for offset in range(terms_to_check):
        n_value = parsed.definition.index_start + offset
        closed_value = evaluate_closed_form(solver.closed_form, n_value)
        closed_terms.append(closed_value)

        if closed_value != generated[offset]:
            mismatches.append({"n": n_value, "generated": generated[offset], "closed_form": closed_value})

    return VerificationResult(
        verified=len(mismatches) == 0,
        checked_terms=terms_to_check,
        generated_terms=generated,
        closed_form_terms=closed_terms,
        mismatches=mismatches,
    )
