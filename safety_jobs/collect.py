# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx>=0.27.0",
#     "beautifulsoup4>=4.12.0",
# ]
# ///
#!/usr/bin/env python3
"""안전관리자 채용 공고 수집·정리 (일일 브리핑용).

SOURCES 순서가 곧 우선순위다. 같은 공고가 여러 곳에 있으면 목록에서 위에 있는
사이트의 것을 남긴다. 경력직 전용 공고와 마감된 공고는 제외한다.

    uv run safety_jobs/collect.py --out briefings   # md/html/json 브리핑 생성

GitHub Actions(.github/workflows/safety-jobs-briefing.yml)가 매일 실행한다.
"""

import argparse
import collections
import datetime as dt
import difflib
import gzip
import html
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import quote, urljoin

import httpx
from bs4 import BeautifulSoup

KST = dt.timezone(dt.timedelta(hours=9))
Q = quote("안전관리자")
# 검색어: 안전관리자 + 업종 무관 HSE/EHS 직무 + 자격증 명시 공고
KEYWORDS = ["안전관리자", "HSE", "EHS", "안전보건", "산업안전기사", "건설안전기사", "NEBOSH", "IOSH", "ISO45001", "안전공학", "안전"]
# 우대 강조(보라색): 외국어·영어 능통 / NEBOSH / IOSH / CSP
LANG_RE = re.compile(r"(?:영어|외국어|어학|English|중국어|일본어|베트남어|스페인어)\s*(?:회화\s*)?(?:능통|능숙|우수|가능|원활|비즈니스|원어민|fluent|business)"
                     r"|(?:TOEIC|토익|OPIc|오픽|TEPS|텝스|TOEIC\s*Speaking|토익\s*스피킹)\s*[:：]?\s*(?:\d{2,3}|IM|IH|AL|Lv|Level)"
                     r"|(?:어학|영어)\s*(?:성적|점수)\s*(?:우대|보유|필수)", re.I)
NEBOSH_RE = re.compile(r"NEBOSH", re.I)
IOSH_RE = re.compile(r"(?<![A-Za-z])IOSH(?![A-Za-z])", re.I)
HSE_ROLE_RE = re.compile(r"(?<![A-Za-z])(?:HSE|EHS|EH&S|SHE|HSEQ|QHSE)(?![A-Za-z])\s*(?:팀|파트|그룹|부문|담당|직무|업무|관리|엔지니어|매니저|"
                         r"Engineer|Specialist|Manager|Analyst|Officer|Coordinator|Supervisor|Leader|Assistant|Staff)", re.I)
CSP_RE = re.compile(r"(?<![A-Za-z])CSP(?![A-Za-z])|Certified\s+Safety\s+Professional", re.I)
CERT_KEY_RE = re.compile(r"(산업|건설)안전(?:산업)?기사")
ISO45001_RE = re.compile(r"ISO\s*[-_]?\s*45001|KOSHA[-\s]*MS", re.I)
# 공고 본문에 이 중 하나라도 있으면 안전 직무 공고로 싣는다
INCLUDE_RE = re.compile(r"산업안전(?:산업)?기사|(?:산업|건설)안전기술사|ISO\s*[-_]?\s*45001|안전\s*공학", re.I)
# '안전관리'는 흔한 말이라 직무로 쓰였거나 자격·우대·담당업무 항목에 있을 때만
SAFETY_DUTY_RE = re.compile(r"안전\s*관리\s*(?:자|업무|담당|선임|병행|직|팀|계획|체계)|안전\s*관리\s*(?:및|/|·)")
DUTY_HEAD = r"담당\s*업무|주요\s*업무|업무\s*내용|직무\s*내용|모집\s*분야"
PREF_IN_TITLE_RE = re.compile(r"[\(\[【][^\)\]】]*우대[^\)\]】]*[\)\]】]|[^\s/,]*\s*우대")
NON_HSE_SAFETY_RE = re.compile(r"Functional\s*Safety|안전\s*인증|Drug\s*Safety|Pharmacovigilance|Patient\s*Safety|Food\s*Safety|Product\s*Safety|Clinical|"
                               r"약물\s*감시|의약품\s*안전|식품\s*안전|안전성\s*(?:평가|정보)", re.I)
WATCH_RE = re.compile(r"감시\s*단")  # 안전감시단 등 감시 인력 모집은 제외
# 회사명에 이 용어가 있으면 제외 (안전·소방 전문 용역사, 학원·교육기관 등). 공백은 무시하고 비교한다
EXCLUDE_CORP_TERMS = ("소방", "조경", "구조엔지니어링", "감시단", "재해예방", "구조안전", "세이프티", "안전관리", "학원",
                      "소방기술단", "교육원", "안전시스템", "방재", "무사퇴근", "보건안전", "호남산업")
EXCLUDE_CORP_RE = re.compile("|".join(map(re.escape, EXCLUDE_CORP_TERMS)))
SALES_RE = re.compile(r"영업|세일즈|(?<![A-Za-z])Sales(?![A-Za-z])|판매\s*(?:사원|직|원)|텔레\s*마케|TM\s*상담", re.I)
HSE_RE = re.compile(r"(?<![A-Za-z])(?:HSE|EHS|SHE|HSEQ|QHSE)(?![A-Za-z])|환경\s*안전|안전\s*환경|안전\s*보건|안전\s*관리")
# 업체명으로 건설사 여부 판단 (제목의 '현장' 등은 공장 현장과 헷갈리므로 쓰지 않음)
CONSTR_NAME_RE = re.compile(r"건설|건축|토건|토목|이앤씨|이엔씨|E&C|ENC|씨엠|(?<![A-Za-z])CM(?![A-Za-z])|종합개발|주택|건영|중공업\s*건설부문|건설부문")

# 건설사는 2026년 시공능력평가 상위 100개사(토목건축)만 싣는다 — construction_top100_2026.tsv
_LATIN = {"A": "에이", "B": "비", "C": "씨", "D": "디", "E": "이", "F": "에프", "G": "지", "H": "에이치", "I": "아이", "J": "제이",
          "K": "케이", "L": "엘", "M": "엠", "N": "엔", "O": "오", "P": "피", "Q": "큐", "R": "알", "S": "에스", "T": "티",
          "U": "유", "V": "브이", "W": "더블유", "X": "엑스", "Y": "와이", "Z": "지"}
_ALIAS = {"아이파크현대산업개발": ["에이치디씨현대산업개발", "현대산업개발", "아이파크현대산업개발"],
          "삼성이앤에이": ["삼성엔지니어링"], "한화": ["한화건설부문", "한화건설"],
          "씨제이대한통운": ["씨제이대한통운건설부문"], "에스엠상선": ["에스엠상선건설부문"]}


def norm_corp(name):
    """업체명 정규화: 법인 표기·공백·괄호 제거, 영문 약칭은 한글 발음으로 (GS건설 → 지에스건설)."""
    n = re.sub(r"\(.*?\)|㈜|주식회사|유한회사|\s", "", name or "")
    n = n.upper().replace("E&C", "이앤씨").replace("E&A", "이앤에이").replace("S&D", "에스앤디").replace("D&I", "디앤아이")
    n = n.replace("IPARK", "아이파크").replace("POSCO", "포스코")
    n = re.sub(r"[A-Z]", lambda m: _LATIN[m.group(0)], n)
    return n.replace("이엔씨", "이앤씨")


def _load_top100():
    table = {}
    path = Path(__file__).with_name("construction_top100_2026.tsv")
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        rank, name = line.split("\t")
        key = norm_corp(name)
        table[key] = (int(rank), name)
        for a in _ALIAS.get(key, []):
            table[a] = (int(rank), name)
    return table


TOP100 = _load_top100()
MIXED_TOP100 = {norm_corp(n) for n in ("두산에너빌리티(주)", "효성중공업(주)", "(주)한화", "씨제이대한통운(주)", "에스엠상선(주)",
                                       "(주)농협네트웍스", "삼성물산(주)", "(주)동양", "(주)대림")}


def top100_rank(company):
    n = norm_corp(company)
    if n in TOP100:
        return TOP100[n][0]
    # '현대건설(주) 건설부문', '한화 건설부문' 처럼 뒤에 부문명이 붙은 경우
    m = re.match(r"(.+?)(?:건설부문|플랜트부문|인프라부문)$", n)
    return TOP100[m.group(1)][0] if m and m.group(1) in TOP100 else None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

SAFETY_RE = re.compile(r"안전|보건관리|(?<![A-Za-z])(?:HSE|EHS|EH&S|SHE|HSEQ|QHSE|HSSE|[Ss]afety|SAFETY)(?![A-Za-z])|산업위생|Industrial\s*Hygien|소방|방재")
CAREER_ONLY_RE = re.compile(r"경력\s*\d+\s*년\s*(이상|↑)?|경력직|경력\s*사원|경력\s*채용|^경력$")
NEWBIE_RE = re.compile(r"신입|인턴|경력\s*무관|졸업\s*예정|전체|무관")

# 강조 규칙 — A가 B보다 우선
HILITE_A_RE = re.compile(r"데이터\s*센터|IDC|하이테크|삼성|하이닉스")
BIG_GROUPS = (
    "삼성 SK 현대 HD현대 LG 롯데 포스코 POSCO 한화 GS 신세계 이마트 CJ 한진 대한항공 KT 두산 LS "
    "DL 대림 HDC 효성 코오롱 OCI KCC 한국타이어 고려아연 영풍 아모레 카카오 네이버 NAVER 쿠팡 "
    "대우건설 금호 태영 호반 부영 중흥 하림 HMM 셀트리온 미래에셋 농협 NH 한국전력 한전 "
    "한국수력원자력 한수원 한국가스공사 에코프로 SGC 동국제강 세아 한솔 대상 오리온 농심 "
    "KCC 현대건설 현대엔지니어링 GS건설 DL이앤씨 롯데건설 SK에코플랜트 포스코이앤씨 삼성물산"
).split()
FOREIGN_NAMES = (
    "3M 쓰리엠 필립모리스 바스프 BASF 듀폰 DuPont 에어리퀴드 린데 Linde 지멘스 Siemens 슈나이더 "
    "ABB 인텔 Intel 마이크론 Micron ASML 램리서치 Lam 어플라이드 Applied 도쿄일렉트론 TEL "
    "에쓰오일 S-OIL 유니레버 P&G 로레알 네슬레 코카콜라 아마존 Amazon AWS 구글 Google "
    "마이크로소프트 Microsoft 에퀴닉스 Equinix 디지털리얼티 다우 Dow 머크 Merck 에보닉 솔베이 "
    "아우모비오 보쉬 Bosch 콘티넨탈 BMW 벤츠 볼보 Volvo GE 하니웰 Honeywell 에머슨 존슨콘트롤즈 "
    "쉘 Shell 엑손 셰브론 토탈 한국알콘 Tesla 테슬라 Air Products 에어프로덕츠 SGS UL DNV 뷰로베리타스"
).split()

CERT_RE = re.compile(
    r"(?:산업|건설|가스|전기|소방|화공|기계|인간공학|화재감식)?안전(?:관리)?(?:기사|산업기사|기술사|지도사)"
    r"|산업위생관리(?:산업)?기사|산업보건지도사|소방(?:설비|시설)?(?:산업)?기사|소방시설관리사|소방안전관리자\s*\d급"
    r"|위험물(?:산업기사|기능장|기능사)|(?:대기|수질)?환경기사|전기(?:산업)?기사|가스(?:산업)?기사|건축(?:산업)?기사"
    r"|토목(?:산업)?기사|화약류(?:관리|제조)?(?:산업)?기사|간호사|보건관리자|운전면허"
)
ENG_RE = re.compile(r"(?:TOEIC\s*Speaking|TOEIC|토익\s*스피킹|토익|OPIc|오픽|TEPS|텝스|영어\s*(?:회화|능통|가능|우수|면접))(?:\s*[\d.]+\s*점?\s*(?:이상|↑)?|\s*(?:IM|IH|AL|Level)\s*\d?\s*(?:이상)?)?", re.I)
MAJOR_RE = re.compile(r"(?:산업|건설|화학|화공|기계|전기|전자|환경|소방|방재|토목|건축|안전|보건|원자력|재료|신소재|산업보건|간호)[가-힣·/]{0,6}(?:공학|학과|학|계열|전공)")
EDU_RE = re.compile(r"(?:학력\s*[:：]?\s*)?(대졸\s*(?:\(4년\))?\s*(?:이상|↑)?|초대졸\s*(?:이상|↑)?|고졸\s*(?:이상|↑)?|학력\s*무관|4년제[^,\n]{0,10}|석사[^,\n]{0,6})")

QUAL_HEAD = r"자격\s*요건|지원\s*자격|응시\s*자격|자격\s*조건|필수\s*(?:요건|사항)|공통\s*자격|Qualifications|Requirements|What\s+you\s+(?:need|bring)|Who\s+you\s+are"
PREF_HEAD = r"우대\s*(?:사항|조건|요건)|우대\s*[:：]|Preferred\s+(?:Qualifications|Skills|Experience)|Nice\s+to\s+have|Desired\s+(?:Qualifications|Skills)"
# 우대 조건에 AI 관련 역량이 있으면 강조(주황)
AI_TERM = r"(?<![A-Za-z])AI(?![A-Za-z])(?!\s*추천)|인공\s*지능|머신\s*러닝|딥\s*러닝|생성형|ChatGPT|(?<![A-Za-z])LLM(?![A-Za-z])|Machine\s*Learning"
AI_NEAR_PREF_RE = re.compile(rf"(?:{AI_TERM})[^.\n]{{0,40}}우대|우대[^.\n]{{0,60}}(?:{AI_TERM})", re.I)
AI_RE = re.compile(AI_TERM, re.I)
STOP = r"Preferred\s+Qualifications|Nice\s+to\s+have|Benefits|What\s+we\s+offer|이\s*기업과\s*나의|로그인\s*하고|적합도|TOP\s*궁금해요|스킬\s*핵심역량|핵심\s*역량|우대|근무\s*조건|근무\s*형태|근무지|근무\s*시간|전형|접수|복리|급여|제출\s*서류|유의\s*사항|기타\s*사항|채용\s*절차|모집\s*인원|기업\s*정보"


@dataclass
class Posting:
    source: str
    title: str
    company: str
    url: str
    listing_text: str = ""
    detail_text: str = ""
    employment: str = ""   # 정규직 / 계약직 / 인턴 / 기타
    level: str = ""        # 신입 / 경력무관 / 신입·경력 / 인턴 / 경력
    deadline: str = ""     # 표시용
    deadline_date: str = ""  # YYYY-MM-DD (정렬·만료 판단)
    qualification: str = ""
    preferred: str = ""
    company_type: str = ""  # 대기업 / 외국계 / 중견 / 공공 ... (사이트 표기)
    hilite: str = ""        # A / B / ""
    industry: str = ""      # 건설 / 일반 산업
    certs: list = field(default_factory=list)  # 공고에 명시된 산업안전기사·건설안전기사
    prefs: list = field(default_factory=list)  # 외국어·영어 능통 / NEBOSH / IOSH / CSP (보라색 강조)
    extra: dict = field(default_factory=dict)


def clean(s) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def text_of(node) -> str:
    return clean(node.get_text(" ")) if node else ""


def soup_text(html_: str) -> str:
    s = BeautifulSoup(html_, "html.parser")
    for t in s(["script", "style", "nav", "header", "footer", "noscript"]):
        t.decompose()
    return clean(s.get_text(" "))


class Fetcher:
    def __init__(self):
        self.c = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=25)
        self.deadline = None  # 사이트 단위 시간 한도 (time.time() 기준)

    def get(self, url, encoding=None, tries=3):
        last = None
        for i in range(tries):
            if self.deadline and time.time() > self.deadline:
                raise TimeoutError("사이트 수집 시간 한도 초과")
            try:
                r = self.c.get(url, headers={"Referer": url})
                r.raise_for_status()
                if encoding:
                    return r.content.decode(encoding, errors="ignore")
                return r.text
            except httpx.HTTPStatusError as e:
                if e.response.status_code < 500:  # 404 등은 재시도해도 같다
                    raise
                last = e
            except Exception as e:  # 타임아웃 등 일시 오류는 재시도
                last = e
            time.sleep(3 + i * 5)
        raise last


# ---------------------------------------------------------------- 날짜
def parse_deadline(text: str, today: dt.date):
    """문자열에서 마감일을 찾아 (표시 문자열, date|None)을 돌려준다."""
    t = clean(text)
    rel = re.search(r"오늘\s*마감|\d{1,2}\s*시\s*마감|내일\s*마감|모레\s*마감|D\s*-\s*(\d+)", t)
    if rel:
        days = int(rel.group(1)) if rel.group(1) else 1 if "내일" in rel.group(0) else 2 if "모레" in rel.group(0) else 0
        d = today + dt.timedelta(days=days)
        return f"{d:%Y-%m-%d}", d
    m = re.search(r"(20\d{2})\s*[.\-/년]\s*(\d{1,2})\s*[.\-/월]\s*(\d{1,2})", t)
    if m:
        d = safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if d:
            return f"{d:%Y-%m-%d}", d
    m = re.search(r"~\s*(\d{1,2})\s*[/.월]\s*(\d{1,2})", t) or re.search(r"\((\d{1,2})/(\d{1,2})\)", t) \
        or re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", t) or re.fullmatch(r"(\d{1,2})/(\d{1,2})", t)
    if m:
        mo, da = int(m.group(1)), int(m.group(2))
        d = safe_date(today.year, mo, da)
        if d and (today - d).days > 60:  # 연말→연초 넘김 (today = 기준일: 게시판은 작성일)
            d = safe_date(today.year + 1, mo, da)
        if d:
            return f"{d:%Y-%m-%d}", d
    if re.search(r"상시|채용\s*시|수시", t):
        return "채용 시 마감", None
    return "", None


def safe_date(y, m, d):
    try:
        return dt.date(y, m, d)
    except ValueError:
        return None


# ---------------------------------------------------------------- 목록 파서
def src_jobkorea(f: Fetcher):
    """잡코리아 신입·인턴 채용관(entry-level-internship)에서 KEYWORDS 검색."""
    out, seen = [], set()
    for kw in KEYWORDS:
        for page in (1, 2, 3):
            url = ("https://www.jobkorea.co.kr/Theme/TemplateFreeGnoList/entry-level-internship?"
                   f"rSearchText={quote(kw)}&themeNo=169&tabNo=0&jobFilter=1&psTab=40&FreePageNo={page}&MainPageNo=1&GIOpenTypeCode=0")
            s = BeautifulSoup(f.get(url), "html.parser")
            items = s.select("li.dmpItem")
            for li in items:
                a = li.select_one(".rTit a")
                if not a:
                    continue
                link = urljoin("https://www.jobkorea.co.kr", a["href"].split("&rPageCode")[0])
                if link in seen:
                    continue
                seen.add(link)
                p = Posting("잡코리아", text_of(a), text_of(li.select_one(".corNm")), link, text_of(li))
                p.deadline = text_of(li.select_one(".rPeriod"))
                p.extra = {"query": kw}
                out.append(p)
            if len(items) < 40:
                break
    return out


