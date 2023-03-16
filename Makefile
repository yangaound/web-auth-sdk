.PHONY: format lint test

all: format lint

format:
	poetry run autoflake -ir --remove-all-unused-imports .; \
	poetry run isort --quiet .; \
	poetry run black --preview .;

lint:
	poetry run pylint -v --load-plugins pylint_quotes ./web_auth ./test

test:
	poetry run pytest -s

test_fastapi:
	poetry run pytest -s --log-cli-level=DEBUG --ignore=test/flask

test_flask:
	poetry run pytest -s --log-cli-level=DEBUG --ignore=test/fastapi

test_versions:
	poetry run tox
