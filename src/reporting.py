"""
reporting.py

CSV and text report utilities for the V2 experiments.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from .models import HybridAnalysisReport


def preview(values, max_items: int = 10) -> str:
    shown = values[:max_items]
    suffix = "" if len(values) <= max_items else f" ... (total {len(values)})"
    return f"{shown}{suffix}"


def report_to_row(report: HybridAnalysisReport) -> dict:
    c = report.classification
    s = report.solver
    v = report.verification
    return {
        "case_name": report.name,
        "recurrence": report.recurrence,
        "order": c.order,
        "is_linear": c.is_linear,
        "is_homogeneous": c.is_homogeneous,
        "coefficient_type": c.coefficient_type,
        "nonhomogeneous_type": c.nonhomogeneous_type,
        "special_operators": ", ".join(c.special_operators),
        "recommended_mode": c.recommended_mode,
        "classification_reason": c.reason,
        "solver_solved": s.solved,
        "solver_method": s.method,
        "closed_form": str(s.closed_form) if s.closed_form is not None else "",
        "characteristic_polynomial": str(s.characteristic_polynomial) if s.characteristic_polynomial is not None else "",
        "characteristic_roots": str(s.characteristic_roots),
        "verification_status": "PASS" if (v and v.verified) else ("NOT_APPLICABLE" if v is None else "FAIL"),
        "fallback_used": report.fallback_used,
        "generated_terms_preview": preview(report.generated_terms),
        "first_differences_preview": preview(report.first_differences),
        "ratios_preview": preview(report.ratios),
        "growth_observation": report.growth_observation,
    }


def save_csv(reports: Iterable[HybridAnalysisReport], output_file: str | Path) -> None:
    rows = [report_to_row(r) for r in reports]
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_text_report(reports: List[HybridAnalysisReport], output_file: str | Path) -> None:
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    for report in reports:
        c = report.classification
        s = report.solver
        v = report.verification
        lines.append("=" * 78)
        lines.append(report.name)
        lines.append("=" * 78)
        lines.append(f"Recurrence: {report.recurrence}")
        lines.append(f"Order: {c.order}")
        lines.append(f"Linear: {c.is_linear}")
        lines.append(f"Homogeneous: {c.is_homogeneous}")
        lines.append(f"Coefficient type: {c.coefficient_type}")
        lines.append(f"Non-homogeneous type: {c.nonhomogeneous_type}")
        lines.append(f"Special operators: {c.special_operators}")
        lines.append(f"Recommended mode: {c.recommended_mode}")
        lines.append(f"Classification reason: {c.reason}")
        lines.append(f"Solver solved: {s.solved}")
        lines.append(f"Solver method: {s.method}")
        if s.closed_form is not None:
            lines.append(f"Closed form: {s.closed_form}")
        if s.characteristic_polynomial is not None:
            lines.append(f"Characteristic polynomial: {s.characteristic_polynomial}")
            lines.append(f"Characteristic roots: {s.characteristic_roots}")
        if v is not None:
            lines.append(f"Verification: {'PASS' if v.verified else 'FAIL'} over {v.checked_terms} terms")
            if v.mismatches:
                lines.append(f"Mismatches: {v.mismatches}")
        else:
            lines.append("Verification: NOT_APPLICABLE")
        lines.append(f"Fallback used: {report.fallback_used}")
        lines.append(f"Generated terms: {preview(report.generated_terms, 15)}")
        lines.append(f"First differences: {preview(report.first_differences, 15)}")
        lines.append(f"Ratios: {preview(report.ratios, 10)}")
        lines.append(f"Growth observation: {report.growth_observation}")
        lines.append("")
    Path(output_file).write_text("\n".join(lines), encoding="utf-8")
