from django.db import models


class TipoLocalizacao(models.TextChoices):
    CAMPUS = "campus", "Campus"
    PREDIO = "predio", "Prédio"
    LABORATORIO = "laboratorio", "Laboratório"
    ARMARIO = "armario", "Armário"
    POSICAO = "posicao", "Posição"


class TipoItem(models.TextChoices):
    EQUIPAMENTO = "equipamento", "Equipamento"
    CONSUMIVEL = "consumivel", "Consumível"
    REAGENTE = "reagente", "Reagente"
    EPI = "epi", "EPI"
    PECA = "peca", "Peça"


class StatusOperacional(models.TextChoices):
    ATIVO = "ativo", "Ativo"
    EM_MANUTENCAO = "em_manutencao", "Em manutenção"
    INATIVO = "inativo", "Inativo"
    DESCARTADO = "descartado", "Descartado"


class Prioridade(models.TextChoices):
    BAIXA = "baixa", "Baixa"
    MEDIA = "media", "Média"
    ALTA = "alta", "Alta"
    CRITICA = "critica", "Crítica"


class StatusRequisicao(models.TextChoices):
    RASCUNHO = "rascunho", "Rascunho"
    ABERTA = "aberta", "Aberta"
    EM_APROVACAO = "em_aprovacao", "Em aprovação"
    APROVADA = "aprovada", "Aprovada"
    REJEITADA = "rejeitada", "Rejeitada"
    ATENDIDA = "atendida", "Atendida"
    CANCELADA = "cancelada", "Cancelada"


class StatusOrdemServico(models.TextChoices):
    ABERTA = "aberta", "Aberta"
    EM_EXECUCAO = "em_execucao", "Em execução"
    AGUARDANDO_PECAS = "aguardando_pecas", "Aguardando peças"
    ENCERRADA = "encerrada", "Encerrada"
    CANCELADA = "cancelada", "Cancelada"


class TipoManutencao(models.TextChoices):
    PREVENTIVA = "preventiva", "Preventiva"
    CORRETIVA = "corretiva", "Corretiva"
    CALIBRACAO = "calibracao", "Calibração"
    VERIFICACAO = "verificacao", "Verificação"
    INSPECAO = "inspecao", "Inspeção"


class StatusInventario(models.TextChoices):
    ABERTO = "aberto", "Aberto"
    EM_ANDAMENTO = "em_andamento", "Em andamento"
    ENCERRADO = "encerrado", "Encerrado"
    CANCELADO = "cancelado", "Cancelado"


class TipoBaixa(models.TextChoices):
    DESCARTE = "descarte", "Descarte"
    BAIXA = "baixa", "Baixa"
    PERDA = "perda", "Perda"
    OBSOLESCENCIA = "obsolescencia", "Obsolescência"
    AVARIA = "avaria_irrecuperavel", "Avaria irrecuperável"


class TipoMovimentacao(models.TextChoices):
    ENTRADA = "entrada", "Entrada"
    SAIDA = "saida", "Saída"
    TRANSFERENCIA = "transferencia", "Transferência"
    AJUSTE = "ajuste", "Ajuste"
    BAIXA = "baixa", "Baixa"
    INVENTARIO = "inventario", "Inventário"
