#!/bin/sh
set -e

service cron start

poetry run python manage.py crontab add

exec "$@"
