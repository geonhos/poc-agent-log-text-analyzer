.PHONY: install format lint type-check test test-cov clean help

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies with Poetry"
	@echo "  make format       - Format code with black and isort"
	@echo "  make lint         - Run flake8 linter"
	@echo "  make type-check   - Run mypy type checker"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make clean        - Remove cache and build files"
	@echo "  make all          - Run format, lint, type-check, and test"

install:
	poetry install

install-langchain:
	poetry install --with langchain

install-llamaindex:
	poetry install --with llamaindex

install-all:
	poetry install --with langchain,llamaindex

format:
	poetry run black src tests
	poetry run isort src tests

lint:
	poetry run flake8 src tests
	poetry run ruff check src tests

type-check:
	poetry run mypy src

test:
	poetry run pytest tests -v

test-cov:
	poetry run pytest tests -v --cov=src --cov-report=term-missing --cov-report=html

test-unit:
	poetry run pytest tests -v -m unit

test-integration:
	poetry run pytest tests -v -m integration

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

all: format lint type-check test
