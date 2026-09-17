"""Real package invariants for the opt-in detailed report layout."""

import sys
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path

from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import one_shot
from build_contract import SpecError
from package_inspection import NS, inspect_package

MARKDOWN = (
    "# 단어 경계가 중요한 TECHNICAL 약어 제목\n\n## 검토 절차\n\n설명 문단이다.\n\n> 인용은 고정폭 코드가 아니다.\n\n- 목록 들여쓰기 유지\n\n도식 1. 검토 기준\n\n본문에 기준을 설명한다.\n\n```python\nif ready:\n    run()\n\n    done()\n```\n\n---\n\n## 전체 로그\n\n```\n"
    + "\n".join(f"row {i}" for i in range(25))
    + "\n```\n\n[1] 참고 문서\n\nhttps://example.org/a-long-path-to-the-reference\n"
)


def spec():
    return {
        "version": 2,
        "kind": "markdown",
        "template": "report",
        "output": "report.hwpx",
        "markdown": MARKDOWN,
        "style": {"layout": "technical-report"},
        "quality": {"hancom": "off", "writing": "off"},
    }


class TechnicalReportTests(unittest.TestCase):
    def test_opt_in_rejects_wrong_type_template_or_orphan_code_font(self):
        for change in [
            {"kind": "brief-report", "template": None},
            {"template": "base"},
            {"style": {"layout": "unknown"}},
            {"style": {"code_font": "Consolas"}},
        ]:
            value = spec()
            value.update(change)
            if value.get("template") is None:
                value.pop("template")
            with self.subTest(change=change), self.assertRaises(SpecError):
                one_shot.validate_spec(value)

    def test_roles_text_pagebreaks_and_code_pagination(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            value = spec()
            original = deepcopy(value)
            result = one_shot.build(value, spec_dir=folder)
            self.assertTrue(result["published"])
            self.assertEqual(value, original)
            self.assertEqual(result["profile"]["body_size"], 11)
            path = folder / "report.hwpx"
            self.assertFalse(inspect_package(path)["errors"])
            with zipfile.ZipFile(path) as z:
                header = E.fromstring(z.read("Contents/header.xml"))
                section = E.fromstring(z.read("Contents/section0.xml"))
            paras = {p.get("id"): p for p in header.findall(".//hh:paraPr", NS)}
            chars = {p.get("id"): p for p in header.findall(".//hh:charPr", NS)}
            fonts = {
                f.get("id"): f.get("face")
                for f in header.xpath(
                    './/hh:fontface[@lang="LATIN"]/hh:font', namespaces=NS
                )
            }
            ps = section.findall("hp:p", NS)
            by_text = {
                "".join(p.xpath("./hp:run/hp:t/text()", namespaces=NS)): p for p in ps
            }

            def setting(p, name):
                return paras[p.get("paraPrIDRef")].find("hh:breakSetting", NS).get(name)

            def font_for(p):
                cp = chars[p.find("hp:run", NS).get("charPrIDRef")]
                return fonts[cp.find("hh:fontRef", NS).get("latin")]

            self.assertEqual(
                setting(by_text[MARKDOWN.splitlines()[0][2:]], "breakLatinWord"),
                "KEEP_WORD",
            )
            self.assertEqual(font_for(by_text["    run()"]), "Consolas")
            self.assertNotEqual(
                font_for(by_text["인용은 고정폭 코드가 아니다."]), "Consolas"
            )
            list_p = next(
                p
                for value, p in by_text.items()
                if value.endswith("목록 들여쓰기 유지")
            )
            self.assertEqual(list_p.get("paraPrIDRef"), "24")
            self.assertEqual(setting(by_text["if ready:"], "keepWithNext"), "1")
            self.assertEqual(setting(by_text["    done()"], "keepWithNext"), "0")
            self.assertEqual(setting(by_text["row 10"], "keepWithNext"), "0")
            self.assertEqual(setting(by_text["도식 1. 검토 기준"], "keepWithNext"), "1")
            self.assertTrue(section.xpath('./hp:p[@pageBreak="1"]', namespaces=NS))
            self.assertTrue(result["checks"]["content"]["ok"])

    def test_same_spec_bytes_and_custom_tokens(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            value = spec()
            value["style"].update(
                body_size=12, font="맑은 고딕", code_font="Courier New", accent="336699"
            )
            first = one_shot.build(value, spec_dir=folder)
            initial = (folder / "report.hwpx").read_bytes()
            second = one_shot.build(value, spec_dir=folder)
            self.assertTrue(first["published"] and second["published"])
            self.assertEqual(initial, (folder / "report.hwpx").read_bytes())
            with zipfile.ZipFile(folder / "report.hwpx") as z:
                header = E.fromstring(z.read("Contents/header.xml"))
            self.assertTrue(
                header.xpath('.//hh:font[@face="Courier New"]', namespaces=NS)
            )
            self.assertEqual(
                header.xpath('.//hh:charPr[@id="0"]/@height', namespaces=NS), ["1200"]
            )


if __name__ == "__main__":
    unittest.main()
