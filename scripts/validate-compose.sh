#!/bin/sh
set -eu

: "${POSTGRES_PASSWORD:=compose-validation-only}"
export POSTGRES_PASSWORD

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    exec docker compose -f deploy/compose/compose.yaml config --quiet
fi
if command -v docker-compose >/dev/null 2>&1; then
    exec docker-compose -f deploy/compose/compose.yaml config --quiet
fi

printf '%s\n' 'Docker Compose v2 is required to validate deploy/compose/compose.yaml.' >&2
exit 127
