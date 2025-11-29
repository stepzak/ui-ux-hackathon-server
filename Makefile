.PHONY: build-base build-all

build-base:
	docker build -t ui-ux-base:latest . --network=host

build-all: build-base
	docker compose --profile all -f docker-compose-prod.yml build

build-dev: build-base
	docker compose --profile all -f docker-compose-dev.yml build

up:
	docker compose --profile all -f docker-compose-prod.yml up

down:
	docker compose --profile all -f  docker-compose-prod.yml -f docker-compose-dev.yml down

dev: build-base
	docker compose --profile all -f docker-compose-dev.yml up

up-database:
	docker compose --profile db -f docker-compose-prod.yml up

migration:
ifndef m
	$(error Please specify migration message: make migration m="your message")
endif
	docker compose -f docker-compose-dev.yml --profile db run --rm migrations sh -c "alembic revision --autogenerate -m '$(m)'"

downgrade:
ifndef to
	$(error Please specify to="-1")
endif
	docker compose -f docker-compose-dev.yml --profile db run --rm migrations sh -c "alembic downgrade $(to)"

upgrade:
ifndef to
	$(error Please specify to="head")
endif
	docker compose -f docker-compose-dev.yml --profile db run --rm migrations sh -c "alembic upgrade $(to)"