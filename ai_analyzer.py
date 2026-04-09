import os
import json
import logging
from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Configuração local de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ThreatReport(BaseModel):
    """Esquema Pydantic para forçar output estruturado da IA."""
    top_threats: List[str] = Field(description="resumo das 3 principais ameaças")
    cves: List[str] = Field(description="códigos CVE como 'CVE-2024-1234'. Se não houver, lista vazia")
    targeted_sectors: List[str] = Field(description="ex: ['Finance', 'Healthcare']")
    attack_vectors: List[str] = Field(description="ex: ['Ransomware', 'Phishing']")

class ThreatIntelAnalyzer:
    """
    Motor de Inteligência que utiliza as capacidades de LLM (gemini-2.5-flash) para
    processar feeds OSINT em massa, realizando as análises estruturadas.
    """
    def __init__(self):
        # Carregamento seguro da GEMINI_API_KEY do sistema
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logging.error("Variável de ambiente 'GEMINI_API_KEY' não foi encontrada!")
            raise ValueError("Chave de API do Gemini ausente no arquivo .env.")
        
        # Definição do System Prompt otimizado para extração JSON
        self.system_instruction = (
            "Você é um Analista de Inteligência de Ameaças Sênior. Sua resposta DEVE OBRIGATORIAMENTE "
            "ser um JSON puro respeitando o schema solicitado. Analise as notícias fornecidas "
            "e extraia as top_threats, cves, targeted_sectors e attack_vectors."
            "Não invente nada inexistente no contexto."
        )

        try:
            self.client = genai.Client(api_key=self.api_key)
            logging.info("Motor de IA carregado: gemini-2.5-flash (Modo JSON Estruturado)")
        except Exception as e:
            logging.error(f"Erro Crítico ao instanciar o modelo: {e}")
            raise

    def generate_executive_report(self, news_list: list) -> dict:
        """
        Recebe as notícias, aplica filtragem e solicita ao engine de IA um
        retorno no formato estrito do schema `ThreatReport` em JSON.
        """
        if not news_list:
            logging.warning("Nenhum dado recebido.")
            return {"error": "Sem dados para processar."}
        
        logging.info("Otimizando payload contextual...")
        
        optimized_context = []
        for i, news in enumerate(news_list):
            source = news.get("source", "Desconhecido")
            title = news.get("title", "Sem título")
            summary = news.get("summary", "Sem resumo")
            optimized_context.append(f"--- Evento SecOps {i+1} ---\nFonte: {source}\nTítulo: {title}\nResumo: {summary}\n")
            
        context_string = "\n".join(optimized_context)

        logging.info("Solicitando Extração JSON via AI...")
        
        try:
            # Integração com os recursos 'Structured Outputs' via Object Schema
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
                 logging.info("Estrutura JSON validada e recebida.")
                 try:
                     # Parse do JSON String devolvido em um Python Dictionary real
                     return json.loads(response.text)
                 except json.JSONDecodeError:
                     return {"error": "Falha no decode", "raw": response.text}
            else:
                 return {"error": "Retorno vazio da API."}

        except Exception as e:
            logging.error(f"Falha de IA: {str(e)}")
            return {"error": str(e)}

if __name__ == "__main__":
    from fetch_news import ThreatIntelNewsFetcher
    
    try:
        fetcher = ThreatIntelNewsFetcher(timeout=10)
        dados_osint = fetcher.fetch_latest_news(limit_per_feed=2)
        
        analyzer = ThreatIntelAnalyzer()
        relatorio_json = analyzer.generate_executive_report(dados_osint)
        
        print("\n\n" + "="*70)
        print(" THREAT INTELLIGENCE (JSON STRUCTURED) ".center(70, " "))
        print("="*70 + "\n")
        print(json.dumps(relatorio_json, indent=4, ensure_ascii=False))
        print("\n" + "="*70)
        
    except ValueError as val_err:
        print(f"\n[!] Bloqueio: {val_err}")
    except Exception as generic_err:
        print(f"\n[!] Falha terminal: {generic_err}")
