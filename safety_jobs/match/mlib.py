# -*- coding: utf-8 -*-
"""jobstack job-search matching.md 가중치(필수40·우대20·경력20·산업/기업10·지역10)로 공고 채점.
지역 선호는 프로필에 없어 제외하고 나머지 90점을 100으로 환산한다. 채점 데이터는 scores.json(공고 URL 키)."""
import json, re, os, datetime
HERE = os.path.dirname(os.path.abspath(__file__))

def _today():
    t = os.environ.get("MATCH_TODAY")
    if t: return datetime.date.fromisoformat(t)
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date()  # KST
TODAY = _today()

def load_scores(P):
    """scores.json(URL 키)을 P(공고 목록)의 순번 키로 바꿔 돌려준다. ALIAS: {새 URL: 옛 URL} 재게시 공고 연결."""
    J = json.load(open(os.path.join(HERE, "scores.json"), encoding="utf-8"))
    alias = J.get("ALIAS", {})
    def pick(tbl, url):
        return tbl.get(url, tbl.get(alias.get(url, ""), None))
    S, THIN, SKIP, NAME, DRAFT = {}, {}, {}, {}, {}
    for i, p in enumerate(P):
        u = p["url"]
        s = pick(J["S"], u)
        if s is not None:
            s = dict(s)
            for k in ("req", "pref"):
                s[k] = [tuple(x) for x in s.get(k, [])]
            S[i] = s
        t = pick(J["THIN"], u)
        if t is not None: THIN[i] = t
        k = pick(J["SKIP"], u)
        if k is not None: SKIP[i] = k
        n = pick(J["NAME"], u)
        if n is not None: NAME[i] = n
        d = pick(J["DRAFT"], u)
        if d is not None: DRAFT[i] = tuple(d)
    return S, THIN, SKIP, NAME, DRAFT

def ind_value(p):
    e = p["extra"]
    h = p.get("hilite", "")
    base = {"A": 1.0, "B": 0.8, "F": 0.8}.get(h)
    if base is None:
        base = 0.6 if e.get("listed") else 0.4
    emp = p["employment"]
    ev = {"정규직": 1.0, "계약직": 0.4, "인턴": 0.8}.get(emp, 0.5)
    txt = p.get("detail_text") or ""
    if emp == "계약직" and re.search(r"정규직\s*전환\s*가능", txt):
        ev = 0.6
    return round((base + ev) / 2, 3)

def mean(items, after=False):
    vals = []
    for it in items:
        label, v, av = it
        if after and av is not None: v = av
        if v is None: continue
        vals.append(v)
    return (sum(vals) / len(vals)) if vals else None

def score(s, p, after=False):
    parts = [(40, mean(s["req"], after)), (20, mean(s["pref"], after)), (20, s["career"]), (10, ind_value(p))]
    num = sum(w * v for w, v in parts if v is not None)
    den = sum(w for w, v in parts if v is not None)
    return round(num / den * 100)

def grade(x):
    return "g" if x >= 80 else ("y" if x >= 60 else "r")

def judgment(g, sc):
    if g == "none": return "지원 권장" if sc >= 70 else "조건부 지원"
    if g == "cert": return "조건부 지원"
    return "신중 검토"

def dday(p):
    ds = p.get("deadline_date") or ""
    if ds:
        d = datetime.date.fromisoformat(ds)
        return ds, (d - TODAY).days
    m = re.search(r"(\d+)\.(\d+)", p.get("deadline") or "")
    if m and "마감" in (p.get("deadline") or "") and "채용 시" not in p["deadline"]:
        d = datetime.date(TODAY.year, int(m.group(1)), int(m.group(2)))
        if (TODAY - d).days > 180: d = datetime.date(TODAY.year + 1, d.month, d.day)  # 연말에 다음 해 마감을 볼 때
        return d.isoformat(), (d - TODAY).days
    return "", None

