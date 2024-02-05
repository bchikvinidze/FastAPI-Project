install: ## Install requirements
	pip install -r requirements.txt

test:  ## Run tests
	pytest library/tests/*.py


format: ## Run code formatters
	isort library
	black library

lint: ## Run code linters
	isort --check library
	black --check library
	flake8 library
	mypy library

test:  ## Run tests with coverage
	pytest --cov
