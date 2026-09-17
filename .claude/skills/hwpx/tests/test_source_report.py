"""Source fidelity is independent of semantic review and model provenance."""

import io
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import one_shot
from source_report import audit, fenced_blocks, main, prepare, scoped_source
from structured_document import compile_blocks

SOURCE = "Article\n\n[spec](https://example.org/spec)\n\n```python\nif ready:\n    run()\n\n    run()\n```\n\n```\nscore: 25.0%\n```\n"
NARRATIVE = "# 실험 상세 보고서\n\n## 설정과 평가\n\n설정 후 평가한다.\n\n@@CODE_01@@\n\n관찰한 값이다.\n\n@@CODE_02@@\n\nhttps://example.org/spec\n"


class SourceReportTests(unittest.TestCase):
    def cli(self, *args):
        with (
            patch.object(sys, "argv", ["source_report.py", *map(str, args)]),
            redirect_stdout(io.StringIO()),
        ):
            return main()

    def test_cli_preflight_and_collision_preserve_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            source, narrative, output = (
                folder / "article.md",
                folder / "narrative.md",
                folder / "prepared",
            )
            source.write_text(SOURCE, encoding="utf-8")
            narrative.write_text(NARRATIVE.replace("@@CODE_02@@", ""), encoding="utf-8")
            args = [
                "prepare",
                "--source",
                source,
                "--narrative",
                narrative,
                "--output-dir",
                output,
            ]
            self.assertEqual(self.cli(*args), 2)
            self.assertFalse(output.exists())
            narrative.write_text(NARRATIVE, encoding="utf-8")
            self.assertEqual(self.cli(*args), 0)
            built_spec = (output / "spec.json").read_bytes()
            self.assertEqual(self.cli(*args), 2)
            self.assertEqual((output / "spec.json").read_bytes(), built_spec)
            before = source.read_bytes()
            self.assertEqual(
                self.cli(
                    "audit",
                    "--source",
                    source,
                    "--report-markdown",
                    output / "report.md",
                    "--output",
                    source,
                ),
                2,
            )
            self.assertEqual(source.read_bytes(), before)

    def test_variable_code_count_and_exact_insertion(self):
        for source, narrative, count in [
            (SOURCE, NARRATIVE, 2),
            ("일반 원문", "# 보고서\n설명", 0),
        ]:
            with self.subTest(count=count):
                spec = prepare(source, narrative)
                markdown = compile_blocks(spec)[0]
                result = audit(source, markdown)
                self.assertTrue(result["ok"])
                self.assertEqual(result["source_code_blocks"], count)
                self.assertTrue(result["semantic_review"].startswith("not_run"))
                self.assertEqual(result["visual_review"], "not_run")

    def test_missing_duplicate_reordered_and_inline_markers_rejected(self):
        cases = [
            NARRATIVE.replace("@@CODE_02@@", ""),
            NARRATIVE.replace("@@CODE_02@@", "@@CODE_01@@"),
            NARRATIVE.replace("@@CODE_01@@", "@@CODE_03@@"),
            NARRATIVE.replace("@@CODE_01@@", "문단 @@CODE_01@@"),
            NARRATIVE.replace("@@CODE_01@@", "@@CODE_02@@").replace(
                "@@CODE_02@@\n\nhttps", "@@CODE_01@@\n\nhttps"
            ),
        ]
        for bad in cases:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                prepare(SOURCE, bad)

    def test_ambiguous_or_unclosed_fences_rejected(self):
        for text in ["```\na", "~~~~\na\n~~~~", "````\na\n````", "  ```\na\n  ```"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                fenced_blocks(text)

    def test_line_endings_and_trailing_spaces_not_code_indentation(self):
        report = compile_blocks(prepare(SOURCE, NARRATIVE))[0]
        self.assertTrue(audit(SOURCE.replace("\n", "\r\n"), report)["ok"])
        self.assertFalse(audit(SOURCE, report.replace("    run()", "run()"))["ok"])
        self.assertFalse(
            audit(SOURCE, report.replace("    run()\n\n    run()", "    run()"))["ok"]
        )
        self.assertFalse(
            audit(
                SOURCE,
                report.replace("https://example.org/spec", "https://example.org/other"),
            )["ok"]
        )

    def test_scope_is_explicit_unique_and_cannot_cut_code(self):
        source = SOURCE + "\nRelated items\n[other](https://example.org/other)\n"
        report = compile_blocks(prepare(SOURCE, NARRATIVE))[0]
        self.assertFalse(audit(source, report)["ok"])
        self.assertTrue(audit(source, report, end_before="Related items")["ok"])
        for text, marker in [("a", "missing"), ("x\nx", "x"), ("```\nx\n```", "x")]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                scoped_source(text, marker)

    def test_diagram_contract_not_fixed_to_three_diagrams(self):
        diagram = {
            "id": "DIAGRAM_01",
            "diagram": {
                "type": "diagram",
                "pattern": "process",
                "nodes": [{"id": "a", "title": "준비"}, {"id": "b", "title": "평가"}],
                "edges": [{"from": "a", "to": "b"}],
            },
        }
        spec = prepare(SOURCE, NARRATIVE + "\n@@DIAGRAM_01@@\n", [diagram])
        self.assertEqual(len(one_shot.validate_spec(spec)["diagrams"]), 1)
        with self.assertRaises(TypeError):
            prepare(SOURCE, NARRATIVE + "\n@@DIAGRAM_01@@\n", {"wrong": diagram})
        for items in [
            [],
            [diagram, diagram],
            [{"id": "DIAGRAM_01", "diagram": 4}],
        ]:
            with self.subTest(items=items), self.assertRaises(ValueError):
                prepare(SOURCE, NARRATIVE + "\n@@DIAGRAM_01@@\n", items)

    def test_audit_checks_hwpx_order_and_does_not_execute_source(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            sentinel = folder / "should-not-exist"
            source = SOURCE.replace("run()", f'open({str(sentinel)!r}, "w")')
            spec = prepare(source, NARRATIVE)
            built = one_shot.build(spec, spec_dir=folder)
            self.assertTrue(built["published"])
            path = folder / "report.hwpx"
            markdown = compile_blocks(spec)[0]
            self.assertTrue(audit(source, markdown, path)["ok"])
            self.assertFalse(sentinel.exists())
            with zipfile.ZipFile(path) as z:
                entries = [(info, z.read(info.filename)) for info in z.infolist()]
            with zipfile.ZipFile(path, "w") as z:
                for info, data in entries:
                    if info.filename == "Contents/section0.xml":
                        data = data.replace(b"score: 25.0%", b"score: 20.0%")
                    z.writestr(info, data)
            result = audit(source, markdown, path)
            self.assertFalse(result["ok"])
            self.assertEqual(
                result["missing_or_out_of_order_hwpx_code_lines"],
                [{"block": 2, "line": 1}],
            )


if __name__ == "__main__":
    unittest.main()
