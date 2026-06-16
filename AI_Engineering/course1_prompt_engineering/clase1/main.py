"""
CLI de la clase 1.

Permite ejecutar el grafo desde la terminal sin abrir LangGraph Studio:

    uv run python main.py -p "Le gusta el cine de los 90 y correr maratones"
    uv run python main.py -p "Toca jazz los fines de semana" --modo baseline

    # Modo comparativo: ejecuta baseline Y role para que veas la diferencia.
    uv run python main.py -p "Le gusta el cine de los 90" --comparar

Para la versión visual e interactiva:  uv run langgraph dev
"""

from __future__ import annotations

import argparse

from graph import graph
from logger import get_logger
from schemas import PeticionConfig

logger = get_logger("main")


#################
# ---- CLI ---- #
#################
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clase 1 — Fundamentos de prompting")
    parser.add_argument(
        "--perfil", "-p", required=True, help="Descripción de la persona y el contexto"
    )
    parser.add_argument(
        "--modo",
        "-m",
        choices=["baseline", "role"],
        default="role",
        help="baseline = prompt mínimo; role = prompt con rol (por defecto)",
    )
    parser.add_argument(
        "--comparar",
        action="store_true",
        help="Ejecuta baseline y role e imprime ambas para compararlas",
    )
    return parser.parse_args()


##########################################
# ---- Presentación de un resultado ---- #
##########################################
def _imprimir(modo: str, resultado: dict) -> None:
    print(f"\n=== MODO: {modo} ===")
    print("Apertura:", resultado["apertura"])
    print("Tono:    ", resultado["tono"])
    print("Por qué: ", resultado["justificacion"])


##############################
# ---- Punto de entrada ---- #
##############################
def main() -> None:
    args = parse_args()

    # Validamos la entrada con Pydantic antes de tocar el grafo.
    peticion = PeticionConfig(perfil=args.perfil, modo=args.modo)

    # Decidimos qué modos ejecutar: uno solo, o los dos para comparar.
    modos = ["baseline", "role"] if args.comparar else [peticion.modo]

    for modo in modos:
        logger.info(f"Ejecutando grafo en modo '{modo}'")
        resultado = graph.invoke({"perfil": peticion.perfil, "modo": modo})
        _imprimir(modo, resultado)

    logger.success("Listo")  # type: ignore[attr-defined]
    if args.comparar:
        print("\nObserva: el modo 'role' suele sonar más natural y conectado.")


if __name__ == "__main__":
    main()
