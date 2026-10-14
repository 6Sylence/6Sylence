import networkx as nx
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from src.config import QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME

class AMEAMemory:
    def __init__(self):
        self.causal_graph = nx.DiGraph()
        self.qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self._init_qdrant()

    def _init_qdrant(self):
        try:
            collections = [c.name for c in self.qdrant.get_collections().collections]
            if COLLECTION_NAME not in collections:
                self.qdrant.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"Aviso: No se pudo conectar a Qdrant (asegúrate de que esté activo si usas memoria vectorial): {e}")

    def add_causal_relation(self, cause: str, effect: str, sector: str):
        if self.causal_graph.has_edge(cause, effect):
            self.causal_graph[cause][effect]["sectors"].add(sector)
        else:
            self.causal_graph.add_edge(cause, effect, sectors={sector})

    def get_graph_insights(self) -> list:
        # Relaciones causa -> efecto con los sectores implicados
        return [
            (cause, effect, sorted(data["sectors"]))
            for cause, effect, data in self.causal_graph.edges(data=True)
        ]
