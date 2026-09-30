# /// script
# requires-python = ">=3.10"
# ///
"""자기소개서 일일 브리핑 HTML 생성.

drafts/index.json 과 drafts/*.md 초안을 읽어 아티팩트용 index.html 을 만든다.
초안 md 형식은 아래와 같다(머리말 + 기업 분석 + 문항).

    ---
    company: 대한전선(주)
    title: 2027 신입사원 채용 (SHE)
    url: https://...
    deadline: 2026-10-11
    tags: 코스피
    written: 2026-10-01
    questions: 자소설닷컴 2026 하반기 문항        (문항 출처 또는 '추정 문항')
    ---
    ## 기업 분석
    - DART: ...
    - 최근 기사: [제목](URL) (YYYY-MM-DD)
    ## Q1 | 1000
    > 문항 원문
    **[소제목]**
    본문 문단...

    python3 safety_jobs/cover_brief.py --drafts drafts --out index.html [--today YYYY-MM-DD]
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


def render(drafts, today, now):
    live = [d for d in drafts if (d["left"] is None or d["left"] >= 0)]
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
        chips = "".join(f'<span class="chip">{e(t.strip())}</span>' for t in m.get("tags", "").split(",") if t.strip())
        badge = '<span class="pill new">NEW</span> ' if d in new else ""
        rows.append(f'<tr><td>{badge}<a href="#{d["id"]}">{e(m.get("company", ""))}</a></td><td>{chips}</td>'
                    f'<td class="wrap">{e(m.get("title", ""))}</td><td class="num">{e(m.get("deadline", ""))}</td>'
                    f'<td>{dpill(d["left"])}</td><td class="num">{len(d["questions"])}문항</td></tr>')
    table = ('<div class="scroll"><table><colgroup><col style="width:20%"><col style="width:16%"><col><col style="width:14%">'
             '<col style="width:10%"><col style="width:9%"></colgroup><thead><tr><th>업체</th><th>구분</th><th>공고</th>'
             '<th>마감일</th><th>남은 기간</th><th>문항</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>"
             if rows else '<p class="empty">마감 전 초안이 없습니다. 관심 기업 정규직 공고가 마감 10일 전이 되면 여기에 초안이 추가됩니다.</p>')

    cards = []
    for d in live:
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
<button type="button" class="copy">답변 복사</button></div></div>''')
        analysis = "".join(f"<li>{inline(a)}</li>" for a in d["analysis"]) or "<li>기업 분석 없음</li>"
        chips = "".join(f'<span class="chip">{e(t.strip())}</span>' for t in m.get("tags", "").split(",") if t.strip())
        open_attr = " open" if d in new or len(live) <= 3 else ""
        cards.append(f'''<details class="draft" id="{d["id"]}"{open_attr}>
<summary><span class="co">{e(m.get("company", ""))}</span>{chips}{dpill(d["left"])}<span class="ttl">{e(m.get("title", ""))}</span></summary>
<div class="body">
<table class="kv"><tbody>
<tr><th>공고</th><td><a href="{e(m.get("url", ""))}" target="_blank" rel="noopener">공고 원문 열기</a></td></tr>
<tr><th>마감 · 작성</th><td class="num">{e(m.get("deadline", ""))} 마감 · {e(m.get("written", ""))} 작성</td></tr>
<tr><th>문항 출처</th><td>{e(m.get("questions", "-"))}</td></tr>
</tbody></table>
<h3>기업 분석</h3><ul class="facts">{analysis}</ul>
{"".join(qs)}
</div></details>''')

    return PAGE.format(date=f"{today:%Y-%m-%d}", weekday="월화수목금토일"[today.weekday()], gen=f"{now:%Y-%m-%d %H:%M}",
                       tiles=tiles_html, table=table, cards="".join(cards) or "")


PAGE = """<title>자기소개서 일일 브리핑</title>
<style>
/* 레이아웃: A4 세로 폭 한 장 — 요약 타일 → 마감순 표 → 공고별 초안(펼침, 문항 카드 편집) */
:root{{
 --primary:#0F6FFF;--primary-hover:#0E65E8;--canvas:#EEF1F5;--surface:#FFFFFF;--alt1:#F2F3F6;--alt2:#E2E4E9;
 --strong:#000000;--text:#1C1C1C;--sub:#303030;--cap:#737373;--border:#E2E4E9;--border-strong:#CCD0D6;--divider:#E9EBEF;
 --ok:#15B874;--warn:#FFA833;--err:#E63B3B;--ok-bg:#E5F7EF;--warn-bg:#FFF3E0;--err-bg:#FDEBEB;--pri-bg:#E7F0FF;
 --font:"Pretendard Variable","Pretendard","Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic","Segoe UI",Roboto,sans-serif;
 --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
 --primary:#3F8CFF;--primary-hover:#0F6FFF;--canvas:#15171C;--surface:#1D1F24;--alt1:#282B33;--alt2:#333741;
 --strong:#FFFFFF;--text:#EBECED;--sub:#C4C4C4;--cap:#8A8A8A;--border:#333741;--border-strong:#4A505F;--divider:#282B33;
 --ok:#44C690;--warn:#FFB95C;--err:#EB5E5E;--ok-bg:#16332A;--warn-bg:#3A2E1A;--err-bg:#3A1F22;--pri-bg:#1A2B47;color-scheme:dark}}}}
:root[data-theme="dark"]{{
 --primary:#3F8CFF;--primary-hover:#0F6FFF;--canvas:#15171C;--surface:#1D1F24;--alt1:#282B33;--alt2:#333741;
 --strong:#FFFFFF;--text:#EBECED;--sub:#C4C4C4;--cap:#8A8A8A;--border:#333741;--border-strong:#4A505F;--divider:#282B33;
 --ok:#44C690;--warn:#FFB95C;--err:#EB5E5E;--ok-bg:#16332A;--warn-bg:#3A2E1A;--err-bg:#3A1F22;--pri-bg:#1A2B47;color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--canvas);color:var(--text);font-family:var(--font);font-size:15px;line-height:1.65;padding-inline:16px;padding-block:24px 48px}}
.sheet{{max-width:210mm;margin:0 auto;display:flex;flex-direction:column;gap:20px}}
a{{color:var(--primary)}} a:focus-visible,button:focus-visible,summary:focus-visible,[contenteditable]:focus-visible{{outline:2px solid var(--primary);outline-offset:2px}}
header{{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:8px 16px;border-bottom:2px solid var(--strong);padding-bottom:12px}}
.eyebrow{{font-size:12px;font-weight:600;letter-spacing:.08em;color:var(--primary)}}
h1{{font-size:28px;font-weight:700;color:var(--strong);margin:2px 0 0;text-wrap:balance}}
.gen{{font-size:12px;color:var(--cap);font-variant-numeric:tabular-nums}}
.tiles{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.tile{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:2px}}
.tile .lbl{{font-size:12px;font-weight:600;color:var(--cap)}}
.tile .num{{font-size:28px;font-weight:700;color:var(--strong);font-variant-numeric:tabular-nums;line-height:1.2}}
.tile small{{font-size:13px;font-weight:600;color:var(--sub);margin-left:2px}}
section.card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px}}
h2{{font-size:18px;font-weight:700;color:var(--strong);margin:0 0 10px}}
h3{{font-size:14px;font-weight:700;color:var(--strong);margin:14px 0 6px}}
.scroll{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;table-layout:fixed;font-size:13px}}
th,td{{text-align:left;padding:8px;border-bottom:1px solid var(--divider);vertical-align:top;overflow-wrap:anywhere}}
thead th{{font-size:12px;font-weight:600;color:var(--cap);background:var(--alt1)}}
.num{{font-variant-numeric:tabular-nums;white-space:nowrap}}
.scroll table{{min-width:640px}}
.pill,.chip{{display:inline-block;font-size:11px;font-weight:600;border-radius:9999px;padding:1px 8px;margin:1px 4px 1px 0;white-space:nowrap}}
.chip{{background:var(--alt1);color:var(--sub);border:1px solid var(--border)}}
.pill{{background:var(--alt1);color:var(--sub)}} .pill.ok{{background:var(--ok-bg);color:var(--ok)}} .pill.warn{{background:var(--warn-bg);color:var(--warn)}}
.pill.err{{background:var(--err-bg);color:var(--err)}} .pill.new{{background:var(--primary);color:var(--surface)}} .pill.mute{{color:var(--cap)}}
.empty{{color:var(--cap);margin:0}}
.rules{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:0;padding:0;list-style:none;font-size:13px}}
.rules li{{background:var(--alt1);border-radius:8px;padding:8px 10px;color:var(--sub)}} .rules b{{color:var(--strong)}}
.draft{{background:var(--surface);border:1px solid var(--border);border-radius:12px}}
.draft summary{{cursor:pointer;padding:14px 16px;display:flex;flex-wrap:wrap;align-items:center;gap:4px 6px;list-style:none}}
.draft summary::-webkit-details-marker{{display:none}}
.draft summary::before{{content:"";width:8px;height:8px;border-right:2px solid var(--cap);border-bottom:2px solid var(--cap);transform:rotate(-45deg);margin-right:6px;transition:transform .15s}}
.draft[open] summary::before{{transform:rotate(45deg)}}
.co{{font-size:18px;font-weight:700;color:var(--strong);margin-right:4px}}
.ttl{{flex-basis:100%;font-size:13px;color:var(--sub);padding-left:20px}}
.draft .body{{padding:0 16px 16px;border-top:1px solid var(--divider)}}
.kv{{margin-top:12px}} .kv th{{width:120px;font-size:12px;color:var(--cap);font-weight:600;background:var(--alt1)}}
.facts{{margin:0;padding-left:18px;font-size:13px;color:var(--sub);display:flex;flex-direction:column;gap:4px}}
.q{{margin-top:16px;border:1px solid var(--border);border-radius:12px;overflow:hidden}}
.qhead{{display:flex;gap:10px;align-items:flex-start;background:var(--alt1);padding:10px 12px}}
.qid{{font-size:12px;font-weight:700;color:var(--surface);background:var(--primary);border-radius:8px;padding:2px 8px;flex:none}}
.qtext{{margin:0;font-size:13px;font-weight:600;color:var(--sub);min-width:0}}
.q h4{{margin:12px 14px 4px;font-size:16px;font-weight:700;color:var(--strong)}}
.ans{{padding:4px 14px 8px;font-size:15px;color:var(--text);max-width:68ch}}
.ans p{{margin:0 0 10px}}
.qfoot{{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;padding:10px 14px;border-top:1px solid var(--divider)}}
.meter{{flex:1 1 120px;height:6px;background:var(--alt2);border-radius:9999px;overflow:hidden}}
.meter i{{display:block;height:100%;background:var(--primary)}}
.q.over .meter i{{background:var(--err)}} .q.low .meter i{{background:var(--warn)}}
.cnt{{font-size:13px;color:var(--cap);font-variant-numeric:tabular-nums}} .cnt b{{color:var(--strong)}}
.state{{font-size:12px;font-weight:600}} .q.ok .state{{color:var(--ok)}} .q.over .state{{color:var(--err)}} .q.low .state{{color:var(--warn)}}
button.copy{{font:600 13px var(--font);color:var(--surface);background:var(--primary);border:0;border-radius:8px;padding:7px 14px;cursor:pointer;min-height:36px}}
button.copy:hover{{background:var(--primary-hover)}}
footer{{font-size:12px;color:var(--cap)}}
@media (max-width:640px){{.tiles{{grid-template-columns:repeat(2,minmax(0,1fr))}}.rules{{grid-template-columns:1fr}}h1{{font-size:24px}}.kv th{{width:88px}}}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
</style>
<div class="sheet">
<header><div><div class="eyebrow">안전관리자 · 정규직 · 마감 10일 전 자동 작성</div><h1>자기소개서 일일 브리핑</h1></div>
<div class="gen">{date} ({weekday}) · 생성 {gen} KST</div></header>
<div class="tiles">{tiles}</div>
<section class="card"><h2>마감순 초안</h2>{table}</section>
<section class="card"><h2>제출 전 확인</h2><ul class="rules">
<li><b>문항·글자수</b> 공고 원문과 대조 (추정 문항이면 교체)</li>
<li><b>수상 표현 금지</b> 논문은 '제출'까지만</li>
<li><b>자격</b> 산업안전기사·ISO45001·NEBOSH는 '취득 준비 중'</li>
<li><b>필수 포함</b> AI 교육 5건 · 해외 안전 교육 15건</li>
<li><b>웹사이트</b> e-safety.vercel.app 표기</li>
<li><b>기업 분석</b> DART 사업보고서 · 최근 3개월 안전 기사</li>
</ul></section>
{cards}
<footer>답변은 바로 고칠 수 있고, 글자수(줄바꿈 제외·공백 포함)는 입력하면서 다시 셉니다. 고친 내용은 이 브라우저에만 남으니 제출 전 '답변 복사'로 옮겨 두세요.</footer>
</div>
<script>
(function(){{
 function len(t){{return t.replace(/\\n/g,"").length}}
 function text(el){{return Array.from(el.querySelectorAll("p")).map(function(p){{return p.innerText.trim()}}).filter(Boolean).join("\\n\\n")||el.innerText.trim()}}
 document.querySelectorAll(".q").forEach(function(q,i){{
  var a=q.querySelector(".ans"),lim=+a.dataset.limit,key="cl:"+(q.closest(".draft")||{{}}).id+":"+i;
  try{{var s=localStorage.getItem(key);if(s)a.innerHTML=s}}catch(e){{}}
  function upd(){{var n=len(text(a)),r=n/lim;q.querySelector(".cnt b").textContent=n.toLocaleString();
   q.querySelector(".meter i").style.width=Math.min(100,r*100)+"%";q.classList.remove("ok","low","over");
   var st=q.querySelector(".state");if(r>1){{q.classList.add("over");st.textContent="초과 "+(n-lim)+"자"}}else if(r>=.8){{q.classList.add("ok");st.textContent="적정"}}else{{q.classList.add("low");st.textContent="부족"}}}}
  a.addEventListener("input",function(){{upd();try{{localStorage.setItem(key,a.innerHTML)}}catch(e){{}}}});upd();
  var b=q.querySelector("button.copy");b.addEventListener("click",function(){{var t=text(a);
   function done(){{b.textContent="복사됨";setTimeout(function(){{b.textContent="답변 복사"}},1500)}}
   function sel(){{var r=document.createRange();r.selectNodeContents(a);var s=getSelection();s.removeAllRanges();s.addRange(r);b.textContent="선택됨 · Ctrl+C"}}
   try{{navigator.clipboard.writeText(t).then(done,sel)}}catch(e){{sel()}}}});
 }});
}})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drafts", default="drafts")
    ap.add_argument("--out", default="index.html")
    ap.add_argument("--today")
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
    Path(args.out).write_text(render(drafts, today, now), encoding="utf-8")
    print(f"{args.out}: 초안 {len(drafts)}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
