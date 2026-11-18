#!/usr/bin/env bash
# God's Eye View 설치 + Claude Code MCP 등록 (macOS / Linux / WSL)
set -euo pipefail

GEV_DIR="${GEV_DIR:-$HOME/gods-eye-view}"
GEV_PORT="${GEV_PORT:-4173}"
GEV_SCOPE="${GEV_SCOPE:-user}"
REPO="https://github.com/bilawalsidhu/gods-eye-view.git"

say()  { printf '\033[1m==> %s\033[0m\n' "$*"; }
fail() { printf '\033[31m오류: %s\033[0m\n' "$*" >&2; exit 1; }

say "1/5 필수 도구 확인"
for cmd in git node npm claude; do
  command -v "$cmd" >/dev/null 2>&1 || fail "'$cmd' 를 찾을 수 없습니다. 먼저 설치하세요."
done

node_ver="$(node -p 'process.versions.node')"
IFS=. read -r maj min _ <<<"$node_ver"
if ! { [ "$maj" -eq 26 ] || { [ "$maj" -eq 24 ] && [ "$min" -ge 14 ]; }; }; then
  fail "Node $node_ver 는 지원되지 않습니다 (24.14 이상 24.x 또는 26.x 필요). nvm/fnm 으로 'nvm install 24' 후 다시 실행하세요."
fi
echo "Node $node_ver OK"

say "2/5 소스 준비: $GEV_DIR"
if [ -d "$GEV_DIR/.git" ]; then
  git -C "$GEV_DIR" pull --ff-only
elif [ -e "$GEV_DIR" ] && [ -n "$(ls -A "$GEV_DIR" 2>/dev/null)" ]; then
  fail "$GEV_DIR 가 비어 있지 않은 다른 폴더입니다. GEV_DIR 로 다른 위치를 지정하세요."
else
  git clone --depth 1 "$REPO" "$GEV_DIR"
fi

say "3/5 의존성 설치 (npm ci)"
( cd "$GEV_DIR" && npm ci )

say "4/5 Claude Code MCP 등록 (scope: $GEV_SCOPE)"
claude mcp remove gods-eye-view --scope "$GEV_SCOPE" >/dev/null 2>&1 || true
claude mcp add --scope "$GEV_SCOPE" gods-eye-view -- \
  node "$GEV_DIR/server/mcp/stdio.js" --api-base "http://localhost:$GEV_PORT"

say "5/5 완료"
cat <<MSG

사용 방법
  1) 터미널 하나에서 앱을 켜 둡니다 (끄지 마세요):
       cd "$GEV_DIR" && npm run dev
  2) Claude Code 를 새로 시작합니다.
  3) 물어보세요:  Show San Diego in God's Eye View with military flights on.
  4) 지구본은 http://localhost:$GEV_PORT 에서 봅니다.

점검:  claude mcp list   (gods-eye-view 가 Connected 인지 확인)
MSG
