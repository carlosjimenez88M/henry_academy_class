"""
Grafo de la clase 1: tu primer grafo en LangGraph.

Es deliberadamente mínimo —un solo nodo— para entender las piezas sin ruido:
    START ──> generar_apertura ──> END

Conceptos que introduce:
- StateGraph y un State tipado con TypedDict.
- Un nodo = una función pura `state -> dict` (devuelve solo lo que cambia).
- LCEL: `prompt | llm.with_structured_output(Schema)` produce un objeto Pydantic.

El objeto `graph` del final es lo que `langgraph dev` carga (ver langgraph.json).
"""

from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from logger import get_logger
from prompts import build_prompt
from schemas import AperturaCoqueta
from settings import get_llm

logger = get_logger("graph")


##############################
# ---- Estado del grafo ---- #
##############################
# El State es el "pizarrón" compartido entre nodos. Cada nodo lee de él y
# escribe en él. Usamos TypedDict (lo nativo de LangGraph) para el estado, y
# Pydantic para la salida del modelo (schemas.py).


class State(TypedDict):
    # --- entradas ---
    perfil: str
    modo: Literal["baseline", "role"]
    # --- salidas (las rellena el nodo) ---
    apertura: str
    justificacion: str
    tono: str


####################################
# ---- Nodo: generar_apertura ---- #
####################################
def generar_apertura(state: State) -> dict:
    """Genera la apertura usando el prompt del modo indicado y salida tipada."""
    modo = state.get("modo", "role")
    logger.info(f"Generando apertura en modo='{modo}'")

    # LCEL: encadenamos prompt -> modelo-con-salida-estructurada.
    prompt = build_prompt(modo)
    llm = get_llm(temperature=0.7)  # algo de creatividad para el mensaje
    chain = prompt | llm.with_structured_output(AperturaCoqueta)

    resultado: AperturaCoqueta = chain.invoke({"perfil": state["perfil"]})  # type: ignore[assignment]

    # Un nodo devuelve SOLO las claves que modifica.
    return {
        "apertura": resultado.apertura,
        "justificacion": resultado.justificacion,
        "tono": resultado.tono,
    }


##################################################
# ---- Construcción y compilación del grafo ---- #
##################################################
def build_graph() -> StateGraph:
    workflow = StateGraph(State)
    workflow.add_node("generar_apertura", generar_apertura)
    workflow.add_edge(START, "generar_apertura")
    workflow.add_edge("generar_apertura", END)
    return workflow


# `graph` es el grafo COMPILADO que exporta este módulo. Lo importan tanto
# main.py como langgraph.json (clave para `langgraph dev`).
graph = build_graph().compile()
