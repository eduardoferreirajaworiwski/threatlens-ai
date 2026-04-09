import feedparser
import requests
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ThreatIntelNewsFetcher:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.feeds = {
            "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
            "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
            "Dark Reading": "https://www.darkreading.com/rss.xml"
        }

    def fetch_latest_news(self, limit_per_feed: int = 10) -> List[Dict]:
        extracted_data = []

        for source_name, url in self.feeds.items():
            logging.info(f"Collecting feed: {source_name}")

            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) OSINT/ThreatIntel Bot'}
                response = requests.get(url, timeout=self.timeout, headers=headers)
                response.raise_for_status()

                feed = feedparser.parse(response.content)

                if feed.bozo and hasattr(feed, 'bozo_exception'):
                    logging.warning(f"Feed format warning for {source_name}: {feed.bozo_exception}")

                count = 0
                for entry in feed.entries:
                    if count >= limit_per_feed:
                        break

                    news_item = {
                        "source": source_name,
                        "title": entry.get("title", "Untitled"),
                        "link": entry.get("link", "Link unavailable"),
                        "publication_date": entry.get("published", entry.get("updated", "Date unavailable")),
                        "summary": entry.get("summary", entry.get("description", "No summary available"))
                    }
                    extracted_data.append(news_item)
                    count += 1

                logging.info(f"Success: {count} articles captured from {source_name}.")

            except requests.exceptions.Timeout:
                logging.error(f"Timeout: No response from {source_name} ({url}).")
            except requests.exceptions.RequestException as req_err:
                logging.error(f"Connection error with {source_name}: {req_err}")
            except Exception as e:
                logging.error(f"Unexpected error processing {source_name}: {e}")

        return extracted_data

if __name__ == "__main__":
    fetcher = ThreatIntelNewsFetcher(timeout=10)

    print("Starting OSINT feed scan...")
    news_list = fetcher.fetch_latest_news(limit_per_feed=10)

    print(f"\nTotal articles processed: {len(news_list)}")
    print("-" * 50)
    for news in news_list[:5]:
        print(f"Source : {news['source']}")
        print(f"Title  : {news['title']}")
        print(f"Date   : {news['publication_date']}")
        print(f"Link   : {news['link']}\n")

    print("[*] Script completed successfully.")
