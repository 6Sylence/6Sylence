# AMEA — Agente Macroeconómico Anticipatorio

Prototipo de agente autónomo que se ejecuta en local:

1. **Ingesta** (`src/ingestion.py`): lee feeds RSS (arXiv q-fin, Reuters).
2. **Razonamiento** (`src/brain.py`): un LLM local vía Ollama extrae causa, efecto directo, efecto de segundo orden, sectores y una puntuación de confianza en JSON.
3. **Memoria** (`src/memory.py`): grafo causal dirigido (NetworkX) y una colección vectorial en Qdrant (preparada, todavía no se escriben embeddings).
4. **Simulación** (`src/simulation.py`): simulación Monte Carlo sobre la confianza; si supera el umbral (0.70) se emite una alerta.
5. **Bucle** (`src/main.py`): repite el ciclo cada hora.

## Requisitos

- Python 3.10–3.12 (`numpy==1.26.3` y `pydantic==2.6.0` no publican wheels para 3.13).
- [Ollama](https://ollama.com) con el modelo descargado: `ollama pull qwen2.5:14b`
- Qdrant (opcional; si no está activo el agente sigue funcionando y solo avisa):
  `docker run -p 6333:6333 qdrant/qdrant`

## Instalación y ejecución

```bash
cd amea_agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

Ejecuta siempre desde `amea_agent/` con `python -m src.main`, porque los módulos importan `src.*`.

## Configuración (`.env`)

| Variable          | Por defecto              |
|-------------------|--------------------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `OLLAMA_MODEL`    | `qwen2.5:14b`            |
| `QDRANT_HOST`     | `localhost`              |
| `QDRANT_PORT`     | `6333`                   |

## Limitaciones conocidas

- El feed de Reuters (`/business/finance/rss`) está descontinuado; el agente lo omite con un aviso. Sustitúyelo en `FEEDS` (`src/main.py`) por otro feed que funcione.
- La puntuación de confianza la genera el LLM. La "simulación" añade ruido gaussiano alrededor de esa cifra, así que no es una señal de trading validada. Esto es un prototipo de investigación, no asesoramiento financiero.
