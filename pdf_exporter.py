from fpdf import FPDF
from fpdf.enums import XPos, YPos
import io
from datetime import datetime

# ── Dark Hacker Theme Colors ──
BG_DARK = (10, 10, 18)
BG_SECTION = (18, 18, 30)
BG_CARD = (24, 26, 40)
BG_NEWS_ROW_A = (20, 22, 35)
BG_NEWS_ROW_B = (26, 28, 44)
NEON_GREEN = (0, 255, 65)
NEON_CYAN = (0, 212, 255)
NEON_RED = (255, 50, 80)
NEON_YELLOW = (255, 220, 40)
ACCENT_PURPLE = (160, 80, 255)
TEXT_WHITE = (230, 230, 240)
TEXT_DIM = (140, 145, 165)


class ThreatPDF(FPDF):
    def _draw_page_bg(self):
        self.set_fill_color(*BG_DARK)
        self.rect(0, 0, self.w, self.h, style='F')

    def header(self):
        self._draw_page_bg()

        self.set_fill_color(*BG_SECTION)
        self.rect(0, 0, self.w, 36, style='F')

        self.set_draw_color(*NEON_GREEN)
        self.set_line_width(0.6)
        self.line(10, 36, self.w - 10, 36)

        self.set_y(5)
        self.set_font('Courier', 'B', 20)
        self.set_text_color(*NEON_GREEN)
        self.cell(0, 10, '> THREAT LENS AI_', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        self.set_font('Courier', '', 7)
        self.set_text_color(*TEXT_DIM)
        current_time = datetime.now().strftime("%Y-%m-%d  %H:%M:%S UTC-3")
        self.cell(0, 5, f'[GENERATED] {current_time}  |  CLASSIFICATION: TACTICAL  |  OSINT + AI ENGINE', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        self.set_font('Courier', 'B', 7)
        self.set_text_color(*NEON_RED)
        self.cell(0, 5, '[ CONFIDENTIAL  //  EXECUTIVE THREAT BRIEFING  //  AI-GENERATED INTELLIGENCE ]', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(*NEON_GREEN)
        self.set_line_width(0.3)
        self.line(10, self.h - 15, self.w - 10, self.h - 15)
        self.set_font('Courier', '', 7)
        self.set_text_color(*TEXT_DIM)
        self.cell(0, 10, f'Threat Lens AI  |  Page {self.page_no()}/{{nb}}  |  Powered by OSINT + Gemini AI', 0, 0, 'C')


def _safe(text: str) -> str:
    return text.encode('latin-1', 'replace').decode('latin-1')


def _section_title(pdf: FPDF, num: str, title: str, color: tuple):
    y = pdf.get_y()
    usable = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_fill_color(*BG_SECTION)
    pdf.rect(pdf.l_margin, y, usable, 10, style='F')

    pdf.set_fill_color(*color)
    pdf.rect(pdf.l_margin, y, 3, 10, style='F')

    pdf.set_x(pdf.l_margin + 6)
    pdf.set_font('Courier', 'B', 11)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f'[{num}] {title}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)


def _metric_box(pdf: FPDF, x: float, y: float, w: float, label: str, value: str, color: tuple):
    pdf.set_fill_color(*BG_CARD)
    pdf.rect(x, y, w, 20, style='F')

    pdf.set_draw_color(*color)
    pdf.set_line_width(0.5)
    pdf.line(x, y, x + w, y)

    pdf.set_xy(x, y + 2)
    pdf.set_font('Courier', '', 6)
    pdf.set_text_color(*TEXT_DIM)
    pdf.cell(w, 4, label.upper(), align='C')

    pdf.set_xy(x, y + 8)
    pdf.set_font('Courier', 'B', 14)
    pdf.set_text_color(*color)
    pdf.cell(w, 8, str(value), align='C')


def _needs_page(pdf: FPDF, height: float) -> bool:
    return pdf.get_y() + height > pdf.h - 20


def generate_executive_pdf(report_data: dict, news_data: list) -> io.BytesIO:
    pdf = ThreatPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    top_threats = report_data.get('top_threats', [])
    cves = report_data.get('cves', [])
    sectors = report_data.get('targeted_sectors', [])
    vectors = report_data.get('attack_vectors', [])

    usable = pdf.w - pdf.l_margin - pdf.r_margin

    # ═══════════════ METRICS DASHBOARD ═══════════════
    y = pdf.get_y()
    box_w = (usable - 9) / 4
    gap = 3
    x0 = pdf.l_margin

    _metric_box(pdf, x0, y, box_w, 'Threats Mapped', str(len(top_threats)), NEON_GREEN)
    _metric_box(pdf, x0 + box_w + gap, y, box_w, 'Critical CVEs', str(len(cves)), NEON_RED)
    _metric_box(pdf, x0 + 2 * (box_w + gap), y, box_w, 'Target Sectors', str(len(sectors)), NEON_CYAN)
    _metric_box(pdf, x0 + 3 * (box_w + gap), y, box_w, 'Attack Vectors', str(len(vectors)), ACCENT_PURPLE)

    pdf.set_y(y + 25)

    # ═══════════════ 01: TOP THREATS ═══════════════
    _section_title(pdf, '01', 'TOP THREATS IDENTIFIED', NEON_GREEN)
    if top_threats:
        for i, threat in enumerate(top_threats):
            if _needs_page(pdf, 10):
                pdf.add_page()
            y = pdf.get_y()
            bg = BG_NEWS_ROW_A if i % 2 == 0 else BG_NEWS_ROW_B
            text = _safe(f"  > {threat}")

            pdf.set_font('Courier', '', 9)
            line_w = usable - 10
            lines = max(1, int(pdf.get_string_width(text) / line_w) + 1)
            row_h = 7 * lines

            pdf.set_fill_color(*bg)
            pdf.rect(pdf.l_margin, y, usable, row_h, style='F')
            pdf.set_fill_color(*NEON_GREEN)
            pdf.rect(pdf.l_margin, y, 2, row_h, style='F')

            pdf.set_x(pdf.l_margin + 4)
            pdf.set_text_color(*TEXT_WHITE)
            pdf.multi_cell(line_w, 7, text=text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.set_font('Courier', 'I', 9)
        pdf.set_text_color(*TEXT_DIM)
        pdf.cell(0, 7, '  [NO THREATS FLAGGED]', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # ═══════════════ 02: CRITICAL CVEs ═══════════════
    if _needs_page(pdf, 30):
        pdf.add_page()
    _section_title(pdf, '02', 'CRITICAL VULNERABILITIES (CVEs)', NEON_RED)
    if cves:
        col_w = (usable - 6) / 3
        y_start = pdf.get_y()
        for i, cve in enumerate(cves):
            col = i % 3
            row = i // 3
            bx = pdf.l_margin + col * (col_w + 3)
            by = y_start + row * 12

            if by + 12 > pdf.h - 20:
                pdf.add_page()
                y_start = pdf.get_y()
                by = y_start

            pdf.set_fill_color(*BG_CARD)
            pdf.rect(bx, by, col_w, 10, style='F')
            pdf.set_draw_color(*NEON_RED)
            pdf.set_line_width(0.3)
            pdf.rect(bx, by, col_w, 10, style='D')
            pdf.set_xy(bx, by)
            pdf.set_font('Courier', 'B', 9)
            pdf.set_text_color(*NEON_RED)
            pdf.cell(col_w, 10, _safe(cve), align='C')

        total_rows = (len(cves) + 2) // 3
        pdf.set_y(y_start + total_rows * 12 + 2)
    else:
        pdf.set_font('Courier', 'I', 9)
        pdf.set_text_color(*NEON_GREEN)
        pdf.cell(0, 7, '  [STATUS: CLEAR - No critical CVEs flagged]', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # ═══════════════ 03: ATTACK VECTORS ═══════════════
    if _needs_page(pdf, 30):
        pdf.add_page()
    _section_title(pdf, '03', 'ATTACK VECTORS DETECTED', ACCENT_PURPLE)
    if vectors:
        for i, v in enumerate(vectors):
            if _needs_page(pdf, 10):
                pdf.add_page()
            y = pdf.get_y()
            pdf.set_fill_color(*BG_CARD)
            pdf.rect(pdf.l_margin, y, usable, 8, style='F')
            pdf.set_fill_color(*ACCENT_PURPLE)
            pdf.rect(pdf.l_margin, y, 2, 8, style='F')
            pdf.set_x(pdf.l_margin + 5)
            pdf.set_font('Courier', 'B', 9)
            pdf.set_text_color(*NEON_YELLOW)
            pdf.cell(8, 8, f'{i+1:02d}')
            pdf.set_font('Courier', '', 9)
            pdf.set_text_color(*TEXT_WHITE)
            pdf.cell(0, 8, _safe(f'  {v}'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.set_font('Courier', 'I', 9)
        pdf.set_text_color(*TEXT_DIM)
        pdf.cell(0, 7, '  [NO VECTORS IDENTIFIED]', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # ═══════════════ 04: TARGETED SECTORS ═══════════════
    if _needs_page(pdf, 25):
        pdf.add_page()
    _section_title(pdf, '04', 'TARGETED SECTORS', NEON_CYAN)
    if sectors:
        pdf.set_font('Courier', 'B', 8)
        tag_x = pdf.l_margin
        tag_y = pdf.get_y()
        for sector in sectors:
            tag_w = pdf.get_string_width(_safe(sector)) + 14
            if tag_x + tag_w > pdf.w - pdf.r_margin:
                tag_x = pdf.l_margin
                tag_y += 12
            pdf.set_fill_color(*BG_CARD)
            pdf.rect(tag_x, tag_y, tag_w, 9, style='F')
            pdf.set_draw_color(*NEON_CYAN)
            pdf.set_line_width(0.3)
            pdf.rect(tag_x, tag_y, tag_w, 9, style='D')
            pdf.set_xy(tag_x, tag_y)
            pdf.set_text_color(*NEON_CYAN)
            pdf.cell(tag_w, 9, _safe(sector), align='C')
            tag_x += tag_w + 5
        pdf.set_y(tag_y + 14)
    else:
        pdf.set_font('Courier', 'I', 9)
        pdf.set_text_color(*TEXT_DIM)
        pdf.cell(0, 7, '  [NO SPECIFIC SECTORS IDENTIFIED]', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    # ═══════════════ 05: OSINT NEWS FEED ═══════════════
    if _needs_page(pdf, 30):
        pdf.add_page()
    _section_title(pdf, '05', 'OSINT SOURCE TRACEABILITY', NEON_GREEN)
    if news_data:
        for i, news in enumerate(news_data):
            if _needs_page(pdf, 18):
                pdf.add_page()
                _section_title(pdf, '05', 'OSINT SOURCE TRACEABILITY (CONT.)', NEON_GREEN)

            y = pdf.get_y()
            source = news.get('source', 'UNKNOWN')
            title = _safe(news.get('title', 'Untitled'))
            link = news.get('link', '')
            display_link = link if len(link) < 80 else link[:77] + '...'

            bg = BG_NEWS_ROW_A if i % 2 == 0 else BG_NEWS_ROW_B
            pdf.set_fill_color(*bg)
            pdf.rect(pdf.l_margin, y, usable, 15, style='F')

            pdf.set_fill_color(*NEON_CYAN)
            pdf.rect(pdf.l_margin, y, 2, 15, style='F')

            pdf.set_xy(pdf.l_margin + 5, y + 1)
            pdf.set_font('Courier', 'B', 7)
            pdf.set_text_color(*NEON_CYAN)
            src_tag = source.upper()[:18]
            pdf.cell(30, 5, f'[{src_tag}]')
            pdf.set_font('Courier', '', 8)
            pdf.set_text_color(*TEXT_WHITE)
            pdf.cell(0, 5, f'  {title[:88]}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_x(pdf.l_margin + 5)
            pdf.set_font('Courier', '', 6)
            pdf.set_text_color(*TEXT_DIM)
            pdf.cell(0, 4, f'Link: {display_link}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_y(y + 16)

    pdf.ln(4)

    # ═══════════════ END BANNER ═══════════════
    if _needs_page(pdf, 16):
        pdf.add_page()

    y = pdf.get_y()
    pdf.set_fill_color(*BG_SECTION)
    pdf.rect(pdf.l_margin, y, usable, 12, style='F')
    pdf.set_draw_color(*NEON_GREEN)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, y, pdf.l_margin + usable, y)
    pdf.line(pdf.l_margin, y + 12, pdf.l_margin + usable, y + 12)

    pdf.set_xy(pdf.l_margin, y + 1)
    pdf.set_font('Courier', 'B', 8)
    pdf.set_text_color(*NEON_GREEN)
    pdf.cell(usable, 10, '> END OF BRIEFING  //  THREAT LENS AI  //  STAY VIGILANT_', align='C')

    pdf_bytes = pdf.output()
    return io.BytesIO(bytes(pdf_bytes))
