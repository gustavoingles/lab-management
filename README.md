# lab-management

A web application for managing laboratory resources, built with Django and managed with uv.

## Tech Stack

- **Python** 3.14
- **Django** 6.0.4
- **django-environ** — environment variable management via `.env`
- **psycopg** 3 — PostgreSQL adapter
- **uv** — project and dependency management

## Project Structure

```
lab-management/
├── lab_management/       # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── pyproject.toml        # Project metadata and dependencies
├── uv.lock               # Locked dependency versions
└── .env                  # Environment variables (not committed)
```

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd lab-management
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Copy the example below into a `.env` file at the project root (next to `manage.py`):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/lab_management
```

### 4. Apply migrations

```bash
uv run python manage.py migrate
```

### 5. Create a superuser

```bash
uv run python manage.py createsuperuser
```

### 6. Run the development server

```bash
uv run python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`. The admin interface is at `/admin/`.

## Adding Dependencies

This project uses `uv` for dependency management. Always use `uv add` to install new packages:

```bash
uv add <package-name>
```

This keeps `pyproject.toml` and `uv.lock` in sync automatically.
