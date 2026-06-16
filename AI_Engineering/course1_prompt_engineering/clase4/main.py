"""
CLI de la clase 4 (Evaluator-Optimizer).

    uv run python main.py -c "Le apasiona la astronomía y hornear pan"
    uv run python main.py -c "Toca el chelo" --umbral 9 --max-iteraciones 4
    uv run langgraph dev   # versión visual del ciclo

Imprime el historial completo: cómo el puntaje sube vuelta a vuelta.
"""

from __future__ import annotations

import argparse

from graph import graph
from logger import get_logger
from schemas import EvalConfig

logger = get_logger("main")


#################
# ---- CLI ---- #
#################
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clase 4 — Evaluator-Optimizer")
    parser.add_argument("--contexto", "-c", required=True, help="Perfil y situación")
    parser.add_argument("--umbral", type=float, default=8.0, help="Puntaje mínimo (0-10)")
    parser.add_argument(
        "--max-iteraciones", type=int, default=3, help="Tope de vueltas del ciclo"
    )
    return parser.parse_args()


##############################
# ---- Punto de entrada ---- #
##############################
def main() -> None:
    args = parse_args()
    config = EvalConfig(
        contexto=args.contexto,
        umbral=args.umbral,
        max_iteraciones=args.max_iteraciones,
    )

    logger.info("Iniciando el ciclo evaluator-optimizer")
    resultado = graph.invoke(
        {
            "contexto": config.contexto,
            "umbral": config.umbral,
            "max_iteraciones": config.max_iteraciones,
            "iteracion": 0,
            "historial": [],
        }
    )

    logger.success("Ciclo terminado")  # type: ignore[attr-defined]
    print("\n--- HISTORIAL DE ITERACIONES ---")
    for linea in resultado["historial"]:
        print(" •", linea)

    print(f"\nIteraciones usadas: {resultado['iteracion']}")
    print(f"Puntaje final:      {resultado['puntaje']}  (aprobado={resultado['aprobado']})")
    print("\n--- MENSAJE FINAL ---")
    print(resultado["borrador"])


if __name__ == "__main__":
    main()
