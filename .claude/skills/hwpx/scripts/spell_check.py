#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spell_check.py — 생성된 HWPX/섹션 XML의 한글 맞춤법·띄어쓰기 검사.

공공기관 보고서에서 자주 나오는 맞춤법·띄어쓰기 오류를 규칙(패턴) 기반으로
점검한다. 형태소 분석기 없이 고빈도 오류만 확정적으로 잡는 보조 검사기이며,
문맥이 필요한 미묘한 맞춤법(로서/로써, 든지/던지, 이/히 부사 등)까지 완전
검출하지는 않는다 — 그런 항목은 `references/korean-spelling.md`의 교정
지침에 따라 최종 사람(또는 Claude)의 교열로 마무리한다.

본문 문단과 표 셀 텍스트를 모두 검사한다(맞춤법은 어디서든 지켜야 하므로).

Usage:
    python spell_check.py output/report.hwpx
    python spell_check.py section0.xml

종료코드: 0 통과 / 1 의심 발견 / 2 사용오류
"""
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree

HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
HP_P = f"{{{HP}}}p"
HP_RUN = f"{{{HP}}}run"
HP_T = f"{{{HP}}}t"

# (정규식, 올바른 표기, 분류, 설명) — 오탐이 적은 고빈도 오류만 수록.
# 각 규칙은 '틀린 표기'를 찾아 '올바른 표기'를 제안한다.
RULES = [
    # 되/돼 (되 + 어 축약형이 필요한 자리)
    (r"됬", "됐", "되/돼", "'되었'의 준말은 '됐'"),
    (r"되서", "돼서", "되/돼", "'되어서'의 준말은 '돼서'"),
    (r"되요", "돼요", "되/돼", "'되어요'의 준말은 '돼요'"),
    # 안/않 (부정 부사 '안'과 어미 '않'의 혼동)
    (r"않되", "안 되", "안/않", "부정은 부사 '안'+'되다' → '안 되'"),
    (r"않돼", "안 돼", "안/않", "부정은 부사 '안'+'돼' → '안 돼'"),
    # 웬/왠
    (r"웬지", "왠지", "웬/왠", "'왜인지'의 준말은 '왠지'"),
    (r"왠만", "웬만", "웬/왠", "'웬만하다'가 올바른 표기"),
    (r"왠일", "웬일", "웬/왠", "'웬일'이 올바른 표기"),
    # 자주 틀리는 낱말
    (r"몇일", "며칠", "맞춤법", "'며칠'이 올바른 표기"),
    (r"역활", "역할", "맞춤법", "'역할'이 올바른 표기"),
    (r"오랜동안", "오랫동안", "맞춤법", "'오랫동안'이 올바른 표기"),
    (r"폭팔", "폭발", "맞춤법", "'폭발'이 올바른 표기"),
    (r"회손", "훼손", "맞춤법", "'훼손'이 올바른 표기"),
    (r"설레임", "설렘", "맞춤법", "'설렘'이 올바른 표기"),
    (r"일찌기", "일찍이", "맞춤법", "'일찍이'가 올바른 표기"),
    (r"금새", "금세", "맞춤법", "'금세'('금시에')가 올바른 표기"),
    (r"희안", "희한", "맞춤법", "'희한하다'가 올바른 표기"),
    (r"뇌졸증", "뇌졸중", "맞춤법", "'뇌졸중'이 올바른 표기"),
    (r"갯수", "개수", "맞춤법", "'개수'가 올바른 표기"),
    (r"촛점", "초점", "맞춤법", "'초점'이 올바른 표기"),
    (r"아니예요", "아니에요", "맞춤법", "'아니에요'가 올바른 표기"),
    (r"뵈요", "봬요", "맞춤법", "'뵈어요'의 준말은 '봬요'"),
    # 띄어쓰기
    (r"(?<=[가-힣])및|및(?=[가-힣])", "및", "띄어쓰기", "'및'은 앞뒤를 띄어 씀"),
    (r"[가-힣]수(있|없)", "수 있/없", "띄어쓰기", "의존명사 '수'는 앞말과 띄어 씀"),
    (r"(할|한|된|될|하는|있는|없는|주는|받는)것", "… 것", "띄어쓰기",
     "의존명사 '것'은 앞말과 띄어 씀"),
]

COMPILED = [(re.compile(pat), fix, cat, desc) for pat, fix, cat, desc in RULES]


def load_section(path: Path):
    """HWPX(zip)면 Contents/section0.xml을, 아니면 파일 자체를 파싱."""
    if zipfile.is_zipfile(str(path)):
        with zipfile.ZipFile(str(path)) as zf:
            return etree.fromstring(zf.read("Contents/section0.xml"))
    return etree.fromstring(path.read_bytes())


def para_own_text(p) -> str:
    """문단 자신의 텍스트만 이어 붙임 (중첩 표 셀은 각자의 문단으로 별도 검사)."""
    parts = []
    for run in p.findall(HP_RUN):
        for t in run.findall(HP_T):
            if t.text:
                parts.append(t.text)
    return "".join(parts)


def check(path: Path):
    """[(분류, 매칭문자열, 제안, 설명, 미리보기)] 목록 반환."""
    root = load_section(path)
    findings = []
    for p in root.iter(HP_P):             # 본문 + 표 셀 문단 모두
        text = para_own_text(p)
        if not text.strip():
            continue
        for rx, fix, cat, desc in COMPILED:
            for m in rx.finditer(text):
                s, e = m.start(), m.end()
                lo, hi = max(0, s - 8), min(len(text), e + 8)
                preview = ("…" if lo > 0 else "") + text[lo:hi] + \
                          ("…" if hi < len(text) else "")
                findings.append((cat, m.group(0), fix, desc, preview.strip()))
    return findings


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python spell_check.py <file.hwpx | section0.xml>",
              file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"오류: 파일을 찾을 수 없음: {path}", file=sys.stderr)
        sys.exit(2)

    findings = check(path)
    print(f"맞춤법·띄어쓰기 검사: {path}")
    if not findings:
        print("  의심 항목 없음 (규칙 기반 고빈도 오류 미검출).")
        print("VALID: 맞춤법 규칙 통과")
        sys.exit(0)

    for cat, hit, fix, desc, preview in findings:
        print(f"  X [{cat}] '{hit}' → '{fix}' — {desc}")
        print(f"      {preview}")
    print(f"  의심 {len(findings)}건 — 문맥 확인 후 교정 필요")
    print("SUSPECT: 맞춤법 의심 항목 발견")
    sys.exit(1)


if __name__ == "__main__":
    main()
