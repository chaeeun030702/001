"""Behavioral regressions for the audit's false-success cases."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import contextlib
import io
import zipfile
from lxml import etree
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import one_shot
import munche_lint
from quality_gate import run_quality_gate
from package_inspection import NS


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def spec(self, kind="markdown"):
        spec = copy.deepcopy(one_shot.EXAMPLES[kind])
        spec["output"] = str(self.base / (kind + ".hwpx"))
        spec["quality"]["hancom"] = "off"
        return spec

    def build(self, spec):
        return one_shot.build(spec, spec_dir=self.base)

    def mutate(self, path, callback):
        with zipfile.ZipFile(path) as z:
            entries = [(i, z.read(i.filename)) for i in z.infolist()]
        with zipfile.ZipFile(path, "w") as z:
            for i, data in entries:
                z.writestr(i, callback(i.filename, data))

    def test_nested_types_and_typos(self):
        for key, value in [
            ("draft", "false"),
            ("draft", None),
            ("version", True),
            ("quality", {"fail_on_warnings": "false"}),
        ]:
            with self.subTest(key=key, value=value):
                s = self.spec()
                s[key] = value
                with self.assertRaises(one_shot.SpecError):
                    self.build(s)
        for key, value in [
            ("붙잉", ["계획서"]),
            ("body", [None]),
            ("body", []),
            ("결재", [{"성멍": "테스트"}]),
        ]:
            with self.subTest(key=key):
                s = self.spec("official-letter")
                s["document"][key] = value
                with self.assertRaises(one_shot.SpecError):
                    self.build(s)

    def test_title_only_and_missing_image_fail_before_publish(self):
        for md in ["# 운영계획", "# 운영계획\n\n![필수 그림](missing.png)"]:
            s = self.spec()
            s["markdown"] = md
            with self.assertRaises(one_shot.SpecError):
                self.build(s)
            self.assertFalse(Path(s["output"]).exists())

    def test_cli_path_collision_preserves_all_inputs(self):
        for mode in ("output", "spec", "source", "override"):
            with self.subTest(mode=mode):
                s = self.spec()
                source = self.base / "source.md"
                source.write_text(s.pop("markdown"), encoding="utf-8")
                s["source"] = str(source)
                out = Path(s["output"])
                out.write_bytes(b"previous-output")
                specpath = self.base / "spec.json"
                specpath.write_text(json.dumps(s), encoding="utf-8")
                report = {
                    "output": out,
                    "spec": specpath,
                    "source": source,
                    "override": self.base / "override.hwpx",
                }[mode]
                report.write_bytes(
                    report.read_bytes() if report.exists() else b"override-original"
                )
                before = {p: p.read_bytes() for p in (source, out, specpath, report)}
                cmd = [
                    sys.executable,
                    str(ROOT / "scripts/one_shot.py"),
                    str(specpath),
                    "--report",
                    str(report),
                ]
                if mode == "override":
                    cmd += ["--output", str(report)]
                r = subprocess.run(
                    cmd, capture_output=True, text=True, encoding="utf-8"
                )
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertFalse(json.loads(r.stdout)["published"])
                for p, data in before.items():
                    self.assertEqual(p.read_bytes(), data)

    def test_cli_json_uses_utf8_even_with_legacy_windows_stdout(self):
        s = self.spec()
        s["미지원–필드🙂"] = True
        specpath = self.base / "unicode.json"
        specpath.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
        run = subprocess.run(
            [sys.executable, str(ROOT / "scripts/one_shot.py"), str(specpath)],
            capture_output=True,
            env={**os.environ, "PYTHONIOENCODING": "cp949", "PYTHONUTF8": "0"},
        )
        self.assertEqual(run.returncode, 2, run.stderr)
        report = json.loads(run.stdout.decode("utf-8"))
        self.assertFalse(report["published"])
        self.assertIn("미지원–필드🙂", " ".join(report["errors"]))
        self.assertNotIn(b"UnicodeEncodeError", run.stderr)

    def test_windows_replace_retry_is_bounded_and_preserves_destination(self):
        from atomic_io import replace_file

        source, target = self.base / "new.bin", self.base / "old.bin"
        source.write_bytes(b"new")
        target.write_bytes(b"old")
        locked = PermissionError("Windows access denied")
        locked.winerror = 5
        real_replace = os.replace
        calls = []

        def temporarily_locked(src, dst):
            calls.append(1)
            if len(calls) < 3:
                raise locked
            return real_replace(src, dst)

        with (
            patch("atomic_io.os.replace", side_effect=temporarily_locked),
            patch("atomic_io.time.sleep"),
        ):
            self.assertEqual(replace_file(source, target), 2)
        self.assertEqual(target.read_bytes(), b"new")
        source.write_bytes(b"next")
        with (
            patch("atomic_io.os.replace", side_effect=locked) as replace,
            patch("atomic_io.time.sleep") as sleep,
        ):
            with self.assertRaises(PermissionError):
                replace_file(source, target)
            self.assertEqual(replace.call_count, 5)
            self.assertEqual(sleep.call_count, 4)
        self.assertEqual(target.read_bytes(), b"new")
        self.assertEqual(source.read_bytes(), b"next")

    def test_hardlink_collision(self):
        s = self.spec()
        source = self.base / "input.hwpx"
        source.write_text(s.pop("markdown"), encoding="utf-8")
        s["source"] = str(source)
        os.link(source, s["output"])
        with self.assertRaises(one_shot.SpecError):
            self.build(s)

    def test_bold_title_draft_and_dates(self):
        for kind in sorted(one_shot.KINDS):
            s = self.spec(kind)
            s["metadata_date"] = "2031-12-24"
            s["draft"] = True
            if kind != "official-letter":
                s["markdown"] = "# **검증 제목**\n\n- 실행 계획 수립\n"
            report = self.build(s)
            self.assertTrue(report["ok"], report["errors"])
            self.assertEqual(report["status"], "DRAFT")
            self.assertTrue(report["draft"])
            with zipfile.ZipFile(s["output"]) as z:
                self.assertIn("2031-12-24", z.read("Contents/content.hpf").decode())
                self.assertIn("[초안]", z.read("Contents/section0.xml").decode())
            self.assertEqual(report["checks"]["visual_review"]["status"], "not_run")
            self.assertIsNone(report["checks"]["hancom"]["ok"])

    def test_warning_policy_and_pagebreak_lint(self):
        self.assertFalse(
            munche_lint.lint("# 제목\n---\n- 업무를 수행한다.")["summary"]["ok"]
        )
        s = self.spec("plan-report")
        s["markdown"] = "# 제목\n\n- " + "긴 항목 내용 " * 20
        s["quality"]["fail_on_warnings"] = True
        report = self.build(s)
        self.assertFalse(report["published"])
        self.assertTrue(any("ITEM_LONG" in w for w in report["warnings"]))

    def test_actual_images_and_source_relative_paths(self):
        folder = self.base / "nested"
        folder.mkdir()
        im = folder / "asset.png"
        Image.new("RGB", (30, 20), "navy").save(im)
        source = folder / "in.md"
        source.write_text(
            "# 그림 보고서\n\n![필수 그림](asset.png)\n\n- 설명 내용\n",
            encoding="utf-8",
        )
        for kind in ("markdown", "brief-report", "plan-report"):
            s = self.spec(kind)
            s.pop("markdown")
            s["source"] = str(source)
            report = self.build(s)
            self.assertTrue(report["ok"], report["errors"])
            with zipfile.ZipFile(s["output"]) as z:
                self.assertIn(
                    hashlib.sha256(im.read_bytes()).digest(),
                    [
                        hashlib.sha256(z.read(n)).digest()
                        for n in z.namelist()
                        if n.startswith("BinData/")
                    ],
                )

    def test_invalid_refs_and_tiny_cells_fail(self):
        s = self.spec("brief-report")
        self.assertTrue(self.build(s)["ok"])
        path = Path(s["output"])

        def bad_cells(name, data):
            if name == "Contents/section0.xml":
                root = etree.fromstring(data)
                for cell in root.findall(".//hp:cellSz", NS):
                    cell.set("width", "1")
                    cell.set("height", "1")
                return etree.tostring(root)
            return data

        self.mutate(path, bad_cells)
        report = run_quality_gate(path, hancom="off")
        self.assertFalse(report["ok"])
        self.assertGreater(report["checks"]["layout"]["text_cells"], 0)
        s = self.spec()
        self.assertTrue(self.build(s)["ok"])
        path = Path(s["output"])
        self.mutate(
            path,
            lambda n, d: (
                d.replace(b'charPrIDRef="0"', b'charPrIDRef="999999"')
                if n.startswith("Contents/section")
                else d
            ),
        )
        report = run_quality_gate(path, hancom="off")
        self.assertFalse(report["ok"])
        self.assertFalse(report["checks"]["references"]["ok"])

    def test_absent_approval_and_contact_fields_leave_no_scaffolding(self):
        s = self.spec("brief-report")
        s["markdown"] = "# 검증 보고서\n\n- 실행 계획 수립\n"
        report = self.build(s)
        self.assertTrue(report["ok"], report)
        with zipfile.ZipFile(s["output"]) as z:
            root = etree.fromstring(z.read("Contents/section0.xml"))
        self.assertFalse(root.find("hp:p", NS).findall(".//hp:tbl", NS))
        self.assertEqual(len(root.findall(".//hp:tbl", NS)), 1)  # title design remains
        s = self.spec("official-letter")
        self.assertTrue(self.build(s)["ok"])
        with zipfile.ZipFile(s["output"]) as z:
            root = etree.fromstring(z.read("Contents/section0.xml"))
        text = "".join(root.itertext())
        for label in ("전화번호", "팩스번호", "시행  ", "협조자"):
            self.assertNotIn(label, text)

    def test_accent_profile_preserves_white_chapter_numbers(self):
        s = self.spec("plan-report")
        s["version"] = 2
        s["profile"] = "public"
        s["markdown"] = "# 계획서\n\n## 운영 개요\n\n- 실행 계획 수립\n"
        self.assertTrue(self.build(s)["ok"])
        with zipfile.ZipFile(s["output"]) as z:
            header = etree.fromstring(z.read("Contents/header.xml"))
            section = etree.fromstring(z.read("Contents/section0.xml"))
        white_ids = {
            cp.get("id")
            for cp in header.findall(".//hh:charPr", NS)
            if cp.get("textColor", "").upper() == "#FFFFFF"
        }
        self.assertTrue(white_ids)
        self.assertTrue(
            any(
                run.get("charPrIDRef") in white_ids and "".join(run.itertext()).strip()
                for run in section.findall(".//hp:run", NS)
            )
        )

    def test_single_glyph_does_not_invent_a_second_line(self):
        from package_inspection import estimated_lines

        self.assertEqual(estimated_lines([2000], 1500), 1)
        self.assertEqual(estimated_lines([1000] * 5, 2100), 3)
        s = self.spec("plan-report")
        s["version"] = 2
        s["markdown"] = "# 계획서\n\n## 운영 개요\n\n- 실행 계획 수립\n"
        s["quality"]["repair_layout"] = True
        report = self.build(s)
        self.assertTrue(report["ok"])
        self.assertFalse(report["repairs"])

    def test_markdown_heading_keeps_following_body_without_changing_body_style(self):
        s = self.spec()
        s["markdown"] = "# 제목\n\n## 후속 절\n\n본문 내용\n"
        report = self.build(s)
        self.assertTrue(report["ok"], report)
        with zipfile.ZipFile(s["output"]) as z:
            header = etree.fromstring(z.read("Contents/header.xml"))
            section = etree.fromstring(z.read("Contents/section0.xml"))
        properties = {p.get("id"): p for p in header.findall(".//hh:paraPr", NS)}
        for paragraph in section.findall("hp:p", NS):
            text = "".join(
                paragraph.xpath("./hp:run/hp:t/text()", namespaces=NS)
            ).strip()
            if text in ("후속 절", "본문 내용"):
                setting = properties[paragraph.get("paraPrIDRef")].find(
                    "hh:breakSetting", NS
                )
                self.assertEqual(
                    setting.get("keepWithNext"), "1" if text == "후속 절" else "0"
                )

    def test_partial_report_failure_is_honest(self):
        s = self.spec()
        specpath = self.base / "input.json"
        specpath.write_text(json.dumps(s), encoding="utf-8")
        output = io.StringIO()
        with (
            patch.object(
                sys,
                "argv",
                [
                    "one_shot",
                    str(specpath),
                    "--report",
                    str(self.base / "quality.json"),
                ],
            ),
            patch.object(
                one_shot,
                "save_report",
                side_effect=OSError("simulated report write failure"),
            ),
            contextlib.redirect_stdout(output),
        ):
            code = one_shot.main()
        report = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "PARTIAL")
        self.assertTrue(report["published"])
        self.assertFalse(report["report_saved"])
        self.assertTrue(zipfile.is_zipfile(s["output"]))

    def test_later_section_and_font_refs(self):
        s = self.spec()
        self.assertTrue(self.build(s)["ok"])
        path = Path(s["output"])
        with zipfile.ZipFile(path, "a") as z:
            root = etree.fromstring(z.read("Contents/section0.xml"))
            root.find(".//hp:run", NS).set("charPrIDRef", "999999")
            z.writestr("Contents/section1.xml", etree.tostring(root))
        report = run_quality_gate(path, hancom="off")
        self.assertFalse(report["ok"])
        self.assertEqual(report["checks"]["references"]["sections"], 2)

    def test_repair_preserves_content_and_updates_whole_row(self):
        from layout_repair import repair_layout
        from package_inspection import inspect_package

        s = self.spec()
        s["markdown"] = (
            "# 표 검증\n\n| 항목 | 설명 |\n| --- | --- |\n| 긴 항목 | "
            + ("긴 설명 내용 " * 25)
            + " |\n"
        )
        self.assertTrue(self.build(s)["ok"])
        path = Path(s["output"])

        def short(name, data):
            if name == "Contents/section0.xml":
                root = etree.fromstring(data)
                for e in root.findall(".//hp:cellSz", NS):
                    e.set("height", "1200")
                return etree.tostring(root)
            return data

        self.mutate(path, short)
        before = inspect_package(path)
        repairs = repair_layout(path)
        after = inspect_package(path)
        self.assertTrue(repairs)
        self.assertLessEqual(len(repairs), 2)
        self.assertEqual(before["paragraphs"], after["paragraphs"])
        with zipfile.ZipFile(path) as z:
            root = etree.fromstring(z.read("Contents/section0.xml"))
        for table in root.findall(".//hp:tbl", NS):
            heights = []
            for row in table.findall("hp:tr", NS):
                values = {
                    int(c.find("hp:cellSz", NS).get("height"))
                    for c in row.findall("hp:tc", NS)
                }
                self.assertEqual(len(values), 1)
                heights.append(values.pop())
            self.assertEqual(int(table.find("hp:sz", NS).get("height")), sum(heights))


if __name__ == "__main__":
    unittest.main()
