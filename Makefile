.PHONY: install
install:
	poetry install

.PHONY: migrate
migrate:
	poetry run python backend/manage.py migrate

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: migrations
migrations:
	poetry run python backend/manage.py makemigrations

.PHONY: runserver
runserver:
	poetry run python backend/manage.py runserver

.PHONY: superuser
superuser:
	poetry run python backend/manage.py createsuperuser

# Used by other developers to prepare the project.
.PHONY: update
update: install migrate install-pre-commit ;
