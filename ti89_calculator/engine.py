"""Core symbolic and numeric computation utilities for the TI-89 inspired calculator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Union

import sympy as sp

Number = Union[int, float, complex, sp.Number]
ExpressionLike = Union[str, sp.Expr]


class CalculatorError(Exception):
    """Base error raised for calculator specific issues."""


@dataclass(frozen=True)
class EvaluationResult:
    """Container describing the result of a calculator operation."""

    output: sp.Expr
    description: str

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        return f"{self.description}: {sp.pretty(self.output)}"


def _safe_namespace(extra_locals: Optional[Mapping[str, object]] = None) -> Dict[str, object]:
    """Return a namespace with approved symbols for sympify."""

    namespace: Dict[str, object] = {
        name: getattr(sp, name)
        for name in (
            "sin",
            "cos",
            "tan",
            "asin",
            "acos",
            "atan",
            "sinh",
            "cosh",
            "tanh",
            "exp",
            "log",
            "ln",
            "sqrt",
            "pi",
            "E",
            "I",
            "Matrix",
            "Symbol",
            "symbols",
            "diff",
            "integrate",
            "limit",
            "series",
            "factor",
            "expand",
            "simplify",
        )
    }
    namespace.update({
        "abs": sp.Abs,
        "sign": sp.sign,
        "det": sp.det,
        "eye": sp.eye,
        "zeros": sp.zeros,
    })

    if extra_locals:
        namespace.update(extra_locals)
    return namespace


def _sympify_expression(expression: ExpressionLike, locals: Optional[Mapping[str, object]] = None) -> sp.Expr:
    if isinstance(expression, sp.Expr):
        return expression
    try:
        return sp.sympify(expression, locals=_safe_namespace(locals))
    except (sp.SympifyError, TypeError) as exc:  # pragma: no cover - defensive
        raise CalculatorError(f"No se pudo interpretar la expresión: {expression}") from exc


def evaluate_expression(expression: ExpressionLike, substitutions: Optional[Mapping[str, Number]] = None) -> EvaluationResult:
    """Evaluate an expression symbolically and optionally apply substitutions."""

    expr = _sympify_expression(expression)
    if substitutions:
        subs_expr = {sp.Symbol(str(k)): v for k, v in substitutions.items()}
        expr = expr.subs(subs_expr)
    simplified = sp.simplify(expr)
    return EvaluationResult(simplified, "Resultado simplificado")


def simplify_expression(expression: ExpressionLike) -> EvaluationResult:
    expr = _sympify_expression(expression)
    simplified = sp.simplify(expr)
    return EvaluationResult(simplified, "Expresión simplificada")


def differentiate_expression(expression: ExpressionLike, variable: str = "x", order: int = 1) -> EvaluationResult:
    expr = _sympify_expression(expression)
    symbol = sp.Symbol(variable)
    derivative = sp.diff(expr, symbol, order)
    return EvaluationResult(derivative, f"Derivada de orden {order} respecto a {variable}")


def integrate_expression(
    expression: ExpressionLike,
    variable: str = "x",
    lower: Optional[Number] = None,
    upper: Optional[Number] = None,
) -> EvaluationResult:
    expr = _sympify_expression(expression)
    symbol = sp.Symbol(variable)
    if lower is None or upper is None:
        result = sp.integrate(expr, symbol)
        description = f"Integral indefinida respecto a {variable}"
    else:
        result = sp.integrate(expr, (symbol, lower, upper))
        description = f"Integral definida respecto a {variable} en [{lower}, {upper}]"
    return EvaluationResult(result, description)


def series_expansion(expression: ExpressionLike, variable: str, point: Number, order: int) -> EvaluationResult:
    expr = _sympify_expression(expression)
    symbol = sp.Symbol(variable)
    result = sp.series(expr, symbol, point, order)
    return EvaluationResult(result.removeO(), f"Serie de {variable} alrededor de {point} hasta orden {order}")


def limit_expression(expression: ExpressionLike, variable: str, point: Number, direction: str = "+") -> EvaluationResult:
    expr = _sympify_expression(expression)
    symbol = sp.Symbol(variable)
    limit_result = sp.limit(expr, symbol, point, dir=direction)
    return EvaluationResult(limit_result, f"Límite cuando {variable}→{point} ({direction})")


def numeric_evaluation(
    expression: ExpressionLike,
    substitutions: Optional[Mapping[str, Number]] = None,
    precision: int = 15,
) -> EvaluationResult:
    expr = _sympify_expression(expression)
    if substitutions:
        expr = expr.subs({sp.Symbol(str(k)): v for k, v in substitutions.items()})
    numeric = sp.N(expr, precision)
    return EvaluationResult(numeric, f"Evaluación numérica con precisión {precision}")


def _parse_equation(expr: ExpressionLike) -> Union[sp.Eq, sp.Expr]:
    if isinstance(expr, sp.Eq):
        return expr
    if isinstance(expr, sp.Expr):
        return expr
    if "=" in str(expr):
        left, right = map(str.strip, str(expr).split("=", 1))
        return sp.Eq(_sympify_expression(left), _sympify_expression(right))
    return _sympify_expression(expr)


def solve_equations(
    equations: Union[ExpressionLike, Sequence[ExpressionLike]],
    variables: Optional[Sequence[str]] = None,
) -> EvaluationResult:
    if isinstance(equations, (str, sp.Expr)):
        eq_list: List[Union[sp.Expr, sp.Eq]] = [_parse_equation(equations)]
    else:
        eq_list = [_parse_equation(eq) for eq in equations]

    if variables:
        symbols = sp.symbols(list(variables))
        solution = sp.solve(eq_list, symbols, dict=True)
    else:
        solution = sp.solve(eq_list, dict=True)

    if solution:
        formatted_solutions = []
        for sol in solution:
            formatted_solutions.append(
                sp.Dict(
                    {
                        (k if isinstance(k, sp.Basic) else sp.Symbol(str(k))): v
                        for k, v in sol.items()
                    }
                )
            )
        formatted = sp.FiniteSet(*formatted_solutions)
    else:
        formatted = sp.EmptySet

    return EvaluationResult(formatted, "Solución del sistema")


def _ensure_matrix(matrix: Union[str, Sequence[Sequence[Number]], sp.Matrix]) -> sp.Matrix:
    if isinstance(matrix, sp.MatrixBase):
        return sp.Matrix(matrix)
    if isinstance(matrix, str):
        try:
            data = sp.sympify(matrix, locals=_safe_namespace())
        except sp.SympifyError as exc:  # pragma: no cover - defensive
            raise CalculatorError("Formato de matriz inválido") from exc
        if isinstance(data, sp.MatrixBase):
            return sp.Matrix(data)
        return sp.Matrix(data)
    return sp.Matrix(matrix)


def matrix_operation(operation: str, matrix: Union[str, Sequence[Sequence[Number]], sp.Matrix]) -> EvaluationResult:
    mat = _ensure_matrix(matrix)
    op = operation.lower()
    if op == "det" or op == "determinant":
        result = mat.det()
        description = "Determinante"
    elif op in {"inv", "inverse"}:
        result = mat.inv()
        description = "Matriz inversa"
    elif op == "rank":
        result = mat.rank()
        description = "Rango"
    elif op in {"eigen", "eigenvals"}:
        eigenvals = mat.eigenvals()
        result = sp.Dict(eigenvals)
        description = "Valores propios (λ: multiplicidad)"
    elif op in {"eigenvects", "eigenvectors"}:
        eigenvects = mat.eigenvects()
        formatted = []
        for val, mult, vects in eigenvects:
            formatted.append(sp.Tuple(val, mult, sp.Tuple(*[sp.Matrix(v) for v in vects])))
        result = sp.FiniteSet(*formatted) if formatted else sp.EmptySet
        description = "Vectores propios"
    elif op == "rref":
        reduced, pivots = mat.rref()
        result = sp.Tuple(reduced, sp.Tuple(*pivots))
        description = "Forma reducida por filas (matriz y pivotes)"
    elif op in {"trace", "tr"}:
        result = mat.trace()
        description = "Traza"
    else:  # pragma: no cover - defensive
        raise CalculatorError(f"Operación de matriz desconocida: {operation}")
    return EvaluationResult(result, description)


def format_result(result: EvaluationResult) -> str:
    """Format a result in a way similar to a TI calculator display."""

    header = f"\n{result.description}\n" + "=" * len(result.description)
    body = sp.pretty(result.output, use_unicode=True)
    return f"{header}\n{body}\n"
