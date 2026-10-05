# /// script
# requires-python = ">=3.10"
# ///
"""저장된 답변과 당초 초안 비교 → 다음 초안 작성에 쓸 수정 사례 정리.

브리핑 페이지에서 '답변 저장'한 답변(아티팩트 db answers 컬렉션, 문서 id = 초안id_문항순번)을
drafts/*.md 의 당초 초안과 문장 단위로 비교해 edits.md 를 만든다. 매일 루틴이 새 초안을 쓰기 전에
이 파일을 읽고, 사용자가 지운 표현은 쓰지 않고 새로 쓴·고친 문장의 내용과 문체를 따른다.
결과에는 자소서 본문이 들어가므로 공개 저장소에 커밋하지 말 것(비공개 아티팩트 작업 폴더에만 둔다).

    python3 safety_jobs/cover_edits.py --answers /tmp/cl/db/answers --drafts /tmp/cl/drafts --out /tmp/cl/drafts/edits.md
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cover_brief import count, load_answers, parse_draft  # noqa: E402


def sentences(t):
    """문단·문장 단위로 자른다(다. / 요. / ? / ! 뒤)."""
    out = []
    for para in t.split("\n\n"):
        out += [s.strip() for s in re.split(r"(?<=[다요까][.?!])\s+|(?<=[?!])\s+", para) if s.strip()]
    return out


def compare(orig, new):
    """문장 목록 비교 → [(종류, 당초, 변경)] 종류: 삭제·추가·수정."""
    a, b = sentences(orig), sentences(new)
    ops = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            ops += [("삭제", s, "") for s in a[i1:i2]]
        elif tag == "insert":
            ops += [("추가", "", s) for s in b[j1:j2]]
        else:
            # 같은 위치의 문장끼리 짝지어 수정으로, 남는 것은 삭제·추가
            k = min(i2 - i1, j2 - j1)
            ops += [("수정", a[i1 + x], b[j1 + x]) for x in range(k)]
            ops += [("삭제", s, "") for s in a[i1 + k:i2]]
            ops += [("추가", "", s) for s in b[j1 + k:j2]]
    return ops


def fragments(o, n):
    """수정된 문장 안에서 바뀐 부분만 '당초'→'변경' 으로 뽑는다(어절 단위)."""
    a, b = o.split(), n.split()
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            out.append(f"'{' '.join(a[i1:i2])}'→'{' '.join(b[j1:j2])}'")
    return ", ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True, help="answers 컬렉션(JSON 목록 또는 문서별 JSON 폴더)")
    ap.add_argument("--drafts", default="drafts")
    ap.add_argument("--out", default="edits.md")
    args = ap.parse_args()

    answers = load_answers(args.answers)
    root = Path(args.drafts)
    files = {p.stem.split("_")[-1]: p for p in root.glob("*.md")}
    cases, totals = [], {"삭제": 0, "추가": 0, "수정": 0}
    for key, v in sorted(answers.items(), key=lambda kv: kv[1]["at"]):
        did, _, qi = key.rpartition("_")
        f = files.get(did)
        if not f or not qi.isdigit():
            continue
        meta, _, questions = parse_draft(f.read_text(encoding="utf-8"))
        if int(qi) >= len(questions):
            continue
        q = questions[int(qi)]
        ops = compare(q["answer"], v["text"])
        sub_changed = v["sub"] and v["sub"] != q["sub"]
        if not ops and not sub_changed:
            continue
        for t, *_ in ops:
            totals[t] += 1
        cases.append((meta, q, v, ops, sub_changed))

    lines = ["# 사용자 수정 사례 (저장한 답변 ↔ 당초 초안)", "",
             f"저장한 답변 {len(answers)}문항 중 바뀐 문항 {len(cases)}개 · 문장 삭제 {totals['삭제']} · 추가 {totals['추가']} · 수정 {totals['수정']}", "",
             "## 새 초안에 반영하는 방법",
             "- 사용자가 지운 문장·표현과 같은 유형은 새 초안에 쓰지 않는다.",
             "- 사용자가 고친 표현(수정 → 오른쪽)을 같은 뜻의 문장에서 우선 쓴다. 어휘·문장 길이·어조도 따른다.",
             "- 사용자가 새로 쓴 문장의 경험·사실은 사용자 확인 자료로 보고 맞는 문항에 쓸 수 있다. 단 그 회사에만 해당하는 회사명·사업·현장 내용은 다른 회사 초안에 옮기지 않는다.",
             "- [절대 규칙]·확정 문안 규칙과 부딪치면 그 규칙이 우선이고, 부딪친 점을 보고에 적는다.", ""]
    for meta, q, v, ops, sub_changed in cases:
        lines.append(f"## {meta.get('company', '')} · {q['id']} ({v['at'][:10]} 저장, {count(q['answer']):,}→{count(v['text']):,}자 / {q['limit']:,}자)")
        if q["question"]:
            lines.append(f"> {q['question']}")
        if sub_changed:
            lines.append(f"- 소제목 수정: [{q['sub']}] → [{v['sub']}]")
        for t, o, n in ops:
            if t == "수정":
                lines.append(f"- 수정: {o} → {n}")
                lines.append(f"  - 바뀐 부분: {fragments(o, n)}")
            else:
                lines.append(f"- {t}: {o or n}")
        lines.append("")
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"{args.out}: 바뀐 문항 {len(cases)}개 · 삭제 {totals['삭제']} · 추가 {totals['추가']} · 수정 {totals['수정']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
