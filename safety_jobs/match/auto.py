# -*- coding: utf-8 -*-
"""공고 본문에서 요건을 읽어 jobstack 가중치(필수40·우대20·경력20·기업10, 지역 제외)로 자동 채점한다."""
import re, datetime, os
HERE = os.path.dirname(os.path.abspath(__file__))

IE = re.compile(r"산업\s*안전\s*(?:산업)?\s*기사|산업\s*안전\s*지도사|안전\s*관리자\s*(?:법적\s*)?선임|선임\s*(?:가능|자격)|안전\s*(?:관리\s*)?(?:관련|분야)?\s*(?:국가\s*)?(?:기술\s*)?자격(?:증)?|안전\s*(?:관련\s*)?자격증|관련\s*자격(?:증)?\s*(?:소지|보유)")
CONSTR_ONLY = re.compile(r"건설\s*안전\s*(?:산업)?\s*기사")
OTHER_CERT = re.compile(r"소방설비|소방안전관리자|위험물\s*(?:산업)?\s*기사|위험물\s*기능|대기환경|수질환경|전기\s*(?:산업)?\s*기사|가스\s*(?:산업)?\s*기사|산업위생관리|화공\s*기사|공조냉동|보건관리자|간호사")
REQ_HEAD = r"자격\s*요건|지원\s*자격|응시\s*자격|자격\s*조건|필수\s*(?:요건|사항)|공통\s*자격|Qualifications|Requirements"
PREF_HEAD = r"우대\s*(?:사항|조건|요건)|우대\s*[:：]|Preferred"
END_HEAD = r"근무\s*조건|근무\s*형태|근무지|전형\s*절차|채용\s*절차|접수\s*(?:기간|방법)|복리\s*후생|복지|제출\s*서류|유의\s*사항|급여|모집\s*인원"

def section(text, head, stops, maxlen=900):
    m = re.search(head, text)
    if not m: return ""
    rest = text[m.end(): m.end() + maxlen]
    n = re.search(stops, rest)
    return rest[: n.start()] if n else rest

REGIONS = [("서울", "서울"), ("경기", "경기"), ("인천", "인천"), ("부산", "부산"), ("울산", "울산"), ("경남", "경남"), ("경북", "경북"), ("대구", "대구"),
           ("대전", "대전"), ("충남", "충남"), ("충북", "충북"), ("광주", "광주"), ("전남", "전남"), ("전북", "전북"), ("강원", "강원"), ("세종", "세종"), ("제주", "제주"),
           ("창원", "경남"), ("김해", "경남"), ("양산", "경남"), ("거제", "경남"), ("구미", "경북"), ("포항", "경북"), ("경주", "경북"), ("천안", "충남"), ("아산", "충남"), ("당진", "충남"),
           ("평택", "경기"), ("화성", "경기"), ("용인", "경기"), ("성남", "경기"), ("수원", "경기"), ("이천", "경기"), ("파주", "경기"), ("안산", "경기"), ("광양", "전남"), ("여수", "전남"), ("군산", "전북"), ("청주", "충북"), ("음성", "충북")]

def region_of(p):
    cond = (p.get("extra") or {}).get("cond") or []
    cand = []
    if cond: cand.append(cond[0])
    t = p.get("detail_text") or ""
    m = re.search(r"근무\s*(?:지|지역|지주소|장소)\s*[:：]?\s*([^\n]{2,40}?)(?=\s*(?:근무\s*(?:일|요일|시간)|지도\s*보기|🎁|🚀|📋|•|$))", t)
    if m: cand.append(m.group(1))
    cand.append(p.get("title") or "")
    loc = (p.get("extra") or {}).get("loc")
    if loc: cand.insert(0, loc)
    for c in cand:
        for key, sido in REGIONS:
            if key in c: return sido
    return "미확인"

def ind_value(p):
    e = p.get("extra") or {}
    h = p.get("hilite", "")
    base = {"A": 1.0, "B": 0.8, "F": 0.8}.get(h)
    if base is None: base = 0.6 if e.get("listed") else 0.4
    emp = p.get("employment", "")
    ev = {"정규직": 1.0, "계약직": 0.4, "인턴": 0.8}.get(emp, 0.5)
    if emp == "계약직" and re.search(r"정규직\s*전환\s*가능", p.get("detail_text") or ""): ev = 0.6
    return round((base + ev) / 2, 3)

