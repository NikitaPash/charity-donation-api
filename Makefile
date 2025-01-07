.PHONY: install
install:
	poetry install

.PHONY: migrate
migrate:
	poetry run python backend/manage.py migrate

.PHONY: migrations
migrations:
	poetry run python backend/manage.py makemigrations

.PHONY: runserver
runserver:
	poetry run python backend/manage.py runserver

.PHONY: superuser
superuser:
	poetry run python backend/manage.py createsuperuser

.PHONY: update
update: install migrate ;
