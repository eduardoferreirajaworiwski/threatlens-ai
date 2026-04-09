import os
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Configuração local de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ThreatIntelAnalyzer:
    """
    Motor de Inteligência que utiliza as capacidades de LLM (gemini-1.5-flash) para
    processar feeds OSINT em massa, realizando as análises e extrações pedidas.
    """
    def __init__(self):
        # Carregamento seguro da GEMINI_API_KEY do sistema
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logging.error("Variável de ambiente 'GEMINI_API_KEY' não foi encontrada!")
            raise ValueError("Chave de API do Gemini ausente no arquivo .env.")
        
        # Instanciar a SDK da LLM
        
        # Definição do System Prompt solicitado (Instruções Base)
        self.system_instruction = (
            "Você é um Analista de Inteligência de Ameaças Sênior. Analise as notícias fornecidas "
            "e gere um Relatório Executivo de Cibersegurança em formato Markdown. O relatório deve conter:\n"
            "1. 🚨 **Top 3 Ameaças Iminentes** (Identifique padrões ou ataques recorrentes nas notícias).\n"
            "2. 🦠 **Vulnerabilidades & Malwares** (Liste os CVEs, ransomwares ou malwares citados).\n"
            "3. 🎯 **Alvos Principais** (Setores ou empresas sob ataque hoje).\n"
            "Seja direto, técnico e não invente dados. Use apenas as notícias fornecidas."
        )

        try:
            # Inicializando a instância do client
            self.client = genai.Client(api_key=self.api_key)
            logging.info("Motor de IA carregado e inicializado: gemini-2.5-flash")
        except Exception as e:
            logging.error(f"Erro Crítico de SDK ao instanciar o modelo Gemini: {e}")
            raise

    def generate_executive_report(self, news_list: list) -> str:
        """
        Recebe as notícias em formato de dicionário, aplica filtragem de contexto e
        solicita ao engine de IA um sumário executivo sobre o cenário das ameaças.
        """
        if not news_list:
            logging.warning("O motor recusou a processar uma lista vazia.")
            return "Erro: Sem dados para processar."
        
        logging.info("Otimizando tokens para inteligência artificial...")
        
        # Filtramos apenas a fonte, o título e o resumo de cada notícia.
        # Descartando a data/link poupamos consideravelmente o contexto.
        optimized_context = []
        for i, news in enumerate(news_list):
            source = news.get("source", "Desconhecido")
            title = news.get("title", "Sem título")
            summary = news.get("summary", "Sem resumo")
            
            event_block = f"--- Evento SecOps {i+1} ---\nFonte: {source}\nTítulo: {title}\nResumo: {summary}\n"
            optimized_context.append(event_block)
            
        context_string = "\n".join(optimized_context)

        logging.info("Prompt construído. Enviando para a Google Generative AI (requer tempo de resposta)...")
        
        try:
            # Chamada principal à API do Gemini utilizando o novo SDK (google-genai)
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=context_string,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction
                )
            )
            
            if response and response.text:
                 logging.info("O Relatório Executivo de Cibersegurança foi concebido via AI.")
                 return response.text
            else:
                 logging.warning("Payload do modelo esteve vazio ou censurado pelos filtros base.")
                 return "Erro de Modelagem: O Gemini retornou uma predição vazia ou bloqueada."

        # Captura extensiva (Timeout, Network Erros, Quota e etc)
        except Exception as e:
            logging.error(f"Ocorreu uma falha grave na comunicação com o LLM: {str(e)}")
            return f"**Erro Temporário de IA:** Não foi possível confeccionar o relatório no momento.\nDetalhe técnico: `{str(e)}`"

if __name__ == "__main__":
    from fetch_news import ThreatIntelNewsFetcher
    
    # Demonstração autossuficiente caso o arquivo seja executado separadamente
    try:
        # Coleta das últimas duas notícias de cada feed
        fetcher = ThreatIntelNewsFetcher(timeout=10)
        dados_osint = fetcher.fetch_latest_news(limit_per_feed=2)
        
        # Iniciar o motor e gerar a inteligência
        analyzer = ThreatIntelAnalyzer()
        relatorio = analyzer.generate_executive_report(dados_osint)
        
        print("\n\n" + "="*70)
        print(" RELATÓRIO DO MOTOR EXECUTIVO SEC-OPS ".center(70, " "))
        print("="*70 + "\n")
        print(relatorio)
        print("\n" + "="*70)
        
    except ValueError as val_err:
        print(f"\n[!] Bloqueio de Configuração: {val_err}")
        print("-> Verifique se renomeou corretamente seu .env e colocou sua API KEY.")
    except ImportError as imp_err:
        print(f"\n[!] Problema no módulo: {imp_err}")
    except Exception as generic_err:
        print(f"\n[!] Falha ao testar via terminal: {generic_err}")