def read_req(p):
    """(req_items, pref_items, gate, thin, notes). item=(label, now, after)"""
    t = re.sub(r"\s+", " ", p.get("detail_text") or "")
    q = p.get("qualification") or ""
    req_sec = section(t, REQ_HEAD, rf"{PREF_HEAD}|{END_HEAD}")
    pref_sec = section(t, PREF_HEAD, END_HEAD, 700)
    req = f"{req_sec} {q}"
    pref = f"{pref_sec} {p.get('preferred') or ''}"
    has_req = len(req_sec.strip()) >= 15 or len(q.strip()) >= 10 and q.strip() not in ("-",)
    items, pitems = [], []
    gate = "none"
    # 자격 — '우대' 문맥의 자격은 필수로 세지 않고, 'A, B, C 중' 나열은 대안으로 본다
    def hard(rx):
        out = []
        for m in rx.finditer(req):
            ctx = req[max(0, m.start() - 10): m.end() + 25]
            if "우대" in ctx: continue
            out.append(m)
        return out
    ie_m = hard(IE); co_m = hard(CONSTR_ONLY)
    ie_req = bool(ie_m or co_m)
    constr_only = bool(co_m) and not ie_m
    other_req = []
    for m in hard(OTHER_CERT):
        near = req[max(0, m.start() - 14): m.start()]
        alt = ie_req and not re.search(r"&|및|동시|그리고|\band\b", near)
        if not alt: other_req.append(m.group(0))
    if ie_req:
        if constr_only:
            items.append(("건설안전기사", 0.0, None)); gate = "other"
        else:
            items.append(("산업안전기사 등 안전관리자 선임 자격", 0.0, 1.0)); gate = "cert"
    if other_req:
        items.append((" · ".join(sorted(set(other_req)))[:30] + " 자격", 0.0, None))
        if re.search(r"대기환경|수질환경", " ".join(other_req)) and not ie_req: gate = "env"
        else: gate = "other"
    # 경력 요구
    exp = re.search(r"경력\s*(\d{1,2})\s*년\s*(?:이상|↑|이상\s*[~\-]\s*\d+\s*년)|(\d{1,2})\s*년\s*이상\s*(?:의\s*)?(?:관련\s*)?(?:경력|경험)", req)
    exp_n = int(exp.group(1) or exp.group(2)) if exp else 0
    career = 1.0
    if exp_n >= 2 and not re.search(r"신입\s*(?:가능|지원|도\s*가능)|경력\s*무관", req):
        career = 0.0; gate = "exp"; items.append((f"경력 {exp_n}년 이상", 0.0, None))
    if career == 1.0:
        for m in re.finditer(r"(?:안전|환경|EHS|HSE|관련)\s*(?:분야\s*)?경력(?!\s*무관|\s*자?\s*우대)(?:\s*필수|\s*자|\s*보유|\s*\d)?|경력자", req):
            ctx = req[max(0, m.start() - 8): m.end() + 12]
            if "우대" in ctx or re.search(r"신입\s*(?:가능|지원|도)|경력\s*무관|신입/경력", req): continue
            career = 0.0; gate = "exp"; items.append(("관련 경력 필수", 0.0, None)); break
    # 학력·전공
    if re.search(r"석사|박사", req) and not re.search(r"학사|대졸|4년제", req):
        items.append(("석사 이상", 0.0, None))
    elif re.search(r"학력\s*무관|고졸|초대졸|전문대|2[,·]?3\s*년제|4년제|대졸|대학교?\s*졸업|졸업\s*예정|학사", req):
        items.append(("학력 요건", 1.0, None))
    if re.search(r"안전\s*(?:공학|관련\s*학과|보건)|산업\s*안전|안전\s*관련\s*(?:학과|전공)", req):
        items.append(("안전 관련 전공", 1.0, None))
    elif re.search(r"(?:공학|이공)\s*계열|관련\s*(?:학과|전공)", req):
        items.append(("공학·관련 전공", 0.5, None))
    # 어학
    if re.search(r"TOEIC|토익|OPIc|오픽|영어", req):
        mm = re.search(r"TOEIC\s*(?:Speaking)?\s*(\d{3})|토익\s*(\d{3})", req)
        n = int(mm.group(1) or mm.group(2)) if mm else 0
        items.append(("영어 성적·활용", 1.0 if n <= 900 else 0.5, None))
    if re.search(r"일본어|중국어|베트남어|JLPT|HSK", req):
        items.append(("일본어·중국어 등 제2외국어", 0.0, None))
    if re.search(r"병역\s*(?:필|면제)|군필", req):
        items.append(("병역 필·면제(해당 시)", None, None))
    # 우대
    if re.search(r"안전\s*(?:공학|관련\s*학과|보건)|산업\s*안전\s*(?:관련|전공)|안전\s*관련\s*(?:학과|전공)", pref): pitems.append(("안전 관련 전공", 1.0, None))
    if re.search(r"영어|TOEIC|토익|OPIc|오픽|어학", pref): pitems.append(("영어·어학", 1.0, None))
    if re.search(r"(?<![A-Za-z])AI(?![A-Za-z])|인공지능|데이터\s*기반|생성형", pref): pitems.append(("AI·데이터 활용", 1.0, None))
    if IE.search(pref) or CONSTR_ONLY.search(pref): pitems.append(("안전 관련 자격증", 0.0, 1.0 if IE.search(pref) else None))
    if re.search(r"경력|경험|유경험", pref): pitems.append(("관련 경력·경험", 0.0, None))
    if OTHER_CERT.search(pref): pitems.append(("기타 자격(위험물·소방 등)", 0.0, None))
    meaningful = [i for i in items if i[0] != "학력 요건"]
    explicit = bool(re.search(r"자격\s*요건|Qualifications|Requirements", t))
    thin = (not meaningful and not pitems and not explicit) or (not has_req and not items)
    return items, pitems, gate, thin, career

