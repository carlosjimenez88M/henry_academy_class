"""
CLI de la clase 3 (Routing).

    uv run python main.py -p "Quiero disculparme por haber llegado tarde a la cita"
    uv run python main.py -p "Me gustaría invitarla a tomar un café sin presión"
    uv run langgraph dev   # versión visual

Verás qué ruta eligió el router y la respuesta del especialista correspondiente.
"""

#######################
# ---- libraries ---- #
#######################

from __future__ import annotations

import argparse

from graph import graph
from logger import get_logger
from schemas import RoutingConfig

logger = get_logger("main")


#################
# ---- CLI ---- #
#################
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clase 3 — Routing")
    parser.add_argument(
        "--peticion", "-p", required=True, help="Lo que la persona quiere expresar"
    )
    return parser.parse_args()


##############################
# ---- Punto de entrada ---- #
##############################
def main() -> None:
    args = parse_args()
    config = RoutingConfig(peticion=args.peticion)

    logger.info("Ejecutando el grafo con routing")
    resultado = graph.invoke({"peticion": config.peticion})

    logger.success("Listo")  # type: ignore[attr-defined]
    print(f"\nRuta elegida: {resultado['ruta']}")
    print(f"Motivo:       {resultado['razon_ruta']}")
    print("\n--- RESPUESTA ---")
    print(resultado["respuesta"])


if __name__ == "__main__":
    main()
