.PHONY: help up down restart logs clean test dev migrate

help:
	@echo "LLM Evaluation - Docker Commands"
	@echo ""
	@echo "make up        - Start all services"
	@echo "make down      - Stop all services"
	@echo "make restart   - Restart all services"
	@echo "make logs      - View logs (all services)"
	@echo "make clean     - Remove all containers and volumes"
	@echo "make test      - Run tests"
	@echo "make dev       - Start in development mode"
	@echo "make migrate   - Run database migrations"
	@echo "make shell     - Open shell in api-gateway"
	@echo "make ps        - Show running services"
	@echo "make build     - Build all images"

up:
	docker-compose up -d
	@echo "Services starting... Wait 30 seconds for initialization"
	@echo "API Gateway: http://localhost:8000"
	@echo "RabbitMQ: http://localhost:15672 (admin/admin)"
	@echo "Grafana: http://localhost:3000 (admin/admin)"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api-gateway

logs-workers:
	docker-compose logs -f worker-gemini worker-gpt

clean:
	@echo "WARNING: This will delete all data. Press Ctrl+C to cancel..."
	@sleep 5
	docker-compose down -v
	docker system prune -f

test:
	docker-compose exec api-gateway pytest tests/ -v

dev:
	docker-compose up

migrate:
	docker-compose exec postgres psql -U postgres -d llm_evaluation -f /docker-entrypoint-initdb.d/init-db.sql

shell:
	docker-compose exec api-gateway /bin/bash

ps:
	docker-compose ps

build:
	docker-compose build

scale-workers:
	docker-compose up -d --scale worker-gemini=3 --scale worker-gpt=3

health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/api/v1/health | jq .

backup-db:
	docker-compose exec postgres pg_dump -U postgres llm_evaluation > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up to backup_$(shell date +%Y%m%d_%H%M%S).sql"

restore-db:
	@echo "Enter backup file name:"
	@read file; cat $$file | docker-compose exec -T postgres psql -U postgres llm_evaluation

install:
	@echo "Copying .env.example to .env..."
	@cp .env.example .env
	@echo "Please edit .env and add your API keys"
	@echo "Then run: make up"
