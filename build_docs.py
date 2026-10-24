# -*- coding: utf-8 -*-
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

BASE = Path(__file__).resolve().parent

DATA = json.load(open(BASE / 'data.json', encoding='utf-8'))['DATA']
models = DATA['headers'][1:]
rows = DATA['rows']

# ---- analysis ----
SECTIONS = {'长焦模拟', '广角模拟'}
def is_na(v):
    return (not v) or v == '—' or v == '-' or v.startswith('—（')
def distinct(vals):
    s = set(v for v in vals if not is_na(v))
    return len(s)

# ---- styles (light theme, print-friendly) ----
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
FONT = 'STSong-Light'
ss = getSampleStyleSheet()
title_s = ParagraphStyle('t', fontName=FONT, fontSize=20, leading=24, textColor=colors.HexColor('#1a1a1f'))
sub_s   = ParagraphStyle('s', fontName=FONT, fontSize=10.5, leading=15, textColor=colors.HexColor('#555'))
note_s  = ParagraphStyle('n', fontName=FONT, fontSize=8.5, leading=13, textColor=colors.HexColor('#666'))
hdr_s   = ParagraphStyle('h', fontName=FONT, fontSize=8.5, leading=11, textColor=colors.white, alignment=TA_CENTER)
grp_s   = ParagraphStyle('g', fontName=FONT, fontSize=9, leading=12, textColor=colors.white, alignment=TA_CENTER)
model_s = ParagraphStyle('m', fontName=FONT, fontSize=8.5, leading=11, textColor=colors.HexColor('#1a1a1f'), alignment=TA_CENTER)
param_s = ParagraphStyle('p', fontName=FONT, fontSize=8.5, leading=11, textColor=colors.HexColor('#1a1a1f'))
cell_s  = ParagraphStyle('c', fontName=FONT, fontSize=7.6, leading=9.6, textColor=colors.HexColor('#222'))
cellc_s = ParagraphStyle('cc', fontName=FONT, fontSize=7.6, leading=9.6, textColor=colors.HexColor('#222'), alignment=TA_CENTER)
sect_s  = ParagraphStyle('sec', fontName=FONT, fontSize=9.5, leading=12, textColor=colors.HexColor('#fff'), alignment=TA_CENTER)

DWARF = colors.HexColor('#e64a40')
ZWO   = colors.HexColor('#d9882e')
GRP_DWARF = colors.HexColor('#b8352c')
GRP_ZWO   = colors.HexColor('#b06f1e')
SECT_FILL = colors.HexColor('#2a2a30')
ZEBRA = colors.HexColor('#f4f4f6')

def brand_of(m):
    return 'dwarf' if m.startswith('DWARF') else 'zwo'

# ---- build table data ----
n = len(models)
colw = [42*mm] + [(273-42)/n*mm for _ in range(n)]  # landscape A4 usable ~273mm

data_table = []
# group row
grp_cells = ['']
dwarf_n = sum(1 for m in models if brand_of(m)=='dwarf')
zwo_n = n - dwarf_n
grp_cells.append(Paragraph('DWARFLAB', grp_s));  # placeholder, will span
# Build group row with spans
group_row = ['']
if dwarf_n: group_row.append(Paragraph('DWARFLAB', grp_s))
if zwo_n:   group_row.append(Paragraph('ZWO Seestar', grp_s))
data_table.append(group_row)

# model row
model_row = [Paragraph('参数', model_s)]
for m in models:
    model_row.append(Paragraph(m, model_s))
data_table.append(model_row)

# body rows
for r in rows:
    label = r[0]
    vals = r[1:]
    if label in SECTIONS:
        sec_row = [Paragraph(f'✦ {label} · 星图软件模拟参数', sect_s)]
        data_table.append(sec_row)
        continue
    row = [Paragraph(label, param_s)]
    for v in vals:
        txt = v if v else '—'
        row.append(Paragraph(str(txt).replace('\n','<br/>'), cell_s))
    data_table.append(row)

# ---- table style ----
ts = [
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333')),
    ('SPAN', (0,0), (0,0)),  # group row first cell empty
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,1), (-1,-1), 0.4, colors.HexColor('#cfcfd4')),
    ('LINEBELOW', (0,0), (-1,0), 0.6, colors.HexColor('#333')),
    ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ('LEFTPADDING', (0,0), (-1,-1), 3),
    ('RIGHTPADDING', (0,0), (-1,-1), 3),
]
# group row spans & fill
ci = 1
if dwarf_n:
    ts.append(('SPAN', (ci,0), (ci+dwarf_n-1,0)))
    ts.append(('BACKGROUND', (ci,0), (ci+dwarf_n-1,0), GRP_DWARF))
    ci += dwarf_n
