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
import datetime as dt
import difflib
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

SAFETY_RE = re.compile(r"안전|보건관리|HSE|EHS|SHE|산업위생|소방|방재")
CAREER_ONLY_RE = re.compile(r"경력\s*\d+\s*년\s*(이상|↑)?|경력직|경력\s*사원|경력\s*채용|^경력$")
NEWBIE_RE = re.compile(r"신입|인턴|경력\s*무관|졸업\s*예정|전체|무관")

# 강조 규칙 — A가 B보다 우선
HILITE_A_RE = re.compile(r"데이터\s*센터|IDC|하이테크|삼성|하이닉스")
BIG_GROUPS = (
    "삼성 SK 현대 HD현대 LG 롯데 포스코 POSCO 한화 GS 신세계 이마트 CJ 한진 대한항공 KT 두산 LS "
    "DL 대림 HDC 효성 코오롱 OCI KCC 한국타이어 고려아연 영풍 아모레 카카오 네이버 NAVER 쿠팡 "
    "대우건설 삼우 금호 태영 호반 부영 중흥 하림 HMM 셀트리온 미래에셋 농협 NH 한국전력 한전 "
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

QUAL_HEAD = r"자격\s*요건|지원\s*자격|응시\s*자격|자격\s*조건|필수\s*(?:요건|사항)|공통\s*자격"
PREF_HEAD = r"우대\s*(?:사항|조건|요건)|우대\s*[:：]"
STOP = r"우대|근무\s*조건|근무\s*형태|근무지|근무\s*시간|전형|접수|복리|급여|제출\s*서류|유의\s*사항|기타\s*사항|채용\s*절차|모집\s*인원|기업\s*정보"


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
        self.c = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=40)

    def get(self, url, encoding=None, tries=2):
        last = None
        for i in range(tries):
            try:
                r = self.c.get(url, headers={"Referer": url})
                r.raise_for_status()
                if encoding:
                    return r.content.decode(encoding, errors="ignore")
                return r.text
            except Exception as e:  # 네트워크 일시 오류는 한 번 재시도
                last = e
                time.sleep(2 + i * 3)
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
        or re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", t)
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
    """잡코리아 신입·인턴 채용관(entry-level-internship)에서 '안전관리자' 검색."""
    out = []
    for page in (1, 2, 3):
        url = ("https://www.jobkorea.co.kr/Theme/TemplateFreeGnoList/entry-level-internship?"
               f"rSearchText={Q}&themeNo=169&tabNo=0&jobFilter=1&psTab=40&FreePageNo={page}&MainPageNo=1&GIOpenTypeCode=0")
        s = BeautifulSoup(f.get(url), "html.parser")
        items = s.select("li.dmpItem")
        for li in items:
            a = li.select_one(".rTit a")
            if not a:
                continue
            p = Posting("잡코리아", text_of(a), text_of(li.select_one(".corNm")),
                        urljoin("https://www.jobkorea.co.kr", a["href"].split("&rPageCode")[0]),
                        text_of(li))
            p.deadline = text_of(li.select_one(".rPeriod"))
            out.append(p)
        if len(items) < 40:
            break
    return out


def src_saramin(f: Fetcher):
    out, seen = [], set()
    urls = [
        # 사용자 지정 검색 URL + 신입/경력무관 필터 100건
        f"https://www.saramin.co.kr/zf_user/search?searchword={Q}&go=&flag=n&searchMode=1&searchType=search&search_done=y&search_optional_item=n",
        f"https://www.saramin.co.kr/zf_user/search?searchword={Q}&searchType=search&exp_cd=1&exp_none=y&recruitPageCount=100&recruitSort=relation",
    ]
    for url in urls:
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
            p.extra = {"rec_idx": rec.group(1), "cond": cond, "sector": bold}
            p.level = cond[1] if len(cond) > 1 else ""
            p.employment = cond[3] if len(cond) > 3 else ""
            p.deadline = text_of(it.select_one(".job_date .date"))
            out.append(p)
    return out


