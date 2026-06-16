"""
Grafo de la clase 2: Prompt Chaining (cadena de especialistas).

Encadenamos 5 nodos en serie. La salida de cada uno entra al siguiente:

    START → coqueton → poeta → naturalizar → redactor → verificador → END

¿Por qué dividir así? Porque controlar 5 tareas pequeñas y específicas da mucha
más calidad (y es más fácil de depurar) que pedirle todo de golpe al modelo en
un único prompt gigante.

Detalle importante: cada paso usa una TEMPERATURA distinta. Los pasos creativos
(coquetón, poeta) van altos; los de control (naturalizar, verificador) van bajos.
"""

#######################
# ---- libraries ---- #
#######################

from __future__ import annotations

from typing import TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph

from logger import get_logger
from prompts import (
    SYSTEM_COQUETON,
    SYSTEM_NATURALIZAR,
    SYSTEM_POETA,
    SYSTEM_REDACTOR,
    SYSTEM_VERIFICADOR,
)
from schemas import Veredicto
from settings import get_llm

logger = get_logger("graph")


##############################
# ---- Estado del grafo ---- #
##############################
# El estado va acumulando el resultado de cada eslabón. Así, al terminar, el
# alumno puede inspeccionar TODOS los pasos intermedios (trazabilidad).


class State(TypedDict):
    contexto: str  # entrada
    idea: str  # paso 1
    version_poetica: str  # paso 2
    version_natural: str  # paso 3
    mensaje_final: str  # paso 4
    aprobado: bool  # paso 5
    observaciones: str  # paso 5


################################################################
# ---- Helper: un paso de texto (system + human → string) ---- #
################################################################
def _paso_texto(system: str, entrada: str, *, temperature: float) -> str:
    """Ejecuta un eslabón simple de la cadena y devuelve texto.

    Reutilizamos esto en los 4 primeros nodos para no repetir el patrón
    `prompt | llm | parser`.
    """
    prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{entrada}")]
    )
    chain = prompt | get_llm(temperature=temperature) | StrOutputParser()
    return chain.invoke({"entrada": entrada})


##############################################
# ---- Nodos (un especialista por nodo) ---- #
##############################################
def coqueton(state: State) -> dict:
    logger.info("Paso 1/5 — coquetón: idea base")
    idea = _paso_texto(SYSTEM_COQUETON, state["contexto"], temperature=0.8)
    return {"idea": idea}


def poeta(state: State) -> dict:
    logger.info("Paso 2/5 — poeta: versión evocadora")
    version = _paso_texto(SYSTEM_POETA, state["idea"], temperature=0.7)
    return {"version_poetica": version}


def naturalizar(state: State) -> dict:
    logger.info("Paso 3/5 — naturalizar: quitar cursilería")
    version = _paso_texto(SYSTEM_NATURALIZAR, state["version_poetica"], temperature=0.3)
    return {"version_natural": version}


def redactor(state: State) -> dict:
    logger.info("Paso 4/5 — redactor: mensaje final")
    final = _paso_texto(SYSTEM_REDACTOR, state["version_natural"], temperature=0.5)
    return {"mensaje_final": final}


def verificador(state: State) -> dict:
    logger.info("Paso 5/5 — verificador: control de calidad")
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_VERIFICADOR), ("human", "Mensaje a revisar:\n{mensaje}")]
    )
    # Salida estructurada: aquí sí necesitamos un booleano fiable, no texto.
    chain = prompt | get_llm(temperature=0.0).with_structured_output(Veredicto)
    veredicto: Veredicto = chain.invoke({"mensaje": state["mensaje_final"]})  # type: ignore[assignment]
    return {"aprobado": veredicto.aprobado, "observaciones": veredicto.observaciones}


##################################################
# ---- Construcción y compilación del grafo ---- #
##################################################
def build_graph() -> StateGraph:
    workflow = StateGraph(State)

    workflow.add_node("coqueton", coqueton)
    workflow.add_node("poeta", poeta)
    workflow.add_node("naturalizar", naturalizar)
    workflow.add_node("redactor", redactor)
    workflow.add_node("verificador", verificador)

    # Las aristas definen el ORDEN de la cadena.
    workflow.add_edge(START, "coqueton")
    workflow.add_edge("coqueton", "poeta")
    workflow.add_edge("poeta", "naturalizar")
    workflow.add_edge("naturalizar", "redactor")
    workflow.add_edge("redactor", "verificador")
    workflow.add_edge("verificador", END)

    return workflow


graph = build_graph().compile()
