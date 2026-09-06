import csv
import io
from pathlib import Path

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONT_NAME = "Helvetica"
for _folder in ("C:/Windows/Fonts", "/usr/share/fonts/truetype/dejavu"):
    for _name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        _path = Path(_folder) / _name
        if _path.exists():
            try:
                pdfmetrics.registerFont(TTFont("VNFont", str(_path)))
                FONT_NAME = "VNFont"
            except Exception:
                pass
            break
    if FONT_NAME != "Helvetica":
        break


def to_csv(rows, headers) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([row.get(h, "") for h in headers])
    return buffer.getvalue().encode("utf-8-sig")


def to_excel(rows, headers, sheet_name="Report") -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name[:31]
    ws.append(list(headers))
    for cell in ws[1]:
        from openpyxl.styles import Font

        cell.font = Font(bold=True)
    for row in rows:
        ws.append([row.get(h, "") for h in headers])
    for idx, h in enumerate(headers, start=1):
        width = max(
            [len(str(h))] + [len(str(row.get(h, ""))) for row in rows[:50]] + [10]
        )
        ws.column_dimensions[chr(64 + idx) if idx <= 26 else "A"].width = min(width + 2, 50)
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def to_pdf(title, rows, headers) -> bytes:
    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        title=title,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    style_title = ParagraphStyle(
        "TitleVN", fontName=FONT_NAME, fontSize=14, spaceAfter=12
    )
    style_cell = ParagraphStyle("CellVN", fontName=FONT_NAME, fontSize=9)
    elements = [Paragraph(title, style_title), Spacer(1, 6)]

    data = [[Paragraph(str(h), style_cell) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(row.get(h, "")), style_cell) for h in headers])

    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    return output.getvalue()
