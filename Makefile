include .env
export $(shell sed 's/=.*//' .env)

up_to = "head"
down_to = "-1"

migrate_up:
	cd internal/db/migrations && alembic upgrade $(up_to)

migrate_down:
	cd internal/db/migrations && alembic downgrade $(down_to)

create_migration:
	 cd internal/db/migrations && alembic revision --message=$(name) --autogenerate

run_unvicorn:
	uvicorn internal.main:app --host 0.0.0.0 --port 8000 --reload

run_gunicorn_workers:
	gunicorn internal.main:app --workers $(workers) --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

docker_run:
	docker-compose up --build

docker_up:
	docker-compose up --build -d

docker_down:
	docker-compose down