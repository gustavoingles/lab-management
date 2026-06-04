# lab-management

Sistema para controle de estoque e manutenção de equipamentos de laboratório (backend Django + API REST).

## O que existe hoje

| Módulo | Status |
|--------|--------|
| Autenticação (web + JWT) | Cadastro, login, app `/app/`, API `/api/v1/auth/` |
| Autorização por perfil | Leitura/escrita por papel nas APIs de domínio |
| Catálogo (Sem. 4) | Categorias, unidades, localizações, itens, equipamentos |
| Estoque (Sem. 5–6) | Estoques, lotes, movimentações, alertas de nível |
| Requisições (Sem. 7) | CRUD, aprovar (reserva estoque), rejeitar, atender itens |
| Reservas de equipamento | Agenda com aprovação do gestor e bloqueio de conflito |
| Ordens de serviço (Sem. 8–10) | OS, manutenções, iniciar/encerrar, status do equipamento |
| Inventário e baixas (Sem. 11–12) | CRUD + auditoria consultável |
| Interface web (templates) | Dashboard, CRUD e fluxos em `/app/` (mesmo CSS do site) |
| Front Next.js (Sem. 3) | Opcional — API já disponível |

**Documentação completa da API:** [docs/guia-backend-api.md](docs/guia-backend-api.md) (passo a passo, todos os endpoints, perfis e exemplos).

**Guia de apresentação ao cliente:** [docs/guia-apresentacao-cliente.md](docs/guia-apresentacao-cliente.md) (telas, dependências, roteiro de demo).

Referências: [database/postgresql_schema.sql](database/postgresql_schema.sql), [docs/modelagem-postgresql.md](docs/modelagem-postgresql.md), [.github/copilot-instructions.md](.github/copilot-instructions.md).

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .   # ou: uv sync

# .env: SECRET_KEY, DEBUG, DATABASE_URL
docker compose up -d   # opcional

python manage.py reset_schema   # só se banco vazio/conflito; confirme: sim
python manage.py migrate
python manage.py bootstrap_admin --email admin@lab.test --nome Admin --password 'SenhaSegura123!'
python manage.py runserver
```

## Interface web (`/app/`)

Depois do login você entra em **`http://127.0.0.1:8000/app/`** — menu lateral, tabelas e formulários no mesmo estilo da landing (Tailwind).

- **Solicitante:** requisições, consulta de itens/estoque  
- **Almoxarife:** catálogo, movimentações, atender requisições  
- **Gestor/Admin:** aprovar requisições, usuários, auditoria  

Recompilar estilos após editar templates: `npm install && npm run build:css`

## API

### Auth — `/api/v1/auth/`

| Método | URL | Descrição |
|--------|-----|-----------|
| POST | `register/` | Cadastro (perfil `solicitante`) |
| POST | `token/` | Login JWT (`email`, `password`) |
| POST | `token/refresh/` | Renovar token |
| GET | `me/` | Usuário autenticado |
| GET | `perfis/` | Lista perfis (admin, gestor) |
| GET/PATCH | `usuarios/`, `usuarios/{id}/` | Gestão de usuários e perfis (admin, gestor) |

### Domínio — `/api/v1/` (header `Authorization: Bearer <token>`)

| Recurso | Endpoints extras |
|---------|------------------|
| `categorias`, `unidades-medida`, `localizacoes`, `itens`, `equipamentos` | CRUD (escrita: admin, gestor, almoxarife) |
| `estoques` | GET; `GET estoques/alertas/` — abaixo do nível de alerta |
| `lotes`, `movimentacoes` | POST movimentação dispara regras de estoque |
| `requisicoes` | `POST .../aprovar/`, `POST .../rejeitar/` (gestor/admin) |
| `requisicao-itens` | `POST .../atender/` (almoxarife+) |
| `ordens-servico` | `POST .../iniciar/`, `POST .../encerrar/` |
| `manutencoes`, `inventarios`, `inventario-itens`, `baixas` | CRUD conforme perfil |
| `auditorias` | Somente leitura (gestor, admin, auditor, fiscal) |

Filtros úteis: `GET /api/v1/itens/?tipo_item=reagente&ativo=true`, `GET /api/v1/equipamentos/?status_operacional=ativo`.

### Perfis (seed)

`solicitante`, `admin`, `gestor`, `almoxarife`, `tecnico_lab`, `tecnico_manutencao`, `auditor`, `fiscal`.

## Testes

```bash
python manage.py test accounts inventory
```

## Próximo passo (cronograma)

- App **Next.js** (Sem. 3) apontando para esta API
- Relatórios/exportação de auditoria
- CI/CD e deploy (DevOps)
