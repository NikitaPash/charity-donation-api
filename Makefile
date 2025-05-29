.PHONY: help
help:
	@echo "Available commands:"
	@echo "  migrate         Apply database migrations"
	@echo "  migrations      Generate new migration files"
	@echo "  full-migration  Run migrations and generate new migrations"
	@echo "  superuser       Create a Django superuser interactively"
	@echo "  create-app N    Start a new Django app named \$(N)"
	@echo "  lint            Run pre-commit hooks on all files"
	@echo "  docker-lint     Run flake8 inside the Docker container"
	@echo "  test            Execute the full test suite"
	@echo "  rebuild         Rebuild Docker containers from scratch"
	@echo "  commit          Run migrations, lint and tests before commit"

.PHONY: migrate
migrate:
	docker-compose run --rm app sh -c "poetry run python manage.py wait_for_db && poetry run python manage.py migrate"

.PHONY: migrations
migrations:
	docker-compose run --rm app sh -c "poetry run python manage.py makemigrations"

.PHONY: full-migration
full-migration: migrations migrate ;

.PHONY: superuser
superuser:
	docker-compose run --rm app sh -c "poetry run python manage.py createsuperuser"

.PHONY: create-app
create-app:
	docker-compose run --rm app sh -c "poetry run python manage.py startapp $(N)"

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: docker-lint
docker-lint:
	docker-compose run --rm app sh -c "poetry run flake8"

.PHONY: test
test:
	docker-compose run --rm app sh -c "poetry run python manage.py test"

.PHONY: rebuild
rebuild:
	docker-compose down && docker-compose up --build

.PHONY: commit
commit: full-migration docker-lint test ;
