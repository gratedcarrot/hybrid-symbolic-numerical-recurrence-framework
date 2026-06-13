# Enhanced Hybrid Symbolic-Numerical Recurrence Model

This repository contains an enhanced version of the hybrid recurrence relation analyser used for the paper:

**A Hybrid Symbolic-Numerical Model for Solving and Simulating Recurrence Relations**

The enhanced version is designed to address reviewer concerns by expanding both:

1. **Symbolic solving ability**
   - first-order homogeneous and non-homogeneous recurrences
   - arithmetic progression cases
   - first-order polynomial non-homogeneous cases
   - second-order and selected higher-order homogeneous linear recurrences
   - repeated characteristic-root cases
   - closed-form verification against recurrence-generated terms
   - external SymPy comparison for comparable symbolic cases

2. **Simulation/fallback ability**
   - first and second differences
   - ratio trend analysis
   - logarithmic growth slope
   - digit-length growth
   - monotonicity detection
   - periodicity/tail-cycle detection
   - spike/jump detection
   - overflow/divergence guard
   - Rowland-specific increment and prime-jump analysis

## Folder structure

```text
enhanced_recurrence_model/
├── run_all.py
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── cases.py
│   ├── engine.py
│   ├── symbolic_solver.py
│   ├── simulator.py
│   ├── analysis.py
│   ├── sympy_compare.py
│   ├── reporting.py
│   └── plotting.py
├── tests/
│   └── test_core.py
├── outputs/
└── plots/
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate # macOS/Linux

pip install -r requirements.txt
```

## Run all experiments

```bash
python run_all.py
```

This creates CSV files in `outputs/` and PNG figures in `plots/`.

## Run tests

```bash
python -m pytest tests
```

## Main CSV outputs

| CSV file | Purpose |
|---|---|
| `case_summary.csv` | Expanded recurrence cases C1-C14 with classification and selected mode. |
| `symbolic_results.csv` | Closed forms, verification status, and match count for symbolic cases. |
| `sympy_comparison_results.csv` | External SymPy comparison for comparable cases. |
| `generated_terms.csv` | Generated sequence terms for all cases. |
| `simulation_indicators.csv` | Multi-indicator behavioural analysis for all cases. |
| `fallback_deep_analysis.csv` | Detailed fallback diagnostics for nonlinear, variable-coefficient, periodic, and number-theoretic cases. |
| `rowland_jump_analysis.csv` | Rowland recurrence increment sequence, jump positions, and prime/composite labels. |
| `scalability_results.csv` | Runtime measurements for increasing term counts. |
| `robustness_results.csv` | Validation/error-handling checks. |
| `ablation_summary.csv` | Initial-vs-enhanced capability comparison. |
| `tool_positioning_table.csv` | Comparison against SymPy, SageMath, MATLAB, and Mathematica. |

## Suggested paper tables from outputs

- Table III: use `case_summary.csv`
- Table IV: use `symbolic_results.csv`
- Table V: use `simulation_indicators.csv`
- Table VI: use `fallback_deep_analysis.csv`
- Table VII: use `rowland_jump_analysis.csv` summary
- Table VIII: use `scalability_results.csv`
- Table IX: use `ablation_summary.csv`
- Related-work/tool comparison: use `tool_positioning_table.csv`
