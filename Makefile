DEV_COMPOSE = docker-compose.dev.yml
PROD_COMPOSE = docker-compose.prod.yml
DEV_ENV = .env.dev
PROD_ENV = .env.prod

up-dev:
	docker compose --env-file $(DEV_ENV) -f $(DEV_COMPOSE) up -d

down-dev:
	docker compose --env-file $(DEV_ENV) -f $(DEV_COMPOSE) down --remove-orphans

rebuild-dev:
	docker compose --env-file $(DEV_ENV) -f $(DEV_COMPOSE) build --no-cache
	docker compose --env-file $(DEV_ENV) -f $(DEV_COMPOSE) up -d

logs-dev:
	docker compose --env-file $(DEV_ENV) -f $(DEV_COMPOSE) logs -f

ps-dev:
	docker compose --env-file $(DEV_ENV) -f $(DEV_COMPOSE) ps

up-prod:
	docker compose --env-file $(PROD_ENV) -f $(PROD_COMPOSE) up -d

down-prod:
	docker compose --env-file $(PROD_ENV) -f $(PROD_COMPOSE) down --remove-orphans

rebuild-prod:
	docker compose --env-file $(PROD_ENV) -f $(PROD_COMPOSE) build --no-cache
	docker compose --env-file $(PROD_ENV) -f $(PROD_COMPOSE) up -d

logs-prod:
	docker compose --env-file $(PROD_ENV) -f $(PROD_COMPOSE) logs -f

ps-prod:
	docker compose --env-file $(PROD_ENV) -f $(PROD_COMPOSE) ps

clean:
	- docker compose --env-file $(DEV_ENV)  -f $(DEV_COMPOSE)  down --remove-orphans -v
	- docker compose --env-file $(PROD_ENV) -f $(PROD_COMPOSE) down --remove-orphans -v
	- docker container prune -f
	- docker network prune -f
	- docker volume prune -f
