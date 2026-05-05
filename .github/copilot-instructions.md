# Sistema de Controle de Estoque e Manutenção de Equipamentos de Laboratório

**Instituição:** Universidade de Maceió – AFYA  
**Curso:** Ciência da Computação  
**Disciplina:** Project Lab  
**Ano:** 2026  

**Equipe:**
- Gustavo Inglês
- Lucas Patrício
- Lucas Souza
- Pedro Moraes

---

## Sumário

1. [Introdução](#introdução)
2. [Desenvolvimento](#desenvolvimento)
   - [2.1 Plano de Projeto](#21-plano-de-projeto)
   - [2.2 Modelagem UML – Visão Estrutural](#22-modelagem-uml--visão-estrutural)
   - [2.3 Modelagem UML – Visão Comportamental](#23-modelagem-uml--visão-comportamental)
   - [2.4 Casos de Uso Detalhados](#24-casos-de-uso-detalhados)
3. [Conclusão](#conclusão)

---

## Introdução

Este documento consolida os artefatos de engenharia de requisitos produzidos ao longo da primeira unidade da disciplina Project Lab, no âmbito do projeto de desenvolvimento do **Sistema de Controle de Estoque e Manutenção de Equipamentos de Laboratório**.

O sistema destina-se a centralizar e formalizar a gestão de ativos laboratoriais em instituições de ensino, pesquisa e extensão. O escopo abrange:

- Equipamentos
- Peças e sobressalentes
- Consumíveis
- Reagentes
- Equipamentos de Proteção Individual (EPIs)

As funcionalidades principais contemplam:

- Controle de localização e custódia
- Movimentações de estoque
- Ordens de serviço
- Manutenções preventivas e corretivas
- Inventários periódicos

**Objetivo final:** assegurar rastreabilidade, disponibilidade operacional, conformidade regulatória e continuidade das atividades laboratoriais.

> **Versões ampliadas dos diagramas:** [Google Drive](https://drive.google.com/drive/folders/1xDHeee0ht4Q1qikmIvQOUWJs49MWzOkr?usp=drive_link)

---

## Desenvolvimento

### 2.1 Plano de Projeto

#### 2.1.1 Stack Tecnológica

Todas as tecnologias adotadas são de código aberto e distribuição gratuita, sem custo de licenciamento.

| Camada | Tecnologia | Observação |
|---|---|---|
| Front-end | Next.js | Renderização e entrega de assets estáticos |
| Back-end | Django | API REST e implementação das regras de negócio |
| Banco de Dados | PostgreSQL | Persistência dos dados e integridade referencial |
| Implantação | Self-hosted / Desktop nativo | Ambiente local ou servidor institucional |

#### 2.1.2 Equipe e Responsabilidades

A equipe é composta por quatro desenvolvedores full-stack.

| Membro | Perfil | Atribuições |
|---|---|---|
| Gustavo Inglês | Full-stack / DevOps | Desenvolvimento full-stack; responsável pelo deploy e configuração do ambiente de desenvolvimento |
| Lucas Patrício | Full-stack / DBA | Desenvolvimento full-stack; co-responsável pela modelagem e administração do banco de dados |
| Lucas Souza | Full-stack | Desenvolvimento full-stack |
| Pedro Moraes | Full-stack / DBA | Desenvolvimento full-stack; co-responsável pela modelagem e administração do banco de dados |

#### 2.1.3 Abordagem de Desenvolvimento

O projeto adota **desenvolvimento enxuto (lean)**, com o objetivo de validar objetivos e regras de negócio o mais rápido possível, lançando novas funcionalidades de forma incremental a cada iteração.

Princípios adotados:

- Cada módulo é entregue como uma **fatia vertical funcional** — da interface ao banco de dados — permitindo validação com os usuários antes de avançar para a próxima etapa.
- Requisitos priorizados conforme ordem definida no cronograma, garantindo que a base de rastreabilidade e autenticação esteja consolidada antes dos módulos de negócio.
- Ao final de cada sprint, o produto parcial é apresentado aos responsáveis para coleta de feedback e ajuste das regras de negócio.

#### 2.1.4 Cronograma

O projeto tem duração de **doze semanas**, organizadas em sprints.

| Período | Módulo / Entrega | Responsáveis | Critério de Aceite |
|---|---|---|---|
| Sem. 1–2 | Modelagem do banco de dados | Lucas Patrício, Pedro Moraes | Diagrama ER aprovado; migrações iniciais aplicadas |
| Sem. 2–3 | Scaffolding Django — autenticação e autorização | Gustavo Inglês, Lucas Souza | Endpoints de autenticação funcionais; middlewares de permissão configurados |
| Sem. 3 | Prototipação e design system | Todos | Wireframes aprovados; componentes base definidos no Next.js |
| Sem. 4 | Módulo de Cadastro e Classificação | Gustavo Inglês, Lucas Souza | CRUD de ativos com categorização e filtros operacionais |
| Sem. 5 | Módulos de Lotes/Validade e Localização/Custódia | Todos | Controle de lotes, alertas de validade e transferência de custódia |
| Sem. 6 | Módulo de Movimentações de Estoque | Lucas Patrício, Pedro Moraes | Entradas, saídas e histórico de movimentações registrados |
| Sem. 7 | Módulos de Níveis Mínimos e Requisições Internas | Todos | Alertas de reposição automáticos; fluxo de solicitação e devolução |
| Sem. 8 | Módulo de Estados Operacionais do Equipamento | Gustavo Inglês, Lucas Souza | Ciclo de vida implementado: ativo, em manutenção, inativo, descartado |
| Sem. 9–10 | Módulos de Manutenção/Calibração e Ordens de Serviço | Todos | Agendamento de manutenções; ciclo completo de OS com histórico por equipamento |
| Sem. 11 | Módulo de Descarte, Baixa e Conformidade | Lucas Patrício, Pedro Moraes | Registro de descarte conforme normas; geração de laudos |
| Sem. 12 | Módulo de Inventário e Auditoria | Todos | Inventários periódicos, relatórios de auditoria e exportação de dados |

#### 2.1.5 Estimativa de Custos

Não há previsão de gastos com licenciamento de software.

| Componente | Descrição | Observação |
|---|---|---|
| Alocação de pessoal | 4 desenvolvedores ao longo de 12 semanas (~3 meses) | Custo variável conforme regime de contratação da instituição |
| Infraestrutura | Possível custo de servidor ou hospedagem | Nulo em ambiente 100% self-hosted local |
| Licenciamento | Next.js, Django, PostgreSQL | Sem custo — tecnologias de código aberto |

---

### 2.2 Modelagem UML – Visão Estrutural

#### 2.2.1 Diagrama de Classes

Modela as principais entidades de domínio e seus relacionamentos.

**Entidades principais:**

- `Item` — núcleo do sistema; especializada em `Equipamento`
- `Lote` — relacionado a `Item`
- `Movimentação` — relacionado a `Item`
- `Estoque` — relacionado a `Item`
- `Requisição` — conecta usuários a itens via `ItemRequisicao`
- `ItemRequisicao` — classe associativa entre `Requisição` e `Item`
- `OrdemServico` — cobre o ciclo de manutenção dos equipamentos
- `Manutencao` — detalha as manutenções por equipamento
- `Auditoria` — registra transversalmente as ações do sistema
- `Usuario` — representa os atores do sistema

**Atributos relevantes por entidade:**

```
Usuario
  - id: int
  - nome: String
  - email: String
  - senha: String
  - perfil: String
  + autenticar()

Item
  - id: int
  - nome: String
  - descricao: String
  - tipo: String
  - unidadeMedida: String
  - controlado: boolean

Equipamento (herda de Item)
  - numeroSerie: String
  - tombamento: String
  - status: String
  + alterarStatus()

Estoque
  - id: int
  - quantidade: int
  - localizacao: String
  + adicionarItens()
  + removerItens()

Lote
  - id: int
  - validade: Date
  - quantidade: int

Movimentacao
  - id: int
  - tipo: String
  - data: Date

Requisicao
  - id: int
  - status: String
  - data: Date
  + criar()
  + aprovar()

ItemRequisicao
  - quantidade: int

OrdemServico
  - id: int
  - descricao: String
  - status: String

Manutencao
  - id: int
  - tipo: String
  - data: Date

Auditoria
  - id: int
  - acao: String
  - data: Date
```

#### 2.2.2 Diagrama de Pacotes

Organiza as responsabilidades do software em camadas arquiteturais coesas:

| Camada | Componentes |
|---|---|
| Apresentação | TelaLogin, TelaCadastroItem, TelaRequisicao |
| Aplicação | UsuarioService, EstoqueService, RequisicaoService, ManutencaoService |
| Domínio | Usuario, Item |
| Infraestrutura | RepositorioUsuario, banco de dados |
| Auditoria | Trilhas de log |

Essa separação favorece a manutenibilidade e o isolamento de responsabilidades, alinhando-se aos princípios de arquitetura em camadas.

#### 2.2.3 Diagrama de Entidades e Relacionamentos

Formaliza a estrutura do banco de dados, detalhando atributos, tipos e cardinalidades.

**Tabelas principais:**

```
USUARIO         — id, nome, email, senha, perfil
ITEM            — id, nome, descricao, tipo, unidade_medida, controlado
EQUIPAMENTO     — id_item (FK), numero_serie, tombamento, status
REQUISICAO      — id, id_usuario (FK), status, data
ORDEM_SERVICO   — id, id_equipamento (FK), descricao, status
MANUTENCAO      — id, id_ordem_servico (FK), tipo, data
AUDITORIA       — id, acao, data
```

**Tabelas operacionais:**

```
ESTOQUE         — id, id_item (FK), quantidade, localizacao
LOTE            — id, id_item (FK), validade, quantidade
MOVIMENTACAO    — id, id_item (FK), tipo, data
```

**Tabela associativa:**

```
ITEM_REQUISICAO — id_requisicao (FK), id_item (FK), quantidade
```

> Relacionamento N:N entre `REQUISICAO` e `ITEM` suportado por `ITEM_REQUISICAO`.

#### 2.2.4 Diagrama de Componentes

Detalha a composição interna do backend e sua interação com integrações externas.

**Componentes agrupados por responsabilidade:**

- Autenticação
- Cadastro
- Movimentações
- Manutenções
- Requisições
- Estoque
- Conformidade
- Auditoria

**Comunicação:** todos os componentes se comunicam através de um **API Gateway REST**.

**Integrações externas:**
- Serviços de notificação
- ERP/LIMS institucionais
- Armazenamento em nuvem (laudos e evidências)

#### 2.2.5 Diagrama da Arquitetura Geral do Sistema

Fluxo de dados em alto nível:

```
Frontend (Next.js — Interface Web)
        ↓
Backend (Django — Controllers API + Autenticação)
        ↓
Serviços
  ├── EstoqueService
  ├── RequisicaoService
  └── ManutencaoService
        ↓
Infraestrutura
  ├── Banco de Dados (PostgreSQL)
  ├── Repositórios
  └── Auditoria
        ↓
Domínio (Entidades)
```

A arquitetura privilegia o **desacoplamento entre camadas**, facilitando evoluções incrementais e substituição de tecnologias específicas sem impacto sistêmico.

---

### 2.3 Modelagem UML – Visão Comportamental

#### 2.3.1 Diagrama de Casos de Uso

**Atores identificados:**

| Ator | Papel |
|---|---|
| Solicitante | Realiza requisições de itens |
| Administrador | Gerencia cadastros, permissões e configurações |
| Gestor | Aprova requisições e supervisiona operações |
| Almoxarife | Controla estoque e movimentações físicas |
| Técnico de Laboratório | Opera equipamentos e realiza requisições internas |
| Técnico de Manutenção | Executa ordens de serviço e manutenções |
| Auditor | Consulta logs e relatórios de auditoria |
| Fiscal | Verifica conformidade regulatória |

**Agrupamentos temáticos dos casos de uso:**

- Usuário e Acesso
- Gestão Operacional
- Requisições
- Movimentações
- Cadastros e Classificação
- Manutenção e Calibração
- Logs e Auditoria

#### 2.3.2 Diagrama de Atividades

Detalha três fluxos operacionais principais:

**Fluxo 1 — Cadastro de Itens (RF01–RF05)**
- Raias: Sistema, Gestor/Admin, Almoxarife
- Inclui: validação de dados obrigatórios, tratamento de itens controlados, registro de auditoria

**Fluxo 2 — Saída de Estoque (RF09, RF13, RF14, RF17)**
- Raias: Sistema, Gestor/Admin, Almoxarife, Técnico de Laboratório
- Inclui: múltiplos lotes sob regra FEFO, verificação de saldo mínimo, autorização de itens controlados

**Fluxo 3 — Ordem de Serviço (RF27–RF32)**
- Raias: Sistema, Técnico de Manutenção
- Inclui: abertura, execução e encerramento de OS, indisponibilidade de peças

#### 2.3.3 Diagrama de Sequência

Descreve a troca de mensagens entre atores e sistema em dois fluxos fundamentais.

**Fluxo 1 — Cadastro de Item (RF01–RF05)**

```
Técnico Lab → Sistema: Acessar módulo Cadastro de Itens
Sistema → Técnico Lab: Exibir formulário de cadastro
Técnico Lab → Sistema: Preencher classificação, descrição, unidade de medida, flag controlado

[alt: Item do tipo Equipamento]
  Sistema → Almoxarife: Solicitar identificação técnica (nº série / tombamento) RF02
  Almoxarife → Sistema: Informar nº de série e tombamento

[alt: Item Controlado]
  Sistema → Almoxarife: Solicitar parâmetros de restrição RF04
  Almoxarife → Sistema: Informar restrições de movimentação

Sistema → Banco de Dados: Validar dados obrigatórios

[alt: Dados Inválidos]
  Sistema → Técnico Lab: Bloquear salvamento — exibir erro (FE1/FE2)

[alt: Dados Válidos]
  Banco de Dados → Banco de Dados: Gerar ID único + gravar Item
  Banco de Dados → Sistema: Confirmação de persistência
  Banco de Dados → Banco de Dados: Registrar log de auditoria RF37
  Sistema → Técnico Lab: Item cadastrado com sucesso
```

**Fluxo 2 — Requisição e Saída de Estoque (RF09, RF13, RF14, RF17, RF19)**

```
Solicitante → Sistema: Abrir requisição interna RF19 (solicitante, finalidade, itens)
Sistema → Banco de Dados: Registrar requisição
Banco de Dados → Sistema: Requisição criada
Sistema → Gestor: Notificar nova requisição
Gestor → Sistema: Avaliar requisição

[alt: Requisição aprovada]
  Gestor → Sistema: Aprovar requisição
  Sistema → Almoxarife: Liberar separação do item
  Almoxarife → Sistema: Registrar saída do item

[alt: Item controlado]
  Sistema → Gestor: Solicitar autorização de saída RF14
  Gestor → Sistema: Autorizar saída

[alt: Múltiplos lotes disponíveis]
  Sistema → Almoxarife: Sugerir lote FEFO (menor validade) RF09
  [alt: Almoxarife aceita sugestão]
    Almoxarife → Sistema: Confirmar lote sugerido
  [alt: Almoxarife recusa]
    Almoxarife → Sistema: Selecionar lote manualmente
```

---

### 2.4 Casos de Uso Detalhados

#### UC01 – RF01: Cadastro de Itens

| Campo | Descrição |
|---|---|
| **Atores** | Administrador do Sistema, Almoxarife |
| **Pré-requisitos** | Usuário autenticado; usuário possui permissão de cadastro; categorias e unidades previamente configuradas |

**Fluxo Principal:**

1. Ator acessa módulo "Cadastro de Itens"
2. Seleciona opção "Novo Item"
3. Informa classificação (equipamento, consumível etc.)
4. Preenche descrição técnica
5. Define unidade de medida
6. Indica se item é controlado
7. Confirma operação
8. Sistema valida dados
9. Sistema gera identificador único
10. Sistema grava item na base de dados

**Fluxos Alternativos:**

- `FA1 — Item Controlado:` sistema solicita parâmetros adicionais de restrição
- `FA2 — Item do tipo Equipamento:` sistema exige futura identificação técnica

**Fluxos de Exceção:**

- `FE1:` Campo obrigatório não preenchido → sistema bloqueia salvamento
- `FE2:` Identificação duplicada → sistema exibe erro e solicita correção
- `FE3:` Falha de persistência → operação cancelada e log registrado

**Pós-condição:** item registrado no sistema, disponível para movimentações futuras, registro auditável criado.

---

#### UC02 – RF02: Identificação Patrimonial e Técnica

| Campo | Descrição |
|---|---|
| **Atores** | Administrador, Almoxarife |
| **Pré-requisitos** | Item classificado como equipamento; cadastro inicial concluído |

**Fluxo Principal:**

1. Ator acessa cadastro do equipamento
2. Informa número de série (obrigatório)
3. Informa número de tombamento (quando aplicável)
4. Confirma registro
5. Sistema valida unicidade
6. Sistema salva identificadores

**Fluxos Alternativos:**

- Equipamento sem tombamento institucional → campo opcional mantido em branco

**Fluxos de Exceção:**

- `FE1:` Número de série já cadastrado → sistema bloqueia
- `FE2:` Formato inválido → sistema solicita correção

**Pós-condição:** equipamento passa a ser rastreável individualmente.

---

#### UC03 – RF03: Unidade de Medida e Fracionamento

| Campo | Descrição |
|---|---|
| **Ator** | Administrador |
| **Pré-requisito** | Item classificado como consumível ou reagente |

**Fluxo Principal:**

1. Acessar cadastro do item
2. Selecionar unidade de medida
3. Definir se permite fracionamento
4. Confirmar configuração

**Fluxos Alternativos:**

- Unidade já cadastrada no sistema

**Fluxos de Exceção:**

- Unidade inexistente → sistema exige cadastro prévio

**Pós-condição:** sistema habilita controle quantitativo adequado.

---

#### UC04 – RF04: Marcação de Item Controlado

| Campo | Descrição |
|---|---|
| **Ator** | Administrador |
| **Pré-requisito** | Item previamente cadastrado |

**Fluxo Principal:**

1. Editar item
2. Ativar flag "controlado"
3. Confirmar alteração
4. Sistema registra mudança e atualiza regras de movimentação

**Fluxos Alternativos:**

- Desmarcar item controlado (com justificativa obrigatória)

**Fluxos de Exceção:**

- Usuário sem permissão → operação negada

**Pós-condição:** item passa a exigir autorização para saída.

---

#### UC05 – RF05: Cadastro de Localização Física

| Campo | Descrição |
|---|---|
| **Ator** | Administrador |
| **Pré-requisitos** | Usuário autenticado; usuário possui perfil de Administrador; sistema operacional e banco disponíveis |

**Fluxo Principal:**

1. Ator acessa o módulo de configurações
2. Seleciona "Cadastrar Localização"
3. Informa o nível hierárquico (campus, prédio, laboratório ou armário/posição)
4. Preenche nome e código identificador (se aplicável)
5. Seleciona a localização pai (quando não for campus)
6. Confirma o cadastro
7. Sistema valida unicidade e consistência hierárquica
8. Sistema salva o registro

**Fluxos Alternativos:**

- `FA1 — Cadastro de Campus:` o sistema não exige localização pai
- `FA2 — Cadastro parcial da estrutura` (ex.: apenas campus e prédio), permitindo complementação posterior

**Fluxos de Exceção:**

- `FE1:` Nome duplicado no mesmo nível → sistema bloqueia cadastro
- `FE2:` Localização pai inexistente ou inválida → sistema solicita correção
- `FE3:` Usuário sem permissão → acesso negado

**Pós-condição:** localização registrada na estrutura hierárquica, disponível para vinculação de itens, registro da ação armazenado para auditoria.

---

## Conclusão

A consolidação dos artefatos de engenharia de requisitos evidencia a maturidade alcançada pela equipe na especificação do sistema. Os principais resultados desta primeira unidade são:

- **Plano de projeto** com premissas claras de escopo, stack tecnológica, alocação de equipe, cronograma de doze semanas e estimativa de custos.
- **Modelagem UML estrutural** (classes, pacotes, ER, componentes e arquitetura geral) traduzindo os requisitos em artefatos formais que orientam a implementação.
- **Modelagem UML comportamental** (casos de uso, atividades e sequência) caracterizando o comportamento esperado sob diferentes cenários operacionais.
- **Casos de uso detalhados** (RF01–RF05) cobrindo o fluxo inicial de cadastro e configuração dos itens, incluindo marcação de itens controlados, identificação patrimonial de equipamentos e estruturação hierárquica de localizações físicas.

A adoção de stack consolidada e de código aberto — **Next.js, Django e PostgreSQL** — aliada à abordagem de **desenvolvimento enxuto com entregas incrementais**, favorece a validação contínua das regras de negócio e reduz o risco de retrabalho.

Ao final do ciclo, espera-se que o sistema ofereça:

- Rastreabilidade completa dos ativos laboratoriais
- Controle efetivo de estoque e manutenções
- Conformidade com as exigências regulatórias aplicáveis
- Continuidade e qualidade das atividades de ensino, pesquisa e extensão