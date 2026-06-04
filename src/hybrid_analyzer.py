"""
hybrid_analyzer.py

Main Version-2 pipeline:
    parse -> classify -> exact solve if eligible -> verify -> simulate/analyze.
"""

from __future__ import annotations

from .analyzer import first_differences, second_differences, ratio_an_over_prev, growth_observation
from .classifier import classify
from .core_engine import generate_sequence
from .models import HybridAnalysisReport, RecurrenceDefinition
from .parser import parse_recurrence
from .symbolic_solver import solve_exact
from .verifier import verify_closed_form


def analyze_recurrence(definition: RecurrenceDefinition, verification_terms: int = 20) -> HybridAnalysisReport:
    parsed = parse_recurrence(definition)
    classification = classify(parsed)
    solver = solve_exact(parsed, classification)

    verification = None
    fallback_used = not solver.solved

    if solver.solved:
        verification = verify_closed_form(parsed, solver, terms_to_check=min(verification_terms, definition.total_terms))
        # If exact verification fails, keep simulation output but mark fallback as used.
        if not verification.verified:
            fallback_used = True

    generated_terms = generate_sequence(
        definition.initial_terms,
        parsed.rule,
        definition.total_terms,
        index_start=definition.index_start,
    )

    d1 = first_differences(generated_terms)
    d2 = second_differences(generated_terms)
    ratios = ratio_an_over_prev(generated_terms)

    return HybridAnalysisReport(
        name=definition.name,
        recurrence=definition.expression,
        classification=classification,
        solver=solver,
        verification=verification,
        generated_terms=generated_terms,
        first_differences=d1,
        second_differences=d2,
        ratios=ratios,
        growth_observation=growth_observation(generated_terms),
        fallback_used=fallback_used,
    )
