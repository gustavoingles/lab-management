# agents.md

This file provides guidance to AI coding agents when working with code in this repository.

## Dependency Management

This project uses **uv** when available. Always prefer:

```bash
uv add <package>          # install and track a new dependency
uv run python manage.py   # run any Django management command
uv sync                   # install all dependencies from lockfile
```

If `uv` is not installed, use a virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python manage.py <command>
```

Never use bare `pip install <package>` without updating `pyproject.toml`.

## Common Commands

```bash
# Run development server
uv run python manage.py runserver

# Database migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Reset DB schema (empty DB only, DEBUG=True)
uv run python manage.py reset_schema

# Create admin user (custom user model + perfil)
uv run python manage.py bootstrap_admin --email admin@lab.test --nome Admin --password 'secret'

# Run tests
uv run python manage.py test
uv run python manage.py test accounts.tests.AuthAPITestCase

# Open Django shell
uv run python manage.py shell
```

## Environment Variables

Create a `.env` file at the project root (next to `manage.py`):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://admin:123456@localhost:5432/banco-lab
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

`settings.py` uses `django-environ`. `DATABASE_URL` drives the PostgreSQL backend.

## Architecture

- `lab_management/` — project config (`settings.py`, `urls.py`, `forms.py`, `views.py`, `auth_backends.py`)
- `accounts/` — custom user (`Usuario`), profiles (`Perfil`), permissions (`permissions.py`), REST auth API
- `inventory/` — domain models, services (estoque, requisições, OS, auditoria), REST viewsets under `/api/v1/`
- `manage.py` — Django CLI entry point
- `pyproject.toml` / `uv.lock` — Python dependencies
- `database/postgresql_schema.sql` — domain DDL reference (Django migrations are source of truth at runtime)
- `docs/modelagem-postgresql.md` — domain modeling notes

New Django apps go at the repository root next to `manage.py` and are registered in `INSTALLED_APPS`.

## Authentication

- `AUTH_USER_MODEL = "accounts.Usuario"` — login field is `email`
- Web: templates under `templates/`, `EmailBackend` in `lab_management.auth_backends`
- API: DRF + SimpleJWT under `/api/v1/auth/` (register, token, refresh, me)
- Default profile on self-registration: `solicitante` (seeded in migration `0002_seed_perfis`)
- Domain tables live in `inventory` models with FK to `AUTH_USER_MODEL`
- Use `inventory.services` for stock movements and workflow actions (approve requisition, close work order)
- Permission classes: `accounts.permissions` (`CanManageCatalog`, `CanManageStock`, etc.)

## Testing

Follow TDD when adding features. Auth tests live in `accounts.tests`. Run:

```bash
uv run python manage.py test accounts
```
