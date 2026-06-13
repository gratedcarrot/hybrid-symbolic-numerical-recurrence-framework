# Hybrid Symbolic-Numerical Recurrence Model

This repository contains the implementation used for the paper:

**A Hybrid Symbolic-Numerical Model for Solving and Simulating Recurrence Relations**

The model follows a solve-or-simulate approach for recurrence relation analysis. It classifies a recurrence, applies symbolic solving where supported, verifies symbolic outputs using generated terms, and routes unsupported recurrence forms to simulation-based behavioural analysis.

## Main Features

### Symbolic solving ability

- First-order homogeneous and non-homogeneous recurrences
- Arithmetic progression cases
- First-order polynomial non-homogeneous cases
- Second-order linear recurrences
- Selected higher-order homogeneous linear recurrences
- Repeated characteristic-root cases
- Closed-form verification against recurrence-generated terms
- External SymPy comparison for comparable symbolic cases

### Simulation and fallback ability

- First and second difference analysis
- Ratio trend analysis
- Logarithmic growth analysis
- Digit-length growth analysis
- Monotonicity detection
- Periodicity and tail-cycle detection
- Spike and jump detection
- Overflow and divergence guarding
- Rowland-specific increment and prime-jump analysis
- Selected OEIS / known-sequence matching

## Folder Structure

```text
recurrence_model/
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

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

For macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run All Experiments

```bash
python run_all.py
```

This generates CSV files in the `outputs/` folder and PNG figures in the `plots/` folder.

## Run Tests

```bash
python -m pytest tests
```

## Main CSV Outputs

| CSV file | Purpose |
|---|---|
| `case_summary.csv` | Expanded recurrence cases C1-C14 with classification and selected mode. |
| `symbolic_results.csv` | Closed forms, verification status, and match count for symbolic cases. |
| `sympy_comparison_results.csv` | External SymPy comparison for comparable symbolic cases. |
| `generated_terms.csv` | Generated sequence terms for all cases. |
| `simulation_indicators.csv` | Multi-indicator behavioural analysis for all cases. |
| `fallback_deep_analysis.csv` | Detailed fallback diagnostics for nonlinear, variable-coefficient, periodic, and number-theoretic cases. |
| `rowland_jump_analysis.csv` | Rowland recurrence increment sequence, jump positions, and prime/composite labels. |
| `sequence_matching_results.csv` | Selected OEIS / known-sequence matching results. |
| `scalability_results.csv` | Runtime measurements for increasing term counts. |
| `robustness_results.csv` | Validation and error-handling checks. |
| `tool_positioning_table.csv` | Comparison against SymPy, SageMath, MATLAB, and Mathematica. |

## Suggested Paper Tables from Outputs

| Paper table | Source file |
|---|---|
| Table III | `case_summary.csv` |
| Table IV | `symbolic_results.csv` and `sympy_comparison_results.csv` |
| Table V | `simulation_indicators.csv` |
| Table VI | `sequence_matching_results.csv` |
| Table VII | `fallback_deep_analysis.csv` and `rowland_jump_analysis.csv` summary |
| Related-work/tool comparison | `tool_positioning_table.csv` |

## Recurrence Cases Covered

The implementation evaluates fourteen recurrence cases, including:

- First-order homogeneous recurrence
- First-order non-homogeneous recurrence
- Arithmetic progression
- Index-term recurrence
- Fibonacci-type recurrence
- Second-order linear recurrence
- Selected higher-order linear recurrence
- Repeated-root recurrence
- Polynomial non-homogeneous recurrence
- Variable-coefficient factorial-type recurrence
- Rowland gcd recurrence
- Nonlinear square recurrence
- Modular periodic recurrence
- Nonlinear product recurrence

## Output Figures

The `plots/` folder contains figures for selected recurrence behaviours, including:

- Fibonacci-type ratio stabilisation
- Rowland gcd increment jumps
- Nonlinear digit-length growth
- Periodic cycle behaviour, where applicable

## Notes

This implementation is designed as a recurrence-specific analysis workflow. It is not intended to replace full computer algebra systems such as SymPy, SageMath, MATLAB, or Wolfram Mathematica. Instead, it combines classification, symbolic solving, computational verification, simulation fallback, behavioural analysis, selected sequence matching, and visualisation in one lightweight Python-based framework.

## License

This project is released under the MIT License.
