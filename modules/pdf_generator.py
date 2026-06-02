import os, traceback
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER


GREEN = '#059669'
LIGHT_BG = '#f1f5f9'
BORDER = '#cbd5e1'
BODY_TEXT = '#1e293b'
MUTED_TEXT = '#64748b'


def _detect_info(row):
    cols = [c.lower() for c in row.keys()]
    all_set = set(cols)

    if any('invoice' in c for c in cols):
        title = 'INVOICE'
        msg = 'Thank you for your business'
        id_col = 'invoice_no'
    elif any(k in all_set for k in ['marks', 'grade', 'roll_no', 'subject']):
        title = 'STUDENT REPORT'
        msg = 'Best wishes for your future'
        id_col = 'name'
    elif any(k in all_set for k in ['emp_id', 'net_pay', 'deductions']):
        title = 'SALARY REPORT'
        msg = 'This is a computer-generated statement'
        id_col = 'name'
    else:
        title = 'REPORT'
        msg = 'Thank you'
        id_col = list(row.keys())[0]

    subtitle = str(row.get(id_col, list(row.values())[0]))
    return title, subtitle, msg


def generate_pdf(row, output_dir, filename):
    title, subtitle, footer_msg = _detect_info(row)

    pdf_path = os.path.join(output_dir, filename)
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            topMargin=14*mm, bottomMargin=14*mm,
                            leftMargin=14*mm, rightMargin=14*mm)
    styles = getSampleStyleSheet()
    avail_w = A4[0] - 28*mm

    hdr_st = ParagraphStyle('HT', fontName='Helvetica-Bold',
                              fontSize=22, leading=26,
                              textColor=colors.white, alignment=TA_CENTER)
    ftr_st = ParagraphStyle('FT', fontName='Helvetica',
                              fontSize=10, leading=14,
                              textColor=colors.white, alignment=TA_CENTER)
    cell = ParagraphStyle('Cell', fontName='Helvetica',
                           fontSize=10, leading=14,
                           textColor=colors.HexColor(BODY_TEXT))
    cell_hdr = ParagraphStyle('HC', fontName='Helvetica-Bold',
                               fontSize=10, leading=14,
                               textColor=colors.white)
    sub_st = ParagraphStyle('Sub', parent=cell, fontSize=12, spaceAfter=10,
                             alignment=TA_CENTER,
                             textColor=colors.HexColor(MUTED_TEXT))
    msg_st = ParagraphStyle('Msg', parent=cell, fontSize=10, spaceAfter=6,
                             alignment=TA_CENTER,
                             textColor=colors.HexColor(MUTED_TEXT))

    elements = []

    # ---- HEADER ----
    hdr = Table([[Paragraph(title, hdr_st)]],
                colWidths=[avail_w], rowHeights=[95])
    hdr.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(GREEN)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(hdr)

    if subtitle:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(subtitle, sub_st))

    # ---- AUTO TABLE from row data ----
    elements.append(Spacer(1, 6))
    hdrs = [Paragraph('Field', cell_hdr), Paragraph('Value', cell_hdr)]
    data_rows = []
    for col, val in row.items():
        data_rows.append([Paragraph(str(col), cell),
                          Paragraph(str(val), cell)])
    tbl_data = [hdrs] + data_rows
    cw = avail_w / 2
    tbl = Table(tbl_data, colWidths=[cw, cw])
    sty = [
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER)),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(GREEN)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    for ri in range(1, len(tbl_data)):
        sty.append(('BACKGROUND', (0, ri), (-1, ri),
                    colors.HexColor(LIGHT_BG if ri % 2 == 0 else '#ffffff')))
    tbl.setStyle(TableStyle(sty))
    elements.append(tbl)

    # ---- FOOTER MESSAGE ----
    if footer_msg:
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(footer_msg, msg_st))

    # ---- FOOTER ----
    elements.append(Spacer(1, 10))
    ftr = Table([[Paragraph(title, ftr_st)]],
                colWidths=[avail_w], rowHeights=[50])
    ftr.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(GREEN)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(ftr)

    try:
        doc.build(elements)
    except Exception as e:
        traceback.print_exc()
        doc.build([Paragraph(f'Error: {e}', cell)])
    return pdf_path
