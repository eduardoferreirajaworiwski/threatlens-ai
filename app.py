import streamlit as st
import pandas as pd
import plotly.express as px
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

# 2. Informação descritiva
st.info("Esta ferramenta utiliza OSINT (RSS Feeds) e IA Generativa (Google Gemini) para mapear ameaças globais em tempo real.")

if st.button("Gerar Relatório Tático de Hoje", type="primary", use_container_width=True):
    with st.spinner("Interceptando feeds globais de ameaças..."):
        try:
            # Passo A: Ingestão de OSINT local
            fetcher = ThreatIntelNewsFetcher(timeout=15)
            news_data = fetcher.fetch_latest_news(limit_per_feed=10)
            
            if not news_data:
                st.error("Não conseguimos capturar nenhuma notícia. Verifique sua rede e os provedores OSINT.")
            else:
                # Passo B: Motor de IA garantindo saída em JSON Pydantic
                analyzer = ThreatIntelAnalyzer()
                report_data = analyzer.generate_executive_report(news_data)
                
                st.markdown("---")
                if "error" in report_data:
                    st.error(report_data["error"])
                else:
                    # Coletando variáveis de forma segura do dict JSON
                    top_threats = report_data.get("top_threats", [])
                    cves = report_data.get("cves", [])
                    sectors = report_data.get("targeted_sectors", [])
                    vectors = report_data.get("attack_vectors", [])

                    # 2. Layout dividido em duas colunas
                    col1, col2 = st.columns(2)
                    
                    # 3. Coluna 1: Métricas Rápidas
                    with col1:
                        st.subheader("📊 Métricas Rápidas")
                        subcol_a, subcol_b = st.columns(2)
                        with subcol_a:
                            st.metric(label="Total de Ameaças Mapeadas", value=len(top_threats))
                        with subcol_b:
                            st.metric(label="Total de CVEs / Vulnerabilidades", value=len(cves))
                            
                        # Podemos colocar um terceiro número de metric também!
                        st.metric(label="Vetores de Ataque Analisados", value=len(vectors))
                        
                    # 4. Coluna 2: Gráfico usando Plotly
                    with col2:
                        st.subheader("🎯 Setores sob ataque")
                        if sectors:
                            # Converte lista textual para Pandas DataFrame
                            df_sectors = pd.DataFrame(sectors, columns=["Setores"])
                            
                            # Agrupa contabilizando as repetições (se a IA achar o mesmo setor 2x)
                            df_grouped = df_sectors.value_counts().reset_index()
                            df_grouped.columns = ["Setor", "Casos"]
                            
                            # Gráfico de barras simples e rápido
                            fig = px.bar(
                                df_grouped, 
                                x="Casos", 
                                y="Setor", 
                                orientation="h",
                                color="Setor",
                                text_auto=True
                            )
                            fig.update_layout(showlegend=False, margin=dict(t=0, l=0, r=0, b=0), height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("A IA não apontou especificamente os setores nas notícias de hoje.")

                    st.divider()
                    
                    # 5. Expanders para Listas Visuais (Detalhamento)
                    st.subheader("📑 Detalhamento Integrado")
                    
                    with st.expander("Resumo Executivo (Top Threats)", expanded=True):
                        for threat in top_threats:
                            st.warning(threat)
                            
                    with st.expander("Vulnerabilidades Críticas (CVEs)", expanded=True):
                        if cves:
                             # Renderizando via Tabela (Pandas Dataframe no st.table ou st.dataframe)
                             df_cves = pd.DataFrame(cves, columns=["Threat Identifiers (CVE)"])
                             st.table(df_cves)
                        else:
                             st.success("Nenhum código CVE crítico flagrado no relatório matinal.")
                             
                    with st.expander("⚙️ Vetores de Ataque Identificados", expanded=True):
                        if vectors:
                            # Renderizando em colunas ou tags
                            for v in vectors:
                                st.info(f"**Vetor:** {v}")
                        else:
                            st.write("Métricas de vetores não disponíveis.")
                
                # 6. Sidebar (Anti-Alucinação)
                st.sidebar.header("📡 Fontes Interceptadas")
                st.sidebar.caption("Para mitigar e evitar alucinação da IA, audite nos links originais do processo executivo:")
                st.sidebar.markdown("---")
                
                for item in news_data:
                    source = item.get("source", "Fonte Desconhecida")
                    title = item.get("title", "Sem título")
                    link = item.get("link", "#")
                    st.sidebar.markdown(f"- **{source}**: [{title}]({link})")
                    
        except ValueError as ve:
            st.error(f"Erro de Ambiente: {ve}. Lembre-se de preencher a GEMINI_API_KEY no arquivo .env!")
        except Exception as e:
            st.error(f"Falha Grave do Analisador Neural: {e}")
