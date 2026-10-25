"""ChatGPT(OpenAI) 웹 검색 질문 — MCP 연결이 없는 예약 루틴에서도 쓰는 명령줄 도구.

기본은 Responses API(gpt-5 + web_search 도구) — gpt-5-search-api(chat/completions)보다 분당 한도가 훨씬 크다
(2026-10-25 확인: gpt-5 1,000,000 TPM, gpt-5-search-api 45,000 TPM). --api chat 이면 예전 방식.
OPENAI_API_KEY(환경 변수)가 있어야 한다. 표준 라이브러리만 쓴다.

    python3 safety_jobs/ask_chatgpt.py "대한유화 2026 신입 안전관리자 공고 마감일, 출처 URL"
    echo "질문" | python3 safety_jobs/ask_chatgpt.py -

분당 한도(429)면 --retry 번(기본 3) 60초씩 기다렸다 다시 묻는다. 답은 표준 출력, 오류는 표준 오류(종료 코드 1).
자소서 본문·개인 정보는 보내지 않는다(회사명·공고명 같은 공개 정보만).
"""
import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

DEFAULT_MODEL = "gpt-5"
CHAT_MODEL = "gpt-5-search-api"


def ssl_context():
    for path in (os.environ.get("SSL_CERT_FILE"), "/root/.ccr/ca-bundle.crt"):
        if path and os.path.exists(path):
            return ssl.create_default_context(cafile=path)
    return ssl.create_default_context()


def _post(url, body, key, retry):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(retry + 1):
        try:
            with urllib.request.urlopen(req, timeout=300, context=ssl_context()) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retry:
                time.sleep(60 if e.code == 429 else 10)
                continue
            raise RuntimeError(f"OpenAI API 오류 {e.code}: {e.read().decode(errors='replace')[:300]}")
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:  # 연결 끊김(긴 검색 응답) → 잠시 뒤 다시
            if attempt < retry:
                time.sleep(10)
                continue
            raise RuntimeError(f"연결 오류: {e}")


def ask(prompt, model=None, system=None, max_tokens=None, retry=3, api="responses", effort=None):
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY 가 설정되어 있지 않습니다.")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    if api == "chat":
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        body = {"model": model or CHAT_MODEL, "messages": msgs}
        if max_tokens:
            body["max_tokens"] = max_tokens
        return _post(f"{base}/chat/completions", body, key, retry)["choices"][0]["message"]["content"]
    body = {"model": model or DEFAULT_MODEL, "input": prompt, "tools": [{"type": "web_search"}]}
    if system:
        body["instructions"] = system
    if effort:  # gpt-5 생각 단계 길이(minimal/low/medium/high) — low 면 빠르다
        body["reasoning"] = {"effort": effort}
    if max_tokens:
        body["max_output_tokens"] = max_tokens
    data = _post(f"{base}/responses", body, key, retry)
    text = "\n".join(c.get("text", "") for o in data.get("output", []) if o.get("type") == "message"
                     for c in o.get("content", []) if c.get("type") == "output_text")
    if not text:
        raise RuntimeError(f"응답에 글이 없습니다(status {data.get('status')}, {data.get('incomplete_details')})")
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", help="질문(‘-’ 이면 표준 입력)")
    ap.add_argument("--model", help=f"기본 {DEFAULT_MODEL}(responses) / {CHAT_MODEL}(chat)")
    ap.add_argument("--api", choices=["responses", "chat"], default="responses")
    ap.add_argument("--effort", choices=["minimal", "low", "medium", "high"], help="responses 생각 단계 길이(빠르게: low)")
    ap.add_argument("--system")
    ap.add_argument("--max-tokens", type=int)
    ap.add_argument("--retry", type=int, default=3)
    a = ap.parse_args()
    prompt = sys.stdin.read() if a.prompt == "-" else a.prompt
    try:
        print(ask(prompt, a.model, a.system, a.max_tokens, a.retry, a.api, a.effort))
    except Exception as e:  # noqa: BLE001 — 명령줄 도구라 메시지만 남긴다
        print(f"[ask_chatgpt] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
