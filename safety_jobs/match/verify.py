# -*- coding: utf-8 -*-
"""빌드 결과 검증: 직접 채점 행마다 회사명·gap 문구가 같은 행에 있는지, 같은 URL이 두 번 채점되지 않았는지 확인한다. 불일치가 있으면 종료 코드 1."""
import json, os, re, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mlib, corp_rule
P = json.load(open(os.environ.get("MAIN_JSON", HERE + "/latest_main.json"), encoding="utf-8"))["postings"]
J = json.load(open(HERE + "/scores.json", encoding="utf-8"))
S, THIN, SKIP, NAME, DRAFT = mlib.load_scores(P)
bad = 0
for u in set(J["S"]) & (set(J["THIN"]) | set(J["SKIP"])):
    print("중복 채점(S와 THIN/SKIP 동시):", u); bad += 1
H = open(HERE + "/matching_briefing.html", encoding="utf-8").read()
byurl = {}
for u, b in re.findall(r'<tr[^>]*data-url="([^"]+)"[^>]*>(.*?)</tr>', H, re.S):
    byurl.setdefault(html.unescape(u), []).append(html.unescape(re.sub(r"<[^>]+>", " ", b)))
ok = 0
for i in sorted(S):
    p = P[i]; dd = mlib.dday(p)[1]
    if corp_rule.drop_reason(p) or (dd is not None and dd < 0): continue
    rows = byurl.get(p["url"])
    if not rows: print("행 없음:", p["company"], p["title"][:30]); bad += 1; continue
    t = re.sub(r"\s+", "", rows[0]); nm = re.sub(r"\(주\)|㈜|\s", "", NAME.get(i, p["company"]))[:4]; g = re.sub(r"\s", "", S[i]["gap"])[:12]
    if nm in t and g in t: ok += 1
    else: print("불일치:", p["company"], "회사명", nm in t, "gap", g in t); bad += 1
print(f"검증 통과 {ok}건, 문제 {bad}건")
sys.exit(1 if bad else 0)
