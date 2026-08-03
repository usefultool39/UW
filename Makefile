.PHONY: setup quality backend-test frontend-test build e2e

setup:
	./启动游戏.command --setup-only

quality:
	./scripts/quality.sh

backend-test:
	backend/.venv/bin/python -m pytest -q

frontend-test:
	npm --prefix frontend run test:unit

build:
	npm --prefix frontend run build

e2e:
	cd frontend && PYTHON_BIN=../backend/.venv/bin/python npm run test:e2e
