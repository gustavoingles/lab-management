# Guia passo a passo — Backend LabManager

Este documento explica como o backend Django funciona, como autenticar, usar cada endpoint e quais perfis podem fazer o quê.

**Base URL local:** `http://127.0.0.1:8000`

---

## 1. Visão geral da arquitetura

```text
Cliente (navegador, Postman, Next.js)
        │
        ▼
┌───────────────────────────────────────┐
│  Django + Django REST Framework       │
│  • Templates web: /login, /register   │
│  • API JSON: /api/v1/...              │
│  • JWT (SimpleJWT)                    │
└───────────────────────────────────────┘
        │
        ▼
   PostgreSQL
```

| Pacote | Função |
|--------|--------|
| `accounts` | Usuários (`Usuario`), perfis (`Perfil`), autenticação JWT, gestão de usuários |
| `inventory` | Domínio: itens, estoque, requisições, OS, inventário, auditoria |
| `lab_management` | Configuração, URLs globais, formulários web |

O banco é criado pelas **migrações Django** (`python manage.py migrate`), não pelo DDL manual (o arquivo `database/postgresql_schema.sql` serve de referência).

---

## 2. Preparar o ambiente (primeira vez)

### 2.1 Variáveis de ambiente

Crie `.env` na raiz do projeto:

```env
SECRET_KEY=uma-chave-secreta-longa
DEBUG=True
DATABASE_URL=postgres://admin:123456@localhost:5432/banco-lab
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 2.2 Subir o banco e migrar

```bash
docker compose up -d          # Postgres, se usar Docker do projeto
source .venv/bin/activate
pip install -e .
python manage.py migrate
```

Se o banco estiver inconsistente e **sem dados importantes**:

```bash
python manage.py reset_schema   # digite: sim
python manage.py migrate
```

### 2.3 Criar o primeiro administrador

```bash
python manage.py bootstrap_admin \
  --email admin@lab.test \
  --nome "Administrador" \
  --password 'SuaSenhaSegura123!'
```

Isso cria usuário com **perfil `admin`** e permissões de superusuário Django (`/admin/`).

### 2.4 Rodar o servidor

```bash
python manage.py runserver
```

---

## 3. Perfis de usuário

Após `migrate`, existem estes perfis (tabela `accounts_perfil`):

| Código | Nome | Papel resumido |
|--------|------|----------------|
| `solicitante` | Solicitante | Abre requisições de material |
| `tecnico_lab` | Técnico de Laboratório | Opera lab; também pode requisitar |
| `almoxarife` | Almoxarife | Estoque, movimentações, cadastros operacionais |
| `gestor` | Gestor | Aprova requisições; **gerencia usuários** (exceto promover a admin) |
| `admin` | Administrador | Tudo na API + pode atribuir perfil **admin** |
| `tecnico_manutencao` | Técnico de Manutenção | Ordens de serviço |
| `auditor` | Auditor | Leitura de auditoria |
| `fiscal` | Fiscal | Leitura de auditoria |

**Cadastro público** (`/register/` ou `POST /api/v1/auth/register/`) sempre cria perfil **`solicitante`**.

**Superusuário Django** (`is_superuser`): ignora checagens de perfil na API e acessa `/admin/`.

---

## 4. Autenticação na API (JWT)

### 4.1 Obter token (login)

```http
POST /api/v1/auth/token/
Content-Type: application/json

{
  "email": "admin@lab.test",
  "password": "SuaSenhaSegura123!"
}
```

**Resposta (200):**

```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

- **access** — envie em todas as requisições protegidas (vida útil ~60 min).
- **refresh** — use para renovar o access sem login de novo.

### 4.2 Usar o token

```http
GET /api/v1/auth/me/
Authorization: Bearer eyJ...
```

### 4.3 Renovar access

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{ "refresh": "eyJ..." }
```

### 4.4 Cadastro (sem token)

```http
POST /api/v1/auth/register/
Content-Type: application/json

