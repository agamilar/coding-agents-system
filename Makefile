.PHONY: help install test lint format clean docker-build docker-up docker-down docker-logs setup

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean temporary files"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - View Docker logs"
	@echo "  make setup         - Initial setup"

install:
	pip install -r requirements.txt

test:
	pytest

test-cov:
	pytest --cov=agents --cov=github_app --cov=utils --cov-report=html --cov-report=term

lint:
	ruff check .
	black --check .
	mypy .

format:
	ruff check --fix .
	black .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov coverage.json
	rm -rf build dist

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-up-ngrok:
	docker-compose --profile ngrok up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

docker-clean:
	docker-compose down -v
	docker system prune -f

setup:
	@echo "Setting up Coding Agents System..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	@if [ ! -d keys ]; then mkdir -p keys; echo "Created keys directory"; fi
	@echo "Setup complete!"
	@echo "Please:"
	@echo "  1. Edit .env file with your credentials"
	@echo "  2. Place private-key.pem in keys/ directory"
	@echo "  3. Run 'make docker-up' or './start.sh'"

dev:
	python app/main.py

run-local: install
	python app/main.py

check-health:
	@curl -s http://localhost:3000/health | python -m json.tool

tunnel:
	python -m utils.tunnel
