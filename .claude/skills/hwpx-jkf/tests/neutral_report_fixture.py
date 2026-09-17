"""Generate disposable test documents; never clone a retired branded layout."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_report(output: Path, *, placeholder: bool = False) -> Path:
    source = output.with_suffix(".md")
    organization = "〔기관명 입력〕" if placeholder else "검증용 기관"
    source.write_text(
        f"# 검증용 보고서\n\n{organization}\n\n"
        "## 추진 내용\n\n검증용 본문입니다.\n\n"
        "| 항목 | 내용 |\n| --- | --- |\n| 일정 | 검증용 일정 |\n",
        encoding="utf-8",
    )
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/md2hwpx.py"), str(source),
         "-o", str(output)], check=True, capture_output=True,
    )
    return output
