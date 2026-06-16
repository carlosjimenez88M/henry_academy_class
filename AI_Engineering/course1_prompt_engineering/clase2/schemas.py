"""
Esquemas Pydantic de la clase 2 (Prompt Chaining).

En una cadena, casi todos los pasos devuelven texto libre (la salida de un
paso es la entrada del siguiente). Pero el ÚLTIMO paso —la verificación— sí
necesita una salida estructurada para poder decidir programáticamente.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

##########################################
# ---- Entrada del grafo (validada) ---- #
##########################################
class ChainConfig(BaseModel):
    contexto: str = Field(
        description="Perfil de la persona y situación para la que escribimos"
    )


###############################################################################
# ---- Salida estructurada del verificador (último eslabón de la cadena) ---- #
###############################################################################
class Veredicto(BaseModel):
    """Resultado del control de calidad final del mensaje."""

    aprobado: bool = Field(
        description="True si el mensaje es respetuoso, natural y enviable"
    )
    observaciones: str = Field(
        description="Qué falla o, si está aprobado, por qué funciona"
    )
