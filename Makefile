.PHONY: format lint test clean build

all: format lint

format:
	poetry run autoflake -ir --remove-all-unused-imports .; \
	poetry run isort --quiet .; \
	poetry run black --preview .;

lint:
	poetry run pylint -v --load-plugins pylint_quotes ./web_auth ./test

startup:
	poetry run uvicorn test.fastapi:app --reload

test:
	poetry run pytest -s --cov=web_auth

test_fastapi:
	poetry run pytest -s --log-cli-level=DEBUG --ignore=test/flask --ignore=test/django

test_flask:
	poetry run pytest -s --log-cli-level=DEBUG --ignore=test/fastapi --ignore=test/django

test_django:
	poetry run pytest -s --log-cli-level=DEBUG --ignore=test/fastapi --ignore=test/flask

test_versions:
	poetry run tox -c fastapi-tox.ini; \
	poetry run tox -c flask-tox.ini; \
	poetry run tox -c django-tox.ini;

clean:
	@if [ -d "build" ]; then \
		rm -rf build; \
	fi
	@if [ -d "dist" ]; then \
		rm -rf dist; \
	fi

build: clean
	poetry build
