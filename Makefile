.PHONY: dev lint test build clean install help

# Development
dev:
	@echo "Starting all services..."
	@cd apps/core && uv run uvicorn app.main:app --reload &
	@pnpm turbo dev

# Linting
lint:
	@echo "Linting Python..."
	@cd apps/core && uv run ruff check .
	@echo "Linting TypeScript..."
	@pnpm turbo lint

# Testing
test:
	@echo "Testing Python..."
	@cd apps/core && uv run pytest
	@echo "Testing TypeScript..."
	@pnpm turbo test

# Building
build:
	@echo "Building Python..."
	@cd apps/core && uv run pip install -e .
	@echo "Building TypeScript..."
	@pnpm turbo build

# Installation
install:
	@echo "Installing Python dependencies..."
	@cd apps/core && uv sync
	@echo "Installing TypeScript dependencies..."
	@pnpm install

# Cleaning
clean:
	@echo "Cleaning Python..."
	@cd apps/core && uv run pip uninstall -y tempus-core || true
	@echo "Cleaning TypeScript..."
	@pnpm clean
	@rm -rf node_modules apps/*/node_modules packages/*/node_modules

# Help
help:
	@echo "Available commands:"
	@echo "  dev     - Start all services in development mode"
	@echo "  lint    - Lint Python and TypeScript code"
	@echo "  test    - Run Python and TypeScript tests"
	@echo "  build   - Build Python and TypeScript packages"
	@echo "  install - Install all dependencies"
	@echo "  clean   - Clean build artifacts and node_modules"
	@echo "  help    - Show this help message"
