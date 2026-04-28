# lab-management

Sistema para controle de estoque e manutencao de equipamentos de laboratorio (backend Django).

**O que ja existe neste repositorio:**

- **Modelo relacional (DDL):** [database/postgresql_schema.sql](database/postgresql_schema.sql)
- **Documentacao da modelagem:** [docs/modelagem-postgresql.md](docs/modelagem-postgresql.md)

## Requisitos

- Python 3.14
- PostgreSQL (compatível com a versao instalada localmente)
- `uv` (gerenciador de dependencias e runner usado no projeto)

## Setup local

1. Clonar o repositorio

```bash
git clone <repo-url>
cd lab-management
```

2. Instalar dependencias

```bash
uv sync
```

3. Criar o arquivo `.env` com as variaveis necessarias (exemplo):

```env
SECRET_KEY=troque_por_uma_chave_secreta
DEBUG=True
DATABASE_URL=postgres://postgres:senha@localhost:5432/lab_management
```

Observacao: se seu banco tem outro nome (por exemplo `lab-management` com hifen), ajuste `DATABASE_URL` conforme necessario.

4. Escolha uma das estrategias de banco abaixo.

### Estrategia A (Django gerencia o schema)

Use apenas migracoes Django para criar as tabelas.

```bash
uv run python manage.py migrate
```

### Estrategia B (DDL aplicado manualmente)

Se voce aplicar o DDL manualmente, deixe essas tabelas fora do controle do Django (use `managed = False` nos modelos correspondentes) ou use um baseline com `--fake-initial` quando aplicavel.

```bash
psql "postgres://<usuario>:<senha>@<host>:<porta>/<dbname>" -f database/postgresql_schema.sql
```

5. Criar superusuario e rodar o servidor de desenvolvimento:

```bash
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Dependencias

Este projeto usa `uv` para gerenciar dependencias. Sempre use `uv add` ao instalar novos pacotes:

```bash
uv add <package-name>
```
