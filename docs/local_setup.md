# Local Development Guide

This document explains how to run the AI Influencer Platform locally for development.

## Recommended Approach

The most reliable local path right now is Docker-based development for infrastructure plus Poetry for the backend and `npm` for the frontend.

Because this machine is using Microsoft Store Python 3.13, local Poetry installs may fail on some binary dependencies. If that happens, use one of these options:

1. install Python 3.12 from the official Python installer and recreate the Poetry environment
2. run the full stack through Docker

## Supported Local Platforms

This guide includes commands for:

- Windows with PowerShell
- macOS with `zsh` or `bash`
- Linux with `bash`

Notes:

- Docker commands are the same on all three platforms
- backend Python commands are the same once Python and Poetry are installed
- the main shell differences are file copy commands and interpreter path selection

## Stack Overview

Local development uses:

- PostgreSQL with `pgvector`
- Redis
- FastAPI backend
- Celery worker
- Celery beat scheduler
- React + Vite frontend

## Prerequisites

Install these first:

- Docker Desktop
- Python 3.12
- Poetry
- Node.js 22+
- npm

Optional but recommended:

- Git
- pgAdmin or TablePlus
- RedisInsight

### OS-specific install notes

#### Windows

- install Python 3.12 from [python.org](https://www.python.org/downloads/)
- avoid Microsoft Store Python for this project if possible
- install Node.js LTS from [nodejs.org](https://nodejs.org/)
- install Docker Desktop

#### macOS

- install Homebrew if not already installed
- install Python 3.12 with `brew install python@3.12`
- install Node.js with `brew install node`
- install Docker Desktop

#### Linux

- install Python 3.12 using your distro package manager or `pyenv`
- install Node.js 22+ using your distro package manager, NodeSource, or `nvm`
- install Docker Engine and Docker Compose plugin

## Shell Conventions Used Below

When a command differs by platform, this document shows separate blocks for:

- `Windows (PowerShell)`
- `macOS / Linux`

## 1. Clone the Repository

```powershell
git clone https://github.com/ai-influencer-vibe/ai-influencer.git
cd ai-influencer
```

## 2. Create Local Environment File

Copy the example environment file:

Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

You can keep the defaults for local development initially.

Important variables:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `REDIS_HOST`
- `REDIS_PORT`
- `API_V1_PREFIX`

## 3. Start Infrastructure

Start Postgres and Redis first:

```bash
docker compose up -d postgres redis
```

Check status:

```bash
docker compose ps
```

## 4. Backend Setup

### Option A: Preferred local Python workflow

Use Python 3.12 and Poetry:

Windows (PowerShell):

```powershell
py -3.12 -m poetry env use 3.12
poetry install
```

macOS / Linux:

```bash
poetry env use python3.12
poetry install
```

Run the API:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend/src
```

Run the worker:

```bash
poetry run celery -A app.workers.celery_app.celery_app worker --loglevel=INFO
```

Run the scheduler:

```bash
poetry run celery -A app.workers.celery_app.celery_app beat --loglevel=INFO
```

### Option B: Docker backend workflow

If your local Python environment is unstable, run the backend services in Docker:

```bash
docker compose up --build api worker beat
```

## 5. Run Database Migrations

Once the backend environment is available, apply migrations:

```bash
poetry run alembic -c backend/alembic.ini upgrade head
```

If using Docker:

```bash
docker compose run --rm api alembic -c backend/alembic.ini upgrade head
```

## 6. Frontend Setup

Install frontend dependencies:

Windows (PowerShell):

```powershell
cd frontend
npm install
npm run dev
```

macOS / Linux:

```bash
cd frontend
npm install
npm run dev
```

The Vite frontend will run on:

- `http://localhost:5173`

The API will run on:

- `http://localhost:8000`

## 7. Full Docker Workflow

To bring up everything with Docker:

```bash
docker compose up --build
```

Services:

- frontend: `http://localhost:5173`
- backend API: `http://localhost:8000`
- postgres: `localhost:5432`
- redis: `localhost:6379`

## 8. Run Tests

Backend tests:

```bash
poetry run pytest
```

If you only want a subset:

```bash
poetry run pytest backend/tests/test_health.py
poetry run pytest backend/tests/test_influencer_service.py
poetry run pytest backend/tests/test_memory_service.py
```

## 9. Useful Development Commands

Format and lint:

```bash
poetry run ruff check .
poetry run mypy backend/src
```

List running containers:

```bash
docker compose ps
```

Stop the stack:

```bash
docker compose down
```

Stop the stack and remove volumes:

```bash
docker compose down -v
```

## 10. Platform-Specific Quick Starts

### Windows Quick Start

1. Install Python 3.12, Node.js, Docker Desktop, and Poetry
2. `Copy-Item .env.example .env`
3. `docker compose up -d postgres redis`
4. `py -3.12 -m poetry env use 3.12`
5. `poetry install`
6. `poetry run alembic -c backend/alembic.ini upgrade head`
7. Start backend:
   `poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend/src`
8. Start frontend in another terminal:
   `cd frontend`
   `npm install`
   `npm run dev`

### macOS Quick Start

1. Install Homebrew, Python 3.12, Node.js, Docker Desktop, and Poetry
2. `cp .env.example .env`
3. `docker compose up -d postgres redis`
4. `poetry env use python3.12`
5. `poetry install`
6. `poetry run alembic -c backend/alembic.ini upgrade head`
7. Start backend:
   `poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend/src`
8. Start frontend in another terminal:
   `cd frontend && npm install && npm run dev`

### Linux Quick Start

1. Install Python 3.12, Node.js, Docker Engine, Docker Compose plugin, and Poetry
2. `cp .env.example .env`
3. `docker compose up -d postgres redis`
4. `poetry env use python3.12`
5. `poetry install`
6. `poetry run alembic -c backend/alembic.ini upgrade head`
7. Start backend:
   `poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend/src`
8. Start frontend in another terminal:
   `cd frontend && npm install && npm run dev`

## 11. Current Local Caveat

This repository currently targets Python 3.12 in `pyproject.toml`.

If you use Microsoft Store Python 3.13 on Windows, Poetry may fail while installing binary dependencies such as:

- `psycopg-binary`
- `numpy`

If that happens:

1. install official Python 3.12 from [python.org](https://www.python.org/downloads/)
2. run `poetry env use 3.12`
3. run `poetry install` again

## 12. First End-to-End Smoke Check

After services are running:

1. open `http://localhost:8000/api/v1/health/`
2. confirm you receive `{"status":"ok"}`
3. open `http://localhost:5173`
4. confirm the admin shell loads

## 13. Suggested Daily Workflow

1. `docker compose up -d postgres redis`
2. run backend locally with Poetry
3. run frontend with `npm run dev`
4. apply migrations when schema changes
5. run targeted tests before pushing