def src_linkareer(f: Fetcher):
    url = f"https://linkareer.com/search?direction=DESC&page=1&q={Q}&sort=RELEVANCE&tab=open-activity"
    h = f.get(url)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
    if not m:
        raise RuntimeError("__NEXT_DATA__ 없음")
    data = json.loads(m.group(1))
    acts = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get("__typename") == "Activity" and o.get("title") and o.get("id"):
                acts[o["id"]] = o
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)
    out = []
    for a in acts.values():
        p = Posting("링커리어", clean(a["title"]), clean(a.get("organizationName")),
                    f"https://linkareer.com/activity/{a['id']}", "")
        jt = a.get("jobTypes") or []
        p.extra = {"jobTypes": jt}
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
            title = text_of(a)
            rest = clean(text_of(tds[4]).replace(title, "", 1))  # "지역 | 채용구분 | 급여"
            parts = [clean(x) for x in rest.split("|")]
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
]


# ---------------------------------------------------------------- 상세 분석
def section(text, head_re, max_len=260):
    m = re.search(rf"(?:{head_re})\s*[:：]?", text)
    if not m:
        return ""
    body = text[m.end():m.end() + 1200]
    stop = re.search(STOP, body[5:])
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
        elif re.search(r"정규직", text):
            e = "정규직"
    if re.search(r"계약|기간제|파견|현장채용", e):
        return "계약직"
    if "정규" in e:
        return "정규직"
    if "인턴" in e:
        return "인턴"
    return "기타/미표기"


def level_of(p: Posting, text):
    lv = p.level
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


def classify_company(p: Posting, text):
    blob = f"{p.company} {p.title}"
    if HILITE_A_RE.search(f"{blob} {p.listing_text} {p.extra.get('sector', '')}"):
        return "A"
    if p.company_type in ("대기업", "외국계") or re.search(r"외국계|외투기업|외국인\s*투자", f"{blob} {text[:3000]}"):
        return "B"
    name = re.sub(r"\(주\)|㈜|주식회사|\s", "", blob)
    if any(re.search(rf"(?<![가-힣A-Za-z]){re.escape(g)}", name) for g in BIG_GROUPS + FOREIGN_NAMES):
        return "B"
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


def relevant(p: Posting) -> bool:
    """안전 직무 공고인가: 제목에 안전 키워드가 있거나, 그룹 공채인데 직무 태그에 안전이 있는 경우."""
    if SAFETY_RE.search(p.title):
        return True
    tags = p.extra.get("sector", "") if p.source == "사람인" else p.listing_text
    return bool(re.search(r"공채|공개\s*채용|신입\s*(사원|직원)", p.title) and SAFETY_RE.search(tags))


def keep(p: Posting, today) -> tuple[bool, str]:
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
    elif not relevant(p):
        return False, "안전 직무 아님"
    if p.level == "경력":
        return False, "경력직"
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
BADGE = {"A": "🔴 ", "B": "🔵 ", "": ""}
GROUPS = [("정규직", "[정규직]"), ("계약직", "[계약직]"), ("인턴", "[인턴]"), ("기타/미표기", "[고용형태 미표기]")]
LEGEND = "🔴 데이터센터·하이테크·삼성·하이닉스 관련 · 🔵 대기업군·외국계 회사 (둘 다 해당하면 🔴)"


def md_cell(s):
    return clean(s).replace("|", "\\|") or "-"


def sort_key(p):
    return ({"A": 0, "B": 1}.get(p.hilite, 2), p.deadline_date or "9999")


