import feedparser
from typing import List, Dict

class DataIngestionEngine:
    def __init__(self, rss_urls: List[str]):
        self.rss_urls = rss_urls

    def fetch_all_feeds(self) -> List[Dict[str, str]]:
        collected_data = []
        for url in self.rss_urls:
            try:
                parsed = feedparser.parse(url)
                # feedparser no lanza excepciones ante errores HTTP/XML: los marca con 'bozo'
                if parsed.bozo and not parsed.entries:
                    print(f"Aviso: feed {url} sin entradas válidas ({parsed.get('bozo_exception')})")
                    continue
                for entry in parsed.entries[:10]:
                    collected_data.append({
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", "")
                    })
            except Exception as e:
                print(f"Error al conectar con feed {url}: {e}")
        return collected_data
