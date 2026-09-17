#!/usr/bin/env python3
"""국내(대한민국) 기준 건설현장 안전점검 체크리스트 생성기.

산업안전보건기준에 관한 규칙(안전보건규칙) 등 국내 규정을 근거로 공종별 점검표를
생성한다. 표준 라이브러리만 사용한다.

주의: 조문 번호·수치는 통용 기준을 정리한 것으로, 사용 전 최신 법령(law.go.kr)과
KOSHA 지침으로 검증해야 한다.

사용 예:
    python3 checklist_kr.py --category 추락
    python3 checklist_kr.py --category 공통 --format md
    python3 checklist_kr.py --category 밀폐공간 --tbm
    python3 checklist_kr.py --list
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field


@dataclass
class Item:
    code: str
    area: str            # 점검 구역/항목
    question: str        # 점검 내용
    ref: str             # 근거(안전보건규칙 등)
    critical: bool = False  # 핵심(중대재해 직결) 여부


@dataclass
class Category:
    key: str
    title: str
    note: str
    items: list = field(default_factory=list)


CATEGORIES: dict = {
    "공통": Category("공통", "공통 안전점검", "모든 공종 공통 기본 점검", [
        Item("G01", "안전관리", "당일 작업 TBM(작업 전 안전점검회의) 실시 여부", "산안법·안전보건규칙(관리감독자 직무)"),
        Item("G02", "위험성평가", "해당 작업 위험성평가 실시·공유 여부", "산안법(위험성평가)"),
        Item("G03", "보호구", "작업조건에 맞는 보호구 지급·착용(안전모·안전화 등)", "안전보건규칙 제32조", critical=True),
        Item("G04", "정리정돈", "통로·작업발판 정리정돈 및 걸림·전도 위험 제거", "안전보건규칙(통로·정리정돈)"),
        Item("G05", "출입통제", "위험구역 출입통제·표지 설치", "안전보건규칙(출입금지)"),
        Item("G06", "안전교육", "채용시·정기·특별 안전보건교육 이수 확인", "산안법(안전보건교육)"),
        Item("G07", "기상", "강풍·강우·강설 등 악천후 시 작업중지 기준 준수", "안전보건규칙(악천후 작업중지)"),
    ]),
    "추락": Category("추락", "추락(떨어짐) 재해 예방 점검", "높이 2m 이상 작업 중점", [
        Item("F01", "개구부", "개구부·단부에 안전난간/덮개/방망 설치", "안전보건규칙(개구부 방호)", critical=True),
        Item("F02", "안전난간", "상부난간대 90~120cm, 중간난간대, 발끝막이판(10cm↑)", "안전보건규칙 제13조"),
        Item("F03", "안전대", "안전대 및 부착설비 설치·체결 상태", "안전보건규칙(안전대 부착설비)", critical=True),
        Item("F04", "작업발판", "작업발판 폭·틈새·고정 상태 적정", "안전보건규칙(작업발판)"),
        Item("F05", "방망", "추락방호망 설치·처짐·고정 상태", "안전보건규칙(추락방호망)"),
        Item("F06", "사다리", "이동식 사다리 설치각도·미끄럼방지·상단 고정", "안전보건규칙/KOSHA 지침"),
    ]),
    "비계": Category("비계", "비계 작업 안전점검", "조립·해체·변경 포함", [
        Item("B01", "조립도", "비계 조립도 작성·준수", "안전보건규칙(비계 조립도)"),
        Item("B02", "발판", "작업발판 전면 설치·고정, 틈새 최소화", "안전보건규칙(비계 작업발판)"),
        Item("B03", "난간", "안전난간·낙하물 방지망 설치", "안전보건규칙(비계 난간)", critical=True),
        Item("B04", "벽이음", "벽이음·버팀 설치 간격 준수", "안전보건규칙(비계 벽이음)"),
        Item("B05", "점검", "작업 시작 전·악천후 후 비계 점검", "안전보건규칙(비계 점검)"),
    ]),
    "굴착": Category("굴착", "굴착·흙막이 안전점검", "무너짐(붕괴) 예방", [
        Item("E01", "기울기", "지반 종류별 굴착면 기울기 기준 준수", "안전보건규칙 별표(굴착면 기울기)", critical=True),
        Item("E02", "지보공", "흙막이 지보공 조립도·계측관리", "안전보건규칙(흙막이 지보공)", critical=True),
        Item("E03", "매설물", "지하 매설물·지장물 사전 확인", "안전보건규칙(굴착 전 조사)"),
        Item("E04", "승하강", "굴착부 안전한 승하강 설비·통로", "안전보건규칙(승하강 설비)"),
        Item("E05", "지하수", "용수·지하수 배수 대책", "안전보건규칙(굴착 배수)"),
        Item("E06", "이격", "굴착부 상단 하중·자재 이격 및 방호", "안전보건규칙(굴착부 관리)"),
    ]),
    "전기": Category("전기", "전기·감전 안전점검", "감전·정전기 예방", [
        Item("P01", "누전차단기", "이동식 전동기계 누전차단기 설치·작동", "안전보건규칙(누전차단기)", critical=True),
        Item("P02", "접지", "전기기계·기구 접지 상태", "안전보건규칙(접지)"),
        Item("P03", "절연", "이동전선·꽂음접속기 피복 손상 없음", "안전보건규칙(전선 절연)"),
        Item("P04", "활선", "활선/활선근접 작업 방호·절연용구", "안전보건규칙(활선작업)", critical=True),
        Item("P05", "습윤", "습윤장소 전기사용 방호조치", "안전보건규칙(습윤장소)"),
    ]),
    "밀폐공간": Category("밀폐공간", "밀폐공간(질식) 안전점검", "질식·중독 예방", [
        Item("C01", "프로그램", "밀폐공간 작업 프로그램 수립·시행", "안전보건규칙(밀폐공간 프로그램)", critical=True),
        Item("C02", "측정", "작업 전·중 산소·유해가스 농도 측정", "안전보건규칙(밀폐공간 측정)", critical=True),
        Item("C03", "환기", "적정공기 유지 위한 환기 실시", "안전보건규칙(밀폐공간 환기)"),
        Item("C04", "감시인", "감시인 배치 및 연락체계 유지", "안전보건규칙(감시인)", critical=True),
        Item("C05", "구조", "송기마스크·구조장비 및 대피·구조 계획", "안전보건규칙(밀폐공간 대피)"),
    ]),
    "화기": Category("화기", "화기·용접 작업 안전점검", "화재·폭발 예방", [
        Item("H01", "허가", "화기작업 허가·절차 준수", "안전보건규칙/사내 화기관리"),
        Item("H02", "격리", "인화성·가연물 격리·제거", "안전보건규칙(화재예방)", critical=True),
        Item("H03", "소화", "소화기 비치 및 불티비산방지 조치", "안전보건규칙(소화설비)"),
        Item("H04", "감시자", "화재감시자 배치 및 작업 후 확인", "안전보건규칙(화재감시)"),
    ]),
    "양중": Category("양중", "양중·중장비 안전점검", "낙하·협착 예방", [
        Item("L01", "방호장치", "크레인·리프트 방호장치 작동", "안전보건규칙(양중기 방호)", critical=True),
        Item("L02", "정격하중", "정격하중 준수 및 과부하 방지", "안전보건규칙(정격하중)", critical=True),
        Item("L03", "신호", "신호수 배치 및 표준신호 사용", "안전보건규칙(신호)"),
        Item("L04", "결속", "인양물 결속·줄걸이 상태 확인", "안전보건규칙(줄걸이)"),
        Item("L05", "통제", "인양 반경 하부 출입통제", "안전보건규칙(출입금지)", critical=True),
    ]),
}


def render_text(cat: Category) -> str:
    lines = [
        f"[국내 기준] {cat.title}",
        f"근거: 산업안전보건기준에 관한 규칙 등 (사용 전 최신 법령 검증 필요)",
        f"비고: {cat.note}",
        "",
        f"{'코드':<5} {'구분':<8} 점검내용 / 근거 / 판정",
        "-" * 70,
    ]
    for it in cat.items:
        star = " ★핵심" if it.critical else ""
        lines.append(f"{it.code:<5} {it.area:<8} {it.question}{star}")
        lines.append(f"{'':<14}근거: {it.ref}  | 판정: [ 적합 / 부적합 / 해당없음 ]")
    lines += ["", "점검자: __________  서명: ______   일시: 20__.__.__  현장: __________"]
    return "\n".join(lines)


def render_md(cat: Category) -> str:
    out = [
        f"# [국내 기준] {cat.title}",
        "",
        f"- 근거: 산업안전보건기준에 관한 규칙 등 (**사용 전 최신 법령 검증 필요**)",
        f"- 비고: {cat.note}",
        "",
        "| 코드 | 구분 | 점검내용 | 근거 | 핵심 | 판정 |",
        "|---|---|---|---|:---:|---|",
    ]
    for it in cat.items:
        out.append(f"| {it.code} | {it.area} | {it.question} | {it.ref} | "
                    f"{'★' if it.critical else ''} | ☐적합 ☐부적합 ☐해당없음 |")
    out += ["", "점검자: ______ / 서명: ______ / 일시: 20__.__.__ / 현장: ______"]
    return "\n".join(out)


def render_tbm(cat: Category) -> str:
    crit = [it for it in cat.items if it.critical] or cat.items[:3]
    out = [
        f"■ TBM(작업 전 안전점검회의) - {cat.title}",
        f"  일시: 20__.__.__   장소: ______   참석: ___명",
        "",
        "  1) 오늘 작업 개요: ____________________",
        "  2) 핵심 위험요인 및 대책:",
    ]
    for it in crit:
        out.append(f"     - {it.question}  (근거: {it.ref})")
    out += [
        "  3) 필수 보호구: 안전모·안전화 등 ____________",
        "  4) 비상연락/대피: ____________",
        "  5) 건강상태 확인(과음·피로 등): 이상 유무 ____",
        "",
        "  ※ 국내 규정 기반. 세부 기준은 최신 법령·KOSHA 지침 확인.",
    ]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="국내 기준 건설 안전점검 체크리스트 생성")
    ap.add_argument("--category", "-c", help="공종/유형 (예: 공통, 추락, 비계, 굴착, 전기, 밀폐공간, 화기, 양중)")
    ap.add_argument("--format", "-f", choices=["text", "md"], default="text", help="출력 형식")
    ap.add_argument("--tbm", action="store_true", help="TBM 브리핑 요약본 생성")
    ap.add_argument("--list", action="store_true", help="사용 가능한 유형 목록 출력")
    args = ap.parse_args()

    if args.list or not args.category:
        print("사용 가능한 유형:")
        for k, c in CATEGORIES.items():
            print(f"  - {k}: {c.title} ({len(c.items)}개 항목)")
        if not args.category:
            print("\n예: python3 checklist_kr.py --category 추락")
        return 0

    cat = CATEGORIES.get(args.category)
    if cat is None:
        print(f"[오류] 알 수 없는 유형: {args.category}")
        print("사용 가능한 유형: " + ", ".join(CATEGORIES.keys()))
        return 1

    if args.tbm:
        print(render_tbm(cat))
    elif args.format == "md":
        print(render_md(cat))
    else:
        print(render_text(cat))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
