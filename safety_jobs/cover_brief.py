# /// script
# requires-python = ">=3.10"
# ///
"""자기소개서 일일 브리핑 HTML 생성.

drafts/index.json 과 drafts/*.md 초안을 읽어 아티팩트용 index.html 을 만든다.
초안 md 형식은 아래와 같다(머리말 + 기업 개요 + 기업 분석 + 문항).

    ---
    company: 대한전선(주)
    title: 2027 신입사원 채용 (SHE)
    url: https://...
    deadline: 2026-10-11
    tags: 코스피
    starter: 신입 초봉 4,500만원 (2025)   (선택: 사용자가 확인한 초봉, 채용현황 브리핑 값보다 우선)
    written: 2026-10-01
    questions: 자소설닷컴 2026 하반기 문항        (문항 출처, 양식이 없으면 '홈페이지 채용 정보 기준 구성')
    ---
    ## 기업 개요
    - 회사: 설립 연도 · 본사 · 상장 시장 · 소속 그룹
    - 주요 사업: ...   (매출 규모·임직원 수·주요 사업장·시공능력평가 순위 등)
    ## 기업 분석
    - DART: ...
    - 최근 기사: [제목](URL) (YYYY-MM-DD)
    ## Q1 | 1000
    > 문항 원문
    **[소제목]**
    본문 문단...

    python3 safety_jobs/cover_brief.py --drafts drafts --out index.html [--today YYYY-MM-DD]
        [--briefing briefings/latest.json ...] [--exclude excluded.json]

표의 '구분' 아래에는 고용형태(머리말 employment), '공고' 아래에는 공고 기재 연봉 · 신입 초봉을 적는다.
초봉은 --briefing 으로 준 채용현황 브리핑의 extra.starter(잡코리아 기업 연봉정보 '신입 초봉 N만원 (연도)')로만
통일한다(같은 공고 → 같은 업체 순, 없으면 '신입 초봉 확인 못 함'). 초안 카드 기본 정보에도 같은 값을 적는다.
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

KST = dt.timezone(dt.timedelta(hours=9))
e = html.escape


def parse_draft(text):
    meta, body = {}, text
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            if v:
                meta[k.strip()] = v.strip()
        body = m.group(2)
    analysis, questions, cur = [], [], None
    for block in re.split(r"^## ", body, flags=re.M)[1:]:
        head, _, rest = block.partition("\n")
        qm = re.match(r"(Q\d+)\s*\|\s*([\d,]+)", head)
        if qm:
            quote = "\n".join(l[1:].strip() for l in rest.splitlines() if l.startswith(">"))
            lines = [l for l in rest.splitlines() if not l.startswith(">")]
            sub = ""
            text_lines = []
            for l in lines:
                sm = re.fullmatch(r"\*\*\[(.+)\]\*\*", l.strip())
                if sm and not sub:
                    sub = sm.group(1)
                else:
                    text_lines.append(l)
            answer = re.sub(r"\n{3,}", "\n\n", "\n".join(text_lines)).strip()
            cur = {"id": qm.group(1), "limit": int(qm.group(2).replace(",", "")), "question": quote, "sub": sub, "answer": answer}
            questions.append(cur)
        elif head.strip().startswith("기업 분석"):
            analysis = [l[2:].strip() for l in rest.splitlines() if l.startswith("- ")]
        elif head.strip().startswith("기업 개요"):
            # 반환 형태를 바꾸지 않도록 머리말에 목록으로 담는다
            meta["overview"] = [l[2:].strip() for l in rest.splitlines() if l.startswith("- ")]
    return meta, analysis, questions


def inline(s):
    """**굵게**, [링크](URL) 만 지원."""
    out, pos = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*|\[([^\]]+)\]\((https?://[^)\s]+)\)", s):
        out.append(e(s[pos:m.start()]))
        if m.group(1):
            out.append(f"<b>{e(m.group(1))}</b>")
        else:
            out.append(f'<a href="{e(m.group(3))}" target="_blank" rel="noopener">{e(m.group(2))}</a>')
        pos = m.end()
    out.append(e(s[pos:]))
    return "".join(out)


def count(s):
    return len(s.replace("\n", ""))


def d_left(deadline, today):
    try:
        return (dt.date.fromisoformat(deadline) - today).days
    except ValueError:
        return None


def dpill(n):
    if n is None:
        return '<span class="pill">마감 미정</span>'
    if n < 0:
        return '<span class="pill mute">마감</span>'
    cls = "err" if n <= 3 else "warn" if n <= 7 else "ok"
    return f'<span class="pill {cls}">D-{n}</span>' if n else '<span class="pill err">오늘 마감</span>'


def chips_of(m):
    return "".join(f'<span class="chip">{e(t.strip())}</span>' for t in m.get("tags", "").split(",") if t.strip())


def draft_body(d, analysis_cls="facts"):
    """공고 정보 표 + 기업 개요 + 기업 분석 + 문항 카드(편집·글자수·복사)."""
    m = d["meta"]
    qs = []
    for q in d["questions"]:
        n = count(q["answer"])
        paras = "".join(f"<p>{inline(p)}</p>" for p in q["answer"].split("\n\n") if p.strip())
        qs.append(f'''<div class="q">
<div class="qhead"><span class="qid">{e(q["id"])}</span><p class="qtext">{e(q["question"]) or "문항 확인 필요"}</p></div>
<h4 contenteditable="true" spellcheck="false">[{e(q["sub"])}]</h4>
<div class="ans" contenteditable="true" spellcheck="false" data-limit="{q["limit"]}">{paras}</div>
<div class="qfoot"><div class="meter"><i style="width:{min(100, n * 100 // max(q["limit"], 1))}%"></i></div>
<span class="cnt"><b>{n:,}</b> / {q["limit"]:,}자</span><span class="state"></span>
<button type="button" class="save" hidden>답변 저장</button><button type="button" class="copy">답변 복사</button></div></div>''')
    def ana(a):
        # 신입 연봉 줄은 채용현황 브리핑 값으로 통일하고, 초안 조사 내용은 굵게 하지 않고 참고로만 남긴다
        if d.get("pay") and a.startswith("신입 연봉:"):
            rest = a[len("신입 연봉:"):].replace("**", "").strip()
            return (f'신입 연봉: <b>{e(d["pay"])}</b> (채용현황 브리핑 기준)'
                    + (f' / 초안 조사 참고(브리핑 값과 다를 수 있음): {inline(rest)}' if rest else ""))
        return inline(a)
    analysis = "".join(f"<li>{ana(a)}</li>" for a in d["analysis"]) or "<li>기업 분석 없음</li>"
    overview = "".join(f"<li>{inline(a)}</li>" for a in m.get("overview", []))
    overview = f'<h3>기업 개요</h3><ul class="{analysis_cls}">{overview}</ul>\n' if overview else ""
    return f'''<div class="ref"><table class="kv"><tbody>
<tr><th>공고</th><td><a href="{e(m.get("url", ""))}" target="_blank" rel="noopener">공고 원문 열기</a></td></tr>
<tr><th>마감 · 작성</th><td class="num">{e(m.get("deadline", ""))} 마감 · {e(m.get("written", ""))} 작성</td></tr>
<tr><th>문항 출처</th><td>{e(m.get("questions", "-"))}</td></tr>{f'<tr><th>연봉 · 초봉</th><td>{e(d["pay"])} <span class="hint">(채용현황 브리핑 기준)</span></td></tr>' if d.get("pay") else ""}
</tbody></table>
{overview}<h3>기업 분석</h3><ul class="{analysis_cls}">{analysis}</ul></div>
{"".join(qs)}'''


def render_letter(d, today):
    """공고 하나의 독립 HTML 문서(A4 세로, 편집·인쇄·저장 가능)."""
    m = d["meta"]
    title = f"{m.get('company', '')} 자기소개서"
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
{STYLE}
</head>
<body>
<div class="sheet">
<header><div><div class="eyebrow">{e(m.get("title", ""))}</div><h1 contenteditable="true" spellcheck="false">{e(title)}</h1>
<div class="chips">{chips_of(m)}{dpill(d["left"])}</div></div>
<div class="doc-actions"><button type="button" class="copy-all btn-ghost">전체 답변 복사</button><button type="button" class="print btn-ghost">인쇄 · PDF</button></div></header>
<p class="hint">제목·소제목·답변을 눌러 바로 고칠 수 있습니다. 고친 뒤 브라우저의 '다른 이름으로 저장'(Ctrl+S)으로 HTML 파일을 저장하면 수정 내용이 그대로 남습니다. 인쇄할 때는 공고 정보·기업 개요·기업 분석과 버튼이 빠지고 문항과 답변만 A4에 나옵니다.</p>
{draft_body(d)}
<footer>작성 {e(m.get("written", ""))} · 글자수는 줄바꿈 제외·공백 포함 기준입니다. 제출 전 공고 원문 문항·글자수와 대조하세요.</footer>
</div>
{SCRIPT}
<script>
document.querySelector("button.print").addEventListener("click",function(){{window.print()}});
document.querySelector("button.copy-all").addEventListener("click",function(){{
 var b=this,t=Array.from(document.querySelectorAll(".q")).map(function(q){{return q.querySelector(".qid").innerText+" "+q.querySelector(".qtext").innerText+"\\n"+q.querySelector("h4").innerText+"\\n"+q.querySelector(".ans").innerText.trim()}}).join("\\n\\n");
 try{{navigator.clipboard.writeText(t).then(function(){{b.textContent="복사됨"}},function(){{b.textContent="복사 실패"}})}}catch(x){{b.textContent="복사 실패"}}
}});
</script>
</body>
</html>
'''


EMP_RE = re.compile(r"정규직|계약직|인턴|파견직?|위촉직|프리랜서")


def employment_of(m, posting=None):
    """고용형태: 초안 머리말 employment → 브리핑 공고 employment → 태그 순."""
    for v in (m.get("employment", ""), (posting or {}).get("employment", "")):
        if v.strip() and v.strip() != "기타/미표기":
            return v.strip()
    hit = EMP_RE.search(m.get("tags", ""))
    return hit.group(0) if hit else "미표기"


def company_keys(name):
    """업체명 비교 키: (주)·㈜·주식회사·공백을 빼고, 괄호 속 별칭(예: S-OIL)도 키로 쓴다."""
    n = re.sub(r"\(주\)|㈜|주식회사|\s", "", name or "")
    keys = {re.sub(r"\(.*?\)", "", n)} | set(re.findall(r"\((.*?)\)", n))
    return {k.lower().replace("-", "") for k in keys if k}


def load_postings(paths):
    """채용 브리핑 latest.json 들 → {"url": url → 공고, "starter": 업체 키 → 신입 초봉}."""
    by_url, starter = {}, {}
    for p in paths or []:
        try:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            print(f"[skip] 브리핑 {p} 읽기 실패", file=sys.stderr)
            continue
        for x in data.get("postings", []) if isinstance(data, dict) else []:
            st = ((x.get("extra") or {}).get("starter") or "").strip()
            if x.get("url") and (x["url"] not in by_url or st):
                by_url[x["url"]] = x
            if st:
                for k in company_keys(x.get("company", "")):
                    starter.setdefault(k, st)
    return {"url": by_url, "starter": starter}


def pay_of(m, postings):
    """표시용 급여: 공고 기재 연봉 · 신입 초봉. 신입 초봉은 채용현황 브리핑(collect.py extra.starter) 값으로만
    통일한다 — 같은 공고(url)의 값, 없으면 같은 업체의 다른 공고 값, 그래도 없으면 '확인 못 함'."""
    pst = postings["url"].get(m.get("url", ""))
    ex = (pst or {}).get("extra") or {}
    pay = (ex.get("salary") or ("연봉 미기재" if pst else "")).strip()
    # 초안 머리말 starter: 는 사용자가 확인해 정한 값이라 브리핑보다 우선한다
    starter = (m.get("starter") or "").strip() or (ex.get("starter") or "").strip() or next(
        (postings["starter"][k] for k in company_keys(m.get("company", "")) if k in postings["starter"]), "")
    return " · ".join(x for x in (pay, starter or "신입 초봉 확인 못 함") if x)


def foreign_section(foreign, excluded, postings):
    """외국계 공고 목록 — 자동 작성하지 않고 '작성 요청' 단추로 요청한 공고만 다음 루틴에서 쓴다."""
    rows = []
    for f in foreign or []:
        if f.get("id") in excluded:
            continue
        m = {"company": f.get("company", ""), "url": f.get("url", ""), "title": f.get("title", "")}
        pst = postings["url"].get(m["url"])
        emp = (pst or {}).get("employment") or "정규직"
        chips = "".join(f'<span class="chip">{e(x)}</span>' for x in f.get("tags", []))
        chips += f'<div class="emp"><span class="pill {"ok" if emp.startswith("정규직") else "mute"}">{e(emp)}</span></div>'
        pay = pay_of(m, postings)
        title = (f'<a class="jd" href="{e(m["url"])}" target="_blank" rel="noopener" title="공고 원문 열기">{e(m["title"])}</a>'
                 + (f'<div class="pay">{e(pay)}</div>' if pay else ""))
        rows.append(f'<tr data-id="{e(f["id"])}"><td>{e(m["company"])}</td><td>{chips}</td><td class="wrap">{title}</td>'
                    f'<td class="num">{e(f.get("deadline_date", ""))}</td><td>{dpill(f.get("days_left"))}</td>'
                    f'<td class="reqcell"><button type="button" class="req" data-id="{e(f["id"])}" data-company="{e(m["company"])}" '
                    f'data-title="{e(m["title"])}" data-url="{e(m["url"])}" disabled>작성 요청</button></td></tr>')
    if not rows:
        return ""
    return ('<section class="card" id="foreign"><h2>외국계 공고 · 요청 시 작성</h2>'
            '<p class="hint" id="reqmsg">외국계 공고는 자동으로 쓰지 않고 목록만 보여 줍니다. <b>작성 요청</b>을 누르면 다음 20:30 리포트에서 초안을 씁니다(마감 5일 전이 아니어도 씀).</p>'
            '<div class="scroll"><table><colgroup><col style="width:17%"><col style="width:14%"><col><col style="width:12%"><col style="width:9%"><col style="width:16%"></colgroup>'
            '<thead><tr><th>업체</th><th>구분</th><th>공고</th><th>마감일</th><th>남은 기간</th><th>작성</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table></div></section>")


def render(drafts, today, now, excluded=(), postings=None, foreign=None):
    postings = postings or {"url": {}, "starter": {}}
    live = [d for d in drafts if (d["left"] is None or d["left"] >= 0) and d["id"] not in excluded]
    new = [d for d in live if d["meta"].get("written") == today.isoformat()]
    live.sort(key=lambda d: (d["left"] if d["left"] is not None else 999, d["meta"].get("company", "")))
    near = min((d["left"] for d in live if d["left"] is not None), default=None)
    tiles = [("오늘 새 초안", len(new), "건"), ("마감 전 초안", len(live), "건"),
             ("가장 가까운 마감", "-" if near is None else ("오늘" if near == 0 else f"D-{near}"), ""),
             ("누적 초안", len(drafts), "건")]
    tiles_html = "".join(f'<div class="tile"><span class="lbl">{e(l)}</span><span class="num">{e(str(v))}<small>{u}</small></span></div>' for l, v, u in tiles)

    rows = []
    for d in live:
        m = d["meta"]
        pst = postings["url"].get(m.get("url", ""))
        emp = employment_of(m, pst)
        chips = "".join(f'<span class="chip">{e(t.strip())}</span>' for t in m.get("tags", "").split(",")
                        if t.strip() and not EMP_RE.fullmatch(t.strip()))
        ecls = "ok" if emp.startswith("정규직") else "warn" if "계약" in emp else "mute"
        chips += f'<div class="emp"><span class="pill {ecls}">{e(emp)}</span></div>'
        pay = d.get("pay") or pay_of(m, postings)
        url = m.get("url", "")
        title_html = ((f'<a class="jd" href="{e(url)}" target="_blank" rel="noopener" title="공고 원문 열기">{e(m.get("title", ""))}</a>'
                       if url.startswith("http") else e(m.get("title", ""))) + (f'<div class="pay">{e(pay)}</div>' if pay else ""))
        badge = '<span class="pill new">NEW</span> ' if d in new else ""
        rows.append(f'<tr data-id="{d["id"]}"><td class="pickcell"><input type="checkbox" class="pick" data-id="{d["id"]}" '
                    f'data-company="{e(m.get("company", ""))}" data-title="{e(m.get("title", ""))}" data-url="{e(m.get("url", ""))}" '
                    f'aria-label="{e(m.get("company", ""))} 선택"></td><td>{badge}<a href="#{d["id"]}">{e(m.get("company", ""))}</a></td><td>{chips}</td>'
                    f'<td class="wrap">{title_html}</td><td class="num">{e(m.get("deadline", ""))}</td>'
                    f'<td>{dpill(d["left"])}</td><td class="num">{len(d["questions"])}문항</td></tr>')
    table = (EXCLUDE_BAR + '<div class="scroll"><table><colgroup><col style="width:36px"><col style="width:19%"><col style="width:15%"><col><col style="width:14%">'
             '<col style="width:10%"><col style="width:9%"></colgroup><thead><tr><th class="pickcell"><input type="checkbox" class="pickall" aria-label="전체 선택"></th><th>업체</th><th>구분</th><th>공고</th>'
             '<th>마감일</th><th>남은 기간</th><th>문항</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>"
             if rows else '<p class="empty">마감 전 초안이 없습니다. 관심 기업 정규직 공고가 마감 5일 전이 되면 여기에 초안이 추가됩니다.</p>')

    cards = []
    for d in live:
        m = d["meta"]
        open_attr = " open" if d in new or len(live) <= 3 else ""
        cards.append(f'''<details class="draft" id="{d["id"]}"{open_attr}>
<summary><span class="co">{e(m.get("company", ""))}</span>{chips_of(m)}{dpill(d["left"])}<span class="ttl">{e(m.get("title", ""))}</span></summary>
<div class="body">
<div class="doc-actions" style="margin-top:12px"><a class="btn-ghost" href="letters/{d["id"]}.html" target="_blank" rel="noopener">편집용 HTML 열기</a></div>
{draft_body(d)}
</div></details>''')

    return PAGE.format(style=STYLE, script=SCRIPT + SAVE_SCRIPT + EXCLUDE_SCRIPT + REQUEST_SCRIPT, foreign=foreign_section(foreign, excluded, postings), date=f"{today:%Y-%m-%d}", weekday="월화수목금토일"[today.weekday()], gen=f"{now:%Y-%m-%d %H:%M}",
                       tiles=tiles_html, table=table, cards="".join(cards) or "")


STYLE = r"""<style>
/* 레이아웃: A4 세로 폭 한 장 — 요약 타일 → 마감순 표 → 공고별 초안(펼침, 문항 카드 편집) */
:root{
 --primary:#0F6FFF;--primary-hover:#0E65E8;--canvas:#EEF1F5;--surface:#FFFFFF;--alt1:#F2F3F6;--alt2:#E2E4E9;
 --strong:#000000;--text:#1C1C1C;--sub:#303030;--cap:#737373;--border:#E2E4E9;--border-strong:#CCD0D6;--divider:#E9EBEF;
 --ok:#15B874;--warn:#FFA833;--err:#E63B3B;--ok-bg:#E5F7EF;--warn-bg:#FFF3E0;--err-bg:#FDEBEB;--pri-bg:#E7F0FF;
 --font:"Pretendard Variable","Pretendard","Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic","Segoe UI",Roboto,sans-serif;
 --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
 --primary:#3F8CFF;--primary-hover:#0F6FFF;--canvas:#15171C;--surface:#1D1F24;--alt1:#282B33;--alt2:#333741;
 --strong:#FFFFFF;--text:#EBECED;--sub:#C4C4C4;--cap:#8A8A8A;--border:#333741;--border-strong:#4A505F;--divider:#282B33;
 --ok:#44C690;--warn:#FFB95C;--err:#EB5E5E;--ok-bg:#16332A;--warn-bg:#3A2E1A;--err-bg:#3A1F22;--pri-bg:#1A2B47;color-scheme:dark}}
:root[data-theme="dark"]{
 --primary:#3F8CFF;--primary-hover:#0F6FFF;--canvas:#15171C;--surface:#1D1F24;--alt1:#282B33;--alt2:#333741;
 --strong:#FFFFFF;--text:#EBECED;--sub:#C4C4C4;--cap:#8A8A8A;--border:#333741;--border-strong:#4A505F;--divider:#282B33;
 --ok:#44C690;--warn:#FFB95C;--err:#EB5E5E;--ok-bg:#16332A;--warn-bg:#3A2E1A;--err-bg:#3A1F22;--pri-bg:#1A2B47;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--canvas);color:var(--text);font-family:var(--font);font-size:15px;line-height:1.65;padding-inline:16px;padding-block:24px 48px}
.sheet{max-width:210mm;margin:0 auto;display:flex;flex-direction:column;gap:20px}
a{color:var(--primary)} a:focus-visible,button:focus-visible,summary:focus-visible,[contenteditable]:focus-visible{outline:2px solid var(--primary);outline-offset:2px}
header{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:8px 16px;border-bottom:2px solid var(--strong);padding-bottom:12px}
.eyebrow{font-size:12px;font-weight:600;letter-spacing:.08em;color:var(--primary)}
h1{font-size:28px;font-weight:700;color:var(--strong);margin:2px 0 0;text-wrap:balance}
.gen{font-size:12px;color:var(--cap);font-variant-numeric:tabular-nums}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.tile{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:2px}
.tile .lbl{font-size:12px;font-weight:600;color:var(--cap)}
.tile .num{font-size:28px;font-weight:700;color:var(--strong);font-variant-numeric:tabular-nums;line-height:1.2}
.tile small{font-size:13px;font-weight:600;color:var(--sub);margin-left:2px}
section.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px}
h2{font-size:18px;font-weight:700;color:var(--strong);margin:0 0 10px}
h3{font-size:14px;font-weight:700;color:var(--strong);margin:14px 0 6px}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:13px}
th,td{text-align:left;padding:8px;border-bottom:1px solid var(--divider);vertical-align:top;overflow-wrap:anywhere}
thead th{font-size:12px;font-weight:600;color:var(--cap);background:var(--alt1)}
.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.scroll table{min-width:640px}
.pill,.chip{display:inline-block;font-size:11px;font-weight:600;border-radius:9999px;padding:1px 8px;margin:1px 4px 1px 0;white-space:nowrap}
.chip{background:var(--alt1);color:var(--sub);border:1px solid var(--border)}
.pill{background:var(--alt1);color:var(--sub)} .pill.ok{background:var(--ok-bg);color:var(--ok)} .pill.warn{background:var(--warn-bg);color:var(--warn)}
.pill.err{background:var(--err-bg);color:var(--err)} .pill.new{background:var(--primary);color:var(--surface)} .pill.mute{color:var(--cap)}
.empty{color:var(--cap);margin:0}
.rules{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:0;padding:0;list-style:none;font-size:13px}
.rules li{background:var(--alt1);border-radius:8px;padding:8px 10px;color:var(--sub)} .rules b{color:var(--strong)}
.draft{background:var(--surface);border:1px solid var(--border);border-radius:12px}
.draft summary{cursor:pointer;padding:14px 16px;display:flex;flex-wrap:wrap;align-items:center;gap:4px 6px;list-style:none}
.draft summary::-webkit-details-marker{display:none}
.draft summary::before{content:"";width:8px;height:8px;border-right:2px solid var(--cap);border-bottom:2px solid var(--cap);transform:rotate(-45deg);margin-right:6px;transition:transform .15s}
.draft[open] summary::before{transform:rotate(45deg)}
.co{font-size:18px;font-weight:700;color:var(--strong);margin-right:4px}
.ttl{flex-basis:100%;font-size:13px;color:var(--sub);padding-left:20px}
.draft .body{padding:0 16px 16px;border-top:1px solid var(--divider)}
.kv{margin-top:12px} .kv th{width:120px;font-size:12px;color:var(--cap);font-weight:600;background:var(--alt1)}
.facts{margin:0;padding-left:18px;font-size:13px;color:var(--sub);display:flex;flex-direction:column;gap:4px}
.q{margin-top:16px;border:1px solid var(--border);border-radius:12px;overflow:hidden}
.qhead{display:flex;gap:10px;align-items:flex-start;background:var(--alt1);padding:10px 12px}
.qid{font-size:12px;font-weight:700;color:var(--surface);background:var(--primary);border-radius:8px;padding:2px 8px;flex:none}
.qtext{margin:0;font-size:13px;font-weight:600;color:var(--sub);min-width:0}
.q h4{margin:12px 14px 4px;font-size:16px;font-weight:700;color:var(--strong)}
.ans{padding:4px 14px 8px;font-size:15px;color:var(--text);max-width:68ch}
.ans p{margin:0 0 10px}
.qfoot{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;padding:10px 14px;border-top:1px solid var(--divider)}
.meter{flex:1 1 120px;height:6px;background:var(--alt2);border-radius:9999px;overflow:hidden}
.meter i{display:block;height:100%;background:var(--primary)}
.q.over .meter i{background:var(--err)} .q.low .meter i{background:var(--warn)}
.cnt{font-size:13px;color:var(--cap);font-variant-numeric:tabular-nums} .cnt b{color:var(--strong)}
.state{font-size:12px;font-weight:600} .q.ok .state{color:var(--ok)} .q.over .state{color:var(--err)} .q.low .state{color:var(--warn)}
button.copy{font:600 13px var(--font);color:var(--surface);background:var(--primary);border:0;border-radius:8px;padding:7px 14px;cursor:pointer;min-height:36px}
button.copy:hover{background:var(--primary-hover)}
button.save{font:600 13px var(--font);color:var(--primary);background:var(--surface);border:1px solid var(--border-strong);border-radius:8px;padding:7px 14px;cursor:pointer;min-height:36px}
button.save:hover{border-color:var(--primary)} button.save.clean{color:var(--ok)} button.save:disabled{opacity:.6;cursor:wait} button.save[hidden]{display:none}
footer{font-size:12px;color:var(--cap)}
@media (max-width:640px){.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}.rules{grid-template-columns:1fr}h1{font-size:24px}.kv th{width:88px}}
.doc-actions{display:flex;flex-wrap:wrap;gap:8px}
.doc-actions a,.doc-actions button{font:600 13px var(--font);border-radius:8px;padding:7px 14px;min-height:36px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center}
.btn-ghost{color:var(--primary);background:var(--surface);border:1px solid var(--border-strong)}
.hint{font-size:12px;color:var(--cap);margin:0}
.chips{margin-top:6px}
a.jd{color:var(--text);text-decoration:underline;text-decoration-color:var(--border-strong);text-underline-offset:3px} a.jd:hover{color:var(--primary);text-decoration-color:var(--primary)} a.jd::after{content:" ↗";font-size:11px;color:var(--cap)}
.emp{margin-top:4px} td .chip,.emp .pill{white-space:normal;max-width:100%} .pay{margin-top:4px;font-size:12px;color:var(--cap);font-variant-numeric:tabular-nums}
@media print{@page{size:A4 portrait;margin:14mm}body{background:#fff;padding:0}.ref,.doc-actions,button.copy,button.save,.state,.meter,.hint{display:none!important}
.q{break-inside:avoid;border-color:#ccc}.sheet{max-width:none}}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
.xbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:0 0 10px}
.xbar[hidden]{display:none}
.xbar button{font:600 13px var(--font);border-radius:8px;padding:6px 12px;min-height:34px;cursor:pointer;border:1px solid var(--border-strong);background:var(--surface);color:var(--sub)}
.xbar button.danger{background:var(--err);border-color:var(--err);color:#fff}
.xbar button:disabled{opacity:.45;cursor:not-allowed}
.xbar .msg{font-size:12px;color:var(--cap)}
.pickcell{width:36px;text-align:center} .pickcell input{width:16px;height:16px;cursor:pointer;accent-color:var(--primary)}
.xlist{margin:8px 0 0;font-size:13px;color:var(--sub)} .xlist summary{cursor:pointer;color:var(--cap);font-size:12px}
.xlist ul{margin:6px 0 0;padding-left:18px} .xlist li{margin:2px 0} .xlist button{margin-left:6px;font:600 12px var(--font);border:1px solid var(--border-strong);background:var(--surface);color:var(--primary);border-radius:6px;padding:1px 8px;cursor:pointer}
tr.gone,.draft.gone{display:none}
button.req{font:600 12px var(--font);border-radius:8px;padding:6px 10px;min-height:32px;cursor:pointer;border:1px solid var(--primary);background:var(--surface);color:var(--primary);white-space:nowrap}
button.req.on{background:var(--primary);color:var(--surface)} button.req:disabled{opacity:.45;cursor:not-allowed}
@media print{#foreign{display:none!important}}
@media print{.xbar,.xlist,.pickcell{display:none!important}}
</style>"""

SCRIPT = r"""<script>
(function(){
 function len(t){return t.replace(/\n/g,"").length}
 function raw(e){return e.innerText||e.textContent||""}  // 접힌 <details> 안에서는 innerText 가 빈 문자열
 function text(el){return Array.from(el.querySelectorAll("p")).map(function(p){return raw(p).trim()}).filter(Boolean).join("\n\n")||raw(el).trim()}
 document.querySelectorAll(".q").forEach(function(q,i){
  var a=q.querySelector(".ans"),lim=+a.dataset.limit,key="cl:"+(q.closest(".draft")||{}).id+":"+i;
  try{var s=localStorage.getItem(key);if(s)a.innerHTML=s}catch(e){}
  function upd(){var n=len(text(a)),r=n/lim;q.querySelector(".cnt b").textContent=n.toLocaleString();
   q.querySelector(".meter i").style.width=Math.min(100,r*100)+"%";q.classList.remove("ok","low","over");
   var st=q.querySelector(".state");if(r>1){q.classList.add("over");st.textContent="초과 "+(n-lim)+"자"}else if(r>=.8){q.classList.add("ok");st.textContent="적정"}else{q.classList.add("low");st.textContent="부족"}}
  a.addEventListener("input",function(){upd();try{localStorage.setItem(key,a.innerHTML)}catch(e){}});upd();q._upd=upd;
  var dd=q.closest("details");if(dd)dd.addEventListener("toggle",function(){if(dd.open)upd()});
  var b=q.querySelector("button.copy");b.addEventListener("click",function(){var t=text(a);
   function done(){b.textContent="복사됨";setTimeout(function(){b.textContent="답변 복사"},1500)}
   function sel(){var r=document.createRange();r.selectNodeContents(a);var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent="선택됨 · Ctrl+C"}
   try{navigator.clipboard.writeText(t).then(done,sel)}catch(e){sel()}});
 });
})();
</script>"""

# 답변 저장은 아티팩트 db 의 answers 컬렉션(문서 id = 초안id_문항순번)에 둔다. 페이지를 열 때 저장본을
# 생성된 답변 위에 덮어 보여 주므로, 루틴이 페이지를 다시 만들어도 사용자가 고친 답변이 유지된다.
# 저장하지 않은 수정(localStorage)이 있으면 그것을 먼저 보여 주고 단추에 '저장 안 됨'을 표시한다.
SAVE_SCRIPT = r"""<script>
(async function(){
 if(!window.claude||!claude.use)return;
 var db=null;try{db=await claude.use("db")}catch(e){}
 if(!db)return;
 var col=db.collection("answers"),saved={};
 try{(await col.get()).docs.forEach(function(d){saved[d.id]=d.data()||{}})}catch(e){}
 function stamp(t){var d=new Date(t);if(isNaN(d))return"";function z(n){return(n<10?"0":"")+n}return(d.getMonth()+1)+"/"+d.getDate()+" "+z(d.getHours())+":"+z(d.getMinutes())}
 document.querySelectorAll("details.draft").forEach(function(dd){
  dd.querySelectorAll(".q").forEach(function(q,i){
   var a=q.querySelector(".ans"),h=q.querySelector("h4"),b=q.querySelector("button.save"),id=dd.id+"_"+i,key="cl:"+dd.id+":"+i,v=saved[id];
   if(!b)return;
   var local=null;try{local=localStorage.getItem(key)}catch(e){}
   function clean(t){b.classList.add("clean");b.textContent="저장됨"+(t?" · "+stamp(t):"");b.title="다시 고치면 '답변 저장'으로 바뀝니다"}
   function dirty(){b.classList.remove("clean");b.textContent="답변 저장";b.title="고친 답변을 이 페이지에 저장"}
   if(v&&v.html&&local==null){a.innerHTML=v.html;if(v.sub)h.innerHTML=v.sub;if(q._upd)q._upd();clean(v.at)}
   else if(local!=null){dirty();b.textContent="답변 저장 · 저장 안 됨"}
   else dirty();
   b.hidden=false;
   a.addEventListener("input",dirty);h.addEventListener("input",dirty);
   b.addEventListener("click",async function(){
    b.disabled=true;b.textContent="저장 중…";var at=new Date().toISOString();
    try{await col.doc(id).set({draft:dd.id,q:i,sub:h.innerHTML,html:a.innerHTML,at:at});
     try{localStorage.removeItem(key)}catch(e){}
     clean(at);
    }catch(e){b.classList.remove("clean");b.textContent="저장 실패 · 다시 시도";b.title=String(e&&(e.code||e.message)||"오류")}
    b.disabled=false;
   });
  });
 });
})();
</script>"""

EXCLUDE_BAR = ('<div class="xbar" hidden><button type="button" class="danger" id="xdel" disabled>선택 삭제</button>'
               '<span id="xask" hidden><button type="button" class="danger" id="xok">제외 확정</button> <button type="button" id="xno">취소</button></span>'
               '<span class="msg" id="xmsg">체크한 공고는 이 목록에서 빠지고 다음 리포트부터 제외됩니다.</span></div>'
               '<details class="xlist" id="xlist" hidden><summary>제외한 공고 <b id="xcnt">0</b>건 · 되돌리기</summary><ul id="xul"></ul></details>')

# 제외 목록은 아티팩트 db 의 excluded 컬렉션(문서 id = 초안 id)에 둔다. 매일 루틴이 이 컬렉션을 읽어
# drafts/excluded.json 으로 내려받고 cover_letters.py·cover_brief.py 에 --exclude 로 넘긴다.
EXCLUDE_SCRIPT = r"""<script>
(async function(){
 if(!window.claude||!claude.use)return;
 var db=null;try{db=await claude.use("db")}catch(e){}
 if(!db)return;
 var bar=document.querySelector(".xbar"),del=document.getElementById("xdel"),msg=document.getElementById("xmsg"),
     list=document.getElementById("xlist"),ul=document.getElementById("xul"),cnt=document.getElementById("xcnt"),
     all=document.querySelector(".pickall"),col=db.collection("excluded"),ask=document.getElementById("xask"),ok=document.getElementById("xok"),no=document.getElementById("xno"),hint=msg.textContent,pending=[];
 if(!bar)return; bar.hidden=false;
 function picks(){return Array.from(document.querySelectorAll("input.pick"))}
 function sync(){var n=picks().filter(function(c){return c.checked&&!c.closest("tr").classList.contains("gone")}).length;
  del.disabled=!n; del.textContent=n?"선택 삭제 ("+n+")":"선택 삭제"}
 document.addEventListener("change",function(ev){
  if(ev.target===all){picks().forEach(function(c){if(!c.closest("tr").classList.contains("gone"))c.checked=all.checked})}
  if(ev.target.classList&&(ev.target.classList.contains("pick")||ev.target===all))sync()});
 del.addEventListener("click",async function(){
  var sel=picks().filter(function(c){return c.checked&&!c.closest("tr").classList.contains("gone")});
  if(!sel.length)return;
  pending=sel;del.hidden=true;ask.hidden=false;
  msg.textContent=sel.length+"건을 다음 리포트부터 제외할까요?";
 });
 no.addEventListener("click",function(){pending=[];ask.hidden=true;del.hidden=false;msg.textContent=hint;sync()});
 ok.addEventListener("click",async function(){
  var sel=pending;pending=[];if(!sel.length)return;
  ok.disabled=no.disabled=true;msg.textContent="저장 중…";
  try{for(var i=0;i<sel.length;i++){var c=sel[i];
    await col.doc(c.dataset.id).set({company:c.dataset.company,title:c.dataset.title,url:c.dataset.url,at:new Date().toISOString()})}
   msg.textContent=sel.length+"건을 제외했습니다. 다음 리포트부터 나오지 않습니다.";
  }catch(e){msg.textContent="저장하지 못했습니다("+(e&&(e.code||e.message)||"오류")+"). 편집 권한이 있는 계정으로 열었는지 확인해 주세요."}
  ok.disabled=no.disabled=false;ask.hidden=true;del.hidden=false;sync();
 });
 col.onSnapshot(function(snap){
  var ids={};ul.textContent="";
  snap.docs.forEach(function(d){var v=d.data()||{};ids[d.id]=1;
   var li=document.createElement("li");li.textContent=(v.company||d.id)+" — "+(v.title||"");
   var b=document.createElement("button");b.type="button";b.textContent="되돌리기";
   b.addEventListener("click",async function(){b.disabled=true;try{await col.doc(d.id).delete()}catch(e){b.disabled=false}});
   li.appendChild(b);ul.appendChild(li)});
  document.querySelectorAll("tr[data-id]").forEach(function(tr){tr.classList.toggle("gone",!!ids[tr.dataset.id]);
   if(ids[tr.dataset.id]){var c=tr.querySelector("input.pick");if(c)c.checked=false}});
  document.querySelectorAll("details.draft").forEach(function(dd){dd.classList.toggle("gone",!!ids[dd.id])});
  var n=snap.docs.length;cnt.textContent=n;list.hidden=!n;sync();
 },function(){msg.textContent="제외 목록을 불러오지 못했습니다."});
})();
</script>"""

# 외국계 작성 요청은 아티팩트 db 의 requested 컬렉션(문서 id = 초안 id)에 둔다. 매일 루틴이 읽어
# cover_letters.py --requested 로 넘기면 그 공고만 초안을 쓴다. 요청 취소는 문서 삭제.
REQUEST_SCRIPT = r"""<script>
(async function(){
 var btns=Array.from(document.querySelectorAll("button.req"));
 if(!btns.length||!window.claude||!claude.use)return;
 var db=null;try{db=await claude.use("db")}catch(e){}
 if(!db)return;
 var col=db.collection("requested"),msg=document.getElementById("reqmsg"),hint=msg?msg.innerHTML:"",req={};
 function paint(){btns.forEach(function(b){var on=!!req[b.dataset.id];b.disabled=false;
  b.classList.toggle("on",on);b.textContent=on?"요청됨 · 취소":"작성 요청";
  b.setAttribute("aria-pressed",on?"true":"false")})}
 btns.forEach(function(b){b.addEventListener("click",async function(){
  var id=b.dataset.id;b.disabled=true;
  try{if(req[id]){await col.doc(id).delete()}
   else{await col.doc(id).set({company:b.dataset.company,title:b.dataset.title,url:b.dataset.url,at:new Date().toISOString()})}
   if(msg)msg.innerHTML=hint}
  catch(e){if(msg)msg.textContent="저장하지 못했습니다("+(e&&(e.code||e.message)||"오류")+"). 편집 권한이 있는 계정으로 열었는지 확인해 주세요.";b.disabled=false}
 })});
 col.onSnapshot(function(snap){req={};snap.docs.forEach(function(d){req[d.id]=1});paint()},
  function(){if(msg)msg.textContent="작성 요청 목록을 불러오지 못했습니다."});
})();
</script>"""

PAGE = """<title>자기소개서 일일 브리핑</title>
{style}
<div class="sheet">
<header><div><div class="eyebrow">안전관리자 · 정규직 · 마감 5일 전 자동 작성</div><h1>자기소개서 일일 브리핑</h1></div>
<div class="gen">{date} ({weekday}) · 생성 {gen} KST</div></header>
<div class="tiles">{tiles}</div>
<section class="card"><h2>마감순 초안</h2>{table}</section>
{foreign}
<section class="card"><h2>제출 전 확인</h2><ul class="rules">
<li><b>문항·글자수</b> 공고 원문과 대조 (추정 문항이면 교체)</li>
<li><b>수상 표현 금지</b> 논문은 '제출'까지만</li>
<li><b>자격</b> 산업안전기사·ISO45001·NEBOSH는 '취득 준비 중'</li>
<li><b>필수 포함</b> AI 교육 5건 · 해외 안전 교육 15건</li>
<li><b>웹사이트</b> e-safety.vercel.app 표기</li>
<li><b>기업 개요·분석</b> DART 사업보고서 · 최근 1년 안전·AI 기사(없으면 주요 기사)</li>
</ul></section>
{cards}
<footer>답변은 바로 고칠 수 있고, 글자수(줄바꿈 제외·공백 포함)는 입력하면서 다시 셉니다. 고친 뒤 '답변 저장'을 누르면 이 페이지에 저장돼 다른 기기와 다음 리포트에서도 그대로 보입니다(누르기 전에는 이 브라우저에만 임시로 남음).</footer>
</div>
{script}
"""


def load_json_list(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8")) if path else []
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def load_excluded(path):
    """제외 목록 JSON → 초안 id 집합. 파일이 없거나 깨졌으면 빈 집합."""
    if not path:
        return set()
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    if isinstance(data, dict):
        data = data.get("excluded") or data.get("docs") or list(data.values())
    out = set()
    for x in data or []:
        if isinstance(x, str):
            out.add(x)
        elif isinstance(x, dict) and (x.get("id") or x.get("doc_id")):
            out.add(x.get("id") or x.get("doc_id"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drafts", default="drafts")
    ap.add_argument("--out", default="index.html")
    ap.add_argument("--today")
    ap.add_argument("--foreign", help="외국계 공고 목록 JSON(cover_letters.py --foreign-out) — 요청 시 작성 표")
    ap.add_argument("--briefing", action="append", help="채용 브리핑 latest.json(초봉·고용형태 조회용, 여러 번 가능)")
    ap.add_argument("--exclude", help="제외 목록 JSON(아티팩트 db excluded 컬렉션을 내려받은 것: id 목록 또는 {id,...} 목록)")
    args = ap.parse_args()
    now = dt.datetime.now(KST)
    today = dt.date.fromisoformat(args.today) if args.today else now.date()
    root = Path(args.drafts)
    try:
        index = json.loads((root / "index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        index = []
    drafts = []
    for item in index:
        f = root / Path(item["file"]).name
        if not f.exists():
            print(f"[skip] {f} 없음", file=sys.stderr)
            continue
        meta, analysis, questions = parse_draft(f.read_text(encoding="utf-8"))
        drafts.append({"id": Path(item["file"]).stem.split("_")[-1], "meta": meta, "analysis": analysis,
                       "questions": questions, "left": d_left(meta.get("deadline", ""), today)})
    excluded = load_excluded(args.exclude)
    postings = load_postings(args.briefing)
    for d in drafts:
        d["pay"] = pay_of(d["meta"], postings)
    Path(args.out).write_text(render(drafts, today, now, excluded, postings, load_json_list(args.foreign)), encoding="utf-8")
    letters = Path(args.out).parent / "letters"
    letters.mkdir(exist_ok=True)
    for d in drafts:
        (letters / f"{d['id']}.html").write_text(render_letter(d, today), encoding="utf-8")
    shown = sum(1 for d in drafts if d["id"] not in excluded)
    print(f"{args.out}: 초안 {len(drafts)}건(제외 {len(drafts) - shown}건), letters/*.html {len(drafts)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
