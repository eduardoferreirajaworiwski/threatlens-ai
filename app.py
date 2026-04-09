import streamlit as st
from fetch_news import ThreatIntelNewsFetcher
from ai_analyzer import ThreatIntelAnalyzer

# 1. Configuração da página e Layout
st.set_page_config(
    page_title="AI Threat Sentinel 🛡️",
    page_icon="🛡️",
    layout="wide"
)

# Header
st.title("AI Threat Sentinel 🛡️")

# 2. Informação descritiva da arquitetura
st.info("Esta ferramenta utiliza OSINT (RSS Feeds) e IA Generativa (Google Gemini) para mapear ameaças globais em tempo real.")

# 3. Interação do Usuário - Botão Principal
# Utilizando layout em colunas para o botão ficar mais bem posicionado no centro caso queiramos,
# mas use_container_width deixará ele de ponta a ponta.
if st.button("Gerar Relatório Tático de Hoje", type="primary", use_container_width=True):
    
    # 4. Feedback visual enquanto realiza a esteira de dados
    with st.spinner("Interceptando feeds globais de ameaças..."):
        try:
            # Passo A: Ingestão de OSINT
            fetcher = ThreatIntelNewsFetcher(timeout=15)
            news_data = fetcher.fetch_latest_news(limit_per_feed=10)
            
            if not news_data:
                st.error("Não conseguimos capturar nenhuma notícia. Verifique sua rede e os provedores OSINT.")
            else:
                # Passo B: Motor de IA / Processamento
                analyzer = ThreatIntelAnalyzer()
                report_markdown = analyzer.generate_executive_report(news_data)
                
                # 5. Exibição de Resposta Centralizada (Markdown da IA)
                st.markdown("---")
                st.markdown(report_markdown)
                
                # 6. Sidebar - Listagem e Rastreabilidade (Fontes Originais)
                st.sidebar.header("📡 Fontes Interceptadas")
                st.sidebar.caption("Para mitigar e evitar alucinação da IA, audite nos links originais que enviamos ao processo.")
                st.sidebar.markdown("---")
                
                # Exibe cada notícia com seu hiperlink para checagem da fonte
                for item in news_data:
                    source = item.get("source", "Fonte Desconhecida")
                    title = item.get("title", "Sem título")
                    link = item.get("link", "#")
                    st.sidebar.markdown(f"- **{source}**: [{title}]({link})")
                    
        except ValueError as ve:
            st.error(f"Erro de Ambiente: {ve}. Lembre-se preencher a GEMINI_API_KEY no arquivo .env!")
        except Exception as e:
            st.error(f"Falha Grave Interna do Sistema: {e}")
