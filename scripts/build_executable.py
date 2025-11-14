"""Utility script to bundle the calculator into a standalone executable."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence


def build_executable(additional_args: Sequence[str] | None = None) -> None:
    """Build a Windows-friendly executable using PyInstaller."""

    try:
        import PyInstaller.__main__  # type: ignore[attr-defined]
    except ImportError as exc:  # pragma: no cover - requires external dependency
        raise SystemExit(
            "PyInstaller no está instalado. Ejecute 'pip install pyinstaller' antes de continuar."
        ) from exc

    project_root = Path(__file__).resolve().parents[1]
    main_module = project_root / "ti89_calculator" / "__main__.py"

    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    args = [
        str(main_module),
        "--name",
        "ti89_calculator",
        "--onefile",
        "--clean",
        "--console",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(build_dir),
        "--specpath",
        str(build_dir),
    ]

    if additional_args:
        args.extend(additional_args)

    PyInstaller.__main__.run(args)


if __name__ == "__main__":  # pragma: no cover - utilidad externa
    build_executable()
