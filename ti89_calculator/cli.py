"""Command line interface for the TI-89 inspired scientific calculator."""
from __future__ import annotations

import argparse
import cmd
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import sympy as sp

from . import (
    differentiate_expression,
    evaluate_expression,
    format_result,
    integrate_expression,
    limit_expression,
    matrix_operation,
    numeric_evaluation,
    series_expansion,
    simplify_expression,
    solve_equations,
)
from .engine import CalculatorError


def _segment_arguments(raw: str) -> List[str]:
    """Split arguments using ';' as delimiter while preserving nested structures."""

    if not raw:
        return []
    segments = [segment.strip() for segment in raw.split(";")]
    return [segment for segment in segments if segment]


def _parse_key_values(pairs: Iterable[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise CalculatorError(f"Argumento inválido, se esperaba clave=valor y se recibió '{pair}'")
        key, value = pair.split("=", 1)
        mapping[key.strip()] = value.strip()
    return mapping


class CalculatorShell(cmd.Cmd):
    intro = "Calculadora científica estilo TI-89. Escriba 'help' para ver los comandos disponibles."
    prompt = "ti89> "

    def default(self, line: str) -> None:  # pragma: no cover - interfaz interactiva
        if not line.strip():
            return
        try:
            result = evaluate_expression(line)
            print(format_result(result))
        except CalculatorError as exc:
            print(f"Error: {exc}")

    def do_eval(self, arg: str) -> None:
        """eval <expresión>: Evalúa y simplifica una expresión."""

        try:
            result = evaluate_expression(arg)
            print(format_result(result))
        except CalculatorError as exc:
            print(f"Error: {exc}")

    def do_simplify(self, arg: str) -> None:
        """simplify <expresión>: Simplifica una expresión."""

        try:
            result = simplify_expression(arg)
            print(format_result(result))
        except CalculatorError as exc:
            print(f"Error: {exc}")

    def do_diff(self, arg: str) -> None:
        """diff <expr>; [variable]; [orden]: Calcula derivadas."""

        pieces = _segment_arguments(arg)
        if not pieces:
            print("Uso: diff <expr>; [variable]; [orden]")
            return
        expr = pieces[0]
        variable = pieces[1] if len(pieces) > 1 else "x"
        order = int(pieces[2]) if len(pieces) > 2 else 1
        try:
            result = differentiate_expression(expr, variable, order)
            print(format_result(result))
        except (CalculatorError, ValueError) as exc:
            print(f"Error: {exc}")

    def do_integrate(self, arg: str) -> None:
        """integrate <expr>; [variable]; [inferior]; [superior]: Calcula integrales."""

        pieces = _segment_arguments(arg)
        if not pieces:
            print("Uso: integrate <expr>; [variable]; [inferior]; [superior]")
            return
        expr = pieces[0]
        variable = pieces[1] if len(pieces) > 1 else "x"
        lower = pieces[2] if len(pieces) > 2 else None
        upper = pieces[3] if len(pieces) > 3 else None
        try:
            lower_value = sp.sympify(lower) if lower is not None else None
            upper_value = sp.sympify(upper) if upper is not None else None
            result = integrate_expression(expr, variable, lower_value, upper_value)
            print(format_result(result))
        except (CalculatorError, ValueError) as exc:
            print(f"Error: {exc}")

    def do_limit(self, arg: str) -> None:
        """limit <expr>; <variable>; <punto>; [dirección]: Calcula límites."""

        pieces = _segment_arguments(arg)
        if len(pieces) < 3:
            print("Uso: limit <expr>; <variable>; <punto>; [dirección]")
            return
        expr, variable, point = pieces[:3]
        direction = pieces[3] if len(pieces) > 3 else "+"
        try:
            result = limit_expression(expr, variable, sp.sympify(point), direction)
            print(format_result(result))
        except (CalculatorError, ValueError) as exc:
            print(f"Error: {exc}")

    def do_series(self, arg: str) -> None:
        """series <expr>; <variable>; <punto>; <orden>: Desarrolla series de Taylor."""

        pieces = _segment_arguments(arg)
        if len(pieces) < 4:
            print("Uso: series <expr>; <variable>; <punto>; <orden>")
            return
        expr, variable, point, order = pieces[:4]
        try:
            result = series_expansion(expr, variable, sp.sympify(point), int(order))
            print(format_result(result))
        except (CalculatorError, ValueError) as exc:
            print(f"Error: {exc}")

    def do_numeric(self, arg: str) -> None:
        """numeric <expr>; [clave=valor ...]; [precision=nn]: Evalúa numéricamente."""

        pieces = _segment_arguments(arg)
        if not pieces:
            print("Uso: numeric <expr>; [x=valor; y=valor; precision=nn]")
            return
        expr = pieces[0]
        substitutions = {}
        precision = 15
        if len(pieces) > 1:
            config = _parse_key_values(pieces[1:])
            for key, value in config.items():
                if key.lower() == "precision":
                    precision = int(value)
                else:
                    substitutions[key] = sp.sympify(value)
        try:
            result = numeric_evaluation(expr, substitutions or None, precision)
            print(format_result(result))
        except (CalculatorError, ValueError) as exc:
            print(f"Error: {exc}")

    def do_solve(self, arg: str) -> None:
        """solve <eq1>; [eq2; ...]; [variables separadas por comas]: Resuelve sistemas."""

        pieces = _segment_arguments(arg)
        if not pieces:
            print("Uso: solve <eq>; [eq2; ...]; [x,y,...]")
            return
        variables: Optional[List[str]] = None
        equations = pieces
        if pieces and "," in pieces[-1]:
            variables = [var.strip() for var in pieces[-1].split(",") if var.strip()]
            equations = pieces[:-1] or []
        if not equations:
            print("Debe proporcionar al menos una ecuación.")
            return
        try:
            result = solve_equations(equations, variables)
            print(format_result(result))
        except CalculatorError as exc:
            print(f"Error: {exc}")

    def do_matrix(self, arg: str) -> None:
        """matrix <operación>; <matriz>: Opera con matrices (det, inv, rank, eigen, rref, trace)."""

        pieces = _segment_arguments(arg)
        if len(pieces) < 2:
            print("Uso: matrix <operación>; <matriz>")
            return
        operation, matrix_expr = pieces[0], pieces[1]
        try:
            result = matrix_operation(operation, matrix_expr)
            print(format_result(result))
        except CalculatorError as exc:
            print(f"Error: {exc}")

    def do_script(self, arg: str) -> None:
        """script <archivo>: Ejecuta un archivo con comandos del intérprete."""

        if not arg:
            print("Uso: script <archivo>")
            return
        path = Path(arg).expanduser()
        if not path.exists():
            print(f"Archivo no encontrado: {path}")
            return
        for line in path.read_text(encoding="utf8").splitlines():  # pragma: no cover - lectura de archivos
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            print(f"→ {line}")
            self.onecmd(line)

    def do_exit(self, _: str) -> bool:  # pragma: no cover - flujo interactivo
        """Salir del intérprete."""

        print("Hasta pronto")
        return True

    do_quit = do_exit


def run_cli(commands: Optional[List[str]] = None) -> None:
    shell = CalculatorShell()
    if commands:
        for command in commands:
            shell.onecmd(command)
    else:
        shell.cmdloop()


def _load_commands_from_file(file_path: Path) -> List[str]:
    content = file_path.read_text(encoding="utf8")
    return [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Calculadora científica avanzada estilo TI-89")
    parser.add_argument(
        "--command",
        "-c",
        action="append",
        help="Comando directo para ejecutar (puede repetirse)",
    )
    parser.add_argument(
        "--script",
        "-s",
        type=Path,
        help="Archivo con comandos a ejecutar",
    )
    args = parser.parse_args(argv)

    commands: List[str] = []
    if args.command:
        commands.extend(args.command)
    if args.script:
        commands.extend(_load_commands_from_file(args.script))

    run_cli(commands or None)


if __name__ == "__main__":  # pragma: no cover
    main()
