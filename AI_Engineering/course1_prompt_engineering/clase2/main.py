"""
CLI de la clase 2 (Prompt Chaining).

    uv run python main.py -c "Le gusta el senderismo y los documentales de naturaleza"
    uv run langgraph dev   # versión visual

Imprime TODOS los pasos intermedios para que veas cómo evoluciona el mensaje a
lo largo de la cadena.
"""

from __future__ import annotations

import argparse

from graph import graph
from logger import get_logger
from schemas import ChainConfig

logger = get_logger("main")


#################
# ---- CLI ---- #
#################
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clase 2 — Prompt Chaining")
    parser.add_argument(
        "--contexto", "-c", required=True, help="Perfil de la persona y la situación"
    )
    return parser.parse_args()


##############################
# ---- Punto de entrada ---- #
##############################
def main() -> None:
    args = parse_args()
    config = ChainConfig(contexto=args.contexto)

    logger.info("Ejecutando la cadena de 5 pasos")
    resultado = graph.invoke({"contexto": config.contexto})

    logger.success("Cadena completada")  # type: ignore[attr-defined]
    print("\n1) Idea base:       ", resultado["idea"])
    print("2) Versión poética: ", resultado["version_poetica"])
    print("3) Versión natural: ", resultado["version_natural"])
    print("4) Mensaje final:   ", resultado["mensaje_final"])
    print("\n5) Verificación:", "APROBADO" if resultado["aprobado"] else "RECHAZADO")
    print("   Observaciones:", resultado["observaciones"])


if __name__ == "__main__":
    main()
