# 04. CCR — Compress · Cache · Retrieve (가역 압축)

전통적 압축은 "중요한 걸 잘못 짚으면 영원히 손실"이라 공격성과 안전성이 상충한다. CCR은 **손실 압축한 부분의 원본을 로컬에 두고, 모델이 요청하면 돌려주는** 방식으로 이 상충을 없앤다.

## 4.1 흐름
```
도구 출력 1000행
  └ SmartCrusher: 20행만 남김
  └ 원본을 해시(abc123)로 LRU 저장소에 보관
  └ 남긴 배열 끝에 센티널 추가 + headroom_retrieve 도구를 요청의 tools에 주입
        ▼ LLM
   A) 20행으로 충분 → 끝 (큰 절감)
   B) headroom_retrieve(hash=abc123) 호출
        → 프록시 Response Handler가 도구 호출을 가로채 ~1ms에 로컬에서 조회
        → 결과를 대화에 붙여 API 호출을 자동 속행 (클라이언트에는 보이지 않음)
```

## 4.2 마커/센티널 형태
| 형태 | 예 | 쓰임 |
|---|---|---|
| dict 센티널 | `{"_ccr_dropped": "<<ccr:HASH N_rows_offloaded>>"}` | dict 배열의 드롭 행 자리 (`CCR_SENTINEL_KEY`) |
| 문자열 센티널 | `"… N more items <<ccr:HASH N_items_offloaded>>"` | 문자열/숫자/혼합 배열 (원소 타입 균일 유지) |
| 텍스트 마커 | `[1000 items compressed to 20. Retrieve more: hash=abc123]` | 문서상의 설명용 형태 |
- 균일 스키마를 가정하는 소비 코드는 `strip_ccr_sentinels(items)`로 센티널을 걸러야 한다(`is_ccr_sentinel`).
- `ccr_config.enabled=False` 또는 `inject_retrieval_marker=False`면 행 드롭 경로에서 **마커와 저장 둘 다** 생략.

## 4.3 4단계 구성
1. **Compression Store** — 해시키 → 원본, LRU/TTL (`headroom/cache/compression_store.py`)
2. **Tool Injection** — `headroom_retrieve` 툴 정의 주입 (`ccr/tool_injection.py`, 이름 상수 `CCR_TOOL_NAME`)
3. **Response Handler** — 모델의 retrieve 호출 가로채기·속행 (`ccr/response_handler.py`, 버퍼링 응답 `buffered_ccr_response.py`)
4. **Context Tracker** — 이전 턴에 압축된 것을 기억하고, 새 질의가 그 내용과 관련 있어 보이면 **모델이 묻기 전에 선제 확장** (예: 5턴째 "auth 미들웨어는?" → 500개 파일 목록 원본 확장). `--no-ccr-proactive-expansion`으로 끔.

## 4.4 가역성의 범위
- CCR은 **메시지를 지우는 게 아니라 콘텐츠 블록**(최신 tool_result 등)을 대상으로 한다. 시스템 프롬프트·툴 정의·지난 턴은 불변.
- **무손실 접기**(03 문서 §3.2)로 해결되는 건 CCR 마커 없이 끝난다. SmartCrusher도 무손실 컴팩션 절감률 ≥ 15%면 손실/CCR 경로를 타지 않는다.
- `mode="agent"`는 CCR 자체를 쓰지 않는다(무손실만).
- 검색(`query`)을 함께 주면 원본 안에서 일치 항목만 반환 가능(MCP `headroom_retrieve`).

## 4.5 TOIN 피드백
사용자가(모델이) 압축된 내용을 *다시 가져온* 패턴은 "그 필드/패턴이 중요했다"는 신호로 학습되어, 이후 같은 도구 출력의 압축에서 더 보존된다. 교차 세션 학습은 `TelemetryConfig.storage_path` 영속화가 필요.

## 4.6 설정
```bash
headroom proxy --port 8787                          # CCR 기본 켜짐
headroom proxy --no-ccr                             # 마커·headroom_retrieve 도구 모두 끔
headroom proxy --no-ccr-proactive-expansion         # 선제 확장만 끔
```
주의: 전체 compress→retrieve 루프(응답 가로채기·선제 확장)는 **프록시 안에서만** 돈다. SDK `compress()` 단독 호출은 임계값을 못 넘으면 마커 자체가 없을 수 있다(`examples/test_ccr.py` 결과가 "No CCR markers").
MCP 경로의 `headroom_compress` 원본 보관은 세션 단위 **1시간 TTL**.