def render_md(postings, failures, now, stats):
    L = [f"# 안전관리자 채용 브리핑 — {now:%Y-%m-%d (%a) %H:%M} KST", ""]
    L.append(f"신입·경력무관·인턴 공고 **{len(postings)}건** (경력직·마감 제외, 중복은 상위 사이트 우선)")
    L += ["", f"범례: {LEGEND}", ""]
    for key, tag in GROUPS:
        rows = sorted([p for p in postings if p.employment == key], key=sort_key)
        if not rows:
            continue
        L += [f"## {tag} {len(rows)}건", ""]
        L.append("| 구분 | 업체명 | 공고명 | 지원 자격 (학과·자격·영어·학력) | 우대 사항 | 접수기한 | 출처 |")
        L.append("|---|---|---|---|---|---|---|")
        for p in rows:
            corp = BADGE[p.hilite] + (f"**{md_cell(p.company)}**" if p.hilite else md_cell(p.company))
            L.append(f"| {md_cell(p.level)} | {corp} | {md_cell(p.title)} | {md_cell(p.qualification)} "
                     f"| {md_cell(p.preferred)} | {md_cell(p.deadline)} | [{p.source}]({p.url}) |")
        L.append("")
    L += ["---", "", "**사이트별 수집 현황**", ""]
    for name, st in stats.items():
        L.append(f"- {name}: {st}")
    if failures:
        L += ["", "**수집 실패**", ""] + [f"- {n}: {e}" for n, e in failures]
    L += ["", "_지원 자격·우대 사항은 상세 페이지에서 자동 추출한 요약입니다. 지원 전 원문을 확인하세요._"]
    return "\n".join(L) + "\n"


def render_html(postings, failures, now, stats):
    e = html.escape
    parts = []
    for key, tag in GROUPS:
        rows = sorted([p for p in postings if p.employment == key], key=sort_key)
        if not rows:
            continue
        trs = "".join(
            f'<tr class="h{p.hilite}"><td>{e(p.level)}</td><td class="corp">{BADGE[p.hilite]}{e(p.company or "-")}</td>'
            f"<td>{e(p.title)}</td><td>{e(p.qualification or '-')}</td><td>{e(p.preferred or '-')}</td>"
            f'<td class="dl">{e(p.deadline)}</td><td><a href="{e(p.url)}" target="_blank" rel="noopener">{e(p.source)}</a></td></tr>'
            for p in rows)
        parts.append(f"<h2>{e(tag)} <span>{len(rows)}건</span></h2><div class=\"wrap\"><table><thead><tr>"
                     "<th>구분</th><th>업체명</th><th>공고명</th><th>지원 자격</th><th>우대 사항</th><th>접수기한</th><th>출처</th>"
                     f"</tr></thead><tbody>{trs}</tbody></table></div>")
    st = "".join(f"<li>{e(n)}: {e(s)}</li>" for n, s in stats.items())
    fl = "".join(f"<li>{e(n)}: {e(x)}</li>" for n, x in failures)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>안전관리자 채용 브리핑</title>
