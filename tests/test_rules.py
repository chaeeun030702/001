"""제외 규칙 회귀 테스트 (수집 없이 제목·업체명 판정만 본다).

실행: uv run --no-project --with pytest --with-requirements <collect.py 의존성> pytest -q tests
"""
import importlib.util
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("collect", ROOT / "safety_jobs" / "collect.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

CASES = json.loads((ROOT / "tests" / "rule_cases.json").read_text(encoding="utf-8"))["cases"]


def make(title, company):
    p = C.Posting("사람인", title, company, f"https://example.invalid/{abs(hash((title, company)))}", title)
    p.extra = {}
    return p


def gates(p):
    """제목·업체명만으로 판정되는 제외 규칙. 걸린 규칙 이름 목록을 돌려준다."""
    hit = []

    def chk(name, fn):
        f = getattr(C, fn, None) if isinstance(fn, str) else fn
        if f is None:
            return
        try:
            r = f(p) if callable(f) and not isinstance(f, re.Pattern) else f.search(f"{p.title} {p.detail_text or ''}")
        except Exception:  # 본문이 필요한 함수는 건너뛴다
            return
        if r:
            hit.append(name)

    chk("excluded_corp", "excluded_corp")
    chk("other_role", "other_role")
    chk("senior_rank", "senior_rank")
    chk("safety_main_reason", "safety_main_reason")
    for rx in ("WATCH_RE", "NON_HSE_SAFETY_RE", "OTHER_ROLE_RE", "COMPOSITE_RE"):
        r = getattr(C, rx, None)
        if isinstance(r, re.Pattern) and r.search(p.title):
            hit.append(rx)
    try:
        if C.relevant(p) is False:
            hit.append("relevant=False")
    except Exception:
        pass
    return hit


@pytest.mark.parametrize("case", CASES, ids=[f"{c['expect']}:{c['title']}@{c['company']}" for c in CASES])
def test_rule(case):
    hit = gates(make(case["title"], case["company"]))
    if case["expect"] == "exclude":
        assert hit, f"빠져야 할 공고가 남음 — 규칙: {case['rule']}"
    else:
        assert not hit, f"남아야 할 공고가 빠짐 — 걸린 규칙: {hit} (의도: {case['rule']})"
