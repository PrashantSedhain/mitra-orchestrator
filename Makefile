.PHONY: install format lint typecheck test check compose-config

install:
	python -m pip install -e '.[dev,database]'

format:
	ruff format .
	ruff check --fix .

lint:
	ruff format --check .
	ruff check .

typecheck:
	mypy src tests

test:
	pytest --cov=mitra_orchestrator --cov-report=term-missing

check: lint typecheck test compose-config

compose-config:
	./scripts/validate-compose.sh