if zwo_n:
    ts.append(('SPAN', (ci,0), (ci+zwo_n-1,0)))
    ts.append(('BACKGROUND', (ci,0), (ci+zwo_n-1,0), GRP_ZWO))

# model header row fill (row index 1)
ts.append(('BACKGROUND', (1,1), (-1,1), colors.HexColor('#e9e9ee')))
ts.append(('LINEBELOW', (0,1), (-1,1), 0.6, colors.HexColor('#9a9aa0')))

# style body rows: zebra + section fills + param cell shading
ridx = 2
for r in rows:
    label = r[0]
    if label in SECTIONS:
        ts.append(('SPAN', (0,ridx), (-1,ridx)))
        ts.append(('BACKGROUND', (0,ridx), (-1,ridx), SECT_FILL))
        ts.append(('TOPPADDING', (0,ridx), (-1,ridx), 4))
        ts.append(('BOTTOMPADDING', (0,ridx), (-1,ridx), 4))
    else:
        if (ridx-2) % 2 == 1:
            ts.append(('BACKGROUND', (0,ridx), (-1,ridx), ZEBRA))
        ts.append(('BACKGROUND', (0,ridx), (0,ridx), colors.HexColor('#ececef')))
        # tint brand name cells lightly
        for j,m in enumerate(models):
            col = 1+j
            if brand_of(m)=='dwarf':
                ts.append(('TEXTCOLOR', (col,ridx), (col,ridx), colors.HexColor('#9a281f')))
            else:
                ts.append(('TEXTCOLOR', (col,ridx), (col,ridx), colors.HexColor('#8a5410')))
    ridx += 1

table = Table(data_table, colWidths=colw, repeatRows=2)
table.setStyle(TableStyle(ts))

# ---- assemble PDF ----
doc = SimpleDocTemplate(str(BASE / '7 款智能望远镜参数对比表.pdf'),
                        pagesize=landscape(A4),
                        leftMargin=12*mm, rightMargin=12*mm,
                        topMargin=12*mm, bottomMargin=12*mm,
                        title='智能望远镜参数规格对比')
diff_count = sum(1 for r in rows if r[0] not in SECTIONS and distinct(r[1:])>1)
story = [
    Paragraph('智能望远镜参数规格对比', title_s),
    Paragraph('DWARFLAB × ZWO Seestar｜共 %d 款机型 · %d 项参数 · %d 项存在差异' % (n, len(rows), diff_count), sub_s),
    Spacer(1, 4),
    HRFlowable(width='100%', thickness=0.8, color=colors.HexColor('#ccc')),
    Spacer(1, 6),
]
story.append(table)
story.append(Spacer(1, 8))
story.append(Paragraph(
    '数据说明：原始数据由 Linea松果 提供。Seestar S50 Pro、S30 Pro 与 S50 参数依据 ZWO / Seestar、Sony 官方资料复核'
    '（2026-08-27）；S50 Pro 于 2026-09-10 二次复核（长焦 OmniVision OS08B10、广角 Sony IMX586；读噪/满阱/QE 官方未公开，'
    '依芯片规格标注）。DWARFLAB Draco 依据 DWARFLAB 官方产品页规格表录入（2026-09-10）。标注「芯片规格 / 官方规格」者来自传感器或'
    '厂商公开资料；标注「几何换算」者为口径焦距推算值；「—（官方未公开）」表示厂商未披露。', note_s))
doc.build(story)
print('PDF written. diff_count =', diff_count)

# ===================== DOCX =====================
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

EA = '宋体'
def set_ea(run):
    run.font.name = EA
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts'); rpr.append(rfonts)
    rfonts.set(qn('w:eastAsia'), EA)

def shade(cell, hexcolor):
    tcpr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hexcolor)
    tcpr.append(sh)

def set_text(cell, text, bold=False, size=8, color=None, align='left'):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = {'left':WD_ALIGN_PARAGRAPH.LEFT,'center':WD_ALIGN_PARAGRAPH.CENTER,
                   'right':WD_ALIGN_PARAGRAPH.RIGHT}[align]
    # support line breaks
    parts = str(text).split('\n')
    for i, part in enumerate(parts):
        if i>0:
            run = p.add_run(); run.add_break()
        else:
            run = p.add_run(part)
            set_ea(run); run.bold = bold; run.font.size = Pt(size)
            if color: run.font.color.rgb = RGBColor.from_string(color)
            continue
        run = p.add_run(part); set_ea(run); run.font.size = Pt(size)
        if color: run.font.color.rgb = RGBColor.from_string(color)
        run.bold = bold

