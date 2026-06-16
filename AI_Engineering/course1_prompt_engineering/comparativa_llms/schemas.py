"""
Esquemas Pydantic del módulo de comparación.

El veredicto del juez es salida estructurada: así "quién gana" es un valor
controlado y podemos usarlo en código (gráficas, métricas, tests).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

################################
# ---- Entrada (validada) ---- #
################################
class ComparacionConfig(BaseModel):
    perfil: str = Field(description="Descripción de la persona y la situación")


####################################
# ---- Veredicto del LLM-juez ---- #
####################################
class Veredicto(BaseModel):
    """Comparación de las dos aperturas hecha por un LLM imparcial."""

    ganador: Literal["openai", "gemini", "empate"] = Field(
        description="Qué respuesta es mejor según los criterios"
    )
    puntaje_openai: int = Field(ge=0, le=10, description="Nota de la respuesta de OpenAI")
    puntaje_gemini: int = Field(ge=0, le=10, description="Nota de la respuesta de Gemini")
    justificacion: str = Field(description="Por qué gana esa (o por qué hay empate)")
