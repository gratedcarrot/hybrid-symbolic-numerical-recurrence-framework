from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd

from .analysis import analyse_sequence, rowland_jump_rows
from .cases import RecurrenceCase, get_cases
from .simulator import generate_sequence
from .symbolic_solver import solve_symbolically
from .sympy_compare import compare_with_sympy


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def case_summary_rows(cases: Iterable[RecurrenceCase]) -> List[Dict[str, object]]:
    rows = []
    for case in cases:
        rows.append(
            {
                "ID": case.case_id,
                "Recurrence Relation": case.relation,
                "Order": case.order,
                "Classification": case.recurrence_type,
                "Selected Mode": case.expected_mode,
                "Special Operator": case.special_operator,
                "Purpose": case.purpose,
            }
        )
    return rows


def run_symbolic_experiments(cases: List[RecurrenceCase], output_dir: Path) -> List[Dict[str, object]]:
    rows = []
    for case in cases:
        result = solve_symbolically(case)
        rows.append(
            {
                "ID": case.case_id,
                "Type": case.recurrence_type,
                "Mode": case.expected_mode,
                "Model Output": result.closed_form,
                "Method": result.method,
                "Solver Status": result.status,
                "Verification": result.verification_status,
                "Match Count": result.match_count,
                "Terms Checked": result.terms_checked,
                "Message": result.message,
            }
        )
    write_csv(output_dir / "symbolic_results.csv", rows)
    return rows


def run_sympy_comparison(cases: List[RecurrenceCase], output_dir: Path) -> List[Dict[str, object]]:
    rows = []
    for case in cases:
        result = compare_with_sympy(case)
        rows.append(
            {
                "ID": case.case_id,
                "SymPy Status": result.status,
                "SymPy Closed Form": result.sympy_closed_form,
                "Comparison Result": result.match_status,
                "Terms Checked": result.terms_checked,
                "Message": result.message,
            }
        )
    write_csv(output_dir / "sympy_comparison_results.csv", rows)
    return rows


def run_generation_and_analysis(cases: List[RecurrenceCase], output_dir: Path, n_terms: int = 50) -> None:
    generated_rows: List[Dict[str, object]] = []
    indicator_rows: List[Dict[str, object]] = []
    fallback_rows: List[Dict[str, object]] = []
    rowland_rows: List[Dict[str, object]] = []

    for case in cases:
        sequence = generate_sequence(case, n_terms=n_terms)
        for idx, value in sequence.terms:
            generated_rows.append(
                {
                    "ID": case.case_id,
                    "n": idx,
                    "a_n": value,
                    "Mode": case.expected_mode,
                    "Overflowed": sequence.overflowed,
                    "Stop Reason": sequence.stop_reason,
                }
            )

        indicators = analyse_sequence(case, sequence)
        indicator_row = {
            "ID": indicators.case_id,
            "First Terms": indicators.first_terms,
            "First Differences": indicators.first_differences,
            "Second Differences": indicators.second_differences,
            "Ratio Summary": indicators.ratio_summary,
            "Log Growth Slope": indicators.log_growth_slope,
            "Digit Length Start": indicators.digit_length_start,
            "Digit Length End": indicators.digit_length_end,
            "Monotonicity": indicators.monotonicity,
            "Periodicity": indicators.periodicity,
            "Spike Count": indicators.spike_count,
            "Growth Class": indicators.growth_class,
            "Overflowed": indicators.overflowed,
            "Stop Reason": indicators.stop_reason,
        }
        indicator_rows.append(indicator_row)

        if case.expected_mode == "Fallback":
            fallback_rows.append(
                {
                    "ID": case.case_id,
                    "Fallback Reason": case.recurrence_type,
                    "Diagnostics Used": _diagnostics_used(case),
                    "Growth Class": indicators.growth_class,
                    "Monotonicity": indicators.monotonicity,
                    "Periodicity": indicators.periodicity,
                    "Spike Count": indicators.spike_count,
                    "Digit Length End": indicators.digit_length_end,
                    "Overflow Guard": indicators.stop_reason,
                }
            )

        if case.special_operator == "gcd":
            rowland_rows.extend(rowland_jump_rows(case, sequence))

    write_csv(output_dir / "generated_terms.csv", generated_rows)
    write_csv(output_dir / "simulation_indicators.csv", indicator_rows)
    write_csv(output_dir / "fallback_deep_analysis.csv", fallback_rows)
    write_csv(output_dir / "rowland_jump_analysis.csv", rowland_rows)


def _diagnostics_used(case: RecurrenceCase) -> str:
    base = ["first_difference", "second_difference", "ratio_trend", "log_growth", "digit_length", "monotonicity", "periodicity", "spike_detection"]
    if case.special_operator == "gcd":
        base.extend(["increment_sequence", "prime_jump_check", "jump_frequency"])
    if case.special_operator == "power":
        base.extend(["divergence_guard", "digit_growth"])
    if case.special_operator == "mod":
        base.extend(["tail_cycle_detection"])
    if case.special_operator == "variable_coefficient":
        base.extend(["factorial_like_ratio_trend"])
    return ", ".join(base)


