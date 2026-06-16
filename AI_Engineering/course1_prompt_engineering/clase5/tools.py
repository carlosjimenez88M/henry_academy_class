"""
Herramientas (tools) de la clase 5 (ReAct).

Una herramienta es una función que el modelo puede DECIDIR llamar. La clave es
que cada tool tiene un contrato claro: tipos de entrada/salida y un docstring que
el modelo lee para saber cuándo y cómo usarla.

Diseñamos tools DETERMINISTAS (sin LLM dentro): hacen cosas que el modelo no
debería inventar (validar reglas, consultar un catálogo). Esa es justo la gracia
de ReAct: el modelo razona, pero delega los hechos en herramientas fiables.
"""

from __future__ import annotations

from langchain_core.tools import tool

###############################################################################
# ---- Datos de apoyo (en un proyecto real vendrían de una BD o una API) ---- #
###############################################################################
# Catálogo mínimo: interés -> plan concreto sugerido.
_CATALOGO_PLANES: dict[str, str] = {
    "cine": "una sesión en un cine de autor seguida de un café para comentarla",
    "musica": "un concierto pequeño en un bar de jazz o una tienda de vinilos",
    "deporte": "una caminata por un parque con buenas vistas",
    "lectura": "una visita a una librería de viejo y luego un té",
    "cocina": "un mercado gastronómico para probar cosas y charlar",
}

# Palabras que delatan presión o falta de respeto (guardrail).
_PALABRAS_PROHIBIDAS = ("insiste", "presiona", "obliga", "explícito", "ya mismo")


########################################
# ---- Tool 1: analizar el perfil ---- #
########################################
@tool
def analizar_perfil(perfil: str) -> str:
    """Extrae las señales clave de un perfil para personalizar el mensaje.

    Args:
        perfil: Texto libre que describe a la persona y la situación.

    Returns:
        Un resumen con los intereses detectados y un tono sugerido.
    """
    texto = perfil.lower()
    intereses = [tema for tema in _CATALOGO_PLANES if tema in texto]
    if not intereses:
        return "No se detectaron intereses claros; usa un tono curioso y neutral."
    return f"Intereses detectados: {', '.join(intereses)}. Tono sugerido: cercano y curioso."


############################################################
# ---- Tool 2: sugerir un plan a partir de un interés ---- #
############################################################
@tool
def sugerir_plan(interes: str) -> str:
    """Propone un plan concreto para un interés dado.

    Args:
        interes: Una de las claves conocidas (cine, musica, deporte, lectura, cocina).

    Returns:
        La descripción de un plan, o un aviso si el interés no está en el catálogo.
    """
    plan = _CATALOGO_PLANES.get(interes.strip().lower())
    if plan is None:
        disponibles = ", ".join(_CATALOGO_PLANES)
        return f"No tengo un plan para '{interes}'. Intereses disponibles: {disponibles}."
    return f"Plan sugerido: {plan}."


#############################################################################
# ---- Tool 3: auditar el respeto del mensaje (guardrail determinista) ---- #
#############################################################################
@tool
def auditar_respeto(mensaje: str) -> str:
    """Valida que un mensaje sea respetuoso y sin presión antes de enviarlo.

    Args:
        mensaje: El texto del mensaje final a revisar.

    Returns:
        "APROBADO" si es seguro, o "RECHAZADO: ..." con el motivo concreto.
    """
    texto = mensaje.lower()
    encontradas = [p for p in _PALABRAS_PROHIBIDAS if p in texto]
    if encontradas:
        return f"RECHAZADO: contiene lenguaje de presión ({', '.join(encontradas)})."
    if len(mensaje.split()) > 60:
        return "RECHAZADO: demasiado largo; un primer mensaje debe ser breve."
    return "APROBADO"


# Lista que exportamos al grafo. Añadir una tool nueva es solo: definirla aquí
# y agregarla a esta lista.
TOOLS = [analizar_perfil, sugerir_plan, auditar_respeto]
