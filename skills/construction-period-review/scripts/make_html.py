#!/usr/bin/env python3
"""성과품을 수정·편집 가능한 HTML(A4 세로) 4개로 작성한다.

    python3 make_html.py <출력폴더> [--input <입력서식.xlsx>]

<출력폴더>는 `python3 -m cpa run ... -o <출력폴더>`(또는 `cpa qty`)의 결과 폴더.
작성 파일 (모두 <출력폴더>/ 아래):
    01_공사기간산정보고서.html  ← _01_공사기간산정보고서.docx
    02_보고서부록.html          ← _02_보고서부록.docx (없으면 02_보고서부록.xlsx)
    03_검토과정_워크북.html     ← 04_검토과정_워크북.xlsx
    04_입력.html                ← --input 파일, 없으면 <출력폴더>/검토입력.xlsx 또는 입력_*.xlsx

각 HTML은 본문을 바로 고칠 수 있고(contenteditable), [저장]은 고친 내용을 HTML 파일로 내려받으며,
[인쇄]는 A4 세로(@page size: A4 portrait)로 출력한다. 필요 패키지: python-docx, openpyxl.
"""
import argparse, base64, datetime, glob, html, os, sys

import docx
import openpyxl
from docx.oxml.ns import qn

A4_CSS = """
:root{--ink:#111;--line:#888;--head:#eef2f7;--accent:#1f4e79}
*{box-sizing:border-box}
html,body{margin:0;background:#d9dde3;color:var(--ink);
  font-family:"Malgun Gothic","맑은 고딕","Noto Sans KR","Apple SD Gothic Neo",sans-serif}
.toolbar{position:sticky;top:0;z-index:9;display:flex;gap:8px;align-items:center;flex-wrap:wrap;
  padding:8px 16px;background:#24313f;color:#fff;font-size:13px}
.toolbar b{margin-right:auto}
.toolbar button{border:0;border-radius:4px;padding:6px 12px;font-size:13px;cursor:pointer;background:#fff;color:#24313f}
.toolbar .hint{opacity:.75;font-size:12px}
.page{width:210mm;min-height:297mm;margin:12px auto;padding:20mm 18mm;background:#fff;
  box-shadow:0 1px 4px rgba(0,0,0,.25);font-size:10pt;line-height:1.55}
.page[contenteditable=true]:focus{outline:2px solid #6aa0d8;outline-offset:-2px}
p{margin:0 0 4pt}
h1{font-size:18pt;color:var(--accent);margin:0 0 10pt;border-bottom:2px solid var(--accent);padding-bottom:4pt}
h2{font-size:13pt;color:var(--accent);margin:14pt 0 6pt}
table{border-collapse:collapse;width:100%;margin:4pt 0 10pt;font-size:8.5pt;table-layout:auto}
th,td{border:1px solid var(--line);padding:2pt 3pt;vertical-align:middle;word-break:keep-all;overflow-wrap:anywhere}
th{background:var(--head)}
table.w2{font-size:7pt} table.w3{font-size:5.5pt} table.w3 td,table.w3 th{padding:1pt}
img{max-width:100%;height:auto}
.num{text-align:right}
.sheet{break-before:page} .sheet:first-of-type{break-before:auto}
.pb{break-before:page}
@page{size:A4 portrait;margin:15mm 12mm}
@media print{
  html,body{background:#fff}
  .toolbar{display:none}
  .page{width:auto;min-height:0;margin:0;padding:0;box-shadow:none}
  tr,img{break-inside:avoid}
  thead{display:table-header-group}
}
"""

TOOLBAR_JS = """
function saveHtml(){
  var d=document.documentElement.cloneNode(true);
  var pg=d.querySelector('.page'); if(pg) pg.setAttribute('contenteditable','true');
  var blob=new Blob(['<!doctype html>\\n'+d.outerHTML],{type:'text/html;charset=utf-8'});
  var a=document.createElement('a'); a.href=URL.createObjectURL(blob);
  a.download=decodeURIComponent((location.pathname.split('/').pop()||document.title+'.html'));
  document.body.appendChild(a); a.click(); a.remove();
}
function toggleEdit(btn){
  var pg=document.querySelector('.page'); var on=pg.getAttribute('contenteditable')!=='true';
  pg.setAttribute('contenteditable',on?'true':'false'); btn.textContent=on?'편집 끄기':'편집 켜기';
}
"""