def src_saramin(f: Fetcher):
    out, seen = [], set()
    # 사용자 지정 검색 URL + 검색어별 신입/경력무관 필터 100건
    urls = [("안전관리자", f"https://www.saramin.co.kr/zf_user/search?searchword={Q}&go=&flag=n&searchMode=1&searchType=search&search_done=y&search_optional_item=n")]
    urls += [(kw, f"https://www.saramin.co.kr/zf_user/search?searchword={quote(kw)}&searchType=search&exp_cd=1&exp_none=y"
                  "&recruitPageCount=100&recruitSort=relation") for kw in KEYWORDS]
    for kw, url in urls:
        s = BeautifulSoup(f.get(url), "html.parser")
        for it in s.select("div.item_recruit"):
            a = it.select_one("h2.job_tit a")
            if not a:
                continue
            rec = re.search(r"rec_idx=(\d+)", a.get("href", ""))
            if not rec or rec.group(1) in seen:
                continue
            seen.add(rec.group(1))
            cond = [text_of(x) for x in it.select(".job_condition > span")]
            p = Posting("사람인", clean(a.get("title") or a.get_text()),
                        text_of(it.select_one(".corp_name a")),
                        f"https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx={rec.group(1)}",
                        text_of(it))
            bold = " ".join(text_of(b) for b in it.select(".job_sector b"))
            p.extra = {"rec_idx": rec.group(1), "cond": cond, "sector": bold, "query": kw}
            p.level = cond[1] if len(cond) > 1 else ""
            p.employment = cond[3] if len(cond) > 3 else ""
            p.deadline = text_of(it.select_one(".job_date .date"))
            out.append(p)
    return out


def src_linkareer(f: Fetcher):
    acts = {}
    for kw in ("안전관리자", "HSE", "EHS", "산업안전기사", "안전"):
        url = f"https://linkareer.com/search?direction=DESC&page=1&q={quote(kw)}&sort=RELEVANCE&tab=open-activity"
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', f.get(url), re.S)
        if not m:
            raise RuntimeError("__NEXT_DATA__ 없음")
        _walk_activities(json.loads(m.group(1)), acts, kw)
    return _linkareer_postings(acts)


def _walk_activities(data, acts, kw):

    def walk(o):
        if isinstance(o, dict):
            if o.get("__typename") == "Activity" and o.get("title") and o.get("id") and o["id"] not in acts:
                acts[o["id"]] = dict(o, _kw=kw)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)


def _linkareer_postings(acts):
    out = []
    for a in acts.values():
        p = Posting("링커리어", clean(a["title"]), clean(a.get("organizationName")),
                    f"https://linkareer.com/activity/{a['id']}", "")
        jt = a.get("jobTypes") or []
        p.extra = {"jobTypes": jt, "query": a.get("_kw", "")}
        names = {"NEW": "신입", "INTERN": "인턴", "EXPERIENCED": "경력", "CONTRACT": "계약직", "REGULAR": "정규직"}
        p.listing_text = " ".join(names.get(x, x) for x in jt)
        if a.get("recruitCloseAt"):
            d = dt.datetime.fromtimestamp(a["recruitCloseAt"] / 1000, KST).date()
            p.deadline = f"{d:%Y-%m-%d}"
        else:
            p.deadline = "채용 시 마감"
        out.append(p)
    return out


def src_worker(f: Fetcher):
    """건설워커 '안전/품질/재료/CAD' 부문 목록(40건 × 3쪽)."""
    out, seen = [], set()
    for page in (1, 2, 3):
        url = f"https://www.worker.co.kr/job/list.asp?jobid=all&key=jkind&bkw=si&list_ea=40&p={page}"
        s = BeautifulSoup(f.get(url, encoding="cp949"), "html.parser")
        for tr in s.find_all("tr"):
            tds = tr.find_all("td", recursive=False)
            if len(tds) < 11:
                continue
            a = tds[4].find("a", href=re.compile(r"view\.asp"))
            if not a:
                continue
            no = re.search(r"no=(\d+)", a["href"])
            if not no or no.group(1) in seen:
                continue
            seen.add(no.group(1))
            full = text_of(tds[4])  # "제목 지역 | 채용구분 | 급여"
            title = text_of(a)
            if "|" in title:
                title = title.split("|")[0].strip()
            head, _, rest = full.partition("|")
            region = head.replace(title, "").strip() if title in head else ""
            if not region and " " in title:  # 제목 끝의 지역명 분리
                t0, _, last = title.rpartition(" ")
                if re.fullmatch(r"[가-힣/·,]{2,12}", last) and re.search(r"서울|경기|인천|세종|강원|충|대전|부산|울산|대구|경|전|광주|제주|해외|전국|기타", last):
                    title, region = t0, last
            parts = [region] + [clean(x) for x in rest.split("|")]
            title, rest = clean(title), " | ".join(parts)
            p = Posting("워커", title, text_of(tds[2]), urljoin("https://www.worker.co.kr/job/", a["href"]),
                        f"{title} {rest} {text_of(tds[6])}")
            p.employment = parts[1] if len(parts) > 1 else ""
            p.level = text_of(tds[6]).split(" ")[0]  # 경력 / 신입 / 무관 / 전체
            p.extra = {"exp_edu": text_of(tds[6]), "region": parts[0] if parts else ""}
            p.deadline = text_of(tds[10])
            out.append(p)
    return out


def board_rows(soup, base, link_fn):
    """학과 게시판(표) → (제목, 링크, 작성일)."""
    rows = []
    for tr in soup.select("tbody tr, table tr"):
        a = tr.find("a")
        tds = tr.find_all("td")
        if not a or len(tds) < 3:
            continue
        title = clean(text_of(a.find("strong")) or a.get("title") or text_of(a))
        title = re.sub(r"^\[\s*일반공지\s*\]\s*", "", title)
        link = link_fn(a)
        date = ""
        for td in tds:
            m = re.search(r"20\d{2}[.\-]\d{2}[.\-]\d{2}", text_of(td))
            if m:
                date = m.group(0).replace(".", "-")
        if title and link and date:  # 작성일 없는 행 = 메뉴/레이아웃 표
            rows.append((title, urljoin(base, link), date))
    return rows


def make_board_source(name, url, link_fn, encoding=None):
    def _src(f: Fetcher):
        s = BeautifulSoup(f.get(url, encoding=encoding), "html.parser")
        out = []
        for title, link, date in board_rows(s, url, link_fn):
            p = Posting(name, title, "", link, f"{title} 작성일 {date}")
            p.extra = {"posted": date}
            out.append(p)
        if not out:
            raise RuntimeError("게시글 목록을 찾지 못함")
        return out
    return _src


def _href(a):
    h = a.get("href", "")
    return None if h.startswith(("#", "javascript")) else h


def _inu(a):
    seq, fnct = a.get("data-bbs-artcl-seq"), a.get("data-fnct-no")
    return f"https://www.inu.ac.kr/bbs/safety/{fnct}/{seq}/artclView.do" if seq and fnct else _href(a)


# ---------------------------------------------------------------- 외국계 채용 사이트 · 기업 채용 페이지
EN_SAFETY_TITLE_RE = re.compile(r"(?<![A-Za-z])(?:HSE|EHS|EH&S|SHE|HSEQ|QHSE|HSSE|Safety|Industrial\s*Hygien\w*)(?![A-Za-z])|안전|보건", re.I)
KOREA_LOC_RE = re.compile(r"Korea|,\s*KOR(?![A-Za-z])|Bundang|Seoul|Pyeongtaek|Hwaseong|Icheon|Cheongju|Gumi|Ulsan|Yeosu|Pohang|Incheon|Suwon|Yongin|"
                          r"Giheung|Asan|Cheonan|Onyang|Busan|Daegu|Gwangju|Daejeon|Pangyo|Seongnam|Anseong|Osan|Paju|"
                          r"서울|경기|평택|화성|이천|청주|구미|울산|여수|포항|인천|수원|용인|기흥|아산|천안|부산|판교|파주|한국", re.I)


def src_peoplenjob(f: Fetcher):
    """피플앤잡(외국계 전문) — 제목 검색 + HSE/EHS 전체 검색."""
    out, seen = [], set()
    queries = [("jobs.title", q) for q in ("안전", "보건", "HSE", "EHS", "Safety", "SHE")]
    queries += [("all", q) for q in ("HSE", "EHS", "NEBOSH", "산업안전기사", "ISO 45001")]
    for fld, q in queries:
        for page in (1, 2, 3):
            url = f"https://www.peoplenjob.com/jobs?field={fld}&q={quote(q)}&page={page}"
            s = BeautifulSoup(f.get(url), "html.parser")
            cards = s.select(".jd-card")
            for c in cards:
                a = c.select_one(".jd-card-title a")
                if not a:
                    continue
                link = a.get("href", "").split("?")[0]
                link = urljoin("https://www.peoplenjob.com", link)
                if link in seen:
                    continue
                seen.add(link)
                for b in a.select(".jd-card-meta-urgent"):  # 'U'(긴급) 배지
                    b.decompose()
                title = text_of(a)
                p = Posting("피플앤잡", title, text_of(c.select_one(".jd-card-company")), link, text_of(c))
                career = text_of(c.select_one(".jd-card-meta-career-text"))
                # 직급: 인턴.신입 포함 → 신입, 사원 → 상세 확인, 대리 이상만 → 경력
                p.level = "신입" if "신입" in career else "" if "사원" in career else "경력"
                p.deadline = re.sub(r"^(\d{1,2})\.(\d{1,2})$", r"\1/\2", text_of(c.select_one(".job-fin-date")))
                p.company_type = "외국계"
                p.extra = {"query": q, "career": career,
                           "loc": text_of(c.select_one(".jd-card-meta-location-text"))}
                out.append(p)
            if len(cards) < 30:
                break
            time.sleep(0.5)
    return out


# (표시 이름, tenant, wd 번호, site, 업종) — Workday 공개 채용 API
WORKDAY = [
    ("3M", "3m", "wd1", "Search", ""),
    ("Applied Materials", "amat", "wd1", "External", "하이테크·반도체"),
    ("Micron", "micron", "wd1", "External", "하이테크·반도체"),
    ("Equinix", "equinix", "wd1", "External", "데이터센터"),
    ("Air Liquide", "airliquidehr", "wd3", "AirLiquideExternalCareer", "반도체 산업가스"),
    ("Air Products", "airproducts", "wd5", "AP0001", "반도체 산업가스"),
]
# Workday 주소를 모르는 회사: 채용 홈에서 myworkdayjobs 링크를 찾아 쓴다 (못 찾으면 건너뜀)
WORKDAY_DISCOVER = [
    ("Lam Research", "https://careers.lamresearch.com/", "하이테크·반도체"),
    ("Linde", "https://www.linde.com/careers", "반도체 산업가스"),
    ("ASML", "https://www.asml.com/en/careers", "하이테크·반도체"),
    ("Corning", "https://www.corning.com/worldwide/en/careers.html", "하이테크"),
    ("Dow", "https://corporate.dow.com/en-us/careers.html", ""),
    ("Honeywell", "https://careers.honeywell.com/", ""),
]
WD_LINK_RE = re.compile(r"https://([a-z0-9-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([A-Za-z0-9_-]+)")
CAREER_STATUS = {}  # 회사별 수집 결과 (사이트 현황표에 표시)
PREV_SEEN = {}      # 직전 브리핑의 URL/업체+공고명 → 처음 수집일 (신규 판정)
REPORT_EVERY = 2    # 보고 주기: 짝수 날(2·4·…·30일) 20:00 — Routine cron '2-30/2'


def last_report_date(today):
    """오늘 이전의 마지막 보고일 (짝수 날, 30일까지). 그 뒤에 처음 수집된 공고가 '신규'."""
    d = today - dt.timedelta(days=1)
    while not (d.day % 2 == 0 and d.day <= 30):
        d -= dt.timedelta(days=1)
    return d


def is_new(p, today):
    fs = p.extra.get("first_seen")
    return bool(fs) and fs > last_report_date(today).isoformat()
PREV_TOTAL = None   # 직전 브리핑 공고 수 (KPI 변화량)


def _html_text(h):
    return clean(BeautifulSoup(h or "", "html.parser").get_text(" "))


def _workday(f: Fetcher, name, tenant, wd, site, sector):
    base = f"https://{tenant}.{wd}.myworkdayjobs.com"
    api = f"{base}/wday/cxs/{tenant}/{site}/jobs"
    found = {}
    for q in ("Korea", "EHS", "HSE", "Safety", "Environmental Health Safety", "안전"):
        for off in range(0, 200, 20):
            if f.deadline and time.time() > f.deadline:
                raise TimeoutError("사이트 수집 시간 한도 초과")
            r = f.c.post(api, json={"appliedFacets": {}, "limit": 20, "offset": off, "searchText": q},
                         headers={"Accept": "application/json", "Content-Type": "application/json"})
            r.raise_for_status()
            d = r.json()
            posts = d.get("jobPostings") or []
            for jp in posts:
                path = jp.get("externalPath", "")
                if path and path not in found:
                    found[path] = jp
            if len(posts) < 20 or (q != "Korea" and off >= 40):
                break
            time.sleep(0.3)
    out = []
    for path, jp in found.items():
        title = clean(jp.get("title", ""))
        loc = clean(jp.get("locationsText", ""))
        if not EN_SAFETY_TITLE_RE.search(title):
            continue
        multi = re.search(r"\d+\s*(?:Locations|개\s*근무지)", loc)
        if not (KOREA_LOC_RE.search(f"{loc} {title}") or multi):
            continue
        p = Posting("기업 채용 페이지", title, name, f"{base}/{site}{path}", f"{title} {loc} {jp.get('postedOn', '')}")
        p.company_type = "외국계"
        p.deadline = "채용 시 마감"  # Workday 공고에는 마감일이 없다
        p.extra = {"query": "Workday", "sector": sector, "loc": loc,
                   "detail_api": f"{base}/wday/cxs/{tenant}/{site}{path}", "need_korea": bool(multi and not KOREA_LOC_RE.search(loc))}
        out.append(p)
    return out


def _rmk_basf(f: Fetcher):
    """BASF (SAP SuccessFactors 채용 사이트) — 한국 근무 공고."""
    page = f.get("https://basf.jobs/search/?q=&locationsearch=Korea")
    tok = re.search(r'CSRFToken\s*=\s*"([^"]+)"', page)
    out = []
    for pn in range(0, 5):
        r = f.c.post("https://basf.jobs/services/recruiting/v1/jobs",
                     json={"locale": "en_US", "pageNumber": pn, "sortBy": "", "keywords": "", "location": "Korea",
                           "facetFilters": {}, "brand": "", "skills": [], "categoryId": 0, "alertId": "", "rcmCandidateId": ""},
                     headers={"Accept": "application/json", "Content-Type": "application/json",
                              "X-CSRF-Token": tok.group(1) if tok else ""})
        r.raise_for_status()
        rows = r.json().get("jobSearchResult") or []
        for row in rows:
            j = row.get("response", row)
            title = clean(j.get("unifiedStandardTitle") or j.get("title") or "")
            locs = " ".join(j.get("jobLocationShort") or [])
            if not EN_SAFETY_TITLE_RE.search(title):
                continue
            url = f"https://basf.jobs/job/{j.get('urlTitle', 'job')}/{j.get('id')}-en_US/"
            p = Posting("기업 채용 페이지", title, "BASF", url, f"{title} {locs}")
            p.company_type = "외국계"
            p.deadline = "채용 시 마감"
            p.extra = {"query": "RMK", "sector": "화학", "loc": locs}
            out.append(p)
        if len(rows) < 10:
            break
    return out


def src_company_careers(f: Fetcher):
    """외국계 기업 채용 페이지(Workday 등)에서 한국 근무 HSE/EHS/Safety 공고."""
    out = []
    targets = list(WORKDAY)
    for name, home, sector in WORKDAY_DISCOVER:
        try:
            m = WD_LINK_RE.search(f.get(home, tries=1))
        except Exception as e:
            CAREER_STATUS[name] = f"채용 홈 접속 실패({type(e).__name__})"
            continue
        if not m:
            CAREER_STATUS[name] = "Workday 등 공개 API 없음 — 자체 검색(스크립트 렌더링)이라 수집 불가"
            continue
        targets.append((name, m.group(1), m.group(2), m.group(3), sector))
    for name, tenant, wd, site, sector in targets:
        try:
            got = _workday(f, name, tenant, wd, site, sector)
            CAREER_STATUS[name] = f"한국 HSE {len(got)}건"
            out += got
        except Exception as e:
            CAREER_STATUS[name] = f"실패({type(e).__name__})"
    try:
        got = _rmk_basf(f)
        CAREER_STATUS["BASF"] = f"한국 HSE {len(got)}건"
        out += got
    except Exception as e:
        CAREER_STATUS["BASF"] = f"실패({type(e).__name__})"
    if not any(v.startswith("한국") for v in CAREER_STATUS.values()):
        raise RuntimeError("기업 채용 페이지 전부 접속 실패: " + ", ".join(f"{k} {v}" for k, v in CAREER_STATUS.items()))
    return out


def src_wanted(f: Fetcher):
    """원티드 — 공개 API (GitHub Actions에서는 403 차단 중)."""
    out = []
    for q in ("안전관리자", "HSE", "EHS", "안전"):
        d = json.loads(f.get(f"https://www.wanted.co.kr/api/v4/jobs?country=kr&query={quote(q)}&years=0&limit=50&offset=0&job_sort=job.latest_order"))
        for j in d.get("data", []):
            p = Posting("원티드", clean(j.get("position", "")), clean((j.get("company") or {}).get("name", "")),
                        f"https://www.wanted.co.kr/wd/{j.get('id')}", clean(j.get("position", "")))
            p.deadline = j.get("due_time") or "채용 시 마감"
            p.extra = {"query": q}
            out.append(p)
    return out


def src_catch(f: Fetcher):
    """캐치 — 검색 결과 (GitHub Actions에서는 403 차단 중)."""
    out, seen = [], set()
    for q in ("안전관리자", "HSE", "EHS", "안전"):
        s = BeautifulSoup(f.get(f"https://www.catch.co.kr/NCS/RecruitSearch?Keyword={quote(q)}"), "html.parser")
        for a in s.select('a[href*="RecruitInfoDetails"]'):
            link = urljoin("https://www.catch.co.kr", a["href"])
            if link in seen or not text_of(a):
                continue
            seen.add(link)
            p = Posting("캐치", text_of(a), "", link, text_of(a.parent))
            p.extra = {"query": q}
            out.append(p)
    return out


MANUAL_POSTINGS_PATH = Path(__file__).with_name("manual_postings.json")


def manual_urls() -> set:
    """지금 manual_postings.json에 남아 있는 공고 주소 (지운 공고는 이전 브리핑에서 이어 싣지 않는다)."""
    try:
        items = json.loads(MANUAL_POSTINGS_PATH.read_text(encoding="utf-8")).get("items", [])
    except (OSError, ValueError):
        return set()
    return {it.get("url") or f"manual:{it['company']}:{it.get('title', '')}" for it in items if it.get("company")}


def src_manual(f: Fetcher):
    """다른 브리핑·채용 달력에서 넘겨받은 공고 (safety_jobs/manual_postings.json). 직무 확인이 필요하면 표시."""
    try:
        items = json.loads(MANUAL_POSTINGS_PATH.read_text(encoding="utf-8")).get("items", [])
    except (OSError, ValueError):
        return []
    out = []
    for it in items:
        if not it.get("company"):
            continue
        # source가 '사람인'이면 다른 세션이 사람인에서 직접 찾아 넘긴 공고 → 사람인 공고로 싣고 상세 본문도 읽는다
        src = it.get("source") or "직접 추가"
        p = Posting(src, clean(it.get("title") or f"{it['company']} 채용"), clean(it["company"]),
                    it.get("url") or f"manual:{it['company']}:{it.get('title', '')}", clean(it.get("title", "")))
        p.deadline = it.get("deadline") or "확인 필요"
        p.employment = it.get("employment") or ""
        p.level = it.get("level") or "신입"
        p.extra = {"manual": True, "needs_check": it.get("safety_job") != "yes",
                   "check_note": it.get("note", ""), "via": it.get("via", "")}
        if src == "LinkedIn":
            p.listing_text = clean(f"{p.title} {it.get('note', '')}")
            p.extra["check_note"] = ""
            p.company_type = it.get("company_type") or "외국계"  # LinkedIn 한국 HSE 공고는 대부분 외국계 기업·헤드헌팅
        rec = re.search(r"rec_idx=(\d+)", p.url)
        if src == "사람인" and rec:
            p.extra["rec_idx"] = rec.group(1)
        if it.get("added"):
            p.extra["first_seen"] = it["added"]  # 처음 찾은 날 (오늘 찾은 신규 판정)
        out.append(p)
    return out


