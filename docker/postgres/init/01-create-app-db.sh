#!/usr/bin/env bash
set -euo pipefail

if [ -z "${APP_POSTGRES_DB:-}" ]; then
  echo "APP_POSTGRES_DB is not set; skipping extra database creation."
  exit 0
fi

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<EOSQL
SELECT 'CREATE DATABASE ${APP_POSTGRES_DB}'
WHERE NOT EXISTS (
  SELECT FROM pg_database WHERE datname = '${APP_POSTGRES_DB}'
)\gexec
EOSQL
