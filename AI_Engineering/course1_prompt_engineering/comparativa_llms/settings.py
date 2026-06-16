"""
Configuración multi-proveedor: una sola fábrica que devuelve el LLM de OpenAI
o de Gemini según se pida.

Idea clave de AI Engineering: programar contra una ABSTRACCIÓN, no contra un
proveedor concreto. LangChain nos da una interfaz común (`.invoke`,
`.with_structured_output`, ...), así que el resto del código no necesita saber
qué proveedor hay detrás. Cambiar de modelo es cambiar un string.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel

from logger import get_logger

logger = get_logger("settings")

Proveedor = Literal["openai", "gemini"]


##################################################
# ---- Carga de variables de entorno (.env) ---- #
##################################################
_THIS_FILE = Path(__file__).resolve()
_ENV_CANDIDATES = (
    _THIS_FILE.parent / ".env",  # comparativa_llms/.env
    _THIS_FILE.parent.parent / ".env",  # course1_prompt_engineering/.env
)


def _load_env() -> None:
    for candidate in _ENV_CANDIDATES:
        if candidate.exists():
            load_dotenv(candidate, override=False)
            logger.info(f"Variables de entorno cargadas desde {candidate}")
            return
    logger.warning("No se encontró ningún .env; se usará el entorno del sistema")


_load_env()


###################################################
# ---- Modelos por defecto de cada proveedor ---- #
###################################################
_MODELOS_DEFECTO: dict[Proveedor, str] = {
    "openai": "gpt-4o-mini",
    # gemini-2.5-flash: comprobado con cuota disponible. Nota: en free tier,
    # gemini-2.0-flash devuelve quota 0; 2.5-flash sí responde.
    "gemini": "gemini-2.5-flash",
}

# Nombres de variable aceptados por proveedor (probamos en orden). Gemini admite
# tanto GEMINI_API_KEY como GOOGLE_API_KEY según cómo lo tengas en el .env.
_CLAVES_ENV: dict[Proveedor, tuple[str, ...]] = {
    "openai": ("OPENAI_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
}


def _leer_clave(provider: Proveedor) -> str | None:
    """Devuelve la primera API key encontrada para el proveedor, o None."""
    for nombre in _CLAVES_ENV[provider]:
        valor = os.getenv(nombre)
        if valor:
            return valor
    return None


###########################################################
# ---- Fábrica multi-proveedor (perezosa + cacheada) ---- #
###########################################################
@lru_cache(maxsize=None)
def get_llm(
    provider: Proveedor = "openai",
    temperature: float = 0.0,
    model: str | None = None,
) -> BaseChatModel:
    """Devuelve el chat model del proveedor pedido.

    Importamos cada SDK *dentro* de su rama para no exigir tener instalados
    ambos si solo usas uno. Si falta la API key, avisamos con un mensaje claro.
    """
    nombre_modelo = model or _MODELOS_DEFECTO[provider]
    clave = _leer_clave(provider)
    if not clave:
        esperadas = " o ".join(_CLAVES_ENV[provider])
        logger.warning(f"No hay API key ({esperadas}): el proveedor '{provider}' fallará al invocar")

    logger.info(f"Creando LLM provider='{provider}' model='{nombre_modelo}' temp={temperature}")

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        # ChatOpenAI lee OPENAI_API_KEY del entorno automáticamente.
        return ChatOpenAI(model=nombre_modelo, temperature=temperature)

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        # Pasamos la clave explícita: así funciona venga de GEMINI_API_KEY o
        # de GOOGLE_API_KEY, sin depender del nombre que espere la librería.
        return ChatGoogleGenerativeAI(
            model=nombre_modelo, temperature=temperature, google_api_key=clave
        )

    raise ValueError(f"Proveedor no soportado: {provider}")
