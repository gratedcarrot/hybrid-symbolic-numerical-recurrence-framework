"""
cases.py

Standard recurrence cases for V2 experiments.
These cases are chosen to demonstrate exact solving, verification, and
simulation fallback.
"""

from __future__ import annotations

from typing import List

from .models import RecurrenceDefinition


def get_v2_cases(total_terms: int = 25) -> List[RecurrenceDefinition]:
    return [
        RecurrenceDefinition(
            name="First-order homogeneous recurrence",
            expression="a_n = 2*a_(n-1)",
            initial_terms=[1],
            total_terms=total_terms,
            index_start=0,
            description="Exact homogeneous first-order case.",
        ),
        RecurrenceDefinition(
            name="First-order non-homogeneous recurrence with constant term",
            expression="a_n = 2*a_(n-1) + 3",
            initial_terms=[1],
            total_terms=total_terms,
            index_start=0,
            description="Exact first-order nonhomogeneous constant case.",
        ),
        RecurrenceDefinition(
            name="Arithmetic progression as recurrence",
            expression="a_n = a_(n-1) + 5",
            initial_terms=[2],
            total_terms=total_terms,
            index_start=0,
            description="Exact first-order c=1 nonhomogeneous case.",
        ),
        RecurrenceDefinition(
            name="First-order non-homogeneous recurrence with index term",
            expression="a_n = 2*a_(n-1) + n",
            initial_terms=[1],
            total_terms=total_terms,
            index_start=0,
            description="Exact first-order polynomial nonhomogeneous case.",
        ),
        RecurrenceDefinition(
            name="Second-order Fibonacci-type recurrence",
            expression="a_n = a_(n-1) + a_(n-2)",
            initial_terms=[0, 1],
            total_terms=total_terms,
            index_start=0,
            description="Exact homogeneous second-order case.",
        ),
        RecurrenceDefinition(
            name="Second-order linear recurrence",
            expression="a_n = 3*a_(n-1) - 2*a_(n-2)",
            initial_terms=[1, 2],
            total_terms=total_terms,
            index_start=0,
            description="Exact homogeneous second-order case with repeated growth pattern.",
        ),
        RecurrenceDefinition(
            name="Rowland gcd recurrence",
            expression="a_n = a_(n-1) + gcd(n, a_(n-1))",
            initial_terms=[7],
            total_terms=total_terms,
            index_start=1,
            description="Nonlinear number-theoretic recurrence; routed to simulation fallback.",
        ),
        RecurrenceDefinition(
            name="Nonlinear square recurrence",
            expression="a_n = a_(n-1)**2 + 1",
            initial_terms=[1],
            total_terms=8,
            index_start=0,
            description="Nonlinear recurrence; routed to simulation fallback.",
        ),
    ]
