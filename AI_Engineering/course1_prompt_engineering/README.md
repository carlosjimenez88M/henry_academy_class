# Curso 1 — Prompt Engineering con LangChain & LangGraph

Cinco clases para dar tus primeros pasos en **AI Engineering**. Empezamos por un
solo prompt y terminamos con un agente que usa herramientas y decide por sí mismo.
Cada clase es un proyecto independiente, escrito de forma modular (con Pydantic y
*typing*), que se ejecuta tanto desde la terminal como de forma visual con
`langgraph dev`.

Usamos un mismo hilo conductor en todas las clases —un *coach* que ayuda a romper
el hielo en una conversación— para que solo cambie la **técnica**, no el dominio.

## Roadmap

| Clase | Tema | Patrón LangGraph | Concepto clave |
| ----- | ---- | ---------------- | -------------- |
| [`clase1`](./clase1) | Fundamentos: zero-shot vs rol, salida estructurada, LCEL | Grafo lineal (1 nodo) | `StateGraph`, `with_structured_output` |
| [`clase2`](./clase2) | Prompt Chaining | Nodos secuenciales | La salida de un paso alimenta el siguiente |
| [`clase3`](./clase3) | Routing | `add_conditional_edges` | Despachar cada caso a un especialista |
| [`clase4`](./clase4) | **Evaluator-Optimizer** | Ciclo + reducer | Mejorar con feedback hasta un umbral medible |
| [`clase5`](./clase5) | ReAct (agente con herramientas) | `ToolNode` + `tools_condition` | El modelo decide qué herramienta usar y cuándo parar |

La dificultad sube clase a clase: cada una añade exactamente una idea nueva sobre
la anterior. La clase 5 incluye además un **reto final** (`clase5/RETO.md`) que
integra todo el curso en un proyecto de nivel producción.

**Bonus** — [`comparativa_llms`](./comparativa_llms): corre el mismo flujo con
**OpenAI y Gemini en paralelo** y un **LLM-juez** devuelve, en formato
estructurado, cuál respuesta es mejor y por qué. Enseña abstracción de proveedor
y *LLM-as-judge* para A/B testing. Requiere `GOOGLE_API_KEY` además de la de OpenAI.

## Requisitos

- [uv](https://docs.astral.sh/uv/) (gestor de entornos y dependencias).
- Una `OPENAI_API_KEY`.

Pon tu clave en `course1_prompt_engineering/.env` (este nivel). Las cuatro clases
la comparten automáticamente vía `langgraph.json` (`"env": "../.env"`), así no la
duplicas. Mira `clase1/.env.example` para el formato.

```
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...        # solo para el módulo bonus comparativa_llms (Gemini)
```

## Cómo trabajar cada clase

Cada carpeta es autónoma. El flujo siempre es el mismo:

```bash
cd clase1          # o clase2, clase3, clase4
uv sync            # crea el entorno e instala dependencias

# Opción A — terminal
uv run python main.py --help

# Opción B — LangGraph Studio (visual e interactivo)
uv run langgraph dev
```

`langgraph dev` levanta un servidor local y abre LangGraph Studio, donde ves el
grafo dibujado y puedes invocarlo editando el estado de entrada a mano. Es la
mejor forma de *entender* qué hace cada nodo.

## Estructura de cada clase

Mantenemos cada responsabilidad en su archivo (separación que se usa en producción):

| Archivo        | Responsabilidad                                           |
| -------------- | --------------------------------------------------------- |
| `logger.py`    | Logger con colores reutilizable.                          |
| `settings.py`  | Carga del `.env` y fábrica del LLM (perezosa + cacheada).  |
| `schemas.py`   | Contratos de datos con Pydantic.                          |
| `prompts.py`   | Los prompts, separados de la lógica.                      |
| `graph.py`     | El grafo de LangGraph. Exporta `graph` (lo carga `langgraph dev`). |
| `main.py`      | CLI para ejecutar desde la terminal.                      |
| `langgraph.json` | Le dice a `langgraph dev` qué grafo cargar.             |
| `pyrightconfig.json` | Hace que la carpeta sea raíz de imports (editor limpio). |

> La `clase5` añade además `tools.py` (las herramientas del agente) y `RETO.md`
> (el desafío final del curso).

El repositorio incluye un `.gitignore` que protege tu `.env` (la API key) y
excluye entornos virtuales y cachés. Nunca subas tu `.env`.

## Idea que se repite en todo el curso

> Buen prompting no es agregar complejidad: es usar la **mínima complejidad que
> garantiza una calidad medible**. Por eso cada clase introduce una sola técnica
> nueva y, en la clase 4, aprendemos a *medir* esa calidad.
