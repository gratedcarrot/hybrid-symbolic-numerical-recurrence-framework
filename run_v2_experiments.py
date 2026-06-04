"""
run_v2_experiments.py

Runs the Version-2 hybrid recurrence analysis pipeline.
Output files:
    results/v2_hybrid_analysis_results.csv
    results/v2_hybrid_analysis_report.txt
    plots/*_sequence.png
    plots/*_log_growth.png

Run:
    python run_v2_experiments.py
"""

from __future__ import annotations

import re
from pathlib import Path

from src.cases import get_v2_cases
from src.hybrid_analyzer import analyze_recurrence
from src.plotter import plot_log_growth, plot_sequence
from src.reporting import save_csv, save_text_report


def safe_name(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "case"


def main() -> None:
    results_dir = Path("results")
    plots_dir = Path("plots")
    results_dir.mkdir(exist_ok=True)
    plots_dir.mkdir(exist_ok=True)

    reports = []
    for case in get_v2_cases(total_terms=25):
        report = analyze_recurrence(case, verification_terms=20)
        reports.append(report)

        base = safe_name(case.name)
        plot_sequence(
            report.generated_terms,
            title=f"Sequence Plot: {case.name}",
            output_file=str(plots_dir / f"{base}_sequence.png"),
            index_start=case.index_start,
        )
        plot_log_growth(
            report.generated_terms,
            title=f"Log Growth Plot: {case.name}",
            output_file=str(plots_dir / f"{base}_log_growth.png"),
            index_start=case.index_start,
        )

    save_csv(reports, results_dir / "v2_hybrid_analysis_results.csv")
    save_text_report(reports, results_dir / "v2_hybrid_analysis_report.txt")

    print("V2 experiments completed.")
    print("Saved:")
    print(" - results/v2_hybrid_analysis_results.csv")
    print(" - results/v2_hybrid_analysis_report.txt")
    print(" - plots/*.png")

    print("\nSummary:")
    for r in reports:
        status = "SOLVED" if r.solver.solved else "SIMULATION-FALLBACK"
        verification = "PASS" if (r.verification and r.verification.verified) else "N/A"
        print(f" - {r.name}: {status}, verification={verification}")


if __name__ == "__main__":
    main()
