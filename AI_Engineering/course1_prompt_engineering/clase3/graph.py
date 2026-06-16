"""
Grafo de la clase 3: Routing (despacho condicional).

Un nodo `router` clasifica la intención y, según el resultado, el grafo manda el
caso a UN especialista distinto:

                      ┌─→ reconciliacion ─┐
    START → router ───┼─→ casual ─────────┼─→ END
                      └─→ romantico ───────┘

La pieza nueva es `add_conditional_edges`: en vez de una arista fija, una función
decide a qué nodo ir leyendo el estado. Así cada problema recibe el trato (y la
temperatura) que le conviene, optimizando calidad y coste.
"""

from __future__ import annotations

from typing import TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph

from logger import get_logger
from prompts import (
    SYSTEM_CASUAL,
    SYSTEM_RECONCILIACION,
    SYSTEM_ROMANTICO,
    SYSTEM_ROUTER,
)
from schemas import Ruta, RutaDecision
from settings import get_llm

logger = get_logger("graph")


##############################
# ---- Estado del grafo ---- #
##############################
class State(TypedDict):
    peticion: str  # entrada
    ruta: Ruta  # decisión del router
    razon_ruta: str  # por qué se eligió esa ruta
    respuesta: str  # salida del especialista


##################################################################
# ---- Nodo router: clasifica y guarda la ruta en el estado ---- #
##################################################################
def router(state: State) -> dict:
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_ROUTER), ("human", "Petición:\n{peticion}")]
    )
    # temperature=0.0: clasificar debe ser estable y reproducible.
    chain = prompt | get_llm(temperature=0.0).with_structured_output(RutaDecision)
    decision: RutaDecision = chain.invoke({"peticion": state["peticion"]})  # type: ignore[assignment]
    logger.info(f"Router → ruta='{decision.ruta}' ({decision.razon})")
    return {"ruta": decision.ruta, "razon_ruta": decision.razon}


###############################################################################
# ---- Función de enrutado: decide el siguiente nodo a partir del estado ---- #
###############################################################################
def elegir_ruta(state: State) -> Ruta:
    """Devuelve el NOMBRE del nodo destino. La usa add_conditional_edges."""
    return state["ruta"]


#############################################################################
# ---- Nodos especialistas (uno por ruta), cada uno con su temperatura ---- #
#############################################################################
def _responder(system: str, peticion: str, *, temperature: float) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{peticion}")]
    )
    chain = prompt | get_llm(temperature=temperature) | StrOutputParser()
    return chain.invoke({"peticion": peticion})


def reconciliacion(state: State) -> dict:
    logger.info("Especialista: reconciliación")
    return {"respuesta": _responder(SYSTEM_RECONCILIACION, state["peticion"], temperature=0.3)}


def casual(state: State) -> dict:
    logger.info("Especialista: casual")
    return {"respuesta": _responder(SYSTEM_CASUAL, state["peticion"], temperature=0.8)}


def romantico(state: State) -> dict:
    logger.info("Especialista: romántico")
    return {"respuesta": _responder(SYSTEM_ROMANTICO, state["peticion"], temperature=0.9)}


##################################################
# ---- Construcción y compilación del grafo ---- #
##################################################
def build_graph() -> StateGraph:
    workflow = StateGraph(State)

    workflow.add_node("router", router)
    workflow.add_node("reconciliacion", reconciliacion)
    workflow.add_node("casual", casual)
    workflow.add_node("romantico", romantico)

    workflow.add_edge(START, "router")

    # Aristas CONDICIONALES: elegir_ruta() devuelve la clave; el dict la mapea
    # al nodo destino. Es el patrón central del routing en LangGraph.
    workflow.add_conditional_edges(
        "router",
        elegir_ruta,
        {
            "reconciliacion": "reconciliacion",
            "casual": "casual",
            "romantico": "romantico",
        },
    )

    workflow.add_edge("reconciliacion", END)
    workflow.add_edge("casual", END)
    workflow.add_edge("romantico", END)

    return workflow


graph = build_graph().compile()
