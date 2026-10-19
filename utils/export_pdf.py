"""
PDF Export Utility for SEO Suite Pro:
Generates executive-branded PDF audit reports using ReportLab with custom gold-accented styling.
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from core.config import (
    BRAND_NAME,
    BRAND_OWNER,
    FOOTER_TEXT,
    LOGO_PATH,
    PORTFOLIO_URL,
)

GOLD_COLOR = colors.HexColor("#D4AF37")
DARK_COLOR = colors.HexColor("#141414")
LIGHT_GOLD = colors.HexColor("#FDF8E2")

def generate_pdf_report(title: str, target_domain: str, kpis: list[tuple[str, str]], issues: list[dict], recommendations: list[str] | None = None) -> bytes:
    """
    Builds a PDF document with branding, KPI summary tables, and issue diagnostics.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        "ReportHeader",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=DARK_COLOR
    )
    sub_style = ParagraphStyle(
        "ReportSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#555555")
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=GOLD_COLOR,
        spaceBefore=14,
        spaceAfter=6
    )
    cell_style = ParagraphStyle(
        "CellNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=DARK_COLOR
    )
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white
    )
    
    story = []
    
    # Header Banner with Logo
    header_data = []
    logo_img = None
    if LOGO_PATH.exists():
        try:
            logo_img = Image(str(LOGO_PATH), width=48, height=48)
        except Exception:
            logo_img = None
            
    title_p = Paragraph(f"<b>{BRAND_NAME}</b><br/><font size=10 color='#666666'>Executive Technical SEO Report — {target_domain}</font>", header_style)
    date_p = Paragraph(f"<font size=8 color='#888888'>Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>Architect: {BRAND_OWNER}</font>", sub_style)
    
    if logo_img:
        banner_table = Table([[logo_img, title_p, date_p]], colWidths=[60, 360, 120])
    else:
        banner_table = Table([[title_p, date_p]], colWidths=[420, 120])
        
    banner_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD_COLOR, spaceBefore=4, spaceAfter=12))
    
    # KPI Grid Table
    story.append(Paragraph("EXECUTIVE KPI SUMMARY", section_style))
    if kpis:
        # Group KPIs into rows of 3
        kpi_rows = []
        for i in range(0, len(kpis), 3):
            chunk = kpis[i:i+3]
            row_cells = []
            for lbl, val in chunk:
                cell_content = f"<b>{lbl}</b><br/><font size=14 color='#B8962E'><b>{val}</b></font>"
                row_cells.append(Paragraph(cell_content, cell_style))
            while len(row_cells) < 3:
                row_cells.append(Paragraph("", cell_style))
            kpi_rows.append(row_cells)
            
        kpi_table = Table(kpi_rows, colWidths=[180, 180, 180])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9F9F9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E0E0E0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EAEAEA")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))
        
    # Top Technical Issues Table
    story.append(Paragraph("PRIORITY ACTION ITEMS & ROOT-CAUSE DIAGNOSTICS", section_style))
    if issues:
        issue_rows = [[
            Paragraph("Category", cell_bold),
            Paragraph("Severity", cell_bold),
            Paragraph("Item / Target", cell_bold),
            Paragraph("Root-Cause Diagnosis & Fix", cell_bold)
        ]]
        
        for item in issues[:12]:
            cat = Paragraph(item.get("category", "General"), cell_style)
            sev = Paragraph(f"<b>{item.get('severity', 'Medium')}</b>", cell_style)
            target = Paragraph(f"<b>{item.get('item', '')}</b><br/><font size=7 color='#666'>{item.get('url', '')[:60]}</font>", cell_style)
            fix_text = f"<b>Problem:</b> {item.get('problem', '')}<br/><b>Fix:</b> {item.get('fix', '')}"
            fix_p = Paragraph(fix_text, cell_style)
            issue_rows.append([cat, sev, target, fix_p])
            
        issue_table = Table(issue_rows, colWidths=[90, 60, 130, 260])
        issue_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FDFDFD")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(issue_table)
        story.append(Spacer(1, 14))
        
    # Strategic Recommendations (e.g. from Gemini or Rules Engine)
    if recommendations:
        story.append(Paragraph("STRATEGIC RECOMMENDATIONS", section_style))
        for rec in recommendations:
            story.append(Paragraph(f"&bull; {rec}", cell_style))
            story.append(Spacer(1, 4))
            
    # Footer Note
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E0E0E0"), spaceBefore=4, spaceAfter=8))
    footer_p = Paragraph(f"<font size=8 color='#777777'>{FOOTER_TEXT} | Portfolio: <a href='{PORTFOLIO_URL}' color='#B8962E'>{PORTFOLIO_URL}</a></font>", sub_style)
    story.append(footer_p)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
