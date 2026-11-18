# hwpx 스킬 설치·확장 작업 기록

- **저장소**: `chaeeun030702/001`
- **작업 브랜치**: `claude/compassionate-einstein-iamv4c`
- **스킬 원본**: https://github.com/kist-aix/hwpx (v0.4.0)
- **작성자**: chaeeun075@gmail.com / Claude Code

---

## 1. 작업 요약

이 세션에서 한글(HWPX) 보고서 자동 생성 스킬 `hwpx`를 설치하고, 업로드용으로 패키징한 뒤, **맞춤법·띄어쓰기 검사 기능**을 새로 추가했다.

| # | 사용자 요청 | 수행 내용 |
|---|-------------|-----------|
| 1 | `https://github.com/kist-aix/hwpx` 스킬 설치 | 리포지토리를 클론하여 프로젝트 `.claude/skills/hwpx/`에 설치, 의존성(`lxml`, `python-hwpx`) 설치, 브랜치에 커밋·푸시 |
| 2 | 사용자 지정 스킬에 추가 | 사용자 전역 `~/.claude/skills/hwpx/`에도 동일 설치 |
| 3 | '설정/스킬/내가 만듦'에 올릴 수 있도록 skill 파일로 생성 | 업로드용 `hwpx.zip`(최상위 `hwpx/SKILL.md` 구조) 패키지 생성·전달 |
| 4 | 스킬에 맞춤법 추가 | `scripts/spell_check.py` + `references/korean-spelling.md` 신규 작성, `SKILL.md` 연동, 재패키징·커밋·푸시 |
| 5 | 전체 기록과 파일을 md 파일로 저장 | 이 문서 |

---

## 2. 설치 위치

| 위치 | 경로 | 비고 |
|------|------|------|
| 프로젝트(커밋됨) | `.claude/skills/hwpx/` | 저장소에 영구 보존, 브랜치에 푸시 |
| 사용자 전역 | `~/.claude/skills/hwpx/` | 원격/임시 환경이라 세션 종료 시 소멸 |
| 업로드 패키지 | `hwpx.zip` | 설정 → 스킬 → 내가 만듦 업로드용 |

> **의존성**: `lxml`(필수), `python-hwpx`(텍스트 추출 시). 스킬 최초 호출 시 자동 설치되며, 이번 세션에서는 수동 설치 완료.

---

## 3. git 커밋 기록

```
46aeb63 Add Korean spell/spacing check to hwpx skill
0f577a3 Install hwpx skill (v0.4.0) into project skills
```

---

## 4. 스킬 디렉토리 구조

```
.claude/skills/hwpx/
├── SKILL.md                     # 스킬 본문 (맞춤법 검토 절 추가됨)
├── README.md, LICENSE, requirements.txt, .gitignore
├── scripts/
│   ├── build_hwpx.py            # report 템플릿 + XML → .hwpx 조립 (핵심)
│   ├── table_builder.py         # 표 템플릿 → XML 생성
│   ├── preview_table.py         # 표 미리보기 .hwpx
│   ├── extract_table_templates.py
│   ├── validate.py             # HWPX 구조 검증
│   ├── style_check.py          # 개조식 문체 규칙 검사 (□/❍ 길이·종결)
│   ├── spell_check.py          # ★신규 — 한글 맞춤법·띄어쓰기 검사
│   ├── text_extract.py         # 텍스트 추출 (python-hwpx)
│   └── office/{pack,unpack}.py
├── templates/
│   ├── base/                   # 내부 스켈레톤
│   ├── report/                 # 보고서 양식 (header.xml, section0.xml)
│   └── tables/                 # 표 템플릿 6종 (basic/status/budget/schedule/checklist/roadmap)
├── assets/                     # 표 라이브러리·시각 기준 .hwpx
└── references/
    ├── hwpx-format.md          # OWPML XML 요소 레퍼런스
    └── korean-spelling.md      # ★신규 — 맞춤법·띄어쓰기 교정 지침
```

