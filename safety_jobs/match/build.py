# -*- coding: utf-8 -*-
import json, html, datetime, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
MAIN_JSON = os.environ.get("MAIN_JSON", HERE + "/latest_main.json")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mlib import *
import mlib

SP = os.path.dirname(os.path.abspath(__file__)) + "/"
d = json.load(open(MAIN_JSON))
P = d["postings"]
S, THIN, SKIP, NAME, DRAFT = mlib.load_scores(P)
import corp_rule
RULE_DROPPED = {}
def _crid_of(p):
    try: live = json.load(open(SP + "cr_ids.json", encoding="utf-8"))
    except Exception: live = []
    for c in live:
        if c["find"][0] in p["company"] and c["find"][1] in p["title"]: return c["id"]
    return ""
for _i in list(S):
    _r = corp_rule.drop_reason(P[_i])
    if _r: RULE_DROPPED[_i] = _r; SKIP[_i] = _r; del S[_i]
for _i in list(THIN):
    _r = corp_rule.drop_reason(P[_i])
    if _r: RULE_DROPPED[_i] = _r; SKIP[_i] = _r; del THIN[_i]
for _i in list(S) + list(THIN):  # 접수 마감이 지난 공고는 분석 제외로 옮긴다
    _dl, _dd = dday(P[_i])
    if _dd is not None and _dd < 0:
        SKIP[_i] = f"접수 마감({_dl[5:]})"
        S.pop(_i, None); THIN.pop(_i, None)
e = lambda s: html.escape(str(s), quote=True)

CL_URL = "https://claude.ai/artifact/GEkympcXxpmb48ez87mY99"
BR_URL = "https://claude.ai/artifact/8vwqioKkr5ADyBJnbVDQZA"

rows = []
for i, s in S.items():
    p = P[i]
    now, aft = score(s, p), score(s, p, True)
    dl, dd = dday(p)
    rows.append(dict(i=i, p=p, s=s, now=now, aft=aft, g=s["gate"], dl=dl, dd=dd,
                     name=NAME.get(i, p["company"]), j=judgment(s["gate"], now if s["gate"] != "cert" else aft)))
by = {k: [r for r in rows if r["g"] == k] for k in ("none", "cert", "other", "exp", "env")}
now_ok = sorted(by["none"], key=lambda r: -r["now"])
cert_ok = sorted(by["cert"], key=lambda r: -r["aft"])
careful = sorted(by["other"] + by["env"] + by["exp"], key=lambda r: -r["now"])

def cls(x): return "ok" if x >= 80 else ("keep" if x >= 60 else "bad")
def gtxt(x): return "지원 추천" if x >= 80 else ("보완 후 가치" if x >= 60 else "신중 검토")

def emp_cell(p, s=None):
    sal = p["extra"].get("salary") or ""
    st = p["extra"].get("starter") or ""
    out = f'{e(p["employment"])}' + ('' if p["level"] == p["employment"] else f'<small>{e(p["level"])}</small>')
    if sal: out += f'<small class="sal">{e(sal)}</small>'
    if st:
        u = p["extra"].get("starter_url")
        out += f'<small class="sal"><a class="starter" href="{e(u)}" target="_blank" rel="noopener">{e(st)}</a></small>' if u else f'<small class="sal">{e(st)}</small>'
    return out

def dl_cell(r):
    if not r["dl"]: return '<td class="dl">채용 시 마감</td>'
    dd = r["dd"]
    soon = " soon" if dd is not None and dd <= 3 else ""
    tag = "D-DAY" if dd == 0 else f"D-{dd}"
    return f'<td class="dl{soon}">{e(r["dl"])}<small class="dd">{tag}</small></td>'

def chips(p):
    x = []
    for g in p["extra"].get("groups") or []: x.append(f'<span class="pill pb">{e(g)}</span>')
    if p["extra"].get("listed"): x.append(f'<span class="pill pk">{e(p["extra"]["listed"])} 상장</span>')
    return "".join(x)

