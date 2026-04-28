CREATE TABLE IF NOT EXISTS categorias (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(40) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL UNIQUE,
    descricao TEXT,
    ativa BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS perfis (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(40) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS unidades_medida (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(120) NOT NULL UNIQUE,
    sigla VARCHAR(20) NOT NULL UNIQUE,
    permite_fracionamento BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS localizacoes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    codigo VARCHAR(60),
    tipo VARCHAR(30) NOT NULL,
    localizacao_pai_id BIGINT REFERENCES localizacoes(id) ON DELETE SET NULL,
    ativa BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (tipo IN ('campus', 'predio', 'laboratorio', 'armario', 'posicao')),
    UNIQUE (tipo, nome, localizacao_pai_id)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    matricula VARCHAR(60) UNIQUE,
    perfil_id BIGINT NOT NULL REFERENCES perfis(id) ON DELETE RESTRICT,
    cargo VARCHAR(120),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (matricula IS NULL OR length(matricula) >= 3)
);

CREATE TABLE IF NOT EXISTS itens (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_interno VARCHAR(60) NOT NULL UNIQUE,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    categoria_id BIGINT REFERENCES categorias(id) ON DELETE RESTRICT,
    unidade_medida_id BIGINT REFERENCES unidades_medida(id) ON DELETE RESTRICT,
    tipo_item VARCHAR(40) NOT NULL,
    controlado BOOLEAN NOT NULL DEFAULT FALSE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (tipo_item IN ('equipamento', 'consumivel', 'reagente', 'epi', 'peca'))
);

CREATE TABLE IF NOT EXISTS equipamentos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL UNIQUE REFERENCES itens(id) ON DELETE CASCADE,
    numero_serie VARCHAR(200) NOT NULL UNIQUE,
    tombamento VARCHAR(200) UNIQUE,
    marca VARCHAR(120),
    modelo VARCHAR(120),
    status_operacional VARCHAR(40) NOT NULL DEFAULT 'ativo',
    data_aquisicao DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (status_operacional IN ('ativo', 'em_manutencao', 'inativo', 'descartado'))
);

CREATE TABLE IF NOT EXISTS estoques (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES itens(id) ON DELETE CASCADE,
    localizacao_id BIGINT NOT NULL REFERENCES localizacoes(id) ON DELETE RESTRICT,
    quantidade_disponivel NUMERIC(14, 3) NOT NULL DEFAULT 0,
    quantidade_reservada NUMERIC(14, 3) NOT NULL DEFAULT 0,
    nivel_minimo NUMERIC(14, 3) NOT NULL DEFAULT 0,
    nivel_alerta NUMERIC(14, 3) NOT NULL DEFAULT 0,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (item_id, localizacao_id),
    CHECK (quantidade_disponivel >= 0),
    CHECK (quantidade_reservada >= 0),
    CHECK (nivel_minimo >= 0),
    CHECK (nivel_alerta >= 0),
    CHECK (nivel_alerta >= nivel_minimo)
);

CREATE TABLE IF NOT EXISTS lotes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES itens(id) ON DELETE CASCADE,
    codigo_lote VARCHAR(120) NOT NULL,
    fabricante VARCHAR(160),
    data_fabricacao DATE,
    data_validade DATE,
    quantidade_disponivel NUMERIC(14, 3) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (item_id, codigo_lote),
    CHECK (quantidade_disponivel >= 0)
);

CREATE TABLE IF NOT EXISTS requisicoes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    solicitante_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    aprovador_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    setor_solicitante VARCHAR(160),
    finalidade TEXT NOT NULL,
    justificativa TEXT,
    prioridade VARCHAR(20) NOT NULL DEFAULT 'media',
    status VARCHAR(30) NOT NULL DEFAULT 'aberta',
    data_solicitacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_aprovacao TIMESTAMPTZ,
    data_atendimento TIMESTAMPTZ,
    observacao TEXT,
    CHECK (prioridade IN ('baixa', 'media', 'alta', 'critica')),
    CHECK (status IN ('rascunho', 'aberta', 'em_aprovacao', 'aprovada', 'rejeitada', 'atendida', 'cancelada'))
);

CREATE TABLE IF NOT EXISTS requisicao_itens (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    requisicao_id BIGINT NOT NULL REFERENCES requisicoes(id) ON DELETE CASCADE,
    item_id BIGINT NOT NULL REFERENCES itens(id) ON DELETE RESTRICT,
    lote_sugerido_id BIGINT REFERENCES lotes(id) ON DELETE SET NULL,
    quantidade_solicitada NUMERIC(14, 3) NOT NULL,
    quantidade_aprovada NUMERIC(14, 3),
    quantidade_atendida NUMERIC(14, 3),
    observacao TEXT,
    CHECK (quantidade_solicitada > 0),
    CHECK (quantidade_aprovada IS NULL OR quantidade_aprovada >= 0),
    CHECK (quantidade_atendida IS NULL OR quantidade_atendida >= 0)
);