---

## 5. 추가 기능: 맞춤법·띄어쓰기 검사

### 5.1 개요
- 규칙(패턴) 기반 검사기로, **오탐이 적은 고빈도 오류만 확정 검출**한다(형태소 분석기 아님).
- 본문 문단과 표 셀 텍스트를 모두 검사한다.
- 문맥이 필요한 미묘한 항목(로서/로써, 든지/던지, `-이`/`-히`, 되어↔돼 판단)은 `korean-spelling.md` 지침에 따라 생성 주체(Claude)가 직접 교열한다.

### 5.2 검증 결과
- 오류 혼합 샘플에서 5건 정확 검출(`됬`, `역활`, `할수있`, `않되`, `몇일`)
- 정상 문장·`및 `(정상 띄어쓰기)에 오탐 0건
- 실제 report 템플릿에 오탐 0건 통과

### 5.3 `SKILL.md` 반영 지점
- 디렉토리 트리에 `spell_check.py`, `korean-spelling.md` 추가
- 「맞춤법·띄어쓰기 검토」 절 신설 (문체 규칙 절 뒤)
- 워크플로우 흐름: `build → validate(구조) → style_check(문체) → spell_check(맞춤법)`
- 스크립트 요약표, Critical Rules(8·9번) 갱신

---

## 6. 신규 파일 전문

### 6.1 `scripts/spell_check.py`

```python
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
```

### 6.2 `references/korean-spelling.md`

```markdown
# 한글 맞춤법·띄어쓰기 교정 지침

보고서 본문·표 텍스트를 작성한 뒤 이 지침으로 교열한다. 자동 검사기
(`scripts/spell_check.py`)는 아래 목록 중 **오탐이 적은 고빈도 오류만**
확정적으로 잡는다. 문맥이 필요한 항목은 검사기가 놓치므로, 생성 주체(Claude)가
아래 규칙에 따라 직접 한 번 더 훑어 교정한다.

## 1. 검사기가 자동으로 잡는 항목 (고빈도·저오탐)
… (되/돼, 안/않, 웬/왠, 몇일→며칠, 역활→역할, 갯수→개수, 촛점→초점,
   및/수/것 띄어쓰기 등 표로 정리)

## 2. 검사기가 놓치는 항목 — 문맥 보고 직접 교정
- 되/돼 : '되어'를 넣어 말이 되면 '돼'
- 안/않 : 안=부사(아니), 않=어미(아니하-), '~지 않다' 자리에만 '않'
- 로서/로써 : 로서=자격·지위, 로써=수단·도구
- 든지/던지 : 든지=선택, 던지=과거 회상
- 부사 -이/-히 : 틈틈이·일일이·번번이 / 꼼꼼히·각별히·충분히
- 개조식 종결과의 관계 : 교정해도 명사형 종결 유지

## 3. 표기 통일(보고서 관례)
- 날짜 표 열 '‘YY.MM.DD', 숫자+단위 붙여 씀, '및'·'등' 남용 금지

## 4. 교정 절차
1. 작성 완료 → 2. spell_check.py → 3. 2절 문맥 교정
   → 4. style_check.py → 5. 재빌드
```
> 전체 내용은 저장소 `references/korean-spelling.md` 참조.

---

## 7. 사용 방법

설치 후 Claude에게 보고서 생성을 요청하면 `hwpx` 스킬이 자동 호출된다.

```
예) "○○ 사업 추진현황 보고서 만들어줘"
    ".hwpx로 2026년 상반기 점검 결과 작성"
```

생성 뒤 검증 흐름:
```bash
python3 scripts/validate.py    output/report.hwpx   # 구조
python3 scripts/style_check.py output/report.hwpx   # 개조식 문체
python3 scripts/spell_check.py output/report.hwpx   # 맞춤법·띄어쓰기
```
