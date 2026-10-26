# -*- coding: utf-8 -*-
"""scores.json 에 없는(아직 채점 안 한) 공고를 보여 준다. 사용: python3 unscored.py [순번 ...]  (순번을 주면 본문까지 출력)"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mlib, corp_rule
P = json.load(open(os.environ.get("MAIN_JSON", HERE + "/latest_main.json"), encoding="utf-8"))["postings"]
J = json.load(open(HERE + "/scores.json", encoding="utf-8"))
known = set(J["S"]) | set(J["THIN"]) | set(J["SKIP"]) | set(J["ALIAS"])
if len(sys.argv) > 1:
    for j in map(int, sys.argv[1:]):
        p = P[j]; e = p.get("extra", {})
        t = re.sub(r"\s+", " ", p.get("detail_text") or p.get("listing_text") or "")
        print(f"=== [{j}] {p['company']} | {p['title']}\n  {p['employment']} {p['level']} | 마감 {p['deadline']} | {p['source']} | {p.get('company_type')} | groups {e.get('groups')} listed {e.get('listed')} 시평 {e.get('top100')}\n  자격: {(p.get('qualification') or '')[:300]}\n  우대: {(p.get('preferred') or '')[:300]}\n  본문({len(t)}자): {t[:1800]}\n  url: {p['url']}\n")
else:
    n = 0
    for j, p in enumerate(P):
        if p["url"] in known: continue
        why = corp_rule.drop_reason(p)
        if why: continue
        dl, dd = mlib.dday(p)
        if dd is not None and dd < 0: continue
        n += 1
        print(f"[{j}] {p['company'][:20]} | {p['title'][:50]} | {p['employment']} {p['level']} | 마감 {p['deadline']} | {p['source']}")
    print(f"-- 채점 필요 {n}건 (규칙·마감으로 이미 빠지는 공고는 제외)")
