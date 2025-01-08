.PHONY: migrate
migrate:
	docker-compose run --rm app sh -c "poetry run python manage.py migrate"

.PHONY: migrations
migrations:
	docker-compose run --rm app sh -c "poetry run python manage.py makemigrations"

.PHONY: superuser
superuser:
	docker-compose run --rm app sh -c "poetry run python backend/manage.py createsuperuser"

.PHONY: create-app
create-app:
	docker-compose run --rm app sh -c "poetry run python manage.py startapp $(N)"

.PHONY: lint
lint:
	poetry run pre-commit run --all-files
