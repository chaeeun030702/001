"""ChatGPT(OpenAI) 웹 검색 질문 — MCP 연결이 없는 예약 루틴에서도 쓰는 명령줄 도구.

server.py(MCP `ask_chatgpt`)와 같은 OpenAI chat/completions 를 표준 라이브러리만으로 부른다.
OPENAI_API_KEY(환경 변수)가 있어야 하고, 기본 모델은 웹 검색이 되는 gpt-5-search-api.

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

DEFAULT_MODEL = "gpt-5-search-api"


def ssl_context():
    for path in (os.environ.get("SSL_CERT_FILE"), "/root/.ccr/ca-bundle.crt"):
        if path and os.path.exists(path):
            return ssl.create_default_context(cafile=path)
    return ssl.create_default_context()


def ask(prompt, model=DEFAULT_MODEL, system=None, max_tokens=None, retry=3):
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY 가 설정되어 있지 않습니다.")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    body = {"model": model, "messages": msgs}
    if max_tokens:
        body["max_tokens"] = max_tokens
    req = urllib.request.Request(f"{base}/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(retry + 1):
        try:
            with urllib.request.urlopen(req, timeout=180, context=ssl_context()) as r:
                data = json.load(r)
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retry:
                time.sleep(60)
                continue
            raise RuntimeError(f"OpenAI API 오류 {e.code}: {e.read().decode(errors='replace')[:300]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", help="질문(‘-’ 이면 표준 입력)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--system")
    ap.add_argument("--max-tokens", type=int)
    ap.add_argument("--retry", type=int, default=3)
    a = ap.parse_args()
    prompt = sys.stdin.read() if a.prompt == "-" else a.prompt
    try:
        print(ask(prompt, a.model, a.system, a.max_tokens, a.retry))
    except Exception as e:  # noqa: BLE001 — 명령줄 도구라 메시지만 남긴다
        print(f"[ask_chatgpt] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
