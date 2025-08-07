# Contract Explainer - Production Makefile
# Convenient commands for development and deployment

.PHONY: help install dev test deploy clean security performance docker

# Default target
help:
	@echo "Contract Explainer - Production Deployment Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run test suite"
	@echo "  security    - Run security scans"
	@echo "  performance - Run performance tests"
	@echo "  docker      - Build and run with Docker"
	@echo "  deploy      - Interactive deployment"
	@echo "  clean       - Clean temporary files"
	@echo "  format      - Format code with Black"
	@echo "  lint        - Run linting checks"
	@echo ""

# Installation
install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

install-dev: install
	@echo "Installing development dependencies..."
	pip install pytest pytest-cov black flake8 bandit safety
	@echo "Development environment ready!"

# Development
dev:
	@echo "Starting development server..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		cp .env.example .env; \
		echo "Please edit .env with your API keys before proceeding!"; \
		exit 1; \
	fi
	python app.py

dev-docker:
	@echo "Starting development server with Docker..."
	docker-compose -f docker-compose.dev.yml up --build

# Testing
test:
	@echo "Running test suite..."
	python -m pytest tests/ -v --cov=app --cov-report=term-missing
	@echo "Tests completed!"

test-coverage:
	@echo "Running tests with HTML coverage report..."
	python -m pytest tests/ --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/"

# Security
security:
	@echo "Running security scans..."
	bandit -r . -f json -o bandit-report.json || true
	bandit -r . -ll
	@echo "Checking for known vulnerabilities..."
	safety check
	@echo "Security scan completed!"

# Performance
performance:
	@echo "Running performance tests..."
	@if command -v k6 >/dev/null 2>&1; then \
		k6 run tests/performance/load-test.js; \
	else \
		echo "k6 not installed. Install from: https://k6.io/docs/getting-started/installation/"; \
	fi

# Code quality
format:
	@echo "Formatting code with Black..."
	black --line-length 100 *.py
	@echo "Code formatted!"

lint:
	@echo "Running linting checks..."
	flake8 --max-line-length=100 --ignore=E203,W503 *.py
	@echo "Linting completed!"

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t contract-explainer:latest .
	@echo "Docker image built!"

docker-run: docker-build
	@echo "Running Docker container..."
	docker run -p 5001:5001 --env-file .env contract-explainer:latest

docker:
	@echo "Starting production Docker setup..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from template..."; \
		cp .env.example .env; \
		echo "Please edit .env with your configuration!"; \
		exit 1; \
	fi
	docker-compose up --build

docker-prod:
	@echo "Starting production Docker services..."
	docker-compose up -d
	docker-compose logs -f

# Deployment
deploy:
	@echo "Starting interactive deployment..."
	python deploy/deploy.py

deploy-heroku:
	@echo "Deploying to Heroku..."
	python deploy/heroku.py

deploy-railway:
	@echo "Deploying to Railway..."
	python deploy/railway.py

deploy-render:
	@echo "Setting up Render deployment..."
	python deploy/render.py

# Maintenance
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f bandit-report.json
	rm -f safety-report.json
	@echo "Cleanup completed!"

clean-docker:
	@echo "Cleaning Docker resources..."
	docker-compose down --remove-orphans
	docker system prune -f
	@echo "Docker cleanup completed!"

# Health checks
health-check:
	@echo "Checking application health..."
	@if curl -f http://localhost:5001/health >/dev/null 2>&1; then \
		echo "✅ Application is healthy"; \
	else \
		echo "❌ Application is not responding"; \
		exit 1; \
	fi

health-detailed:
	@echo "Getting detailed health information..."
	curl -s http://localhost:5001/health/detailed | python -m json.tool

# Monitoring
logs:
	@echo "Showing application logs..."
	@if [ -f app.log ]; then \
		tail -f app.log; \
	else \
		echo "No log file found. Check your configuration."; \
	fi

metrics:
	@echo "Getting application metrics..."
	curl -s http://localhost:5001/metrics

# Environment management
env-check:
	@echo "Checking environment configuration..."
	@python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = ['DEEPSEEK_API_KEY', 'FLASK_SECRET_KEY']
missing_vars = []

for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print('❌ Missing required environment variables:')
    for var in missing_vars:
        print(f'  - {var}')
    exit(1)
else:
    print('✅ All required environment variables are set')
"

# Pre-deployment checks
pre-deploy: env-check test security
	@echo "Running pre-deployment checks..."
	@echo "✅ Environment variables verified"
	@echo "✅ Tests passed"
	@echo "✅ Security scans completed"
	@echo "Ready for deployment!"

# Full development setup
setup: install-dev env-check
	@echo "Setting up development environment..."
	@if [ ! -d uploads ]; then mkdir uploads; fi
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env with your API keys"
	@echo "2. Run 'make dev' to start development server"
	@echo "3. Visit http://localhost:5001"

# Production readiness check
prod-ready: pre-deploy performance
	@echo "Production readiness check completed!"
	@echo "Your application is ready for deployment! 🚀"

# Quick commands for common tasks
start: dev
stop:
	@echo "Stopping development server..."
	@pkill -f "python app.py" || true

restart: stop start

# Database operations (for future features)
db-init:
	@echo "Database initialization would go here..."

db-migrate:
	@echo "Database migration would go here..."

# Backup operations
backup:
	@echo "Creating backup..."
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	tar -czf "backup_$$timestamp.tar.gz" \
		--exclude=__pycache__ \
		--exclude=.git \
		--exclude=venv \
		--exclude=node_modules \
		--exclude=htmlcov \
		--exclude="*.pyc" \
		. && \
	echo "Backup created: backup_$$timestamp.tar.gz"

# Utility commands
version:
	@echo "Contract Explainer v1.0.0"
	@python --version
	@pip list | grep -E "(flask|python|gunicorn)"

status:
	@echo "Application Status:"
	@echo "=================="
	@make health-check
	@echo ""
	@echo "System Resources:"
	@python -c "
import psutil
print(f'CPU: {psutil.cpu_percent(interval=1):.1f}%')
print(f'Memory: {psutil.virtual_memory().percent:.1f}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent:.1f}%')
"