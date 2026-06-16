"""
Esquemas Pydantic de la clase 1.

Aquí vive el "contrato" de datos: qué le pedimos al modelo que devuelva. Usar
Pydantic + with_structured_output() en lugar de parsear texto a mano nos da:
- Validación automática de tipos y campos obligatorios.
- Autocompletado en el editor.
- Un único sitio donde leer la forma de la salida.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

############################################
# ---- Salida estructurada del modelo ---- #
############################################
class AperturaCoqueta(BaseModel):
    """Lo que el modelo debe devolver: una apertura conversacional y su porqué.

    Las descripciones de cada Field NO son decorativas: viajan al modelo como
    parte del esquema y mejoran la calidad de la salida.
    """

    apertura: str = Field(description="Mensaje breve para romper el hielo (1-2 frases)")
    justificacion: str = Field(
        description="Por qué esta apertura encaja con el perfil de la persona"
    )
    tono: Literal["divertido", "elegante", "directo", "curioso"] = Field(
        description="Tono dominante del mensaje"
    )


########################################################################
# ---- Configuración de la petición (entrada del grafo, validada) ---- #
########################################################################
class PeticionConfig(BaseModel):
    """Parámetros de entrada que controla quien usa el grafo desde la CLI."""

    perfil: str = Field(description="Descripción de la persona y el contexto")
    modo: Literal["baseline", "role"] = Field(
        default="role",
        description="baseline = prompt mínimo; role = prompt con rol/persona",
    )
