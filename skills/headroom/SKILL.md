---
name: headroom
description: Headroom(headroomlabs-ai/headroom) — AI 에이전트가 읽는 도구 출력·로그·RAG·파일·대화 이력을 LLM에 보내기 전에 로컬에서 압축해 토큰 비용을 줄이는 "컨텍스트 압축 레이어"의 동작 로직과 사용법을 설명한다. 사용자가 Headroom, 토큰 절감, 컨텍스트 압축, headroom wrap/proxy/learn/mcp, CCR(headroom_retrieve), SmartCrusher, ContentRouter, 출력 토큰 절감을 묻거나 도입·설정·튜닝·문제 해결을 요청할 때 사용한다.
---

# Headroom — 컨텍스트 압축 레이어

> 기준: `headroomlabs-ai/headroom` 기본 브랜치 커밋 `72302a3` (2026-10-12) 소스 직접 확인. Apache-2.0.
> 한 줄 요약: **에이전트가 읽는 모든 것을 LLM에 닿기 전에 로컬에서 압축하고, 원본은 로컬에 캐시해 필요할 때 되살린다.**

## 1. 무엇인가
| 구분 | 내용 |
|---|---|
| 정체 | 에이전트 ↔ LLM 사이에 끼는 **로컬 압축 프록시/라이브러리/MCP 서버** (Python `headroom-ai`, TypeScript SDK, Rust 코어) |
| 압축 대상 | 도구 출력(JSON·로그·검색결과·diff), 코드, 텍스트, HTML, 이미지, 대화 이력 |
| 핵심 약속 | 같은 답을 더 적은 토큰으로. 압축은 **로컬**에서 수행(프롬프트가 압축용으로 외부 전송되지 않음) |
| 3가지 축 | ① 입력 압축 ② 출력 토큰 절감 ③ 학습/메모리(`learn`, cross-agent memory) |

## 2. 로직 한눈에 (자세한 건 `references/`)
```
요청(messages)
  │  ① Live-zone 판별: 캐시된 앞부분(frozen prefix)은 바이트 그대로 보존, 최신 블록만 후보
  ▼
  CacheAligner      → 시스템 프롬프트의 UUID/타임스탬프/JWT/해시 "감지·경고"만 (수정 안 함)
  ▼
  ContentRouter     → 내용 유형 감지 → 알맞은 압축기로 라우팅
  │     ├ JSON 배열  → SmartCrusher (통계 기반 행 선택, Rust)
  │     ├ 소스코드   → CodeCompressor (tree-sitter AST)
  │     ├ 검색결과   → SearchCompressor     ├ 로그/빌드 → LogCompressor
  │     ├ diff       → DiffCompressor       ├ HTML → 추출기
  │     ├ 표/설정    → Tabular/Config       └ 일반 텍스트 → Kompress-v2-base(ML, 선택)
  │   0단계로 항상 "무손실 접기(lossless-first)"를 먼저 시도
  ▼
  CCR               → 손실 압축분의 원본을 해시키로 로컬 저장 + <<ccr:HASH>> 마커 + headroom_retrieve 도구 주입
  ▼
압축된 요청 → LLM
  ▲ 모델이 headroom_retrieve(hash)를 부르면 프록시가 가로채 원본을 돌려줌(클라이언트는 모름)
```
핵심 불변식: **(a)** 대화 메시지를 *삭제하지 않는다* **(b)** 캐시 핫존(시스템 프롬프트·툴 정의·지난 턴)은 *바이트 불변* **(c)** 압축기가 실패하거나 더 커지면 *원본 반환(fail-open)*.

## 3. 언제 쓰나 / 쓰지 않나
- **쓰기 좋음**: 도구 출력이 큰 장시간 에이전트 세션(SRE 디버깅, 코드 탐색, 이슈 트리아지), 여러 에이전트 공유 메모리, "되돌릴 수 있는" 압축이 필요할 때.
- **효과 작음**: 짧은 대화, 이미 조밀한 산문, 코드(대부분 보호되어 통과), `min_input_words` 미만 블록(바이트 동일 반환).
- **건너뜀**: 한 공급자의 네이티브 컴팩션만 쓰고 메모리 공유가 불필요하거나, 로컬 프로세스를 못 띄우는 샌드박스.

## 4. 빠른 시작
```bash
pip install "headroom-ai[all]"            # CLI 포함 (npm 패키지는 SDK 전용, CLI 없음)
headroom wrap claude                      # 에이전트를 감싸 실행(프록시 자동 기동). 해제: headroom unwrap claude
headroom proxy --port 8787                # 코드 변경 없는 프록시 (ANTHROPIC_BASE_URL=http://127.0.0.1:8787)
headroom mcp install                      # MCP 도구: headroom_compress / headroom_retrieve / headroom_stats
headroom doctor ; headroom perf ; headroom dashboard   # 점검·성능·대시보드
headroom learn [--apply]                  # 실패 세션에서 교정 규칙 추출 → CLAUDE.local.md
export HEADROOM_OUTPUT_SHAPER=1           # 출력 토큰 절감(기본 꺼짐)
```
```python
from headroom import compress
r = compress(messages, model="gpt-4o")      # 같은 형식의 messages 반환
print(r.tokens_saved, r.compression_ratio)
```

## 5. 이 스킬을 쓰는 방법 (Claude용 지침)
1. 사용자가 **개념/원리**를 물으면 §2와 `references/02~05`를 근거로 설명한다.
2. **도입/설정**이면 `references/06`(설치·CLI·환경변수)을 따라 안내하고, 에이전트 종류별 `wrap` 가능 여부를 확인한다.
3. **효과가 안 나오는 이유**는 `references/07`(한계·보호 규칙)에서 찾는다 — 코드 보호, 최근 N개 보호, 임계값, 분석 의도 키워드가 대표 원인.
4. 수치(절감률 등)는 README의 **재현 가능한 벤치**(`benchmarks/index_proof_table.py --seed 20260902`)와 "내 트래픽에서 `headroom savings`로 측정" 원칙을 함께 전한다. 출력 토큰 절감은 **추정치**임을 밝힌다.
5. 문서와 코드가 어긋나는 곳(예: CacheAligner)은 **코드가 정답**임을 `references/07`의 "문서-코드 불일치"로 알린다.

## 6. 참고 파일
| 파일 | 내용 |
|---|---|
| `references/01-overview.md` | 문제 정의, 구성요소 지도, 진입 방식 4가지 |
| `references/02-pipeline-logic.md` | 요청 수명주기, live-zone, 파이프라인·서킷브레이커, `compress()` 옵션/모드 |
| `references/03-compressors.md` | ContentRouter 라우팅·무손실 우선·net-cost 게이트, SmartCrusher 알고리즘, 각 압축기 |
| `references/04-ccr-reversible.md` | CCR 마커·센티널·도구 주입·응답 가로채기·TTL |
| `references/05-output-and-learning.md` | 출력 토큰 절감(verbosity/effort), `learn`, 메모리, SharedContext |
| `references/06-install-and-usage.md` | 설치, wrap 대상 표, 프록시/MCP/SDK 연동, 환경변수, 진단 |
| `references/07-limitations-and-caveats.md` | 한계, 보호 규칙, 문서-코드 불일치, 텔레메트리 |
| `README.md` | 이 패키지 소개 |
