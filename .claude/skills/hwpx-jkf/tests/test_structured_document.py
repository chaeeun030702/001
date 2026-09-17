import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import one_shot


def example(pattern="process", kind="markdown"):
    nodes = [
        {
            "id": "diagnose",
            "title": "현황 진단",
            "text": "업무·데이터 현황 분석",
            "role": "기획부서",
        },
        {
            "id": "select",
            "title": "우선과제 선정",
            "text": "효과와 실행 가능성 검토",
            "role": "현업부서",
        },
        {
            "id": "pilot",
            "title": "시범 적용",
            "text": "검증 후 성과 공유",
            "role": "현업부서",
        },
    ]
    edges = [
        {"from": "diagnose", "to": "select", "label": "진단 결과"},
        {"from": "select", "to": "pilot", "label": "선정 과제"},
    ]
    if pattern == "hierarchy":
        edges[1]["from"] = "diagnose"
    return {
        "version": 2,
        "kind": kind,
        "output": "sample.hwpx",
        "title": "기관 AX 전략 특강 운영계획",
        "metadata_date": "2026-08-25",
        "profile": "public",
        "facts": {"date": "2026. 8. 25.", "time": "15:00∼17:30", "fee": "무료"},
        "blocks": [
            {"type": "heading", "text": "운영 개요"},
            {
                "type": "table",
                "headers": ["구분", "내용"],
                "rows": [
                    ["일시", "2026. 8. 25. 15:00∼17:30"],
                    ["참가비", "무료"],
                    ["대상", "검증용 가상기관 구성원"],
                ],
            },
            {"type": "heading", "text": "AX 실행 흐름"},
            {"type": "diagram", "pattern": pattern, "nodes": nodes, "edges": edges},
            {
                "type": "paragraph",
                "text": "특강 이후 부서별 실행 과제 발굴 및 적용 결과 공유",
            },
        ],
        "quality": {"hancom": "off"},
    }


class StructuredTests(unittest.TestCase):
    def test_patterns_and_generators(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(os.environ.get("HWPX_QA_ARTIFACTS", td))
            base.mkdir(parents=True, exist_ok=True)
            for pattern in ("process", "hierarchy", "swimlane"):
                for kind in ("markdown", "brief-report", "plan-report"):
                    with self.subTest(pattern=pattern, kind=kind):
                        spec = example(pattern, kind)
                        spec["output"] = str(base / f"{kind}-{pattern}.hwpx")
                        result = one_shot.build(spec, spec_dir=base)
                        self.assertTrue(result["ok"], result["errors"])
                        self.assertEqual(len(result["diagrams"]), 1)
                        with zipfile.ZipFile(spec["output"]) as z:
                            xml = z.read("Contents/section0.xml").decode()
                            self.assertNotIn("HWPX_DIAGRAM_", xml)
                            self.assertIn('pageBreak="NONE"', xml)
                            self.assertNotIn("<hp:pic", xml)
                        (base / f"{kind}-{pattern}.json").write_text(
                            json.dumps(result, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )

    def test_facts_unknowns_and_unsupported_graph(self):
        with tempfile.TemporaryDirectory() as td:
            s = example()
            s["facts"]["missing"] = "반드시 포함할 사실"
            with self.assertRaises(one_shot.SpecError):
                one_shot.build(s, spec_dir=Path(td))
            s = example()
            s["unknowns"] = ["장소 미정"]
            with self.assertRaises(one_shot.SpecError):
                one_shot.build(s, spec_dir=Path(td))
            s = example()
            s["blocks"][3]["edges"][0]["to"] = "pilot"
            with self.assertRaises(ValueError):
                one_shot.build(s, spec_dir=Path(td))
            s = example()
            s["blocks"][3]["nodes"][0]["title"] = "○○기관"
            with self.assertRaises(one_shot.SpecError):
                one_shot.build(s, spec_dir=Path(td))

    def test_reproducibility(self):
        with tempfile.TemporaryDirectory() as td:
            s = example()
            s["output"] = str(Path(td) / "a.hwpx")
            self.assertTrue(one_shot.build(s, spec_dir=Path(td))["ok"])
            a = Path(s["output"]).read_bytes()
            s["output"] = str(Path(td) / "b.hwpx")
            self.assertTrue(one_shot.build(s, spec_dir=Path(td))["ok"])
            self.assertEqual(a, Path(s["output"]).read_bytes())


if __name__ == "__main__":
    unittest.main()
