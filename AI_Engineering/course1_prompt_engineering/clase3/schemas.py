"""
Esquemas Pydantic de la clase 3 (Routing).

El corazón del routing es la decisión del router. La pedimos como salida
estructurada para que la "ruta" sea un valor controlado (un Literal), no texto
libre que luego tengamos que adivinar.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# Las rutas posibles, definidas UNA vez y reutilizadas en todo el grafo.
Ruta = Literal["reconciliacion", "casual", "romantico"]


##########################################
# ---- Entrada del grafo (validada) ---- #
##########################################
class RoutingConfig(BaseModel):
    peticion: str = Field(description="Lo que la persona quiere lograr o expresar")


#######################################################
# ---- Decisión del router (salida estructurada) ---- #
#######################################################
class RutaDecision(BaseModel):
    """Clasificación de la intención en una de las rutas disponibles."""

    ruta: Ruta = Field(description="La ruta que mejor encaja con la intención")
    razon: str = Field(description="Justificación breve de por qué esa ruta")
