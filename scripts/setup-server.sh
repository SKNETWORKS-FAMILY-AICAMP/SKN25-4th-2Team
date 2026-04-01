#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="arxplore_server"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

if [[ ! -f .env ]]; then
  echo ".env 파일이 없습니다. 루트에 .env를 만든 뒤 다시 실행하세요."
  exit 1
fi

docker build -t arxplore-airflow -f docker/airflow/Dockerfile .
docker compose -p "${PROJECT_NAME}" -f docker-compose.server.yml up -d --build

echo
echo "[server] 컨테이너 상태"
docker compose -p "${PROJECT_NAME}" -f docker-compose.server.yml ps

echo
echo "[server] 접속 정보"
echo "Airflow: http://localhost:${SERVER_AIRFLOW_PORT:-18080}"
echo "MongoDB: localhost:${SERVER_MONGO_PORT:-17017}"
echo "PostgreSQL: localhost:${SERVER_POSTGRES_PORT:-15432}"
