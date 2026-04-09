import streamlit as st
import pandas as pd
import plotly.express as px
from fetch_news import ThreatIntelNewsFetcher
from ai_analyzer import ThreatIntelAnalyzer
from db_manager import init_db, save_report, get_historical_sectors
from pdf_exporter import generate_executive_pdf

st.set_page_config(
    page_title="Threat Lens AI 🔍",
    page_icon="🔍",
    layout="wide"
)

init_db()

if 'report_data' not in st.session_state:
    st.session_state.report_data = None
    st.session_state.news_data = None

st.title("Threat Lens AI 🔍")

st.info("Real-time cyber threat intelligence powered by OSINT feeds and Google Gemini AI.")

tab1, tab2 = st.tabs(["🛡️ Threat Intel (Live)", "📈 Historical Data"])

with tab1:
    if st.button("Generate Today's Tactical Report", type="primary", use_container_width=True):
        with st.spinner("Intercepting global threat feeds..."):
            try:
                fetcher = ThreatIntelNewsFetcher(timeout=15)
                news_data = fetcher.fetch_latest_news(limit_per_feed=10)

                if not news_data:
                    st.error("Could not capture any news. Check your network and OSINT providers.")
                else:
                    analyzer = ThreatIntelAnalyzer()
                    report_data = analyzer.generate_executive_report(news_data)

                    if "error" in report_data:
                        st.error(report_data["error"])
                    else:
                        st.session_state.report_data = report_data
                        st.session_state.news_data = news_data
                        save_report(report_data)
                        st.success("Analysis complete and saved to database!")

            except ValueError as ve:
                st.error(f"Environment Error: {ve}. Make sure to set GEMINI_API_KEY in your .env file!")
            except Exception as e:
                st.error(f"Critical Engine Failure: {e}")

    st.markdown("---")

    if st.session_state.report_data is not None:
        report_data = st.session_state.report_data
        news_data = st.session_state.news_data

        top_threats = report_data.get("top_threats", [])
        cves = report_data.get("cves", [])
        sectors = report_data.get("targeted_sectors", [])
        vectors = report_data.get("attack_vectors", [])

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Quick Metrics")
            subcol_a, subcol_b = st.columns(2)
            with subcol_a:
                st.metric(label="Threats Mapped", value=len(top_threats))
            with subcol_b:
                st.metric(label="Critical CVEs", value=len(cves))
            st.metric(label="Attack Vectors Analyzed", value=len(vectors))

        with col2:
            st.subheader("🎯 Targeted Sectors")
            if sectors:
                df_sectors = pd.DataFrame(sectors, columns=["Sectors"])
                df_grouped = df_sectors.value_counts().reset_index()
                df_grouped.columns = ["Sector", "Cases"]

                fig = px.bar(
                    df_grouped, x="Cases", y="Sector", orientation="h", color="Sector", text_auto=True
                )
                fig.update_layout(showlegend=False, margin=dict(t=0, l=0, r=0, b=0), height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No specific sectors were identified in today's news.")

        st.divider()
        st.subheader("📑 Detailed Breakdown")

        with st.expander("Executive Summary (Top Threats)", expanded=True):
            for threat in top_threats:
                st.warning(threat)

        with st.expander("Critical Vulnerabilities (CVEs)", expanded=True):
            if cves:
                df_cves = pd.DataFrame(cves, columns=["Threat Identifiers (CVE)"])
                st.table(df_cves)
            else:
                st.success("No critical CVE codes flagged in this report.")

        with st.expander("⚙️ Attack Vectors Identified", expanded=True):
            if vectors:
                for v in vectors:
                    st.info(f"**Vector:** {v}")
            else:
                st.write("No vector metrics available.")

        st.sidebar.header("📡 Intercepted Sources")
        st.sidebar.caption("To mitigate AI hallucination, audit the original links:")
        st.sidebar.markdown("---")

        if news_data:
            for item in news_data:
                source = item.get("source", "Unknown Source")
                title = item.get("title", "Untitled")
                link = item.get("link", "#")
                st.sidebar.markdown(f"- **{source}**: [{title}]({link})")

        st.markdown("---")
        st.subheader("📥 Export Report")

        pdf_buffer = generate_executive_pdf(report_data, news_data)

        st.download_button(
            label="📄 Download Executive Report (PDF)",
            data=pdf_buffer,
            file_name="threatlens_executive_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

with tab2:
    st.subheader("Historical Overview")

    historical_df = get_historical_sectors()

    if not historical_df.empty:
        fig_hist = px.bar(
            historical_df,
            x="Count",
            y="Sector",
            orientation="h",
            color="Sector",
            text_auto=True,
            title="Global Sectors Attacked (Historical)"
        )
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("Your historical database is empty. Go to the 'Threat Intel (Live)' tab and generate a report!")
