#!/usr/bin/env python3
"""Regression tests for the one-shot generation and release contract."""

import hashlib
import json
import sys
import tempfile
import zipfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import one_shot  # noqa: E402


PASS = FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name} {detail}")


def production_example(kind, output):
    spec = deepcopy(one_shot.EXAMPLES[kind])
    spec["output"] = str(output)
    spec["quality"] = {"hancom": "off", "reject_placeholders": True}
    return spec


print("[계약·스키마]")
schema = json.loads(one_shot.SCHEMA_PATH.read_text(encoding="utf-8"))
check("지원 스키마 버전", schema["properties"]["version"]["enum"] == [1, 2])
check("지원 문서 유형 고정", set(schema["properties"]["kind"]["enum"]) == one_shot.KINDS)
typo = deepcopy(one_shot.EXAMPLES["brief-report"])
typo["ouptut"] = typo.pop("output")
try:
    one_shot.validate_spec(typo)
    typo_rejected = False
except one_shot.SpecError:
    typo_rejected = True
check("오탈자 필드는 묵인하지 않음", typo_rejected)

with tempfile.TemporaryDirectory() as td:
    temp = Path(td)

    print("[문서 유형별 원샷 생성]")
    reports = {}
    for kind in sorted(one_shot.KINDS):
        out = temp / f"{kind}.hwpx"
        reports[kind] = one_shot.build(production_example(kind, out), spec_dir=temp)
        report = reports[kind]
        check(f"{kind}: 품질 게이트 통과", report["ok"], str(report.get("errors")))
        check(f"{kind}: 통과 후에만 공개", report["published"] and out.is_file())
        check(f"{kind}: 공개 경로만 리포트", report["file"] == str(out.resolve()))
        with zipfile.ZipFile(out) as zf:
            check(f"{kind}: HWPX 필수 파트", {
                "mimetype", "Contents/content.hpf", "Contents/header.xml", "Contents/section0.xml"
            }.issubset(zf.namelist()))

    print("[결정론]")
    a = temp / "same-a.hwpx"
    b = temp / "same-b.hwpx"
    one_shot.build(production_example("official-letter", a), spec_dir=temp)
    one_shot.build(production_example("official-letter", b), spec_dir=temp)
    check(
        "같은 명세 → 같은 최종 바이트",
        hashlib.sha256(a.read_bytes()).digest() == hashlib.sha256(b.read_bytes()).digest(),
    )

    print("[저품질 차단·원자적 공개]")
    blocked = temp / "blocked.hwpx"
    blocked.write_bytes(b"existing-user-file")
    bad = production_example("official-letter", blocked)
    bad["document"]["기관명"] = "○○기관"
    try:
        one_shot.build(bad, spec_dir=temp)
        rejected = False
    except one_shot.SpecError:
        rejected = True
    check("미해결 플레이스홀더 차단", rejected)
    check("사전검사 실패 시 기존 파일 보존", blocked.read_bytes() == b"existing-user-file")

    bad_lint = production_example("official-letter", temp / "bad-lint.hwpx")
    bad_lint["document"]["body"] = ["행사는 오후 3시에 시작합니다."]
    try:
        one_shot.build(bad_lint, spec_dir=temp)
        lint_rejected = False
    except one_shot.SpecError:
        lint_rejected = True
    check("공문 표기 오류 생성 전 차단", lint_rejected)

    bad_required = production_example("brief-report", temp / "missing.hwpx")
    bad_required["quality"]["required_text"] = ["본문에 절대로 없는 문구"]
    missing_report = one_shot.build(bad_required, spec_dir=temp)
    check("필수 문구 누락 시 품질 게이트 실패", not missing_report["ok"])
    check("품질 게이트 실패 산출물 미공개", not (temp / "missing.hwpx").exists())

    source = temp / "source.md"
    source.write_text("# ○○기관 운영계획\n## 개요\n- 내용\n", encoding="utf-8")
    source_spec = {
        "version": 1,
        "kind": "plan-report",
        "output": str(temp / "source.hwpx"),
        "source": source.name,
        "quality": {"hancom": "off", "reject_placeholders": True},
    }
    try:
        one_shot.build(source_spec, spec_dir=temp)
        source_rejected = False
    except one_shot.SpecError:
        source_rejected = True
    check("source 입력도 동일한 플레이스홀더 검사", source_rejected)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
