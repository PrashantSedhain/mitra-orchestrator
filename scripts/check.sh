#!/bin/sh
set -eu
ruff format --check .
ruff check .
mypy src tests
pytest --cov=mitra_orchestrator --cov-report=term-missing
./scripts/validate-compose.sh
