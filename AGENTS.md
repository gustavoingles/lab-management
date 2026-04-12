# agents.md

This file provides guidance to AI coding agents when working with code in this repository.

## Dependency Management

This project uses **uv** for all dependency and environment management. Always use:

```bash
uv add <package>          # install and track a new dependency
uv run python manage.py   # run any Django management command
uv run django-admin       # run django-admin commands
uv sync                   # install all dependencies from lockfile
```

Never use `pip install` directly — it bypasses `pyproject.toml` and `uv.lock`.

## Common Commands

```bash
# Run development server
uv run python manage.py runserver

# Database migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Run tests
uv run python manage.py test

# Run a single test
uv run python manage.py test <app_label>.tests.<TestClass>.<test_method>

# Open Django shell
uv run python manage.py shell
```

## Environment Variables

Create a `.env` file at the project root (next to `manage.py`) before running anything. Required variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/lab_management
```

`settings.py` uses `django-environ` to read these. `DATABASE_URL` drives the database backend — PostgreSQL is the target database.

## Architecture

- `lab_management/` — Django project config package (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`)
- `manage.py` — Django CLI entry point
- `pyproject.toml` — single source of truth for dependencies and project metadata

The uv project root and Django project root are the same directory (`.` was used with `startproject`). New Django apps go at the root level alongside `manage.py` and are registered in `INSTALLED_APPS`.
