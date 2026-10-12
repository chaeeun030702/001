#!/usr/bin/env python3
"""수집 직후 '오늘 처음 찾은 신규 공고'를 이메일로 보낸다 (GitHub Actions에서 실행).

환경변수 (GitHub Secrets):
  MAIL_USER          보내는 Gmail 주소 (SMTP 로그인 ID)
  MAIL_APP_PASSWORD  Gmail 앱 비밀번호 (16자리, 2단계 인증 필요)
  MAIL_TO            받는 주소 (쉼표로 여러 개 가능, 없으면 MAIL_USER)
  SITE_URL           (선택) 브리핑 웹 주소 — 메일 하단 '웹에서 보기' 링크
  SMTP_HOST/SMTP_PORT (선택) 기본 smtp.gmail.com / 465

같은 날 수집이 여러 번 돌아도(19:07·19:27·수동 실행) 이미 보낸 공고는 다시 보내지 않도록
briefings/notified.json 에 보낸 주소를 기록한다. 이 파일은 워크플로가 briefings/ 와 함께 커밋한다.
시크릿이 없거나 신규 공고가 0건이면 보내지 않고 정상 종료한다.
"""
import argparse
import html
import json
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

BADGE = {"A": "🔴 ", "B": "🔵 ", "F": "🌐 ", "": ""}
ORDER = {"A": 0, "B": 1, "F": 2}


def load_new(briefings: Path):
    data = json.loads((briefings / "latest.json").read_text(encoding="utf-8"))
    today = data["generated_at"][:10]  # 수집기가 KST 기준으로 기록한 날짜
    new = [p for p in data["postings"] if (p.get("extra") or {}).get("first_seen") == today]
    new.sort(key=lambda p: (ORDER.get(p.get("hilite", ""), 3), p.get("deadline_date") or "9999"))
    return today, new


def load_sent(path: Path, today: str):
    if path.exists():
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
            if d.get("date") == today:
                return set(d.get("urls", []))
        except (ValueError, OSError):
            pass
    return set()


def render(today: str, rows: list, site_url: str):
    md = today[5:].replace("-", "/")
    subject = f"[안전관리자 채용] 신규 공고 {len(rows)}건 ({md})"
    text = [subject, ""]
    body = []
    for p in rows:
        company = BADGE.get(p.get("hilite", ""), "") + (p.get("company") or "")
        meta = " · ".join(x for x in (p.get("employment"), p.get("level"), p.get("deadline"), p.get("source")) if x)
        text += [f"- {company} | {p.get('title', '')}", f"  {meta}", f"  {p.get('url', '')}", ""]
        body.append(
            "<tr>"
            f"<td style='padding:8px;border-bottom:1px solid #e2e4e9'><b>{html.escape(company)}</b></td>"
            f"<td style='padding:8px;border-bottom:1px solid #e2e4e9'>"
            f"<a href='{html.escape(p.get('url', ''), quote=True)}'>{html.escape(p.get('title', ''))}</a>"
            f"<br><small style='color:#737373'>{html.escape(meta)}</small></td></tr>"
        )
    link = f"<p><a href='{html.escape(site_url, quote=True)}'>웹에서 전체 브리핑 보기</a></p>" if site_url else ""
    if site_url:
        text.append(f"웹에서 보기: {site_url}")
    page = (
        "<div style='font-family:sans-serif;font-size:14px'>"
        f"<h3>🆕 신규 공고 {len(rows)}건 ({md})</h3>"
        f"<table style='border-collapse:collapse;width:100%'>{''.join(body)}</table>{link}"
        "<p style='color:#737373;font-size:12px'>지원 자격·우대 사항은 자동 추출 요약이므로 지원 전 원문을 확인하세요.</p></div>"
    )
    return subject, "\n".join(text), page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--briefings", default="briefings")
    ap.add_argument("--dry-run", action="store_true", help="메일을 보내지 않고 내용만 출력")
    args = ap.parse_args()
    b = Path(args.briefings)

    user = os.environ.get("MAIL_USER", "").strip()
    pw = os.environ.get("MAIL_APP_PASSWORD", "").strip()
    to = [x.strip() for x in (os.environ.get("MAIL_TO") or user).split(",") if x.strip()]
    if not args.dry_run and not (user and pw and to):
        print("[notify] MAIL_USER/MAIL_APP_PASSWORD 시크릿이 없어 건너뜀")
        return 0

    today, new = load_new(b)
    sent_path = b / "notified.json"
    sent = load_sent(sent_path, today)
    rows = [p for p in new if p.get("url") not in sent]
    if not rows:
        print(f"[notify] {today} 보낼 신규 공고 없음 (신규 {len(new)}건, 이미 발송 {len(new) - len(rows)}건)")
        return 0

    subject, text, page = render(today, rows, os.environ.get("SITE_URL", "").strip())
    if args.dry_run:
        print(text)
        return 0

    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = subject, user, ", ".join(to)
    msg.set_content(text)
    msg.add_alternative(page, subtype="html")
    with smtplib.SMTP_SSL(os.environ.get("SMTP_HOST", "smtp.gmail.com"), int(os.environ.get("SMTP_PORT", "465")), timeout=60) as s:
        s.login(user, pw)
        s.send_message(msg)

    sent_path.write_text(
        json.dumps({"date": today, "urls": sorted(sent | {p["url"] for p in rows})}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"[notify] {len(rows)}건 발송 완료 → {len(to)}명")
    return 0


if __name__ == "__main__":
    sys.exit(main())
