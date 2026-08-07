.PHONY: quality release backend-test frontend-test frontend-build

quality:
	./scripts/quality.sh

release:
	./scripts/release.sh

backend-test:
	./backend/.venv/bin/python -m pytest -q backend/tests

frontend-test:
	npm --prefix frontend run test:unit

frontend-build:
	npm --prefix frontend run build
