.PHONY: help install install-bot install-api run-bot run-api format lint docker-run clean
.DEFAULT_GOAL := help

# === НАСТРОЙКИ ===
PYTHON_VERSION := 3.11
BREW_PYTHON := python@$(PYTHON_VERSION)

# Пути к микросервисам
BOT_DIR := services/bot
API_DIR := services/database-api

help:
	@echo ""
	@echo "Usage: make \033[36m<target>\033[0m"
	@echo ""
	@echo "Targets:"
	@echo "  \033[36minstall\033[0m          Install dependencies for ALL services"
	@echo "  \033[36mrun-bot\033[0m          Run Bot locally"
	@echo "  \033[36mrun-api\033[0m          Run DB API locally (FastAPI)"
	@echo "  \033[36mformat\033[0m           Auto-format code in ALL folders"
	@echo "  \033[36mlint\033[0m             Check code style (CI mode)"
	@echo "  \033[36mdocker-run\033[0m       Run everything in Docker"
	@echo "  \033[36mclean\033[0m            Remove cache and venvs"
	@echo ""

# === INSTALLATION ===

install: install-bot install-api
	@echo "📝 Creating root .env file if not exists..."
	@test -f .env || cp .env.example .env
	@echo "✅ \033[32mFull Project Installation complete!\033[0m"

install-bot:
	@echo "🤖 Installing BOT dependencies..."
	@cd $(BOT_DIR) && poetry env use $$(brew --prefix $(BREW_PYTHON))/bin/python$(PYTHON_VERSION)
	@cd $(BOT_DIR) && poetry run pip install -U pip setuptools wheel
	@cd $(BOT_DIR) && poetry install

install-api:
	@echo "🗄️ Installing DB API dependencies..."
	@cd $(API_DIR) && poetry env use $$(brew --prefix $(BREW_PYTHON))/bin/python$(PYTHON_VERSION)
	@cd $(API_DIR) && poetry run pip install -U pip setuptools wheel
	@cd $(API_DIR) && poetry install

# === RUNNING ===

run-bot:
	@echo "🚀 Running Bot..."
	@cd $(BOT_DIR) && poetry run python -m src.main

run-api:
	@echo "🚀 Running DB API (Access at http://localhost:8000/docs)..."
	@cd $(API_DIR) && poetry run uvicorn src.main:app --reload

# === CODE QUALITY (DRY Principle apply here) ===

format:
	@echo "🎨 Formatting BOT..."
	@cd $(BOT_DIR) && poetry run isort .
	@cd $(BOT_DIR) && poetry run black .
	@echo "🎨 Formatting API..."
	@cd $(API_DIR) && poetry run isort .
	@cd $(API_DIR) && poetry run black .

formater: format

lint:
	@echo "🔍 Linting BOT..."
	@cd $(BOT_DIR) && poetry run isort --check-only .
	@cd $(BOT_DIR) && poetry run black --check .
	@echo "🔍 Linting API..."
	@cd $(API_DIR) && poetry run isort --check-only .
	@cd $(API_DIR) && poetry run black --check .

# === DOCKER ===

docker-build:
	docker-compose build

docker-run:
	docker-compose down
	docker-compose up --build

clean:
	@echo "🧹 Cleaning up..."
	@rm -rf $(BOT_DIR)/.venv
	@rm -rf $(API_DIR)/.venv
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@echo "✨ Cleaned!"
