#!/usr/bin/env python3
"""국내(대한민국) 기준 산업재해 보고 판정기.

사고 정보를 입력하면 다음을 판정한다.
  - 산업안전보건법상 '중대재해' 해당 여부(시행규칙 제3조)
  - 중대재해처벌법상 '중대산업재해' 해당 여부(제2조)
  - 일반 산업재해 보고 대상 여부(산안법 제57조, 시행규칙 제73조)
그리고 해당 시 보고 기한·방법을 안내한다. 표준 라이브러리만 사용한다.

주의: 판정 기준은 통용 기준을 정리한 것으로, 실제 보고 전 최신 법령(law.go.kr)과
관할 지방고용노동관서 안내로 반드시 검증해야 한다. 특히 중대재해처벌법의 상시근로자
5명 미만 적용제외 등 세부 요건은 법령 확인이 필요하다.

사용 예:
    python3 incident_kr.py --deaths 1
    python3 incident_kr.py --injured-3m 2          # 3개월 이상 요양 부상 2명(동시)
    python3 incident_kr.py --injured-total 10      # 부상/직업성질병 동시 10명
    python3 incident_kr.py --hospital-6m 2          # (중처법) 6개월 이상 치료 2명
    python3 incident_kr.py --occdisease-1y 3        # (중처법) 급성중독 등 1년내 3명
    python3 incident_kr.py --workloss-days 5        # 휴업 5일 → 일반 보고 대상
"""
from __future__ import annotations

import argparse


def classify(a) -> dict:
    result = {"중대재해_산안법": [], "중대산업재해_중처법": [], "일반보고": []}

    # 1) 산업안전보건법 시행규칙 제3조 — 중대재해
    if a.deaths >= 1:
        result["중대재해_산안법"].append("사망자 1명 이상")
    if a.injured_3m >= 2:
        result["중대재해_산안법"].append("3개월 이상 요양 부상자 동시 2명 이상")
    if a.injured_total >= 10:
        result["중대재해_산안법"].append("부상자·직업성질병자 동시 10명 이상")

    # 2) 중대재해처벌법 제2조 — 중대산업재해
    if a.deaths >= 1:
        result["중대산업재해_중처법"].append("사망자 1명 이상")
    if a.hospital_6m >= 2:
        result["중대산업재해_중처법"].append("동일 사고로 6개월 이상 치료 부상자 2명 이상")
    if a.occdisease_1y >= 3:
        result["중대산업재해_중처법"].append("동일 유해요인 직업성 질병자 1년 이내 3명 이상")

    # 3) 일반 산업재해 보고(산안법 제57조, 시행규칙 제73조)
    if a.deaths >= 1:
        result["일반보고"].append("사망 발생")
    if a.workloss_days >= 3:
        result["일반보고"].append(f"3일 이상 휴업 재해(입력 {a.workloss_days}일)")

    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="국내 기준 산업재해/중대재해 보고 판정")
    ap.add_argument("--deaths", type=int, default=0, help="사망자 수")
    ap.add_argument("--injured-3m", type=int, default=0, help="(산안법) 3개월 이상 요양 부상자(동시)")
    ap.add_argument("--injured-total", type=int, default=0, help="(산안법) 부상자+직업성질병자 동시 인원")
    ap.add_argument("--hospital-6m", type=int, default=0, help="(중처법) 6개월 이상 치료 부상자(동일 사고)")
    ap.add_argument("--occdisease-1y", type=int, default=0, help="(중처법) 급성중독 등 직업성질병자(1년 이내)")
    ap.add_argument("--workloss-days", type=int, default=0, help="휴업일수(최대)")
    ap.add_argument("--workers", type=int, default=-1, help="상시근로자 수(중처법 적용 참고, 미입력 시 -1)")
    args = ap.parse_args()

    r = classify(args)
    print("=" * 60)
    print(" 국내 기준 산업재해 보고 판정 결과")
    print("=" * 60)

    is_serious = bool(r["중대재해_산안법"])
    is_cep = bool(r["중대산업재해_중처법"])
    is_general = bool(r["일반보고"])

    print(f"\n[1] 산업안전보건법상 '중대재해' 해당: {'예 ✅' if is_serious else '아니오'}")
    for x in r["중대재해_산안법"]:
        print(f"    - {x}")
    if is_serious:
        print("    → 보고: 관할 지방고용노동관서에 '지체 없이' 전화·팩스 등으로 보고")
        print("      (발생개요·피해상황, 조치 및 전망 등)")

    print(f"\n[2] 중대재해처벌법상 '중대산업재해' 해당: {'예 ✅' if is_cep else '아니오'}")
    for x in r["중대산업재해_중처법"]:
        print(f"    - {x}")
    if is_cep:
        print("    → 경영책임자 안전보건확보의무 및 수사·처벌 대상 가능. 법률 검토 필요.")
        if 0 <= args.workers < 5:
            print(f"    ⚠️ 상시근로자 {args.workers}명(5명 미만) → 적용 제외 가능(세부 요건 법령 확인).")

    print(f"\n[3] 일반 산업재해 보고 대상(산안법 제57조): {'예 ✅' if is_general else '아니오/추가확인'}")
    for x in r["일반보고"]:
        print(f"    - {x}")
    if is_general:
        print("    → 보고: 재해발생일부터 '1개월 이내' 산업재해조사표 제출(관할 지방고용노동관서)")

    if not (is_serious or is_cep or is_general):
        print("\n입력 기준으로는 위 3개 보고 요건에 해당하지 않으나,")
        print("경미재해도 기록·관리 의무가 있을 수 있으니 최신 법령·사내 절차를 확인하세요.")

    print("\n" + "-" * 60)
    print("※ 본 판정은 참고용입니다. 실제 보고 전 국가법령정보센터(law.go.kr)와")
    print("  관할 지방고용노동관서 안내로 반드시 검증하세요. 법령은 개정될 수 있습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
