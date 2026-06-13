from src.cases import get_cases
from src.simulator import generate_sequence
from src.symbolic_solver import solve_symbolically
from src.analysis import analyse_sequence


def test_symbolic_cases_verify():
    for case in get_cases():
        if case.expected_mode == "Symbolic":
            result = solve_symbolically(case, verification_terms=12)
            assert result.verification_status == "PASS", (case.case_id, result.message)


def test_rowland_increment_contains_prime_jumps():
    case = [c for c in get_cases() if c.case_id == "C12"][0]
    seq = generate_sequence(case, n_terms=30)
    values = [v for _, v in seq.terms]
    increments = [values[i] - values[i - 1] for i in range(1, len(values))]
    assert 5 in increments
    assert 11 in increments


def test_periodic_case_detected():
    case = [c for c in get_cases() if c.case_id == "C14"][0]
    seq = generate_sequence(case, n_terms=20)
    indicators = analyse_sequence(case, seq)
    assert "periodic" in indicators.growth_class or "cycle" in indicators.periodicity
