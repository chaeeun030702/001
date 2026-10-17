# -*- coding: utf-8 -*-
"""종합건설사·엔지니어링은 상위 15개사만, 전문건설업체는 제외 (사용자 요청 2026-10-14)."""
import re
ENGINEERING_TOP15 = ("도화엔지니어링", "유신", "한국종합기술", "건화", "동명기술공단", "삼안", "이산", "다산컨설턴트", "경동엔지니어링", "평화엔지니어링",
                     "수성엔지니어링", "동부엔지니어링", "서영엔지니어링", "선진엔지니어링", "삼성이앤에이", "삼성E&A", "현대엔지니어링")
ENG_TOP_RE = re.compile("|".join(re.escape(re.sub(r"\s", "", n)) for n in ENGINEERING_TOP15))
ENG_RE = re.compile(r"엔지니어링|엔지니어|이엔지|E&G|ENG(?![A-Za-z])|기술단|기술공단|종합기술|건축사사무소|컨설턴트|감리|기술사사무소")
SPECIALTY_TITLE_RE = re.compile(r"전기\s*공사|설비\s*공사|소방\s*공사|통신\s*공사|배관|철콘|철근\s*콘크리트|토공|방수|도장|해체\s*공사|가설|비계|금속\s*창호|조경|기계\s*설비\s*(?:공사|시공)|클린룸|HVAC|공조|훅업|SET-?UP|셋업|PC\s*제작|플랜트\s*(?:건설\s*)?현장|토목\s*현장|건축\s*현장|시공\s*현장|건설\s*현장|공사\s*현장|신축\s*공사|증개축|철거")
SPECIALTY_NAME_RE = re.compile(r"(?:전기|설비|소방|배관|통신|방수|도장|조경|토건|기초|지반|해체|테크|기공|산전)(?:\(주\)|㈜)?$|전기공사|설비공사|기술공업|이앤씨|이엔씨|E&C|건설|개발|토목")

def name_of(p):
    return re.sub(r"\(주\)|㈜|주식회사|\(유\)|\s", "", p.get("company") or "")

PUBLIC_AFFIL_RE = re.compile(r"^코레일|^한국철도|^에스알$")
SAFETY_NAME_RE = re.compile(r"안전|세이프|safety", re.I)

def drop_reason(p):
    """제외 사유 문자열, 대상이면 ''. p는 latest.json 의 공고 dict."""
    name = name_of(p)
    if SAFETY_NAME_RE.search(p.get("company") or "") and "공공" not in (p.get("company_type") or ""):
        return "회사명에 안전·세이프티"
    rank = (p.get("extra") or {}).get("top100")
    if p.get("industry") == "건설":
        if rank and rank <= 15: return ""
        return "종합건설사 상위 15위 밖·전문건설"
    if PUBLIC_AFFIL_RE.search(name): return ""  # 코레일·SR 등 공기업 자회사는 전문건설 이름 규칙에서 제외
    if ENG_TOP_RE.search(name): return ""
    if ENG_RE.search(name): return "엔지니어링 상위 15개사 밖"
    if SPECIALTY_TITLE_RE.search(p.get("title") or "") and not (p.get("extra") or {}).get("groups"):
        return "전문건설(시공 현장)"
    if SPECIALTY_NAME_RE.search(name) and not (p.get("extra") or {}).get("groups") and not (p.get("extra") or {}).get("listed"):
        return "전문건설업체"
    return ""
