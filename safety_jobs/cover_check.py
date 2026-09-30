# /// script
# requires-python = ">=3.10"
# ///
"""자기소개서 초안 문맥 재검토(작성 후 필수).

초안 md(drafts/*.md)의 문항 답변(소제목 포함)만 대상으로 아래를 검사한다.
기업 분석·머리말은 제출하지 않는 참고 영역이라 검사하지 않는다.

  [오류] 타사 이름·브랜드·슬로건 — 지원 회사가 아닌 건설사/대기업 계열/주거 브랜드/다른 자소서에서 온 문구
  [오류] '수료'(수료증 제외) · 논문 수상 표현 · 자격 '취득/보유' 표현 · '연휴 당직' 옛 표현 · ILO 한글 미병기
  [오류] 중국어 병기 검증 수치(232곳·227곳) · '외국어'(→ 다국어) · '전기안전 데이터베이스' 단독 표기(→ 전기안전과 건설안전 분야)
  [오류] 글자수 한도 초과 / [경고] 한도의 80% 미만 또는 98% 초과
  [오류] 확정 문안(아카이브 01_guide.md 의 '### 확정 문안' 블록) — (아버지·진로 변경) 필수. 졸업연구는
         요약(졸업연구) 또는 긴 서술(졸업연구 동기·연결) 중 하나만 — 둘 다 있으면 중복
  [오류] 논문 이야기 반복 — 졸업연구 세부 내용이 두 문항 이상에 나오거나, 고유 사실(30,896건·7.1%·78.6%·
         2022년 7월 사고·사전작업허가서·e-safety 등)이 두 문항 이상에 나옴

    python3 safety_jobs/cover_check.py drafts/2026-10-01_xxxx.md [...] --guide archive/01_guide.md [--briefing briefings/latest.json]

오류가 하나라도 있으면 종료 코드 1.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cover_brief import count, parse_draft  # noqa: E402

HERE = Path(__file__).parent
# 교육·학회·기관 이름은 타사로 보지 않는다
ALLOW = {"Google", "구글", "Microsoft", "마이크로소프트", "Anthropic", "Coursera", "ILO", "AIChE", "OSHAcademy", "CCOHS",
         "UniAthena", "Alison", "KOSHA", "한국전기공사협회", "대한전기학회", "고용노동부", "한국산업안전보건공단", "안전보건공단"}
GROUPS = ("삼성 SK 현대 HD현대 LG 롯데 포스코 POSCO 한화 GS 신세계 CJ 한진 KT 두산 LS DL 대림 HDC 효성 코오롱 KCC "
          "금호 태영 호반 부영 중흥 대우 쌍용 계룡 한신 서희 동부 코오롱 우미 반도 제일 한양 BGF 대한전선").split()
BRANDS = ("래미안 힐스테이트 디에이치 자이 푸르지오 써밋 이편한세상 e편한세상 아크로 더샵 롯데캐슬 르엘 아이파크 "
          "SK뷰 한화포레나 포레나 위브 두산위브 아테라 호반써밋 베르디움 한신더휴 중흥S클래스 어울림 하늘채 데시앙 "
          "센트레빌 스위첸 리첸시아 수자인 로제비앙").split()
# 다른 자소서(아카이브)에서 옮겨 올 수 있는 회사 고유 문구
SLOGANS = ["Your Dream, Our Space", "Global Ocean Solution Provider", "자이보이스", "H-안전지갑", "레디오션",
           "신뢰와 협력", "도전과 열정", "자율과 책임", "작업중지권 전면"]
HANGUL = "가-힣"
# 졸업연구 표지(한 문항에 3개 이상이면 '자세히 쓴 문항')와, 한 번만 써야 하는 고유 사실
THESIS = [r"30,896", r"e-safety", r"졸업연구", r"논문", r"사전작업허가서", r"7\.1%", r"78\.6%", r"2022년 7월", r"GraphRAG",
          r"검전", r"단락접지", r"다국어 위험성평가표", r"232곳", r"데이터베이스|Database", r"KOSHA GUIDE", r"정전작업"]
# 같은 경험을 여러 문항에서 되풀이하지 않도록(경고). 5S·3정은 지원동기와 입사 후 계획에서 다시 쓰는 것을 허용
TOPICS = [r"캐나다", r"복지부장|학생회", r"캠퍼스 폴리스", r"과대표", r"미국 대학|공과대학 연수", r"영어회화 강사", r"오픽", r"태권도"]
FACTS = [r"30,896", r"7\.1%", r"78\.6%", r"2022년 7월", r"232곳", r"GraphRAG", r"검전", r"e-safety", r"사전작업허가서"]


def core(name):
    n = re.sub(r"\(주\)|㈜|주식회사|\(유\)|유한회사|\s", "", name or "")
    return n


def own_tokens(company):
    c = core(company)
    toks = {c}
    base = re.sub(r"(건설|이앤씨|엔지니어링|산업|중공업|물산|전선|로지스|오션)$", "", c)
    if len(base) >= 2:
        toks.add(base)
    for g in GROUPS:
        if c.startswith(g):
            toks.add(g)
    return {t for t in toks if t}


def load_top100():
    names = []
    for line in (HERE / "construction_top100_2026.tsv").read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or "\t" not in line:
            continue
        names.append(core(line.split("\t", 1)[1]))
    return names


def candidates(briefing):
    names = set(load_top100())
    if briefing:
        try:
            for p in json.loads(Path(briefing).read_text(encoding="utf-8")).get("postings", []):
                c = core(p.get("company", ""))
                if len(c) >= 3:
                    names.add(c)
        except (OSError, ValueError):
            pass
    return names


def name_re(n):
    # 두 글자 이하 한글 그룹명(현대·삼성 등)은 뒤에 한글이 바로 붙으면(현대적, 삼성동) 제외
    if re.fullmatch(f"[{HANGUL}]{{1,2}}", n):
        return re.compile(rf"(?<![{HANGUL}]){re.escape(n)}(?=건설|그룹|계열|이앤씨|엔지니어링|물산|[^{HANGUL}]|$)")
    return re.compile(rf"(?<![{HANGUL}A-Za-z]){re.escape(n)}")


def canon_blocks(guide):
    out = {}
    if not guide:
        return out
    t = Path(guide).read_text(encoding="utf-8")
    for m in re.finditer(r"^### 확정 문안 \((.+?)\)\s*\n\s*\n> (.+)$", t, re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def check(path, names, canon):
    meta, _analysis, qs = parse_draft(Path(path).read_text(encoding="utf-8"))
    company = meta.get("company", "")
    own = own_tokens(company)
    errs, warns = [], []
    whole = "\n".join(f"{q['sub']}\n{q['answer']}" for q in qs)

    def hits(text):
        found = set()
        for n in names | set(GROUPS) | set(BRANDS):
            if n in ALLOW or any(n == o or n in o or o in n for o in own):
                continue
            if name_re(n).search(text):
                found.add(n)
        for s in SLOGANS:
            if s in text:
                found.add(s)
        return found

    for q in qs:
        text = f"{q['sub']}\n{q['answer']}"
        for n in sorted(hits(text)):
            i = text.find(n)
            errs.append(f"{q['id']}: 타사/다른 자소서 문구 '{n}' — …{text[max(0, i - 25):i + len(n) + 25]}…".replace("\n", " "))
        n, lim = count(q["answer"]), q["limit"]
        if n > lim:
            errs.append(f"{q['id']}: 글자수 초과 {n}/{lim}")
        elif n < lim * 0.8 or n > lim * 0.98:
            warns.append(f"{q['id']}: 글자수 {n}/{lim} ({n * 100 // lim}%) — 권장 80~98%")
        for pat, msg in [(r"수료(?!증)", "'수료' → '이수'"), (r"(우수상|최우수상|수상했|수상하|입상)", "논문 수상 표현(제출까지만)"),
                         (r"(산업안전기사|건설안전기사|NEBOSH|ISO\s*45001 내부심사원)[^.。]{0,15}(취득했|보유|소지)", "자격 취득·보유 표현('취득 준비 중')"),
                         (r"연휴 당직", "옛 표현 '연휴 당직'"), (r"(?<!\()ILO(?!\))", "ILO 한글 병기('국제노동기구(ILO)')"),
                         (r"232곳|227곳", "중국어 병기 검증 수치는 쓰지 않음"), (r"외국어", "'외국어' → '다국어(영어·중국어·베트남어 등)'"),
                         (r"(?<!과 )(?<!및 )전기안전 (데이터베이스|Database|DB)", "'전기안전과 건설안전 분야의 데이터베이스'로")]:
            if re.search(pat, text):
                errs.append(f"{q['id']}: {msg}")
    def has(key):
        c = canon.get(key)
        return bool(c) and re.sub(r"\s+", " ", c) in re.sub(r"\s+", " ", whole)
    if canon.get("아버지·진로 변경") and not has("아버지·진로 변경"):
        errs.append("확정 문안(아버지·진로 변경) 원문이 답변에 없음 — 줄였다면 보고에 적을 것")
    long_form = has("졸업연구 동기") or has("졸업연구 연결")
    if canon.get("졸업연구"):
        if long_form and has("졸업연구"):
            errs.append("졸업연구 중복: 요약 확정 문안(졸업연구)과 긴 서술(동기·연결)이 함께 있음 — 한 문항에서만 풀어 쓸 것")
        elif not long_form and not has("졸업연구"):
            errs.append("졸업연구 확정 문안(요약 또는 동기·연결)이 답변에 없음")
    if not re.search(r"Google|구글", whole):
        warns.append("AI 교육 기관명(Google·Microsoft·Anthropic)이 한 번도 없음")
    # 같은 논문 이야기 반복: 졸업연구 고유 사실이 두 문항 이상에 나오면 오류
    per_q = {}
    for q in qs:
        text = f"{q['sub']}\n{q['answer']}"
        per_q[q["id"]] = {m for m in THESIS if re.search(m, text)}
    heavy = [k for k, v in per_q.items() if len(v) >= 3]
    if len(heavy) > 1:
        errs.append(f"논문 이야기 반복: {', '.join(heavy)}에 졸업연구 세부 내용이 여러 번 나옴 — 한 문항에서만 자세히 쓰고 나머지는 다른 경험으로")
    for fact in FACTS:
        qids = [q["id"] for q in qs if re.search(fact, f"{q['sub']}\n{q['answer']}")]
        if len(qids) > 1:
            errs.append(f"같은 사실 반복 '{fact.replace(chr(92), '')}': {', '.join(qids)}")
    for t in TOPICS:
        qids = [q["id"] for q in qs if re.search(t, f"{q['sub']}\n{q['answer']}")]
        if len(qids) > 1:
            warns.append(f"같은 경험 반복 '{t}': {', '.join(qids)} — 한 문항에서만 쓰는 것이 좋음")
    if company and not any(o in whole for o in own):
        warns.append(f"답변에 지원 회사명('{core(company)}')이 한 번도 없음")
    return company, errs, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drafts", nargs="+")
    ap.add_argument("--guide", help="archive/01_guide.md (확정 문안)")
    ap.add_argument("--briefing", help="briefings/latest.json (업체명 목록 보강)")
    args = ap.parse_args()
    names, canon = candidates(args.briefing), canon_blocks(args.guide)
    bad = 0
    for p in args.drafts:
        company, errs, warns = check(p, names, canon)
        print(f"== {company} ({p}) — 오류 {len(errs)} · 경고 {len(warns)}")
        for x in errs:
            print("  [오류]", x)
        for x in warns:
            print("  [경고]", x)
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
