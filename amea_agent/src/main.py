import time
from src.ingestion import DataIngestionEngine
from src.brain import EconomicBrain
from src.memory import AMEAMemory
from src.simulation import ArbitrageSimulator

FEEDS = [
    "https://export.arxiv.org/rss/q-fin",
    "https://www.reuters.com/business/finance/rss"
]

def run_agent_loop():
    print("Iniciando Agente Macroeconómico Anticipatorio (AMEA)...")
    ingestion = DataIngestionEngine(FEEDS)
    brain = EconomicBrain()
    memory = AMEAMemory()
    simulator = ArbitrageSimulator(confidence_threshold=0.70)

    while True:
        print("\n--- Ejecutando ciclo de escaneo macroeconómico ---")
        raw_items = ingestion.fetch_all_feeds()

        for item in raw_items[:3]:
            print(f"Procesando: {item['title']}")
            analysis = brain.analyze_event_causality(item['title'], item['summary'])

            if analysis and "cause" in analysis and "direct_effect" in analysis:
                for sector in analysis.get("affected_sectors", ["General"]):
                    memory.add_causal_relation(
                        cause=analysis["cause"],
                        effect=analysis["direct_effect"],
                        sector=sector
                    )

                is_opportunity = simulator.evaluate_opportunity(analysis)
                if is_opportunity:
                    print(f"Acción recomendada: Posicionarse en efectos de segundo orden -> {analysis.get('second_order_effect')}")

        print(f"Relaciones causales en memoria: {len(memory.get_graph_insights())}")
        print("Ciclo completado. Durmiendo por 1 hora...")
        time.sleep(3600)

if __name__ == "__main__":
    run_agent_loop()
