import json
import ollama
from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL

class EconomicBrain:
    def __init__(self):
        self.client = ollama.Client(host=OLLAMA_BASE_URL)
        self.model = OLLAMA_MODEL

    def analyze_event_causality(self, title: str, summary: str) -> dict:
        prompt = f"""
        Analiza la siguiente noticia económica o tecnológica desde una perspectiva macroeconómica y de arbitraje sistémico.
        Extrae las relaciones de causa y efecto en formato JSON estricto con las siguientes claves:
        - "primary_event": Resumen corto del evento.
        - "affected_sectors": Lista de sectores económicos afectados (ej. semiconductores, energía, logística).
        - "cause": Qué provocó este evento.
        - "direct_effect": Efecto inmediato.
        - "second_order_effect": Efecto secundario u oportunidad oculta a mediano plazo.
        - "confidence_score": Un número flotante del 0.0 al 1.0 que indique el impacto potencial.

        Noticia:
        Título: {title}
        Resumen: {summary}

        Devuelve ÚNICAMENTE el objeto JSON válido, sin texto adicional antes ni después.
        """

        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1}
            )
        except Exception as e:
            print(f"Error contactando Ollama en {OLLAMA_BASE_URL} (modelo {self.model}): {e}")
            return {}

        content = response['message']['content']
        try:
            clean_content = content.replace("```json", "").replace("```", "").strip()
            # Tolera texto extra alrededor del objeto JSON
            start, end = clean_content.find("{"), clean_content.rfind("}")
            if start != -1 and end != -1:
                clean_content = clean_content[start:end + 1]
            data = json.loads(clean_content)
        except Exception as e:
            print(f"Error parseando JSON del LLM: {e} | Respuesta cruda: {content}")
            return {}

        # Normalización de tipos para el resto del pipeline
        try:
            data["confidence_score"] = max(0.0, min(1.0, float(data.get("confidence_score", 0.0))))
        except (TypeError, ValueError):
            data["confidence_score"] = 0.0
        sectors = data.get("affected_sectors")
        if isinstance(sectors, str):
            sectors = [sectors]
        data["affected_sectors"] = sectors or ["General"]
        return data
