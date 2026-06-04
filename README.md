# lab-management

Sistema para controle de estoque e manutenção de equipamentos de laboratório (backend Django).

## O que existe hoje

| Área | Status |
|------|--------|
| Autenticação (web) | Cadastro, login, logout, recuperação de senha |
| Autenticação (API) | Cadastro, JWT, perfil do usuário logado |
| Modelo de usuário | `accounts.Usuario` (e-mail) + `accounts.Perfil` |
| Domínio de estoque | DDL e documentação; modelos Django ainda não integrados |

Referências de modelagem:

- [database/postgresql_schema.sql](database/postgresql_schema.sql)
- [docs/modelagem-postgresql.md](docs/modelagem-postgresql.md)

## Requisitos

- Python 3.14+
- PostgreSQL (local ou [docker-compose.yml](docker-compose.yml))
- `uv` **ou** `venv` + `pip`

## Setup local

### 1. Clonar e entrar no projeto

```bash
git clone <repo-url>
cd lab-management
```

### 2. Dependências

Com **uv** (recomendado):

```bash
uv sync
```

Sem **uv** (alternativa):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### 3. Variáveis de ambiente

Crie `.env` na raiz do projeto:

```env
SECRET_KEY=troque-por-uma-chave-secreta
DEBUG=True
DATABASE_URL=postgres://admin:123456@localhost:5432/banco-lab
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Ajuste `DATABASE_URL` conforme seu Postgres. Com o Docker deste repositório, use usuário `admin`, senha `123456` e banco `banco-lab`.

### 4. Banco de dados (auth via Django)

Suba o Postgres, se usar Docker:

```bash
docker compose up -d
```

Aplique migrações:

```bash
# com uv
uv run python manage.py migrate

# ou com venv ativo
python manage.py migrate
```

Se o banco já tinha o DDL antigo ou migrações conflitantes **e não há dados a preservar**, reinicie o schema:

```bash
python manage.py reset_schema   # confirme com: sim
python manage.py migrate
```

Alternativa com `psql`:

```bash
psql "$DATABASE_URL" -f database/reset_schema.sql
python manage.py migrate
```

### 5. Usuário administrador

O modelo customizado exige perfil. Use:

```bash
python manage.py bootstrap_admin \
  --email admin@lab.test \
  --nome Administrador \
  --password 'SuaSenhaSegura123!'
```

### 6. Servidor e testes

```bash
python manage.py runserver
python manage.py test accounts
```

## API de autenticação (`/api/v1/auth/`)

| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `/api/v1/auth/register/` | Não | Cadastro (perfil padrão: `solicitante`) |
| POST | `/api/v1/auth/token/` | Não | Login — body: `{"email","password"}` |
| POST | `/api/v1/auth/token/refresh/` | Não | Renovar access token |
| GET | `/api/v1/auth/me/` | JWT | Dados do usuário logado |

Exemplo de cadastro:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Silva",
    "email": "maria@lab.test",
    "password": "SenhaSegura123!",
    "password_confirm": "SenhaSegura123!"
  }'
```

Exemplo de login:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"maria@lab.test","password":"SenhaSegura123!"}'
```

Use o `access` retornado:

```bash
curl http://127.0.0.1:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

## Cadastro web

- `/register/` — cria conta e redireciona para `/login/` (sem login automático)
- `/login/` — autenticação por e-mail e senha
- `/admin/` — painel Django

## Perfis cadastrados (seed)

Após `migrate`, estes perfis existem: `solicitante`, `admin`, `gestor`, `almoxarife`, `tecnico_lab`, `tecnico_manutencao`, `auditor`, `fiscal`.

Novos cadastros (API e web) recebem automaticamente o perfil `solicitante`.

## Estratégia de banco para o domínio (futuro)

- **Auth:** tabelas `accounts_perfil` e `accounts_usuario` — geridas pelo Django.
- **Estoque/inventário:** usar o DDL como referência; implementar modelos `managed=True` com FK para `AUTH_USER_MODEL`, sem reaplicar a tabela legada `usuarios` do SQL.

## Comandos úteis

```bash
python manage.py reset_schema      # limpa schema (DEBUG=True)
python manage.py bootstrap_admin   # cria superusuário
python manage.py test accounts     # testes de auth
```

## Dependências

Pacotes principais: Django, django-environ, psycopg, djangorestframework, djangorestframework-simplejwt, django-cors-headers.

Com uv, adicione pacotes com:

```bash
uv add <package-name>
```