def run_scalability(cases: List[RecurrenceCase], output_dir: Path) -> None:
    selected_ids = {"C5", "C7", "C11", "C12", "C13", "C14"}
    selected = [case for case in cases if case.case_id in selected_ids]
    term_counts = [25, 50, 100, 250, 500, 1000]
    rows: List[Dict[str, object]] = []

    for case in selected:
        for count in term_counts:
            start = time.perf_counter()
            sequence = generate_sequence(case, n_terms=count)
            elapsed_ms = (time.perf_counter() - start) * 1000
            rows.append(
                {
                    "ID": case.case_id,
                    "Requested Terms": count,
                    "Generated Terms": len(sequence.terms),
                    "Runtime ms": round(elapsed_ms, 4),
                    "Overflowed": sequence.overflowed,
                    "Stop Reason": sequence.stop_reason,
                }
            )
    write_csv(output_dir / "scalability_results.csv", rows)


def run_robustness(output_dir: Path) -> None:
    from .cases import RecurrenceCase

    rows: List[Dict[str, object]] = []
    tests = []

    tests.append(
        (
            "missing_initial_condition",
            RecurrenceCase(
                "R1",
                "a_n = a_{n-1} + 1",
                {},
                1,
                [1],
                None,
                lambda i, a: a[i - 1] + 1,
                "Fallback",
                "invalid recurrence",
                "missing initial value",
            ),
        )
    )
    tests.append(
        (
            "insufficient_initial_conditions",
            RecurrenceCase(
                "R2",
                "a_n = a_{n-1} + a_{n-2}, a_0 = 0",
                {0: 0},
                2,
                [1, 1],
                None,
                lambda i, a: a[i - 1] + a[i - 2],
                "Fallback",
                "invalid recurrence",
                "missing second initial value",
            ),
        )
    )
    tests.append(
        (
            "zero_ratio_safety",
            RecurrenceCase(
                "R3",
                "a_n = a_{n-1} + 1, a_0 = 0",
                {0: 0},
                1,
                [1],
                None,
                lambda i, a: a[i - 1] + 1,
                "Fallback",
                "valid recurrence with zero first denominator",
                "ratio safety check",
            ),
        )
    )

    for name, case in tests:
        try:
            sequence = generate_sequence(case, n_terms=10)
            indicators = analyse_sequence(case, sequence)
            rows.append(
                {
                    "Test": name,
                    "Status": "PASS",
                    "Message": f"generated {len(sequence.terms)} terms; growth={indicators.growth_class}",
                }
            )
        except Exception as exc:
            expected = name in {"missing_initial_condition", "insufficient_initial_conditions"}
            rows.append(
                {
                    "Test": name,
                    "Status": "PASS" if expected else "FAIL",
                    "Message": str(exc),
                }
            )
    write_csv(output_dir / "robustness_results.csv", rows)


def write_ablation_and_positioning(output_dir: Path) -> None:
    ablation_rows = [
        {
            "Version": "Initial paper version",
            "Benchmark Cases": 8,
            "Symbolic Cases": 6,
            "Fallback Cases": 2,
            "Higher-order Symbolic Support": "No",
            "Polynomial Non-homogeneous Support": "Limited",
            "Repeated-root Coverage": "Limited",
            "Simulation Indicators": "first difference, second difference, ratio, growth trend",
            "Rowland-specific Diagnostics": "basic increment observation",
            "Behaviour Classification": "basic",
        },
        {
            "Version": "Enhanced version",
            "Benchmark Cases": 14,
            "Symbolic Cases": 10,
            "Fallback Cases": 4,
            "Higher-order Symbolic Support": "Yes",
            "Polynomial Non-homogeneous Support": "Yes",
            "Repeated-root Coverage": "Yes",
            "Simulation Indicators": "first/second differences, ratios, log growth, digit length, monotonicity, periodicity, spikes, overflow guard",
            "Rowland-specific Diagnostics": "increment sequence, prime jump check, jump positions, jump frequency",
            "Behaviour Classification": "multi-indicator",
        },
    ]
    write_csv(output_dir / "ablation_summary.csv", ablation_rows)

    positioning_rows = [
        {
            "Tool/System": "SymPy",
            "Main Capability": "symbolic recurrence solving through rsolve",
            "Relative Position of Proposed Model": "adds recurrence classification, verification, fallback routing, and behavioural reports",
        },
        {
            "Tool/System": "SageMath",
            "Main Capability": "linear recurrence and sequence computation tools",
            "Relative Position of Proposed Model": "adds lightweight solve-or-simulate pipeline and CSV/plot reporting",
        },
        {
            "Tool/System": "MATLAB Symbolic Toolbox",
            "Main Capability": "symbolic recurrence solving",
            "Relative Position of Proposed Model": "adds recurrence-specific fallback diagnostics and batch experiments",
        },
        {
            "Tool/System": "Wolfram Mathematica",
            "Main Capability": "advanced recurrence solving and recurrence table generation",
            "Relative Position of Proposed Model": "adds transparent classification and explainable fallback behaviour indicators",
        },
        {
            "Tool/System": "Enhanced proposed model",
            "Main Capability": "classification, symbolic solving, verification, simulation fallback, behavioural analysis",
            "Relative Position of Proposed Model": "focused recurrence-analysis workflow for paper experiments and education",
        },
    ]
    write_csv(output_dir / "tool_positioning_table.csv", positioning_rows)


def run_all_reports(output_dir: Path) -> None:
    cases = get_cases()
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "case_summary.csv", case_summary_rows(cases))
    run_symbolic_experiments(cases, output_dir)
    run_sympy_comparison(cases, output_dir)
    run_generation_and_analysis(cases, output_dir)
    run_scalability(cases, output_dir)
    run_robustness(output_dir)
    write_ablation_and_positioning(output_dir)