{
  "nome": "Maria Silva",
  "email": "maria@lab.test",
  "password": "SenhaSegura123!",
  "password_confirm": "SenhaSegura123!",
  "matricula": "2026001",
  "cargo": "Estudante"
}
```

Perfil atribuído automaticamente: **`solicitante`**.

### 4.5 Quem sou eu

```http
GET /api/v1/auth/me/
Authorization: Bearer ...
```

---

## 5. Gestão de usuários (admin / gestor)

Apenas perfis **`admin`** e **`gestor`** acessam estes endpoints.

### 5.1 Listar perfis disponíveis (para dropdown)

```http
GET /api/v1/auth/perfis/
Authorization: Bearer ...
```

### 5.2 Listar usuários

```http
GET /api/v1/auth/usuarios/
Authorization: Bearer ...
```

Query opcional:

- `?perfil=solicitante`
- `?ativo=true`

### 5.3 Ver um usuário

```http
GET /api/v1/auth/usuarios/3/
Authorization: Bearer ...
```

### 5.4 Alterar perfil e dados (PATCH)

```http
PATCH /api/v1/auth/usuarios/3/
Authorization: Bearer ...
Content-Type: application/json

{
  "perfil_id": 4,
  "nome": "Maria Silva",
  "cargo": "Almoxarife",
  "matricula": "2026001",
  "is_active": true
}
```

Use `perfil_id` retornado em `GET /api/v1/auth/perfis/`.

**Regras:**

| Ação | Quem pode |
|------|-----------|
| Promover alguém a **`admin`** | Só usuário com perfil **`admin`** |
| Alterar usuário que já é **`admin`** | Só **`admin`** |
| Promover para gestor, almoxarife, solicitante, etc. | **`admin`** ou **`gestor`** |
| Desativar conta (`is_active: false`) | **`admin`** ou **`gestor`** (não a própria conta) |
| Elevar o **próprio** perfil para gestão/admin | Bloqueado (exceto superusuário) |

**Exemplo:** gestor pode tornar um solicitante em almoxarife; gestor **não** pode tornar ninguém em admin.

### 5.5 Solicitar troca de perfil (fluxo do solicitante)

Qualquer usuário autenticado pode pedir alteração de perfil. A análise é feita por **gestor** ou **admin** (mesmas regras do PATCH direto: só **admin** aprova destino `admin`).

```http
GET /api/v1/auth/perfis-disponiveis/
Authorization: Bearer ...
```

Lista perfis ativos **exceto** o perfil atual do usuário.

```http
POST /api/v1/auth/solicitacoes-perfil/
Authorization: Bearer ...
Content-Type: application/json