<style>
:root{{--bg:#fff;--ink:#1c2530;--muted:#66707a;--line:#e3e6ea;--a:#fde8e8;--a-ink:#b42318;--b:#e6f0fd;--b-ink:#1d4ed8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#14181d;--ink:#e6e9ec;--muted:#9aa4ae;--line:#2a3139;--a:#3a1d1d;--a-ink:#ff8a80;--b:#172a44;--b-ink:#8ab4ff}}}}
body{{margin:0;padding:16px;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Noto Sans KR",sans-serif}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:16px;margin:24px 0 8px}} h2 span{{color:var(--muted);font-weight:500}}
.legend span{{display:inline-block;padding:2px 8px;border-radius:4px;margin-right:6px}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;min-width:900px}}
th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
th{{font-size:12px;color:var(--muted)}} tr.hA{{background:var(--a)}} tr.hA .corp{{color:var(--a-ink);font-weight:700}}
tr.hB{{background:var(--b)}} tr.hB .corp{{color:var(--b-ink);font-weight:700}} .dl{{white-space:nowrap}}
a{{color:var(--b-ink)}} .note{{color:var(--muted);font-size:12px}}
</style></head><body>
<h1>안전관리자 채용 브리핑 — {now:%Y-%m-%d %H:%M} KST</h1>
<p>신입·경력무관·인턴 공고 <b>{len(postings)}건</b> (경력직·마감 제외, 중복은 상위 사이트 우선)</p>
<p class="legend"><span style="background:var(--a);color:var(--a-ink)">🔴 데이터센터·하이테크·삼성·하이닉스</span><span style="background:var(--b);color:var(--b-ink)">🔵 대기업군·외국계</span></p>
{''.join(parts)}
<h2>사이트별 수집 현황</h2><ul>{st}</ul>{f'<h2>수집 실패</h2><ul>{fl}</ul>' if fl else ''}
<p class="note">지원 자격·우대 사항은 상세 페이지에서 자동 추출한 요약입니다. 지원 전 원문을 확인하세요.</p>
</body></html>"""


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="briefings", help="출력 디렉터리")
    ap.add_argument("--max-detail", type=int, default=150, help="상세 페이지 최대 조회 수")
    args = ap.parse_args()

    now = dt.datetime.now(KST)
    today = now.date()
    f = Fetcher()
    raw, failures, stats = [], [], {}
    for name, fn, _ in SOURCES:
        try:
            found = fn(f)
            raw.append((name, found))
        except Exception as e:  # 사이트 하나가 실패해도 나머지는 계속
            failures.append((name, f"{type(e).__name__}: {e}"[:160]))
            stats[name] = "수집 실패"

    kept, n_detail = [], 0
    for name, found in raw:
        counts = {"목록": len(found), "채택": 0}
        for p in found:
            # 목록 단계에서 명백히 무관한 것은 상세 조회 전에 거른다
            if p.extra.get("posted") is None and not relevant(p):
                counts["안전 직무 아님"] = counts.get("안전 직무 아님", 0) + 1
                continue
            # 목록에 '경력 n년'만 있는 공고(사람인·워커)는 경력직으로 보고 상세 조회 없이 제외
            lv = p.level or ""
            if p.source in ("사람인", "워커") and lv.startswith("경력") and not NEWBIE_RE.search(lv):
                counts["경력직"] = counts.get("경력직", 0) + 1
                continue
            if n_detail < args.max_detail:
                try:
                    url = p.url
                    if p.source == "사람인":
                        url = f"https://www.saramin.co.kr/zf_user/jobs/relay/view-detail?rec_idx={p.extra['rec_idx']}&rec_seq=0"
                    t = soup_text(f.get(url, encoding="cp949" if p.source == "워커" else None))
                    if p.extra.get("posted") is not None:  # 게시판: 메뉴 등 사이트 공통부 제거, 본문만
                        i = t.find(p.title[:12])
                        t = t[i:] if i >= 0 else t
                    p.detail_text = t[:15000]
                    n_detail += 1
                    time.sleep(0.4)
                except Exception as e:
                    print(f"[detail] {p.url}: {e}", file=sys.stderr)
            analyze(p, today)
            ok, why = keep(p, today)
            if not ok:
                counts[why] = counts.get(why, 0) + 1
                continue
            if is_dup(p, kept):
                counts["중복(상위 사이트 우선)"] = counts.get("중복(상위 사이트 우선)", 0) + 1
                continue
            counts["채택"] += 1
            kept.append(p)
        stats[name] = ", ".join(f"{k} {v}" for k, v in counts.items())

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    md = render_md(kept, failures, now, stats)
    (out / f"{today:%Y-%m-%d}.md").write_text(md, encoding="utf-8")
    (out / "latest.md").write_text(md, encoding="utf-8")
    (out / "latest.html").write_text(render_html(kept, failures, now, stats), encoding="utf-8")
    for p in kept:
        p.detail_text = p.detail_text[:1500]
    (out / "latest.json").write_text(json.dumps(
        {"generated_at": now.isoformat(), "postings": [asdict(p) for p in kept], "failures": failures, "stats": stats},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(md)
    return 0 if len(failures) < len(SOURCES) else 2


if __name__ == "__main__":
    sys.exit(main())
