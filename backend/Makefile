# Backend Makefile

.PHONY: help install dev test lint format

help:
	@echo "ProtoForge Backend Commands"
	@echo "==========================="
	@echo "make install  - Install dependencies"
	@echo "make dev      - Run development server"
	@echo "make test     - Run tests"
	@echo "make lint     - Lint code"
	@echo "make format   - Format code"

install:
	uv pip install -r requirements.txt

dev:
	uv pip install -e .
	python -m src.gateway.app

test:
	PYTHONPATH=. pytest tests/ -v

lint:
	ruff check src/

format:
	ruff format src/
