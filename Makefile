# Makefile - ProtoForge

.PHONY: help check install dev docker-init docker-start docker-stop test lint format config

help:
	@echo "ProtoForge Make Commands"
	@echo "========================"
	@echo "make check          - Check system prerequisites"
	@echo "make install        - Install all dependencies"
	@echo "make dev            - Start all services"
	@echo "make docker-init    - Initialize Docker sandbox"
	@echo "make docker-start   - Start with Docker"
	@echo "make docker-stop    - Stop Docker services"
	@echo "make test           - Run tests"
	@echo "make lint           - Lint code"
	@echo "make format         - Format code"
	@echo "make config         - Generate config files"

# Check prerequisites
check:
	@echo "Checking prerequisites..."
	@command -v python3 >/dev/null 2>&1 || { echo "Python3 required"; exit 1; }
	@command -v pnpm >/dev/null 2>&1 || { echo "pnpm required"; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo "uv required"; exit 1; }
	@echo "All prerequisites met"

# Install all dependencies
install:
	@echo "Installing dependencies..."
	cd backend && make install
	cd frontend && make install
	@echo "Dependencies installed"

# Development server
dev:
	@echo "Starting ProtoForge..."
	cd backend && make dev

# Docker initialization
docker-init:
	@echo "Pulling sandbox image..."
	docker pull protoforge/sandbox:latest || true

# Docker start
docker-start:
	@echo "Starting ProtoForge with Docker..."
	docker-compose up -d
	@echo "ProtoForge running at http://localhost:2026"

# Docker stop
docker-stop:
	@echo "Stopping ProtoForge..."
	docker-compose down

# Run tests
test:
	cd backend && make test

# Lint code
lint:
	cd backend && make lint

# Format code
format:
	cd backend && make format

# Generate config
config:
	@echo "Generating configuration..."
	@cp config.example.yaml config.yaml 2>/dev/null || true
	@cp extensions_config.example.json extensions_config.json 2>/dev/null || true
	@echo "Config generated - edit config.yaml to add your API keys"
