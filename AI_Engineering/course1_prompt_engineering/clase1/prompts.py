"""
Prompts de la clase 1.

Idea central de la clase: comparar dos formas de pedirle lo mismo al modelo.
- baseline: instrucción mínima, sin identidad ni restricciones (zero-shot puro).
- role:     define ROL + VALORES + RESTRICCIONES (prompting basado en rol).

Mantener los prompts aquí (y no incrustados en el grafo) deja el grafo limpio y
permite iterar el texto del prompt sin tocar la lógica.
"""
#######################
# ---- libraries ---- #
#######################
from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

####################################################################
# ---- System prompts: las dos variantes que vamos a comparar ---- #
####################################################################
SYSTEM_BASELINE = (
    "Sugiere un mensaje para iniciar una conversación con la persona descrita."
)

SYSTEM_ROLE = """\
Eres un coach conversacional elegante, respetuoso y práctico.

VALORES:
- Naturalidad por encima de la cursilería.
- Respeto: nada de presión, insistencia ni lenguaje explícito.

TAREA:
- A partir del perfil, propones UNA apertura breve (1-2 frases) para romper
  el hielo, que conecte con algo concreto de esa persona e invite a responder.\
"""


##############################################
# ---- Fábrica del prompt según el modo ---- #
##############################################
def build_prompt(modo: str) -> ChatPromptTemplate:
    """Construye el ChatPromptTemplate según el modo elegido.

    El mensaje 'human' es idéntico en ambos modos a propósito: lo único que
    cambia es el 'system'. Así el alumno ve el efecto aislado del rol.
    """
    system = SYSTEM_ROLE if modo == "role" else SYSTEM_BASELINE
    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Perfil de la persona:\n{perfil}"),
        ]
    )
