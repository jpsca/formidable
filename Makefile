.PHONY: install
install:
	uv sync --extra email --group dev --group test --group debug --group doc

.PHONY: test
test:
	uv run pytest -x src tests

.PHONY: lint
lint:
	uv run ruff check src tests
	uv run ty check

.PHONY: coverage
coverage:
	uv run pytest --cov-config=pyproject.toml --cov-report html --cov formidable src tests

.PHONY: docs
docs:
	cd docs && uv run python docs.py

.PHONY: docs-build
docs-build:
	cd docs && uv run python docs.py build

.PHONY: docs-deploy
docs-deploy:
	cd docs && uv run sh deploy.sh