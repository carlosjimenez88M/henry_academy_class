"""
Esquemas Pydantic de la clase 4 (Evaluator-Optimizer).

El evaluador es un "LLM como juez" (LLM-as-judge): puntúa el borrador según una
rúbrica de 4 criterios ortogonales. Pedir esa puntuación como objeto Pydantic
(en vez de texto) es lo que nos permite decidir en código si seguir iterando.

Mejoramos la rúbrica del material original (que medía con reglas/regex) usando
al modelo como juez con criterios explícitos y rangos validados (0-10).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

##########################################
# ---- Entrada del grafo (validada) ---- #
##########################################
class EvalConfig(BaseModel):
    contexto: str = Field(description="Perfil de la persona y situación")
    umbral: float = Field(
        default=8.0,
        ge=0.0,
        le=10.0,
        description="Puntaje promedio mínimo para aprobar y detener el ciclo",
    )
    max_iteraciones: int = Field(
        default=3,
        ge=1,
        le=6,
        description="Tope de vueltas del ciclo (evita bucles infinitos y coste)",
    )


#########################################################
# ---- Rúbrica del evaluador (salida estructurada) ---- #
#########################################################
class Evaluacion(BaseModel):
    """Puntuación del borrador en 4 criterios independientes (0-10 cada uno).

    Las descripciones viajan al modelo y definen QUÉ mide cada criterio, así el
    juez es consistente entre iteraciones.
    """

    personalizacion: int = Field(
        ge=0, le=10, description="¿Usa señales concretas del perfil?"
    )
    naturalidad: int = Field(
        ge=0, le=10, description="¿Suena humano y conversacional, sin cursilería?"
    )
    respeto: int = Field(
        ge=0, le=10, description="¿Sin presión, insistencia ni lenguaje inapropiado?"
    )
    accionable: int = Field(
        ge=0, le=10, description="¿Invita a responder con un gancho o pregunta?"
    )
    feedback: str = Field(
        description="Crítica concreta y accionable para mejorar el borrador"
    )

    @property
    def promedio(self) -> float:
        """Promedio de los 4 criterios. Lo calculamos en código (fiable),
        no se lo pedimos al modelo."""
        criterios = (
            self.personalizacion,
            self.naturalidad,
            self.respeto,
            self.accionable,
        )
        return round(sum(criterios) / len(criterios), 2)
