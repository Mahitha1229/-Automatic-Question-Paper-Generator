import io, os
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, Image as RLImage)
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Inches

BASE = os.path.dirname(os.path.abspath(__file__))

# groups = [(heading_or_None, [item, ...]), ...]
# item   = {"no", "question", "marks", "qtype", "options": [...], "image_path"}


def _opts(it):
    o = it.get("options") or []
    if not o and it.get("qtype") == "true_false":
        o = ["True", "False"]
    return o


def _img_path(it):
    p = it.get("image_path")
    if not p:
        return None
    full = os.path.join(BASE, p)
    return full if os.path.exists(full) else None


def _pdf_image(path, max_w=10 * cm, max_h=6 * cm):
    w, h = ImageReader(path).getSize()
    s = min(max_w / w, max_h / h, 1)
    return RLImage(path, width=w * s, height=h * s, hAlign="LEFT")


def _para(text, style):
    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def make_pdf(groups, title, subject, duration, total):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=16, spaceAfter=4)
    center = ParagraphStyle("c", parent=ss["Normal"], alignment=1, fontSize=11)
    sec = ParagraphStyle("sec", parent=ss["Heading3"], spaceBefore=12, spaceAfter=6)
    body = ParagraphStyle("b", parent=ss["Normal"], fontSize=11, leading=14)
    opt = ParagraphStyle("o", parent=body, leftIndent=14, spaceBefore=2)

    story = [_para(title, h1), _para(subject, center), Spacer(1, 8)]
    meta = Table([[f"Time: {duration}", f"Total Marks: {total}"]], colWidths=[8.5*cm, 8.5*cm])
    meta.setStyle(TableStyle([("ALIGN", (0, 0), (0, 0), "LEFT"), ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                              ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold")]))
    story += [meta, HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=4, spaceAfter=6)]

    for heading, items in groups:
        if heading:
            story.append(_para(heading, sec))
        rows = []
        for it in items:
            cell = [_para(it["question"], body)]
            img = _img_path(it)
            if img:
                try:
                    cell += [Spacer(1, 4), _pdf_image(img)]
                except Exception:
                    cell.append(_para("[image could not be loaded]", body))
            for i, o in enumerate(_opts(it)):
                cell.append(_para(f"({chr(65 + i)}) {o}", opt))
            rows.append([f"Q{it['no']}.", cell, f"[{it['marks']}]"])
        tbl = Table(rows, colWidths=[1.2*cm, 14.3*cm, 1.5*cm])
        tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        story.append(tbl)
    doc.build(story)
    return buf.getvalue()


def make_docx(groups, title, subject, duration, total):
    d = Document()
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title); r.bold = True; r.font.size = Pt(16)
    p = d.add_paragraph(subject); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    d.add_paragraph(f"Time: {duration}\t\t\tTotal Marks: {total}")
    for heading, items in groups:
        if heading:
            d.add_heading(heading, level=3)
        for it in items:
            d.add_paragraph(f"Q{it['no']}. {it['question']}  [{it['marks']} marks]")
            img = _img_path(it)
            if img:
                try:
                    d.add_picture(img, width=Inches(3.2))
                except Exception:
                    d.add_paragraph("[image could not be loaded]")
            for i, o in enumerate(_opts(it)):
                op = d.add_paragraph(f"({chr(65 + i)}) {o}")
                op.paragraph_format.left_indent = Inches(0.4)
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def make_txt(groups, title, subject, duration, total):
    lines = [title, subject, f"Time: {duration}    Total Marks: {total}"]
    for heading, items in groups:
        if heading:
            lines += ["", heading]
        for it in items:
            lines.append(f"Q{it['no']}. {it['question']} [{it['marks']} marks]")
            if _img_path(it):
                lines.append("    [Image: " + os.path.basename(it["image_path"]) + "]")
            for i, o in enumerate(_opts(it)):
                lines.append(f"    ({chr(65 + i)}) {o}")
    return "\n".join(lines)