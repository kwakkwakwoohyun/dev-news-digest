#!/usr/bin/env bash
# Claude Code가 파일을 수정(Edit/Write)한 직후 자동으로 실행되는 하네스 스크립트.
# 목적: 코드 스타일/타입 오류를 사람이 리뷰하기 전에 즉시 잡아내는 것.

set -uo pipefail  # set -e는 의도적으로 뺐다: 린트가 실패해도 훅 자체가 죽지 않고 메시지를 보여주기 위함

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
BACKEND_DIR="$PROJECT_DIR/backend"

# backend 폴더가 아직 없으면 조용히 통과 (초기 스캐폴딩 전 단계)
if [ ! -d "$BACKEND_DIR" ]; then
  exit 0
fi

cd "$BACKEND_DIR" || exit 0

# ruff가 설치되어 있을 때만 실행 (가상환경 세팅 전이면 건너뜀)
if command -v ruff >/dev/null 2>&1; then
  echo "[하네스] ruff로 린트 검사 중..."
  ruff check .
else
  echo "[하네스] ruff가 설치되어 있지 않아 린트 검사를 건너뜁니다. (pip install -r requirements-dev.txt)"
fi
