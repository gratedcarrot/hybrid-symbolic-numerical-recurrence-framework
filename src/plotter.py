"""
plotter.py

Simple plotting utilities for recurrence outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import List
import math

import matplotlib.pyplot as plt

Number = int | float


def ensure_parent(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def plot_sequence(seq: List[Number], title: str, output_file: str, index_start: int = 0) -> None:
    ensure_parent(output_file)
    x_values = list(range(index_start, index_start + len(seq)))
    plt.figure(figsize=(7.2, 4.2))
    plt.plot(x_values, seq, marker="o", linewidth=1.5, markersize=3)
    plt.title(title)
    plt.xlabel("n")
    plt.ylabel("a_n")
    plt.grid(True, alpha=0.35)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()


def plot_values(values: List[Number], title: str, ylabel: str, output_file: str, start_index: int = 0) -> None:
    ensure_parent(output_file)
    x_values = list(range(start_index, start_index + len(values)))
    plt.figure(figsize=(7.2, 4.2))
    plt.plot(x_values, values, marker="o", linewidth=1.5, markersize=3)
    plt.title(title)
    plt.xlabel("n")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.35)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()


def plot_log_growth(seq: List[Number], title: str, output_file: str, index_start: int = 0) -> None:
    ensure_parent(output_file)
    x_values = list(range(index_start, index_start + len(seq)))
    y_values = [math.log10(abs(float(x)) + 1.0) for x in seq]
    plt.figure(figsize=(7.2, 4.2))
    plt.plot(x_values, y_values, marker="o", linewidth=1.5, markersize=3)
    plt.title(title)
    plt.xlabel("n")
    plt.ylabel("log10(|a_n| + 1)")
    plt.grid(True, alpha=0.35)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()
