#!/usr/bin/env bash
set -e

echo "⏳ Waiting for PostgreSQL…"
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -q; do
  sleep 1
done
echo "✅ PostgreSQL is ready."

echo "📦 Running migrations…"
uv run python manage.py migrate --noinput

echo "🌱 Seeding demo data (skips if already seeded)…"
uv run python manage.py zerar_apresentacao --noinput --skip-if-seeded

echo "📂 Collecting static files…"
uv run python manage.py collectstatic --noinput

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              🧪  Lab Management — Demo Ready  🧪           ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║   URL:   http://localhost:8000                              ║"
echo "║                                                            ║"
echo "║   Demo Users (password: SenhaSegura123!)                   ║"
echo "║   ├── admin@lab.test       (Admin)                         ║"
echo "║   ├── gestor@lab.test      (Gestor)                        ║"
echo "║   ├── almox@lab.test       (Almoxarife)                    ║"
echo "║   └── aluno@lab.test       (Solicitante)                   ║"
echo "║                                                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

exec uv run python manage.py runserver 0.0.0.0:8000