def det(r):
    s = r["s"]
    def lis(items):
        sym = {1.0: "충족", 0.5: "부분", 0.0: "미충족", None: "확인 필요"}
        return "".join(f'<li class="m{"1" if v==1.0 else ("h" if v==0.5 else ("0" if v==0.0 else "n"))}"><b>{sym[v]}</b>{e(l)}</li>' for l, v, _ in items)
    out = f'<details class="why"><summary>항목별 채점 보기</summary><div class="two"><div><h4>필수 요건</h4><ul>{lis(s["req"])}</ul></div>'
    out += f'<div><h4>우대 사항</h4><ul>{lis(s["pref"]) if s["pref"] else "<li class=mn>공고에 우대 사항 없음 — 채점에서 제외</li>"}</ul></div></div></details>'
    return out

def prio_row(rank, r, mode):
    p, s = r["p"], r["s"]
    sc = r["now"]
    meter = f'<span class="mt"><i class="{cls(sc)}" style="width:{sc}%"></i></span>'
    if mode == "cert":
        sc_html = f'<span class="big {cls(r["aft"])}">{r["aft"]}<small>%</small></span><small class="sub">취득 후 · 현재 {r["now"]}%</small>'
        meter = f'<span class="mt two"><i class="{cls(r["now"])}" style="width:{r["now"]}%"></i><i class="gain" style="width:{max(r["aft"]-r["now"],0)}%"></i></span>'
    else:
        sc_html = f'<span class="big {cls(sc)}">{sc}<small>%</small></span><small class="sub">{gtxt(sc)}</small>'
    thin = " ".join(["<span class='pill pw'>요건 간략</span>" if len(s["req"]) <= 2 and not s["pref"] else ""])
    dr = DRAFT.get(r["i"])
    dr_html = f'<span class="pill {dr[0]}">{e(dr[1])}</span>' if dr else ""
    if _crid_of(r["p"]): dr_html += f' <a class="pill pai cl" href="#{_crid_of(r["p"])}">기업분석 보기</a>'
    return f'''<tr data-url="{e(p["url"])}"><td class="rk"><input type="checkbox" class="xsel" data-url="{e(p["url"])}" data-company="{e(r["name"])}" data-title="{e(p["title"])}" aria-label="{e(r["name"])} 선택">{rank}</td>
<td class="corp"><strong><a class="co" href="{e(p["url"])}" target="_blank" rel="noopener">{e(r["name"])}</a></strong>{chips(p)}
<a class="tl" href="{e(p["url"])}" target="_blank" rel="noopener">{e(p["title"])}</a><small class="src2">{e(p["source"])}</small></td>
<td class="scc">{sc_html}{meter}{thin}</td>
<td class="lv">{emp_cell(p)}</td>
<td class="why2"><p class="up"><b>강점</b>{e(s["up"])}</p><p class="gp"><b>GAP</b>{e(s["gap"])}</p><p class="td"><b>할 일</b>{e(s["todo"])}</p>{dr_html}{det(r)}</td>
{dl_cell(r)}</tr>'''

def table(rs, mode):
    head = '<th class="rkh"><input type="checkbox" class="pickall" aria-label="전체 선택">#</th><th>업체 · 공고</th><th>매칭도</th><th>고용형태 · 연봉</th><th>근거와 GAP</th><th>접수기한</th>'
    body = "".join(prio_row(k + 1, r, mode) for k, r in enumerate(rs))
    return f'<div class="scroll"><table class="tm"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

# ----- KPI / counts -----
n_all = len(P); n_score = len(rows); n_thin = len(THIN); n_skip = len(SKIP)
n_now = len(now_ok); n_cert = len(cert_ok)
soon = [r for r in rows if r["dd"] is not None and r["dd"] <= 3 and r["g"] != "exp"]
green_after = [r for r in rows if r["g"] == "cert" and r["aft"] >= 80]

def kpi(l, v, s, dot=None):
    d_ = f'<span class="dot" style="background:var(--{dot})"></span>' if dot else ""
    return f'<div class="kpi"><span class="l">{d_}{l}</span><span class="v">{v}</span><span class="s">{s}</span></div>'

