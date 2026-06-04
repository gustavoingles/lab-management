-- Use apenas se o banco NÃO tiver dados a preservar.
-- Necessário quando o DDL completo foi aplicado antes das migrações Django de auth.
-- Depois execute: uv run python manage.py migrate

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;
GRANT ALL ON SCHEMA public TO CURRENT_USER;
