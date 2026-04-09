from fpdf import FPDF
import io
from datetime import datetime

class ThreatPDF(FPDF):
    def header(self):
        # Arial (or Helvetica) bold 15
        self.set_font('Helvetica', 'B', 15)
        # Title
        self.cell(0, 10, 'AI Threat Sentinel - Relatório Executivo', border=0, ln=1, align='C')
        
        # Subtitle with date
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(100, 100, 100) # Gray
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cell(0, 10, f'Gerado em: {current_time}', border=0, ln=1, align='C')
        
        # Line break
        self.ln(10)
        # Reset text color
        self.set_text_color(0, 0, 0)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Helvetica italic 8
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        # Page number
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generate_executive_pdf(report_data: dict, news_data: list) -> io.BytesIO:
    """
    Gera um relatório executivo em PDF usando a biblioteca fpdf2.
    Retorna um objeto io.BytesIO pronto para ser usado como download no Streamlit.
    """
    pdf = ThreatPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 1. Visão Geral das Ameaças
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(41, 128, 185) # Blue color for headers
    pdf.cell(0, 10, '1. Visão Geral das Ameaças', ln=1)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(0, 0, 0)
    top_threats = report_data.get('top_threats', [])
    if top_threats:
        for threat in top_threats:
            pdf.multi_cell(0, 8, txt=f"\x95 {threat}") # \x95 is ANSI bullet character, or we can use '-'
    else:
        pdf.multi_cell(0, 8, txt="Nenhuma ameaça identificada.")
    pdf.ln(5)

    # 2. Indicadores Críticos
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 10, '2. Indicadores Críticos', ln=1)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(35, 8, 'CVEs:', ln=0)
    pdf.set_font('Helvetica', '', 11)
    cves = report_data.get('cves', [])
    pdf.multi_cell(0, 8, txt=", ".join(cves) if cves else "Nenhum CVE crítico destacado.")
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(35, 8, 'Setores Alvo:', ln=0)
    pdf.set_font('Helvetica', '', 11)
    targeted_sectors = report_data.get('targeted_sectors', [])
    pdf.multi_cell(0, 8, txt=", ".join(targeted_sectors) if targeted_sectors else "Nenhum setor específico.")
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(35, 8, 'Vetores de Ataque:', ln=0)
    pdf.set_font('Helvetica', '', 11)
    attack_vectors = report_data.get('attack_vectors', [])
    pdf.multi_cell(0, 8, txt=", ".join(attack_vectors) if attack_vectors else "Nenhum vetor identificado.")
    pdf.ln(5)

    # 3. Rastreabilidade (Fontes OSINT)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 10, '3. Rastreabilidade (Fontes OSINT)', ln=1)
    pdf.set_text_color(0, 0, 0)
    
    if news_data:
        for news in news_data:
            source = news.get('source', 'Desconhecido')
            title = news.get('title', 'Sem título')
            link = news.get('link', '')
            
            # Em bold para a fonte
            pdf.set_font('Helvetica', 'B', 10)
            pdf.write(6, f"[{source}] ")
            
            # Normal para o título
            pdf.set_font('Helvetica', '', 10)
            # Remove any special chars that fpdf standard core fonts can't handle perfectly out of the box
            title_clean = title.encode('latin-1', 'replace').decode('latin-1')
            pdf.write(6, f"{title_clean}\n")
            
            # Link styling (blue and underline)
            if link:
                pdf.set_text_color(0, 0, 255)
                pdf.set_font('Helvetica', 'U', 9)
                pdf.write(6, link, link)
                pdf.set_text_color(0, 0, 0)
                pdf.write(6, "\n")
            
            pdf.ln(4)
    else:
        pdf.set_font('Helvetica', '', 11)
        pdf.multi_cell(0, 8, txt="Nenhuma fonte processada para este relatório.")

    # fpdf2 implicitamente retorna um bytearray no metodo output() 
    # quando nenhum path é especificado.
    pdf_bytes = pdf.output()
    return io.BytesIO(bytes(pdf_bytes))