def set_widths(table, widths_cm):
    table.autofit = False
    table.allow_autofit = False
    for row in table.rows:
        for idx, w in enumerate(widths_cm):
            row.cells[idx].width = Cm(w)

dw = Document()
sec = dw.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = sec.page_height, sec.page_width
sec.left_margin = Cm(1.2); sec.right_margin = Cm(1.2)
sec.top_margin = Cm(1.2); sec.bottom_margin = Cm(1.2)

tp = dw.add_paragraph(); tp.alignment = WD_ALIGN_PARAGRAPH.LEFT
r = tp.add_run('智能望远镜参数规格对比'); set_ea(r); r.bold = True; r.font.size = Pt(18); r.font.color.rgb = RGBColor.from_string('1A1A1F')
sp = dw.add_paragraph()
r = sp.add_run('DWARFLAB × ZWO Seestar｜共 %d 款机型 · %d 项参数 · %d 项存在差异' % (n, len(rows), diff_count))
set_ea(r); r.font.size = Pt(10.5); r.font.color.rgb = RGBColor.from_string('555555')

widths = [4.4] + [(27.3-4.4)/n for _ in range(n)]  # Cm
t = dw.add_table(rows=2, cols=n+1)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
t.style = 'Table Grid'

# group row
g0 = t.rows[0].cells[0]; set_text(g0, '', size=8)
ci = 1
if dwarf_n:
    gcell = t.rows[0].cells[ci]
    set_text(gcell, 'DWARFLAB', bold=True, size=9, color='FFFFFF', align='center'); shade(gcell, 'B8352C')
    merge = t.rows[0].cells[ci]
    for k in range(ci+1, ci+dwarf_n):
        merge = merge.merge(t.rows[0].cells[k])
    ci += dwarf_n
if zwo_n:
    gcell = t.rows[0].cells[ci]
    set_text(gcell, 'ZWO Seestar', bold=True, size=9, color='FFFFFF', align='center'); shade(gcell, 'B06F1E')
    merge = t.rows[0].cells[ci]
    for k in range(ci+1, ci+zwo_n):
        merge = merge.merge(t.rows[0].cells[k])

# model row
set_text(t.rows[1].cells[0], '参数', bold=True, size=8.5, align='center'); shade(t.rows[1].cells[0], 'ECECEF')
for j,m in enumerate(models):
    c = t.rows[1].cells[1+j]
    set_text(c, m, bold=True, size=8.5, align='center'); shade(c, 'E9E9EE')
    if brand_of(m)=='dwarf': c.paragraphs[0].runs[0].font.color.rgb = RGBColor.from_string('9A281F')
    else: c.paragraphs[0].runs[0].font.color.rgb = RGBColor.from_string('8A5410')

# body
for r in rows:
    label = r[0]; vals = r[1:]
    cells = t.add_row().cells
    if label in SECTIONS:
        set_text(cells[0], f'✦ {label} · 星图软件模拟参数', bold=True, size=9, color='FFFFFF', align='center')
        shade(cells[0], '2A2A30')
        merge = cells[0]
        for k in range(1, n+1):
            merge = merge.merge(cells[k])
        continue
    set_text(cells[0], label, bold=True, size=8.5); shade(cells[0], 'ECECEF')
    for j,v in enumerate(vals):
        c = cells[1+j]
        txt = v if v else '—'
        set_text(c, txt, size=7.8)
        if brand_of(models[j])=='dwarf': c.paragraphs[0].runs[0].font.color.rgb = RGBColor.from_string('9A281F')
        else: c.paragraphs[0].runs[0].font.color.rgb = RGBColor.from_string('8A5410')

set_widths(t, widths)

# note
np_ = dw.add_paragraph()
r = np_.add_run(
    '数据说明：原始数据由 Linea松果 提供。Seestar S50 Pro、S30 Pro 与 S50 参数依据 ZWO / Seestar、Sony 官方资料复核'
    '（2026-08-27）；S50 Pro 于 2026-09-10 二次复核（长焦 OmniVision OS08B10、广角 Sony IMX586；读噪/满阱/QE 官方未公开，'
    '依芯片规格标注）。DWARFLAB Draco 依据 DWARFLAB 官方产品页规格表录入（2026-09-10）。标注「芯片规格 / 官方规格」者来自传感器或'
    '厂商公开资料；标注「几何换算」者为口径焦距推算值；「—（官方未公开）」表示厂商未披露。')
set_ea(r); r.font.size = Pt(8.5); r.font.color.rgb = RGBColor.from_string('666666')

dw.save(str(BASE / 'telescope_compare.docx'))
print('DOCX written.')

