.PHONY: install
install:
	uv sync --extra email --group dev --group test --group debug --group doc --python 3.13

.PHONY: test
test:
	uv run pytest -x src tests

.PHONY: lint
lint:
	uv run ruff check src tests
	uv run ty check

.PHONY: coverage
coverage:
	uv run pytest --cov-config=pyproject.toml --cov-report html src tests

.PHONY: docs
docs:
	cd docs && \
		uv run python docs.py

.PHONY: docs-build
docs-build:
	cd docs && uv run python docs.py build

.PHONY: docs-deploy
docs-deploy:
	rm -rf docs/build
	cd docs && \
		uv run python docs.py build --llm && \
		rsync --recursive --delete --progress build code:/var/www/formidable/
