#!/usr/bin/env python3
"""research_plan.py(연구학교 연구계획서 생성기) 테스트.

사용법: python3 tests/test_research_plan.py
"""
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import research_plan  # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


print("[reference]")
check("assets/research-school-plan-reference.hwpx 존재", research_plan.REF.exists())

have_lxml = False
try:
    import lxml  # noqa: F401
    have_lxml = True
except Exception:
    pass


def gen(**kw):
    d = tempfile.mkdtemp()
    out = Path(d) / "plan.hwpx"
    research_plan.generate(str(out), **kw)
    x = zipfile.ZipFile(out).read("Contents/section0.xml").decode(errors="ignore")
    v = c = None
    if have_lxml:
        v = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py"), str(out)],
                           capture_output=True, text=True).stdout
        c = subprocess.run([sys.executable, str(ROOT / "scripts/fill_hwpx.py"),
                            "check", str(out), "--strict"], capture_output=True, text=True).returncode
    return out, x, v, c


print("[generate -- 기본 복제 및 메타데이터 치환]")
out, x, v, c = gen(school="서울초등학교", title="디지털 맞춤형 교육과정", year="2027")
check("표지 학교명 치환", "서울초등학교" in x)
check("표지 연구주제 치환", "디지털 맞춤형 교육과정" in x)
check("표지 연도 치환", "2027" in x)

if have_lxml:
    check("validate VALID", v and "VALID" in v and "INVALID" not in v, detail=str(v)[:80])
    check("check --strict 통과", c == 0)

print(f"\n결과: {PASS} passed, {FAIL} failed")
if FAIL > 0:
    sys.exit(1)
