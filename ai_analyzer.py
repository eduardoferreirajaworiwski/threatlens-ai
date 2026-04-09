import os
import json
import logging
from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ThreatReport(BaseModel):
    top_threats: List[str] = Field(description="Summary of the top 3 threats identified")
    cves: List[str] = Field(description="CVE codes like 'CVE-2024-1234'. Empty list if none found")
    targeted_sectors: List[str] = Field(description="e.g. ['Finance', 'Healthcare']")
    attack_vectors: List[str] = Field(description="e.g. ['Ransomware', 'Phishing']")

class ThreatIntelAnalyzer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            logging.error("Environment variable 'GEMINI_API_KEY' not found!")
            raise ValueError("Gemini API key missing from .env file.")

        self.system_instruction = (
            "You are a Senior Threat Intelligence Analyst. Your response MUST be pure JSON "
            "respecting the requested schema. Analyze the provided news and extract "
            "top_threats, cves, targeted_sectors and attack_vectors. "
            "Do not invent anything that does not exist in the context."
        )

        try:
            self.client = genai.Client(api_key=self.api_key)
            logging.info("AI engine loaded: gemini-2.5-flash (Structured JSON Mode)")
        except Exception as e:
            logging.error(f"Critical error instantiating model: {e}")
            raise

    def generate_executive_report(self, news_list: list) -> dict:
        if not news_list:
            logging.warning("No data received.")
            return {"error": "No data to process."}

        logging.info("Optimizing contextual payload...")

        optimized_context = []
        for i, news in enumerate(news_list):
            source = news.get("source", "Unknown")
            title = news.get("title", "Untitled")
            summary = news.get("summary", "No summary")
            optimized_context.append(f"--- SecOps Event {i+1} ---\nSource: {source}\nTitle: {title}\nSummary: {summary}\n")

        context_string = "\n".join(optimized_context)

        logging.info("Requesting structured JSON extraction via AI...")

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=context_string,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    response_mime_type="application/json",
                    response_schema=ThreatReport,
                )
            )

            if response and response.text:
                logging.info("JSON structure validated and received.")
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    return {"error": "JSON decode failure", "raw": response.text}
            else:
                return {"error": "Empty API response."}

        except Exception as e:
            logging.error(f"AI failure: {str(e)}")
            return {"error": str(e)}

if __name__ == "__main__":
    from fetch_news import ThreatIntelNewsFetcher

    try:
        fetcher = ThreatIntelNewsFetcher(timeout=10)
        osint_data = fetcher.fetch_latest_news(limit_per_feed=2)

        analyzer = ThreatIntelAnalyzer()
        report_json = analyzer.generate_executive_report(osint_data)

        print("\n" + "=" * 70)
        print(" THREAT INTELLIGENCE (JSON STRUCTURED) ".center(70))
        print("=" * 70 + "\n")
        print(json.dumps(report_json, indent=4, ensure_ascii=False))
        print("\n" + "=" * 70)

    except ValueError as val_err:
        print(f"\n[!] Blocked: {val_err}")
    except Exception as generic_err:
        print(f"\n[!] Fatal failure: {generic_err}")