{
  "perfil_id": 4,
  "justificativa": "Passo a atuar no almoxarifado do laboratório."
}
```

- Apenas **uma** solicitação **pendente** por usuário.
- `GET /api/v1/auth/solicitacoes-perfil/` — o solicitante vê as suas; gestor/admin vê todas (`?status=pendente` opcional).
- `POST .../solicitacoes-perfil/{id}/aprovar/` — gestor/admin (gestor não aprova destino `admin`).
- `POST .../solicitacoes-perfil/{id}/rejeitar/` — gestor/admin.
- `POST .../solicitacoes-perfil/{id}/cancelar/` — apenas o solicitante, se ainda pendente.

**Interface web:** `/app/meu-perfil/solicitacao/` (solicitante) e `/app/solicitacoes-perfil/` (gestão).

---

## 6. Convenções da API de domínio

- **Prefixo:** `/api/v1/`
- **Formato:** JSON
- **Autenticação:** `Authorization: Bearer <access>` (exceto register e token)
- **CRUD padrão (ViewSet):**

| Método | URL | Ação |
|--------|-----|------|
| GET | `/recurso/` | Listar |
| POST | `/recurso/` | Criar |
| GET | `/recurso/{id}/` | Detalhe |
| PUT/PATCH | `/recurso/{id}/` | Atualizar |
| DELETE | `/recurso/{id}/` | Excluir |

Respostas de erro comuns: `401` (sem token), `403` (perfil sem permissão), `400` (validação).

---

## 7. Matriz de permissões (resumo)

Legenda: **L** = leitura (GET), **E** = escrita (POST/PATCH/DELETE), **—** = sem acesso.

| Recurso / ação | solicitante | tecnico_lab | almoxarife | gestor | admin | tecnico_manut. | auditor/fiscal |
|----------------|:-----------:|:-----------:|:----------:|:------:|:-----:|:--------------:|:--------------:|
| Auth register/token | ✓ público | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Gestão usuários | — | — | — | E | E | — | — |
| Solicitar troca de perfil | E (criar/cancelar) | E | E | E (revisar) | E | E | E |
| Catálogo (categorias, itens, …) | L | L | E | E | E | L | L |
| Estoque, lotes, movimentações | L | L | E | E | E | L | L |
| Requisições (criar) | E | E | E | E | E | — | — |
| Requisições aprovar/rejeitar | — | — | — | E | E | — | — |
| Atender item requisição | — | — | E | E | E | — | — |
| Ordens de serviço | L | L | L | E | E | E | L |
| Inventário / baixas | L | L | E | E | E | L | L |
| Auditorias (só leitura) | — | — | — | L | L | — | L |

---

## 8. Endpoints — Autenticação (`/api/v1/auth/`)

| Método | URL | Auth | Descrição |
|--------|-----|------|-----------|
| POST | `register/` | Não | Cria conta (perfil `solicitante`) |
| POST | `token/` | Não | Login → JWT |
| POST | `token/refresh/` | Não | Renova access |
| GET | `me/` | Sim | Dados do usuário logado |
| GET | `perfis/` | admin, gestor | Lista perfis ativos |
| GET | `usuarios/` | admin, gestor | Lista usuários |
| GET | `usuarios/{id}/` | admin, gestor | Detalhe usuário |
| PATCH | `usuarios/{id}/` | admin, gestor | Atualiza perfil/dados (regras §5) |
| GET | `perfis-disponiveis/` | Sim | Perfis que o usuário pode solicitar |
| GET/POST | `solicitacoes-perfil/` | Sim | Lista / cria solicitação de perfil |
| POST | `solicitacoes-perfil/{id}/aprovar/` | admin, gestor | Aprova e aplica novo perfil |
| POST | `solicitacoes-perfil/{id}/rejeitar/` | admin, gestor | Rejeita solicitação |
| POST | `solicitacoes-perfil/{id}/cancelar/` | Solicitante (dono) | Cancela pendente |

---

## 9. Endpoints — Catálogo

### 9.1 Categorias — `/api/v1/categorias/`

Classificação de itens (equipamento, consumível, etc.).

**Campos:** `codigo`, `nome`, `descricao`, `ativa`

**Quem escreve:** admin, gestor, almoxarife

```bash
curl -X POST http://127.0.0.1:8000/api/v1/categorias/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"codigo":"REAG","nome":"Reagentes","ativa":true}'
```

### 9.2 Unidades de medida — `/api/v1/unidades-medida/`

**Campos:** `nome`, `sigla`, `permite_fracionamento`

### 9.3 Localizações — `/api/v1/localizacoes/`

Hierarquia: campus → prédio → laboratório → armário → posição.

**Campos:** `nome`, `codigo`, `tipo`, `localizacao_pai` (id ou null), `ativa`

**`tipo`:** `campus`, `predio`, `laboratorio`, `armario`, `posicao`

### 9.4 Itens — `/api/v1/itens/`

Núcleo do cadastro de materiais/equipamentos.

**Campos:** `codigo_interno`, `nome`, `descricao`, `categoria`, `unidade_medida`, `tipo_item`, `controlado`, `ativo`

**`tipo_item`:** `equipamento`, `consumivel`, `reagente`, `epi`, `peca`

**Filtros:** `?tipo_item=reagente&ativo=true`

### 9.5 Equipamentos — `/api/v1/equipamentos/`

Extensão 1:1 de item com `tipo_item=equipamento`.

**Campos:** `item` (id), `numero_serie`, `tombamento`, `marca`, `modelo`, `status_operacional`, `data_aquisicao`

**`status_operacional`:** `ativo`, `em_manutencao`, `inativo`, `descartado`

**Filtro:** `?status_operacional=ativo`

---

## 10. Endpoints — Estoque

### 10.1 Estoques — `/api/v1/estoques/` (somente leitura)

Saldo por item + localização. Campos incluem `quantidade_disponivel`, `nivel_minimo`, `nivel_alerta`.

**Alerta de reposição:**

```http
GET /api/v1/estoques/alertas/
Authorization: Bearer ...
```

Retorna registros em que `quantidade_disponivel <= nivel_alerta`.

### 10.2 Lotes — `/api/v1/lotes/`

Controle por lote e validade (FEFO).

**Campos:** `item`, `codigo_lote`, `fabricante`, `data_fabricacao`, `data_validade`, `quantidade_disponivel`

**Filtro:** `?item=1`

### 10.3 Movimentações — `/api/v1/movimentacoes/`

Registra entrada, saída, transferência ou ajuste e **atualiza estoque** (e lote, se informado).

**Somente POST e GET** (não edita movimentação antiga).

```http
POST /api/v1/movimentacoes/
Content-Type: application/json
Authorization: Bearer ...

