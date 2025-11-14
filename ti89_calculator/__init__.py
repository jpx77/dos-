"""Advanced TI-89 inspired scientific calculator package."""

from .engine import (
    evaluate_expression,
    simplify_expression,
    differentiate_expression,
    integrate_expression,
    solve_equations,
    series_expansion,
    limit_expression,
    numeric_evaluation,
    matrix_operation,
    format_result,
)

__all__ = [
    "evaluate_expression",
    "simplify_expression",
    "differentiate_expression",
    "integrate_expression",
    "solve_equations",
    "series_expansion",
    "limit_expression",
    "numeric_evaluation",
    "matrix_operation",
    "format_result",
]
