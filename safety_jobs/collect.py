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
사이트의 것을 남긴다. 경력직 전용 공고는 제외하고 신입/경력무관/인턴만 남긴다.

    uv run safety_jobs/collect.py                 # 마크다운 브리핑을 stdout으로
    uv run safety_jobs/collect.py --json out.json # 원자료도 JSON으로 저장

사이트 구조가 바뀌어도 동작하도록 사이트별 셀렉터 → 범용(표/목록 행) 순서로
시도한다. 접근이 막힌 사이트는 브리핑 하단 '수집 실패'에 표시된다.
"""

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

KST = dt.timezone(dt.timedelta(hours=9))

# (이름, URL, 안전 키워드 필터 필요 여부) — 순서 = 중복 시 우선순위
SOURCES = [
    ("잡코리아", "https://www.jobkorea.co.kr/theme/entry-level-internship", True),
    ("사람인", "https://www.saramin.co.kr/zf_user/search?searchword=%EC%95%88%EC%A0%84%EA%B4%80%EB%A6%AC%EC%9E%90&go=&flag=n&searchMode=1&searchType=search&search_done=y&search_optional_item=n", True),
    ("링커리어", "https://linkareer.com/search?direction=DESC&page=1&q=%EC%95%88%EC%A0%84%EA%B4%80%EB%A6%AC%EC%9E%90&sort=RELEVANCE&tab=open-activity", True),
    ("워커", "https://www.worker.co.kr/job/list.asp", True),
    ("서울과기대 안전공학과", "https://safety.seoultech.ac.kr/b_information/job_info", False),
    ("충북대 안전공학과", "https://safety.chungbuk.ac.kr/safety5_2", False),
    ("인천대 안전공학과", "https://www.inu.ac.kr/safety/3207/subview.do", False),
    ("부경대 안전공학과", "https://safety.pknu.ac.kr/safety/2080", False),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

SAFETY_RE = re.compile(r"안전|보건|HSE|EHS|SHE|산업위생|소방|건설안전|방재")
JOB_HINT_RE = re.compile(r"채용|모집|신입|인턴|계약|정규|경력|공고|구인|사원")
NEWBIE_RE = re.compile(r"신입|인턴|경력\s*무관|경력무관|신입[·/ ]?경력|졸업\s*예정")
CAREER_ONLY_RE = re.compile(r"경력\s*\d+\s*년\s*(이상|↑)|경력직|경력\s*사원")
DEADLINE_RE = re.compile(
    r"(20\d{2}[.\-/년]\s*\d{1,2}[.\-/월]\s*\d{1,2}일?|~\s*\d{1,2}/\d{1,2}(\([월화수목금토일]\))?"
    r"|상시\s*채용|채용\s*시\s*마감|D-\d+|오늘\s*마감|내일\s*마감)"
)
MAJOR_RE = re.compile(r"[가-힣A-Za-z]{2,12}(?:공학|학과|계열|전공)(?:\s*전공자?)?")
CERT_RE = re.compile(
    r"(?:산업|건설|가스|전기|소방|화공|기계|위험물|인간공학)?안전(?:기술|산업)?(?:기사|산업기사|기술사|지도사)"
    r"|산업위생관리(?:산업)?기사|소방설비(?:산업)?기사|위험물(?:산업기사|기능장)|환경기사|대기환경기사|수질환경기사"
    r"|전기기사|가스기사|건축기사|토목기사|소방시설관리사|보건관리자|간호사|운전면허"
)
ENG_RE = re.compile(r"(TOEIC|토익|TOEIC\s*Speaking|토스|OPIc|오픽|TEPS|텝스|영어\s*(회화|능통|가능|우수))(?:(?!우대|필수|자격)[^,\n;]){0,15}", re.I)
PREF_BLOCK_RE = re.compile(r"우대\s*(사항|조건)?\s*[:：]?\s*(.{0,200})")


@dataclass
class Posting:
    source: str
    title: str
    company: str
    url: str
    listing_text: str = ""
    detail_text: str = ""
    employment: str = ""  # 정규직 / 계약직 / 인턴 / ""
    level: str = ""       # 신입 / 경력무관 / 인턴 / 신입·경력
    majors: list = field(default_factory=list)
    certs: list = field(default_factory=list)
    english: list = field(default_factory=list)
    preferred: str = ""
    deadline: str = ""


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def fetch(client: httpx.Client, url: str) -> str:
    r = client.get(url, follow_redirects=True, timeout=25)
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------- 목록 파싱
def parse_saramin(soup, base):
    out = []
    for item in soup.select("div.item_recruit"):
        a = item.select_one("h2.job_tit a")
        if not a:
            continue
        corp = item.select_one("strong.corp_name a, .corp_name a")
        out.append((clean(a.get("title") or a.get_text()), clean(corp.get_text()) if corp else "",
                    urljoin(base, a.get("href", "")), clean(item.get_text(" "))))
    return out


def parse_generic(soup, base):
    """표 행/목록 항목 중 링크가 있는 것을 공고 후보로 본다."""
    out, seen = [], set()
    for row in soup.select("tr, li, article, div[class*=item], div[class*=list] > div"):
        a = row.find("a", href=True)
        if not a:
            continue
        href = a["href"]
        if href.startswith(("javascript:void", "#")) and not a.get("onclick"):
            continue
        title = clean(a.get("title") or a.get_text(" "))
        text = clean(row.get_text(" "))
        if len(title) < 6 or len(text) > 600:
            continue
        url = urljoin(base, href)
        if url in seen:
            continue
        seen.add(url)
        corp = row.select_one("[class*=corp], [class*=company], [class*=name]")
        out.append((title, clean(corp.get_text()) if corp else "", url, text))
    return out


def parse_next_data(html, base):
    """Next.js 페이지(링커리어 등)의 __NEXT_DATA__에서 제목/링크를 찾는다."""
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return []
    out = []

    def walk(o):
        if isinstance(o, dict):
            title = o.get("title")
            if isinstance(title, str) and o.get("id") is not None:
                org = o.get("organizationName") or ""
                if not org and isinstance(o.get("organization"), dict):
                    org = o["organization"].get("name", "")
                out.append((clean(title), clean(org or ""), urljoin(base, f"/activity/{o['id']}"),
                            clean(json.dumps(o, ensure_ascii=False)[:600])))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    try:
        walk(json.loads(m.group(1)))
    except json.JSONDecodeError:
        return []
    return out


def list_postings(client, name, url, need_filter):
    html = fetch(client, url)
    soup = BeautifulSoup(html, "html.parser")
    rows = (parse_saramin(soup, url) if "saramin" in url else []) or parse_next_data(html, url) or parse_generic(soup, url)
    result = []
    for title, corp, link, text in rows:
        blob = f"{title} {text}"
        if need_filter and not SAFETY_RE.search(blob):
            continue
        if not need_filter and not (SAFETY_RE.search(blob) or JOB_HINT_RE.search(blob)):
            continue
        if not corp:
            corp = guess_company(title)
        result.append(Posting(name, title, corp, link, text))
    return result


def guess_company(title):
    m = re.match(r"^\s*[\[\(【]([^\]\)】]{2,30})[\]\)】]", title)
    if m and not re.search(r"채용|모집|공고|정규|계약|인턴|신입", m.group(1)):
        return clean(m.group(1))
    m = re.match(r"^\s*((?:\(주\)|㈜|주식회사)?\s*[가-힣A-Za-z0-9&]+(?:\(주\)|㈜)?)\s", title)
    return clean(m.group(1)) if m else ""


# ---------------------------------------------------------------- 상세 분석
def uniq(seq, limit=5):
    out = []
    for x in seq:
        x = clean(x)
        if x and x not in out:
            out.append(x)
    return out[:limit]


def analyze(p: Posting):
    text = f"{p.title} {p.listing_text} {p.detail_text}"
    head = f"{p.title} {p.listing_text}"

    if re.search(r"인턴", head):
        p.employment = "인턴"
    if re.search(r"계약직|기간제|촉탁", text):
        p.employment = p.employment or "계약직"
    if re.search(r"정규직", text) and not re.search(r"계약직|기간제", head):
        p.employment = "정규직" if p.employment != "인턴" else p.employment
    if re.search(r"정규직\s*전환", text) and p.employment == "인턴":
        p.employment = "인턴(정규직 전환형)"

    if re.search(r"경력\s*무관|경력무관", text):
        p.level = "경력무관"
    elif re.search(r"신입\s*[·/]\s*경력|신입\s*및\s*경력", text):
        p.level = "신입·경력"
    elif "인턴" in (p.employment or "") or "인턴" in head:
        p.level = "인턴"
    elif re.search(r"신입|졸업\s*예정", text):
        p.level = "신입"
    elif CAREER_ONLY_RE.search(text):
        p.level = "경력"

    p.majors = uniq(m.group(0) for m in MAJOR_RE.finditer(p.detail_text or p.listing_text)
                    if not re.search(r"우대|필수|이상", m.group(0)))
    p.certs = uniq(m.group(0) for m in CERT_RE.finditer(text))
    p.english = uniq((m.group(0) for m in ENG_RE.finditer(text)), 3)
    m = PREF_BLOCK_RE.search(p.detail_text)
    if m:
        p.preferred = clean(re.split(r"(근무|전형|접수|제출|급여|복리)", m.group(2))[0])[:120]
    dl = [d.group(0) for d in DEADLINE_RE.finditer(f"{p.listing_text} {p.detail_text}")]
    p.deadline = clean(dl[-1]) if dl else ""


def is_entry_level(p: Posting) -> bool:
    return p.level in ("신입", "경력무관", "인턴", "신입·경력") or (
        p.level == "" and not CAREER_ONLY_RE.search(p.title)
    )


def dedup_key(p: Posting) -> str:
    corp = re.sub(r"\(주\)|㈜|주식회사|\s", "", p.company)
    title = re.sub(r"[\[\]\(\)【】<>『』\"'·,.\-_/|:]|\s|20\d{2}년?|하반기|상반기", "", p.title)
    title = title.replace(corp, "") if corp else title
    return f"{corp}|{title[:25]}"


# ---------------------------------------------------------------- 출력
def md_escape(s):
    return clean(s).replace("|", "\\|") or "-"


def render(postings, failures, now):
    lines = [f"# 안전관리자 채용 브리핑 — {now:%Y-%m-%d (%a) %H:%M} KST", ""]
    lines.append(f"신입·경력무관·인턴 공고 {len(postings)}건 (경력직 제외, 중복은 상위 사이트 우선)")
    lines.append("")
    lines.append("| 구분 | 업체명 | 지원 자격 (학과·자격·영어) | 우대 사항 | 접수기한 | 출처 |")
    lines.append("|---|---|---|---|---|---|")
    for p in postings:
        tag = f"[{p.employment}] " if p.employment.startswith(("정규직", "계약직")) else ""
        kind = " / ".join(x for x in (p.level, p.employment) if x) or "확인 필요"
        qual = "; ".join(filter(None, [
            ", ".join(p.majors) and "학과: " + ", ".join(p.majors),
            ", ".join(p.certs) and "자격: " + ", ".join(p.certs),
            ", ".join(p.english) and "영어: " + ", ".join(p.english),
        ])) or "상세 확인"
        lines.append(
            f"| {md_escape(kind)} | {md_escape(tag + p.company)}<br>{md_escape(p.title)} | {md_escape(qual)} "
            f"| {md_escape(p.preferred)} | {md_escape(p.deadline)} | [{p.source}]({p.url}) |"
        )
    if failures:
        lines += ["", "**수집 실패**", ""] + [f"- {n}: {e}" for n, e in failures]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="원자료를 저장할 JSON 경로")
    ap.add_argument("--max-detail", type=int, default=60, help="상세 페이지 최대 조회 수")
    args = ap.parse_args()

    now = dt.datetime.now(KST)
    postings, failures, seen = [], [], set()
    with httpx.Client(headers=HEADERS, trust_env=True) as client:
        for name, url, need_filter in SOURCES:
            try:
                found = list_postings(client, name, url, need_filter)
            except Exception as e:  # 사이트 하나가 실패해도 나머지는 계속
                failures.append((name, f"{type(e).__name__}: {e}"[:160]))
                continue
            for p in found:
                key = dedup_key(p)
                if key in seen:  # 상위 사이트에서 이미 수집됨
                    continue
                seen.add(key)
                postings.append(p)

        for i, p in enumerate(postings):
            if i < args.max_detail:
                try:
                    soup = BeautifulSoup(fetch(client, p.url), "html.parser")
                    for t in soup(["script", "style", "nav", "header", "footer"]):
                        t.decompose()
                    p.detail_text = clean(soup.get_text(" "))[:8000]
                except Exception as e:
                    p.detail_text = ""
                    print(f"[detail] {p.url}: {e}", file=sys.stderr)
            analyze(p)

    postings = [p for p in postings if is_entry_level(p)]
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"generated_at": now.isoformat(), "postings": [asdict(p) for p in postings],
                       "failures": failures}, f, ensure_ascii=False, indent=2)
    print(render(postings, failures, now))
    return 0 if len(failures) < len(SOURCES) else 2


if __name__ == "__main__":
    sys.exit(main())