{
  "item_id": 1,
  "tipo_movimentacao": "entrada",
  "quantidade": "50.000",
  "localizacao_destino_id": 2,
  "motivo": "Compra inicial"
}
```

| tipo_movimentacao | Obrigatório |
|-------------------|-------------|
| `entrada` | `localizacao_destino_id` |
| `saida` | `localizacao_origem_id` |
| `transferencia` | origem e destino |
| `ajuste` | `localizacao_destino_id` (define saldo absoluto) |

Opcional: `lote_id`, `observacao`

---

## 11. Endpoints — Requisições internas

### 11.1 Requisições — `/api/v1/requisicoes/`

**Criar (solicitante+):**

```json
{
  "finalidade": "Aula prática de química",
  "prioridade": "media",
  "justificativa": "Turma B"
}
```

O `solicitante` é o usuário logado.

**Status:** `rascunho`, `aberta`, `em_aprovacao`, `aprovada`, `rejeitada`, `atendida`, `cancelada`

**Ações extras (gestor/admin):**

```http
POST /api/v1/requisicoes/{id}/aprovar/
POST /api/v1/requisicoes/{id}/rejeitar/
Content-Type: application/json

{ "motivo": "Estoque insuficiente" }
```

### 11.2 Itens da requisição — `/api/v1/requisicao-itens/`

```json
{
  "requisicao": 1,
  "item": 3,
  "quantidade_solicitada": "2.500",
  "lote_sugerido": null
}
```

**Atender (almoxarife+, após aprovação):**

```http
POST /api/v1/requisicao-itens/{id}/atender/
Content-Type: application/json

{
  "localizacao_origem_id": 2,
  "lote_id": 1
}
```

Gera movimentação de **saída** e pode marcar requisição como `atendida` quando todos os itens forem atendidos.

---

## 12. Endpoints — Manutenção

### 12.1 Ordens de serviço — `/api/v1/ordens-servico/`

```json
{
  "equipamento": 1,
  "descricao_problema": "Não liga",
  "prioridade": "alta"
}
```

**Ações:**

```http
POST /api/v1/ordens-servico/{id}/iniciar/
```

Coloca OS em execução e equipamento em `em_manutencao`.

```http
POST /api/v1/ordens-servico/{id}/encerrar/
Content-Type: application/json

