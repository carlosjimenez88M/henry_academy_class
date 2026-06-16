"""
CLI del módulo de comparación OpenAI vs Gemini.

    uv run python main.py -p "Le gusta el cine de los 90 y correr maratones"
    uv run langgraph dev   # versión visual (verás los dos nodos en paralelo)

Requiere OPENAI_API_KEY y GOOGLE_API_KEY en el .env del curso.
"""

from __future__ import annotations

import argparse

from graph import graph
from logger import get_logger
from schemas import ComparacionConfig

logger = get_logger("main")


#################
# ---- CLI ---- #
#################
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Comparativa OpenAI vs Gemini")
    parser.add_argument("--perfil", "-p", required=True, help="Perfil y situación")
    return parser.parse_args()


##############################
# ---- Punto de entrada ---- #
##############################
def main() -> None:
    args = parse_args()
    config = ComparacionConfig(perfil=args.perfil)

    logger.info("Comparando OpenAI vs Gemini")
    resultado = graph.invoke({"perfil": config.perfil})

    logger.success("Comparación terminada")  # type: ignore[attr-defined]
    print("\n--- OpenAI ---")
    print(resultado["salida_openai"], f"\n(puntaje: {resultado['puntaje_openai']}/10)")
    print("\n--- Gemini ---")
    print(resultado["salida_gemini"], f"\n(puntaje: {resultado['puntaje_gemini']}/10)")
    print(f"\nGANADOR: {resultado['ganador'].upper()}")
    print("Motivo: ", resultado["justificacion"])


if __name__ == "__main__":
    main()
