# /// script
# requires-python = ">=3.10"
# ///
"""자기소개서 자동 작성 대상 공고 선정.

브리핑(briefings/latest.json)에서 관심 기업(대기업 계열·외국계·코스피·코스닥)의
정규직 안전관리자 공고 중 접수 마감이 10일 이내로 들어온 공고를 고른다.
이미 초안이 있는 공고(폴더 안 .md 에 같은 공고 URL이 적힌 것)는 건너뛴다.

    uv run safety_jobs/cover_letters.py --briefing briefings/latest.json [--briefing other/latest.json]

가장 최근(generated_at) 브리핑을 쓰고, 대상 목록을 JSON으로 출력한다.
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

KST = dt.timezone(dt.timedelta(hours=9))
OUT_DIR = Path("프로젝트/claude 자기소개서/현대건설 신입사원 자기소개서")
LEAD_DAYS = 10  # 마감 10일 전부터 작성 (그 뒤에 처음 수집된 공고는 수집 즉시)
TARGET_GROUPS = ("대기업 계열", "외국계")
TARGET_MARKETS = ("코스피", "코스닥")


def load_latest(paths):
    best = None
    for p in paths:
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if best is None or d.get("generated_at", "") > best.get("generated_at", ""):
            best = d
    return best


def tags_of(p):
    x = p.get("extra") or {}
    tags = [g for g in x.get("groups") or [] if g in TARGET_GROUPS]
    if x.get("listed") in TARGET_MARKETS:
        tags.append(x["listed"])
    return tags


def drafted_urls(out_dir):
    urls = set()
    for f in out_dir.glob("*.md"):
        for m in re.finditer(r"공고 URL:\s*<?(\S+?)>?\s*$", f.read_text(encoding="utf-8"), re.M):
            urls.add(m.group(1))
    return urls


def slug(s, n=30):
    s = re.sub(r"\(주\)|㈜|주식회사|\[[^\]]*\]", "", s)
    s = re.sub(r"[\\/:*?\"<>|()\[\]\s]+", " ", s).strip()
    return s[:n].strip().replace(" ", "_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--briefing", action="append", default=[], help="latest.json (여러 개면 최신 것)")
    ap.add_argument("--out", default=str(OUT_DIR), help="초안 폴더")
    ap.add_argument("--days", type=int, default=LEAD_DAYS)
    ap.add_argument("--today", help="YYYY-MM-DD (기본: 오늘 KST)")
    args = ap.parse_args()

    d = load_latest(args.briefing or ["briefings/latest.json"])
    if d is None:
        print("브리핑 파일을 읽지 못함", file=sys.stderr)
        return 2
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(KST).date()
    out = Path(args.out)
    done = drafted_urls(out) if out.exists() else set()

    targets = []
    for p in d.get("postings", []):
        if p.get("employment") != "정규직" or not p.get("deadline_date"):
            continue
        tags = tags_of(p)
        if not tags:
            continue
        left = (dt.date.fromisoformat(p["deadline_date"]) - today).days
        if not 0 < left <= args.days or p["url"] in done:
            continue
        targets.append({
            "company": p["company"], "title": p["title"], "url": p["url"], "source": p["source"],
            "deadline_date": p["deadline_date"], "days_left": left, "tags": tags,
            "industry": p.get("industry", ""), "level": p.get("level", ""),
            "qualification": p.get("qualification", ""), "preferred": p.get("preferred", ""),
            "detail_text": (p.get("detail_text") or "")[:1500],
            "file": str(out / f"{p['deadline_date']}_{slug(p['company'], 20)}_{slug(p['title'])}.md"),
        })
    targets.sort(key=lambda t: t["deadline_date"])
    print(json.dumps({"generated_at": d.get("generated_at"), "today": today.isoformat(),
                      "already_drafted": len(done), "targets": targets}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
