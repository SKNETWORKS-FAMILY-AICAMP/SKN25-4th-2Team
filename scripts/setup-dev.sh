#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="arxplore_dev"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if [[ ! -f .env ]]; then
  echo ".env 파일이 없습니다. 루트에 .env를 만든 뒤 다시 실행하세요."
  exit 1
fi

docker compose -p "${PROJECT_NAME}" -f docker-compose.dev.yml up -d --build

echo
echo "[dev] 컨테이너 상태"
docker compose -p "${PROJECT_NAME}" -f docker-compose.dev.yml ps

echo
echo "[dev] 접속 정보"
echo "Frontend:  http://localhost:${FRONTEND_PORT:-5173}"
echo "Jupyter: http://localhost:${JUPYTER_PORT:-18888} (WSL 외부 접속 시 WSL IP 사용)"
echo "Django:    http://localhost:${DJANGO_PORT:-18001} (API + React shell)"
echo "접속 명령: docker compose -p ${PROJECT_NAME} -f docker-compose.dev.yml exec dev bash"
