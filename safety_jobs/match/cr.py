# -*- coding: utf-8 -*-
"""기업분석 카드 생성. 카드 내용은 cr_cards.json(데이터)에서 읽고, 연결된 공고가 수집본에 없거나 마감이면 카드를 싣지 않는다."""
import html, os, json, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mlib
e = lambda s: html.escape(s, quote=True)
MAIN = json.load(open(os.environ.get("MAIN_JSON", HERE + "/latest_main.json"), encoding="utf-8"))["postings"]
J = json.load(open(HERE + "/cr_cards.json", encoding="utf-8"))
CR, SKIP_CR = J["cards"], set(J.get("skip", []))

def posting_of(c):
    a, b = c["find"]
    for p in MAIN:
        if a in p["company"] and b in p["title"]: return p

def card(c):
    f = "".join(f"<li>{x}</li>" for x in c["facts"])
    r = "".join(f"<li>{e(x)}</li>" for x in c["risks"])
    q = "".join(f"<li>{e(x)}</li>" for x in c["qs"])
    return f'''<article class="cr" id="{c["id"]}">
<div class="crh"><div><h3>{e(c["name"])}</h3><p class="crt">{e(c["title"])}</p></div>
<div class="crm"><span class="pill keep">{e(c["verdict"])}</span><span class="crs">{e(c["score"])}</span><span class="crs">접수 {e(c["due"])}</span></div></div>
<p class="crl">{e(c["lead"])}</p>
<div class="crc"><div><h4>확인된 사실</h4><ul>{f}</ul></div>
<div><h4>위험과 출처 미확보</h4><ul class="rk">{r}</ul><h4>보완 계획</h4><p class="crp">{e(c["todo"])}</p><h4>면접 예상 질문</h4><ol>{q}</ol></div></div></article>'''

LIVE = []
for x in CR:
    if x["id"] in SKIP_CR: continue
    p = posting_of(x)
    if not p: continue
    dl, dd = mlib.dday(p)
    if dd is not None and dd < 0: continue
    if dl:
        x["due"] = f'{dl[5:]}{" 10시" if x.get("due_suffix") else ""} · ' + ("오늘 마감" if dd == 0 else f"D-{dd}")
    else:
        x["due"] = "채용 시 마감"
    LIVE.append(x)
out = "".join(card(c) for c in LIVE)
open(HERE + "/cr_n.txt", "w").write(str(len(LIVE)))
open(HERE + "/cr.html", "w").write(out)
open(HERE + "/cr_ids.json", "w").write(json.dumps([{"id": x["id"], "find": x["find"], "short": x["short"]} for x in LIVE], ensure_ascii=False))
print(len(out))
