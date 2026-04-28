# Modelagem PostgreSQL - Versão Fiel ao Domínio

## Objetivo

Este documento define uma modelagem relacional mais fiel ao domínio descrito no projeto de controle de estoque e manutenção de equipamentos de laboratório.

O foco é refletir os requisitos já narrados no documento do projeto: cadastro, classificação, localização e custódia, lotes e validade, movimentações, requisições internas, ordens de serviço, manutenção/calibração, inventário, baixa/descarte e auditoria.

## Escopo desta versão

- Cadastro de usuários e perfis.
- Cadastro de categorias, unidades de medida e localizações hierárquicas.
- Cadastro de itens com distinção entre item genérico e equipamento.
- Controle de estoques por local, lotes com validade e movimentações.
- Requisições internas com aprovação e atendimento parcial.
- Ordens de serviço com histórico de manutenções e calibrações.
- Inventários periódicos, baixas e descarte.
- Auditoria de ações relevantes.

## Entidades principais

### `usuarios`

- `id`
- `nome`
- `email`
- `senha_hash`
- `perfil_id`
- `ativo`
- `created_at`
- `updated_at`

### `perfis`

- `id`
- `codigo`
- `nome`
- `descricao`

### `categorias`

- `id`
- `codigo`
- `nome`
- `descricao`
- `ativa`

### `unidades_medida`

- `id`
- `nome`
- `sigla`
- `permite_fracionamento`

### `localizacoes`

- `id`
- `nome`
- `codigo`
- `tipo`
- `localizacao_pai_id`
- `ativa`
- `created_at`
- `updated_at`

### `itens`

- `id`
- `nome`
- `codigo_interno`
- `descricao`
- `categoria_id`
- `unidade_medida_id`
- `tipo_item`
- `controlado`
- `ativo`
- `created_at`

- `updated_at`

### `equipamentos`

- `id`
- `item_id`
- `numero_serie`
- `tombamento`
- `marca`
- `modelo`
- `status_operacional`
- `data_aquisicao`
- `created_at`
- `updated_at`

### `estoques`

- `id`
- `item_id`
- `localizacao_id`
- `quantidade_disponivel`
- `quantidade_reservada`
- `nivel_minimo`
- `nivel_alerta`
- `updated_at`

### `lotes`

- `id`
- `item_id`
- `codigo_lote`
- `fabricante`
- `data_fabricacao`
- `validade`
- `quantidade_disponivel`
- `created_at`
- `updated_at`

### `movimentacoes`

- `id`
- `item_id`
- `lote_id`
- `usuario_id`
- `localizacao_origem_id`
- `localizacao_destino_id`
- `tipo_movimentacao`
- `quantidade`
- `motivo`
- `created_at`

### `requisicoes`

- `id`
- `solicitante_id`
- `aprovador_id`
- `setor_solicitante`
- `status`
- `finalidade`
- `justificativa`
- `prioridade`
- `created_at`
- `data_aprovacao`
- `data_atendimento`
- `observacao`

### `requisicao_itens`

- `id`
- `requisicao_id`
- `item_id`
- `lote_sugerido_id`
- `quantidade_solicitada`
- `quantidade_aprovada`
- `quantidade_atendida`
- `observacao`

### `ordens_servico`

- `id`
- `equipamento_id`
- `solicitante_id`
- `tecnico_responsavel_id`
- `descricao_problema`
- `descricao_servico`
- `prioridade`
- `status`
- `aberta_em`
- `inicio_execucao_em`
- `encerrada_em`
- `laudo_emitido`

### `manutencoes`

- `id`
- `ordem_servico_id`
- `tipo_manutencao`
- `descricao`
- `resultado`
- `realizada_em`
- `custo_estimado`
- `proximo_vencimento`

### `inventarios`

- `id`
- `nome`
- `descricao`
- `responsavel_id`
- `status`
- `iniciado_em`
- `encerrado_em`

### `inventario_itens`

- `id`
- `inventario_id`
- `item_id`
- `localizacao_id`
- `quantidade_sistema`
- `quantidade_contada`
- `diferenca`
- `observacao`

### `baixas`

- `id`
- `item_id`
- `equipamento_id`
- `usuario_id`
- `tipo_baixa`
- `motivo`
- `destino_final`
- `documento_referencia`
- `realizada_em`

### `auditorias`

- `id`
- `usuario_id`
- `acao`
- `entidade`
- `entidade_id`
- `detalhes`
- `ip_origem`
- `created_at`

## Relacionamentos

- `localizacoes.localizacao_pai_id` aponta para `localizacoes.id`.
- `itens.codigo_interno` identifica o item no sistema.
- `itens.categoria_id` aponta para `categorias.id`.
- `itens.unidade_medida_id` aponta para `unidades_medida.id`.
- `equipamentos.item_id` é 1:1 com `itens.id`.
- `estoques.item_id` e `estoques.localizacao_id` criam o saldo por local, com reserva e níveis mínimos.
- `lotes.item_id` referencia o item controlado por lote e sustenta FEFO.
- `movimentacoes` registra a trilha de entrada, saída, transferência, ajuste, baixa e inventário.
- `requisicao_itens` resolve o N:N entre `requisicoes` e `itens` com rastreio do lote sugerido.
- `ordens_servico.equipamento_id` referencia o equipamento e permite histórico de manutenção e laudo.
- `inventario_itens` consolida a contagem física contra o saldo do sistema.
- `baixas` registra descarte, perda, obsolescência e baixa definitiva.
- `auditorias` registra eventos relevantes de qualquer entidade.

## Regras de modelagem recomendadas

- Usar `CHECK` para campos enumerados como `perfil`, `tipo_item`, `tipo_movimentacao`, `status`, `prioridade`, `status_operacional` e `tipo_baixa`.
- Garantir unicidade em `usuarios.email`, `categorias.codigo`, `categorias.nome`, `perfis.codigo`, `perfis.nome`, `itens.codigo_interno`, `equipamentos.numero_serie` e `equipamentos.tombamento` quando aplicável.
- Usar `NUMERIC(14,3)` para quantidades de materiais e `BIGINT` para identificadores.
- Preferir `TIMESTAMPTZ` para datas de criação e eventos.
- Guardar observações de auditoria em `JSONB` e origem de acesso em `INET`.

## Ordem sugerida de implementação

1. `categorias`, `perfis`, `unidades_medida`, `localizacoes` e `usuarios`.
2. `itens` e `equipamentos`.
3. `estoques`, `lotes` e `movimentacoes`.
4. `requisicoes` e `requisicao_itens`.
5. `ordens_servico` e `manutencoes`.
6. `inventarios` e `inventario_itens`.
7. `baixas` e `auditorias`.

## Próximo passo prático

Se quiser, o próximo arquivo pode ser um script SQL completo para executar diretamente no PostgreSQL com esse modelo.
