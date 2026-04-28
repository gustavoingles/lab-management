# lab-management

Sistema para controle de estoque e manutenção de equipamentos de laboratório (backend Django).

**O que já existe neste repositório:**

- **Modelo relacional (DDL):** [database/postgresql_schema.sql](database/postgresql_schema.sql)
- **Documentação da modelagem:** [docs/modelagem-postgresql.md](docs/modelagem-postgresql.md)
- **Regra de prática TDD:** [.agents/skills/always-tdd/SKILL.md](.agents/skills/always-tdd/SKILL.md)

**Resumo rápido:** o schema PostgreSQL foi modelado e incluído em `database/postgresql_schema.sql`. Ele pode ser aplicado manualmente em um servidor PostgreSQL local antes de executar as migrações Django.

**Pré-requisitos**

- Python 3.14
- PostgreSQL (compatível com a versão instalada localmente)
- `uv` (gerenciador de dependências e runner usado no projeto)

**Setup local (passo a passo mínimo)**

1. Clonar o repositório

```bash
git clone <repo-url>
cd lab-management
```

2. Instalar dependências

```bash
uv sync
```

3. Criar o arquivo `.env` com as variáveis necessárias (exemplo):

```env
SECRET_KEY=troque_por_uma_chave_secreta
DEBUG=True
DATABASE_URL=postgres://postgres:senha@localhost:5432/lab_management
```

Observação: se seu banco tem outro nome (por exemplo `lab-management` com hífen), ajuste `DATABASE_URL` conforme necessário.

4. (Opcional) Aplicar o schema SQL direto no banco — útil para provisionar todas as tabelas e índices descritos na modelagem:

```bash
psql "postgres://<usuario>:<senha>@<host>:<porta>/<dbname>" -f database/postgresql_schema.sql
```

5. Executar as migrações Django (garante migrações das apps e do Django):

```bash
uv run python manage.py migrate
```

6. Criar superusuário e rodar o servidor de desenvolvimento:

```bash
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

**Arquivos importantes**

- **DDL do banco:** [database/postgresql_schema.sql](database/postgresql_schema.sql)
- **Modelagem e documentação:** [docs/modelagem-postgresql.md](docs/modelagem-postgresql.md)
- **Política TDD (skill):** [.agents/skills/always-tdd/SKILL.md](.agents/skills/always-tdd/SKILL.md)

Se quiser, eu posso também:

- Gerar um arquivo `.env.example` com os valores de template
- Dividir as alterações recentes em commits atômicos com mensagens em Português (prévia das mensagens antes de aplicar)

Quer que eu já gere o `.env.example` e prepare os commits atômicos agora?

--
Atualizado em 28 de abril de 2026
