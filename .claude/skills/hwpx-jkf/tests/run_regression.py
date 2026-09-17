"""Run executable test files independently and retain failure evidence."""

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "python": sys.version,
        "platform": platform.platform(),
        "root": str(args.root),
        "dependencies": {},
        "tests": [],
    }
    for name in ("lxml", "jsonschema", "Pillow", "pywin32", "PyMuPDF"):
        try:
            result["dependencies"][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result["dependencies"][name] = None
    env = {**os.environ, "PYTHONUTF8": "1"}
    env.pop("HWPX_QA_ARTIFACTS", None)
    for test in sorted((args.root / "tests").glob("test_*.py")):
        start = time.perf_counter()
        try:
            run = subprocess.run(
                [sys.executable, str(test)],
                cwd=args.root,
                env=env,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )
            entry = {
                "test": test.name,
                "exit_code": run.returncode,
                "stdout": run.stdout,
                "stderr": run.stderr,
            }
        except subprocess.TimeoutExpired:
            entry = {
                "test": test.name,
                "exit_code": None,
                "stderr": "test timed out after 60 seconds",
            }
        entry["seconds"] = time.perf_counter() - start
        result["tests"].append(entry)
        print(
            f"{test.name}: {entry['exit_code']} ({entry['seconds']:.2f}s)", flush=True
        )
    result["passed"] = sum(t["exit_code"] == 0 for t in result["tests"])
    result["failed"] = len(result["tests"]) - result["passed"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{result['passed']} files passed, {result['failed']} failed", flush=True)
    return int(result["failed"] > 0)


if __name__ == "__main__":
    sys.exit(main())