{
  "laudo_emitido": true,
  "status_equipamento": "ativo"
}
```

### 12.2 Manutenções — `/api/v1/manutencoes/`

Registros ligados à OS: `tipo_manutencao` (`preventiva`, `corretiva`, `calibracao`, …), `descricao`, `resultado`, `custo_estimado`, `proximo_vencimento`.

---

## 13. Endpoints — Inventário e baixas

### 13.1 Inventários — `/api/v1/inventarios/`

Contagem periódica: `nome`, `descricao`, `responsavel`, `status` (`aberto`, `em_andamento`, `encerrado`, `cancelado`).

### 13.2 Itens do inventário — `/api/v1/inventario-itens/`

`quantidade_sistema`, `quantidade_contada`, `diferenca` (calculada automaticamente).

### 13.3 Baixas — `/api/v1/baixas/`

Descarte, perda, obsolescência: `item` ou `equipamento`, `tipo_baixa`, `motivo`, `destino_final`, `documento_referencia`.

---

## 14. Endpoints — Auditoria

### `/api/v1/auditorias/` (somente GET)

Registro automático de ações importantes (criar item, movimentar estoque, aprovar requisição, etc.).

**Quem lê:** admin, gestor, auditor, fiscal

**Campos:** `usuario`, `acao`, `entidade`, `entidade_id`, `detalhes` (JSON), `ip_origem`, `created_at`

---

## 15. Interface web (templates Django)

A aplicação web usa o **mesmo CSS** da landing (`static/css/styles.css`) e autenticação por **sessão** (cookie), não JWT.

| URL | Descrição |
|-----|-----------|
| `/` | Landing page |
| `/login/` | Login → redireciona para `/app/` |
| `/register/` | Cadastro → redireciona para `/login/` |
| `/app/` | Dashboard (resumo, atalhos) |
| `/app/itens/`, `/app/categorias/`, … | Catálogo |
| `/app/estoques/`, `/app/movimentacoes/nova/` | Estoque |
| `/app/requisicoes/` | Requisições (detalhe com aprovar/atender) |
| `/app/ordens-servico/` | Ordens de serviço |
| `/app/usuarios/` | Editar perfil de usuários (admin/gestor) |
| `/app/auditoria/` | Log de auditoria |
| `/admin/` | Django Admin (superusuário) |

O menu lateral exibe apenas links permitidos ao **perfil** do usuário logado.

A API REST permanece disponível para integrações (Postman, mobile, Next.js futuro).

---

## 16. Fluxo completo de exemplo

1. **Admin** faz login → recebe JWT.
2. **Admin** promove Maria para almoxarife: `PATCH /api/v1/auth/usuarios/{id}/` com `perfil_id` do almoxarife.
3. **Almoxarife** cadastra categoria, localização, item, equipamento.
4. **Almoxarife** registra entrada: `POST /api/v1/movimentacoes/` tipo `entrada`.
5. **Solicitante** cria requisição + itens.
6. **Gestor** `POST .../requisicoes/1/aprovar/`.
7. **Almoxarife** `POST .../requisicao-itens/1/atender/`.
8. **Gestor** consulta `GET /api/v1/auditorias/`.

---

## 17. Testes automatizados

```bash
python manage.py test accounts inventory
```

---

## 18. Referências no repositório

- [README.md](../README.md) — setup rápido
- [AGENTS.md](../AGENTS.md) — orientação para ferramentas de IA
- [modelagem-postgresql.md](modelagem-postgresql.md) — modelo de dados
- [.github/copilot-instructions.md](../.github/copilot-instructions.md) — contexto acadêmico do projeto

---

## 19. O que ainda não está no backend

- Front **Next.js** (consumo visual da API)
- Relatórios PDF / exportação em massa
- CI/CD e deploy automatizado
- Blacklist de JWT no logout

Para dúvidas sobre um endpoint específico, use `GET` no recurso com token válido e inspecione o JSON retornado; em desenvolvimento, `DEBUG=True` exibe detalhes de erro 400.
