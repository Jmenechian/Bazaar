COMPOSE = docker compose -f infra/docker-compose.yml

.PHONY: help up down logs ps clean test lint

help:
	@echo "Bazaar Development Commands:"
	@echo "  make up      - Start infrastructure containers (Postgres, Mongo, NATS, Redis)"
	@echo "  make down    - Stop infrastructure containers"
	@echo "  make logs    - Tail container logs"
	@echo "  make ps      - Show running container status and health"
	@echo "  make clean   - Stop containers and delete all persistent volumes"
	@echo "  make run-users - Run Users service locally with auto-reload (port 8001)"
	@echo "  make test    - Run Go and Python tests"
	@echo "  make lint    - Run Go and Python linters"

run-users: up
	@cd services/users && .venv/bin/uvicorn main:app --reload --port 8001

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

clean:
	$(COMPOSE) down -v

test:
	@echo "==> Running Go tests..."
	go test ./...
	@if [ -d services/users/.venv ]; then \
		echo "==> Running Python tests..."; \
		(cd services/users && .venv/bin/pytest); \
	fi

lint:
	@echo "==> Running Go vet..."
	go vet ./...
	@if command -v ruff >/dev/null 2>&1; then \
		echo "==> Running Ruff on Python..."; \
		(cd services/users && ruff check .); \
	fi