def mean(items, after=False):
    v = []
    for l, x, a in items:
        if after and a is not None: x = a
        if x is None: continue
        v.append(x)
    return sum(v) / len(v) if v else None

def score(items, pitems, career, ind, after=False):
    parts = [(40, mean(items, after)), (20, mean(pitems, after)), (20, career), (10, ind)]
    num = sum(w * v for w, v in parts if v is not None); den = sum(w for w, v in parts if v is not None)
    return round(num / den * 100)

def global_cert_mention(p):
    t = re.sub(r"\s+", " ", f"{p.get('title') or ''} {p.get('listing_text') or ''} {p.get('detail_text') or ''}")
    for rx in (IE, CONSTR_ONLY):
        for m in rx.finditer(t):
            ctx = t[max(0, m.start() - 14): m.end() + 25]
            if "우대" in ctx or "취득 지원" in ctx or "선임 목적 아님" in ctx: continue
            return ctx
    return ""

def analyze_posting(p):
    items, pitems, gate, thin, career = read_req(p)
    if gate == "none" and not thin and global_cert_mention(p):
        gate = "maybe"
        items = items + [("안전 관련 자격(필수 여부 확인)", 0.5, 1.0)]
    ind = ind_value(p)
    brief = (not thin) and len([i for i in items if i[0] != "학력 요건"]) <= 1 and not pitems and gate in ("none",)
    out = dict(gate=gate, thin=thin, region=region_of(p), req=items, pref=pitems, brief=brief)
    if not thin:
        out["now"] = score(items, pitems, career, ind); out["aft"] = score(items, pitems, career, ind, True)
    return out

if __name__ == "__main__":
    import json, sys
    d = json.load(open(HERE + "/latest_main.json"))
    for i, p in enumerate(d["postings"]):
        a = analyze_posting(p)
        print(i, p["company"][:12], a["gate"], "thin" if a["thin"] else f'{a["now"]}→{a["aft"]}', a["region"], [x[0] for x in a["req"]][:5])
