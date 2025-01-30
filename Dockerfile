FROM python:3.11-slim

LABEL maintainer="nikpash"

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install dependencies
RUN python -m venv /py && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && python -m venv /py \
    && pip install --upgrade pip \
    && pip install poetry \
    flake8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock .flake8 /app/

RUN poetry install --no-root

WORKDIR /app/backend

EXPOSE 8000

RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

USER django-user
