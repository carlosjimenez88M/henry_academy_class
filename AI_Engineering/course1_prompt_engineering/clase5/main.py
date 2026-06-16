"""
CLI de la clase 5 (ReAct).

    uv run python main.py -p "Le gusta el cine de autor y los vinilos"
    uv run python main.py -p "Disfruta cocinar y los mercados" --traza
    uv run langgraph dev   # versión visual del bucle ReAct

Con --traza ves el ciclo completo: qué herramientas pidió el agente, con qué
argumentos y qué le devolvieron. Es la mejor forma de entender ReAct.
"""

#######################
# ---- libraries ---- #
#######################

from __future__ import annotations

import argparse

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from graph import graph
from logger import get_logger
from schemas import ReactConfig

logger = get_logger("main")


#################
# ---- CLI ---- #
#################
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clase 5 — Agente ReAct")
    parser.add_argument("--perfil", "-p", required=True, help="Perfil y situación")
    parser.add_argument(
        "--traza", action="store_true", help="Muestra el ciclo razonar/actuar paso a paso"
    )
    return parser.parse_args()


#####################################################################
# ---- Traza: imprime el recorrido razonar → actuar → observar ---- #
#####################################################################
def _imprimir_traza(mensajes: list) -> None:
    print("\n--- TRAZA ReAct ---")
    for m in mensajes:
        if isinstance(m, AIMessage) and m.tool_calls:
            for tc in m.tool_calls:
                print(f"[ACCIÓN]      {tc['name']}({tc['args']})")
        elif isinstance(m, ToolMessage):
            print(f"[OBSERVACIÓN] {m.content}")
        elif isinstance(m, AIMessage) and m.content:
            print(f"[PENSAMIENTO] {m.content}")


##############################
# ---- Punto de entrada ---- #
##############################
def main() -> None:
    args = parse_args()
    config = ReactConfig(perfil=args.perfil)

    logger.info("Ejecutando el agente ReAct")
    entrada = HumanMessage(content=f"Perfil de la persona:\n{config.perfil}")
    # recursion_limit acota el bucle por si el agente se enreda (cinturón de seguridad).
    resultado = graph.invoke({"messages": [entrada]}, {"recursion_limit": 12})

    if args.traza:
        _imprimir_traza(resultado["messages"])

    logger.success("Agente terminado")  # type: ignore[attr-defined]
    print("\n--- MENSAJE FINAL ---")
    print(resultado["messages"][-1].content)


if __name__ == "__main__":
    main()
