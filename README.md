# Hybrid Symbolic–Numerical Recurrence Framework

This repository contains the code and generated outputs for the paper:

**A Hybrid Symbolic–Numerical Framework for Solving and Simulating Recurrence Relations**

The framework follows a **solve-or-simulate** workflow for recurrence relation analysis:

1. Parse a structured recurrence expression.
2. Classify recurrence structure.
3. Attempt exact symbolic solving for supported classes.
4. Verify the closed-form expression against recurrence-generated terms.
5. Route unsupported, nonlinear, or number-theoretic recurrences to simulation fallback.
6. Generate numerical summaries and plots.

## Main Features

- Structured recurrence parsing
- Classification by order, linearity, homogeneity, coefficient type, and special operators
- Closed-form solving for supported first-order and homogeneous linear constant-coefficient recurrences
- Computational verification of symbolic solutions
- Simulation fallback for unsupported/nonlinear recurrences such as Rowland gcd recurrence and nonlinear square recurrence
- Numerical analysis using differences, ratios, monotonicity, and growth indicators
- Optional comparison with SymPy for supported symbolic cases

## Repository Structure

```text
src/                    Core framework modules
  parser.py              Recurrence expression parser
  classifier.py          Recurrence classifier
  symbolic_solver.py     Closed-form solver for supported classes
  core_engine.py         Iterative sequence generation engine
  verifier.py            Closed-form verification module
  analyzer.py            Numerical analysis utilities
  hybrid_analyzer.py     Main solve-or-simulate pipeline
  plotter.py             Plot generation
  cases.py               Experimental recurrence cases
  reporting.py           CSV/text report generation

tests/                  Test scripts
results/                Generated CSV and text reports
plots/                  Generated experiment plots
paper_figures/          Final figures used in the manuscript
run_v2_experiments.py   Main experiment runner
compare_with_sympy.py   Optional comparison with SymPy
requirements.txt        Python dependencies
```

## Installation

Python 3.10 or later is recommended.

```bash
pip install -r requirements.txt
```

## Run Experiments

```bash
python run_v2_experiments.py
```

Generated outputs:

```text
results/v2_hybrid_analysis_results.csv
results/v2_hybrid_analysis_report.txt
plots/*.png
```

## Compare with SymPy

```bash
python compare_with_sympy.py
```

Generated output:

```text
results/v2_sympy_comparison.csv
```

## Run Tests

```bash
python tests/test_v2_pipeline.py
```

or, if `pytest` is installed:

```bash
python -m pytest tests/test_v2_pipeline.py
```

## Experimental Cases

The included experiments evaluate eight recurrence cases:

- First-order homogeneous recurrence
- First-order non-homogeneous recurrence with constant term
- Arithmetic progression as recurrence
- First-order non-homogeneous recurrence with index term
- Second-order Fibonacci-type recurrence
- Second-order linear recurrence
- Rowland gcd recurrence
- Nonlinear square recurrence

The first six cases are solved symbolically and verified. The Rowland gcd recurrence and nonlinear square recurrence are routed to simulation fallback.

## Notes

The framework is designed as a scoped recurrence-analysis workflow, not as a universal replacement for computer algebra systems. Its contribution is the integration of classification, symbolic solving, computational verification, numerical analysis, visualization, and simulation fallback within one transparent pipeline.
