from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from .analysis import rowland_jump_rows
from .cases import get_cases
from .simulator import generate_sequence


def _case(case_id: str):
    for case in get_cases():
        if case.case_id == case_id:
            return case
    raise KeyError(case_id)


def make_plots(plot_dir: Path) -> None:
    plot_dir.mkdir(parents=True, exist_ok=True)
    plot_fibonacci_ratio(plot_dir / "fibonacci_ratio_stabilisation.png")
    plot_rowland_increments(plot_dir / "rowland_increment_jumps.png")
    plot_nonlinear_digit_growth(plot_dir / "nonlinear_digit_growth.png")
    plot_periodic_case(plot_dir / "periodic_tail_cycle.png")


def plot_fibonacci_ratio(path: Path) -> None:
    case = _case("C5")
    seq = generate_sequence(case, n_terms=35)
    terms = seq.terms
    xs = [idx for idx, _ in terms[2:]]
    ratios = []
    for i in range(2, len(terms)):
        prev = terms[i - 1][1]
        curr = terms[i][1]
        ratios.append(curr / prev if prev != 0 else None)
    xs = xs[-len(ratios):]
    ratios = [r for r in ratios if r is not None]
    xs = xs[-len(ratios):]

    plt.figure(figsize=(7, 4))
    plt.plot(xs, ratios, marker="o")
    plt.axhline(1.61803398875, linestyle="--", linewidth=1)
    plt.xlabel("n")
    plt.ylabel("a_n / a_{n-1}")
    plt.title("Fibonacci-type ratio stabilisation")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def plot_rowland_increments(path: Path) -> None:
    case = _case("C12")
    seq = generate_sequence(case, n_terms=80)
    rows = rowland_jump_rows(case, seq)
    xs = [row["n"] for row in rows]
    inc = [row["increment"] for row in rows]

    plt.figure(figsize=(7, 4))
    plt.stem(xs, inc)
    plt.xlabel("n")
    plt.ylabel("Increment d_n")
    plt.title("Rowland gcd recurrence increment jumps")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def plot_nonlinear_digit_growth(path: Path) -> None:
    case = _case("C13")
    seq = generate_sequence(case, n_terms=12, max_digits=2000)
    xs = [idx for idx, _ in seq.terms]
    digit_lengths = [len(str(abs(value))) for _, value in seq.terms]

    plt.figure(figsize=(7, 4))
    plt.plot(xs, digit_lengths, marker="o")
    plt.xlabel("n")
    plt.ylabel("Number of digits in a_n")
    plt.title("Nonlinear square recurrence digit-length growth")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def plot_periodic_case(path: Path) -> None:
    case = _case("C14")
    seq = generate_sequence(case, n_terms=25)
    xs = [idx for idx, _ in seq.terms]
    values = [value for _, value in seq.terms]

    plt.figure(figsize=(7, 4))
    plt.plot(xs, values, marker="o")
    plt.xlabel("n")
    plt.ylabel("a_n")
    plt.title("Modular recurrence tail-cycle behaviour")
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
