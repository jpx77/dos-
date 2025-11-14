"""Command line interface for the TI-89 inspired scientific calculator."""
from __future__ import annotations

import argparse
import cmd
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import sympy as sp
from colorama import Fore, Style, init as colorama_init

from . import (
    differentiate_expression,
    evaluate_expression,
    integrate_expression,
    limit_expression,
    matrix_operation,
    numeric_evaluation,
    series_expansion,
    simplify_expression,
    solve_equations,
)
from .engine import CalculatorError, EvaluationResult


_COLORAMA_READY = False


def _ensure_colorama_initialized() -> None:
    global _COLORAMA_READY
    if not _COLORAMA_READY:
        colorama_init(autoreset=True)
        _COLORAMA_READY = True


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
    """Interactive shell with light blue themed output similar to a TI-89."""

    def __init__(self, use_color: bool = True) -> None:
        super().__init__()
        self.use_color = use_color
        if self.use_color:
            _ensure_colorama_initialized()
        self.prompt = self._accent("ti89> ")
        self.intro = self._accent(
            "Calculadora científica estilo TI-89. Escriba 'help' para ver los comandos disponibles."
        )

    # --- Styling helpers -------------------------------------------------

    def _accent(self, message: str) -> str:
        if not self.use_color:
            return message
        return f"{Style.BRIGHT}{Fore.LIGHTBLUE_EX}{message}{Style.RESET_ALL}"

    def _emphasis(self, message: str) -> str:
        if not self.use_color:
            return message
        return f"{Style.BRIGHT}{Fore.WHITE}{message}{Style.RESET_ALL}"

    def _error(self, message: str) -> str:
        if not self.use_color:
            return message
        return f"{Style.BRIGHT}{Fore.LIGHTRED_EX}{message}{Style.RESET_ALL}"

    def _muted(self, message: str) -> str:
        if not self.use_color:
            return message
        return f"{Fore.CYAN}{message}{Style.RESET_ALL}"

    def _print_result(self, result: EvaluationResult) -> None:
        header = result.description
        body = sp.pretty(result.output, use_unicode=True)
        print()
        print(self._accent(header))
        print(self._accent("=" * len(header)))
        if body.strip():
            for line in body.splitlines():
                print(self._emphasis(line))
        else:
            print(self._emphasis("0"))
        print()

    def _print_error(self, message: str) -> None:
        print(self._error(f"Error: {message}"))

    def _print_hint(self, message: str) -> None:
        print(self._muted(message))

    # --- Command handlers -------------------------------------------------

    def default(self, line: str) -> None:  # pragma: no cover - interfaz interactiva
        if not line.strip():
            return
        try:
            result = evaluate_expression(line)
            self._print_result(result)
        except CalculatorError as exc:
            self._print_error(str(exc))

    def do_eval(self, arg: str) -> None:
        """eval <expresión>: Evalúa y simplifica una expresión."""

        try:
            result = evaluate_expression(arg)
            self._print_result(result)
        except CalculatorError as exc:
            self._print_error(str(exc))

    def do_simplify(self, arg: str) -> None:
        """simplify <expresión>: Simplifica una expresión."""

        try:
            result = simplify_expression(arg)
            self._print_result(result)
        except CalculatorError as exc:
            self._print_error(str(exc))

    def do_diff(self, arg: str) -> None:
        """diff <expr>; [variable]; [orden]: Calcula derivadas."""

        pieces = _segment_arguments(arg)
        if not pieces:
            self._print_hint("Uso: diff <expr>; [variable]; [orden]")
            return
        expr = pieces[0]
        variable = pieces[1] if len(pieces) > 1 else "x"
        order = int(pieces[2]) if len(pieces) > 2 else 1
        try:
            result = differentiate_expression(expr, variable, order)
            self._print_result(result)
        except (CalculatorError, ValueError) as exc:
            self._print_error(str(exc))

    def do_integrate(self, arg: str) -> None:
        """integrate <expr>; [variable]; [inferior]; [superior]: Calcula integrales."""

        pieces = _segment_arguments(arg)
        if not pieces:
            self._print_hint("Uso: integrate <expr>; [variable]; [inferior]; [superior]")
            return
        expr = pieces[0]
        variable = pieces[1] if len(pieces) > 1 else "x"
        lower = pieces[2] if len(pieces) > 2 else None
        upper = pieces[3] if len(pieces) > 3 else None
        try:
            lower_value = sp.sympify(lower) if lower is not None else None
            upper_value = sp.sympify(upper) if upper is not None else None
            result = integrate_expression(expr, variable, lower_value, upper_value)
            self._print_result(result)
        except (CalculatorError, ValueError) as exc:
            self._print_error(str(exc))

    def do_limit(self, arg: str) -> None:
        """limit <expr>; <variable>; <punto>; [dirección]: Calcula límites."""

        pieces = _segment_arguments(arg)
        if len(pieces) < 3:
            self._print_hint("Uso: limit <expr>; <variable>; <punto>; [dirección]")
            return
        expr, variable, point = pieces[:3]
        direction = pieces[3] if len(pieces) > 3 else "+"
        try:
            result = limit_expression(expr, variable, sp.sympify(point), direction)
            self._print_result(result)
        except (CalculatorError, ValueError) as exc:
            self._print_error(str(exc))

    def do_series(self, arg: str) -> None:
        """series <expr>; <variable>; <punto>; <orden>: Desarrolla series de Taylor."""

        pieces = _segment_arguments(arg)
        if len(pieces) < 4:
            self._print_hint("Uso: series <expr>; <variable>; <punto>; <orden>")
            return
        expr, variable, point, order = pieces[:4]
        try:
            result = series_expansion(expr, variable, sp.sympify(point), int(order))
            self._print_result(result)
        except (CalculatorError, ValueError) as exc:
            self._print_error(str(exc))

    def do_numeric(self, arg: str) -> None:
        """numeric <expr>; [clave=valor ...]; [precision=nn]: Evalúa numéricamente."""

        pieces = _segment_arguments(arg)
        if not pieces:
            self._print_hint("Uso: numeric <expr>; [x=valor; y=valor; precision=nn]")
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
            self._print_result(result)
        except (CalculatorError, ValueError) as exc:
            self._print_error(str(exc))

    def do_solve(self, arg: str) -> None:
        """solve <eq1>; [eq2; ...]; [variables separadas por comas]: Resuelve sistemas."""

        pieces = _segment_arguments(arg)
        if not pieces:
            self._print_hint("Uso: solve <eq>; [eq2; ...]; [x,y,...]")
            return
        variables: Optional[List[str]] = None
        equations = pieces
        if pieces and "," in pieces[-1]:
            variables = [var.strip() for var in pieces[-1].split(",") if var.strip()]
            equations = pieces[:-1] or []
        if not equations:
            self._print_hint("Debe proporcionar al menos una ecuación.")
            return
        try:
            result = solve_equations(equations, variables)
            self._print_result(result)
        except CalculatorError as exc:
            self._print_error(str(exc))

    def do_matrix(self, arg: str) -> None:
        """matrix <operación>; <matriz>: Opera con matrices (det, inv, rank, eigen, rref, trace)."""

        pieces = _segment_arguments(arg)
        if len(pieces) < 2:
            self._print_hint("Uso: matrix <operación>; <matriz>")
            return
        operation, matrix_expr = pieces[0], pieces[1]
        try:
            result = matrix_operation(operation, matrix_expr)
            self._print_result(result)
        except CalculatorError as exc:
            self._print_error(str(exc))

    def do_script(self, arg: str) -> None:
        """script <archivo>: Ejecuta un archivo con comandos del intérprete."""

        if not arg:
            self._print_hint("Uso: script <archivo>")
            return
        path = Path(arg).expanduser()
        if not path.exists():
            self._print_error(f"Archivo no encontrado: {path}")
            return
        for line in path.read_text(encoding="utf8").splitlines():  # pragma: no cover - lectura de archivos
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            print(self._accent(f"→ {line}"))
            self.onecmd(line)

    def do_exit(self, _: str) -> bool:  # pragma: no cover - flujo interactivo
        """Salir del intérprete."""

        print(self._accent("Hasta pronto"))
        return True

    do_quit = do_exit


def run_cli(commands: Optional[List[str]] = None, use_color: bool = True) -> None:
    shell = CalculatorShell(use_color=use_color)
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
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Desactiva los colores ANSI en la salida (útil al redirigir a archivos)",
    )
    args = parser.parse_args(argv)

    commands: List[str] = []
    if args.command:
        commands.extend(args.command)
    if args.script:
        commands.extend(_load_commands_from_file(args.script))

    run_cli(commands or None, use_color=not args.no_color)


if __name__ == "__main__":  # pragma: no cover
    main()
