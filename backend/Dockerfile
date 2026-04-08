FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.5

COPY pyproject.toml README.md* /app/
COPY backend /app/backend

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with dev

ENV PYTHONPATH=/app/backend/src

WORKDIR /app/backend
