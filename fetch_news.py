import feedparser
import requests
import logging
from typing import List, Dict

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ThreatIntelNewsFetcher:
    """
    Classe responsável por buscar as últimas notícias de fontes de Threat Intelligence
    via RSS feeds (OSINT).
    """
    def __init__(self, timeout: int = 15):
         # O timeout é essencial para evitar o travamento se o feed estiver fora do ar
        self.timeout = timeout
        self.feeds = {
            "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
            "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
            "Dark Reading": "https://www.darkreading.com/rss.xml"
        }

    def fetch_latest_news(self, limit_per_feed: int = 10) -> List[Dict]:
        """
        Extrai as últimas notícias de cada source configurado no feed.
        
        Retorna:
            Uma lista de dicionários contendo os detalhes das notícias extraídas.
        """
        extracted_data = []

        for source_name, url in self.feeds.items():
            logging.info(f"Coletando feed: {source_name}")
            
            try:
                # Utilizando a biblioteca 'requests' para injetar um controle robusto 
                # de timeout antes de passar o payload ao feedparser
                # Adicionamos headers para simular um navegador e evitar ser bloqueado
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) OSINT/ThreatIntel Bot'}
                response = requests.get(url, timeout=self.timeout, headers=headers)
                response.raise_for_status()

                # Parseando o conteúdo baixado utilizando feedparser
                feed = feedparser.parse(response.content)

                # Avaliando casos em que o parse ocorreu com algum erro de estrutura do XML
                if feed.bozo and hasattr(feed, 'bozo_exception'):
                     logging.warning(f"Alerta de formatação do feed {source_name}: {feed.bozo_exception}")

                count = 0
                for entry in feed.entries:
                    if count >= limit_per_feed:
                        break
                    
                    # Extração segura e estruturada das entidades pedidas
                    news_item = {
                        "source": source_name,
                        "title": entry.get("title", "Sem título"),
                        "link": entry.get("link", "Link não disponível"),
                        "publication_date": entry.get("published", entry.get("updated", "Data não disponível")),
                        "summary": entry.get("summary", entry.get("description", "Resumo não disponível"))
                    }
                    extracted_data.append(news_item)
                    count += 1
                    
                logging.info(f"Sucesso: {count} notícias capturadas do {source_name}.")

            except requests.exceptions.Timeout:
                logging.error(f"Timeout: Demora na resposta da fonte {source_name} ({url}).")
            except requests.exceptions.RequestException as req_err:
                logging.error(f"Erro de conexão com o feed {source_name}: {req_err}")
            except Exception as e:
                logging.error(f"Erro inesperado no processamento do feed {source_name}: {e}")

        return extracted_data

if __name__ == "__main__":
    # Instanciando o Fetcher
    fetcher = ThreatIntelNewsFetcher(timeout=10)
    
    # Coletando os dados requisitados
    print("Iniciando varredura de feeds OSINT...")
    news_list = fetcher.fetch_latest_news(limit_per_feed=10)
    
    # Exibir um demonstrativo dos resultados colhidos
    print(f"\nTotal de notícias processadas com sucesso: {len(news_list)}")
    print("-" * 50)
    for news in news_list[:5]: # Exibindo apenas as primeiras para demonstração
        print(f"Fonte  : {news['source']}")
        print(f"Título : {news['title']}")
        print(f"Data   : {news['publication_date']}")
        print(f"Link   : {news['link']}\n")

    print("[*] Script finalizado com sucesso.")
