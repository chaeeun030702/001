# /// script
# requires-python = ">=3.10"
# ///
"""자기소개서 자동 작성 대상 공고 선정.

브리핑(briefings/latest.json)의 모든 공고 중 접수 마감이 10일 이내로 들어온 공고와
'채용 시 마감'(상시·수시·인재 Pool 등 마감일 없는 공고)을 고른다(2026-10-15 사용자 요청 — 고용형태·기업 구분과
관계없이 작성, 제외 목록에 있는 공고와 장애인·보훈 전형 공고는 뺀다).
이미 초안이 있는 공고(drafts/index.json 에 같은 공고 URL이 있는 것)는 건너뛴다.
초안과 개인 자료는 공개 저장소가 아니라 비공개 아티팩트(자기소개서 일일 브리핑)에 둔다.

    python3 safety_jobs/cover_letters.py --briefing briefings/latest.json [--briefing other/latest.json] --done drafts/index.json

브리핑을 여러 개 주면 공고를 URL 기준으로 합친다(같은 URL은 최신 generated_at 쪽 값). 대상 목록을 JSON으로 출력한다.

외국계 공고도 같은 기준으로 대상에 넣는다(규칙 40 영문 커버레터 추가). 브리핑 페이지의 '작성 요청' 단추로
요청한 공고(--requested, 아티팩트 db requested 컬렉션, 초안 id 기준)는 마감 기간과 관계없이 대상에 넣는다.

    ... --requested requested.json --foreign-out foreign.json
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

KST = dt.timezone(dt.timedelta(hours=9))
LEAD_DAYS = 10  # 마감 10일 전부터 작성 (그 뒤에 처음 수집된 공고는 수집 즉시)
OPEN_DEADLINE = re.compile(r"채용\s*시|상시|수시")  # 마감일 없는 공고(채용 시 마감)
SKIP_TITLE = re.compile(r"장애인|보훈")  # 지원 자격이 맞지 않는 전형
TARGET_GROUPS = ("대기업 계열", "외국계")
TARGET_MARKETS = ("코스피", "코스닥")


def load_latest(paths):
    """브리핑 여러 개의 공고를 URL 기준으로 합친다(최신 generated_at 이 우선)."""
    docs = []
    for p in paths:
        try:
            docs.append(json.loads(Path(p).read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    if not docs:
        return None
    docs.sort(key=lambda d: d.get("generated_at", ""))
    merged = {}
    for d in docs:
        for p in d.get("postings", []):
            merged[p["url"]] = p
    return {"generated_at": docs[-1].get("generated_at"), "postings": list(merged.values())}


def tags_of(p):
    x = p.get("extra") or {}
    tags = [g for g in x.get("groups") or [] if g in TARGET_GROUPS]
    if x.get("listed") in TARGET_MARKETS:
        tags.append(x["listed"])
    return tags


def drafted_urls(index_path):
    try:
        return {d["url"] for d in json.loads(Path(index_path).read_text(encoding="utf-8"))}
    except (OSError, ValueError, KeyError, TypeError):
        return set()


def draft_id(url):
    return hashlib.sha1(url.encode()).hexdigest()[:8]


def load_excluded(path):
    sys.path.insert(0, str(Path(__file__).parent))
    from cover_brief import load_excluded as _load
    return _load(path)


def load_excluded_all(paths):
    """제외 목록 여러 개 → 초안 id 집합. 자소서 브리핑 excluded(문서 id = 초안 id)와
    채용 브리핑 excluded(문서마다 url)를 함께 받는다 — url 이 있으면 sha1(url)[:8] 로 바꾼다."""
    out = set()
    for path in paths or []:
        out |= load_excluded(path)
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            data = data.get("excluded") or data.get("docs") or list(data.values())
        for x in data or []:
            if isinstance(x, dict) and x.get("url"):
                out.add(draft_id(x["url"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--briefing", action="append", default=[], help="latest.json (여러 개면 최신 것)")
    ap.add_argument("--done", default="drafts/index.json", help="작성된 초안 목록")
    ap.add_argument("--days", type=int, default=LEAD_DAYS)
    ap.add_argument("--today", help="YYYY-MM-DD (기본: 오늘 KST)")
    ap.add_argument("--exclude", action="append", default=[],
                    help="제외 목록 JSON(자소서 브리핑 '선택 삭제' 초안 id, 또는 채용 브리핑 excluded 의 url 목록). 여러 번 줄 수 있음")
    ap.add_argument("--requested", help="작성 요청 JSON(브리핑 페이지에서 '작성 요청'한 외국계 공고, 초안 id 기준)")
    ap.add_argument("--foreign-out", help="요청 전 외국계 공고 목록을 저장할 JSON 경로(cover_brief.py --foreign)")
    args = ap.parse_args()

    d = load_latest(args.briefing or ["briefings/latest.json"])
    if d is None:
        print("브리핑 파일을 읽지 못함", file=sys.stderr)
        return 2
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(KST).date()
    done = drafted_urls(args.done)
    excluded = load_excluded_all(args.exclude)
    requested = load_excluded(args.requested)

    targets, foreign = [], []
    for p in d.get("postings", []):
        pid = draft_id(p["url"])
        if p["url"] in done or pid in excluded or SKIP_TITLE.search(p.get("title", "")):
            continue
        tags = tags_of(p)
        if p.get("deadline_date"):
            left = (dt.date.fromisoformat(p["deadline_date"]) - today).days
            if left < 0 or (left > args.days and pid not in requested):
                continue
            file = f"drafts/{p['deadline_date']}_{pid}.md"
        elif OPEN_DEADLINE.search(p.get("deadline", "")):
            left, file = None, f"drafts/open_{pid}.md"
        else:
            continue
        targets.append({
            "company": p["company"], "title": p["title"], "url": p["url"], "source": p["source"],
            "deadline_date": p.get("deadline_date") or "", "deadline": p.get("deadline", ""), "days_left": left,
            "tags": tags, "employment": p.get("employment", ""), "company_type": p.get("company_type", ""),
            "industry": p.get("industry", ""), "level": p.get("level", ""),
            "qualification": p.get("qualification", ""), "preferred": p.get("preferred", ""),
            "detail_text": (p.get("detail_text") or "")[:1500],
            "id": pid, "file": file, "requested": pid in requested,
        })
    targets.sort(key=lambda t: t["deadline_date"] or "9999")
    foreign.sort(key=lambda t: t["deadline_date"])
    if args.foreign_out:
        Path(args.foreign_out).write_text(json.dumps(foreign, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"generated_at": d.get("generated_at"), "today": today.isoformat(),
                      "already_drafted": len(done), "targets": targets,
                      "foreign_listed": len(foreign)}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
