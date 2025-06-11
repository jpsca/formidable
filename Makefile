.PHONY: install
install:
	uv sync --group dev --group test --group debug

.PHONY: test
test:
	uv run pytest -x src tests

.PHONY: lint
lint:
	uv run ruff check src tests

.PHONY: types
types:
	uv run pyright src tests

.PHONY: coverage
coverage:
	uv run pytest --cov-report html --cov-report xml --cov src tests
	uv run genbadge coverage -i coverage.xml -n COVERAGE -o coverage.svg

.PHONY: tox
tox:
	uv run tox
