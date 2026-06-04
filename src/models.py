"""
models.py

Shared dataclasses for Version 2 of the recurrence-analysis framework.
The V2 framework is designed as a hybrid symbolic-numerical system:
1. Parse recurrence input.
2. Classify mathematical structure.
3. Attempt exact solving for supported classes.
4. Verify symbolic output against generated terms.
5. Fall back to simulation for unsupported/nonlinear cases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

Number = int | float


@dataclass
class RecurrenceDefinition:
    """
    Internal representation of a recurrence relation.

    Expression convention:
        The recurrence defines a_n using n and previous terms.

    Supported previous-term aliases in user input:
        a_prev, a_prev1, a_prev2, ...
        a_(n-1), a_(n-2), ...
        a(n-1), a(n-2), ...
    """

    name: str
    expression: str
    initial_terms: List[Number]
    total_terms: int = 20
    index_start: int = 0
    description: str = ""


@dataclass
class ParsedRecurrence:
    """Parsed form used by generator, classifier, and solver."""

    definition: RecurrenceDefinition
    normalized_expression: str
    order: int
    previous_symbols: List[str]
    rule: Callable[[int, List[Number]], Number]
    sympy_expression: Optional[Any] = None
    parse_warnings: List[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    """Mathematical classification produced before solving."""

    order: int
    is_linear: bool
    is_homogeneous: Optional[bool]
    coefficient_type: str
    nonhomogeneous_type: str
    special_operators: List[str]
    solver_eligible: bool
    recommended_mode: str
    reason: str
    coefficients: List[Any] = field(default_factory=list)
    nonhomogeneous_part: Optional[Any] = None


@dataclass
class SolverResult:
    """Exact solver result for supported recurrences."""

    solved: bool
    method: str
    closed_form: Optional[Any]
    characteristic_polynomial: Optional[Any] = None
    characteristic_roots: List[Any] = field(default_factory=list)
    reason: str = ""


@dataclass
class VerificationResult:
    """Compares recurrence-generated terms against closed-form terms."""

    verified: bool
    checked_terms: int
    generated_terms: List[Number]
    closed_form_terms: List[Number]
    mismatches: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class HybridAnalysisReport:
    """One complete report row for a recurrence case."""

    name: str
    recurrence: str
    classification: ClassificationResult
    solver: SolverResult
    verification: Optional[VerificationResult]
    generated_terms: List[Number]
    first_differences: List[Number]
    second_differences: List[Number]
    ratios: List[float]
    growth_observation: str
    fallback_used: bool
