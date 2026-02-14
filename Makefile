.PHONY: help install test lint format clean docker-build docker-up docker-down

help:
	@echo "UniVoice Development Commands"
	@echo "=============================="
	@echo "install       - Install dependencies"
	@echo "test          - Run tests"
	@echo "lint          - Run linters"
	@echo "format        - Format code"
	@echo "clean         - Clean build artifacts"
	@echo "docker-build  - Build Docker images"
	@echo "docker-up     - Start services with Docker Compose"
	@echo "docker-down   - Stop services"

install:
	pip install -r requirements.txt

install-poetry:
	poetry install

test:
	pytest -v --cov=src --cov-report=html

lint:
	ruff check src/
	mypy src/

format:
	black src/
	ruff check --fix src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build/ dist/ *.egg-info htmlcov/ .pytest_cache/ .coverage

docker-build:
	docker build -t univoice-base:latest -f Dockerfile.base .
	docker build -t univoice-audio-ingress:latest -f services/audio_ingress/Dockerfile .
	docker build -t univoice-speech-to-text:latest -f services/speech_to_text/Dockerfile .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