CREATE TABLE IF NOT EXISTS ordens_servico (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    equipamento_id BIGINT NOT NULL REFERENCES equipamentos(id) ON DELETE RESTRICT,
    solicitante_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    tecnico_responsavel_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    descricao_problema TEXT NOT NULL,
    descricao_servico TEXT,
    prioridade VARCHAR(20) NOT NULL DEFAULT 'media',
    status VARCHAR(40) NOT NULL DEFAULT 'aberta',
    aberta_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    inicio_execucao_em TIMESTAMPTZ,
    encerrada_em TIMESTAMPTZ,
    laudo_emitido BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (prioridade IN ('baixa', 'media', 'alta', 'critica')),
    CHECK (status IN ('aberta', 'em_execucao', 'aguardando_pecas', 'encerrada', 'cancelada'))
);

CREATE TABLE IF NOT EXISTS manutencoes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ordem_servico_id BIGINT NOT NULL REFERENCES ordens_servico(id) ON DELETE CASCADE,
    tipo_manutencao VARCHAR(40) NOT NULL,
    descricao TEXT,
    resultado TEXT,
    realizada_em TIMESTAMPTZ,
    custo_estimado NUMERIC(14, 2),
    proximo_vencimento DATE,
    CHECK (tipo_manutencao IN ('preventiva', 'corretiva', 'calibracao', 'verificacao', 'inspecao')),
    CHECK (custo_estimado IS NULL OR custo_estimado >= 0)
);

CREATE TABLE IF NOT EXISTS inventarios (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(160) NOT NULL,
    descricao TEXT,
    responsavel_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'aberto',
    iniciado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    encerrado_em TIMESTAMPTZ,
    CHECK (status IN ('aberto', 'em_andamento', 'encerrado', 'cancelado'))
);

CREATE TABLE IF NOT EXISTS inventario_itens (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    inventario_id BIGINT NOT NULL REFERENCES inventarios(id) ON DELETE CASCADE,
    item_id BIGINT NOT NULL REFERENCES itens(id) ON DELETE RESTRICT,
    localizacao_id BIGINT REFERENCES localizacoes(id) ON DELETE SET NULL,
    quantidade_sistema NUMERIC(14, 3) NOT NULL DEFAULT 0,
    quantidade_contada NUMERIC(14, 3) NOT NULL DEFAULT 0,
    diferenca NUMERIC(14, 3) GENERATED ALWAYS AS (quantidade_contada - quantidade_sistema) STORED,
    observacao TEXT,
    CHECK (quantidade_sistema >= 0),
    CHECK (quantidade_contada >= 0)
);

CREATE TABLE IF NOT EXISTS baixas (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT REFERENCES itens(id) ON DELETE RESTRICT,
    equipamento_id BIGINT REFERENCES equipamentos(id) ON DELETE RESTRICT,
    usuario_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    tipo_baixa VARCHAR(40) NOT NULL,
    motivo TEXT NOT NULL,
    destino_final TEXT,
    documento_referencia VARCHAR(120),
    realizada_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (tipo_baixa IN ('descarte', 'baixa', 'perda', 'obsolescencia', 'avaria_irrecuperavel')),
    CHECK (item_id IS NOT NULL OR equipamento_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES itens(id) ON DELETE RESTRICT,
    lote_id BIGINT REFERENCES lotes(id) ON DELETE SET NULL,
    usuario_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    requisicao_item_id BIGINT REFERENCES requisicao_itens(id) ON DELETE SET NULL,
    ordem_servico_id BIGINT REFERENCES ordens_servico(id) ON DELETE SET NULL,
    inventario_item_id BIGINT REFERENCES inventario_itens(id) ON DELETE SET NULL,
    baixa_id BIGINT REFERENCES baixas(id) ON DELETE SET NULL,
    localizacao_origem_id BIGINT REFERENCES localizacoes(id) ON DELETE SET NULL,
    localizacao_destino_id BIGINT REFERENCES localizacoes(id) ON DELETE SET NULL,
    tipo_movimentacao VARCHAR(20) NOT NULL,
    quantidade NUMERIC(14, 3) NOT NULL,
    saldo_resultante NUMERIC(14, 3),
    motivo TEXT,
    observacao TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (tipo_movimentacao IN ('entrada', 'saida', 'transferencia', 'ajuste', 'baixa', 'inventario')),
    CHECK (quantidade > 0)
);

CREATE TABLE IF NOT EXISTS auditorias (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    acao VARCHAR(200) NOT NULL,
    entidade VARCHAR(120) NOT NULL,
    entidade_id BIGINT,
    detalhes JSONB,
    ip_origem INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_itens_categoria_id ON itens (categoria_id);
CREATE INDEX IF NOT EXISTS idx_itens_unidade_medida_id ON itens (unidade_medida_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_perfil_id ON usuarios (perfil_id);
CREATE INDEX IF NOT EXISTS idx_estoques_item_localizacao ON estoques (item_id, localizacao_id);
CREATE INDEX IF NOT EXISTS idx_lotes_item_validade ON lotes (item_id, data_validade);
CREATE INDEX IF NOT EXISTS idx_requisicoes_status ON requisicoes (status);
CREATE INDEX IF NOT EXISTS idx_ordens_servico_status ON ordens_servico (status);
CREATE INDEX IF NOT EXISTS idx_inventarios_status ON inventarios (status);
CREATE INDEX IF NOT EXISTS idx_movimentacoes_item_created_at ON movimentacoes (item_id, created_at DESC);
