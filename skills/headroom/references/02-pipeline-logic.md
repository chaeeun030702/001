# 02. 파이프라인 로직

## 2.1 요청 수명주기
`Setup → Pre-Start → Post-Start → Input Received → Input Cached → Input Routed → Input Compressed → Input Remembered → Pre-Send → Post-Send → Response Received`
(`headroom/pipeline.py`의 `PipelineStage`; 확장은 `on_pipeline_event(...)`로 각 단계를 관찰/수정). `compress()`·SDK·프록시가 이 수명주기를 공유한다.

## 2.2 변환 순서 (`TransformPipeline._build_default_transforms`)
```
0. ToolResultInterceptor  (롤아웃 플래그 tool_result_interceptors — 예: ast-grep Read 개요화; 먼저 줄여서 뒤 단계가 이득)
1. CacheAligner           (config.cache_aligner.enabled — 감지·경고 전용)
2. ContentRouter          (모든 유형을 감지해 알맞은 압축기로)
```
과거의 `IntelligentContextManager`/`RollingWindow`(메시지를 *버리는* 단계)는 **Phase B PR-B1에서 제거**되었다. 지금은 *live-zone-only* 압축이 유일한 전략이다.

### `apply()` 의사코드
```python
def apply(messages, model, model_limit, **kw):
    if breaker_is_open():                      # 연속 실패 3회 → 60초간 패스스루
        return passthrough(messages)           # transforms_applied=["pipeline:circuit_open"]
    tokens_before = tokenizer.count_messages(messages)
    cur = deep_copy(messages)                  # 입력 불변
    for t in transforms:
        if not t.should_apply(cur, tokenizer, **kw): continue
        try:  res = t.apply(cur, tokenizer, **kw)
        except Exception: breaker_record_failure(); raise   # 로그엔 프레임 위치만(페이로드 비노출)
        cur = res.messages                     # 변환기가 보고한 토큰 수 재사용(재카운트 안 함)
    breaker_record_success()
    # 절감이 100토큰 초과일 때만, 그리고 입력이 100k 토큰 이하일 때만 waste-signal 진단(텔레메트리 전용)
    return TransformResult(cur, tokens_before, tokens_after, transforms_applied, warnings, timing)
```
- 서킷브레이커: `HEADROOM_PIPELINE_BREAKER_THRESHOLD`(기본 3), `HEADROOM_PIPELINE_BREAKER_COOLDOWN_S`(기본 60). 잘못된 값은 경고 후 기본값.
- 토크나이저: OpenAI=tiktoken(정확), Anthropic=보정된 추정(~3.5자/토큰), 오픈모델=HF(설치 시), 미상=문자 기반 추정.

## 2.3 Live-zone: "무엇을 건드려도 되는가"
캐시 적중(0.1× 읽기 요금)을 지키기 위해 **프리픽스는 바이트 단위로 불변**이어야 한다. 그래서:
- **바닥(floor)**: `frozen_message_count` — 명시적 `cache_control` 마커로 계산(Rust `compute_frozen_count`). 이 인덱스 미만은 절대 변경 금지.
- **천장(ceiling)**: 최신 user 메시지. 직전 assistant 메시지는 "다음 응답이 이어받는 핫존"이라 건드리지 않음.
- **후보**: 최신 user 메시지 안의 블록. 가장 흔한 것은 `tool_result`, `text`(사용자가 붙여넣은 긴 로그)도 가능.
- **변경 방식**: JSON을 파싱→수정→재직렬화하지 않고 **바이트 범위 수술**(`out = body[..start] || 교체문 || body[end..]`). 압축 안 한 구간의 SHA-256이 입력과 동일함을 CI 테스트(`byte_fidelity_outside_compressed_block`)로 고정.
- **토크나이저 검증 게이트**: 블록별로 `compressed.tokens >= original.tokens`면 원본으로 되돌림.
- **유형별 임계값**(코드 주석 기준): 소스코드 2048, 일반 텍스트 5120(바이트), HTML은 현재 no-op.
- 디스패처는 현재 Anthropic `/v1/messages`용이 먼저 구현되고, OpenAI Chat/Responses·Gemini는 각자 walker 필요(Phase C에서 확장 — 요청 형태가 다르기 때문: OpenAI는 `role:"tool"`, Responses는 `input`+`function_call_output`, Gemini는 `contents/parts/function_response`).

## 2.4 `compress()` 옵션과 모드
| 옵션 | 기본 | 의미 |
|---|---|---|
| `compress_user_messages` | False | 사용자 메시지도 압축(문서/RAG는 True) |
| `compress_system_messages` | True | 시스템 프롬프트 압축 여부(음성 에이전트는 False) |
| `protect_recent` | 4 | 마지막 N개 메시지는 압축 안 함(0이면 전부) |
| `protect_analysis_context` | True | "analyze/review/…" 의도가 보이면 코드 보호 |
| `frozen_message_count` | 0 | 이미 공급자 캐시에 앵커된 앞부분 수(프록시가 자동 계산) |
| `target_ratio` | None | Kompress 보존 비율(None=모델 결정 ~15% 보존, 0.5/0.7=보수적). SmartCrusher에는 영향 없음 |
| `min_tokens_to_compress` | 250 | 이보다 짧은 메시지는 유지 |
| `kompress_model` | None | `'disabled'`면 ML 텍스트 압축 끔(SmartCrusher+CacheAligner만) |
| `savings_profile` | None | 예: `'agent-90'` 고절감 프로파일 |
| `diagnostics` | False | 메시지별 결정(`MessageDecision`) 반환. `HEADROOM_DIAGNOSTICS=1`도 가능 |
| `mode` | None | `None`=기본(CCR 제거+검색 허용), `"agent"`=**무손실 치밀화만**(CCR·ML 없음, 결정적이라 캐시 안전, `verify_lossless` 강제) |
| `verify_lossless` | False | 메시지별 왕복 검증, 증명 못 하면 원본으로 되돌림 → `CompressResult.lossless`, `reverted_messages` |

`densify()`는 `mode="agent"`의 약칭. 훅(`CompressionHooks`)으로 메시지별 **bias(소프트 가중)** 와 **protect(하드 거부권)** 를 줄 수 있다.

### 사용 패턴
```python
compress(messages, model="gpt-4o")                                   # 코딩 에이전트 기본
compress(messages, model="claude-opus-4-20250514",
         compress_user_messages=True, target_ratio=0.5, protect_recent=0)  # 금융 문서
compress(messages, model="gpt-4o", target_ratio=0.2)                 # 로그/검색결과 공격적
compress(messages, model="…", mode="agent")                          # 라이브 에이전트: 무손실만
```