def fetch_detail(f: Fetcher, p: Posting) -> str:
    if p.url.startswith("manual:") or p.source == "LinkedIn":  # LinkedIn은 자동 접속하지 않는다 (브라우저 작업이 DB에 넣은 값만 씀)
        return ""
    if p.extra.get("detail_api"):  # Workday: JSON 상세
        r = f.c.get(p.extra["detail_api"], headers={"Accept": "application/json"})
        r.raise_for_status()
        info = r.json().get("jobPostingInfo", {})
        locs = " ".join([info.get("location", "")] + (info.get("additionalLocations") or []))
        p.extra["loc"] = clean(locs) or p.extra.get("loc", "")
        p.extra["time_type"] = info.get("timeType", "")
        return clean(f"{info.get('title', '')} 근무지 {locs} {info.get('timeType', '')} "
                     f"{_html_text(info.get('jobDescription'))}")
    url = p.url
    if p.source == "사람인":
        url = f"https://www.saramin.co.kr/zf_user/jobs/relay/view-detail?rec_idx={p.extra['rec_idx']}&rec_seq=0"
    return soup_text(f.get(url, encoding="cp949" if p.source == "워커" else None))


EN_YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:or\s+more\s+|\+\s*)?years?(?:'|’)?\s*(?:of\s+)?(?:\w+\s+){0,4}?(?:experience|exp\.)", re.I)
EN_ENTRY_RE = re.compile(r"new\s*grad|recent\s*graduate|entry[\s-]*level|(?<![A-Za-z])intern(?:ship)?(?![A-Za-z])|no\s+(?:prior\s+)?experience\s+(?:is\s+)?required|0\s*[-~]\s*\d\s*years?|신입", re.I)


def foreign_level(p: Posting):
    """외국계 채용 페이지·피플앤잡 공고의 경력 요건 (영문 'N+ years of experience' 포함)."""
    t = p.detail_text
    if p.source == "피플앤잡" and p.level == "경력":
        return
    if EN_ENTRY_RE.search(f"{p.title} {t[:6000]}") or re.search(r"신입\s*(?:가능|지원|포함)|경력\s*무관", t):
        p.level = p.level or "신입"
        return
    years = [int(m.group(1)) for m in EN_YEARS_RE.finditer(t)]
    years += [int(m.group(1)) for m in re.finditer(r"경력\s*(\d{1,2})\s*년\s*(?:이상|↑)", t)]
    if years and min(years) >= 2:
        p.level = "경력"
    elif years:
        p.level = "신입·경력"
    elif p.source == "피플앤잡" and not p.level:
        p.level = "신입·경력" if "사원" in p.extra.get("career", "") else ""


# (이름, 수집 함수, 게시판 여부) — 순서 = 중복 시 우선순위
SOURCES = [
    ("잡코리아", src_jobkorea, False),
    ("사람인", src_saramin, False),
    ("링커리어", src_linkareer, False),
    ("워커", src_worker, False),
    ("서울과기대 안전공학과", make_board_source(
        "서울과기대 안전공학과", "https://safety.seoultech.ac.kr/b_information/job_info/", _href), True),
    ("충북대 안전공학과", make_board_source(
        "충북대 안전공학과", "https://safety.chungbuk.ac.kr/safety5_2", _href), True),
    ("인천대 안전공학과", make_board_source(
        "인천대 안전공학과", "https://www.inu.ac.kr/safety/3207/subview.do", _inu), True),
    ("부경대 안전공학과", make_board_source(
        "부경대 안전공학과", "https://safety.pknu.ac.kr/safety/2080", _href), True),
    ("피플앤잡", src_peoplenjob, False),
    ("기업 채용 페이지", src_company_careers, False),
    ("원티드", src_wanted, False),
    ("캐치", src_catch, False),
    ("직접 추가", src_manual, False),
]


# ---------------------------------------------------------------- 상세 분석
def section(text, head_re, max_len=260):
    m = re.search(rf"(?:{head_re})\s*[:：]?", text)
    if not m:
        return ""
    body = text[m.end():m.end() + 1200]
    stop = re.search(STOP if "우대" not in head_re else STOP.replace("|우대", ""), body[5:])
    if stop:
        body = body[:stop.start() + 5]
    return clean(body)[:max_len]


def uniq(seq, limit=4):
    out = []
    for x in seq:
        x = clean(x)
        if x and not any(x in y or y in x for y in out):
            out.append(x)
    return out[:limit]


def summarize_qual(qual_txt, whole):
    src = qual_txt or whole
    majors = uniq(m.group(0) for m in MAJOR_RE.finditer(src))
    certs = uniq((m.group(0) for m in CERT_RE.finditer(src)), 4)
    eng = uniq((m.group(0) for m in ENG_RE.finditer(whole)), 2)
    edu = uniq((m.group(1) for m in EDU_RE.finditer(src)), 1)
    parts = []
    if majors:
        parts.append("학과: " + ", ".join(majors))
    if certs:
        parts.append("자격: " + ", ".join(certs))
    if eng:
        parts.append("영어: " + ", ".join(eng))
    if edu:
        parts.append("학력: " + edu[0])
    if not parts and qual_txt:
        parts.append(qual_txt[:110])
    return " / ".join(parts)


def detail_fields(p: Posting):
    t = p.detail_text
    if p.source == "잡코리아":
        m = re.search(r"고용형태\s*([가-힣·,/ ]{2,20}?)\s*(?:직급|급여|근무)", t)
        if m:
            p.employment = clean(m.group(1))
        m = re.search(r"지원자격\s*경력\s*([가-힣·↑0-9 ]{2,15}?)\s*학력", t)
        if m:
            p.level = clean(m.group(1))
        m = re.search(r"마감일\s*(20\d{2}\.\d{2}\.\d{2})", t)
        if m:
            p.deadline = m.group(1)
        m = re.search(r"지원자격\s*경력\s*[가-힣·↑0-9 ]{2,15}?\s*학력\s*([가-힣0-9()↑ ]{2,15}?)\s*(?:스킬|우대|핵심|자격증|$)", t)
        if m:
            p.extra["edu"] = clean(m.group(1))
        m = re.search(r"산업\s*\(업종\)\s*([가-힣·,/ ]{2,30}?)\s*(?:지도보기|위치|설립|대표|$)", t)
        if m:
            p.extra["biz"] = clean(m.group(1))
        m = re.search(r"기업구분\s*([가-힣]+)", t)
        if m:
            p.company_type = m.group(1)
    elif p.source == "링커리어":
        m = re.search(r"기업형태\s*([가-힣]+)", t)
        if m:
            p.company_type = m.group(1)
        m = re.search(r"마감일\s*(20\d{2}\.\d{2}\.\d{2})", t)
        if m:
            p.deadline = m.group(1)
    elif p.source == "워커":
        if p.deadline in ("", "채용시"):
            m = re.search(r"마감일\s*(20\d{2}년\s*\d{1,2}월\s*\d{1,2}일|채용시)", t)
            if m:
                p.deadline = m.group(1)
    elif p.extra.get("posted") is not None:  # 학과 게시판
        m = re.search(r"(?:접수\s*기간|마감|지원서\s*접수)[^~]{0,30}~\s*([^)\]]{3,25})", t)
        p.deadline = m.group(1) if m else ""


def employment_of(p: Posting, text):
    e = p.employment
    if p.source == "링커리어":
        jt = p.extra.get("jobTypes", [])
        e = "계약직" if "CONTRACT" in jt else "인턴" if "INTERN" in jt else "정규직" if "NEW" in jt else ""
    if not e:
        if re.search(r"인턴", p.title):
            e = "인턴"
        elif re.search(r"계약직|기간제|촉탁|PJT|프로젝트\s*계약", f"{p.title} {text}"):
            e = "계약직"
        elif re.search(r"(?<![A-Za-z])(?:Contract(?:or)?|Temporary|Fixed[\s-]*term)(?![A-Za-z])", f"{p.title} {p.extra.get('time_type', '')}", re.I):
            e = "계약직"
        elif re.search(r"정규직", text) or re.search(r"Full[\s_-]*time|Regular|Permanent", p.extra.get("time_type", ""), re.I):
            e = "정규직"
    if re.search(r"계약|기간제|파견|현장채용", e):
        return "계약직"
    if "정규" in e:
        return "정규직"
    if "인턴" in e:
        return "인턴"
    return "기타/미표기"


# 대리급 이상(대리·과장·차장·부장·팀장·임원, 영문 Senior/Manager/Director 등) 공고는 경력직으로 보고 제외
SENIOR_RANK_RE = re.compile(r"대리|과장|차장|부장|팀장|실장|임원|책임|수석|매니저|디렉터|"
                            r"(?<![A-Za-z])(?:Senior|Sr\.?|Director|Head|Principal|Lead|Manager|Supervisor|VP|Chief)(?![A-Za-z])", re.I)
JUNIOR_RANK_RE = re.compile(r"사원|주임|신입|인턴|졸업|(?<![A-Za-z])(?:Junior|Jr\.?|Associate|Entry|Intern|Graduate|Trainee)(?![A-Za-z])", re.I)
RANK_FIELD_RE = re.compile(r"직급\s*(?:/\s*직책)?\s*[:：]?\s*([가-힣·,/.~\- ]{2,24}?)(?=\s*(?:급여|근무|직책|연봉|모집|$))")


# 본문에 명시된 대리급 이상 요건(우대 포함)
BODY_SENIOR_RE = re.compile(r"(?:대리|과장|차장|부장|책임|수석)\s*급|(?:대리|과장|차장|부장)\s*(?:이상|~|-)")


TITLE_YEARS_RE = re.compile(r"(\d{1,2})\s*(?:[-~]\s*\d{1,2}\s*)?년\s*(?:이상|↑|차|경력|\))|경력\s*(\d{1,2})\s*[-~]")


def senior_rank(p: Posting) -> bool:
    """대리급 이상이 명시된 공고인가 (제목·직급 표기·본문, 우대 표기 포함). 기술사 우대는 제외하지 않는다.
    직급 표기에 사원·신입을 함께 뽑는다고 되어 있으면 제외하지 않는다."""
    title = p.title
    if SENIOR_RANK_RE.search(title) and not JUNIOR_RANK_RE.search(title):
        return True
    for m in BODY_SENIOR_RE.finditer(p.detail_text or ""):
        near = p.detail_text[max(0, m.start() - 12):m.end() + 4]
        if not JUNIOR_RANK_RE.search(near):
            return True
    m = RANK_FIELD_RE.search(p.detail_text or "")
    field_ = m.group(1) if m else ""
    if p.source == "피플앤잡":
        field_ = p.extra.get("career", "") or field_
    return bool(SENIOR_RANK_RE.search(field_) and not JUNIOR_RANK_RE.search(field_))


LINKEDIN_EXEC_RE = re.compile(r"(?<![A-Za-z])(?:Director|Head\s+of|VP|Vice\s+President|Chief)(?![A-Za-z])", re.I)


def level_of(p: Posting, text):
    lv = p.level
    if p.source == "LinkedIn":
        # 브라우저 작업이 넘긴 값을 그대로 쓴다. 'Manager'는 외국계에서 실무 담당 직함이라 제외하지 않고,
        # Director 이상만 경력으로 본다. 경력 요건을 아직 못 읽은 공고('경력 요건 확인 필요')는 싣는다.
        if LINKEDIN_EXEC_RE.search(p.title):
            p.extra["senior"] = True
            return "경력"
        return lv or "경력 요건 확인 필요"
    if senior_rank(p):
        p.extra["senior"] = True
        return "경력"
    # 제목의 '3년 이상', '2-5년 경력', '(10~20년)' 등 2년 이상 경력 요건
    yrs = [int(m.group(1) or m.group(2)) for m in TITLE_YEARS_RE.finditer(p.title)]
    if yrs and min(yrs) >= 2 and not NEWBIE_RE.search(p.title):
        return "경력"
    if re.search(r"신입\s*[Xx×]|신입\s*불가", p.title) or (
            CAREER_ONLY_RE.search(p.title) and not NEWBIE_RE.search(p.title)):
        return "경력"
    if p.source == "링커리어":
        jt = set(p.extra.get("jobTypes", []))
        if jt and jt <= {"EXPERIENCED", "CONTRACT"} and "EXPERIENCED" in jt:
            return "경력"
        return "인턴" if "INTERN" in jt else "신입"
    if lv in ("전체", "무관", "경력무관") or re.search(r"경력\s*무관", lv):
        return "경력무관"
    if "신입" in lv and "경력" in lv:
        return "신입·경력"
    if "신입" in lv:
        return "신입"
    if "인턴" in lv:
        return "인턴"
    if "경력" in lv:
        # 목록엔 '경력'이어도 본문에 '신입 가능'이면 살린다
        return "신입·경력" if re.search(r"신입\s*(가능|지원\s*가능)", text) else "경력"
    head = f"{p.title} {p.listing_text}"
    if re.search(r"신입|인턴|졸업\s*예정|채용연계|채용형", head):
        return "인턴" if "인턴" in head else "신입"
    if CAREER_ONLY_RE.search(p.title):
        return "경력"
    return "신입" if p.extra.get("posted") is not None else "확인 필요"


def _name_hit(name, words):
    return any(re.search(rf"(?<![가-힣A-Za-z]){re.escape(w)}", name) for w in words)


def _group_tag(title):
    """제목 머리의 [GS계열사], [DB월드/DB그룹] 같은 계열 표기 (외국계 표기가 함께면 제외)."""
    if re.search(r"대기업\s*계열", title):
        return True
    for tag in re.findall(r"\[([^\]]+)\]", title):
        parts = [x.strip() for x in tag.split("/")]
        if "외국계" not in parts and any(re.search(r"(?:계열사?|그룹)$", x) for x in parts):
            return True
    return False


def company_groups(p: Posting, text):
    """['대기업 계열', '외국계'] 중 해당하는 것 (둘 다일 수 있음)."""
    name = re.sub(r"\(주\)|㈜|주식회사|\s", "", p.company)
    groups = []
    if (p.company_type == "대기업" or re.search(r"기업\s*(?:구분|형태)\s*대기업", text)
            or _group_tag(p.title) or _name_hit(name, BIG_GROUPS)):
        groups.append("대기업 계열")
    if (p.company_type == "외국계" or re.search(r"기업\s*(?:구분|형태)\s*외국계|외국인\s*투자\s*기업", text)
            or re.search(r"외국계|외투기업", p.title) or _name_hit(name, FOREIGN_NAMES)
            or re.search(r"코리아.*(?:\(유\)|유한)|(?:\(유\)|유한회사).*코리아|(?<![가-힣])(?:Korea|Inc\.?|Ltd\.?|GmbH|LLC)(?![A-Za-z])", p.company)):
        groups.append("외국계")
    return groups


def classify_company(p: Posting, text):
    """행 강조 색: A(데이터센터·하이테크·삼성·하이닉스) > B(대기업 계열) > F(외국계)."""
    p.extra["groups"] = company_groups(p, text)
    if HILITE_A_RE.search(f"{p.company} {p.title} {p.listing_text} {p.extra.get('sector', '')}"):
        return "A"
    if "대기업 계열" in p.extra["groups"]:
        return "B"
    if "외국계" in p.extra["groups"]:
        return "F"
    return ""


def guess_company(title):
    title = re.sub(r"^\s*(?:\[\s*(?:채용|모집|인턴|공채|일반공지)\s*\]\s*)+", "", title)
    title = re.sub(r"^\s*(?:20)?\d{2}\s*년(?:도)?\s*(?:[상하]반기)?\s*", "", title)
    m = re.match(r"^\s*[\[\(【]([^\]\)】]{2,30})[\]\)】]", title)
    if m:
        first = clean(re.split(r"[/,]", m.group(1))[0])
        if not re.search(r"채용|모집|공고|정규|계약|인턴|신입|대외|일반공지", first):
            return first
    m = re.match(r"^\s*((?:\(주\)|㈜|주식회사)?\s*[가-힣A-Za-z&][가-힣A-Za-z0-9&]{1,14}(?:\(주\)|㈜)?)\s", title)
    if m and not re.match(r"제\s*\d", m.group(1).strip()):
        return clean(m.group(1))
    return ""


def analyze(p: Posting, today):
    text = p.detail_text
    detail_fields(p)
    if p.source in ("피플앤잡", "기업 채용 페이지"):
        foreign_level(p)
    if not p.company:
        p.company = guess_company(p.title)
    p.employment = employment_of(p, f"{p.listing_text} {text[:4000]}")
    p.level = level_of(p, text)
    qual = section(text, QUAL_HEAD)
    pref = section(text, PREF_HEAD, 180)
    p.qualification = summarize_qual(qual, text[:6000])
    if p.source == "사람인" and p.extra.get("cond"):
        edu = p.extra["cond"][2] if len(p.extra["cond"]) > 2 else ""
        if edu and "학력" not in p.qualification:
            p.qualification = " / ".join(filter(None, [p.qualification, f"학력: {edu}"]))
    if p.extra.get("edu") and "학력" not in p.qualification:
        p.qualification = " / ".join(filter(None, [re.sub(r"^경력\s*\S+\s*", "", p.qualification), f"학력: {p.extra['edu']}"]))
    if p.source == "워커" and "학력" not in p.qualification:
        edu = p.extra.get("exp_edu", "").split(" ", 1)[-1]
        p.qualification = " / ".join(filter(None, [p.qualification, f"학력: {edu}"]))
    if pref:
        certs = uniq(m.group(0) for m in CERT_RE.finditer(pref))
        p.preferred = (", ".join(certs) + " · " if certs else "") + pref[:110]
    ref = safe_date(*map(int, p.extra["posted"].split("-"))) if p.extra.get("posted") else today
    disp, d = parse_deadline(p.deadline, ref)
    if not disp and p.extra.get("posted") is not None:
        disp, d = parse_deadline(p.title, ref)
    p.deadline = disp or p.deadline or "확인 필요"
    p.deadline_date = d.isoformat() if d else ""
    p.hilite = classify_company(p, text)
    p.extra["salary"] = "" if salary_of(p) == NO_SALARY else salary_of(p)
    p.extra["listed"] = listed_market(p)
    p.certs = sorted({f"{m.group(1)}안전기사" for m in CERT_KEY_RE.finditer(f"{p.title} {p.listing_text} {text}")})
    if ISO45001_RE.search(f"{p.title} {text}"):
        p.certs.append("ISO 45001")
    blob = f"{p.title} {p.listing_text} {text}"
    p.prefs = [lab for lab, rx in (("외국어·영어", LANG_RE), ("NEBOSH", NEBOSH_RE), ("IOSH", IOSH_RE), ("CSP", CSP_RE)) if rx.search(blob)]
    pref_sec = section(text, PREF_HEAD, 600)
    p.extra["ai"] = bool(AI_RE.search(pref_sec) or AI_NEAR_PREF_RE.search(text))
    p.extra["benefits"] = benefits_of(f"{p.listing_text} {text}")
    rank = top100_rank(p.company)
    p.extra["top100"] = rank
    sector = f"{p.listing_text[:12]} {p.extra.get('biz', '')}"
    mixed = norm_corp(p.company) in MIXED_TOP100  # 건설 외 주력 사업이 있는 시평 100위 업체
    by_name = rank and not mixed or re.search(r"건설\s*부문|건설사업", f"{p.company} {p.title}")
    p.industry = "건설" if (by_name or p.source == "워커" or CONSTR_NAME_RE.search(p.company)
                            or re.search(r"건설·건축|건설업|건축|토목|공사업", sector)) else "일반 산업"


OTHER_TRADE_RE = re.compile(r"공무|시공|공사\s*관리|현장\s*소장|현장\s*대리인|품질|설계|전기|기계|설비|토목|건축|조경|감리|생산|용접|정비|"
                            r"배관|도장|측량|구매|총무|사무|회계|인사|물류|운전|시설\s*관리|CAD", re.I)


def other_trade(p: Posting) -> bool:
    """안전이 아닌 공종·직무를 모집하는 공고인가 (제목 기준, 우대 표기는 제외하고 판단)."""
    title = PREF_IN_TITLE_RE.sub(" ", p.title)
    return bool(OTHER_TRADE_RE.search(title)) and not re.search(r"안전\s*(?:관리|보건|담당|팀|환경)|보건\s*관리|HSE|EHS|SHE", title, re.I)


def relevant(p: Posting):
    """안전 직무 공고인가. True / False / None(상세 본문을 봐야 앎).

    - 제목에 안전·HSE 키워드, 또는 목록에 산업안전기사·건설안전기사가 보이면 True
    - 그룹 공채인데 직무 태그에 안전이 있으면 True
    - HSE·EHS·자격증 검색어로 걸린 공고는 상세 본문에서 자격증/HSE 언급을 확인(None)
    """
    tags = p.extra.get("sector", "") if p.source == "사람인" else p.listing_text
    # 제목의 '(안전관리 우대)' 같은 표기는 안전관리 우대가 명시된 것으로 보고 살린다
    if any(re.search(r"안전\s*관리", m.group(0)) for m in PREF_IN_TITLE_RE.finditer(p.title)):
        return True
    title = PREF_IN_TITLE_RE.sub(" ", p.title)
    if other_trade(p) and not re.search(r"안전|보건|HSE|EHS|EH&S|SHE", title, re.I):
        return None if p.extra.get("query") else False  # 타공종 모집 → 본문의 우대 명시 여부로 판단
    if SAFETY_RE.search(title) or CERT_KEY_RE.search(f"{p.title} {tags}"):
        return True
    if re.search(r"공채|공개\s*채용|신입\s*(사원|직원)", title) and SAFETY_RE.search(tags):
        return True
    if p.extra.get("query"):  # 검색어로 걸렸지만 제목만으로는 모를 때 → 상세 본문 확인
        return None
    return False


# 담당 업무 항목에 '안전'이 있는지 (정보보안·안전하게·안전벨트 같은 말과 단순 '안전수칙 준수'는 빼고 본다)
DUTY_SAFETY_RE = re.compile(r"(?<!보)안전(?![하한히]|벨트|유리|용품|장치|성\s*(?:평가|시험|정보))|보건\s*관리|산업\s*위생|유해\s*요인|근골격|작업\s*환경\s*측정|"
                            r"(?<![A-Za-z])(?:HSE|EHS|EH&S|SHE|HSEQ|QHSE|HSSE|[Ss]afety|SAFETY)(?![A-Za-z])")
DUTY_COMPLY_RE = re.compile(r"(?:안전|EHS|HSE)[^.\n·•\-]{0,20}(?:규정|수칙|규칙|요구\s*사항|정책)[^.\n·•\-]{0,20}(?:준수|기반|따라|따른)", re.I)
DUTY_STOP_RE = re.compile(rf"{STOP}|{QUAL_HEAD}")


def duty_text(t: str) -> str:
    """본문의 모든 담당 업무(주요 업무·업무 내용·모집 분야) 항목을 이어 붙인다."""
    out = []
    for m in re.finditer(rf"(?:{DUTY_HEAD})\s*[:：]?", t):
        body = t[m.end():m.end() + 800]
        st = DUTY_STOP_RE.search(body, 5)
        out.append(body[:st.start()] if st else body)
    return clean(" ".join(out))


def title_safe(p: Posting) -> bool:
    title = PREF_IN_TITLE_RE.sub(" ", p.title)
    return bool(SAFETY_RE.search(title) or CERT_KEY_RE.search(p.title))


def duty_verdict(p: Posting):
    """제목에 안전 직무가 없을 때 담당 업무로 판정. True(안전 있음) / False(없음) / None(본문·항목을 못 읽음)."""
    if title_safe(p) or not p.detail_text:
        return None
    d = duty_text(p.detail_text[:12000])
    if len(re.sub(r"\W", "", d)) < 10:
        return None
    return bool(DUTY_SAFETY_RE.search(DUTY_COMPLY_RE.sub(" ", d)))


DUTY_CHECK_NOTE = "담당 업무 항목을 읽지 못함 — 안전 업무 포함 여부 확인 필요"


def duty_gate(p: Posting) -> str:
    """담당 업무 기준 판정: 'ok'(싣기) / 'drop'(제외) / 'check'(직무 확인 필요) / ''(제목으로 이미 안전 직무)."""
    if p.extra.get("manual") or p.extra.get("posted") is not None or title_safe(p):
        return ""
    v = duty_verdict(p)
    return "ok" if v else "drop" if v is False else "check"


def relevant_after_detail(p: Posting) -> bool:
    r = relevant(p)
    if r is not None:
        return r
    t = p.detail_text[:12000]
    if CERT_KEY_RE.search(t) or NEBOSH_RE.search(t) or IOSH_RE.search(t) or INCLUDE_RE.search(t):
        return True
    # '안전관리' 우대가 명시돼 있으면 살린다
    pref = section(t, PREF_HEAD, 400)
    if re.search(r"안전\s*관리", pref) or re.search(r"안전\s*관리[^.\n]{0,30}우대", t):
        return True
    # 타공종을 모집하면서 '안전관리 경험/경력'만 요구하는 공고는 제외 (실제 안전관리 업무 병행은 인정)
    body = re.sub(r"안전\s*관리[^.\n]{0,15}(?:경험|경력)", " ", t) if other_trade(p) else t
    secs = " ".join(section(body, h, 400) for h in (QUAL_HEAD, DUTY_HEAD))
    if SAFETY_DUTY_RE.search(body) or re.search(r"안전\s*관리", secs):
        return True
    # HSE/EHS는 직무·팀 이름으로 쓰였을 때만 (단순 'EHS 규정 준수' 같은 언급은 제외).
    # 타공종 모집 공고에서 회사 EHS팀이 언급된 것만으로는 살리지 않는다
    if other_trade(p):
        return False
    return bool(HSE_ROLE_RE.search(t))


PUBLIC_CORP_RE = re.compile(r"(?:공단|공사|진흥원|기술원|연구원|안전원|재단)(?:\(.*?\))?$")  # 공공기관은 제외하지 않는다


def excluded_corp(p: Posting) -> bool:
    """회사명에 제외 용어(EXCLUDE_CORP_TERMS)가 있는 민간 업체인가. 공공기관은 제외하지 않는다."""
    name = re.sub(r"\s|\(주\)|㈜|주식회사", "", p.company or "")
    if not EXCLUDE_CORP_RE.search(name):
        return False
    return not ("공공" in p.company_type or PUBLIC_CORP_RE.search(name))


# 브리핑 화면에서 체크 후 삭제한 공고 (Routine이 페이지 DB에서 safety_jobs/excluded.json으로 옮겨 둔다)
EXCLUDED_PATH = Path(__file__).with_name("excluded.json")
EXCLUDED_URLS: set = set()
EXCLUDED_KEYS: set = set()


def _ex_key(company, title):
    return norm_company(company or "") + "|" + norm_title(title or "", company or "")


def load_excluded():
    try:
        items = json.loads(EXCLUDED_PATH.read_text(encoding="utf-8")).get("items", [])
    except (OSError, ValueError):
        return 0
    for it in items:
        if it.get("url"):
            EXCLUDED_URLS.add(it["url"])
        if it.get("company") or it.get("title"):
            EXCLUDED_KEYS.add(_ex_key(it.get("company"), it.get("title")))
    return len(items)


def user_excluded(p: Posting) -> bool:
    return p.url in EXCLUDED_URLS or _ex_key(p.company, p.title) in EXCLUDED_KEYS


PUBLIC_NAME_RE = re.compile(r"(?:공사|공단|발전|공기업|진흥원|기술원)(?:\(주\)|㈜)?$|^한국")
ENERGY_CHEM_RE = re.compile(r"에너지|화학|케미칼|정유|오일|가스|발전|석유|플랜트|원자력|전력")
GONGCHAE_RE = re.compile(r"공채|공개\s*채용|신입\s*사원|하반기\s*(?:신입|채용)|대졸\s*신입|채용형\s*인턴")


def needs_check_reason(p: Posting) -> str:
    """안전 직무로 확정되진 않았지만 놓치면 안 되는 공고인가 → '직무 확인 필요'로 남긴다."""
    name = re.sub(r"\s|\(주\)|㈜|주식회사", "", p.company or "")
    focus = bool(p.extra.get("groups") or p.extra.get("listed") or p.extra.get("top100") or PUBLIC_NAME_RE.search(name))
    if not focus:
        return ""
    t = (p.detail_text or "")[:12000]
    text = " ".join([p.title, p.listing_text] + [section(t, h, 400) for h in (DUTY_HEAD, QUAL_HEAD, PREF_HEAD)])
    if GONGCHAE_RE.search(p.title) and (p.industry == "건설" or ENERGY_CHEM_RE.search(f"{name} {p.extra.get('biz', '')}")):
        return "건설·에너지 공채 — 안전 직무 포함 여부 확인 필요"
    if p.extra.get("query") and SAFETY_RE.search(text):
        return "안전 키워드에 걸렸지만 직무 확인 필요"
    return ""


def keep(p: Posting, today) -> tuple[bool, str]:
    if user_excluded(p):
        return False, "사용자 삭제"
    if excluded_corp(p):
        return False, "제외 업체명"
    blob = f"{p.title} {p.listing_text} {p.extra.get('sector', '')}"
    if p.extra.get("posted") is not None:  # 학과 게시판: 최근 글 + 채용 공고 + 안전 직무
        posted = safe_date(*map(int, p.extra["posted"].split("-"))) if p.extra["posted"] else None
        if posted and (today - posted).days > 75:
            return False, "오래된 게시글"
        if re.search(r"설명회|특강|공모|대외|세미나|박람회|사이트\s*안내|교육생|장학", p.title):
            return False, "채용 공고 아님"
        if not re.search(r"채용|모집|인턴|신입", p.title):
            return False, "채용 공고 아님"
        if not SAFETY_RE.search(f"{blob} {p.detail_text[:8000]}"):
            return False, "안전 직무 아님"
    elif p.extra.get("manual"):
        pass
    else:
        g = duty_gate(p)
        if g == "drop":
            return False, "담당 업무에 안전 없음"
        if g == "ok":
            pass  # 담당 업무에 '안전'이 있으면 안전 직무로 싣는다
        elif not relevant_after_detail(p):
            why = needs_check_reason(p)
            if not why:
                return False, "안전 직무 아님"
            p.extra["needs_check"] = True
            p.extra["check_note"] = why
        elif g == "check":
            p.extra["needs_check"] = True
            p.extra["check_note"] = DUTY_CHECK_NOTE
    if NON_HSE_SAFETY_RE.search(p.title):
        return False, "안전 직무 아님"
    if p.extra.get("need_korea") and not KOREA_LOC_RE.search(p.extra.get("loc", "")):
        return False, "한국 근무 아님"
    if SALES_RE.search(p.title):
        return False, "영업직"
    if WATCH_RE.search(f"{p.title} {p.listing_text} {p.detail_text}"):
        return False, "감시단"
    if p.industry == "건설" and not p.extra.get("top100"):
        return False, "건설사(시평 100위 밖)"
    if p.level == "경력":
        return False, "대리급 이상" if p.extra.get("senior") else "경력직"
    if p.employment == "계약직" and not contract_ok(p):
        return False, "계약직(관심 기업 외)"
    if p.deadline_date and p.deadline_date < today.isoformat():
        return False, "마감"
    return True, ""


def norm_company(c):
    return re.sub(r"\(주\)|㈜|주식회사|\s|\(.*?\)", "", c or "").lower()


def norm_title(t, corp):
    t = re.sub(r"[\[\]\(\)【】<>『』\"'·,.\-_/|:~]|\s|20\d{2}년?|하반기|상반기|채용|모집|공고|안내", "", t or "")
    return t.replace(corp, "") if corp else t


def is_dup(p, kept):
    c, t = norm_company(p.company), norm_title(p.title, norm_company(p.company))
    for q in kept:
        qc = norm_company(q.company)
        if c and qc and (c in qc or qc in c):
            qt = norm_title(q.title, qc)
            if difflib.SequenceMatcher(None, t, qt).ratio() >= 0.6:
                return True
    return False


# ---------------------------------------------------------------- 출력
# ---------------------------------------------------------------- 연봉 · 대기업 신입 공채
_AMT = r"\d[\d,\.]*(?:\s*(?:만\s*원|만원|원|억))?(?:\s*[~\-–]\s*\d[\d,\.]*)?\s*(?:만\s*원|만원|원|억)(?:\s*(?:이상|이하|내외|수준|부터|전후))?"
_WON = r"₩\s*\d[\d,]*"
SALARY_AMT_RE = re.compile(rf"(?:연봉|연\s*급|급여|월\s*급여|월급|초봉|초임)\s*(?:조건|기준)?\s*[:：]?\s*(?:\(?\s*)?((?:(?:일급|월급|시급|주급|연봉)\s*)?(?:약\s*)?(?:{_AMT}|{_WON}))")
_DECIDE = (r"회사\s*내규(?:에\s*(?:따[라른름]\w*|의\w*))?|내규에\s*(?:따[라른름]\w*)|면접\s*[후시]\s*(?:연봉\s*)?(?:결정|협의)|"
           r"추후\s*(?:협의|결정)|협의\s*후\s*결정|협의\s*결정|협의")
SALARY_TXT_RE = re.compile(rf"(?:연봉|연\s*급|급여|보수|월급)[^.\n]{{0,12}}?({_DECIDE})")
SALARY_LOOSE_RE = re.compile(r"(회사\s*내규(?:에\s*(?:따[라른름]\w*))?|면접\s*후\s*(?:연봉\s*)?(?:결정|협의))")
NO_SALARY = "연봉 미기재"


def salary_of(p):
    """공고 본문에서 연봉(금액 · 회사 내규 · 면접 후 결정 등)을 찾는다. 없으면 '연봉 미기재'."""
    if "salary" in p.extra:
        return p.extra["salary"] or NO_SALARY
    for t in (p.detail_text, p.listing_text):
        t = clean(t)
        for rx in (SALARY_AMT_RE, SALARY_TXT_RE, SALARY_LOOSE_RE):
            m = rx.search(t)
            if m:
                return re.sub(r"^면접\s*([후시])\s*", r"면접 \1 ", clean(m.group(1)))[:40]
    return NO_SALARY


# ---------------------------------------------------------------- 기업별 신입사원 초봉 (잡코리아 기업 연봉정보)
STARTER: dict = {}          # norm_corp(업체명) → {"id", "pay", "year", "checked"}
STARTER_MAX_LOOKUPS = 250   # 실행당 새로 조회할 기업 수 (나머지는 다음 실행)
STARTER_MATCH_V = 2         # 매칭 규칙 버전 — 이전 규칙으로 못 찾은 업체는 바로 다시 조회
STARTER_TTL_DAYS, STARTER_MISS_DAYS = 30, 14


def _jk_company_id(f, name):
    """잡코리아 기업 검색에서 업체명이 같은 기업의 urlId."""
    q = re.sub(r"\(.*?\)|㈜|주식회사|유한회사", "", name).strip()
    if not q:
        return None
    t = f.get(f"https://www.jobkorea.co.kr/Search/?stext={quote(q)}&tabType=corp", tries=2).replace('\\"', '"')
    want = norm_corp(name)
    cands = [(norm_corp(m.group(1)), m.group(2))
             for m in re.finditer(r'"name":"([^"]+)","businessNo":"[^"]*".{0,600}?"urlId":"(\d+)"', t)]
    cands += [(norm_corp(BeautifulSoup(m.group(2), "html.parser").get_text()), m.group(1))
              for m in re.finditer(r'href="https://www\.jobkorea\.co\.kr/Company/(\d+)"[^>]*>(.{0,300}?)</a>', t, re.S)]
    for n, cid in cands:  # 1) 정규화 이름 일치
        if n == want:
            return cid
    # 2) 완화: 한쪽 이름이 다른 쪽에 포함(짧은 쪽 3자 이상, 길이 차 6자 이내) — 가장 비슷한 것
    best, score = None, 0.0
    for n, cid in cands:
        if not n:
            continue
        short, long_ = sorted((n, want), key=len)
        if len(short) >= 3 and short in long_ and len(long_) - len(short) <= 6:
            r = difflib.SequenceMatcher(None, n, want).ratio()
            if r > score:
                best, score = cid, r
    if best:
        return best
    # 3) 검색 결과 기업이 하나뿐이고 이름이 매우 비슷하면 채택
    uniq = {cid: n for n, cid in cands if n}
    if len(uniq) == 1:
        cid, n = next(iter(uniq.items()))
        if difflib.SequenceMatcher(None, n, want).ratio() >= 0.75:
            return cid
    return None


def _jk_starter_pay(f, cid):
    """기업 연봉정보 페이지의 '신입사원 초봉 N 만원'과 기준 연도."""
    txt = soup_text(f.get(f"https://www.jobkorea.co.kr/company/{cid}/salary", tries=2))
    m = re.search(r"신입\s*사원\s*초봉\s*([\d,]+)\s*만\s*원", txt)
    if not m or m.group(1).replace(",", "") in ("", "0"):
        return None, None
    y = re.search(r"(20\d{2})년\s*기준", txt)
    return f"{m.group(1)}만원", (y.group(1) if y else "")


# 인터넷 조사로 확인한 신입 초봉 (잡코리아 값보다 우선). safety_jobs/starter_manual.json
STARTER_MANUAL_PATH = Path(__file__).with_name("starter_manual.json")
STARTER_MANUAL: dict = {}


def load_starter_manual():
    try:
        items = json.loads(STARTER_MANUAL_PATH.read_text(encoding="utf-8")).get("items", [])
    except (OSError, ValueError):
        return
    for it in items:
        if it.get("pay") or it.get("suppress"):  # suppress: 근거 없는 잡코리아 값 숨김
            for name in [it.get("company", "")] + list(it.get("aliases", [])):
                if norm_corp(name):
                    STARTER_MANUAL[norm_corp(name)] = it


def load_starter(cache: Path):
    try:
        STARTER.update(json.loads(cache.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        pass


def fill_starter(f, postings, today, cache: Path):
    """공고 업체별 신입 초봉을 채운다 (캐시 30일, 못 찾은 업체는 14일 뒤 재조회)."""
    looked = 0
    for p in postings:
        key = norm_corp(p.company)
        if not key or len(key) < 2:
            continue
        hit = STARTER.get(key)
        if hit:
            age = (today - dt.date.fromisoformat(hit["checked"])).days
            stale_miss = not hit.get("id") and hit.get("v", 1) < STARTER_MATCH_V
            if not stale_miss and age <= (STARTER_TTL_DAYS if hit.get("pay") else STARTER_MISS_DAYS):
                continue
        if looked >= STARTER_MAX_LOOKUPS:
            continue
        looked += 1
        rec = {"id": None, "pay": None, "year": "", "checked": today.isoformat(), "v": STARTER_MATCH_V}
        try:
            rec["id"] = (hit or {}).get("id") or _jk_company_id(f, p.company)
            if rec["id"]:
                rec["pay"], rec["year"] = _jk_starter_pay(f, rec["id"])
            time.sleep(0.3)
        except Exception as e:
            print(f"[starter] {p.company}: {e}", file=sys.stderr)
            continue
        STARTER[key] = rec
    load_starter_manual()
    for p in postings:
        man = STARTER_MANUAL.get(norm_corp(p.company))
        if man and man.get("suppress") and not man.get("pay"):
            p.extra["starter"] = ""
            p.extra.pop("starter_url", None)
            continue
        if man:  # 인터넷 조사 값 우선
            p.extra["starter"] = f"신입 초봉 {man['pay']}" + (f" ({man['year']}, {man.get('source', '웹 조사')})" if man.get("year") else f" ({man.get('source', '웹 조사')})")
            p.extra["starter_url"] = man.get("url", "")
            continue
        hit = STARTER.get(norm_corp(p.company)) or {}
        p.extra["starter"] = (f"신입 초봉 {hit['pay']}" + (f" ({hit['year']})" if hit.get("year") else "")) if hit.get("pay") else ""
        if hit.get("pay"):
            p.extra["starter_url"] = f"https://www.jobkorea.co.kr/company/{hit['id']}/salary"
    cache.write_text(json.dumps(STARTER, ensure_ascii=False, indent=0), encoding="utf-8")
    return looked


def pay_text(p):
    """표시용: 공고 기재 연봉 + 기업 신입 초봉."""
    return " · ".join(x for x in (salary_of(p), p.extra.get("starter", "")) if x)


BIGCORP_TITLE_RE = re.compile(r"공채|공개\s*채용|신입\s*사원|하반기\s*신입|채용\s*연계")


def is_bigcorp_entry(p):
    """대기업 신입 공채: 대기업 계열이면서 경력직이 아니고, 신입이거나 제목에 공채류 표기가 있는 공고."""
    return ("대기업 계열" in p.extra.get("groups", []) and p.level != "경력"
            and (p.level == "신입" or bool(BIGCORP_TITLE_RE.search(p.title))))


BADGE = {"A": "🔴 ", "B": "🔵 ", "F": "🌐 ", "": ""}
GROUPS = [("정규직", "[정규직]"), ("계약직", "[계약직]"), ("인턴", "[인턴]"), ("기타/미표기", "[고용형태 미표기]")]
def saramin_today(p, today):
    """사람인에서 오늘 처음 찾은 공고 → '신규 공고'에만 싣는다."""
    return p.source == "사람인" and p.extra.get("first_seen") == today.isoformat()


def group_key(p):
    """공고 표 묶음 키. 대기업 신입 공채는 계약직·인턴이 아니면 정규직에 넣는다."""
    if is_bigcorp_entry(p) and p.employment not in ("계약직", "인턴"):
        return "정규직"
    return p.employment if p.employment in dict(GROUPS) else "기타/미표기"


def md_check(p):
    if not p.extra.get("needs_check"):
        return ""
    return " ⚠️ **[직무 확인 필요]** " + md_cell(p.extra.get("check_note", ""))


def md_src(p):
    return p.source if p.url.startswith("manual:") else f"[{p.source}]({p.url})"


def employment_groups(postings, today):
    """공고 표 묶음: 정규직·계약직·(인턴)·고용형태 미표기. 직무 확인 필요 공고도 여기에 표시와 함께 싣고,
    사람인에서 오늘 처음 찾은 공고는 '신규 공고'에만 싣는다."""
    rest = [p for p in postings if not saramin_today(p, today)]
    out = [(key, tag, sorted([p for p in rest if group_key(p) == key], key=sort_key)) for key, tag in GROUPS]
    return [g for g in out if g[2]]


def check_pill(p):
    if not p.extra.get("needs_check"):
        return ""
    e = html.escape
    note = p.extra.get("check_note", "")
    return '<span class="pill pck">직무 확인 필요</span>' + (f'<small class="ckn">{e(note)}</small>' if note else "")


def big_pill(p):
    return '<span class="pill pb">대기업 신입 공채</span>' if is_bigcorp_entry(p) else ""


def href(p):
    return "" if p.url.startswith("manual:") else p.url
LEGEND = ("🔴 데이터센터·하이테크·삼성·하이닉스 관련 · 🔵 대기업 계열사 · 🌐 외국계 회사 (여럿 해당하면 🔴 > 🔵 > 🌐, 업체명 옆에 [대기업 계열]/[외국계] 표기) · "
          "🟣 외국어·영어 능통 / NEBOSH / IOSH / CSP 우대 (🔴·🔵와 함께 표시될 수 있음) · [코스피]/[코스닥] 상장사 · 🤖 AI 역량 우대")


def md_cell(s):
    return clean(s).replace("|", "\\|") or "-"


def sort_key(p):
    return ({"A": 0, "B": 1, "F": 2}.get(p.hilite, 3), p.deadline_date or "9999")


def deadline_md(p, today):
    """3일 이내 마감은 ⏰·굵게·D-n 으로 표시 (마크다운은 글자색을 못 쓰므로 HTML에서만 붉은색)."""
    if p.deadline_date:
        left = (dt.date.fromisoformat(p.deadline_date) - today).days
        if left <= 3:
            return f"⏰ **{md_cell(p.deadline)} (D-{left})**" if left else f"⏰ **{md_cell(p.deadline)} (오늘 마감)**"
    return md_cell(p.deadline)


def render_md(postings, failures, now, stats):
    L = [f"# 안전관리자 채용 브리핑 — {now:%Y-%m-%d (%a) %H:%M} KST", ""]
    n_gen = sum(p.industry == "일반 산업" for p in postings)
    n_cert = sum(bool(p.certs) for p in postings)
    n_pref = sum(bool(p.prefs) for p in postings)
    L.append(f"신입·경력무관·인턴 공고 **{len(postings)}건** (경력직·마감 제외, 중복은 상위 사이트 우선) · "
             f"일반 산업체 {n_gen}건 · 건설 {len(postings) - n_gen}건 · 산업/건설안전기사·ISO 45001 명시 {n_cert}건 · "
             f"🟣 외국어·NEBOSH·IOSH·CSP 우대 {n_pref}건")
    L += ["", "건설사는 2026년 시공능력평가 상위 100개사(토목건축)만 싣습니다."]
    L += ["", f"범례: {LEGEND} · 🆕 지난 보고({last_report_date(now.date()):%m/%d}) 이후 추가", ""]
    new = sorted([p for p in postings if is_new(p, now.date())], key=sort_key)
    L += [f"## 🆕 신규 공고 {len(new)}건 (지난 보고 {last_report_date(now.date()):%m/%d} 이후)", ""]
    if new:
        L += ["| 업체명 | 공고명 | 고용형태 · 연봉 | 접수기한 | 출처 |", "|---|---|---|---|---|"]
        L += [f"| {BADGE[p.hilite]}{md_cell(p.company)}{' [대기업 신입 공채]' if is_bigcorp_entry(p) else ''} | {md_cell(p.title)}{md_check(p)} | {p.employment}<br>{md_cell(pay_text(p))} | {deadline_md(p, now.date())} | {md_src(p)} |" for p in new]
    else:
        L.append("_새로 추가된 공고가 없습니다._")
    L.append("")
    for key, tag, rows in employment_groups(postings, now.date()):
        L += [f"## {tag} {len(rows)}건", ""]
        L.append("| 구분 · 연봉 | 업체명 | 공고명 | 지원 자격 (학과·자격·영어·학력) | 우대 사항 | 접수기한 | 출처 |")
        L.append("|---|---|---|---|---|---|---|")
        for p in rows:
            corp = ("🆕 " if is_new(p, now.date()) else "") + BADGE[p.hilite] + (f"**{md_cell(p.company)}**" if p.hilite else md_cell(p.company))
            corp += "".join(f" [{g}]" for g in p.extra.get("groups", []))
            corp += " [대기업 신입 공채]" if is_bigcorp_entry(p) else ""
            corp += f" [{p.extra['listed']}]" if p.extra.get("listed") else ""
            if p.industry == "건설" and p.extra.get("top100"):
                corp += f" (시평 {p.extra['top100']}위)"
            cert = f"**[{'·'.join(p.certs)} 명시]** " if p.certs else ""
            cert += f"🟣 **[{'·'.join(p.prefs)} 우대]** " if p.prefs else ""
            cert += "🤖 **[AI 우대]** " if p.extra.get("ai") else ""
            cert += f"🏠 **[복지: {'·'.join(p.extra['benefits'])}]** " if p.extra.get("benefits") else ""
            L.append(f"| {md_cell(p.level)} · {md_cell(p.industry)}<br>{md_cell(pay_text(p))} | {corp} | {md_cell(p.title)}{md_check(p)} | {cert}{md_cell(p.qualification)} "
                     f"| {md_cell(p.preferred)} | {deadline_md(p, now.date())} | {md_src(p)}{' (이전 수집)' if p.extra.get('carried') else ''} |")
        L.append("")
    L += ["---", "", "**사이트별 수집 현황**", ""]
    for name, st in stats.items():
        L.append(f"- {name}: {st}")
    if failures:
        L += ["", "**수집 실패**", ""] + [f"- {n}: {e}" for n, e in failures]
    if CAREER_STATUS:
        L += ["", "**기업 채용 페이지**", "", "| 기업 | 결과 |", "|---|---|"] + [f"| {k} | {v} |" for k, v in CAREER_STATUS.items()]
    L += ["", "_지원 자격·우대 사항은 상세 페이지에서 자동 추출한 요약입니다. 지원 전 원문을 확인하세요._"]
    return "\n".join(L) + "\n"


HTML_CSS = """
/* 레이아웃: sticky 헤더 + 좌측 섹션 내비(데스크톱) + 콘텐츠 캔버스(KPI → 차트 → 흐름도 → 필터 → 표) */
:root{
  --primary:#0F6FFF; --primary-hover:#0E65E8; --primary-active:#0B4FB5;
  --bg-page:#FFFFFF; --canvas:#EEF1F5; --surface:#FFFFFF; --alt1:#F2F3F6; --alt2:#E2E4E9;
  --text-strong:#000000; --text:#1C1C1C; --text-sub:#303030; --caption:#737373;
  --border:#E2E4E9; --border-strong:#CCD0D6; --divider:#E9EBEF;
  --success:#15B874; --warning:#FFA833; --error:#E63B3B; --purple:#B357FF; --sky:#00BDDE; --orange:#FE6F3F;
  --r-sm:8px; --r-md:12px; --r-lg:16px; --r-pill:9999px;
  --sh1:0 1px 3px rgba(0,0,0,.06);
  --font:"Pretendard Variable","Pretendard","Apple SD Gothic Neo","Noto Sans KR","Segoe UI",Roboto,-apple-system,sans-serif;
  --mono:ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --primary:#3F8CFF; --primary-hover:#0F6FFF; --primary-active:#0E65E8;
  --bg-page:#1D1F24; --canvas:#15171C; --surface:#1D1F24; --alt1:#282B33; --alt2:#333741;
  --text-strong:#FFFFFF; --text:#EBECED; --text-sub:#C4C4C4; --caption:#8A8A8A;
  --border:#333741; --border-strong:#4A505F; --divider:#282B33;
  --success:#44C690; --warning:#FFB95C; --error:#EB5E5E; --purple:#C279FF; --sky:#33CAE5; --orange:#FE8C65; color-scheme:dark}}
:root[data-theme="dark"]{
  --primary:#3F8CFF; --primary-hover:#0F6FFF; --primary-active:#0E65E8;
  --bg-page:#1D1F24; --canvas:#15171C; --surface:#1D1F24; --alt1:#282B33; --alt2:#333741;
  --text-strong:#FFFFFF; --text:#EBECED; --text-sub:#C4C4C4; --caption:#8A8A8A;
  --border:#333741; --border-strong:#4A505F; --divider:#282B33;
  --success:#44C690; --warning:#FFB95C; --error:#EB5E5E; --purple:#C279FF; --sky:#33CAE5; --orange:#FE8C65; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--canvas);color:var(--text);font:400 14px/1.55 var(--font);margin:0}
.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg-page);border-bottom:1px solid var(--border);
  display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;padding:12px 20px}
.top h1{font-size:18px;font-weight:700;margin:0;color:var(--text-strong)}
.top .when{font-size:12px;color:var(--caption);font-variant-numeric:tabular-nums}
.top .chip{margin-left:auto}
.edit-bar{display:flex;align-items:center;gap:6px}
.edit-bar button{height:32px;padding:0 12px;border:1px solid var(--border-strong);border-radius:var(--r-sm);background:var(--surface);color:var(--text-sub);font:600 13px var(--font);cursor:pointer}
.edit-bar button:hover{background:var(--alt1)} .edit-bar button[aria-pressed="true"]{background:var(--primary);border-color:var(--primary);color:#FFFFFF}
.edit-bar #edit-msg{font-size:12px;color:var(--caption)}
.icon-btn{width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;border:0;background:none;color:var(--text-sub);border-radius:var(--r-sm);cursor:pointer}
th.pickcell,td.pickcell{width:44px;text-align:center;padding-left:8px;padding-right:4px}
.pickcell input{width:16px;height:16px;margin:2px 0 0;cursor:pointer;accent-color:var(--primary)}
tr.xd{display:none!important} .ev.xd{display:none!important}
tr.xon{outline:2px solid var(--error);outline-offset:-2px}
.xbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-end;gap:8px;position:relative}
.top .xbar .xmsg{max-width:320px;text-align:right;line-height:1.35}
.xbar li button{white-space:nowrap;flex:none}
@media (max-width:719px){.top .xbar .xmsg:not(.ask){display:none}.top .xbar{width:100%;justify-content:flex-start}}
.xbar button{height:40px;padding:0 14px;border:1px solid var(--border-strong);border-radius:var(--r-sm);background:var(--surface);color:var(--text-sub);font:600 13px var(--font);cursor:pointer}
.xbar button.danger{border-color:var(--error);color:var(--error)} .xbar button.danger:not(:disabled):hover{background:color-mix(in srgb,var(--error) 10%,var(--surface))}
.xgrp{display:inline-flex;flex-wrap:wrap;align-items:center;gap:8px}
.xmsg{font-size:12px;color:var(--caption)} .xmsg.ask{font-size:14px;font-weight:600;color:var(--text-strong)}
.xlist{font-size:13px;color:var(--text-sub);position:relative}
.xlist summary{cursor:pointer;color:var(--text-sub);font-size:12px;font-weight:600;height:40px;display:flex;align-items:center;gap:4px;padding:0 10px;border:1px solid var(--border-strong);border-radius:var(--r-sm);list-style:none}
.xlist summary::-webkit-details-marker{display:none}
.xlist[open] ul{position:absolute;right:0;top:46px;z-index:6;width:min(420px,calc(100vw - 32px));background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);box-shadow:var(--sh2,0 2px 8px rgba(0,0,0,.08));padding:10px;margin:0}
.xlist ul:empty::before{content:"제외한 공고가 없습니다.";color:var(--caption);font-size:12px}
.xbar button.danger.solid{background:var(--error);border-color:var(--error);color:#FFFFFF}
.xbar button.danger.solid:not(:disabled):hover{background:var(--error);filter:brightness(.9)}
.xbar button:disabled{opacity:.45;cursor:not-allowed}
.xbar ul{list-style:none;display:grid;gap:4px;max-height:300px;overflow:auto}
.xbar li{display:flex;gap:8px;align-items:center;font-size:13px}
.xbar li button{height:28px;padding:0 10px;font-size:12px}
.icon-btn:hover{background:var(--alt1);color:var(--text-strong)}
.edit-bar .icon-btn{width:40px;height:40px;padding:0;border:0;background:none}
body.editing main [contenteditable="true"]{outline:1px dashed var(--border-strong);outline-offset:2px;cursor:text}
body.editing main [contenteditable="true"]:focus{outline:2px solid var(--primary)}
.shell{display:grid;grid-template-columns:220px minmax(0,1fr);min-height:100%}
.side{background:var(--bg-page);border-right:1px solid var(--border);padding:12px 0;position:sticky;top:57px;align-self:start;height:calc(100vh - 57px);overflow:auto}
.side .sec{font-size:12px;font-weight:600;color:var(--caption);padding:12px 20px 4px;letter-spacing:.02em}
.side a{display:flex;align-items:center;justify-content:space-between;height:44px;padding:0 20px;color:var(--text-sub);text-decoration:none;font-size:14px}
.side a:hover{background:var(--alt1)} .side a b{font-weight:600;font-variant-numeric:tabular-nums;color:var(--caption)}
.side a:focus-visible,.chipnav a:focus-visible,button:focus-visible,input:focus-visible{outline:2px solid var(--primary);outline-offset:2px}
.chipnav{display:none;gap:8px;overflow-x:auto;padding-bottom:4px}
.chipnav a{flex:none;padding:6px 12px;border:1px solid var(--border);border-radius:var(--r-pill);background:var(--surface);color:var(--text-sub);text-decoration:none;font-size:13px}
main{padding:20px;display:grid;gap:16px;min-width:0;max-width:1400px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:16px;min-width:0}
.card h2{font-size:18px;font-weight:700;margin:0 0 12px;color:var(--text-strong);text-wrap:balance}
.card h2 .n{font-size:14px;font-weight:600;color:var(--caption);margin-left:6px}
.kpis{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-md);padding:14px 16px;display:grid;gap:2px}
.kpi .l{font-size:12px;font-weight:600;color:var(--caption)}
.kpi .v{font-size:32px;font-weight:700;color:var(--text-strong);font-variant-numeric:tabular-nums;line-height:1.2}
.kpi .s{font-size:12px;color:var(--caption)}
.kpi .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:1px}
.charts{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr))}
.bars{display:grid;gap:8px}
.bar{display:grid;grid-template-columns:minmax(84px,32%) minmax(0,1fr) 36px;align-items:center;gap:8px;font-size:13px}
.bar .k{color:var(--text-sub);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .t{display:block;height:14px;background:var(--alt1);border-radius:4px;overflow:hidden}
.bar .f{display:block;height:100%;background:var(--primary);border-radius:0 4px 4px 0;min-width:2px}
.bar .f.warn{background:var(--error)} .bar .f.pp{background:var(--purple)} .bar .f.none{background:var(--border-strong)}
.bar .v{text-align:right;font-variant-numeric:tabular-nums;font-weight:600;color:var(--text)}
.bar:hover .k{color:var(--text-strong)}
.flow{display:flex;flex-wrap:nowrap;align-items:stretch;gap:8px;overflow-x:auto;padding-bottom:2px}
.step{flex:1 0 104px;border:1px solid var(--border);border-radius:var(--r-sm);padding:10px 12px;background:var(--alt1);display:grid;gap:2px}
.step .l{font-size:12px;font-weight:600;color:var(--caption)} .step .v{font-size:20px;font-weight:700;font-variant-numeric:tabular-nums;color:var(--text-strong)}
.step.minus .v{color:var(--text-sub)} .step.final{background:var(--surface);border-color:var(--primary)} .step.final .v{color:var(--primary)}
.arrow{display:flex;align-items:center;color:var(--border-strong)}
.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.tools input{flex:1 1 220px;min-width:0;height:40px;border:1px solid var(--border-strong);border-radius:var(--r-sm);padding:0 12px;background:var(--surface);color:var(--text);font:inherit}
.seg{display:flex;flex-wrap:wrap;gap:6px}
.seg button{height:40px;padding:0 14px;border:1px solid var(--border-strong);border-radius:var(--r-sm);background:var(--surface);color:var(--text-sub);font:600 13px var(--font);cursor:pointer}
.seg button:hover{background:var(--alt1)}
.seg button[aria-pressed="true"]{background:var(--primary);border-color:var(--primary);color:#FFFFFF}
.scroll{overflow-x:auto;border:1px solid var(--border);border-radius:var(--r-sm)}
/* 열 너비: 대기업 신입 공채·신규 공고(5열 .t5)와 본문 표(7열 .t7) */
table.t5,table.t7{table-layout:fixed;overflow-wrap:anywhere}
table.t5{min-width:920px} table.t7{min-width:1100px}
.t5 th,.t7 th,.t5 td.lv,.t7 td.lv,.t5 td.dl,.t7 td.dl,.t5 td.src,.t7 td.src{white-space:normal}
.t5 th:nth-child(1){width:44px}.t5 th:nth-child(2){width:20%}.t5 th:nth-child(3){width:31%}.t5 th:nth-child(4){width:25%}.t5 th:nth-child(5){width:14%}.t5 th:nth-child(6){width:8%}
.t7 th:nth-child(1){width:44px}.t7 th:nth-child(2){width:9%}.t7 th:nth-child(3){width:15%}.t7 th:nth-child(4){width:19%}.t7 th:nth-child(5){width:20%}.t7 th:nth-child(6){width:16%}.t7 th:nth-child(7){width:11%}.t7 th:nth-child(8){width:8%}
td.lv small.sal{color:var(--text-sub);font-weight:600}
td.lv small.sal a.starter{color:var(--primary);text-decoration:none} td.lv small.sal a.starter:hover{text-decoration:underline}
table{border-collapse:collapse;width:100%;min-width:1000px}
th,td{padding:10px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--divider)}
th{font-size:12px;font-weight:600;color:var(--caption);background:var(--alt1);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td{min-height:52px} td.lv{white-space:nowrap;color:var(--text-sub)} td.lv small{display:block;font-size:12px;color:var(--caption)} td.corp{min-width:150px} td.corp strong{display:block;font-weight:600;color:var(--text-strong)}
td.dl{white-space:nowrap;font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:13px}
td.dl.soon{color:var(--error);font-weight:700}
td.dl.soon::after{content:"임박";display:inline-block;margin-left:6px;padding:0 6px;border-radius:var(--r-pill);font:600 11px var(--font);
  background:color-mix(in srgb,var(--error) 14%,transparent);color:var(--error)}
tr.hA{background:color-mix(in srgb,var(--error) 8%,var(--surface))}
tr.hB{background:color-mix(in srgb,var(--primary) 7%,var(--surface))}
tr.hF{background:color-mix(in srgb,var(--sky) 9%,var(--surface))}
.pill{display:inline-flex;align-items:center;gap:4px;margin-top:4px;font-size:11px;font-weight:600;padding:1px 8px;border-radius:var(--r-pill);border:1px solid var(--border-strong);color:var(--text-sub)}
.pill::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
.pill.pa::before{background:var(--error)} .pill.pb::before{background:var(--primary)} .pill.pf::before{background:var(--sky)} .pill.pk{border-color:var(--text-sub);color:var(--text-strong)} .pill.pk::before{background:var(--text-strong);border-radius:2px} .pill.pc{margin:0 0 4px}.pill.pc::before{background:var(--success)}
.pill.pp{margin:4px 4px 0 0;border-color:var(--purple);background:color-mix(in srgb,var(--purple) 12%,transparent);color:var(--text-strong)}.pill.pp::before{background:var(--purple)}
td.ttl .prefs{display:flex;flex-wrap:wrap}
.pill.ok::before{background:var(--success)} .pill.bad::before{background:var(--error)} .pill.keep::before{background:var(--warning)}
a{color:var(--primary)} a:hover{color:var(--primary-hover)}
td.src{white-space:nowrap}
.src small{display:block;color:var(--caption)}
.empty{color:var(--caption);font-size:13px;padding:8px 0}
.note{font-size:12px;color:var(--caption);margin:0}
[hidden]{display:none!important}
/* 채용 달력: 주 단위 7열 그리드, 좁은 화면에서는 공고 있는 날짜만 목록으로 */
.cal-head{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:8px;margin-bottom:12px}
.cal-head h2{margin:0} .cal-head .range{font-size:12px;color:var(--caption);font-variant-numeric:tabular-nums}
.cal-legend{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;color:var(--caption);margin-bottom:8px}
.cal-legend span::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px;vertical-align:0;background:var(--border-strong)}
.cal-legend .tgl{font-style:normal;display:inline-flex;align-items:center;gap:4px}
.cal-legend .tgl .tg{font-style:normal;font-size:10px;font-weight:600;padding:0 4px;border-radius:4px;border:1px solid currentColor}
.cal-legend .tgl .tg.b{color:var(--primary)} .cal-legend .tgl .tg.f{color:var(--sky)} .cal-legend .tgl .tg.k{color:var(--text-sub)}
.cal-legend .la::before{background:var(--error)} .cal-legend .lb::before{background:var(--primary)} .cal-legend .lf::before{background:var(--sky)} .cal-legend .lp::before{background:var(--purple)}
.cal{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));border-top:1px solid var(--border);border-left:1px solid var(--border)}
.cal .wd{font-size:12px;font-weight:600;color:var(--caption);padding:6px 8px;background:var(--alt1);border-right:1px solid var(--border);border-bottom:1px solid var(--border)}
.cal .wd.sun{color:var(--error)}
.day{min-height:96px;padding:6px;border-right:1px solid var(--border);border-bottom:1px solid var(--border);display:grid;align-content:start;gap:3px;min-width:0}
.day .dn{font-size:12px;font-weight:600;color:var(--text-sub);font-variant-numeric:tabular-nums;display:flex;justify-content:space-between;gap:4px}
.day .dn .mo{color:var(--primary)} .day .dn .cnt{color:var(--caption);font-weight:600}
.day.out{background:var(--alt1)} .day.out .dn{color:var(--caption);opacity:.6}
.day.today{box-shadow:inset 0 0 0 2px var(--primary)} .day.soon .dn{color:var(--error)}
.day.sun .dn{color:var(--error)}
.ev{display:flex;align-items:center;gap:4px;font-size:12px;line-height:1.35;color:var(--text);text-decoration:none;min-width:0;border-radius:4px;padding:1px 2px}
.ev:hover{background:var(--alt1);color:var(--primary)} .ev:focus-visible{outline:2px solid var(--primary);outline-offset:1px}
.ev::before{content:"";flex:none;width:6px;height:6px;border-radius:50%;background:var(--border-strong)}
.ev.hA::before{background:var(--error)} .ev.hB::before{background:var(--primary)} .ev.hF::before{background:var(--sky)} .ev.pp::before{background:var(--purple)}
.ev span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.ev .tg{flex:none;font-style:normal;font-size:10px;font-weight:600;line-height:1.4;padding:0 4px;border-radius:4px;border:1px solid currentColor}
.ev .tg.b{color:var(--primary)} .ev .tg.f{color:var(--sky)} .ev .tg.k{color:var(--text-sub)} .ev .tg.ai{color:var(--orange)}
.pill.pn{border-color:var(--success);background:color-mix(in srgb,var(--success) 14%,transparent);color:var(--text-strong)} .pill.pn::before{background:var(--success)}
.ev .tg.n,.cal-legend .tgl .tg.n{color:var(--success)}
.bnf{display:flex;flex-wrap:wrap;gap:0 4px;margin-top:2px}
.pill.pw{margin:4px 0 0;border-color:var(--warning);background:color-mix(in srgb,var(--warning) 14%,transparent);color:var(--text-strong)} .pill.pw::before{background:var(--warning)}
.pill.pck{margin:0 0 4px;border-color:var(--warning);color:var(--text-strong)} .pill.pck::before{background:var(--warning)}
small.ckn{display:block;font-size:12px;color:var(--caption)}
.pill.pai{margin:4px 4px 0 0;border-color:var(--orange);background:color-mix(in srgb,var(--orange) 12%,transparent);color:var(--text-strong)} .pill.pai::before{background:var(--orange)}
.cal-legend .tgl .tg.ai{color:var(--orange)}
.day details summary{font-size:12px;color:var(--primary);cursor:pointer;list-style:none} .day details summary::-webkit-details-marker{display:none}
.day details[open] summary{margin-bottom:2px}
td.corp a.co{color:var(--text-strong);text-decoration:none} td.corp a.co:hover{color:var(--primary);text-decoration:underline}
@media (max-width:719px){
  .cal{display:block;border:0}.cal .wd,.day.empty,.day.out{display:none}
  .day{min-height:0;border:1px solid var(--border);border-radius:var(--r-sm);margin-bottom:8px;padding:10px}
  .day .dn .wdn{display:inline} .day .dn .mo{display:none}}
@media (min-width:720px){.day .dn .wdn,.day .dn .mo2{display:none}}
@media (max-width:1023px){.shell{grid-template-columns:1fr}.side{display:none}.chipnav{display:flex}}
@media (max-width:480px){main{padding:16px}.kpi .v{font-size:28px}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""

HTML_JS = """
(function(){
  /* 테마 전환: 다크 토큰을 직접 쓰는 data-theme 전환, 선택은 이 브라우저에만 기억 */
  var b=document.getElementById('theme-toggle'), r=document.documentElement; if(!b) return;
  try{var t=localStorage.getItem('brief-theme'); if(t) r.dataset.theme=t;}catch(e){}
  b.addEventListener('click',function(){
    var dark=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
    r.dataset.theme=dark?'light':'dark'; b.setAttribute('aria-pressed',String(!dark));
    try{localStorage.setItem('brief-theme',r.dataset.theme)}catch(e){}
  });
})();
(function(){
  /* 편집: 표·제목·메모 텍스트를 직접 고치고, 이 브라우저에 저장 (같은 날 브리핑에만 적용) */
  var bar=document.querySelector('.edit-bar'); if(!bar) return;
  var key=bar.dataset.key, main=document.querySelector('main');
  var tgl=document.getElementById('edit-toggle'), sv=document.getElementById('edit-save'),
      rs=document.getElementById('edit-reset'), msg=document.getElementById('edit-msg');
  var SEL='main h2, main td, main .note, main .kpi .l, main .kpi .s, main .step .l';
  function store(){try{return window.localStorage}catch(e){return null}}
  function say(t){msg.textContent=t; if(t) setTimeout(function(){msg.textContent=''},2500)}
  try{var st=store(), saved=st&&st.getItem(key); if(saved){main.innerHTML=saved; rs.hidden=false; say('저장된 편집본을 불러왔습니다')}}catch(e){}
  function setEdit(on){
    document.body.classList.toggle('editing',on); tgl.setAttribute('aria-pressed',String(on));
    tgl.textContent=on?'편집 끝내기':'편집'; sv.hidden=!on;
    document.querySelectorAll(SEL).forEach(function(el){ if(on) el.setAttribute('contenteditable','true'); else el.removeAttribute('contenteditable'); });
  }
  tgl.addEventListener('click',function(){setEdit(tgl.getAttribute('aria-pressed')!=='true')});
  main.addEventListener('click',function(ev){ if(document.body.classList.contains('editing')&&ev.target.closest('a')) ev.preventDefault(); });
  sv.addEventListener('click',function(){
    setEdit(false); var st=store();
    try{ st.setItem(key,main.innerHTML); rs.hidden=false; say('이 브라우저에 저장했습니다'); }
    catch(e){ say('이 환경에서는 저장할 수 없습니다. 파일 편집본(latest_edit.html)을 사용하세요'); }
    setEdit(true);
  });
  rs.addEventListener('click',function(){ try{store().removeItem(key)}catch(e){} location.reload(); });
})();
(function(){
  var q=document.getElementById('q'), mode='all';
  var btns=document.querySelectorAll('.seg button');
  function apply(){
    var t=(q.value||'').trim().toLowerCase();
    document.querySelectorAll('section.grp').forEach(function(sec){
      var n=0;
      sec.querySelectorAll('tbody tr').forEach(function(tr){
        var ok=!tr.classList.contains('xd')&&(!t||tr.textContent.toLowerCase().indexOf(t)>=0)&&
          (mode==='all'||(mode==='A'&&tr.classList.contains('hA'))||(mode==='B'&&tr.dataset.grp.indexOf('대기업')>=0)||(mode==='F'&&tr.dataset.grp.indexOf('외국계')>=0)||(mode==='K'&&tr.dataset.listed!=='')||
           (mode==='soon'&&tr.querySelector('td.dl.soon'))||(mode==='gen'&&tr.dataset.ind==='일반 산업')||
           (mode==='cert'&&tr.dataset.cert==='1')||(mode==='pref'&&tr.dataset.pref==='1')||(mode==='ai'&&tr.dataset.ai==='1')||(mode==='new'&&tr.dataset.new==='1')||(mode==='bnf'&&tr.dataset.bnf==='1'));
        tr.hidden=!ok; if(ok)n++;
      });
      sec.querySelector('.n').textContent=n+'건';
      sec.querySelector('.empty').hidden=n>0; sec.querySelector('.scroll').hidden=n===0;
    });
  }
  q.addEventListener('input',apply); document.addEventListener('brief-refilter',apply);
  btns.forEach(function(b){b.addEventListener('click',function(){
    mode=b.dataset.mode; btns.forEach(function(x){x.setAttribute('aria-pressed',String(x===b))}); apply();});});
})();
(function(){
  /* 선택 삭제: 업체 왼쪽 체크 → '선택 삭제' → 게시 페이지의 공유 DB(excluded)에 기록, 다음 리포트부터 수집에서 제외.
     DB가 없는 환경(내려받은 HTML)은 이 브라우저에서만 숨긴다. */
  var LS='brief-excluded', db=null, col=null, ex={};
  var del=document.getElementById('x-del'); if(!del) return;
  var cEl=document.getElementById('x-cnt'), ul=document.getElementById('x-items'), msg=document.getElementById('x-msg');
  var HINT='체크한 공고는 이 목록에서 빠지고 다음 리포트부터 제외됩니다.';
  function say(t,ask){msg.textContent=t||HINT; msg.classList.toggle('ask',!!ask)}
  function sel(){return Array.prototype.slice.call(document.querySelectorAll('input.xsel:checked'))}
  function sync(){
    var urls={}; sel().forEach(function(c){urls[c.dataset.url]=1});
    var n=Object.keys(urls).length; del.disabled=!n;
    document.querySelectorAll('tr[data-url]').forEach(function(tr){tr.classList.toggle('xon',!!urls[tr.dataset.url])});
    document.querySelectorAll('input.pickall').forEach(function(a){
      var bs=Array.prototype.filter.call(a.closest('table').querySelectorAll('tbody tr'),function(tr){return !tr.hidden&&!tr.classList.contains('xd')})
        .map(function(tr){return tr.querySelector('input.xsel')}).filter(Boolean);
      var on=bs.filter(function(b){return b.checked}).length;
      a.checked=bs.length>0&&on===bs.length; a.indeterminate=on>0&&on<bs.length;
    });
  }
  function render(){
    var keys=Object.keys(ex);
    document.querySelectorAll('tr[data-url]').forEach(function(tr){tr.classList.toggle('xd',!!ex[tr.dataset.url])});
    document.querySelectorAll('a.ev').forEach(function(a){a.classList.toggle('xd',!!ex[a.getAttribute('href')])});
    cEl.textContent=keys.length; ul.textContent='';
    keys.forEach(function(u){
      var li=document.createElement('li'), s=document.createElement('span'), b=document.createElement('button');
      s.textContent=(ex[u].company||'-')+' · '+(ex[u].title||'');
      b.type='button'; b.textContent='되돌리기'; b.addEventListener('click',function(){restore(u)});
      li.appendChild(b); li.appendChild(s); ul.appendChild(li);
    });
    document.dispatchEvent(new Event('brief-refilter')); sync();
  }
  function hid(u){var h=0;for(var i=0;i<u.length;i++){h=(h*31+u.charCodeAt(i))|0}return 'x'+(h>>>0).toString(36)+u.length.toString(36)}
  function loadLocal(){try{ex=JSON.parse(localStorage.getItem(LS)||'{}')||{}}catch(e){ex={}}}
  function saveLocal(){try{localStorage.setItem(LS,JSON.stringify(ex))}catch(e){}}
  document.addEventListener('change',function(ev){if(ev.target.classList&&ev.target.classList.contains('pickall')){
    var on=ev.target.checked;
    Array.prototype.forEach.call(ev.target.closest('table').querySelectorAll('tbody tr'),function(tr){
      if(tr.hidden||tr.classList.contains('xd')) return; var b=tr.querySelector('input.xsel'); if(!b) return;
      document.querySelectorAll('input.xsel').forEach(function(c){if(c.dataset.url===b.dataset.url)c.checked=on});
    }); sync(); return;}
    if(ev.target.classList&&ev.target.classList.contains('xsel')){
    var u=ev.target.dataset.url, on=ev.target.checked;
    document.querySelectorAll('input.xsel').forEach(function(c){if(c.dataset.url===u)c.checked=on}); sync();}});
  var conf=document.getElementById('x-confirm'), yes=document.getElementById('x-yes'), no=document.getElementById('x-no');
  function picked(){var m={}; sel().forEach(function(c){m[c.dataset.url]={url:c.dataset.url,company:c.dataset.company,title:c.dataset.title}}); return m}
  function askClose(){conf.hidden=true; del.hidden=false; say(''); del.focus()}
  del.addEventListener('click',function(){
    var n=Object.keys(picked()).length; if(!n) return;
    del.hidden=true; conf.hidden=false; say(n+'건을 다음 리포트부터 제외할까요?',true); yes.focus();
  });
  no.addEventListener('click',askClose);
  conf.addEventListener('keydown',function(ev){if(ev.key==='Escape')askClose()});
  yes.addEventListener('click',async function(){
    var pick=picked(); var list=Object.keys(pick); if(!list.length){askClose(); return;}
    yes.disabled=true; no.disabled=true; say('저장 중…');
    var done=0;
    for(var i=0;i<list.length;i++){
      var it=pick[list[i]]; it.at=new Date().toISOString();
      if(col){ try{ await col.doc(hid(it.url)).set(it); ex[it.url]=it; done++; }catch(e){ say('저장하지 못했습니다 ('+(e&&e.code||'error')+'). 편집 권한이 있는 계정으로 열어 주세요.'); break; } }
      else { ex[it.url]=it; done++; }
    }
    if(!col){ saveLocal(); render(); say(done+'건을 이 브라우저에서 숨겼습니다. 다음 리포트에 반영하려면 게시된 브리핑 페이지에서 삭제하세요.'); }
    else { render(); if(done===list.length) say(done+'건을 제외했습니다 — 다음 리포트부터 빠집니다.'); }
    sel().forEach(function(c){c.checked=false}); sync();
    yes.disabled=false; no.disabled=false; conf.hidden=true; del.hidden=false;
  });
  async function restore(u){
    if(col){ try{ await col.doc(hid(u)).delete(); say('되돌렸습니다. 다음 리포트부터 다시 수집합니다.'); }catch(e){ say('복원하지 못했습니다 ('+(e&&e.code||'error')+').'); } }
    else { delete ex[u]; saveLocal(); render(); say('되돌렸습니다.'); }
  }
  loadLocal(); render();
  if(window.claude&&typeof window.claude.use==='function'){
    window.claude.use('db').then(function(d){
      if(!d){ say('공유 저장소를 쓸 수 없어 이 브라우저에서만 숨깁니다.'); return; }
      db=d; col=db.collection('excluded');
      col.onSnapshot(function(snap){
        var m={}; snap.docs.forEach(function(doc){var v=doc.data(); if(v&&v.url) m[v.url]=v}); ex=m; render();
      }, function(){ col=null; say('공유 저장소 연결이 끊겨 이 브라우저에서만 숨깁니다.'); });
    }).catch(function(){});
  }
})();
"""


def parse_stat(v):
    """'목록 35, 채택 34, 경력직 1' → {'목록': 35, ...}"""
    return {k.strip(): int(n) for k, n in re.findall(r"([^,\d]+?)\s(\d+)(?=,|$)", v or "")}


SEMI_DC_RE = re.compile(r"반도체|하이닉스|(?<![A-Za-z])FAB(?![A-Za-z])|웨이퍼|데이터\s*센터|(?<![A-Za-z])IDC(?![A-Za-z])|클린룸", re.I)
SEMI_DC_TITLE_RE = re.compile(r"삼성(?!동)|하이테크")  # 제목·업체명에서만 (본문의 '삼성동' 주소 등 오인 방지)


def calendar_eligible(p):
    """관심 기업: 대기업 계열·외국계·코스피/코스닥 상장·데이터센터/반도체 관련.
    달력에는 이 공고만 싣고, 계약직은 이 조건일 때만 브리핑에 남긴다."""
    if p.extra.get("groups") or p.extra.get("listed") or p.hilite == "A":
        return True
    if SEMI_DC_TITLE_RE.search(f"{p.company} {p.title}"):
        return True
    return bool(SEMI_DC_RE.search(f"{p.company} {p.title} {p.listing_text} {p.extra.get('sector', '')} {(p.detail_text or '')[:4000]}"))


CONTRACT_TOP_RANK = 15  # 계약직 건설사는 시공능력평가(도급순위) 15위 이내도 인정


def contract_ok(p):
    """계약직 유지 조건: 관심 기업이거나, 도급순위 15위 이내 건설사."""
    rank = p.extra.get("top100")
    return calendar_eligible(p) or (p.industry == "건설" and bool(rank) and rank <= CONTRACT_TOP_RANK)


def render_calendar(postings, today, months=2, show=5):
    """접수기한 달력: 오늘부터 2개월, 주 단위. 업체명을 누르면 공고로 이동."""
    e = html.escape
    end_m, end_y = today.month + months, today.year
    while end_m > 12:
        end_m, end_y = end_m - 12, end_y + 1
    end = safe_date(end_y, end_m, min(today.day, 28)) or today + dt.timedelta(days=61)
    by_day = collections.defaultdict(list)
    for p in postings:
        if p.deadline_date and calendar_eligible(p):
            d = dt.date.fromisoformat(p.deadline_date)
            if today <= d <= end:
                by_day[d].append(p)
    start = today - dt.timedelta(days=(today.weekday() + 1) % 7)  # 일요일 시작
    last = end + dt.timedelta(days=(5 - end.weekday()) % 7)        # 토요일 끝
    wd = "".join(f'<div class="wd{" sun" if i == 0 else ""}">{w}</div>' for i, w in enumerate("일월화수목금토"))
    cells = []
    d = start
    while d <= last:
        items = sorted(by_day.get(d, []), key=lambda p: ({"A": 0, "B": 1, "F": 2}.get(p.hilite, 3 if not p.prefs else 2.5), p.company))
        cls = ["day"]
        if d < today or d > end:
            cls.append("out")
        if not items:
            cls.append("empty")
        if d == today:
            cls.append("today")
        if items and (d - today).days <= 3:
            cls.append("soon")
        if d.weekday() == 6:
            cls.append("sun")

        def ev(p):
            c = f"ev h{p.hilite}" + (" pp" if p.prefs and not p.hilite else "")
            tip = f"{p.company} · {p.title} · {p.deadline}"
            grp = p.extra.get("groups", [])
            tags = ('<i class="tg b" title="대기업 계열">대</i>' if "대기업 계열" in grp else "") + \
                   ('<i class="tg f" title="외국계">외</i>' if "외국계" in grp else "")
            if p.extra.get("listed"):
                ab = {"코스피": "KS", "코스닥": "KQ"}.get(p.extra["listed"], p.extra["listed"])
                tags += f'<i class="tg k" title="{e(p.extra["listed"])} 상장">{ab}</i>'
            if p.extra.get("ai"):
                tags += '<i class="tg ai" title="AI 우대">AI</i>'
            if is_new(p, today):
                tags += '<i class="tg n" title="지난 보고 이후 신규">N</i>'
            return (f'<a class="{c}" href="{e(p.url)}" target="_blank" rel="noopener" title="{e(tip)}">'
                    f'<span>{e(p.company or p.title)}</span>{tags}</a>')
        body = "".join(ev(p) for p in items[:show])
        if len(items) > show:
            body += f'<details><summary>+{len(items) - show}건 더 보기</summary>{"".join(ev(p) for p in items[show:])}</details>'
        mo = f'<span class="mo">{d.month}월</span> ' if d.day == 1 or d == start else ""
        wdn = f' <span class="wdn">({"월화수목금토일"[d.weekday()]})</span>'
        cnt = f'<span class="cnt">{len(items)}건</span>' if items else ""
        mo2 = f'<span class="mo2">{d.month}월 </span>'
        cells.append(f'<div class="{" ".join(cls)}"><div class="dn"><span>{mo}{mo2}{d.day}일{wdn}</span>{cnt}</div>{body}</div>')
        d += dt.timedelta(days=1)
    n = sum(len(v) for v in by_day.values())
    return (f'<section class="card" id="calendar"><div class="cal-head"><h2>채용 달력<span class="n">{n}건</span></h2>'
            f'<span class="range">{today:%Y-%m-%d} ~ {end:%Y-%m-%d} 접수 마감 · 대기업 계열·외국계·코스피/코스닥 상장·데이터센터/반도체 관련만</span></div>'
            '<div class="cal-legend"><span class="la">데이터센터·하이테크·삼성·하이닉스</span><span class="lb">대기업 계열</span><span class="lf">외국계</span>'
            '<span class="lp">외국어·NEBOSH·IOSH·CSP 우대</span><span>상장사·반도체 관련</span>'
            '<em class="tgl"><i class="tg b">대</i> 대기업 계열 <i class="tg f">외</i> 외국계 '
            '<i class="tg k">KS</i> 코스피 <i class="tg k">KQ</i> 코스닥 <i class="tg ai">AI</i> AI 우대 <i class="tg n">N</i> 신규</em></div>'
            f'<div class="cal">{wd}{"".join(cells)}</div></section>')


PICK_TH = '<th class="pickcell"><input type="checkbox" class="pickall" aria-label="전체 선택"></th>'


def xsel(p):
    """맨 왼쪽 선택 칸 (체크 → 선택 삭제 → 제외 확정 시 다음 리포트부터 제외)."""
    e = html.escape
    return (f'<td class="pickcell"><input type="checkbox" class="xsel" data-url="{e(p.url)}" data-company="{e(p.company)}" '
            f'data-title="{e(p.title)}" aria-label="{e((p.company or "") + " 선택")}"></td>')


def new_pill(p, today):
    return '<span class="pill pn">신규</span>' if is_new(p, today) else ""


def group_pills(p):
    cls = {"대기업 계열": "pb", "외국계": "pf"}
    out = "".join(f'<span class="pill {cls[g]}">{g}</span>' for g in p.extra.get("groups", []))
    if p.extra.get("listed"):
        out += f'<span class="pill pk">{p.extra["listed"]} 상장</span>'
    return out


def rank_pill(p):
    r = p.extra.get("top100")
    return f'<span class="pill">시평 {r}위</span>' if p.industry == "건설" and r else ""


# 복지 표시: 공고 본문에 명시된 경우만 (자녀학자금 · 노조 · 주택지원 · 기숙사)
BENEFIT_RES = [
    ("자녀학자금", re.compile(r"자녀\s*(?:대학\s*)?(?:학자금|학비|교육비|장학금?|등록금)|학자금\s*(?:지원|보조|대출|지급)?|학비\s*(?:지원|보조)|(?:대학\s*)?등록금\s*지원|장학금\s*지원")),
    ("노조", re.compile(r"노동\s*조합|노조(?!\s*(?:없|미가입))")),
    ("주택지원", re.compile(r"주택\s*(?:자금|구입|지원|대출|임차)|주거\s*(?:비\s*)?지원|주거비|사택|관사|전세\s*(?:자금|대출|지원)|임차\s*지원|월세\s*지원")),
    ("기숙사", re.compile(r"기숙사|숙소\s*(?:제공|지원)|숙식\s*(?:제공|지원)")),
]


def benefits_of(text):
    return [lab for lab, rx in BENEFIT_RES if rx.search(text or "")]


def benefit_pills(p):
    b = p.extra.get("benefits") or []
    return ('<span class="bnf">' + "".join(f'<span class="pill pw">{x}</span>' for x in b) + "</span>") if b else ""


def ai_pill(p):
    return '<span class="pill pai">AI 우대</span>' if p.extra.get("ai") else ""


def pref_pills(p):
    if not p.prefs:
        return ""
    return '<span class="prefs">' + "".join(f'<span class="pill pp">{html.escape(x)} 우대</span>' for x in p.prefs) + "</span>"


def cert_pills(p):
    return "".join(f'<span class="pill pc">{html.escape(c)} 명시</span> ' for c in p.certs)


def render_html(postings, failures, now, stats):
    e = html.escape
    today = now.date()

    def days_left(p):
        return (dt.date.fromisoformat(p.deadline_date) - today).days if p.deadline_date else None

    soon = {id(p) for p in postings if days_left(p) is not None and days_left(p) <= 3}
    postings_all = postings  # 직무 확인 필요 공고도 고용형태 묶음에 표시와 함께 싣는다
    groups = employment_groups(postings, today)
    sid = {"정규직": "regular", "계약직": "contract", "인턴": "intern"}
    n_a = sum(p.hilite == "A" for p in postings)
    n_b = sum("대기업 계열" in p.extra.get("groups", []) for p in postings)
    n_f = sum("외국계" in p.extra.get("groups", []) for p in postings)
    n_ks = sum(p.extra.get("listed") == "코스피" for p in postings)
    n_kq = sum(p.extra.get("listed") == "코스닥" for p in postings)
    new_rows = sorted([p for p in postings if is_new(p, today)], key=sort_key)
    n_new = len(new_rows)
    failed = {n for n, _ in failures}
    ok_sites = len(SOURCES) - len(failed)

    # KPI 타일 (전체 공고는 직전 브리핑 대비 변화량)
    if PREV_TOTAL is None:
        delta_txt = "경력직·마감 제외"
    else:
        dv = len(postings) - PREV_TOTAL
        delta_txt = f"직전 대비 {'▲' if dv > 0 else '▼' if dv < 0 else '–'}{abs(dv) if dv else ''} (경력직·마감 제외)"
    def kpi(label, value, sub="", dot=""):
        d = f'<span class="dot" style="background:var({dot})"></span>' if dot else ""
        return f'<div class="kpi"><span class="l">{d}{e(label)}</span><span class="v">{value}</span><span class="s">{e(sub)}</span></div>'
    by = {k: len(r) for k, _, r in groups}
    kpis = "".join([
        kpi("전체 공고", len(postings), delta_txt),
        kpi("신규", n_new, f"지난 보고({last_report_date(today):%m/%d}) 이후 추가", "--success"),
        kpi("정규직", by.get("정규직", 0), f"{by.get('정규직', 0) * 100 // max(len(postings), 1)}%"),
        kpi("계약직", by.get("계약직", 0), f"{by.get('계약직', 0) * 100 // max(len(postings), 1)}%"),
        kpi("일반 산업체", sum(p.industry == "일반 산업" for p in postings), "건설 외 제조·서비스 등"),
        kpi("산업·건설안전기사·ISO 45001 명시", sum(bool(p.certs) for p in postings), "공고에 자격·인증 기재"),
        kpi("외국어·NEBOSH·IOSH·CSP 우대", sum(bool(p.prefs) for p in postings), "우대 조건 기재", "--purple"),
        kpi("복지 명시", sum(bool(p.extra.get("benefits")) for p in postings), "자녀학자금·노조·주택지원·기숙사", "--warning"),
        kpi("AI 우대", sum(bool(p.extra.get("ai")) for p in postings), "우대 조건에 AI 역량", "--orange"),
        kpi("3일 내 마감", len(soon), "접수 서두름", "--error"),
        kpi("데이터센터·하이테크·삼성·하이닉스", n_a, "집중 관심", "--error"),
        kpi("대기업 계열", n_b, "그룹 계열사", "--primary"),
        kpi("외국계", n_f, "외국계 기업", "--sky"),
        kpi("외국계 채널", sum(p.source in ("피플앤잡", "기업 채용 페이지") for p in postings), "피플앤잡·기업 채용 페이지", "--sky"),
        kpi("코스피·코스닥 상장", n_ks + n_kq, f"코스피 {n_ks} · 코스닥 {n_kq}", "--text-strong"),
    ])

    # 막대 차트(단일 계열, primary 한 색)
    def bars(items, cls=lambda k: ""):
        mx = max([v for _, v in items] + [1])
        return '<div class="bars">' + "".join(
            f'<div class="bar" title="{e(k)}: {v}건"><span class="k">{e(k)}</span>'
            f'<span class="t"><span class="f {cls(k)}" style="width:{v * 100 / mx:.1f}%"></span></span><span class="v">{v}</span></div>'
            for k, v in items) + "</div>"
    by_src = collections.Counter(p.source for p in postings)
    src_items = [(n.replace(" 안전공학과", ""), by_src.get(n, 0)) for n, _, _ in SOURCES]
    buckets = [("3일 이내", 0, 3), ("4–7일", 4, 7), ("8–14일", 8, 14), ("15–30일", 15, 30), ("31일 이상", 31, 10**6)]
    dl_items = [(lab, sum(1 for p in postings if days_left(p) is not None and lo <= days_left(p) <= hi)) for lab, lo, hi in buckets]
    dl_items.append(("채용 시·미확인", sum(1 for p in postings if days_left(p) is None)))
    lv = collections.Counter(p.level for p in postings)
    lv_items = [(k, lv.get(k, 0)) for k in ("신입", "신입·경력", "경력무관", "인턴") if lv.get(k)]
    pref_items = [(x + " 우대", sum(x in p.prefs for p in postings)) for x in ("외국어·영어", "NEBOSH", "IOSH", "CSP")]
    ind_items = [("일반 산업", sum(p.industry == "일반 산업" for p in postings)),
                 ("건설", sum(p.industry == "건설" for p in postings)),
                 ("산업안전기사 명시", sum("산업안전기사" in p.certs for p in postings)),
                 ("건설안전기사 명시", sum("건설안전기사" in p.certs for p in postings)),
                 ("ISO 45001 명시", sum("ISO 45001" in p.certs for p in postings))]
    charts = (
        f'<div class="card"><h2>사이트별 채택 공고</h2>{bars(src_items)}</div>'
        f'<div class="card"><h2>접수기한까지 남은 기간</h2>'
        f'{bars(dl_items, lambda k: "warn" if k == "3일 이내" else "none" if k.startswith("채용") else "")}</div>'
        f'<div class="card"><h2>경력 구분</h2>{bars(lv_items)}</div>'
        f'<div class="card"><h2>업종 · 자격증 명시</h2>{bars(ind_items)}</div>'
        f'<div class="card"><h2>외국어 · NEBOSH · IOSH · CSP 우대</h2>{bars(pref_items, lambda k: "pp")}</div>')

    # 수집 → 채택 흐름도
    agg = collections.Counter()
    for n, v in stats.items():
        agg.update(parse_stat(v))
    total = agg.get("목록", 0)
    steps = [("수집 목록", total, "")]
    for lab, keys in (("안전 직무 외", ["안전 직무 아님", "담당 업무에 안전 없음", "채용 공고 아님"]), ("경력직·대리급 이상", ["경력직", "대리급 이상"]),
                      ("대상 기준 외", ["건설사(시평 100위 밖)", "계약직(관심 기업 외)", "영업직", "감시단", "한국 근무 아님"]),
                      ("마감·오래된 글", ["마감", "오래된 게시글"]), ("중복", ["중복(상위 사이트 우선)"])):
        c = sum(agg.get(k, 0) for k in keys)
        if c:
            steps.append((lab, f"−{c}", "minus"))
    n_carried = sum(1 for p in postings if p.extra.get("carried"))
    if n_carried:
        steps.append(("이전 수집 유지", f"+{n_carried}", "minus"))
    steps.append(("브리핑 채택", len(postings), "final"))
    arrow = '<span class="arrow" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></span>'
    flow = arrow.join(f'<div class="step {c}"><span class="l">{e(l)}</span><span class="v">{v}</span></div>' for l, v, c in steps)

    def sal_small(p):
        st = p.extra.get("starter", "")
        link = (f'<a class="starter" href="{e(p.extra.get("starter_url", ""))}" target="_blank" rel="noopener">{e(st)}</a>' if st else "")
        return f'<small class="sal">{e(salary_of(p))}</small>' + (f'<small class="sal">{link}</small>' if link else "")

    def co_link(p):
        if not href(p):
            return e(p.company or "-")
        return f'<a class="co" href="{e(p.url)}" target="_blank" rel="noopener">{e(p.company or "-")}</a>'

    def src_link(p):
        via = f'<small>{e(p.extra["via"])}</small>' if p.extra.get("via") else ""
        if not href(p):
            return e(p.source) + via
        return f'<a href="{e(p.url)}" target="_blank" rel="noopener">{e(p.source)}</a>' + via

    # 공고 표
    pill = {"A": '<span class="pill pa">데이터센터·하이테크·삼성·하이닉스</span>', "B": "", "F": "", "": ""}
    secs, nav = [], []
    for key, tag, rows in groups:
        i = sid.get(key, "other")
        nav.append((i, tag, len(rows)))
        trs = "".join(
            f'<tr class="h{p.hilite}" data-url="{e(p.url)}" data-ind="{e(p.industry)}" data-cert="{1 if p.certs else 0}" data-pref="{1 if p.prefs else 0}" data-ai="{1 if p.extra.get("ai") else 0}" data-grp="{e(" ".join(p.extra.get("groups", [])))}" data-listed="{e(p.extra.get("listed", ""))}" data-new="{1 if is_new(p, today) else 0}" data-bnf="{1 if p.extra.get("benefits") else 0}">{xsel(p)}<td class="lv">{e(p.level)}<small>{e(p.industry)}</small>{sal_small(p)}</td>'
            f'<td class="corp"><strong>{co_link(p)}</strong>{new_pill(p, today)}{big_pill(p)}{pill[p.hilite]}{group_pills(p)}{rank_pill(p)}</td>'
            f"<td class=\"ttl\">{e(p.title)}{check_pill(p)}{pref_pills(p)}{ai_pill(p)}{benefit_pills(p)}</td><td>{cert_pills(p)}{e(p.qualification or '-')}</td><td>{e(p.preferred or '-')}</td>"
            f'<td class="dl{" soon" if id(p) in soon else ""}">{e(p.deadline)}</td>'
            f'<td class="src">{src_link(p)}'
            f'{"<small>이전 수집</small>" if p.extra.get("carried") else ""}</td></tr>'
            for p in rows)
        secs.append(
            f'<section class="card grp" id="{i}"><h2>{e(tag)}<span class="n">{len(rows)}건</span></h2>'
            '<p class="empty" hidden>조건에 맞는 공고가 없습니다.</p>'
            '<div class="scroll"><table class="t7"><thead><tr>' + PICK_TH + '<th>구분 · 연봉</th><th>업체명</th><th>공고명</th>'
            "<th>지원 자격 (학과·자격·영어·학력)</th><th>우대 사항</th><th>접수기한</th><th>출처</th></tr></thead>"
            f"<tbody>{trs}</tbody></table></div></section>")

    # 수집 현황 표
    srows = []
    for n, _, _ in SOURCES:
        v = stats.get(n, "")
        d = parse_stat(v)
        if n in failed and "유지" in v:
            st = '<span class="pill keep">실패 · 직전 공고 유지</span>'
        elif n in failed:
            st = '<span class="pill bad">수집 실패</span>'
        else:
            st = '<span class="pill ok">정상</span>'
        why = ", ".join(f"{k} {c}" for k, c in d.items() if k not in ("목록", "채택")) or "-"
        err = next((x.splitlines()[0] for m, x in failures if m == n), "")
        srows.append(f"<tr><td>{e(n)}</td><td>{st}</td><td class='dl'>{d.get('목록', '-')}</td>"
                     f"<td class='dl'>{d.get('채택', by_src.get(n, 0))}</td><td>{e(why)}</td><td>{e(err[:80]) or '-'}</td></tr>")
    status = ('<div class="scroll"><table style="min-width:760px"><thead><tr><th>사이트 (우선순위 순)</th><th>상태</th><th>목록</th>'
              f'<th>채택</th><th>제외 사유</th><th>오류</th></tr></thead><tbody>{"".join(srows)}</tbody></table></div>')

    crows = []
    for k, v in CAREER_STATUS.items():
        m = re.match(r"한국 HSE (\d+)건", v)
        st = ('<span class="pill ok">수집</span>' if m else
              '<span class="pill keep">API 없음</span>' if "API 없음" in v else '<span class="pill bad">접속 실패</span>')
        crows.append(f"<tr><td>{e(k)}</td><td>{st}</td><td class='dl'>{m.group(1) if m else '-'}</td>"
                     f"<td>{'-' if m else e(v)}</td></tr>")
    careers = ('<section class="card" id="careers"><h2>기업 채용 페이지 현황<span class="n">한국 근무 HSE·EHS·Safety 공고 기준</span></h2>'
               '<div class="scroll"><table style="min-width:560px"><thead><tr><th>기업</th><th>상태</th><th>한국 HSE 공고</th><th>비고</th></tr></thead>'
               f'<tbody>{"".join(crows)}</tbody></table></div></section>') if crows else ""
    def rows5(rows, pill_new=False):
        return "".join(
            f'<tr class="h{p.hilite}" data-url="{e(p.url)}">{xsel(p)}<td class="corp"><strong>{co_link(p)}</strong>'
            f'{new_pill(p, today) if pill_new else ""}{big_pill(p)}{group_pills(p)}</td><td>{e(p.title)}{check_pill(p)}{benefit_pills(p)}</td><td class="lv">{e(p.employment)}<small>{e(p.level)}</small>{sal_small(p)}</td>'
            f'<td class="dl{" soon" if id(p) in soon else ""}">{e(p.deadline)}</td><td class="src">{src_link(p)}</td></tr>'
            for p in rows)
    head5 = '<div class="scroll"><table class="t5"><thead><tr>' + PICK_TH + '<th>업체명</th><th>공고명</th><th>고용형태 · 연봉</th><th>접수기한</th><th>출처</th></tr></thead>'
    newsec = (f'<section class="card" id="new"><h2>신규 공고<span class="n">{n_new}건 · 지난 보고({last_report_date(today):%m/%d}) 이후 추가</span></h2>'
              + (f'{head5}<tbody>{rows5(new_rows)}</tbody></table></div>' if new_rows else '<p class="empty">새로 추가된 공고가 없습니다.</p>')
              + '</section>')
    side = ('<div class="sec">요약</div><a href="#new">신규 공고 <b>' + str(n_new) + '</b></a><a href="#summary">지표·차트</a><a href="#calendar">채용 달력</a><a href="#flow">수집 흐름</a>'
            '<div class="sec">공고</div>' + "".join(f'<a href="#{i}">{e(t)} <b>{c}</b></a>' for i, t, c in nav)
            + '<div class="sec">수집</div><a href="#status">사이트 현황</a>'
            + ('<a href="#careers">기업 채용 페이지</a>' if crows else ""))
    chipnav = f'<a href="#new">신규 {n_new}</a><a href="#calendar">채용 달력</a>' + "".join(f'<a href="#{i}">{e(t)} {c}</a>' for i, t, c in nav)

    return f"""<title>안전관리자 채용 브리핑</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap">
<style>{HTML_CSS}</style>
<header class="top"><h1>안전관리자 채용 브리핑</h1>
  <span class="when">{now:%Y-%m-%d %H:%M} KST 수집</span>
  <span class="pill {'ok' if not failed else 'keep'} chip">{ok_sites}/{len(SOURCES)} 사이트 수집</span>
  <div class="xbar" role="group" aria-label="선택 공고 삭제">
    <span id="x-msg" class="xmsg" role="status">체크한 공고는 이 목록에서 빠지고 다음 리포트부터 제외됩니다.</span>
    <button type="button" id="x-del" class="danger solid" disabled>선택 삭제</button>
    <span id="x-confirm" class="xgrp" role="group" aria-label="제외 확인" hidden><button type="button" id="x-yes" class="danger solid">제외 확정</button> <button type="button" id="x-no">취소</button></span>
    <details id="x-list" class="xlist"><summary>제외한 공고 <b id="x-cnt">0</b>건 · 되돌리기</summary><ul id="x-items"></ul></details>
  </div>
  <div class="edit-bar" data-key="brief-{now:%Y%m%d%H%M}">
    <button type="button" id="edit-toggle" aria-pressed="false">편집</button>
    <button type="button" id="edit-save" hidden>저장</button>
    <button type="button" id="edit-reset" hidden>원래대로</button>
    <span id="edit-msg" role="status"></span>
  <button type="button" class="icon-btn" id="theme-toggle" aria-label="라이트/다크 테마 전환" title="테마 전환">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
  </button></div></header>
<div class="shell">
<nav class="side" aria-label="섹션">{side}</nav>
<main>
<nav class="chipnav" aria-label="섹션">{chipnav}<a href="#status">사이트 현황</a></nav>
<div class="kpis" id="summary">{kpis}</div>
{newsec}
{render_calendar(postings_all, today)}
<div class="charts">{charts}</div>
<div class="card" id="flow"><h2>수집에서 채택까지</h2><div class="flow">{flow}</div></div>
<div class="card tools" role="search">
  <label for="q" class="sr" hidden>공고 검색</label>
  <input id="q" type="search" placeholder="업체명·공고명·자격 검색" aria-label="업체명, 공고명, 자격 검색">
  <div class="seg" role="group" aria-label="강조 필터">
    <button type="button" data-mode="all" aria-pressed="true">전체</button>
    <button type="button" data-mode="new" aria-pressed="false">신규</button>
    <button type="button" data-mode="A" aria-pressed="false">데이터센터·하이테크·삼성·하이닉스</button>
    <button type="button" data-mode="B" aria-pressed="false">대기업 계열</button>
    <button type="button" data-mode="F" aria-pressed="false">외국계</button>
    <button type="button" data-mode="K" aria-pressed="false">코스피·코스닥 상장</button>
    <button type="button" data-mode="gen" aria-pressed="false">일반 산업체</button>
    <button type="button" data-mode="cert" aria-pressed="false">산업·건설안전기사·ISO 45001 명시</button>
    <button type="button" data-mode="pref" aria-pressed="false">외국어·NEBOSH·IOSH·CSP 우대</button>
    <button type="button" data-mode="ai" aria-pressed="false">AI 우대</button>
    <button type="button" data-mode="soon" aria-pressed="false">3일 내 마감</button>
    <button type="button" data-mode="bnf" aria-pressed="false">복지: 학자금·노조·주택·기숙사</button>
  </div>
  </div></div>
{''.join(secs)}
<section class="card" id="status"><h2>사이트별 수집 현황</h2>{status}</section>
{careers}
<p class="note">지원 자격·우대 사항은 상세 페이지에서 자동 추출한 요약입니다. 지원 전 원문을 확인하세요.</p>
</main></div>
<script>{HTML_JS}</script>
"""


UNDATED_KEEP_DAYS = 14  # 마감일이 없는 공고('채용 시 마감' 등)는 처음 수집 후 이 기간만 유지


def carry_over(prev_path, failed, kept, stats, today):
    """직전 브리핑에서 아직 접수 중인 공고를 이어서 싣는다.

    검색 결과 순위가 바뀌어 오늘 목록에 안 보이거나, 사이트 수집에 실패해도
    접수기한이 남은 공고는 리스트에 남긴다. 마감일이 없는 공고는 처음 수집 후
    UNDATED_KEEP_DAYS 일까지만 유지한다. 지금 규칙(건설사 시평 100위 등)은 다시 적용한다.
    """
    try:
        prev = json.loads(prev_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    prev_day = prev.get("generated_at", "")[:10]
    added = collections.Counter()
    for d in prev.get("postings", []):
        try:
            p = Posting(**d)
        except TypeError:  # 이전 형식 필드
            continue
        if p.deadline_date:
            if p.deadline_date < today.isoformat():
                continue
        else:
            first = p.extra.get("first_seen") or prev_day
            if not first or (today - dt.date.fromisoformat(first)).days > UNDATED_KEEP_DAYS:
                continue
        if excluded_corp(p):  # 제외 업체명 재적용
            continue
        if p.industry == "건설" and not p.extra.get("top100"):
            continue
        if user_excluded(p):  # 브리핑에서 삭제한 공고
            continue
        if p.extra.get("manual") and p.url not in manual_urls():  # 직접 추가 목록에서 지운 공고
            continue
        if senior_rank(p) or NON_HSE_SAFETY_RE.search(p.title):  # 대리급 이상·비HSE 제외 재적용
            continue
        g = duty_gate(p)  # 담당 업무 기준 재적용
        if g == "drop":
            continue
        if g == "ok":
            p.extra.pop("needs_check", None)
            p.extra.pop("check_note", None)
        elif g == "check" and not p.extra.get("needs_check"):
            p.extra["needs_check"] = True
            p.extra["check_note"] = DUTY_CHECK_NOTE
        yrs = [int(m.group(1) or m.group(2)) for m in TITLE_YEARS_RE.finditer(p.title)]
        if yrs and min(yrs) >= 2 and not NEWBIE_RE.search(p.title):
            continue
        if SALES_RE.search(p.title) or WATCH_RE.search(f"{p.title} {p.detail_text}"):  # 영업직·감시단 제외 재적용
            continue
        if any(q.url == p.url for q in kept) or is_dup(p, kept):
            continue
        p.extra["carried"] = p.extra.get("carried") or prev_day
        p.hilite = classify_company(p, p.detail_text)  # 지금 기준으로 강조 다시 판정
        p.extra["listed"] = listed_market(p)
        if p.employment == "계약직" and not contract_ok(p):  # 계약직은 관심 기업만
            continue
        if "benefits" not in p.extra:
            p.extra["benefits"] = benefits_of(f"{p.listing_text} {p.detail_text}")
        if "ai" not in p.extra:
            t = p.detail_text or ""
            p.extra["ai"] = bool(AI_RE.search(section(t, PREF_HEAD, 600)) or AI_NEAR_PREF_RE.search(t))
        kept.append(p)
        added[p.source] += 1
    for name, n in added.items():
        note = f"직전 브리핑에서 접수 중 공고 {n}건 유지"
        stats[name] = f"수집 실패 → {note}" if name in failed else f"{stats.get(name, '')}, {note}".lstrip(", ")


# ---------------------------------------------------------------- 상장사 (KRX)
KRX_MARKETS = [("코스피", "stockMkt"), ("코스닥", "kosdaqMkt")]
LISTED: dict = {}  # 정규화 업체명 → '코스피' / '코스닥'


def load_listed(f: Fetcher, cache: Path):
    """한국거래소 KIND 상장법인 목록을 받아 LISTED를 채운다. 실패하면 직전 캐시를 쓴다."""
    table, errors = {}, []
    for market, code in KRX_MARKETS:
        url = f"https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType={code}"
        try:
            s = BeautifulSoup(f.get(url, encoding="cp949"), "html.parser")
            rows = s.find_all("tr")
            head = [text_of(x) for x in rows[0].find_all(["th", "td"])] if rows else []
            col = head.index("회사명") if "회사명" in head else 0
            n = 0
            for tr in rows[1:]:
                tds = tr.find_all("td")
                if len(tds) > col and text_of(tds[col]):
                    table[norm_corp(text_of(tds[col]))] = market
                    n += 1
            if n < 100:
                raise RuntimeError(f"{market} 목록이 {n}건뿐")
        except Exception as e:
            errors.append(f"{market}: {type(e).__name__}")
    if table and not errors:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(table, ensure_ascii=False), encoding="utf-8")
    elif cache.exists():
        table = {**json.loads(cache.read_text(encoding="utf-8")), **table}
    LISTED.clear()
    LISTED.update(table)
    return errors


def listed_market(p: Posting):
    n = norm_corp(p.company)
    if n in LISTED:
        return LISTED[n]
    m = re.search(r"기업구분[^()]{0,20}\((코스피|코스닥|유가증권|KOSPI|KOSDAQ)", p.detail_text or "")
    if m:
        return {"유가증권": "코스피", "KOSPI": "코스피", "KOSDAQ": "코스닥"}.get(m.group(1), m.group(1))
    return ""


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="briefings", help="출력 디렉터리")
    ap.add_argument("--max-detail", type=int, default=1600, help="상세 페이지 최대 조회 수")
    args = ap.parse_args()

    now = dt.datetime.now(KST)
    today = now.date()
    f = Fetcher()
    krx_err = load_listed(f, Path(args.out) / "krx_listed.json")
    if krx_err:
        print(f"[krx] {krx_err} (캐시 {len(LISTED)}개사 사용)", file=sys.stderr)
    try:  # 이전에 본 공고는 처음 수집일을 이어받는다
        for d in json.loads((Path(args.out) / "latest.json").read_text(encoding="utf-8")).get("postings", []):
            fs = (d.get("extra") or {}).get("first_seen")
            if fs:
                PREV_SEEN.setdefault(d["url"], fs)
                PREV_SEEN.setdefault(norm_company(d.get("company", "")) + "|" + norm_title(d.get("title", ""), d.get("company", "")), fs)
    except (OSError, ValueError, KeyError):
        pass
    n_ex = load_excluded()
    if n_ex:
        print(f"[excluded] 사용자 삭제 {n_ex}건 적용", file=sys.stderr)
    raw, failures, stats = [], [], {}
    SOURCE_BUDGET = 420  # 사이트 하나에 최대 7분 (느린 사이트가 전체 실행을 막지 않게)
    for name, fn, _ in SOURCES:
        for attempt in (1, 2):
            f.deadline = time.time() + SOURCE_BUDGET
            try:
                raw.append((name, fn(f)))
                break
            except Exception as e:  # 사이트 하나가 실패해도 나머지는 계속
                client_err = isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500
                if attempt == 1 and not client_err and "시간 한도" not in str(e):
                    time.sleep(30)  # 사이트 단위로 한 번 더
                    continue
                msg = f"{type(e).__name__}: {e}".splitlines()[0][:160]
                if name in ("원티드", "캐치") and client_err and e.response.status_code == 403:
                    msg = "사이트가 해외·자동 접속(GitHub Actions)을 403으로 차단 — 수집 불가"
                if name == "충북대 안전공학과" and client_err:
                    msg = "학과 서버가 해외 접속(GitHub Actions)에 404를 반환 — 국내 IP에서만 열림 (학교 본 사이트는 정상)"
                failures.append((name, msg))
                stats[name] = "수집 실패"
                break

    f.deadline = None
    t_detail_end = time.time() + 22 * 60  # 상세 조회 전체 한도 22분
    kept, n_detail = [], 0
    for name, found in raw:
        counts = {"목록": len(found), "채택": 0}
        for p in found:
            # 목록 단계에서 명백히 무관한 것은 상세 조회 전에 거른다
            if p.extra.get("posted") is None and not p.extra.get("manual") and relevant(p) is False:
                counts["안전 직무 아님"] = counts.get("안전 직무 아님", 0) + 1
                continue
            # 목록에 '경력 n년'만 있는 공고(사람인·워커)는 경력직으로 보고 상세 조회 없이 제외
            lv = p.level or ""
            if p.source in ("사람인", "워커", "피플앤잡") and lv.startswith("경력") and not NEWBIE_RE.search(lv):
                counts["경력직"] = counts.get("경력직", 0) + 1
                continue
            if n_detail < args.max_detail and time.time() < t_detail_end:
                for attempt in (1, 2):  # 상세 본문이 없으면 자격·우대·복지·연봉을 못 읽으므로 한 번 더 시도
                    try:
                        t = fetch_detail(f, p)
                        if p.extra.get("posted") is not None:  # 게시판: 메뉴 등 사이트 공통부 제거, 본문만
                            i = t.find(p.title[:12])
                            t = t[i:] if i >= 0 else t
                        p.detail_text = t[:15000]
                        n_detail += 1
                        time.sleep(0.3)
                        break
                    except Exception as e:
                        print(f"[detail] {p.url}: {e}", file=sys.stderr)
                        time.sleep(2)
            elif not p.url.startswith("manual:"):
                counts["상세 미조회(한도)"] = counts.get("상세 미조회(한도)", 0) + 1
            analyze(p, today)
            ok, why = keep(p, today)
            if not ok:
                counts[why] = counts.get(why, 0) + 1
                continue
            if is_dup(p, kept):
                counts["중복(상위 사이트 우선)"] = counts.get("중복(상위 사이트 우선)", 0) + 1
                continue
            counts["채택"] += 1
            p.extra["first_seen"] = (PREV_SEEN.get(p.url) or PREV_SEEN.get(norm_company(p.company) + "|" + norm_title(p.title, p.company))
                                     or p.extra.get("first_seen") or today.isoformat())
            kept.append(p)
        stats[name] = ", ".join(f"{k} {v}" for k, v in counts.items())

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    global PREV_TOTAL
    try:
        PREV_TOTAL = len(json.loads((out / "latest.json").read_text(encoding="utf-8")).get("postings", []))
    except (OSError, ValueError):
        PREV_TOTAL = None
    carry_over(out / "latest.json", [n for n, _ in failures], kept, stats, today)
    # 본문 없이 실린 공고(이전 수집 포함)는 남은 한도 안에서 상세를 다시 읽어 복지·연봉·자격을 채운다
    for p in kept:
        if n_detail >= args.max_detail or time.time() > t_detail_end + 4 * 60:
            break
        if len(p.detail_text or "") >= 600 or p.url.startswith("manual:") or p.extra.get("posted") is not None:
            continue
        try:
            t = fetch_detail(f, p)
        except Exception as e:
            print(f"[detail-refill] {p.url}: {e}", file=sys.stderr)
            continue
        n_detail += 1
        if len(t) <= len(p.detail_text or ""):
            continue
        p.detail_text = t[:15000]
        p.extra["benefits"] = benefits_of(f"{p.listing_text} {t}")
        p.extra.pop("salary", None)
        sal = salary_of(p)
        p.extra["salary"] = "" if sal == NO_SALARY else sal
        if not p.qualification or p.qualification == "-":
            p.qualification = summarize_qual(section(t, QUAL_HEAD), t[:6000])
        if not p.preferred:
            pref = section(t, PREF_HEAD, 180)
            p.preferred = pref[:110] if pref else ""
        time.sleep(0.3)
    uniq_kept, seen_url = [], set()  # 같은 공고(URL) 중복 방지
    for p in kept:
        if p.url not in seen_url:
            seen_url.add(p.url)
            uniq_kept.append(p)
    kept[:] = uniq_kept
    load_starter(out / "starter_salary.json")
    n_look = fill_starter(f, kept, today, out / "starter_salary.json")
    print(f"[starter] 신규 조회 {n_look}개사, 초봉 확인 {sum(bool(p.extra.get('starter')) for p in kept)}/{len(kept)}건", file=sys.stderr)
    md = render_md(kept, failures, now, stats)
    (out / f"{today:%Y-%m-%d}.md").write_text(md, encoding="utf-8")
    (out / "latest.md").write_text(md, encoding="utf-8")
    page = render_html(kept, failures, now, stats)
    (out / "latest.html").write_text(page, encoding="utf-8")
    # 내려받아 편집기·브라우저에서 고칠 수 있는 완전한 HTML 문서
    (out / "latest_edit.html").write_text(
        '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + page.replace("</style>", "</style>\n</head>\n<body>", 1) + "\n</body>\n</html>\n", encoding="utf-8")
    for p in kept:
        p.detail_text = p.detail_text[:1500]
    (out / "latest.json").write_text(json.dumps(
        {"generated_at": now.isoformat(), "postings": [asdict(p) for p in kept], "failures": failures, "stats": stats,
         "careers": CAREER_STATUS},
        ensure_ascii=False, indent=1), encoding="utf-8")
    # 날짜별 보관본 — 이후 작업·규칙 변경 때도 이전 수집 정보를 되살릴 수 있게 남긴다
    hist = out / "history"
    hist.mkdir(exist_ok=True)
    with gzip.open(hist / f"{today:%Y-%m-%d}.json.gz", "wt", encoding="utf-8") as fh:
        json.dump({"generated_at": now.isoformat(), "postings": [asdict(p) for p in kept], "stats": stats},
                  fh, ensure_ascii=False)
    print(md)
    return 0 if len(failures) < len(SOURCES) else 2


if __name__ == "__main__":
    sys.exit(main())
