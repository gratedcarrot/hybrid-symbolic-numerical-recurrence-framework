"""
Basic tests for the V2 recurrence framework.
Run from project root:
    python -m pytest tests/test_v2_pipeline.py
or without pytest:
    python tests/test_v2_pipeline.py
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.hybrid_analyzer import analyze_recurrence
from src.models import RecurrenceDefinition


def test_first_order_nonhomogeneous_closed_form():
    case = RecurrenceDefinition(
        name="first order nonhomogeneous",
        expression="a_n = 2*a_(n-1) + 3",
        initial_terms=[1],
        total_terms=10,
        index_start=0,
    )
    report = analyze_recurrence(case, verification_terms=10)
    assert report.solver.solved is True
    assert report.verification is not None
    assert report.verification.verified is True
    assert report.generated_terms[:5] == [1, 5, 13, 29, 61]


def test_fibonacci_closed_form_verifies():
    case = RecurrenceDefinition(
        name="fibonacci",
        expression="a_n = a_(n-1) + a_(n-2)",
        initial_terms=[0, 1],
        total_terms=10,
        index_start=0,
    )
    report = analyze_recurrence(case, verification_terms=10)
    assert report.solver.solved is True
    assert report.verification is not None
    assert report.verification.verified is True
    assert report.generated_terms[:10] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_rowland_fallback():
    case = RecurrenceDefinition(
        name="rowland",
        expression="a_n = a_(n-1) + gcd(n, a_(n-1))",
        initial_terms=[7],
        total_terms=10,
        index_start=1,
    )
    report = analyze_recurrence(case, verification_terms=10)
    assert report.solver.solved is False
    assert report.fallback_used is True
    assert report.generated_terms[:10] == [7, 8, 9, 10, 15, 18, 19, 20, 21, 22]


if __name__ == "__main__":
    test_first_order_nonhomogeneous_closed_form()
    test_fibonacci_closed_form_verifies()
    test_rowland_fallback()
    print("All V2 tests passed.")
