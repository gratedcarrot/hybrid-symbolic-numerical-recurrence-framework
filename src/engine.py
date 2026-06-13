from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .analysis import analyse_sequence
from .cases import RecurrenceCase
from .simulator import generate_sequence
from .symbolic_solver import solve_symbolically


@dataclass
class AnalysisReport:
    case_id: str
    selected_mode: str
    classification: str
    symbolic_status: str
    verification: str
    growth_class: str
    message: str


def analyse_case(case: RecurrenceCase, n_terms: int = 50) -> AnalysisReport:
    symbolic = solve_symbolically(case)
    sequence = generate_sequence(case, n_terms=n_terms)
    indicators = analyse_sequence(case, sequence)
    return AnalysisReport(
        case_id=case.case_id,
        selected_mode=case.expected_mode,
        classification=case.recurrence_type,
        symbolic_status=symbolic.status,
        verification=symbolic.verification_status,
        growth_class=indicators.growth_class,
        message=symbolic.message,
    )
