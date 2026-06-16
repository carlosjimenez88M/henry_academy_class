"""
Grafo de la clase 5: ReAct (Reasoning + Acting).

ReAct = el modelo alterna entre RAZONAR y ACTUAR (llamar herramientas), usando
lo que observa para decidir el siguiente paso, hasta que tiene la respuesta.

    START → agente → ¿pidió usar una tool?
              ↑                │  no → END
              │                │  sí
              └──── tools ◀────┘

Piezas nuevas:
- `bind_tools`: le damos al modelo el "catálogo" de herramientas disponibles.
- `ToolNode`: nodo prefabricado que EJECUTA las tools que el modelo pidió.
- `tools_condition`: función prefabricada que mira el último mensaje y decide si
  hay que ir a ejecutar tools o si ya podemos terminar.

El bucle agente → tools → agente es el corazón del patrón ReAct.
"""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from logger import get_logger
from prompts import SYSTEM_AGENTE
from settings import get_llm
from tools import TOOLS

logger = get_logger("graph")


##############################
# ---- Estado del grafo ---- #
##############################
# Reutilizamos MessagesState (de LangGraph): trae un campo `messages` con el
# reducer add_messages ya configurado, que ACUMULA la conversación (humano,
# IA, llamadas a tools y sus resultados). Es lo estándar para agentes.


class State(MessagesState):
    pass


###############################################
# ---- Modelo con herramientas enlazadas ---- #
###############################################
# temperature baja: usar herramientas con fiabilidad pesa más que la creatividad.


def _llm_con_tools():
    return get_llm(temperature=0.2).bind_tools(TOOLS)


##########################################################################
# ---- Nodo agente: razona y, si hace falta, pide llamar a una tool ---- #
##########################################################################
def agente(state: State) -> dict:
    logger.info("Agente — razonando sobre el siguiente paso")
    # Anteponemos el system prompt a la conversación acumulada.
    mensajes = [SystemMessage(content=SYSTEM_AGENTE)] + state["messages"]
    respuesta = _llm_con_tools().invoke(mensajes)
    # add_messages añade la respuesta (que puede incluir tool_calls) al estado.
    return {"messages": [respuesta]}


##################################################
# ---- Construcción y compilación del grafo ---- #
##################################################
def build_graph() -> StateGraph:
    workflow = StateGraph(State)

    workflow.add_node("agente", agente)
    workflow.add_node("tools", ToolNode(TOOLS))  # ejecuta las tools pedidas

    workflow.add_edge(START, "agente")

    # tools_condition devuelve "tools" si el último mensaje pidió herramientas,
    # o END si el agente ya dio su respuesta final.
    workflow.add_conditional_edges("agente", tools_condition)

    # Tras ejecutar las tools, volvemos al agente con las observaciones. Ese
    # retorno es lo que crea el bucle ReAct.
    workflow.add_edge("tools", "agente")

    return workflow


graph = build_graph().compile()
