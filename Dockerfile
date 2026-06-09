# ── Stage 1: Build Tailwind CSS ──────────────────────────────────────
FROM node:22-alpine AS css-builder

WORKDIR /build

COPY package.json package-lock.json ./
RUN npm ci

# Tailwind needs the source templates to tree-shake classes
COPY static/css/input.css ./static/css/input.css
COPY templates/ ./templates/

RUN npx @tailwindcss/cli \
    -i ./static/css/input.css \
    -o ./static/css/styles.css \
    --minify


# ── Stage 2: Python / Django runtime ────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps for psycopg (libpq) and pg_isready (used by entrypoint)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install Python dependencies via uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy project source
COPY . .

# Overwrite CSS with the compiled output from stage 1
COPY --from=css-builder /build/static/css/styles.css ./static/css/styles.css

# Make entrypoint executable
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
