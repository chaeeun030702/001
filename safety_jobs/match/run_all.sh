#!/bin/sh
# 사용: sh run_all.sh <main latest.json> <broad latest.json>   (이 폴더에서 실행, 결과: matching_briefing.html)
set -e
cd "$(dirname "$0")"
[ "$(realpath "$1")" = "$PWD/latest_main.json" ] || cp "$1" latest_main.json
export MAIN_JSON="$PWD/latest_main.json"
python3 build_broad.py "$2"
python3 cr.py
python3 build.py
