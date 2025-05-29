# Charity Donation API

A Django REST API for managing charity campaigns and donations while providing donors with transparency and ease of contribution.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Environment Setup](#environment-setup)
  - [Local Development](#local-development)
  - [Docker Setup](#docker-setup)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Makefile Commands](#makefile-commands)
- [Testing](#testing)
- [Contributing](#contributing)

## Overview

The Charity Donation API provides a platform for creating and managing charity campaigns, allowing users to make donations while ensuring transparency throughout the process. The system manages user accounts, campaign details, document verification, and the donation process.

## Features

- User authentication and profile management
- Campaign creation and management with moderation workflow
- Document upload for campaign verification
- Secure donation processing
- Balance management for users
- Comprehensive API documentation with Swagger UI
- Containerized deployment using Docker

## Prerequisites

- Python 3.11+
- Poetry (Python package manager)
- PostgreSQL (or Docker for containerized database)
- Docker and Docker Compose (for containerized setup)

## Installation

### Environment Setup

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY = your_secret_key_here

DJANGO_ENV='development'/'production'

DB_HOST='db'
DB_NAME='db_name'
DB_USER='user'
DB_PASS='password'

REDIS_HOST=redis
REDIS_PORT=6379

```

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/charity-donation-api.git
   cd charity-donation-api
   ```

2. Install dependencies using Poetry for local development:
   ```
   poetry install
   ```

### Docker Setup

1. Build and start the Docker containers:
   ```
   docker-compose up -d --build
   ```

2. The API will be available at http://localhost:8000/api/docs

## Project Structure

```
charity-donation-api/
├── backend/               # Main Django project
│   ├── campaign/          # Campaign management app
│   ├── core/              # Core settings and configuration
│   ├── donation/          # Donation processing app
│   ├── main_app/          # Shared utilities
│   ├── user/              # User management app
│   └── manage.py          # Django management script
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker container configuration
├── Makefile               # Automation scripts
├── poetry.lock            # Poetry dependency lock file
├── pyproject.toml         # Poetry project configuration
└── README.md              # Project documentation
```

## API Endpoints

After running the server, visit the Swagger documentation at:
- http://localhost:8000/api/docs/

Key endpoints include:
- `/api/users/` - User management
- `/api/campaigns/` - Campaign management
- `/api/donations/` - Donation processing

## Makefile Commands

The project includes a Makefile for common development tasks:

- `make help` - Show available commands
- `make migrate` - Apply database migrations
- `make migrations` - Generate new migration files
- `make full-migration` - Run migrations and generate new migrations
- `make superuser` - Create a Django superuser interactively
- `make create-app N` - Start a new Django app named N
- `make lint` - Run pre-commit hooks on all files
- `make docker-lint` - Run flake8 inside the Docker container
- `make test` - Execute the full test suite
- `make rebuild` - Rebuild Docker containers from scratch
- `make commit` - Run migrations, lint and tests before commit

Example:
```
make up      # Start the application
make test    # Run the test suite
```

## Testing

Run the tests using the following command:

```
make test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
