"""Fixed v1 workload; Hancom/render latency is excluded and reported separately."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import statistics
import sys
import tempfile
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--runs", type=int, default=10)
    args = ap.parse_args()
    sys.path.insert(0, str(args.root / "scripts"))
    import one_shot

    report = {
        "root": str(args.root),
        "runs": args.runs,
        "hancom": "off",
        "visual_review": "not_run",
        "workloads": {},
    }
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        for kind in sorted(one_shot.KINDS):
            times = []
            hashes = []
            failures = []
            for i in range(args.runs + 1):
                spec = copy.deepcopy(one_shot.EXAMPLES[kind])
                spec["quality"]["hancom"] = "off"
                spec["output"] = str(base / f"{kind}-{i}.hwpx")
                start = time.perf_counter()
                result = one_shot.build(spec, spec_dir=base)
                elapsed = (time.perf_counter() - start) * 1000
                if not result["ok"]:
                    failures.append(result)
                    continue
                if i:
                    times.append(elapsed)
                    hashes.append(
                        hashlib.sha256(Path(spec["output"]).read_bytes()).hexdigest()
                    )
            report["workloads"][kind] = {
                "median_ms": statistics.median(times) if times else None,
                "p90_ms": sorted(times)[max(0, int(len(times) * 0.9) - 1)]
                if times
                else None,
                "samples_ms": times,
                "stable_bytes": len(set(hashes)) == 1,
                "failed_runs": len(failures),
                "failures": failures,
            }
            print(
                kind, report["workloads"][kind]["median_ms"], len(failures), flush=True
            )
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
