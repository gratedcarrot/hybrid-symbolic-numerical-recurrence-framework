"""
parser.py

A controlled symbolic parser for recurrence expressions.
It supports common recurrence notations and converts them into a safe internal form.

Examples accepted as expression input:
    2*a_prev + 3
    a_prev1 + a_prev2
    3*a_(n-1) - 2*a_(n-2)
    a(n-1) + gcd(n, a(n-1))

For full equations, the RHS is extracted:
    a_n = 2*a_(n-1) + 3
"""

from __future__ import annotations

from typing import Any, Dict, List
import math
import re

import sympy as sp

from .models import ParsedRecurrence, RecurrenceDefinition


SAFE_EVAL_FUNCTIONS: Dict[str, Any] = {
    "abs": abs,
    "min": min,
    "max": max,
    "pow": pow,
    "round": round,
    "gcd": math.gcd,
    "lcm": math.lcm,
    "sqrt": math.sqrt,
    "floor": math.floor,
    "ceil": math.ceil,
}

SAFE_SYMPY_FUNCTIONS: Dict[str, Any] = {
    "Abs": sp.Abs,
    "sqrt": sp.sqrt,
    "floor": sp.floor,
    "ceiling": sp.ceiling,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
}


PREV_PATTERN_UNDERSCORE = re.compile(r"\ba_prev(\d*)\b")
PREV_PATTERN_PAREN = re.compile(r"a\s*\(?\s*n\s*-\s*(\d+)\s*\)?")
PREV_PATTERN_LATEX = re.compile(r"a_\{?\s*n\s*-\s*(\d+)\s*\}?")


def extract_rhs(expression: str) -> str:
    """If an equation is supplied, keep only the right-hand side."""
    text = expression.strip()
    if "=" in text:
        return text.split("=", 1)[1].strip()
    return text


def normalize_expression(expression: str) -> str:
    """
    Convert recurrence notation to parser variables:
        a_prev or a_prev1 -> x1
        a_(n-1), a(n-1), a_{n-1} -> x1
        a_(n-2), a(n-2), a_{n-2} -> x2
    """
    text = extract_rhs(expression)
    text = text.replace("^", "**")

    # Convert a_(n-1), a(n-1), a_{n-1}; do this before a_prev.
    text = re.sub(r"a_\s*\(\s*n\s*-\s*(\d+)\s*\)", lambda m: f"x{m.group(1)}", text)
    text = re.sub(r"a\s*\(\s*n\s*-\s*(\d+)\s*\)", lambda m: f"x{m.group(1)}", text)
    text = re.sub(r"a_\{\s*n\s*-\s*(\d+)\s*\}", lambda m: f"x{m.group(1)}", text)
    text = re.sub(r"a_\s*n\s*-\s*(\d+)", lambda m: f"x{m.group(1)}", text)

    # Convert a_prev or a_prevN.
    def repl_prev(match: re.Match) -> str:
        number = match.group(1)
        return "x1" if number == "" else f"x{number}"

    text = PREV_PATTERN_UNDERSCORE.sub(repl_prev, text)
    return text.strip()


def infer_order(normalized_expression: str) -> int:
    refs = [int(x) for x in re.findall(r"\bx(\d+)\b", normalized_expression)]
    return max(refs) if refs else 1


def parse_sympy_expression(normalized_expression: str, order: int):
    """Parse expression to SymPy where possible. gcd/lcm are intentionally not symbolically parsed."""
    if re.search(r"\b(gcd|lcm)\s*\(", normalized_expression):
        return None, ["gcd/lcm expressions are treated as simulation-fallback cases."]

    n = sp.Symbol("n", integer=True, nonnegative=True)
    local_dict: Dict[str, Any] = {"n": n}
    for i in range(1, order + 1):
        local_dict[f"x{i}"] = sp.Symbol(f"x{i}")
    local_dict.update(SAFE_SYMPY_FUNCTIONS)

    try:
        return sp.sympify(normalized_expression, locals=local_dict), []
    except Exception as exc:
        return None, [f"SymPy parsing failed: {exc}"]


def build_rule(normalized_expression: str, order: int):
    """Build a safe numerical recurrence rule from the normalized expression."""
    compiled = compile(normalized_expression, "<recurrence_expression>", "eval")

    def next_term(n: int, seq: List[float]):
        if len(seq) < order:
            raise ValueError(f"Need at least {order} term(s) before generating next term.")

        local_vars: Dict[str, Any] = {"n": n}
        for i in range(1, order + 1):
            local_vars[f"x{i}"] = seq[-i]

        safe_globals = {"__builtins__": {}}
        safe_globals.update(SAFE_EVAL_FUNCTIONS)
        value = eval(compiled, safe_globals, local_vars)

        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value

    return next_term


def parse_recurrence(definition: RecurrenceDefinition) -> ParsedRecurrence:
    normalized = normalize_expression(definition.expression)
    order = infer_order(normalized)

    if len(definition.initial_terms) < order:
        raise ValueError(
            f"Insufficient initial terms. Expression has order {order}, "
            f"but only {len(definition.initial_terms)} initial term(s) were provided."
        )

    sympy_expr, warnings = parse_sympy_expression(normalized, order)
    rule = build_rule(normalized, order)

    return ParsedRecurrence(
        definition=definition,
        normalized_expression=normalized,
        order=order,
        previous_symbols=[f"x{i}" for i in range(1, order + 1)],
        rule=rule,
        sympy_expression=sympy_expr,
        parse_warnings=warnings,
    )