_gen = d.get("generated_at", "")
try:
    _g = datetime.datetime.fromisoformat(_gen); WHEN = f"{_g.year}-{_g.month:02d}-{_g.day:02d} {_g.hour:02d}:{_g.minute:02d} KST"
except Exception:
    WHEN = _gen[:16]
_sk = {"마감": 0, "해외": 0, "기타": 0}
for _u, _w in SKIP.items():
    _sk["마감" if "마감" in _w and "채용" not in _w else ("해외" if _w.startswith("해외") else "기타")] += 1
_scope_n = len([1 for i in SKIP if i in RULE_DROPPED])
_skip_note = " · ".join(x for x in [f"마감 {_sk['마감']}건" if _sk["마감"] else "", f"해외 근무 {_sk['해외']}건" if _sk["해외"] else "", f"그 밖의 사유 {_sk['기타'] - _scope_n}건" if _sk["기타"] - _scope_n > 0 else "", f"건설·엔지니어링·회사명 기준 외 {len(RULE_DROPPED)}건" if RULE_DROPPED else ""] if x)
kpis = "".join([
    kpi("분석한 공고", n_all, f"{WHEN} 수집분 전체"),
    kpi("매칭도 산출", n_score, "자격·직무 요건 본문 확보", "primary"),
    kpi("지금 지원 가능", n_now, "자격증 없이 요건 충족", "success"),
    kpi("산업안전기사 취득 후", n_cert, "자격 하나로 지원 가능해지는 공고", "warning"),
    kpi("취득 후 80%+", len(green_after), "지원 추천 구간에 드는 공고", "success"),
    kpi("다른 자격·경력 필요", len(careful), "신중 검토 대상", "error"),
    kpi("3일 내 마감", len(soon), " · ".join(r["name"] for r in soon) or "해당 없음", "error"),
    kpi("근거 부족", n_thin, "요건 미기재·본문 없음", None),
    kpi("분석 제외", n_skip, _skip_note, None),
])

# ----- charts -----
def bars(items, colcls=""):
    mx = max(v for _, v, _ in items) or 1
    out = ""
    for k, v, c in items:
        out += f'<div class="bar"><span class="k">{e(k)}</span><span class="t"><span class="f {c}" style="width:{max(v/mx*100,2):.0f}%"></span></span><span class="v">{v}</span></div>'
    return f'<div class="bars">{out}</div>'

dist = [("80% 이상 · 지원 추천", len([r for r in rows if r["now"] >= 80]), ""),
        ("60~79% · 보완 후 가치", len([r for r in rows if 60 <= r["now"] < 80]), "keep"),
        ("60% 미만 · 신중 검토", len([r for r in rows if r["now"] < 60]), "warn")]
dist_aft = [("80% 이상 · 지원 추천", len([r for r in rows if (r["aft"] if r["g"] in ("cert",) else r["now"]) >= 80]), ""),
            ("60~79% · 보완 후 가치", len([r for r in rows if 60 <= (r["aft"] if r["g"] in ("cert",) else r["now"]) < 80]), "keep"),
            ("60% 미만 · 신중 검토", len([r for r in rows if (r["aft"] if r["g"] in ("cert",) else r["now"]) < 60]), "warn")]

gaps = [("산업안전기사 한 가지로 해소", len(by["cert"]), ""),
        ("자격 없이 지원 가능", len(by["none"]), "ok"),
        ("건설안전기사·위험물·소방설비 등 추가 자격", len(by["other"]), "keep"),
        ("경력 3년 이상 요구", len(by["exp"]), "warn"),
        ("환경 직무(대기환경기사)", len(by["env"]), "pp")]

gain = sorted(cert_ok, key=lambda r: -(r["aft"] - r["now"]))
gain_html = ""
for r in gain:
    gain_html += (f'<div class="bar"><span class="k">{e(r["name"])}</span><span class="t two"><span class="f" style="width:{r["now"]}%"></span>'
                  f'<span class="f gainf" style="width:{r["aft"]-r["now"]}%"></span></span><span class="v">{r["now"]}→{r["aft"]}</span></div>')

