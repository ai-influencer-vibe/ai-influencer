# CI Guide

This repository uses GitHub Actions to run baseline automated checks on every relevant push and pull request.

## Workflows

### Backend CI

File:

- `.github/workflows/backend-ci.yml`

Runs when backend code or `pyproject.toml` changes.

Checks:

- `ruff` linting
- `mypy` type checking
- `pytest`
- coverage XML artifact upload

Environment:

- Ubuntu
- Python 3.12
- Poetry-managed dependencies

## Coverage

The backend workflow produces:

- terminal coverage output in the job logs
- `coverage.xml` uploaded as a GitHub Actions artifact

This gives us a durable coverage file even before integrating a service like Codecov.

### Frontend CI

File:

- `.github/workflows/frontend-ci.yml`

Runs when frontend code changes.

Checks:

- dependency installation
- production build with Vite

Environment:

- Ubuntu
- Node.js 22

## Why this setup

This project currently benefits most from:

- fast feedback on pull requests
- repeatable backend quality gates
- a lightweight frontend sanity check
- CI behavior that is more stable than local Windows Python packaging

## Future Enhancements

Recommended next improvements:

1. add a coverage threshold gate
2. add frontend linting and unit tests once the UI grows
3. add Postgres-backed integration tests for repository and migration validation
4. add Docker image build verification