def page(title, body):
    stamp = datetime.date.today().isoformat()
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>{A4_CSS}</style></head>
<body>
<div class="toolbar"><b>{html.escape(title)}</b>
<span class="hint">본문을 눌러 바로 고칠 수 있습니다 · A4 세로</span>
<button onclick="toggleEdit(this)">편집 끄기</button>
<button onclick="saveHtml()">저장(HTML)</button>
<button onclick="window.print()">인쇄 / PDF</button></div>
<div class="page" contenteditable="true" spellcheck="false">
{body}
<p style="margin-top:14pt;font-size:8pt;color:#666">작성일 {stamp}</p>
</div>
<script>{TOOLBAR_JS}</script>
</body></html>
"""


def esc(v):
    return html.escape("" if v is None else str(v)).replace("\n", "<br>")


def wide_cls(ncols):
    return "w3" if ncols > 20 else "w2" if ncols > 9 else ""


# ---------- DOCX → HTML ----------
def run_html(run, doc):
    out = []
    for blip in run._r.iter(qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        part = doc.part.related_parts.get(rid)
        if part is not None:
            ct = getattr(part, "content_type", "image/png")
            out.append(f'<img src="data:{ct};base64,{base64.b64encode(part.blob).decode()}" alt="">')
    t = esc(run.text)
    if t:
        st = []
        if run.font.size:
            st.append(f"font-size:{run.font.size.pt:g}pt")
        if run.font.color is not None and run.font.color.rgb is not None:
            st.append(f"color:#{run.font.color.rgb}")
        if st:
            t = f'<span style="{";".join(st)}">{t}</span>'
        if run.bold:
            t = f"<b>{t}</b>"
        if run.italic:
            t = f"<i>{t}</i>"
        if run.underline:
            t = f"<u>{t}</u>"
        out.append(t)
    return "".join(out)


ALIGN = {1: "center", 2: "right", 3: "justify"}


def para_html(p, doc):
    if any(br.get(qn("w:type")) == "page" for br in p._p.iter(qn("w:br"))) and not p.text.strip():
        return '<div class="pb"></div>'
    inner = "".join(run_html(r, doc) for r in p.runs)
    if not inner.strip():
        return "<p>&nbsp;</p>"
    al = ALIGN.get(int(p.alignment) if p.alignment is not None else 0)
    style = f' style="text-align:{al}"' if al else ""
    return f"<p{style}>{inner}</p>"


def table_html(t, doc):
    rows = []
    seen = set()
    ncols = max((len(r.cells) for r in t.rows), default=0)
    for ri, row in enumerate(t.rows):
        cells = []
        for tc in row._tr.tc_lst:
            if id(tc) in seen:
                continue
            seen.add(id(tc))
            pr = tc.tcPr
            span = 1
            vm = None
            if pr is not None:
                gs = pr.find(qn("w:gridSpan"))
                span = int(gs.get(qn("w:val"))) if gs is not None else 1
                v = pr.find(qn("w:vMerge"))
                vm = None if v is None else (v.get(qn("w:val")) or "continue")
            if vm == "continue":
                continue
            rs = 1
            if vm == "restart":  # 아래로 이어지는 병합 개수
                idx = list(row._tr.tc_lst).index(tc)
                for nr in t.rows[ri + 1:]:
                    tcs = nr._tr.tc_lst
                    if idx < len(tcs) and tcs[idx].tcPr is not None:
                        v2 = tcs[idx].tcPr.find(qn("w:vMerge"))
                        if v2 is not None and (v2.get(qn("w:val")) or "continue") == "continue":
                            rs += 1
                            continue
                    break
            from docx.table import _Cell
            cell = _Cell(tc, t)
            txt = "<br>".join(filter(None, ("".join(run_html(r, doc) for r in p.runs) for p in cell.paragraphs)))
            tag = "th" if ri == 0 else "td"
            attrs = (f' colspan="{span}"' if span > 1 else "") + (f' rowspan="{rs}"' if rs > 1 else "")
            cells.append(f"<{tag}{attrs}>{txt}</{tag}>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return f'<table class="{wide_cls(ncols)}">' + "\n".join(rows) + "</table>"


def docx_to_html(path):
    doc = docx.Document(path)
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    out = []
    for el in doc.element.body.iterchildren():
        if el.tag == qn("w:p"):
            out.append(para_html(Paragraph(el, doc), doc))
            if el.find(".//" + qn("w:sectPr")) is not None:
                out.append('<div class="pb"></div>')
        elif el.tag == qn("w:tbl"):
            out.append(table_html(Table(el, doc), doc))
    return "\n".join(out)


# ---------- XLSX → HTML ----------
def fmt(v):
    if isinstance(v, float):
        return f"{v:,.3f}".rstrip("0").rstrip(".")
    if isinstance(v, (datetime.datetime, datetime.date)):
        return v.strftime("%Y-%m-%d")
    return v


def sheet_html(ws):
    merged = {}
    skip = set()
    for rng in ws.merged_cells.ranges:
        merged[(rng.min_row, rng.min_col)] = (rng.max_row - rng.min_row + 1, rng.max_col - rng.min_col + 1)
        for r in range(rng.min_row, rng.max_row + 1):
            for c in range(rng.min_col, rng.max_col + 1):
                if (r, c) != (rng.min_row, rng.min_col):
                    skip.add((r, c))
    # 비어 있는 끝 행·열 잘라내기
    maxr = maxc = 0
    for row in ws.iter_rows():
        for c in row:
            if c.value not in (None, ""):
                maxr, maxc = max(maxr, c.row), max(maxc, c.column)
    if not maxr:
        return "<p>(빈 시트)</p>"
    rows = []
    for r in range(1, maxr + 1):
        cells = []
        for c in range(1, maxc + 1):
            if (r, c) in skip:
                continue
            cell = ws.cell(r, c)
            v = fmt(cell.value)
            rs, cs = merged.get((r, c), (1, 1))
            attrs = (f' colspan="{cs}"' if cs > 1 else "") + (f' rowspan="{rs}"' if rs > 1 else "")
            st = []
            fill = cell.fill.fgColor.rgb if cell.fill and cell.fill.fill_type == "solid" else None
            if isinstance(fill, str) and len(fill) == 8 and fill not in ("00000000", "FFFFFFFF"):
                st.append(f"background:#{fill[2:]}")
            if cell.font and cell.font.b:
                st.append("font-weight:bold")
            if isinstance(cell.value, (int, float)):
                attrs += ' class="num"'
            if st:
                attrs += f' style="{";".join(st)}"'
            cells.append(f"<td{attrs}>{esc(v)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    # 엑셀 열 너비를 비율로 옮긴다
    from openpyxl.utils import get_column_letter
    ws_ = [ws.column_dimensions[get_column_letter(c)].width or 9 for c in range(1, maxc + 1)]
    tot = sum(ws_) or 1
    cols = "".join(f'<col style="width:{w / tot * 100:.1f}%">' for w in ws_)
    return f'<table class="{wide_cls(maxc)}"><colgroup>{cols}</colgroup>' + "\n".join(rows) + "</table>"


def xlsx_to_html(path, title):
    wb = openpyxl.load_workbook(path, data_only=True)
    out = [f"<h1>{esc(title)}</h1>"]
    for ws in wb.worksheets:
        if ws.sheet_state != "visible" or ws.title.startswith("_"):
            continue
        out.append(f'<section class="sheet"><h2>{esc(ws.title)}</h2>{sheet_html(ws)}</section>')
    return "\n".join(out)


def write(path, title, body):
    with open(path, "w", encoding="utf-8") as f:
        f.write(page(title, body))
    print("작성:", path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", help="cpa 결과 폴더")
    ap.add_argument("--input", help="입력서식 xlsx (생략 시 결과 폴더의 검토입력.xlsx / 입력_*.xlsx)")
    a = ap.parse_args()
    o = a.out
    j = lambda n: os.path.join(o, n)

    src = j("_01_공사기간산정보고서.docx")
    if os.path.exists(src):
        write(j("01_공사기간산정보고서.html"), "공사기간 산정보고서", docx_to_html(src))
    else:
        print("[경고] _01_공사기간산정보고서.docx 없음 — 보고서 HTML 생략", file=sys.stderr)

    if os.path.exists(j("_02_보고서부록.docx")):
        write(j("02_보고서부록.html"), "보고서 부록", docx_to_html(j("_02_보고서부록.docx")))
    elif os.path.exists(j("02_보고서부록.xlsx")):
        write(j("02_보고서부록.html"), "보고서 부록", xlsx_to_html(j("02_보고서부록.xlsx"), "보고서 부록"))
    else:
        print("[경고] 보고서 부록 원본 없음", file=sys.stderr)

    if os.path.exists(j("04_검토과정_워크북.xlsx")):
        write(j("03_검토과정_워크북.html"), "검토과정 워크북",
              xlsx_to_html(j("04_검토과정_워크북.xlsx"), "검토과정 워크북"))
    else:
        print("[경고] 04_검토과정_워크북.xlsx 없음", file=sys.stderr)

    inp = a.input or next(iter([p for p in [j("검토입력.xlsx")] if os.path.exists(p)]
                                + sorted(glob.glob(j("입력_*.xlsx")))), None)
    if inp and os.path.exists(inp):
        write(j("04_입력.html"), "입력", xlsx_to_html(inp, "입력 (" + os.path.basename(inp) + ")"))
    else:
        print("[경고] 입력서식 xlsx 없음 — --input 으로 지정하십시오", file=sys.stderr)


if __name__ == "__main__":
    main()
