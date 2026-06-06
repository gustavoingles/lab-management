FROM python:3.13-slim

WORKDIR /app

# Install uv from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies before copying source (cache-friendly layer order)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

# Strip Windows CRLF from entrypoint in case the file was written on Windows
RUN sed -i 's/\r$//' entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
