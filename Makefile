.PHONY: help install run format formatter lint docker-run clean
.DEFAULT_GOAL := help

# Переменные для удобства
PYTHON_VERSION := 3.11
BREW_PYTHON := python@$(PYTHON_VERSION)

help:
	@echo ""
	@echo "Usage: make \033[36m<target>\033[0m"
	@echo ""
	@echo "Targets:"
	@echo "  \033[36minstall\033[0m      Full setup for macOS (Brew Python + Poetry + Deps)"
	@echo "  \033[36mrun\033[0m          Run bot locally"
	@echo "  \033[36mformat\033[0m       Auto-format code (Black + Isort)"
	@echo "  \033[36mlint\033[0m         Check code style (CI mode)"
	@echo "  \033[36mdocker-build\033[0m Build Docker image"
	@echo "  \033[36mdocker-run\033[0m   Run inside Docker"
	@echo "  \033[36mclean\033[0m        Remove cache and virtual env"
	@echo ""

install:
	@echo "📦 Checking system requirements..."
	@which brew > /dev/null || (echo "❌ Homebrew not found. Please install it first."; exit 1)
	
	@echo "🐍 Installing/Updating Python $(PYTHON_VERSION)..."
	@brew list $(BREW_PYTHON) &>/dev/null || brew install $(BREW_PYTHON)
	
	@echo "📜 Installing Poetry..."
	@brew list poetry &>/dev/null || brew install poetry
	
	@echo "🔧 Configuring Poetry environment..."
	@poetry env use $$(brew --prefix $(BREW_PYTHON))/bin/python$(PYTHON_VERSION)
	
	@echo "🛠 Upgrading internal pip & build tools (fixes Rust errors)..."
	@poetry run pip install -U pip setuptools wheel
	
	@echo "📥 Installing project dependencies..."
	@poetry install
	
	@echo "📝 Creating .env file if not exists..."
	@test -f .env || cp .env.example .env
	
	@echo "✅ \033[32mInstallation complete! Don't forget to edit .env file!\033[0m"

run:
	poetry run python -m src.main

format:
	poetry run isort .
	poetry run black .



formatter: format

lint:
	poetry run isort --check-only .
	poetry run black --check .

docker-build:
	docker build .

docker-run:
	docker-compose down
	docker-compose up --build

clean:
	rm -rf .venv
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
