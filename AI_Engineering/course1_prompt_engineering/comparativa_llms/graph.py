"""
Grafo de comparación: OpenAI vs Gemini, juzgado por un tercer LLM.

Generamos la misma apertura con DOS proveedores en paralelo y luego un LLM-juez
imparcial decide cuál es mejor:

                 ┌─→ generar_openai ─┐
    START ───────┤                   ├─→ juez → END
                 └─→ generar_gemini ─┘

Conceptos:
- Fan-out / fan-in: dos nodos sin dependencia entre sí corren en paralelo; el
  nodo `juez` espera a que AMBOS terminen (tiene una arista desde cada uno).
- Abstracción de proveedor: ambos nodos usan la MISMA función con distinto
  `provider`; el código no cambia, solo el modelo de detrás.
- LLM-as-judge: el resultado final lo decide y lo devuelve un LLM (estructurado).
"""

from __future__ import annotations

from typing import TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph

from logger import get_logger
from prompts import HUMAN_JUEZ, SYSTEM_GENERADOR, SYSTEM_JUEZ
from schemas import Veredicto
from settings import Proveedor, get_llm

logger = get_logger("graph")


##############################
# ---- Estado del grafo ---- #
##############################
class State(TypedDict):
    perfil: str  # entrada
    salida_openai: str  # apertura generada por OpenAI
    salida_gemini: str  # apertura generada por Gemini
    ganador: str  # veredicto del juez
    puntaje_openai: int
    puntaje_gemini: int
    justificacion: str


#################################################################
# ---- Generación con un proveedor concreto (reutilizable) ---- #
#################################################################
def _generar(perfil: str, provider: Proveedor) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_GENERADOR), ("human", "Perfil:\n{perfil}")]
    )
    chain = prompt | get_llm(provider=provider, temperature=0.7) | StrOutputParser()
    return chain.invoke({"perfil": perfil})


def generar_openai(state: State) -> dict:
    logger.info("Generando con OpenAI")
    return {"salida_openai": _generar(state["perfil"], "openai")}


def generar_gemini(state: State) -> dict:
    logger.info("Generando con Gemini")
    return {"salida_gemini": _generar(state["perfil"], "gemini")}


#####################################################################
# ---- Nodo juez: compara y devuelve el veredicto estructurado ---- #
#####################################################################
def juez(state: State) -> dict:
    logger.info("Juez — comparando ambas aperturas")
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_JUEZ), ("human", HUMAN_JUEZ)]
    )
    # El juez usa OpenAI (temperatura 0 para imparcialidad y consistencia).
    chain = prompt | get_llm(provider="openai", temperature=0.0).with_structured_output(Veredicto)
    veredicto: Veredicto = chain.invoke(  # type: ignore[assignment]
        {
            "perfil": state["perfil"],
            "salida_openai": state["salida_openai"],
            "salida_gemini": state["salida_gemini"],
        }
    )
    logger.info(f"Ganador: {veredicto.ganador}")
    return {
        "ganador": veredicto.ganador,
        "puntaje_openai": veredicto.puntaje_openai,
        "puntaje_gemini": veredicto.puntaje_gemini,
        "justificacion": veredicto.justificacion,
    }


##################################################
# ---- Construcción y compilación del grafo ---- #
##################################################
def build_graph() -> StateGraph:
    workflow = StateGraph(State)

    workflow.add_node("generar_openai", generar_openai)
    workflow.add_node("generar_gemini", generar_gemini)
    workflow.add_node("juez", juez)

    # Fan-out: ambos generadores arrancan a la vez desde START.
    workflow.add_edge(START, "generar_openai")
    workflow.add_edge(START, "generar_gemini")

    # Fan-in: el juez espera a los dos antes de ejecutarse.
    workflow.add_edge("generar_openai", "juez")
    workflow.add_edge("generar_gemini", "juez")

    workflow.add_edge("juez", END)
    return workflow


graph = build_graph().compile()
