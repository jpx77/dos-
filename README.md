# Calculadora científica avanzada (estilo TI-89)

Este proyecto provee una calculadora científica de línea de comandos inspirada en la TI-89 de Texas Instruments. Utiliza [SymPy](https://www.sympy.org) para ofrecer álgebra simbólica, cálculo, análisis numérico y utilidades de álgebra lineal desde la terminal.

## Requisitos

- Python 3.9 o superior
- Dependencias listadas en `requirements.txt`

Instalación rápida:

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows use `.venv\\Scripts\\activate`
pip install -r requirements.txt
```

## Uso interactivo

Inicie la consola inspirada en la TI-89 con:

```bash
python -m ti89_calculator
```

La consola acepta comandos específicos o expresiones libres (que se simplifican automáticamente). Escriba `help` para ver la lista completa. Los argumentos múltiples se separan con `;` al estilo de los menús de la calculadora.

### Comandos principales

| Comando | Descripción | Ejemplo |
| --- | --- | --- |
| `eval <expr>` | Evalúa y simplifica una expresión. | `eval sin(pi/6)^2 + cos(pi/6)^2` |
| `simplify <expr>` | Simplifica manualmente una expresión. | `simplify (x^3 - x)/(x^2 - 1)` |
| `diff <expr>; [var]; [orden]` | Derivadas de cualquier orden. | `diff sin(x^2); x; 2` |
| `integrate <expr>; [var]; [a]; [b]` | Integrales indefinidas o definidas. | `integrate exp(-x^2); x; -oo; oo` |
| `limit <expr>; <var>; <punto>; [dir]` | Cálculo de límites laterales. | `limit sin(x)/x; x; 0; +` |
| `series <expr>; <var>; <punto>; <orden>` | Serie de Taylor o Laurent. | `series log(1+x); x; 0; 5` |
| `numeric <expr>; [x=valor; ...; precision=n]` | Evaluación numérica con sustituciones. | `numeric sin(x); x=1.234; precision=25` |
| `solve <eq1>; [...]; [x,y,...]` | Resuelve ecuaciones y sistemas simbólicos. | `solve x^2 + y^2 = 5; x - y = 1; x,y` |
| `matrix <op>; <matriz>` | Operaciones matriciales (`det`, `inv`, `rank`, `eigen`, `rref`, `trace`). | `matrix det; [[1,2],[3,4]]` |
| `script <archivo>` | Ejecuta un archivo con comandos de la consola. | `script ejemplos.txt` |

### Ejemplo de sesión

```
ti89> diff sin(x^2); x

Derivada de orden 1 respecto a x
================================
2⋅x⋅cos(x²)

ti89> integrate exp(-x^2); x; -oo; oo

Integral definida respecto a x en [-oo, oo]
===========================================
√π

ti89> matrix eigen; [[2, 1], [1, 2]]

Valores propios
===============
⎡(3, 1), (1, 1)⎤
```

## Ejecución no interactiva

Puede encadenar comandos sin ingresar al modo interactivo:

```bash
python -m ti89_calculator -c "eval sin(pi/3)" -c "diff x^5; x; 3"
```

También es posible preparar un archivo de script (`.txt`) con una lista de comandos (uno por línea) y ejecutarlo con `python -m ti89_calculator -s ruta/al/script.txt`.

## Estructura del proyecto

```
ti89_calculator/
├── __init__.py
├── __main__.py
├── cli.py
└── engine.py
```

- `engine.py` contiene la lógica simbólica y numérica.
- `cli.py` implementa la interfaz de línea de comandos con una experiencia similar a la TI-89.

## Próximos pasos sugeridos

- Añadir exportación de resultados a formatos como LaTeX o JSON.
- Integrar graficación 2D/3D utilizando bibliotecas como Matplotlib.
- Incorporar más atajos y menús contextuales estilo calculadora física.
