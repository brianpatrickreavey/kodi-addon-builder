.PHONY: help test lint format clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test:  ## Run tests with coverage
	pytest --cov=src/kodi_addon_builder --cov-report=html --cov-report=term --cov-report=term-missing

lint:  ## Run linting with flake8
	flake8 src/ tests/

format:  ## Format code with black
	black --config pyproject.toml src/ tests/

format-check:  ## Check formatting with black
	black --config pyproject.toml --check --diff src/ tests/

type-check:  ## Run type checking with pyright
	pyright src/

clean:  ## Clean up generated files
	rm -rf htmlcov/ .coverage .pytest_cache/ src/*.egg-info/ dist/

build:  ## Build package distributions
	python -m build

build-check:  ## Check built distributions
	twine check dist/*