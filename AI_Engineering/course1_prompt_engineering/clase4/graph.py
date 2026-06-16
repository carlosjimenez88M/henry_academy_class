"""
Grafo de la clase 4: Evaluator-Optimizer (el patrón estrella).

Dos roles colaboran en un CICLO:
- generador (optimizer): escribe / reescribe el borrador.
- evaluador (juez): puntúa el borrador con una rúbrica y da feedback.

    START → generador → evaluador → ¿aprobado o sin iteraciones?
                ↑                         │  sí → END
                └─────────── no ──────────┘

El bucle se repite hasta que el promedio supera el `umbral` O se agotan las
`max_iteraciones`. Es el mismo principio que un humano editando: escribir,
recibir crítica, reescribir. La diferencia es que aquí lo medimos y automatizamos.

Conceptos nuevos:
- Aristas condicionales que vuelven a un nodo anterior (un ciclo real).
- Un reducer `operator.add` para acumular el historial de cada iteración.
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph

from logger import get_logger
from prompts import (
    HUMAN_EVALUADOR,
    HUMAN_MEJORA,
    HUMAN_PRIMERA,
    SYSTEM_EVALUADOR,
    SYSTEM_GENERADOR,
)
from schemas import Evaluacion
from settings import get_llm

logger = get_logger("graph")


##############################
# ---- Estado del grafo ---- #
##############################
class State(TypedDict):
    # --- entradas / configuración ---
    contexto: str
    umbral: float
    max_iteraciones: int
    # --- estado del ciclo ---
    borrador: str
    feedback: str
    puntaje: float
    iteracion: int
    aprobado: bool
    # `historial` se ACUMULA en cada vuelta gracias al reducer operator.add.
    # Sin el reducer, cada nodo SOBRESCRIBIRÍA la lista en vez de añadir.
    historial: Annotated[list[str], operator.add]


########################################
# ---- Nodo generador (optimizer) ---- #
########################################
def generador(state: State) -> dict:
    iteracion = state.get("iteracion", 0) + 1
    feedback = state.get("feedback", "")

    # Si ya hay feedback, MEJORAMOS; si no, generamos la primera versión.
    if feedback:
        logger.info(f"Generador — iteración {iteracion}: mejorando con feedback")
        human = HUMAN_MEJORA
        variables = {
            "contexto": state["contexto"],
            "borrador": state["borrador"],
            "feedback": feedback,
        }
    else:
        logger.info(f"Generador — iteración {iteracion}: primera versión")
        human = HUMAN_PRIMERA
        variables = {"contexto": state["contexto"]}

    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM_GENERADOR), ("human", human)])
    chain = prompt | get_llm(temperature=0.7) | StrOutputParser()
    borrador = chain.invoke(variables)

    return {"borrador": borrador, "iteracion": iteracion}


###################################
# ---- Nodo evaluador (juez) ---- #
###################################
def evaluador(state: State) -> dict:
    logger.info("Evaluador — puntuando el borrador")
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_EVALUADOR), ("human", HUMAN_EVALUADOR)]
    )
    # temperature=0.0: un juez debe ser consistente.
    chain = prompt | get_llm(temperature=0.0).with_structured_output(Evaluacion)
    evaluacion: Evaluacion = chain.invoke(  # type: ignore[assignment]
        {"contexto": state["contexto"], "borrador": state["borrador"]}
    )

    promedio = evaluacion.promedio
    aprobado = promedio >= state["umbral"]
    logger.info(f"Puntaje promedio: {promedio} (umbral {state['umbral']}) → aprobado={aprobado}")

    registro = (
        f"Iter {state['iteracion']}: promedio={promedio} "
        f"(pers={evaluacion.personalizacion}, nat={evaluacion.naturalidad}, "
        f"resp={evaluacion.respeto}, acc={evaluacion.accionable}) — {evaluacion.feedback}"
    )

    return {
        "puntaje": promedio,
        "feedback": evaluacion.feedback,
        "aprobado": aprobado,
        "historial": [registro],  # el reducer lo añade al historial existente
    }


##############################################################
# ---- Decisión del ciclo: ¿seguir iterando o terminar? ---- #
##############################################################
def decidir(state: State) -> str:
    """Cierra el ciclo si el borrador aprueba o si agotamos las iteraciones.

    Devuelve el nombre del siguiente nodo: "generador" para otra vuelta, o END
    (la constante "__end__") para terminar.
    """
    if state["aprobado"]:
        logger.info("Aprobado: terminamos.")
        return END
    if state["iteracion"] >= state["max_iteraciones"]:
        logger.info("Máximo de iteraciones alcanzado: terminamos.")
        return END
    logger.info("No aprobado: volvemos al generador.")
    return "generador"


##################################################
# ---- Construcción y compilación del grafo ---- #
##################################################
def build_graph() -> StateGraph:
    workflow = StateGraph(State)

    workflow.add_node("generador", generador)
    workflow.add_node("evaluador", evaluador)

    workflow.add_edge(START, "generador")
    workflow.add_edge("generador", "evaluador")

    # Arista condicional que puede VOLVER a 'generador' → esto crea el ciclo.
    workflow.add_conditional_edges(
        "evaluador",
        decidir,
        {"generador": "generador", END: END},
    )

    return workflow


graph = build_graph().compile()