flow = [("수집 공고", n_all, ""), ("마감·해외·기준 외 제외", f"−{n_skip}", "minus"), ("근거 부족", f"−{n_thin}", "minus"),
        ("매칭도 산출", n_score, ""), ("자격 없이 지원 가능", n_now, "final")]
flow_html = ""
for k, (l, v, c) in enumerate(flow):
    if k: flow_html += '<span class="arrow" aria-hidden="true">→</span>'
    flow_html += f'<div class="step {c}"><span class="l">{l}</span><span class="v">{v}</span></div>'

# ----- calendar -----
cal_ev = {}
def add_ev(date, label, kind, url, title):
    cal_ev.setdefault(date, []).append((label, kind, url, title))
for r in rows:
    if r["dl"]:
        kind = "g" if r["g"] == "none" else ("b" if r["g"] == "cert" else "w")
        add_ev(r["dl"], r["name"], kind, r["p"]["url"], f'{r["name"]} · {r["p"]["title"]} · {r["dl"]}')
for i in THIN:
    p = P[i]; dl, dd = dday(p)
    if dl: add_ev(dl, p["company"], "n", p["url"], f'{p["company"]} · {p["title"]} · {dl} · 근거 부족')
start = datetime.date(2026, 10, 11)
cells = ""
wd = ["일", "월", "화", "수", "목", "금", "토"]
cells += "".join(f'<div class="wd{" sun" if k == 0 else ""}">{w}</div>' for k, w in enumerate(wd))
dates_all = sorted(cal_ev)
last = datetime.date.fromisoformat(dates_all[-1])
nweeks = ((last - start).days // 7) + 1
for k in range(nweeks * 7):
    dt = start + datetime.timedelta(days=k)
    iso = dt.isoformat(); evs = cal_ev.get(iso, [])
    c = ["day"]
    if dt < TODAY: c.append("past")
    if dt == TODAY: c.append("today")
    if 0 <= (dt - TODAY).days <= 3: c.append("soon")
    if dt.weekday() == 6: c.append("sun")
    if not evs: c.append("empty")
    lab = f'{dt.month}월 {dt.day}일' if (dt.day == 1 or k == 0) else f'{dt.day}일'
    h = f'<div class="dn"><span>{lab} <span class="wdn">({wd[(dt.weekday()+1)%7]})</span></span>' + (f'<span class="cnt">{len(evs)}건</span>' if evs else "") + '</div>'
    for lbl, kind, u, t in evs:
        h += f'<a class="ev k{kind}" href="{e(u)}" target="_blank" rel="noopener" title="{e(t)}"><span>{e(lbl)}</span></a>'
    cells += f'<div class="{" ".join(c)}">{h}</div>'
def short(n): return re.sub(r"\(주\)|㈜|\(유\)|\s", "", n)
_now_names = ", ".join(short(r["name"]) for r in now_ok[:5])
_cert80 = [r for r in sorted(cert_ok, key=lambda r: -r["aft"]) if r["aft"] >= 80]
_cert_names = ", ".join(short(r["name"]) for r in _cert80[:4])
LEAD_NOW = (f'<li><span class="tag ok">지금 지원</span><span>자격증 없이 낼 수 있는 공고는 <b>{n_now}건</b>입니다. {_now_names} 등이 해당합니다.</span></li>')
LEAD_CERT = (f'<li><span class="tag keep">기사 취득</span><span><b>산업안전기사 하나</b>로 {n_cert}건이 지원 가능해집니다. 취득 후 매칭도가 80%를 넘는 공고는 {len(_cert80)}건({_cert_names} 등)입니다. 건설안전기사·위험물산업기사·소방설비기사를 따로 요구하는 공고는 이 자격으로 풀리지 않습니다.</span></li>')
_crn = int(open(SP + "cr_n.txt").read()) if os.path.exists(SP + "cr_n.txt") else 5
_cr_names = "·".join(c["name"] for c in __import__("cr").CR) if False else ""
open_end = [r for r in rows if not r["dl"]]
open_names = "".join(f'<li>{e(r["name"])} <span class="pill {"ok" if r["g"]=="none" else "keep"}">{e(r["p"]["title"][:28])}</span></li>' for r in open_end)

# ----- excluded tables -----
def ex_table(dct, head):
    body = ""
    for i, why in sorted(dct.items()):
        p = P[i]; dl, dd = dday(p)
        body += (f'<tr><td class="corp"><strong><a class="co" href="{e(p["url"])}" target="_blank" rel="noopener">{e(p["company"])}</a></strong></td>'
                 f'<td class="ttl"><a class="tl" href="{e(p["url"])}" target="_blank" rel="noopener">{e(p["title"][:60])}</a></td>'
                 f'<td class="lv">{e(p["employment"])}<small>{e(p["level"])}</small></td><td>{e(why)}</td>'
                 f'<td class="dl">{e(dl) if dl else "채용 시"}</td><td class="src">{e(p["source"])}</td></tr>')
    return (f'<div class="scroll"><table class="tx"><thead><tr><th>업체명</th><th>공고명</th><th>고용형태</th><th>{head}</th><th>접수기한</th><th>출처</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')

css = open(SP + "base.css").read()
extra_css = open(SP + "extra.css").read()
body_html = open(SP + "body.tpl.html").read()
CRH = open(SP + "cr.html").read()
import os
BROADH = open(SP + "broad.html").read() if os.path.exists(SP + "broad.html") else ""
BN = re.search(r"국내 전체 신입 안전 채용<span class=\"n\">(\d+)건", BROADH)
BN = BN.group(1) if BN else ""
_cr_live = json.load(open(SP + "cr_ids.json", encoding="utf-8")) if os.path.exists(SP + "cr_ids.json") else []
LEAD_CR = (f'<li><span class="tag keep">기업분석</span><span>상위 {_crn}곳({"·".join(x["short"] for x in _cr_live)})을 조사한 결과 <b>모두 조건부 지원</b>입니다. 공통으로 확인할 것은 계약직 전환·처우(출처 미확보)와 자격증 없이 맡는 업무 범위입니다.' + "" + '</span></li>')
_bs = json.load(open(SP + "broad_stats.json")) if os.path.exists(SP + "broad_stats.json") else {}
_GL = {"none": "자격 없이 지원 가능", "cert": "산업안전(산업)기사 필요", "other": "다른 자격도 필요", "env": "환경 자격 필요"}
if soon:
    _items = " · ".join(f'<b>{e(r["name"])}</b> {r["dl"][5:]}({"오늘" if r["dd"] == 0 else "D-" + str(r["dd"])}) {_GL.get(r["g"], r["g"])}' for r in soon)
    LEAD_SOON = f'<li><span class="tag bad">마감 임박</span><span>3일 안에 마감되는 공고는 {len(soon)}건입니다. {_items}.</span></li>'
else:
    LEAD_SOON = '<li><span class="tag bad">마감 임박</span><span>3일 안에 마감되는 공고는 없습니다.</span></li>'
_exp_names = list(dict.fromkeys(re.sub(r"\s*\(주\)|㈜", "", r["name"]).strip() for r in rows if r["g"] == "exp" and "수집기" in r["s"]["gap"]))
_ovs = len([1 for v in SKIP.values() if v.startswith("해외")])
LEAD_NOTE = ('<li><span class="tag">주의</span><span>' + (f"수집 목록의 <b>{'·'.join(e(x) for x in _exp_names)}</b>는 본문이 경력직(3년 이상 등)인데 '신입'이나 '경력무관'으로 표기돼 있어 신입 지원 대상에서 뺐습니다. " if _exp_names else "") + (f"해외 근무 공고 {_ovs}건도 뺐습니다." if _ovs else "") + '</span></li>') if (_exp_names or _ovs) else ""
LEAD_SCOPE = (f'<li><span class="tag">기준</span><span>종합건설사와 엔지니어링 회사는 <b>상위 15개사만</b> 싣고 전문건설업체는 뺐습니다(시평 15위 안 종합건설사, 설계·감리 상위 15개사 기준). 회사명에 안전·세이프티가 들어간 업체도 뺐습니다. 이 기준으로 직접 채점 목록에서 {len(RULE_DROPPED)}건, 국내 전체 목록에서 {_bs.get("rule_dropped", 0)}건이 빠졌습니다.</span></li>\n')
BLEAD = ""
if BROADH and os.path.exists(SP + "broad_stats.json"):
    _b = json.load(open(SP + "broad_stats.json")); _c = _b["cnt"]
    BLEAD = (f'<li><span class="tag ok">국내 전체</span><span>안전 신입으로 지원할 수 있는 국내 공고 <b>{_b["n"]}건</b>을 모았습니다. 자격 없이 지원 가능 {_c.get("none",0)}건, 산업안전기사 필요 {_c.get("cert",0)}건, 자격 언급(필수 여부 확인) {_c.get("maybe",0)}건, '
             f'다른 자격 {_c.get("other",0)+_c.get("env",0)}건, 경력 요구 {_c.get("exp",0)}건, 직무 확인 필요 {_c.get("chk",0)}건, 근거 부족 {_c.get("thin",0)}건입니다. 아래 \'국내 전체\' 섹션에서 자격·지역·고용형태로 걸러 볼 수 있습니다.</span></li>\n')

repl = {
 "{{KPIS}}": kpis, "{{T_NOW}}": table(now_ok, "now"), "{{T_CERT}}": table(cert_ok, "cert"), "{{T_CAREFUL}}": table(careful, "now"),
 "{{N_NOW}}": str(n_now), "{{N_SCORE}}": str(n_score), "{{N_CERT}}": str(n_cert), "{{N_CAREFUL}}": str(len(careful)), "{{N_THIN}}": str(n_thin), "{{N_SKIP}}": str(n_skip),
 "{{DIST}}": bars(dist), "{{DIST_AFT}}": bars(dist_aft), "{{GAPS}}": bars(gaps), "{{GAIN}}": f'<div class="bars">{gain_html}</div>',
 "{{FLOW}}": flow_html, "{{CAL}}": cells, "{{OPEN_END}}": open_names, "{{N_WEEKS}}": str(nweeks),
 "{{T_THIN}}": ex_table(THIN, "근거 부족 사유"), "{{T_SKIP}}": ex_table(SKIP, "제외 사유"),
 "{{BROAD_LEAD}}": BLEAD, "{{LEAD_NOW}}": LEAD_NOW, "{{LEAD_CERT}}": LEAD_CERT, "{{LEAD_CR}}": LEAD_CR, "{{LEAD_SCOPE}}": LEAD_SCOPE, "{{LEAD_SOON}}": LEAD_SOON, "{{LEAD_NOTE}}": LEAD_NOTE, "{{WHEN}}": WHEN, "{{TODAY}}": TODAY.isoformat(), "{{N_CR}}": str(_crn), "{{CR}}": CRH, "{{BROAD}}": BROADH, "{{NAV_BROAD}}": (f'<a href="#broad">국내 전체 <b>{BN}</b></a>' if BROADH else ""), "{{CHIP_BROAD}}": (f'<a href="#broad">국내 전체 {BN}</a>' if BROADH else ""), "{{CL_URL}}": CL_URL, "{{BR_URL}}": BR_URL,
}
for k, v in repl.items(): body_html = body_html.replace(k, v)

out = f'''<title>안전관리자 채용 매칭 브리핑</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap">
<style>
{css}
{extra_css}
</style>
{body_html}'''
open(SP + "matching_briefing.html", "w").write(out)
print(len(out), "bytes", "now", n_now, "cert", n_cert, "careful", len(careful), "soon", [r["name"] for r in soon], "green_after", [r["name"] for r in green_after])
